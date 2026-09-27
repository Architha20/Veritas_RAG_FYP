"""
VeritasRAG Document QA & Hallucination Flagging Layer UI.
FastAPI web application with interactive grounding verification and approach selection.

Run:
    run_ui.bat
"""

import os
import re
import sys
import shutil
import tempfile
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Ensure root directory is on sys.path so we can import veritasrag
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from rag_pipeline import extract_text, chunk_text, DocumentIndex
from veritasrag import VeritasMiddleware, Chunk

app = FastAPI(title="VeritasRAG - Document QA & Grounding")

# Single in-memory index for the uploaded document
_current_index = {"index": None, "filename": None}

def _preload_sample_document():
    sample_file = os.path.join(os.path.dirname(__file__), "sample_doc.txt")
    if os.path.exists(sample_file):
        try:
            sample_text = extract_text(sample_file)
            chunks = chunk_text(sample_text)
            _current_index["index"] = DocumentIndex(chunks)
            _current_index["filename"] = "sample_doc.txt (Ibuprofen Clinical Pharmacology)"
            print("[INFO] Preloaded sample_doc.txt into active index.")
        except Exception as err:
            print(f"[WARN] Could not preload sample doc: {err}")

_preload_sample_document()

# Shared verification middleware instance
_middleware = VeritasMiddleware(default_mode="embedding")

INDEX_HTML_PATH = os.path.join(os.path.dirname(__file__), "index.html")


class AskRequest(BaseModel):
    question: str
    top_k: int = 3
    approach: str = "embedding"   # Web UI locked to Approach A. Use veritas_cli.py for B, C, hybrid.


def extract_grounded_answer(question: str, context_chunks: List[str]) -> str:
    """
    Synthesizes a clean, natural answer grounded strictly in the retrieved document chunks.
    Works 100% locally without requiring any external LLM or backend server.
    """
    if not context_chunks:
        return "I could not find sufficient information in the document to answer this question."

    # Extract valid sentences across the retrieved chunks
    sentences = []
    for chunk in context_chunks:
        for s in re.split(r"(?<=[.!?])\s+", chunk.strip()):
            s = s.strip()
            if len(s) > 15 and s not in sentences:
                sentences.append(s)

    if not sentences:
        return " ".join(context_chunks[:2])

    # Rank sentences by term overlap with query words
    stop_words = {
        "what", "is", "the", "of", "and", "in", "to", "for", "a", "an",
        "how", "who", "when", "where", "why", "does", "do", "are", "about",
        "tell", "me", "can", "you", "which", "give"
    }
    q_words = set(re.findall(r"\w+", question.lower())) - stop_words

    scored = []
    for s in sentences:
        s_words = set(re.findall(r"\w+", s.lower()))
        overlap = len(q_words & s_words)
        scored.append((overlap, s))

    scored.sort(key=lambda x: x[0], reverse=True)
    best_sentences = [s for score, s in scored[:2] if score > 0]
    if not best_sentences:
        best_sentences = sentences[:2]

    return " ".join(best_sentences)


@app.get("/", response_class=HTMLResponse)
async def home():
    if os.path.exists(INDEX_HTML_PATH):
        with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Veritas UI index.html not found</h1>"


@app.post("/api/v1/upload")
async def upload_document(file: UploadFile = File(...)):
    allowed_ext = (".pdf", ".docx", ".txt")
    if not file.filename.lower().endswith(allowed_ext):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {allowed_ext}",
        )

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
            detail="No document uploaded yet. Please upload a document first.",
        )

    # 1. Retrieve top-k semantic chunks from the document
    chunks = _current_index["index"].retrieve(req.question, top_k=req.top_k)

    # 2. Extract and synthesize the grounded answer directly from the document
    answer_text = extract_grounded_answer(req.question, chunks)

    # Web UI is strictly locked to Approach A (Embedding Similarity).
    # Approaches B, C, and Hybrid are tested through the Terminal CLI (veritas_cli.py).
    active_approach = "embedding"
    approach_display = "Approach A: Embedding Similarity (MiniLM)"

    # 3. Real-Time Verification using VeritasRAG Middleware (Approach A: Embedding)
    chunk_objs = [
        Chunk(chunk_id=f"chunk_{i+1}", content=c, source=_current_index["filename"])
        for i, c in enumerate(chunks)
    ]

    verif = _middleware.verify(
        query=req.question,
        response=answer_text,
        chunks=chunk_objs,
        mode=active_approach,
    )

    return {
        "filename": _current_index["filename"],
        "question": req.question,
        "response": answer_text,
        "chunks": chunks,
        "approach": active_approach,
        "approach_label": approach_display,
        "overall_grounding_score": round(verif.overall_grounding_score * 100, 1),
        "overall_classification": verif.overall_classification,
        "processing_time_ms": round(verif.processing_time_ms, 1),
        "sentence_overlays": [
            {
                "sentence": s.sentence,
                "inference_type": s.inference_type.value,
                "grounding_score": round(s.grounding_score * 100, 1),
                "cited_chunk_ids": s.cited_chunk_ids,
                "top_evidence_excerpt": s.top_evidence_excerpt,
            }
            for s in verif.sentence_overlays
        ],
    }


@app.get("/api/v1/status")
async def status():
    return {
        "document_loaded": _current_index["index"] is not None,
        "filename": _current_index["filename"],
    }