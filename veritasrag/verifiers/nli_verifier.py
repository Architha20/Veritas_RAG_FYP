"""
Approach B: Cross-Encoder Natural Language Inference (NLI) Verifier.
Uses DeBERTa-v3-MNLI cross-encoders to evaluate logical entailment,
neutrality, and contradiction between retrieved chunks (premises) and
generated sentences (hypotheses).
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple, Dict
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from .base import BaseVerifier
from ..core.models import Chunk, SentenceOverlay, InferenceType

LOCAL_DEBERTA_PATH = Path(__file__).resolve().parent.parent.parent / "models" / "nli-deberta-v3-base"
DEFAULT_DEBERTA_MODEL = str(LOCAL_DEBERTA_PATH) if LOCAL_DEBERTA_PATH.exists() else "cross-encoder/nli-deberta-v3-base"


class NLIVerifier(BaseVerifier):
    """
    Approach B: Evaluates factual entailment using cross-encoder NLI.
    Captures logical contradictions, negations, and nuanced factual claims
    that pure bi-encoders miss.
    """

    DEFAULT_MODEL = DEFAULT_DEBERTA_MODEL

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: Optional[str] = None,
        threshold_grounded: float = 0.70,
        threshold_contradiction: float = 0.50,
    ):
        self._model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.threshold_grounded = threshold_grounded
        self.threshold_contradiction = threshold_contradiction

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

        # Extract label mappings (entailment, neutral, contradiction)
        id2label = self.model.config.id2label
        self.label2id = {label.lower(): idx for idx, label in id2label.items()}
        # Normalize labels
        self.entail_idx = self._find_label_index(["entailment"])
        self.neutral_idx = self._find_label_index(["neutral"])
        self.contradict_idx = self._find_label_index(["contradiction"])

    def _find_label_index(self, candidates: List[str]) -> int:
        for idx, label in self.model.config.id2label.items():
            for c in candidates:
                if c in label.lower():
                    return idx
        return 0

    @property
    def name(self) -> str:
        return "nli_cross_encoder"

    @property
    def model_name(self) -> str:
        return self._model_name

    def _predict_pairs(
        self,
        pairs: List[Tuple[str, str]],
        batch_size: int = 16,
    ) -> np.ndarray:
        """
        Runs cross-encoder NLI inference on (premise, hypothesis) pairs.
        Returns softmax probabilities of shape (N, num_labels).
        """
        if not pairs:
            return np.empty((0, 3))

        all_probs: List[np.ndarray] = []

        with torch.no_grad():
            for i in range(0, len(pairs), batch_size):
                batch_pairs = pairs[i : i + batch_size]
                premises = [p[0] for p in batch_pairs]
                hypotheses = [p[1] for p in batch_pairs]

                inputs = self.tokenizer(
                    premises,
                    hypotheses,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="pt",
                ).to(self.device)

                logits = self.model(**inputs).logits
                probs = torch.softmax(logits, dim=-1).cpu().numpy()
                all_probs.append(probs)

        return np.vstack(all_probs)

    def _extract_excerpt(self, chunk_content: str, max_chars: int = 120) -> str:
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
        For each sentence, check NLI entailment against each chunk.
        """
        if not sentences:
            return []

        if not chunks:
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

        # Build cross pairs: (chunk.content, sentence)
        pairs: List[Tuple[str, str]] = []
        pair_map: List[Tuple[int, Chunk]] = []  # (sentence_idx, chunk)

        for s_idx, sentence in enumerate(sentences):
            for chunk in chunks:
                pairs.append((chunk.content, sentence))
                pair_map.append((s_idx, chunk))

        # Run inference
        probs = self._predict_pairs(pairs)

        # Aggregate results per sentence
        overlays: List[SentenceOverlay] = []

        for s_idx, sentence in enumerate(sentences):
            # Find all pair predictions for this sentence
            indices = [i for i, (idx, _) in enumerate(pair_map) if idx == s_idx]

            best_chunk_score = -1.0
            best_entailment = 0.0
            max_contradiction = 0.0
            best_chunk: Optional[Chunk] = None
            direct_contradiction = False

            for i in indices:
                p_entail = float(probs[i, self.entail_idx])
                p_neutral = float(probs[i, self.neutral_idx])
                p_contra = float(probs[i, self.contradict_idx])
                chunk = pair_map[i][1]

                if p_contra > max_contradiction:
                    max_contradiction = p_contra

                # Net support from this specific chunk
                chunk_score = p_entail * (1.0 - p_contra)
                if chunk_score > best_chunk_score:
                    best_chunk_score = chunk_score
                    best_entailment = p_entail
                    best_chunk = chunk

                # Check if this chunk directly contradicts the claim
                if p_contra >= self.threshold_contradiction and p_entail < 0.25:
                    direct_contradiction = True

            grounding_score = max(0.0, min(1.0, best_chunk_score))

            # Classify
            if (direct_contradiction and best_entailment < 0.50) or grounding_score < 0.35:
                inf_type = InferenceType.HALLUCINATED
                cited_ids = []
                excerpt = None
            elif grounding_score >= self.threshold_grounded:
                inf_type = InferenceType.GROUNDED
                cited_ids = [best_chunk.chunk_id] if best_chunk else []
                excerpt = self._extract_excerpt(best_chunk.content) if best_chunk else None
            else:
                inf_type = InferenceType.INFERRED
                cited_ids = [best_chunk.chunk_id] if best_chunk else []
                excerpt = self._extract_excerpt(best_chunk.content) if best_chunk else None

            overlays.append(
                SentenceOverlay(
                    sentence_index=s_idx,
                    sentence=sentence,
                    grounding_score=round(grounding_score, 4),
                    inference_type=inf_type,
                    cited_chunk_ids=cited_ids,
                    top_evidence_excerpt=excerpt,
                    confidence=round(max(best_entailment, max_contradiction), 4),
                )
            )

        return overlays
