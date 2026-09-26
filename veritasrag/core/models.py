"""
Core data models for VeritasRAG.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class InferenceType(str, Enum):
    GROUNDED = "grounded"
    INFERRED = "inferred"
    HALLUCINATED = "hallucinated"
    CONTESTED = "contested"


class Chunk(BaseModel):
    chunk_id: str
    content: str
    source: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AtomicClaim(BaseModel):
    claim_id: Optional[str] = None
    claim_text: str
    parent_sentence_index: int
    grounding_score: float = 0.0
    inference_type: InferenceType = InferenceType.HALLUCINATED
    supporting_chunk_id: Optional[str] = None
    evidence_excerpt: Optional[str] = None


class SentenceOverlay(BaseModel):
    sentence_index: int
    sentence: str
    grounding_score: float
    inference_type: InferenceType
    cited_chunk_ids: List[str] = Field(default_factory=list)
    top_evidence_excerpt: Optional[str] = None
    atomic_claims: List[AtomicClaim] = Field(default_factory=list)
    confidence: float = 1.0


class VerificationResult(BaseModel):
    request_id: Optional[str] = None
    query: str
    rag_response: str
    overall_grounding_score: float
    overall_classification: str
    sentence_overlays: List[SentenceOverlay]
    processing_time_ms: float
    approaches_used: List[str] = Field(default_factory=list)
    model_metadata: Dict[str, str] = Field(default_factory=dict)
