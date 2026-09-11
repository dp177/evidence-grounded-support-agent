"""Evaluate TF-IDF + Logistic Regression baseline on Golden Evaluation Set v1.

Loads model from artifacts/tfidf/ and evaluates on data/golden/golden_set.jsonl.
Outputs metrics and returns dictionary.
"""

import json
from pathlib import Path
import sys
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from support_agent.classification.tfidf_classifier import TfidfIntentClassifier
from support_agent.evaluation.classification_metrics import (
    evaluate_calibration,
    evaluate_multi_intent,
    evaluate_primary_intent,
    evaluate_status,
    evaluate_threshold_abstention,
)


def evaluate_tfidf(golden_path: Path = ROOT_DIR / "data" / "golden" / "golden_set.jsonl"):
    print("=" * 60)
    print("EVALUATING TF-IDF + LOGISTIC REGRESSION BASELINE")
    print("=" * 60)

    # 1. Load model
    model_dir = ROOT_DIR / "artifacts" / "tfidf"
    print(f"Loading TF-IDF model from: {model_dir}")
    clf = TfidfIntentClassifier.load(model_dir)
    print(f"Model loaded. Classes ({len(clf.classes_)}): {clf.classes_}")

    # 2. Load Golden Set
    cases = []
    with open(golden_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
    print(f"Loaded {len(cases)} test cases from {golden_path}")

    # 3. Predict
    records = clf.predict_cases(cases)

    # 4. Extract ground truth and predictions for NORMAL cases
    normal_indices = [i for i, c in enumerate(cases) if c.get("classification_status") == "NORMAL"]
    normal_true = [cases[i]["primary_intent"] for i in normal_indices]
    normal_pred = [records[i]["primary_intent"] for i in normal_indices]
    normal_conf = [records[i]["confidence"] for i in normal_indices]

    # Metrics on normal cases
    metrics_primary = evaluate_primary_intent(normal_true, normal_pred, labels=clf.classes_)
    calib_metrics = evaluate_calibration(normal_true, normal_pred, normal_conf)
    thresh_results = evaluate_threshold_abstention(normal_true, normal_pred, normal_conf)

    # Multi-intent evaluation across all 200 cases
    gold_intents = [c.get("intents", []) for c in cases]
    pred_intents = [r["intents"] for r in records]
    metrics_multi = evaluate_multi_intent(gold_intents, pred_intents, all_intents=clf.classes_)

    # Status evaluation across all 200 cases
    gold_status = [c.get("classification_status", "NORMAL") for c in cases]
    pred_status = [r["classification_status"] for r in records]
    metrics_status = evaluate_status(gold_status, pred_status)

    print("-" * 60)
    print(f"Primary Intent Accuracy (on Normal cases, n={len(normal_indices)}): {metrics_primary['accuracy']:.4f}")
    print(f"Primary Intent Macro F1: {metrics_primary['macro_f1']:.4f}")
    print(f"Primary Intent Weighted F1: {metrics_primary['weighted_f1']:.4f}")
    print(f"Multi-Intent Micro F1 (all 200 cases): {metrics_multi['micro_f1']:.4f}")
    print(f"Multi-Intent Exact Match: {metrics_multi['exact_set_match']:.4f}")
    print(f"Expected Calibration Error (ECE): {calib_metrics['expected_calibration_error']:.4f}")
    print("=" * 60)

    return {
        "model": "TFIDF_LogisticRegression",
        "primary_accuracy": round(metrics_primary["accuracy"], 4),
        "primary_macro_f1": round(metrics_primary["macro_f1"], 4),
        "primary_weighted_f1": round(metrics_primary["weighted_f1"], 4),
        "multi_intent_micro_f1": round(metrics_multi["micro_f1"], 4),
        "multi_intent_exact_match": round(metrics_multi["exact_set_match"], 4),
        "status_macro_f1": round(metrics_status["macro_f1"], 4),
        "state_macro_f1": 0.0,  # TF-IDF primary baseline does not predict state
        "per_intent": metrics_primary["per_intent"],
        "confusion_matrix": metrics_primary["confusion_matrix"],
        "labels": metrics_primary["labels"],
        "calibration": calib_metrics,
        "threshold_abstention": thresh_results,
        "records": records,
    }


if __name__ == "__main__":
    evaluate_tfidf()
