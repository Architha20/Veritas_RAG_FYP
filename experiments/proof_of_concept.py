"""
VeritasRAG — Proof of Concept
Approach A: Embedding-Based Cosine Similarity Grounding Verifier

Requirements:
    pip install sentence-transformers spacy
    python -m spacy download en_core_web_sm

Run:
    python proof_of_concept.py
"""

import time
import json
from dataclasses import dataclass, field, asdict
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer
import spacy


# ─────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────

@dataclass
class Chunk:
    chunk_id: str
    content: str
    source: str = ""


@dataclass
class SentenceOverlay:
    sentence_index: int
    sentence: str
    grounding_score: float
    inference_type: str          # "grounded" | "inferred" | "hallucinated"
    top_chunk_id: Optional[str]
    evidence_excerpt: Optional[str]
    emoji: str = ""

    def __post_init__(self):
        self.emoji = {"grounded": "🟢", "inferred": "🟡", "hallucinated": "🔴"}.get(
            self.inference_type, "⚪"
        )


@dataclass
class VerificationResult:
    query: str
    rag_response: str
    overall_grounding_score: float
    overall_classification: str
    sentence_overlays: List[SentenceOverlay]
    processing_time_ms: float
    model_used: str


# ─────────────────────────────────────────────
# Core Components
# ─────────────────────────────────────────────

class SentenceSplitter:
    """
    Component ①: Splits RAG response into individual sentences using spaCy.
    """

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def split(self, text: str) -> List[str]:
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        return sentences


class EmbeddingVerifier:
    """
    Component ③ — Approach A: Embedding-Based Cosine Similarity Grounding Verifier.

    For each sentence in the RAG response:
      1. Encode the sentence into a vector using all-MiniLM-L6-v2.
      2. Compute cosine similarity against each retrieved chunk's embedding.
      3. Take the maximum similarity score across all chunks.
      4. Classify based on configurable thresholds.
    """

    THRESHOLD_GROUNDED = 0.75   # ≥ this → grounded
    THRESHOLD_INFERRED = 0.50   # ≥ this (< grounded) → inferred
                                # < this → hallucinated

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"[VeritasRAG] Loading embedding model: {model_name} ...")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        print(f"[VeritasRAG] Model loaded. ✓")

    def _cosine_similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        dot = np.dot(vec_a, vec_b)
        norm = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
        return float(dot / norm) if norm > 0 else 0.0

    def _classify(self, score: float) -> str:
        if score >= self.THRESHOLD_GROUNDED:
            return "grounded"
        elif score >= self.THRESHOLD_INFERRED:
            return "inferred"
        else:
            return "hallucinated"

    def verify(
        self,
        sentences: List[str],
        chunks: List[Chunk],
    ) -> List[SentenceOverlay]:
        """
        Verify each sentence against the retrieved chunks.
        Returns a list of SentenceOverlay objects.
        """

        # Pre-compute chunk embeddings (in production, these come from Redis cache)
        chunk_embeddings = {
            chunk.chunk_id: self.model.encode(chunk.content, convert_to_numpy=True)
            for chunk in chunks
        }

        overlays: List[SentenceOverlay] = []

        for idx, sentence in enumerate(sentences):
            # Encode the sentence
            sentence_embedding = self.model.encode(sentence, convert_to_numpy=True)

            # Compute cosine similarity against every chunk
            best_score = 0.0
            best_chunk_id = None
            best_excerpt = None

            for chunk in chunks:
                sim = self._cosine_similarity(sentence_embedding, chunk_embeddings[chunk.chunk_id])
                if sim > best_score:
                    best_score = sim
                    best_chunk_id = chunk.chunk_id
                    # Extract short evidence excerpt (first 80 chars of the chunk)
                    best_excerpt = chunk.content[:80].strip() + "..."

            inference_type = self._classify(best_score)

            # If hallucinated, there's no supporting chunk
            if inference_type == "hallucinated":
                best_chunk_id = None
                best_excerpt = None

            overlays.append(
                SentenceOverlay(
                    sentence_index=idx,
                    sentence=sentence,
                    grounding_score=round(best_score, 3),
                    inference_type=inference_type,
                    top_chunk_id=best_chunk_id,
                    evidence_excerpt=best_excerpt,
                )
            )

        return overlays


class OverlayGenerator:
    """
    Component ⑤: Generates human-readable and machine-readable overlays.
    """

    @staticmethod
    def generate_terminal_output(result: VerificationResult) -> str:
        lines = []
        lines.append("\n" + "=" * 60)
        lines.append("  VeritasRAG — Proof of Concept Results")
        lines.append("=" * 60)
        lines.append(f"\nQuery: {result.query}\n")
        lines.append("-" * 60)

        for overlay in result.sentence_overlays:
            lines.append(f'\nSentence {overlay.sentence_index + 1}: "{overlay.sentence}"')
            lines.append(f"  ├─ Score      : {overlay.grounding_score:.2f}")
            lines.append(f"  ├─ Label      : {overlay.emoji} {overlay.inference_type.upper()}")
            if overlay.top_chunk_id:
                lines.append(f"  └─ Top Chunk  : {overlay.top_chunk_id} (evidence: \"{overlay.evidence_excerpt}\")")
            else:
                lines.append(f"  └─ Top Chunk  : None — no supporting evidence found")

        lines.append("\n" + "-" * 60)
        lines.append(f"Overall Grounding Score : {result.overall_grounding_score:.2f}")
        lines.append(f"Classification          : {result.overall_classification.replace('_', ' ').title()}")
        lines.append(f"Sentences Analyzed      : {len(result.sentence_overlays)}")

        hallucinated_count = sum(
            1 for o in result.sentence_overlays if o.inference_type == "hallucinated"
        )
        inferred_count = sum(
            1 for o in result.sentence_overlays if o.inference_type == "inferred"
        )
        grounded_count = sum(
            1 for o in result.sentence_overlays if o.inference_type == "grounded"
        )

        lines.append(f"  🟢 Grounded   : {grounded_count}")
        lines.append(f"  🟡 Inferred   : {inferred_count}")
        lines.append(f"  🔴 Hallucinated: {hallucinated_count}")
        lines.append(f"Processing Time         : {result.processing_time_ms:.0f}ms")
        lines.append(f"Model Used              : {result.model_used}")
        lines.append("=" * 60 + "\n")

        return "\n".join(lines)

    @staticmethod
    def generate_json(result: VerificationResult) -> str:
        """Returns JSON overlay — this is the machine-readable API output."""
        output = {
            "query": result.query,
            "overall_grounding_score": result.overall_grounding_score,
            "overall_classification": result.overall_classification,
            "processing_time_ms": result.processing_time_ms,
            "model_used": result.model_used,
            "sentence_overlays": [
                {
                    "sentence_index": o.sentence_index,
                    "sentence": o.sentence,
                    "grounding_score": o.grounding_score,
                    "inference_type": o.inference_type,
                    "top_chunk_id": o.top_chunk_id,
                    "evidence_excerpt": o.evidence_excerpt,
                }
                for o in result.sentence_overlays
            ],
        }
        return json.dumps(output, indent=2)

    @staticmethod
    def generate_html(result: VerificationResult) -> str:
        """Returns a color-coded HTML overlay."""
        color_map = {
            "grounded": "#d4edda",    # green
            "inferred": "#fff3cd",    # yellow
            "hallucinated": "#f8d7da", # red
        }
        border_map = {
            "grounded": "#28a745",
            "inferred": "#ffc107",
            "hallucinated": "#dc3545",
        }
        emoji_map = {"grounded": "🟢", "inferred": "🟡", "hallucinated": "🔴"}

        sentences_html = ""
        for o in result.sentence_overlays:
            bg = color_map[o.inference_type]
            border = border_map[o.inference_type]
            emoji = emoji_map[o.inference_type]
            cite = f"<br/><small style='color:#666'>↳ Source: {o.top_chunk_id} — \"{o.evidence_excerpt}\"</small>" if o.top_chunk_id else "<br/><small style='color:#dc3545'>↳ ⚠️ No supporting evidence found</small>"
            sentences_html += f"""
        <div style='margin:8px 0; padding:10px 14px; border-left:4px solid {border}; background:{bg}; border-radius:4px; font-family:sans-serif;'>
            {emoji} <strong>{o.sentence}</strong> <span style='color:#555; font-size:0.85em;'>[Score: {o.grounding_score:.2f}]</span>
            {cite}
        </div>"""

        html = f"""<!DOCTYPE html>
<html>
<head><title>VeritasRAG — Grounding Overlay</title></head>
<body style='max-width:800px; margin:40px auto; font-family:sans-serif;'>
    <h2>VeritasRAG Grounding Overlay</h2>
    <p><strong>Query:</strong> {result.query}</p>
    <p><strong>Overall Score:</strong> {result.overall_grounding_score:.2f} — <em>{result.overall_classification.replace('_', ' ').title()}</em></p>
    <hr/>
    <h3>Sentence-Level Analysis</h3>
    {sentences_html}
    <hr/>
    <p style='color:#888; font-size:0.85em;'>Processed in {result.processing_time_ms:.0f}ms using {result.model_used}</p>
</body>
</html>"""
        return html


# ─────────────────────────────────────────────
# VeritasRAG Middleware (Main Orchestrator)
# ─────────────────────────────────────────────

class VeritasMiddleware:
    """
    Main VeritasRAG middleware orchestrator.

    Usage:
        veritas = VeritasMiddleware()
        result = veritas.verify(query=query, response=rag_response, chunks=chunks)
    """

    def __init__(self):
        self.splitter = SentenceSplitter()
        self.verifier = EmbeddingVerifier()
        self.overlay_gen = OverlayGenerator()

    def _compute_overall_score(self, overlays: List[SentenceOverlay]) -> tuple:
        if not overlays:
            return 0.0, "hallucinated"
        avg_score = round(sum(o.grounding_score for o in overlays) / len(overlays), 3)
        if avg_score >= EmbeddingVerifier.THRESHOLD_GROUNDED:
            classification = "grounded"
        elif avg_score >= EmbeddingVerifier.THRESHOLD_INFERRED:
            classification = "partially_grounded"
        else:
            classification = "hallucinated"
        return avg_score, classification

    def verify(self, query: str, response: str, chunks: List[Chunk]) -> VerificationResult:
        """Full verification pipeline."""
        start = time.time()

        # ① Split into sentences
        sentences = self.splitter.split(response)

        # ③ Verify each sentence (Approach A)
        overlays = self.verifier.verify(sentences, chunks)

        # ④ Aggregate
        overall_score, classification = self._compute_overall_score(overlays)

        elapsed_ms = round((time.time() - start) * 1000, 1)

        return VerificationResult(
            query=query,
            rag_response=response,
            overall_grounding_score=overall_score,
            overall_classification=classification,
            sentence_overlays=overlays,
            processing_time_ms=elapsed_ms,
            model_used=self.verifier.model_name,
        )


# ─────────────────────────────────────────────
# Demo: Run the PoC
# ─────────────────────────────────────────────

def run_demo():
    print("\n[VeritasRAG] Initializing Proof of Concept...")

    # ── Sample RAG scenario ──────────────────────────────────────────────────

    QUERY = "What is the capital of France and what is its population?"

    RAG_RESPONSE = (
        "Paris is the capital of France. "
        "It has a population of approximately 2.1 million in the city proper. "
        "The city was founded by the Romans in the 3rd century BC."
    )

    CHUNKS = [
        Chunk(
            chunk_id="chunk_001",
            content="Paris, the capital city of France, is located on the Seine River. "
                    "The city proper has a population of about 2.16 million as of the 2021 census.",
            source="france_demographics.pdf (p.12)",
        ),
        Chunk(
            chunk_id="chunk_002",
            content="France is a country in Western Europe. Its capital is Paris, "
                    "which is also the largest city in the country.",
            source="europe_geography.pdf (p.5)",
        ),
    ]

    # ── Run verification ─────────────────────────────────────────────────────

    middleware = VeritasMiddleware()
    result = middleware.verify(query=QUERY, response=RAG_RESPONSE, chunks=CHUNKS)

    # ── Output: Terminal ─────────────────────────────────────────────────────

    print(OverlayGenerator.generate_terminal_output(result))

    # ── Output: JSON ─────────────────────────────────────────────────────────

    json_output = OverlayGenerator.generate_json(result)
    with open("veritasrag_output.json", "w") as f:
        f.write(json_output)
    print("[VeritasRAG] JSON overlay saved → veritasrag_output.json")

    # ── Output: HTML ─────────────────────────────────────────────────────────

    html_output = OverlayGenerator.generate_html(result)
    with open("veritasrag_overlay.html", "w") as f:
        f.write(html_output)
    print("[VeritasRAG] HTML overlay saved → veritasrag_overlay.html")
    print("[VeritasRAG] Open veritasrag_overlay.html in a browser to see the color-coded output.\n")

    # ── Second demo: Medical scenario (more risk) ────────────────────────────

    print("\n" + "=" * 60)
    print("  DEMO 2: Medical Scenario")
    print("=" * 60)

    QUERY_2 = "What is the recommended dosage of ibuprofen for adults?"

    RAG_RESPONSE_2 = (
        "The standard adult dose of ibuprofen is 200-400mg every 4-6 hours. "
        "The maximum daily dose should not exceed 1200mg without medical supervision. "
        "Ibuprofen was originally developed in the 1950s by Dr. Andrew Jack."
    )

    CHUNKS_2 = [
        Chunk(
            chunk_id="med_chunk_001",
            content="For adults, ibuprofen is typically taken at 200 to 400 mg per dose, "
                    "every 4 to 6 hours as needed. The maximum OTC daily dose is 1200 mg.",
            source="drug_formulary.pdf (p.88)",
        ),
    ]

    result_2 = middleware.verify(query=QUERY_2, response=RAG_RESPONSE_2, chunks=CHUNKS_2)
    print(OverlayGenerator.generate_terminal_output(result_2))

    html_output_2 = OverlayGenerator.generate_html(result_2)
    with open("veritasrag_medical_overlay.html", "w") as f:
        f.write(html_output_2)
    print("[VeritasRAG] Medical HTML overlay saved → veritasrag_medical_overlay.html\n")


if __name__ == "__main__":
    run_demo()
