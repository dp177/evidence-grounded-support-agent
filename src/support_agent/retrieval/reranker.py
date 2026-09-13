"""Candidate Reranker for Semantic Retrieval.

Applies lexical, intent, state, and boilerplate penalty scoring on top of semantic similarity.
Provides conversation deduplication.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional
import yaml

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# Configurable defaults
DEFAULT_WEIGHTS = {
    "semantic": 1.0,
    "lexical": 0.2,
    "intent": 0.1,
    "area": 0.1,
    "state": 0.1,
    "action_penalty": -0.15,
}

# Generic words to de-emphasize in lexical matching
LEXICAL_STOP_WORDS = {"order", "package", "delivery", "refund", "help", "amazon", "please", "hi", "hello", "thanks"}

# Patterns that indicate a generic boilerplate response
BOILERPLATE_PATTERNS = [
    r"reach us via phone or chat",
    r"send us a dm",
    r"dm us",
    r"sorry to hear",
    r"we'd like to help",
    r"provide us with more details",
    r"can you please confirm",
    r"we would like to look into this",
    r"click the link below",
    r"sorry for the wait",
    r"sorry for the frustration",
]


class CandidateReranker:
    """Reranks historical candidates based on multi-signal compatibility."""

    def __init__(self, config_path: str = "configs/reranking.yaml"):
        self.weights = DEFAULT_WEIGHTS.copy()
        self.max_results_per_conversation = 1
        self._load_config(config_path)
        
        self.boilerplate_regexes = [re.compile(p, re.IGNORECASE) for p in BOILERPLATE_PATTERNS]

    def _load_config(self, config_path: str) -> None:
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            
            rerank_cfg = cfg.get("reranking", {})
            weights = rerank_cfg.get("weights", {})
            for k, v in weights.items():
                if k in self.weights:
                    self.weights[k] = float(v)
            
            self.max_results_per_conversation = rerank_cfg.get("max_results_per_conversation", 1)
        except Exception as e:
            logger.warning("Could not load %s, using defaults. Error: %s", config_path, str(e))

    def _compute_lexical_similarity(self, query: str, candidates: List[Dict[str, Any]]) -> List[float]:
        """Compute TF-IDF cosine similarity between query and candidate customer_message."""
        if not query or not candidates:
            return [0.0] * len(candidates)

        texts = [query] + [c.get("customer_message", "") for c in candidates]
        
        # Use simple tokenization, ignoring our custom generic stop words
        vectorizer = TfidfVectorizer(stop_words=list(LEXICAL_STOP_WORDS), token_pattern=r"(?u)\b\w+\b")
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            # Row 0 is query, Row 1..N are candidates
            cosine_sims = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
            return cosine_sims.tolist()
        except ValueError:
            # E.g. if all texts are empty or only contain stop words
            return [0.0] * len(candidates)

    def _check_overlap(self, predicted: Optional[List[str]], actual: Optional[List[str]]) -> float:
        """Return 1.0 if there is any intersection, else 0.0."""
        if not predicted or actual is None:
            return 0.0
        
        # In actual metadata, if it is a string instead of a list, wrap it
        if isinstance(actual, str):
            if actual.strip() == "":
                actual_set = set()
            else:
                actual_set = {actual}
        elif isinstance(actual, list):
            actual_set = set(actual)
        else:
            return 0.0

        if not actual_set:
            return 0.0

        pred_set = set(predicted)
        if pred_set.intersection(actual_set):
            return 1.0
        return 0.0

    def _compute_action_penalty(self, brand_response: str) -> float:
        """Return a penalty score (1.0 if generic, 0.0 if not) for generic boilerplate responses."""
        if not brand_response:
            return 0.0
        
        for regex in self.boilerplate_regexes:
            if regex.search(brand_response):
                return 1.0
        return 0.0

    def rerank(
        self,
        query_text: str,
        candidates: List[Dict[str, Any]],
        predicted_intents: Optional[List[str]] = None,
        predicted_areas: Optional[List[str]] = None,
        predicted_states: Optional[List[str]] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Rerank candidates and apply conversation deduplication."""
        if not candidates:
            return []

        # 1. Compute lexical scores
        lexical_scores = self._compute_lexical_similarity(query_text, candidates)

        # 2. Score each candidate
        scored_candidates = []
        for i, c in enumerate(candidates):
            semantic_score = c.get("score", 0.0)
            lexical_score = lexical_scores[i] if i < len(lexical_scores) else 0.0
            
            metadata = c.get("metadata", {})
            # Extract historical labels (they may not exist, which is fine)
            raw_intents = metadata.get("intents")
            raw_areas = metadata.get("areas")
            raw_state = metadata.get("state")
            
            intent_score = self._check_overlap(predicted_intents, raw_intents) if raw_intents is not None else None
            area_score = self._check_overlap(predicted_areas, raw_areas) if raw_areas is not None else None
            state_score = self._check_overlap(predicted_states, raw_state) if raw_state is not None else None
            
            brand_response = c.get("brand_response", "")
            action_penalty_flag = self._compute_action_penalty(brand_response)
            action_usefulness = 1.0 - action_penalty_flag

            final_score = (
                self.weights["semantic"] * semantic_score
                + self.weights["lexical"] * (lexical_score if lexical_score is not None else 0.0)
                + self.weights["intent"] * (intent_score if intent_score is not None else 0.0)
                + self.weights["area"] * (area_score if area_score is not None else 0.0)
                + self.weights["state"] * (state_score if state_score is not None else 0.0)
                + self.weights["action_penalty"] * action_penalty_flag
            )

            scored_candidates.append({
                **c,
                "final_score": final_score,
                "rerank_score": final_score,
                "semantic_score": semantic_score,
                "lexical_score": lexical_score,
                "intent_score": intent_score,
                "area_score": area_score,
                "state_score": state_score,
                "action_usefulness": action_usefulness,
                "action_penalty_flag": action_penalty_flag,
            })

        # 3. Sort by final score descending
        scored_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)

        # 4. Deduplicate conversations
        final_results = []
        conversation_counts: Dict[int, int] = {}
        
        for c in scored_candidates:
            cid = c.get("conversation_id")
            if cid is not None:
                count = conversation_counts.get(cid, 0)
                if count < self.max_results_per_conversation:
                    final_results.append(c)
                    conversation_counts[cid] = count + 1
            else:
                final_results.append(c)
            
            if len(final_results) >= top_k:
                break

        for idx, res in enumerate(final_results):
            res["rank"] = idx + 1

        return final_results
