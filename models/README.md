# VeritasRAG Models Directory

This directory stores offline model weights for VeritasRAG.

Because pre-trained model weights (such as `nli-deberta-v3-base`) exceed GitHub's 100MB file size limit, model weight files (`*.safetensors`, `*.bin`, `*.pt`) are not committed to Git.

## Setup Instructions

### Option 1: Automatic Download (Online Mode)
VeritasRAG will automatically fetch models from Hugging Face Hub if they are not detected in this directory:
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- NLI model: `cross-encoder/nli-deberta-v3-base`

### Option 2: Pre-cache for Full Offline Execution
To populate this directory with physical model weights for fully offline execution, run:
```bash
python scripts/save_models_locally.py
```
This script downloads both models and saves them to:
- `models/all-MiniLM-L6-v2/`
- `models/nli-deberta-v3-base/`
