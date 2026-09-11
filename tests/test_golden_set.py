"""Unit tests for the locked Golden Evaluation Set (data/golden/golden_set.jsonl)."""

import json
from pathlib import Path
import pytest
import yaml


@pytest.fixture(scope="module")
def golden_data():
    golden_path = Path(__file__).resolve().parent.parent / "data" / "golden" / "golden_set.jsonl"
    assert golden_path.exists(), f"Golden set not found at {golden_path}"
    cases = []
    with open(golden_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))
    return cases


@pytest.fixture(scope="module")
def taxonomy_meta():
    tax_path = Path(__file__).resolve().parent.parent / "configs" / "taxonomy_v1.yaml"
    assert tax_path.exists(), f"Taxonomy file not found at {tax_path}"
    with open(tax_path, encoding="utf-8") as f:
        tax = yaml.safe_load(f)
    intent_to_area = {}
    for area, data in tax.get("areas", {}).items():
        for intent in data.get("intents", []):
            intent_to_area[intent] = area
    return {
        "intent_to_area": intent_to_area,
        "frozen_intents": set(intent_to_area.keys()),
        "areas": set(tax.get("areas", {}).keys()),
        "statuses": set(tax.get("classification_status", [])),
    }


def test_golden_set_exact_count(golden_data):
    """Verify golden set contains exactly 200 cases."""
    assert len(golden_data) == 200, f"Expected exactly 200 cases, found {len(golden_data)}"


def test_golden_case_ids_unique(golden_data):
    """Verify all 200 case_ids are unique."""
    case_ids = [c["case_id"] for c in golden_data]
    assert len(case_ids) == len(set(case_ids)), "Duplicate case_id found in golden set"


def test_golden_conversation_ids_unique(golden_data):
    """Verify all 200 conversation_ids are unique (no conversation leakage)."""
    conv_ids = [str(c["conversation_id"]) for c in golden_data]
    assert len(conv_ids) == len(set(conv_ids)), "Duplicate conversation_id found in golden set"


def test_no_null_customer_messages(golden_data):
    """Verify all records contain non-empty customer messages and contexts."""
    for c in golden_data:
        msg = c.get("customer_message")
        assert msg is not None and len(str(msg).strip()) > 0, f"Record {c.get('gold_id')} has empty message"
        ctx = c.get("context")
        assert ctx is not None and len(str(ctx).strip()) > 0, f"Record {c.get('gold_id')} has empty context"


def test_valid_taxonomy_references(golden_data, taxonomy_meta):
    """Verify every declared intent is one of the 14 frozen leaf intents and maps to the correct area."""
    frozen_intents = taxonomy_meta["frozen_intents"]
    intent_to_area = taxonomy_meta["intent_to_area"]

    for c in golden_data:
        status = c.get("classification_status")
        intents = c.get("intents", [])
        areas = c.get("areas", [])
        primary = c.get("primary_intent")

        if status == "NORMAL":
            assert len(intents) >= 1, f"Normal case {c['gold_id']} has no intents"
            for intent in intents:
                assert intent in frozen_intents, f"Invalid intent '{intent}' in {c['gold_id']}"
                expected_area = intent_to_area[intent]
                assert expected_area in areas, f"Area mismatch for intent '{intent}' in {c['gold_id']}"
            assert primary in intents, f"primary_intent '{primary}' not in intents list for {c['gold_id']}"
        else:
            assert len(intents) == 0, f"Non-normal case {c['gold_id']} should not have business intents"
            assert primary is None, f"Non-normal case {c['gold_id']} should have null primary_intent"


def test_multi_intent_invariants(golden_data):
    """Verify multi-intent cases have is_multi_intent=True and >=2 intents."""
    multi_cases = [c for c in golden_data if c["is_multi_intent"]]
    assert len(multi_cases) == 20, f"Expected exactly 20 multi-intent cases, found {len(multi_cases)}"

    for c in multi_cases:
        assert len(c["intents"]) >= 2, f"Multi-intent case {c['gold_id']} has < 2 intents"
        assert c["classification_status"] == "NORMAL"

    single_cases = [c for c in golden_data if c["classification_status"] == "NORMAL" and not c["is_multi_intent"]]
    for c in single_cases:
        assert len(c["intents"]) == 1, f"Single-intent case {c['gold_id']} has != 1 intent"


def test_classification_status_invariants(golden_data):
    """Verify classification status distribution and formatting."""
    statuses = [c["classification_status"] for c in golden_data]
    assert statuses.count("NORMAL") == 175
    assert statuses.count("AMBIGUOUS") == 15
    assert statuses.count("OUT_OF_SCOPE") == 10


def test_high_risk_escalation_invariants(golden_data):
    """Verify exactly 10 high-risk cases with should_escalate=True and valid reasons."""
    high_risk_cases = [c for c in golden_data if c["should_escalate"]]
    assert len(high_risk_cases) == 10, f"Expected 10 high-risk cases, found {len(high_risk_cases)}"
    for c in high_risk_cases:
        assert len(c["escalation_reason"]) >= 1, f"High-risk case {c['gold_id']} missing escalation reason"


def test_split_manifest_isolation(golden_data):
    """Verify split_manifest.json exists and confirms zero conversation leakage."""
    manifest_path = Path(__file__).resolve().parent.parent / "data" / "splits" / "split_manifest.json"
    assert manifest_path.exists(), f"Split manifest not found at {manifest_path}"

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    golden_convs = set(str(c["conversation_id"]) for c in golden_data)
    manifest_golden_convs = set(str(x) for x in manifest["golden_conversation_ids"])

    assert golden_convs == manifest_golden_convs, "Mismatch between golden set conv IDs and manifest"
    assert manifest.get("conversation_leakage_detected") is False, "Manifest reports conversation leakage"
    assert manifest.get("total_golden_conversations") == 200
