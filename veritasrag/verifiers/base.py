"""
Abstract Base Class for VeritasRAG Verifiers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..core.models import Chunk, SentenceOverlay


class BaseVerifier(ABC):
    """
    Base class that all verification approaches must implement.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name/identifier of this verifier."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the underlying model used."""
        pass

    @abstractmethod
    def verify(
        self,
        sentences: List[str],
        chunks: List[Chunk],
    ) -> List[SentenceOverlay]:
        """
        Verifies each sentence against the retrieved chunks.
        Returns a list of SentenceOverlay objects.
        """
        pass
