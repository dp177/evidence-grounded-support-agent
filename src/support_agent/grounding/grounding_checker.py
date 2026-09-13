"""Grounding Checker — Phase 9 & Phase 9.1.

Checks whether a generated support reply is actually supported by:
  1. The current customer conversation
  2. Retrieved historical evidence

Phase 9.1 Tightened Grounding Rules:
  - Historical evidence demonstrates "How Amazon handled a similar historical situation."
  - Historical evidence does NOT establish "What Amazon has already done for the current customer."
  - Current-action claims ("We've received...", "We can offer you...", "Your refund is...")
    require CURRENT_CONVERSATION support; historical evidence alone is insufficient.
  - Safe generalizations (e.g. "You can contact support by phone") are permitted when
    supported by historical evidence.
  - Every claim is assigned a source_type:
      CURRENT_CONVERSATION_SUPPORTED
      HISTORICAL_EVIDENCE_SUPPORTED
      BOTH
      UNSUPPORTED
      CONTRADICTED

Uses a hybrid strategy:
  - Deterministic checks first (hard safety keywords, current-action patterns, amounts, IDs)
  - LLM semantic entailment for residual claim verification
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from support_agent.llm.client import BaseLLMClient, get_llm_client, parse_json_from_text

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PROMPT_PATH = Path("prompts/grounding_v1.md")

# Claim source types (Task 1 & Task 5)
SOURCE_TYPE_CURRENT_CONV = "CURRENT_CONVERSATION_SUPPORTED"
SOURCE_TYPE_HISTORICAL = "HISTORICAL_EVIDENCE_SUPPORTED"
SOURCE_TYPE_BOTH = "BOTH"
SOURCE_TYPE_UNSUPPORTED = "UNSUPPORTED"
SOURCE_TYPE_CONTRADICTED = "CONTRADICTED"

VALID_SOURCE_TYPES = {
    SOURCE_TYPE_CURRENT_CONV,
    SOURCE_TYPE_HISTORICAL,
    SOURCE_TYPE_BOTH,
    SOURCE_TYPE_UNSUPPORTED,
    SOURCE_TYPE_CONTRADICTED,
}

# Strict current-action patterns (Task 3)
CURRENT_ACTION_PATTERNS: List[tuple[str, str]] = [
    (r"\bwe('ve| have) received\b", "We've received"),
    (r"\bwe('ve| have) checked\b", "We've checked"),
    (r"\bwe('ve| have) confirmed\b", "We've confirmed"),
    (r"\bwe('ve| have) opened\b", "We've opened"),
    (r"\bwe('ve| have) escalated\b", "We've escalated"),
    (r"\bwe('ve| have) issued\b", "We've issued"),
    (r"\bwe('ve| have) refunded\b", "We've refunded"),
    (r"\bwe('ve| have) sent\b", "We've sent"),
    (r"\bwe (can|are able to) offer you\b", "We can offer you"),
    (r"\byour order is\b", "Your order is"),
    (r"\byour refund (is|has been|was)\b", "Your refund is/has been"),
    (r"\byour account has\b", "Your account has"),
]

# Claim categories that require explicit evidence support
HIGH_RISK_KEYWORDS: List[str] = [
    # Refund
    r"\brefund\b", r"\brefunded\b", r"\brefunding\b", r"\brefund has been\b",
    r"\brefund (was|is|will be|has been) (approved|confirmed|issued|processed|sent)\b",
    r"\byou(r| will)? (get|receive|have) (a )?refund\b",
    r"\bmoney (back|returned|refunded)\b",
    r"\bcredit (has been|will be|was) (applied|issued|added)\b",
    # Delivery
    r"\bdeliver(y|ed|ing)?\b", r"\bship(ped|ping|s)?\b",
    r"\barriv(e|es|ed|al)\b", r"\bexpected delivery\b",
    r"\bguarante(e|ed)?\b",
    # Dates and timing — specific patterns
    r"\bguarante(e|ed)?.{0,30}\d+\s*(business\s+)?days?\b",
    r"\bby (monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    r"\bby\s+(tomorrow|tonight|today)\b",
    # Order status
    r"\border (has been|was|is) (cancelled|canceled|shipped|dispatched|confirmed)\b",
    r"\bcancell?(ation|ed|ing)?\b",
    # Replacement / compensation
    r"\breplacement\b", r"\bsent.{0,20}replacement\b",
    r"\bcompensati(on|ng)\b", r"\b(given|issued|offered).{0,15}compensati\b",
    # Eligibility
    r"\beligibl(e|ility)\b",
    # Account actions
    r"\baccount (has been|was|is) (reset|closed|unlocked|suspended|updated)\b",
    # Policy statements presented as facts
    r"\bour policy (is|states|says|allows|requires)\b",
    r"\bpolicy (is|states|requires|allows)\b",
    # Promises
    r"\bwe will\b", r"\bi will\b", r"\bwe (have|have already)\b",
    r"\bwill (contact|call|email|follow up|process)\b",
    # Support channels
    r"\b(contact|reach) us (by|via|through|on)\b",
    r"\b(chat|phone|email) (support|us|channel)\b",
]

# Phrases that are clearly generic politeness — never need evidence
POLITENESS_PATTERNS: List[str] = [
    r"^(i'?m?\s+)?(so\s+)?(very\s+)?sorry",
    r"^thank(s| you)",
    r"^(i\s+)?understand",
    r"^(i\s+)?apologi",
    r"^(we|i)\s+(are\s+)?here to help",
    r"^(please (let|feel free|don't hesitate))",
    r"^how (can|may) (i|we) help",
    r"^i hope",
    r"^i'd be (happy|glad) to",
    r"^(is there|are there) anything",
]

# Hard safety trigger phrases — immediate fail unless explicitly in current conversation
HARD_SAFETY_PATTERNS: List[str] = [
    r"(refund|money).{0,30}(has been|have been|was|is) (issued|processed|sent|approved|confirmed)",
    r"(we|i|amazon).{0,20}(have|has|already) (issued|processed|approved|confirmed|sent).{0,20}(refund|credit|money)",
    r"your (refund|money|credit).{0,30}(is|will be|are).{0,30}(arriving|on its way|coming|in \d+ days)",
    r"refund.{0,20}(will arrive|arrives|is coming).{0,20}(by|before|on).{0,30}(tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
    r"(delivery|order|package).{0,20}guaranteed",
    r"(we|i|amazon).{0,20}(have|has) (cancelled|canceled|replaced|compensated|issued)",
    r"compensation.{0,20}(has been|have been|was|is) (approved|issued|confirmed|sent)",
    r"(you are|you're|you have been) (eligible|approved|confirmed)",
    r"your account (has been|was|is) (updated|reset|changed|unlocked|closed)",
]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _is_politeness_only(sentence: str) -> bool:
    """Return True if the sentence is generic politeness that needs no evidence."""
    s = sentence.strip().lower()
    if len(s) < 5:
        return True
    for pat in POLITENESS_PATTERNS:
        if re.search(pat, s, re.IGNORECASE):
            return True
    return False


def _contains_high_risk_claim(text: str) -> bool:
    """Return True if the text contains any high-risk claim pattern."""
    for pat in HIGH_RISK_KEYWORDS:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def _is_current_conversation_supported(phrase_or_sent: str, conv_text: str) -> bool:
    """Check if an asserted current-case claim is explicitly confirmed in the current conversation."""
    if not conv_text or not conv_text.strip():
        return False
    s = phrase_or_sent.lower()
    c = conv_text.lower()

    # Refund issuance/approval (e.g. Test D: "Amazon emailed me saying my refund was issued")
    if "refund" in s and any(w in s for w in ("issued", "processed", "sent", "approved", "confirmed")):
        return bool(
            re.search(r"\brefund.{0,25}(was|has been|is) (issued|processed|sent|approved|confirmed)\b", c)
            or re.search(r"\b(issued|processed|sent|approved|confirmed).{0,25}refund\b", c)
        )

    # We've received
    if re.search(r"\bwe('ve| have) received\b", s):
        m = re.search(r"\bwe('ve| have) received (?:your )?([a-z0-9_-]+)", s)
        if m:
            item = m.group(2)
            return bool(
                re.search(rf"\b(received|got|have).{{0,15}}{item}\b", c)
                or re.search(rf"\b{item}.{{0,15}}(received|got)\b", c)
            )
        return "received" in c

    # We can offer you
    if re.search(r"\bwe (can|are able to) offer you\b", s):
        m = re.search(r"\bwe (can|are able to) offer you (?:a |an )?([a-z0-9_-]+)", s)
        if m:
            opt = m.group(2)
            return opt in c and ("offer" in c or "option" in c)
        return "offer" in c

    # We've checked / confirmed / opened / escalated / sent / refunded
    for action in ["checked", "confirmed", "opened", "escalated", "sent", "refunded"]:
        if re.search(rf"\bwe('ve| have) {action}\b", s):
            return bool(re.search(rf"\b(have|we|already|was) {action}\b", c))

    # Your order is ...
    if re.search(r"\byour order is\b", s):
        m = re.search(r"\byour order is (?:currently |now )?([a-z0-9_-]+)", s)
        if m:
            stat = m.group(1)
            if stat in ("delayed", "cancelled", "canceled", "delivered", "shipped", "arriving", "lost"):
                return stat in c
        return False

    # Your account has ...
    if re.search(r"\byour account has\b", s):
        return "your account" in c

    return False


def _detect_hard_safety_violations(reply: str, conv_text: str = "") -> List[str]:
    """Deterministically detect hard safety rule violations in the reply.

    If the fact is explicitly established in the CURRENT CONVERSATION,
    it is not considered an invented fact.
    """
    violations = []
    for pat in HARD_SAFETY_PATTERNS:
        m = re.search(pat, reply, re.IGNORECASE)
        if m:
            matched = m.group(0)
            if conv_text and _is_current_conversation_supported(matched, conv_text):
                continue
            violations.append(f"Hard safety violation: matched pattern → '{matched}'")
    return violations


def _detect_current_action_violations(reply: str, conv_text: str = "") -> List[Dict[str, Any]]:
    """Detect current-action assertions that lack current-conversation support (Task 3)."""
    violations = []
    sentences = _extract_sentences(reply)
    for sent in sentences:
        for pat, pat_name in CURRENT_ACTION_PATTERNS:
            m = re.search(pat, sent, re.IGNORECASE)
            if m:
                if not _is_current_conversation_supported(sent, conv_text):
                    violations.append({
                        "sentence": sent,
                        "matched": m.group(0),
                        "pattern_name": pat_name,
                        "message": f"Unsupported current action/promise '{m.group(0)}' not confirmed in current conversation",
                    })
                break
    return violations


def _extract_evidence_ids(retrieved_evidence: List[Dict[str, Any]]) -> List[str]:
    """Extract valid document IDs from the retrieved evidence list."""
    ids = []
    for ev in retrieved_evidence:
        doc_id = ev.get("document_id") or ev.get("id") or ev.get("doc_id")
        if doc_id:
            ids.append(str(doc_id))
    return ids


def _validate_evidence_ids(claimed_ids: List[str], valid_ids: List[str]) -> List[str]:
    """Return a list of claimed IDs that do NOT exist in valid_ids."""
    valid_set = set(valid_ids) | {"CURRENT_CONVERSATION"}
    return [cid for cid in claimed_ids if cid not in valid_set]


def _extract_sentences(text: str) -> List[str]:
    """Split reply into sentences for claim analysis."""
    raw = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in raw if s.strip()]


def _build_conversation_text(customer_conversation: Dict[str, Any]) -> str:
    """Format the current conversation for inclusion in grounding prompt."""
    parts = []
    context = customer_conversation.get("context", "")
    message = customer_conversation.get("customer_message", "")
    if context:
        parts.append(f"Context:\n{context}")
    if message:
        parts.append(f"Customer:\n{message}")
    return "\n".join(parts)


def _build_evidence_text(retrieved_evidence: List[Dict[str, Any]]) -> str:
    """Format retrieved evidence for inclusion in grounding prompt."""
    if not retrieved_evidence:
        return "No historical evidence retrieved."
    parts = []
    for i, ev in enumerate(retrieved_evidence, 1):
        doc_id = ev.get("document_id") or ev.get("id") or f"evidence_{i}"
        customer_msg = ev.get("customer_message", "")
        brand_resp = ev.get("brand_response", "")
        context = ev.get("relevant_context", "") or ev.get("context", "")
        parts.append(f"\nEvidence {i} (ID: {doc_id})")
        if customer_msg:
            parts.append(f"Customer: {customer_msg}")
        if context:
            parts.append(f"Context: {context}")
        if brand_resp:
            parts.append(f"Amazon: {brand_resp}")
    return "\n".join(parts)


def _load_system_prompt(prompt_path: Optional[str] = None) -> str:
    """Load grounding system prompt from file."""
    path = Path(prompt_path) if prompt_path else _PROMPT_PATH
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        logger.warning(f"Could not load grounding prompt from {path}: {e}. Using inline fallback.")
        return (
            "You are evaluating whether a generated customer-support reply is supported "
            "by the supplied conversation and retrieved evidence. "
            "Historical evidence demonstrates how Amazon handled similar cases; it does NOT prove "
            "that the same action has been taken for the current customer. "
            "Current-action assertions require CURRENT_CONVERSATION support. "
            "Return structured JSON only."
        )


# ---------------------------------------------------------------------------
# Deterministic pre-checks
# ---------------------------------------------------------------------------

def _deterministic_precheck(
    reply: str,
    customer_conversation: Dict[str, Any],
    retrieved_evidence: List[Dict[str, Any]],
    valid_evidence_ids: List[str],
    generator_evidence_ids: List[str],
) -> Dict[str, Any]:
    """Run all deterministic checks before sending to LLM."""
    risk_flags: List[str] = []
    deterministic_unsupported: List[str] = []
    deterministic_claims: List[Dict[str, Any]] = []
    invalid_ids: List[str] = []

    conv_text = (
        str(customer_conversation.get("context", "") or "")
        + " "
        + str(customer_conversation.get("customer_message", "") or "")
    ).strip()

    # 1. Hard safety rule violations
    violations = _detect_hard_safety_violations(reply, conv_text)
    risk_flags.extend(violations)

    # 2. Strict current-action patterns (Task 3)
    action_violations = _detect_current_action_violations(reply, conv_text)
    for act_v in action_violations:
        msg = act_v["message"]
        sent = act_v["sentence"]
        risk_flags.append(msg)
        if sent not in deterministic_unsupported:
            deterministic_unsupported.append(sent)
        deterministic_claims.append({
            "claim": sent,
            "claim_text": sent,
            "source_type": SOURCE_TYPE_UNSUPPORTED,
            "evidence_ids": [],
            "support_status": "UNSUPPORTED",
            "status": "UNSUPPORTED",
            "reason": msg,
            "explanation": msg,
        })

    # 3. Validate evidence IDs claimed by the generator
    if generator_evidence_ids:
        invalid_ids = _validate_evidence_ids(generator_evidence_ids, valid_evidence_ids)
        for inv_id in invalid_ids:
            risk_flags.append(f"Invented evidence ID: '{inv_id}' not in retrieved evidence")

    # 4. Specific number / amount / date contradiction
    reply_amounts = re.findall(r"\$[\d,]+(?:\.\d+)?|\d+\s*dollars?", reply, re.IGNORECASE)
    ev_text = " ".join(
        (ev.get("customer_message", "") + " " + ev.get("brand_response", ""))
        for ev in retrieved_evidence
    )
    all_source_text = conv_text + " " + ev_text
    for amt in reply_amounts:
        if amt.replace(",", "").replace("$", "").replace("dollars", "").strip() not in all_source_text:
            msg = f"Specific amount '{amt}' not found in any evidence"
            deterministic_unsupported.append(msg)
            risk_flags.append(f"Unsupported specific amount: '{amt}'")
            deterministic_claims.append({
                "claim": f"Amount {amt}",
                "claim_text": f"Amount {amt}",
                "source_type": SOURCE_TYPE_UNSUPPORTED,
                "evidence_ids": [],
                "support_status": "UNSUPPORTED",
                "status": "UNSUPPORTED",
                "reason": msg,
                "explanation": msg,
            })

    return {
        "risk_flags": risk_flags,
        "deterministic_unsupported": deterministic_unsupported,
        "deterministic_claims": deterministic_claims,
        "invalid_evidence_ids": invalid_ids,
        "has_hard_violations": len(violations) > 0 or len(action_violations) > 0,
        "conv_text": conv_text,
    }


# ---------------------------------------------------------------------------
# Main grounding function
# ---------------------------------------------------------------------------

def check_grounding(
    customer_conversation: Dict[str, Any],
    classification: Dict[str, Any],
    retrieved_evidence: List[Dict[str, Any]],
    generated_reply: str,
    llm_client: Optional[BaseLLMClient] = None,
    prompt_path: Optional[str] = None,
    generator_evidence_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Verify whether a generated support reply is grounded in the conversation
    and retrieved evidence.

    Returns dict with keys:
        grounded, grounding_score, supported_claims, partially_supported_claims,
        unsupported_claims, contradicted_claims, evidence_used,
        risk_flags, needs_revision, needs_human_review,
        claims (full per-claim detail with source_type), revision_suggestion,
        deterministic_flags, invalid_evidence_ids, llm_used
    """
    if not generated_reply or not generated_reply.strip():
        return _empty_grounding_result(error="Empty reply provided")

    if llm_client is None:
        llm_client = get_llm_client()

    generator_evidence_ids = generator_evidence_ids or []
    valid_evidence_ids = _extract_evidence_ids(retrieved_evidence)
    system_prompt = _load_system_prompt(prompt_path)

    # -----------------------------------------------------------------------
    # Step 1: Deterministic pre-checks
    # -----------------------------------------------------------------------
    precheck = _deterministic_precheck(
        reply=generated_reply,
        customer_conversation=customer_conversation,
        retrieved_evidence=retrieved_evidence,
        valid_evidence_ids=valid_evidence_ids,
        generator_evidence_ids=generator_evidence_ids,
    )

    # -----------------------------------------------------------------------
    # Step 2: Check if reply is purely politeness (fast path)
    # -----------------------------------------------------------------------
    sentences = _extract_sentences(generated_reply)
    all_politeness = all(_is_politeness_only(s) for s in sentences)
    if all_politeness and not precheck["risk_flags"]:
        return {
            "grounded": True,
            "grounding_score": 1.0,
            "claims": [
                {
                    "claim": s,
                    "claim_text": s,
                    "source_type": SOURCE_TYPE_CURRENT_CONV,
                    "evidence_ids": ["CURRENT_CONVERSATION"],
                    "support_status": "SUPPORTED",
                    "status": "SUPPORTED",
                    "reason": "Generic politeness — no external evidence required",
                    "explanation": "Generic politeness — no external evidence required",
                }
                for s in sentences
            ],
            "supported_claims": sentences,
            "partially_supported_claims": [],
            "unsupported_claims": [],
            "contradicted_claims": [],
            "evidence_used": ["CURRENT_CONVERSATION"],
            "risk_flags": [],
            "needs_revision": False,
            "needs_human_review": False,
            "revision_suggestion": "",
            "deterministic_flags": [],
            "invalid_evidence_ids": [],
            "llm_used": False,
            "fast_path": "politeness_only",
        }

    # -----------------------------------------------------------------------
    # Step 3: LLM semantic entailment
    # -----------------------------------------------------------------------
    conv_text = _build_conversation_text(customer_conversation)
    ev_text = _build_evidence_text(retrieved_evidence)

    user_prompt = f"""CURRENT CONVERSATION
--------------------
{conv_text}

CLASSIFICATION
--------------
Primary intent: {classification.get('primary_intent', classification.get('intents', ['UNKNOWN'])[0] if classification.get('intents') else 'UNKNOWN')}
Intents: {classification.get('intents', [])}
States: {classification.get('states', [])}

HISTORICAL EVIDENCE (guidance only — NEVER assume these actions occurred for the current customer)
--------------------------------------------------------------------------------------------------
{ev_text}

GENERATED REPLY TO EVALUATE
-----------------------------
{generated_reply}

Valid evidence IDs in this context: {valid_evidence_ids}

Evaluate the reply above and return a JSON object with claim source_type classifications as described in the system prompt."""

    llm_result: Dict[str, Any] = {}
    llm_used = False
    llm_error: Optional[str] = None

    try:
        llm_resp = llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            json_mode=True,
            temperature=0.0,
            max_tokens=2048,
        )
        raw_content = llm_resp.content
        llm_result = parse_json_from_text(raw_content)
        llm_used = True
    except Exception as e:
        llm_error = str(e)
        logger.warning(f"Grounding LLM call failed: {e}. Falling back to deterministic-only result.")
        llm_result = _deterministic_fallback(
            sentences=sentences,
            precheck=precheck,
            valid_evidence_ids=valid_evidence_ids,
        )

    # -----------------------------------------------------------------------
    # Step 4: Post-process and merge deterministic + LLM results
    # -----------------------------------------------------------------------
    result = _merge_results(llm_result, precheck, valid_evidence_ids, llm_used, llm_error)
    return result


# ---------------------------------------------------------------------------
# Helper: normalize claim dictionaries
# ---------------------------------------------------------------------------

def _normalize_claim(c: Dict[str, Any], conv_text: str = "") -> Dict[str, Any]:
    """Ensure claim dict has all required fields with valid types (Task 1 & 5)."""
    claim_text = c.get("claim") or c.get("claim_text") or ""
    status = (c.get("support_status") or c.get("status") or "SUPPORTED").upper()
    reason = c.get("reason") or c.get("explanation") or ""
    ev_ids = list(c.get("evidence_ids") or [])
    source_type = c.get("source_type")

    # Infer source_type if missing or invalid
    if source_type not in VALID_SOURCE_TYPES:
        if status == "CONTRADICTED":
            source_type = SOURCE_TYPE_CONTRADICTED
        elif status == "UNSUPPORTED":
            source_type = SOURCE_TYPE_UNSUPPORTED
        elif "CURRENT_CONVERSATION" in ev_ids and any(eid != "CURRENT_CONVERSATION" for eid in ev_ids):
            source_type = SOURCE_TYPE_BOTH
        elif "CURRENT_CONVERSATION" in ev_ids:
            source_type = SOURCE_TYPE_CURRENT_CONV
        elif ev_ids:
            source_type = SOURCE_TYPE_HISTORICAL
        else:
            source_type = SOURCE_TYPE_CURRENT_CONV if _is_politeness_only(claim_text) else SOURCE_TYPE_UNSUPPORTED

    # Task 2 enforcement: Historical evidence may NOT by itself support current account state/actions
    if source_type == SOURCE_TYPE_HISTORICAL or (ev_ids and "CURRENT_CONVERSATION" not in ev_ids):
        for pat, pat_name in CURRENT_ACTION_PATTERNS:
            if re.search(pat, claim_text, re.IGNORECASE):
                if not _is_current_conversation_supported(claim_text, conv_text):
                    source_type = SOURCE_TYPE_UNSUPPORTED
                    status = "UNSUPPORTED"
                    reason = f"Historical evidence cannot support current-case assertion '{pat_name}'; requires current-conversation support."
                    break

    return {
        "claim": claim_text,
        "claim_text": claim_text,
        "source_type": source_type,
        "evidence_ids": ev_ids,
        "support_status": status,
        "status": status,
        "reason": reason,
        "explanation": reason,
    }


# ---------------------------------------------------------------------------
# Helper: deterministic fallback (when LLM is offline)
# ---------------------------------------------------------------------------

def _deterministic_fallback(
    sentences: List[str],
    precheck: Dict[str, Any],
    valid_evidence_ids: List[str],
) -> Dict[str, Any]:
    """Build a best-effort grounding result without LLM."""
    conv_text = precheck.get("conv_text", "")
    claims = []
    unsupported = []
    supported = []

    for s in sentences:
        if _is_politeness_only(s):
            claims.append({
                "claim": s,
                "claim_text": s,
                "source_type": SOURCE_TYPE_CURRENT_CONV,
                "support_status": "SUPPORTED",
                "status": "SUPPORTED",
                "evidence_ids": ["CURRENT_CONVERSATION"],
                "reason": "Generic politeness — no evidence required",
                "explanation": "Generic politeness — no evidence required",
            })
            supported.append(s)
        elif _is_current_conversation_supported(s, conv_text):
            claims.append({
                "claim": s,
                "claim_text": s,
                "source_type": SOURCE_TYPE_CURRENT_CONV,
                "support_status": "SUPPORTED",
                "status": "SUPPORTED",
                "evidence_ids": ["CURRENT_CONVERSATION"],
                "reason": "Supported by current conversation",
                "explanation": "Supported by current conversation",
            })
            supported.append(s)
        elif _contains_high_risk_claim(s) or any(re.search(pat, s, re.IGNORECASE) for pat, _ in CURRENT_ACTION_PATTERNS):
            claims.append({
                "claim": s,
                "claim_text": s,
                "source_type": SOURCE_TYPE_UNSUPPORTED,
                "support_status": "UNSUPPORTED",
                "status": "UNSUPPORTED",
                "evidence_ids": [],
                "reason": "High-risk claim or current action not confirmed in conversation; LLM offline",
                "explanation": "High-risk claim or current action not confirmed in conversation; LLM offline",
            })
            unsupported.append(s)
        else:
            claims.append({
                "claim": s,
                "claim_text": s,
                "source_type": SOURCE_TYPE_HISTORICAL if valid_evidence_ids else SOURCE_TYPE_CURRENT_CONV,
                "support_status": "SUPPORTED",
                "status": "SUPPORTED",
                "evidence_ids": valid_evidence_ids[:1] if valid_evidence_ids else ["CURRENT_CONVERSATION"],
                "reason": "General guidance assumed supported offline",
                "explanation": "General guidance assumed supported offline",
            })
            supported.append(s)

    n_claims = max(len(claims), 1)
    n_supported = len(supported)
    score = round(n_supported / n_claims, 3)
    grounded = len(unsupported) == 0 and not precheck.get("has_hard_violations", False)

    return {
        "grounded": grounded,
        "grounding_score": score,
        "claims": claims,
        "supported_claims": supported,
        "partially_supported_claims": [],
        "unsupported_claims": unsupported,
        "contradicted_claims": [],
        "evidence_used": valid_evidence_ids[:1] if valid_evidence_ids else [],
        "risk_flags": precheck.get("risk_flags", []),
        "needs_revision": not grounded,
        "needs_human_review": precheck.get("has_hard_violations", False),
        "revision_suggestion": "LLM offline — manual review recommended for high-risk claims",
    }


# ---------------------------------------------------------------------------
# Helper: merge LLM output with deterministic results
# ---------------------------------------------------------------------------

def _merge_results(
    llm_result: Dict[str, Any],
    precheck: Dict[str, Any],
    valid_evidence_ids: List[str],
    llm_used: bool,
    llm_error: Optional[str],
) -> Dict[str, Any]:
    """Merge LLM grounding output with deterministic precheck results."""
    conv_text = precheck.get("conv_text", "")
    raw_claims = llm_result.get("claims", [])
    claims = [_normalize_claim(c, conv_text) for c in raw_claims]

    # Incorporate deterministic claims
    for dc in precheck.get("deterministic_claims", []):
        norm_dc = _normalize_claim(dc, conv_text)
        if not any(c["claim"] == norm_dc["claim"] for c in claims):
            claims.append(norm_dc)

    # Separate by status
    supported = [c["claim"] for c in claims if c["support_status"] == "SUPPORTED"]
    partially = [c["claim"] for c in claims if c["support_status"] == "PARTIALLY_SUPPORTED"]
    unsupported = [c["claim"] for c in claims if c["support_status"] == "UNSUPPORTED"]
    contradicted = [c["claim"] for c in claims if c["support_status"] == "CONTRADICTED"]

    # Incorporate any strings from llm_result lists
    for s in llm_result.get("unsupported_claims", []):
        if s not in unsupported:
            unsupported.append(s)
    for s in precheck.get("deterministic_unsupported", []):
        if s not in unsupported:
            unsupported.append(s)
    for s in llm_result.get("contradicted_claims", []):
        if s not in contradicted:
            contradicted.append(s)

    evidence_used = list(llm_result.get("evidence_used", []))
    for c in claims:
        for eid in c.get("evidence_ids", []):
            if eid not in evidence_used:
                evidence_used.append(eid)

    # Validate evidence IDs
    invalid_llm_ids = _validate_evidence_ids(evidence_used, valid_evidence_ids)
    risk_flags = list(llm_result.get("risk_flags", []))
    if invalid_llm_ids:
        for inv_id in invalid_llm_ids:
            rf = f"LLM referenced invalid evidence ID: '{inv_id}'"
            if rf not in risk_flags:
                risk_flags.append(rf)
        evidence_used = [eid for eid in evidence_used if eid in set(valid_evidence_ids) | {"CURRENT_CONVERSATION"}]

    # Merge deterministic risk flags
    for rf in precheck.get("risk_flags", []):
        if rf not in risk_flags:
            risk_flags.append(rf)

    # Decisions
    grounded = bool(llm_result.get("grounded", True))
    needs_revision = bool(llm_result.get("needs_revision", False))
    needs_human_review = bool(llm_result.get("needs_human_review", False))
    revision_suggestion = llm_result.get("revision_suggestion", "")

    if precheck.get("has_hard_violations"):
        grounded = False
        needs_revision = True
        needs_human_review = True
        if not revision_suggestion:
            revision_suggestion = "Hard safety violations / unsupported current-case assertions detected — remove invented actions/dates/approvals"

    if unsupported or contradicted:
        grounded = False
        needs_revision = True

    if contradicted:
        needs_human_review = True

    # Recompute score
    n_total = len(supported) + len(partially) + len(unsupported) + len(contradicted)
    if n_total > 0:
        score = round((len(supported) + len(partially)) / n_total, 3)
    else:
        score = 0.0 if not grounded else 1.0

    return {
        "grounded": grounded,
        "grounding_score": score,
        "claims": claims,
        "supported_claims": supported,
        "partially_supported_claims": partially,
        "unsupported_claims": unsupported,
        "contradicted_claims": contradicted,
        "evidence_used": evidence_used,
        "risk_flags": risk_flags,
        "needs_revision": needs_revision,
        "needs_human_review": needs_human_review,
        "revision_suggestion": revision_suggestion,
        "deterministic_flags": precheck.get("risk_flags", []),
        "invalid_evidence_ids": precheck.get("invalid_evidence_ids", []) + invalid_llm_ids,
        "llm_used": llm_used,
        "llm_error": llm_error,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _empty_grounding_result(error: str = "") -> Dict[str, Any]:
    return {
        "grounded": False,
        "grounding_score": 0.0,
        "claims": [],
        "supported_claims": [],
        "partially_supported_claims": [],
        "unsupported_claims": [],
        "contradicted_claims": [],
        "evidence_used": [],
        "risk_flags": [error] if error else ["Empty reply"],
        "needs_revision": True,
        "needs_human_review": True,
        "revision_suggestion": "Reply was empty",
        "deterministic_flags": [],
        "invalid_evidence_ids": [],
        "llm_used": False,
        "llm_error": error,
    }
