import pandas as pd
import numpy as np

# Load files
df_adj = pd.read_csv('data/golden/golden_v1_assistant_adjudicated.csv')
df_prio = pd.read_csv('data/golden/golden_v1_priority_decisions.csv')

print(f"Loaded df_adj: {df_adj.shape}")
print(f"Loaded df_prio: {df_prio.shape}")

# Map prio columns to assistant recommendation columns
prio_map = {
    'human_status': 'assistant_status_recommendation',
    'human_areas': 'assistant_areas_recommendation',
    'human_intents': 'assistant_intents_recommendation',
    'human_primary_intent': 'assistant_primary_intent_recommendation',
    'human_states': 'assistant_states_recommendation',
    'human_should_escalate': 'assistant_should_escalate_recommendation',
    'human_escalation_reason': 'assistant_escalation_reason_recommendation',
    'human_notes': 'assistant_notes_recommendation',
}

# Sync prio recommendations into df_adj for the 24 priority cases
for idx, row in df_prio.iterrows():
    gid = row['gold_id']
    match_mask = df_adj['gold_id'] == gid
    for p_col, a_col in prio_map.items():
        df_adj.loc[match_mask, a_col] = row[p_col]

# Save updated df_adj preserving proposed_* and auditable assistant_*_recommendation
df_adj.to_csv('data/golden/golden_v1_assistant_adjudicated.csv', index=False)
print("Updated data/golden/golden_v1_assistant_adjudicated.csv")

# TASK 2: Create golden_v1_human_signoff.csv
signoff_cols = [
    'gold_id',
    'case_id',
    'conversation_id',
    'customer_message',
    'context',
    'assistant_status_recommendation',
    'assistant_areas_recommendation',
    'assistant_intents_recommendation',
    'assistant_primary_intent_recommendation',
    'assistant_states_recommendation',
    'assistant_should_escalate_recommendation',
    'assistant_escalation_reason_recommendation',
    'assistant_notes_recommendation',
]

df_signoff = df_adj[signoff_cols].copy()
df_signoff['human_decision'] = ""
df_signoff['human_override_reason'] = ""
df_signoff['human_notes'] = ""

df_signoff.to_csv('data/golden/golden_v1_human_signoff.csv', index=False)
print(f"Created data/golden/golden_v1_human_signoff.csv: shape {df_signoff.shape}")
print("Columns:", df_signoff.columns.tolist())

# TASK 3: Create priority_human_signoff.csv
prio_signoff_cols = [
    'gold_id',
    'case_id',
    'customer_message',
    'context',
    'assistant_status_recommendation',
    'assistant_areas_recommendation',
    'assistant_intents_recommendation',
    'assistant_primary_intent_recommendation',
    'assistant_states_recommendation',
    'assistant_should_escalate_recommendation',
    'assistant_escalation_reason_recommendation',
    'assistant_notes_recommendation',
]

# Filter for the 24 priority cases in the order of df_prio
prio_gids = df_prio['gold_id'].tolist()
df_prio_signoff = df_adj[df_adj['gold_id'].isin(prio_gids)][prio_signoff_cols].copy()
# Reorder to match df_prio order
df_prio_signoff['sort_idx'] = df_prio_signoff['gold_id'].apply(lambda g: prio_gids.index(g))
df_prio_signoff = df_prio_signoff.sort_values('sort_idx').drop(columns=['sort_idx'])

df_prio_signoff['human_decision'] = ""
df_prio_signoff['human_override_reason'] = ""
df_prio_signoff['human_notes'] = ""

df_prio_signoff.to_csv('data/golden/priority_human_signoff.csv', index=False)
print(f"Created data/golden/priority_human_signoff.csv: shape {df_prio_signoff.shape}")
print("Columns:", df_prio_signoff.columns.tolist())
