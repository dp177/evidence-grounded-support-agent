import pandas as pd

df_adj = pd.read_csv('data/golden/golden_v1_assistant_adjudicated.csv')
df_prio = pd.read_csv('data/golden/golden_v1_priority_decisions.csv')

merged = df_prio.merge(df_adj, on='gold_id', suffixes=('_prio', '_adj'))
print('Merged len:', len(merged))

cols_to_check = [
    ('human_status_prio', 'assistant_status_recommendation'),
    ('human_areas_prio', 'assistant_areas_recommendation'),
    ('human_intents_prio', 'assistant_intents_recommendation'),
    ('human_primary_intent_prio', 'assistant_primary_intent_recommendation'),
    ('human_states_prio', 'assistant_states_recommendation'),
    ('human_should_escalate_prio', 'assistant_should_escalate_recommendation'),
    ('human_escalation_reason_prio', 'assistant_escalation_reason_recommendation'),
    ('human_notes_prio', 'assistant_notes_recommendation'),
]

for p_col, a_col in cols_to_check:
    diff = (merged[p_col].fillna('') != merged[a_col].fillna('')).sum()
    print(f"{p_col} vs {a_col}: {diff} diffs")
    if diff > 0:
        for idx, r in merged[merged[p_col].fillna('') != merged[a_col].fillna('')].iterrows():
            print(f"  {r['gold_id']}: prio='{r[p_col]}' vs adj='{r[a_col]}'")
