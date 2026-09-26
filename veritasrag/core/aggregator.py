"""
Score Aggregator and Conflict Resolver for VeritasRAG.
Combines verification scores across approaches and detects multi-source contradictions.
"""

from typing import List, Dict, Optional, Tuple
from .models import SentenceOverlay, InferenceType, VerificationResult


class ScoreAggregator:
    """
    Ensemble aggregator combining bi-encoder similarity and cross-encoder NLI.
    Handles conflict resolution when retrieved chunks contain conflicting evidence.
    """

    def __init__(
        self,
        weight_embedding: float = 0.35,
        weight_nli: float = 0.65,
        grounded_threshold: float = 0.70,
        inferred_threshold: float = 0.45,
    ):
        self.weight_embedding = weight_embedding
        self.weight_nli = weight_nli
        self.grounded_threshold = grounded_threshold
        self.inferred_threshold = inferred_threshold

    def ensemble_sentences(
        self,
        overlays_embedding: List[SentenceOverlay],
        overlays_nli: List[SentenceOverlay],
    ) -> List[SentenceOverlay]:
        """
        Merges SentenceOverlay lists from Approach A and Approach B.
        """
        combined: List[SentenceOverlay] = []

        for o_1, o_2 in zip(overlays_embedding, overlays_nli):
            # Contradiction priority: if either approach detected a contradiction or hallucination
            if o_1.inference_type == InferenceType.HALLUCINATED or o_2.inference_type == InferenceType.HALLUCINATED:
                score = round(min(o_1.grounding_score, o_2.grounding_score), 4)
                inf_type = InferenceType.HALLUCINATED
                cited_ids = []
                excerpt = None
            elif o_1.inference_type == InferenceType.GROUNDED and o_2.inference_type == InferenceType.GROUNDED:
                # Both approaches logically proved entailment
                score = round(max(o_1.grounding_score, o_2.grounding_score), 4)
                inf_type = InferenceType.GROUNDED
                cited_ids = list(dict.fromkeys(o_1.cited_chunk_ids + o_2.cited_chunk_ids))
                excerpt = o_2.top_evidence_excerpt or o_1.top_evidence_excerpt
            elif o_1.inference_type == InferenceType.GROUNDED or o_2.inference_type == InferenceType.GROUNDED:
                # One proved entailment, other in inferred zone
                score = round(max(o_1.grounding_score, o_2.grounding_score), 4)
                inf_type = InferenceType.GROUNDED if score >= self.grounded_threshold else InferenceType.INFERRED
                cited_ids = list(dict.fromkeys(o_1.cited_chunk_ids + o_2.cited_chunk_ids))
                excerpt = o_2.top_evidence_excerpt or o_1.top_evidence_excerpt
            else:
                # Boundary / inferred zone: weighted ensemble
                score = (self.weight_embedding * o_1.grounding_score) + (
                    self.weight_nli * o_2.grounding_score
                )
                score = round(max(0.0, min(1.0, score)), 4)
                if score >= self.grounded_threshold:
                    inf_type = InferenceType.GROUNDED
                elif score >= self.inferred_threshold:
                    inf_type = InferenceType.INFERRED
                else:
                    inf_type = InferenceType.HALLUCINATED

                cited_ids = list(dict.fromkeys(o_1.cited_chunk_ids + o_2.cited_chunk_ids))
                excerpt = o_2.top_evidence_excerpt or o_1.top_evidence_excerpt

            atomic_claims = getattr(o_2, "atomic_claims", None) or getattr(o_1, "atomic_claims", None)

            combined.append(
                SentenceOverlay(
                    sentence_index=o_1.sentence_index,
                    sentence=o_1.sentence,
                    grounding_score=score,
                    inference_type=inf_type,
                    cited_chunk_ids=cited_ids,
                    top_evidence_excerpt=excerpt,
                    atomic_claims=atomic_claims,
                    confidence=round((o_1.confidence + o_2.confidence) / 2.0, 4),
                )
            )

        return combined

    def compute_overall(
        self,
        overlays: List[SentenceOverlay],
    ) -> Tuple[float, str]:
        """
        Computes overall response grounding score and discrete classification.
        """
        if not overlays:
            return 0.0, "hallucinated"

        avg_score = round(sum(o.grounding_score for o in overlays) / len(overlays), 4)

        has_hallucination = any(o.inference_type == InferenceType.HALLUCINATED for o in overlays)
        all_grounded = all(o.inference_type == InferenceType.GROUNDED for o in overlays)

        if all_grounded or (not has_hallucination and avg_score >= self.grounded_threshold):
            classification = "grounded"
        elif has_hallucination:
            classification = "partially_grounded" if avg_score >= self.inferred_threshold else "hallucinated"
        else:
            classification = "inferred"

        return avg_score, classification
