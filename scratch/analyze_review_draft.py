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

print("=== OVERALL COUNTS (200 ROWS) ===")
print(f"Total cases: {len(df)}")
print(f"Status differences: {status_diff.sum()}")
print(f"Intents differences: {intents_diff.sum()}")
print(f"Primary intent differences: {primary_diff.sum()}")
print(f"Either intent or primary differences: {(intents_diff | primary_diff).sum()}")
print(f"Escalation differences: {esc_diff.sum()}")
print(f"Rows with review_flags: {flags_present.sum()}")

any_discrepancy = intents_diff | primary_diff | status_diff | esc_diff
print(f"Rows with any discrepancy (intent OR status OR escalate): {any_discrepancy.sum()}")
all_flagged_or_disc = any_discrepancy | flags_present
print(f"Rows with discrepancy OR review_flags: {all_flagged_or_disc.sum()}")

print("\n=== REVIEW FLAGS BREAKDOWN ===")
flags_df = df[flags_present]
print(flags_df['review_flags'].value_counts())

print("\n=== ALL ROWS WITH REVIEW_FLAGS (22 rows) ===")
for idx, row in flags_df.iterrows():
    print(f"[{row['gold_id']}] Flag: {row['review_flags']}")
    print(f"  Status: {row['proposed_status']} -> {row['human_status']}")
    print(f"  Primary: {row['proposed_primary_intent']} -> {row['human_primary_intent']}")
    print(f"  Intents: {row['proposed_intents']} -> {row['human_intents']}")
    print(f"  Escalate: {row['proposed_should_escalate']} -> {row['human_should_escalate']}")
    print(f"  Notes: {row['human_notes']}")
    print()

