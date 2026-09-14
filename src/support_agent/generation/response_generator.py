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

CLARIFICATION_SYSTEM_PROMPT = """You are a helpful, professional, and friendly AI customer-support assistant for Amazon retail customer support.
The customer's message lacks sufficient information or a specific actionable issue (classification status: AMBIGUOUS, primary_intent: null).

Your task is to ask a concise, polite, and natural clarifying question to find out what specific Amazon issue the customer needs help with.

STRICT RULES:
1. Be concise (1 to 2 sentences max).
2. Acknowledge the customer's greeting or message naturally and politely.
3. Ask for the missing details needed to identify their specific support issue (e.g., asking if they need assistance with an order, package delivery, return, refund, or account).
4. NEVER invent order numbers, tracking IDs, delivery dates, refund amounts, or account facts.
5. NEVER promise specific actions, refunds, replacements, or account changes.
6. NEVER claim that a refund, replacement, escalation, or account change has occurred, and NEVER claim that you have checked or received account details yourself (e.g. do not say "we have received your details" or "I checked your account").
7. NEVER expose internal reasoning or mention words like "classification", "intent", "RAG", "confidence", "AMBIGUOUS", "pipeline", or model internals.
8. Output MUST be a single valid JSON object:
{
  "reply": "concise, natural clarifying response",
  "evidence_ids": []
}
"""


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
        
        # 2. Classification & Operational State Constraints
        states = classification.get("states", [])
        state_hints = []
        for s in states:
            if s == "WAITING_WINDOW_EXCEEDED":
                state_hints.append("Customer waiting window elapsed or repeated support attempts reported. Acknowledge prior delay/attempts and provide next escalation/investigation steps; do NOT advise merely waiting more.")
            elif s == "CARRIER_ALREADY_CONTACTED":
                state_hints.append("Customer has already contacted the carrier. Do NOT tell them to contact carrier again.")
            elif s == "TRACKING_ALREADY_CHECKED":
                state_hints.append("Customer has already verified tracking. Do NOT tell them to check tracking again (locating tracking number instructions are allowed if requested).")
            elif s == "DETAILS_ALREADY_PROVIDED":
                state_hints.append("Customer has already provided details/order info. Do NOT ask for the same details again.")

        parts.append("\nCLASSIFICATION\n--------------")
        parts.append(f"Primary intent: {classification.get('primary_intent', 'UNKNOWN')}")
        parts.append(f"Intent(s): {classification.get('intents', [])}")
        parts.append(f"Area: {classification.get('areas', [])}")
        parts.append(f"State: {states}")
        if state_hints:
            parts.append(f"State Constraints: {' '.join(state_hints)}")
        
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

    def format_clarification_input(
        self,
        customer_message: str,
        context: Optional[str] = None,
        classification: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Structure the prompt for generating a clarification question."""
        parts = []
        parts.append("CURRENT CONVERSATION\n--------------------")
        if context and context.strip():
            parts.append(f"Context:\n{context.strip()}")
        parts.append(f"Customer:\n{customer_message.strip()}")

        parts.append("\nCLASSIFICATION\n--------------")
        clf = classification or {}
        parts.append(f"Status: {clf.get('classification_status', 'AMBIGUOUS')}")
        parts.append(f"Primary intent: {clf.get('primary_intent')}")

        parts.append("\nINSTRUCTION\n-----------")
        parts.append("The customer inquiry is ambiguous or missing specific details. Ask a helpful, polite clarifying question to identify their Amazon retail support issue.")

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

    def generate_clarification(
        self,
        customer_message: str,
        context: Optional[str] = None,
        classification: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a natural clarifying question for AMBIGUOUS inquiries via LLM."""
        prompt = self.format_clarification_input(customer_message, context, classification)
        fallback_reply = "Hi! How can I help you today?"

        try:
            llm_resp = self.llm_client.generate(
                prompt=prompt,
                system_prompt=CLARIFICATION_SYSTEM_PROMPT,
                json_mode=True,
                temperature=0.3,
                max_tokens=150,
            )

            output = llm_resp.json()
            if not isinstance(output, dict):
                raise ValueError(f"LLM did not return a JSON object: {type(output)}")

            reply = str(output.get("reply", "")).strip()
            if not reply or len(reply) < 5:
                raise ValueError("LLM returned empty or too short clarification reply")

            # Validate that the reply doesn't leak internal pipeline words
            leak_words = ["classification", "confidence", "ambiguous", "rag", "pipeline", "taxonomy"]
            if any(w in reply.lower() for w in leak_words):
                logger.warning(f"Clarification leaked internal words: {reply}. Using fallback.")
                reply = fallback_reply

            return {
                "reply": reply,
                "evidence_ids": [],
                "needs_grounding_review": False,
                "needs_human_review": False,
            }
        except Exception as e:
            logger.error(f"Clarification generation failed: {e}. Using deterministic emergency fallback.")
            return {
                "reply": fallback_reply,
                "evidence_ids": [],
                "needs_grounding_review": False,
                "needs_human_review": False,
                "error": str(e),
            }

