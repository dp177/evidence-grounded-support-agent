"""Deterministic tests for High-Risk Escalation Overrides and State Precedence.

Verifies:
1. hacked account -> escalate
2. unauthorized email change -> escalate
3. unauthorized password change -> escalate
4. repeated customer-care attempts -> escalate
5. account locked after failed recovery -> escalate
6. normal login issue without security/repeated-failure signal -> remains eligible for normal handling
7. tracking already checked + asks where tracking number is -> NOT inconsistent
8. already-provided information is not requested again
9. no unsupported "I checked your account/order" capability claims
"""

from __future__ import annotations

import pytest
from typing import Any, Dict

from support_agent.classification.state_extractor import extract_conversation_state
from support_agent.escalation.decision import decide_escalation
from support_agent.escalation.escalation_policy import EscalationConfig, check_state_consistency
from support_agent.escalation.high_risk import evaluate_high_risk_escalation
from evaluation.graders.response import check_capability_safety


@pytest.fixture
def config() -> EscalationConfig:
    return EscalationConfig.from_yaml()


# 1. Hacked account -> escalate
def test_hacked_account_escalates(config: EscalationConfig) -> None:
    conv = {"customer_message": "My Amazon account got hacked wtf. Need immediate help."}
    clf = {"primary_intent": "ACCOUNT_LOGIN_ISSUES", "status": "NORMAL", "states": ["INITIAL_INQUIRY"], "confidence": 0.95}
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}
    reply = "Please contact our specialized account security team right away."

    override = evaluate_high_risk_escalation(conv, clf)
    assert override is not None
    assert override["reason_code"] == "ACCOUNT_SECURITY_COMPROMISE"

    res = decide_escalation(clf, [], reply, grnd, customer_conversation=conv, config=config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "ACCOUNT_SECURITY_COMPROMISE" in res["reason_codes"]


# 2. Unauthorized email change -> escalate
def test_unauthorized_email_change_escalates(config: EscalationConfig) -> None:
    conv = {"customer_message": "account hacked , my email account linked with amazon changed without authorisation. Need immediate help."}
    clf = {"primary_intent": "ACCOUNT_LOGIN_ISSUES", "status": "NORMAL", "states": ["INITIAL_INQUIRY"], "confidence": 0.95}
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}
    reply = "I apologize for the trouble. Please reach out to customer care."

    override = evaluate_high_risk_escalation(conv, clf)
    assert override is not None
    assert override["reason_code"] == "ACCOUNT_SECURITY_COMPROMISE"

    res = decide_escalation(clf, [], reply, grnd, customer_conversation=conv, config=config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "ACCOUNT_SECURITY_COMPROMISE" in res["reason_codes"]


# 3. Unauthorized password change -> escalate
def test_unauthorized_password_change_escalates(config: EscalationConfig) -> None:
    conv = {"customer_message": "I can not access my amazon account. I have not made any request to change my password and email. But they have been changed. What to do"}
    clf = {"primary_intent": "ACCOUNT_LOGIN_ISSUES", "status": "NORMAL", "states": ["INITIAL_INQUIRY"], "confidence": 0.95}
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}
    reply = "Could you please confirm the email address associated with your account?"

    override = evaluate_high_risk_escalation(conv, clf)
    assert override is not None
    assert override["reason_code"] == "ACCOUNT_SECURITY_COMPROMISE"

    res = decide_escalation(clf, [], reply, grnd, customer_conversation=conv, config=config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "ACCOUNT_SECURITY_COMPROMISE" in res["reason_codes"]


# 4. Repeated customer-care attempts -> escalate
def test_repeated_customer_care_attempts_escalates(config: EscalationConfig) -> None:
    msg = "Unable to access my Amazon Account, contacted Customer care more than 5 times, still no luck, can some one help me here!"
    conv = {"customer_message": msg}
    
    # State extraction precedence check
    state = extract_conversation_state(customer_message=msg)
    assert state == ["WAITING_WINDOW_EXCEEDED"]

    clf = {"primary_intent": "ACCOUNT_LOGIN_ISSUES", "status": "NORMAL", "states": state, "confidence": 0.95}
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}
    reply = "Can you please provide your registered email?"

    override = evaluate_high_risk_escalation(conv, clf, conversation_state=state)
    assert override is not None
    assert override["reason_code"] == "REPEATED_FAILED_SUPPORT_ATTEMPTS"

    res = decide_escalation(clf, [], reply, grnd, customer_conversation=conv, config=config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "REPEATED_FAILED_SUPPORT_ATTEMPTS" in res["reason_codes"]


# 5. Account locked after failed recovery -> escalate
def test_account_locked_after_failed_recovery_escalates(config: EscalationConfig) -> None:
    msg = "So Amazon decided an order I placed was suspicious and locked my account. Password reset appears to work but still can't log in. Ugh."
    conv = {"customer_message": msg}
    clf = {"primary_intent": "ACCOUNT_LOGIN_ISSUES", "status": "NORMAL", "states": ["INITIAL_INQUIRY"], "confidence": 0.95}
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}
    reply = "I understand your account is locked. Can you please verify your billing address?"

    override = evaluate_high_risk_escalation(conv, clf)
    assert override is not None
    assert override["reason_code"] == "ACCOUNT_SECURITY_COMPROMISE"

    res = decide_escalation(clf, [], reply, grnd, customer_conversation=conv, config=config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert "ACCOUNT_SECURITY_COMPROMISE" in res["reason_codes"]


# 6. Normal login issue without security/repeated-failure signal -> remains eligible for normal handling
def test_normal_login_issue_remains_eligible_for_auto_handle(config: EscalationConfig) -> None:
    conv = {"customer_message": "I forgot my password and would like instructions on how to reset it."}
    clf = {"primary_intent": "ACCOUNT_LOGIN_ISSUES", "status": "NORMAL", "states": ["INITIAL_INQUIRY"], "confidence": 0.95}
    ev = [{"document_id": "doc_pwd_1", "score": 0.85}]
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}
    reply = "You can reset your password by going to the login assistance page and entering your email."

    # Must NOT trigger high-risk override
    override = evaluate_high_risk_escalation(conv, clf)
    assert override is None

    res = decide_escalation(clf, ev, reply, grnd, customer_conversation=conv, config=config)
    assert res["decision"] == "AUTO_HANDLE"
    assert res["sub_decision"] == "RESOLVE"
    assert "SAFE_TO_AUTO_HANDLE" in res["reason_codes"]


# 7. Tracking already checked + asks where tracking number is -> NOT inconsistent
def test_tracking_already_checked_asks_where_tracking_number_is_not_inconsistent(config: EscalationConfig) -> None:
    conv = {"customer_message": "Where can I find my tracking number?"}
    
    # Customer merely asking where tracking number is does NOT infer TRACKING_ALREADY_CHECKED
    inferred_state = extract_conversation_state("Where can I find my tracking number?")
    assert inferred_state == ["INITIAL_INQUIRY"]

    # If state is set to TRACKING_ALREADY_CHECKED, answering where tracking number is located must NOT be blocked
    reply = "You can find your tracking number in Your Orders under the order details."
    violations = check_state_consistency(["TRACKING_ALREADY_CHECKED"], reply, conv, config)
    assert violations == []


# 8. Already-provided information is not requested again
def test_already_provided_details_flagged_if_requested_again(config: EscalationConfig) -> None:
    conv = {"customer_message": "I already sent you my order details in the previous message."}
    reply = "Please provide your order number so we can investigate."
    violations = check_state_consistency(["DETAILS_ALREADY_PROVIDED"], reply, conv, config)
    assert len(violations) > 0
    assert violations[0]["reason_code"] == "INCONSISTENT_WITH_STATE"


# 9. No unsupported capability claims ("I checked your account/order")
def test_no_unsupported_capability_claims() -> None:
    # A reply falsely claiming the assistant checked the account or contacted the carrier
    bad_reply = "I checked your account and contacted UPS to expedite your package delivery."
    safety = check_capability_safety(bad_reply, grounding_block={"grounded": True})
    assert safety["capability_hallucination_detected"] is True
    assert len(safety["capability_hallucinations"]) > 0

    # A safe, grounded reply providing customer guidance
    good_reply = "To check your delivery status, you can visit Your Orders and select Track Package."
    safe_safety = check_capability_safety(good_reply, grounding_block={"grounded": True})
    assert safe_safety["capability_hallucination_detected"] is False


# ===========================================================================
# Policy Iteration 2 Regression Tests: FIX A (Carrier Misconduct / Refusal)
# ===========================================================================

def test_carrier_misconduct_refusal_escalates(config: EscalationConfig) -> None:
    cases = [
        "The delivery driver refused to deliver to my apartment door and drove away.",
        "Courier demanded that I come down to the van to pick up my heavy parcel.",
        "The delivery agent was hostile, screamed at me, and rudely shouted profanities.",
        "The driver threw the fragile box over the fence and forged my signature.",
    ]
    for msg in cases:
        conv = {"customer_message": msg}
        clf = {"primary_intent": "CARRIER_FEEDBACK_AND_INSTRUCTIONS", "status": "NORMAL", "states": ["INITIAL_INQUIRY"], "confidence": 0.95}
        override = evaluate_high_risk_escalation(conv, clf)
        assert override is not None, f"Expected override for: {msg}"
        assert override["reason_code"] == "CARRIER_MISCONDUCT_AND_REFUSAL"

        res = decide_escalation(clf, [], "I apologize for this experience.", {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}, customer_conversation=conv, config=config)
        assert res["decision"] == "HUMAN_REVIEW"
        assert "CARRIER_MISCONDUCT_AND_REFUSAL" in res["reason_codes"]


def test_routine_carrier_instructions_remain_eligible_for_auto_handle(config: EscalationConfig) -> None:
    routine_cases = [
        "Can you please leave a delivery note to drop the parcel on the front porch?",
        "Where can I add the gate access code #4491 for the UPS delivery driver?",
        "How can I contact the carrier to update my delivery preferences?",
        "The delivery driver was very polite and placed the parcel safely today.",
    ]
    for msg in routine_cases:
        conv = {"customer_message": msg}
        clf = {"primary_intent": "CARRIER_FEEDBACK_AND_INSTRUCTIONS", "status": "NORMAL", "states": ["INITIAL_INQUIRY"], "confidence": 0.95}
        override = evaluate_high_risk_escalation(conv, clf)
        assert override is None, f"Did not expect override for routine case: {msg}"

        ev = [{"document_id": "doc_carrier_1", "score": 0.85}]
        res = decide_escalation(clf, ev, "You can add delivery instructions under Your Orders.", {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}, customer_conversation=conv, config=config)
        assert res["decision"] == "AUTO_HANDLE"
        assert "SAFE_TO_AUTO_HANDLE" in res["reason_codes"]


# ===========================================================================
# Policy Iteration 2 Regression Tests: FIX B (Repeated Failed Support)
# ===========================================================================

def test_repeated_support_linguistic_variants_escalate(config: EscalationConfig) -> None:
    variants = [
        ("I have contacted support 5 separate times about this delayed parcel and each representative transfers me to someone else!", ["WAITING_WINDOW_EXCEEDED"]),
        ("I have been in touch with customer service across 4 attempts and no resolution was offered.", ["WAITING_WINDOW_EXCEEDED"]),
        ("Representative transferred me three times to different departments with still no luck.", ["INITIAL_INQUIRY"]),
        ("Support promised a callback that never came after the stated window.", ["WAITING_WINDOW_EXCEEDED"]),
    ]
    for msg, st in variants:
        conv = {"customer_message": msg}
        clf = {"primary_intent": "ORDER_STATUS_AND_TRACKING", "status": "NORMAL", "states": st, "confidence": 0.90}
        override = evaluate_high_risk_escalation(conv, clf, conversation_state=st)
        assert override is not None, f"Expected repeated support override for: {msg}"
        assert override["reason_code"] == "REPEATED_FAILED_SUPPORT_ATTEMPTS"

        res = decide_escalation(clf, [], "Let me connect you with support.", {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}, customer_conversation=conv, config=config)
        assert res["decision"] == "HUMAN_REVIEW"
        assert "REPEATED_FAILED_SUPPORT_ATTEMPTS" in res["reason_codes"]


def test_single_support_contact_does_not_escalate(config: EscalationConfig) -> None:
    single_contacts = [
        "I contacted support yesterday to ask about estimated delivery date.",
        "I spoke with an agent earlier who answered my question about returns.",
        "Reached out to customer care last week to confirm the tracking ID.",
    ]
    for msg in single_contacts:
        conv = {"customer_message": msg}
        clf = {"primary_intent": "ORDER_STATUS_AND_TRACKING", "status": "NORMAL", "states": ["INITIAL_INQUIRY"], "confidence": 0.90}
        override = evaluate_high_risk_escalation(conv, clf)
        assert override is None, f"Single contact must not trigger high risk: {msg}"


# ===========================================================================
# Policy Iteration 2 Regression Tests: FIX C (Account Security Compromise)
# ===========================================================================

def test_security_compromise_linguistic_variants_escalate(config: EscalationConfig) -> None:
    security_cases = [
        "Someone broke into my account and ordered expensive electronics without my permission!",
        "My Amazon account was hijacked and I can no longer log in.",
        "I never requested that password change and suspect someone else accessed my account.",
        "An unauthorized intruder changed both my email and phone number.",
        "Suspicious account activity detected on my profile that wasn't me.",
    ]
    for msg in security_cases:
        conv = {"customer_message": msg}
        clf = {"primary_intent": "ACCOUNT_LOGIN_ISSUES", "status": "NORMAL", "states": ["INITIAL_INQUIRY"], "confidence": 0.95}
        override = evaluate_high_risk_escalation(conv, clf)
        assert override is not None, f"Expected security compromise override for: {msg}"
        assert override["reason_code"] == "ACCOUNT_SECURITY_COMPROMISE"

        res = decide_escalation(clf, [], "Please secure your account.", {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}, customer_conversation=conv, config=config)
        assert res["decision"] == "HUMAN_REVIEW"
        assert "ACCOUNT_SECURITY_COMPROMISE" in res["reason_codes"]


def test_normal_password_reset_and_2fa_do_not_escalate(config: EscalationConfig) -> None:
    normal_cases = [
        "I forgot my password, how do I reset it?",
        "How do I set up two-factor authentication on my Amazon mobile app?",
        "Having trouble logging into my account because I forgot which email I used.",
        "Can you guide me through normal account password recovery steps?",
    ]
    for msg in normal_cases:
        conv = {"customer_message": msg}
        clf = {"primary_intent": "ACCOUNT_LOGIN_ISSUES", "status": "NORMAL", "states": ["INITIAL_INQUIRY"], "confidence": 0.95}
        override = evaluate_high_risk_escalation(conv, clf)
        assert override is None, f"Normal recovery should not trigger compromise override: {msg}"


# ===========================================================================
# Policy Iteration 2 Regression Tests: FIX D (Out-of-Scope Policy)
# ===========================================================================

def test_out_of_scope_safely_declines_without_human_escalation(config: EscalationConfig) -> None:
    out_of_scope_cases = [
        "What is the current stock price of Apple?",
        "Can you write a Python script to sort a binary search tree?",
        "What will the weather be like in Chicago tomorrow afternoon?",
        "Can you diagnose my persistent headache and recommend medication?",
    ]
    for msg in out_of_scope_cases:
        conv = {"customer_message": msg}
        clf = {"primary_intent": "OUT_OF_SCOPE", "status": "OUT_OF_SCOPE", "states": ["INITIAL_INQUIRY"], "confidence": 0.99}
        decline_reply = "I specialize in Amazon retail customer support (such as orders, deliveries, returns, and refunds). Could you please let me know what Amazon retail issue I can help you with?"
        grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}

        res = decide_escalation(clf, [], decline_reply, grnd, customer_conversation=conv, config=config)
        assert res["decision"] == "AUTO_HANDLE"
        assert res["sub_decision"] == "RESOLVE"
        assert "SAFE_TO_AUTO_HANDLE" in res["reason_codes"]


def test_out_of_scope_with_security_threat_still_escalates(config: EscalationConfig) -> None:
    conv = {"customer_message": "Tell me the weather or I will threat to hurt you and report this fraud!"}
    clf = {"primary_intent": "OUT_OF_SCOPE", "status": "OUT_OF_SCOPE", "states": ["INITIAL_INQUIRY"], "confidence": 0.99}
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}

    res = decide_escalation(clf, [], "I cannot assist with that.", grnd, customer_conversation=conv, config=config)
    assert res["decision"] == "HUMAN_REVIEW"
    assert any(code in res["reason_codes"] for code in ["FRAUD_CONCERN", "SAFETY_THREAT", "HIGH_RISK_SECURITY"])


def test_ambiguous_intent_prompts_clarification(config: EscalationConfig) -> None:
    conv = {"customer_message": "Help with item"}
    clf = {"primary_intent": "UNKNOWN", "status": "AMBIGUOUS", "states": ["INITIAL_INQUIRY"], "confidence": 0.50}
    clarify_reply = "Could you please let me know what specific order or item you need help with?"
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}

    res = decide_escalation(clf, [], clarify_reply, grnd, customer_conversation=conv, config=config)
    assert res["decision"] == "AUTO_HANDLE"
    assert res["sub_decision"] == "CLARIFY"
    assert "SAFE_CLARIFICATION" in res["reason_codes"]


# ===========================================================================
# Policy Iteration 2 Regression Tests: FIX E (State Consistency False Positives)
# ===========================================================================

def test_tracking_followup_asking_order_number_not_inconsistent(config: EscalationConfig) -> None:
    conv = {
        "customer_message": "I already checked the tracking, why is the package delayed in transit?",
        "context": "CUSTOMER: Can you check on my package?\nBRAND: Have you checked tracking?\nCUSTOMER: I already checked the tracking, why is the package delayed in transit?",
    }
    reply = "Could you please provide your order number so I can investigate the delay?"
    violations = check_state_consistency(["TRACKING_ALREADY_CHECKED"], reply, conv, config)
    assert violations == []

    # And decide_escalation should not flag INCONSISTENT_WITH_STATE
    clf = {"primary_intent": "ORDER_STATUS_AND_TRACKING", "status": "NORMAL", "states": ["TRACKING_ALREADY_CHECKED"], "confidence": 0.90}
    grnd = {"grounded": True, "grounding_score": 1.0, "unsupported_claims": [], "contradicted_claims": []}
    res = decide_escalation(clf, [], reply, grnd, customer_conversation=conv, config=config)
    assert "INCONSISTENT_WITH_STATE" not in res["reason_codes"]


def test_tracking_followup_explaining_status_not_inconsistent(config: EscalationConfig) -> None:
    conv = {
        "customer_message": "Tracking page indicates 'Package arrived at carrier facility', how long until out for delivery?",
    }
    reply = "I understand the tracking page indicates 'Package arrived at carrier facility'. Packages are typically dispatched within 24 hours."
    violations = check_state_consistency(["TRACKING_ALREADY_CHECKED"], reply, conv, config)
    assert violations == []


def test_true_state_inconsistency_commands_recheck_flagged(config: EscalationConfig) -> None:
    conv = {"customer_message": "I already checked the tracking website and it has not updated."}
    reply = "Please check the carrier tracking portal for updates on your shipment."
    violations = check_state_consistency(["TRACKING_ALREADY_CHECKED"], reply, conv, config)
    assert len(violations) > 0
    assert violations[0]["reason_code"] == "INCONSISTENT_WITH_STATE"


def test_asking_order_number_when_already_supplied_flagged(config: EscalationConfig) -> None:
    conv = {
        "customer_message": "Can you check on my order?",
        "context": "CUSTOMER: My order number is 112-9901823-1120938.\nBRAND: Checking now.",
    }
    reply = "Could you please provide your order number?"
    violations = check_state_consistency(["DETAILS_ALREADY_PROVIDED"], reply, conv, config)
    assert len(violations) > 0
    assert violations[0]["reason_code"] == "INCONSISTENT_WITH_STATE"

