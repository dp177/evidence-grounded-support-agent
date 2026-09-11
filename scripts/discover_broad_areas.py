#!/usr/bin/env python3
"""
Broad Area Intent Discovery Script for AmazonHelp Support Cases.

Performs unsupervised clustering across k in [6, 8, 10, 12] on semantic embeddings,
evaluates silhouette scores and cluster balance, extracts top representative cases
closest to cluster centroids, and outputs candidate area summaries.

Usage:
    python scripts/discover_broad_areas.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score

# Fix console encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DISCOVERY_DATA = PROJECT_ROOT / "data" / "processed" / "intent_discovery_cases.parquet"
DEFAULT_OUTPUT_CLUSTERS = PROJECT_ROOT / "data" / "processed" / "intent_discovery_clusters.jsonl"
K_CANDIDATES = [6, 8, 10, 12]
RANDOM_STATE = 42


def extract_cluster_keywords(texts: List[str], top_n: int = 6) -> List[str]:
    """Extract top descriptive n-grams for a cluster using TF-IDF."""
    if not texts:
        return []
    try:
        vec = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=1000,
            min_df=2,
        )
        X = vec.fit_transform(texts)
        scores = np.asarray(X.mean(axis=0)).flatten()
        top_indices = scores.argsort()[::-1][:top_n]
        feature_names = np.array(vec.get_feature_names_out())
        return list(feature_names[top_indices])
    except Exception:
        return []


def suggest_candidate_label(keywords: List[str], representative_texts: List[str]) -> Tuple[str, str]:
    """
    Derive a preliminary candidate area name and description from keywords and examples.
    This serves as a candidate label suggestion for human review.
    """
    joined = " ".join(keywords).lower()
    first_example = representative_texts[0].lower() if representative_texts else ""

    if any(w in joined for w in ["delivery", "delivered", "package", "tracking", "courier", "dispatch"]):
        return "DELIVERY_AND_TRACKING", "Shipment delays, tracking updates, missing delivery, carrier inquiries"
    if any(w in joined for w in ["refund", "refunded", "money", "account", "bank", "charged"]):
        return "REFUND_AND_BILLING", "Refund requests, unauthorized charges, payment status, pricing disputes"
    if any(w in joined for w in ["return", "replacement", "damaged", "defective", "item", "exchange", "pickup"]):
        return "RETURNS_AND_REPLACEMENTS", "Returning items, defective/damaged products, replacement requests, pickup issues"
    if any(w in joined for w in ["order", "cancel", "cancelled", "placed", "ordered"]):
        return "ORDER_MANAGEMENT", "Order status, cancellation requests, order modifications"
    if any(w in joined for w in ["prime", "membership", "subscription", "video", "music", "kindle"]):
        return "DIGITAL_AND_PRIME", "Amazon Prime membership, digital streaming, Kindle, subscription management"
    if any(w in joined for w in ["account", "login", "password", "sign", "email", "otp"]):
        return "ACCOUNT_AND_SECURITY", "Account access, password resets, verification, security issues"
    if any(w in joined for w in ["app", "website", "link", "page", "error", "server"]):
        return "TECHNICAL_AND_APP_ISSUES", "App malfunctions, website checkout errors, broken links"
    
    return "CUSTOMER_SERVICE_GENERAL", "General feedback, service inquiries, follow-up clarification"


def run_broad_discovery(
    discovery_path: Path,
    output_clusters_path: Path,
    k_values: List[int] = K_CANDIDATES,
    selected_k: int = 8,
) -> Dict[str, Any]:
    """
    Execute broad-area clustering experiments and extract representative cases.
    """
    print("=" * 65)
    print("BROAD-AREA INTENT DISCOVERY EXPERIMENT")
    print("=" * 65)
    print(f"Dataset path : {discovery_path.as_posix()}")
    print(f"Output path  : {output_clusters_path.as_posix()}\n")

    # Add src to sys.path
    src_dir = PROJECT_ROOT / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from support_agent.taxonomy.embeddings import get_or_compute_embeddings

    # 1. Load discovery cases
    df = pd.read_parquet(discovery_path)
    print(f"1. Loaded {len(df):,} discovery cases.")

    # 2. Get embeddings
    print("2. Generating / loading semantic embeddings (all-MiniLM-L6-v2)...")
    embeddings = get_or_compute_embeddings(
        texts=df["customer_message_clean"].tolist(),
        ids=df["discovery_id"].tolist(),
    )
    print(f"   Embedding matrix shape: {embeddings.shape}")

    # 3. Clustering sweep over k values
    print("\n" + "-" * 65)
    print("3. CLUSTERING EVALUATION SWEEP (k in [6, 8, 10, 12])")
    print("-" * 65)
    print(f"{'k':<4} {'Silhouette':<12} {'Smallest %':<12} {'Largest %':<12} {'Cluster Sizes'}")
    print("-" * 65)

    experiments = {}
    fitted_models = {}

    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        fitted_models[k] = (kmeans, labels)

        # Silhouette on a representative subsample (for speed & stability)
        sub_indices = np.random.RandomState(RANDOM_STATE).choice(len(embeddings), size=min(4000, len(embeddings)), replace=False)
        sil = silhouette_score(embeddings[sub_indices], labels[sub_indices])

        counts = pd.Series(labels).value_counts().sort_index()
        pcts = counts / len(labels) * 100
        min_pct = pcts.min()
        max_pct = pcts.max()
        size_str = ", ".join([str(c) for c in counts.tolist()])

        print(f"{k:<4} {sil:<12.4f} {min_pct:>6.2f}%      {max_pct:>6.2f}%      [{size_str}]")

        experiments[k] = {
            "silhouette": float(sil),
            "min_pct": float(min_pct),
            "max_pct": float(max_pct),
            "cluster_sizes": [int(c) for c in counts.tolist()],
        }

    # 4. Detailed Extraction on selected candidate k
    print("\n" + "-" * 65)
    print(f"4. EXTRACTING REPRESENTATIVE EXAMPLES FOR CANDIDATE k = {selected_k}")
    print("-" * 65)

    kmeans_sel, labels_sel = fitted_models[selected_k]
    df["cluster_id"] = labels_sel
    centroids = kmeans_sel.cluster_centers_

    cluster_records = []

    for c_id in range(selected_k):
        c_mask = (df["cluster_id"] == c_id)
        c_df = df[c_mask].copy()
        c_embeddings = embeddings[c_mask]
        centroid = centroids[c_id]

        # Compute Euclidean distance to centroid (since embeddings are L2 normalized, Euclidean ~ Cosine distance)
        dists = np.linalg.norm(c_embeddings - centroid, axis=1)
        c_df["dist_to_centroid"] = dists

        # Top 10 closest to centroid
        rep_cases = c_df.sort_values("dist_to_centroid").head(10)

        rep_texts = rep_cases["customer_message_clean"].tolist()
        keywords = extract_cluster_keywords(c_df["customer_message_clean"].sample(min(500, len(c_df)), random_state=RANDOM_STATE).tolist())
        cand_name, cand_desc = suggest_candidate_label(keywords, rep_texts)

        # Confidence based on cluster coherence (distance variance & silhouette)
        avg_dist = float(np.mean(dists))
        coherence_confidence = "HIGH" if avg_dist < 0.75 else ("MEDIUM" if avg_dist < 0.90 else "EXPLORATORY")

        print(f"\n[CLUSTER {c_id}] -> {cand_name} (Size: {len(c_df):,}, {len(c_df)/len(df)*100:.1f}%)")
        print(f"  Description: {cand_desc}")
        print(f"  Top Keywords: {', '.join(keywords[:6])}")
        print(f"  Coherence Confidence: {coherence_confidence} (mean dist: {avg_dist:.3f})")
        print("  Representative customer examples:")
        for idx, row in rep_cases.head(3).iterrows():
            print(f"    * [{row['case_id']}] \"{row['customer_message_clean'][:100]}...\"")

        record = {
            "cluster_id": c_id,
            "candidate_name": cand_name,
            "candidate_description": cand_desc,
            "cluster_size": len(c_df),
            "cluster_percentage": round(len(c_df) / len(df) * 100, 2),
            "top_keywords": keywords,
            "coherence_confidence": coherence_confidence,
            "mean_centroid_distance": round(avg_dist, 4),
            "representative_cases": [
                {
                    "case_id": r["case_id"],
                    "discovery_id": r["discovery_id"],
                    "conversation_id": int(r["conversation_id"]),
                    "turn_index": int(r["turn_index"]),
                    "customer_message_clean": r["customer_message_clean"],
                    "context_clean": r["context_clean"],
                    "brand_response_clean": r["brand_response_clean"],
                    "distance_to_centroid": round(float(r["dist_to_centroid"]), 4),
                }
                for _, r in rep_cases.iterrows()
            ],
        }
        cluster_records.append(record)

    # 5. Save cluster records to JSONL
    output_clusters_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_clusters_path, "w", encoding="utf-8") as f:
        for rec in cluster_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"\n5. Saved {len(cluster_records)} cluster profiles to: {output_clusters_path.as_posix()}")

    return {
        "sweep_experiments": experiments,
        "selected_k": selected_k,
        "cluster_records": cluster_records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover broad support intent areas.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DISCOVERY_DATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_CLUSTERS)
    parser.add_argument("--k", type=int, default=8, help="Selected candidate k for detailed profile extraction")
    args = parser.parse_args()

    run_broad_discovery(args.data, args.output, selected_k=args.k)


if __name__ == "__main__":
    main()
