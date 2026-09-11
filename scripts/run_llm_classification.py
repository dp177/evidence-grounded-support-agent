"""Run LLM intent classification on the locked Golden Evaluation Set v1.

Caches all responses in artifacts/llm_predictions/ to prevent redundant calls.
Uses ThreadPoolExecutor for fast, rate-limit resilient parallel evaluation.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import sys
import time

sys.path.insert(0, "src")

from support_agent.classification.llm_classifier import LLMIntentClassifier
from support_agent.evaluation.classification_metrics import evaluate_classification_records

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    golden_path = Path("data/golden/golden_set.jsonl")
    if not golden_path.exists():
        logger.error(f"Golden set not found at {golden_path}")
        sys.exit(1)

    with open(golden_path, "r", encoding="utf-8") as f:
        golden_cases = [json.loads(line) for line in f if line.strip()]

    logger.info(f"Loaded {len(golden_cases)} golden evaluation cases.")

    classifier = LLMIntentClassifier(cache_dir="artifacts/llm_predictions")
    
    # Check cache status
    cached_count = sum(
        1 for c in golden_cases
        if (Path("artifacts/llm_predictions") / f"{c['gold_id']}.json").exists()
    )
    logger.info(f"Existing cached predictions: {cached_count}/{len(golden_cases)}")

    t0 = time.time()
    predictions = classifier.classify_batch(golden_cases, max_workers=2, use_cache=True)
    elapsed = time.time() - t0
    logger.info(f"Classification completed in {elapsed:.1f}s.")

    # Evaluate against golden truth
    eval_results = evaluate_classification_records(golden_cases, predictions)
    primary_metrics = eval_results["primary_intent"]
    multi_metrics = eval_results["multi_intent"]
    status_metrics = eval_results["status"]
    state_metrics = eval_results["state"]
    calibration_metrics = eval_results["calibration"]

    logger.info("=== OpenRouter LLM Evaluation Results ===")
    logger.info(f"Primary Intent Accuracy (Normal cases): {primary_metrics['accuracy']:.4f}")
    logger.info(f"Primary Intent Macro F1: {primary_metrics['macro_f1']:.4f}")
    logger.info(f"Primary Intent Weighted F1: {primary_metrics['weighted_f1']:.4f}")
    logger.info(f"Multi-Intent Micro F1: {multi_metrics['micro_f1']:.4f}")
    logger.info(f"Multi-Intent Exact Match: {multi_metrics['exact_set_match']:.4f}")
    logger.info(f"Status Macro F1: {status_metrics['macro_f1']:.4f}")
    logger.info(f"State Macro F1: {state_metrics['macro_f1']:.4f}")
    logger.info(f"Expected Calibration Error (ECE): {calibration_metrics['expected_calibration_error']:.4f}")

    # Save summary
    out_file = Path("results/llm_classification_summary.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "model": classifier.client.model if hasattr(classifier.client, "model") else "openrouter",
        "num_cases": len(golden_cases),
        "primary_intent": primary_metrics,
        "multi_intent": multi_metrics,
        "status": status_metrics,
        "state": state_metrics,
        "calibration": calibration_metrics,
        "threshold_abstention": eval_results["abstention"],
    }
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Saved summary to {out_file}")


if __name__ == "__main__":
    main()
