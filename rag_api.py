"""
FastAPI wrapper around rag_pipeline.py - real file upload via HTTP,
not manually placing files in the project folder.

Run:
    uvicorn rag_api:app --reload --port 8001

Then open http://127.0.0.1:8001/docs to upload a file and ask questions
through the Swagger UI, same way you tested verify.py's /api/v1/verify.

Endpoints:
    POST /api/v1/upload  - upload a PDF/DOCX/TXT, builds the index
    POST /api/v1/ask     - ask a question against the last uploaded doc
"""

import os
import shutil
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from rag_pipeline import extract_text, chunk_text, DocumentIndex, answer_question

app = FastAPI(title="VeritasRAG - Document QA")

# Single in-memory index, holding whatever was most recently uploaded.
# Fine for a one-user demo; would need per-session storage for multiple
# concurrent users.
_current_index = {"index": None, "filename": None}


class AskRequest(BaseModel):
    question: str
    top_k: int = 3


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!DOCTYPE html>
<html>
<head>
  <title>VeritasRAG - Document QA</title>
  <style>
    body { font-family: sans-serif; max-width: 700px; margin: 40px auto; padding: 0 20px; }
    h1 { font-size: 1.4em; }
    .box { border: 1px solid #ccc; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
    input[type=text] { width: 70%; padding: 8px; }
    button { padding: 8px 16px; cursor: pointer; }
    #status { color: #555; font-size: 0.9em; margin-top: 8px; }
    .qa { border-bottom: 1px solid #eee; padding: 12px 0; }
    .q { font-weight: bold; }
    .chunks { font-size: 0.85em; color: #666; margin-top: 6px; }
  </style>
</head>
<body>
  <h1>VeritasRAG - Document QA</h1>

  <div class="box">
    <input type="file" id="fileInput" accept=".pdf,.docx,.txt">
    <button onclick="uploadFile()">Upload</button>
    <div id="status"></div>
  </div>

  <div class="box">
    <input type="text" id="questionInput" placeholder="Ask a question about the document...">
    <button onclick="askQuestion()">Ask</button>
  </div>

  <div id="history"></div>

  <script>
    async function uploadFile() {
      const fileInput = document.getElementById('fileInput');
      const status = document.getElementById('status');
      if (!fileInput.files.length) { status.textContent = 'Choose a file first.'; return; }

      status.textContent = 'Uploading and indexing...';
      const formData = new FormData();
      formData.append('file', fileInput.files[0]);

      try {
        const res = await fetch('/api/v1/upload', { method: 'POST', body: formData });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Upload failed');
        status.textContent = `Indexed "${data.filename}" (${data.num_chunks} chunks). Ready for questions.`;
      } catch (err) {
        status.textContent = 'Error: ' + err.message;
      }
    }

    async function askQuestion() {
      const questionInput = document.getElementById('questionInput');
      const question = questionInput.value.trim();
      if (!question) return;

      const history = document.getElementById('history');
      const entry = document.createElement('div');
      entry.className = 'qa';
      entry.innerHTML = `<div class="q">Q: ${question}</div><div>Thinking...</div>`;
      history.prepend(entry);
      questionInput.value = '';

      try {
        const res = await fetch('/api/v1/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Request failed');

        const chunksHtml = data.chunks.map((c, i) => `[${i+1}] ${c}`).join('<br>');
        entry.innerHTML = `
          <div class="q">Q: ${question}</div>
          <div>${data.response}</div>
          <div class="chunks"><b>Source chunks used:</b><br>${chunksHtml}</div>
        `;
      } catch (err) {
        entry.innerHTML = `<div class="q">Q: ${question}</div><div>Error: ${err.message}</div>`;
      }
    }
  </script>
</body>
</html>
"""


@app.post("/api/v1/upload")
async def upload_document(file: UploadFile = File(...)):
    allowed_ext = (".pdf", ".docx", ".txt")
    if not file.filename.lower().endswith(allowed_ext):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {allowed_ext}",
        )

    # Save the upload to a temp file so extract_text() can read it by path.
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        text = extract_text(tmp_path)
        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No extractable text found in the uploaded file.",
            )
        chunks = chunk_text(text)
        index = DocumentIndex(chunks)
    finally:
        os.remove(tmp_path)

    _current_index["index"] = index
    _current_index["filename"] = file.filename

    return {
        "filename": file.filename,
        "num_chunks": len(chunks),
        "status": "indexed",
    }


@app.post("/api/v1/ask")
async def ask_question(req: AskRequest):
    if _current_index["index"] is None:
        raise HTTPException(
            status_code=400,
            detail="No document uploaded yet. Call /api/v1/upload first.",
        )

    result = answer_question(_current_index["index"], req.question, top_k=req.top_k)
    return {
        "filename": _current_index["filename"],
        "question": req.question,
        "response": result["response"],
        "chunks": result["chunks"],
    }


@app.get("/api/v1/status")
async def status():
    return {
        "document_loaded": _current_index["index"] is not None,
        "filename": _current_index["filename"],
    }