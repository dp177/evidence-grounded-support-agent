"""
Data loader module for AmazonHelp support cases.

Provides simple, robust, reusable functions for loading and validating
the processed support cases dataset.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Union

import pandas as pd

from support_agent.data.schema import SupportCase

# Default repository location resolved relative to module file
DEFAULT_DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "processed"
DEFAULT_PARQUET_FILE = DEFAULT_DATA_DIR / "amazon_support_cases.parquet"
DEFAULT_CSV_FILE = DEFAULT_DATA_DIR / "amazon_support_cases.csv"

# Minimum required columns for support-case processing
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


def get_default_dataset_path() -> Path:
    """
    Determine the default dataset path.

    Prefers Parquet for speed and nested structure preservation;
    falls back to CSV if Parquet is not present.
    """
    if DEFAULT_PARQUET_FILE.exists():
        return DEFAULT_PARQUET_FILE
    if DEFAULT_CSV_FILE.exists():
        return DEFAULT_CSV_FILE
    raise FileNotFoundError(
        f"Default dataset not found. Looked for:\n"
        f"  - {DEFAULT_PARQUET_FILE}\n"
        f"  - {DEFAULT_CSV_FILE}"
    )


def validate_cases(df: pd.DataFrame) -> bool:
    """
    Validate that a support-case DataFrame adheres to required schema and integrity rules.

    Args:
        df: pandas DataFrame to validate.

    Returns:
        bool: True if validation passes.

    Raises:
        TypeError: If input is not a pandas DataFrame.
        ValueError: If required columns are missing, dataset is empty,
                    or critical integrity checks fail.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")

    if df.empty:
        raise ValueError("Dataset is empty (0 rows)")

    # 1. Required column presence
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in dataset: {missing_cols}")

    # 2. Case ID uniqueness
    duplicate_cases = df["case_id"].duplicated().sum()
    if duplicate_cases > 0:
        raise ValueError(f"Dataset contains {duplicate_cases:,} duplicate case_id values")

    # 3. Response Tweet ID uniqueness
    duplicate_responses = df["response_tweet_id"].duplicated().sum()
    if duplicate_responses > 0:
        raise ValueError(f"Dataset contains {duplicate_responses:,} duplicate response_tweet_id values")

    # 4. Critical text fields must not be entirely empty
    for field in ["case_id", "customer_message_original", "brand_response_original"]:
        empty_count = (df[field].astype(str).str.strip() == "").sum()
        if empty_count > 0:
            raise ValueError(f"Column '{field}' contains {empty_count:,} empty strings")

    # 5. Numerical ID positivity
    for num_col in ["conversation_id", "response_tweet_id", "customer_tweet_id"]:
        invalid_num = (df[num_col] <= 0).sum()
        if invalid_num > 0:
            raise ValueError(f"Column '{num_col}' contains {invalid_num:,} non-positive identifiers")

    return True


def load_cases(
    path: Optional[Union[str, Path]] = None,
    language: Optional[str] = None,
    quality_ok_only: bool = False,
    columns: Optional[List[str]] = None,
    limit: Optional[int] = None,
) -> pd.DataFrame:
    """
    Load support cases into a pandas DataFrame.

    Prefers Parquet format. Falls back to CSV if explicitly requested or if
    path points to a .csv file.

    Args:
        path: Path to dataset file (.parquet or .csv). If None, uses default.
        language: Optional language code filter (e.g., 'en').
        quality_ok_only: If True, filters for quality_status == 'OK'.
        columns: Optional list of specific columns to load.
        limit: Optional maximum number of rows to return.

    Returns:
        pd.DataFrame containing loaded cases.

    Raises:
        FileNotFoundError: If the specified or default file does not exist.
        ValueError: If an unsupported file extension is provided.
    """
    file_path = Path(path) if path else get_default_dataset_path()

    if not file_path.exists():
        raise FileNotFoundError(f"Support cases dataset not found at: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix == ".parquet":
        filters = []
        if language is not None:
            filters.append(("language", "==", language))
        if quality_ok_only:
            filters.append(("quality_status", "==", "OK"))

        df = pd.read_parquet(
            file_path,
            columns=columns,
            filters=filters if filters else None,
        )

    elif suffix == ".csv":
        df = pd.read_csv(file_path, usecols=columns)
        if language is not None and "language" in df.columns:
            df = df[df["language"] == language]
        if quality_ok_only and "quality_status" in df.columns:
            df = df[df["quality_status"] == "OK"]

    elif suffix == ".jsonl":
        import json
        records = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        df = pd.DataFrame(records)
        if columns:
            df = df[[c for c in columns if c in df.columns]]
        if language is not None and "language" in df.columns:
            df = df[df["language"] == language]
        if quality_ok_only and "quality_status" in df.columns:
            df = df[df["quality_status"] == "OK"]

    else:
        raise ValueError(
            f"Unsupported file format '{suffix}'. Expected '.parquet', '.csv', or '.jsonl'"
        )

    if limit is not None and limit > 0:
        df = df.iloc[:limit]

    return df


def to_support_cases(df: pd.DataFrame) -> List[SupportCase]:
    """Convert a support-case DataFrame into a list of validated SupportCase objects."""
    return [SupportCase.from_dict(row) for row in df.to_dict(orient="records")]
