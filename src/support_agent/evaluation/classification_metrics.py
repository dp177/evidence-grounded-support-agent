"""Classification evaluation metrics for AmazonHelp customer support agent.

Calculates:
- Primary intent metrics (accuracy, macro/weighted F1, per-intent precision/recall/F1, confusion matrix)
- Multi-intent metrics (micro F1, macro F1, exact set match)
- Status metrics (accuracy, macro F1)
- State metrics (accuracy, macro F1)
- Confidence calibration & threshold abstention analysis
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)


def evaluate_primary_intent(
    y_true: List[str],
    y_pred: List[str],
    labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Calculate comprehensive primary intent metrics."""
    if not labels:
        labels = sorted(list(set(y_true) | set(y_pred)))

    acc = float(accuracy_score(y_true, y_pred))
    macro_f1 = float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0))

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )

    per_intent = {}
    for i, label in enumerate(labels):
        per_intent[label] = {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i]),
        }

    cm = confusion_matrix(y_true, y_pred, labels=labels)

    return {
        "accuracy": acc,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "labels": labels,
        "per_intent": per_intent,
        "confusion_matrix": cm.tolist(),
    }


def evaluate_multi_intent(
    y_true_sets: List[List[str] | Set[str]],
    y_pred_sets: List[List[str] | Set[str]],
    all_intents: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Calculate multi-label intent metrics: micro F1, macro F1, exact set match."""
    if not all_intents:
        s = set()
        for item in y_true_sets + y_pred_sets:
            s.update(item)
        all_intents = sorted(list(s))

    n = len(y_true_sets)
    if n == 0:
        return {"micro_f1": 0.0, "macro_f1": 0.0, "exact_set_match": 0.0, "total_cases": 0}

    # Binary indicator matrices
    intent_to_idx = {intent: i for i, intent in enumerate(all_intents)}
    k = len(all_intents)
    y_true_bin = np.zeros((n, k), dtype=int)
    y_pred_bin = np.zeros((n, k), dtype=int)

    exact_matches = 0
    for i in range(n):
        true_set = set(y_true_sets[i])
        pred_set = set(y_pred_sets[i])
        if true_set == pred_set:
            exact_matches += 1

        for it in true_set:
            if it in intent_to_idx:
                y_true_bin[i, intent_to_idx[it]] = 1
        for it in pred_set:
            if it in intent_to_idx:
                y_pred_bin[i, intent_to_idx[it]] = 1

    micro_f1 = float(f1_score(y_true_bin, y_pred_bin, average="micro", zero_division=0))
    macro_f1 = float(f1_score(y_true_bin, y_pred_bin, average="macro", zero_division=0))
    exact_match = float(exact_matches / n)

    return {
        "micro_f1": micro_f1,
        "macro_f1": macro_f1,
        "exact_set_match": exact_match,
        "total_cases": n,
    }


def evaluate_status(
    y_true: List[str],
    y_pred: List[str],
    labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Calculate classification status metrics (NORMAL, AMBIGUOUS, OUT_OF_SCOPE)."""
    if not labels:
        labels = ["NORMAL", "AMBIGUOUS", "OUT_OF_SCOPE"]

    acc = float(accuracy_score(y_true, y_pred))
    macro_f1 = float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0))
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    return {
        "accuracy": acc,
        "macro_f1": macro_f1,
        "labels": labels,
        "confusion_matrix": cm.tolist(),
    }


def evaluate_state(
    y_true: List[str | List[str]],
    y_pred: List[str | List[str]],
    allowed_states: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Calculate conversation state metrics."""
    # Normalize strings (pick first if list)
    norm_true = [s[0] if isinstance(s, list) and s else str(s) for s in y_true]
    norm_pred = [s[0] if isinstance(s, list) and s else str(s) for s in y_pred]

    if not allowed_states:
        allowed_states = sorted(list(set(norm_true) | set(norm_pred)))

    acc = float(accuracy_score(norm_true, norm_pred))
    macro_f1 = float(f1_score(norm_true, norm_pred, labels=allowed_states, average="macro", zero_division=0))

    return {
        "accuracy": acc,
        "macro_f1": macro_f1,
        "allowed_states": allowed_states,
    }


def evaluate_calibration(
    y_true: List[str],
    y_pred: List[str],
    confidences: List[float],
    n_bins: int = 10,
) -> Dict[str, Any]:
    """Evaluate model-reported confidence calibration (histogram, bucket accuracy, ECE)."""
    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    correctness = [1 if t == p else 0 for t, p in zip(y_true, y_pred)]

    total_samples = len(confidences)
    if total_samples == 0:
        return {"ece": 0.0, "buckets": []}

    buckets = []
    ece = 0.0

    for i in range(n_bins):
        low = bin_boundaries[i]
        high = bin_boundaries[i + 1]

        if i == n_bins - 1:
            indices = [idx for idx, c in enumerate(confidences) if low <= c <= high]
        else:
            indices = [idx for idx, c in enumerate(confidences) if low <= c < high]

        count = len(indices)
        if count > 0:
            avg_conf = float(np.mean([confidences[idx] for idx in indices]))
            avg_acc = float(np.mean([correctness[idx] for idx in indices]))
            ece += (count / total_samples) * abs(avg_acc - avg_conf)
        else:
            avg_conf = float((low + high) / 2.0)
            avg_acc = 0.0

        buckets.append({
            "bin_range": f"{low:.1f}-{high:.1f}",
            "count": count,
            "mean_confidence": round(avg_conf, 4),
            "accuracy": round(avg_acc, 4),
        })

    return {
        "expected_calibration_error": round(float(ece), 4),
        "total_samples": total_samples,
        "buckets": buckets,
    }


def evaluate_threshold_abstention(
    y_true: List[str],
    y_pred: List[str],
    confidences: List[float],
    thresholds: List[float] = [0.50, 0.60, 0.70, 0.80, 0.90],
) -> List[Dict[str, Any]]:
    """Evaluate abstention behavior across confidence thresholds."""
    results = []
    total = len(y_true)

    for thresh in thresholds:
        accepted_indices = [i for i, c in enumerate(confidences) if c >= thresh]
        acc_count = len(accepted_indices)
        coverage = acc_count / total if total > 0 else 0.0
        rejected_fraction = 1.0 - coverage

        if acc_count > 0:
            accepted_true = [y_true[i] for i in accepted_indices]
            accepted_pred = [y_pred[i] for i in accepted_indices]
            accuracy = float(accuracy_score(accepted_true, accepted_pred))
        else:
            accuracy = 0.0

        results.append({
            "threshold": thresh,
            "accepted_count": acc_count,
            "coverage": round(coverage, 4),
            "rejected_fraction": round(rejected_fraction, 4),
            "accuracy_on_accepted": round(accuracy, 4),
        })

    return results


def evaluate_classification_records(
    gold_records: List[Dict[str, Any]],
    pred_records: List[Dict[str, Any]],
    allowed_intents: Optional[List[str]] = None,
    allowed_states: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Calculate all benchmark metrics comparing gold record dicts against model prediction dicts."""
    if len(gold_records) != len(pred_records):
        raise ValueError(f"Length mismatch: {len(gold_records)} gold vs {len(pred_records)} predictions")

    # 1. Primary intent on NORMAL cases
    normal_indices = [
        i for i, c in enumerate(gold_records)
        if c.get("classification_status") == "NORMAL" and c.get("primary_intent") is not None
    ]
    if normal_indices:
        normal_true = [str(gold_records[i]["primary_intent"]) for i in normal_indices]
        normal_pred = [str(pred_records[i].get("primary_intent") or "OUT_OF_SCOPE_OR_AMBIGUOUS") for i in normal_indices]
        normal_conf = [float(pred_records[i].get("confidence", 0.5)) for i in normal_indices]
        primary_metrics = evaluate_primary_intent(normal_true, normal_pred, labels=allowed_intents)
        calibration_metrics = evaluate_calibration(normal_true, normal_pred, normal_conf)
        abstention_metrics = evaluate_threshold_abstention(normal_true, normal_pred, normal_conf)
    else:
        primary_metrics = {"accuracy": 0.0, "macro_f1": 0.0, "weighted_f1": 0.0, "labels": [], "per_intent": {}, "confusion_matrix": []}
        calibration_metrics = {"expected_calibration_error": 0.0, "total_samples": 0, "buckets": []}
        abstention_metrics = []

    # 2. Multi-intent on all cases
    gold_intents = [c.get("intents", []) for c in gold_records]
    pred_intents = [p.get("intents", []) for p in pred_records]
    multi_metrics = evaluate_multi_intent(gold_intents, pred_intents, all_intents=allowed_intents)

    # 3. Status on all cases
    gold_status = [str(c.get("classification_status", "NORMAL")) for c in gold_records]
    pred_status = [str(p.get("classification_status", "NORMAL")) for p in pred_records]
    status_metrics = evaluate_status(gold_status, pred_status)

    # 4. State on all cases
    gold_states = [c.get("states", ["INITIAL_INQUIRY"]) for c in gold_records]
    pred_states = [p.get("states", ["INITIAL_INQUIRY"]) for p in pred_records]
    state_metrics = evaluate_state(gold_states, pred_states, allowed_states=allowed_states)

    return {
        "num_cases": len(gold_records),
        "num_normal_cases": len(normal_indices),
        "primary_intent": primary_metrics,
        "multi_intent": multi_metrics,
        "status": status_metrics,
        "state": state_metrics,
        "calibration": calibration_metrics,
        "abstention": abstention_metrics,
    }

