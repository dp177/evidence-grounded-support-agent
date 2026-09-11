"""Run Majority Baseline on the locked Golden Evaluation Set v1.

Determines the majority intent strictly from the development pool and evaluates on Golden v1.
Outputs: results/majority_baseline.json
"""

import json
from pathlib import Path
import sys
import pandas as pd

# Ensure 'src' is importable
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from support_agent.classification.majority import MajorityClassifier
from support_agent.evaluation.classification_metrics import (
    evaluate_primary_intent,
    evaluate_multi_intent,
    evaluate_status,
)


def run_majority():
    print("=" * 60)
    print("RUNNING MAJORITY BASELINE EVALUATION")
    print("=" * 60)

    # 1. Load split manifest to guarantee zero leakage
    manifest_path = ROOT_DIR / "data" / "splits" / "split_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    golden_conv_ids = set(str(c) for c in manifest["golden_conversation_ids"])
    print(f"Loaded {len(golden_conv_ids)} isolated golden conversation IDs.")

    # 2. Load development training pool
    dev_parquet = ROOT_DIR / "data" / "processed" / "amazon_support_cases.parquet"
    print(f"Loading canonical cases from: {dev_parquet}")
    df_raw = pd.read_parquet(dev_parquet)

    # Strictly filter out golden conversations
    dev_df = df_raw[~df_raw["conversation_id"].astype(str).isin(golden_conv_ids)].copy()
    print(f"Total canonical cases: {len(df_raw)}")
    print(f"Development training pool size: {len(dev_df)} cases (Zero golden cases included)")

    # 3. Fit Majority Classifier
    clf = MajorityClassifier()
    clf.fit(dev_df, golden_conversation_ids=golden_conv_ids)
    print(f"Majority intent determined from dev pool: '{clf.majority_intent_}' (Area: {clf.majority_area_})")
    print(f"Top 5 intent match frequencies in dev pool: {sorted(clf.intent_counts_.items(), key=lambda x: x[1], reverse=True)[:5]}")

    # 4. Load Golden v1 cases
    golden_path = ROOT_DIR / "data" / "golden" / "golden_set.jsonl"
    golden_cases = []
    with open(golden_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                golden_cases.append(json.loads(line))
    print(f"Loaded {len(golden_cases)} test cases from {golden_path}")

    # 5. Predict on Golden v1
    preds = clf.predict(golden_cases)
    pred_records = clf.predict_records(golden_cases)

    # 6. Extract ground truth labels
    # Primary intent evaluation on NORMAL cases (or all cases treating non-normal as NONE)
    gold_primary = [c.get("primary_intent") or "OUT_OF_SCOPE_OR_AMBIGUOUS" for c in golden_cases]
    y_pred_primary = [p if c.get("classification_status") == "NORMAL" else p for c, p in zip(golden_cases, preds)]

    # Also evaluate on normal cases only
    normal_indices = [i for i, c in enumerate(golden_cases) if c.get("classification_status") == "NORMAL"]
    normal_true = [golden_cases[i]["primary_intent"] for i in normal_indices]
    normal_pred = [preds[i] for i in normal_indices]

    metrics_normal = evaluate_primary_intent(normal_true, normal_pred)

    gold_intents = [c.get("intents", []) for c in golden_cases]
    pred_intents = [r["intents"] for r in pred_records]
    metrics_multi = evaluate_multi_intent(gold_intents, pred_intents)

    gold_status = [c.get("classification_status", "NORMAL") for c in golden_cases]
    pred_status = [r["classification_status"] for r in pred_records]
    metrics_status = evaluate_status(gold_status, pred_status)

    output = {
        "model": "MajorityBaseline",
        "development_pool_size": len(dev_df),
        "golden_test_size": len(golden_cases),
        "majority_intent": clf.majority_intent_,
        "majority_area": clf.majority_area_,
        "primary_intent_normal_cases": {
            "total_normal_cases": len(normal_indices),
            "accuracy": round(metrics_normal["accuracy"], 4),
            "macro_f1": round(metrics_normal["macro_f1"], 4),
            "weighted_f1": round(metrics_normal["weighted_f1"], 4),
        },
        "multi_intent_metrics": {
            "micro_f1": round(metrics_multi["micro_f1"], 4),
            "macro_f1": round(metrics_multi["macro_f1"], 4),
            "exact_set_match": round(metrics_multi["exact_set_match"], 4),
        },
        "status_metrics": {
            "accuracy": round(metrics_status["accuracy"], 4),
            "macro_f1": round(metrics_status["macro_f1"], 4),
        },
        "dev_intent_counts": clf.intent_counts_,
    }

    # Save output
    results_dir = ROOT_DIR / "results"
    results_dir.mkdir(exist_ok=True)
    out_file = results_dir / "majority_baseline.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("-" * 60)
    print(f"Majority Baseline Primary Accuracy (on Normal cases): {metrics_normal['accuracy']:.4f}")
    print(f"Majority Baseline Primary Macro F1: {metrics_normal['macro_f1']:.4f}")
    print(f"Majority Baseline Multi-Intent Micro F1: {metrics_multi['micro_f1']:.4f}")
    print(f"Saved results to: {out_file}")
    print("=" * 60)


if __name__ == "__main__":
    run_majority()
