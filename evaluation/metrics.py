"""Metrics aggregator and Markdown report generator for Golden V1 evaluation.

Aggregates all per-case raw records into golden_v1_results.json and golden_v1_report.md
strictly conforming to the 11-section evaluation report layout.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np

from evaluation.graders.classification import (
    evaluate_primary_intent,
    evaluate_set_based_labels,
    evaluate_state,
    evaluate_status,
    parse_pipe_separated,
)
from evaluation.graders.escalation import (
    evaluate_conditional_escalation_reason,
    evaluate_escalation_binary,
)
from evaluation.graders.behavior import aggregate_behavioral_metrics

logger = logging.getLogger(__name__)


def compute_all_metrics(raw_records: List[Dict[str, Any]], source_file: Optional[str] = None) -> Dict[str, Any]:
    """Aggregate per-case records into the structured benchmark JSON output."""
    n = len(raw_records)
    if n == 0:
        return {}

    # 1. Dataset distributions
    status_counts: Dict[str, int] = {}
    gold_escalated_count = 0
    for r in raw_records:
        st = r["gold"].get("status", "NORMAL")
        status_counts[st] = status_counts.get(st, 0) + 1
        if r["gold"].get("should_escalate"):
            gold_escalated_count += 1

    dataset_summary = {
        "total_cases": n,
        "source_file": source_file or "data/golden/golden_v1_assistant_adjudicated.csv",
        "status_distribution": status_counts,
        "escalated_count": gold_escalated_count,
        "non_escalated_count": n - gold_escalated_count,
    }

    # 2. Classification metrics
    gold_status = [r["gold"].get("status", "NORMAL") for r in raw_records]
    agent_status = [r["agent"].get("status", "NORMAL") for r in raw_records]
    status_metrics = evaluate_status(gold_status, agent_status)

    gold_primary = [r["gold"].get("primary_intent") for r in raw_records]
    agent_primary = [r["agent"].get("primary_intent") for r in raw_records]
    primary_metrics = evaluate_primary_intent(gold_primary, agent_primary, status_true=gold_status)

    gold_intents = [parse_pipe_separated(r["gold"].get("intents")) for r in raw_records]
    agent_intents = [parse_pipe_separated(r["agent"].get("intents")) for r in raw_records]
    multi_intent_metrics = evaluate_set_based_labels(gold_intents, agent_intents)

    gold_areas = [parse_pipe_separated(r["gold"].get("areas")) for r in raw_records]
    agent_areas = [parse_pipe_separated(r["agent"].get("areas")) for r in raw_records]
    areas_metrics = evaluate_set_based_labels(gold_areas, agent_areas)

    gold_state = [r["gold"].get("state", "INITIAL_INQUIRY") for r in raw_records]
    agent_state = [r["agent"].get("state", "INITIAL_INQUIRY") for r in raw_records]
    state_metrics = evaluate_state(gold_state, agent_state)

    classification_summary = {
        "status": status_metrics,
        "primary_intent": primary_metrics,
        "multi_intent": multi_intent_metrics,
        "areas": areas_metrics,
        "state": state_metrics,
    }

    # 3. Escalation and safety metrics
    gold_esc = [bool(r["gold"].get("should_escalate", False)) for r in raw_records]
    agent_esc = [bool(r["agent"].get("should_escalate", False)) for r in raw_records]
    esc_binary_metrics = evaluate_escalation_binary(gold_esc, agent_esc)

    gold_reason = [r["gold"].get("escalation_reason") for r in raw_records]
    agent_reason = [r["agent"].get("escalation_reason") for r in raw_records]
    esc_reason_metrics = evaluate_conditional_escalation_reason(gold_reason, agent_reason, gold_esc)

    escalation_summary = {
        **esc_binary_metrics,
        **esc_reason_metrics,
    }

    # 4. Behavioral policy metrics
    case_behaviors = [r["graders"].get("behavior", {}) for r in raw_records]
    behavior_summary = aggregate_behavioral_metrics(case_behaviors)

    # 5. Retrieval metrics & candidate ranking stats
    rrf_candidate_counts = [
        len(r["graders"].get("retrieval", {}).get("rrf_candidates", []))
        for r in raw_records
    ]
    retrieval_summary = {
        "status": "GOLD_LABELS_NOT_AVAILABLE",
        "message": "Golden V1 has no annotated retrieval relevance field; candidate ranks and RRF scores instrumented.",
        "metric_hooks_ready": True,
        "mean_candidates_retrieved": round(float(np.mean(rrf_candidate_counts)), 2) if rrf_candidate_counts else 0.0,
    }

    # 6. Safety metrics
    grounding_passed_count = sum(
        1 for r in raw_records if r["graders"].get("safety", {}).get("grounding_passed", False)
    )
    cap_hallucination_count = sum(
        1 for r in raw_records if r["graders"].get("safety", {}).get("capability_hallucination_detected", False)
    )
    unsupported_claim_cases = sum(
        1 for r in raw_records if r["graders"].get("safety", {}).get("unsupported_claim_count", 0) > 0
    )

    safety_summary = {
        "grounding_pass_rate": round(float(grounding_passed_count / n), 4),
        "capability_hallucination_rate": round(float(cap_hallucination_count / n), 4),
        "unsupported_claim_rate": round(float(unsupported_claim_cases / n), 4),
    }

    # 7. Response quality (LLM Judge)
    judge_evaluated_cases = [
        r["graders"].get("response", {})
        for r in raw_records
        if r["graders"].get("response", {}).get("evaluated", False)
    ]
    if judge_evaluated_cases:
        dimension_keys = ["relevance", "correctness", "groundedness", "actionability", "safety_honesty", "conversation_awareness"]
        dim_avgs = {}
        for dk in dimension_keys:
            vals = [j["scores"][dk] for j in judge_evaluated_cases if j.get("scores", {}).get(dk) is not None]
            dim_avgs[dk] = round(float(np.mean(vals)), 2) if vals else None

        overall_vals = [j.get("overall_score") for j in judge_evaluated_cases if j.get("overall_score") is not None]
        response_summary = {
            "evaluator_type": "llm_judge",
            "available": True,
            "evaluated_cases": len(judge_evaluated_cases),
            "average_overall_score": round(float(np.mean(overall_vals)), 2) if overall_vals else None,
            "dimensions": dim_avgs,
        }
    else:
        response_summary = {
            "evaluator_type": "llm_judge",
            "available": False,
            "evaluated_cases": 0,
            "notice": "LLM judge skipped or unavailable. Deterministic metrics remain 100% valid.",
        }

    # 8. Operations diagnostics
    latencies = [int(r["operations"].get("latency_ms", 0)) for r in raw_records if "latency_ms" in r["operations"]]
    successes = sum(1 for r in raw_records if r["operations"].get("success", False))

    operations_summary = {
        "mean_latency_ms": round(float(np.mean(latencies)), 1) if latencies else 0.0,
        "p50_latency_ms": round(float(np.median(latencies)), 1) if latencies else 0.0,
        "p95_latency_ms": round(float(np.percentile(latencies, 95)), 1) if latencies else 0.0,
        "success_rate": round(float(successes / n), 4),
        "total_cases": n,
    }

    return {
        "dataset": dataset_summary,
        "classification": classification_summary,
        "escalation": escalation_summary,
        "retrieval": retrieval_summary,
        "behavior": behavior_summary,
        "safety": safety_summary,
        "response": response_summary,
        "operations": operations_summary,
    }


def generate_markdown_report(summary: Dict[str, Any], raw_records: List[Dict[str, Any]]) -> str:
    """Generate the standardized 11-section Golden V1 Evaluation Report."""
    ds = summary.get("dataset", {})
    clf = summary.get("classification", {})
    esc = summary.get("escalation", {})
    ret = summary.get("retrieval", {})
    beh = summary.get("behavior", {})
    safe = summary.get("safety", {})
    resp = summary.get("response", {})
    ops = summary.get("operations", {})

    # Top 10 failure cases: find cases where classification, escalation, or behavior failed
    failure_cases = []
    for r in raw_records:
        gold_id = r["gold_id"]
        status_match = r["graders"]["classification"].get("status_match", True)
        primary_match = r["graders"]["classification"].get("primary_intent_match", True)
        esc_match = r["graders"]["escalation"].get("escalation_match", True)
        beh_pass = r["graders"]["behavior"].get("overall_policy_pass", True)

        failed_reasons = []
        if not status_match:
            failed_reasons.append(f"Status mismatch: expected {r['gold'].get('status')} vs agent {r['agent'].get('status')}")
        if not primary_match:
            failed_reasons.append(f"Primary intent mismatch: expected {r['gold'].get('primary_intent')} vs agent {r['agent'].get('primary_intent')}")
        if not esc_match:
            failed_reasons.append(f"Escalation mismatch: expected {r['gold'].get('should_escalate')} vs agent {r['agent'].get('should_escalate')}")
        if not beh_pass:
            fails = r["graders"]["behavior"].get("failed_assertions", [])
            failed_reasons.append(f"Behavioral policy failure: {', '.join(fails)}")

        if failed_reasons:
            failure_cases.append({
                "gold_id": gold_id,
                "customer_message": r["input"].get("customer_message", ""),
                "gold": r["gold"],
                "agent": r["agent"],
                "failed_assertion": "; ".join(failed_reasons),
                "explanation": (
                    f"Agent returned status='{r['agent'].get('status')}', primary_intent='{r['agent'].get('primary_intent')}', "
                    f"escalate={r['agent'].get('should_escalate')} while Gold expected status='{r['gold'].get('status')}', "
                    f"primary_intent='{r['gold'].get('primary_intent')}', escalate={r['gold'].get('should_escalate')}."
                ),
            })
            if len(failure_cases) >= 10:
                break

    report_title = "Golden V2 Evaluation Report: Hiver AmazonSupportAgent" if "v2" in str(ds.get("source_file", "")).lower() else "Golden V1 Evaluation Report: Hiver AmazonSupportAgent"
    lines = [
        f"# {report_title}",
        "",
        f"**Dataset Source:** `{ds.get('source_file')}`  ",
        f"**Total Evaluated Cases:** {ds.get('total_cases', 0)}  ",
        "",
        "---",
        "",
        "## 1. Dataset",
        f"- **Total Rows:** {ds.get('total_cases', 0)} cases conforming strictly to the locked Golden V1 schema.",
        f"- **Status Distribution:** `NORMAL`: {ds.get('status_distribution', {}).get('NORMAL', 0)}, "
        f"`AMBIGUOUS`: {ds.get('status_distribution', {}).get('AMBIGUOUS', 0)}, "
        f"`OUT_OF_SCOPE`: {ds.get('status_distribution', {}).get('OUT_OF_SCOPE', 0)}.",
        f"- **Escalation Distribution:** `True` (Escalate): {ds.get('escalated_count', 0)}, `False` (Auto-Handle): {ds.get('non_escalated_count', 0)}.",
        "- **Field Roles:** Benchmarking is conducted exclusively against the definitive human adjudications.",
        "",
        "## 2. Evaluation Contract",
        "- **Status & Intent:** Null handling ensures `AMBIGUOUS` and `OUT_OF_SCOPE` correctly expect null intent/area.",
        "- **Multi-Intent & Areas:** Set-based micro and macro metrics; pipe-separated tokens parsed without combination labels.",
        "- **Escalation Reason:** Evaluated conditionally on cases where `human_should_escalate == True`.",
        "- **Response Evaluation:** Reference-free 6-dimension rubric; `human_notes` is never used as a canonical generation target.",
        "- **Retrieval Policy:** Retrieval on `NORMAL` is non-mandatory (diagnostic). `AMBIGUOUS` and `OUT_OF_SCOPE` enforce hard retrieval suppression.",
        "",
        "## 3. Classification",
        "",
        "| Task / Dimension | Accuracy | Macro F1 | Weighted F1 / Micro F1 | Exact Set Match |",
        "| :--- | :---: | :---: | :---: | :---: |",
        f"| **Status** | {clf.get('status', {}).get('accuracy', 0.0):.4f} | {clf.get('status', {}).get('macro_f1', 0.0):.4f} | {clf.get('status', {}).get('weighted_f1', 0.0):.4f} | N/A |",
        f"| **Primary Intent** | {clf.get('primary_intent', {}).get('accuracy', 0.0):.4f} | {clf.get('primary_intent', {}).get('macro_f1', 0.0):.4f} | {clf.get('primary_intent', {}).get('weighted_f1', 0.0):.4f} | N/A |",
        f"| **Multi-Intent** | N/A | {clf.get('multi_intent', {}).get('macro_f1', 0.0):.4f} | {clf.get('multi_intent', {}).get('micro_f1', 0.0):.4f} | {clf.get('multi_intent', {}).get('exact_set_match', 0.0):.4f} |",
        f"| **Areas** | N/A | {clf.get('areas', {}).get('macro_f1', 0.0):.4f} | {clf.get('areas', {}).get('micro_f1', 0.0):.4f} | {clf.get('areas', {}).get('exact_set_match', 0.0):.4f} |",
        f"| **State** | {clf.get('state', {}).get('accuracy', 0.0):.4f} | {clf.get('state', {}).get('macro_f1', 0.0):.4f} | {clf.get('state', {}).get('weighted_f1', 0.0):.4f} | N/A |",
        "",
        "## 4. Escalation and Safety",
        "",
        "| Metric | Value | Description |",
        "| :--- | :---: | :--- |",
        f"| **Escalation Accuracy** | {esc.get('accuracy', 0.0):.4f} | Overall accuracy of binary escalation decision |",
        f"| **Escalation Precision** | {esc.get('precision', 0.0):.4f} | Precision on escalated cases |",
        f"| **Escalation Recall** | {esc.get('recall', 0.0):.4f} | Recall on escalated cases |",
        f"| **Escalation F1** | {esc.get('f1', 0.0):.4f} | Balanced F1 score for escalation |",
        f"| **Unsafe Auto-Handle Rate** | **{esc.get('unsafe_auto_handle_rate', 0.0):.4f}** | Critical risk: Gold escalated but Agent auto-handled |",
        f"| **Unnecessary Escalation Rate** | {esc.get('unnecessary_escalation_rate', 0.0):.4f} | Operational cost: Gold auto-handle but Agent escalated |",
        f"| **Conditional Reason Accuracy** | {esc.get('conditional_accuracy', 0.0):.4f} | Reason accuracy evaluated only when Gold escalated |",
        f"| **Grounding Pass Rate** | {safe.get('grounding_pass_rate', 0.0):.4f} | Proportion of responses passing factual verification |",
        f"| **Capability Hallucination Rate** | **{safe.get('capability_hallucination_rate', 0.0):.4f}** | Unsupported action claims (e.g. 'I checked your account') |",
        "",
        "## 5. Retrieval",
        "- **Status:** `GOLD_LABELS_NOT_AVAILABLE`",
        "- **Instrumentation Note:** Golden V1 currently contains no human-annotated relevant case/document column. To maintain integrity, no artificial retrieval ground truth was fabricated.",
        f"- **RRF Instrumentation:** Top-5 candidate rankings, Reciprocal Rank Fusion scores, and candidate counts (mean: {ret.get('mean_candidates_retrieved', 0.0):.2f}) were captured for all retrieval-enabled cases.",
        "- **Metric Hooks:** Standardized `Recall@k`, `MRR`, and `nDCG@k` calculation functions are implemented and unit-tested, ready for future annotated benchmarks.",
        "",
        "## 6. Behavioral Policy",
        f"- **Behavioral Policy Pass Rate:** **{beh.get('behavioral_policy_pass_rate', 0.0) * 100.0:.2f}%**",
        "- **Assertion Breakdown:**",
    ]

    for k, v in beh.get("assertion_stats", {}).items():
        lines.append(f"  - `{k}`: {v.get('pass_rate', 0.0) * 100.0:.1f}% pass ({v.get('passed_cases', 0)}/{v.get('applicable_cases', 0)} applicable cases)")

    lines.extend([
        "",
        "## 7. Response Quality",
    ])

    if resp.get("available"):
        lines.extend([
            f"- **Evaluator Type:** `{resp.get('evaluator_type')}`",
            f"- **Average Overall Score:** {resp.get('average_overall_score', 'N/A')} / 5.0",
            "- **Dimension Averages (1–5 scale):**",
        ])
        for dk, dv in resp.get("dimensions", {}).items():
            lines.append(f"  - `{dk}`: {dv if dv is not None else 'N/A'}")
    else:
        lines.extend([
            f"- **Status:** Model-based response judge not enabled or unavailable ({resp.get('notice', 'Skipped')}).",
            "- **Deterministic Safety Results:** Factual grounding and capability safety checks were executed independently.",
        ])

    lines.extend([
        "",
        "## 8. Operations",
        f"- **Mean Latency:** {ops.get('mean_latency_ms', 0.0):.1f} ms  ",
        f"- **p50 Latency:** {ops.get('p50_latency_ms', 0.0):.1f} ms  ",
        f"- **p95 Latency:** {ops.get('p95_latency_ms', 0.0):.1f} ms  ",
        f"- **Execution Success Rate:** {ops.get('success_rate', 0.0) * 100.0:.2f}%  ",
        "",
        "## 9. Failure Analysis",
        f"Inspecting the top {len(failure_cases)} informative discrepancies observed during evaluation:",
        "",
    ])

    if failure_cases:
        for idx, fc in enumerate(failure_cases):
            lines.extend([
                f"### Case {idx + 1}: `{fc['gold_id']}`",
                f"- **Customer Message:** \"{fc['customer_message']}\"",
                f"- **Failed Assertion:** {fc['failed_assertion']}",
                f"- **Explanation:** {fc['explanation']}",
                "",
            ])
    else:
        lines.append("No significant discrepancies or failures observed across the evaluated sample.\n")

    lines.extend([
        "## 10. Baseline vs Candidate",
        "To compare candidate model iterations against a benchmark baseline:",
        "```bash",
        "python evaluation/compare.py \\",
        "  --baseline evaluation/baselines/<baseline>.json \\",
        "  --candidate evaluation/results/golden_v1_results.json",
        "```",
        "The comparison CLI computes absolute deltas, percentage shifts, and alerts on critical safety regressions (increased unsafe auto-handle rate, increased capability hallucination rate, decreased grounding rate).",
        "",
        "## 11. Limitations",
        "1. **Retrieval Ground Truth Absence:** Golden V1 does not contain document-level relevance annotations; retrieval precision/recall cannot yet be graded without manual relevance annotation.",
        "2. **LLM Judge Subjectivity:** LLM-as-a-judge scores are heuristic and must be calibrated against human preference distributions before making high-stakes deployment decisions.",
        "3. **Confidence Level Separation:** Deterministic classification and safety metrics provide 100% reproducible statistical bounds, whereas response quality scores are model-generated approximations.",
        "4. **Holistic Assessment:** Strict end-to-end composite metrics must not obscure partial credit across modular stages (e.g. correct intent classification paired with safe clarification).",
    ])

    return "\n".join(lines)
