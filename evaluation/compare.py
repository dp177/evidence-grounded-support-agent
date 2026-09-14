"""Baseline vs Candidate Comparison CLI for AmazonSupportAgent evaluation results.

Usage:
  python evaluation/compare.py \\
    --baseline evaluation/baselines/baseline.json \\
    --candidate evaluation/results/golden_v1_results.json

Calculates absolute and percentage deltas, tabular comparison, and regression alerts.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def calculate_delta(base: Optional[float], cand: Optional[float]) -> Tuple[Optional[float], Optional[float]]:
    """Compute (absolute_delta, percentage_delta)."""
    if base is None or cand is None:
        return None, None
    abs_delta = cand - base
    if base != 0.0:
        pct_delta = (abs_delta / abs(base)) * 100.0
    else:
        pct_delta = 0.0 if abs_delta == 0.0 else (100.0 if abs_delta > 0 else -100.0)
    return round(abs_delta, 4), round(pct_delta, 2)


def extract_metric(data: Dict[str, Any], path: List[str]) -> Optional[float]:
    """Safely traverse a nested dict for a numeric metric."""
    curr: Any = data
    for key in path:
        if not isinstance(curr, dict) or key not in curr:
            return None
        curr = curr[key]
    if curr is None:
        return None
    try:
        return float(curr)
    except (ValueError, TypeError):
        return None


def compare_benchmarks(
    baseline_path: Path | str,
    candidate_path: Path | str,
) -> Dict[str, Any]:
    """Compare two evaluation result JSON files."""
    b_path = Path(baseline_path)
    c_path = Path(candidate_path)

    if not b_path.exists():
        raise FileNotFoundError(f"Baseline file not found: {b_path}")
    if not c_path.exists():
        raise FileNotFoundError(f"Candidate file not found: {c_path}")

    with open(b_path, "r", encoding="utf-8") as f:
        base_data = json.load(f)
    with open(c_path, "r", encoding="utf-8") as f:
        cand_data = json.load(f)

    # Metric definitions to compare
    # Format: (display_name, [dict_path], higher_is_better, is_critical_safety)
    metric_specs = [
        ("Status Macro F1", ["classification", "status", "macro_f1"], True, False),
        ("Primary Intent Macro F1", ["classification", "primary_intent", "macro_f1"], True, False),
        ("Multi-Intent Micro F1", ["classification", "multi_intent", "micro_f1"], True, False),
        ("Areas Micro F1", ["classification", "areas", "micro_f1"], True, False),
        ("State Macro F1", ["classification", "state", "macro_f1"], True, False),
        ("Escalation Recall", ["escalation", "recall"], True, True),
        ("Escalation F1", ["escalation", "f1"], True, False),
        ("Unsafe Auto-Handle Rate", ["escalation", "unsafe_auto_handle_rate"], False, True),
        ("Unnecessary Escalation Rate", ["escalation", "unnecessary_escalation_rate"], False, False),
        ("Behavioral Policy Pass Rate", ["behavior", "behavioral_policy_pass_rate"], True, False),
        ("Grounding Pass Rate", ["safety", "grounding_pass_rate"], True, True),
        ("Capability Hallucination Rate", ["safety", "capability_hallucination_rate"], False, True),
        ("Response Overall Score", ["response", "average_overall_score"], True, False),
        ("p50 Latency (ms)", ["operations", "p50_latency_ms"], False, False),
        ("Success Rate", ["operations", "success_rate"], True, False),
    ]

    rows = []
    regressions = []

    for name, path, higher_is_better, is_critical in metric_specs:
        b_val = extract_metric(base_data, path)
        c_val = extract_metric(cand_data, path)
        abs_d, pct_d = calculate_delta(b_val, c_val)

        status = "SAME"
        if abs_d is not None and abs_d != 0.0:
            improved = (abs_d > 0) if higher_is_better else (abs_d < 0)
            if improved:
                status = "IMPROVED"
            else:
                status = "REGRESSION"
                regressions.append({
                    "metric": name,
                    "baseline": b_val,
                    "candidate": c_val,
                    "abs_delta": abs_d,
                    "pct_delta": pct_d,
                    "is_critical": is_critical,
                })

        rows.append({
            "metric": name,
            "baseline": b_val,
            "candidate": c_val,
            "abs_delta": abs_d,
            "pct_delta": pct_d,
            "status": status,
            "is_critical": is_critical,
        })

    return {
        "baseline_file": str(b_path),
        "candidate_file": str(c_path),
        "metrics": rows,
        "regressions": regressions,
    }


def print_comparison_table(result: Dict[str, Any]) -> None:
    """Format comparison result as a readable console table."""
    print("=" * 88)
    print(f"BASELINE:  {result['baseline_file']}")
    print(f"CANDIDATE: {result['candidate_file']}")
    print("=" * 88)
    print(f"{'Metric':<32} {'Baseline':<12} {'Candidate':<12} {'Abs Delta':<12} {'% Delta':<10} {'Status':<10}")
    print("-" * 88)

    for row in result["metrics"]:
        m_name = row["metric"]
        b_str = f"{row['baseline']:.4f}" if row['baseline'] is not None else "N/A"
        c_str = f"{row['candidate']:.4f}" if row['candidate'] is not None else "N/A"
        ad_str = f"{row['abs_delta']:+.4f}" if row['abs_delta'] is not None else "N/A"
        pd_str = f"{row['pct_delta']:+.2f}%" if row['pct_delta'] is not None else "N/A"
        stat = row["status"]

        # Alert marker on critical regressions
        if row["is_critical"] and stat == "REGRESSION":
            stat_display = "!! CRIT REG !!"
        elif stat == "REGRESSION":
            stat_display = "REGRESSION"
        elif stat == "IMPROVED":
            stat_display = "+ IMPROVED"
        else:
            stat_display = "  UNCHANGED"

        print(f"{m_name:<32} {b_str:<12} {c_str:<12} {ad_str:<12} {pd_str:<10} {stat_display:<10}")

    print("=" * 88)
    critical_regs = [r for r in result["regressions"] if r["is_critical"]]
    if critical_regs:
        print("\nCRITICAL SAFETY REGRESSIONS DETECTED:")
        for cr in critical_regs:
            print(f"  - [CRITICAL] {cr['metric']}: {cr['baseline']} -> {cr['candidate']} ({cr['pct_delta']:+.2f}%)")
    elif result["regressions"]:
        print(f"\nObserved {len(result['regressions'])} non-critical performance regressions.")
    else:
        print("\nNo regressions detected. Candidate is on par or improved across all evaluated metrics.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare baseline vs candidate evaluation results.")
    parser.add_argument("--baseline", required=True, help="Path to baseline results JSON file")
    parser.add_argument("--candidate", required=True, help="Path to candidate results JSON file")
    parser.add_argument("--fail-on-regression", action="store_true", help="Exit with non-zero code if critical regressions detected")

    args = parser.parse_args()

    try:
        res = compare_benchmarks(args.baseline, args.candidate)
        print_comparison_table(res)

        if args.fail_on_regression:
            has_crit = any(r["is_critical"] for r in res["regressions"])
            if has_crit:
                sys.exit(1)
    except Exception as e:
        print(f"Comparison error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
