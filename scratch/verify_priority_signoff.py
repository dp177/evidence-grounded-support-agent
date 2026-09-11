import pandas as pd

df_prio = pd.read_csv('data/golden/priority_human_signoff.csv')
df_orig = pd.read_csv('data/golden/golden_v1_priority_decisions.csv')

print(f"priority_human_signoff.csv row count: {len(df_prio)}")
print(f"golden_v1_priority_decisions.csv row count: {len(df_orig)}")

# 1. Verify 24 rows exist
assert len(df_prio) == 24, f"Expected 24 rows, found {len(df_prio)}"
print("[PASS] Exactly 24 rows exist.")

# 2. Verify all 24 human_decision values are ACCEPT
accept_count = (df_prio['human_decision'] == 'ACCEPT').sum()
print(f"ACCEPT count: {accept_count} / {len(df_prio)}")
assert accept_count == 24, f"Expected 24 ACCEPT decisions, found {accept_count}"
print("[PASS] All 24 human_decision values are ACCEPT.")

# 3. Verify no assistant recommendation columns were modified
# Compare df_prio with df_orig for the recommendation fields
cols_to_compare = [
    'gold_id',
    'human_status',
    'human_areas',
    'human_intents',
    'human_primary_intent',
    'human_states',
    'human_should_escalate',
    'human_escalation_reason'
]

mismatches = 0
for col in cols_to_compare:
    s_prio = df_prio[col].fillna('').astype(str).str.strip()
    s_orig = df_orig[col].fillna('').astype(str).str.strip()
    diff = (s_prio != s_orig).sum()
    if diff > 0:
        print(f"Mismatch in {col}: {diff} differences")
        mismatches += diff
    else:
        print(f"[PASS] Column '{col}' matches original recommendations perfectly.")

if mismatches == 0:
    print("[PASS] No assistant recommendation columns were modified!")
else:
    print(f"[FAIL] Found {mismatches} mismatches in recommendations.")
