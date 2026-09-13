"""Conversation Graph Builder for Twitter Support Threads.

Reconstructs the directed conversation graph from AmazonHelp support cases:
- tweet_id -> tweet record
- in_response_to_tweet_id parent relationships
- Branching conversations & multiple responses
- Resilient lookup handling missing/malformed relationships
"""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
from typing import Any, Dict, List, Optional, Set, Tuple
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class TweetRecord:
    """Represents a single tweet node in the conversation graph."""
    tweet_id: int
    author_id: str
    role: str  # "CUSTOMER" or "BRAND"
    text: str
    in_response_to_tweet_id: Optional[int] = None
    turn_index: int = 0
    conversation_id: Optional[int] = None
    case_id: Optional[str] = None
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tweet_id": self.tweet_id,
            "author_id": self.author_id,
            "role": self.role,
            "text": self.text,
            "in_response_to_tweet_id": self.in_response_to_tweet_id,
            "turn_index": self.turn_index,
            "conversation_id": self.conversation_id,
            "case_id": self.case_id,
            "created_at": self.created_at,
        }


class ConversationGraph:
    """Directed graph of support tweets linked by reply parent pointers."""

    def __init__(self) -> None:
        self.tweets: Dict[int, TweetRecord] = {}
        self.parent_map: Dict[int, int] = {}
        self.children_map: Dict[int, List[int]] = {}
        self.conversation_tweets: Dict[int, List[int]] = {}
        self.root_tweets: Set[int] = set()

    def add_tweet(self, tweet: TweetRecord) -> None:
        """Add a tweet record and update graph links."""
        tid = tweet.tweet_id
        if tid in self.tweets:
            # If already present, merge attributes if previous was placeholder
            existing = self.tweets[tid]
            if not existing.text and tweet.text:
                existing.text = tweet.text
            if not existing.in_response_to_tweet_id and tweet.in_response_to_tweet_id:
                existing.in_response_to_tweet_id = tweet.in_response_to_tweet_id
                self.parent_map[tid] = tweet.in_response_to_tweet_id
                self.children_map.setdefault(tweet.in_response_to_tweet_id, []).append(tid)
            return

        self.tweets[tid] = tweet

        parent_id = tweet.in_response_to_tweet_id
        if parent_id is not None:
            self.parent_map[tid] = parent_id
            self.children_map.setdefault(parent_id, []).append(tid)
        else:
            self.root_tweets.add(tid)

        cid = tweet.conversation_id
        if cid is not None:
            self.conversation_tweets.setdefault(cid, []).append(tid)

    def get_tweet(self, tweet_id: int) -> Optional[TweetRecord]:
        return self.tweets.get(tweet_id)

    def get_parent(self, tweet_id: int) -> Optional[TweetRecord]:
        parent_id = self.parent_map.get(tweet_id)
        return self.tweets.get(parent_id) if parent_id is not None else None

    def get_children(self, tweet_id: int) -> List[TweetRecord]:
        child_ids = self.children_map.get(tweet_id, [])
        return [self.tweets[cid] for cid in child_ids if cid in self.tweets]

    def get_ancestor_path(self, tweet_id: int, max_depth: int = 50) -> List[TweetRecord]:
        """Return the ancestor path from root down to (and including) tweet_id.
        
        Handles cycles, missing nodes, and depth caps gracefully.
        """
        path: List[TweetRecord] = []
        curr_id: Optional[int] = tweet_id
        visited: Set[int] = set()

        while curr_id is not None and curr_id not in visited and len(path) < max_depth:
            visited.add(curr_id)
            rec = self.tweets.get(curr_id)
            if rec is None:
                break
            path.append(rec)
            curr_id = self.parent_map.get(curr_id)

        # Reverse so path is strictly chronological: [root, ..., parent, tweet_id]
        return path[::-1]

    def get_preceding_context(self, customer_tweet_id: int) -> List[TweetRecord]:
        """Return all ancestor tweets preceding customer_tweet_id in chronological order."""
        path = self.get_ancestor_path(customer_tweet_id)
        if path and path[-1].tweet_id == customer_tweet_id:
            return path[:-1]
        return path


def build_conversation_graph(cases_df: pd.DataFrame) -> Tuple[ConversationGraph, Dict[str, Any]]:
    """Build a ConversationGraph from AmazonHelp support cases DataFrame.
    
    Robustly tracks:
    - Parent references from brand response -> customer tweet
    - Thread-level sequential links from subsequent customer tweets -> prior brand responses
    - Multiple brand replies to the same customer tweet (split tweets / branching)
    - Branching customer replies
    """
    graph = ConversationGraph()
    diagnostics: Dict[str, Any] = {
        "total_cases_processed": len(cases_df),
        "total_tweets": 0,
        "customer_tweets": 0,
        "brand_tweets": 0,
        "unique_conversations": 0,
        "multiple_responses_count": 0,
        "branching_conversations_count": 0,
        "unresolved_parents_count": 0,
        "root_tweets_count": 0,
    }

    # Sort once upfront by conversation_id and turn_index for blazing fast streaming
    sorted_df = cases_df.sort_values(["conversation_id", "turn_index"])
    diagnostics["unique_conversations"] = int(cases_df["conversation_id"].nunique())

    cust_response_counts: Dict[int, int] = {}
    curr_cid: Optional[int] = None
    prev_brand_tid: Optional[int] = None
    has_branching = False
    seen_cust_tids: Set[int] = set()

    for row in sorted_df.itertuples(index=False):
        cid = int(row.conversation_id)
        if cid != curr_cid:
            if has_branching:
                diagnostics["branching_conversations_count"] += 1
            curr_cid = cid
            prev_brand_tid = None
            has_branching = False
            seen_cust_tids = set()

        cust_tid = int(row.customer_tweet_id)
        resp_tid = int(row.response_tweet_id)
        turn_idx = int(row.turn_index)
        cust_author = str(getattr(row, "customer_author_id", "CUSTOMER"))
        case_id = str(getattr(row, "case_id", ""))

        # Strictly use canonical clean representations - never fall back silently to raw Twitter text
        cust_clean_val = getattr(row, "customer_message_clean", None)
        cust_text = str(cust_clean_val).strip() if cust_clean_val is not None else ""

        brand_clean_val = getattr(row, "brand_response_clean", None)
        brand_text = str(brand_clean_val).strip() if brand_clean_val is not None else ""

        cust_response_counts[cust_tid] = cust_response_counts.get(cust_tid, 0) + 1

        if cust_tid in seen_cust_tids:
            has_branching = True
        seen_cust_tids.add(cust_tid)

        cust_parent = prev_brand_tid if prev_brand_tid is not None else None

        # 1. Customer node
        cust_node = TweetRecord(
            tweet_id=cust_tid,
            author_id=cust_author,
            role="CUSTOMER",
            text=cust_text,
            in_response_to_tweet_id=cust_parent,
            turn_index=turn_idx,
            conversation_id=cid,
            case_id=case_id,
            created_at=getattr(row, "created_at", None) if pd.notna(getattr(row, "created_at", None)) else None,
        )
        graph.add_tweet(cust_node)

        # 2. Brand node
        brand_node = TweetRecord(
            tweet_id=resp_tid,
            author_id="AmazonHelp",
            role="BRAND",
            text=brand_text,
            in_response_to_tweet_id=cust_tid,
            turn_index=turn_idx + 1,
            conversation_id=cid,
            case_id=case_id,
            created_at=getattr(row, "created_at", None) if pd.notna(getattr(row, "created_at", None)) else None,
        )
        graph.add_tweet(brand_node)

        prev_brand_tid = resp_tid

    if has_branching:
        diagnostics["branching_conversations_count"] += 1

    # Compute diagnostics
    diagnostics["total_tweets"] = len(graph.tweets)
    diagnostics["customer_tweets"] = sum(1 for t in graph.tweets.values() if t.role == "CUSTOMER")
    diagnostics["brand_tweets"] = sum(1 for t in graph.tweets.values() if t.role == "BRAND")
    diagnostics["root_tweets_count"] = len(graph.root_tweets)
    diagnostics["multiple_responses_count"] = sum(1 for count in cust_response_counts.values() if count > 1)
    diagnostics["unresolved_parents_count"] = sum(
        1 for tid, pid in graph.parent_map.items() if pid not in graph.tweets
    )

    logger.info(
        f"Graph reconstructed: {diagnostics['total_tweets']} tweets "
        f"({diagnostics['customer_tweets']} cust, {diagnostics['brand_tweets']} brand) "
        f"across {diagnostics['unique_conversations']} conversations."
    )
    return graph, diagnostics
