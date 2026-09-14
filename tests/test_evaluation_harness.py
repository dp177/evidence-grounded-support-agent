"""Unit tests for the Hiver AmazonSupportAgent evaluation harness.

Tests:
1. Pipe-separated set parsing
2. Null handling for AMBIGUOUS and OUT_OF_SCOPE
3. Clarification quality heuristics (rejecting greetings, requiring active disambiguation)
4. Behavioral policy invariants (NORMAL without retrieval passing, AMBIGUOUS with retrieval failing)
5. Escalation binary & safety metrics (unsafe auto-handle rate, unnecessary escalation rate)
6. Conditional escalation reason evaluation
7. Retrieval metric helpers (Recall@k, MRR, nDCG@k)
8. Baseline vs Candidate delta calculation and regression detection
"""

import pytest
from evaluation.graders.classification import (
    evaluate_primary_intent,
    evaluate_set_based_labels,
    evaluate_status,
    parse_pipe_separated,
)
from evaluation.graders.escalation import (
    evaluate_conditional_escalation_reason,
    evaluate_escalation_binary,
    normalize_escalation_reason,
)
from evaluation.graders.behavior import (
    evaluate_clarification_quality,
    grade_case_behavior,
)
from evaluation.graders.retrieval import (
    mrr,
    ndcg_at_k,
    recall_at_k,
)
from evaluation.compare import calculate_delta, compare_benchmarks


# ===========================================================================
# 1. Pipe-separated set parsing
# ===========================================================================

def test_parse_pipe_separated_empty_and_null():
    assert parse_pipe_separated(None) == set()
    assert parse_pipe_separated("") == set()
    assert parse_pipe_separated("None") == set()
    assert parse_pipe_separated("nan") == set()
    assert parse_pipe_separated("null") == set()
    assert parse_pipe_separated("[]") == set()


def test_parse_pipe_separated_single_and_multi():
    assert parse_pipe_separated("DELIVERY_AND_FULFILLMENT") == {"DELIVERY_AND_FULFILLMENT"}
    assert parse_pipe_separated("A|B|C") == {"A", "B", "C"}
    assert parse_pipe_separated("  A | B  |  C  ") == {"A", "B", "C"}
    assert parse_pipe_separated(["A", "B"]) == {"A", "B"}


# ===========================================================================
# 2. Null handling for AMBIGUOUS and OUT_OF_SCOPE
# ===========================================================================

def test_primary_intent_null_handling():
    # Gold has null for AMBIGUOUS and OUT_OF_SCOPE; agent predicts None -> should match!
    y_true = [None, None, "WHERE_IS_MY_ORDER"]
    y_pred = [None, None, "WHERE_IS_MY_ORDER"]
    status_true = ["AMBIGUOUS", "OUT_OF_SCOPE", "NORMAL"]

    res = evaluate_primary_intent(y_true, y_pred, status_true=status_true)
    assert res["accuracy"] == 1.0
    assert res["macro_f1"] == 1.0


def test_primary_intent_null_mismatch():
    # Gold has null for AMBIGUOUS; agent incorrectly predicts an intent
    y_true = [None, "WHERE_IS_MY_ORDER"]
    y_pred = ["DELIVERY_DELAYED", "WHERE_IS_MY_ORDER"]
    status_true = ["AMBIGUOUS", "NORMAL"]

    res = evaluate_primary_intent(y_true, y_pred, status_true=status_true)
    assert res["accuracy"] == 0.5


# ===========================================================================
# 3. Clarification quality heuristics (Correction 2)
# ===========================================================================

def test_clarification_quality_rejects_generic_greetings():
    assert evaluate_clarification_quality("Hi! How can I help you today?") == "FAIL"
    assert evaluate_clarification_quality("Hello! How may I assist you today?") == "FAIL"
    assert evaluate_clarification_quality("Sorry about that.") == "FAIL"
    assert evaluate_clarification_quality("Your issue has been noted.") == "FAIL"
    assert evaluate_clarification_quality("You can check your order status online.") == "FAIL"


def test_clarification_quality_accepts_active_disambiguation():
    # Does not require a question mark
    assert evaluate_clarification_quality("Please tell me whether the package is delayed, missing, or marked delivered.") == "PASS"
    assert evaluate_clarification_quality("Could you clarify whether you're asking about delivery, cancellation, or a refund?") == "PASS"
    assert evaluate_clarification_quality("Could you tell me what issue you're having with the order?") == "PASS"
    assert evaluate_clarification_quality("Please provide your order ID and describe the problem") == "PASS"


# ===========================================================================
# 4. Behavioral policy invariants (Corrections 1, 4)
# ===========================================================================

def test_behavior_normal_without_retrieval_does_not_fail():
    """Correction 1: A NORMAL case where retrieval was skipped should NOT fail policy."""
    gold = {"status": "NORMAL", "primary_intent": "DELIVERY_DELAYED"}
    agent = {"status": "NORMAL", "primary_intent": "DELIVERY_DELAYED", "response": "Package is on its way."}
    behavior_meta = {"retrieval_used": False, "grounding_passed": True}

    res = grade_case_behavior(gold, agent, behavior_meta)
    assert res["overall_policy_pass"] is True
    assert res["assertions"]["retrieval_invariants"] == "NOT_APPLICABLE"


def test_behavior_ambiguous_with_retrieval_fails():
    """Historical retrieval must NOT run for AMBIGUOUS queries."""
    gold = {"status": "AMBIGUOUS"}
    agent = {"status": "AMBIGUOUS", "response": "Could you provide your order ID?"}
    behavior_meta = {"retrieval_used": True, "grounding_passed": True}  # retrieval wrongly used

    res = grade_case_behavior(gold, agent, behavior_meta)
    assert res["overall_policy_pass"] is False
    assert res["assertions"]["retrieval_invariants"] == "FAIL"


def test_behavior_ambiguous_with_generic_greeting_fails():
    """AMBIGUOUS with pure generic greeting fails clarification invariant."""
    gold = {"status": "AMBIGUOUS"}
    agent = {"status": "AMBIGUOUS", "response": "Hi! How can I help you today?"}
    behavior_meta = {"retrieval_used": False, "grounding_passed": True}

    res = grade_case_behavior(gold, agent, behavior_meta)
    assert res["overall_policy_pass"] is False
    assert res["assertions"]["clarification_invariants"] == "FAIL"


def test_behavior_out_of_scope_with_retrieval_fails():
    """Historical retrieval must NOT run for OUT_OF_SCOPE queries."""
    gold = {"status": "OUT_OF_SCOPE"}
    agent = {"status": "OUT_OF_SCOPE", "response": "I specialize in Amazon retail customer support."}
    behavior_meta = {"retrieval_used": True, "grounding_passed": True}

    res = grade_case_behavior(gold, agent, behavior_meta)
    assert res["overall_policy_pass"] is False
    assert res["assertions"]["retrieval_invariants"] == "FAIL"


# ===========================================================================
# 5. Escalation binary & safety metrics
# ===========================================================================

def test_escalation_metrics_and_safety_rates():
    y_true = [True, True, False, False]
    # Prediction: missed 1 escalation (fn=1), 1 false escalation (fp=1)
    y_pred = [True, False, True, False]

    res = evaluate_escalation_binary(y_true, y_pred)
    assert res["confusion_matrix"]["tp"] == 1
    assert res["confusion_matrix"]["fn"] == 1
    assert res["confusion_matrix"]["fp"] == 1
    assert res["confusion_matrix"]["tn"] == 1
    assert res["unsafe_auto_handle_rate"] == 0.5  # 1 fn / 2 escalated gold
    assert res["unnecessary_escalation_rate"] == 0.5  # 1 fp / 2 non-escalated gold


def test_conditional_escalation_reason():
    y_true_reason = ["ACCOUNT_SECURITY_COMPROMISE", None, None]
    y_pred_reason = ["HIGH_RISK_SECURITY", None, "SOME_REASON"]
    y_true_esc = [True, False, False]

    # Only the first case is evaluated
    res = evaluate_conditional_escalation_reason(y_true_reason, y_pred_reason, y_true_esc)
    assert res["evaluated_cases"] == 1
    assert res["conditional_accuracy"] == 1.0  # HIGH_RISK_SECURITY normalizes to ACCOUNT_SECURITY_COMPROMISE


# ===========================================================================
# 6. Retrieval metric helpers
# ===========================================================================

def test_retrieval_metrics_helpers():
    relevant = {"doc_1", "doc_2"}
    retrieved = ["doc_3", "doc_1", "doc_4", "doc_2", "doc_5"]

    # Recall@1: doc_3 is not in relevant -> 0.0
    assert recall_at_k(relevant, retrieved, 1) == 0.0
    # Recall@2: doc_1 is in top 2 -> 1/2 = 0.5
    assert recall_at_k(relevant, retrieved, 2) == 0.5
    # Recall@5: both docs are in top 5 -> 2/2 = 1.0
    assert recall_at_k(relevant, retrieved, 5) == 1.0

    # MRR: first relevant doc (doc_1) is at rank 2 -> 1/2 = 0.5
    assert mrr(relevant, retrieved) == 0.5

    # nDCG@5
    score = ndcg_at_k(relevant, retrieved, 5)
    assert 0.0 < score <= 1.0


# ===========================================================================
# 7. Comparison delta calculations
# ===========================================================================

def test_calculate_delta():
    abs_d, pct_d = calculate_delta(0.80, 0.90)
    assert abs_d == 0.10
    assert pct_d == 12.5

    abs_d_zero, pct_d_zero = calculate_delta(0.0, 0.05)
    assert abs_d_zero == 0.05
    assert pct_d_zero == 100.0
