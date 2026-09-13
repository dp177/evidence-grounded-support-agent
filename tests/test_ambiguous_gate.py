"""Development & Unit tests for Classifier V2 ambiguous / no-intent handling and Runtime Retrieval Gate.

Covers:
- Development test cases A-G ("hi", "hello", "can you help me?", "hi, my package is late",
  "my package is late", "it says delivered but I never got it", "tell me the weather")
- Retrieval mock test proving retriever.search() is called 0 times for AMBIGUOUS and OUT_OF_SCOPE,
  and 1 time for NORMAL
- Multi-turn test preserving conversation_id and recomputing classification dynamically
"""

from unittest.mock import MagicMock, patch
import pytest

from support_agent.agent import SupportAgent
from support_agent.classification.llm_classifier import LLMIntentClassifier
from support_agent.llm.client import BaseLLMClient, LLMResponse


class DummyLLMClient(BaseLLMClient):
    """Deterministic mock LLM client for test cases A-G."""

    def _make_resp(self, json_str: str) -> LLMResponse:
        return LLMResponse(
            content=json_str,
            provider="dummy",
            model="dummy-model",
            review_mode="offline_eval",
        )

    def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> LLMResponse:
        p_lower = prompt.lower()

        # Development Cases A-C: Greetings / vague requests
        if 'current customer message:\n"hi"' in p_lower:
            return self._make_resp(
                '{"classification_status": "AMBIGUOUS", "areas": [], "intents": [], "primary_intent": null, "states": ["INITIAL_INQUIRY"], "confidence": 0.95, "reasoning": "Greeting without actionable support issue"}'
            )
        if 'current customer message:\n"hello"' in p_lower:
            return self._make_resp(
                '{"classification_status": "AMBIGUOUS", "areas": [], "intents": [], "primary_intent": null, "states": ["INITIAL_INQUIRY"], "confidence": 0.95, "reasoning": "Greeting without actionable support issue"}'
            )
        if 'current customer message:\n"can you help me?"' in p_lower:
            return self._make_resp(
                '{"classification_status": "AMBIGUOUS", "areas": [], "intents": [], "primary_intent": null, "states": ["INITIAL_INQUIRY"], "confidence": 0.95, "reasoning": "Vague help request without details"}'
            )

        # Development Case D: Greeting + actionable problem
        if 'current customer message:\n"hi, my package is late"' in p_lower:
            return self._make_resp(
                '{"classification_status": "NORMAL", "areas": ["DELIVERY_AND_FULFILLMENT"], "intents": ["DELIVERY_DELAYED"], "primary_intent": "DELIVERY_DELAYED", "states": ["INITIAL_INQUIRY"], "confidence": 0.95, "reasoning": "Package is late past promised window"}'
            )

        # Development Case E: Direct late package
        if 'current customer message:\n"my package is late"' in p_lower:
            return self._make_resp(
                '{"classification_status": "NORMAL", "areas": ["DELIVERY_AND_FULFILLMENT"], "intents": ["DELIVERY_DELAYED"], "primary_intent": "DELIVERY_DELAYED", "states": ["INITIAL_INQUIRY"], "confidence": 0.95, "reasoning": "Package is late past promised window"}'
            )

        # Development Case F: Delivered not received
        if 'current customer message:\n"it says delivered but i never got it"' in p_lower:
            return self._make_resp(
                '{"classification_status": "NORMAL", "areas": ["DELIVERY_AND_FULFILLMENT"], "intents": ["MARKED_DELIVERED_NOT_RECEIVED"], "primary_intent": "MARKED_DELIVERED_NOT_RECEIVED", "states": ["INITIAL_INQUIRY"], "confidence": 0.95, "reasoning": "Marked delivered but physical parcel missing"}'
            )

        # Development Case G: Out of scope
        if 'current customer message:\n"tell me the weather"' in p_lower:
            return self._make_resp(
                '{"classification_status": "OUT_OF_SCOPE", "areas": [], "intents": [], "primary_intent": null, "states": ["INITIAL_INQUIRY"], "confidence": 0.95, "reasoning": "Weather is outside Amazon support"}'
            )

        # Fallback response for generation / grounding
        return self._make_resp(
            '{"reply": "We apologize for the delivery delay. Let me check this for you.", "evidence_ids": ["doc_1"], "needs_grounding_review": false, "needs_human_review": false, "grounded": true, "grounding_score": 1.0, "claims": []}'
        )


@pytest.fixture
def classifier():
    client = DummyLLMClient()
    return LLMIntentClassifier(client=client)


@pytest.fixture
def mock_agent():
    client = DummyLLMClient()
    mock_retriever = MagicMock()
    mock_reranker = MagicMock()
    mock_reranker.weights = {
        "semantic": 1.0,
        "lexical": 0.3,
        "intent": 0.2,
        "area": 0.1,
        "state": 0.1,
        "action_penalty": -0.2,
    }
    mock_reranker.rerank.return_value = [
        {
            "id": "cand_1",
            "document_id": "doc_1",
            "case_id": "case_1",
            "customer_message": "Where is my item",
            "brand_response": "We apologize for the delay. We are tracking it.",
            "score": 0.88,
            "intents": ["DELIVERY_DELAYED"],
            "states": ["INITIAL_INQUIRY"],
            "action_penalty_flag": 0.0,
            "semantic_score": 0.90,
            "lexical_score": 0.80,
            "intent_score": 1.0,
            "state_score": 1.0,
            "rerank_score": 0.92,
        }
    ]
    mock_service = MagicMock()
    mock_service.retriever = mock_retriever
    mock_service.reranker = mock_reranker

    clf = LLMIntentClassifier(client=client)
    return SupportAgent(
        classifier=clf,
        retrieval_service=mock_service,
        llm_client=client,
    )


# ===========================================================================
# 1. Development Test Cases A-G
# ===========================================================================

def test_case_a_hi(classifier):
    """Case A: 'hi' -> AMBIGUOUS, no intents, primary_intent null."""
    res = classifier.classify_case("hi", use_cache=False)
    assert res["classification_status"] == "AMBIGUOUS"
    assert res["intents"] == []
    assert res["areas"] == []
    assert res["primary_intent"] is None


def test_case_b_hello(classifier):
    """Case B: 'hello' -> AMBIGUOUS."""
    res = classifier.classify_case("hello", use_cache=False)
    assert res["classification_status"] == "AMBIGUOUS"
    assert res["intents"] == []
    assert res["primary_intent"] is None


def test_case_c_can_you_help_me(classifier):
    """Case C: 'can you help me?' -> AMBIGUOUS."""
    res = classifier.classify_case("can you help me?", use_cache=False)
    assert res["classification_status"] == "AMBIGUOUS"
    assert res["intents"] == []
    assert res["primary_intent"] is None


def test_case_d_hi_my_package_is_late(classifier):
    """Case D: 'hi, my package is late' -> NORMAL, DELIVERY_DELAYED (greeting does not obscure issue)."""
    res = classifier.classify_case("hi, my package is late", use_cache=False)
    assert res["classification_status"] == "NORMAL"
    assert res["primary_intent"] == "DELIVERY_DELAYED"
    assert "DELIVERY_DELAYED" in res["intents"]


def test_case_e_my_package_is_late(classifier):
    """Case E: 'my package is late' -> NORMAL, DELIVERY_DELAYED."""
    res = classifier.classify_case("my package is late", use_cache=False)
    assert res["classification_status"] == "NORMAL"
    assert res["primary_intent"] == "DELIVERY_DELAYED"


def test_case_f_marked_delivered_not_received(classifier):
    """Case F: 'it says delivered but I never got it' -> NORMAL, MARKED_DELIVERED_NOT_RECEIVED."""
    res = classifier.classify_case("it says delivered but I never got it", use_cache=False)
    assert res["classification_status"] == "NORMAL"
    assert res["primary_intent"] == "MARKED_DELIVERED_NOT_RECEIVED"


def test_case_g_tell_me_the_weather(classifier):
    """Case G: 'tell me the weather' -> OUT_OF_SCOPE."""
    res = classifier.classify_case("tell me the weather", use_cache=False)
    assert res["classification_status"] == "OUT_OF_SCOPE"
    assert res["primary_intent"] is None
    assert res["intents"] == []


# ===========================================================================
# 2. Retrieval Mock Test: Gate Proof
# ===========================================================================

def test_retrieval_mock_gate_ambiguous(mock_agent):
    """Prove that for AMBIGUOUS messages, retriever.search() is called ZERO times."""
    agent = mock_agent

    resp = agent.handle(
        conversation_id="test_conv_ambiguous",
        messages=[{"role": "customer", "text": "hi"}],
    )

    # Proves retriever.search() called ZERO times
    assert agent.retrieval_service.retriever.search.call_count == 0
    assert resp["classification"]["status"] == "AMBIGUOUS"
    assert resp["classification"]["primary_intent"] is None
    assert resp["retrieved_evidence"] == []
    assert resp["reranking"]["final_count"] == 0
    assert resp["generated_reply"]["reply"] == "Hi! How can I help you today?"
    assert resp["escalation"]["decision"] == "AUTO_HANDLE"
    assert resp["escalation"]["action"] == "CLARIFY"
    assert "SAFE_CLARIFICATION" in resp["escalation"]["reason_codes"]


def test_retrieval_mock_gate_normal(mock_agent):
    """Prove that for NORMAL messages, retriever.search() is called ONCE."""
    agent = mock_agent

    fake_candidates = [
        {
            "id": "cand_1",
            "document_id": "doc_1",
            "case_id": "case_1",
            "customer_message": "Where is my item",
            "brand_response": "We apologize for the delay. We are tracking it.",
            "score": 0.88,
            "intents": ["DELIVERY_DELAYED"],
            "states": ["INITIAL_INQUIRY"],
            "action_penalty_flag": 0.0,
            "semantic_score": 0.90,
            "lexical_score": 0.80,
            "intent_score": 1.0,
            "state_score": 1.0,
            "rerank_score": 0.92,
        }
    ]
    agent.retrieval_service.retriever.search.return_value = fake_candidates

    resp = agent.handle(
        conversation_id="test_conv_normal",
        messages=[{"role": "customer", "text": "my package is late"}],
    )

    # Proves retriever.search() called exactly ONCE
    assert agent.retrieval_service.retriever.search.call_count == 1
    assert resp["classification"]["status"] == "NORMAL"
    assert resp["classification"]["primary_intent"] == "DELIVERY_DELAYED"
    assert len(resp["retrieved_evidence"]) > 0


def test_retrieval_mock_gate_out_of_scope(mock_agent):
    """Prove that for OUT_OF_SCOPE messages, retriever.search() is called ZERO times."""
    agent = mock_agent

    resp = agent.handle(
        conversation_id="test_conv_oos",
        messages=[{"role": "customer", "text": "tell me the weather"}],
    )

    # Proves retriever.search() called ZERO times
    assert agent.retrieval_service.retriever.search.call_count == 0
    assert resp["classification"]["status"] == "OUT_OF_SCOPE"
    assert resp["classification"]["primary_intent"] is None
    assert resp["retrieved_evidence"] == []


# ===========================================================================
# 3. Multi-Turn Test
# ===========================================================================

def test_multi_turn_ambiguous_then_normal(mock_agent):
    """Prove that Turn 1 ('hi') skips retrieval, while Turn 2 ('my package is late') triggers retrieval."""
    agent = mock_agent
    conversation_id = "test_conv_multiturn_123"

    fake_candidates = [
        {
            "id": "cand_1",
            "document_id": "doc_1",
            "case_id": "case_1",
            "customer_message": "My order is delayed",
            "brand_response": "We are investigating the delay.",
            "score": 0.90,
            "intents": ["DELIVERY_DELAYED"],
            "states": ["INITIAL_INQUIRY"],
            "action_penalty_flag": 0.0,
            "semantic_score": 0.90,
            "lexical_score": 0.80,
            "intent_score": 1.0,
            "state_score": 1.0,
            "rerank_score": 0.92,
        }
    ]
    agent.retrieval_service.retriever.search.return_value = fake_candidates

    # Turn 1: "hi"
    turn1_resp = agent.handle(
        conversation_id=conversation_id,
        messages=[{"role": "customer", "text": "hi"}],
    )

    assert turn1_resp["conversation_id"] == conversation_id
    assert turn1_resp["classification"]["status"] == "AMBIGUOUS"
    assert turn1_resp["classification"]["primary_intent"] is None
    assert agent.retrieval_service.retriever.search.call_count == 0

    # Turn 2: "my package is late" with context from Turn 1
    turn2_resp = agent.handle(
        conversation_id=conversation_id,
        messages=[
            {"role": "customer", "text": "hi"},
            {"role": "assistant", "text": turn1_resp["generated_reply"]["reply"]},
            {"role": "customer", "text": "my package is late"},
        ],
    )

    assert turn2_resp["conversation_id"] == conversation_id
    assert turn2_resp["classification"]["status"] == "NORMAL"
    assert turn2_resp["classification"]["primary_intent"] == "DELIVERY_DELAYED"
    # Search called ONCE now on Turn 2
    assert agent.retrieval_service.retriever.search.call_count == 1
    assert len(turn2_resp["retrieved_evidence"]) > 0

