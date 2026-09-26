"""
End-to-end tests for VeritasMiddleware.
Compatible with both pytest and unittest.
"""

import unittest
from veritasrag.middleware import VeritasMiddleware
from veritasrag.core.models import Chunk, InferenceType


class TestVeritasMiddleware(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.middleware = VeritasMiddleware(default_mode="embedding")

    def test_middleware_end_to_end(self):
        query = "What is the capital of France and who founded it?"
        response = "Paris is the capital of France. It was founded by extraterrestrial aliens in 1999."
        chunks = [
            Chunk(
                chunk_id="chunk_paris",
                content="Paris is the capital and largest city of France, situated along the Seine River.",
            )
        ]

        result = self.middleware.verify(query=query, response=response, chunks=chunks)

        self.assertEqual(result.query, query)
        self.assertEqual(len(result.sentence_overlays), 2)
        self.assertGreater(result.processing_time_ms, 0)

        # Sentence 1: Grounded
        self.assertEqual(result.sentence_overlays[0].inference_type, InferenceType.GROUNDED)
        self.assertIn("chunk_paris", result.sentence_overlays[0].cited_chunk_ids)

        # Sentence 2: Hallucinated
        self.assertEqual(result.sentence_overlays[1].inference_type, InferenceType.HALLUCINATED)

        # JSON generation
        json_str = self.middleware.to_json(result)
        self.assertIn("overall_grounding_score", json_str)

        # HTML generation
        html_str = self.middleware.to_html(result)
        self.assertIn("<!DOCTYPE html>", html_str)
        self.assertIn("VeritasRAG Grounding Report", html_str)


if __name__ == "__main__":
    unittest.main()
