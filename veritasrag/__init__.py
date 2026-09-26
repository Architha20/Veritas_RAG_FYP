"""
VeritasRAG: Real-Time Hallucination-Flagging Middleware Layer for RAG Pipelines.
"""

from .middleware import VeritasMiddleware
from .core.models import (
    Chunk,
    SentenceOverlay,
    AtomicClaim,
    VerificationResult,
    InferenceType,
)

__version__ = "0.1.0"

__all__ = [
    "VeritasMiddleware",
    "Chunk",
    "SentenceOverlay",
    "AtomicClaim",
    "VerificationResult",
    "InferenceType",
]
