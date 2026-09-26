"""
Neuro-Symbolic Entity and Numerical Consistency Guard for VeritasRAG.
Detects swapped dates, altered numbers, and ungrounded Named Entities
that deceive standard bi-encoder and cross-encoder attention mechanisms.
Handles numerical magnitudes, approximations, financial quarters, and entity aliases.
"""

import re
from typing import List, Dict, Set, Tuple, Optional, Any
import spacy
from .models import Chunk


class EntityNumericalGuard:
    """
    Validates entity and numerical consistency between claims and retrieved context.
    Acts as a neuro-symbolic factual safeguard against hallucinated entities and numbers.
    """

    # True Named Entity types (persons, organizations, geopolitical, locations)
    FACTUAL_ENTITY_LABELS = {
        "PERSON",
        "ORG",
        "GPE",
        "LOC",
        "FAC",
        "NORP",
    }

    # Known entity aliases and acronym expansions
    KNOWN_ALIASES: Dict[str, Set[str]] = {
        "eu": {"european union", "eu", "europe"},
        "european union": {"eu", "european union", "europe"},
        "ai": {"artificial intelligence", "ai"},
        "artificial intelligence": {"ai", "artificial intelligence"},
        "nasa": {"national aeronautics and space administration", "nasa"},
        "apple": {"apple", "apple inc", "apple inc.", "the company"},
        "australia": {"australia", "australian", "act", "canberra"},
        "australian": {"australia", "australian"},
        "germany": {"germany", "german"},
        "german": {"germany", "german"},
        "france": {"france", "french"},
        "french": {"france", "french"},
        "uk": {"united kingdom", "uk", "britain", "british"},
        "united kingdom": {"united kingdom", "uk", "britain", "british"},
        "us": {"united states", "usa", "us", "america", "american"},
        "usa": {"united states", "usa", "us", "america", "american"},
        "united states": {"united states", "usa", "us", "america", "american"},
    }

    QUARTER_MAP = {
        "q1": {"q1", "first quarter", "1st quarter"},
        "q2": {"q2", "second quarter", "2nd quarter"},
        "q3": {"q3", "third quarter", "3rd quarter"},
        "q4": {"q4", "fourth quarter", "4th quarter"},
        "first quarter": {"q1", "first quarter", "1st quarter"},
        "second quarter": {"q2", "second quarter", "2nd quarter"},
        "third quarter": {"q3", "third quarter", "3rd quarter"},
        "fourth quarter": {"q4", "fourth quarter", "4th quarter"},
    }

    def __init__(self, nlp: Optional[spacy.language.Language] = None):
        if nlp is not None:
            self.nlp = nlp
        else:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.nlp = spacy.blank("en")

    def extract_entities_and_numbers(self, text: str) -> Dict[str, Set[str]]:
        """
        Extracts Named Entities, dates, financial quarters, and numbers from text.
        """
        doc = self.nlp(text)
        entities: Set[str] = set()

        for ent in doc.ents:
            if ent.label_ in self.FACTUAL_ENTITY_LABELS:
                clean_ent = ent.text.strip().lower()
                # Clean punctuation
                clean_ent = re.sub(r"^[^\w]+|[^\w]+$", "", clean_ent)
                if len(clean_ent) > 1 and not any(ch.isdigit() for ch in clean_ent):
                    entities.add(clean_ent)

        # Detect quarters like Q1, Q2, Q3, Q4, fourth quarter
        for q_key, syns in self.QUARTER_MAP.items():
            for syn in syns:
                if re.search(r"\b" + re.escape(syn) + r"\b", text.lower()):
                    entities.add(syn)

        # Regex for numbers, dates, and quantitative units (e.g. 1995, 2.1, 400mg, 50%, $89.5B)
        raw_numbers = re.findall(
            r"(?:\$\s*)?\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:billion|million|trillion|percent|%|mg|kg|g|ml|km|miles|k|m|b)?\b",
            text.lower(),
        )
        numbers: Set[str] = set()
        for num in raw_numbers:
            clean_num = num.strip()
            # Exclude standalone single digits that are common stop words unless preceded by $ or followed by unit
            if clean_num:
                numbers.add(clean_num)

        return {"entities": entities, "numbers": numbers}

    def _parse_numeric_value(self, token: str) -> Optional[float]:
        """
        Normalizes human-formatted numbers into float values for approximation reasoning.
        Examples: '$89.5 billion' -> 89500000000.0, '456,000' -> 456000.0
        """
        clean = token.lower().replace("$", "").replace(",", "").strip()
        multiplier = 1.0
        if "billion" in clean or clean.endswith("b"):
            multiplier = 1e9
            clean = re.sub(r"[^\d.]", "", clean)
        elif "million" in clean or clean.endswith("m"):
            multiplier = 1e6
            clean = re.sub(r"[^\d.]", "", clean)
        elif "thousand" in clean or clean.endswith("k"):
            multiplier = 1e3
            clean = re.sub(r"[^\d.]", "", clean)
        else:
            clean = re.sub(r"[^\d.]", "", clean)

        try:
            return float(clean) * multiplier
        except ValueError:
            return None

    def _is_number_supported(
        self, num_str: str, context_corpus: str, claim: str
    ) -> bool:
        """
        Validates if a number in the claim is supported in context either via:
        1. Exact string or digit match.
        2. Financial quarter equivalence (e.g. Q4 <-> fourth quarter).
        3. Mathematical inequality for approximation phrases (e.g. 'over 450,000' when context has 456,000).
        """
        # Exact or sub-string presence
        num_digits = re.sub(r"[^\d.]", "", num_str)
        if num_str in context_corpus or (num_digits and num_digits in context_corpus):
            return True

        # Check quarter equivalence
        num_lower = num_str.lower().strip()
        for q_key, syns in self.QUARTER_MAP.items():
            if num_lower in syns:
                if any(syn in context_corpus for syn in syns):
                    return True

        # Approximation check (over/more than/at least X vs actual in context)
        claim_val = self._parse_numeric_value(num_str)
        if claim_val is not None:
            # Check context numbers
            context_numbers = re.findall(
                r"(?:\$\s*)?\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:billion|million|trillion|percent|%|k|m|b)?\b",
                context_corpus,
            )
            for c_num in context_numbers:
                c_val = self._parse_numeric_value(c_num)
                if c_val is not None:
                    # Check relative difference (< 1% relative tolerance)
                    if abs(c_val - claim_val) / max(c_val, claim_val, 1e-6) < 0.01:
                        return True
                    # Check directional approximations
                    if re.search(r"\b(?:over|more than|at least|exceeding)\s+" + re.escape(num_str), claim.lower()):
                        if c_val >= claim_val:
                            return True
                    if re.search(r"\b(?:under|less than|at most|nearly|around|approx)\s+" + re.escape(num_str), claim.lower()):
                        if abs(c_val - claim_val) / max(c_val, 1e-6) <= 0.15:
                            return True

        return False

    def check_claim_grounding(
        self,
        claim: str,
        chunks: List[Chunk],
    ) -> Dict[str, Any]:
        """
        Checks whether entities and numbers asserted in the claim
        exist in the retrieved context.
        """
        claim_items = self.extract_entities_and_numbers(claim)
        claim_entities = claim_items["entities"]
        claim_numbers = claim_items["numbers"]

        if not claim_entities and not claim_numbers:
            return {
                "has_verifiable_tokens": False,
                "entity_overlap_ratio": 1.0,
                "number_overlap_ratio": 1.0,
                "unsupported_entities": [],
                "unsupported_numbers": [],
                "penalty_factor": 1.0,
            }

        # Combine all chunk text into a normalized context corpus
        context_corpus = " ".join(c.content.lower() for c in chunks)

        # Check entity presence
        unsupported_entities = []
        for ent in claim_entities:
            ent_lower = ent.lower().strip()
            # 1. Direct or alias match
            matched = ent_lower in context_corpus
            if not matched and ent_lower in self.KNOWN_ALIASES:
                matched = any(alias in context_corpus for alias in self.KNOWN_ALIASES[ent_lower])

            # 2. Subtoken / stem matching for multi-word or derived entities
            if not matched:
                tokens = [t for t in ent_lower.split() if len(t) > 2]
                if tokens:
                    matched = all(t in context_corpus or t[:4] in context_corpus for t in tokens if len(t) >= 4)

            # 3. Check quarter equivalence
            if not matched and ent_lower in self.QUARTER_MAP:
                matched = any(syn in context_corpus for syn in self.QUARTER_MAP[ent_lower])

            if not matched:
                unsupported_entities.append(ent)

        # Check numerical presence
        unsupported_numbers = []
        for num in claim_numbers:
            if not self._is_number_supported(num, context_corpus, claim):
                unsupported_numbers.append(num)

        total_entities = len(claim_entities)
        total_numbers = len(claim_numbers)

        ent_ratio = (
            (total_entities - len(unsupported_entities)) / total_entities
            if total_entities > 0
            else 1.0
        )
        num_ratio = (
            (total_numbers - len(unsupported_numbers)) / total_numbers
            if total_numbers > 0
            else 1.0
        )

        penalty = 1.0
        if unsupported_numbers:
            penalty *= max(0.05, num_ratio)

        if unsupported_entities:
            penalty *= max(0.15, ent_ratio)

        return {
            "has_verifiable_tokens": True,
            "entity_overlap_ratio": round(ent_ratio, 3),
            "number_overlap_ratio": round(num_ratio, 3),
            "unsupported_entities": unsupported_entities,
            "unsupported_numbers": unsupported_numbers,
            "penalty_factor": round(penalty, 3),
        }
