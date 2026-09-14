"""Retrieval Service coordinating semantic search, lexical search, and candidate reranking."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from support_agent.retrieval.retriever import QdrantRetriever, format_query_text
from support_agent.retrieval.lexical_retriever import LexicalRetriever
from support_agent.retrieval.reranker import CandidateReranker


class RetrievalService:
    """Orchestrates Qdrant semantic retrieval, TF-IDF lexical retrieval, and RRF reranking."""

    def __init__(
        self,
        retriever: Optional[QdrantRetriever] = None,
        lexical_retriever: Optional[LexicalRetriever] = None,
        reranker: Optional[CandidateReranker] = None,
        config_path: str = "configs/retrieval.yaml",
        rerank_config_path: str = "configs/reranking.yaml",
    ):
        self.retriever = retriever or QdrantRetriever(config_path=config_path)
        self.lexical_retriever = lexical_retriever or LexicalRetriever()
        self.reranker = reranker or CandidateReranker(config_path=rerank_config_path)

    def retrieve(
        self,
        customer_message: str,
        context: Optional[str] = None,
        predicted_intents: Optional[List[str]] = None,
        predicted_areas: Optional[List[str]] = None,
        predicted_states: Optional[List[str]] = None,
        top_k_initial: int = 30,
        top_k_final: int = 5,
        k: int = 60,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """Execute the two-ranking retrieval and RRF reranking pipeline.

        1. Construct query text from customer message and context.
        2. Run dense semantic retrieval (Top 30 candidates).
        3. Run lexical keyword retrieval (Top 30 candidates).
        4. Fuse the two ranked lists using Reciprocal Rank Fusion (k=60).
        5. Return Top 5 candidates sorted by descending RRF score.
        """
        query_text = format_query_text(customer_message, context)

        # 1. Semantic search (Top 30)
        semantic_candidates = self.retriever.search(query_text=query_text, top_k=top_k_initial)

        # 2. Lexical search (Top 30)
        lexical_candidates = []
        if self.lexical_retriever:
            try:
                lexical_candidates = self.lexical_retriever.search(query_text=query_text, top_k=top_k_initial)
            except Exception:
                lexical_candidates = []

        if not semantic_candidates and not lexical_candidates:
            return []

        # 3. Rerank via RRF and deduplicate
        final_results = self.reranker.rerank(
            query_text=query_text,
            semantic_candidates=semantic_candidates,
            lexical_candidates=lexical_candidates,
            candidates=semantic_candidates,
            top_k=top_k_final,
            k=k,
        )

        # Add 1-based rank
        for i, res in enumerate(final_results):
            res["rank"] = i + 1

        return final_results

