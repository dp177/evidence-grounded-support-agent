"""Majority Intent Classifier Baseline.

Determines the most frequent business intent strictly using the development dataset pool.
Golden evaluation set data is explicitly forbidden during fitting.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
import pandas as pd


# Default taxonomy intent patterns to identify intent distribution in development cases
DEFAULT_DEV_PATTERNS = {
    "DELIVERY_DELAYED": r"\b(?:delayed|delay|late|supposed to arrive|past due|overdue|still not arrived|not arrived yet)\b",
    "PRIME_MEMBERSHIP_MANAGEMENT": r"\b(?:prime membership|amazon prime|cancel prime|prime renewed|prime subscription)\b",
    "DAMAGED_OR_DEFECTIVE_ITEM": r"\b(?:damaged|broken|cracked|shattered|defective|faulty|torn|leaking|not working)\b",
    "DIGITAL_CONTENT_ACCESS": r"\b(?:kindle|fire stick|prime video|ebook|digital content|download|audiobook)\b",
    "CANCEL_ORDER_REQUEST": r"\b(?:cancel.*order|cancellation|cancel this|cancel my item|stop shipment|ordered by mistake)\b",
    "CARRIER_FEEDBACK_AND_INSTRUCTIONS": r"\b(?:delivery (?:driver|guy|agent|person)|courier (?:rude|refused)|left in (?:the )?(?:rain|bin)|safe place|porch|gate code)\b",
    "MARKED_DELIVERED_NOT_RECEIVED": r"\b(?:marked.*delivered|shows.*delivered|says.*delivered|stated.*delivered|delivered.*not received|delivered.*didn\'t receive)\b",
    "WHERE_IS_MY_ORDER": r"\b(?:where is|where\'s|track my|tracking update|track order|when will.*arrive|status of my order)\b",
    "WRONG_ITEM_RECEIVED": r"\b(?:wrong (?:item|product|size|color)|different item|ordered.*received|not what i ordered)\b",
    "REFUND_STATUS_INQUIRY": r"\b(?:where is.*refund|refund status|when.*refund|refund not received|refund credited|money back)\b",
    "ACCOUNT_LOGIN_ISSUES": r"\b(?:can\'t log in|login|password reset|otp|verification code|account locked|hacked)\b",
    "RETURN_PICKUP_ISSUE": r"\b(?:return pickup|pick up.*return|pickup.*courier|courier.*pickup|return.*not picked up|return label)\b",
    "UNRECOGNIZED_OR_DUPLICATE_CHARGE": r"\b(?:charged twice|double charged|unauthorized charge|extra charge|deducted twice|charged my card|why.*charged)\b",
    "MODIFY_ORDER_DETAILS": r"\b(?:change address|change delivery address|update address|modify order|change delivery date)\b",
}

INTENT_TO_AREA = {
    "WHERE_IS_MY_ORDER": "DELIVERY_AND_FULFILLMENT",
    "DELIVERY_DELAYED": "DELIVERY_AND_FULFILLMENT",
    "MARKED_DELIVERED_NOT_RECEIVED": "DELIVERY_AND_FULFILLMENT",
    "CARRIER_FEEDBACK_AND_INSTRUCTIONS": "DELIVERY_AND_FULFILLMENT",
    "DAMAGED_OR_DEFECTIVE_ITEM": "RETURNS_AND_REPLACEMENTS",
    "WRONG_ITEM_RECEIVED": "RETURNS_AND_REPLACEMENTS",
    "RETURN_PICKUP_ISSUE": "RETURNS_AND_REPLACEMENTS",
    "REFUND_STATUS_INQUIRY": "REFUNDS_AND_BILLING",
    "UNRECOGNIZED_OR_DUPLICATE_CHARGE": "REFUNDS_AND_BILLING",
    "CANCEL_ORDER_REQUEST": "ORDER_MANAGEMENT",
    "MODIFY_ORDER_DETAILS": "ORDER_MANAGEMENT",
    "PRIME_MEMBERSHIP_MANAGEMENT": "DIGITAL_SERVICES_AND_PRIME",
    "DIGITAL_CONTENT_ACCESS": "DIGITAL_SERVICES_AND_PRIME",
    "ACCOUNT_LOGIN_ISSUES": "ACCOUNT_ACCESS_AND_SECURITY",
}


class MajorityClassifier:
    """Trivial baseline predicting the single most frequent business intent from the development set."""

    def __init__(self, default_intent: str = "DELIVERY_DELAYED"):
        self.majority_intent_: Optional[str] = default_intent
        self.majority_area_: Optional[str] = INTENT_TO_AREA.get(default_intent, "DELIVERY_AND_FULFILLMENT")
        self.intent_counts_: Dict[str, int] = {}
        self.fitted_: bool = False

    def fit(
        self,
        dev_df: pd.DataFrame,
        golden_conversation_ids: Optional[Set[Any]] = None,
        text_column: str = "customer_message_clean",
        label_column: Optional[str] = None,
    ) -> "MajorityClassifier":
        """Determine the most frequent business intent strictly from development data."""
        # 1. Enforce zero leakage from golden conversations
        if golden_conversation_ids:
            golden_str_ids = {str(gid) for gid in golden_conversation_ids}
            leakage = dev_df["conversation_id"].astype(str).isin(golden_str_ids).sum()
            if leakage > 0:
                raise ValueError(
                    f"CRITICAL: Found {leakage} cases belonging to golden conversations in development training data!"
                )

        # 2. Determine majority intent
        if label_column and label_column in dev_df.columns:
            counts = dev_df[label_column].value_counts().to_dict()
        else:
            # Match regex patterns over clean customer text
            col = text_column if text_column in dev_df.columns else "customer_message"
            counts = {}
            for intent, pat in DEFAULT_DEV_PATTERNS.items():
                match_count = int(
                    dev_df[col].str.contains(pat, case=False, regex=True, na=False).sum()
                )
                counts[intent] = match_count

        self.intent_counts_ = counts
        if counts:
            self.majority_intent_ = max(counts.items(), key=lambda x: x[1])[0]
        else:
            self.majority_intent_ = "DELIVERY_DELAYED"

        self.majority_area_ = INTENT_TO_AREA.get(self.majority_intent_, "DELIVERY_AND_FULFILLMENT")
        self.fitted_ = True
        return self

    def predict(self, cases: List[Dict[str, Any]] | pd.DataFrame) -> List[str]:
        """Predict primary intent for a list of cases."""
        n = len(cases)
        return [self.majority_intent_] * n

    def predict_records(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Predict standardized classification records."""
        records = []
        for _ in cases:
            records.append({
                "classification_status": "NORMAL",
                "areas": [self.majority_area_],
                "intents": [self.majority_intent_],
                "primary_intent": self.majority_intent_,
                "is_multi_intent": False,
                "states": ["INITIAL_INQUIRY"],
                "confidence": 1.0,
            })
        return records
