import json

with open("evaluation/results/golden_v2_raw.jsonl", encoding="utf-8") as f:
    records = {r["gold_id"]: r for r in (json.loads(line) for line in f)}

print("=== INSPECTING MISSED SECURITY CASES (5) ===")
for gid in ['gold_v2_0001', 'gold_v2_0007', 'gold_v2_0009', 'gold_v2_0011', 'gold_v2_0013']:
    r = records[gid]
    print(f"[{gid}] Message: {r['input']['customer_message']}")
    print(f"       Agent Clf: status={r['agent']['status']}, primary={r['agent']['primary_intent']}, state={r['agent']['state']}")
    print(f"       Agent Esc: escalate={r['agent']['should_escalate']}, decision={r['agent']['escalation_reason']}")
    print()

print("=== INSPECTING MISSED REPEATED SUPPORT CASES (8) ===")
for gid in ['gold_v2_0055', 'gold_v2_0056', 'gold_v2_0088', 'gold_v2_0098', 'gold_v2_0104', 'gold_v2_0119', 'gold_v2_0122', 'gold_v2_0153']:
    r = records[gid]
    print(f"[{gid}] Message: {r['input']['customer_message']}")
    print(f"       Agent Clf: status={r['agent']['status']}, primary={r['agent']['primary_intent']}, state={r['agent']['state']}")
    print(f"       Agent Esc: escalate={r['agent']['should_escalate']}, decision={r['agent']['escalation_reason']}")
    print()

print("=== INSPECTING CARRIER MISCONDUCT CASES (8) ===")
for gid in ['gold_v2_0071', 'gold_v2_0072', 'gold_v2_0073', 'gold_v2_0074', 'gold_v2_0075', 'gold_v2_0076', 'gold_v2_0146', 'gold_v2_0159']:
    r = records[gid]
    print(f"[{gid}] Message: {r['input']['customer_message']}")
    print(f"       Agent Clf: status={r['agent']['status']}, primary={r['agent']['primary_intent']}")
    print(f"       Agent Esc: escalate={r['agent']['should_escalate']}, decision={r['agent']['escalation_reason']}")
    print()

print("=== INSPECTING ROUTINE CARRIER INSTRUCTIONS (4) ===")
for gid in ['gold_v2_0077', 'gold_v2_0078', 'gold_v2_0079', 'gold_v2_0080']:
    r = records[gid]
    print(f"[{gid}] Message: {r['input']['customer_message']}")
    print(f"       Agent Esc: escalate={r['agent']['should_escalate']}, decision={r['agent']['escalation_reason']}")
    print()
