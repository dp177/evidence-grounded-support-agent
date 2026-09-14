"""Retrieval grader and metric calculation helpers for AmazonSupportAgent evaluation.

Documents and respects that Golden V1 currently contains NO gold annotated
relevant-document labels. Transparently records candidate rankings and provides
callable metric functions (Recall@k, MRR, nDCG@k) for future annotations.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Set


def recall_at_k(relevant_ids: Set[str], retrieved_ids: List[str], k: int) -> float:
    """Compute Recall@k.

    Fraction of relevant documents present in the top-k retrieved candidates.
    Returns 0.0 if relevant_ids is empty.
    """
    if not relevant_ids:
        return 0.0
    top_k = set(retrieved_ids[:k])
    matched = relevant_ids.intersection(top_k)
    return float(len(matched) / len(relevant_ids))


def mrr(relevant_ids: Set[str], retrieved_ids: List[str]) -> float:
    """Compute Mean Reciprocal Rank (MRR).

    Reciprocal of the 1-based rank of the first relevant document in the retrieved list.
    Returns 0.0 if no relevant document is retrieved.
    """
    if not relevant_ids:
        return 0.0
    for idx, doc_id in enumerate(retrieved_ids):
        if doc_id in relevant_ids:
            return float(1.0 / (idx + 1))
    return 0.0


def ndcg_at_k(relevant_ids: Set[str], retrieved_ids: List[str], k: int) -> float:
    """Compute normalized Discounted Cumulative Gain at k (nDCG@k) with binary relevance."""
    if not relevant_ids:
        return 0.0

    top_k = retrieved_ids[:k]
    dcg = 0.0
    for idx, doc_id in enumerate(top_k):
        rel = 1.0 if doc_id in relevant_ids else 0.0
        dcg += rel / math.log2(idx + 2)

    # Ideal DCG: all min(|relevant|, k) relevant items at the top
    ideal_hits = min(len(relevant_ids), k)
    idcg = sum(1.0 / math.log2(idx + 2) for idx in range(ideal_hits))

    if idcg == 0.0:
        return 0.0
    return float(dcg / idcg)


def grade_case_retrieval(
    retrieval_output: Dict[str, Any],
    gold_relevant_ids: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """Record candidate rankings and calculate retrieval metrics if gold labels are provided."""
    sem_cands = retrieval_output.get("semantic_candidates", [])
    lex_cands = retrieval_output.get("lexical_candidates", [])
    rrf_cands = retrieval_output.get("rrf_candidates", [])

    extracted_rrf = []
    for idx, c in enumerate(rrf_cands):
        extracted_rrf.append({
            "case_id": str(c.get("case_id", "")),
            "document_id": str(c.get("doc_id", c.get("document_id", ""))),
            "semantic_rank": c.get("semantic_rank"),
            "lexical_rank": c.get("lexical_rank"),
            "rrf_rank": c.get("rank", idx + 1),
            "rrf_score": c.get("rrf_score"),
        })

    record: Dict[str, Any] = {
        "status": "EVALUATED" if gold_relevant_ids else "GOLD_LABELS_NOT_AVAILABLE",
        "candidate_counts": {
            "semantic": len(sem_cands),
            "lexical": len(lex_cands),
            "rrf": len(rrf_cands),
        },
        "rrf_candidates": extracted_rrf,
    }

    if gold_relevant_ids:
        rrf_doc_ids = [c.get("case_id") or c.get("document_id", "") for c in rrf_cands]
        record["metrics"] = {
            "recall_at_1": round(recall_at_k(gold_relevant_ids, rrf_doc_ids, 1), 4),
            "recall_at_5": round(recall_at_k(gold_relevant_ids, rrf_doc_ids, 5), 4),
            "mrr": round(mrr(gold_relevant_ids, rrf_doc_ids), 4),
            "ndcg_at_5": round(ndcg_at_k(gold_relevant_ids, rrf_doc_ids, 5), 4),
        }
    else:
        record["metrics"] = None

    return record
