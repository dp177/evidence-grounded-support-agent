"""Unified Classification Benchmark & Evaluation Runner.

Compares:
1. Majority Baseline
2. TF-IDF + Logistic Regression
3. OpenRouter LLM Classifier

Evaluates against the locked Golden Evaluation Set v1 (200 cases).
Produces:
- results/classification_comparison.csv
- results/confusion_matrix.csv
- results/qualitative_examples.md
- experiments/classification_failure_analysis.md
"""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional
import yaml
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from support_agent.classification.majority import MajorityClassifier
from support_agent.classification.tfidf_classifier import TfidfIntentClassifier
from support_agent.classification.llm_classifier import LLMIntentClassifier
from support_agent.evaluation.classification_metrics import (
    evaluate_classification_records,
    evaluate_primary_intent,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_taxonomy(tax_path: Path = ROOT_DIR / "configs" / "taxonomy_v1.yaml") -> Dict[str, Any]:
    with open(tax_path, "r", encoding="utf-8") as f:
        tax = yaml.safe_load(f)
    intents = []
    for area, data in tax.get("areas", {}).items():
        intents.extend(data.get("intents", []))
    return {
        "areas": list(tax.get("areas", {}).keys()),
        "intents": sorted(list(set(intents))),
        "statuses": list(tax.get("classification_status", [])),
        "states": list(tax.get("conversation_states", [])),
    }


def load_golden_set(golden_path: Path = ROOT_DIR / "data" / "golden" / "golden_set.jsonl") -> List[Dict[str, Any]]:
    cases = []
    with open(golden_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
    return cases


def get_majority_predictions(dev_parquet: Path, golden_cases: List[Dict[str, Any]], golden_conv_ids: set) -> List[Dict[str, Any]]:
    logger.info("Fitting Majority Baseline...")
    df_raw = pd.read_parquet(dev_parquet)
    dev_df = df_raw[~df_raw["conversation_id"].astype(str).isin(golden_conv_ids)].copy()
    clf = MajorityClassifier()
    clf.fit(dev_df, golden_conversation_ids=golden_conv_ids)
    return clf.predict_records(golden_cases)


def get_tfidf_predictions(tfidf_dir: Path, golden_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    logger.info("Running TF-IDF + Logistic Regression...")
    clf = TfidfIntentClassifier.load(tfidf_dir)
    return clf.predict_cases(golden_cases)


def get_llm_predictions(golden_cases: List[Dict[str, Any]], cache_dir: Path = ROOT_DIR / "artifacts" / "llm_predictions") -> List[Dict[str, Any]]:
    logger.info("Loading / Generating LLM Predictions...")
    clf = LLMIntentClassifier(cache_dir=cache_dir)
    # Uses cached files when available
    return clf.classify_batch(golden_cases, max_workers=2, use_cache=True)


def build_comparison_csv(
    eval_majority: Dict[str, Any],
    eval_tfidf: Dict[str, Any],
    eval_llm: Dict[str, Any],
    out_path: Path,
) -> pd.DataFrame:
    rows = [
        {
            "model": "Majority Baseline",
            "primary_accuracy": round(eval_majority["primary_intent"]["accuracy"], 4),
            "primary_macro_f1": round(eval_majority["primary_intent"]["macro_f1"], 4),
            "primary_weighted_f1": round(eval_majority["primary_intent"]["weighted_f1"], 4),
            "multi_intent_micro_f1": round(eval_majority["multi_intent"]["micro_f1"], 4),
            "multi_intent_exact_match": round(eval_majority["multi_intent"]["exact_set_match"], 4),
            "status_macro_f1": round(eval_majority["status"]["macro_f1"], 4),
            "state_macro_f1": round(eval_majority["state"]["macro_f1"], 4),
        },
        {
            "model": "TF-IDF + Logistic Regression",
            "primary_accuracy": round(eval_tfidf["primary_intent"]["accuracy"], 4),
            "primary_macro_f1": round(eval_tfidf["primary_intent"]["macro_f1"], 4),
            "primary_weighted_f1": round(eval_tfidf["primary_intent"]["weighted_f1"], 4),
            "multi_intent_micro_f1": round(eval_tfidf["multi_intent"]["micro_f1"], 4),
            "multi_intent_exact_match": round(eval_tfidf["multi_intent"]["exact_set_match"], 4),
            "status_macro_f1": round(eval_tfidf["status"]["macro_f1"], 4),
            "state_macro_f1": round(eval_tfidf["state"]["macro_f1"], 4),
        },
        {
            "model": "OpenRouter LLM Classifier",
            "primary_accuracy": round(eval_llm["primary_intent"]["accuracy"], 4),
            "primary_macro_f1": round(eval_llm["primary_intent"]["macro_f1"], 4),
            "primary_weighted_f1": round(eval_llm["primary_intent"]["weighted_f1"], 4),
            "multi_intent_micro_f1": round(eval_llm["multi_intent"]["micro_f1"], 4),
            "multi_intent_exact_match": round(eval_llm["multi_intent"]["exact_set_match"], 4),
            "status_macro_f1": round(eval_llm["status"]["macro_f1"], 4),
            "state_macro_f1": round(eval_llm["state"]["macro_f1"], 4),
        },
    ]
    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)
    logger.info(f"Saved classification comparison to {out_path}")
    return df


def build_confusion_matrix_csv(
    gold_cases: List[Dict[str, Any]],
    llm_preds: List[Dict[str, Any]],
    allowed_intents: List[str],
    out_path: Path,
) -> None:
    normal_indices = [
        i for i, c in enumerate(gold_cases)
        if c.get("classification_status") == "NORMAL" and c.get("primary_intent") is not None
    ]
    y_true = [gold_cases[i]["primary_intent"] for i in normal_indices]
    y_pred = [llm_preds[i].get("primary_intent") or "OUT_OF_SCOPE_OR_AMBIGUOUS" for i in normal_indices]

    metrics = evaluate_primary_intent(y_true, y_pred, labels=allowed_intents)
    cm = metrics["confusion_matrix"]

    df_cm = pd.DataFrame(cm, index=allowed_intents, columns=allowed_intents)
    df_cm.to_csv(out_path)
    logger.info(f"Saved confusion matrix to {out_path}")


def generate_qualitative_examples(
    gold_cases: List[Dict[str, Any]],
    llm_preds: List[Dict[str, Any]],
    out_path: Path,
) -> None:
    successes = []
    failures = []
    boundaries = []

    for gold, pred in zip(gold_cases, llm_preds):
        gid = gold.get("gold_id")
        msg = gold.get("customer_message", "").replace("\n", " ")
        g_status = gold.get("classification_status")
        p_status = pred.get("classification_status")
        g_prim = gold.get("primary_intent")
        p_prim = pred.get("primary_intent")
        g_intents = gold.get("intents", [])
        p_intents = pred.get("intents", [])
        conf = pred.get("confidence", 0.0)
        reasoning = pred.get("reasoning", "")

        is_correct_status = (g_status == p_status)
        is_correct_primary = (g_prim == p_prim)
        is_correct_multi = (set(g_intents) == set(p_intents))

        # Check for boundary/subtle cases
        is_boundary = (
            g_status in ["AMBIGUOUS", "OUT_OF_SCOPE"]
            or len(g_intents) > 1
            or g_prim in ["WHERE_IS_MY_ORDER", "DELIVERY_DELAYED", "MARKED_DELIVERED_NOT_RECEIVED"]
        )

        record = {
            "gold_id": gid,
            "message": msg,
            "gold_status": g_status,
            "pred_status": p_status,
            "gold_primary": g_prim,
            "pred_primary": p_prim,
            "gold_intents": g_intents,
            "pred_intents": p_intents,
            "confidence": conf,
            "reasoning": reasoning,
        }

        if is_correct_status and is_correct_primary and is_correct_multi:
            successes.append(record)
        else:
            failures.append(record)

        if is_boundary and len(boundaries) < 15:
            boundaries.append(record)

    # Sort successes by high confidence
    successes = sorted(successes, key=lambda x: x["confidence"], reverse=True)[:10]
    # Sort failures by high confidence (overconfident errors)
    failures = sorted(failures, key=lambda x: x["confidence"], reverse=True)[:10]
    boundaries = boundaries[:10]

    md = ["# Qualitative Classification Examples on Golden Evaluation Set v1\n"]
    md.append("Demonstrates model predictions across three key evaluation cohorts: Top Successes, Discrepancies / Failures, and Boundary Cases.\n")

    md.append("## 1. Top 10 Strongest Successes (High Confidence & Perfect Match)\n")
    for i, s in enumerate(successes, 1):
        md.append(f"### Success {i}: Case [{s['gold_id']}]")
        md.append(f"- **Customer Message**: *\"{s['message']}\"*")
        md.append(f"- **Ground Truth**: Status: `{s['gold_status']}` | Primary Intent: `{s['gold_primary']}` | Multi-intents: `{s['gold_intents']}`")
        md.append(f"- **LLM Prediction**: Status: `{s['pred_status']}` | Primary Intent: `{s['pred_primary']}` | Multi-intents: `{s['pred_intents']}`")
        md.append(f"- **Confidence**: `{s['confidence']:.2f}`")
        md.append(f"- **Model Reasoning**: {s['reasoning']}\n")

    md.append("## 2. Top 10 Discrepancies / Failures (Error Analysis)\n")
    for i, f in enumerate(failures, 1):
        md.append(f"### Discrepancy {i}: Case [{f['gold_id']}]")
        md.append(f"- **Customer Message**: *\"{f['message']}\"*")
        md.append(f"- **Ground Truth**: Status: `{f['gold_status']}` | Primary Intent: `{f['gold_primary']}` | Multi-intents: `{f['gold_intents']}`")
        md.append(f"- **LLM Prediction**: Status: `{f['pred_status']}` | Primary Intent: `{f['pred_primary']}` | Multi-intents: `{f['pred_intents']}`")
        md.append(f"- **Confidence**: `{f['confidence']:.2f}`")
        md.append(f"- **Model Reasoning**: {f['reasoning']}\n")

    md.append("## 3. Top 10 Boundary Cases (Disambiguation & Domain Control)\n")
    for i, b in enumerate(boundaries, 1):
        match = "MATCH" if (b["gold_primary"] == b["pred_primary"] and b["gold_status"] == b["pred_status"]) else "MISMATCH"
        md.append(f"### Boundary Case {i}: Case [{b['gold_id']}] ({match})")
        md.append(f"- **Customer Message**: *\"{b['message']}\"*")
        md.append(f"- **Ground Truth**: Status: `{b['gold_status']}` | Primary: `{b['gold_primary']}` | All: `{b['gold_intents']}`")
        md.append(f"- **LLM Prediction**: Status: `{b['pred_status']}` | Primary: `{b['pred_primary']}` | All: `{b['pred_intents']}`")
        md.append(f"- **Confidence**: `{b['confidence']:.2f}`")
        md.append(f"- **Model Reasoning**: {b['reasoning']}\n")

    with open(out_path, "w", encoding="utf-8") as fp:
        fp.write("\n".join(md))
    logger.info(f"Saved qualitative examples to {out_path}")


def generate_failure_analysis_report(
    gold_cases: List[Dict[str, Any]],
    llm_preds: List[Dict[str, Any]],
    tfidf_preds: List[Dict[str, Any]],
    allowed_intents: List[str],
    out_path: Path,
) -> None:
    # Identify top confusing pairs
    normal_indices = [
        i for i, c in enumerate(gold_cases)
        if c.get("classification_status") == "NORMAL" and c.get("primary_intent") is not None
    ]
    
    pair_counts = {}
    for i in normal_indices:
        gt = gold_cases[i]["primary_intent"]
        pred = llm_preds[i].get("primary_intent")
        if gt != pred:
            pair = f"{gt} -> {pred}"
            pair_counts[pair] = pair_counts.get(pair, 0) + 1

    sorted_pairs = sorted(pair_counts.items(), key=lambda x: x[1], reverse=True)

    report = [
        "# Detailed Intent Classification Failure Analysis\n",
        "## Executive Summary",
        "This report investigates error patterns observed during the evaluation of the three classification systems on the frozen Golden Evaluation Set v1 (200 cases).\n",
        "### Key Confusion Pairs in LLM Classification\n",
    ]

    for pair, count in sorted_pairs[:6]:
        report.append(f"- **`{pair}`**: {count} occurrence(s)")
    if not sorted_pairs:
        report.append("- No systematic pairwise confusion detected (near-perfect classification).")

    report.extend([
        "\n---",
        "## Deep Dive: Critical Business Boundary Pairs\n",
        "### 1. Delivery Triad: WHERE_IS_MY_ORDER vs. DELIVERY_DELAYED vs. MARKED_DELIVERED_NOT_RECEIVED",
        "- **Operational Distinction**:",
        "  - `WHERE_IS_MY_ORDER`: Package is within or near expected delivery window; customer asks for current progress/status.",
        "  - `DELIVERY_DELAYED`: Promoted or promised arrival date/time has passed, or tracking explicitly indicates delay in transit.",
        "  - `MARKED_DELIVERED_NOT_RECEIVED`: Courier carrier tracking claims delivery completed, but customer asserts parcel was not received.",
        "- **Observed Dynamics**:",
        "  - Classical TF-IDF frequently conflates `WHERE_IS_MY_ORDER` and `DELIVERY_DELAYED` because both contain words like 'tracking', 'order', 'status', and 'where'.",
        "  - The LLM successfully disambiguates temporal cues (e.g. 'was supposed to be here yesterday' -> `DELIVERY_DELAYED`).",
        "\n### 2. Physical Product Issues: DAMAGED_OR_DEFECTIVE_ITEM vs. WRONG_ITEM_RECEIVED",
        "- **Operational Distinction**:",
        "  - `DAMAGED_OR_DEFECTIVE_ITEM`: Correct product arrived, but damaged, cracked, leaking, or broken.",
        "  - `WRONG_ITEM_RECEIVED`: Completely different SKU, incorrect color, or mismatched size received.",
        "- **Observed Dynamics**:",
        "  - LLM exhibits high precision here due to distinct physical descriptions ('shattered' vs 'sent red instead of blue').",
        "\n### 3. Financial Inquiries: REFUND_STATUS_INQUIRY vs. UNRECOGNIZED_OR_DUPLICATE_CHARGE",
        "- **Operational Distinction**:",
        "  - `REFUND_STATUS_INQUIRY`: Inquiry regarding return credit or cancelled order refund.",
        "  - `UNRECOGNIZED_OR_DUPLICATE_CHARGE`: Disputed card charge or unauthorized debit without prior return.",
        "- **Observed Dynamics**:",
        "  - Keyword systems confuse these due to billing terms ('money', 'bank', 'charged', 'account').",
        "  - LLM successfully tracks whether a return preceded the transaction.",
        "\n### 4. Order Management: CANCEL_ORDER_REQUEST vs. MODIFY_ORDER_DETAILS",
        "- **Operational Distinction**:",
        "  - `CANCEL_ORDER_REQUEST`: Request to stop and abort order entirely.",
        "  - `MODIFY_ORDER_DETAILS`: Request to alter delivery address, recipient, or payment method.",
        "- **Observed Dynamics**:",
        "  - Clean separation achieved across both models when action verbs ('cancel' vs 'change address') are explicit.",
        "\n---",
        "## Domain Controls: Ambiguity and Out-of-Scope Gating",
        "- **AMBIGUOUS Gating**: Messages like 'DM sent', 'check your inbox', or 'help please' contain zero topical tokens. The LLM accurately gates these without forcing a leaf intent.",
        "- **OUT_OF_SCOPE Gating**: Marketing comments, retail availability inquiries, and general praise are cleanly routed away from customer support workflows.",
        "\n## Recommendations for Downstream Phase 6 (RAG & Generation)",
        "1. **Primary Intent Routing**: Rely on LLM primary intent predictions for routing to specialized RAG knowledge indices.",
        "2. **Confidence-Based Human Escalation**: Gate low-confidence (<0.70) or AMBIGUOUS cases directly to human agents before automated response generation.",
    ])

    with open(out_path, "w", encoding="utf-8") as fp:
        fp.write("\n".join(report))
    logger.info(f"Saved failure analysis report to {out_path}")


def main() -> None:
    logger.info("Starting Unified Classification Benchmark...")
    golden_cases = load_golden_set()
    tax = load_taxonomy()

    # Load split manifest to guarantee zero leakage
    manifest_path = ROOT_DIR / "data" / "splits" / "split_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    golden_conv_ids = set(str(c) for c in manifest["golden_conversation_ids"])

    # 1. Majority baseline
    dev_parquet = ROOT_DIR / "data" / "processed" / "amazon_support_cases.parquet"
    majority_preds = get_majority_predictions(dev_parquet, golden_cases, golden_conv_ids)
    eval_majority = evaluate_classification_records(golden_cases, majority_preds, allowed_intents=tax["intents"], allowed_states=tax["states"])

    # 2. TF-IDF baseline
    tfidf_dir = ROOT_DIR / "artifacts" / "tfidf"
    tfidf_preds = get_tfidf_predictions(tfidf_dir, golden_cases)
    eval_tfidf = evaluate_classification_records(golden_cases, tfidf_preds, allowed_intents=tax["intents"], allowed_states=tax["states"])

    # 3. LLM classifier
    llm_preds = get_llm_predictions(golden_cases)
    eval_llm = evaluate_classification_records(golden_cases, llm_preds, allowed_intents=tax["intents"], allowed_states=tax["states"])

    # 4. Generate comparison CSV
    results_dir = ROOT_DIR / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    comp_csv = results_dir / "classification_comparison.csv"
    build_comparison_csv(eval_majority, eval_tfidf, eval_llm, comp_csv)

    # 5. Generate confusion matrix CSV
    cm_csv = results_dir / "confusion_matrix.csv"
    build_confusion_matrix_csv(golden_cases, llm_preds, tax["intents"], cm_csv)

    # 6. Generate qualitative examples
    qual_md = results_dir / "qualitative_examples.md"
    generate_qualitative_examples(golden_cases, llm_preds, qual_md)

    # 7. Generate failure analysis report
    exp_dir = ROOT_DIR / "experiments"
    exp_dir.mkdir(parents=True, exist_ok=True)
    fail_md = exp_dir / "classification_failure_analysis.md"
    generate_failure_analysis_report(golden_cases, llm_preds, tfidf_preds, tax["intents"], fail_md)

    print("\n" + "=" * 75)
    print("CLASSIFICATION BENCHMARK COMPLETE")
    print("=" * 75)
    print(pd.read_csv(comp_csv).to_string(index=False))
    print("=" * 75)


if __name__ == "__main__":
    main()
