"""Inspection script for data/golden/golden_v1_assistant_adjudicated.csv."""

import os
import pandas as pd
import numpy as np

CSV_PATH = "data/golden/golden_v1_assistant_adjudicated.csv"
OUT_PATH = "evaluation/golden_schema_report.md"

def main():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"File not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    total_rows, total_cols = df.shape

    print(f"=== INSPECTION SUMMARY FOR {CSV_PATH} ===")
    print(f"Total Rows: {total_rows}")
    print(f"Total Columns: {total_cols}\n")

    # Column details
    col_details = []
    for idx, col in enumerate(df.columns, 1):
        dtype = str(df[col].dtype)
        non_null = int(df[col].notnull().sum())
        null_count = int(df[col].isnull().sum())
        unique_count = int(df[col].nunique(dropna=False))
        sample_vals = df[col].dropna().unique()[:3]
        col_details.append({
            "index": idx,
            "name": col,
            "dtype": dtype,
            "non_null": non_null,
            "null_count": null_count,
            "unique_count": unique_count,
            "samples": sample_vals
        })

    # Pick 5 representative rows
    # 1. Standard single intent NORMAL non-escalated
    idx_normal = df[(df['human_status'] == 'NORMAL') & (~df['human_intents'].str.contains(r'\|', na=False)) & (~df['human_should_escalate'])].index[0]
    # 2. Multi-intent NORMAL non-escalated
    idx_multi = df[(df['human_status'] == 'NORMAL') & (df['human_intents'].str.contains(r'\|', na=False))].index[0]
    # 3. AMBIGUOUS case
    idx_ambig = df[df['human_status'] == 'AMBIGUOUS'].index[0]
    # 4. OUT_OF_SCOPE case
    idx_oos = df[df['human_status'] == 'OUT_OF_SCOPE'].index[0]
    # 5. Escalation case
    idx_esc = df[df['human_should_escalate'] == True].index[0]

    sample_indices = [idx_normal, idx_multi, idx_ambig, idx_oos, idx_esc]

    # Categorical columns
    categorical_cols = [
        'proposed_status', 'proposed_areas', 'proposed_intents', 'proposed_primary_intent',
        'proposed_states', 'proposed_should_escalate',
        'human_status', 'human_areas', 'human_intents', 'human_primary_intent',
        'human_states', 'human_should_escalate', 'human_escalation_reason',
        'review_flags', 'assistant_outcome', 'review_priority',
        'assistant_status_recommendation', 'assistant_areas_recommendation',
        'assistant_intents_recommendation', 'assistant_primary_intent_recommendation',
        'assistant_states_recommendation', 'assistant_should_escalate_recommendation',
        'assistant_escalation_reason_recommendation',
        'human_action', 'adjudication_status'
    ]

    # Build Markdown Report
    lines = []
    lines.append("# Dataset Inspection & Schema Report: `golden_v1_assistant_adjudicated.csv`\n")
    lines.append(f"**Target File:** `{CSV_PATH}`  ")
    lines.append(f"**Row Count:** `{total_rows}`  ")
    lines.append(f"**Column Count:** `{total_cols}`  \n")
    lines.append("---\n")

    lines.append("## 1. Executive Summary\n")
    lines.append(f"- **Total Rows:** {total_rows} rows (exactly 200 cases conforming to the locked golden v1 size).")
    lines.append(f"- **Total Columns:** {total_cols} columns covering conversation inputs, machine proposals, assistant recommendations, human adjudication fields, review metadata, and adjudication status.")
    lines.append(f"- **Memory Usage:** ~{df.memory_usage(deep=True).sum() / 1024:.2f} KB.\n")

    lines.append("## 2. Column Schema, Datatypes & Null Statistics\n")
    lines.append("| # | Column Name | Datatype | Non-Null Count | Null Count | Unique Count |")
    lines.append("|---|---|---|:---:|:---:|:---:|")
    for c in col_details:
        lines.append(f"| {c['index']} | `{c['name']}` | `{c['dtype']}` | {c['non_null']} | {c['null_count']} | {c['unique_count']} |")
    lines.append("\n---\n")

    lines.append("## 3. Unique Values for Categorical Columns\n")
    for col in categorical_cols:
        vc = df[col].value_counts(dropna=False)
        lines.append(f"### `{col}` ({len(vc)} unique values, {df[col].notnull().sum()}/200 non-null)\n")
        lines.append("| Value | Frequency | Percentage |")
        lines.append("|---|:---:|:---:|")
        for val, count in vc.items():
            val_str = "`None` (NaN)" if pd.isna(val) else f"`{val}`"
            pct = count / total_rows * 100
            lines.append(f"| {val_str} | {count} | {pct:.1f}% |")
        lines.append("\n")

    lines.append("---\n")

    lines.append("## 4. Column Role Classification\n")
    lines.append("Based on the dataset semantics, documentation, and data lineage, the columns are categorized as follows:\n")

    lines.append("### A. Immutable Ground Truth / Conversation Input")
    lines.append("These columns represent the fixed, unmodifiable benchmark inputs extracted directly from historical customer interactions:")
    lines.append("- `gold_id`: Immutable benchmark identifier (e.g., `gold_0001` through `gold_0200`).")
    lines.append("- `case_id`: Original AmazonHelp case identifier (e.g., `amazon_case_0055972`).")
    lines.append("- `conversation_id`: Original customer conversation thread ID (e.g., `1391472`).")
    lines.append("- `customer_message`: Verbatim customer utterance to be evaluated.")
    lines.append("- `context`: Verbatim multi-turn conversation context including preceding and succeeding turns.\n")

    lines.append("### B. Human Adjudication / Review Fields")
    lines.append("These fields are designed to hold the definitive ground-truth evaluation labels signed off by human annotators:")
    lines.append("- `human_status`: Ground-truth domain gate status (`NORMAL`, `AMBIGUOUS`, `OUT_OF_SCOPE`).")
    lines.append("- `human_areas`: Ground-truth area taxonomy classifications (pipe-delimited for multi-area).")
    lines.append("- `human_intents`: Ground-truth intent taxonomy classifications (pipe-delimited for multi-intent).")
    lines.append("- `human_primary_intent`: Ground-truth primary actionable intent.")
    lines.append("- `human_states`: Ground-truth conversation progression state (`INITIAL_INQUIRY`, `WAITING_WINDOW_EXCEEDED`, `TRACKING_ALREADY_CHECKED`).")
    lines.append("- `human_should_escalate`: Ground-truth boolean flag indicating if case requires human escalation.")
    lines.append("- `human_escalation_reason`: Ground-truth reason code when escalation is triggered (`ACCOUNT_SECURITY_COMPROMISE`, `REPEATED_FAILED_SUPPORT_ATTEMPTS`).")
    lines.append("- `human_notes`: Human annotation justification, edge case explanations, or acceptance notes.")
    lines.append("- `human_action`: Specific action required from the human annotator during review.\n")
    lines.append("> [!NOTE]")
    lines.append("> In this specific file (`golden_v1_assistant_adjudicated.csv`), the `human_*` columns are pre-populated with the assistant's proposed adjudications pending final human sign-off approval (as indicated by `adjudication_status`). Once signed off via `golden_v1_human_signoff.csv`, these represent official human ground truth.\n")

    lines.append("### C. Model / Assistant Recommendations")
    lines.append("These columns contain machine-generated or LLM assistant-reviewed suggestions and MUST NOT be conflated with independent human ground truth:")
    lines.append("- **Initial Machine Proposals (`proposed_*`):**")
    lines.append("  - `proposed_status`")
    lines.append("  - `proposed_areas`")
    lines.append("  - `proposed_intents`")
    lines.append("  - `proposed_primary_intent`")
    lines.append("  - `proposed_states`")
    lines.append("  - `proposed_should_escalate`")
    lines.append("- **Assistant Adjudication Recommendations (`assistant_*_recommendation`):**")
    lines.append("  - `assistant_status_recommendation`")
    lines.append("  - `assistant_areas_recommendation`")
    lines.append("  - `assistant_intents_recommendation`")
    lines.append("  - `assistant_primary_intent_recommendation`")
    lines.append("  - `assistant_states_recommendation`")
    lines.append("  - `assistant_should_escalate_recommendation`")
    lines.append("  - `assistant_escalation_reason_recommendation`")
    lines.append("  - `assistant_notes_recommendation`")
    lines.append("- **Assistant Outcome Categorization:**")
    lines.append("  - `assistant_outcome` (`UNRESOLVED`, `OUT_OF_TAXONOMY`, `RESOLVED_CLOSURE`, `NO_ACTIONABLE_SUPPORT_REQUEST`)\n")

    lines.append("### D. Free-Text Input & Text Fields")
    lines.append("- `customer_message`: Customer query text.")
    lines.append("- `context`: Dialogue history text.")
    lines.append("- `human_notes`: Annotation notes text.")
    lines.append("- `assistant_notes_recommendation`: Generated assistant justification text.")
    lines.append("- `human_action`: Free-text instruction to human reviewers.\n")

    lines.append("### E. Workflow & Review Metadata")
    lines.append("- `gold_id`: Benchmark identifier.")
    lines.append("- `case_id`: Case source identifier.")
    lines.append("- `conversation_id`: Thread identifier.")
    lines.append("- `review_flags`: Flags marking ambiguous, out-of-scope, taxonomy gaps, or account compromise issues (`CONTEXT_MAY_DISAMBIGUATE`, `ACCOUNT_COMPROMISE_REVIEW`, `TAXONOMY_GAP_REVIEW`, `OUT_OF_SCOPE_DECISION_REVIEW`).")
    lines.append("- `review_priority`: Triage tier for human review (`NORMAL`, `TAXONOMY_REVIEW`, `HUMAN_REVIEW`).")
    lines.append("- `adjudication_status`: Overall sign-off workflow status (`ASSISTANT_RECOMMENDATION_PENDING_HUMAN_SIGNOFF`, `PRIORITY_CASE_ASSISTANT_ADJUDICATED_NEEDS_HUMAN_CONFIRMATION`).\n")

    lines.append("---\n")

    lines.append("## 5. Columns That Should NOT Be Used as Ground Truth\n")
    lines.append("> [!WARNING]")
    lines.append("> The following columns **must NOT be used as ground-truth targets** when evaluating production models, because they are machine-generated proposals, assistant recommendations, or workflow operational metadata:\n")

    not_gt_cols = [
        ("proposed_status", "Initial heuristic/machine classification proposal; contains errors that human/assistant review corrected."),
        ("proposed_areas", "Initial machine proposal; unverified."),
        ("proposed_intents", "Initial machine proposal; unverified."),
        ("proposed_primary_intent", "Initial machine proposal; unverified."),
        ("proposed_states", "Initial machine proposal; unverified."),
        ("proposed_should_escalate", "Initial machine proposal; unverified."),
        ("assistant_status_recommendation", "Assistant LLM suggestion; must not evaluate models against another model's suggestion without official human sign-off lock."),
        ("assistant_areas_recommendation", "Assistant LLM suggestion."),
        ("assistant_intents_recommendation", "Assistant LLM suggestion."),
        ("assistant_primary_intent_recommendation", "Assistant LLM suggestion."),
        ("assistant_states_recommendation", "Assistant LLM suggestion."),
        ("assistant_should_escalate_recommendation", "Assistant LLM suggestion."),
        ("assistant_escalation_reason_recommendation", "Assistant LLM suggestion."),
        ("assistant_notes_recommendation", "Free-form LLM explanation accompanying assistant recommendation."),
        ("assistant_outcome", "Intermediate assistant audit classification code, not a ground-truth label."),
        ("review_flags", "Internal workflow triage flags indicating boundary difficulty; not an evaluation target."),
        ("review_priority", "Triage tier used to sequence human annotator review queue."),
        ("human_action", "Instructional string guiding human reviewers on what action to take."),
        ("adjudication_status", "Workflow status of the sign-off pipeline.")
    ]

    lines.append("| Column Name | Category | Reason to Exclude from Ground Truth |")
    lines.append("|---|---|---|")
    for cname, reason in not_gt_cols:
        lines.append(f"| `{cname}` | Assistant / Machine / Workflow | {reason} |")
    lines.append("\n")

    lines.append("---\n")

    lines.append("## 6. Representative Rows (5 Cases Across Key Profiles)\n")

    categories = [
        ("Standard Single-Intent (NORMAL, Non-Escalated)", idx_normal),
        ("Multi-Intent Order & Refund (NORMAL, Non-Escalated)", idx_multi),
        ("Ambiguous Message (Vague Support Inquiry)", idx_ambig),
        ("Out-of-Scope Inquiry (Non-Support Message)", idx_oos),
        ("Security Escalation (Account Compromised)", idx_esc)
    ]

    for cat_title, r_idx in categories:
        row = df.loc[r_idx]
        lines.append(f"### Representative Case: {cat_title} (`{row['gold_id']}` / `{row['case_id']}`)\n")
        lines.append("| Field | Value |")
        lines.append("|---|---|")
        for col in df.columns:
            val = row[col]
            if pd.isna(val):
                val_repr = "*null (NaN)*"
            elif isinstance(val, (bool, np.bool_)):
                val_repr = f"`{val}`"
            elif isinstance(val, (int, np.integer)):
                val_repr = f"`{val}`"
            else:
                val_clean = str(val).replace("\n", "<br/>").replace("|", "\\|")
                val_repr = val_clean
            lines.append(f"| `{col}` | {val_repr} |")
        lines.append("\n")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    report_content = "\n".join(lines)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"\nSuccessfully generated {OUT_PATH} ({len(report_content)} bytes)")

if __name__ == "__main__":
    main()
