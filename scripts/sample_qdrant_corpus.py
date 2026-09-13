"""Sample a representative subset of the retrieval corpus for development."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

import pandas as pd

from support_agent.retrieval.sampler import build_retrieval_sample, get_thread_bucket, get_turn_bucket

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sample_qdrant_corpus")


def print_distributions(
    df_full: pd.DataFrame,
    df_old_10k: pd.DataFrame,
    df_new_10k: pd.DataFrame,
) -> None:
    """Print comparative distributions."""
    top_langs = {"en", "es", "fr", "ja", "pt", "de"}

    print("\n" + "=" * 60)
    print("COMPARATIVE DISTRIBUTIONS")
    print("=" * 60)

    print("\n--- Thread Length Bucket ---")
    for b in ["2-4", "5-8", "9-16", "17-32", "33+"]:
        f_p = (df_full["thread_length"].apply(get_thread_bucket) == b).mean() * 100
        o_p = (df_old_10k["thread_length"].apply(get_thread_bucket) == b).mean() * 100
        n_p = (df_new_10k["thread_length"].apply(get_thread_bucket) == b).mean() * 100
        print(f"{b:8s} | Full: {f_p:5.2f}% | Old 10k: {o_p:5.2f}% | New 10k: {n_p:5.2f}%")

    print("\n--- Turn Index Bucket ---")
    for b in ["1", "2", "3-4", "5-8", "9+"]:
        f_p = (df_full["turn_index"].apply(get_turn_bucket) == b).mean() * 100
        o_p = (df_old_10k["turn_index"].apply(get_turn_bucket) == b).mean() * 100
        n_p = (df_new_10k["turn_index"].apply(get_turn_bucket) == b).mean() * 100
        print(f"{b:8s} | Full: {f_p:5.2f}% | Old 10k: {o_p:5.2f}% | New 10k: {n_p:5.2f}%")

    print("\n--- Language Group ---")
    for l in ["en", "ja", "fr", "es", "pt", "de", "other"]:
        f_p = (df_full["language"].apply(lambda x: str(x) if str(x) in top_langs else "other") == l).mean() * 100
        o_p = (df_old_10k["language"].apply(lambda x: str(x) if str(x) in top_langs else "other") == l).mean() * 100
        n_p = (df_new_10k["language"].apply(lambda x: str(x) if str(x) in top_langs else "other") == l).mean() * 100
        print(f"{l:8s} | Full: {f_p:5.2f}% | Old 10k: {o_p:5.2f}% | New 10k: {n_p:5.2f}%")

    print("\n--- Quality Status ---")
    for q in ["OK", "OTHER"]:
        f_p = (df_full["quality_status"].apply(lambda x: "OK" if x == "OK" else "OTHER") == q).mean() * 100
        o_p = (df_old_10k["quality_status"].apply(lambda x: "OK" if x == "OK" else "OTHER") == q).mean() * 100
        n_p = (df_new_10k["quality_status"].apply(lambda x: "OK" if x == "OK" else "OTHER") == q).mean() * 100
        print(f"{q:8s} | Full: {f_p:5.2f}% | Old 10k: {o_p:5.2f}% | New 10k: {n_p:5.2f}%")

    print("\n--- Customer Message Words ---")
    w_f = df_full["customer_message"].str.split().str.len()
    w_o = df_old_10k["customer_message"].str.split().str.len()
    w_n = df_new_10k["customer_message"].str.split().str.len()
    print(f"Full:    mean={w_f.mean():.2f}, std={w_f.std():.2f}, median={w_f.median():.1f}, p90={w_f.quantile(0.9):.1f}")
    print(f"Old 10k: mean={w_o.mean():.2f}, std={w_o.std():.2f}, median={w_o.median():.1f}, p90={w_o.quantile(0.9):.1f}")
    print(f"New 10k: mean={w_n.mean():.2f}, std={w_n.std():.2f}, median={w_n.median():.1f}, p90={w_n.quantile(0.9):.1f}")

    print("\n--- Brand Response Words ---")
    w_f = df_full["brand_response"].str.split().str.len()
    w_o = df_old_10k["brand_response"].str.split().str.len()
    w_n = df_new_10k["brand_response"].str.split().str.len()
    print(f"Full:    mean={w_f.mean():.2f}, std={w_f.std():.2f}, median={w_f.median():.1f}, p90={w_f.quantile(0.9):.1f}")
    print(f"Old 10k: mean={w_o.mean():.2f}, std={w_o.std():.2f}, median={w_o.median():.1f}, p90={w_o.quantile(0.9):.1f}")
    print(f"New 10k: mean={w_n.mean():.2f}, std={w_n.std():.2f}, median={w_n.median():.1f}, p90={w_n.quantile(0.9):.1f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sample retrieval documents for Qdrant development.")
    parser.add_argument("--documents", default="data/processed/retrieval_documents.parquet")
    parser.add_argument("--golden", default="data/golden/golden_set.jsonl")
    parser.add_argument("--out-parquet", default="data/processed/qdrant_development_sample.parquet")
    parser.add_argument("--out-ids", default="data/processed/qdrant_development_sample_ids.json")
    parser.add_argument("--target-size", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-docs-per-conversation", type=int, default=3)
    args = parser.parse_args()

    logger.info("Loading full corpus from %s", args.documents)
    df_full = pd.read_parquet(args.documents)

    logger.info("Building representative sample (target=%d, cap=%d, seed=%d)", args.target_size, args.max_docs_per_conversation, args.seed)
    df_sampled, metadata = build_retrieval_sample(
        documents=df_full.copy(),
        target_size=args.target_size,
        seed=args.seed,
        max_docs_per_conversation=args.max_docs_per_conversation,
        golden_path=args.golden,
    )

    logger.info("Sample generated with exactly %d rows.", len(df_sampled))
    logger.info("Unique conversations: %d", metadata["unique_conversations"])

    # Extract IDs
    selected_ids = df_sampled["document_id"].tolist()
    with open(args.out_ids, "w", encoding="utf-8") as f:
        json.dump(selected_ids, f, indent=2)
    logger.info("Saved sample IDs to %s", args.out_ids)
    
    # Save metadata
    meta_path = args.out_ids.replace("_ids.json", "_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Saved metadata to %s", meta_path)

    # Save Parquet
    df_sampled.to_parquet(args.out_parquet, index=False)
    logger.info("Saved sampled parquet to %s", args.out_parquet)

    # Output Comparative Report
    df_old_10k = df_full.head(args.target_size)
    print_distributions(df_full, df_old_10k, df_sampled)


if __name__ == "__main__":
    main()
