"""
Approach A: Embedding-Based Cosine Similarity Grounding Verifier.
Uses SentenceTransformers (all-MiniLM-L6-v2) for ultra-fast bi-encoder matching.
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer

from .base import BaseVerifier
from ..core.models import Chunk, SentenceOverlay, InferenceType
from ..core.cache import ChunkEmbeddingCache

LOCAL_MINILM_PATH = Path(__file__).resolve().parent.parent.parent / "models" / "all-MiniLM-L6-v2"
DEFAULT_MINILM_MODEL = str(LOCAL_MINILM_PATH) if LOCAL_MINILM_PATH.exists() else "all-MiniLM-L6-v2"


class EmbeddingVerifier(BaseVerifier):
    """
    Approach A: Encodes sentences and chunks into dense vectors,
    calculates cosine similarity, and maps scores to grounding categories.
    """

    DEFAULT_MODEL = DEFAULT_MINILM_MODEL
    THRESHOLD_GROUNDED = 0.75
    THRESHOLD_INFERRED = 0.50

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        cache: Optional[ChunkEmbeddingCache] = None,
        threshold_grounded: float = THRESHOLD_GROUNDED,
        threshold_inferred: float = THRESHOLD_INFERRED,
    ):
        self._model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.cache = cache or ChunkEmbeddingCache()
        self.threshold_grounded = threshold_grounded
        self.threshold_inferred = threshold_inferred

    @property
    def name(self) -> str:
        return "embedding_similarity"

    @property
    def model_name(self) -> str:
        return self._model_name

    def _cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Compute cosine similarity between two 1D numpy vectors."""
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))

    def _classify(self, score: float) -> InferenceType:
        if score >= self.threshold_grounded:
            return InferenceType.GROUNDED
        elif score >= self.threshold_inferred:
            return InferenceType.INFERRED
        else:
            return InferenceType.HALLUCINATED

    def _extract_excerpt(self, chunk_content: str, max_chars: int = 120) -> str:
        """Extract a representative evidence snippet from chunk text."""
        cleaned = " ".join(chunk_content.split())
        if len(cleaned) <= max_chars:
            return cleaned
        return cleaned[:max_chars].rstrip() + "..."

    def verify(
        self,
        sentences: List[str],
        chunks: List[Chunk],
    ) -> List[SentenceOverlay]:
        """
        Verify each sentence against all candidate chunks.
        """
        if not sentences:
            return []

        if not chunks:
            # If no context was retrieved, all sentences are hallucinated/unsupported
            return [
                SentenceOverlay(
                    sentence_index=idx,
                    sentence=s,
                    grounding_score=0.0,
                    inference_type=InferenceType.HALLUCINATED,
                    cited_chunk_ids=[],
                    top_evidence_excerpt=None,
                    confidence=1.0,
                )
                for idx, s in enumerate(sentences)
            ]

        # 1. Compute or retrieve chunk embeddings
        chunk_embeddings: List[Tuple[Chunk, np.ndarray]] = []
        for chunk in chunks:
            cached_emb = self.cache.get(chunk.content, self._model_name)
            if cached_emb is None:
                emb = self.model.encode(chunk.content, convert_to_numpy=True)
                self.cache.set(chunk.content, self._model_name, emb)
            else:
                emb = cached_emb
            chunk_embeddings.append((chunk, emb))

        # 2. Batch encode all sentences
        sentence_embeddings = self.model.encode(sentences, convert_to_numpy=True)

        overlays: List[SentenceOverlay] = []

        for idx, (sentence, s_emb) in enumerate(zip(sentences, sentence_embeddings)):
            best_score = -1.0
            best_chunk: Optional[Chunk] = None

            for chunk, c_emb in chunk_embeddings:
                sim = self._cosine_similarity(s_emb, c_emb)
                if sim > best_score:
                    best_score = sim
                    best_chunk = chunk

            best_score = max(0.0, min(1.0, float(best_score)))
            inf_type = self._classify(best_score)

            if inf_type == InferenceType.HALLUCINATED:
                cited_ids = []
                excerpt = None
            else:
                cited_ids = [best_chunk.chunk_id] if best_chunk else []
                excerpt = self._extract_excerpt(best_chunk.content) if best_chunk else None

            overlays.append(
                SentenceOverlay(
                    sentence_index=idx,
                    sentence=sentence,
                    grounding_score=round(best_score, 4),
                    inference_type=inf_type,
                    cited_chunk_ids=cited_ids,
                    top_evidence_excerpt=excerpt,
                    confidence=round(best_score if inf_type == InferenceType.GROUNDED else (1.0 - best_score), 4),
                )
            )

        return overlays
