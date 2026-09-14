"""Deterministic classification graders for AmazonSupportAgent Golden V1 evaluation.

Implements evaluation for:
- Status (NORMAL, AMBIGUOUS, OUT_OF_SCOPE)
- Primary Intent (with strict null handling for AMBIGUOUS/OUT_OF_SCOPE)
- Multi-Intent (set-based parsing and micro/macro metrics)
- Areas (set-based parsing and micro/macro metrics)
- Operational States
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)


def parse_pipe_separated(val: Any) -> Set[str]:
    """Parse pipe-separated strings into a normalized set of uppercase tokens.

    Handles:
    - None / NaN / empty string -> empty set
    - Single token -> set with one token
    - "A|B|C" -> {"A", "B", "C"}
    - Iterables (lists, sets) -> set of normalized strings
    """
    if val is None:
        return set()
    if isinstance(val, (list, set, tuple)):
        return {str(item).strip() for item in val if item and str(item).strip()}
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ("none", "nan", "null", "[]"):
        return set()
    return {part.strip() for part in val_str.split("|") if part.strip()}


def normalize_primary_intent(val: Any) -> Optional[str]:
    """Normalize primary intent to a clean string or None."""
    if val is None:
        return None
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ("none", "nan", "null"):
        return None
    return val_str


def evaluate_status(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
    """Calculate Status metrics: Accuracy, Macro F1, Weighted F1, Confusion Matrix."""
    labels = sorted(list(set(y_true) | set(y_pred)))
    acc = float(accuracy_score(y_true, y_pred)) if y_true else 0.0
    macro_f1 = float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)) if y_true else 0.0
    weighted_f1 = float(f1_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0)) if y_true else 0.0
    cm = confusion_matrix(y_true, y_pred, labels=labels).tolist() if y_true else []

    return {
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "labels": labels,
        "confusion_matrix": cm,
        "total_cases": len(y_true),
    }


def evaluate_primary_intent(
    y_true: List[Optional[str]],
    y_pred: List[Optional[str]],
    status_true: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Calculate Primary Intent metrics with strict, correct null handling.

    For AMBIGUOUS and OUT_OF_SCOPE cases, the expected primary intent is None.
    If the agent predicts None (or status is AMBIGUOUS/OUT_OF_SCOPE), that counts as a match.
    We represent the null class explicitly as '<NO_INTENT>' for metric computation so that
    None is not silently converted into an arbitrary taxonomy class.
    """
    assert len(y_true) == len(y_pred), "y_true and y_pred must have equal length"
    n = len(y_true)
    if n == 0:
        return {"accuracy": 0.0, "macro_f1": 0.0, "weighted_f1": 0.0, "per_class": {}}

    NO_INTENT_TOKEN = "<NO_INTENT>"

    y_true_clean = []
    y_pred_clean = []

    for i in range(n):
        st = status_true[i] if status_true else None
        t = normalize_primary_intent(y_true[i])
        p = normalize_primary_intent(y_pred[i])

        # For AMBIGUOUS or OUT_OF_SCOPE, expected is NO_INTENT_TOKEN
        if st in ("AMBIGUOUS", "OUT_OF_SCOPE") or t is None:
            y_true_clean.append(NO_INTENT_TOKEN)
        else:
            y_true_clean.append(t)

        if p is None:
            y_pred_clean.append(NO_INTENT_TOKEN)
        else:
            y_pred_clean.append(p)

    labels = sorted(list(set(y_true_clean) | set(y_pred_clean)))
    acc = float(accuracy_score(y_true_clean, y_pred_clean))
    macro_f1 = float(f1_score(y_true_clean, y_pred_clean, labels=labels, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_true_clean, y_pred_clean, labels=labels, average="weighted", zero_division=0))

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true_clean, y_pred_clean, labels=labels, zero_division=0
    )

    per_class = {}
    for idx, label in enumerate(labels):
        per_class[label] = {
            "precision": round(float(precision[idx]), 4),
            "recall": round(float(recall[idx]), 4),
            "f1": round(float(f1[idx]), 4),
            "support": int(support[idx]),
        }

    return {
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "per_class": per_class,
        "labels": labels,
        "total_cases": n,
    }


def evaluate_set_based_labels(
    y_true_sets: List[Set[str]],
    y_pred_sets: List[Set[str]],
) -> Dict[str, Any]:
    """Calculate multi-label set-based metrics: micro precision/recall/F1, macro F1, exact match."""
    assert len(y_true_sets) == len(y_pred_sets), "Sets lists must have equal length"
    n = len(y_true_sets)
    if n == 0:
        return {
            "micro_precision": 0.0,
            "micro_recall": 0.0,
            "micro_f1": 0.0,
            "macro_f1": 0.0,
            "exact_set_match": 0.0,
            "total_cases": 0,
        }

    all_tokens = sorted(list(set.union(*y_true_sets, *y_pred_sets))) if (y_true_sets or y_pred_sets) else []
    if not all_tokens:
        return {
            "micro_precision": 1.0,
            "micro_recall": 1.0,
            "micro_f1": 1.0,
            "macro_f1": 1.0,
            "exact_set_match": 1.0,
            "total_cases": n,
        }

    token_to_idx = {tok: i for i, tok in enumerate(all_tokens)}
    k = len(all_tokens)
    y_true_bin = np.zeros((n, k), dtype=int)
    y_pred_bin = np.zeros((n, k), dtype=int)

    exact_matches = 0
    for i in range(n):
        true_s = y_true_sets[i]
        pred_s = y_pred_sets[i]
        if true_s == pred_s:
            exact_matches += 1

        for t in true_s:
            if t in token_to_idx:
                y_true_bin[i, token_to_idx[t]] = 1
        for p in pred_s:
            if p in token_to_idx:
                y_pred_bin[i, token_to_idx[p]] = 1

    p_micro, r_micro, f1_micro, _ = precision_recall_fscore_support(
        y_true_bin, y_pred_bin, average="micro", zero_division=0
    )
    macro_f1 = float(f1_score(y_true_bin, y_pred_bin, average="macro", zero_division=0))
    exact_match_rate = float(exact_matches / n)

    return {
        "micro_precision": round(float(p_micro), 4),
        "micro_recall": round(float(r_micro), 4),
        "micro_f1": round(float(f1_micro), 4),
        "macro_f1": round(macro_f1, 4),
        "exact_set_match": round(exact_match_rate, 4),
        "total_cases": n,
    }


def evaluate_state(y_true: List[str], y_pred: List[Any]) -> Dict[str, Any]:
    """Calculate conversation state metrics."""
    assert len(y_true) == len(y_pred), "y_true and y_pred must have equal length"
    n = len(y_true)
    if n == 0:
        return {"accuracy": 0.0, "macro_f1": 0.0, "weighted_f1": 0.0}

    # Normalize pred: could be a string or a list of strings
    clean_preds: List[str] = []
    for p in y_pred:
        if isinstance(p, list):
            clean_preds.append(str(p[0]).strip() if p else "INITIAL_INQUIRY")
        else:
            clean_preds.append(str(p).strip() if p else "INITIAL_INQUIRY")

    clean_trues = [str(t).strip() for t in y_true]
    labels = sorted(list(set(clean_trues) | set(clean_preds)))

    acc = float(accuracy_score(clean_trues, clean_preds))
    macro_f1 = float(f1_score(clean_trues, clean_preds, labels=labels, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(clean_trues, clean_preds, labels=labels, average="weighted", zero_division=0))

    return {
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "labels": labels,
        "total_cases": n,
    }


def grade_case_classification(gold: Dict[str, Any], agent: Dict[str, Any]) -> Dict[str, Any]:
    """Grade classification for a single case. Returns boolean match flags."""
    gold_status = str(gold.get("status", "NORMAL")).strip()
    agent_status = str(agent.get("status", "NORMAL")).strip()
    status_match = (gold_status == agent_status)

    gold_primary = normalize_primary_intent(gold.get("primary_intent"))
    agent_primary = normalize_primary_intent(agent.get("primary_intent"))

    if gold_status in ("AMBIGUOUS", "OUT_OF_SCOPE"):
        primary_intent_match = (agent_primary is None or agent_status in ("AMBIGUOUS", "OUT_OF_SCOPE"))
    else:
        primary_intent_match = (gold_primary == agent_primary)

    gold_intents = parse_pipe_separated(gold.get("intents"))
    agent_intents = parse_pipe_separated(agent.get("intents"))
    multi_intent_exact_match = (gold_intents == agent_intents)

    gold_areas = parse_pipe_separated(gold.get("areas"))
    agent_areas = parse_pipe_separated(agent.get("areas"))
    areas_exact_match = (gold_areas == agent_areas)

    gold_state = str(gold.get("state", "INITIAL_INQUIRY")).strip()
    agent_state_raw = agent.get("state") or agent.get("states", ["INITIAL_INQUIRY"])
    if isinstance(agent_state_raw, list):
        agent_state = str(agent_state_raw[0]).strip() if agent_state_raw else "INITIAL_INQUIRY"
    else:
        agent_state = str(agent_state_raw).strip()
    state_match = (gold_state == agent_state)

    return {
        "status_match": status_match,
        "primary_intent_match": primary_intent_match,
        "multi_intent_exact_match": multi_intent_exact_match,
        "areas_exact_match": areas_exact_match,
        "state_match": state_match,
    }
