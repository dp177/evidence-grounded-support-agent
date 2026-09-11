import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/discrepancies.json', encoding='utf-8') as f:
    rows = json.load(f)

print("=== STATUS DISCREPANCIES (23) ===")
for r in rows:
    if r['status_changed']:
        print(f"[{r['gold_id']}] {r['proposed_status']} -> {r['human_status']} | Proposed Pri: {r['proposed_primary']} -> Draft Pri: {r['human_primary']}")
        print(f"   Notes: {r['human_notes']}")
        print(f"   Msg: {r['customer_message'][:90]}...")
        print()

print("=== ESCALATION DISCREPANCIES (5) ===")
for r in rows:
    if r['escalate_changed']:
        print(f"[{r['gold_id']}] Escalate: {r['proposed_escalate']} -> {r['human_escalate']}")
        print(f"   Reason: {r['human_escalation_reason']}")
        print(f"   Notes: {r['human_notes']}")
        print(f"   Msg: {r['customer_message'][:90]}...")
        print()

