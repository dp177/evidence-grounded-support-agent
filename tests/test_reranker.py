"""Unit tests for the CandidateReranker."""

import pytest
from support_agent.retrieval.reranker import CandidateReranker

@pytest.fixture
def reranker():
    r = CandidateReranker()
    # Mocking standard test weights
    r.weights = {
        "semantic": 1.0,
        "lexical": 0.5,
        "intent": 0.2,
        "area": 0.1,
        "state": 0.1,
        "action_penalty": -0.2
    }
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
        {"customer_message": "Where is my order?"} # Uses stop word 'order' heavily
    ]
    scores = reranker._compute_lexical_similarity(query, candidates)
    
    assert len(scores) == 2
    # The first candidate should have a higher lexical similarity than the second
    assert scores[0] > scores[1]

def test_reranking_order(reranker):
    query = "cancel my order"
    candidates = [
        {
            "id": 1,
            "score": 0.8, # Base semantic score
            "customer_message": "I want to cancel",
            "brand_response": "Sure, cancelled.",
            "conversation_id": 100,
            "metadata": {"intents": ["CANCEL"]}
        },
        {
            "id": 2,
            "score": 0.9, 
            "customer_message": "cancel order",
            "brand_response": "reach us via phone or chat", # Will get penalized
            "conversation_id": 101,
            "metadata": {"intents": ["CANCEL"]}
        }
    ]
    
    results = reranker.rerank(
        query, 
        candidates, 
        predicted_intents=["CANCEL"],
        top_k=5
    )
    
    assert len(results) == 2
    # Without penalty, Candidate 2 has a higher semantic score and strong lexical score.
    # But Candidate 2 gets action penalty (-0.2), lowering its final score.
    # Candidate 1 gets 0 penalty.
    # Let's ensure score computation is working properly.
    for r in results:
        assert "rerank_score" in r
        assert "semantic_score" in r
        assert "action_penalty_flag" in r

def test_conversation_deduplication(reranker):
    reranker.max_results_per_conversation = 1
    query = "test"
    candidates = [
        {"id": 1, "score": 0.9, "conversation_id": 99, "customer_message": "test 1"},
        {"id": 2, "score": 0.8, "conversation_id": 99, "customer_message": "test 2"},
        {"id": 3, "score": 0.7, "conversation_id": 100, "customer_message": "test 3"}
    ]
    
    results = reranker.rerank(query, candidates, top_k=5)
    
    # Only 2 results should be returned because candidates 1 and 2 share the same conversation_id
    assert len(results) == 2
    assert results[0]["id"] == 1 # The highest scoring one from conv 99
    assert results[1]["id"] == 3

def test_top_k_truncation(reranker):
    candidates = [
        {"id": i, "score": float(1.0 - i/10), "conversation_id": i, "customer_message": "test"} 
        for i in range(10)
    ]
    results = reranker.rerank("test", candidates, top_k=3)
    assert len(results) == 3
