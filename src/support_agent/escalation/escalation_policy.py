"""Escalation Policy Configuration & Evaluators — Phase 10.

Loads deterministic escalation policy rules from configs/escalation.yaml
and provides evaluation functions for:
  - Security & fraud triggers
  - Operational state consistency
  - Classification confidence gates
  - Retrieval quality evaluation
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG_PATH = Path("configs/escalation.yaml")


class EscalationConfig:
    """Encapsulates deterministic escalation configuration."""

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        cfg = config_dict or {}

        # Classification gates
        clf_cfg = cfg.get("classification", {})
        self.min_confidence: float = float(clf_cfg.get("min_confidence", 0.70))
        self.allow_ambiguous_clarification: bool = bool(clf_cfg.get("allow_ambiguous_clarification", True))
        self.block_out_of_scope: bool = bool(clf_cfg.get("block_out_of_scope", False))

        # Security & Fraud
        sec_cfg = cfg.get("security_and_fraud", {})
        self.high_risk_intents: Set[str] = set(sec_cfg.get("high_risk_intents", [
            "ACCOUNT_ACCESS_RECOVERY",
            "PAYMENT_AND_BILLING_DISPUTES",
        ]))
        self.risk_keywords: List[str] = list(sec_cfg.get("risk_keywords", [
            "fraud", "scam", "police", "hacked", "unauthorized", "stolen", "compromised"
        ]))
        self.escalate_on_risk_keywords: bool = bool(sec_cfg.get("escalate_on_risk_keywords", True))

        # Grounding hard blockers
        grnd_cfg = cfg.get("grounding", {})
        self.require_grounded: bool = bool(grnd_cfg.get("require_grounded", True))
        self.max_contradicted_claims: int = int(grnd_cfg.get("max_contradicted_claims", 0))
        self.max_unsupported_claims: int = int(grnd_cfg.get("max_unsupported_claims", 0))
        self.block_unsupported_current_actions: bool = bool(grnd_cfg.get("block_unsupported_current_actions", True))
        self.block_invalid_evidence_ids: bool = bool(grnd_cfg.get("block_invalid_evidence_ids", True))

        # Retrieval quality
        ret_cfg = cfg.get("retrieval", {})
        self.min_top_evidence_score: float = float(ret_cfg.get("min_top_evidence_score", 0.45))
        self.require_evidence_for_resolution: bool = bool(ret_cfg.get("require_evidence_for_resolution", True))

        # State inconsistency
        self.state_inconsistency_rules: Dict[str, Any] = cfg.get("state_inconsistency", {})

    @classmethod
    def from_yaml(cls, path: Optional[Path | str] = None) -> EscalationConfig:
        p = Path(path) if path else _DEFAULT_CONFIG_PATH
        if not p.exists():
            logger.warning(f"Escalation config {p} not found, using default settings.")
            return cls({})
        try:
            with open(p, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return cls(data)
        except Exception as e:
            logger.error(f"Failed to load escalation config from {p}: {e}")
            return cls({})


# ---------------------------------------------------------------------------
# Evaluator Helpers
# ---------------------------------------------------------------------------

def detect_security_fraud_signals(
    customer_conversation: Dict[str, Any],
    classification: Dict[str, Any],
    config: EscalationConfig,
) -> List[Dict[str, str]]:
    """Check for security and fraud triggers in intent and conversation text."""
    triggers: List[Dict[str, str]] = []

    # 1. Intent check
    primary_intent = classification.get("primary_intent") or ""
    all_intents = set(classification.get("intents") or []) | {primary_intent}
    matched_high_risk = all_intents & config.high_risk_intents
    if matched_high_risk:
        triggers.append({
            "type": "SECURITY",
            "reason_code": "HIGH_RISK_SECURITY",
            "message": f"Intent '{list(matched_high_risk)[0]}' requires mandatory human specialist review.",
        })

    # 2. Text keyword check
    msg = str(customer_conversation.get("customer_message") or "").lower()
    ctx = str(customer_conversation.get("context") or "").lower()
    full_text = f"{ctx} {msg}"

    if config.escalate_on_risk_keywords:
        for kw in config.risk_keywords:
            if re.search(rf"\b{re.escape(kw)}\b", full_text, re.IGNORECASE):
                if kw in ("fraud", "scam", "police"):
                    reason_code = "FRAUD_CONCERN"
                    trig_type = "FRAUD"
                elif kw in ("kill", "threat"):
                    reason_code = "SAFETY_THREAT"
                    trig_type = "SECURITY"
                else:
                    reason_code = "HIGH_RISK_SECURITY"
                    trig_type = "SECURITY"

                triggers.append({
                    "type": trig_type,
                    "reason_code": reason_code,
                    "message": f"Customer conversation mentions severe risk keyword: '{kw}'.",
                })
                break  # one keyword match is sufficient

    return triggers


def check_state_consistency(
    states: List[str],
    response_text: str,
    customer_conversation: Dict[str, Any],
    config: EscalationConfig,
) -> List[Dict[str, str]]:
    """Evaluate whether the generated response is operationally consistent with conversation states.

    Operates on ACTIONS already completed by the customer vs actions demanded by the assistant,
    rather than merely the existence of a state label.
    """
    violations: List[Dict[str, str]] = []
    if not states or not response_text:
        return violations

    resp = response_text.lower()
    state_set = set(states)

    cust_msg = str(customer_conversation.get("customer_message") or "").lower()
    ctx = str(customer_conversation.get("context") or "").lower()
    full_text = f"{ctx} {cust_msg}".strip()

    for st in state_set:
        # Special case: asking where/how to locate tracking number or order number is NOT inconsistent
        if st == "TRACKING_ALREADY_CHECKED":
            if re.search(r"\b(?:where|how)\b.*\b(?:find|locate|get|check|see)\b.*\b(?:tracking|order)\s*(?:number|id|#)?\b", cust_msg):
                continue

        rule = config.state_inconsistency_rules.get(st)
        if not rule:
            continue
        patterns = rule.get("blocked_response_patterns", [])
        code = rule.get("reason_code", "INCONSISTENT_WITH_STATE")
        msg = rule.get("message", f"Response is inconsistent with state '{st}'.")

        # Handle DETAILS_ALREADY_PROVIDED based on what actions were actually completed
        if st == "DETAILS_ALREADY_PROVIDED":
            matched_pat = None
            for pat in patterns:
                if re.search(pat, resp, re.IGNORECASE):
                    matched_pat = pat
                    break

            if matched_pat:
                if full_text:
                    asking_order_id = bool(re.search(r"\b(?:order\s+(?:number|id|#)|order\s+reference|account\s+details)\b", resp, re.IGNORECASE))
                    customer_asserted_order_provided = bool(re.search(
                        r"\b(?:already|previously)\s+(?:sent|provided|given|shared)\b.*?\b(?:order\s+(?:details|number|id|#)|details|information|info)\b",
                        full_text,
                        re.IGNORECASE,
                    ))
                    customer_has_order_id = customer_asserted_order_provided or bool(re.search(
                        r"\b\d{3}-\d{7}-\d{7}\b|\border\s*(?:#|number|id)?\s*:?\s*\d{5,}\b",
                        full_text,
                        re.IGNORECASE,
                    ))
                    asking_email = bool(re.search(r"\b(?:email(?:\s+address)?)\b", resp, re.IGNORECASE))
                    customer_has_email = bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", full_text))

                    # Asking for missing order number or email when not yet provided is legitimate follow-up
                    if asking_order_id and not customer_has_order_id:
                        continue
                    if asking_email and not customer_has_email:
                        continue

                violations.append({
                    "state": st,
                    "reason_code": code,
                    "matched_pattern": matched_pat,
                    "message": msg,
                })
            continue

        for pat in patterns:
            if re.search(pat, resp, re.IGNORECASE):
                violations.append({
                    "state": st,
                    "reason_code": code,
                    "matched_pattern": pat,
                    "message": msg,
                })
                break

    return violations


def is_clarification_response(response_text: str) -> bool:
    """Determine if a response is a harmless clarification / information-gathering request."""
    if not response_text or not response_text.strip():
        return False
    t = response_text.strip().lower()

    # Ends with question mark and has question phrasing
    has_question = "?" in t
    asking_phrases = [
        "could you please", "can you please", "please provide", "please let us know",
        "let me know", "tell us", "which amazon", "what is your order", "share your order"
    ]
    is_asking = any(p in t for p in asking_phrases)

    # Resolution promises indicate it is NOT purely clarification
    resolution_phrases = [
        "refund has been", "we will deliver", "order is cancelled", "we have credited",
        "replacement has been sent"
    ]
    has_resolution = any(p in t for p in resolution_phrases)

    return (has_question or is_asking) and not has_resolution
