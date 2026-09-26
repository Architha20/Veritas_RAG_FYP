"""
FastAPI REST API Server for VeritasRAG Middleware.
Provides endpoints for real-time verification and visual overlay retrieval.
"""

from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from ..middleware import VeritasMiddleware
from ..core.models import Chunk, VerificationResult


# Input schemas for the API
class VerifyRequest(BaseModel):
    query: str = Field(..., example="What is the capital of France?")
    response: str = Field(
        ...,
        example="Paris is the capital of France. It has 2.1 million people. The city was founded in 1980.",
    )
    chunks: List[Chunk] = Field(
        ...,
        example=[
            {
                "chunk_id": "chunk_01",
                "content": "Paris is the capital and most populous city of France, with about 2.16 million residents.",
                "source": "france_geography.pdf",
            }
        ],
    )
    mode: Optional[str] = Field("embedding", description="'embedding', 'nli', or 'ensemble'")


# Initialize FastAPI app
app = FastAPI(
    title="VeritasRAG Middleware API",
    description="Real-Time Hallucination-Flagging Middleware Layer for Retrieval-Augmented Generation (RAG) Pipelines",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global middleware instance
middleware = VeritasMiddleware()


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "VeritasRAG",
        "version": "0.1.0",
        "models": {
            "embedding": middleware.embedding_verifier.model_name,
        },
    }


@app.post("/api/v1/verify", response_model=VerificationResult)
def verify_rag_output(req: VerifyRequest):
    """
    Submits a RAG response and retrieved chunks for real-time grounding analysis.
    Returns structured JSON with sentence-level grounding scores, classifications,
    and cited chunk IDs.
    """
    try:
        result = middleware.verify(
            query=req.query,
            response=req.response,
            chunks=req.chunks,
            mode=req.mode,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/verify/html", response_class=HTMLResponse)
def verify_rag_output_html(req: VerifyRequest):
    """
    Returns an interactive, color-coded HTML overlay for direct rendering
    in browser iframes or web dashboards.
    """
    try:
        result = middleware.verify(
            query=req.query,
            response=req.response,
            chunks=req.chunks,
            mode=req.mode,
        )
        return HTMLResponse(content=middleware.to_html(result))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
