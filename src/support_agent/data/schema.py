"""
Canonical Data Schema for AmazonHelp Support Cases.

This module defines the foundational schema for the evidence-grounded
support agent. Each instance represents a single support case:
    Conversation History (context)
    + Current Customer Message
    + Historical Amazon Response

Dataset Provenance:
- Source: Customer Support on Twitter (twcs.csv) filtered for @AmazonHelp.
- Granularity: One support turn/interaction per case (not an isolated tweet).
- Invariants:
    * 0 null values across canonical columns.
    * case_id and response_tweet_id are strictly 1:1 and unique.
    * Multi-turn conversations share the same conversation_id.
"""

from __future__ import annotations

import ast
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Union


@dataclass
class TurnContext:
    """Represents a single conversational turn in the thread history preceding or including this case."""

    role: str  # 'CUSTOMER' or 'BRAND'
    author: str  # e.g., '184337' or 'AmazonHelp'
    text: str  # Original tweet text for this turn

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TurnContext:
        return cls(
            role=str(data.get("role", "")).strip(),
            author=str(data.get("author", "")).strip(),
            text=str(data.get("text", "")).strip(),
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "author": self.author,
            "text": self.text,
        }


@dataclass
class SupportCase:
    """
    Canonical representation of an AmazonHelp support case.

    Each row conceptually models an agent decision point: given the conversation
    history and the latest customer inquiry, what was the Amazon representative's response?
    """

    # --- Core Identifiers ---
    case_id: str
    conversation_id: int
    response_tweet_id: int
    customer_tweet_id: int
    customer_author_id: str
    turn_index: int

    # --- Message Content ---
    customer_message_original: str
    customer_message_clean: str
    brand_response_original: str
    brand_response_clean: str

    # --- Conversational History & Context ---
    # Structured sequence of prior/current turns in original text
    context: List[TurnContext] = field(default_factory=list)
    # Cleaned multi-turn dialogue text
    context_clean: str = ""

    # --- Thread Structure Metadata ---
    thread_length: int = 0
    thread_customer_turns: int = 0
    thread_brand_turns: int = 0

    # --- Data Hygiene & Linguistic Signals ---
    language: str = "en"
    quality_status: str = "OK"

    # --- Response Taxonomy ---
    # ABSENT in the processed dataset: will be populated in downstream taxonomy & intent phases
    response_type: Optional[str] = None

    # --- Auxiliary Pipeline Attributes (Present in Dataset) ---
    model_input: str = ""
    rag_document: str = ""
    customer_length: int = 0
    response_length: int = 0
    is_short_customer: bool = False
    is_short_response: bool = False

    def validate(self) -> None:
        """Validate structural and semantic invariants for this case."""
        if not self.case_id or not isinstance(self.case_id, str):
            raise ValueError(f"Invalid case_id: {self.case_id!r}")

        if self.conversation_id <= 0:
            raise ValueError(f"conversation_id must be positive: {self.conversation_id}")

        if self.response_tweet_id <= 0:
            raise ValueError(f"response_tweet_id must be positive: {self.response_tweet_id}")

        if self.customer_tweet_id <= 0:
            raise ValueError(f"customer_tweet_id must be positive: {self.customer_tweet_id}")

        if self.turn_index < 0:
            raise ValueError(f"turn_index cannot be negative: {self.turn_index}")

        if not self.customer_message_original:
            raise ValueError("customer_message_original cannot be empty")

        if not self.brand_response_original:
            raise ValueError("brand_response_original cannot be empty")

        if self.thread_length < 2:
            raise ValueError(f"thread_length must be >= 2 for support interaction, got {self.thread_length}")

        if not isinstance(self.context, list):
            raise TypeError(f"context must be a list of TurnContext, got {type(self.context)}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SupportCase:
        """Parse a support case from a dictionary (e.g. from Parquet, CSV, or JSON)."""
        # Parse context
        raw_context = data.get("context", [])
        parsed_context: List[TurnContext] = []

        if isinstance(raw_context, str):
            try:
                raw_context = json.loads(raw_context)
            except Exception:
                try:
                    raw_context = ast.literal_eval(raw_context)
                except Exception:
                    raw_context = []

        if hasattr(raw_context, "__iter__") and not isinstance(raw_context, (str, bytes, dict)):
            for item in raw_context:
                if isinstance(item, TurnContext):
                    parsed_context.append(item)
                elif isinstance(item, dict):
                    parsed_context.append(TurnContext.from_dict(item))
                elif isinstance(item, (list, tuple)) and len(item) >= 3:
                    parsed_context.append(TurnContext(role=str(item[0]), author=str(item[1]), text=str(item[2])))

        # Fallback aliases
        cust_orig = data.get("customer_message_original") or data.get("customer_message", "")
        brand_orig = data.get("brand_response_original") or data.get("brand_response", "")

        return cls(
            case_id=str(data["case_id"]),
            conversation_id=int(data["conversation_id"]),
            response_tweet_id=int(data["response_tweet_id"]),
            customer_tweet_id=int(data["customer_tweet_id"]),
            customer_author_id=str(data.get("customer_author_id", "")),
            turn_index=int(data.get("turn_index", 0)),
            customer_message_original=str(cust_orig),
            customer_message_clean=str(data.get("customer_message_clean", "")),
            brand_response_original=str(brand_orig),
            brand_response_clean=str(data.get("brand_response_clean", "")),
            context=parsed_context,
            context_clean=str(data.get("context_clean", "")),
            thread_length=int(data.get("thread_length", 0)),
            thread_customer_turns=int(data.get("thread_customer_turns", 0)),
            thread_brand_turns=int(data.get("thread_brand_turns", 0)),
            language=str(data.get("language", "en")),
            quality_status=str(data.get("quality_status", "OK")),
            response_type=data.get("response_type"),
            model_input=str(data.get("model_input", "")),
            rag_document=str(data.get("rag_document", "")),
            customer_length=int(data.get("customer_length", 0)),
            response_length=int(data.get("response_length", 0)),
            is_short_customer=bool(data.get("is_short_customer", False)),
            is_short_response=bool(data.get("is_short_response", False)),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert support case to a JSON-serializable dictionary."""
        d = asdict(self)
        d["context"] = [t.to_dict() for t in self.context]
        return d


# Documentation of dataset columns and status
CANONICAL_COLUMNS: List[str] = [
    "case_id",
    "conversation_id",
    "response_tweet_id",
    "customer_tweet_id",
    "turn_index",
    "customer_author_id",
    "customer_message",
    "brand_response",
    "context",
    "thread_length",
    "thread_customer_turns",
    "thread_brand_turns",
    "customer_message_original",
    "brand_response_original",
    "customer_message_clean",
    "brand_response_clean",
    "context_clean",
    "model_input",
    "rag_document",
    "customer_length",
    "response_length",
    "is_short_customer",
    "is_short_response",
    "language",
    "quality_status",
]

ABSENT_COLUMNS: Dict[str, str] = {
    "response_type": (
        "Absent from raw Twitter data and initial case extraction. "
        "Will be populated during downstream intent taxonomy / response strategy stages "
        "(e.g., direct_answer, clarify_info, escalate_human, redirect_link)."
    )
}
