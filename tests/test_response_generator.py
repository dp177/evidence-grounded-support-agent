"""Unit tests for the ResponseGenerator module."""

import pytest
from unittest.mock import MagicMock
from support_agent.generation.response_generator import ResponseGenerator
from support_agent.llm.client import BaseLLMClient, LLMResponse

class MockLLMClient(BaseLLMClient):
    def __init__(self, raw_content: str):
        self.raw_content = raw_content

    def generate(self, prompt, **kwargs):
        return LLMResponse(
            content=self.raw_content,
            provider="mock",
            model="mock",
            review_mode="mock"
        )

def test_format_input_truncates_evidence():
    gen = ResponseGenerator(llm_client=MockLLMClient("{}"))
    gen.config["max_evidence_items"] = 2
    
    classification = {"primary_intent": "TEST"}
    evidence = [
        {"document_id": "1", "customer_message": "1", "brand_response": "A"},
        {"document_id": "2", "customer_message": "2", "brand_response": "B"},
        {"document_id": "3", "customer_message": "3", "brand_response": "C"}
    ]
    
    formatted = gen.format_input("help", "", classification, evidence)
    
    assert "Evidence 1" in formatted
    assert "Evidence 2" in formatted
    assert "Evidence 3" not in formatted

def test_generate_response_success():
    mock_json = '''
    {
      "reply": "Here is a refund.",
      "evidence_ids": ["doc_1"],
      "needs_grounding_review": false,
      "needs_human_review": false
    }
    '''
    gen = ResponseGenerator(llm_client=MockLLMClient(mock_json))
    
    res = gen.generate_response("test", "", {}, [])
    assert res["reply"] == "Here is a refund."
    assert res["evidence_ids"] == ["doc_1"]
    assert res["needs_grounding_review"] is False

def test_generate_response_fallback_missing_keys():
    mock_json = '{"reply": "Missing other keys"}'
    gen = ResponseGenerator(llm_client=MockLLMClient(mock_json))
    
    res = gen.generate_response("test", "", {}, [])
    assert res["reply"] == "Missing other keys"
    assert res["evidence_ids"] == []
    assert res["needs_grounding_review"] is True
    assert res["needs_human_review"] is True

def test_generate_response_malformed_json():
    gen = ResponseGenerator(llm_client=MockLLMClient("I am not a JSON object"))
    
    res = gen.generate_response("test", "", {}, [])
    assert "error" in res
    assert res["needs_human_review"] is True
    assert "technical difficulties" in res["reply"]
