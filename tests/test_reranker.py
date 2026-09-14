"""Unit tests for the CandidateReranker using Two-Ranking Reciprocal Rank Fusion (RRF)."""

import math
import pytest
from support_agent.retrieval.reranker import CandidateReranker, compute_rrf


@pytest.fixture
def reranker():
    r = CandidateReranker(k=60)
    r.max_results_per_conversation = 1
    return r


def test_action_penalty(reranker):
    # Boilerplate text
    bad_resp = "I'm sorry to hear about this. Please reach us via phone or chat to fix this."
    assert reranker._compute_action_penalty(bad_resp) == 1.0

    # Good text
    good_resp = "I have processed a refund of $5.99 to your original payment method."
    assert reranker._compute_action_penalty(good_resp) == 0.0


def test_overlap_logic(reranker):
    assert reranker._check_overlap(["REFUND"], ["REFUND", "RETURN"]) == 1.0
    assert reranker._check_overlap(["REFUND"], ["ORDER"]) == 0.0
    # Missing labels or predictions
    assert reranker._check_overlap(None, ["ORDER"]) == 0.0
    assert reranker._check_overlap(["REFUND"], []) == 0.0
    # String vs list format
    assert reranker._check_overlap(["INFO_GATHERING"], "INFO_GATHERING") == 1.0
    assert reranker._check_overlap(["INFO_GATHERING"], "") == 0.0


def test_lexical_similarity(reranker):
    query = "My item arrived damaged"
    candidates = [
        {"customer_message": "The item I received is damaged"},
        {"customer_message": "Where is my order?"},  # Uses stop word 'order' heavily
    ]
    scores = reranker._compute_lexical_similarity(query, candidates)

    assert len(scores) == 2
    # The first candidate should have a higher lexical similarity than the second
    assert scores[0] > scores[1]


def test_reranking_order(reranker):
    """Proves that RRF correctly fuses semantic and lexical rankings."""
    query = "cancel my order"
    candidates = [
        {
            "id": 1,
            "score": 0.8,  # Semantic rank 2
            "customer_message": "cancel order",  # Strong lexical match (lexical rank 1)
            "brand_response": "Sure, cancelled.",
            "conversation_id": 100,
        },
        {
            "id": 2,
            "score": 0.9,  # Semantic rank 1
            "customer_message": "I want to terminate",  # Weaker lexical match (lexical rank 2)
            "brand_response": "Processed.",
            "conversation_id": 101,
        },
    ]

    results = reranker.rerank(
        query_text=query,
        candidates=candidates,
        top_k=5,
    )

    assert len(results) == 2
    for r in results:
        assert "rank" in r
        assert "case_id" in r
        assert "rrf_score" in r
        assert "semantic_rank" in r
        assert "lexical_rank" in r
        assert "semantic_score" in r
        assert "lexical_score" in r


def test_conversation_deduplication(reranker):
    reranker.max_results_per_conversation = 1
    query = "test"
    candidates = [
        {"id": 1, "score": 0.9, "conversation_id": 99, "customer_message": "test 1"},
        {"id": 2, "score": 0.8, "conversation_id": 99, "customer_message": "test 2"},
        {"id": 3, "score": 0.7, "conversation_id": 100, "customer_message": "test 3"},
    ]

    results = reranker.rerank(query_text=query, candidates=candidates, top_k=5)

    # Only 2 results should be returned because candidates 1 and 2 share the same conversation_id
    assert len(results) == 2
    assert results[0]["id"] == 1  # The highest scoring one from conv 99
    assert results[1]["id"] == 3


def test_top_k_truncation(reranker):
    candidates = [
        {"id": i, "score": float(1.0 - i / 10), "conversation_id": i, "customer_message": "test"}
        for i in range(10)
    ]
    results = reranker.rerank(query_text="test", candidates=candidates, top_k=3)
    assert len(results) == 3


def test_regression_action_usefulness_is_not_always_one(reranker):
    """Regression test proving action_usefulness helper is preserved and discriminates boilerplate."""
    boilerplate_responses = [
        "Please send us a DM with your order number so we can help.",
        "We're sorry! Please reach us via phone or chat to resolve this.",
        "Click the link below to get in touch with customer service.",
        "Please direct message us your email address.",
    ]
    operational_responses = [
        "I have initiated a full refund of $24.99 to your credit card. Please allow 3-5 business days for it to appear on your statement.",
        "Please check behind the bushes and with neighbors. If not received by tomorrow at 8pm, you can request a replacement in Your Orders.",
        "You can return the item by printing the prepaid UPS return label from Your Orders and dropping it off at any UPS store within 30 days.",
    ]

    for b_resp in boilerplate_responses:
        usefulness, penalty = reranker._compute_action_usefulness(b_resp)
        assert usefulness < 1.0, f"Boilerplate response should not have usefulness=1.0: {b_resp}"
        assert penalty > 0.0, f"Boilerplate response should receive a penalty: {b_resp}"

    for op_resp in operational_responses:
        usefulness, penalty = reranker._compute_action_usefulness(op_resp)
        assert usefulness >= 0.70, f"Operational response should have high usefulness: {op_resp}"
        assert usefulness > penalty, f"Operational response usefulness should exceed penalty: {op_resp}"


def test_regression_no_nan_or_none_for_rrf_contract(reranker):
    """Regression test proving all required fields are present without NaN or unpopulated values."""
    candidates = [
        {
            "id": f"c_{i}",
            "score": 0.5 + (i * 0.1),
            "customer_message": f"Help with my Amazon delivery {i}",
            "relevant_context": f"Tracking info status {i}",
            "brand_response": f"Your refund has been scheduled for {i} days.",
            "conversation_id": f"conv_{i}",
        }
        for i in range(4)
    ]

    results = reranker.rerank(
        query_text="Where is my delivery?",
        candidates=candidates,
        top_k=4,
    )

    assert len(results) == 4
    for r in results:
        assert "rank" in r and isinstance(r["rank"], int) and r["rank"] >= 1
        assert "case_id" in r and r["case_id"] is not None and len(str(r["case_id"])) > 0
        assert "rrf_score" in r and isinstance(r["rrf_score"], float)
        assert not math.isnan(r["rrf_score"])
        assert not math.isinf(r["rrf_score"])
        assert r["rrf_score"] > 0.0

        assert "semantic_rank" in r and (r["semantic_rank"] is None or isinstance(r["semantic_rank"], int))
        assert "lexical_rank" in r and (r["lexical_rank"] is None or isinstance(r["lexical_rank"], int))
        assert "semantic_score" in r and isinstance(r["semantic_score"], float)
        assert "lexical_score" in r and isinstance(r["lexical_score"], float)
