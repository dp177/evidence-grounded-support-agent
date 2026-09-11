"""Unit tests for SupportCase and TurnContext models."""

from pathlib import Path
import pytest
import pandas as pd

from support_agent.data.schema import (
    TurnContext,
    SupportCase,
    CANONICAL_COLUMNS,
    ABSENT_COLUMNS,
)
from support_agent.data.loader import (
    load_cases,
    validate_cases,
    to_support_cases,
    DEFAULT_PARQUET_FILE,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "processed" / "sample_cases.jsonl"


def test_turn_context_serialization():
    turn = TurnContext(role="CUSTOMER", author="12345", text="Help with my order")
    d = turn.to_dict()
    assert d["role"] == "CUSTOMER"
    assert d["author"] == "12345"
    assert d["text"] == "Help with my order"

    turn_restored = TurnContext.from_dict(d)
    assert turn == turn_restored


def test_support_case_from_dict_and_validate():
    case_dict = {
        "case_id": "amazon_case_0000001",
        "conversation_id": 1001,
        "response_tweet_id": 2002,
        "customer_tweet_id": 3003,
        "customer_author_id": "cust_42",
        "turn_index": 1,
        "customer_message_original": "@AmazonHelp my package is late",
        "customer_message_clean": "my package is late",
        "brand_response_original": "@cust_42 We are sorry, please DM us.",
        "brand_response_clean": "We are sorry, please DM us.",
        "context": [
            {"role": "CUSTOMER", "author": "cust_42", "text": "@AmazonHelp my package is late"}
        ],
        "context_clean": "CUSTOMER: my package is late",
        "thread_length": 2,
        "thread_customer_turns": 1,
        "thread_brand_turns": 1,
        "language": "en",
        "quality_status": "OK",
        "response_type": None,
    }
    case = SupportCase.from_dict(case_dict)
    case.validate()

    assert case.case_id == "amazon_case_0000001"
    assert case.conversation_id == 1001
    assert len(case.context) == 1
    assert case.context[0].role == "CUSTOMER"
    assert case.response_type is None

    serialized = case.to_dict()
    assert serialized["case_id"] == "amazon_case_0000001"
    assert serialized["context"][0]["role"] == "CUSTOMER"


def test_validation_errors():
    # Empty case_id
    with pytest.raises(ValueError, match="Invalid case_id"):
        SupportCase.from_dict({
            "case_id": "",
            "conversation_id": 1,
            "response_tweet_id": 1,
            "customer_tweet_id": 1,
            "customer_message_original": "hi",
            "brand_response_original": "hello",
            "thread_length": 2,
        }).validate()

    # Non-positive conversation_id
    with pytest.raises(ValueError, match="conversation_id must be positive"):
        SupportCase.from_dict({
            "case_id": "c1",
            "conversation_id": 0,
            "response_tweet_id": 1,
            "customer_tweet_id": 1,
            "customer_message_original": "hi",
            "brand_response_original": "hello",
            "thread_length": 2,
        }).validate()

    # thread_length < 2
    with pytest.raises(ValueError, match="thread_length must be >= 2"):
        SupportCase.from_dict({
            "case_id": "c1",
            "conversation_id": 1,
            "response_tweet_id": 1,
            "customer_tweet_id": 1,
            "customer_message_original": "hi",
            "brand_response_original": "hello",
            "thread_length": 1,
        }).validate()


def test_canonical_columns_and_absent_columns():
    assert "case_id" in CANONICAL_COLUMNS
    assert "response_tweet_id" in CANONICAL_COLUMNS
    assert "customer_tweet_id" in CANONICAL_COLUMNS
    assert "response_type" in ABSENT_COLUMNS


def test_to_support_cases_from_sample():
    df = load_cases(path=SAMPLE_PATH, limit=10)
    cases = to_support_cases(df)
    assert len(cases) == 10
    assert isinstance(cases[0], SupportCase)
    cases[0].validate()
