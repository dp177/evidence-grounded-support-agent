"""Unit and integration tests for Qdrant vector store, embeddings, and retrieval."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

import numpy as np
import pandas as pd
import pytest
from qdrant_client import models

from support_agent.retrieval.embeddings import EmbeddingEngine, compute_corpus_hash
from support_agent.retrieval.retriever import QdrantRetriever, format_query_text
from support_agent.retrieval.vector_store import (
    QdrantVectorStore,
    VectorStore,
    get_vector_store,
)
from scripts.build_qdrant_index import validate_golden_exclusion, validate_schema, build_payload


class TestVectorStoreAbstraction:
    def test_local_qdrant_initialization(self, tmp_path: Path):
        """Test local Qdrant initializes cleanly with persistent directory."""
        store_path = tmp_path / "qdrant_test"
        store = QdrantVectorStore(mode="local", local_path=str(store_path))
        assert isinstance(store, VectorStore)
        assert store.mode == "local"
        assert store_path.exists()

    def test_cloud_configuration_validation(self, monkeypatch):
        """Test that cloud mode raises errors if URL or API key is missing."""
        monkeypatch.delenv("QDRANT_URL", raising=False)
        monkeypatch.delenv("QDRANT_API_KEY", raising=False)

        # Missing URL
        with pytest.raises(ValueError, match="requires a valid URL"):
            QdrantVectorStore(mode="cloud", cloud_url=None)

        # Missing API key
        with pytest.raises(ValueError, match="requires an API key"):
            QdrantVectorStore(mode="cloud", cloud_url="https://fake.qdrant.io:6333", api_key=None)

    def test_config_switching_via_env(self, monkeypatch, tmp_path: Path):
        """Test switching mode and path via environment variables."""
        test_path = tmp_path / "env_qdrant"
        monkeypatch.setenv("QDRANT_MODE", "local")
        monkeypatch.setenv("QDRANT_PATH", str(test_path))

        store = QdrantVectorStore.from_config()
        assert store.mode == "local"
        assert store.local_path == test_path

    def test_collection_creation_and_info(self, tmp_path: Path):
        """Test collection creation, dimension, and info querying."""
        store = QdrantVectorStore(mode="local", local_path=str(tmp_path))
        coll_name = "test_collection"

        store.create_collection(coll_name, dimension=128, distance="cosine")
        info = store.get_collection_info(coll_name)

        assert info["name"] == coll_name
        assert info["vector_dimension"] == 128
        assert "Cosine" in info["distance"]
        assert store.count(coll_name) == 0

    def test_batch_upsert_and_count(self, tmp_path: Path):
        """Test batch upsert of points and count verification."""
        store = QdrantVectorStore(mode="local", local_path=str(tmp_path))
        coll_name = "test_batch"
        store.create_collection(coll_name, dimension=4, distance="cosine")

        points = [
            models.PointStruct(id=0, vector=[1.0, 0.0, 0.0, 0.0], payload={"doc_id": "d0", "category": "shipping"}),
            models.PointStruct(id=1, vector=[0.0, 1.0, 0.0, 0.0], payload={"doc_id": "d1", "category": "refund"}),
            models.PointStruct(id=2, vector=[0.0, 0.0, 1.0, 0.0], payload={"doc_id": "d2", "category": "damaged"}),
        ]
        upserted = store.upsert(coll_name, points)
        assert upserted == 3
        assert store.count(coll_name) == 3

    def test_search_and_top_k(self, tmp_path: Path):
        """Test search ordering and top_k boundary behavior."""
        store = QdrantVectorStore(mode="local", local_path=str(tmp_path))
        coll_name = "test_search"
        store.create_collection(coll_name, dimension=4, distance="cosine")

        points = [
            models.PointStruct(id=0, vector=[1.0, 0.0, 0.0, 0.0], payload={"doc_id": "d0"}),
            models.PointStruct(id=1, vector=[0.9, 0.1, 0.0, 0.0], payload={"doc_id": "d1"}),
            models.PointStruct(id=2, vector=[0.0, 1.0, 0.0, 0.0], payload={"doc_id": "d2"}),
        ]
        store.upsert(coll_name, points)

        # Query close to point 0
        results = store.search(coll_name, query_vector=[1.0, 0.0, 0.0, 0.0], top_k=2)
        assert len(results) == 2
        assert results[0]["payload"]["doc_id"] == "d0"
        assert results[0]["score"] > 0.99
        assert results[1]["payload"]["doc_id"] == "d1"

    def test_payload_integrity(self, tmp_path: Path):
        """Verify all payload fields are preserved and deserialized accurately."""
        store = QdrantVectorStore(mode="local", local_path=str(tmp_path))
        coll_name = "test_payload"
        store.create_collection(coll_name, dimension=4, distance="cosine")

        payload = {
            "document_id": "retrieval_doc_0000001",
            "case_id": "amazon_case_0000001",
            "conversation_id": 12345,
            "turn_index": 2,
            "customer_tweet_id": 999111,
            "brand_response_tweet_id": 999222,
            "customer_message": "Where is my book?",
            "relevant_context": "CUSTOMER: Order placed\nAMAZON: Shipped yesterday",
            "brand_response": "We are looking into this for you.",
            "selected_context_tweet_ids": [999001, 999002],
            "selected_context_scores": [2.5, 1.8],
            "thread_length": 4,
            "language": "en",
            "quality_status": "valid",
        }
        store.upsert(coll_name, [models.PointStruct(id=1, vector=[0.5, 0.5, 0.5, 0.5], payload=payload)])

        results = store.search(coll_name, query_vector=[0.5, 0.5, 0.5, 0.5], top_k=1)
        assert len(results) == 1
        res_payload = results[0]["payload"]

        assert res_payload["document_id"] == "retrieval_doc_0000001"
        assert res_payload["conversation_id"] == 12345
        assert res_payload["customer_message"] == "Where is my book?"
        assert res_payload["selected_context_tweet_ids"] == [999001, 999002]
        assert res_payload["selected_context_scores"] == [2.5, 1.8]


class TestGoldenLeakageAssertion:
    def test_golden_leakage_assertion_failure(self, tmp_path: Path):
        """Verify build immediately fails if any Golden V1 conversation is in the index pool."""
        golden_file = tmp_path / "golden_set.jsonl"
        with open(golden_file, "w", encoding="utf-8") as f:
            f.write(json.dumps({"conversation_id": 1001, "gold_id": "gold_001"}) + "\n")
            f.write(json.dumps({"conversation_id": 1002, "gold_id": "gold_002"}) + "\n")

        # Overlapping pool
        indexed_cids = {1001, 2001, 2002}

        with pytest.raises(ValueError, match="Golden V1 leakage detected"):
            validate_golden_exclusion(indexed_cids, golden_path=str(golden_file))

    def test_golden_leakage_assertion_success(self, tmp_path: Path):
        """Verify build succeeds when overlap is 0."""
        golden_file = tmp_path / "golden_set.jsonl"
        with open(golden_file, "w", encoding="utf-8") as f:
            f.write(json.dumps({"conversation_id": 1001, "gold_id": "gold_001"}) + "\n")
            f.write(json.dumps({"conversation_id": 1002, "gold_id": "gold_002"}) + "\n")

        # Disjoint pool
        indexed_cids = {2001, 2002, 2003}
        report = validate_golden_exclusion(indexed_cids, golden_path=str(golden_file))
        assert report["overlap_count"] == 0
        assert report["golden_conversations_excluded"] == 2
        assert report["indexed_conversations"] == 3


class TestEmbeddingCacheValidation:
    def test_corpus_hash_deterministic(self):
        """Corpus hash must be deterministic and sensitive to text changes."""
        texts_a = ["Hello world", "Order tracking inquiry"]
        texts_b = ["Hello world", "Order tracking inquiry"]
        texts_c = ["Hello world", "Order tracking inquiry modified"]

        hash_a = compute_corpus_hash(texts_a)
        hash_b = compute_corpus_hash(texts_b)
        hash_c = compute_corpus_hash(texts_c)

        assert hash_a == hash_b
        assert hash_a != hash_c

    def test_cache_invalidation_on_content_change(self, tmp_path: Path):
        """Embedding cache must invalidate and recompute when corpus text hash changes."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()

        df_orig = pd.DataFrame({"embedding_text": ["text one", "text two"]})
        engine = EmbeddingEngine(model_name="all-MiniLM-L6-v2", dimension=384)

        # Mock encode to avoid expensive inference in test
        call_count = [0]
        def mock_encode(texts, **kwargs):
            call_count[0] += 1
            return np.ones((len(texts), 384), dtype=np.float32) * call_count[0]

        engine.encode = mock_encode

        # First compute
        emb1 = engine.get_or_create_embeddings(df_orig, cache_dir=cache_dir, source_path="test.parquet")
        assert call_count[0] == 1
        assert emb1[0, 0] == 1.0

        # Second compute with identical dataframe -> should hit cache without calling encode
        emb2 = engine.get_or_create_embeddings(df_orig, cache_dir=cache_dir, source_path="test.parquet")
        assert call_count[0] == 1  # Not incremented!
        assert emb2[0, 0] == 1.0

        # Third compute with modified text -> should detect hash change and recompute
        df_modified = pd.DataFrame({"embedding_text": ["text one", "text two CHANGED"]})
        emb3 = engine.get_or_create_embeddings(df_modified, cache_dir=cache_dir, source_path="test.parquet")
        assert call_count[0] == 2  # Recomputed!
        assert emb3[0, 0] == 2.0


class TestQueryFormatting:
    def test_format_query_text(self):
        """Query representation matches Phase 6B standard format."""
        formatted = format_query_text(
            customer_message="Package not arrived",
            context="Carrier: In transit",
        )
        expected = "CUSTOMER:\nPackage not arrived\n\nCONTEXT:\nCarrier: In transit"
        assert formatted == expected

    def test_format_query_text_no_context(self):
        """Query representation works cleanly without context."""
        formatted = format_query_text(customer_message="Help please")
        assert formatted == "CUSTOMER:\nHelp please"
