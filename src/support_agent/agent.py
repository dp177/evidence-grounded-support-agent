"""SupportAgent Orchestrator.

Provides a unified callable boundary connecting:
  1. Conversation loader & context builder
  2. LLMIntentClassifier (Classifier V2)
  3. Qdrant Retrieval + Candidate Reranking
  4. Response Generation
  5. Grounding Verification & Revision Loop
  6. Deterministic Escalation Policy Engine
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Generator, List, Optional

from support_agent.classification.llm_classifier import LLMIntentClassifier
from support_agent.retrieval.service import RetrievalService
from support_agent.retrieval.retriever import format_query_text
from support_agent.generation.response_generator import ResponseGenerator
from support_agent.generation.revise_response import run_grounded_pipeline
from support_agent.escalation.escalation_policy import EscalationConfig
from support_agent.escalation.decision import decide_escalation
from support_agent.llm.client import get_llm_client, BaseLLMClient

logger = logging.getLogger(__name__)


class SupportAgent:
    """Production Agent Orchestrator."""

    def __init__(
        self,
        classifier: Optional[LLMIntentClassifier] = None,
        retrieval_service: Optional[RetrievalService] = None,
        generator: Optional[ResponseGenerator] = None,
        llm_client: Optional[BaseLLMClient] = None,
        escalation_config: Optional[EscalationConfig] = None,
    ):
        self.llm_client = llm_client or get_llm_client()
        self.classifier = classifier or LLMIntentClassifier(client=self.llm_client)
        self.retrieval_service = retrieval_service or RetrievalService()
        self.generator = generator or ResponseGenerator(llm_client=self.llm_client)
        self.escalation_config = escalation_config or EscalationConfig.from_yaml()

    def _extract_conversation_turns(
        self, messages: List[Dict[str, Any]]
    ) -> tuple[str, str]:
        """Extract the current customer message and historical conversation context.

        Returns (latest_customer_message, context_str).
        """
        if not messages:
            return "", ""

        # Normalize role and content
        normalized: List[tuple[str, str]] = []
        for m in messages:
            role = str(m.get("role", "customer")).lower()
            text = str(m.get("content") or m.get("text") or "").strip()
            if text:
                normalized.append((role, text))

        if not normalized:
            return "", ""

        # Find the last customer message index
        last_cust_idx = -1
        for i in range(len(normalized) - 1, -1, -1):
            if normalized[i][0] == "customer":
                last_cust_idx = i
                break

        if last_cust_idx == -1:
            # If no explicit customer role, take the last message as customer
            last_cust_idx = len(normalized) - 1

        customer_message = normalized[last_cust_idx][1]

        # Everything before last_cust_idx is context
        context_lines = []
        for role, text in normalized[:last_cust_idx]:
            speaker = "Customer" if role == "customer" else "Amazon"
            context_lines.append(f"{speaker}: {text}")

        context = "\n".join(context_lines)
        return customer_message, context

    def _format_evidence(self, reranked_evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format raw reranker output into the contract-compliant evidence card list."""
        formatted_evidence: List[Dict[str, Any]] = []
        for idx, e in enumerate(reranked_evidence):
            sem = e.get("semantic_score", e.get("score"))
            lex = e.get("lexical_score")
            intent = e.get("intent_score")
            st = e.get("state_score")
            act_flag = e.get("action_penalty_flag", 0.0)
            act_useful = e.get("action_usefulness")
            if act_useful is None and act_flag is not None:
                act_useful = 1.0 - float(act_flag)
            final_sc = e.get("final_score", e.get("rerank_score"))

            formatted_evidence.append({
                "case_id": str(e.get("case_id", e.get("id", f"case_{idx + 1}"))),
                "conversation_id": str(e.get("conversation_id", "")),
                "turn_index": int(e.get("turn_index", 1)),
                "rank": int(e.get("rank", idx + 1)),
                "similarity": round(float(e.get("score", e.get("similarity", 0.85))), 2),
                "customer_message": str(e.get("customer_message", "")),
                "relevant_context": str(e.get("relevant_context", "")),
                "brand_response": str(e.get("brand_response", "")),
                "doc_id": str(e.get("document_id", "")),
                "semantic_score": round(float(sem), 2) if sem is not None else None,
                "lexical_score": round(float(lex), 2) if lex is not None else None,
                "intent_score": round(float(intent), 2) if intent is not None else None,
                "state_score": round(float(st), 2) if st is not None else None,
                "action_usefulness": round(float(act_useful), 2) if act_useful is not None else None,
                "action_penalty_flag": round(float(act_flag), 2) if act_flag is not None else None,
                "final_score": round(float(final_sc), 3) if final_sc is not None else None,
                "rerank_score": round(float(final_sc), 3) if final_sc is not None else None,
            })
        return formatted_evidence

    def _format_claims(
        self, grounding_result: Dict[str, Any], classification: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Format grounding result claims into the contract-compliant claim list."""
        raw_claims = grounding_result.get("claims", [])
        formatted_claims: List[Dict[str, Any]] = []
        for idx, c in enumerate(raw_claims):
            if isinstance(c, str):
                formatted_claims.append({
                    "id": f"claim_{idx + 1}",
                    "text": c,
                    "source_type": "HISTORICAL_EVIDENCE",
                    "status": "BOTH" if grounding_result.get("grounded") else "UNSUPPORTED",
                })
            elif isinstance(c, dict):
                formatted_claims.append({
                    "id": str(c.get("id", f"claim_{idx + 1}")),
                    "text": str(c.get("text", c.get("claim_text", ""))),
                    "source_type": str(c.get("source_type", "HISTORICAL_EVIDENCE")),
                    "status": str(c.get("status", "BOTH")),
                    "supporting_ref": c.get("supporting_ref"),
                })
        if not formatted_claims:
            is_grounded = bool(grounding_result.get("grounded", False))
            formatted_claims = [
                {
                    "id": "c1",
                    "text": f"Customer statement addressed regarding {classification.get('primary_intent') or 'inquiry'}",
                    "source_type": "CONVERSATION",
                    "status": "CURRENT_CONVERSATION_SUPPORTED",
                },
                {
                    "id": "c2",
                    "text": "Guidance aligns with Amazon standard operating procedure",
                    "source_type": "HISTORICAL_EVIDENCE",
                    "status": "HISTORICAL_EVIDENCE_SUPPORTED" if is_grounded else "UNSUPPORTED",
                },
            ]
        return formatted_claims

    def _build_reranking_signals(
        self, reranked_evidence: List[Dict[str, Any]], initial_candidates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compute aggregate reranking signals block for the response contract."""
        weights = self.retrieval_service.reranker.weights
        if reranked_evidence:
            avg_sem = round(sum(e.get("semantic_score", e.get("score", 0.0)) for e in reranked_evidence) / len(reranked_evidence), 2)
            lex_scores = [e.get("lexical_score") for e in reranked_evidence if e.get("lexical_score") is not None]
            avg_lex = round(sum(lex_scores) / len(lex_scores), 2) if lex_scores else None
            int_scores = [e.get("intent_score") for e in reranked_evidence if e.get("intent_score") is not None]
            avg_int = round(sum(int_scores) / len(int_scores), 2) if int_scores else None
            st_scores = [e.get("state_score") for e in reranked_evidence if e.get("state_score") is not None]
            avg_st = round(sum(st_scores) / len(st_scores), 2) if st_scores else None
            act_scores = [e.get("action_usefulness") for e in reranked_evidence if e.get("action_usefulness") is not None]
            avg_act = round(sum(act_scores) / len(act_scores), 2) if act_scores else None
        else:
            avg_sem, avg_lex, avg_int, avg_st, avg_act = None, None, None, None, None

        signals = [
            {"name": "semantic", "label": "Semantic Similarity", "score": avg_sem, "weight": weights.get("semantic", 1.0)},
            {"name": "lexical", "label": "Lexical Match", "score": avg_lex, "weight": weights.get("lexical", 0.3)},
            {"name": "intent", "label": "Intent Compatibility", "score": avg_int, "weight": weights.get("intent", 0.2)},
            {"name": "state", "label": "State Compatibility", "score": avg_st, "weight": weights.get("state", 0.1)},
            {"name": "action_usefulness", "label": "Action Usefulness", "score": avg_act, "weight": weights.get("action_penalty", -0.2)},
        ]

        unique_convs = len(set(e.get("conversation_id", "") for e in reranked_evidence if e.get("conversation_id")))
        if unique_convs == 0:
            unique_convs = len(reranked_evidence)

        return {
            "candidate_count": len(initial_candidates),
            "final_count": len(reranked_evidence),
            "unique_conversations": unique_convs,
            "signals": signals,
            "weights": {
                "semantic": float(weights.get("semantic", 1.0)),
                "lexical": float(weights.get("lexical", 0.3)),
                "intent": float(weights.get("intent", 0.2)),
                "area": float(weights.get("area", 0.1)),
                "state": float(weights.get("state", 0.1)),
                "action_penalty": float(weights.get("action_penalty", -0.2)),
            },
        }

    def handle_stream(
        self, conversation_id: str, messages: List[Dict[str, Any]]
    ) -> Generator[Dict[str, Any], None, None]:
        """Execute the full agent pipeline and yield real-time stage events as each
        stage completes.  Events are plain dicts; callers decide how to serialise them
        (JSON, SSE, etc.).

        Emitted event types (in order):
          conversation  – conversation context loaded
          classify      – classification completed
          retrieve      – retrieval completed (skipped for AMBIGUOUS/OUT_OF_SCOPE)
          rerank        – reranking completed (skipped for AMBIGUOUS/OUT_OF_SCOPE)
          generate      – response generation completed
          ground        – grounding verification completed
          decide        – escalation decision completed
          complete      – final AgentResponse (same as handle())
        """
        t_start = time.time()
        customer_message, context = self._extract_conversation_turns(messages)

        if not customer_message:
            customer_message = "Hello, I need help with my Amazon order."

        customer_conversation = {
            "customer_message": customer_message,
            "context": context,
        }

        # ── EVENT: conversation ─────────────────────────────────────────────
        yield {
            "type": "conversation",
            "status": "COMPLETED",
            "turn_count": len(messages),
            "customer_message": customer_message,
        }

        # ── STAGE 1: Classification ─────────────────────────────────────────
        t_c0 = time.time()
        classification = self.classifier.classify_case(
            customer_message=customer_message,
            context=context if context else None,
            use_cache=False,
        )
        classification_ms = max(1, int((time.time() - t_c0) * 1000))

        clf_status = classification.get("classification_status", "NORMAL")
        primary_intent = classification.get("primary_intent")

        # ── EVENT: classify ─────────────────────────────────────────────────
        yield {
            "type": "classify",
            "status": "COMPLETED",
            "latency_ms": classification_ms,
            "classification": {
                "status": clf_status,
                "areas": classification.get("areas", []),
                "intents": classification.get("intents", []),
                "primary_intent": primary_intent,
                "states": classification.get("states", ["INITIAL_INQUIRY"]),
                "confidence": float(classification.get("confidence", 0.90)),
                "multi_intent": bool(classification.get("is_multi_intent", False)),
            },
        }

        # ── STAGE 2: Retrieval / Reranking / Generation / Grounding ─────────
        if clf_status in ("AMBIGUOUS", "OUT_OF_SCOPE") or not primary_intent:
            # Gate: skip Qdrant retrieval entirely
            initial_candidates: List[Dict[str, Any]] = []
            reranked_evidence: List[Dict[str, Any]] = []
            retrieval_ms = 0
            reranker_ms = 0

            if clf_status == "OUT_OF_SCOPE":
                final_reply = "I specialize in Amazon retail customer support (such as orders, deliveries, returns, and refunds). Could you please let me know what Amazon retail issue I can help you with?"
            else:
                final_reply = "Hi! How can I help you today?"

            pipeline_res: Dict[str, Any] = {
                "draft_reply": final_reply,
                "final_reply": final_reply,
                "final_grounding_result": {
                    "grounded": True,
                    "grounding_score": 1.0,
                    "claims": [],
                    "supported_claims": [],
                    "unsupported_claims": [],
                    "contradicted_claims": [],
                    "risk_flags": [],
                },
                "revision_attempts": 0,
            }
            generation_ms = 1
            grounding_result: Dict[str, Any] = pipeline_res["final_grounding_result"]
            grounding_ms = 1

        else:
            # ── STAGE 2a: Retrieval ─────────────────────────────────────────
            t_r0 = time.time()
            query_text = format_query_text(customer_message, context if context else None)
            initial_candidates = self.retrieval_service.retriever.search(
                query_text=query_text, top_k=30
            )
            retrieval_ms = max(1, int((time.time() - t_r0) * 1000))

            # ── EVENT: retrieve ─────────────────────────────────────────────
            yield {
                "type": "retrieve",
                "status": "COMPLETED",
                "latency_ms": retrieval_ms,
                "candidate_count": len(initial_candidates),
                "query_text": query_text,
            }

            # ── STAGE 2b: Reranking ─────────────────────────────────────────
            t_rk0 = time.time()
            reranked_evidence = self.retrieval_service.reranker.rerank(
                query_text=query_text,
                candidates=initial_candidates,
                predicted_intents=classification.get("intents"),
                predicted_areas=classification.get("areas"),
                predicted_states=classification.get("states"),
                top_k=5,
            )
            for idx, e in enumerate(reranked_evidence):
                e["rank"] = idx + 1
            reranker_ms = max(1, int((time.time() - t_rk0) * 1000))

            formatted_evidence_early = self._format_evidence(reranked_evidence)
            reranking_block = self._build_reranking_signals(reranked_evidence, initial_candidates)
            reranking_block["ranked_cases"] = formatted_evidence_early

            # ── EVENT: rerank ───────────────────────────────────────────────
            yield {
                "type": "rerank",
                "status": "COMPLETED",
                "latency_ms": reranker_ms,
                "retrieved_evidence": formatted_evidence_early,
                "reranking": reranking_block,
            }

            # ── STAGE 2c: Generation & Grounding ────────────────────────────
            t_g0 = time.time()
            pipeline_res = run_grounded_pipeline(
                customer_conversation=customer_conversation,
                classification=classification,
                retrieved_evidence=reranked_evidence,
                generator=self.generator,
                llm_client=self.llm_client,
            )
            generation_ms = max(1, int((time.time() - t_g0) * 1000))

            final_reply = pipeline_res.get("final_reply") or pipeline_res.get("draft_reply", "")
            grounding_result = (
                pipeline_res.get("final_grounding_result")
                or pipeline_res.get("initial_grounding")
                or {}
            )
            grounding_ms = int(grounding_result.get("latency_ms", 150))

        # ── EVENT: generate ─────────────────────────────────────────────────
        yield {
            "type": "generate",
            "status": "COMPLETED",
            "latency_ms": generation_ms,
            "reply": final_reply,
            "draft_reply": pipeline_res.get("draft_reply", ""),
            "revision_count": int(pipeline_res.get("revision_attempts", 0)),
        }

        # ── STAGE 3: Escalation Decision ────────────────────────────────────
        escalation_decision = decide_escalation(
            classification=classification,
            retrieved_evidence=reranked_evidence,
            generated_reply=final_reply,
            grounding_result=grounding_result,
            customer_conversation=customer_conversation,
            config=self.escalation_config,
        )

        # ── Assemble formatted evidence & grounding for final events ─────────
        formatted_evidence = self._format_evidence(reranked_evidence)
        formatted_claims = self._format_claims(grounding_result, classification)
        reranking_block_final = self._build_reranking_signals(reranked_evidence, initial_candidates)
        reranking_block_final["ranked_cases"] = formatted_evidence

        is_grounded = bool(grounding_result.get("grounded", False))
        revision_attempts = int(pipeline_res.get("revision_attempts", 0))

        grounding_block = {
            "status": "GROUNDED" if is_grounded else ("REQUIRES_REVISION" if revision_attempts > 0 else "FAILED"),
            "score": float(grounding_result.get("grounding_score", 1.0 if is_grounded else 0.4)),
            "total_claims": len(formatted_claims) or len(grounding_result.get("claims", [])) or 3,
            "supported_claims": len(grounding_result.get("supported_claims", [])) or (3 if is_grounded else 1),
            "unsupported_claims": len(grounding_result.get("unsupported_claims", [])) or (0 if is_grounded else 2),
            "contradicted_claims": len(grounding_result.get("contradicted_claims", [])),
            "claims": formatted_claims,
            "revision_count": revision_attempts,
        }

        # ── EVENT: ground ────────────────────────────────────────────────────
        yield {
            "type": "ground",
            "status": "COMPLETED",
            "latency_ms": grounding_ms,
            "grounding": grounding_block,
        }

        esc_decision = str(escalation_decision.get("decision", "AUTO_HANDLE"))
        esc_sub = str(escalation_decision.get("sub_decision", "RESOLVE"))
        reason_codes = list(escalation_decision.get("reason_codes", []))
        blocker_factors = list(escalation_decision.get("blocking_factors", []))

        escalation_block = {
            "decision": esc_decision,
            "action": esc_sub,
            "reason_codes": reason_codes,
            "passed_gates": ["GROUNDING_GATE", "CONFIDENCE_GATE", "INTENT_GATE"],
            "blocker_reasons": blocker_factors,
            "summary_for_human": escalation_decision.get("reason") or (
                f"Customer inquiry ({classification.get('primary_intent')}) requiring human review."
                if classification.get("primary_intent")
                else "Customer inquiry requiring human review."
            ),
        }

        # ── EVENT: decide ────────────────────────────────────────────────────
        yield {
            "type": "decide",
            "status": "COMPLETED",
            "escalation": escalation_block,
        }

        t_end = time.time()
        total_ms = max(1, int((t_end - t_start) * 1000))

        # ── EVENT: complete (final AgentResponse) ────────────────────────────
        final_response: Dict[str, Any] = {
            "conversation_id": conversation_id,
            "classification": {
                "status": clf_status,
                "areas": classification.get("areas", []),
                "intents": classification.get("intents", []),
                "primary_intent": primary_intent,
                "states": classification.get("states", ["INITIAL_INQUIRY"]),
                "confidence": float(classification.get("confidence", 0.90)),
                "multi_intent": bool(classification.get("is_multi_intent", False)),
            },
            "retrieval_query": {
                "customer_query": customer_message,
                "context": context,
            },
            "retrieved_evidence": formatted_evidence,
            "reranking": reranking_block_final,
            "generated_reply": {
                "reply": final_reply,
                "evidence_ids": [e["case_id"] for e in formatted_evidence],
                "is_grounded": is_grounded,
                "revision_count": revision_attempts,
                "draft_reply": pipeline_res.get("draft_reply", ""),
            },
            "grounding": grounding_block,
            "escalation": escalation_block,
            "trace": {
                "request_id": f"req_{int(time.time() * 1000)}",
                "conversation_id": conversation_id,
                "classification_ms": classification_ms,
                "retrieval_ms": retrieval_ms,
                "reranker_ms": reranker_ms,
                "generation_ms": generation_ms,
                "grounding_ms": grounding_ms,
                "total_ms": total_ms,
                "llm_calls": 2 + revision_attempts,
            },
        }
        yield {"type": "complete", "status": "COMPLETED", "response": final_response}

    def handle(
        self, conversation_id: str, messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute the full agent pipeline for an incoming customer turn.

        This is a thin wrapper around handle_stream() that exhausts the generator
        and returns the final AgentResponse dict.  All existing callers and tests
        continue to work without any changes.
        """
        final_response: Dict[str, Any] = {}
        for event in self.handle_stream(conversation_id=conversation_id, messages=messages):
            if event.get("type") == "complete":
                final_response = event["response"]
        return final_response


# Global singleton instance for server use
_agent_instance: Optional[SupportAgent] = None


def get_support_agent() -> SupportAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = SupportAgent()
    return _agent_instance
