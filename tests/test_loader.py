"""Tests for data loader and validation functions."""

from pathlib import Path
import pytest
import pandas as pd

from support_agent.data.loader import (
    load_cases,
    validate_cases,
    REQUIRED_COLUMNS,
    DEFAULT_PARQUET_FILE,
)
from support_agent.data.schema import SupportCase, TurnContext

# Reference paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = PROJECT_ROOT / "data" / "processed" / "sample_cases.jsonl"


def test_load_cases_missing_file():
    """Verify that a missing file path raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_cases(path=PROJECT_ROOT / "data" / "processed" / "does_not_exist.parquet")


def test_load_cases_unsupported_format(tmp_path):
    """Verify that an unsupported file extension raises ValueError."""
    fake_file = tmp_path / "data.txt"
    fake_file.write_text("dummy")
    with pytest.raises(ValueError, match="Unsupported file format"):
        load_cases(path=fake_file)


def test_load_cases_from_sample():
    """Verify loading from the test sample jsonl file."""
    df = load_cases(path=SAMPLE_PATH)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 100
    for col in REQUIRED_COLUMNS:
        assert col in df.columns


def test_load_cases_limit():
    """Verify that the limit parameter restricts returned rows."""
    df = load_cases(path=SAMPLE_PATH, limit=10)
    assert len(df) == 10


def test_validate_cases_success():
    """Verify that valid dataset passes validation."""
    df = load_cases(path=SAMPLE_PATH)
    assert validate_cases(df) is True


def test_validate_cases_missing_column():
    """Verify that missing required columns triggers ValueError."""
    df = load_cases(path=SAMPLE_PATH)
    df_missing = df.drop(columns=["customer_message_original"])
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_cases(df_missing)


def test_validate_cases_empty_df():
    """Verify that empty DataFrame triggers ValueError."""
    empty_df = pd.DataFrame(columns=REQUIRED_COLUMNS)
    with pytest.raises(ValueError, match="Dataset is empty"):
        validate_cases(empty_df)


def test_validate_cases_invalid_type():
    """Verify that non-DataFrame input triggers TypeError."""
    with pytest.raises(TypeError, match="Expected pandas DataFrame"):
        validate_cases("not a dataframe")


def test_schema_turn_context_and_case():
    """Verify basic schema domain model creation and validation."""
    turn = TurnContext(role="CUSTOMER", author="user_1", text="Order delayed")
    assert turn.role == "CUSTOMER"
    assert turn.to_dict()["author"] == "user_1"

    case = SupportCase.from_dict({
        "case_id": "amazon_case_0000001",
        "conversation_id": 101,
        "response_tweet_id": 202,
        "customer_tweet_id": 303,
        "customer_author_id": "user_1",
        "turn_index": 0,
        "customer_message_original": "Where is my package?",
        "customer_message_clean": "Where is my package?",
        "brand_response_original": "Hi, please send us a DM.",
        "brand_response_clean": "Hi, please send us a DM.",
        "context": [{"role": "CUSTOMER", "author": "user_1", "text": "Where is my package?"}],
        "thread_length": 2,
    })
    case.validate()
    assert case.case_id == "amazon_case_0000001"
    assert case.conversation_id == 101
