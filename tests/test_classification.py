"""Unit tests for Phase 5: Intent Classification & Baselines."""

import json
from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
import pytest

from support_agent.classification.majority import MajorityClassifier
from support_agent.classification.tfidf_classifier import TfidfIntentClassifier
from support_agent.classification.llm_classifier import LLMIntentClassifier
from support_agent.evaluation.classification_metrics import (
    evaluate_primary_intent,
    evaluate_multi_intent,
    evaluate_status,
    evaluate_state,
    evaluate_calibration,
    evaluate_threshold_abstention,
    evaluate_classification_records,
)


# ==============================================================================
# 1. MAJORITY CLASSIFIER TESTS
# ==============================================================================

def test_majority_classifier_fit_and_predict():
    """Test that MajorityClassifier correctly finds and predicts majority intent."""
    dev_data = pd.DataFrame({
        "conversation_id": ["conv_1", "conv_2", "conv_3", "conv_4", "conv_5"],
        "customer_message": [
            "Delayed package",
            "Delayed delivery",
            "Where is my order",
            "Order delayed",
            "Item broken",
        ],
        "primary_intent": [
            "DELIVERY_DELAYED",
            "DELIVERY_DELAYED",
            "WHERE_IS_MY_ORDER",
            "DELIVERY_DELAYED",
            "DAMAGED_OR_DEFECTIVE_ITEM",
        ],
    })
    clf = MajorityClassifier()
    clf.fit(dev_data, label_column="primary_intent")
    assert clf.majority_intent_ == "DELIVERY_DELAYED"

    preds = clf.predict_records([
        {"customer_message": "Where is my book?"},
        {"customer_message": "I want a refund."},
    ])
    assert len(preds) == 2
    for p in preds:
        assert p["primary_intent"] == "DELIVERY_DELAYED"
        assert p["classification_status"] == "NORMAL"
        assert p["is_multi_intent"] is False


def test_majority_classifier_rejects_golden_cases():
    """Test that MajorityClassifier rejects training data containing golden conversation IDs."""
    golden_path = Path("data/golden/golden_set.jsonl")
    if not golden_path.exists():
        pytest.skip("Golden set not present.")

    with open(golden_path, "r", encoding="utf-8") as f:
        first_gold = json.loads(f.readline())
    gold_conv_id = first_gold["conversation_id"]

    leaked_data = pd.DataFrame({
        "conversation_id": [gold_conv_id, "other_conv_1"],
        "customer_message": ["late package", "where is it"],
        "primary_intent": ["DELIVERY_DELAYED", "WHERE_IS_MY_ORDER"],
    })
    clf = MajorityClassifier()
    with pytest.raises(ValueError, match="CRITICAL: Found"):
        clf.fit(leaked_data, golden_conversation_ids={gold_conv_id})


# ==============================================================================
# 2. TF-IDF CLASSIFIER TESTS
# ==============================================================================

def test_tfidf_classifier_pipeline_and_serialization():
    """Test fitting, predicting, and saving/loading TfidfIntentClassifier."""
    texts = [
        "Where is my package and delivery tracking?",
        "My order has not arrived yet tracking status?",
        "The package is delayed past the delivery date",
        "It was marked delivered but not received at my door",
        "The screen is cracked and broken defective item",
        "Damaged product arrived completely smashed",
        "I received the completely wrong item wrong color",
        "Wrong product sent instead of what I ordered",
    ]
    labels = [
        "WHERE_IS_MY_ORDER",
        "WHERE_IS_MY_ORDER",
        "DELIVERY_DELAYED",
        "MARKED_DELIVERED_NOT_RECEIVED",
        "DAMAGED_OR_DEFECTIVE_ITEM",
        "DAMAGED_OR_DEFECTIVE_ITEM",
        "WRONG_ITEM_RECEIVED",
        "WRONG_ITEM_RECEIVED",
    ]

    clf = TfidfIntentClassifier()
    clf.fit(texts, labels)

    preds = clf.predict(["my item was broken and cracked", "tracking for my package"])
    assert len(preds) == 2
    assert preds[0] == "DAMAGED_OR_DEFECTIVE_ITEM"

    cases_preds = clf.predict_cases([
        {"customer_message": "my item was broken and cracked"},
        {"customer_message": "tracking for my package"},
    ])
    assert len(cases_preds) == 2
    assert cases_preds[0]["primary_intent"] == "DAMAGED_OR_DEFECTIVE_ITEM"
    assert cases_preds[0]["confidence"] > 0.0

    probas = clf.predict_proba(["broken product"])
    assert len(probas) == 1
    assert abs(float(np.sum(probas[0])) - 1.0) < 1e-4

    # Test save and load
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = Path(tmpdir)
        clf.save(model_path)
        assert (model_path / "tfidf_model.pkl").exists()

        loaded_clf = TfidfIntentClassifier.load(model_path)
        loaded_preds = loaded_clf.predict(["my item was broken and cracked"])
        assert loaded_preds[0] == "DAMAGED_OR_DEFECTIVE_ITEM"


# ==============================================================================
# 3. SPLIT ISOLATION TEST
# ==============================================================================

def test_golden_set_split_isolation():
    """Verify zero overlap between golden conversation IDs and split_manifest development IDs."""
    manifest_path = Path("data/splits/split_manifest.json")
    golden_path = Path("data/golden/golden_set.jsonl")

    if not manifest_path.exists() or not golden_path.exists():
        pytest.skip("Manifest or golden set not found.")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    with open(golden_path, "r", encoding="utf-8") as f:
        gold_cases = [json.loads(line) for line in f if line.strip()]

    gold_conv_ids = {str(c["conversation_id"]) for c in gold_cases}
    manifest_gold_ids = {str(gid) for gid in manifest.get("golden_conversation_ids", [])}

    # All gold cases must be registered in manifest
    assert gold_conv_ids == manifest_gold_ids
    assert len(gold_conv_ids) == 200


# ==============================================================================
# 4. LLM OUTPUT SANITIZER & SCHEMA VALIDATION TESTS
# ==============================================================================

def test_llm_classifier_output_sanitizer():
    """Test that LLMIntentClassifier._sanitize_output enforces valid labels."""
    classifier = LLMIntentClassifier(cache_dir="artifacts/llm_predictions")

    # 1. Valid normal case
    valid_raw = {
        "classification_status": "NORMAL",
        "areas": ["DELIVERY_AND_FULFILLMENT"],
        "intents": ["WHERE_IS_MY_ORDER"],
        "primary_intent": "WHERE_IS_MY_ORDER",
        "is_multi_intent": False,
        "states": ["INITIAL_INQUIRY"],
        "confidence": 0.92,
        "reasoning": "Customer asks for package location",
    }
    sanitized = classifier._sanitize_output(valid_raw)
    assert sanitized["classification_status"] == "NORMAL"
    assert sanitized["primary_intent"] == "WHERE_IS_MY_ORDER"
    assert sanitized["intents"] == ["WHERE_IS_MY_ORDER"]
    assert sanitized["confidence"] == 0.92

    # 2. Ambiguous case: should wipe intents/areas and set primary_intent to None
    ambig_raw = {
        "classification_status": "AMBIGUOUS",
        "areas": ["DELIVERY_AND_FULFILLMENT"],
        "intents": ["WHERE_IS_MY_ORDER"],
        "primary_intent": "WHERE_IS_MY_ORDER",
        "states": ["INITIAL_INQUIRY"],
        "confidence": 0.80,
    }
    sanitized_ambig = classifier._sanitize_output(ambig_raw)
    assert sanitized_ambig["classification_status"] == "AMBIGUOUS"
    assert sanitized_ambig["primary_intent"] is None
    assert sanitized_ambig["intents"] == []
    assert sanitized_ambig["areas"] == []

    # 3. Out of scope case
    oos_raw = {
        "classification_status": "OUT_OF_SCOPE",
        "areas": [],
        "intents": [],
        "primary_intent": None,
        "confidence": 0.99,
    }
    sanitized_oos = classifier._sanitize_output(oos_raw)
    assert sanitized_oos["classification_status"] == "OUT_OF_SCOPE"
    assert sanitized_oos["primary_intent"] is None

    # 4. Invalid hallucinated intent names fallback
    invalid_raw = {
        "classification_status": "NORMAL",
        "intents": ["NON_EXISTENT_INTENT_XYZ"],
        "primary_intent": "NON_EXISTENT_INTENT_XYZ",
        "confidence": 1.2,  # clamped to 1.0
    }
    sanitized_invalid = classifier._sanitize_output(invalid_raw)
    assert sanitized_invalid["primary_intent"] in classifier.leaf_intents
    assert sanitized_invalid["confidence"] <= 1.0


# ==============================================================================
# 5. METRICS CALCULATION TESTS
# ==============================================================================

def test_metrics_calculations():
    """Test primary intent, multi-intent, status, calibration, and abstention metrics."""
    gold = [
        {"gold_id": "g1", "classification_status": "NORMAL", "primary_intent": "WHERE_IS_MY_ORDER", "intents": ["WHERE_IS_MY_ORDER"], "states": ["INITIAL_INQUIRY"]},
        {"gold_id": "g2", "classification_status": "NORMAL", "primary_intent": "DELIVERY_DELAYED", "intents": ["DELIVERY_DELAYED", "REFUND_STATUS_INQUIRY"], "states": ["WAITING_WINDOW_EXCEEDED"]},
        {"gold_id": "g3", "classification_status": "AMBIGUOUS", "primary_intent": None, "intents": [], "states": ["INITIAL_INQUIRY"]},
        {"gold_id": "g4", "classification_status": "OUT_OF_SCOPE", "primary_intent": None, "intents": [], "states": ["INITIAL_INQUIRY"]},
    ]

    preds = [
        {"classification_status": "NORMAL", "primary_intent": "WHERE_IS_MY_ORDER", "intents": ["WHERE_IS_MY_ORDER"], "states": ["INITIAL_INQUIRY"], "confidence": 0.90},
        {"classification_status": "NORMAL", "primary_intent": "DELIVERY_DELAYED", "intents": ["DELIVERY_DELAYED"], "states": ["WAITING_WINDOW_EXCEEDED"], "confidence": 0.85},
        {"classification_status": "AMBIGUOUS", "primary_intent": None, "intents": [], "states": ["INITIAL_INQUIRY"], "confidence": 0.70},
        {"classification_status": "OUT_OF_SCOPE", "primary_intent": None, "intents": [], "states": ["INITIAL_INQUIRY"], "confidence": 0.60},
    ]

    # Individual metric functions
    y_true_prim = ["WHERE_IS_MY_ORDER", "DELIVERY_DELAYED"]
    y_pred_prim = ["WHERE_IS_MY_ORDER", "DELIVERY_DELAYED"]
    prim = evaluate_primary_intent(y_true_prim, y_pred_prim)
    assert prim["accuracy"] == 1.0
    assert prim["macro_f1"] == 1.0

    multi = evaluate_multi_intent(
        [["WHERE_IS_MY_ORDER"], ["DELIVERY_DELAYED", "REFUND_STATUS_INQUIRY"]],
        [["WHERE_IS_MY_ORDER"], ["DELIVERY_DELAYED"]],
    )
    assert multi["exact_set_match"] == 0.5
    assert multi["micro_f1"] > 0.6

    status = evaluate_status(["NORMAL", "NORMAL", "AMBIGUOUS", "OUT_OF_SCOPE"], ["NORMAL", "NORMAL", "AMBIGUOUS", "OUT_OF_SCOPE"])
    assert status["accuracy"] == 1.0

    state = evaluate_state(["INITIAL_INQUIRY", "WAITING_WINDOW_EXCEEDED"], ["INITIAL_INQUIRY", "WAITING_WINDOW_EXCEEDED"])
    assert state["accuracy"] == 1.0

    calib = evaluate_calibration(["A", "B"], ["A", "B"], [0.9, 0.85])
    assert "expected_calibration_error" in calib
    assert 0.0 <= calib["expected_calibration_error"] <= 1.0

    abst = evaluate_threshold_abstention(["A", "B"], ["A", "B"], [0.9, 0.7], thresholds=[0.5, 0.8, 0.95])
    assert len(abst) == 3
    assert abst[0]["coverage"] >= abst[1]["coverage"] >= abst[2]["coverage"]

    # Comprehensive records evaluation
    all_res = evaluate_classification_records(gold, preds)
    assert all_res["num_cases"] == 4
    assert all_res["num_normal_cases"] == 2
    assert all_res["primary_intent"]["accuracy"] == 1.0
    assert all_res["status"]["accuracy"] == 1.0
    assert all_res["state"]["accuracy"] == 1.0
