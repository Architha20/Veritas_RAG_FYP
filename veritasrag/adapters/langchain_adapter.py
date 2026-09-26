"""
LangChain Adapter for VeritasRAG.
Allows drop-in verification as a LangChain BaseCallbackHandler.
"""

from typing import Any, Dict, List, Optional
from ..core.models import Chunk, VerificationResult
from ..middleware import VeritasMiddleware


class VeritasLangChainCallback:
    """
    Interception callback for LangChain pipelines.
    Collects retrieved documents and LLM generations, then automatically
    runs VeritasRAG grounding verification.
    """

    def __init__(self, mode: str = "embedding"):
        self.middleware = VeritasMiddleware(default_mode=mode)
        self.last_query: Optional[str] = None
        self.retrieved_chunks: List[Chunk] = []
        self.last_result: Optional[VerificationResult] = None

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        if "query" in inputs:
            self.last_query = str(inputs["query"])
        elif "input" in inputs:
            self.last_query = str(inputs["input"])

    def on_retriever_end(self, documents: List[Any], **kwargs: Any) -> None:
        """Capture documents retrieved by vector database."""
        self.retrieved_chunks = []
        for idx, doc in enumerate(documents):
            chunk_id = getattr(doc, "id", None) or f"doc_{idx}"
            content = getattr(doc, "page_content", str(doc))
            source = getattr(doc, "metadata", {}).get("source", "unknown")
            self.retrieved_chunks.append(Chunk(chunk_id=chunk_id, content=content, source=source))

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """Capture LLM generation and trigger verification."""
        try:
            gen_text = response.generations[0][0].text
        except (AttributeError, IndexError):
            gen_text = str(response)

        if self.last_query and self.retrieved_chunks:
            self.last_result = self.middleware.verify(
                query=self.last_query,
                response=gen_text,
                chunks=self.retrieved_chunks,
            )

    def get_overlay_html(self) -> Optional[str]:
        if self.last_result:
            return self.middleware.to_html(self.last_result)
        return None
