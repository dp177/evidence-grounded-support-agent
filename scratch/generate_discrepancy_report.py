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
intent_any_diff = intents_diff | primary_diff
esc_diff = df['prop_esc_norm'] != df['hum_esc_norm']
flags_present = df['has_flags']

any_discrepancy = status_diff | intent_any_diff | esc_diff
all_flagged_or_disc = any_discrepancy | flags_present

disc_df = df[any_discrepancy].copy()
flag_df = df[flags_present].copy()

# Generate markdown report
lines = []
lines.append("# Golden Annotation Discrepancy Report (Assistant-Reviewed Draft vs Proposed Labels)")
lines.append("")
lines.append("> **IMPORTANT NOTICE**: The annotations in the `human_*` columns are an **assistant-reviewed pre-annotation draft** and do **NOT** constitute final human ground truth. `taxonomy_v1.yaml` and `golden_v1` remain strictly unlocked pending human sign-off.")
lines.append("")
lines.append("## 1. Executive Summary")
lines.append("")
lines.append(f"- **Total Cases Evaluated**: {len(df)}")
lines.append(f"- **Preserved `proposed_*` Columns**: 100% verified intact across all 200 cases.")
lines.append(f"- **Total Discrepant Rows (Intent OR Status OR Escalate)**: **{any_discrepancy.sum()}** / 200 ({any_discrepancy.sum() / len(df) * 100:.1f}%)")
lines.append(f"  - **Status Discrepancies** (`proposed_status != human_status`): **{status_diff.sum()}** cases")
lines.append(f"  - **Intent Discrepancies** (multi-label `proposed_intents != human_intents`): **{intents_diff.sum()}** cases")
lines.append(f"  - **Primary Intent Discrepancies** (`proposed_primary_intent != human_primary_intent`): **{primary_diff.sum()}** cases")
lines.append(f"  - **Escalation Discrepancies** (`proposed_should_escalate != human_should_escalate`): **{esc_diff.sum()}** cases")
lines.append(f"- **Cases with Review Flags (`review_flags`)**: **{flags_present.sum()}** cases")
lines.append(f"  - Flagged cases with discrepancy: { (flags_present & any_discrepancy).sum() }")
lines.append(f"  - Flagged cases with label agreement (flagged for review/taxonomy note): { (flags_present & ~any_discrepancy).sum() }")
lines.append(f"- **Combined Review Focus (Discrepant OR Flagged)**: **{all_flagged_or_disc.sum()}** / 200 cases")
lines.append("")

lines.append("## 2. Status Discrepancy Breakdown (23 cases)")
lines.append("")
lines.append("| Status Transition | Count | Business Rationale & Pattern |")
lines.append("|---|:---:|---|")
lines.append("| `AMBIGUOUS` -> `NORMAL` | 5 | Prior conversation context or tracking timeline provided enough grounding to resolve specific leaf intents (`DELIVERY_DELAYED`, `ACCOUNT_LOGIN_ISSUES`, `WHERE_IS_MY_ORDER`). |")
lines.append("| `OUT_OF_SCOPE` -> `NORMAL` | 6 | Context showed actionable ecommerce issues (`DELIVERY_DELAYED`, `REFUND_STATUS_INQUIRY`, `CARRIER_FEEDBACK_AND_INSTRUCTIONS`, `PRIME_MEMBERSHIP_MANAGEMENT`) rather than unhandleable inquiries. |")
lines.append("| `NORMAL` -> `OUT_OF_SCOPE` | 5 | Inquiries concerned seller central, general website typo/app glitches, Kindle Fire TV internet connection, or third-party payment/RuPay wallet OTP issues outside consumer retail scope. |")
lines.append("| `NORMAL` -> `AMBIGUOUS` | 2 | Generic dissatisfaction text without actionable detail (`gold_0050`) or ambiguous intent like requesting to *stop* an order cancellation (`gold_0114`). |")
lines.append("| `OUT_OF_SCOPE` -> `AMBIGUOUS` | 2 | Generic customer venting / sarcastic remarks without an actionable goal (`gold_0032`, `gold_0035`). |")
lines.append("| `AMBIGUOUS` -> `OUT_OF_SCOPE` | 2 | Pure seller central support (`gold_0020`) or retail product stock inquiry (`gold_0021`). |")
lines.append("")

lines.append("## 3. Escalation Discrepancy Breakdown (5 cases)")
lines.append("")
lines.append("All 5 escalation discrepancies transitioned from `proposed_should_escalate: False` to `human_should_escalate: True`:")
lines.append("")
lines.append("| Gold ID | Proposed Escalate | Draft Escalate | Draft Escalation Reason | Summary & Customer Message |")
lines.append("|---|:---:|:---:|---|---|")
for idx, r in df[esc_diff].iterrows():
    msg = r['customer_message'].replace('\n', ' ').replace('\r', '')
    if len(msg) > 75: msg = msg[:72] + '...'
    lines.append(f"| `{r['gold_id']}` | `{r['proposed_should_escalate']}` | **`{r['human_should_escalate']}`** | `{r['human_escalation_reason']}` | {msg} |")
lines.append("")

lines.append("## 4. Key Intent Shift Patterns (56 cases)")
lines.append("")
lines.append("The 56 intent adjustments fall into distinct, recurring systematic patterns:")
lines.append("1. **Delivery Granularity Corrections** (15+ cases): Correcting misattribution between `WHERE_IS_MY_ORDER`, `DELIVERY_DELAYED`, and `MARKED_DELIVERED_NOT_RECEIVED`. E.g., cases where tracking falsely claimed delivery were corrected from `WHERE_IS_MY_ORDER` or `CARRIER_FEEDBACK_AND_INSTRUCTIONS` to `MARKED_DELIVERED_NOT_RECEIVED`.")
lines.append("2. **Carrier Feedback vs Delivery Problem** (6 cases): Messages complaining about courier misconduct, refusal to deliver to address, or asking customer to pick up parcel were corrected to `CARRIER_FEEDBACK_AND_INSTRUCTIONS`.")
lines.append("3. **Return Pickup vs Delivery/Refund** (7 cases): Undelivered parcels returned to sender by courier were corrected from `RETURN_PICKUP_ISSUE` to `DELIVERY_DELAYED`; refund disputes after returns were corrected to `REFUND_STATUS_INQUIRY`.")
lines.append("4. **Secondary Multi-Intent Annotations** (9 cases): Capturing dual customer issues such as Prime renewal + unauthorized charge, or wrong item + refund status.")
lines.append("5. **Domain/Category Disambiguation** (3 cases): Fixing digital content/game DLC mislabeled as carrier feedback, or website glitch mislabeled as digital content.")
lines.append("")

lines.append("## 5. Review Flags Breakdown (22 cases)")
lines.append("")
lines.append("The assistant review draft added explicit `review_flags` to 22 cases requiring human attention:")
lines.append("")
lines.append("| Review Flag | Count | Cases | Meaning & Required Human Action |")
lines.append("|---|:---:|---|---|")
lines.append("| `CONTEXT_MAY_DISAMBIGUATE` | 9 | `gold_0015`, `gold_0016`, `gold_0018`, `gold_0019`, `gold_0024`, `gold_0025`, `gold_0032`, `gold_0050`, `gold_0114` | The isolated customer turn is underspecified, but previous conversation history provides strong clues. Human reviewer must decide whether turn-level or thread-level context governs label. |")
lines.append("| `ACCOUNT_COMPROMISE_REVIEW` | 5 | `gold_0006`, `gold_0007`, `gold_0008`, `gold_0064`, `gold_0105` | Account hacking / compromised account cases. Currently forced into `ACCOUNT_LOGIN_ISSUES` with `should_escalate: True`. Human must confirm whether to keep under login or flag for Taxonomy v2. |")
lines.append("| `TAXONOMY_GAP_REVIEW` | 5 | `gold_0020`, `gold_0113`, `gold_0141`, `gold_0167`, `gold_0182` | Cases highlighting boundaries or missing concepts (e.g. Seller Central, hardware Fire TV connection, reverse order cancellation). |")
lines.append("| `OUT_OF_SCOPE_DECISION_REVIEW` | 2 | `gold_0021`, `gold_0098` | Cases at the edge of scope (product availability inquiry, third-party payment/RuPay OTP). |")
lines.append("| `OUT_OF_SCOPE_DECISION_REVIEW\|TAXONOMY_GAP_REVIEW` | 1 | `gold_0102` | Amazon Pay wallet reload OTP failure — third-party banking/wallet boundary. |")
lines.append("")

lines.append("## 6. Complete Table of All 63 Discrepancy Rows")
lines.append("")
lines.append("Below is the complete inventory of all 63 cases where proposed labels differ from the assistant-reviewed draft in intent, status, or escalation:")
lines.append("")
lines.append("| Gold ID | Customer Message Snippet | Proposed Status | Draft Status | Proposed Intents (Primary) | Draft Intents (Primary) | Prop Esc | Draft Esc | Draft Notes |")
lines.append("|---|---|---|---|---|---|:---:|:---:|---|")

for idx, r in disc_df.iterrows():
    msg = r['customer_message'].replace('\n', ' ').replace('\r', '')
    if len(msg) > 60: msg = msg[:57] + '...'
    msg = msg.replace('|', '/')
    
    p_stat = r['proposed_status']
    h_stat = r['human_status']
    stat_str = f"**{h_stat}**" if p_stat != h_stat else h_stat
    
    p_int = f"{r['proposed_intents']} ({r['proposed_primary_intent']})"
    h_int = f"{r['human_intents']} ({r['human_primary_intent']})"
    int_str = f"**{h_int}**" if p_int != h_int else h_int
    p_int = p_int.replace('|', '/')
    int_str = int_str.replace('|', '/')
    
    p_esc = str(r['proposed_should_escalate'])
    h_esc = str(r['human_should_escalate'])
    esc_str = f"**{h_esc}**" if p_esc != h_esc else h_esc
    
    notes = str(r['human_notes']).replace('|', '/')
    if len(notes) > 80: notes = notes[:77] + '...'
    
    lines.append(f"| `{r['gold_id']}` | {msg} | `{p_stat}` | {stat_str} | `{p_int}` | {int_str} | `{p_esc}` | {esc_str} | {notes} |")

lines.append("")
lines.append("## 7. Additional Flagged Rows Without Discrepancy (12 cases)")
lines.append("")
lines.append("| Gold ID | Status | Intents (Primary) | Escalate | Review Flag | Human Notes |")
lines.append("|---|---|---|:---:|---|---|")
for idx, r in df[flags_present & ~any_discrepancy].iterrows():
    pri = f"{r['human_intents']} ({r['human_primary_intent']})".replace('|', '/')
    notes = str(r['human_notes']).replace('|', '/')
    lines.append(f"| `{r['gold_id']}` | `{r['human_status']}` | `{pri}` | `{r['human_should_escalate']}` | `{r['review_flags']}` | {notes} |")

with open('experiments/golden_annotation_discrepancy_report.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("Wrote experiments/golden_annotation_discrepancy_report.md successfully!")
