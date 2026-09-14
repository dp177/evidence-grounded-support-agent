"""OpenRouter LLM Intent Classifier for AmazonHelp Support Cases.

Provides:
- Zero-shot / few-shot prompt formulation constrained strictly to configs/taxonomy_v1.yaml
- Multi-intent parsing (no combination labels)
- Conversation state classification
- Ambiguity and out-of-scope domain gating
- Local prediction caching under artifacts/llm_predictions/
- Robust JSON parsing and schema sanitization
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Set
import yaml

from support_agent.llm.client import BaseLLMClient, get_llm_client
from support_agent.classification.state_extractor import extract_conversation_state

logger = logging.getLogger(__name__)

INTENT_DEFINITIONS = """
ALLOWED BROAD AREAS AND LEAF INTENTS (TAXONOMY V1.0):

1. DELIVERY_AND_FULFILLMENT:
   - WHERE_IS_MY_ORDER: Customer asks for package whereabouts, dispatch progress, or estimated arrival date within or near the promised delivery window (no confirmed delay).
   - DELIVERY_DELAYED: Guaranteed or promised delivery date has elapsed, or courier explicitly marked package as delayed in transit.
   - MARKED_DELIVERED_NOT_RECEIVED: Tracking indicates delivered or left with resident/neighbour, but customer physically did not receive the parcel.
   - CARRIER_FEEDBACK_AND_INSTRUCTIONS: Courier misconduct, driver rudeness, refusal to deliver to address, or special delivery instructions (safe place, gate code).

2. RETURNS_AND_REPLACEMENTS:
   - DAMAGED_OR_DEFECTIVE_ITEM: Item arrived physically broken, leaking, cracked, damaged packaging, or non-functional.
   - WRONG_ITEM_RECEIVED: Completely different product, wrong SKU, wrong size, or incorrect color delivered.
   - RETURN_PICKUP_ISSUE: Courier failed to arrive for scheduled return pickup, or problems with return drop-off/label.

3. REFUNDS_AND_BILLING:
   - REFUND_STATUS_INQUIRY: Inquiry or dispute regarding expected bank credit from a completed return or cancelled order.
   - UNRECOGNIZED_OR_DUPLICATE_CHARGE: Disputed credit card debit, duplicate transaction, or unexpected bank charge.

4. ORDER_MANAGEMENT:
   - CANCEL_ORDER_REQUEST: Request to cancel an existing active order before or during fulfillment.
   - MODIFY_ORDER_DETAILS: Request to change delivery address, payment method, recipient, or delivery date.

5. DIGITAL_SERVICES_AND_PRIME:
   - PRIME_MEMBERSHIP_MANAGEMENT: Unwanted Prime subscription renewal, cancellation, or Prime trial fee dispute.
   - DIGITAL_CONTENT_ACCESS: Trouble accessing Kindle ebooks, Prime Video streaming, Amazon Music, or digital download codes.

6. ACCOUNT_ACCESS_AND_SECURITY:
   - ACCOUNT_LOGIN_ISSUES: Password reset loops, OTP verification failures, account lockouts, or unauthorized account access.

ALLOWED CONVERSATION STATES:
- INITIAL_INQUIRY: First message or problem statement with no previous support actions mentioned.
- TRACKING_ALREADY_CHECKED: Customer explicitly states they already checked tracking website or app.
- CARRIER_ALREADY_CONTACTED: Customer explicitly states they already spoke to or called the courier/carrier.
- DETAILS_ALREADY_PROVIDED: Customer states they already sent DM, order number, or account details.
- WAITING_WINDOW_EXCEEDED: Customer states they were told to wait a number of days/hours and that window has passed.
"""

CLASSIFICATION_SYSTEM_PROMPT = f"""You are an expert AI customer-support intent classifier for AmazonHelp.
Your task is to classify customer support inquiries against the FROZEN TAXONOMY V1.0.

{INTENT_DEFINITIONS}

DECISION ORDER & CLASSIFICATION PRINCIPLE:
The classifier answers TWO questions in strict order:
QUESTION A: "Does this message contain an actionable customer-support issue?"
QUESTION B: "If yes, which taxonomy intent(s) describe that issue?"

Follow this decision order:
STEP 1: Read the complete current conversation.
STEP 2: Determine whether there is an actionable support issue.
STEP 3: If no actionable issue (greeting, acknowledgement, vague request for help):
    status = "AMBIGUOUS"
    areas = []
    intents = []
    primary_intent = null
STEP 4: If clearly outside the supported domain:
    status = "OUT_OF_SCOPE"
    areas = []
    intents = []
    primary_intent = null
STEP 5: Otherwise (actionable retail support issue present):
    status = "NORMAL"
    classify into one or more valid taxonomy leaf intents.
STEP 6: Infer current conversation states independently.

STRICT CLASSIFICATION RULES:
1. Return ONLY valid labels from the taxonomy above. NEVER invent new intent names or hybrid combination labels.
2. DO NOT FORCE A BUSINESS INTENT:
   - Do not force a business intent when the customer has not expressed an actionable support problem.
   - If the message is only a greeting, acknowledgement, vague request for help, or otherwise lacks sufficient information to identify a support issue, return AMBIGUOUS with no intent.
   - Only assign a leaf intent when the conversation contains evidence for that intent.
   - AMBIGUOUS is a classification status, not a leaf intent. Do NOT invent a "GREETING" intent.
3. GREETINGS AND CONVERSATIONAL OPENINGS:
   - Pure greetings or vague help requests ("hi", "hello", "hey", "can you help me?", "please help", "anyone there?", "good morning", "I have a question", "I need help", "I need help with something") must be classified as AMBIGUOUS with areas: [], intents: [], primary_intent: null, states: ["INITIAL_INQUIRY"]. The classifier must NOT invent a support issue.
   - ACTIONABLE GREETINGS: The existence of a greeting does NOT make the whole message ambiguous if an actionable issue is present. For example: "hi, my package is late" -> status: "NORMAL", intents: ["DELIVERY_DELAYED"], primary_intent: "DELIVERY_DELAYED". The actionable support issue takes priority!
4. RECOGNIZABLE SUPPORT ISSUES IN HOSTILE, EMOTIONAL, OR POORLY PHRASED MESSAGES:
   - If a customer message contains a recognizable operational support problem, classify that problem even when the wording is emotional, abusive, incomplete, or poorly phrased. Do not use AMBIGUOUS merely because the message is hostile or missing secondary details. Safety and escalation will be handled separately by the security layer.
   - For example: "i will kill you give me instant refund" -> status: "NORMAL", intents: ["REFUND_STATUS_INQUIRY"], primary_intent: "REFUND_STATUS_INQUIRY", areas: ["REFUNDS_AND_BILLING"]. The operational problem is clearly a refund request.
   - For example: "give me my money back right now you thieves" -> status: "NORMAL", intents: ["REFUND_STATUS_INQUIRY"], primary_intent: "REFUND_STATUS_INQUIRY".
5. MULTI-TURN RECOMPUTATION:
   - Classification must consider the FULL current conversation. Ambiguity is not a permanent conversation state; it is recomputed on every turn. If Turn 1 is "hi" (AMBIGUOUS) and Turn 2 is "my package is late", Turn 2 is NORMAL (DELIVERY_DELAYED).
6. DO NOT CONFUSE AMBIGUOUS WITH OUT_OF_SCOPE:
   - AMBIGUOUS: Unclear or greeting within retail support context ("hi", "can you help me?", "terrible service", "check your DM").
   - OUT_OF_SCOPE: Clearly outside Amazon retail support (e.g. "tell me today's weather in Delhi", social banter, non-retail merchant/seller central, stock inquiries).
7. Multi-intent rule: If the customer expresses TWO OR MORE distinct actionable issues in one inquiry (e.g., package delayed AND wants a refund), set is_multi_intent to true, list all applicable leaf intents in "intents", and choose the single most operationally urgent intent as "primary_intent".
8. State rule: Select the most accurate conversation state from the 5 allowed states based on what the customer has already done.
9. Output format: Respond ONLY with a valid JSON object matching this schema:

{{
  "classification_status": "NORMAL" | "AMBIGUOUS" | "OUT_OF_SCOPE",
  "areas": ["AREA_NAME"],
  "intents": ["INTENT_NAME"],
  "primary_intent": "INTENT_NAME" or null,
  "is_multi_intent": false or true,
  "states": ["STATE_NAME"],
  "confidence": 0.95,
  "reasoning": "brief explanation"
}}
"""


def validate_demo_isolation(
    demos_path: Path | str = "data/development/classification_demos.jsonl",
    golden_manifest_path: Path | str = "data/splits/split_manifest.json",
) -> bool:
    """Validate that zero demonstration conversations appear in Golden V1."""
    manifest_file = Path(golden_manifest_path)
    golden_ids = set()
    if manifest_file.exists():
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            golden_ids.update(str(c) for c in manifest.get("golden_conversation_ids", []))

    demo_file = Path(demos_path)
    if not demo_file.exists():
        raise FileNotFoundError(f"Demonstration file not found: {demo_file}")

    demo_conv_ids = set()
    total_demos = 0
    with open(demo_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                demo_conv_ids.add(str(rec.get("conversation_id")))
                total_demos += 1

    leakage = demo_conv_ids.intersection(golden_ids)
    if leakage:
        raise ValueError(
            f"CRITICAL LEAKAGE: Found {len(leakage)} demonstration conversation IDs in Golden V1: {leakage}"
        )
    return True


class LLMIntentClassifier:
    """OpenRouter-based LLM classifier constrained to Taxonomy v1."""

    def __init__(
        self,
        client: Optional[BaseLLMClient] = None,
        cache_dir: Optional[Path | str] = None,
        taxonomy_path: Optional[Path | str] = None,
        prompt_path: Optional[Path | str] = None,
        system_prompt: Optional[str] = None,
    ):
        self.client = client or get_llm_client()
        self.cache_dir = Path(cache_dir) if cache_dir else Path("artifacts/llm_predictions")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        if system_prompt:
            self.system_prompt = system_prompt
        elif prompt_path and Path(prompt_path).exists():
            self.system_prompt = Path(prompt_path).read_text(encoding="utf-8")
        else:
            self.system_prompt = CLASSIFICATION_SYSTEM_PROMPT

        # Load taxonomy for strict validation
        tax_file = Path(taxonomy_path) if taxonomy_path else Path("configs/taxonomy_v1.yaml")
        if tax_file.exists():
            with open(tax_file, "r", encoding="utf-8") as f:
                tax = yaml.safe_load(f)
            self.areas = set(tax.get("areas", {}).keys())
            self.leaf_intents = set()
            self.intent_to_area = {}
            for a, d in tax.get("areas", {}).items():
                for it in d.get("intents", []):
                    self.leaf_intents.add(it)
                    self.intent_to_area[it] = a
            self.statuses = set(tax.get("classification_status", ["NORMAL", "AMBIGUOUS", "OUT_OF_SCOPE"]))
            self.states = set(tax.get("conversation_states", []))
        else:
            self.areas = set()
            self.leaf_intents = set()
            self.intent_to_area = {}
            self.statuses = {"NORMAL", "AMBIGUOUS", "OUT_OF_SCOPE"}
            self.states = set()

    def _build_user_prompt(self, customer_message: str, context: Optional[str] = None) -> str:
        ctx_str = f"Conversation Context:\n{context}\n\n" if context else ""
        return (
            f"{ctx_str}"
            f"Current Customer Message:\n\"{customer_message}\"\n\n"
            f"Classify this inquiry according to Taxonomy v1.0. Output valid JSON only."
        )

    def _sanitize_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all fields conform strictly to Taxonomy v1.0."""
        status = str(data.get("classification_status", "NORMAL")).strip()
        if status not in self.statuses:
            status = "NORMAL"

        conf = float(data.get("confidence", 0.85))
        conf = max(0.0, min(1.0, conf))

        if status in ["AMBIGUOUS", "OUT_OF_SCOPE"]:
            return {
                "classification_status": status,
                "areas": [],
                "intents": [],
                "primary_intent": None,
                "is_multi_intent": False,
                "states": ["INITIAL_INQUIRY"],
                "confidence": round(conf, 4),
                "reasoning": str(data.get("reasoning", "")),
            }

        # Validate intents
        raw_intents = data.get("intents", [])
        if isinstance(raw_intents, str):
            raw_intents = [i.strip() for i in raw_intents.split("|")]

        valid_intents = [i for i in raw_intents if i in self.leaf_intents]
        if not valid_intents:
            # Fallback if model invented a non-existent intent
            valid_intents = ["DELIVERY_DELAYED"]

        primary = data.get("primary_intent")
        if primary not in valid_intents:
            primary = valid_intents[0]

        is_multi = bool(data.get("is_multi_intent", len(valid_intents) > 1))
        if len(valid_intents) > 1:
            is_multi = True

        areas = sorted(list({self.intent_to_area.get(it, "DELIVERY_AND_FULFILLMENT") for it in valid_intents}))

        raw_states = data.get("states", ["INITIAL_INQUIRY"])
        if isinstance(raw_states, str):
            raw_states = [raw_states]
        valid_states = [s for s in raw_states if s in self.states]
        if not valid_states:
            valid_states = ["INITIAL_INQUIRY"]

        return {
            "classification_status": "NORMAL",
            "areas": areas,
            "intents": valid_intents,
            "primary_intent": primary,
            "is_multi_intent": is_multi,
            "states": valid_states,
            "confidence": round(conf, 4),
            "reasoning": str(data.get("reasoning", "")),
        }

    def classify_case(
        self,
        customer_message: str,
        context: Optional[str] = None,
        gold_id: Optional[str] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Classify a single case with local caching."""
        # 1. Check local cache
        cache_file = None
        if gold_id and use_cache:
            cache_file = self.cache_dir / f"{gold_id}.json"
            if cache_file.exists():
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cached = json.load(f)
                    res = self._sanitize_output(cached)
                    res["states"] = extract_conversation_state(customer_message, context, res.get("states"))
                    return res
                except Exception as e:
                    logger.warning(f"Failed to read cache for {gold_id}: {e}")


        # 2. Invoke OpenRouter LLM with retry loop
        prompt = self._build_user_prompt(customer_message, context)
        parsed = None
        max_attempts = 4
        for attempt in range(1, max_attempts + 1):
            try:
                resp = self.client.generate(
                    prompt=prompt,
                    system_prompt=self.system_prompt,
                    temperature=0.0,
                    max_tokens=2000,
                )
                candidate = resp.json()
                if isinstance(candidate, list) and candidate:
                    candidate = candidate[0]
                if isinstance(candidate, dict):
                    parsed = candidate
                    break
                else:
                    raise ValueError(f"Expected JSON object, got {type(candidate)}")
            except Exception as e:
                logger.warning(f"LLM classification attempt {attempt}/{max_attempts} failed for {gold_id}: {e}")
                if attempt < max_attempts:
                    time.sleep(2.0 * attempt)
                else:
                    logger.error(f"All {max_attempts} attempts failed for {gold_id}: {e}")
                    import re
                    msg_lower = f"{context or ''} {customer_message}".lower()
                    if re.search(r"\b(?:refund|money back|reimburse|credit back)\b", msg_lower):
                        parsed = {
                            "classification_status": "NORMAL",
                            "areas": ["REFUNDS_AND_BILLING"],
                            "intents": ["REFUND_STATUS_INQUIRY"],
                            "primary_intent": "REFUND_STATUS_INQUIRY",
                            "is_multi_intent": False,
                            "states": ["INITIAL_INQUIRY"],
                            "confidence": 0.85,
                            "reasoning": "Determined from customer operational refund request keywords after LLM error",
                        }
                    elif re.search(r"\b(?:late|delayed|not arrived|hasn't arrived|where is (?:my )?(?:order|package|delivery|item))\b", msg_lower):
                        parsed = {
                            "classification_status": "NORMAL",
                            "areas": ["DELIVERY_AND_FULFILLMENT"],
                            "intents": ["DELIVERY_DELAYED"],
                            "primary_intent": "DELIVERY_DELAYED",
                            "is_multi_intent": False,
                            "states": ["INITIAL_INQUIRY"],
                            "confidence": 0.85,
                            "reasoning": "Determined from customer operational delivery keywords after LLM error",
                        }
                    else:
                        parsed = {
                            "classification_status": "AMBIGUOUS",
                            "areas": [],
                            "intents": [],
                            "primary_intent": None,
                            "is_multi_intent": False,
                            "states": ["INITIAL_INQUIRY"],
                            "confidence": 0.0,
                            "reasoning": f"Fallback due to model call error: {e}",
                        }

        sanitized = self._sanitize_output(parsed)
        sanitized["states"] = extract_conversation_state(customer_message, context, sanitized.get("states"))

        # 3. Save to local cache
        if cache_file:
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(sanitized, f, indent=2)
            except Exception as e:
                logger.warning(f"Failed to write cache for {gold_id}: {e}")

        return sanitized


    def classify_batch(
        self,
        cases: List[Dict[str, Any]],
        max_workers: int = 4,
        use_cache: bool = True,
    ) -> List[Dict[str, Any]]:
        """Classify a list of golden cases in parallel with caching and rate limit protection."""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        total = len(cases)
        results = [None] * total

        def _worker(idx: int, case: Dict[str, Any]):
            gid = case.get("gold_id", f"case_{idx+1}")
            msg = case.get("customer_message", "")
            ctx = case.get("context", "")
            pred = self.classify_case(msg, ctx, gold_id=gid, use_cache=use_cache)
            return idx, gid, pred

        completed = 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {
                executor.submit(_worker, i, c): i for i, c in enumerate(cases)
            }
            for fut in as_completed(future_to_idx):
                idx, gid, pred = fut.result()
                results[idx] = pred
                completed += 1
                if completed % 10 == 0 or completed == total:
                    logger.info(
                        f"Classified {completed}/{total} cases (Latest: [{gid}] -> {pred['classification_status']}:{pred['primary_intent']})"
                    )

        return results

