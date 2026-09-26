"""
VeritasRAG Middleware Orchestrator.
Main entry point for verifying RAG pipeline outputs.
"""

import time
import uuid
from typing import List, Optional, Union, Dict, Any

from .core.models import Chunk, SentenceOverlay, VerificationResult, InferenceType
from .core.splitter import SentenceSplitter
from .core.cache import ChunkEmbeddingCache
from .core.aggregator import ScoreAggregator
from .verifiers.embedding_verifier import EmbeddingVerifier
from .overlay.json_builder import JSONOverlayBuilder
from .overlay.html_renderer import HTMLOverlayRenderer


class VeritasMiddleware:
    """
    Main middleware layer for VeritasRAG.

    Example Usage:
        middleware = VeritasMiddleware()
        result = middleware.verify(
            query="What is the capital of France?",
            response="Paris is the capital of France. It has 2M people.",
            chunks=[Chunk(chunk_id="c1", content="Paris is the capital of France.")]
        )
        print(result.overall_grounding_score)
        html = middleware.to_html(result)
    """

    def __init__(
        self,
        default_mode: str = "embedding",
        cache: Optional[ChunkEmbeddingCache] = None,
        embedding_model_name: Optional[str] = None,
        nli_model_name: Optional[str] = None,
    ):
        self.default_mode = default_mode
        self.cache = cache or ChunkEmbeddingCache()
        self.splitter = SentenceSplitter()
        self.aggregator = ScoreAggregator()

        # Initialize Approach A
        kwargs_emb = {"cache": self.cache}
        if embedding_model_name is not None:
            kwargs_emb["model_name"] = embedding_model_name
        self.embedding_verifier = EmbeddingVerifier(**kwargs_emb)

        # Lazy load Approach B (NLI) on demand
        self._nli_model_name = nli_model_name
        self._nli_verifier = None
        self._atomic_verifier = None

    @property
    def nli_verifier(self):
        """Lazy load NLI verifier to optimize startup latency and memory."""
        if self._nli_verifier is None:
            from .verifiers.nli_verifier import NLIVerifier
            kwargs_nli = {}
            if self._nli_model_name is not None:
                kwargs_nli["model_name"] = self._nli_model_name
            self._nli_verifier = NLIVerifier(**kwargs_nli)
        return self._nli_verifier

    @property
    def atomic_verifier(self):
        """Lazy load Approach C Atomic Verifier."""
        if self._atomic_verifier is None:
            from .verifiers.atomic_verifier import AtomicVerifier
            self._atomic_verifier = AtomicVerifier(nli_verifier=self.nli_verifier)
        return self._atomic_verifier

    def verify(
        self,
        query: str,
        response: str,
        chunks: List[Union[Chunk, Dict[str, Any]]],
        mode: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> VerificationResult:
        """
        Executes end-to-end grounding verification on a RAG response.
        """
        start_time = time.time()
        req_id = request_id or str(uuid.uuid4())
        active_mode = mode or self.default_mode

        # Normalize chunks to Chunk Pydantic instances if raw dicts passed
        normalized_chunks: List[Chunk] = []
        for c in chunks:
            if isinstance(c, Chunk):
                normalized_chunks.append(c)
            elif isinstance(c, dict):
                normalized_chunks.append(Chunk(**c))

        # 1. Split RAG response into discrete sentences
        sentences = self.splitter.split(response)
        if not sentences:
            elapsed = (time.time() - start_time) * 1000
            return VerificationResult(
                request_id=req_id,
                query=query,
                rag_response=response,
                overall_grounding_score=0.0,
                overall_classification="empty_response",
                sentence_overlays=[],
                processing_time_ms=round(elapsed, 2),
                approaches_used=[],
            )

        # 2. Run verification based on active mode
        approaches_used = []

        if active_mode == "embedding":
            overlays = self.embedding_verifier.verify(sentences, normalized_chunks)
            approaches_used.append(self.embedding_verifier.name)

        elif active_mode == "nli":
            overlays = self.nli_verifier.verify(sentences, normalized_chunks)
            approaches_used.append(self.nli_verifier.name)

        elif active_mode == "ensemble":
            overlays_emb = self.embedding_verifier.verify(sentences, normalized_chunks)
            overlays_nli = self.nli_verifier.verify(sentences, normalized_chunks)
            overlays = self.aggregator.ensemble_sentences(overlays_emb, overlays_nli)
            approaches_used.extend([self.embedding_verifier.name, self.nli_verifier.name])

        elif active_mode == "atomic":
            overlays = self.atomic_verifier.verify(sentences, normalized_chunks)
            approaches_used.append(self.atomic_verifier.name)

        elif active_mode in ("hybrid", "sota"):
            # SOTA Hybrid: Macro NLI Cross-Encoder + Micro Atomic Fact Entailment + Entity Guard
            overlays_nli = self.nli_verifier.verify(sentences, normalized_chunks)
            overlays_atomic = self.atomic_verifier.verify(sentences, normalized_chunks)
            overlays = self.aggregator.ensemble_sentences(overlays_nli, overlays_atomic)
            approaches_used.extend(["nli_cross_encoder", "atomic_fact_entailment", "neuro_symbolic_entity_guard"])

        else:
            raise ValueError(
                f"Unknown verification mode '{active_mode}'. Supported: embedding, nli, ensemble, atomic, hybrid"
            )

        # 3. Compute overall grounding score and classification
        overall_score, classification = self.aggregator.compute_overall(overlays)
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return VerificationResult(
            request_id=req_id,
            query=query,
            rag_response=response,
            overall_grounding_score=overall_score,
            overall_classification=classification,
            sentence_overlays=overlays,
            processing_time_ms=elapsed_ms,
            approaches_used=approaches_used,
            model_metadata={
                "embedding_model": self.embedding_verifier.model_name,
                "mode": active_mode,
            },
        )

    @staticmethod
    def to_json(result: VerificationResult, indent: int = 2) -> str:
        return JSONOverlayBuilder.to_json(result, indent=indent)

    @staticmethod
    def to_html(result: VerificationResult) -> str:
        return HTMLOverlayRenderer.render(result)

    @staticmethod
    def save_html(result: VerificationResult, file_path: str) -> None:
        html = HTMLOverlayRenderer.render(result)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
