"""Semantic retriever interface querying Qdrant with standardized query representation."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml

from support_agent.retrieval.embeddings import EmbeddingEngine
from support_agent.retrieval.vector_store import VectorStore, get_vector_store


def format_query_text(customer_message: str, context: Optional[str] = None) -> str:
    """Format query according to Phase 6B standard representation.

    CUSTOMER:
    <current customer message>

    CONTEXT:
    <current relevant conversation context>
    """
    parts = [f"CUSTOMER:\n{customer_message.strip()}"]
    if context and context.strip():
        parts.append(f"CONTEXT:\n{context.strip()}")
    return "\n\n".join(parts)


class QdrantRetriever:
    """Retriever utilizing Qdrant vector store and sentence transformer embeddings."""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_engine: Optional[EmbeddingEngine] = None,
        collection_name: Optional[str] = None,
        config_path: Union[str, Path] = "configs/retrieval.yaml",
    ):
        self.config_path = Path(config_path)
        cfg: Dict[str, Any] = {}
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}

        coll_cfg = cfg.get("collection", {})
        self.collection_name = collection_name or coll_cfg.get("name", "amazon_support_cases_v1")
        self.vector_store = vector_store or get_vector_store(config_path=self.config_path)
        self.embedding_engine = embedding_engine or EmbeddingEngine.from_config(config_path=self.config_path)

    def search(
        self,
        query_text: str,
        top_k: int = 30,
        filters: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """Search historical evidence matching query_text.

        Returns structured dictionaries containing:
        - document_id
        - case_id
        - conversation_id
        - score
        - customer_message
        - relevant_context
        - brand_response
        - metadata
        """
        # Encode query to vector
        query_vector = self.embedding_engine.encode_query(query_text)

        # Search vector store
        raw_results = self.vector_store.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            top_k=top_k,
            filters=filters,
        )

        formatted_results: List[Dict[str, Any]] = []
        for r in raw_results:
            payload = r.get("payload", {})
            metadata = {
                k: v
                for k, v in payload.items()
                if k not in (
                    "document_id",
                    "case_id",
                    "conversation_id",
                    "customer_message",
                    "relevant_context",
                    "brand_response",
                )
            }
            formatted_results.append({
                "document_id": payload.get("document_id"),
                "case_id": payload.get("case_id"),
                "conversation_id": payload.get("conversation_id"),
                "score": r.get("score", 0.0),
                "customer_message": payload.get("customer_message", ""),
                "relevant_context": payload.get("relevant_context", ""),
                "brand_response": payload.get("brand_response", ""),
                "metadata": metadata,
            })

        return formatted_results
