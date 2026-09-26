"""
Unit tests for SentenceSplitter.
Compatible with both pytest and unittest.
"""

import unittest
from veritasrag.core.splitter import SentenceSplitter


class TestSentenceSplitter(unittest.TestCase):
    def setUp(self):
        self.splitter = SentenceSplitter()

    def test_clean_text(self):
        raw = "  Hello   world! \r\n This is a test.  "
        cleaned = self.splitter.clean_text(raw)
        self.assertEqual(cleaned, "Hello world!\nThis is a test.")

    def test_split_simple_sentences(self):
        text = "Paris is the capital of France. It has a population of 2.1 million. The city is famous."
        sents = self.splitter.split(text)
        self.assertEqual(len(sents), 3)
        self.assertEqual(sents[0], "Paris is the capital of France.")
        self.assertIn("2.1 million", sents[1])

    def test_split_numbered_and_bullet_lists(self):
        text = """
        1. First item about AI.
        2. Second item about RAG systems.
        - Bullet point on hallucinations.
        """
        sents = self.splitter.split(text)
        self.assertEqual(len(sents), 3)
        self.assertEqual(sents[0], "First item about AI.")
        self.assertEqual(sents[1], "Second item about RAG systems.")
        self.assertEqual(sents[2], "Bullet point on hallucinations.")

    def test_split_empty_text(self):
        self.assertEqual(self.splitter.split(""), [])
        self.assertEqual(self.splitter.split("   "), [])


if __name__ == "__main__":
    unittest.main()
