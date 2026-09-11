import pandas as pd
import json

df = pd.read_csv('data/golden/golden_annotation_review.csv')

def norm_str(v):
    if pd.isna(v):
        return ''
    return str(v).strip()

def norm_bool(v):
    if pd.isna(v):
        return None
    s = str(v).strip().lower()
    if s in ['true', '1', 't', 'yes']:
        return True
    if s in ['false', '0', 'f', 'no']:
        return False
    return None

df['prop_status_norm'] = df['proposed_status'].apply(norm_str)
df['hum_status_norm'] = df['human_status'].apply(norm_str)

df['prop_intents_norm'] = df['proposed_intents'].apply(norm_str)
df['hum_intents_norm'] = df['human_intents'].apply(norm_str)

df['prop_primary_norm'] = df['proposed_primary_intent'].apply(norm_str)
df['hum_primary_norm'] = df['human_primary_intent'].apply(norm_str)

df['prop_esc_norm'] = df['proposed_should_escalate'].apply(norm_bool)
df['hum_esc_norm'] = df['human_should_escalate'].apply(norm_bool)

df['has_flags'] = df['review_flags'].apply(lambda v: bool(norm_str(v)))

status_diff = df['prop_status_norm'] != df['hum_status_norm']
intents_diff = df['prop_intents_norm'] != df['hum_intents_norm']
primary_diff = df['prop_primary_norm'] != df['hum_primary_norm']
esc_diff = df['prop_esc_norm'] != df['hum_esc_norm']
flags_present = df['has_flags']

any_discrepancy = intents_diff | primary_diff | status_diff | esc_diff
all_flagged_or_disc = any_discrepancy | flags_present

discrepant_rows = []
for idx, r in df[all_flagged_or_disc].iterrows():
    discrepant_rows.append({
        'gold_id': r['gold_id'],
        'case_id': r['case_id'],
        'customer_message': r['customer_message'],
        'proposed_status': r['proposed_status'],
        'human_status': r['human_status'],
        'status_changed': r['prop_status_norm'] != r['hum_status_norm'],
        'proposed_intents': r['proposed_intents'],
        'human_intents': r['human_intents'],
        'intents_changed': r['prop_intents_norm'] != r['hum_intents_norm'],
        'proposed_primary': r['proposed_primary_intent'],
        'human_primary': r['human_primary_intent'],
        'primary_changed': r['prop_primary_norm'] != r['hum_primary_norm'],
        'proposed_escalate': r['proposed_should_escalate'],
        'human_escalate': r['human_should_escalate'],
        'escalate_changed': r['prop_esc_norm'] != r['hum_esc_norm'],
        'review_flags': r['review_flags'] if pd.notna(r['review_flags']) else '',
        'human_notes': r['human_notes'] if pd.notna(r['human_notes']) else '',
        'human_escalation_reason': r['human_escalation_reason'] if pd.notna(r['human_escalation_reason']) else ''
    })

with open('scratch/discrepancies.json', 'w', encoding='utf-8') as f:
    json.dump(discrepant_rows, f, indent=2)

print(f"Dumped {len(discrepant_rows)} rows to scratch/discrepancies.json")
