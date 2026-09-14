"""Lexical Retriever for Historical Support Cases.

Provides Top-N candidate retrieval based on lexical keyword relevance (TF-IDF vocabulary overlap)
over the historical precedent corpus.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# Standard stop words to de-emphasize generic greetings/fillers
LEXICAL_STOP_WORDS = {
    "order", "package", "delivery", "refund", "help", "amazon",
    "please", "hi", "hello", "thanks", "thank", "you"
}


class LexicalRetriever:
    """Retrieves Top-K historical support cases based on lexical relevance."""

    def __init__(
        self,
        corpus_path: str = "data/processed/qdrant_development_sample.parquet",
    ):
        self.corpus_path = Path(corpus_path)
        self.documents: List[Dict[str, Any]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[Any] = None
        self._is_indexed = False

        self._initialize_index()

    def _initialize_index(self) -> None:
        """Load corpus and precompute TF-IDF representation."""
        if not self.corpus_path.exists():
            logger.warning(
                "Lexical corpus path %s does not exist. Lexical retrieval will return empty.",
                self.corpus_path,
            )
            return

        try:
            df = pd.read_parquet(self.corpus_path)
            docs = []
            texts = []
            for _, row in df.iterrows():
                cid = str(row.get("case_id") or row.get("document_id") or "")
                cust_msg = str(row.get("customer_message") or "")
                ctx = str(row.get("relevant_context") or "")
                brand_resp = str(row.get("brand_response") or "")

                # Combined text used for lexical indexing
                combined_text = f"{cust_msg} {ctx}".strip()
                if not combined_text:
                    combined_text = cust_msg

                docs.append({
                    "case_id": cid,
                    "document_id": str(row.get("document_id") or cid),
                    "conversation_id": str(row.get("conversation_id") or ""),
                    "turn_index": int(row.get("turn_index", 1)),
                    "customer_message": cust_msg,
                    "relevant_context": ctx,
                    "brand_response": brand_resp,
                    "metadata": {
                        "thread_length": row.get("thread_length"),
                        "language": row.get("language"),
                        "quality_status": row.get("quality_status"),
                    },
                })
                texts.append(combined_text)

            self.documents = docs
            self.vectorizer = TfidfVectorizer(
                stop_words=list(LEXICAL_STOP_WORDS),
                token_pattern=r"(?u)\b\w+\b",
                max_features=25000,
                ngram_range=(1, 2),
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
            self._is_indexed = True
            logger.info("LexicalRetriever indexed %d documents from %s", len(self.documents), self.corpus_path)
        except Exception as e:
            logger.error("Failed to initialize LexicalRetriever: %s", e)
            self.documents = []
            self._is_indexed = False

    def search(
        self,
        query_text: str,
        top_k: int = 30,
    ) -> List[Dict[str, Any]]:
        """Search historical documents for Top-K lexical matches.

        Returns structured dictionaries containing case details and 'score' (lexical relevance).
        """
        if not self._is_indexed or self.vectorizer is None or self.tfidf_matrix is None or not query_text.strip():
            return []

        try:
            q_vec = self.vectorizer.transform([query_text])
            sims = cosine_similarity(q_vec, self.tfidf_matrix).flatten()

            # Find top_k indices sorted descending
            top_indices = sims.argsort()[::-1][:top_k]

            results: List[Dict[str, Any]] = []
            for rank_idx, idx in enumerate(top_indices):
                score = round(float(sims[idx]), 4)
                doc = self.documents[idx]
                results.append({
                    "case_id": doc["case_id"],
                    "document_id": doc["document_id"],
                    "conversation_id": doc["conversation_id"],
                    "turn_index": doc["turn_index"],
                    "customer_message": doc["customer_message"],
                    "relevant_context": doc["relevant_context"],
                    "brand_response": doc["brand_response"],
                    "metadata": doc.get("metadata", {}),
                    "score": score,
                    "lexical_score": score,
                })

            return results
        except Exception as e:
            logger.error("Lexical search failed: %s", e)
            return []
