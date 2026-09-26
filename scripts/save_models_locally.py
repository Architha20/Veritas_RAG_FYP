"""
Script to save Hugging Face models directly inside the local `models/` project directory.
This ensures the repository contains all physical model weights locally.
"""
import os
import sys
from pathlib import Path

# Set up paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
MINILM_DIR = MODELS_DIR / "all-MiniLM-L6-v2"
DEBERTA_DIR = MODELS_DIR / "nli-deberta-v3-base"

print(f"[VeritasRAG] Project root: {PROJECT_ROOT}")
print(f"[VeritasRAG] Target models directory: {MODELS_DIR}")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# 1. Save all-MiniLM-L6-v2
print("\n[1/2] Saving sentence-transformers/all-MiniLM-L6-v2 to local directory...")
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
embedding_model.save(str(MINILM_DIR))
print(f"  --> Saved to {MINILM_DIR} successfully!")

# 2. Save cross-encoder/nli-deberta-v3-base
print("\n[2/2] Saving cross-encoder/nli-deberta-v3-base to local directory...")
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model_name = "cross-encoder/nli-deberta-v3-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

DEBERTA_DIR.mkdir(parents=True, exist_ok=True)
tokenizer.save_pretrained(str(DEBERTA_DIR))
model.save_pretrained(str(DEBERTA_DIR))
print(f"  --> Saved to {DEBERTA_DIR} successfully!")

print("\n[VeritasRAG] All models successfully saved locally inside ./models/")
