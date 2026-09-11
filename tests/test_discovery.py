"""Tests for Intent Discovery dataset, deterministic sampling, and invariants."""

from pathlib import Path
import pytest
import pandas as pd

from support_agent.data.loader import REQUIRED_COLUMNS
from scripts.build_intent_discovery import PRESERVED_COLUMNS, build_discovery_dataset

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DISCOVERY_PATH = PROJECT_ROOT / "data" / "processed" / "intent_discovery_cases.parquet"
CANONICAL_PATH = PROJECT_ROOT / "data" / "processed" / "amazon_support_cases.parquet"


def test_discovery_dataset_exists_and_row_count():
    """Verify that the discovery dataset exists and contains exactly 10,000 cases."""
    assert DISCOVERY_PATH.exists(), f"Discovery dataset not found at {DISCOVERY_PATH}"
    df = pd.read_parquet(DISCOVERY_PATH)
    assert len(df) == 10000, f"Expected 10,000 rows, got {len(df)}"


def test_discovery_required_columns():
    """Verify all preserved columns and discovery_id are present."""
    df = pd.read_parquet(DISCOVERY_PATH)
    assert "discovery_id" in df.columns
    for col in PRESERVED_COLUMNS:
        assert col in df.columns, f"Missing preserved column: {col}"


def test_discovery_no_nulls_and_no_empty_customer_messages():
    """Verify 0 null values and non-empty customer clean text."""
    df = pd.read_parquet(DISCOVERY_PATH)
    assert df.isna().sum().sum() == 0, "Discovery dataset contains unexpected null values"
    empty_cust = (df["customer_message_clean"].astype(str).str.strip() == "").sum()
    assert empty_cust == 0, f"Found {empty_cust} empty customer clean messages"


def test_discovery_id_uniqueness_and_format():
    """Verify discovery_id is 100% unique and formatted correctly."""
    df = pd.read_parquet(DISCOVERY_PATH)
    assert df["discovery_id"].duplicated().sum() == 0, "Duplicate discovery_ids found"
    assert df["discovery_id"].iloc[0] == "discovery_00000"
    assert df["discovery_id"].iloc[-1] == "discovery_09999"


def test_conversation_and_customer_caps():
    """Verify conversation dominance guardrails (max 2 cases per conversation, max 3 per customer)."""
    df = pd.read_parquet(DISCOVERY_PATH)
    max_conv = df["conversation_id"].value_counts().max()
    max_cust = df["customer_author_id"].value_counts().max()
    assert max_conv <= 2, f"Conversation dominance exceeded: max {max_conv} > 2"
    assert max_cust <= 3, f"Customer dominance exceeded: max {max_cust} > 3"


def test_deterministic_reproducibility(tmp_path):
    """Verify that sampling is strictly deterministic given the same seed."""
    if not CANONICAL_PATH.exists():
        pytest.skip("Canonical dataset not found for reproducibility test")

    temp_out1 = tmp_path / "disc_test1.parquet"
    temp_out2 = tmp_path / "disc_test2.parquet"

    # Sample small subset of 50 rows deterministically twice
    df1 = build_discovery_dataset(CANONICAL_PATH, temp_out1, target_size=50, seed=42)
    df2 = build_discovery_dataset(CANONICAL_PATH, temp_out2, target_size=50, seed=42)

    assert df1["case_id"].tolist() == df2["case_id"].tolist(), "Sampling is not deterministic"
