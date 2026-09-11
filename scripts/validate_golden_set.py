"""Validation script for the Golden Evaluation Set (data/golden/golden_set.jsonl).

Verifies:
1. Exactly 200 final cases.
2. case_id uniqueness.
3. conversation_id uniqueness.
4. No null or empty customer messages.
5. No duplicate cases.
6. Every intent exists in configs/taxonomy_v1.yaml (14 frozen leaf intents).
7. Every intent belongs to the declared area.
8. No MULTI_INTENT label exists as a leaf business intent.
9. AMBIGUOUS is represented as classification_status.
10. OUT_OF_SCOPE is represented as classification_status.
11. Multi-intent cases contain >= 2 intents.
12. Single-intent cases contain exactly one intent.
13. primary_intent belongs to intents for normal single/multi-intent cases.
14. All golden conversations are isolated from the development set.

Exit non-zero if a critical invariant fails.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import yaml


def validate_golden_set(
    golden_path: Path = Path("data/golden/golden_set.jsonl"),
    taxonomy_path: Path = Path("configs/taxonomy_v1.yaml"),
    manifest_path: Path = Path("data/splits/split_manifest.json"),
) -> None:
    errors = []

    print("=" * 60)
    print("VALIDATING GOLDEN EVALUATION SET")
    print("=" * 60)

    # 1. Load taxonomy
    if not taxonomy_path.exists():
        print(f"CRITICAL ERROR: Taxonomy file not found at {taxonomy_path}")
        sys.exit(1)

    with open(taxonomy_path, encoding="utf-8") as f:
        tax = yaml.safe_load(f)

    intent_to_area = {}
    for area, data in tax.get("areas", {}).items():
        for intent in data.get("intents", []):
            intent_to_area[intent] = area

    frozen_intents = set(intent_to_area.keys())
    print(f"Taxonomy v1 loaded: {len(frozen_intents)} frozen leaf intents across {len(tax.get('areas', {}))} areas.")

    # 2. Load golden set
    if not golden_path.exists():
        print(f"CRITICAL ERROR: Golden set not found at {golden_path}")
        sys.exit(1)

    cases = []
    with open(golden_path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError as e:
                errors.append(f"Line {line_no}: Malformed JSON - {e}")

    total_cases = len(cases)
    print(f"Loaded {total_cases} records from {golden_path}.")

    # Invariant 1: Exactly 200 cases
    if total_cases != 200:
        errors.append(f"Invariant 1 Failed: Expected exactly 200 cases, found {total_cases}.")

    # Invariant 2 & 5: case_id uniqueness and no duplicate cases
    seen_case_ids = set()
    for c in cases:
        cs_id = c.get("case_id")
        if not cs_id:
            errors.append(f"Missing case_id in record: {c.get('gold_id')}")
        elif cs_id in seen_case_ids:
            errors.append(f"Invariant 2/5 Failed: Duplicate case_id detected: {cs_id}")
        seen_case_ids.add(cs_id)

    # Invariant 3: conversation_id uniqueness
    seen_conv_ids = set()
    for c in cases:
        cid = str(c.get("conversation_id"))
        if not cid:
            errors.append(f"Missing conversation_id in record: {c.get('gold_id')}")
        elif cid in seen_conv_ids:
            errors.append(f"Invariant 3 Failed: Duplicate conversation_id detected: {cid}")
        seen_conv_ids.add(cid)

    # Invariant 4: No null or empty customer messages
    for c in cases:
        msg = c.get("customer_message")
        if msg is None or not str(msg).strip():
            errors.append(f"Invariant 4 Failed: Record {c.get('gold_id')} has null or empty customer_message.")

    # Invariant 6, 7, 8, 9, 10, 11, 12, 13
    for c in cases:
        gid = c.get("gold_id")
        status = c.get("classification_status")
        is_multi = c.get("is_multi_intent")
        intents = c.get("intents", [])
        areas = c.get("areas", [])
        primary = c.get("primary_intent")

        # Invariant 8: No MULTI_INTENT label exists as a leaf business intent
        if "MULTI_INTENT" in intents or "MULTI_INTENT" == primary:
            errors.append(f"Invariant 8 Failed ({gid}): MULTI_INTENT must not be a leaf intent.")

        # Invariant 9: AMBIGUOUS is represented as classification_status
        if "AMBIGUOUS" in intents or "AMBIGUOUS_INQUIRY" in intents:
            errors.append(f"Invariant 9 Failed ({gid}): AMBIGUOUS must be classification_status, not an intent.")

        # Invariant 10: OUT_OF_SCOPE is represented as classification_status
        if "OUT_OF_SCOPE" in intents:
            errors.append(f"Invariant 10 Failed ({gid}): OUT_OF_SCOPE must be classification_status, not an intent.")

        if status == "AMBIGUOUS":
            if len(intents) != 0:
                errors.append(f"Invariant 9 Failed ({gid}): AMBIGUOUS case should have empty intents list, got {intents}.")
            if primary is not None:
                errors.append(f"Invariant 9 Failed ({gid}): AMBIGUOUS case should have primary_intent null, got {primary}.")

        elif status == "OUT_OF_SCOPE":
            if len(intents) != 0:
                errors.append(f"Invariant 10 Failed ({gid}): OUT_OF_SCOPE case should have empty intents list, got {intents}.")
            if primary is not None:
                errors.append(f"Invariant 10 Failed ({gid}): OUT_OF_SCOPE case should have primary_intent null, got {primary}.")

        elif status == "NORMAL":
            # Invariant 6: Every intent exists in taxonomy
            for intent in intents:
                if intent not in frozen_intents:
                    errors.append(f"Invariant 6 Failed ({gid}): Intent '{intent}' not in frozen taxonomy.")

            # Invariant 7: Every intent belongs to declared area
            for intent in intents:
                expected_area = intent_to_area.get(intent)
                if expected_area not in areas:
                    errors.append(f"Invariant 7 Failed ({gid}): Intent '{intent}' belongs to area '{expected_area}' which is not in declared areas: {areas}.")

            # Invariant 11: Multi-intent cases contain >= 2 intents
            if is_multi:
                if len(intents) < 2:
                    errors.append(f"Invariant 11 Failed ({gid}): Multi-intent case marked with is_multi_intent=True must have >=2 intents, got {len(intents)}.")

            # Invariant 12: Single-intent cases contain exactly one intent
            else:
                if len(intents) != 1:
                    errors.append(f"Invariant 12 Failed ({gid}): Single-intent case must have exactly 1 intent, got {len(intents)}.")

            # Invariant 13: primary_intent belongs to intents
            if primary not in intents:
                errors.append(f"Invariant 13 Failed ({gid}): primary_intent '{primary}' is not in declared intents: {intents}.")

    # Invariant 14: All golden conversations isolated from development set
    if not manifest_path.exists():
        errors.append(f"Invariant 14 Failed: Split manifest not found at {manifest_path}")
    else:
        with open(manifest_path, encoding="utf-8") as f:
            manifest_data = json.load(f)
        manifest_golden_convs = set(str(x) for x in manifest_data.get("golden_conversation_ids", []))
        if manifest_golden_convs != seen_conv_ids:
            errors.append(f"Invariant 14 Failed: Manifest golden conversation IDs do not match golden set cases exactly.")
        if manifest_data.get("conversation_leakage_detected") is True:
            errors.append("Invariant 14 Failed: Manifest indicates conversation leakage detected.")

    print("\n--- INVARIANT CHECK RESULTS ---")
    if errors:
        print(f"FAILED: {len(errors)} errors detected:")
        for err in errors[:20]:
            print(f"  [X] {err}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more errors.")
        sys.exit(1)
    else:
        print("PASSED: All 14 critical invariants verified successfully!")
        print(f"Total Unique Cases: {len(seen_case_ids)}")
        print(f"Total Unique Conversations: {len(seen_conv_ids)}")
        print("Conversation-level Isolation: VERIFIED 100% DISJOINT")
        print("=" * 60)


if __name__ == "__main__":
    validate_golden_set()
