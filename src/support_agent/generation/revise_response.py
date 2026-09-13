"""Response Revision Module — Phase 9.

If grounding finds unsupported or contradicted claims, this module:

Option A: Revise the response using only supported evidence.
Option B: Request missing information (if facts are simply unknown).
Option C: Recommend human escalation (if revision keeps failing).

Maximum revision attempts: 2
After 2 failed attempts → grounding_status=FAILED, needs_human_review=True.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from support_agent.llm.client import BaseLLMClient, get_llm_client
from support_agent.generation.response_generator import ResponseGenerator
from support_agent.grounding.grounding_checker import check_grounding

logger = logging.getLogger(__name__)

MAX_REVISION_ATTEMPTS = 2

_REVISION_SYSTEM_PROMPT = """You are an Amazon customer-support response assistant revising a draft reply.

The previous draft contained unsupported, contradicted, or incorrectly promoted claims.

CORE GROUNDING RULE:
Historical evidence shows how Amazon previously handled similar cases; it NEVER establishes what Amazon has already done for the current customer. Never state or imply that an action has already been taken on the current account unless the current conversation explicitly confirms it.

You MUST produce a revised reply following this priority:
1. Remove ALL unsupported or contradicted current-case claims (e.g. "We've received...", "We've checked...", "We can offer you...").
2. If an action or policy is mentioned in historical evidence, convert it to a SAFE GENERAL INSTRUCTION if appropriate (e.g. convert "We can offer you delivery tomorrow" or "We've opened a case" into general instructions like "You may explore safe place delivery options in your account" or "You can contact support via chat").
3. If specific customer facts or order details are needed to proceed, ASK FOR MISSING INFORMATION (e.g. "Could you please provide your order number?").
4. If the issue cannot be safely resolved with available evidence, suggest ESCALATION or contacting human customer support.
5. Remain helpful, professional, empathetic, and concise.

Return a single valid JSON object with exactly these keys:
{
  "reply": "revised reply text",
  "evidence_ids": ["list of evidence IDs used — only from the supplied evidence"],
  "needs_human_review": false,
  "revision_strategy": "one of: REWRITE_WITHOUT_UNSUPPORTED / CONVERT_TO_SAFE_GENERAL / REQUEST_INFO / ESCALATE"
}
"""


def _build_revision_prompt(
    customer_conversation: Dict[str, Any],
    classification: Dict[str, Any],
    retrieved_evidence: List[Dict[str, Any]],
    original_reply: str,
    grounding_result: Dict[str, Any],
    attempt: int,
) -> str:
    """Build the revision prompt with all context and the list of problems."""
    context = customer_conversation.get("context", "")
    message = customer_conversation.get("customer_message", "")

    ev_parts = []
    for i, ev in enumerate(retrieved_evidence, 1):
        doc_id = ev.get("document_id") or ev.get("id") or f"evidence_{i}"
        customer_msg = ev.get("customer_message", "")
        brand_resp = ev.get("brand_response", "")
        ev_parts.append(
            f"Evidence {i} (ID: {doc_id})\n"
            f"Customer: {customer_msg}\n"
            f"Amazon: {brand_resp}"
        )

    unsupported = grounding_result.get("unsupported_claims", [])
    contradicted = grounding_result.get("contradicted_claims", [])
    risk_flags = grounding_result.get("risk_flags", [])
    suggestion = grounding_result.get("revision_suggestion", "")

    return f"""REVISION ATTEMPT {attempt} of {MAX_REVISION_ATTEMPTS}

CURRENT CONVERSATION
--------------------
Context: {context}
Customer: {message}

CLASSIFICATION
--------------
Primary intent: {classification.get('primary_intent', 'UNKNOWN')}
Intents: {classification.get('intents', [])}
States: {classification.get('states', [])}

HISTORICAL EVIDENCE
-------------------
{chr(10).join(ev_parts) if ev_parts else "No historical evidence retrieved."}

ORIGINAL DRAFT REPLY (to be revised)
--------------------------------------
{original_reply}

PROBLEMS DETECTED BY GROUNDING VERIFIER
----------------------------------------
Unsupported claims:
{chr(10).join(f'  - {c}' for c in unsupported) if unsupported else '  (none)'}

Contradicted claims:
{chr(10).join(f'  - {c}' for c in contradicted) if contradicted else '  (none)'}

Risk flags:
{chr(10).join(f'  - {f}' for f in risk_flags) if risk_flags else '  (none)'}

Revision suggestion: {suggestion}

Please produce a revised reply that fixes all the problems above.
If you cannot produce a grounded reply with the available evidence,
set revision_strategy to REQUEST_INFO or ESCALATE."""


def revise_response(
    customer_conversation: Dict[str, Any],
    classification: Dict[str, Any],
    retrieved_evidence: List[Dict[str, Any]],
    original_reply: str,
    initial_grounding_result: Dict[str, Any],
    llm_client: Optional[BaseLLMClient] = None,
    grounding_prompt_path: Optional[str] = None,
    generator_evidence_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Attempt to revise a draft reply that failed grounding.

    Parameters
    ----------
    customer_conversation : dict
        {'customer_message': str, 'context': str}
    classification : dict
        ClassifierV2 output.
    retrieved_evidence : list of dict
        Reranked evidence items.
    original_reply : str
        The draft reply that failed grounding.
    initial_grounding_result : dict
        The grounding result that triggered the revision.
    llm_client : BaseLLMClient, optional
    grounding_prompt_path : str, optional
        Path to grounding_v1.md override.
    generator_evidence_ids : list of str, optional

    Returns
    -------
    dict with keys:
        final_reply, grounding_status, needs_human_review,
        revision_attempts, revision_history, final_grounding_result
    """
    if llm_client is None:
        llm_client = get_llm_client()

    history: List[Dict[str, Any]] = []
    current_reply = original_reply
    current_grounding = initial_grounding_result

    for attempt in range(1, MAX_REVISION_ATTEMPTS + 1):
        logger.info(f"[RevisionLoop] Attempt {attempt}/{MAX_REVISION_ATTEMPTS}")

        revision_prompt = _build_revision_prompt(
            customer_conversation=customer_conversation,
            classification=classification,
            retrieved_evidence=retrieved_evidence,
            original_reply=current_reply,
            grounding_result=current_grounding,
            attempt=attempt,
        )

        revised_reply = current_reply  # fallback
        revision_strategy = "REWRITE_WITHOUT_UNSUPPORTED"
        revised_evidence_ids: List[str] = []

        try:
            llm_resp = llm_client.generate(
                prompt=revision_prompt,
                system_prompt=_REVISION_SYSTEM_PROMPT,
                json_mode=True,
                temperature=0.0,
                max_tokens=600,
            )
            from support_agent.llm.client import parse_json_from_text
            rev_output = parse_json_from_text(llm_resp.content)
            revised_reply = rev_output.get("reply", current_reply)
            revision_strategy = rev_output.get("revision_strategy", "REWRITE_WITHOUT_UNSUPPORTED")
            revised_evidence_ids = rev_output.get("evidence_ids", [])

            # If the model chose to escalate or request info, stop looping
            if revision_strategy in ("ESCALATE", "REQUEST_INFO"):
                logger.info(f"[RevisionLoop] Model chose strategy '{revision_strategy}' — stopping early")
                new_grounding = {
                    "grounded": True,  # safe response
                    "grounding_score": 1.0,
                    "unsupported_claims": [],
                    "contradicted_claims": [],
                    "risk_flags": [],
                    "needs_revision": False,
                    "needs_human_review": revision_strategy == "ESCALATE",
                    "revision_suggestion": "",
                    "evidence_used": [],
                    "claims": [],
                    "supported_claims": [],
                    "partially_supported_claims": [],
                    "deterministic_flags": [],
                    "invalid_evidence_ids": [],
                    "llm_used": True,
                }
                history.append({
                    "attempt": attempt,
                    "reply": revised_reply,
                    "strategy": revision_strategy,
                    "grounding": new_grounding,
                })
                return _build_revision_result(
                    final_reply=revised_reply,
                    grounding_status="PASSED" if revision_strategy == "REQUEST_INFO" else "ESCALATED",
                    needs_human_review=revision_strategy == "ESCALATE",
                    revision_attempts=attempt,
                    history=history,
                    final_grounding=new_grounding,
                )

        except Exception as e:
            logger.warning(f"[RevisionLoop] LLM revision call failed on attempt {attempt}: {e}")
            history.append({
                "attempt": attempt,
                "reply": current_reply,
                "strategy": "ERROR",
                "error": str(e),
                "grounding": current_grounding,
            })
            # Don't retry if LLM is down — go to human review
            return _build_revision_result(
                final_reply=current_reply,
                grounding_status="FAILED",
                needs_human_review=True,
                revision_attempts=attempt,
                history=history,
                final_grounding=current_grounding,
                error=f"LLM revision failed: {e}",
            )

        # Re-check grounding on the revised reply
        new_grounding = check_grounding(
            customer_conversation=customer_conversation,
            classification=classification,
            retrieved_evidence=retrieved_evidence,
            generated_reply=revised_reply,
            llm_client=llm_client,
            prompt_path=grounding_prompt_path,
            generator_evidence_ids=revised_evidence_ids,
        )

        history.append({
            "attempt": attempt,
            "reply": revised_reply,
            "strategy": revision_strategy,
            "grounding": new_grounding,
        })

        if new_grounding.get("grounded"):
            logger.info(f"[RevisionLoop] Grounding PASSED on attempt {attempt}")
            return _build_revision_result(
                final_reply=revised_reply,
                grounding_status="PASSED",
                needs_human_review=False,
                revision_attempts=attempt,
                history=history,
                final_grounding=new_grounding,
            )

        # Still failing — update for next attempt
        current_reply = revised_reply
        current_grounding = new_grounding

    # Exhausted all attempts
    logger.warning(f"[RevisionLoop] Grounding FAILED after {MAX_REVISION_ATTEMPTS} attempts — escalating to human")
    return _build_revision_result(
        final_reply=current_reply,
        grounding_status="FAILED",
        needs_human_review=True,
        revision_attempts=MAX_REVISION_ATTEMPTS,
        history=history,
        final_grounding=current_grounding,
    )


def _build_revision_result(
    final_reply: str,
    grounding_status: str,
    needs_human_review: bool,
    revision_attempts: int,
    history: List[Dict[str, Any]],
    final_grounding: Dict[str, Any],
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """Assemble the final revision result dict."""
    result: Dict[str, Any] = {
        "final_reply": final_reply,
        "grounding_status": grounding_status,
        "needs_human_review": needs_human_review,
        "revision_attempts": revision_attempts,
        "revision_history": history,
        "final_grounding_result": final_grounding,
    }
    if error:
        result["error"] = error
    return result


# ---------------------------------------------------------------------------
# Full pipeline helper
# ---------------------------------------------------------------------------

def run_grounded_pipeline(
    customer_conversation: Dict[str, Any],
    classification: Dict[str, Any],
    retrieved_evidence: List[Dict[str, Any]],
    generator: Optional[Any] = None,
    llm_client: Optional[BaseLLMClient] = None,
    grounding_prompt_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run the full grounded response pipeline:
        Generation → Grounding → (Revision if needed)

    Parameters
    ----------
    customer_conversation : dict
        {'customer_message': str, 'context': str}
    classification : dict
        ClassifierV2 output.
    retrieved_evidence : list of dict
        Reranked evidence items.
    generator : ResponseGenerator, optional
        Defaults to a new ResponseGenerator().
    llm_client : BaseLLMClient, optional
    grounding_prompt_path : str, optional

    Returns
    -------
    dict with keys:
        draft_reply, initial_grounding, final_reply, grounding_status,
        needs_human_review, revision_attempts, revision_history,
        final_grounding_result, pipeline_stage
    """
    if llm_client is None:
        llm_client = get_llm_client()

    if generator is None:
        generator = ResponseGenerator(llm_client=llm_client)

    customer_message = customer_conversation.get("customer_message", "")
    context = customer_conversation.get("context", "")

    # Step 1: Generate draft
    gen_output = generator.generate_response(
        customer_message=customer_message,
        context=context,
        classification=classification,
        historical_evidence=retrieved_evidence,
    )
    draft_reply = gen_output.get("reply", "")
    generator_evidence_ids = gen_output.get("evidence_ids", [])

    # Step 2: Ground check
    grounding = check_grounding(
        customer_conversation=customer_conversation,
        classification=classification,
        retrieved_evidence=retrieved_evidence,
        generated_reply=draft_reply,
        llm_client=llm_client,
        prompt_path=grounding_prompt_path,
        generator_evidence_ids=generator_evidence_ids,
    )

    if grounding.get("grounded"):
        return {
            "draft_reply": draft_reply,
            "initial_grounding": grounding,
            "final_reply": draft_reply,
            "grounding_status": "PASSED",
            "needs_human_review": grounding.get("needs_human_review", False),
            "revision_attempts": 0,
            "revision_history": [],
            "final_grounding_result": grounding,
            "pipeline_stage": "generation_passed_grounding",
            "generator_output": gen_output,
        }

    # Step 3: Revision loop
    revision_result = revise_response(
        customer_conversation=customer_conversation,
        classification=classification,
        retrieved_evidence=retrieved_evidence,
        original_reply=draft_reply,
        initial_grounding_result=grounding,
        llm_client=llm_client,
        grounding_prompt_path=grounding_prompt_path,
        generator_evidence_ids=generator_evidence_ids,
    )

    return {
        "draft_reply": draft_reply,
        "initial_grounding": grounding,
        "final_reply": revision_result.get("final_reply", draft_reply),
        "grounding_status": revision_result.get("grounding_status", "UNKNOWN"),
        "needs_human_review": revision_result.get("needs_human_review", True),
        "revision_attempts": revision_result.get("revision_attempts", 0),
        "revision_history": revision_result.get("revision_history", []),
        "final_grounding_result": revision_result.get("final_grounding_result", grounding),
        "pipeline_stage": "generation_revised_after_grounding",
        "generator_output": gen_output,
    }
