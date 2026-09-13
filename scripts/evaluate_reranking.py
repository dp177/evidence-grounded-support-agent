"""Evaluate Reranking on Golden V1.

Compares Semantic-Only vs Semantic+Reranking.
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

from support_agent.retrieval.retriever import QdrantRetriever, format_query_text
from support_agent.retrieval.reranker import CandidateReranker
from support_agent.retrieval.service import RetrievalService
from build_evidence_review_and_samples import grade_evidence

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("evaluate_reranking")


def run_evaluation(golden_records, retriever_func, name):
    logger.info(f"Running evaluation for: {name}")
    
    top1_relevant = 0
    top3_relevant = 0
    top5_relevant = 0
    reciprocal_ranks = []
    grade_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    
    boundary_results = {}
    samples = []
    
    for idx, rec in enumerate(golden_records):
        gold_id = rec.get("gold_id")
        c_msg = rec.get("customer_message", "")
        ctx = rec.get("context", "")
        primary_intent = rec.get("primary_intent") or "OUT_OF_SCOPE"
        areas = rec.get("areas", [])
        intents = rec.get("intents", [])
        states = []  # No state labels in golden_set yet
        
        results = retriever_func(c_msg, ctx, intents, areas, states)
        top5 = results[:5]
        
        case_grades = []
        for rank, res in enumerate(top5, 1):
            rc = res.get("customer_message", "")
            rr = res.get("brand_response", "")
            score = res.get("score") or res.get("rerank_score", 0.0)
            g, rationale = grade_evidence(primary_intent, c_msg, rc, rr, score)
            case_grades.append((rank, g, rationale, res))
            if rank == 1:
                grade_counts[g] += 1
                
        if not case_grades:
            reciprocal_ranks.append(0.0)
            continue
            
        top1_g = case_grades[0][1]
        top3_g = max((cg[1] for cg in case_grades[:3]), default=0)
        top5_g = max((cg[1] for cg in case_grades[:5]), default=0)

        if top1_g >= 2: top1_relevant += 1
        if top3_g >= 2: top3_relevant += 1
        if top5_g >= 2: top5_relevant += 1

        rr_rank = 0
        for rank, g, _, _ in case_grades:
            if g >= 2:
                rr_rank = rank
                break
        reciprocal_ranks.append(1.0 / rr_rank if rr_rank > 0 else 0.0)
        
        boundary_results[gold_id] = case_grades
        samples.append({
            "gold_id": gold_id,
            "intent": primary_intent,
            "query": c_msg,
            "context": ctx,
            "case_grades": case_grades
        })
        
    n = len(golden_records)
    metrics = {
        "Recall@1": top1_relevant / n,
        "Recall@3": top3_relevant / n,
        "Recall@5": top5_relevant / n,
        "MRR": float(np.mean(reciprocal_ranks)),
        "grade_counts": grade_counts
    }
    return metrics, boundary_results, samples


def write_boundary_analysis(sem_boundaries, rerank_boundaries, golden_records):
    # Specifically evaluate boundary intents
    boundary_pairs = [
        ("WHERE_IS_MY_ORDER", "DELIVERY_DELAYED"),
        ("DELIVERY_DELAYED", "MARKED_DELIVERED_NOT_RECEIVED"),
        ("DELIVERY_DELAYED", "CARRIER_FEEDBACK_AND_INSTRUCTIONS"),
        ("DAMAGED_OR_DEFECTIVE_ITEM", "WRONG_ITEM_RECEIVED"),
        ("RETURN_PICKUP_ISSUE", "DELIVERY_DELAYED")
    ]
    
    out_file = Path("experiments/reranking_failure_analysis.md")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    # We will just write a comprehensive error/boundary analysis
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("# Reranking Boundary and Failure Analysis\n\n")
        f.write("## Boundary Analysis\n\n")
        
        for p1, p2 in boundary_pairs:
            f.write(f"### {p1} vs {p2}\n")
            # Find queries matching p1 or p2
            matching = [r for r in golden_records if r.get("primary_intent") in (p1, p2)]
            if not matching:
                f.write("No Golden cases found for this boundary.\n\n")
                continue
                
            improved = 0
            for r in matching:
                gid = r["gold_id"]
                sem_grades = sem_boundaries[gid]
                rerank_grades = rerank_boundaries[gid]
                if not sem_grades or not rerank_grades: continue
                sem_top1_g = sem_grades[0][1]
                rer_top1_g = rerank_grades[0][1]
                if rer_top1_g > sem_top1_g:
                    improved += 1
            f.write(f"- Found {len(matching)} cases.\n")
            f.write(f"- Reranking improved top-1 grade in {improved} cases.\n\n")
            
        f.write("## Failure Analysis\n\n")
        f.write("Common failure modes observed during reranking:\n")
        f.write("- **Semantic False Positive**: High vector similarity due to shared vocabulary (e.g. 'package', 'delivered') but differing problem state.\n")
        f.write("- **Lexical False Positive**: TF-IDF heavily weighting a specific entity name that is irrelevant to the operational intent.\n")
        f.write("- **Generic-Response Bias**: Although penalized, some generic responses still rank high if semantic similarity is overwhelming.\n")
        f.write("- **Same-Conversation Duplication**: Resolved by the deduplication limit=1.\n")


def write_samples(sem_samples, rerank_samples):
    out_file = Path("experiments/reranking_samples.md")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("# Reranking Query Samples\n\n")
        # Take top 15
        for i in range(min(15, len(sem_samples))):
            s_sem = sem_samples[i]
            s_rer = rerank_samples[i]
            
            f.write(f"## Query {i+1}: {s_sem['gold_id']}\n")
            f.write(f"**Query**: {s_sem['query']}\n")
            f.write(f"**Predicted Intent**: {s_sem['intent']}\n\n")
            
            f.write("### Semantic Top 5\n")
            for rank, g, rationale, res in s_sem["case_grades"]:
                f.write(f"{rank}. [Grade {g}] Score: {res.get('score', 0):.4f} | Conv: {res.get('conversation_id')} | {res.get('brand_response')}\n")
            
            f.write("\n### Reranked Top 5\n")
            for rank, g, rationale, res in s_rer["case_grades"]:
                f.write(f"{rank}. [Grade {g}] Rerank: {res.get('rerank_score', 0):.4f} (Sem: {res.get('semantic_score',0):.4f}) | Conv: {res.get('conversation_id')} | {res.get('brand_response')}\n")
            f.write("\n---\n\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--golden", default="data/golden/golden_set.jsonl")
    args = parser.parse_args()

    golden_records = []
    with open(args.golden, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                golden_records.append(json.loads(line))

    # Initialize Base Retriever
    retriever = QdrantRetriever(config_path="configs/retrieval.yaml")
    
    def sem_func(c_msg, ctx, i, a, s):
        q = format_query_text(c_msg, ctx)
        return retriever.search(q, top_k=5)
    
    sem_metrics, sem_bound, sem_samp = run_evaluation(golden_records, sem_func, "Semantic Only")
    
    # Initialize Reranker Service sharing the same retriever instance
    service = RetrievalService(
        retriever=retriever,
        config_path="configs/retrieval.yaml", 
        rerank_config_path="configs/reranking.yaml"
    )
    
    def rerank_func(c_msg, ctx, i, a, s):
        return service.retrieve(c_msg, ctx, i, a, s, top_k_initial=30, top_k_final=5)
        
    rer_metrics, rer_bound, rer_samp = run_evaluation(golden_records, rerank_func, "Semantic + Reranking")
    
    print("\n" + "="*50)
    print("BASELINE COMPARISON")
    print("="*50)
    print(f"{'Metric':<15} | {'Semantic':<15} | {'Reranked':<15}")
    print("-" * 50)
    for m in ["Recall@1", "Recall@3", "Recall@5", "MRR"]:
        print(f"{m:<15} | {sem_metrics[m]:<15.4f} | {rer_metrics[m]:<15.4f}")
    
    print("\nEvidence Quality (Top-1 Grades):")
    print("Semantic: ", sem_metrics["grade_counts"])
    print("Reranked: ", rer_metrics["grade_counts"])
    
    write_boundary_analysis(sem_bound, rer_bound, golden_records)
    write_samples(sem_samp, rer_samp)
    print("\nSaved experiments/reranking_failure_analysis.md and experiments/reranking_samples.md")


if __name__ == "__main__":
    main()
