import pandas as pd

v1 = pd.read_csv('data/golden/golden_v1_assistant_adjudicated.csv')
v2 = pd.read_csv('data/golden/golden_v2_assistant_adjudicated.csv')
v3 = pd.read_csv('data/golden/golden_v3_assistant_adjudicated.csv')

def jaccard(s1, s2):
    w1 = set(s1.lower().split())
    w2 = set(s2.lower().split())
    return len(w1 & w2) / max(1, len(w1 | w2))

high_pairs = []
for idx, msg3 in enumerate(v3['customer_message'], 1):
    for prev_name, prev_df in [('V1', v1), ('V2', v2)]:
        for p_idx, msg_prev in enumerate(prev_df['customer_message'], 1):
            sim = jaccard(msg3, msg_prev)
            if sim >= 0.60:
                high_pairs.append((sim, f'V3_{idx}', msg3, f'{prev_name}_{p_idx}', msg_prev))

high_pairs.sort(reverse=True, key=lambda x: x[0])
print(f'Found {len(high_pairs)} pairs with Jaccard >= 0.60:')
for sim, v3_id, m3, prev_id, mp in high_pairs:
    print(f'[{sim:.3f}] {v3_id}: "{m3}" vs {prev_id}: "{mp}"')
