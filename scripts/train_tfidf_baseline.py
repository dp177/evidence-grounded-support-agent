"""Train TF-IDF + Logistic Regression Intent Classifier on the development training pool.

Strictly excludes all golden conversation IDs to guarantee zero leakage.
Saves model artifacts to artifacts/tfidf/.
"""

import json
from pathlib import Path
import sys
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from support_agent.classification.majority import DEFAULT_DEV_PATTERNS
from support_agent.classification.tfidf_classifier import TfidfIntentClassifier


def prepare_dev_training_data(
    dev_df: pd.DataFrame,
    max_per_intent: int = 1000,
    random_state: int = 42,
) -> Tuple[List[str], List[str]]:
    """Sample a balanced/stratified labeled training set from development conversations."""
    sampled_texts = []
    sampled_labels = []

    # First include curated development review cases if available
    curated_path = ROOT_DIR / "data" / "processed" / "taxonomy_review_cases.jsonl"
    curated_cases = []
    if curated_path.exists():
        with open(curated_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    curated_cases.append(json.loads(line))
        for c in curated_cases:
            intent = c.get("proposed_intent")
            if intent in DEFAULT_DEV_PATTERNS:
                txt = f"{c.get('customer_message_clean', '')} \n {c.get('context_clean', '')}".strip()
                sampled_texts.append(txt)
                sampled_labels.append(intent)

    print(f"Loaded {len(sampled_texts)} curated development cases.")

    # Next, sample from development pool using high-precision patterns
    rng = np.random.default_rng(random_state)
    for intent, pat in DEFAULT_DEV_PATTERNS.items():
        matches = dev_df[
            dev_df["customer_message_clean"].str.contains(pat, case=False, regex=True, na=False)
        ]
        curr_count = sampled_labels.count(intent)
        needed = max_per_intent - curr_count
        if needed > 0 and len(matches) > 0:
            sample_size = min(needed, len(matches))
            sampled_indices = rng.choice(matches.index, size=sample_size, replace=False)
            sub = dev_df.loc[sampled_indices]
            for _, r in sub.iterrows():
                txt = f"{r.get('customer_message_clean', '')} \n {r.get('context_clean', '')}".strip()
                sampled_texts.append(txt)
                sampled_labels.append(intent)

    return sampled_texts, sampled_labels


def train_tfidf():
    print("=" * 60)
    print("TRAINING TF-IDF + LOGISTIC REGRESSION CLASSIFIER")
    print("=" * 60)

    # 1. Load split manifest to verify zero leakage
    manifest_path = ROOT_DIR / "data" / "splits" / "split_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    golden_conv_ids = set(str(c) for c in manifest["golden_conversation_ids"])
    print(f"Loaded {len(golden_conv_ids)} isolated golden conversation IDs.")

    # 2. Load development dataset
    parquet_path = ROOT_DIR / "data" / "processed" / "amazon_support_cases.parquet"
    print(f"Loading development pool from: {parquet_path}")
    df_raw = pd.read_parquet(parquet_path)

    dev_df = df_raw[~df_raw["conversation_id"].astype(str).isin(golden_conv_ids)].copy()
    print(f"Development pool size: {len(dev_df)} cases (Zero golden conversations).")

    # 3. Prepare training samples
    texts, labels = prepare_dev_training_data(dev_df, max_per_intent=1000)
    print(f"Total training examples extracted: {len(texts)}")

    label_counts = pd.Series(labels).value_counts()
    print("\n--- Training Class Distribution ---")
    for intent, cnt in label_counts.items():
        print(f"  {intent}: {cnt}")

    # 4. Fit classifier
    print("\nFitting TfidfIntentClassifier (max_features=10000, C=1.0)...")
    clf = TfidfIntentClassifier(max_features=10000, ngram_range=(1, 2), C=1.0, max_iter=1000)
    clf.fit(texts, labels)
    print(f"Fitted on {len(clf.classes_)} classes. Vocabulary size: {len(clf.vectorizer.vocabulary_)}")

    # 5. Save model bundle
    artifact_dir = ROOT_DIR / "artifacts" / "tfidf"
    saved_file = clf.save(artifact_dir)
    print(f"Model successfully saved to: {saved_file}")
    print(f"Metadata saved to: {artifact_dir / 'metadata.json'}")
    print("=" * 60)


if __name__ == "__main__":
    train_tfidf()
