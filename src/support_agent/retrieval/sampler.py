"""Hierarchical stratified sampling for retrieval documents."""

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd


def load_golden_conversations(golden_path: str) -> set[int]:
    """Load conversation IDs from the Golden set to exclude them from sampling."""
    golden_file = Path(golden_path)
    golden_cids: set[int] = set()
    if golden_file.exists():
        with open(golden_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    if "conversation_id" in record:
                        golden_cids.add(int(record["conversation_id"]))
    return golden_cids


def get_thread_bucket(val: int) -> str:
    """Bucket thread lengths."""
    if pd.isna(val):
        return "2-4"
    if val <= 4:
        return "2-4"
    if val <= 8:
        return "5-8"
    if val <= 16:
        return "9-16"
    if val <= 32:
        return "17-32"
    return "33+"


def get_turn_bucket(val: int) -> str:
    """Bucket turn indices."""
    if pd.isna(val):
        return "1"
    if val == 1:
        return "1"
    if val == 2:
        return "2"
    if val <= 4:
        return "3-4"
    if val <= 8:
        return "5-8"
    return "9+"


def build_retrieval_sample(
    documents: pd.DataFrame,
    target_size: int = 10000,
    seed: int = 42,
    max_docs_per_conversation: int = 3,
    golden_path: str = "data/golden/golden_set.jsonl",
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Build a representative retrieval corpus sample using hierarchical stratification."""
    initial_count = len(documents)

    # 1. Exclude Golden V1 conversations
    golden_cids = load_golden_conversations(golden_path)
    df_clean = documents[~documents["conversation_id"].isin(golden_cids)].copy()
    candidate_count = len(df_clean)

    # 2. Cap documents per conversation deterministically
    rng = np.random.RandomState(seed)
    df_clean["sub_order"] = rng.rand(len(df_clean))
    df_clean = df_clean.sort_values(["conversation_id", "sub_order"])
    df_capped = df_clean.groupby("conversation_id").head(max_docs_per_conversation).copy()
    df_capped.drop(columns=["sub_order"], inplace=True)

    # 3. Compute Stratification columns
    top_langs = {"en", "es", "fr", "ja", "pt", "de"}
    
    # Stratum features for the full corpus (to get proportional weights)
    documents["lang_group"] = documents["language"].apply(lambda x: str(x) if str(x) in top_langs else "other")
    documents["thread_bucket"] = documents["thread_length"].apply(get_thread_bucket)
    documents["turn_bucket"] = documents["turn_index"].apply(get_turn_bucket)
    documents["quality_group"] = documents["quality_status"].apply(lambda x: "OK" if x == "OK" else "OTHER")
    documents["stratum"] = (
        documents["lang_group"]
        + "|"
        + documents["thread_bucket"]
        + "|"
        + documents["turn_bucket"]
        + "|"
        + documents["quality_group"]
    )

    # Stratum features for the capped pool
    df_capped["lang_group"] = df_capped["language"].apply(lambda x: str(x) if str(x) in top_langs else "other")
    df_capped["thread_bucket"] = df_capped["thread_length"].apply(get_thread_bucket)
    df_capped["turn_bucket"] = df_capped["turn_index"].apply(get_turn_bucket)
    df_capped["quality_group"] = df_capped["quality_status"].apply(lambda x: "OK" if x == "OK" else "OTHER")
    df_capped["stratum"] = (
        df_capped["lang_group"]
        + "|"
        + df_capped["thread_bucket"]
        + "|"
        + df_capped["turn_bucket"]
        + "|"
        + df_capped["quality_group"]
    )

    # 4. Proportional Allocation
    stratum_weights = documents["stratum"].value_counts(normalize=True)
    ideal_counts = stratum_weights * target_size
    alloc = np.floor(ideal_counts).astype(int)
    remainder = ideal_counts - alloc
    shortfall = target_size - alloc.sum()
    if shortfall > 0:
        top_rem = remainder.nlargest(int(shortfall)).index
        for r in top_rem:
            alloc.loc[r] += 1

    # 5. Stratified Sampling
    selected_indices = []
    for stratum, count in alloc.items():
        pool = df_capped[df_capped["stratum"] == stratum]
        take = min(len(pool), int(count))
        if take > 0:
            sampled = pool.sample(n=take, random_state=seed)
            selected_indices.extend(sampled.index.tolist())

    # 6. Fill deficit if any strata were short due to capping
    if len(selected_indices) < target_size:
        deficit = target_size - len(selected_indices)
        unselected = df_capped.loc[~df_capped.index.isin(selected_indices)]
        if len(unselected) < deficit:
            raise ValueError(f"Not enough documents to fill sample target of {target_size}")
        fill = unselected.sample(n=deficit, random_state=seed)
        selected_indices.extend(fill.index.tolist())

    df_sampled = df_capped.loc[selected_indices].copy()

    # Drop temporary stratification columns to keep schema clean
    df_sampled.drop(columns=["lang_group", "thread_bucket", "turn_bucket", "quality_group", "stratum"], inplace=True)
    documents.drop(columns=["lang_group", "thread_bucket", "turn_bucket", "quality_group", "stratum"], inplace=True)

    metadata = {
        "full_corpus_count": initial_count,
        "candidate_count_after_golden_exclusion": candidate_count,
        "selected_count": len(df_sampled),
        "random_seed": seed,
        "conversation_cap": max_docs_per_conversation,
        "unique_conversations": int(df_sampled["conversation_id"].nunique()),
        "golden_conversations_excluded": len(golden_cids),
    }

    return df_sampled, metadata
