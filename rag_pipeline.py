"""
Minimal RAG pipeline: upload a document, ask questions, get an answer
grounded in that document.

Requires Ollama running locally (https://ollama.com):
    ollama pull llama3.2:3b
"""

import re
import requests
import numpy as np
import spacy
from sentence_transformers import SentenceTransformer

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"

_embed_model = None
_nlp = None


def get_embed_model():
    global _embed_model
    if _embed_model is None:
        print("Loading embedding model...")
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embed_model


def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def extract_text(file_path):
    """Extract raw text from a PDF, DOCX, or TXT file."""
    if file_path.lower().endswith(".pdf"):
        import pdfplumber
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)

    elif file_path.lower().endswith(".docx"):
        import docx
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    elif file_path.lower().endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    else:
        raise ValueError(f"Unsupported file type: {file_path}")


def chunk_text(text, sentences_per_chunk=3, overlap=1):
    """Split text into overlapping chunks of a few sentences each."""
    nlp = get_nlp()
    text = re.sub(r"\s+", " ", text).strip()
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    chunks = []
    step = max(1, sentences_per_chunk - overlap)
    for i in range(0, len(sentences), step):
        chunk = " ".join(sentences[i:i + sentences_per_chunk])
        if chunk:
            chunks.append(chunk)
        if i + sentences_per_chunk >= len(sentences):
            break
    return chunks


class DocumentIndex:
    """In-memory embedding index for one document's chunks."""

    def __init__(self, chunks):
        self.chunks = chunks
        model = get_embed_model()
        self.embeddings = model.encode(chunks)

    def retrieve(self, question, top_k=3):
        model = get_embed_model()
        q_emb = model.encode(question)
        sims = model.similarity(q_emb, self.embeddings)[0]
        top_idx = np.argsort(-np.array(sims))[:top_k]
        return [self.chunks[i] for i in top_idx]


def generate_answer(question, context_chunks):
    """Call local Ollama LLM, grounded strictly in the retrieved chunks."""
    context = "\n\n".join(f"- {c}" for c in context_chunks)
    prompt = (
        "Answer the question using ONLY the information in the context below. "
        "If the context doesn't contain the answer, say so - do not use outside knowledge.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )

    response = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def answer_question(index, question, top_k=3):
    """Full pipeline: retrieve relevant chunks, generate a grounded answer."""
    chunks = index.retrieve(question, top_k=top_k)
    answer = generate_answer(question, chunks)
    return {"response": answer, "chunks": chunks}