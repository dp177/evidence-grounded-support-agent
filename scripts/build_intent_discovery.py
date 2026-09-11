#!/usr/bin/env python3
"""
Intent Discovery Dataset Builder for AmazonHelp Support Agent.

Constructs a balanced, stratified 10,000-case dataset for unsupervised
semantic clustering and hierarchical intent discovery.

Sampling Criteria:
- Filter: language == 'en', quality_status == 'OK', customer_message_clean is non-empty.
- Diversity guardrail 1: Maximum 2 cases per conversation_id.
- Diversity guardrail 2: Maximum 3 cases per customer_author_id.
- Stratification: Multi-dimensional bins across:
    * thread_length (short: 2-3, medium: 4-7, long: 8-15, deep: 16+)
    * turn_index (initial: 0, early: 1, mid: 2-4, late: 5+)
    * customer message length (short: <=70, medium: 71-125, long: >125)
- Deterministic: Fixed random seed (SEED=42).
- Output: data/processed/intent_discovery_cases.parquet (with discovery_id).

Usage:
    python scripts/build_intent_discovery.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

# Fix console encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SEED = 42
TARGET_SAMPLE_SIZE = 10000

PRESERVED_COLUMNS: List[str] = [
    "case_id",
    "conversation_id",
    "customer_author_id",
    "turn_index",
    "customer_message_clean",
    "customer_message_original",
    "context_clean",
    "brand_response_clean",
    "thread_length",
    "thread_customer_turns",
    "thread_brand_turns",
    "language",
    "quality_status",
]


def build_discovery_dataset(
    input_path: Path,
    output_path: Path,
    target_size: int = TARGET_SAMPLE_SIZE,
    seed: int = SEED,
) -> pd.DataFrame:
    """
    Extract a stratified, diverse intent discovery dataset.
    """
    print("=" * 65)
    print("BUILDING INTENT DISCOVERY DATASET")
    print("=" * 65)
    print(f"Source: {input_path.as_posix()}")
    print(f"Target: {output_path.as_posix()}\n")

    if not input_path.exists():
        raise FileNotFoundError(f"Source dataset not found: {input_path}")

    # 1. Load canonical dataset
    df_raw = pd.read_parquet(input_path)
    source_rows = len(df_raw)
    print(f"1. Total source rows in canonical dataset: {source_rows:,}")

    # Validate column presence
    missing = [c for c in PRESERVED_COLUMNS if c not in df_raw.columns]
    if missing:
        raise ValueError(f"Missing required columns in source dataset: {missing}")

    # 2. Filter English, OK quality, non-empty clean text
    mask_eligible = (
        (df_raw["language"] == "en")
        & (df_raw["quality_status"] == "OK")
        & (df_raw["customer_message_clean"].astype(str).str.strip() != "")
    )
    df_eligible = df_raw[mask_eligible][PRESERVED_COLUMNS].copy()
    eligible_rows = len(df_eligible)
    print(f"2. Eligible English OK rows: {eligible_rows:,} ({eligible_rows / source_rows * 100:.2f}% of source)")

    # 3. Conversation & Customer dominance guardrails
    # Shuffle first deterministically
    df_shuffled = df_eligible.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    # Restrict max 2 cases per conversation
    conv_counts = df_shuffled.groupby("conversation_id").cumcount()
    df_capped = df_shuffled[conv_counts < 2].copy()

    # Restrict max 3 cases per customer
    cust_counts = df_capped.groupby("customer_author_id").cumcount()
    df_capped = df_capped[cust_counts < 3].copy()
    print(f"3. Rows after conversation (<=2) and customer (<=3) caps: {len(df_capped):,}")

    # 4. Construct Stratification Bins
    # Bin thread length
    thread_bins = pd.cut(
        df_capped["thread_length"],
        bins=[0, 3, 7, 15, 1000],
        labels=["thread_2_3", "thread_4_7", "thread_8_15", "thread_16_plus"],
    )

    # Bin turn index
    turn_bins = pd.cut(
        df_capped["turn_index"],
        bins=[-1, 0, 1, 4, 1000],
        labels=["turn_0", "turn_1", "turn_2_4", "turn_5_plus"],
    )

    # Bin customer message length
    msg_len = df_capped["customer_message_clean"].astype(str).str.len()
    len_bins = pd.cut(
        msg_len,
        bins=[0, 70, 125, 10000],
        labels=["len_short", "len_med", "len_long"],
    )

    # Create composite stratum key
    df_capped["stratum"] = (
        thread_bins.astype(str) + "_" + turn_bins.astype(str) + "_" + len_bins.astype(str)
    )

    # 5. Stratified proportional sampling
    strata = df_capped["stratum"].value_counts()
    sample_fractions = strata / strata.sum()
    target_per_stratum = (sample_fractions * target_size).round().astype(int)

    sampled_dfs = []
    rng = np.random.default_rng(seed)

    for stratum_name, target_count in target_per_stratum.items():
        sub_df = df_capped[df_capped["stratum"] == stratum_name]
        n_to_sample = min(len(sub_df), target_count)
        if n_to_sample > 0:
            sampled_dfs.append(sub_df.sample(n=n_to_sample, random_state=seed))

    df_sample = pd.concat(sampled_dfs, ignore_index=True)

    # Adjust if slight rounding discrepancy from target_size
    diff = target_size - len(df_sample)
    if diff > 0:
        remaining = df_capped[~df_capped["case_id"].isin(df_sample["case_id"])]
        fill = remaining.sample(n=diff, random_state=seed)
        df_sample = pd.concat([df_sample, fill], ignore_index=True)
    elif diff < 0:
        df_sample = df_sample.sample(n=target_size, random_state=seed).reset_index(drop=True)

    # Final deterministic sort by conversation_id and turn_index
    df_sample = df_sample.sort_values(["conversation_id", "turn_index", "case_id"]).reset_index(drop=True)

    # 6. Add discovery_id
    df_sample["discovery_id"] = [f"discovery_{i:05d}" for i in range(len(df_sample))]

    # Order columns: discovery_id first, followed by preserved columns
    final_cols = ["discovery_id"] + PRESERVED_COLUMNS
    df_final = df_sample[final_cols].copy()

    # 7. Save to Parquet
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_parquet(output_path, index=False)
    print(f"4. Saved {len(df_final):,} rows to: {output_path.as_posix()}\n")

    # 8. Print Sampling Statistics
    print("-" * 65)
    print("SAMPLING & DISTRIBUTION STATISTICS")
    print("-" * 65)
    print(f"Total discovery rows       : {len(df_final):,}")
    print(f"Unique conversations       : {df_final['conversation_id'].nunique():,}")
    print(f"Unique customers           : {df_final['customer_author_id'].nunique():,}")
    print(f"Max cases per conversation : {df_final['conversation_id'].value_counts().max()}")
    print(f"Max cases per customer     : {df_final['customer_author_id'].value_counts().max()}")

    print("\nThread Length Quantiles:")
    for q, val in df_final["thread_length"].quantile([0.1, 0.25, 0.5, 0.75, 0.9, 0.99]).items():
        print(f"  - {int(q * 100)}th percentile : {val:.0f}")

    print("\nTurn Index Distribution:")
    turn_counts = df_final["turn_index"].value_counts().sort_index()
    for t in range(min(6, len(turn_counts))):
        c = turn_counts.get(t, 0)
        print(f"  - Turn {t:<2} : {c:>5,} ({c / len(df_final) * 100:>5.1f}%)")
    later_turns = turn_counts[turn_counts.index >= 6].sum()
    print(f"  - Turn 6+ : {later_turns:>5,} ({later_turns / len(df_final) * 100:>5.1f}%)")

    print("\nMessage Length Distribution (customer_message_clean):")
    lens = df_final["customer_message_clean"].astype(str).str.len()
    print(f"  - Mean length   : {lens.mean():.1f} characters")
    print(f"  - Median length : {lens.median():.1f} characters")
    print(f"  - Min / Max     : {lens.min()} / {lens.max()} characters")

    print("\nLanguage Distribution:")
    for lang, count in df_final["language"].value_counts().items():
        print(f"  - {lang:<8} : {count:,} (100.0%)")

    print("=" * 65)
    print("DATASET CREATION SUCCESSFUL.")
    print("=" * 65)

    return df_final


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    default_input = project_root / "data" / "processed" / "amazon_support_cases.parquet"
    default_output = project_root / "data" / "processed" / "intent_discovery_cases.parquet"

    parser = argparse.ArgumentParser(description="Build intent discovery dataset.")
    parser.add_argument("--input", type=Path, default=default_input)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--size", type=int, default=TARGET_SAMPLE_SIZE)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    build_discovery_dataset(args.input, args.output, args.size, args.seed)


if __name__ == "__main__":
    main()
