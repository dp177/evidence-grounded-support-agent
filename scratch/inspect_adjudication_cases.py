import pandas as pd
import json

df = pd.read_csv('data/golden/golden_v1_adjudication_review.csv')

print("All columns:")
for i, col in enumerate(df.columns):
    non_null = df[col].notna().sum()
    print(f"{i}: {col} ({non_null}/{len(df)} non-null)")

print("\n--- 14 TAXONOMY_REVIEW cases ---")
tax_cases = df[df['review_priority'] == 'TAXONOMY_REVIEW']
print(tax_cases[['gold_id', 'case_id', 'review_flags', 'assistant_outcome', 'human_status', 'assistant_status_recommendation', 'human_primary_intent', 'assistant_primary_intent_recommendation', 'human_action']].to_string())

print("\n--- 10 HUMAN_REVIEW cases ---")
hum_cases = df[df['review_priority'] == 'HUMAN_REVIEW']
print(hum_cases[['gold_id', 'case_id', 'review_flags', 'assistant_outcome', 'human_status', 'assistant_status_recommendation', 'human_primary_intent', 'assistant_primary_intent_recommendation', 'human_action']].to_string())
