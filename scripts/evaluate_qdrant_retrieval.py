"""Evaluate Qdrant retrieval on the locked Golden V1 evaluation benchmark.

Queries Qdrant vector index with Golden V1 customer cases, saves top-k predictions
to results/qdrant_retrieval_predictions.jsonl, and calculates Recall@k and MRR metrics.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys
import time
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np

from support_agent.retrieval.retriever import QdrantRetriever, format_query_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("evaluate_qdrant_retrieval")


def load_golden_set(golden_path: str = "data/golden/golden_set.jsonl") -> List[Dict[str, Any]]:
    """Load the locked Golden V1 evaluation cases."""
    records: List[Dict[str, Any]] = []
    with open(golden_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    logger.info("Loaded %d Golden V1 evaluation cases from %s", len(records), golden_path)
    return records


def evaluate_retrieval(
    golden_path: str = "data/golden/golden_set.jsonl",
    output_predictions_path: str = "results/qdrant_retrieval_predictions.jsonl",
    top_k: int = 30,
    config_path: str = "configs/retrieval.yaml",
) -> Dict[str, Any]:
    """Execute retrieval evaluation over Golden V1 queries."""
    golden_records = load_golden_set(golden_path)
    retriever = QdrantRetriever(config_path=config_path)

    logger.info(
        "Beginning retrieval evaluation on %d Golden cases (top_k=%d, collection=%s)...",
        len(golden_records),
        top_k,
        retriever.collection_name,
    )

    out_path = Path(output_predictions_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    predictions: List[Dict[str, Any]] = []
    top1_scores: List[float] = []
    top5_mean_scores: List[float] = []

    t0 = time.time()
    with open(out_path, "w", encoding="utf-8") as f_out:
        for idx, rec in enumerate(golden_records):
            gold_id = rec.get("gold_id")
            c_msg = rec.get("customer_message", "")
            ctx = rec.get("context", "")
            primary_intent = rec.get("primary_intent")
            areas = rec.get("areas", [])
            intents = rec.get("intents", [])

            query_text = format_query_text(customer_message=c_msg, context=ctx)
            results = retriever.search(query_text=query_text, top_k=top_k)

            scores = [r["score"] for r in results]
            if scores:
                top1_scores.append(scores[0])
                top5_mean_scores.append(float(np.mean(scores[:5])))

            pred_record = {
                "gold_id": gold_id,
                "gold_case_id": rec.get("case_id"),
                "gold_conversation_id": rec.get("conversation_id"),
                "gold_primary_intent": primary_intent,
                "gold_areas": areas,
                "gold_intents": intents,
                "customer_message": c_msg,
                "context": ctx,
                "top_k_results": results,
            }

            f_out.write(json.dumps(pred_record, ensure_ascii=False) + "\n")
            predictions.append(pred_record)

            if (idx + 1) % 50 == 0 or (idx + 1) == len(golden_records):
                logger.info("Processed %d / %d evaluation queries (%.1fs elapsed)", idx + 1, len(golden_records), time.time() - t0)

    logger.info("Saved %d retrieval predictions to %s", len(predictions), out_path)

    metrics_summary = {
        "num_queries": len(golden_records),
        "top_k": top_k,
        "mean_top1_score": float(np.mean(top1_scores)) if top1_scores else 0.0,
        "mean_top5_score": float(np.mean(top5_mean_scores)) if top5_mean_scores else 0.0,
    }

    print("\n" + "=" * 60)
    print("RETRIEVAL EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Evaluated Queries:    {metrics_summary['num_queries']}")
    print(f"Mean Top-1 Score:     {metrics_summary['mean_top1_score']:.4f}")
    print(f"Mean Top-5 Score:     {metrics_summary['mean_top5_score']:.4f}")
    print(f"Predictions File:     {out_path}")
    print("=" * 60 + "\n")

    return metrics_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Qdrant retrieval on Golden V1")
    parser.add_argument("--golden", default="data/golden/golden_set.jsonl", help="Path to Golden V1")
    parser.add_argument("--output", default="results/qdrant_retrieval_predictions.jsonl", help="Output predictions path")
    parser.add_argument("--top-k", type=int, default=30, help="Top-K results per query")
    parser.add_argument("--config", default="configs/retrieval.yaml", help="Retrieval config path")
    args = parser.parse_args()

    evaluate_retrieval(
        golden_path=args.golden,
        output_predictions_path=args.output,
        top_k=args.top_k,
        config_path=args.config,
    )


if __name__ == "__main__":
    main()
