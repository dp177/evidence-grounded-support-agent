"""Retrieval Service coordinating semantic search and candidate reranking."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from support_agent.retrieval.retriever import QdrantRetriever, format_query_text
from support_agent.retrieval.reranker import CandidateReranker


class RetrievalService:
    """Orchestrates Qdrant retrieval, formatting, and semantic+lexical reranking."""

    def __init__(
        self,
        retriever: Optional[QdrantRetriever] = None,
        reranker: Optional[CandidateReranker] = None,
        config_path: str = "configs/retrieval.yaml",
        rerank_config_path: str = "configs/reranking.yaml",
    ):
        self.retriever = retriever or QdrantRetriever(config_path=config_path)
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
    ) -> List[Dict[str, Any]]:
        """Execute the full retrieval and reranking pipeline.
        
        1. Construct query
        2. Generate embedding & fetch Top 30 semantic matches
        3. Rerank candidates using semantic, lexical, intent, state, and boilerplate signals
        4. Apply conversation deduplication
        5. Return Top 5 candidates
        """
        query_text = format_query_text(customer_message, context)
        
        # Semantic search
        candidates = self.retriever.search(query_text=query_text, top_k=top_k_initial)
        
        if not candidates:
            return []

        # Rerank and deduplicate
        final_results = self.reranker.rerank(
            query_text=query_text,
            candidates=candidates,
            predicted_intents=predicted_intents,
            predicted_areas=predicted_areas,
            predicted_states=predicted_states,
            top_k=top_k_final,
        )
        
        # Add a rank field to the final results as requested
        for i, res in enumerate(final_results):
            res["rank"] = i + 1
            
        return final_results
