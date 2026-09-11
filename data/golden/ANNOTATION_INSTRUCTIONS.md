# AmazonHelp Golden Set — Human Annotation Instructions

**Benchmark Version:** `golden_v1` (200 cases)  
**Taxonomy Reference:** `configs/taxonomy_v1.yaml`  
**Detailed Boundary Guide:** `configs/annotation_guide.md`  
**Review File:** `data/golden/golden_annotation_review.csv`  

---

## 1. Ground Rules & Core Philosophy

> [!IMPORTANT]
> **The existing proposed labels are NOT ground truth.**
> They are machine/heuristic proposals for reference. Human annotators must evaluate each conversation independently and establish definitive ground truth in the `human_*` columns.

### Non-Negotiable Labeling Principles:

1. **Read Full Conversation Context, Not Just the Customer Message**:
   Single tweets on Twitter can be truncated, refer back to previous turns, or omit critical details that are only revealed in the surrounding context. Always read `context` before deciding.

2. **`AMBIGUOUS` is a Status, NOT an Intent**:
   If a message lacks sufficient details to know what the customer wants (e.g. *"Can someone please check my DM?"*, *"I have a problem with my order"*), set:
   - `human_status = AMBIGUOUS`
   - `human_areas = ""`
   - `human_intents = ""`
   - `human_primary_intent = ""`
   Do NOT invent or guess a business intent for ambiguous messages.

3. **`OUT_OF_SCOPE` is a Domain Gate Status, NOT an Intent**:
   If a message is social banter, marketing praise, stock questions, or non-support content (e.g. *"Congratulations to Jeff Bezos!"*), set:
   - `human_status = OUT_OF_SCOPE`
   - `human_areas = ""`
   - `human_intents = ""`
   - `human_primary_intent = ""`
   **Critical Rule:** Do NOT call genuine customer support complaints *OUT_OF_SCOPE* simply because they are angry, sarcastic, or poorly phrased.

4. **`MULTI_INTENT` is Represented by Multiple Intents (Multi-Label)**:
   Never create hybrid or combination labels (e.g. `DELAY_AND_REFUND` is prohibited).
   If a customer raises two or more distinct actionable issues in one message:
   - `human_status = NORMAL`
   - `human_intents = INTENT_A|INTENT_B`
   - `human_areas = AREA_A|AREA_B`
   - `human_primary_intent =` the most operationally central intent

5. **Conversation State is Strictly Decoupled from Intent**:
   The customer's situational progress in dialogue (`INITIAL_INQUIRY`, `TRACKING_ALREADY_CHECKED`, `CARRIER_ALREADY_CONTACTED`, `DETAILS_ALREADY_PROVIDED`, `WAITING_WINDOW_EXCEEDED`) describes *what has already happened*, while intent describes *what the customer needs*. Never conflate state with intent.

6. **Outcome is Separate from Intent**:
   Outcome describes the terminal disposition of the ticket (`RESOLVED_CLOSURE`, `ESCALATED_HUMAN_TIER2`, etc.) and must not be mixed into business intent.

---

## 2. Key Intent Boundary Distinctions

Before annotating, review these 4 most common confusion pairs from [`configs/annotation_guide.md`](file:///e:/Intern_Presentation/Hiver%20Project/configs/annotation_guide.md):

### A. `WHERE_IS_MY_ORDER` vs `DELIVERY_DELAYED`
- **`WHERE_IS_MY_ORDER`**: Customer is asking for package whereabouts, dispatch progress, or estimated arrival date within or near the promised delivery window without a confirmed missed date.
- **`DELIVERY_DELAYED`**: Customer states the promised/guaranteed delivery date has elapsed, or tracking explicitly says "delayed in transit".
- *Rule:* If the customer doesn't state it's past due, choose `WHERE_IS_MY_ORDER`. If they state it was due yesterday or is overdue, choose `DELIVERY_DELAYED`.

### B. `DELIVERY_DELAYED` vs `MARKED_DELIVERED_NOT_RECEIVED`
- **`DELIVERY_DELAYED`**: The package is still in transit (not delivered) according to tracking.
- **`MARKED_DELIVERED_NOT_RECEIVED`**: Digital tracking shows "Delivered", "Handed to resident", or "Left in porch", but customer states they physically did not receive it.
- *Rule:* If tracking indicates delivered but the customer has no package, choose `MARKED_DELIVERED_NOT_RECEIVED`.

### C. `WRONG_ITEM_RECEIVED` vs `DAMAGED_OR_DEFECTIVE_ITEM`
- **`WRONG_ITEM_RECEIVED`**: The package arrived with the incorrect SKU, wrong size, or completely different product. (Triggers mandatory return label and inventory replacement).
- **`DAMAGED_OR_DEFECTIVE_ITEM`**: Customer received the correct ordered product, but it arrived physically broken, leaking, cracked, or non-functional. (Often eligible for concession/replacement without physical return).

### D. `REFUND_STATUS_INQUIRY` vs `UNRECOGNIZED_OR_DUPLICATE_CHARGE`
- **`REFUND_STATUS_INQUIRY`**: Follow-up regarding expected bank credit from a previously authorized return or cancellation.
- **`UNRECOGNIZED_OR_DUPLICATE_CHARGE`**: Disputed credit card debit, dual authorization hold, or unwanted subscription renewal charge.

---

## 3. Human Review Column Schema (`golden_annotation_review.csv`)

When reviewing each row in `data/golden/golden_annotation_review.csv`, fill in the empty `human_*` columns:

| Column Name | Permissible Values / Format | Description |
|---|---|---|
| `human_status` | `NORMAL`, `AMBIGUOUS`, `OUT_OF_SCOPE` | High-level classification status. |
| `human_areas` | Pipe-delimited list from the 6 areas, e.g. `DELIVERY_AND_FULFILLMENT` or `DELIVERY_AND_FULFILLMENT\|REFUNDS_AND_BILLING`. Leave empty if not `NORMAL`. |
| `human_intents` | Pipe-delimited list from the 14 frozen leaf intents, e.g. `DELIVERY_DELAYED` or `DELIVERY_DELAYED\|UNRECOGNIZED_OR_DUPLICATE_CHARGE`. Leave empty if not `NORMAL`. |
| `human_primary_intent` | Single intent from `human_intents`. Must be non-empty if `human_status == NORMAL`, empty otherwise. |
| `human_states` | Pipe-delimited list from: `INITIAL_INQUIRY`, `TRACKING_ALREADY_CHECKED`, `CARRIER_ALREADY_CONTACTED`, `DETAILS_ALREADY_PROVIDED`, `WAITING_WINDOW_EXCEEDED`. |
| `human_should_escalate` | `True` or `False` | True if the case requires human agent intervention under security, fraud, or repeated SLA failure policies. |
| `human_escalation_reason` | Pipe-delimited list, e.g. `ACCOUNT_SECURITY_COMPROMISE`, `SECURITY_LOCKOUT`, `REPEATED_FAILED_SUPPORT_ATTEMPTS`, `CARRIER_MISCONDUCT_SEVERE`. Leave empty if `human_should_escalate == False`. |
| `human_notes` | Free text | Document boundary edge cases, rationale for overturning proposed labels, or subtle nuances. |

---

## 4. Frozen Vocabulary Reference (Taxonomy v1)

### 6 Broad Business Areas:
1. `DELIVERY_AND_FULFILLMENT`
2. `RETURNS_AND_REPLACEMENTS`
3. `REFUNDS_AND_BILLING`
4. `ORDER_MANAGEMENT`
5. `DIGITAL_SERVICES_AND_PRIME`
6. `ACCOUNT_ACCESS_AND_SECURITY`

### 14 Frozen Leaf Intents:
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
