"""Golden Evaluation Runner for Hiver AmazonSupportAgent.

Executes the REAL current AmazonSupportAgent against data/golden/golden_v1_assistant_adjudicated.csv
with:
- Fresh isolated conversation_id per case
- Pure observable event collection (no internal CoT)
- Comprehensive deterministic grading + optional LLM-as-judge
- Clean separation of gold, agent, trace, graders, operations, and errors
- Output to golden_v1_raw.jsonl, golden_v1_results.json, and golden_v1_report.md
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import logging
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# Safe console encoding for Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from support_agent.agent import SupportAgent
from support_agent.llm.client import get_llm_client

from evaluation.graders.classification import grade_case_classification
from evaluation.graders.escalation import grade_case_escalation
from evaluation.graders.behavior import grade_case_behavior
from evaluation.graders.retrieval import grade_case_retrieval
from evaluation.graders.response import ResponseGrader
from evaluation.metrics import compute_all_metrics, generate_markdown_report

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_GOLDEN_PATH = ROOT / "data/golden/golden_v1_assistant_adjudicated.csv"
DEFAULT_OUTPUT_DIR = ROOT / "evaluation/results"


def build_case_messages(customer_message: str, context: Optional[str]) -> List[Dict[str, str]]:
    """Convert raw golden dataset message and context into normalized turn list for SupportAgent."""
    msg_clean = str(customer_message or "").strip()
    ctx_clean = str(context or "").strip()

    if not ctx_clean or ctx_clean == f"CUSTOMER: {msg_clean}":
        return [{"role": "customer", "content": msg_clean}]

    lines = [l.strip() for l in ctx_clean.splitlines() if l.strip()]
    messages: List[Dict[str, str]] = []
    for line in lines:
        if line.upper().startswith("CUSTOMER:"):
            messages.append({"role": "customer", "content": line[9:].strip()})
        elif line.upper().startswith("BRAND:") or line.upper().startswith("AMAZON:"):
            messages.append({"role": "assistant", "content": line[6:].strip()})
        else:
            messages.append({"role": "assistant", "content": line})

    # Ensure current turn is present at the end
    if not messages or messages[-1]["content"] != msg_clean or messages[-1]["role"] != "customer":
        messages.append({"role": "customer", "content": msg_clean})

    return messages


def evaluate_single_case(
    row: Dict[str, Any],
    agent: SupportAgent,
    response_grader: ResponseGrader,
    skip_llm_judge: bool = False,
) -> Dict[str, Any]:
    """Execute real agent pipeline for a single Golden case and grade all facets."""
    gold_id = str(row.get("gold_id", ""))
    case_id = str(row.get("case_id", ""))
    customer_message = str(row.get("customer_message", ""))
    context = str(row.get("context", ""))

    # ISOLATED TRIAL: Generate fresh, distinct conversation_id for every trial
    conv_id = f"eval_{gold_id}_{uuid.uuid4().hex[:8]}"

    # Ground truth values (Strictly the 7 definitive fields)
    gold_record = {
        "status": str(row.get("human_status", "NORMAL")).strip(),
        "areas": str(row.get("human_areas", "")).strip() if pd.notna(row.get("human_areas")) else None,
        "intents": str(row.get("human_intents", "")).strip() if pd.notna(row.get("human_intents")) else None,
        "primary_intent": str(row.get("human_primary_intent", "")).strip() if pd.notna(row.get("human_primary_intent")) else None,
        "state": str(row.get("human_states", "INITIAL_INQUIRY")).strip(),
        "should_escalate": bool(row.get("human_should_escalate", False)),
        "escalation_reason": str(row.get("human_escalation_reason", "")).strip() if pd.notna(row.get("human_escalation_reason")) else None,
    }

    messages = build_case_messages(customer_message, context)

    t0 = time.time()
    events: List[Dict[str, Any]] = []
    final_response: Dict[str, Any] = {}
    errors: List[str] = []
    success = True

    try:
        # Run real agent handle_stream to capture observable events
        for event in agent.handle_stream(conversation_id=conv_id, messages=messages):
            ev_type = event.get("type")
            ev_status = event.get("status", "COMPLETED")
            ev_lat = event.get("latency_ms")

            # Capture only observable pipeline events (NO internal chain-of-thought)
            events.append({
                "type": ev_type,
                "status": ev_status,
                "latency_ms": ev_lat,
            })

            if ev_type == "complete":
                final_response = event.get("response", {})
    except Exception as ex:
        success = False
        err_msg = f"Agent pipeline failure: {type(ex).__name__}: {ex}"
        logger.error(f"[{gold_id}] {err_msg}")
        errors.append(err_msg)

    latency_ms = max(1, int((time.time() - t0) * 1000))

    # Extract agent outputs
    clf_out = final_response.get("classification", {})
    agent_status = clf_out.get("status", "NORMAL")
    agent_primary = clf_out.get("primary_intent")
    agent_intents = clf_out.get("intents", [])
    agent_areas = clf_out.get("areas", [])
    agent_states = clf_out.get("states", ["INITIAL_INQUIRY"])

    esc_out = final_response.get("escalation", {})
    agent_decision = esc_out.get("decision", "AUTO_HANDLE")
    agent_should_escalate = (agent_decision == "HUMAN_REVIEW")
    agent_reason_codes = esc_out.get("reason_codes", [])
    agent_reason = agent_reason_codes[0] if agent_reason_codes else None

    gen_out = final_response.get("generated_reply", {})
    agent_reply = gen_out.get("reply", "")
    agent_grounding = final_response.get("grounding", {})

    agent_record = {
        "status": agent_status,
        "areas": agent_areas,
        "intents": agent_intents,
        "primary_intent": agent_primary,
        "state": agent_states[0] if agent_states else "INITIAL_INQUIRY",
        "should_escalate": agent_should_escalate,
        "escalation_reason": agent_reason,
        "response": agent_reply,
        "grounding": agent_grounding,
    }

    # Behavioral flags observed
    retrieval_used = any(e["type"] == "retrieve" for e in events) or len(final_response.get("retrieved_evidence", [])) > 0
    reranking_used = any(e["type"] == "rerank" for e in events)
    generation_used = any(e["type"] == "generate" for e in events) or bool(agent_reply)
    grounding_passed = bool(agent_grounding.get("status") == "GROUNDED" or gen_out.get("is_grounded", False))

    behavior_meta = {
        "retrieval_used": retrieval_used,
        "reranking_used": reranking_used,
        "generation_used": generation_used,
        "grounding_passed": grounding_passed,
    }

    # Execute graders for this case
    clf_grade = grade_case_classification(gold_record, agent_record)
    esc_grade = grade_case_escalation(gold_record, agent_record)
    beh_grade = grade_case_behavior(gold_record, agent_record, behavior_meta)

    # Retrieval rankings
    retrieval_data = {
        "semantic_candidates": final_response.get("reranking", {}).get("ranked_cases", []),
        "lexical_candidates": [],
        "rrf_candidates": final_response.get("retrieved_evidence", []),
    }
    ret_grade = grade_case_retrieval(retrieval_data, gold_relevant_ids=None)

    # Response quality & capability safety
    enable_judge = (not skip_llm_judge) and success and bool(agent_reply)
    resp_grade_raw = response_grader.grade_response(
        customer_message=customer_message,
        context=context,
        generated_reply=agent_reply,
        grounding_block=agent_grounding,
        enable_llm_judge=enable_judge,
    )

    safety_grade = resp_grade_raw.get("safety", {})
    response_grade = resp_grade_raw.get("judge", {})

    model_calls = final_response.get("trace", {}).get("llm_calls", 1 if success else 0)

    # Complete separated raw record conforming to Correction 5
    return {
        "gold_id": gold_id,
        "case_id": case_id,
        "conversation_id": conv_id,
        "input": {
            "customer_message": customer_message,
            "context": context,
        },
        "gold": gold_record,
        "agent": agent_record,
        "trace": {
            "events": events,
        },
        "graders": {
            "classification": clf_grade,
            "escalation": esc_grade,
            "behavior": beh_grade,
            "retrieval": ret_grade,
            "safety": safety_grade,
            "response": response_grade,
        },
        "operations": {
            "latency_ms": latency_ms,
            "success": success,
            "model_calls": model_calls,
            "tokens": None,
            "estimated_cost": None,
        },
        "errors": errors,
    }


def run_evaluation(
    golden_path: Path | str = DEFAULT_GOLDEN_PATH,
    output_dir: Path | str = DEFAULT_OUTPUT_DIR,
    limit: Optional[int] = None,
    concurrency: int = 1,
    skip_llm_judge: bool = False,
    checkpoint_file: Optional[Path | str] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Path]:
    """Run full evaluation across the Golden dataset."""
    golden_file = Path(golden_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not golden_file.exists():
        raise FileNotFoundError(f"Golden dataset not found at {golden_file}")

    df = pd.read_csv(golden_file)
    total_golden_rows = len(df)
    assert total_golden_rows == 200, f"Golden V1 contract requires exactly 200 rows; found {total_golden_rows}"

    if "v3" in golden_file.name.lower():
        prefix = "golden_v3"
        dataset_label = "Golden V3"
    elif "v2" in golden_file.name.lower():
        prefix = "golden_v2"
        dataset_label = "Golden V2"
    else:
        prefix = "golden_v1"
        dataset_label = "Golden V1"

    cases_to_run = df.to_dict("records")
    if limit is not None and limit > 0:
        cases_to_run = cases_to_run[:limit]
        print(f"Running evaluation on subset of {len(cases_to_run)} cases (limit={limit}).")
    else:
        print(f"Running full evaluation on all {len(cases_to_run)} {dataset_label} cases.")

    # Initialize shared components
    agent = SupportAgent()
    response_grader = ResponseGrader(llm_client=agent.llm_client)

    completed_cases: Dict[str, Dict[str, Any]] = {}
    cp_path = Path(checkpoint_file) if checkpoint_file else out_dir / f"{prefix}_eval_checkpoint.json"

    if cp_path.exists():
        try:
            with open(cp_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
                for item in saved:
                    completed_cases[item["gold_id"]] = item
            print(f"Loaded {len(completed_cases)} existing cases from checkpoint.")
        except Exception as e:
            logger.warning(f"Could not read checkpoint {cp_path}: {e}")

    remaining = [c for c in cases_to_run if str(c.get("gold_id")) not in completed_cases]
    print(f"Cases to execute: {len(remaining)} (concurrency={concurrency}, skip_llm_judge={skip_llm_judge})")

    if remaining:
        if concurrency > 1:
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
                future_to_case = {
                    executor.submit(
                        evaluate_single_case,
                        case,
                        agent,
                        response_grader,
                        skip_llm_judge,
                    ): case for case in remaining
                }

                done_count = 0
                for future in concurrent.futures.as_completed(future_to_case):
                    res = future.result()
                    completed_cases[res["gold_id"]] = res
                    done_count += 1
                    if done_count % 5 == 0 or done_count == len(remaining):
                        print(f"  [{done_count:3d}/{len(remaining)}] Completed {res['gold_id']}")
                        with open(cp_path, "w", encoding="utf-8") as f:
                            json.dump(list(completed_cases.values()), f, indent=2)
        else:
            for idx, case in enumerate(remaining):
                res = evaluate_single_case(case, agent, response_grader, skip_llm_judge)
                completed_cases[res["gold_id"]] = res
                print(f"  [{idx + 1:3d}/{len(remaining)}] Completed {res['gold_id']}")
                if (idx + 1) % 5 == 0 or idx + 1 == len(remaining):
                    with open(cp_path, "w", encoding="utf-8") as f:
                        json.dump(list(completed_cases.values()), f, indent=2)

    # Order results to match golden dataset sequence
    ordered_results = [completed_cases[str(c.get("gold_id"))] for c in cases_to_run if str(c.get("gold_id")) in completed_cases]

    # 1. Write per-case raw JSONL file
    raw_jsonl_path = out_dir / f"{prefix}_raw.jsonl"
    with open(raw_jsonl_path, "w", encoding="utf-8") as f:
        for rec in ordered_results:
            f.write(json.dumps(rec, default=str) + "\n")
    print(f"\nSaved raw JSONL records to: {raw_jsonl_path} ({len(ordered_results)} records)")

    # 2. Compute aggregate metrics
    metrics_summary = compute_all_metrics(ordered_results, source_file=str(golden_file))

    # 3. Write results JSON
    results_json_path = out_dir / f"{prefix}_results.json"
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2, default=str)
    print(f"Saved results summary to: {results_json_path}")

    # 4. Generate & write Markdown report
    report_content = generate_markdown_report(metrics_summary, ordered_results)
    report_path = out_dir / f"{prefix}_report.md"
    report_path.write_text(report_content, encoding="utf-8")
    print(f"Saved final evaluation report to: {report_path}")

    return ordered_results, metrics_summary, report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Golden evaluation for AmazonSupportAgent.")
    parser.add_argument("--golden-path", "--input", dest="golden_path", default=str(DEFAULT_GOLDEN_PATH), help="Path to golden CSV")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of cases (e.g. 5 for smoke test)")
    parser.add_argument("--concurrency", type=int, default=1, help="Concurrent workers")
    parser.add_argument("--skip-llm-judge", action="store_true", help="Skip model-based LLM judge")
    parser.add_argument("--checkpoint", default=None, help="Path to checkpoint file")

    args = parser.parse_args()

    try:
        run_evaluation(
            golden_path=args.golden_path,
            output_dir=args.output_dir,
            limit=args.limit,
            concurrency=args.concurrency,
            skip_llm_judge=args.skip_llm_judge,
            checkpoint_file=args.checkpoint,
        )
    except Exception as e:
        logger.error(f"Evaluation harness failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
