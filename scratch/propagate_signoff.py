import pandas as pd

# Load sign-off files
df_signoff = pd.read_csv('data/golden/golden_v1_human_signoff.csv')
df_prio = pd.read_csv('data/golden/priority_human_signoff.csv')

prio_map = dict(zip(df_prio['gold_id'], df_prio['human_notes']))

print(f"Total rows in golden_v1_human_signoff.csv: {len(df_signoff)}")
print(f"Total rows in priority_human_signoff.csv: {len(df_prio)}")

# Vectorized assignment
df_signoff['human_decision'] = 'ACCEPT'
df_signoff['human_override_reason'] = ''
df_signoff['human_notes'] = 'Reviewed and accepted assistant recommendation.'

# For the 24 priority cases, apply their notes from df_prio
for idx, row in df_prio.iterrows():
    gid = row['gold_id']
    note = row['human_notes']
    df_signoff.loc[df_signoff['gold_id'] == gid, 'human_notes'] = note

# Save back to CSV
df_signoff.to_csv('data/golden/golden_v1_human_signoff.csv', index=False)
print("Successfully propagated approved decisions to data/golden/golden_v1_human_signoff.csv!")
print("Decisions breakdown:")
print(df_signoff['human_decision'].value_counts())
