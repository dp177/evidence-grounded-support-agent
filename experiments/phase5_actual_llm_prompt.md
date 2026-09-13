# Phase 5 Actual LLM Classifier Prompt Inspection

**Inspection Date**: 2026-09-12  
**Implementation Files Inspected**:
- `src/support_agent/classification/llm_classifier.py`
- `src/support_agent/llm/client.py`
- `configs/taxonomy_v1.yaml`
- `.env`

---

## 1. Architectural Inspection (10 Key Dimension Audit)

### 1. System Message
The system prompt is defined by `CLASSIFICATION_SYSTEM_PROMPT` in [`src/support_agent/classification/llm_classifier.py`](file:///e:/Intern_Presentation/Hiver%20Project/src/support_agent/classification/llm_classifier.py#L63-L87). It instructs the model on its role, injects frozen Taxonomy v1.0 definitions, specifies 7 disambiguation/status rules, and defines the target JSON schema.

```text
You are an expert AI customer-support intent classifier for AmazonHelp.
Your task is to classify customer support inquiries against the FROZEN TAXONOMY V1.0.

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


STRICT CLASSIFICATION RULES:
1. Return ONLY valid labels from the taxonomy above. NEVER invent new intent names or hybrid combination labels.
2. AMBIGUOUS rule: If the customer message is too vague to know what they want (e.g., "help please", "check your DM", "terrible service"), set classification_status to "AMBIGUOUS", areas to [], intents to [], and primary_intent to null.
3. OUT_OF_SCOPE rule: If the message is social banter, marketing praise, stock availability inquiries, or non-retail merchant support (e.g. Seller Central), set classification_status to "OUT_OF_SCOPE", areas to [], intents to [], and primary_intent to null.
4. NORMAL rule: If the customer expresses an actionable support need, set classification_status to "NORMAL".
5. Multi-intent rule: If the customer expresses TWO OR MORE distinct actionable issues in one inquiry (e.g., package delayed AND wants a refund), set is_multi_intent to true, list all applicable leaf intents in "intents", and choose the single most operationally urgent intent as "primary_intent".
6. State rule: Select the most accurate conversation state from the 5 allowed states based on what the customer has already done.
7. Output format: Respond ONLY with a valid JSON object matching this schema:

{
  "classification_status": "NORMAL" | "AMBIGUOUS" | "OUT_OF_SCOPE",
  "areas": ["AREA_NAME"],
  "intents": ["INTENT_NAME"],
  "primary_intent": "INTENT_NAME" or null,
  "is_multi_intent": false or true,
  "states": ["STATE_NAME"],
  "confidence": 0.95,
  "reasoning": "brief explanation"
}
```

---

### 2. User Message Template
Formulated by `_build_user_prompt(customer_message, context)` in [`src/support_agent/classification/llm_classifier.py`](file:///e:/Intern_Presentation/Hiver%20Project/src/support_agent/classification/llm_classifier.py#L124-L130):

```text
Conversation Context:
{context}

Current Customer Message:
"{customer_message}"

Classify this inquiry according to Taxonomy v1.0. Output valid JSON only.
```
*(Note: If `context` is empty or None, the `Conversation Context:\n...` block is omitted).*

---

### 3. Taxonomy Content Injected
Directly transcribed from frozen `configs/taxonomy_v1.yaml`:
- **6 Broad Areas**: `DELIVERY_AND_FULFILLMENT`, `RETURNS_AND_REPLACEMENTS`, `REFUNDS_AND_BILLING`, `ORDER_MANAGEMENT`, `DIGITAL_SERVICES_AND_PRIME`, `ACCOUNT_ACCESS_AND_SECURITY`.
- **14 Leaf Intents**:
  1. `WHERE_IS_MY_ORDER`
  2. `DELIVERY_DELAYED`
  3. `MARKED_DELIVERED_NOT_RECEIVED`
  4. `CARRIER_FEEDBACK_AND_INSTRUCTIONS`
  5. `DAMAGED_OR_DEFECTIVE_ITEM`
  6. `WRONG_ITEM_RECEIVED`
  7. `RETURN_PICKUP_ISSUE`
  8. `REFUND_STATUS_INQUIRY`
  9. `UNRECOGNIZED_OR_DUPLICATE_CHARGE`
  10. `CANCEL_ORDER_REQUEST`
  11. `MODIFY_ORDER_DETAILS`
  12. `PRIME_MEMBERSHIP_MANAGEMENT`
  13. `DIGITAL_CONTENT_ACCESS`
  14. `ACCOUNT_LOGIN_ISSUES`
- **5 Conversation States**: `INITIAL_INQUIRY`, `TRACKING_ALREADY_CHECKED`, `CARRIER_ALREADY_CONTACTED`, `DETAILS_ALREADY_PROVIDED`, `WAITING_WINDOW_EXCEEDED`.

---

### 4. Annotation/Decision Rules Injected
Explicit constraints embedded in the system prompt:
1. **Label Closed-World Constraint**: Explicit prohibition on inventing novel labels or hybrid strings.
2. **Ambiguity Gating Rule**: Vague or context-less inquiries forced to `AMBIGUOUS` with null primary intent and empty intent arrays.
3. **Out-of-Scope Domain Gating Rule**: Social banter, seller support, marketing inquiries routed to `OUT_OF_SCOPE` with null primary intent.
4. **Actionability (NORMAL) Rule**: Actionable retail customer service requests marked `NORMAL`.
5. **Multi-Intent Decomposition Rule**: Multiple issues decomposed into distinct leaf intent list, with the most operationally critical chosen as `primary_intent`.
6. **State Selection Rule**: Grounded in historical user actions mentioned in context or message.
7. **Strict JSON Schema Enforcement**: Strict JSON object response only.

---

### 5. Conversation Context Injected
Full preceding thread turns (`CUSTOMER:` and `BRAND:` dialogue history) are injected under `Conversation Context:` to enable multi-turn disambiguation (e.g. knowing whether details were already provided or tracking was already checked).

---

### 6. Output Schema
Prompt specifies an exact JSON object structure:
```json
{
  "classification_status": "NORMAL" | "AMBIGUOUS" | "OUT_OF_SCOPE",
  "areas": ["AREA_NAME"],
  "intents": ["INTENT_NAME"],
  "primary_intent": "INTENT_NAME" or null,
  "is_multi_intent": false or true,
  "states": ["STATE_NAME"],
  "confidence": 0.95,
  "reasoning": "brief explanation"
}
```

---

### 7. Model Name
- Read from `OPENROUTER_MODEL` environment variable:
  - Configured value in `.env`: `meta-llama/llama-3.1-8b-instruct`

---

### 8. Temperature and Generation Parameters
- `temperature`: `0.0` (deterministic greedy decoding)
- `max_tokens`: `2000`
- `timeout`: `90` seconds
- `max_retries`: `3` attempts with exponential backoff on retryable HTTP codes (`{429, 500, 502, 503, 504}`)
- `HTTP Headers`:
  - `Content-Type`: `application/json`
  - `HTTP-Referer`: `https://github.com/dp177/evidence-grounded-support-agent`
  - `X-Title`: `AmazonSupportAgent`
  - `Authorization`: `Bearer [REDACTED]`

---

### 9. Few-Shot Demonstrations / In-Context Examples
- **Zero few-shot examples included**.
- The classifier operates in **pure zero-shot mode** relying solely on taxonomy definitions and operational boundary rules.

---

### 10. Golden Set Contamination / Leakage Audit
- **Zero golden annotations or metadata are passed to the model**.
- No `gold_id`, `sampling_category`, `difficulty`, `annotator_notes`, `should_escalate`, or ground-truth label fields are present in the request payload.
- Only the raw input text (`customer_message`) and dialog turns (`context`) from the customer interaction are provided in the user prompt.
- Evaluation against `data/golden/golden_set.jsonl` is completely blind.

---

## 2. Concrete Concrete Golden-Set Payload: Case [gold_0001]

Below is the **sanitized representation of the exact JSON payload** sent to the OpenRouter Chat Completions endpoint (`https://openrouter.ai/api/v1/chat/completions`) for `gold_0001`:

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
      "content": "You are an expert AI customer-support intent classifier for AmazonHelp.\nYour task is to classify customer support inquiries against the FROZEN TAXONOMY V1.0.\n\n\nALLOWED BROAD AREAS AND LEAF INTENTS (TAXONOMY V1.0):\n\n1. DELIVERY_AND_FULFILLMENT:\n   - WHERE_IS_MY_ORDER: Customer asks for package whereabouts, dispatch progress, or estimated arrival date within or near the promised delivery window (no confirmed delay).\n   - DELIVERY_DELAYED: Guaranteed or promised delivery date has elapsed, or courier explicitly marked package as delayed in transit.\n   - MARKED_DELIVERED_NOT_RECEIVED: Tracking indicates delivered or left with resident/neighbour, but customer physically did not receive the parcel.\n   - CARRIER_FEEDBACK_AND_INSTRUCTIONS: Courier misconduct, driver rudeness, refusal to deliver to address, or special delivery instructions (safe place, gate code).\n\n2. RETURNS_AND_REPLACEMENTS:\n   - DAMAGED_OR_DEFECTIVE_ITEM: Item arrived physically broken, leaking, cracked, damaged packaging, or non-functional.\n   - WRONG_ITEM_RECEIVED: Completely different product, wrong SKU, wrong size, or incorrect color delivered.\n   - RETURN_PICKUP_ISSUE: Courier failed to arrive for scheduled return pickup, or problems with return drop-off/label.\n\n3. REFUNDS_AND_BILLING:\n   - REFUND_STATUS_INQUIRY: Inquiry or dispute regarding expected bank credit from a completed return or cancelled order.\n   - UNRECOGNIZED_OR_DUPLICATE_CHARGE: Disputed credit card debit, duplicate transaction, or unexpected bank charge.\n\n4. ORDER_MANAGEMENT:\n   - CANCEL_ORDER_REQUEST: Request to cancel an existing active order before or during fulfillment.\n   - MODIFY_ORDER_DETAILS: Request to change delivery address, payment method, recipient, or delivery date.\n\n5. DIGITAL_SERVICES_AND_PRIME:\n   - PRIME_MEMBERSHIP_MANAGEMENT: Unwanted Prime subscription renewal, cancellation, or Prime trial fee dispute.\n   - DIGITAL_CONTENT_ACCESS: Trouble accessing Kindle ebooks, Prime Video streaming, Amazon Music, or digital download codes.\n\n6. ACCOUNT_ACCESS_AND_SECURITY:\n   - ACCOUNT_LOGIN_ISSUES: Password reset loops, OTP verification failures, account lockouts, or unauthorized account access.\n\nALLOWED CONVERSATION STATES:\n- INITIAL_INQUIRY: First message or problem statement with no previous support actions mentioned.\n- TRACKING_ALREADY_CHECKED: Customer explicitly states they already checked tracking website or app.\n- CARRIER_ALREADY_CONTACTED: Customer explicitly states they already spoke to or called the courier/carrier.\n- DETAILS_ALREADY_PROVIDED: Customer states they already sent DM, order number, or account details.\n- WAITING_WINDOW_EXCEEDED: Customer states they were told to wait a number of days/hours and that window has passed.\n\n\nSTRICT CLASSIFICATION RULES:\n1. Return ONLY valid labels from the taxonomy above. NEVER invent new intent names or hybrid combination labels.\n2. AMBIGUOUS rule: If the customer message is too vague to know what they want (e.g., \"help please\", \"check your DM\", \"terrible service\"), set classification_status to \"AMBIGUOUS\", areas to [], intents to [], and primary_intent to null.\n3. OUT_OF_SCOPE rule: If the message is social banter, marketing praise, stock availability inquiries, or non-retail merchant support (e.g. Seller Central), set classification_status to \"OUT_OF_SCOPE\", areas to [], intents to [], and primary_intent to null.\n4. NORMAL rule: If the customer expresses an actionable support need, set classification_status to \"NORMAL\".\n5. Multi-intent rule: If the customer expresses TWO OR MORE distinct actionable issues in one inquiry (e.g., package delayed AND wants a refund), set is_multi_intent to true, list all applicable leaf intents in \"intents\", and choose the single most operationally urgent intent as \"primary_intent\".\n6. State rule: Select the most accurate conversation state from the 5 allowed states based on what the customer has already done.\n7. Output format: Respond ONLY with a valid JSON object matching this schema:\n\n{\n  \"classification_status\": \"NORMAL\" | \"AMBIGUOUS\" | \"OUT_OF_SCOPE\",\n  \"areas\": [\"AREA_NAME\"],\n  \"intents\": [\"INTENT_NAME\"],\n  \"primary_intent\": \"INTENT_NAME\" or null,\n  \"is_multi_intent\": false or true,\n  \"states\": [\"STATE_NAME\"],\n  \"confidence\": 0.95,\n  \"reasoning\": \"brief explanation\"\n}\n"
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

### Model Response (Cached in `artifacts/llm_predictions/gold_0001.json`)
```json
{
  "classification_status": "NORMAL",
  "areas": [
    "DELIVERY_AND_FULFILLMENT"
  ],
  "intents": [
    "CARRIER_FEEDBACK_AND_INSTRUCTIONS"
  ],
  "primary_intent": "CARRIER_FEEDBACK_AND_INSTRUCTIONS",
  "is_multi_intent": false,
  "states": [
    "INITIAL_INQUIRY"
  ],
  "confidence": 0.95,
  "reasoning": "Customer reports rude delivery agent who refused delivery unless someone came down, matching carrier misconduct/refusal intent."
}
```
