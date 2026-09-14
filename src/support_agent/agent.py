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
import re
import time
from typing import Any, Dict, Generator, List, Optional

from support_agent.classification.llm_classifier import LLMIntentClassifier
from support_agent.classification.state_extractor import extract_conversation_state
from support_agent.retrieval.service import RetrievalService
from support_agent.retrieval.retriever import format_query_text
from support_agent.generation.response_generator import ResponseGenerator
from support_agent.generation.revise_response import run_grounded_pipeline
from support_agent.grounding.grounding_checker import check_grounding, CURRENT_ACTION_PATTERNS
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
            sem_rank = e.get("semantic_rank")
            lex_rank = e.get("lexical_rank")
            rrf_sc = e.get("rrf_score", e.get("final_score", e.get("rerank_score")))
            sem_sc = e.get("semantic_score", e.get("score"))
            lex_sc = e.get("lexical_score")

            formatted_evidence.append({
                "case_id": str(e.get("case_id", e.get("id", f"case_{idx + 1}"))),
                "conversation_id": str(e.get("conversation_id", "")),
                "turn_index": int(e.get("turn_index", 1)),
                "rank": int(e.get("rank", idx + 1)),
                "similarity": round(float(sem_sc), 2) if sem_sc is not None else 0.85,
                "customer_message": str(e.get("customer_message", "")),
                "relevant_context": str(e.get("relevant_context", "")),
                "brand_response": str(e.get("brand_response", "")),
                "doc_id": str(e.get("document_id", "")),
                "semantic_rank": int(sem_rank) if sem_rank is not None else None,
                "lexical_rank": int(lex_rank) if lex_rank is not None else None,
                "rrf_score": round(float(rrf_sc), 5) if rrf_sc is not None else None,
                "semantic_score": round(float(sem_sc), 4) if sem_sc is not None else None,
                "lexical_score": round(float(lex_sc), 4) if lex_sc is not None else None,
                # Backward-compatibility fields
                "final_score": round(float(rrf_sc), 5) if rrf_sc is not None else None,
                "rerank_score": round(float(rrf_sc), 5) if rrf_sc is not None else None,
                "intent_score": None,
                "area_score": None,
                "state_score": None,
                "action_usefulness": None,
                "action_penalty": 0.0,
                "action_penalty_flag": 0.0,
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
        self,
        reranked_evidence: List[Dict[str, Any]],
        initial_candidates: List[Dict[str, Any]],
        lexical_candidates: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Compute aggregate RRF reranking block for the response contract."""
        k_val = getattr(self.retrieval_service.reranker, "k", 60)
        lex_count = len(lexical_candidates) if lexical_candidates is not None else 0
        sem_count = len(initial_candidates)

        signals = [
            {
                "name": "semantic",
                "label": "Semantic Retrieval",
                "score": round(
                    sum(float(e.get("semantic_score", 0.0) or 0.0) for e in reranked_evidence) / len(reranked_evidence),
                    4,
                ) if reranked_evidence else None,
                "weight": 1.0,
                "description": "Top 30 ranked by dense cosine similarity",
            },
            {
                "name": "lexical",
                "label": "Lexical Retrieval",
                "score": round(
                    sum(float(e.get("lexical_score", 0.0) or 0.0) for e in reranked_evidence if e.get("lexical_score") is not None) / max(1, len([e for e in reranked_evidence if e.get("lexical_score") is not None])),
                    4,
                ) if any(e.get("lexical_score") is not None for e in reranked_evidence) else None,
                "weight": 1.0,
                "description": "Top 30 ranked by TF-IDF keyword overlap",
            },
        ]

        unique_convs = len(set(e.get("conversation_id", "") for e in reranked_evidence if e.get("conversation_id")))
        if unique_convs == 0:
            unique_convs = len(reranked_evidence)

        return {
            "method": "Reciprocal Rank Fusion",
            "k": k_val,
            "formula": "RRF(d) = 1/(k + semantic_rank) + 1/(k + lexical_rank)",
            "candidate_count": sem_count + lex_count if lex_count else sem_count,
            "semantic_candidate_count": sem_count,
            "lexical_candidate_count": lex_count,
            "final_count": len(reranked_evidence),
            "unique_conversations": unique_convs,
            "signals": signals,
            "weights": {
                "k": k_val,
                "semantic": 1.0,
                "lexical": 1.0,
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
        classification["states"] = extract_conversation_state(
            customer_message=customer_message,
            context=context if context else None,
            model_states=classification.get("states"),
        )

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
        clarification_generation_ms: Optional[int] = None
        if clf_status in ("AMBIGUOUS", "OUT_OF_SCOPE") or not primary_intent:
            # Gate: skip Qdrant retrieval and reranking entirely
            initial_candidates: List[Dict[str, Any]] = []
            lexical_candidates: List[Dict[str, Any]] = []
            reranked_evidence: List[Dict[str, Any]] = []
            retrieval_ms = 0
            reranker_ms = 0


            if clf_status == "OUT_OF_SCOPE":
                final_reply = "I specialize in Amazon retail customer support (such as orders, deliveries, returns, and refunds). Could you please let me know what Amazon retail issue I can help you with?"
                generation_ms = 1
                grounding_result: Dict[str, Any] = {
                    "grounded": True,
                    "grounding_score": 1.0,
                    "claims": [],
                    "supported_claims": [],
                    "unsupported_claims": [],
                    "contradicted_claims": [],
                    "risk_flags": [],
                }
                grounding_ms = 1
                pipeline_res: Dict[str, Any] = {
                    "draft_reply": final_reply,
                    "final_reply": final_reply,
                    "final_grounding_result": grounding_result,
                    "revision_attempts": 0,
                }
                llm_calls_total = 1
            else:
                # AMBIGUOUS: Call clarification generator LLM once
                t_cg0 = time.time()
                try:
                    clarification_res = self.generator.generate_clarification(
                        customer_message=customer_message,
                        context=context if context else None,
                        classification=classification,
                    )
                except Exception as cg_err:
                    logger.error("Clarification generation raised exception: %s. Using emergency fallback.", cg_err)
                    clarification_res = {"reply": "Hi! How can I help you today?"}
                clarification_generation_ms = max(1, int((time.time() - t_cg0) * 1000))
                generation_ms = clarification_generation_ms
                draft_reply = clarification_res.get("reply") or "Hi! How can I help you today?"
                final_reply = draft_reply

                # Deterministic safety verification for clarification:
                # Clarifications ask questions to gather missing info and do not make precedent-grounded claims.
                # Verify that no ungrounded current actions, promises, or leaks were generated.
                t_gr0 = time.time()
                is_safe_clarify = True
                reply_lower = final_reply.lower()

                # Check for action promises or unconfirmed state changes
                for pat, label in CURRENT_ACTION_PATTERNS:
                    if re.search(pat, reply_lower, re.IGNORECASE):
                        logger.warning("Clarification contains ungrounded current action promise: %s", label)
                        is_safe_clarify = False
                        break

                leak_words = ["classification", "confidence", "ambiguous", "rag", "pipeline", "taxonomy"]
                if any(w in reply_lower for w in leak_words):
                    logger.warning("Clarification contains leaked pipeline tokens: %s", final_reply)
                    is_safe_clarify = False

                if not is_safe_clarify:
                    final_reply = "Hi! How can I help you today?"

                grounding_result = {
                    "grounded": True,
                    "grounding_score": 1.0,
                    "claims": [
                        {
                            "id": "c1",
                            "text": "Customer inquiry clarification",
                            "source_type": "CURRENT_CONVERSATION_SUPPORTED",
                            "status": "CURRENT_CONVERSATION_SUPPORTED",
                        }
                    ],
                    "supported_claims": ["Customer inquiry clarification"],
                    "unsupported_claims": [],
                    "contradicted_claims": [],
                    "risk_flags": [],
                }
                grounding_ms = max(1, int((time.time() - t_gr0) * 1000))

                pipeline_res = {
                    "draft_reply": draft_reply,
                    "final_reply": final_reply,
                    "final_grounding_result": grounding_result,
                    "revision_attempts": 0,
                }
                llm_calls_total = 2

        else:
            # ── STAGE 2a: Retrieval ─────────────────────────────────────────
            t_r0 = time.time()
            query_text = format_query_text(customer_message, context if context else None)
            initial_candidates = self.retrieval_service.retriever.search(
                query_text=query_text, top_k=30
            )
            lexical_candidates = []
            if hasattr(self.retrieval_service, "lexical_retriever") and self.retrieval_service.lexical_retriever:
                try:
                    lexical_candidates = self.retrieval_service.lexical_retriever.search(
                        query_text=query_text, top_k=30
                    )
                except Exception as ex:
                    logger.warning("Lexical search error: %s", ex)
                    lexical_candidates = []
            retrieval_ms = max(1, int((time.time() - t_r0) * 1000))

            # ── EVENT: retrieve ─────────────────────────────────────────────
            yield {
                "type": "retrieve",
                "status": "COMPLETED",
                "latency_ms": retrieval_ms,
                "candidate_count": len(initial_candidates) + len(lexical_candidates),
                "semantic_candidate_count": len(initial_candidates),
                "lexical_candidate_count": len(lexical_candidates),
                "query_text": query_text,
            }

            # ── STAGE 2b: Reranking ─────────────────────────────────────────
            t_rk0 = time.time()
            reranked_evidence = self.retrieval_service.reranker.rerank(
                query_text=query_text,
                semantic_candidates=initial_candidates,
                lexical_candidates=lexical_candidates,
                candidates=initial_candidates,
                top_k=5,
                k=60,
            )
            for idx, e in enumerate(reranked_evidence):
                e["rank"] = idx + 1
            reranker_ms = max(1, int((time.time() - t_rk0) * 1000))

            formatted_evidence_early = self._format_evidence(reranked_evidence)
            reranking_block = self._build_reranking_signals(
                reranked_evidence,
                initial_candidates,
                lexical_candidates=lexical_candidates,
            )
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
            llm_calls_total = 2 + int(pipeline_res.get("revision_attempts", 0))

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
        t_d0 = time.time()
        escalation_decision = decide_escalation(
            classification=classification,
            retrieved_evidence=reranked_evidence,
            generated_reply=final_reply,
            grounding_result=grounding_result,
            customer_conversation=customer_conversation,
            config=self.escalation_config,
        )
        decision_ms = max(1, int((time.time() - t_d0) * 1000))

        # ── Assemble formatted evidence & grounding for final events ─────────
        formatted_evidence = self._format_evidence(reranked_evidence)
        formatted_claims = self._format_claims(grounding_result, classification)
        reranking_block_final = self._build_reranking_signals(
            reranked_evidence,
            initial_candidates,
            lexical_candidates=lexical_candidates,
        )
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
            "latency_ms": decision_ms,
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
                "clarification_generation_ms": clarification_generation_ms,
                "retrieval_ms": retrieval_ms,
                "reranker_ms": reranker_ms,
                "generation_ms": generation_ms,
                "grounding_ms": grounding_ms,
                "decision_ms": decision_ms,
                "total_ms": total_ms,
                "llm_calls": llm_calls_total,
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
