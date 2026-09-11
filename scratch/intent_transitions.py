import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('scratch/discrepancies.json', encoding='utf-8') as f:
    rows = json.load(f)

intent_diffs = [r for r in rows if r['intents_changed'] or r['primary_changed']]
print(f"Total intent discrepancies: {len(intent_diffs)}")

# Discrepancies by transition of primary intent
transitions = {}
for r in intent_diffs:
    p_pri = str(r['proposed_primary'])
    h_pri = str(r['human_primary'])
    pair = f"{p_pri} -> {h_pri}"
    transitions[pair] = transitions.get(pair, 0) + 1

sorted_trans = sorted(transitions.items(), key=lambda x: x[1], reverse=True)
print("\n--- Primary Intent Transitions ---")
for pair, cnt in sorted_trans:
    print(f"  {pair}: {cnt}")

print("\n--- All Intent Discrepancy Rows ---")
for r in intent_diffs:
    print(f"[{r['gold_id']}] Status: {r['proposed_status']} -> {r['human_status']}")
    print(f"   Proposed: intents=[{r['proposed_intents']}], pri={r['proposed_primary']}")
    print(f"   Draft:    intents=[{r['human_intents']}], pri={r['human_primary']}")
    print(f"   Notes:    {r['human_notes']}")
    print(f"   Msg:      {r['customer_message'][:80]}...")
    print()

