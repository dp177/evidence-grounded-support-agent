import pandas as pd
import json

df = pd.read_csv('data/golden/golden_v1_adjudication_review.csv')

def get_case_dict(r):
    return {
        'gold_id': r['gold_id'],
        'case_id': r['case_id'],
        'customer_message': r['customer_message'],
        'context': r['context'],
        'proposed_status': r['proposed_status'],
        'proposed_primary': r['proposed_primary_intent'],
        'proposed_intents': r['proposed_intents'],
        'proposed_escalate': r['proposed_should_escalate'],
        'rec_status': r['assistant_status_recommendation'],
        'rec_primary': r['assistant_primary_intent_recommendation'],
        'rec_intents': r['assistant_intents_recommendation'],
        'rec_escalate': r['assistant_should_escalate_recommendation'],
        'rec_escalation_reason': r['assistant_escalation_reason_recommendation'],
        'rec_notes': r['assistant_notes_recommendation'],
        'review_flags': r['review_flags'],
        'assistant_outcome': r['assistant_outcome'],
        'human_action': r['human_action']
    }

tax_cases = [get_case_dict(r) for _, r in df[df['review_priority'] == 'TAXONOMY_REVIEW'].iterrows()]
hum_cases = [get_case_dict(r) for _, r in df[df['review_priority'] == 'HUMAN_REVIEW'].iterrows()]

with open('scratch/tax_review_details.json', 'w', encoding='utf-8') as f:
    json.dump(tax_cases, f, indent=2)

with open('scratch/hum_review_details.json', 'w', encoding='utf-8') as f:
    json.dump(hum_cases, f, indent=2)

print(f"Saved {len(tax_cases)} tax cases and {len(hum_cases)} hum cases to scratch JSON files.")
