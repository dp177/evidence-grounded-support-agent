import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/tax_review_details.json', encoding='utf-8') as f:
    tax = json.load(f)

print("=== 14 TAXONOMY REVIEW CASES ===")
for c in tax:
    print(f"[{c['gold_id']}] Case: {c['case_id']} | Flags: {c['review_flags']} | Outcome: {c['assistant_outcome']}")
    print(f"   Customer Msg: {c['customer_message']}")
    print(f"   Context: {c['context'][:120]}...")
    print(f"   Proposed: status={c['proposed_status']} | intents={c['proposed_intents']} | primary={c['proposed_primary']} | esc={c['proposed_escalate']}")
    print(f"   Assistant Rec: status={c['rec_status']} | intents={c['rec_intents']} | primary={c['rec_primary']} | esc={c['rec_escalate']} ({c['rec_escalation_reason']})")
    print(f"   Notes: {c['rec_notes']}")
    print()

with open('scratch/hum_review_details.json', encoding='utf-8') as f:
    hum = json.load(f)

print("=== 10 HUMAN REVIEW CASES ===")
for c in hum:
    print(f"[{c['gold_id']}] Case: {c['case_id']} | Flags: {c['review_flags']} | Outcome: {c['assistant_outcome']}")
    print(f"   Customer Msg: {c['customer_message']}")
    print(f"   Context: {c['context'][:120]}...")
    print(f"   Proposed: status={c['proposed_status']} | intents={c['proposed_intents']} | primary={c['proposed_primary']} | esc={c['proposed_escalate']}")
    print(f"   Assistant Rec: status={c['rec_status']} | intents={c['rec_intents']} | primary={c['rec_primary']} | esc={c['rec_escalate']} ({c['rec_escalation_reason']})")
    print(f"   Notes: {c['rec_notes']}")
    print()
