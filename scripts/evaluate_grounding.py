"""Evaluate grounding on 40 development examples.

Runs the full pipeline:
  LLMIntentClassifier -> RetrievalService (Qdrant + Reranking) -> ResponseGenerator -> Grounding Check

Records results and writes:
  experiments/grounding_dev_review.md
  experiments/grounding_trace_examples.md
  experiments/grounding_dev_raw.json
"""

from __future__ import annotations

import json
import logging
import random
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

# --- Path setup ---
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from support_agent.llm.client import get_llm_client
from support_agent.classification.llm_classifier import LLMIntentClassifier
from support_agent.retrieval.service import RetrievalService
from support_agent.generation.response_generator import ResponseGenerator
from support_agent.generation.revise_response import run_grounded_pipeline
from support_agent.grounding.grounding_checker import (
    check_grounding,
    _contains_high_risk_claim,
)

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DEV_SAMPLE_PATH = ROOT / "data/processed/qdrant_development_sample.parquet"
GOLDEN_PATH = ROOT / "data/golden/golden_set.jsonl"
TAXONOMY_PATH = ROOT / "configs/taxonomy_v1.yaml"
CLASSIFIER_CONFIG = ROOT / "configs/classifier_v2.yaml"
RETRIEVAL_CONFIG = ROOT / "configs/retrieval.yaml"
RERANKING_CONFIG = ROOT / "configs/reranking.yaml"
PROMPT_PATH = ROOT / "prompts/classification_v2.md"

N_EXAMPLES = 40
RANDOM_SEED = 42
OUTPUT_DIR = ROOT / "experiments"
REVIEW_DOC = OUTPUT_DIR / "grounding_dev_review.md"
TRACE_DOC = OUTPUT_DIR / "grounding_trace_examples.md"


# ---------------------------------------------------------------------------
# Load golden set conversation IDs to exclude
# ---------------------------------------------------------------------------

def load_golden_conversation_ids() -> set:
    ids = set()
    if GOLDEN_PATH.exists():
        with open(GOLDEN_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    cid = obj.get("conversation_id") or obj.get("id")
                    if cid:
                        ids.add(str(cid))
                except Exception:
                    pass
    return ids


# ---------------------------------------------------------------------------
# Sample development cases
# ---------------------------------------------------------------------------

def sample_dev_cases(n: int = N_EXAMPLES) -> List[Dict[str, Any]]:
    """Sample diverse cases from the development corpus, excluding Golden V1."""
    df = pd.read_parquet(DEV_SAMPLE_PATH)
    golden_ids = load_golden_conversation_ids()

    if "conversation_id" in df.columns:
        df = df[~df["conversation_id"].astype(str).isin(golden_ids)]

    rows = df.sample(n=min(n, len(df)), random_state=RANDOM_SEED)
    cases = []
    for _, row in rows.iterrows():
        case: Dict[str, Any] = {
            "customer_message": str(row.get("customer_message_clean") or row.get("customer_message", "")),
            "context": str(row.get("context_clean") or row.get("context", "")),
            "conversation_id": str(row.get("conversation_id", "unknown")),
            "document_id": str(row.get("document_id", "unknown")),
        }
        cases.append(case)
    return cases


# ---------------------------------------------------------------------------
# Pipeline runner for a single case
# ---------------------------------------------------------------------------

def run_case(
    case: Dict[str, Any],
    classifier: LLMIntentClassifier,
    retrieval_service: RetrievalService,
    generator: ResponseGenerator,
    llm_client: Any,
) -> Dict[str, Any]:
    """Run the full grounded pipeline on a single case."""
    customer_message = case["customer_message"]
    context = case["context"]

    # 1. Classify
    classification: Dict[str, Any] = {
        "primary_intent": "UNKNOWN",
        "intents": [],
        "areas": [],
        "states": [],
    }
    try:
        clf_output = classifier.classify_case(
            customer_message=customer_message,
            context=context if context else None,
            use_cache=True,
        )
        # Normalise output — classify_case returns the full output dict
        primary = (
            clf_output.get("primary_intent")
            or (clf_output.get("intents") or ["UNKNOWN"])[0]
        )
        classification = {
            "primary_intent": primary,
            "intents": clf_output.get("intents", [primary] if primary != "UNKNOWN" else []),
            "areas": clf_output.get("areas", []),
            "states": clf_output.get("states", []),
        }
    except Exception as e:
        logger.warning(f"Classification failed: {e}")
        classification["error"] = str(e)

    # 2. Retrieve + rerank via RetrievalService
    top_evidence: List[Dict[str, Any]] = []
    try:
        top_evidence = retrieval_service.retrieve(
            customer_message=customer_message,
            context=context if context else None,
            predicted_intents=classification.get("intents"),
            predicted_areas=classification.get("areas"),
            predicted_states=classification.get("states"),
            top_k_initial=30,
            top_k_final=5,
        )
    except Exception as e:
        logger.warning(f"Retrieval failed: {e}")

    # 3. Full grounded pipeline (generation + grounding + revision)
    pipeline_result: Dict[str, Any] = {
        "draft_reply": "",
        "final_reply": "",
        "grounding_status": "ERROR",
        "needs_human_review": True,
        "revision_attempts": 0,
        "revision_history": [],
        "initial_grounding": {},
        "final_grounding_result": {},
    }
    try:
        pipeline_result = run_grounded_pipeline(
            customer_conversation={"customer_message": customer_message, "context": context},
            classification=classification,
            retrieved_evidence=top_evidence,
            generator=generator,
            llm_client=llm_client,
        )
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        pipeline_result["error"] = str(e)

    return {
        "conversation_id": case.get("conversation_id"),
        "document_id": case.get("document_id"),
        "customer_message": customer_message,
        "context": context,
        "classification": classification,
        "retrieved_evidence": top_evidence,
        "pipeline_result": pipeline_result,
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def build_review_doc(results: List[Dict[str, Any]]) -> str:
    lines = [
        "# Phase 9: Grounding Verification — Development Review",
        "",
        f"**Development examples evaluated:** {len(results)}",
        f"**Random seed:** {RANDOM_SEED}",
        f"**Max revision attempts:** 2",
        "",
    ]

    n_passed_first = sum(
        1 for r in results
        if r["pipeline_result"].get("grounding_status") == "PASSED"
        and r["pipeline_result"].get("revision_attempts", 0) == 0
    )
    n_passed_revised = sum(
        1 for r in results
        if r["pipeline_result"].get("grounding_status") == "PASSED"
        and r["pipeline_result"].get("revision_attempts", 0) > 0
    )
    n_failed = sum(1 for r in results if r["pipeline_result"].get("grounding_status") == "FAILED")
    n_escalated = sum(1 for r in results if r["pipeline_result"].get("grounding_status") == "ESCALATED")
    n_error = sum(1 for r in results if r["pipeline_result"].get("grounding_status") == "ERROR")
    n_human = sum(1 for r in results if r["pipeline_result"].get("needs_human_review"))
    n_revised = sum(1 for r in results if r["pipeline_result"].get("revision_attempts", 0) > 0)

    total = max(len(results), 1)

    lines += [
        "## Summary Statistics",
        "",
        "| Metric | Count | % |",
        "|--------|-------|---|",
        f"| Grounded on first attempt | {n_passed_first} | {100*n_passed_first//total}% |",
        f"| Passed after revision | {n_passed_revised} | {100*n_passed_revised//total}% |",
        f"| Failed grounding → human review | {n_failed} | {100*n_failed//total}% |",
        f"| Escalated by revision loop | {n_escalated} | {100*n_escalated//total}% |",
        f"| Error | {n_error} | {100*n_error//total}% |",
        f"| Needs human review (total) | {n_human} | {100*n_human//total}% |",
        f"| Triggered revision | {n_revised} | {100*n_revised//total}% |",
        "",
    ]

    # Average revision attempts
    revision_attempts = [r["pipeline_result"].get("revision_attempts", 0) for r in results]
    avg_attempts = sum(revision_attempts) / total
    lines += [
        f"**Average revision attempts per case:** {avg_attempts:.2f}",
        "",
    ]

    # Grounding score distribution
    final_scores = [
        r["pipeline_result"].get("final_grounding_result", {}).get("grounding_score", None)
        for r in results
    ]
    valid_scores = [s for s in final_scores if s is not None]
    if valid_scores:
        avg_score = sum(valid_scores) / len(valid_scores)
        lines += [
            f"**Average final grounding score:** {avg_score:.3f}",
            "",
        ]

    # Unsupported claim examples
    lines += ["## Unsupported Claim Examples", ""]
    all_unsupported: List[str] = []
    for r in results:
        fg = r["pipeline_result"].get("final_grounding_result", {})
        ig = r["pipeline_result"].get("initial_grounding", {})
        all_unsupported.extend(ig.get("unsupported_claims", [])[:3])
    if all_unsupported:
        for i, c in enumerate(all_unsupported[:20], 1):
            lines.append(f"{i}. {c}")
    else:
        lines.append("No unsupported claims detected in this sample.")
    lines.append("")

    # Risk flag examples
    lines += ["## Risk Flag Examples", ""]
    all_flags: List[str] = []
    for r in results:
        ig = r["pipeline_result"].get("initial_grounding", {})
        all_flags.extend(ig.get("risk_flags", [])[:2])
    if all_flags:
        for i, f in enumerate(all_flags[:15], 1):
            lines.append(f"{i}. {f}")
    else:
        lines.append("No risk flags detected.")
    lines.append("")

    # Successful revision examples
    revised_passed = [
        r for r in results
        if r["pipeline_result"].get("revision_attempts", 0) > 0
        and r["pipeline_result"].get("grounding_status") == "PASSED"
    ]
    lines += ["## Successful Revision Examples", ""]
    for r in revised_passed[:3]:
        pr = r["pipeline_result"]
        lines += [
            f"**Conversation:** `{r['conversation_id']}`",
            f"**Customer:** {r['customer_message'][:300]}",
            f"**Draft (failed grounding):** {pr.get('draft_reply', '')[:300]}",
            f"**Revised (passed):** {pr.get('final_reply', '')[:300]}",
            f"**Revision attempts:** {pr.get('revision_attempts')}",
            "",
        ]
    if not revised_passed:
        lines.append("No successful revisions in this sample.")
    lines.append("")

    # Human review cases
    human_cases = [r for r in results if r["pipeline_result"].get("needs_human_review")]
    lines += ["## Cases Requiring Human Review", ""]
    for r in human_cases[:5]:
        pr = r["pipeline_result"]
        fg = pr.get("final_grounding_result", {})
        ig = pr.get("initial_grounding", {})
        lines += [
            f"**Conversation:** `{r['conversation_id']}`",
            f"**Customer:** {r['customer_message'][:300]}",
            f"**Grounding status:** {pr.get('grounding_status')}",
            f"**Risk flags:** {ig.get('risk_flags', [])}",
            f"**Contradicted:** {ig.get('contradicted_claims', [])}",
            f"**Unsupported:** {ig.get('unsupported_claims', [])}",
            "",
        ]
    if not human_cases:
        lines.append("No cases required human review.")
    lines.append("")

    # False approval / rejection analysis
    lines += [
        "## False Approval / False Rejection Analysis",
        "",
        "> Without human ground-truth labels on these development cases, we cannot compute",
        "> exact false approval / rejection rates. Analysis below is structural.",
        "",
    ]

    potential_fa = [
        r for r in results
        if r["pipeline_result"].get("grounding_status") == "PASSED"
        and _contains_high_risk_claim(r["pipeline_result"].get("final_reply", ""))
        and not r["pipeline_result"].get("final_grounding_result", {}).get("risk_flags")
    ]
    lines += [
        f"**Potential false approvals** (passed + high-risk text + no flags): **{len(potential_fa)}**",
        "",
    ]
    for r in potential_fa[:5]:
        lines.append(f"- `{r['conversation_id']}`: {r['pipeline_result'].get('final_reply', '')[:200]}")
    lines.append("")

    # Potential false rejections — cases where revision was triggered but the draft looks safe
    potential_fr = [
        r for r in results
        if r["pipeline_result"].get("revision_attempts", 0) > 0
        and not _contains_high_risk_claim(r["pipeline_result"].get("draft_reply", ""))
    ]
    lines += [
        f"**Potential false rejections** (revision triggered + no high-risk keywords in draft): **{len(potential_fr)}**",
        "",
    ]
    for r in potential_fr[:3]:
        lines.append(f"- `{r['conversation_id']}`: draft='{r['pipeline_result'].get('draft_reply', '')[:200]}'")
    lines.append("")

    # Evidence ID validation summary
    invalid_id_cases = [
        r for r in results
        if r["pipeline_result"].get("initial_grounding", {}).get("invalid_evidence_ids")
    ]
    lines += [
        f"## Evidence ID Validation",
        f"",
        f"Cases with invalid (invented) evidence IDs in initial draft: **{len(invalid_id_cases)}**",
        "",
    ]
    for r in invalid_id_cases[:5]:
        ig = r["pipeline_result"].get("initial_grounding", {})
        valid_ids = [e.get("document_id") for e in r.get("retrieved_evidence", [])]
        lines += [
            f"- `{r['conversation_id']}`: invalid={ig.get('invalid_evidence_ids', [])} | valid={valid_ids}",
        ]
    lines.append("")

    # Per-case table
    lines += ["---", "", "## Per-Case Summary Table", ""]
    lines.append("| # | Conversation | Intent | Grounding Status | Revision Att. | Score | Human Review |")
    lines.append("|---|-------------|--------|-----------------|---------------|-------|-------------|")
    for i, r in enumerate(results, 1):
        pr = r["pipeline_result"]
        fg = pr.get("final_grounding_result", {})
        clf = r["classification"]
        lines.append(
            f"| {i} | `{r['conversation_id'][:20]}` | {clf.get('primary_intent', '?')[:25]} "
            f"| {pr.get('grounding_status', '?')} | {pr.get('revision_attempts', 0)} "
            f"| {fg.get('grounding_score', 'N/A')} | {'✅' if not pr.get('needs_human_review') else '🚨'} |"
        )
    lines.append("")

    # Detailed per-case section
    lines += ["---", "", "## Detailed Per-Case Review", ""]
    for i, r in enumerate(results, 1):
        pr = r["pipeline_result"]
        fg = pr.get("final_grounding_result", {})
        ig = pr.get("initial_grounding", {})
        clf = r["classification"]
        ev = r.get("retrieved_evidence", [])

        lines += [
            f"### Case {i}: `{r['conversation_id']}`",
            f"",
            f"**CUSTOMER MESSAGE:**",
            f"> {r['customer_message'][:500]}",
            f"",
            f"**CONTEXT:** {r['context'][:300] if r['context'] else '(none)'}",
            f"",
            f"**CLASSIFICATION:**",
            f"- Primary intent: `{clf.get('primary_intent', 'UNKNOWN')}`",
            f"- Intents: {clf.get('intents', [])}",
            f"- States: {clf.get('states', [])}",
            f"",
            f"**RETRIEVED EVIDENCE ({len(ev)} items):**",
        ]
        for j, e in enumerate(ev[:3], 1):
            doc_id = e.get("document_id", f"ev_{j}")
            score = e.get("score", 0.0)
            lines += [
                f"  {j}. ID=`{doc_id}` (score={score:.3f})",
                f"     Customer: {e.get('customer_message', '')[:150]}",
                f"     Amazon: {e.get('brand_response', '')[:150]}",
            ]
        lines += [
            f"",
            f"**DRAFT REPLY:**",
            f"> {pr.get('draft_reply', '(none)')[:500]}",
            f"",
            f"**INITIAL GROUNDING DECISION:**",
            f"- Grounded: `{ig.get('grounded', 'N/A')}` | Score: `{ig.get('grounding_score', 'N/A')}`",
            f"- Unsupported claims: {ig.get('unsupported_claims', [])}",
            f"- Contradicted claims: {ig.get('contradicted_claims', [])}",
            f"- Risk flags: {ig.get('risk_flags', [])}",
            f"- Evidence IDs used: {ig.get('evidence_used', [])}",
            f"- Invalid IDs: {ig.get('invalid_evidence_ids', [])}",
            f"- Valid retrieved IDs: {[e.get('document_id') for e in ev]}",
            f"",
            f"**REVISION:** {pr.get('revision_attempts', 0)} attempt(s) | Status: `{pr.get('grounding_status', '?')}`",
            f"",
            f"**FINAL REPLY:**",
            f"> {pr.get('final_reply', '(none)')[:500]}",
            f"",
            f"**FINAL GROUNDING:** Score=`{fg.get('grounding_score', 'N/A')}` | Needs human review: `{pr.get('needs_human_review', 'N/A')}`",
            f"",
            "---",
            "",
        ]

    return "\n".join(lines)


def build_trace_doc(results: List[Dict[str, Any]], n_traces: int = 10) -> str:
    """Build full 10-case trace document."""
    lines = [
        "# Phase 9: Grounding Trace Examples",
        "",
        "Full end-to-end audit traces — customer → classify → retrieve → generate → ground → revise.",
        "",
    ]

    # Pick diverse examples
    passed_first = [r for r in results if r["pipeline_result"].get("grounding_status") == "PASSED"
                    and r["pipeline_result"].get("revision_attempts", 0) == 0]
    revised = [r for r in results if r["pipeline_result"].get("revision_attempts", 0) > 0]
    failed = [r for r in results if r["pipeline_result"].get("grounding_status") == "FAILED"]
    escalated = [r for r in results if r["pipeline_result"].get("grounding_status") == "ESCALATED"]
    errors = [r for r in results if r["pipeline_result"].get("grounding_status") == "ERROR"]

    # Build diverse selection
    selected: List[tuple] = []
    for r in passed_first[:5]:
        selected.append(("PASSED (first attempt)", r))
    for r in revised[:2]:
        selected.append(("REVISED", r))
    for r in failed[:2]:
        selected.append(("FAILED → human review", r))
    for r in escalated[:1]:
        selected.append(("ESCALATED", r))
    # Fill to n_traces from any remaining
    used = {id(r) for _, r in selected}
    for r in results:
        if len(selected) >= n_traces:
            break
        if id(r) not in used:
            selected.append(("ADDITIONAL", r))
            used.add(id(r))

    for label, r in selected[:n_traces]:
        pr = r["pipeline_result"]
        ig = pr.get("initial_grounding", {})
        fg = pr.get("final_grounding_result", {})
        clf = r["classification"]
        ev = r.get("retrieved_evidence", [])
        history = pr.get("revision_history", [])

        lines += [
            "---",
            "",
            f"## [{label}] Conversation: `{r['conversation_id']}`",
            "",
            "### CUSTOMER",
            f"**Message:** {r['customer_message']}",
            "",
            f"**Context:** {r['context'][:500] if r['context'] else '(none)'}",
            "",
            "### CLASSIFICATION",
            f"- Primary intent: `{clf.get('primary_intent', 'UNKNOWN')}`",
            f"- All intents: {clf.get('intents', [])}",
            f"- States: {clf.get('states', [])}",
            f"- Areas: {clf.get('areas', [])}",
            "",
            f"### RETRIEVED EVIDENCE ({len(ev)} items after reranking)",
        ]
        valid_ev_ids = [e.get("document_id") for e in ev]
        for j, e in enumerate(ev, 1):
            doc_id = e.get("document_id", f"ev_{j}")
            score = e.get("score", 0.0)
            ctx = e.get("relevant_context", "") or ""
            lines += [
                f"",
                f"**Evidence {j}** — ID: `{doc_id}` | Rerank Score: `{score:.4f}`",
                f"- Customer: {e.get('customer_message', '')[:200]}",
                f"- Context: {ctx[:150]}",
                f"- Amazon: {e.get('brand_response', '')[:200]}",
            ]

        lines += [
            "",
            "### DRAFT REPLY",
            f"> {pr.get('draft_reply', '(none)')}",
            "",
            "### GROUNDING DECISION (Initial)",
            f"- **Grounded:** `{ig.get('grounded', 'N/A')}`",
            f"- **Grounding score:** `{ig.get('grounding_score', 'N/A')}`",
            f"- **LLM used:** `{ig.get('llm_used', 'N/A')}`",
            f"- **Fast path:** `{ig.get('fast_path', 'N/A')}`",
        ]

        unsup = ig.get("unsupported_claims", [])
        cont = ig.get("contradicted_claims", [])
        flags = ig.get("risk_flags", [])
        ev_used = ig.get("evidence_used", [])
        inv_ids = ig.get("invalid_evidence_ids", [])

        lines += [
            "",
            "**UNSUPPORTED CLAIMS:**",
        ]
        if unsup:
            for c in unsup:
                lines.append(f"- ❌ {c}")
        else:
            lines.append("- (none)")

        lines += ["", "**CONTRADICTED CLAIMS:**"]
        if cont:
            for c in cont:
                lines.append(f"- ⚠️ {c}")
        else:
            lines.append("- (none)")

        lines += ["", "**RISK FLAGS:**"]
        if flags:
            for f in flags:
                lines.append(f"- 🚩 {f}")
        else:
            lines.append("- (none)")

        lines += [
            "",
            "**EVIDENCE ID VALIDATION:**",
            f"- Claimed by generator: {pr.get('generator_output', {}).get('evidence_ids', ig.get('evidence_used', []))}",
            f"- Valid retrieved IDs: {valid_ev_ids}",
            f"- Invalid (invented) IDs: {inv_ids}",
            f"- Evidence used in grounding check: {ev_used}",
        ]

        lines += [
            "",
            "### REVISION",
            f"- **Attempts:** {pr.get('revision_attempts', 0)}",
            f"- **Grounding status:** `{pr.get('grounding_status', '?')}`",
        ]
        for h in history:
            g = h.get("grounding", {})
            lines.append(
                f"  - Attempt {h.get('attempt')}: strategy=`{h.get('strategy')}` | "
                f"grounded=`{g.get('grounded')}` | score=`{g.get('grounding_score')}`"
            )

        lines += [
            "",
            "### FINAL REPLY",
            f"> {pr.get('final_reply', '(none)')}",
            "",
            "### FINAL GROUNDING SUMMARY",
            f"- **Grounded:** `{fg.get('grounded', 'N/A')}`",
            f"- **Final score:** `{fg.get('grounding_score', 'N/A')}`",
            f"- **Needs human review:** `{pr.get('needs_human_review', 'N/A')}`",
            f"- **Evidence used:** {fg.get('evidence_used', [])}",
            "",
        ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("Phase 9: Grounding Verification — Development Evaluation")
    print(f"Evaluating {N_EXAMPLES} development cases")
    print("=" * 60)

    llm_client = get_llm_client()

    # Initialise pipeline components
    print("\n[1/5] Loading pipeline components...")

    classifier = None
    try:
        classifier = LLMIntentClassifier(
            client=llm_client,
            taxonomy_path=str(TAXONOMY_PATH),
            prompt_path=str(PROMPT_PATH) if PROMPT_PATH.exists() else None,
            cache_dir=str(ROOT / "artifacts/llm_predictions_v2"),
        )
        print("  ✅ LLMIntentClassifier loaded")
    except Exception as e:
        print(f"  ❌ LLMIntentClassifier failed: {e}")

    retrieval_service = None
    try:
        retrieval_service = RetrievalService(
            config_path=str(RETRIEVAL_CONFIG),
            rerank_config_path=str(RERANKING_CONFIG),
        )
        print("  ✅ RetrievalService loaded")
    except Exception as e:
        print(f"  ❌ RetrievalService failed: {e}")

    generator = ResponseGenerator(llm_client=llm_client)
    print("  ✅ ResponseGenerator loaded")

    if not classifier or not retrieval_service:
        print("\n  FATAL: Cannot proceed without classifier and retrieval service.")
        sys.exit(1)

    # Sample cases
    print(f"\n[2/5] Sampling {N_EXAMPLES} development cases...")
    cases = sample_dev_cases(N_EXAMPLES)
    print(f"  Sampled {len(cases)} cases (excluding Golden V1)")

    # Run pipeline
    print(f"\n[3/5] Running full grounded pipeline...")
    results = []
    for i, case in enumerate(cases, 1):
        print(f"  [{i:2d}/{len(cases)}] conv={case['conversation_id'][:25]:25s}", end=" ", flush=True)
        t0 = time.time()
        try:
            result = run_case(
                case=case,
                classifier=classifier,
                retrieval_service=retrieval_service,
                generator=generator,
                llm_client=llm_client,
            )
        except Exception as e:
            result = {
                "conversation_id": case.get("conversation_id"),
                "document_id": case.get("document_id"),
                "customer_message": case.get("customer_message", ""),
                "context": case.get("context", ""),
                "classification": {},
                "retrieved_evidence": [],
                "pipeline_result": {
                    "draft_reply": "",
                    "final_reply": "",
                    "grounding_status": "ERROR",
                    "needs_human_review": True,
                    "revision_attempts": 0,
                    "revision_history": [],
                    "initial_grounding": {},
                    "final_grounding_result": {},
                    "error": str(e),
                },
            }
        elapsed = time.time() - t0
        status = result["pipeline_result"].get("grounding_status", "?")
        score = result["pipeline_result"].get("final_grounding_result", {}).get("grounding_score", "?")
        print(f"→ {status:10s} score={score} ({elapsed:.1f}s)")
        results.append(result)

    # Print summary
    print("\n[4/5] Computing summary statistics...")
    n = len(results)
    n_passed_first = sum(1 for r in results if r["pipeline_result"].get("grounding_status") == "PASSED"
                         and r["pipeline_result"].get("revision_attempts", 0) == 0)
    n_passed_rev = sum(1 for r in results if r["pipeline_result"].get("grounding_status") == "PASSED"
                       and r["pipeline_result"].get("revision_attempts", 0) > 0)
    n_failed = sum(1 for r in results if r["pipeline_result"].get("grounding_status") == "FAILED")
    n_escalated = sum(1 for r in results if r["pipeline_result"].get("grounding_status") == "ESCALATED")
    n_error = sum(1 for r in results if r["pipeline_result"].get("grounding_status") == "ERROR")
    n_human = sum(1 for r in results if r["pipeline_result"].get("needs_human_review"))
    n_revised = sum(1 for r in results if r["pipeline_result"].get("revision_attempts", 0) > 0)
    attempts = [r["pipeline_result"].get("revision_attempts", 0) for r in results]
    avg_att = sum(attempts) / max(n, 1)

    print(f"""
  Total cases:                  {n}
  Grounded (first attempt):     {n_passed_first}  ({100*n_passed_first//max(n,1)}%)
  Passed after revision:        {n_passed_rev}  ({100*n_passed_rev//max(n,1)}%)
  Failed → human review:        {n_failed}  ({100*n_failed//max(n,1)}%)
  Escalated by revision loop:   {n_escalated}  ({100*n_escalated//max(n,1)}%)
  Error:                        {n_error}  ({100*n_error//max(n,1)}%)
  Needs human review (total):   {n_human}  ({100*n_human//max(n,1)}%)
  Triggered revision:           {n_revised}  ({100*n_revised//max(n,1)}%)
  Avg revision attempts:        {avg_att:.2f}
    """)

    # Write reports
    print("[5/5] Writing output documents...")
    OUTPUT_DIR.mkdir(exist_ok=True)

    review_md = build_review_doc(results)
    REVIEW_DOC.write_text(review_md, encoding="utf-8")
    print(f"  ✅ {REVIEW_DOC}")

    trace_md = build_trace_doc(results, n_traces=10)
    TRACE_DOC.write_text(trace_md, encoding="utf-8")
    print(f"  ✅ {TRACE_DOC}")

    raw_path = OUTPUT_DIR / "grounding_dev_raw.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  ✅ {raw_path}")

    print("\n✅ Phase 9 Development Evaluation COMPLETE.")


if __name__ == "__main__":
    main()
