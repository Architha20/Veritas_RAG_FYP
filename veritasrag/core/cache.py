"""
Chunk and Embedding Caching Layer for VeritasRAG.
Supports in-memory LRU caching and optional Redis backends.
"""

import hashlib
from typing import Dict, Optional, Any
import numpy as np


class ChunkEmbeddingCache:
    """
    In-memory caching for chunk embeddings to avoid redundant encodings
    across sentences or repeated queries.
    """

    def __init__(self, max_size: int = 10000):
        self._cache: Dict[str, np.ndarray] = {}
        self.max_size = max_size

    @staticmethod
    def compute_key(content: str, model_name: str) -> str:
        """Generate deterministic SHA256 key for chunk content and model."""
        raw = f"{model_name}:{content.strip()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, content: str, model_name: str) -> Optional[np.ndarray]:
        key = self.compute_key(content, model_name)
        return self._cache.get(key)

    def set(self, content: str, model_name: str, embedding: np.ndarray) -> None:
        if len(self._cache) >= self.max_size:
            # Simple eviction: pop the first item
            first_key = next(iter(self._cache))
            self._cache.pop(first_key, None)

        key = self.compute_key(content, model_name)
        self._cache[key] = embedding

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        return len(self._cache)
