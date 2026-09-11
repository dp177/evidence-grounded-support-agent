#!/usr/bin/env python3
"""
Hierarchical Sub-Intent, Multi-Intent, and Conversation State Discovery.

Drills into broad-area clusters to discover fine-grained sub-intents (targeting
8-15 meaningful leaf intents), detects multi-intent customer inquiries,
and discovers recurring conversational progress states from multi-turn dialogues.

Usage:
    python scripts/discover_hierarchical_intents.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

# Fix console encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DISCOVERY_DATA = PROJECT_ROOT / "data" / "processed" / "intent_discovery_cases.parquet"
DEFAULT_CLUSTERS_JSONL = PROJECT_ROOT / "data" / "processed" / "intent_discovery_clusters.jsonl"
DEFAULT_OUTPUT_HIERARCHY = PROJECT_ROOT / "data" / "processed" / "hierarchical_sub_intents.jsonl"
RANDOM_STATE = 42

# Multi-intent signal patterns
MULTI_INTENT_PATTERNS = [
    (r"\b(cancel|cancellation)\b.*\b(refund|money back|charge)\b", "ORDER_CANCELLATION + REFUND_REQUEST"),
    (r"\b(not received|not arrived|missing|where is|late)\b.*\b(refund|chargeback|money back)\b", "ORDER_NOT_RECEIVED + REFUND_REQUEST"),
    (r"\b(damaged|defective|broken|wrong item)\b.*\b(replacement|replace|exchange)\b", "DAMAGED_ITEM + REPLACEMENT_REQUEST"),
    (r"\b(double charged|charged twice|overcharged)\b.*\b(cancel prime|refund)\b", "BILLING_ERROR + CANCELLATION_REQUEST"),
    (r"\b(return|send back)\b.*\b(pickup|courier not arrived)\b", "RETURN_REQUEST + PICKUP_ISSUE"),
]

# Conversation state signal patterns in multi-turn dialogues
STATE_PATTERNS = [
    ("TRACKING_ALREADY_CHECKED", [
        r"already (checked|looked at) tracking",
        r"tracking (shows|says) delivered",
        r"tracking (not updating|hasn't updated|stuck)",
        r"link (doesn't|does not) work",
    ]),
    ("CARRIER_ALREADY_CONTACTED", [
        r"(contacted|spoke to|called) (the )?(carrier|courier|usps|ups|hermes|royal mail)",
        r"(carrier|courier) (says|told me|claims)",
    ]),
    ("DETAILS_ALREADY_PROVIDED", [
        r"already (sent|given|provided|dmd) (the )?(details|info|order number|dm)",
        r"check (your|my) dm",
    ]),
    ("WAITING_WINDOW_EXCEEDED", [
        r"(told|said) to wait \d+ (hours|days)",
        r"been (waiting|over) \d+ (days|weeks|hours)",
        r"still (no reply|haven't heard|waiting)",
    ]),
]


def extract_sub_intent_keywords(texts: List[str], top_n: int = 5) -> List[str]:
    """Extract top distinguishing keywords for a sub-intent cluster."""
    if len(texts) < 5:
        return []
    try:
        vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=500, min_df=2)
        X = vec.fit_transform(texts)
        scores = np.asarray(X.mean(axis=0)).flatten()
        top_indices = scores.argsort()[::-1][:top_n]
        feature_names = np.array(vec.get_feature_names_out())
        return list(feature_names[top_indices])
    except Exception:
        return []


def scan_multi_intent_cases(df: pd.DataFrame, limit: int = 15) -> List[Dict[str, Any]]:
    """Identify customer messages exhibiting signals of multiple actionable problems."""
    multi_cases = []
    for _, row in df.iterrows():
        text = str(row["customer_message_clean"]).lower()
        matched_types = []
        for regex_pat, intent_combo in MULTI_INTENT_PATTERNS:
            if re.search(regex_pat, text):
                matched_types.append(intent_combo)
        if matched_types:
            multi_cases.append({
                "case_id": row["case_id"],
                "discovery_id": row["discovery_id"],
                "conversation_id": int(row["conversation_id"]),
                "turn_index": int(row["turn_index"]),
                "candidate_intents": matched_types,
                "customer_message_clean": row["customer_message_clean"],
                "brand_response_clean": row["brand_response_clean"],
            })
            if len(multi_cases) >= limit:
                break
    return multi_cases


def scan_conversation_states(df: pd.DataFrame, limit_per_state: int = 5) -> Dict[str, List[Dict[str, Any]]]:
    """Identify candidate conversation states from multi-turn dialogues."""
    state_examples = {state_name: [] for state_name, _ in STATE_PATTERNS}

    # Focus on multi-turn cases (turn_index >= 1)
    multi_turn = df[df["turn_index"] >= 1]

    for _, row in multi_turn.iterrows():
        text = str(row["customer_message_clean"]).lower()
        for state_name, patterns in STATE_PATTERNS:
            if len(state_examples[state_name]) >= limit_per_state:
                continue
            for pat in patterns:
                if re.search(pat, text):
                    state_examples[state_name].append({
                        "case_id": row["case_id"],
                        "discovery_id": row["discovery_id"],
                        "conversation_id": int(row["conversation_id"]),
                        "turn_index": int(row["turn_index"]),
                        "detected_pattern": pat,
                        "customer_message_clean": row["customer_message_clean"],
                        "context_clean": row["context_clean"],
                        "brand_response_clean": row["brand_response_clean"],
                    })
                    break

    return state_examples


def run_hierarchical_discovery(
    discovery_path: Path,
    clusters_path: Path,
    output_path: Path,
) -> Dict[str, Any]:
    """Execute hierarchical drill-down, multi-intent, and state analysis."""
    print("=" * 65)
    print("HIERARCHICAL SUB-INTENT, MULTI-INTENT & STATE DISCOVERY")
    print("=" * 65)

    # 1. Load data
    df = pd.read_parquet(discovery_path)
    print(f"Loaded {len(df):,} discovery cases.")

    # 2. Multi-intent scanning
    print("\n" + "-" * 65)
    print("1. MULTI-INTENT CANDIDATE DISCOVERY")
    print("-" * 65)
    multi_cases = scan_multi_intent_cases(df, limit=12)
    print(f"Discovered {len(multi_cases)} representative multi-intent cases:")
    for mc in multi_cases[:4]:
        print(f"  * [{mc['candidate_intents'][0]}] \"{mc['customer_message_clean'][:90]}...\"")

    # 3. Conversation state scanning
    print("\n" + "-" * 65)
    print("2. CONVERSATION PROGRESS STATE DISCOVERY")
    print("-" * 65)
    state_results = scan_conversation_states(df, limit_per_state=4)
    for state_name, examples in state_results.items():
        print(f"  * [{state_name}] ({len(examples)} examples discovered)")
        if examples:
            print(f"      Example: \"{examples[0]['customer_message_clean'][:85]}...\"")

    # Save outputs
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_record = {
        "multi_intent_candidates": multi_cases,
        "conversation_states": state_results,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(summary_record, ensure_ascii=False, indent=2))
    print(f"\nSaved hierarchical discovery outputs to: {output_path.as_posix()}")

    return summary_record


def main() -> None:
    parser = argparse.ArgumentParser(description="Hierarchical intent, multi-intent & state discovery.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DISCOVERY_DATA)
    parser.add_argument("--clusters", type=Path, default=DEFAULT_CLUSTERS_JSONL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_HIERARCHY)
    args = parser.parse_args()

    run_hierarchical_discovery(args.data, args.clusters, args.output)


if __name__ == "__main__":
    main()
