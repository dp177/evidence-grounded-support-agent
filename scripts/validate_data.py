#!/usr/bin/env python3
"""
Data Validation Script for AmazonHelp Support Cases.

Validates the integrity, schema, distributions, and conversational invariants
of the canonical processed Parquet dataset.

Usage:
    python scripts/validate_data.py
    python scripts/validate_data.py --path data/processed/amazon_support_cases.parquet
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

import pandas as pd

# Fix console encoding on Windows environments
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Required columns that MUST be present for valid support-case operations
REQUIRED_COLUMNS: List[str] = [
    "case_id",
    "conversation_id",
    "response_tweet_id",
    "customer_tweet_id",
    "customer_author_id",
    "turn_index",
    "customer_message_original",
    "customer_message_clean",
    "brand_response_original",
    "brand_response_clean",
    "context",
    "context_clean",
    "thread_length",
]


def validate_dataset(parquet_path: Path) -> bool:
    """
    Perform validation checks on the processed Parquet dataset.

    Returns:
        bool: True if all checks pass, False if any critical check fails.
    """
    print("=" * 65)
    print(" AMAZONHELP SUPPORT CASES: DATASET INTEGRITY VALIDATION")
    print("=" * 65)
    print(f"Target file: {parquet_path.as_posix()}\n")

    if not parquet_path.exists():
        print(f"[FAIL] Target file does not exist: {parquet_path}")
        return False

    file_size_mb = parquet_path.stat().st_size / (1024 * 1024)
    print(f"File size: {file_size_mb:.2f} MB")

    # Load dataset
    try:
        df = pd.read_parquet(parquet_path)
    except Exception as e:
        print(f"[FAIL] Failed to read Parquet file: {e}")
        return False

    is_valid = True
    row_count, col_count = df.shape
    print(f"Loaded records: {row_count:,} rows, {col_count} columns\n")

    # ---------------------------------------------------------
    # 1. Schema & Required Columns Check
    # ---------------------------------------------------------
    print("-" * 65)
    print("1. SCHEMA & REQUIRED COLUMNS")
    print("-" * 65)
    existing_columns = set(df.columns)
    missing_required = [c for c in REQUIRED_COLUMNS if c not in existing_columns]

    if missing_required:
        print(f"[FAIL] Missing required columns: {missing_required}")
        is_valid = False
    else:
        print(f"[PASS] All {len(REQUIRED_COLUMNS)} required columns are present.")

    print("\nColumns & Dtypes:")
    for col, dtype in df.dtypes.items():
        req_flag = " (REQUIRED)" if col in REQUIRED_COLUMNS else ""
        print(f"  - {col:<26}: {str(dtype):<15}{req_flag}")

    # ---------------------------------------------------------
    # 2. Null Value Check
    # ---------------------------------------------------------
    print("\n" + "-" * 65)
    print("2. MISSING / NULL VALUES")
    print("-" * 65)
    null_counts = df.isna().sum()
    total_nulls = null_counts.sum()

    if total_nulls == 0:
        print("[PASS] 0 null values found across all columns.")
    else:
        print(f"[FAIL] Found {total_nulls:,} total null values:")
        for col, n in null_counts[null_counts > 0].items():
            print(f"  - {col}: {n:,} nulls ({n / row_count * 100:.2f}%)")
        is_valid = False

    # ---------------------------------------------------------
    # 3. Identifiers & Uniqueness Checks
    # ---------------------------------------------------------
    print("\n" + "-" * 65)
    print("3. IDENTIFIERS & UNIQUENESS CHECKS")
    print("-" * 65)

    # Case ID
    case_id_dupes = df["case_id"].duplicated().sum()
    if case_id_dupes == 0:
        print(f"[PASS] case_id uniqueness: 100% unique ({df['case_id'].nunique():,} unique, 0 duplicates)")
    else:
        print(f"[FAIL] Duplicate case_id values found: {case_id_dupes:,}")
        is_valid = False

    # Response Tweet ID
    if "response_tweet_id" in df.columns:
        resp_dupes = df["response_tweet_id"].duplicated().sum()
        if resp_dupes == 0:
            print(f"[PASS] response_tweet_id uniqueness: 100% unique (0 duplicates)")
        else:
            print(f"[FAIL] Duplicate response_tweet_id found: {resp_dupes:,}")
            is_valid = False

    # Conversation ID
    if "conversation_id" in df.columns:
        conv_unique = df["conversation_id"].nunique()
        conv_dupes = df["conversation_id"].duplicated().sum()
        print(f"[INFO] Unique conversations: {conv_unique:,}")
        print(f"[INFO] Multi-turn conversation case rows: {conv_dupes:,} (cases sharing a root conversation_id)")

    # Customer Author ID
    if "customer_author_id" in df.columns:
        cust_unique = df["customer_author_id"].nunique()
        print(f"[INFO] Unique customers: {cust_unique:,}")

    # ---------------------------------------------------------
    # 4. Critical Field Integrity & Emptiness Invariants
    # ---------------------------------------------------------
    print("\n" + "-" * 65)
    print("4. CRITICAL FIELD INTEGRITY & VALUE INVARIANTS")
    print("-" * 65)

    # 4a. Original message emptiness check (must be 100% non-empty across entire dataset)
    for field in ["case_id", "customer_message_original", "brand_response_original"]:
        if field in df.columns:
            empty_count = (df[field].astype(str).str.strip() == "").sum()
            if empty_count == 0:
                print(f"[PASS] {field:<28}: 0 empty strings (100% populated)")
            else:
                print(f"[FAIL] {field:<28}: Found {empty_count:,} unexpectedly empty strings!")
                is_valid = False

    # 4b. Cleaned message check in standard 'OK' quality partition
    if "quality_status" in df.columns:
        df_ok = df[df["quality_status"] == "OK"]
        empty_cust_clean_ok = (df_ok["customer_message_clean"].astype(str).str.strip() == "").sum()
        empty_brand_clean_ok = (df_ok["brand_response_clean"].astype(str).str.strip() == "").sum()

        if empty_cust_clean_ok == 0 and empty_brand_clean_ok == 0:
            print(f"[PASS] clean texts in 'OK' quality ({len(df_ok):,} rows): 0 empty strings (100% valid)")
        else:
            print(f"[FAIL] Found unexpected empty cleaned strings in OK rows: cust={empty_cust_clean_ok}, brand={empty_brand_clean_ok}")
            is_valid = False

        # Verify that any empty clean messages in the overall dataset are appropriately flagged
        empty_cust_clean_all = df[df["customer_message_clean"].astype(str).str.strip() == ""]
        if len(empty_cust_clean_all) > 0:
            unflagged_cust = empty_cust_clean_all[~empty_cust_clean_all["is_short_customer"]]
            if len(unflagged_cust) == 0:
                print(f"[PASS] All {len(empty_cust_clean_all)} empty cleaned customer messages are correctly flagged with is_short_customer=True")
            else:
                print(f"[FAIL] Found {len(unflagged_cust)} unflagged empty customer clean messages!")
                is_valid = False

        empty_brand_clean_all = df[df["brand_response_clean"].astype(str).str.strip() == ""]
        if len(empty_brand_clean_all) > 0:
            unflagged_brand = empty_brand_clean_all[~empty_brand_clean_all["is_short_response"]]
            if len(unflagged_brand) == 0:
                print(f"[PASS] All {len(empty_brand_clean_all)} empty cleaned brand responses are correctly flagged with is_short_response=True")
            else:
                print(f"[FAIL] Found {len(unflagged_brand)} unflagged empty brand clean responses!")
                is_valid = False

    # 4c. Numerical ID invariants
    num_fields = ["conversation_id", "response_tweet_id", "customer_tweet_id"]
    for field in num_fields:
        if field in df.columns:
            invalid_ids = (df[field] <= 0).sum()
            if invalid_ids == 0:
                print(f"[PASS] {field:<28}: All values positive (> 0)")
            else:
                print(f"[FAIL] {field:<28}: Found {invalid_ids:,} non-positive values!")
                is_valid = False

    # 4d. Turn index >= 0
    if "turn_index" in df.columns:
        invalid_turns = (df["turn_index"] < 0).sum()
        if invalid_turns == 0:
            print(f"[PASS] {'turn_index':<28}: All values >= 0 (max: {df['turn_index'].max()})")
        else:
            print(f"[FAIL] {'turn_index':<28}: Found {invalid_turns:,} negative turn indices!")
            is_valid = False

    # 4e. Thread length >= 2
    if "thread_length" in df.columns:
        invalid_len = (df["thread_length"] < 2).sum()
        if invalid_len == 0:
            print(f"[PASS] {'thread_length':<28}: All values >= 2")
        else:
            print(f"[FAIL] {'thread_length':<28}: Found {invalid_len:,} thread_length < 2!")
            is_valid = False

    # ---------------------------------------------------------
    # 5. Thread Length Distribution
    # ---------------------------------------------------------
    if "thread_length" in df.columns:
        print("\n" + "-" * 65)
        print("5. THREAD LENGTH DISTRIBUTION")
        print("-" * 65)
        mean_len = df["thread_length"].mean()
        median_len = df["thread_length"].median()
        p25 = df["thread_length"].quantile(0.25)
        p75 = df["thread_length"].quantile(0.75)
        p90 = df["thread_length"].quantile(0.90)
        p95 = df["thread_length"].quantile(0.95)
        p99 = df["thread_length"].quantile(0.99)
        max_len = df["thread_length"].max()

        print(f"Mean thread length       : {mean_len:.2f}")
        print(f"Median thread length     : {median_len:.0f}")
        print(f"25th percentile (Q1)     : {p25:.0f}")
        print(f"75th percentile (Q3)     : {p75:.0f}")
        print(f"90th percentile          : {p90:.0f}")
        print(f"95th percentile          : {p95:.0f}")
        print(f"99th percentile          : {p99:.0f}")
        print(f"Maximum thread length    : {max_len}")

    # ---------------------------------------------------------
    # 6. Language Distribution
    # ---------------------------------------------------------
    if "language" in df.columns:
        print("\n" + "-" * 65)
        print("6. LANGUAGE DISTRIBUTION")
        print("-" * 65)
        lang_counts = df["language"].value_counts()
        print(f"Total detected languages : {len(lang_counts)}")
        print(f"{'Language':<12} {'Count':<10} {'Percentage':<10}")
        print("-" * 34)
        for lang, count in lang_counts.head(10).items():
            pct = count / row_count * 100
            print(f"{str(lang):<12} {count:<10,} {pct:>6.2f}%")
        if len(lang_counts) > 10:
            other_count = lang_counts.iloc[10:].sum()
            other_pct = other_count / row_count * 100
            print(f"{'others (' + str(len(lang_counts) - 10) + ')':<12} {other_count:<10,} {other_pct:>6.2f}%")

    # ---------------------------------------------------------
    # 7. Quality Status Distribution
    # ---------------------------------------------------------
    if "quality_status" in df.columns:
        print("\n" + "-" * 65)
        print("7. QUALITY STATUS DISTRIBUTION")
        print("-" * 65)
        quality_counts = df["quality_status"].value_counts()
        print(f"{'Quality Status':<45} {'Count':<10} {'Percentage':<10}")
        print("-" * 67)
        for status, count in quality_counts.items():
            pct = count / row_count * 100
            print(f"{str(status):<45} {count:<10,} {pct:>6.2f}%")

    # ---------------------------------------------------------
    # Summary & Status
    # ---------------------------------------------------------
    print("\n" + "=" * 65)
    if is_valid:
        print("[SUCCESS] ALL CRITICAL DATASET INTEGRITY CHECKS PASSED.")
        print("=" * 65)
        return True
    else:
        print("[FAILURE] CRITICAL INTEGRITY CHECKS FAILED.")
        print("=" * 65)
        return False


def main() -> None:
    # Resolve default path relative to script location using pathlib
    project_root = Path(__file__).resolve().parent.parent
    default_parquet = project_root / "data" / "processed" / "amazon_support_cases.parquet"

    parser = argparse.ArgumentParser(description="Validate processed AmazonHelp support cases.")
    parser.add_argument(
        "--path",
        type=Path,
        default=default_parquet,
        help="Path to processed parquet file (defaults to data/processed/amazon_support_cases.parquet)",
    )
    args = parser.parse_args()

    passed = validate_dataset(args.path)
    if not passed:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
