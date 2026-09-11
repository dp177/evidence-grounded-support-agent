import pandas as pd

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

print("=== DISCREPANCY SUMMARY ===")
print(f"Total Rows: {len(df)}")
print(f"Status Discrepancies (proposed_status != human_status): {status_diff.sum()}")
print(f"Intents Discrepancies (proposed_intents != human_intents): {intents_diff.sum()}")
print(f"Primary Intent Discrepancies (proposed_primary_intent != human_primary_intent): {primary_diff.sum()}")
print(f"Escalation Discrepancies (proposed_should_escalate != human_should_escalate): {esc_diff.sum()}")
print(f"Total Unique Discrepant Rows (where intent OR status OR escalate differs): {any_discrepancy.sum()}")
print(f"Rows with review_flags present: {flags_present.sum()}")

# Let's inspect the status transitions:
print("\n--- Status Transition Matrix ---")
print(pd.crosstab(df['prop_status_norm'], df['hum_status_norm'], margins=True))

# Let's inspect escalation differences
print("\n--- Escalation Discrepant Rows ---")
esc_rows = df[esc_diff]
for idx, r in esc_rows.iterrows():
    print(f"{r['gold_id']}: proposed_esc={r['proposed_should_escalate']} -> human_esc={r['human_should_escalate']} | reason={r['human_escalation_reason']} | notes={r['human_notes']}")

# Let's check status differences details
print("\n--- Status Discrepant Rows (23 rows) ---")
status_rows = df[status_diff]
for idx, r in status_rows.iterrows():
    print(f"{r['gold_id']}: {r['proposed_status']} -> {r['human_status']} | primary: {r['proposed_primary_intent']} -> {r['human_primary_intent']} | notes: {r['human_notes']}")

# Let's check intent differences where status didn't change (pure intent differences)
pure_intent_diff = (intents_diff | primary_diff) & (~status_diff)
print(f"\n--- Pure Intent Discrepancies (Status Unchanged) ({pure_intent_diff.sum()} rows) ---")
for idx, r in df[pure_intent_diff].iterrows():
    print(f"{r['gold_id']}: proposed=[{r['proposed_intents']}] (pri={r['proposed_primary_intent']}) -> human=[{r['human_intents']}] (pri={r['human_primary_intent']}) | notes: {r['human_notes']}")
