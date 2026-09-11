import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/hum_review_details.json', encoding='utf-8') as f:
    hum = json.load(f)

print("=== ALL 10 HUMAN REVIEW CASES ===")
for i, c in enumerate(hum, 1):
    print(f"{i}. [{c['gold_id']}] {c['case_id']} | Flags: {c['review_flags']} | Outcome: {c['assistant_outcome']}")
    print(f"   Customer Msg: {c['customer_message']}")
    print(f"   Context Excerpt: {c['context'][:140]}...")
    print(f"   Proposed: status={c['proposed_status']} | intents={c['proposed_intents']} | primary={c['proposed_primary']} | esc={c['proposed_escalate']}")
    print(f"   Rec: status={c['rec_status']} | intents={c['rec_intents']} | primary={c['rec_primary']} | esc={c['rec_escalate']} ({c['rec_escalation_reason']})")
    print(f"   Notes: {c['rec_notes']}")
    print()
