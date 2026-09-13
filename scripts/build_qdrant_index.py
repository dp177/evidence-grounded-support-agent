"""Build and persist local Qdrant vector index for historical retrieval documents.

Enforces zero Golden V1 leakage assertion, validates payload schema,
and writes artifacts/retrieval/qdrant_manifest.json.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

import numpy as np
import pandas as pd
from qdrant_client.http.models import PointStruct

from support_agent.retrieval.embeddings import EmbeddingEngine, compute_corpus_hash
from support_agent.retrieval.vector_store import QdrantVectorStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("build_qdrant_index")

REQUIRED_COLUMNS = [
    "document_id",
    "case_id",
    "conversation_id",
    "turn_index",
    "customer_tweet_id",
    "brand_response_tweet_id",
    "customer_message",
    "relevant_context",
    "brand_response",
    "selected_context_tweet_ids",
    "selected_context_scores",
    "thread_length",
    "language",
    "quality_status",
    "embedding_text",
]


def validate_schema(df: pd.DataFrame) -> None:
    """Validate that dataframe contains all required columns for payload and embedding."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Retrieval documents dataframe missing required columns: {missing}")
    logger.info("Schema validation PASSED (%d required columns present)", len(REQUIRED_COLUMNS))


def validate_golden_exclusion(
    indexed_conversation_ids: Set[int],
    golden_path: str = "data/golden/golden_set.jsonl",
) -> Dict[str, Any]:
    """Ensure zero overlap between golden evaluation conversation IDs and indexed corpus."""
    golden_file = Path(golden_path)
    if not golden_file.exists():
        raise FileNotFoundError(f"Golden set file not found: {golden_path}")

    golden_cids: Set[int] = set()
    with open(golden_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                cid = record.get("conversation_id")
                if cid is not None:
                    golden_cids.add(int(cid))

    overlap = golden_cids.intersection(indexed_conversation_ids)
    overlap_count = len(overlap)

    report = {
        "golden_conversations_excluded": len(golden_cids),
        "indexed_conversations": len(indexed_conversation_ids),
        "overlap_count": overlap_count,
    }

    logger.info(
        "Golden Leakage Check: %d golden conversations, %d indexed conversations, %d overlap",
        report["golden_conversations_excluded"],
        report["indexed_conversations"],
        overlap_count,
    )

    if overlap_count > 0:
        raise ValueError(
            f"CRITICAL: Golden V1 leakage detected! {overlap_count} Golden conversation IDs found in index corpus: {overlap}"
        )

    return report


def build_payload(row: pd.Series) -> Dict[str, Any]:
    """Construct clean, JSON-serializable Qdrant payload from a dataframe row."""
    # Convert numpy arrays/lists to standard python lists
    selected_context_tweet_ids = row["selected_context_tweet_ids"]
    if isinstance(selected_context_tweet_ids, np.ndarray):
        selected_context_tweet_ids = selected_context_tweet_ids.tolist()
    elif isinstance(selected_context_tweet_ids, list):
        selected_context_tweet_ids = [int(x) for x in selected_context_tweet_ids]
    else:
        selected_context_tweet_ids = []

    selected_context_scores = row["selected_context_scores"]
    if isinstance(selected_context_scores, np.ndarray):
        selected_context_scores = selected_context_scores.tolist()
    elif isinstance(selected_context_scores, list):
        selected_context_scores = [float(x) for x in selected_context_scores]
    else:
        selected_context_scores = []

    return {
        "document_id": str(row["document_id"]),
        "case_id": str(row["case_id"]),
        "conversation_id": int(row["conversation_id"]),
        "turn_index": int(row["turn_index"]),
        "customer_tweet_id": int(row["customer_tweet_id"]) if pd.notna(row["customer_tweet_id"]) else None,
        "brand_response_tweet_id": int(row["brand_response_tweet_id"]) if pd.notna(row["brand_response_tweet_id"]) else None,
        "customer_message": str(row["customer_message"]) if pd.notna(row["customer_message"]) else "",
        "relevant_context": str(row["relevant_context"]) if pd.notna(row["relevant_context"]) else "",
        "brand_response": str(row["brand_response"]) if pd.notna(row["brand_response"]) else "",
        "selected_context_tweet_ids": selected_context_tweet_ids,
        "selected_context_scores": selected_context_scores,
        "thread_length": int(row["thread_length"]) if pd.notna(row["thread_length"]) else 0,
        "language": str(row["language"]) if pd.notna(row["language"]) else "en",
        "quality_status": str(row["quality_status"]) if pd.notna(row["quality_status"]) else "valid",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Qdrant vector index for historical retrieval")
    parser.add_argument("--documents", default="data/processed/retrieval_documents.parquet", help="Path to retrieval parquet")
    parser.add_argument("--golden", default="data/golden/golden_set.jsonl", help="Path to Golden V1 jsonl")
    parser.add_argument("--config", default="configs/retrieval.yaml", help="Path to retrieval configuration")
    parser.add_argument("--batch-size", type=int, default=1000, help="Qdrant upsert batch size")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit for testing")
    parser.add_argument("--force-recompute-embeddings", action="store_true", help="Force embedding recomputation")
    parser.add_argument("--sample-metadata", default=None, help="Path to sample metadata json (e.g. data/processed/qdrant_development_sample_metadata.json)")
    args = parser.parse_args()

    t_start = time.time()
    logger.info("Starting Qdrant index build...")

    # 1. Load retrieval documents
    logger.info("Loading retrieval documents from %s", args.documents)
    df = pd.read_parquet(args.documents)
    if args.limit:
        logger.info("Applying limit: %d rows (testing mode)", args.limit)
        df = df.head(args.limit).copy()

    logger.info("Loaded %d documents", len(df))

    # 2. Validate schema
    validate_schema(df)

    # 3. Validate Golden V1 exclusion
    indexed_cids = set(int(cid) for cid in df["conversation_id"].unique())
    leakage_report = validate_golden_exclusion(indexed_cids, golden_path=args.golden)

    # 4. Compute or load embeddings
    embedding_engine = EmbeddingEngine.from_config(config_path=args.config)
    corpus_hash = compute_corpus_hash(df["embedding_text"])
    embeddings = embedding_engine.get_or_create_embeddings(
        df=df,
        text_column="embedding_text",
        source_path=args.documents,
        force_recompute=args.force_recompute_embeddings,
        show_progress_bar=True,
    )

    if len(embeddings) != len(df):
        raise ValueError(f"Embedding count ({len(embeddings)}) does not match document count ({len(df)})")

    # 5. Initialize Qdrant Local
    logger.info("Initializing QdrantVectorStore from %s", args.config)
    vector_store = QdrantVectorStore.from_config(config_path=args.config)

    # 6. Create collection
    collection_name = "amazon_support_cases_v1"
    dim = embedding_engine.dimension
    logger.info("Creating Qdrant collection '%s' (dim=%d, distance=cosine)...", collection_name, dim)
    vector_store.create_collection(
        collection_name=collection_name,
        dimension=dim,
        distance="cosine",
    )

    # 7. Insert points in batches
    logger.info("Indexing %d points in batches of %d...", len(df), args.batch_size)
    total_docs = len(df)
    points_to_upsert: List[PointStruct] = []
    total_upserted = 0

    t_upsert_start = time.time()
    for idx, (_, row) in enumerate(df.iterrows()):
        payload = build_payload(row)
        vector = embeddings[idx].tolist()

        points_to_upsert.append(
            PointStruct(
                id=idx,
                vector=vector,
                payload=payload,
            )
        )

        if len(points_to_upsert) >= args.batch_size:
            vector_store.upsert(collection_name, points_to_upsert)
            total_upserted += len(points_to_upsert)
            points_to_upsert = []
            if total_upserted % 10000 == 0 or total_upserted == total_docs:
                logger.info(
                    "Upserted %d / %d points (%.1f%%) in %.1fs",
                    total_upserted,
                    total_docs,
                    100.0 * total_upserted / total_docs,
                    time.time() - t_upsert_start,
                )

    if points_to_upsert:
        vector_store.upsert(collection_name, points_to_upsert)
        total_upserted += len(points_to_upsert)

    logger.info("Completed upserting %d points in %.2fs", total_upserted, time.time() - t_upsert_start)

    # 8. Verify point count and vector dimension
    verified_count = vector_store.count(collection_name)
    coll_info = vector_store.get_collection_info(collection_name)
    logger.info(
        "Verification: Qdrant reports %d points in collection '%s' (dimension=%s, distance=%s)",
        verified_count,
        collection_name,
        coll_info.get("vector_dimension"),
        coll_info.get("distance"),
    )

    if verified_count != len(df):
        raise ValueError(f"Verification FAILED: expected {len(df)} points, got {verified_count}")

    # 9. Save Qdrant manifest
    manifest_path = Path("artifacts/retrieval/qdrant_manifest.json")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    
    sample_metadata = {}
    if args.sample_metadata and Path(args.sample_metadata).exists():
        with open(args.sample_metadata, "r", encoding="utf-8") as f:
            sample_metadata = json.load(f)

    manifest_data = {
        "provider": "qdrant",
        "mode": vector_store.mode,
        "collection_name": collection_name,
        "point_count": verified_count,
        "vector_dimension": dim,
        "distance_metric": "cosine",
        "embedding_model": embedding_engine.model_name,
        "source_dataset": args.documents,
        "corpus_hash": corpus_hash,
        "golden_exclusion_count": leakage_report["golden_conversations_excluded"],
        "indexed_conversations": leakage_report["indexed_conversations"],
        "build_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    }
    
    if sample_metadata:
        manifest_data["sampling_strategy"] = "hierarchical_stratified"
        manifest_data["target_size"] = sample_metadata.get("selected_count", verified_count)
        manifest_data["random_seed"] = sample_metadata.get("random_seed")
        manifest_data["conversation_cap"] = sample_metadata.get("conversation_cap")
        manifest_data["unique_conversations"] = sample_metadata.get("unique_conversations")
        # We assume corpus_hash above is the sample hash, let's keep source corpus hash if possible
        # Actually it's enough to dump the sample metadata dict as a sub-object or merge it
        manifest_data["sample_metadata"] = sample_metadata

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    logger.info("Saved Qdrant manifest to %s", manifest_path)
    logger.info("ALL STEPS COMPLETED in %.2fs", time.time() - t_start)


if __name__ == "__main__":
    main()
