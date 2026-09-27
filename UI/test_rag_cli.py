"""
Quick interactive test: point this at a real PDF/DOCX/TXT file, ask
questions in the terminal, see the retrieved chunks and generated answer.

Usage:
    python test_rag_cli.py path/to/document.pdf
"""

import sys
from rag_pipeline import extract_text, chunk_text, DocumentIndex, answer_question


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_rag_cli.py path/to/document.pdf")
        sys.exit(1)

    file_path = sys.argv[1]

    print(f"Extracting text from {file_path}...")
    text = extract_text(file_path)
    print(f"Extracted {len(text)} characters.")

    print("Chunking...")
    chunks = chunk_text(text)
    print(f"Created {len(chunks)} chunks.")

    print("Building embedding index...")
    index = DocumentIndex(chunks)
    print("Ready.\n")

    print("Ask questions about the document (type 'quit' to exit).")
    while True:
        question = input("\nQuestion: ").strip()
        if question.lower() in ("quit", "exit"):
            break
        if not question:
            continue

        result = answer_question(index, question)

        print("\n--- Retrieved chunks ---")
        for i, c in enumerate(result["chunks"], 1):
            print(f"[{i}] {c[:150]}{'...' if len(c) > 150 else ''}")

        print(f"\n--- Answer ---\n{result['response']}")


if __name__ == "__main__":
    main()