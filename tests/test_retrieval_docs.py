"""Unit and Integration Tests for Retrieval Document Construction & Context Selection.

Covers:
- Tweet graph reconstruction & parent-child navigation
- Branching and multiple response tracking
- Malformed relationships and cycle resilience
- Golden V1 conversation leakage guard
- Deterministic context scoring and capping (max_context_turns)
- Chronological ordering of selected context
- Retrieval document schema invariants and embedding text formatting
"""

from pathlib import Path
import pytest
import pandas as pd

from support_agent.retrieval.conversation_builder import (
    TweetRecord,
    ConversationGraph,
    build_conversation_graph,
)
from support_agent.retrieval.context_selector import (
    score_turn,
    select_relevant_context,
    tokenize,
)
from support_agent.retrieval.document_builder import (
    format_embedding_text,
    validate_retrieval_isolation,
    RetrievalDocument,
    parse_context_clean,
    get_clean_preceding_turns,
    build_retrieval_documents,
)


def test_graph_reconstruction_linear_and_branching():
    mock_cases = pd.DataFrame([
        # Conversation 1: Linear thread
        {
            "case_id": "c1_1",
            "conversation_id": 100,
            "turn_index": 1,
            "customer_tweet_id": 101,
            "response_tweet_id": 102,
            "customer_author_id": "cust_A",
            "customer_message_clean": "My package is missing",
            "brand_response_clean": "Please send your order number",
        },
        {
            "case_id": "c1_2",
            "conversation_id": 100,
            "turn_index": 3,
            "customer_tweet_id": 103,
            "response_tweet_id": 104,
            "customer_author_id": "cust_A",
            "customer_message_clean": "Order is 123-4567890-1234567",
            "brand_response_clean": "We will check tracking",
        },
        # Conversation 2: Multiple responses to same customer tweet (branching)
        {
            "case_id": "c2_1",
            "conversation_id": 200,
            "turn_index": 1,
            "customer_tweet_id": 201,
            "response_tweet_id": 202,
            "customer_author_id": "cust_B",
            "customer_message_clean": "Help with Prime",
            "brand_response_clean": "Here is step 1/2",
        },
        {
            "case_id": "c2_2",
            "conversation_id": 200,
            "turn_index": 2,
            "customer_tweet_id": 201,  # Same customer tweet
            "response_tweet_id": 203,  # Second brand reply
            "customer_author_id": "cust_B",
            "customer_message_clean": "Help with Prime",
            "brand_response_clean": "Here is step 2/2",
        },
    ])

    graph, diag = build_conversation_graph(mock_cases)

    # Invariants
    assert diag["unique_conversations"] == 2
    assert diag["total_cases_processed"] == 4
    assert diag["multiple_responses_count"] == 1  # cust_tid 201 received 2 responses

    # Check parent-child links in linear conversation
    resp_102 = graph.get_tweet(102)
    assert resp_102 is not None
    assert resp_102.in_response_to_tweet_id == 101

    cust_103 = graph.get_tweet(103)
    assert cust_103 is not None
    assert cust_103.in_response_to_tweet_id == 102  # Linked to preceding brand tweet

    # Check ancestor path
    path = graph.get_ancestor_path(104)
    path_ids = [t.tweet_id for t in path]
    assert path_ids == [101, 102, 103, 104]

    # Check branching node children
    children_201 = [t.tweet_id for t in graph.get_children(201)]
    assert 202 in children_201
    assert 203 in children_201


def test_malformed_relationships_handling():
    graph = ConversationGraph()
    # Missing parent
    orphan = TweetRecord(tweet_id=999, author_id="user", role="CUSTOMER", text="hello", in_response_to_tweet_id=888)
    graph.add_tweet(orphan)
    assert graph.get_parent(999) is None  # Does not crash

    # Cycles
    t1 = TweetRecord(tweet_id=1, author_id="u1", role="CUSTOMER", text="1", in_response_to_tweet_id=2)
    t2 = TweetRecord(tweet_id=2, author_id="u2", role="BRAND", text="2", in_response_to_tweet_id=1)
    graph.add_tweet(t1)
    graph.add_tweet(t2)
    path = graph.get_ancestor_path(1, max_depth=10)
    assert len(path) <= 2  # Handled without infinite loop


def test_golden_leakage_assertion():
    golden_path = Path("data/golden/golden_set.jsonl")
    if not golden_path.exists():
        pytest.skip("Golden set file not present.")

    # Valid disjoint IDs
    disjoint_cids = [999999991, 999999992, 999999993]
    assert validate_retrieval_isolation(disjoint_cids, golden_path) is True

    # Intentionally leak a real Golden V1 ID
    import json
    with open(golden_path, "r", encoding="utf-8") as f:
        first_gold = json.loads(f.readline())
    leaked_cid = int(first_gold["conversation_id"])

    with pytest.raises(ValueError, match="CRITICAL LEAKAGE DETECTED"):
        validate_retrieval_isolation([999999991, leaked_cid], golden_path)


def test_context_selector_scoring_and_caps():
    preceding_turns = [
        {"turn_index": 0, "role": "CUSTOMER", "author": "cust", "text": "My package hasn't arrived", "tweet_id": 10},
        {"turn_index": 1, "role": "BRAND", "author": "AmazonHelp", "text": "Please check tracking link", "tweet_id": 11},
        {"turn_index": 2, "role": "CUSTOMER", "author": "cust", "text": "I already checked tracking, it says delayed", "tweet_id": 12},
        {"turn_index": 3, "role": "BRAND", "author": "AmazonHelp", "text": "Can you provide order number?", "tweet_id": 13},
        {"turn_index": 4, "role": "CUSTOMER", "author": "cust", "text": "Order is 123-4567890-1234567", "tweet_id": 14},
        {"turn_index": 5, "role": "BRAND", "author": "AmazonHelp", "text": "Please wait 48 hours for Hermes courier", "tweet_id": 15},
        {"turn_index": 6, "role": "CUSTOMER", "author": "cust", "text": "I already waited 3 days and contacted carrier", "tweet_id": 16},
        {"turn_index": 7, "role": "BRAND", "author": "AmazonHelp", "text": "We will investigate this with Hermes", "tweet_id": 17},
    ]

    curr_msg = "It has been 4 days now, still nothing delivered, I need my refund"

    # Test scoring with max_context_turns = 4
    fmt_ctx, sel_tids, sel_scores, details = select_relevant_context(
        preceding_turns, curr_msg, max_context_turns=4
    )

    # Must respect cap
    assert len(sel_tids) == 4
    assert len(sel_scores) == 4
    assert len(details) == 4

    # Selected turns must be in strictly ascending chronological order
    turn_indices = [d["turn_index"] for d in details]
    assert turn_indices == sorted(turn_indices)

    # High-value signals must be captured (order number, already contacted carrier, courier mention)
    matched_all_reasons = [r for d in details for r in d["matched_reasons"]]
    assert any("order_number_present" in r or "already_contacted_carrier" in r or "waiting_window_exceeded" in r for r in matched_all_reasons)


def test_current_turn_and_response_always_included():
    cust_msg = "Where is my book?"
    brand_resp = "It is arriving tomorrow."
    ctx_str = "CUSTOMER: Hello\nBRAND: Hi"

    emb_text = format_embedding_text(cust_msg, ctx_str, brand_resp)

    assert "CUSTOMER:\nWhere is my book?" in emb_text
    assert "RELEVANT CONTEXT:\nCUSTOMER: Hello\nBRAND: Hi" in emb_text
    assert "AMAZON RESPONSE:\nIt is arriving tomorrow." in emb_text


def test_retrieval_document_schema():
    doc = RetrievalDocument(
        document_id="retrieval_doc_0000001",
        case_id="amazon_case_0000001",
        conversation_id=1572864,
        turn_index=3,
        customer_tweet_id=1572863,
        brand_response_tweet_id=1572865,
        customer_message="Where is my order?",
        relevant_context="CUSTOMER: Order placed\nBRAND: Acknowledged",
        brand_response="We are checking on it",
        selected_context_tweet_ids=[1572860, 1572861],
        selected_context_scores=[2.45, 1.80],
        created_at=None,
        thread_length=6,
        language="en",
        quality_status="OK",
        embedding_text="CUSTOMER:\nWhere is my order?\n\nRELEVANT CONTEXT:\nCUSTOMER: Order placed\nBRAND: Acknowledged\n\nAMAZON RESPONSE:\nWe are checking on it",
    )

    d = doc.to_dict()
    assert d["document_id"] == "retrieval_doc_0000001"
    assert d["customer_tweet_id"] == 1572863
    assert d["brand_response_tweet_id"] == 1572865
    assert len(d["selected_context_scores"]) == 2
    assert "CUSTOMER:" in d["embedding_text"]


def test_deterministic_reproducibility():
    preceding = [
        {"turn_index": 0, "role": "CUSTOMER", "author": "c", "text": "Tracking number 99999999", "tweet_id": 1},
        {"turn_index": 1, "role": "BRAND", "author": "b", "text": "Will look into it", "tweet_id": 2},
    ]
    msg = "Any update on tracking?"

    ctx1, tids1, scores1, _ = select_relevant_context(preceding, msg, max_context_turns=6)
    ctx2, tids2, scores2, _ = select_relevant_context(preceding, msg, max_context_turns=6)

    assert ctx1 == ctx2
    assert tids1 == tids2
    assert scores1 == scores2


def test_clean_context_reconstruction_does_not_use_raw_context(tmp_path):
    """Prove retrieval context does not read raw context text for embedding content."""
    mock_df = pd.DataFrame([
        {
            "case_id": "test_case_001",
            "conversation_id": 5000,
            "turn_index": 1,
            "customer_tweet_id": 5001,
            "response_tweet_id": 5002,
            "customer_author_id": "cust_123",
            "customer_message": "@AmazonHelp My Echo Show is broken! https://t.co/raw123 &amp; need help",
            "customer_message_clean": "My Echo Show is broken! <URL> & need help",
            "brand_response": "@123456 Have you tried restarting your Echo Show? ^SG",
            "brand_response_clean": "Have you tried restarting your Echo Show?",
            "context": [
                {
                    "role": "CUSTOMER",
                    "author": "cust_123",
                    "text": "@AmazonHelp My Echo Show is broken! https://t.co/raw123 &amp; need help",
                }
            ],
            "context_clean": "CUSTOMER: My Echo Show is broken! <URL> & need help",
            "thread_length": 4,
            "language": "en",
            "quality_status": "OK",
        },
        {
            "case_id": "test_case_002",
            "conversation_id": 5000,
            "turn_index": 3,
            "customer_tweet_id": 5003,
            "response_tweet_id": 5004,
            "customer_author_id": "cust_123",
            "customer_message": "@AmazonHelp Yes restarted the Echo Show but still black screen",
            "customer_message_clean": "Yes restarted the Echo Show but still black screen",
            "brand_response": "@123456 We will issue a replacement for your Echo Show. ^HD",
            "brand_response_clean": "We will issue a replacement for your Echo Show.",
            "context": [
                {
                    "role": "CUSTOMER",
                    "author": "cust_123",
                    "text": "@AmazonHelp My Echo Show is broken! https://t.co/raw123 &amp; need help",
                },
                {
                    "role": "BRAND",
                    "author": "AmazonHelp",
                    "text": "@123456 Have you tried restarting your Echo Show? ^SG",
                },
                {
                    "role": "CUSTOMER",
                    "author": "cust_123",
                    "text": "@AmazonHelp Yes restarted the Echo Show but still black screen",
                },
            ],
            "context_clean": (
                "CUSTOMER: My Echo Show is broken! <URL> & need help\n"
                "BRAND: Have you tried restarting your Echo Show?\n"
                "CUSTOMER: Yes restarted the Echo Show but still black screen"
            ),
            "thread_length": 4,
            "language": "en",
            "quality_status": "OK",
        },
    ])

    in_parquet = tmp_path / "mock_cases.parquet"
    out_parquet = tmp_path / "mock_retrieval.parquet"
    golden_file = tmp_path / "mock_golden.jsonl"
    golden_file.write_text('{"conversation_id": 99999}\n', encoding="utf-8")
    mock_df.to_parquet(in_parquet, index=False)

    docs_df, audit = build_retrieval_documents(
        input_parquet_path=in_parquet,
        output_parquet_path=out_parquet,
        golden_path=golden_file,
    )

    assert len(docs_df) == 2

    # Verify second case: has preceding context from first interaction
    doc2 = docs_df[docs_df["case_id"] == "test_case_002"].iloc[0]

    # 1. customer_message comes strictly from customer_message_clean
    assert doc2["customer_message"] == "Yes restarted the Echo Show but still black screen"

    # 2. brand_response comes strictly from brand_response_clean
    assert doc2["brand_response"] == "We will issue a replacement for your Echo Show."

    # 3. relevant_context does NOT contain raw @mentions, raw t.co URLs, HTML entities, or agent signatures
    assert "@AmazonHelp" not in doc2["relevant_context"]
    assert "@123456" not in doc2["relevant_context"]
    assert "https://t.co" not in doc2["relevant_context"]
    assert "&amp;" not in doc2["relevant_context"]
    assert "^SG" not in doc2["relevant_context"]
    assert "^HD" not in doc2["relevant_context"]

    # 4. Context preserved domain entity "Echo Show"
    assert "Echo Show" in doc2["relevant_context"]

    # 5. Provenance tweet IDs were recovered
    assert 5001 in doc2["selected_context_tweet_ids"]
    assert 5002 in doc2["selected_context_tweet_ids"]

    # 6. embedding_text format is strictly tripartite and noise-free
    emb_text = doc2["embedding_text"]
    assert "@" not in emb_text
    assert "t.co" not in emb_text
    assert "&amp;" not in emb_text
    assert "CUSTOMER:\nYes restarted the Echo Show but still black screen" in emb_text
    assert "AMAZON RESPONSE:\nWe will issue a replacement for your Echo Show." in emb_text
