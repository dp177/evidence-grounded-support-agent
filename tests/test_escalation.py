"""Tests for Phase 10: Deterministic Auto-Handle vs Human Escalation.

Verifies all safety gates, reason codes, blocking factors, and state-consistency rules:
  1. Grounded safe auto-handle
  2. Failed grounding -> human review
  3. Contradicted claims -> human review
  4. Ambiguous classification -> safe clarification or human review
  5. Out of scope -> human review
  6. Security risk -> human review
  7. Fraud concern -> human review
  8. Low classifier confidence -> human review
  9. TRACKING_ALREADY_CHECKED state violation -> human review
  10. CARRIER_ALREADY_CONTACTED state violation -> human review
  11. DETAILS_ALREADY_PROVIDED state violation -> human review
  12. Malformed / empty response -> human review
  13. Insufficient retrieval evidence -> human review
"""

from __future__ import annotations

import pytest
from typing import Any, Dict

from support_agent.escalation.decision import decide_escalation
from support_agent.escalation.escalation_policy import EscalationConfig, is_clarification_response


@pytest.fixture
def base_config() -> EscalationConfig:
    return EscalationConfig({
        "classification": {
            "min_confidence": 0.70,
            "allow_ambiguous_clarification": True,
            "block_out_of_scope": True,
        },
        "security_and_fraud": {
            "high_risk_intents": ["ACCOUNT_ACCESS_RECOVERY", "PAYMENT_AND_BILLING_DISPUTES"],
            "risk_keywords": ["fraud", "scam", "police", "hacked", "unauthorized", "stolen"],
            "escalate_on_risk_keywords": True,
        },
        "grounding": {
            "require_grounded": True,
            "max_contradicted_claims": 0,
            "max_unsupported_claims": 0,
            "block_unsupported_current_actions": True,
            "block_invalid_evidence_ids": True,
        },
        "retrieval": {
            "min_top_evidence_score": 0.45,
            "require_evidence_for_resolution": True,
        },
        "state_inconsistency": {
            "TRACKING_ALREADY_CHECKED": {
                "blocked_response_patterns": [
                    r"(?:check|track)\s+(?:the\s+)?(?:tracking|order\s+status|parcel)"
                ],
                "reason_code": "INCONSISTENT_WITH_STATE",
                "message": "Response tells customer to check tracking when already verified.",
            },
            "CARRIER_ALREADY_CONTACTED": {
                "blocked_response_patterns": [
                    r"(?:contact|call|reach\s+out\s+to)\s+(?:the\s+)?(?:carrier|courier|driver)"
                ],
                "reason_code": "INCONSISTENT_WITH_STATE",
                "message": "Response redirects to carrier when already contacted.",
            },
            "DETAILS_ALREADY_PROVIDED": {
                "blocked_response_patterns": [
                    r"provide\s+(?:your\s+)?(?:order\s+number|details)"
                ],
                "reason_code": "INCONSISTENT_WITH_STATE",
                "message": "Response asks for details already provided.",
            },
        },
    })


def test_grounded_safe_auto_handle(base_config: EscalationConfig) -> None:
    clf = {"primary_intent": "DELIVERY_DELAYED", "states": [], "confidence": 0.95}
    ev = [{"document_id": "doc_1", "score": 0.75}]
    reply = "I apologize for the delay. You may explore safe place delivery options in your account."
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}

    res = decide_escalation(clf, ev, reply, grnd, config=base_config)
    assert res["decision"] == "AUTO_HANDLE"
    assert res["sub_decision"] == "RESOLVE"
    assert "SAFE_TO_AUTO_HANDLE" in res["reason_codes"]
    assert res["blocking_factors"] == []


def test_failed_grounding_triggers_human_review(base_config: EscalationConfig) -> None:
    clf = {"primary_intent": "DELIVERY_DELAYED", "states": [], "confidence": 0.95}
    ev = [{"document_id": "doc_1", "score": 0.75}]
    reply = "We have issued your full refund of $50."
    grnd = {
        "grounded": False,
        "grounding_score": 0.0,
        "unsupported_claims": ["We have issued your full refund of $50."],
        "contradicted_claims": [],
        "risk_flags": ["Hard safety violation: refund issued"],
    }

    res = decide_escalation(clf, ev, reply, grnd, config=base_config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "GROUNDING_FAILURE" in res["reason_codes"]
    assert len(res["blocking_factors"]) > 0


def test_contradicted_response_triggers_human_review(base_config: EscalationConfig) -> None:
    clf = {"primary_intent": "WHERE_IS_MY_ORDER", "states": [], "confidence": 0.90}
    ev = [{"document_id": "doc_1", "score": 0.70}]
    reply = "Your order was delivered yesterday."
    grnd = {
        "grounded": False,
        "grounding_score": 0.0,
        "unsupported_claims": [],
        "contradicted_claims": ["Your order was delivered yesterday."],
    }

    res = decide_escalation(clf, ev, reply, grnd, config=base_config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "CONTRADICTED_RESPONSE" in res["reason_codes"]


def test_ambiguous_safe_clarification_allowed(base_config: EscalationConfig) -> None:
    clf = {"primary_intent": "UNKNOWN", "status": "AMBIGUOUS", "confidence": 0.50}
    ev = [{"document_id": "doc_1", "score": 0.60}]
    reply = "Could you please clarify which item you are referring to?"
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}

    res = decide_escalation(clf, ev, reply, grnd, config=base_config)
    assert res["decision"] == "AUTO_HANDLE"
    assert res["sub_decision"] == "CLARIFY"
    assert "SAFE_CLARIFICATION" in res["reason_codes"]


def test_ambiguous_unclear_without_clarification_escalates(base_config: EscalationConfig) -> None:
    clf = {"primary_intent": "UNKNOWN", "status": "AMBIGUOUS", "confidence": 0.50}
    ev = [{"document_id": "doc_1", "score": 0.60}]
    reply = "Thank you for contacting Amazon. We are here for you."
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}

    res = decide_escalation(clf, ev, reply, grnd, config=base_config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "AMBIGUOUS_CLASSIFICATION" in res["reason_codes"]


def test_out_of_scope_triggers_human_review(base_config: EscalationConfig) -> None:
    clf = {"primary_intent": "OUT_OF_SCOPE", "status": "OUT_OF_SCOPE", "confidence": 0.95}
    ev = []
    reply = "I cannot assist with medical advice."
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}

    res = decide_escalation(clf, ev, reply, grnd, config=base_config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "OUT_OF_SCOPE" in res["reason_codes"]


def test_security_intent_triggers_human_review(base_config: EscalationConfig) -> None:
    clf = {"primary_intent": "ACCOUNT_ACCESS_RECOVERY", "states": [], "confidence": 0.92}
    ev = [{"document_id": "doc_1", "score": 0.70}]
    reply = "You can reset your password at <URL>."
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}

    res = decide_escalation(clf, ev, reply, grnd, config=base_config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "HIGH_RISK_SECURITY" in res["reason_codes"]


def test_fraud_keyword_triggers_human_review(base_config: EscalationConfig) -> None:
    clf = {"primary_intent": "DELIVERY_DELAYED", "states": [], "confidence": 0.85}
    ev = [{"document_id": "doc_1", "score": 0.70}]
    conv = {"customer_message": "A scammer committed fraud on my account and stole money!"}
    reply = "Please let us know how we can help."
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}

    res = decide_escalation(clf, ev, reply, grnd, customer_conversation=conv, config=base_config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "FRAUD_CONCERN" in res["reason_codes"]


def test_low_classifier_confidence_escalates_when_resolving(base_config: EscalationConfig) -> None:
    clf = {"primary_intent": "WHERE_IS_MY_ORDER", "states": [], "confidence": 0.45}
    ev = [{"document_id": "doc_1", "score": 0.70}]
    reply = "Your parcel will arrive within 2 business days."
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}

    res = decide_escalation(clf, ev, reply, grnd, config=base_config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "LOW_CLASSIFICATION_CONFIDENCE" in res["reason_codes"]


def test_tracking_already_checked_state_violation(base_config: EscalationConfig) -> None:
    clf = {"primary_intent": "WHERE_IS_MY_ORDER", "states": ["TRACKING_ALREADY_CHECKED"], "confidence": 0.90}
    ev = [{"document_id": "doc_1", "score": 0.70}]
    reply = "Please check the tracking link here: <URL> for updates."
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}

    res = decide_escalation(clf, ev, reply, grnd, config=base_config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "INCONSISTENT_WITH_STATE" in res["reason_codes"]


def test_carrier_already_contacted_state_violation(base_config: EscalationConfig) -> None:
    clf = {"primary_intent": "CARRIER_FEEDBACK_AND_INSTRUCTIONS", "states": ["CARRIER_ALREADY_CONTACTED"], "confidence": 0.90}
    ev = [{"document_id": "doc_1", "score": 0.70}]
    reply = "Please contact the carrier directly for more information."
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}

    res = decide_escalation(clf, ev, reply, grnd, config=base_config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "INCONSISTENT_WITH_STATE" in res["reason_codes"]


def test_details_already_provided_state_violation(base_config: EscalationConfig) -> None:
    clf = {"primary_intent": "CARRIER_FEEDBACK_AND_INSTRUCTIONS", "states": ["DETAILS_ALREADY_PROVIDED"], "confidence": 0.90}
    ev = [{"document_id": "doc_1", "score": 0.70}]
    reply = "Please provide your order number so we can check."
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}

    res = decide_escalation(clf, ev, reply, grnd, config=base_config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "INCONSISTENT_WITH_STATE" in res["reason_codes"]


def test_malformed_empty_reply(base_config: EscalationConfig) -> None:
    clf = {"primary_intent": "DELIVERY_DELAYED", "states": [], "confidence": 0.90}
    res = decide_escalation(clf, [], "   ", {"grounded": True}, config=base_config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "MALFORMED_RESPONSE" in res["reason_codes"]


def test_insufficient_retrieval_evidence_for_resolution(base_config: EscalationConfig) -> None:
    clf = {"primary_intent": "DELIVERY_DELAYED", "states": [], "confidence": 0.90}
    ev = [{"document_id": "doc_1", "score": 0.20}]  # Below min_top_evidence_score 0.45
    reply = "Standard deliveries take 3-5 days across domestic regions."
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}

    res = decide_escalation(clf, ev, reply, grnd, config=base_config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "INSUFFICIENT_EVIDENCE" in res["reason_codes"]
