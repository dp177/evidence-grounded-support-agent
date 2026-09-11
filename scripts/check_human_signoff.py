"""Automated validation script for Golden Evaluation Set v1 Human Sign-Off.

Checks data integrity, taxonomy compliance, and human adjudication readiness.
"""

from pathlib import Path
import sys
import pandas as pd
import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "configs" / "taxonomy_v1.yaml"
SIGNOFF_PATH = ROOT_DIR / "data" / "golden" / "golden_v1_human_signoff.csv"
PRIORITY_PATH = ROOT_DIR / "data" / "golden" / "priority_human_signoff.csv"


def load_taxonomy(config_path: Path):
    if not config_path.exists():
        raise FileNotFoundError(f"Taxonomy configuration missing at: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        tax = yaml.safe_load(f)

    areas = set(tax["areas"].keys())
    leaf_intents = set()
    for area, data in tax["areas"].items():
        for intent in data["intents"]:
            leaf_intents.add(intent)

    statuses = set(tax["classification_status"])
    states = set(tax["conversation_states"])
    return areas, leaf_intents, statuses, states


def is_blank(val) -> bool:
    if pd.isna(val):
        return True
    s = str(val).strip()
    return s == "" or s.lower() == "nan"


def validate_signoff():
    errors = []

    # 1. Load taxonomy
    try:
        areas, leaf_intents, statuses, states = load_taxonomy(CONFIG_PATH)
    except Exception as e:
        print(f"[FAIL] Error loading taxonomy: {e}")
        sys.exit(1)

    # 2. Check golden_v1_human_signoff.csv existence
    if not SIGNOFF_PATH.exists():
        print(f"[FAIL] Missing human sign-off file: {SIGNOFF_PATH}")
        sys.exit(1)

    df_signoff = pd.read_csv(SIGNOFF_PATH)

    # Check 1: Exactly 200 rows exist
    if len(df_signoff) != 200:
        errors.append(f"Expected exactly 200 rows in golden_v1_human_signoff.csv, found {len(df_signoff)}")

    # Check 2: gold_id is unique
    if df_signoff["gold_id"].nunique() != len(df_signoff):
        errors.append(f"gold_id contains duplicates ({df_signoff['gold_id'].nunique()} unique / {len(df_signoff)} total)")

    # Check 3: conversation_id is unique
    if df_signoff["conversation_id"].nunique() != len(df_signoff):
        errors.append(f"conversation_id contains duplicates ({df_signoff['conversation_id'].nunique()} unique / {len(df_signoff)} total)")

    # Check 4: all assistant recommendations use valid taxonomy labels
    for idx, row in df_signoff.iterrows():
        gid = row["gold_id"]
        status = str(row["assistant_status_recommendation"]).strip()
        if status not in statuses:
            errors.append(f"[{gid}] Invalid assistant status recommendation: '{status}'")

        if status == "NORMAL":
            primary = str(row["assistant_primary_intent_recommendation"]).strip()
            if primary not in leaf_intents:
                errors.append(f"[{gid}] Invalid assistant primary intent recommendation: '{primary}'")

            intents_str = str(row["assistant_intents_recommendation"]).strip()
            row_intents = [i.strip() for i in intents_str.split("|")]
            for it in row_intents:
                if it not in leaf_intents:
                    errors.append(f"[{gid}] Invalid assistant intent recommendation: '{it}'")
            if primary not in row_intents:
                errors.append(f"[{gid}] Assistant primary intent '{primary}' not in recommended intents '{row_intents}'")

            areas_str = str(row["assistant_areas_recommendation"]).strip()
            for ar in [a.strip() for a in areas_str.split("|")]:
                if ar not in areas:
                    errors.append(f"[{gid}] Invalid assistant area recommendation: '{ar}'")

        elif status in ["AMBIGUOUS", "OUT_OF_SCOPE"]:
            pri = str(row["assistant_primary_intent_recommendation"]).strip()
            if pri and pri != "nan" and pri != "":
                errors.append(f"[{gid}] Assistant recommendation with status '{status}' has business intent: '{pri}'")

        # Check state recommendation
        state_str = str(row["assistant_states_recommendation"]).strip()
        for st in [s.strip() for s in state_str.split("|")]:
            if st not in states:
                errors.append(f"[{gid}] Invalid assistant state recommendation: '{st}'")

    # Check 5: human fields are either completely blank OR validly populated
    human_decisions = df_signoff["human_decision"].apply(lambda v: "" if is_blank(v) else str(v).strip())
    non_blank_decisions = human_decisions[human_decisions != ""]

    all_human_blank = (len(non_blank_decisions) == 0)

    # Validate populated decisions
    for idx, row in df_signoff.iterrows():
        gid = row["gold_id"]
        dec = str(row["human_decision"]).strip()
        if not is_blank(dec):
            # Must be ACCEPT or OVERRIDE
            if dec not in ["ACCEPT", "OVERRIDE"]:
                errors.append(f"[{gid}] Invalid human_decision '{dec}', must be 'ACCEPT' or 'OVERRIDE'")

            # When OVERRIDE, validate override content if structured labels are supplied
            if dec == "OVERRIDE":
                ov_text = str(row.get("human_override_reason", "")).strip()
                if is_blank(ov_text):
                    errors.append(f"[{gid}] human_decision is 'OVERRIDE' but human_override_reason is empty")

                # Check rule 7: MULTI_INTENT cannot be used as a business intent
                if "MULTI_INTENT" in ov_text:
                    errors.append(f"[{gid}] MULTI_INTENT cannot be used as a business intent in override")

    # Check priority file if present
    if PRIORITY_PATH.exists():
        df_prio = pd.read_csv(PRIORITY_PATH)
        if len(df_prio) != 24:
            errors.append(f"Expected 24 rows in priority_human_signoff.csv, found {len(df_prio)}")

    # Summary Display
    print("=" * 60)
    print("GOLDEN EVALUATION SET V1 — HUMAN SIGN-OFF AUDIT")
    print("=" * 60)
    print(f"Total Rows Evaluated: {len(df_signoff)}")
    print(f"Unique gold_id: {df_signoff['gold_id'].nunique()}")
    print(f"Unique conversation_id: {df_signoff['conversation_id'].nunique()}")
    print(f"Priority Review Cases: {len(df_prio) if PRIORITY_PATH.exists() else 'N/A'}")
    print(f"Human Decisions Recorded: {len(non_blank_decisions)} / 200")
    print("-" * 60)

    if errors:
        print(f"[FAIL] Found {len(errors)} validation errors:")
        for err in errors[:20]:
            print(f"  - {err}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more errors.")
        sys.exit(1)

    print("[PASS] All structural and taxonomy validation rules satisfied.")
    print("[PASS] All 200 assistant recommendations use valid taxonomy labels.")

    if all_human_blank:
        print("-" * 60)
        print("HUMAN SIGN-OFF STATUS = PENDING")
        print("All human fields are currently blank as expected.")
        print("Golden v1 is waiting for human sign-off.")
        print("=" * 60)
        sys.exit(0)
    elif len(non_blank_decisions) == 200:
        print("-" * 60)
        print("HUMAN SIGN-OFF STATUS = APPROVED")
        print("All 200 human decisions recorded and verified.")
        print("=" * 60)
        sys.exit(0)
    else:
        print("-" * 60)
        print(f"HUMAN SIGN-OFF STATUS = PARTIALLY_COMPLETED ({len(non_blank_decisions)}/200)")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    validate_signoff()
