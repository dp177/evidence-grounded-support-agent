"""Deterministic Context Selection Engine for Customer Support Threads.

Selects the most decision-relevant preceding conversation turns to accompany
the current customer inquiry and brand response.

Criteria:
1. Recency
2. Operational identifiers / entities (order numbers, currency, tracking, postal codes)
3. Delivery & tracking status
4. Customer action states ("already checked", "already contacted", "already provided", "waiting period exceeded")
5. Temporal deadlines and dates
6. Lexical & semantic overlap with current customer message
7. Root problem anchor (turn 0)
8. Dialogue-role relationship (immediate preceding brand prompts / commitments)
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional, Set, Tuple

# Pre-compiled operational regex patterns
ORDER_NUMBER_PATTERN = re.compile(r"\b(?:\d{3}-\d{7}-\d{7}|\d{17}|4__credit_card__\w*)\b", re.IGNORECASE)
MONEY_PATTERN = re.compile(r"(?:[\$£€]\s*\d+|\b\d+\s*(?:dollars?|pounds?|rupees?|rs\.?|cents?|pence)\b|\brefund(?:ed)?\b|\bcharged?\b)", re.IGNORECASE)
COURIER_PATTERN = re.compile(r"\b(?:hermes|usps|ups|fedex|royal\s*mail|blue\s*dart|bluedart|dhl|dpd|yodel|ontrac|carrier|courier|driver)\b", re.IGNORECASE)
POSTAL_CODE_PATTERN = re.compile(r"\b(?:[a-z]{1,2}\d[a-z\d]?\s*\d[a-z]{2}|\d{5}(?:-\d{4})?|\d{6})\b", re.IGNORECASE)
TRACKING_STATUS_PATTERN = re.compile(r"\b(?:tracking|dispatched?|shipped?|in\s*transit|out\s*for\s*delivery|delivered|undelivered|package|parcel|order\s*status)\b", re.IGNORECASE)

# Action / Customer State phrases
ALREADY_CHECKED_PATTERN = re.compile(r"\b(?:already\s*checked|checked\s*(?:the\s*)?tracking|app\s*says|website\s*says|tracking\s*says|shows\s*(?:as\s*)?delivered|marked\s*(?:as\s*)?delivered)\b", re.IGNORECASE)
ALREADY_CONTACTED_PATTERN = re.compile(r"\b(?:already\s*contacted|spoke\s*(?:to|with)|called\s*(?:the\s*)?(?:carrier|courier|driver|customer\s*service)|contacted\s*(?:the\s*)?seller)\b", re.IGNORECASE)
ALREADY_PROVIDED_PATTERN = re.compile(r"\b(?:already\s*provided|already\s*sent|sent\s*(?:a\s*)?dm|given\s*details|provided\s*details|details\s*sent|order\s*number\s*above)\b", re.IGNORECASE)
WAITING_WINDOW_PATTERN = re.compile(r"\b(?:waited|waiting\s*for|been\s*waiting|told\s*to\s*wait|still\s*nothing|still\s*waiting|\d+\s*(?:days?|hours?|weeks?)\s*(?:ago|later)|passed\s*(?:the\s*)?date|exceeded)\b", re.IGNORECASE)
TEMPORAL_DEADLINE_PATTERN = re.compile(r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|yesterday|tomorrow|today|due\s*date|promised\s*date|estimated\s*delivery)\b", re.IGNORECASE)
BRAND_COMMITMENT_PATTERN = re.compile(r"\b(?:file\s*a\s*claim|refund\s*has\s*been|please\s*allow|wait\s*\d+\s*(?:hours?|business\s*days?)|investigat(?:e|ing)|replacement\s*order)\b", re.IGNORECASE)

STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to", "for", "with", "about",
    "by", "of", "from", "is", "am", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "do", "does", "did", "i", "me", "my", "you", "your", "it", "its", "we", "they", "this",
    "that", "these", "those", "hi", "hello", "please", "thanks", "thank", "amazon", "help", "amazonhelp"
}


def tokenize(text: str) -> Set[str]:
    """Tokenize text into lowercase alphanumeric words excluding stopwords."""
    words = re.findall(r"\b[a-zA-Z0-9_-]{2,}\b", text.lower())
    return {w for w in words if w not in STOPWORDS}


@dataclass
class ScoredTurn:
    """Represents a historical turn with an inspectable relevance score."""
    turn_index: int
    role: str
    author: str
    text: str
    tweet_id: Optional[int] = None
    relevance_score: float = 0.0
    matched_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "turn_index": self.turn_index,
            "role": self.role,
            "author": self.author,
            "text": self.text,
            "tweet_id": self.tweet_id,
            "relevance_score": round(self.relevance_score, 4),
            "matched_reasons": self.matched_reasons,
        }


def score_turn(
    turn: Dict[str, Any],
    turn_idx: int,
    total_preceding_turns: int,
    current_tokens: Set[str],
) -> ScoredTurn:
    """Calculate transparent relevance score for a preceding conversation turn."""
    role = str(turn.get("role", "CUSTOMER")).upper()
    author = str(turn.get("author", ""))
    text = str(turn.get("text", "")).strip()
    tid = turn.get("tweet_id")

    score = 0.0
    reasons: List[str] = []

    # 1. Recency score: decay from 1.0 based on distance to current turn
    distance = total_preceding_turns - 1 - turn_idx
    recency_bonus = max(0.0, 1.0 - (0.12 * distance))
    score += recency_bonus
    reasons.append(f"recency:{recency_bonus:.2f}")

    # 2. Operational Identifiers / Entities
    if ORDER_NUMBER_PATTERN.search(text):
        score += 2.5
        reasons.append("order_number_present")

    if MONEY_PATTERN.search(text):
        score += 2.0
        reasons.append("financial_terms")

    if COURIER_PATTERN.search(text):
        score += 1.8
        reasons.append("carrier_courier_mention")

    if POSTAL_CODE_PATTERN.search(text):
        score += 1.5
        reasons.append("postal_code_present")

    # 3. Delivery / Tracking State
    if TRACKING_STATUS_PATTERN.search(text):
        score += 1.5
        reasons.append("delivery_tracking_terms")

    # 4. Action / Customer State Signals
    if ALREADY_CHECKED_PATTERN.search(text):
        score += 2.5
        reasons.append("already_checked_tracking")

    if ALREADY_CONTACTED_PATTERN.search(text):
        score += 2.5
        reasons.append("already_contacted_carrier")

    if ALREADY_PROVIDED_PATTERN.search(text):
        score += 2.0
        reasons.append("details_already_provided")

    if WAITING_WINDOW_PATTERN.search(text):
        score += 2.5
        reasons.append("waiting_window_exceeded")

    # 5. Temporal Deadlines
    if TEMPORAL_DEADLINE_PATTERN.search(text):
        score += 1.2
        reasons.append("temporal_deadline_anchor")

    # 6. Lexical Overlap with Current Customer Turn
    turn_tokens = tokenize(text)
    if current_tokens and turn_tokens:
        overlap = turn_tokens.intersection(current_tokens)
        overlap_ratio = len(overlap) / len(current_tokens)
        if overlap_ratio > 0.10:
            overlap_score = round(2.5 * overlap_ratio, 3)
            score += overlap_score
            reasons.append(f"lexical_overlap:{overlap_score:.2f}({','.join(list(overlap)[:3])})")

    # 7. Root Problem Anchor (Turn 0)
    if turn_idx == 0 and role == "CUSTOMER":
        score += 1.8
        reasons.append("root_customer_problem_anchor")

    # 8. Dialogue Role Relationships
    if distance == 0 and role == "BRAND":
        # Immediate preceding brand turn (what the customer is directly answering)
        score += 1.5
        reasons.append("immediate_preceding_brand_prompt")

    if role == "BRAND" and BRAND_COMMITMENT_PATTERN.search(text):
        score += 1.5
        reasons.append("brand_commitment_instruction")

    return ScoredTurn(
        turn_index=turn_idx,
        role=role,
        author=author,
        text=text,
        tweet_id=int(tid) if tid is not None and str(tid).isdigit() else None,
        relevance_score=score,
        matched_reasons=reasons,
    )


def select_relevant_context(
    preceding_turns: List[Dict[str, Any]],
    current_customer_message: str,
    max_context_turns: int = 6,
) -> Tuple[str, List[Optional[int]], List[float], List[Dict[str, Any]]]:
    """Select up to max_context_turns from preceding_turns using deterministic scoring.
    
    Args:
        preceding_turns: Chronological list of turns before the current customer inquiry.
        current_customer_message: The current customer turn being answered.
        max_context_turns: Maximum historical turns to preserve (default: 6).
        
    Returns:
        Tuple of:
        - formatted_context_str: Clean chronological multi-line string "ROLE: text"
        - selected_tweet_ids: List of tweet_ids of the selected turns
        - selected_scores: List of float scores of the selected turns
        - scored_turn_details: List of ScoredTurn dicts
    """
    if not preceding_turns:
        return "", [], [], []

    current_tokens = tokenize(current_customer_message)
    total_turns = len(preceding_turns)

    # 1. Score every candidate turn
    scored_turns: List[ScoredTurn] = []
    for i, t in enumerate(preceding_turns):
        turn_dict = t.to_dict() if hasattr(t, "to_dict") else dict(t)
        scored = score_turn(turn_dict, turn_idx=i, total_preceding_turns=total_turns, current_tokens=current_tokens)
        scored_turns.append(scored)

    # 2. Select top K turns
    if len(scored_turns) <= max_context_turns:
        selected_turns = scored_turns
    else:
        # Sort by relevance_score descending, pick top max_context_turns
        ranked = sorted(scored_turns, key=lambda st: st.relevance_score, reverse=True)
        selected_turns = ranked[:max_context_turns]
        # Re-sort strictly chronologically by original turn_index
        selected_turns = sorted(selected_turns, key=lambda st: st.turn_index)

    # 3. Format output
    lines = []
    selected_tids: List[Optional[int]] = []
    selected_scores: List[float] = []
    turn_details: List[Dict[str, Any]] = []

    for st in selected_turns:
        lines.append(f"{st.role}: {st.text}")
        selected_tids.append(st.tweet_id)
        selected_scores.append(round(st.relevance_score, 4))
        turn_details.append(st.to_dict())

    formatted_context = "\n".join(lines)
    return formatted_context, selected_tids, selected_scores, turn_details
