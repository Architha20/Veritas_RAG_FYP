"""
Unit tests for Approach A EmbeddingVerifier.
Compatible with both pytest and unittest.
"""

import unittest
from veritasrag.core.models import Chunk, InferenceType
from veritasrag.verifiers.embedding_verifier import EmbeddingVerifier


class TestEmbeddingVerifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.verifier = EmbeddingVerifier()

    def test_grounded_sentence(self):
        chunks = [
            Chunk(
                chunk_id="chunk_01",
                content="The standard adult dose of ibuprofen is 200 to 400 mg every 4 to 6 hours.",
            )
        ]
        sentences = ["The adult dosage of ibuprofen is 200-400 mg every 4-6 hours."]
        overlays = self.verifier.verify(sentences, chunks)

        self.assertEqual(len(overlays), 1)
        self.assertGreaterEqual(overlays[0].grounding_score, 0.70)
        self.assertIn(overlays[0].inference_type, (InferenceType.GROUNDED, InferenceType.INFERRED))
        self.assertIn("chunk_01", overlays[0].cited_chunk_ids)

    def test_hallucinated_sentence(self):
        chunks = [
            Chunk(
                chunk_id="chunk_01",
                content="France is in Western Europe with capital in Paris.",
            )
        ]
        sentences = ["The Apollo 11 moon landing occurred in July 1969."]
        overlays = self.verifier.verify(sentences, chunks)

        self.assertEqual(len(overlays), 1)
        self.assertLess(overlays[0].grounding_score, 0.50)
        self.assertEqual(overlays[0].inference_type, InferenceType.HALLUCINATED)
        self.assertEqual(overlays[0].cited_chunk_ids, [])

    def test_empty_chunks(self):
        sentences = ["Some random claim."]
        overlays = self.verifier.verify(sentences, [])
        self.assertEqual(len(overlays), 1)
        self.assertEqual(overlays[0].inference_type, InferenceType.HALLUCINATED)
        self.assertEqual(overlays[0].grounding_score, 0.0)


if __name__ == "__main__":
    unittest.main()
