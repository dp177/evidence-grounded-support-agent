# Classifier v2 Prompt Inspection (Few-Shot Demonstration Architecture)

**Inspection Date**: 2026-09-12  
**Classifier Version**: 2.0 (Few-Shot Prompting via `configs/classifier_v2.yaml`)  
**Prompt File**: `prompts/classification_v2.md`  
**Demonstrations File**: `data/development/classification_demos.jsonl` (55 validated dev-only demonstrations)  
**Configured Model**: `meta-llama/llama-3.1-8b-instruct`  

---

## 1. Architectural Overview & Configuration

In Classifier v2, the model is augmented with 55 development-only demonstrations embedded directly in the system message.

### Configuration (`configs/classifier_v2.yaml`)
```yaml
version: "2.0"
taxonomy_version: "1.0"
few_shot_enabled: true
demonstration_count: 55
demo_source: "development_only"
prompt_file: "prompts/classification_v2.md"
demos_file: "data/development/classification_demos.jsonl"
cache_dir: "artifacts/llm_predictions_v2"
model: "meta-llama/llama-3.1-8b-instruct"
temperature: 0.0
max_tokens: 2000
```

### Key Differences from Classifier v1
1. **Zero-Shot $\rightarrow$ Few-Shot**: V1 contained only taxonomy definitions. V2 injects 55 concrete exemplars into a dedicated `FEW-SHOT EXAMPLES` section.
2. **Explicit Anti-Copying Rule**: Rule 7 instructs the model to use examples for interpretation rather than superficial lexical pattern matching.
3. **Boundary Contrast Guidance**: Targeted examples explicitly disambiguate `WHERE_IS_MY_ORDER` vs `DELIVERY_DELAYED`, `DELIVERY_DELAYED` vs `MARKED_DELIVERED_NOT_RECEIVED`, `DAMAGED` vs `WRONG_ITEM`, `CANCEL` vs `MODIFY`, etc.
4. **Multi-Intent & Domain Gating Demonstrations**: Real examples showing how to decompose multiple issues and how to assign `AMBIGUOUS` and `OUT_OF_SCOPE`.
5. **Prompt Externalization**: The prompt is stored in [`prompts/classification_v2.md`](file:///e:/Intern_Presentation/Hiver%20Project/prompts/classification_v2.md) rather than hardcoded in Python code.
6. **Isolated Prediction Cache**: V2 inferences are stored in `artifacts/llm_predictions_v2/`, leaving V1 predictions in `artifacts/llm_predictions/` untouched for exact ablation comparison.

---

## 2. Golden Set Isolation & Zero-Leakage Proof

- **Isolation Validation Function**: `validate_demo_isolation()`
- **Audit Result**: `55 demonstrations across 55 unique conversations. 0 golden overlaps.`
- **Check**: `intersection(demonstration_conversation_ids, golden_conversation_ids) == empty` verified with return code 0.
- **Payload Sanitization**: No golden IDs, labels, or notes are transmitted to OpenRouter.

---

## 3. Concrete Example: Sanitized Request Payload for Case [gold_0001]

Below is the exact payload sent to OpenRouter (`https://openrouter.ai/api/v1/chat/completions`) for `gold_0001`:

### Request Endpoint & Headers
```http
POST /api/v1/chat/completions HTTP/1.1
Host: openrouter.ai
Authorization: Bearer sk-or-v1-****************************************
Content-Type: application/json
HTTP-Referer: https://github.com/dp177/evidence-grounded-support-agent
X-Title: AmazonSupportAgent
```

### Request Body (Sanitized Payload)
```json
{
  "model": "meta-llama/llama-3.1-8b-instruct",
  "messages": [
    {
      "role": "system",
      "content": "You are an expert AI customer-support intent classifier for AmazonHelp.\nYour task is to classify customer support inquiries against the FROZEN TAXONOMY V1.0.\n\nALLOWED BROAD AREAS AND LEAF INTENTS (TAXONOMY V1.0):\n\n1. DELIVERY_AND_FULFILLMENT:\n   - WHERE_IS_MY_ORDER: Customer asks for package whereabouts, dispatch progress, or estimated arrival date within or near the promised delivery window (no confirmed delay).\n   - DELIVERY_DELAYED: Guaranteed or promised delivery date has elapsed, or courier explicitly marked package as delayed in transit.\n   - MARKED_DELIVERED_NOT_RECEIVED: Tracking indicates delivered or left with resident/neighbour, but customer physically did not receive the parcel.\n   - CARRIER_FEEDBACK_AND_INSTRUCTIONS: Courier misconduct, driver rudeness, refusal to deliver to address, or special delivery instructions (safe place, gate code).\n\n2. RETURNS_AND_REPLACEMENTS:\n   - DAMAGED_OR_DEFECTIVE_ITEM: Item arrived physically broken, leaking, cracked, damaged packaging, or non-functional.\n   - WRONG_ITEM_RECEIVED: Completely different product, wrong SKU, wrong size, or incorrect color delivered.\n   - RETURN_PICKUP_ISSUE: Courier failed to arrive for scheduled return pickup, or problems with return drop-off/label.\n\n3. REFUNDS_AND_BILLING:\n   - REFUND_STATUS_INQUIRY: Inquiry or dispute regarding expected bank credit from a completed return or cancelled order.\n   - UNRECOGNIZED_OR_DUPLICATE_CHARGE: Disputed credit card debit, duplicate transaction, or unexpected bank charge.\n\n4. ORDER_MANAGEMENT:\n   - CANCEL_ORDER_REQUEST: Request to cancel an existing active order before or during fulfillment.\n   - MODIFY_ORDER_DETAILS: Request to change delivery address, payment method, recipient, or delivery date.\n\n5. DIGITAL_SERVICES_AND_PRIME:\n   - PRIME_MEMBERSHIP_MANAGEMENT: Unwanted Prime subscription renewal, cancellation, or Prime trial fee dispute.\n   - DIGITAL_CONTENT_ACCESS: Trouble accessing Kindle ebooks, Prime Video streaming, Amazon Music, or digital download codes.\n\n6. ACCOUNT_ACCESS_AND_SECURITY:\n   - ACCOUNT_LOGIN_ISSUES: Password reset loops, OTP verification failures, account lockouts, or unauthorized account access.\n\nALLOWED CONVERSATION STATES:\n- INITIAL_INQUIRY: First message or problem statement with no previous support actions mentioned.\n- TRACKING_ALREADY_CHECKED: Customer explicitly states they already checked tracking website or app.\n- CARRIER_ALREADY_CONTACTED: Customer explicitly states they already spoke to or called the courier/carrier.\n- DETAILS_ALREADY_PROVIDED: Customer states they already sent DM, order number, or account details.\n- WAITING_WINDOW_EXCEEDED: Customer states they were told to wait a number of days/hours and that window has passed.\n\nSTRICT CLASSIFICATION RULES:\n1. Return ONLY valid labels from the taxonomy above. NEVER invent new intent names or hybrid combination labels.\n2. AMBIGUOUS rule: If the customer message is too vague to know what they want (e.g., \"help please\", \"check your DM\", \"terrible service\"), set classification_status to \"AMBIGUOUS\", areas to [], intents to [], and primary_intent to null.\n3. OUT_OF_SCOPE rule: If the message is social banter, marketing praise, stock availability inquiries, or non-retail merchant support (e.g. Seller Central), set classification_status to \"OUT_OF_SCOPE\", areas to [], intents to [], and primary_intent to null.\n4. NORMAL rule: If the customer expresses an actionable support need, set classification_status to \"NORMAL\".\n5. Multi-intent rule: If the customer expresses TWO OR MORE distinct actionable issues in one inquiry (e.g., package delayed AND wants a refund), set is_multi_intent to true, list all applicable leaf intents in \"intents\", and choose the single most operationally urgent intent as \"primary_intent\".\n6. State rule: Select the most accurate conversation state from the 5 allowed states based on what the customer has already done.\n7. ANTI-COPYING RULE: Use the examples to understand the intended interpretation of each taxonomy label. Do not copy an example's answer merely because the wording looks similar. Classify the actual current conversation using the taxonomy and conversation context.\n8. Output format: Respond ONLY with a valid JSON object matching this schema:\n\n{\n  \"classification_status\": \"NORMAL\" | \"AMBIGUOUS\" | \"OUT_OF_SCOPE\",\n  \"areas\": [\"AREA_NAME\"],\n  \"intents\": [\"INTENT_NAME\"],\n  \"primary_intent\": \"INTENT_NAME\" or null,\n  \"is_multi_intent\": false or true,\n  \"states\": [\"STATE_NAME\"],\n  \"confidence\": 0.95,\n  \"reasoning\": \"brief explanation\"\n}\n\n==================================================\nFEW-SHOT EXAMPLES\n==================================================\n\n[... 55 compact development-pool demonstrations ...]\n\n==================================================\nEND FEW-SHOT EXAMPLES\n=================================================="
    },
    {
      "role": "user",
      "content": "Conversation Context:\nCUSTOMER: rude & disrespectful delivery person who refused 2 deliver to the mentioned address until someone comes down and collects it.(1/2)\nBRAND: I apologize for the inappropriate behavior of the delivery agent.1/3\nBRAND: I've noted your comments and have forwarded your feedback internally. 2/3\n\nCurrent Customer Message:\n\"rude & disrespectful delivery person who refused 2 deliver to the mentioned address until someone comes down and collects it.(1/2)\"\n\nClassify this inquiry according to Taxonomy v1.0. Output valid JSON only."
    }
  ],
  "temperature": 0.0,
  "max_tokens": 2000
}
```

---

## 4. Prompt Size and Efficiency Audit

- **Total Demonstrations**: 55
- **System Prompt Character Count**: 16,838 characters
- **Approximate System Prompt Tokens**: ~3,150 tokens
- **Average Demonstration Length**: ~28 words
- **Efficiency Impact**: Readily fits within standard model context windows (<4k prompt tokens) while operating well below limits, keeping per-request latency low and throughput high.
