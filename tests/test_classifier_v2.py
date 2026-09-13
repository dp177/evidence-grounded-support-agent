"""Unit tests for Phase 5.1: Classifier v2 Few-Shot Demonstration Architecture."""

import json
from pathlib import Path
import tempfile
import pytest
import yaml

from support_agent.classification.llm_classifier import (
    LLMIntentClassifier,
    validate_demo_isolation,
)


def test_demo_isolation_valid():
    """Verify that data/development/classification_demos.jsonl has zero golden overlap."""
    demos_path = Path("data/development/classification_demos.jsonl")
    manifest_path = Path("data/splits/split_manifest.json")
    assert demos_path.exists(), "Demonstrations file must exist"
    assert manifest_path.exists(), "Manifest file must exist"
    assert validate_demo_isolation(demos_path, manifest_path) is True


def test_demo_isolation_detects_leakage():
    """Verify that validate_demo_isolation raises ValueError when golden conversation IDs are present."""
    manifest_path = Path("data/splits/split_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    golden_conv = str(manifest["golden_conversation_ids"][0])

    with tempfile.TemporaryDirectory() as tmpdir:
        fake_demo = Path(tmpdir) / "leaked_demos.jsonl"
        fake_data = [
            {"demo_id": "demo_0001", "conversation_id": golden_conv, "intent": "DELIVERY_DELAYED"},
            {"demo_id": "demo_0002", "conversation_id": "clean_conv_999", "intent": "WHERE_IS_MY_ORDER"},
        ]
        with open(fake_demo, "w", encoding="utf-8") as f:
            for d in fake_data:
                f.write(json.dumps(d) + "\n")

        with pytest.raises(ValueError, match="CRITICAL LEAKAGE"):
            validate_demo_isolation(fake_demo, manifest_path)


def test_demo_schema_and_uniqueness():
    """Verify that all demonstrations contain required schema fields and have unique conversations."""
    demos_path = Path("data/development/classification_demos.jsonl")
    demos = []
    with open(demos_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                demos.append(json.loads(line))

    assert len(demos) >= 42, f"Expected at least 42 demonstrations, got {len(demos)}"

    demo_ids = set()
    conv_ids = set()
    required_fields = ["demo_id", "case_id", "conversation_id", "customer_message", "context", "selection_reason"]

    for d in demos:
        for rf in required_fields:
            assert rf in d, f"Missing field {rf} in {d}"
            assert str(d[rf]).strip(), f"Empty field {rf} in {d}"

        demo_ids.add(d["demo_id"])
        conv_ids.add(str(d["conversation_id"]))

    assert len(demo_ids) == len(demos), "Demonstration IDs must be strictly unique"
    assert len(conv_ids) == len(demos), "Conversation IDs must be strictly unique across demonstrations"


def test_demo_taxonomy_references():
    """Verify that all demonstrations reference legitimate Taxonomy v1.0 labels."""
    tax_path = Path("configs/taxonomy_v1.yaml")
    with open(tax_path, "r", encoding="utf-8") as f:
        tax = yaml.safe_load(f)

    valid_areas = set(tax.get("areas", {}).keys())
    valid_intents = set()
    for a, d in tax.get("areas", {}).items():
        valid_intents.update(d.get("intents", []))
    valid_statuses = set(tax.get("classification_status", ["NORMAL", "AMBIGUOUS", "OUT_OF_SCOPE"]))

    demos_path = Path("data/development/classification_demos.jsonl")
    with open(demos_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                status = d.get("classification_status", "NORMAL")
                assert status in valid_statuses, f"Invalid status: {status}"

                if status == "NORMAL":
                    if not d.get("is_multi_intent"):
                        assert d.get("intent") in valid_intents, f"Invalid intent: {d.get('intent')}"
                        assert d.get("area") in valid_areas, f"Invalid area: {d.get('area')}"
                    else:
                        for it in d.get("intents", []):
                            assert it in valid_intents, f"Invalid multi-intent: {it}"
                        assert d.get("primary_intent") in valid_intents


def test_prompt_v2_structure_and_anti_copying():
    """Verify that prompts/classification_v2.md exists and contains anti-copying rule and few-shot block."""
    prompt_file = Path("prompts/classification_v2.md")
    assert prompt_file.exists(), "prompts/classification_v2.md must exist"

    content = prompt_file.read_text(encoding="utf-8")
    assert "ANTI-COPYING RULE" in content
    assert "FEW-SHOT EXAMPLES" in content
    assert "END FEW-SHOT EXAMPLES" in content
    assert "DELIVERY_DELAYED" in content
    assert "WHERE_IS_MY_ORDER" in content
    assert "ACCOUNT_LOGIN_ISSUES" in content


def test_classifier_v2_config():
    """Verify configs/classifier_v2.yaml format and parameters."""
    cfg_file = Path("configs/classifier_v2.yaml")
    assert cfg_file.exists()

    with open(cfg_file, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    assert cfg.get("version") == "2.0"
    assert cfg.get("few_shot_enabled") is True
    assert cfg.get("demo_source") == "development_only"
    assert Path(cfg.get("prompt_file")).exists()
    assert Path(cfg.get("demos_file")).exists()


def test_classifier_v2_instantiation():
    """Verify that LLMIntentClassifier correctly loads prompts/classification_v2.md."""
    clf = LLMIntentClassifier(
        prompt_path="prompts/classification_v2.md",
        cache_dir="artifacts/llm_predictions_v2",
    )
    assert "FEW-SHOT EXAMPLES" in clf.system_prompt
    assert "ANTI-COPYING RULE" in clf.system_prompt
    assert clf.cache_dir == Path("artifacts/llm_predictions_v2")
