import json
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

records = [json.loads(line) for line in open("evaluation/results/golden_v1_raw.jsonl", encoding="utf-8")]
print(f"Total records: {len(records)}")
for r in records:
    if r["gold"]["should_escalate"]:
        print(f"[{r['gold_id']}] Gold Reason: {r['gold']['escalation_reason']}")
        print(f"  Customer: {r['input']['customer_message']}")
        print(f"  Context: {r['input']['context']}")
        print(f"  Agent Escalate: {r['agent']['should_escalate']} | Agent Reason: {r['agent']['escalation_reason']} | State: {r['agent']['state']}")
        print("-" * 60)
