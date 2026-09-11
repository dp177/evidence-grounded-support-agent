import json

with open('scratch/discrepancies.json', encoding='utf-8') as f:
    rows = json.load(f)

only_flag = [r for r in rows if not (r['status_changed'] or r['intents_changed'] or r['primary_changed'] or r['escalate_changed'])]
print(f'Rows with ONLY review_flags and no discrepancy: {len(only_flag)}')
for r in only_flag:
    print(f"  {r['gold_id']}: {r['review_flags']} | {r['human_status']} | {r['human_primary']}")

disc_and_flag = [r for r in rows if (r['status_changed'] or r['intents_changed'] or r['primary_changed'] or r['escalate_changed']) and r['review_flags']]
print(f'\nRows with BOTH discrepancy AND review_flags: {len(disc_and_flag)}')
for r in disc_and_flag:
    chgs = []
    if r['status_changed']: chgs.append('status')
    if r['intents_changed'] or r['primary_changed']: chgs.append('intent')
    if r['escalate_changed']: chgs.append('escalate')
    print(f"  {r['gold_id']}: {r['review_flags']} | changes: {', '.join(chgs)}")

disc_no_flag = [r for r in rows if (r['status_changed'] or r['intents_changed'] or r['primary_changed'] or r['escalate_changed']) and not r['review_flags']]
print(f'\nRows with discrepancy but NO review_flags: {len(disc_no_flag)}')

