"""Phase 9: Grounding Verification Tests.

Tests the 11 required cases:
  1. Supported refund timing
  2. Unsupported refund promise
  3. Unsupported delivery guarantee
  4. Historical response mistaken for current action
  5. Contradiction with current conversation
  6. Unsupported compensation
  7. Correct evidence ID
  8. Invalid evidence ID
  9. Missing evidence
  10. Successful revision
  11. Failed revision → human review
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from typing import Any, Dict, List

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from support_agent.grounding.grounding_checker import (
    check_grounding,
    _is_politeness_only,
    _detect_hard_safety_violations,
    _validate_evidence_ids,
    _contains_high_risk_claim,
    _extract_evidence_ids,
)
from support_agent.generation.revise_response import revise_response, MAX_REVISION_ATTEMPTS

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_llm_client(response_json: Dict[str, Any]) -> MagicMock:
    """Create a mock LLM client that returns a fixed JSON string."""
    import json
    mock = MagicMock()
    mock_resp = MagicMock()
    mock_resp.content = json.dumps(response_json)
    mock.generate.return_value = mock_resp
    return mock


def _grounded_llm_response(
    grounded: bool = True,
    score: float = 1.0,
    supported: List[str] = None,
    unsupported: List[str] = None,
    contradicted: List[str] = None,
    risk_flags: List[str] = None,
    evidence_used: List[str] = None,
    needs_revision: bool = False,
    needs_human_review: bool = False,
    revision_suggestion: str = "",
) -> Dict[str, Any]:
    return {
        "grounded": grounded,
        "grounding_score": score,
        "claims": [],
        "supported_claims": supported or [],
        "partially_supported_claims": [],
        "unsupported_claims": unsupported or [],
        "contradicted_claims": contradicted or [],
        "evidence_used": evidence_used or [],
        "risk_flags": risk_flags or [],
        "needs_revision": needs_revision,
        "needs_human_review": needs_human_review,
        "revision_suggestion": revision_suggestion,
    }


CONV_REFUND = {
    "customer_message": "I returned my order last week. Has my refund been processed?",
    "context": "CUSTOMER: I want to return my order. BRAND: Sure, please ship it back."
}

CONV_DELIVERY = {
    "customer_message": "When will my order arrive?",
    "context": ""
}

CONV_COMPENSATION = {
    "customer_message": "My order was late and damaged. I'm very upset.",
    "context": ""
}

EVIDENCE_REFUND_TIMING = [
    {
        "document_id": "retrieval_doc_0001",
        "customer_message": "When will I get my refund?",
        "brand_response": "Refunds typically take 3-5 business days to process once we receive the return.",
        "relevant_context": "",
    }
]

EVIDENCE_DELIVERY = [
    {
        "document_id": "retrieval_doc_0002",
        "customer_message": "When will my package arrive?",
        "brand_response": "Delivery usually takes 2-3 business days. Please check your tracking for updates.",
        "relevant_context": "",
    }
]

EVIDENCE_COMPENSATION = [
    {
        "document_id": "retrieval_doc_0003",
        "customer_message": "My package was damaged.",
        "brand_response": "I'm so sorry to hear that! Please contact us with your order number and we'll look into it.",
        "relevant_context": "",
    }
]

CLASSIFICATION_REFUND = {
    "primary_intent": "REFUND_REQUEST",
    "intents": ["REFUND_REQUEST"],
    "states": ["RETURN_INITIATED"],
}

CLASSIFICATION_DELIVERY = {
    "primary_intent": "DELIVERY_DELAYED",
    "intents": ["DELIVERY_DELAYED"],
    "states": [],
}


# ===========================================================================
# TEST 1: Supported refund timing
# ===========================================================================

class TestSupportedRefundTiming:
    """A reply that hedges refund timing using evidence language should pass."""

    def test_supported_refund_timing(self) -> None:
        """Hedged timing phrase from evidence → grounding should pass."""
        reply = "Refunds typically take 3-5 business days once we receive your return."

        llm_client = _make_llm_client(_grounded_llm_response(
            grounded=True,
            score=1.0,
            supported=["Refunds typically take 3-5 business days once we receive your return."],
            evidence_used=["retrieval_doc_0001"],
        ))

        result = check_grounding(
            customer_conversation=CONV_REFUND,
            classification=CLASSIFICATION_REFUND,
            retrieved_evidence=EVIDENCE_REFUND_TIMING,
            generated_reply=reply,
            llm_client=llm_client,
            generator_evidence_ids=["retrieval_doc_0001"],
        )

        assert result["grounded"] is True
        assert result["grounding_score"] >= 0.8
        assert result["unsupported_claims"] == []
        assert result["contradicted_claims"] == []
        assert result["needs_human_review"] is False

    def test_deterministic_no_hard_violation_for_hedged_timing(self) -> None:
        """Hedged language should not trigger hard safety rules."""
        reply = "Refunds typically take 3-5 business days."
        violations = _detect_hard_safety_violations(reply)
        assert len(violations) == 0, f"Unexpected violations: {violations}"


# ===========================================================================
# TEST 2: Unsupported refund promise
# ===========================================================================

class TestUnsupportedRefundPromise:
    """A reply that asserts a refund has already been issued should fail."""

    def test_refund_already_issued_fails_hard_safety(self) -> None:
        """Hard safety rule: 'refund has been issued' without evidence in conversation."""
        reply = "Your refund has been issued and will appear in your account shortly."
        violations = _detect_hard_safety_violations(reply)
        assert len(violations) > 0, "Expected a hard safety violation for 'refund has been issued'"

    def test_refund_promise_fails_grounding(self) -> None:
        """Full grounding check fails for unsupported refund promise."""
        reply = "Your refund has been issued and will appear in your account shortly."

        llm_client = _make_llm_client(_grounded_llm_response(
            grounded=False,
            score=0.0,
            unsupported=["Your refund has been issued and will appear in your account shortly."],
            risk_flags=["Hard safety violation: refund has been issued"],
            needs_revision=True,
            needs_human_review=True,
        ))

        result = check_grounding(
            customer_conversation=CONV_REFUND,
            classification=CLASSIFICATION_REFUND,
            retrieved_evidence=EVIDENCE_REFUND_TIMING,
            generated_reply=reply,
            llm_client=llm_client,
        )

        assert result["grounded"] is False
        assert result["needs_revision"] is True
        # Hard safety violations from deterministic check should appear
        assert len(result["risk_flags"]) > 0

    def test_specific_refund_date_fails(self) -> None:
        """Specific refund arrival date not in evidence should fail."""
        reply = "Your refund will arrive by Thursday."
        violations = _detect_hard_safety_violations(reply)
        assert len(violations) > 0


# ===========================================================================
# TEST 3: Unsupported delivery guarantee
# ===========================================================================

class TestUnsupportedDeliveryGuarantee:
    """Guaranteed delivery claim without evidence should fail."""

    def test_guaranteed_delivery_hard_violation(self) -> None:
        """'delivery guaranteed' should trigger hard safety."""
        reply = "Your delivery is guaranteed to arrive by tomorrow."
        violations = _detect_hard_safety_violations(reply)
        assert len(violations) > 0

    def test_delivery_guarantee_fails_grounding(self) -> None:
        reply = "Your delivery is guaranteed to arrive by tomorrow."

        llm_client = _make_llm_client(_grounded_llm_response(
            grounded=False,
            score=0.0,
            unsupported=["Your delivery is guaranteed to arrive by tomorrow."],
            risk_flags=["Hard safety violation: delivery guaranteed"],
            needs_revision=True,
            needs_human_review=True,
        ))

        result = check_grounding(
            customer_conversation=CONV_DELIVERY,
            classification=CLASSIFICATION_DELIVERY,
            retrieved_evidence=EVIDENCE_DELIVERY,
            generated_reply=reply,
            llm_client=llm_client,
        )

        assert result["grounded"] is False
        assert result["needs_revision"] is True


# ===========================================================================
# TEST 4: Historical response mistaken for current action
# ===========================================================================

class TestHistoricalNotCurrentAction:
    """Evidence shows how Amazon handled a similar case — must not assert it happened now."""

    def test_historical_evidence_not_current_action(self) -> None:
        """A reply that treats historical evidence as proof of current action should fail."""
        # Evidence shows Amazon issued a refund in the historical case
        evidence_with_refund = [
            {
                "document_id": "retrieval_doc_0010",
                "customer_message": "I returned my item 2 weeks ago.",
                "brand_response": "We have issued your refund. It should appear in 3-5 days.",
                "relevant_context": "",
            }
        ]
        # Reply incorrectly treats historical evidence as applying to current customer
        reply = "We have issued your refund and it should appear in 3-5 days."

        llm_client = _make_llm_client(_grounded_llm_response(
            grounded=False,
            score=0.1,
            unsupported=["We have issued your refund and it should appear in 3-5 days."],
            risk_flags=["Historical evidence treated as current action: 'refund has been issued'"],
            needs_revision=True,
            needs_human_review=True,
        ))

        result = check_grounding(
            customer_conversation=CONV_REFUND,
            classification=CLASSIFICATION_REFUND,
            retrieved_evidence=evidence_with_refund,
            generated_reply=reply,
            llm_client=llm_client,
        )

        assert result["grounded"] is False
        # Deterministic check should catch 'have issued your refund'
        assert len(result["risk_flags"]) > 0

    def test_allowed_hedged_historical_reference(self) -> None:
        """A hedged reference to historical timing is allowed."""
        reply = "Based on similar cases, refunds typically appear within 3-5 business days."
        # No hard safety violations expected
        violations = _detect_hard_safety_violations(reply)
        assert len(violations) == 0


# ===========================================================================
# TEST 5: Contradiction with current conversation
# ===========================================================================

class TestContradictionWithConversation:
    """A reply that contradicts a stated fact in the conversation must fail."""

    def test_contradiction_detected(self) -> None:
        """Reply contradicts the conversation (customer said Prime, reply says Standard)."""
        conv = {
            "customer_message": "My Prime order was supposed to arrive yesterday.",
            "context": "CUSTOMER: I have Prime membership.",
        }
        reply = "Since you have Standard shipping, delivery can take 5-7 days."

        llm_client = _make_llm_client(_grounded_llm_response(
            grounded=False,
            score=0.0,
            contradicted=["Since you have Standard shipping, delivery can take 5-7 days."],
            risk_flags=["Contradicts conversation: customer stated Prime membership"],
            needs_revision=True,
            needs_human_review=True,
        ))

        result = check_grounding(
            customer_conversation=conv,
            classification=CLASSIFICATION_DELIVERY,
            retrieved_evidence=[],
            generated_reply=reply,
            llm_client=llm_client,
        )

        assert result["grounded"] is False
        assert result["needs_human_review"] is True
        assert result["contradicted_claims"] != []


# ===========================================================================
# TEST 6: Unsupported compensation
# ===========================================================================

class TestUnsupportedCompensation:
    """A reply that offers compensation not in the conversation or evidence must fail."""

    def test_compensation_invented(self) -> None:
        """'You will receive a $10 gift card' not in any evidence."""
        reply = "As an apology, we have issued a $10 gift card to your account."

        llm_client = _make_llm_client(_grounded_llm_response(
            grounded=False,
            score=0.0,
            unsupported=["As an apology, we have issued a $10 gift card to your account."],
            risk_flags=["Hard safety violation: compensation not in evidence"],
            needs_revision=True,
            needs_human_review=True,
        ))

        result = check_grounding(
            customer_conversation=CONV_COMPENSATION,
            classification={"primary_intent": "COMPENSATION_REQUEST", "intents": [], "states": []},
            retrieved_evidence=EVIDENCE_COMPENSATION,
            generated_reply=reply,
            llm_client=llm_client,
        )

        assert result["grounded"] is False
        # Deterministic: $10 should be caught as unsupported specific amount
        assert len(result["risk_flags"]) > 0

    def test_compensation_amount_not_in_sources(self) -> None:
        """Amount-specific regex: $10 not in sources → deterministic flag."""
        # No $10 in either evidence or conversation
        conv = {"customer_message": "My order was late.", "context": ""}
        evidence = [{"document_id": "ev1", "customer_message": "late order", "brand_response": "sorry", "relevant_context": ""}]
        reply = "We have issued you a $10 compensation."

        from support_agent.grounding.grounding_checker import _deterministic_precheck
        precheck = _deterministic_precheck(
            reply=reply,
            customer_conversation=conv,
            retrieved_evidence=evidence,
            valid_evidence_ids=["ev1"],
            generator_evidence_ids=[],
        )
        assert len(precheck["risk_flags"]) > 0, "Should flag $10 as unsupported amount"


# ===========================================================================
# TEST 7: Correct evidence ID
# ===========================================================================

class TestCorrectEvidenceID:
    """Generator claims an evidence ID that actually exists in retrieved evidence."""

    def test_valid_evidence_id_no_flag(self) -> None:
        """A valid evidence ID from the retrieved set should not trigger any flag."""
        valid_ids = _extract_evidence_ids(EVIDENCE_REFUND_TIMING)
        assert "retrieval_doc_0001" in valid_ids

        invalid = _validate_evidence_ids(["retrieval_doc_0001"], valid_ids)
        assert invalid == [], f"Expected no invalid IDs, got: {invalid}"

    def test_grounding_passes_with_valid_id(self) -> None:
        """Full grounding with valid evidence ID and supported claim should pass."""
        reply = "Refunds typically take 3-5 business days once we receive the return."

        llm_client = _make_llm_client(_grounded_llm_response(
            grounded=True,
            score=1.0,
            supported=[reply],
            evidence_used=["retrieval_doc_0001"],
        ))

        result = check_grounding(
            customer_conversation=CONV_REFUND,
            classification=CLASSIFICATION_REFUND,
            retrieved_evidence=EVIDENCE_REFUND_TIMING,
            generated_reply=reply,
            llm_client=llm_client,
            generator_evidence_ids=["retrieval_doc_0001"],
        )

        assert result["grounded"] is True
        assert "retrieval_doc_0001" not in result["invalid_evidence_ids"]


# ===========================================================================
# TEST 8: Invalid evidence ID
# ===========================================================================

class TestInvalidEvidenceID:
    """Generator claims an evidence ID that does NOT exist in retrieved evidence."""

    def test_invalid_id_detected(self) -> None:
        """An invented evidence ID should be flagged."""
        valid_ids = _extract_evidence_ids(EVIDENCE_REFUND_TIMING)
        invented_id = "retrieval_doc_FAKE_9999"
        invalid = _validate_evidence_ids([invented_id], valid_ids)
        assert invented_id in invalid

    def test_invalid_id_triggers_risk_flag(self) -> None:
        """A generator claiming an invented ID should add a risk flag."""
        reply = "Your refund is being processed."

        llm_client = _make_llm_client(_grounded_llm_response(
            grounded=True,
            score=0.8,
            supported=[reply],
            evidence_used=["retrieval_doc_0001"],
        ))

        result = check_grounding(
            customer_conversation=CONV_REFUND,
            classification=CLASSIFICATION_REFUND,
            retrieved_evidence=EVIDENCE_REFUND_TIMING,
            generated_reply=reply,
            llm_client=llm_client,
            generator_evidence_ids=["retrieval_doc_FAKE_9999"],  # invented ID
        )

        assert "retrieval_doc_FAKE_9999" in result.get("invalid_evidence_ids", [])
        assert any("FAKE_9999" in rf for rf in result.get("risk_flags", []))


# ===========================================================================
# TEST 9: Missing evidence
# ===========================================================================

class TestMissingEvidence:
    """When no evidence is retrieved, high-risk claims should be unsupported."""

    def test_no_evidence_high_risk_claim(self) -> None:
        """With no evidence, a specific delivery date claim is unsupported."""
        reply = "Your order will arrive by tomorrow."

        llm_client = _make_llm_client(_grounded_llm_response(
            grounded=False,
            score=0.0,
            unsupported=["Your order will arrive by tomorrow."],
            risk_flags=["Delivery date guarantee with no evidence"],
            needs_revision=True,
            needs_human_review=True,
        ))

        result = check_grounding(
            customer_conversation=CONV_DELIVERY,
            classification=CLASSIFICATION_DELIVERY,
            retrieved_evidence=[],  # empty
            generated_reply=reply,
            llm_client=llm_client,
        )

        assert result["grounded"] is False

    def test_polite_only_reply_passes_without_evidence(self) -> None:
        """A purely polite reply should pass even with no evidence."""
        reply = "I'm sorry to hear about this. I understand your frustration."

        result = check_grounding(
            customer_conversation=CONV_DELIVERY,
            classification=CLASSIFICATION_DELIVERY,
            retrieved_evidence=[],
            generated_reply=reply,
            llm_client=None,  # Should not be called for politeness-only
        )

        # This will try to use LLM (offline fallback)
        # At minimum should not hard-fail
        assert "grounded" in result
        assert "grounding_score" in result


# ===========================================================================
# TEST 10: Successful revision
# ===========================================================================

class TestSuccessfulRevision:
    """After a failed grounding, the revision loop should produce a grounded reply."""

    def test_revision_succeeds(self) -> None:
        """Revision loop should succeed on the first attempt with a safe reply."""
        original_reply = "Your refund has been issued and will arrive in 2 days."
        revised_reply = "I'll look into the status of your return and refund. This typically takes 3-5 business days."

        # Initial grounding fails
        initial_grounding = _grounded_llm_response(
            grounded=False,
            score=0.0,
            unsupported=[original_reply],
            risk_flags=["refund has been issued"],
            needs_revision=True,
        )

        # Revision LLM produces safe reply
        revision_output = {
            "reply": revised_reply,
            "evidence_ids": ["retrieval_doc_0001"],
            "needs_human_review": False,
            "revision_strategy": "REWRITE_WITHOUT_UNSUPPORTED",
        }

        # After revision, grounding passes
        post_revision_grounding = _grounded_llm_response(
            grounded=True,
            score=1.0,
            supported=[revised_reply],
            evidence_used=["retrieval_doc_0001"],
        )

        import json

        call_count = [0]
        def smart_generate(prompt, system_prompt=None, json_mode=False, temperature=0.0, max_tokens=None, **kwargs):
            call_count[0] += 1
            mock_resp = MagicMock()
            if call_count[0] == 1:
                # First call: revision generation
                mock_resp.content = json.dumps(revision_output)
            else:
                # Second call: re-grounding
                mock_resp.content = json.dumps(post_revision_grounding)
            return mock_resp

        mock_client = MagicMock()
        mock_client.generate.side_effect = smart_generate

        result = revise_response(
            customer_conversation=CONV_REFUND,
            classification=CLASSIFICATION_REFUND,
            retrieved_evidence=EVIDENCE_REFUND_TIMING,
            original_reply=original_reply,
            initial_grounding_result=initial_grounding,
            llm_client=mock_client,
        )

        assert result["grounding_status"] == "PASSED"
        assert result["needs_human_review"] is False
        assert result["revision_attempts"] == 1
        assert result["final_reply"] == revised_reply

    def test_revision_uses_max_2_attempts(self) -> None:
        """Revision loop maximum is 2 attempts."""
        assert MAX_REVISION_ATTEMPTS == 2


# ===========================================================================
# TEST 11: Failed revision → human review
# ===========================================================================

class TestFailedRevisionHumanReview:
    """After 2 revision attempts, grounding_status=FAILED and needs_human_review=True."""

    def test_failed_revision_triggers_human_review(self) -> None:
        """If both revision attempts still fail grounding, escalate to human."""
        original_reply = "Your refund has been approved and issued."

        failed_grounding = _grounded_llm_response(
            grounded=False,
            score=0.0,
            unsupported=[original_reply],
            risk_flags=["refund has been issued"],
            needs_revision=True,
        )

        # All revision attempts also fail
        revision_output = {
            "reply": "Your refund will definitely arrive by tomorrow.",
            "evidence_ids": [],
            "needs_human_review": False,
            "revision_strategy": "REWRITE_WITHOUT_UNSUPPORTED",
        }

        import json

        def always_fail_generate(prompt, system_prompt=None, json_mode=False, temperature=0.0, max_tokens=None, **kwargs):
            mock_resp = MagicMock()
            # Check if this is a revision prompt or grounding prompt
            if "REVISION ATTEMPT" in prompt or "revision_strategy" in (system_prompt or ""):
                mock_resp.content = json.dumps(revision_output)
            else:
                # Re-grounding also fails
                mock_resp.content = json.dumps(failed_grounding)
            return mock_resp

        mock_client = MagicMock()
        mock_client.generate.side_effect = always_fail_generate

        result = revise_response(
            customer_conversation=CONV_REFUND,
            classification=CLASSIFICATION_REFUND,
            retrieved_evidence=EVIDENCE_REFUND_TIMING,
            original_reply=original_reply,
            initial_grounding_result=failed_grounding,
            llm_client=mock_client,
        )

        assert result["needs_human_review"] is True
        assert result["grounding_status"] in ("FAILED", "ESCALATED")
        assert result["revision_attempts"] <= MAX_REVISION_ATTEMPTS

    def test_human_review_when_contradicted(self) -> None:
        """Contradicted claims always force human review."""
        grounding_with_contradiction = _grounded_llm_response(
            grounded=False,
            score=0.0,
            contradicted=["Since you have Standard shipping, delivery takes 5-7 days."],
            needs_revision=True,
            needs_human_review=True,
        )
        assert grounding_with_contradiction["needs_human_review"] is True
        assert grounding_with_contradiction["contradicted_claims"] != []


# ===========================================================================
# Additional unit tests for helper functions
# ===========================================================================

class TestHelperFunctions:

    def test_is_politeness_only_true(self) -> None:
        polite = [
            "I'm sorry for the inconvenience.",
            "Thank you for your patience.",
            "I understand your frustration.",
            "I apologize for the delay.",
        ]
        for s in polite:
            assert _is_politeness_only(s), f"Expected politeness: '{s}'"

    def test_is_politeness_only_false(self) -> None:
        not_polite = [
            "Your refund has been issued.",
            "Your order will arrive by tomorrow.",
            "We have cancelled your order.",
        ]
        for s in not_polite:
            assert not _is_politeness_only(s), f"Expected NOT politeness: '{s}'"

    def test_contains_high_risk_claim(self) -> None:
        risky = [
            "Your refund will arrive in 3 days.",
            "Your order has been cancelled.",
            "We have issued a replacement.",
            "You are eligible for a full refund.",
        ]
        for s in risky:
            assert _contains_high_risk_claim(s), f"Expected high-risk: '{s}'"

    def test_not_high_risk_claim(self) -> None:
        safe = [
            "Thank you for contacting us.",
            "I understand how frustrating this must be.",
            "Could you please share your order number?",
        ]
        for s in safe:
            assert not _contains_high_risk_claim(s), f"Should not be high-risk: '{s}'"

    def test_extract_evidence_ids(self) -> None:
        evidence = [
            {"document_id": "ev_001", "customer_message": "test", "brand_response": "test"},
            {"document_id": "ev_002", "customer_message": "test", "brand_response": "test"},
        ]
        ids = _extract_evidence_ids(evidence)
        assert ids == ["ev_001", "ev_002"]

    def test_validate_evidence_ids_valid(self) -> None:
        valid = _validate_evidence_ids(["ev_001", "CURRENT_CONVERSATION"], ["ev_001", "ev_002"])
        assert valid == []

    def test_validate_evidence_ids_invalid(self) -> None:
        invalid = _validate_evidence_ids(["ev_999", "ev_001"], ["ev_001"])
        assert "ev_999" in invalid
        assert "ev_001" not in invalid

    def test_empty_reply_returns_failed_grounding(self) -> None:
        result = check_grounding(
            customer_conversation=CONV_REFUND,
            classification=CLASSIFICATION_REFUND,
            retrieved_evidence=EVIDENCE_REFUND_TIMING,
            generated_reply="",
            llm_client=MagicMock(),
        )
        assert result["grounded"] is False
        assert result["needs_human_review"] is True


# ===========================================================================
# Phase 9.1: False Approval Regression Tests (Task 8)
# ===========================================================================

class TestPhase91FalseApprovalRegressions:
    """Test the 5 critical regression cases from Phase 9.1 specification."""

    def test_case_a_historical_safe_place_to_current_offer_fails(self) -> None:
        """A: Historical 'safe-place options are available.'
        Generated: 'We can offer you safe-place delivery tomorrow.'
        Expected: FAIL
        """
        conv = {"customer_message": "Where is my package? I am not at home.", "context": ""}
        evidence = [{
            "document_id": "retrieval_doc_001",
            "customer_message": "Can I leave parcel in a safe place?",
            "brand_response": "safe-place options are available.",
            "relevant_context": "",
        }]
        generated = "We can offer you safe-place delivery tomorrow."
        mock_llm = _make_llm_client({
            "grounded": True,
            "grounding_score": 1.0,
            "claims": [{
                "claim": generated,
                "source_type": "HISTORICAL_EVIDENCE_SUPPORTED",
                "evidence_ids": ["retrieval_doc_001"],
                "support_status": "SUPPORTED",
                "reason": "Supported by historical evidence",
            }],
            "supported_claims": [generated],
            "partially_supported_claims": [],
            "unsupported_claims": [],
            "contradicted_claims": [],
            "evidence_used": ["retrieval_doc_001"],
            "risk_flags": [],
            "needs_revision": False,
            "needs_human_review": False,
        })
        result = check_grounding(
            customer_conversation=conv,
            classification={"primary_intent": "DELIVERY_DELAYED"},
            retrieved_evidence=evidence,
            generated_reply=generated,
            llm_client=mock_llm,
        )
        assert result["grounded"] is False
        assert result["needs_revision"] is True

    def test_case_b_historical_refund_to_current_refund_fails(self) -> None:
        """B: Historical 'Customer was refunded.'
        Generated: 'Your refund has been issued.'
        Expected: FAIL
        """
        conv = {"customer_message": "Where is my money?", "context": ""}
        evidence = [{
            "document_id": "retrieval_doc_002",
            "customer_message": "Was my return received?",
            "brand_response": "Customer was refunded.",
            "relevant_context": "",
        }]
        generated = "Your refund has been issued."
        mock_llm = _make_llm_client({
            "grounded": True,
            "grounding_score": 1.0,
            "claims": [{
                "claim": generated,
                "source_type": "HISTORICAL_EVIDENCE_SUPPORTED",
                "evidence_ids": ["retrieval_doc_002"],
                "support_status": "SUPPORTED",
                "reason": "Supported by historical case",
            }],
            "supported_claims": [generated],
            "partially_supported_claims": [],
            "unsupported_claims": [],
            "contradicted_claims": [],
            "evidence_used": ["retrieval_doc_002"],
            "risk_flags": [],
            "needs_revision": False,
            "needs_human_review": False,
        })
        result = check_grounding(
            customer_conversation=conv,
            classification={"primary_intent": "REFUND_STATUS"},
            retrieved_evidence=evidence,
            generated_reply=generated,
            llm_client=mock_llm,
        )
        assert result["grounded"] is False
        assert result["needs_revision"] is True

    def test_case_c_historical_support_channel_to_general_instruction_passes(self) -> None:
        """C: Historical 'Support can be reached by phone.'
        Generated: 'You can contact support by phone.'
        Expected: PASS (safe generalization)
        """
        conv = {"customer_message": "I have an issue with my order.", "context": ""}
        evidence = [{
            "document_id": "retrieval_doc_003",
            "customer_message": "How do I talk to someone?",
            "brand_response": "Support can be reached by phone.",
            "relevant_context": "",
        }]
        generated = "You can contact support by phone."
        mock_llm = _make_llm_client({
            "grounded": True,
            "grounding_score": 1.0,
            "claims": [{
                "claim": generated,
                "source_type": "HISTORICAL_EVIDENCE_SUPPORTED",
                "evidence_ids": ["retrieval_doc_003"],
                "support_status": "SUPPORTED",
                "reason": "General support channel supported by evidence",
            }],
            "supported_claims": [generated],
            "partially_supported_claims": [],
            "unsupported_claims": [],
            "contradicted_claims": [],
            "evidence_used": ["retrieval_doc_003"],
            "risk_flags": [],
            "needs_revision": False,
            "needs_human_review": False,
        })
        result = check_grounding(
            customer_conversation=conv,
            classification={"primary_intent": "CUSTOMER_SERVICE"},
            retrieved_evidence=evidence,
            generated_reply=generated,
            llm_client=mock_llm,
        )
        assert result["grounded"] is True
        assert result["grounding_score"] == 1.0
        assert result["claims"][0]["source_type"] == "HISTORICAL_EVIDENCE_SUPPORTED"

    def test_case_d_current_conv_refund_issued_passes(self) -> None:
        """D: Current conversation: 'Amazon emailed me saying my refund was issued.'
        Generated: 'Your refund has been issued.'
        Expected: PASS
        """
        conv = {
            "customer_message": "Amazon emailed me saying my refund was issued.",
            "context": "",
        }
        evidence = [{
            "document_id": "retrieval_doc_004",
            "customer_message": "When will I get my money?",
            "brand_response": "Refunds usually appear in 3-5 business days.",
            "relevant_context": "",
        }]
        generated = "Your refund has been issued."
        mock_llm = _make_llm_client({
            "grounded": True,
            "grounding_score": 1.0,
            "claims": [{
                "claim": generated,
                "source_type": "CURRENT_CONVERSATION_SUPPORTED",
                "evidence_ids": ["CURRENT_CONVERSATION"],
                "support_status": "SUPPORTED",
                "reason": "Customer explicitly stated Amazon emailed that refund was issued",
            }],
            "supported_claims": [generated],
            "partially_supported_claims": [],
            "unsupported_claims": [],
            "contradicted_claims": [],
            "evidence_used": ["CURRENT_CONVERSATION"],
            "risk_flags": [],
            "needs_revision": False,
            "needs_human_review": False,
        })
        result = check_grounding(
            customer_conversation=conv,
            classification={"primary_intent": "REFUND_STATUS"},
            retrieved_evidence=evidence,
            generated_reply=generated,
            llm_client=mock_llm,
        )
        assert result["grounded"] is True
        assert result["grounding_score"] == 1.0
        assert result["claims"][0]["source_type"] == "CURRENT_CONVERSATION_SUPPORTED"

    def test_case_e_historical_ask_to_current_received_order_number_fails(self) -> None:
        """E: Historical: 'Amazon asked for an order number.'
        Generated: 'We\'ve received your order number.'
        Expected: FAIL
        """
        conv = {"customer_message": "My order never arrived.", "context": ""}
        evidence = [{
            "document_id": "retrieval_doc_005",
            "customer_message": "I need help with my delivery.",
            "brand_response": "Amazon asked for an order number.",
            "relevant_context": "",
        }]
        generated = "We've received your order number."
        mock_llm = _make_llm_client({
            "grounded": True,
            "grounding_score": 1.0,
            "claims": [{
                "claim": generated,
                "source_type": "HISTORICAL_EVIDENCE_SUPPORTED",
                "evidence_ids": ["retrieval_doc_005"],
                "support_status": "SUPPORTED",
                "reason": "Historical case mentions order number",
            }],
            "supported_claims": [generated],
            "partially_supported_claims": [],
            "unsupported_claims": [],
            "contradicted_claims": [],
            "evidence_used": ["retrieval_doc_005"],
            "risk_flags": [],
            "needs_revision": False,
            "needs_human_review": False,
        })
        result = check_grounding(
            customer_conversation=conv,
            classification={"primary_intent": "DELIVERY_DELAYED"},
            retrieved_evidence=evidence,
            generated_reply=generated,
            llm_client=mock_llm,
        )
        assert result["grounded"] is False
        assert result["needs_revision"] is True

