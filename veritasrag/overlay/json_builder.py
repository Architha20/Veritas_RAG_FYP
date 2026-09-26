"""
JSON Overlay Serializer for VeritasRAG.
Produces machine-readable API and pipeline payloads.
"""

import json
from typing import Dict, Any
from ..core.models import VerificationResult


class JSONOverlayBuilder:
    """
    Serializes a VerificationResult into standard JSON or Python dictionary.
    """

    @staticmethod
    def to_dict(result: VerificationResult) -> Dict[str, Any]:
        return result.model_dump()

    @staticmethod
    def to_json(result: VerificationResult, indent: int = 2) -> str:
        return json.dumps(result.model_dump(), indent=indent, default=str)
