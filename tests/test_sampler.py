"""Unit tests for retrieval document sampler."""

import pandas as pd
import pytest
from pathlib import Path

from support_agent.retrieval.sampler import build_retrieval_sample, get_thread_bucket, get_turn_bucket


@pytest.fixture
def mock_documents():
    """Create a mock dataset resembling retrieval documents."""
    data = []
    # Create 50 conversations with 1 to 5 documents each
    for cid in range(1, 51):
        num_docs = (cid % 5) + 1
        for i in range(num_docs):
            data.append({
                "document_id": f"doc_{cid}_{i}",
                "case_id": f"case_{cid}",
                "conversation_id": cid,
                "turn_index": i + 1,
                "thread_length": num_docs * 2,
                "language": "en" if cid % 2 == 0 else ("es" if cid % 3 == 0 else "other"),
                "quality_status": "OK" if cid % 5 != 0 else "OTHER",
                "customer_message": "hello " * (cid % 10 + 1),
                "brand_response": "hi " * (cid % 10 + 1),
            })
    return pd.DataFrame(data)


@pytest.fixture
def mock_golden_file(tmp_path):
    """Create a mock golden set jsonl file."""
    golden_path = tmp_path / "mock_golden.jsonl"
    with open(golden_path, "w", encoding="utf-8") as f:
        f.write('{"conversation_id": 1}\n')
        f.write('{"conversation_id": 5}\n')
        f.write('{"conversation_id": 10}\n')
    return str(golden_path)


def test_deterministic_sampling(mock_documents, mock_golden_file):
    """Ensure exact same sample is produced given same seed."""
    df1, _ = build_retrieval_sample(
        mock_documents.copy(),
        target_size=20,
        seed=42,
        max_docs_per_conversation=3,
        golden_path=mock_golden_file,
    )
    df2, _ = build_retrieval_sample(
        mock_documents.copy(),
        target_size=20,
        seed=42,
        max_docs_per_conversation=3,
        golden_path=mock_golden_file,
    )
    assert df1["document_id"].tolist() == df2["document_id"].tolist()

    df3, _ = build_retrieval_sample(
        mock_documents.copy(),
        target_size=20,
        seed=99,
        max_docs_per_conversation=3,
        golden_path=mock_golden_file,
    )
    assert df1["document_id"].tolist() != df3["document_id"].tolist()


def test_exact_target_size(mock_documents, mock_golden_file):
    """Ensure sample size strictly matches target_size."""
    target_sizes = [10, 25, 50]
    for size in target_sizes:
        df, meta = build_retrieval_sample(
            mock_documents.copy(),
            target_size=size,
            seed=42,
            max_docs_per_conversation=3,
            golden_path=mock_golden_file,
        )
        assert len(df) == size
        assert meta["selected_count"] == size


def test_golden_exclusion(mock_documents, mock_golden_file):
    """Ensure Golden conversations are strictly excluded."""
    df, meta = build_retrieval_sample(
        mock_documents.copy(),
        target_size=20,
        seed=42,
        max_docs_per_conversation=3,
        golden_path=mock_golden_file,
    )
    sampled_cids = set(df["conversation_id"].unique())
    golden_cids = {1, 5, 10}
    assert sampled_cids.intersection(golden_cids) == set()
    assert meta["golden_conversations_excluded"] == 3


def test_conversation_cap(mock_documents, mock_golden_file):
    """Ensure no conversation exceeds max_docs_per_conversation."""
    cap = 2
    df, meta = build_retrieval_sample(
        mock_documents.copy(),
        target_size=30,
        seed=42,
        max_docs_per_conversation=cap,
        golden_path=mock_golden_file,
    )
    doc_counts = df["conversation_id"].value_counts()
    assert doc_counts.max() <= cap
    assert meta["conversation_cap"] == cap


def test_no_duplicate_documents(mock_documents, mock_golden_file):
    """Ensure all sampled documents are strictly unique."""
    df, _ = build_retrieval_sample(
        mock_documents.copy(),
        target_size=50,
        seed=42,
        max_docs_per_conversation=3,
        golden_path=mock_golden_file,
    )
    assert df["document_id"].is_unique


def test_distribution_preservation(mock_documents, mock_golden_file):
    """Ensure distributions match as closely as possible within cap constraints."""
    df, meta = build_retrieval_sample(
        mock_documents.copy(),
        target_size=60,
        seed=42,
        max_docs_per_conversation=5,  # no capping impact for this test
        golden_path=mock_golden_file,
    )
    
    # Check language group presence
    assert "en" in df["language"].values
    assert "es" in df["language"].values
    
    # Check correct metadata
    assert meta["full_corpus_count"] == len(mock_documents)
