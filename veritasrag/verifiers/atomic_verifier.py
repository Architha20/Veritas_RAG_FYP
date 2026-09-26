"""
Approach C: Atomic Fact Extraction and Sub-Passage Entailment Verifier.
Decomposes compound sentences into atomic verifiable claims, locates
the focal sub-passage evidence, and applies neuro-symbolic entity checks.
"""

import re
from typing import List, Optional, Tuple, Dict, Any
import numpy as np
import spacy

from .base import BaseVerifier
from ..core.models import Chunk, SentenceOverlay, AtomicClaim, InferenceType
from ..core.entity_guard import EntityNumericalGuard


class AtomicVerifier(BaseVerifier):
    """
    Approach C: Fine-grained atomic fact verification with sub-passage zooming.
    Eliminates the "partial sentence hallucination" and "attention dispersion" failure modes.
    """

    def __init__(
        self,
        nli_verifier: Optional[BaseVerifier] = None,
        entity_guard: Optional[EntityNumericalGuard] = None,
        threshold_grounded: float = 0.65,
        threshold_inferred: float = 0.40,
    ):
        self._nli_verifier = nli_verifier
        self.entity_guard = entity_guard or EntityNumericalGuard()
        self.threshold_grounded = threshold_grounded
        self.threshold_inferred = threshold_inferred
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = spacy.blank("en")

    @property
    def name(self) -> str:
        return "atomic_fact_entailment"

    @property
    def model_name(self) -> str:
        return (
            f"AtomicDecomposer + {self._nli_verifier.model_name}"
            if self._nli_verifier
            else "AtomicDecomposer"
        )

    def decompose_sentence(self, sentence: str, sentence_idx: int) -> List[AtomicClaim]:
        """
        Decomposes a compound sentence into atomic sub-claims.
        Uses dependency parsing to detect coordinated clauses and relative clauses
        with their own verbs, preserving semantic coherence and subjects.
        """
        doc = self.nlp(sentence)

        # Identify finite verbs / auxiliaries
        verbs = [tok for tok in doc if tok.pos_ in ("VERB", "AUX")]
        if len(verbs) <= 1:
            return [
                AtomicClaim(
                    claim_id=f"sent_{sentence_idx}_claim_0",
                    claim_text=sentence.strip().rstrip("."),
                    parent_sentence_index=sentence_idx,
                )
            ]

        # Check for coordinate conjunctions joining clauses
        conjunctions = [
            tok for tok in doc if tok.pos_ == "CCONJ" or tok.text.lower() in (";", "whereas", "while", "although")
        ]
        if not conjunctions:
            return [
                AtomicClaim(
                    claim_id=f"sent_{sentence_idx}_claim_0",
                    claim_text=sentence.strip().rstrip("."),
                    parent_sentence_index=sentence_idx,
                )
            ]

        # Extract subject from root verb
        root_verb = next((tok for tok in doc if tok.dep_ == "ROOT"), None)
        subject_text = ""
        if root_verb:
            subj_toks = [tok for tok in root_verb.lefts if tok.dep_ in ("nsubj", "nsubjpass")]
            if subj_toks:
                subject_text = "".join(tok.text_with_ws for tok in subj_toks[0].subtree).strip()

        # Split on coordinating conjunctions that separate clauses
        raw_parts = re.split(r";|\b(?:and|but|while|whereas|although|however)\b", sentence, flags=re.IGNORECASE)
        valid_parts = []
        for p in raw_parts:
            p_clean = p.strip().strip(",").strip()
            if not p_clean:
                continue
            p_doc = self.nlp(p_clean)
            p_verbs = [tok for tok in p_doc if tok.pos_ in ("VERB", "AUX")]
            # Only consider a clause if it has at least one verb and >= 3 words
            if len(p_clean.split()) >= 3 and p_verbs:
                has_subj = any(tok.dep_ in ("nsubj", "nsubjpass") for tok in p_doc) if p_doc.has_annotation("DEP") else False
                if not has_subj and subject_text and not p_clean.lower().startswith(subject_text.lower()):
                    reconstructed = f"{subject_text} {p_clean}"
                else:
                    reconstructed = p_clean
                valid_parts.append(reconstructed.rstrip("."))

        if len(valid_parts) < 2:
            valid_parts = [sentence.strip().rstrip(".")]

        atomic_claims = []
        for c_idx, text in enumerate(valid_parts):
            atomic_claims.append(
                AtomicClaim(
                    claim_id=f"sent_{sentence_idx}_claim_{c_idx}",
                    claim_text=text,
                    parent_sentence_index=sentence_idx,
                )
            )
        return atomic_claims

    def _extract_focal_subpassages(self, chunks: List[Chunk]) -> List[Tuple[Chunk, str]]:
        """
        Extracts focal candidate premises: includes the full chunk content
        plus multi-sentence sliding windows for longer contexts to preserve coreference.
        """
        subpassages: List[Tuple[Chunk, str]] = []
        for chunk in chunks:
            # 1. Always include full chunk to preserve pronoun antecedents and global context
            subpassages.append((chunk, chunk.content))

            # 2. If chunk has multiple sentences, add 2-sentence sliding windows
            doc = self.nlp(chunk.content)
            sents = [s.text.strip() for s in doc.sents if s.text.strip()]
            if len(sents) > 2:
                for i in range(len(sents) - 1):
                    window = f"{sents[i]} {sents[i+1]}"
                    subpassages.append((chunk, window))
        return subpassages

    def verify_atomic_claim(
        self,
        claim: AtomicClaim,
        chunks: List[Chunk],
        subpassages: List[Tuple[Chunk, str]],
    ) -> AtomicClaim:
        """
        Verifies a single atomic claim against candidate focal sub-passages
        and applies neuro-symbolic entity/numerical checks.
        """
        # 1. Neuro-symbolic entity guard check
        guard_res = self.entity_guard.check_claim_grounding(claim.claim_text, chunks)
        penalty = guard_res["penalty_factor"]

        # 2. Verification using NLI or lexical-semantic matcher
        best_score = 0.0
        best_chunk: Optional[Chunk] = None
        best_passage: Optional[str] = None

        if self._nli_verifier:
            # Mini chunks from sub-passages
            mini_chunks = [
                Chunk(chunk_id=c.chunk_id, content=p, source=c.source)
                for c, p in subpassages
            ]
            overlays = self._nli_verifier.verify([claim.claim_text], mini_chunks)
            if overlays:
                best_score = overlays[0].grounding_score
                if overlays[0].cited_chunk_ids:
                    best_chunk_id = overlays[0].cited_chunk_ids[0]
                    best_chunk = next((c for c in chunks if c.chunk_id == best_chunk_id), None)
                    best_passage = overlays[0].top_evidence_excerpt
        else:
            # Lexical Jaccard + token overlap fallback
            claim_tokens = set(claim.claim_text.lower().split())
            for chunk, passage in subpassages:
                pass_tokens = set(passage.lower().split())
                inter = claim_tokens.intersection(pass_tokens)
                score = len(inter) / len(claim_tokens) if claim_tokens else 0.0
                if score > best_score:
                    best_score = score
                    best_chunk = chunk
                    best_passage = passage

        # Apply entity guard penalty
        final_score = round(best_score * penalty, 4)

        if penalty < 0.35:
            inf_type = InferenceType.HALLUCINATED
        elif final_score >= self.threshold_grounded:
            inf_type = InferenceType.GROUNDED
        elif final_score >= self.threshold_inferred:
            inf_type = InferenceType.INFERRED
        else:
            inf_type = InferenceType.HALLUCINATED

        claim.grounding_score = final_score
        claim.inference_type = inf_type
        claim.supporting_chunk_id = best_chunk.chunk_id if best_chunk and inf_type != InferenceType.HALLUCINATED else None
        claim.evidence_excerpt = best_passage if best_passage and inf_type != InferenceType.HALLUCINATED else None

        return claim

    def verify(
        self,
        sentences: List[str],
        chunks: List[Chunk],
    ) -> List[SentenceOverlay]:
        """
        Full verification decomposing sentences into atomic claims and aggregating scores.
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

        # Extract focal sub-passages across all chunks
        subpassages = self._extract_focal_subpassages(chunks)
        overlays: List[SentenceOverlay] = []

        for s_idx, sentence in enumerate(sentences):
            # 1. Decompose into atomic claims
            claims = self.decompose_sentence(sentence, s_idx)

            # 2. Verify each claim
            verified_claims = [
                self.verify_atomic_claim(c, chunks, subpassages) for c in claims
            ]

            # 3. Aggregate claim scores to sentence level
            avg_score = (
                sum(c.grounding_score for c in verified_claims) / len(verified_claims)
                if verified_claims
                else 0.0
            )
            has_hallucination = any(
                c.inference_type == InferenceType.HALLUCINATED for c in verified_claims
            )
            all_grounded = all(
                c.inference_type == InferenceType.GROUNDED for c in verified_claims
            )

            if all_grounded and avg_score >= self.threshold_grounded:
                sentence_type = InferenceType.GROUNDED
            elif has_hallucination:
                # If any atomic sub-claim is fabricated, the sentence is unfaithful
                sentence_type = InferenceType.HALLUCINATED
            elif avg_score >= self.threshold_inferred:
                sentence_type = InferenceType.INFERRED
            else:
                sentence_type = InferenceType.HALLUCINATED

            cited_ids = list(
                dict.fromkeys(
                    c.supporting_chunk_id
                    for c in verified_claims
                    if c.supporting_chunk_id
                )
            )
            excerpts = [
                c.evidence_excerpt
                for c in verified_claims
                if c.evidence_excerpt
            ]
            top_excerpt = excerpts[0] if excerpts else None

            overlays.append(
                SentenceOverlay(
                    sentence_index=s_idx,
                    sentence=sentence,
                    grounding_score=round(avg_score, 4),
                    inference_type=sentence_type,
                    cited_chunk_ids=cited_ids,
                    top_evidence_excerpt=top_excerpt,
                    atomic_claims=verified_claims,
                    confidence=round(avg_score if sentence_type == InferenceType.GROUNDED else (1.0 - avg_score), 4),
                )
            )

        return overlays
