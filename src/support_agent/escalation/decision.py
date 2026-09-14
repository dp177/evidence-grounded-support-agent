"""Final Decision Engine — Phase 10.

Implements decide_escalation() to evaluate all safety, classification,
state, retrieval, and grounding signals, returning a deterministic
decision: AUTO_HANDLE vs HUMAN_REVIEW, accompanied by stable reason codes.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from support_agent.escalation.escalation_policy import (
    EscalationConfig,
    check_state_consistency,
    detect_security_fraud_signals,
    is_clarification_response,
)
from support_agent.escalation.high_risk import evaluate_high_risk_escalation

logger = logging.getLogger(__name__)


def decide_escalation(
    classification: Dict[str, Any],
    retrieved_evidence: List[Dict[str, Any]],
    generated_reply: str,
    grounding_result: Dict[str, Any],
    customer_conversation: Optional[Dict[str, Any]] = None,
    conversation_state: Optional[List[str]] = None,
    risk_signals: Optional[Dict[str, Any]] = None,
    config: Optional[EscalationConfig] = None,
) -> Dict[str, Any]:
    """
    Decide whether a support message should be auto-handled or escalated to a human.

    Parameters
    ----------
    classification : dict
        Output from ClassifierV2 (primary_intent, intents, states, status, confidence).
    retrieved_evidence : list of dict
        Top retrieved and reranked evidence documents.
    generated_reply : str
        The final proposed customer response.
    grounding_result : dict
        Output from Grounding Checker (grounded, claims, risk_flags, unsupported_claims, etc.).
    customer_conversation : dict, optional
        Contains 'customer_message' and 'context'.
    conversation_state : list of str, optional
        List of operational states. Defaults to classification['states'].
    risk_signals : dict, optional
        Additional runtime risk signals.
    config : EscalationConfig, optional
        Policy configuration instance. If None, loads from configs/escalation.yaml.

    Returns
    -------
    dict
        {
          "decision": "AUTO_HANDLE" | "HUMAN_REVIEW",
          "sub_decision": "RESOLVE" | "CLARIFY" | "ESCALATE",
          "reason_codes": List[str],
          "reason": str,
          "confidence": float,
          "blocking_factors": List[str],
          "state_consistency": Dict[str, Any]
        }
    """
    if config is None:
        config = EscalationConfig.from_yaml()

    customer_conv = customer_conversation or {}
    states = conversation_state if conversation_state is not None else classification.get("states", [])
    if isinstance(states, str):
        states = [states]

    blocking_factors: List[str] = []
    reason_codes: List[str] = []

    # -----------------------------------------------------------------------
    # Gate 1: Empty or Malformed Reply
    # -----------------------------------------------------------------------
    if not generated_reply or not generated_reply.strip() or len(generated_reply.strip()) < 5:
        return {
            "decision": "HUMAN_REVIEW",
            "sub_decision": "ESCALATE",
            "reason_codes": ["MALFORMED_RESPONSE"],
            "reason": "Proposed reply is empty, incomplete, or malformed.",
            "confidence": 0.0,
            "blocking_factors": ["Empty or malformed generated reply."],
            "state_consistency": {"violations": []},
        }

    # -----------------------------------------------------------------------
    # Gate 1b: Deterministic High-Risk Escalation Overrides
    # -----------------------------------------------------------------------
    high_risk_override = evaluate_high_risk_escalation(
        customer_conversation=customer_conv,
        classification=classification,
        conversation_state=states,
    )
    if high_risk_override:
        return {
            "decision": "HUMAN_REVIEW",
            "sub_decision": "ESCALATE",
            "reason_codes": [high_risk_override["reason_code"]],
            "reason": high_risk_override["message"],
            "confidence": 0.0,
            "blocking_factors": [high_risk_override["message"]],
            "state_consistency": {"violations": []},
        }


    # -----------------------------------------------------------------------
    # Gate 2: Grounding Verification Hard Blockers
    # -----------------------------------------------------------------------
    is_grounded = bool(grounding_result.get("grounded", False))
    grnd_status = grounding_result.get("grounding_status", "PASSED" if is_grounded else "FAILED")
    contradicted = grounding_result.get("contradicted_claims", [])
    unsupported = grounding_result.get("unsupported_claims", [])
    risk_flags = grounding_result.get("risk_flags", [])
    invalid_ids = grounding_result.get("invalid_evidence_ids", [])

    if invalid_ids and config.block_invalid_evidence_ids:
        blocking_factors.append(f"Invalid/invented evidence IDs referenced: {invalid_ids}")
        reason_codes.append("INVALID_EVIDENCE_IDS")

    if contradicted and config.max_contradicted_claims == 0:
        blocking_factors.append(f"Contradicted claims detected: {contradicted}")
        reason_codes.append("CONTRADICTED_RESPONSE")

    # Check for unconfirmed current action patterns in risk flags or claims
    current_action_violations = [
        f for f in risk_flags if "current action" in f.lower() or "current-case" in f.lower()
    ]
    if current_action_violations and config.block_unsupported_current_actions:
        blocking_factors.append("Reply asserts unconfirmed current-case actions or promises.")
        reason_codes.append("UNSUPPORTED_CURRENT_ACTION")

    if not is_grounded or grnd_status == "FAILED" or (unsupported and config.max_unsupported_claims == 0):
        if "GROUNDING_FAILURE" not in reason_codes:
            reason_codes.append("GROUNDING_FAILURE")
        if unsupported:
            blocking_factors.append(f"Unsupported factual claims remaining: {unsupported[:2]}")
        else:
            blocking_factors.append("Grounding verification did not pass.")

    # If any grounding failure occurred, escalate to human
    if not is_grounded or grnd_status == "FAILED" or reason_codes:
        main_reason = (
            "The generated reply contains unsupported or contradicted claims that conflict "
            "with the conversation or lack evidence."
        )
        if current_action_violations:
            main_reason = "The generated reply makes an unverified claim about current account status or action taken."
        elif contradicted:
            main_reason = "The generated reply directly contradicts statements in the active conversation."

        return {
            "decision": "HUMAN_REVIEW",
            "sub_decision": "ESCALATE",
            "reason_codes": list(dict.fromkeys(reason_codes)),
            "reason": main_reason,
            "confidence": float(grounding_result.get("grounding_score", 0.0)),
            "blocking_factors": blocking_factors,
            "state_consistency": {"violations": []},
        }

    # -----------------------------------------------------------------------
    # Gate 3: Security & Fraud Risk Triggers
    # -----------------------------------------------------------------------
    sec_triggers = detect_security_fraud_signals(customer_conv, classification, config)
    if sec_triggers:
        for trig in sec_triggers:
            reason_codes.append(trig["reason_code"])
            blocking_factors.append(trig["message"])

        return {
            "decision": "HUMAN_REVIEW",
            "sub_decision": "ESCALATE",
            "reason_codes": list(dict.fromkeys(reason_codes)),
            "reason": sec_triggers[0]["message"],
            "confidence": 0.0,
            "blocking_factors": blocking_factors,
            "state_consistency": {"violations": []},
        }

    # -----------------------------------------------------------------------
    # Gate 4: Classification Scope & Confidence
    # -----------------------------------------------------------------------
    clf_status = str(classification.get("classification_status") or classification.get("status") or "NORMAL").upper()
    primary_intent = str(classification.get("primary_intent") or "UNKNOWN").upper()
    clf_confidence = float(classification.get("confidence", 1.0) if classification.get("confidence") is not None else 1.0)
    is_clarify = is_clarification_response(generated_reply)

    if clf_status == "OUT_OF_SCOPE":
        if config.block_out_of_scope:
            return {
                "decision": "HUMAN_REVIEW",
                "sub_decision": "ESCALATE",
                "reason_codes": ["OUT_OF_SCOPE"],
                "reason": "Customer inquiry falls outside supported Amazon retail support domain.",
                "confidence": clf_confidence,
                "blocking_factors": ["Inquiry classified as OUT_OF_SCOPE."],
                "state_consistency": {"violations": []},
            }
        else:
            return {
                "decision": "AUTO_HANDLE",
                "sub_decision": "RESOLVE",
                "reason_codes": ["SAFE_TO_AUTO_HANDLE"],
                "reason": "Customer inquiry is outside supported Amazon retail domain; safely declined without human escalation.",
                "confidence": clf_confidence,
                "blocking_factors": [],
                "state_consistency": {"violations": []},
            }

    if clf_status == "AMBIGUOUS" or primary_intent == "UNKNOWN":
        if config.allow_ambiguous_clarification and is_clarify:
            # Safe clarification path allowed
            pass
        else:
            return {
                "decision": "HUMAN_REVIEW",
                "sub_decision": "ESCALATE",
                "reason_codes": ["AMBIGUOUS_CLASSIFICATION"],
                "reason": "Customer intent is ambiguous and cannot be safely resolved without human review.",
                "confidence": clf_confidence,
                "blocking_factors": ["Customer intent is ambiguous or unclassified."],
                "state_consistency": {"violations": []},
            }

    if clf_confidence < config.min_confidence:
        if is_clarify and config.allow_ambiguous_clarification:
            pass  # Allow asking clarification on low confidence
        else:
            return {
                "decision": "HUMAN_REVIEW",
                "sub_decision": "ESCALATE",
                "reason_codes": ["LOW_CLASSIFICATION_CONFIDENCE"],
                "reason": f"Classifier confidence ({clf_confidence:.2f}) is below safe auto-handle threshold ({config.min_confidence:.2f}).",
                "confidence": clf_confidence,
                "blocking_factors": [f"Classifier confidence {clf_confidence:.2f} < {config.min_confidence:.2f}"],
                "state_consistency": {"violations": []},
            }

    # -----------------------------------------------------------------------
    # Gate 5: Operational State Inconsistency
    # -----------------------------------------------------------------------
    state_violations = check_state_consistency(states, generated_reply, customer_conv, config)
    if state_violations:
        for sv in state_violations:
            reason_codes.append(sv["reason_code"])
            blocking_factors.append(sv["message"])

        return {
            "decision": "HUMAN_REVIEW",
            "sub_decision": "ESCALATE",
            "reason_codes": list(dict.fromkeys(reason_codes)),
            "reason": state_violations[0]["message"],
            "confidence": clf_confidence,
            "blocking_factors": blocking_factors,
            "state_consistency": {"violations": state_violations},
        }

    # -----------------------------------------------------------------------
    # Gate 6: Retrieval Quality Signals
    # -----------------------------------------------------------------------
    if retrieved_evidence:
        top_score = float(retrieved_evidence[0].get("score", 0.0))
        if top_score < config.min_top_evidence_score and not is_clarify:
            return {
                "decision": "HUMAN_REVIEW",
                "sub_decision": "ESCALATE",
                "reason_codes": ["INSUFFICIENT_EVIDENCE"],
                "reason": f"Top retrieved evidence score ({top_score:.3f}) is below minimum quality threshold ({config.min_top_evidence_score:.2f}).",
                "confidence": top_score,
                "blocking_factors": [f"Top evidence score {top_score:.3f} < {config.min_top_evidence_score:.2f}"],
                "state_consistency": {"violations": []},
            }
    elif not is_clarify and config.require_evidence_for_resolution:
        return {
            "decision": "HUMAN_REVIEW",
            "sub_decision": "ESCALATE",
            "reason_codes": ["INSUFFICIENT_EVIDENCE"],
            "reason": "No relevant historical evidence was retrieved to support resolution.",
            "confidence": 0.0,
            "blocking_factors": ["No evidence retrieved for resolution response."],
            "state_consistency": {"violations": []},
        }

    # -----------------------------------------------------------------------
    # All Safety Gates Passed: AUTO_HANDLE
    # -----------------------------------------------------------------------
    final_confidence = min(clf_confidence, float(grounding_result.get("grounding_score", 1.0)))
    if is_clarify:
        return {
            "decision": "AUTO_HANDLE",
            "sub_decision": "CLARIFY",
            "reason_codes": ["SAFE_CLARIFICATION"],
            "reason": "Proposed response safely requests missing information without making ungrounded claims.",
            "confidence": round(final_confidence, 3),
            "blocking_factors": [],
            "state_consistency": {"violations": []},
        }

    return {
        "decision": "AUTO_HANDLE",
        "sub_decision": "RESOLVE",
        "reason_codes": ["SAFE_TO_AUTO_HANDLE"],
        "reason": "Classification, grounding, evidence, and operational state checks all passed safety criteria.",
        "confidence": round(final_confidence, 3),
        "blocking_factors": [],
        "state_consistency": {"violations": []},
    }
