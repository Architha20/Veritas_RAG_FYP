"""
VeritasRAG Quickstart Interactive Demo.
Run:
    python demo.py
"""

import os
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure root directory is on sys.path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from veritasrag import VeritasMiddleware, Chunk, InferenceType


def main():
    print("=" * 70)
    print("  [VeritasRAG] Real-Time Hallucination Flagging Middleware Demo")
    print("=" * 70)

    # 1. Initialize Middleware (defaults to fast embedding similarity)
    print("\n[1/3] Initializing VeritasRAG Middleware...")
    middleware = VeritasMiddleware(default_mode="embedding")

    # 2. Define a realistic RAG test case (medical QA)
    query = "What is the recommended adult dosage of ibuprofen and its history?"

    rag_response = (
        "The standard adult dose of ibuprofen is 200 to 400 mg every 4 to 6 hours. "
        "The maximum daily dose should not exceed 1200 mg without prescription. "
        "Ibuprofen was invented in 1995 by Dr. Mark Zuckerberg at Harvard University."
    )

    retrieved_chunks = [
        Chunk(
            chunk_id="chunk_rx_01",
            content="For adults, ibuprofen is typically administered at 200 to 400 mg per dose, "
                    "every 4 to 6 hours as needed. The maximum OTC daily dosage should not exceed 1200 mg.",
            source="drug_reference_guide.pdf (page 42)",
        ),
        Chunk(
            chunk_id="chunk_hist_02",
            content="Ibuprofen was discovered by Stewart Adams and John Nicholson in 1961 at the Boots UK research department.",
            source="pharmacology_history.pdf (page 12)",
        ),
    ]

    print(f"\n[2/3] Verifying RAG output against {len(retrieved_chunks)} retrieved chunks...")
    print(f"Query: \"{query}\"\n")

    mode = sys.argv[1] if len(sys.argv) > 1 else "hybrid"
    result = middleware.verify(
        query=query,
        response=rag_response,
        chunks=retrieved_chunks,
        mode=mode,
    )

    # 3. Print Results to Terminal
    label_map = {
        InferenceType.GROUNDED: "[GROUNDED]",
        InferenceType.INFERRED: "[INFERRED]",
        InferenceType.HALLUCINATED: "[HALLUCINATED]",
        InferenceType.CONTESTED: "[CONTESTED]",
    }

    print("-" * 70)
    print(f"Overall Grounding Score: {result.overall_grounding_score:.2f} "
          f"({result.overall_classification.upper().replace('_', ' ')})")
    print(f"Processing Latency     : {result.processing_time_ms:.1f}ms")
    print(f"Approaches Used        : {', '.join(result.approaches_used)}")
    print("-" * 70)
    print("\nSentence-Level Flagging Breakdown:")

    for o in result.sentence_overlays:
        tag = label_map.get(o.inference_type, "[UNKNOWN]")
        print(f"\n{tag} [{o.sentence_index + 1}] {o.sentence}")
        print(f"   |- Score : {o.grounding_score:.2f} ({o.inference_type.value.upper()})")
        if o.cited_chunk_ids:
            print(f"   `- Source: {', '.join(o.cited_chunk_ids)} -> \"{o.top_evidence_excerpt}\"")
        else:
            print(f"   `- Source: [UNSUPPORTED] No grounding evidence found in chunks.")

    # 4. Generate & Save Interactive HTML Report
    html_output_path = os.path.join(ROOT_DIR, "veritasrag_demo_overlay.html")
    middleware.save_html(result, html_output_path)
    print(f"\n[3/3] Color-coded interactive HTML overlay saved to:")
    print(f"      {html_output_path}")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
