"""Validation tests for frozen Taxonomy v1 configuration (configs/taxonomy_v1.yaml)."""

from pathlib import Path
import yaml
import pytest


@pytest.fixture
def taxonomy_config():
    config_path = Path(__file__).resolve().parent.parent / "configs" / "taxonomy_v1.yaml"
    assert config_path.exists(), f"Configuration file not found at {config_path}"
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data


def test_taxonomy_metadata(taxonomy_config):
    """Verify version, brand, and frozen status."""
    assert taxonomy_config.get("version") == "1.0"
    assert taxonomy_config.get("brand") == "AmazonHelp"
    assert taxonomy_config.get("status") == "FROZEN"


def test_leaf_intents_count_and_uniqueness(taxonomy_config):
    """Verify exactly 14 leaf business intents with no duplicates across all areas."""
    areas = taxonomy_config.get("areas", {})
    assert len(areas) == 6, f"Expected 6 business areas, found {len(areas)}"

    all_intents = []
    for area_name, area_data in areas.items():
        intents = area_data.get("intents", [])
        assert len(intents) > 0, f"Area {area_name} has no intents"
        for intent in intents:
            assert isinstance(intent, str), f"Intent {intent} is not a string"
            all_intents.append(intent)

    # Exactly 14 leaf business intents
    assert len(all_intents) == 14, f"Expected exactly 14 leaf intents, found {len(all_intents)}: {all_intents}"

    # No duplicate intent names
    unique_intents = set(all_intents)
    assert len(unique_intents) == 14, f"Duplicate intents detected: {len(all_intents) - len(unique_intents)}"


def test_non_intent_controls_not_in_leaf_intents(taxonomy_config):
    """Verify MULTI_INTENT, AMBIGUOUS, and OUT_OF_SCOPE are excluded from business intents."""
    areas = taxonomy_config.get("areas", {})
    all_intents = set()
    for area_data in areas.values():
        all_intents.update(area_data.get("intents", []))

    assert "MULTI_INTENT" not in all_intents
    assert "AMBIGUOUS_INQUIRY" not in all_intents
    assert "AMBIGUOUS" not in all_intents
    assert "OUT_OF_SCOPE" not in all_intents


def test_classification_status_exists(taxonomy_config):
    """Verify required classification status values."""
    statuses = taxonomy_config.get("classification_status", [])
    expected_statuses = {"NORMAL", "AMBIGUOUS", "OUT_OF_SCOPE"}
    assert expected_statuses.issubset(set(statuses)), f"Missing classification statuses: {expected_statuses - set(statuses)}"


def test_multi_intent_property_type(taxonomy_config):
    """Verify multi_intent is modeled as a boolean property."""
    multi_intent = taxonomy_config.get("multi_intent", {})
    assert multi_intent.get("type") == "boolean"


def test_conversation_states_exist(taxonomy_config):
    """Verify required conversation states exist."""
    states = taxonomy_config.get("conversation_states", [])
    expected_states = {
        "INITIAL_INQUIRY",
        "TRACKING_ALREADY_CHECKED",
        "CARRIER_ALREADY_CONTACTED",
        "DETAILS_ALREADY_PROVIDED",
        "WAITING_WINDOW_EXCEEDED",
    }
    assert expected_states.issubset(set(states)), f"Missing conversation states: {expected_states - set(states)}"


def test_outcomes_exist(taxonomy_config):
    """Verify required outcomes exist."""
    outcomes = taxonomy_config.get("outcomes", [])
    expected_outcomes = {
        "RESOLVED_CLOSURE",
        "ESCALATED_HUMAN_TIER2",
        "DEFLECTED_SELF_SERVICE",
        "CONCESSION_ISSUED",
        "ABANDONED_UNRESPONSIVE",
    }
    assert expected_outcomes.issubset(set(outcomes)), f"Missing outcomes: {expected_outcomes - set(outcomes)}"


def test_all_14_intents_have_definitions(taxonomy_config):
    """Verify all 14 leaf intents have concise, non-empty definitions."""
    areas = taxonomy_config.get("areas", {})
    all_intents = []
    for area_data in areas.values():
        all_intents.extend(area_data.get("intents", []))

    definitions = taxonomy_config.get("definitions", {})
    for intent in all_intents:
        assert intent in definitions, f"Intent {intent} is missing a definition"
        assert len(definitions[intent].strip()) > 10, f"Definition for {intent} is too short"
