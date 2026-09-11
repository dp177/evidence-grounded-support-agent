"""Unit tests for LLM provider abstraction, OpenRouterClient, and OfflineReviewClient."""

import os
from unittest.mock import MagicMock, patch
import pytest

from support_agent.llm.client import (
    BaseLLMClient,
    LLMResponse,
    OfflineReviewClient,
    OpenRouterClient,
    get_llm_client,
    parse_json_from_text,
)


def test_base_llm_client_is_abstract():
    """Ensure BaseLLMClient cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseLLMClient()


def test_provider_configuration_explicit():
    """Test initializing OpenRouterClient with explicit parameters."""
    client = OpenRouterClient(
        api_key="test_key_12345",
        model="test-provider/test-model",
        base_url="https://test.openrouter.ai/api/v1",
        site_url="https://mytestsite.org",
        app_name="TestApp",
        timeout=45,
        max_retries=2,
    )
    assert client.api_key == "test_key_12345"
    assert client.model == "test-provider/test-model"
    assert client.base_url == "https://test.openrouter.ai/api/v1"
    assert client.site_url == "https://mytestsite.org"
    assert client.app_name == "TestApp"
    assert client.timeout == 45
    assert client.max_retries == 2


def test_missing_api_key_raises_value_error(monkeypatch):
    """Test that missing API key raises ValueError without secret leakage."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(ValueError) as excinfo:
        OpenRouterClient(api_key="", model="test-model")
    assert "OPENROUTER_API_KEY is not set" in str(excinfo.value)


def test_missing_model_raises_value_error(monkeypatch):
    """Test that missing model raises ValueError."""
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    with pytest.raises(ValueError) as excinfo:
        OpenRouterClient(api_key="valid_key", model="")
    assert "OPENROUTER_MODEL is not set" in str(excinfo.value)


def test_offline_client_initialization_and_generation():
    """Test OfflineReviewClient generation output and metadata."""
    offline_client = OfflineReviewClient()
    assert offline_client.model is None
    assert offline_client.provider == "offline"
    assert offline_client.review_mode == "offline"

    response = offline_client.generate(prompt="Review intent WHERE_IS_MY_ORDER", json_mode=True)
    assert isinstance(response, LLMResponse)
    assert response.provider == "offline"
    assert response.model is None
    assert response.review_mode == "offline"

    parsed = response.json()
    assert parsed["review_mode"] == "offline"
    assert parsed["provider"] == "offline"
    assert "structural_checks" in parsed


def test_get_llm_client_fallback_when_offline_forced():
    """Test factory returns OfflineReviewClient when force_offline is True."""
    client = get_llm_client(force_offline=True)
    assert isinstance(client, OfflineReviewClient)
    assert client.review_mode == "offline"


def test_get_llm_client_fallback_when_key_missing(monkeypatch):
    """Test factory falls back to OfflineReviewClient when key is missing."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    client = get_llm_client()
    assert isinstance(client, OfflineReviewClient)


def test_json_parsing_clean():
    """Test parsing clean direct JSON."""
    raw = '{"intent": "WHERE_IS_MY_ORDER", "decision": "KEEP", "confidence": 0.95}'
    parsed = parse_json_from_text(raw)
    assert parsed["intent"] == "WHERE_IS_MY_ORDER"
    assert parsed["decision"] == "KEEP"
    assert parsed["confidence"] == 0.95


def test_json_parsing_markdown_block():
    """Test extracting JSON wrapped in markdown code fence."""
    raw = """Here is the review result:
```json
{
  "intent": "DELIVERY_DELAYED",
  "decision": "KEEP",
  "recommended_name": "DELIVERY_DELAYED"
}
```
Hope this helps!"""
    parsed = parse_json_from_text(raw)
    assert parsed["intent"] == "DELIVERY_DELAYED"
    assert parsed["decision"] == "KEEP"


def test_json_parsing_array():
    """Test parsing JSON array of items."""
    raw = """[
        {"intent": "INTENT_A", "decision": "KEEP"},
        {"intent": "INTENT_B", "decision": "MERGE"}
    ]"""
    parsed = parse_json_from_text(raw)
    assert isinstance(parsed, list)
    assert len(parsed) == 2
    assert parsed[0]["intent"] == "INTENT_A"


def test_malformed_json_raises_value_error():
    """Test that malformed JSON raises ValueError with clear message."""
    with pytest.raises(ValueError) as excinfo:
        parse_json_from_text("This is an unparseable response with { broken: json,")
    assert "Failed to parse valid JSON" in str(excinfo.value)

    with pytest.raises(ValueError):
        parse_json_from_text("")


def test_taxonomy_review_schema_validation():
    """Verify that a taxonomy review payload conforms to expected schema."""
    sample_payload = {
        "provider": "openrouter",
        "model": "google/gemini-3.1-pro-preview",
        "review_mode": "openrouter",
        "timestamp": "2026-09-12T02:00:00Z",
        "reviews": [
            {
                "intent": "WHERE_IS_MY_ORDER",
                "decision": "KEEP",
                "recommended_name": "WHERE_IS_MY_ORDER",
                "reason": "High volume and distinct tracking status check within promised window.",
                "closest_confusable_intents": ["DELIVERY_DELAYED"],
                "operational_distinction": "Directs customer to tracking page vs escalation for overdue parcel.",
                "annotation_difficulty": "LOW",
                "confidence": 0.95,
            }
        ],
    }

    assert "provider" in sample_payload
    assert "model" in sample_payload
    assert "review_mode" in sample_payload
    assert "reviews" in sample_payload

    review = sample_payload["reviews"][0]
    required_keys = {
        "intent",
        "decision",
        "recommended_name",
        "reason",
        "closest_confusable_intents",
        "operational_distinction",
        "annotation_difficulty",
        "confidence",
    }
    assert required_keys.issubset(review.keys())
    assert review["decision"] in {"KEEP", "MERGE", "SPLIT", "RENAME", "DROP"}
    assert review["annotation_difficulty"] in {"LOW", "MEDIUM", "HIGH"}
    assert 0.0 <= review["confidence"] <= 1.0


def test_openrouter_client_mock_retry_success():
    """Test OpenRouterClient retry handling for transient status code 429."""
    mock_resp_429 = MagicMock()
    mock_resp_429.status_code = 429

    mock_resp_200 = MagicMock()
    mock_resp_200.status_code = 200
    mock_resp_200.json.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": '{"result": "success"}',
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"total_tokens": 42},
    }

    client = OpenRouterClient(
        api_key="mock_key",
        model="test-model",
        max_retries=2,
        retry_delay=0.01,
    )

    with patch("requests.post", side_effect=[mock_resp_429, mock_resp_200]) as mock_post:
        resp = client.generate(prompt="hello")
        assert mock_post.call_count == 2
        assert resp.content == '{"result": "success"}'
        assert resp.provider == "openrouter"
        assert resp.review_mode == "openrouter"
