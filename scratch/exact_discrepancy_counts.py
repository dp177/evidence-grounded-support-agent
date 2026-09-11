import json
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
intent_any_diff = intents_diff | primary_diff
esc_diff = df['prop_esc_norm'] != df['hum_esc_norm']
flags_present = df['has_flags']

union_discrepancies = status_diff | intents_diff | esc_diff
union_all_three_or_primary = status_diff | intent_any_diff | esc_diff

print("=== EXACT ROW COUNTS ===")
print(f"Status differences: {status_diff.sum()} cases")
print(f"  IDs: {df[status_diff]['gold_id'].tolist()}")
print(f"\nIntents differences (proposed_intents != human_intents): {intents_diff.sum()} cases")
print(f"  IDs: {df[intents_diff]['gold_id'].tolist()}")
print(f"\nPrimary intent differences: {primary_diff.sum()} cases")
print(f"  IDs: {df[primary_diff]['gold_id'].tolist()}")
print(f"\nEither proposed_intents != human_intents OR proposed_primary != human_primary: {intent_any_diff.sum()} cases")
print(f"  IDs: {df[intent_any_diff]['gold_id'].tolist()}")
print(f"\nEscalation differences (proposed_should_escalate != human_should_escalate): {esc_diff.sum()} cases")
print(f"  IDs: {df[esc_diff]['gold_id'].tolist()}")
print(f"\nUnion (proposed_intents != human_intents OR status diff OR esc diff): {union_discrepancies.sum()} cases")
print(f"Union including primary_intent diff: {union_all_three_or_primary.sum()} cases")

# Let's check which row is in primary_diff but not in intents_diff, if any
diff_pri_not_int = primary_diff & (~intents_diff)
if diff_pri_not_int.sum() > 0:
    print(f"\nIn primary_diff but NOT intents_diff: {df[diff_pri_not_int][['gold_id', 'proposed_intents', 'human_intents', 'proposed_primary_intent', 'human_primary_intent']]}")

diff_int_not_pri = intents_diff & (~primary_diff)
if diff_int_not_pri.sum() > 0:
    print(f"\nIn intents_diff but NOT primary_diff: {df[diff_int_not_pri][['gold_id', 'proposed_intents', 'human_intents', 'proposed_primary_intent', 'human_primary_intent']]}")

