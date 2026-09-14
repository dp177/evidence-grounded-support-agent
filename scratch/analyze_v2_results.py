import json
from collections import defaultdict

with open("evaluation/results/golden_v2_raw.jsonl", encoding="utf-8") as f:
    records = [json.loads(line) for line in f]

print(f"Total records: {len(records)}")

gold_escalated = [r for r in records if r["gold"]["should_escalate"]]
correctly_escalated = [r for r in gold_escalated if r["agent"]["should_escalate"]]
unsafe_auto_handles = [r for r in gold_escalated if not r["agent"]["should_escalate"]]

print(f"Correctly escalated (TP): {len(correctly_escalated)}/{len(gold_escalated)} ({len(correctly_escalated)/len(gold_escalated):.1%})")
print(f"Unsafe auto-handles (FN): {len(unsafe_auto_handles)}/{len(gold_escalated)} ({len(unsafe_auto_handles)/len(gold_escalated):.1%})")

# Breakdown by gold escalation reason
reason_breakdown = defaultdict(lambda: {"total": 0, "tp": 0, "fn": 0, "fn_cases": []})
for r in gold_escalated:
    rea = r["gold"]["escalation_reason"]
    reason_breakdown[rea]["total"] += 1
    if r["agent"]["should_escalate"]:
        reason_breakdown[rea]["tp"] += 1
    else:
        reason_breakdown[rea]["fn"] += 1
        reason_breakdown[rea]["fn_cases"].append(r["gold_id"])

print("\n--- By Gold Escalation Reason ---")
for rea, d in reason_breakdown.items():
    rec = d["tp"] / d["total"] if d["total"] > 0 else 0
    print(f"{rea:35s}: Total={d['total']}, TP={d['tp']}, FN={d['fn']} (Recall: {rec:.1%}) -> FN IDs: {d['fn_cases']}")

# Inspect Unnecessary Escalations (FP)
non_escalated = [r for r in records if not r["gold"]["should_escalate"]]
unnecessary_escalations = [r for r in non_escalated if r["agent"]["should_escalate"]]
print(f"\nUnnecessary Escalations (FP): {len(unnecessary_escalations)}/{len(non_escalated)} ({len(unnecessary_escalations)/len(non_escalated):.1%})")

fp_reasons = defaultdict(list)
for r in unnecessary_escalations:
    agent_rea = r["agent"].get("escalation_reason")
    fp_reasons[agent_rea].append(r["gold_id"])

print("\nFP Agent Escalation Reasons:")
for rea, ids in fp_reasons.items():
    print(f"  {rea}: count={len(ids)}, IDs={ids}")
