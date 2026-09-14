"""Deterministic unit tests for Two-Ranking Reciprocal Rank Fusion (RRF) Reranker.

Covers:
1. Exact RRF mathematical formula with k=60 (including Candidate A and B from specification).
2. Missing rank handling (unranked contributes 0.0, rank field is None / null, not 0).
3. Strictly descending RRF score order.
4. Candidate appearing in both lists beats single-retrieval candidate.
5. Exact backend output dictionary contract.
6. Immunity to decommissioned signals (intent, area, state, action penalty).
7. Top-K truncation (e.g., top_k=5, top_k=3).
8. Conversation deduplication preserving unique customer threads.
"""

import pytest
from support_agent.retrieval.reranker import CandidateReranker, compute_rrf


@pytest.fixture
def rrf_reranker():
    return CandidateReranker(k=60)


def test_rrf_exact_math():
    """Requirement 1: Exact RRF mathematical formula with k=60.

    Candidate A: semantic rank = 1, lexical rank = 4
        RRF(A) = 1/(60+1) + 1/(60+4) = 1/61 + 1/64 = 0.0163934 + 0.015625 = 0.03202

    Candidate B: semantic rank = 2, lexical rank = 1
        RRF(B) = 1/(60+2) + 1/(60+1) = 1/62 + 1/61 = 0.0161290 + 0.0163934 = 0.03252
    """
    score_a = compute_rrf(semantic_rank=1, lexical_rank=4, k=60)
    assert score_a == 0.03202, f"Expected 0.03202, got {score_a}"

    score_b = compute_rrf(semantic_rank=2, lexical_rank=1, k=60)
    assert score_b == 0.03252, f"Expected 0.03252, got {score_b}"

    assert score_b > score_a, "Candidate B should rank higher than Candidate A"


def test_rrf_missing_rank_handling(rrf_reranker):
    """Requirement 2: If a candidate does not appear in one ranking, that ranking contributes 0.0.

    Rank field must be None (not 0 or fake rank).
    """
    # Candidate only in semantic
    score_sem_only = compute_rrf(semantic_rank=1, lexical_rank=None, k=60)
    assert score_sem_only == round(1.0 / 61, 5)  # 0.01639

    # Candidate only in lexical
    score_lex_only = compute_rrf(semantic_rank=None, lexical_rank=1, k=60)
    assert score_lex_only == round(1.0 / 61, 5)  # 0.01639

    sem_candidates = [
        {"case_id": "case_sem_only", "score": 0.90, "customer_message": "Where is my item"}
    ]
    lex_candidates = []

    results = rrf_reranker.rerank(
        query_text="Where is my item",
        semantic_candidates=sem_candidates,
        lexical_candidates=lex_candidates,
        top_k=5,
    )

    assert len(results) == 1
    res = results[0]
    assert res["case_id"] == "case_sem_only"
    assert res["semantic_rank"] == 1
    assert res["lexical_rank"] is None, "Missing lexical ranking must be None, never 0"
    assert res["rrf_score"] == 0.01639


def test_rrf_descending_sort_order(rrf_reranker):
    """Requirement 3: Candidates must be sorted strictly by descending RRF score."""
    # Semantic ranks: 1, 2, 3
    sem_candidates = [
        {"case_id": "c_1", "score": 0.95},
        {"case_id": "c_2", "score": 0.85},
        {"case_id": "c_3", "score": 0.75},
    ]
    # Lexical ranks: c_2 is #1, c_1 is #4, c_3 is not present
    lex_candidates = [
        {"case_id": "c_2", "score": 0.70},
        {"case_id": "c_4", "score": 0.60},
        {"case_id": "c_5", "score": 0.50},
        {"case_id": "c_1", "score": 0.40},
    ]

    results = rrf_reranker.rerank(
        query_text="test query",
        semantic_candidates=sem_candidates,
        lexical_candidates=lex_candidates,
        top_k=5,
    )

    # c_2: sem=2, lex=1 -> 1/62 + 1/61 = 0.03252
    # c_1: sem=1, lex=4 -> 1/61 + 1/64 = 0.03202
    assert results[0]["case_id"] == "c_2"
    assert results[0]["rank"] == 1
    assert results[0]["rrf_score"] == 0.03252

    assert results[1]["case_id"] == "c_1"
    assert results[1]["rank"] == 2
    assert results[1]["rrf_score"] == 0.03202

    # Check strict descending order
    for i in range(len(results) - 1):
        assert results[i]["rrf_score"] >= results[i + 1]["rrf_score"]


def test_rrf_candidate_appearing_in_both_beats_single(rrf_reranker):
    """Requirement 4: A candidate appearing in both rankings beats a single-ranking candidate."""
    # Candidate Dual: rank 10 in semantic, rank 10 in lexical
    # RRF(Dual) = 1/70 + 1/70 = 2/70 = 0.02857
    # Candidate Solo: rank 1 in semantic, unranked in lexical
    # RRF(Solo) = 1/61 + 0 = 0.01639
    sem = [{"case_id": f"s_{i}", "score": 1.0 - (i * 0.05)} for i in range(1, 15)]
    # Replace s_10 with dual
    sem[9] = {"case_id": "dual_case", "score": 0.50}

    lex = [{"case_id": f"l_{i}", "score": 1.0 - (i * 0.05)} for i in range(1, 15)]
    lex[9] = {"case_id": "dual_case", "score": 0.50}

    results = rrf_reranker.rerank(
        query_text="query",
        semantic_candidates=sem,
        lexical_candidates=lex,
        top_k=5,
    )

    # Find dual_case and s_1 (Solo rank 1)
    dual_cand = next((c for c in results if c["case_id"] == "dual_case"), None)
    s1_cand = next((c for c in results if c["case_id"] == "s_1"), None)

    assert dual_cand is not None
    assert s1_cand is not None
    assert dual_cand["rrf_score"] > s1_cand["rrf_score"], (
        f"Dual ranking candidate ({dual_cand['rrf_score']}) should beat solo rank #1 ({s1_cand['rrf_score']})"
    )


def test_rrf_candidate_output_contract(rrf_reranker):
    """Requirement 5: Output dictionary contract compliance.

    Each selected candidate must include:
    {
      "rank": 1,
      "case_id": "...",
      "semantic_rank": 1,
      "lexical_rank": 4,
      "rrf_score": 0.03202,
      "semantic_score": 0.85,
      "lexical_score": 0.62
    }
    """
    sem = [{"case_id": "case_alpha", "score": 0.85, "customer_message": "msg"}]
    lex = [{"case_id": "other_case", "score": 0.90}, {"case_id": "other_2", "score": 0.80}, {"case_id": "other_3", "score": 0.70}, {"case_id": "case_alpha", "score": 0.62}]

    results = rrf_reranker.rerank(
        query_text="msg",
        semantic_candidates=sem,
        lexical_candidates=lex,
        top_k=5,
    )

    cand = next(c for c in results if c["case_id"] == "case_alpha")
    assert "rank" in cand and isinstance(cand["rank"], int)
    assert cand["case_id"] == "case_alpha"
    assert cand["semantic_rank"] == 1
    assert cand["lexical_rank"] == 4
    assert cand["rrf_score"] == 0.03202
    assert cand["semantic_score"] == 0.85
    assert cand["lexical_score"] == 0.62


def test_rrf_decommissioned_signals_immunity(rrf_reranker):
    """Requirement 6: Intent, area, state, and action penalty must NOT affect RRF ranking or score."""
    cand_a = {
        "case_id": "case_a",
        "score": 0.80,
        "metadata": {"intents": ["UNRELATED_INTENT"], "state": "UNRELATED_STATE", "area": "OTHER"},
        "brand_response": "Please reach us via phone or chat. Send us a dm.",  # Deflection boilerplate
    }
    cand_b = {
        "case_id": "case_b",
        "score": 0.70,
        "metadata": {"intents": ["PERFECT_INTENT"], "state": "PERFECT_STATE", "area": "TARGET"},
        "brand_response": "I have processed a full refund of $25.99 to your card.",  # Good resolution
    }

    # Semantic: cand_a is rank 1, cand_b is rank 2
    # Lexical: cand_a is rank 1, cand_b is rank 2
    results = rrf_reranker.rerank(
        query_text="refund request",
        semantic_candidates=[cand_a, cand_b],
        lexical_candidates=[cand_a, cand_b],
        predicted_intents=["PERFECT_INTENT"],
        predicted_areas=["TARGET"],
        predicted_states=["PERFECT_STATE"],
        top_k=2,
    )

    # cand_a has semantic rank 1 and lexical rank 1 -> RRF = 1/61 + 1/61 = 0.03279
    # cand_b has semantic rank 2 and lexical rank 2 -> RRF = 1/62 + 1/62 = 0.03226
    # Even though cand_b matches predicted intent and cand_a has boilerplate,
    # cand_a MUST rank #1 because RRF depends ONLY on retrieval ranks!
    assert results[0]["case_id"] == "case_a"
    assert results[0]["rrf_score"] == 0.03279
    assert results[1]["case_id"] == "case_b"
    assert results[1]["rrf_score"] == 0.03226


def test_rrf_top_k_truncation(rrf_reranker):
    """Requirement 7: Top-K truncation works accurately."""
    sem = [{"case_id": f"c_{i}", "score": 1.0 - (i * 0.02)} for i in range(20)]
    results_5 = rrf_reranker.rerank("query", semantic_candidates=sem, top_k=5)
    assert len(results_5) == 5

    results_3 = rrf_reranker.rerank("query", semantic_candidates=sem, top_k=3)
    assert len(results_3) == 3


def test_rrf_conversation_deduplication(rrf_reranker):
    """Requirement 8: Conversation deduplication preserves unique threads."""
    sem = [
        {"case_id": "c_1", "conversation_id": "thread_100", "score": 0.90},
        {"case_id": "c_2", "conversation_id": "thread_100", "score": 0.85},
        {"case_id": "c_3", "conversation_id": "thread_200", "score": 0.80},
    ]

    results = rrf_reranker.rerank("query", semantic_candidates=sem, top_k=5)
    # Only 2 results returned because c_1 and c_2 share thread_100
    assert len(results) == 2
    assert results[0]["case_id"] == "c_1"
    assert results[1]["case_id"] == "c_3"
