"""Response Generator Module.

Uses OpenRouter LLM to synthesize customer replies grounded in historical evidence and conversation state.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from support_agent.llm.client import get_llm_client, BaseLLMClient

logger = logging.getLogger(__name__)

# Default config fallback
DEFAULT_CONFIG = {
    "max_reply_tokens": 300,
    "temperature": 0.1,
    "max_evidence_items": 3,
}

class ResponseGenerator:
    """Synthesizes customer replies using LLM grounded in semantic retrieval."""

    def __init__(
        self,
        llm_client: Optional[BaseLLMClient] = None,
        config_path: str = "configs/response_generation.yaml",
        prompt_path: str = "prompts/response_generation_v1.md",
    ):
        self.llm_client = llm_client or get_llm_client()
        self.config = DEFAULT_CONFIG.copy()
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
                if "response_generation" in cfg:
                    self.config.update(cfg["response_generation"])
        except Exception as e:
            logger.warning(f"Could not load config {config_path}: {e}. Using defaults.")

        self.system_prompt = ""
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
        except Exception as e:
            logger.error(f"Could not load system prompt from {prompt_path}: {e}")
            self.system_prompt = "You are an Amazon customer-support response assistant. Respond in JSON."

    def format_input(
        self,
        customer_message: str,
        context: str,
        classification: Dict[str, Any],
        historical_evidence: List[Dict[str, Any]],
    ) -> str:
        """Structure the LLM input exactly as requested by Phase 8."""
        parts = []
        
        # 1. Current Conversation
        parts.append("CURRENT CONVERSATION\n--------------------")
        if context.strip():
            parts.append(f"Context:\n{context.strip()}")
        parts.append(f"Customer:\n{customer_message.strip()}")
        
        # 2. Classification
        parts.append("\nCLASSIFICATION\n--------------")
        parts.append(f"Primary intent: {classification.get('primary_intent', 'UNKNOWN')}")
        parts.append(f"Intent(s): {classification.get('intents', [])}")
        parts.append(f"Area: {classification.get('areas', [])}")
        parts.append(f"State: {classification.get('states', [])}")
        
        # 3. Historical Evidence
        parts.append("\nHISTORICAL EVIDENCE\n-------------------")
        max_ev = self.config.get("max_evidence_items", 3)
        truncated_evidence = historical_evidence[:max_ev]
        
        if not truncated_evidence:
            parts.append("No historical evidence retrieved.")
        else:
            for i, ev in enumerate(truncated_evidence, 1):
                parts.append(f"\nEvidence {i} (ID: {ev.get('document_id', 'unknown')})")
                parts.append(f"Customer:\n{ev.get('customer_message', '')}")
                if ev.get("relevant_context"):
                    parts.append(f"Context:\n{ev.get('relevant_context')}")
                parts.append(f"Amazon:\n{ev.get('brand_response', '')}")

        return "\n".join(parts)

    def generate_response(
        self,
        customer_message: str,
        context: str,
        classification: Dict[str, Any],
        historical_evidence: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate a grounded reply via the LLM client."""
        prompt = self.format_input(customer_message, context, classification, historical_evidence)
        
        try:
            llm_resp = self.llm_client.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                json_mode=True,
                temperature=self.config.get("temperature", 0.1),
                max_tokens=self.config.get("max_reply_tokens", 300),
            )
            
            # The client handles parsing if we call .json()
            output = llm_resp.json()
            
            # Basic validation
            if not isinstance(output, dict):
                raise ValueError(f"LLM did not return a JSON object. Returned: {type(output)}")
            
            # Fill schema fallbacks if model forgot them
            if "reply" not in output:
                output["reply"] = "I apologize, but I need more information to assist you."
            if "evidence_ids" not in output:
                output["evidence_ids"] = []
            if "needs_grounding_review" not in output:
                output["needs_grounding_review"] = True
            if "needs_human_review" not in output:
                output["needs_human_review"] = True
                
            return output
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return {
                "reply": "I apologize, I am experiencing technical difficulties processing your request. Please hold while I transfer you to a human associate.",
                "evidence_ids": [],
                "needs_grounding_review": True,
                "needs_human_review": True,
                "error": str(e)
            }
