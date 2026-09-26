"""
Sentence Splitting and Text Normalization for VeritasRAG.
Uses spaCy (en_core_web_sm) with rules for technical/academic text.
"""

import re
from typing import List, Tuple
import spacy


class SentenceSplitter:
    """
    Splits text into discrete, verifiable sentence units.
    Handles abbreviations, decimal numbers, citations, bullet points, and URLs.
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            # Fallback if model not installed by name
            self.nlp = spacy.blank("en")
            self.nlp.add_pipe("sentencizer")

    def clean_text(self, text: str) -> str:
        """Normalize whitespace and strip problematic formatting."""
        if not text:
            return ""
        text = re.sub(r"\r\n|\r", "\n", text)
        text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def split(self, text: str) -> List[str]:
        """
        Splits RAG response text into individual sentences.
        Filters out empty lines, standalone numbering, or single punctuation characters.
        """
        cleaned = self.clean_text(text)
        if not cleaned:
            return []

        doc = self.nlp(cleaned)
        sentences: List[str] = []

        for sent in doc.sents:
            s_text = sent.text.strip()
            # Remove leading bullet symbols (-, *, •, 1., 2.)
            s_text = re.sub(r"^(\d+\.|\*|\-|\•)\s*", "", s_text).strip()
            # Ignore trivial fragments (< 3 characters or just punctuation)
            if len(s_text) >= 3 and any(c.isalnum() for c in s_text):
                sentences.append(s_text)

        return sentences

    def split_with_spans(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Returns list of (sentence_text, start_char, end_char) for highlighting in original text.
        """
        cleaned = self.clean_text(text)
        if not cleaned:
            return []

        doc = self.nlp(cleaned)
        results: List[Tuple[str, int, int]] = []

        for sent in doc.sents:
            s_text = sent.text.strip()
            if len(s_text) >= 3 and any(c.isalnum() for c in s_text):
                results.append((s_text, sent.start_char, sent.end_char))

        return results
