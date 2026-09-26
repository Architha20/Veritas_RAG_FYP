"""
Unit tests for VeritasRAG Core Data Models.
Compatible with both pytest and unittest.
"""

import unittest
from veritasrag.core.models import (
    Chunk,
    SentenceOverlay,
    VerificationResult,
    InferenceType,
)


class TestCoreModels(unittest.TestCase):
    def test_chunk_creation(self):
        c = Chunk(chunk_id="c1", content="Sample context chunk.", source="doc.pdf")
        self.assertEqual(c.chunk_id, "c1")
        self.assertEqual(c.content, "Sample context chunk.")
        self.assertEqual(c.source, "doc.pdf")

    def test_sentence_overlay_creation(self):
        o = SentenceOverlay(
            sentence_index=0,
            sentence="Test claim.",
            grounding_score=0.92,
            inference_type=InferenceType.GROUNDED,
            cited_chunk_ids=["c1"],
            top_evidence_excerpt="Sample context",
        )
        self.assertEqual(o.inference_type, InferenceType.GROUNDED)
        self.assertEqual(o.grounding_score, 0.92)
        self.assertIn("c1", o.cited_chunk_ids)

    def test_verification_result_serialization(self):
        res = VerificationResult(
            query="Test query",
            rag_response="Test response.",
            overall_grounding_score=0.88,
            overall_classification="grounded",
            sentence_overlays=[],
            processing_time_ms=120.5,
        )
        data = res.model_dump()
        self.assertEqual(data["query"], "Test query")
        self.assertEqual(data["overall_grounding_score"], 0.88)


if __name__ == "__main__":
    unittest.main()
