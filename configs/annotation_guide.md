# AmazonHelp Taxonomy v1 — Human Annotation Guide

**Status:** FROZEN  
**Taxonomy Version:** 1.0  
**Target Brand:** AmazonHelp  

This guide provides definitive rules, boundary distinguishing criteria, and concrete empirical examples for human annotators labeling AmazonHelp customer support conversations.

---

## 1. Separation of Concepts

Human annotators must never conflate orthogonal dimensions of a support conversation. Every case is evaluated along five distinct axes:

```
+-----------------------------------------------------------------------------------+
| 1. CLASSIFICATION STATUS: NORMAL | AMBIGUOUS | OUT_OF_SCOPE                       |
+-----------------------------------------------------------------------------------+
| 2. MULTI-INTENT PROPERTY: is_multi_intent: true | false                           |
+-----------------------------------------------------------------------------------+
| 3. BUSINESS INTENTS: Set of active leaf intents from the 14 frozen classes        |
+-----------------------------------------------------------------------------------+
| 4. CONVERSATION STATE: Informational stage of the customer in the dialogue        |
+-----------------------------------------------------------------------------------+
| 5. OUTCOME: Terminal resolution or disposition of the interaction                 |
+-----------------------------------------------------------------------------------+
```

1. **Business Intents (14 Leaf Classes)**: The underlying customer problem requiring business resolution.
2. **Classification Status**:
   - `NORMAL`: Issue is clearly expressed and belongs to in-scope support.
   - `AMBIGUOUS`: Inquiry lacks sufficient detail to determine routing (e.g. *"Can someone check my DM?"*, *"I have a problem with my order"*).
   - `OUT_OF_SCOPE`: Non-support messages, unsolicited feedback, marketing banter, or general social comments.
3. **Multi-Intent Property**: A boolean flag (`is_multi_intent: true/false`). When multiple independent problems are raised, list each intent in `intents: []`. Combinatorial hybrid labels (e.g. `DELAY_AND_REFUND`) are strictly prohibited.
4. **Conversation State**: The customer's situational status in multi-turn dialogues:
   - `INITIAL_INQUIRY`: Customer opening turn presenting issue.
   - `TRACKING_ALREADY_CHECKED`: Customer explicitly notes tracking link was already consulted and inadequate.
   - `CARRIER_ALREADY_CONTACTED`: Customer already contacted courier directly without resolution.
   - `DETAILS_ALREADY_PROVIDED`: Customer already sent order number/DM in a previous turn.
   - `WAITING_WINDOW_EXCEEDED`: Promised SLA or wait window (e.g. 24h/48h) has expired.
5. **Outcomes**:
   - `RESOLVED_CLOSURE`: Customer issue solved; customer confirms or thanks agent.
   - `ESCALATED_HUMAN_TIER2`: Escalated to supervisor or specialist queue.
   - `DEFLECTED_SELF_SERVICE`: Successfully routed to self-service portal (e.g. Your Orders).
   - `CONCESSION_ISSUED`: Refund, replacement, or gift credit granted.
   - `ABANDONED_UNRESPONSIVE`: Customer stops responding after agent request.

---

## 2. Multi-Intent Representation

When a customer expresses two or more distinct business problems in a single message, do NOT attempt to force a single winner or invent combination labels. Assign multiple labels from the 14 frozen leaf intents:

### Standard Multi-Intent Case:
**Customer:** *"My package is delayed and I was charged twice."*

```json
{
  "classification_status": "NORMAL",
  "is_multi_intent": true,
  "areas": [
    "DELIVERY_AND_FULFILLMENT",
    "REFUNDS_AND_BILLING"
  ],
  "intents": [
    "DELIVERY_DELAYED",
    "UNRECOGNIZED_OR_DUPLICATE_CHARGE"
  ],
  "primary_intent": "DELIVERY_DELAYED"
}
```

---

## 3. Pairwise Boundary Decision Rules

Annotators must adhere to the following rules when choosing between closely confusable intents.

### Boundary 1: `WHERE_IS_MY_ORDER` vs `DELIVERY_DELAYED`

- **Positive Rule for `WHERE_IS_MY_ORDER`**: Customer asks for current parcel location, dispatch progress, or estimated arrival date within or near the promised delivery window.
- **Positive Rule for `DELIVERY_DELAYED`**: Customer states that the promised or guaranteed delivery date has passed without arrival, or tracking explicitly says "delayed".
- **Boundary Rule**:
  - If the customer does *not* state the package is overdue, label as `WHERE_IS_MY_ORDER`.
  - If the customer explicitly mentions a missed delivery date (e.g. *"was supposed to arrive yesterday"*, *"paid for next-day and it's day 3"*), label as `DELIVERY_DELAYED`.
- **Examples**:
  - `WHERE_IS_MY_ORDER`: *"Can I have a tracking update on my order #408-5604067?"* (case `amazon_case_0039900`)
  - `DELIVERY_DELAYED`: *"My package was guaranteed for delivery by 8pm yesterday and hasn't arrived. Where is it?"* (case `amazon_case_0036794`)
- **When Evidence is Insufficient**: If the customer simply asks *"Where is my order?"* without dates or delay complaints, default to `WHERE_IS_MY_ORDER`.

---

### Boundary 2: `DELIVERY_DELAYED` vs `MARKED_DELIVERED_NOT_RECEIVED`

- **Positive Rule for `DELIVERY_DELAYED`**: Package is still in transit according to tracking, but is overdue past the SLA.
- **Positive Rule for `MARKED_DELIVERED_NOT_RECEIVED`**: Digital tracking status indicates "Delivered", "Handed to resident", or "Left in porch", but customer states they did not physically receive it.
- **Boundary Rule**:
  - If tracking status shows in-transit or late $\rightarrow$ `DELIVERY_DELAYED`.
  - If tracking status shows delivered $\rightarrow$ `MARKED_DELIVERED_NOT_RECEIVED`.
- **Examples**:
  - `DELIVERY_DELAYED`: *"Paid for next day Prime delivery on Friday, it is now Tuesday and still nothing."* (case `amazon_case_0025122`)
  - `MARKED_DELIVERED_NOT_RECEIVED`: *"Fed up with this, parcel is marked as delivered but no delivery was made."* (case `amazon_case_0005594`)
- **When Evidence is Insufficient**: If customer says *"I haven't received my order"*, check if they mention the app saying "delivered". If no mention of delivery confirmation, check conversation context; if still ambiguous, label `DELIVERY_DELAYED` if past SLA or `WHERE_IS_MY_ORDER` if inquiring.

---

### Boundary 3: `DELIVERY_DELAYED` vs `CARRIER_FEEDBACK_AND_INSTRUCTIONS`

- **Positive Rule for `DELIVERY_DELAYED`**: Primary grievance is transit timeline and overdue package.
- **Positive Rule for `CARRIER_FEEDBACK_AND_INSTRUCTIONS`**: Primary grievance is courier conduct, safe-place mishandling, gate code/access issues, driver rudeness, or customs/KYC documentation.
- **Boundary Rule**:
  - If courier threw package over fence, left in rain, or driver was rude $\rightarrow$ `CARRIER_FEEDBACK_AND_INSTRUCTIONS`.
  - If package was delayed by carrier during transit without specific driver/property complaints $\rightarrow$ `DELIVERY_DELAYED`.
- **Examples**:
  - `DELIVERY_DELAYED`: *"Carrier tracking says delayed in transit at depot for 4 days."*
  - `CARRIER_FEEDBACK_AND_INSTRUCTIONS`: *"Your courier left my package out in the pouring rain instead of putting it in the porch."* (case `amazon_case_0042191`)
- **When Evidence is Insufficient**: If customer complains that driver didn't show up on a scheduled day, prioritize `DELIVERY_DELAYED` unless driver falsified attempt records (*"Driver claimed nobody home but I was at window"* $\rightarrow$ `CARRIER_FEEDBACK_AND_INSTRUCTIONS`).

---

### Boundary 4: `DAMAGED_OR_DEFECTIVE_ITEM` vs `WRONG_ITEM_RECEIVED`

- **Positive Rule for `DAMAGED_OR_DEFECTIVE_ITEM`**: Customer received the ordered item, but it is physically broken, cracked, crushed, leaking, or electrically defective.
- **Positive Rule for `WRONG_ITEM_RECEIVED`**: Customer received an incorrect SKU, wrong size, different color, or completely different merchandise.
- **Boundary Rule**:
  - Broken/defective correct item $\rightarrow$ `DAMAGED_OR_DEFECTIVE_ITEM`.
  - Intact or broken incorrect item $\rightarrow$ `WRONG_ITEM_RECEIVED`. (If the item is completely wrong, warehouse fulfillment error is primary).
- **Examples**:
  - `DAMAGED_OR_DEFECTIVE_ITEM`: *"The screen on my Kindle arrived shattered inside the box."* (case `amazon_case_0042191`)
  - `WRONG_ITEM_RECEIVED`: *"I ordered a blue winter coat size L and received a red pair of sneakers."* (case `amazon_case_0015604`)
- **When Evidence is Insufficient**: If customer says *"Item is not right"*, check whether they describe physical breakage (defect) or incorrect specifications (wrong item). If totally unclear, set `classification_status: AMBIGUOUS`.

---

### Boundary 5: `REFUND_STATUS_INQUIRY` vs `UNRECOGNIZED_OR_DUPLICATE_CHARGE`

- **Positive Rule for `REFUND_STATUS_INQUIRY`**: Customer expects money back from a previously authorized return or cancellation and asks when it will credit their bank.
- **Positive Rule for `UNRECOGNIZED_OR_DUPLICATE_CHARGE`**: Customer discovers unauthorized, unexpected, or double debits on their bank/credit card.
- **Boundary Rule**:
  - Inquiring about return credit timeline $\rightarrow$ `REFUND_STATUS_INQUIRY`.
  - Disputing dual billing or unauthorized charges $\rightarrow$ `UNRECOGNIZED_OR_DUPLICATE_CHARGE`.
- **Examples**:
  - `REFUND_STATUS_INQUIRY`: *"I returned order #405-7027922 a week ago. When will the refund credit my bank?"* (case `amazon_case_0001850`)
  - `UNRECOGNIZED_OR_DUPLICATE_CHARGE`: *"I was charged twice on my Visa card for the exact same order #403-728."* (case `amazon_case_0001850`)
- **When Evidence is Insufficient**: If customer says *"Why did you take my money?"* after a return, classify as `REFUND_STATUS_INQUIRY`. If prior to return or unexplained, classify as `UNRECOGNIZED_OR_DUPLICATE_CHARGE`.

---

### Boundary 6: `CANCEL_ORDER_REQUEST` vs `MODIFY_ORDER_DETAILS`

- **Positive Rule for `CANCEL_ORDER_REQUEST`**: Customer requests complete cancellation/termination of the order prior to shipment.
- **Positive Rule for `MODIFY_ORDER_DETAILS`**: Customer wants to keep the order but update delivery address, payment method, or delivery day.
- **Boundary Rule**:
  - Customer wants to stop the purchase $\rightarrow$ `CANCEL_ORDER_REQUEST`.
  - Customer wants the item but needs details corrected $\rightarrow$ `MODIFY_ORDER_DETAILS`.
- **Examples**:
  - `CANCEL_ORDER_REQUEST`: *"I accidentally ordered two of these. Please cancel order #104-569 immediately."* (case `amazon_case_0034643`)
  - `MODIFY_ORDER_DETAILS`: *"I put in my old apartment address by mistake. Can I update the shipping address?"* (case `amazon_case_0034643`)
- **When Evidence is Insufficient**: If customer says *"Wrong address, help!"*, check if they ask to change it (`MODIFY_ORDER_DETAILS`) or ask to cancel and re-order (`CANCEL_ORDER_REQUEST`).

---

### Boundary 7: `PRIME_MEMBERSHIP_MANAGEMENT` vs `DIGITAL_CONTENT_ACCESS`

- **Positive Rule for `PRIME_MEMBERSHIP_MANAGEMENT`**: Inquiries regarding Prime subscription status, fee renewals, student discounts, or Prime membership cancellation.
- **Positive Rule for `DIGITAL_CONTENT_ACCESS`**: Technical problems streaming Prime Video, reading Kindle books, listening to Amazon Music, or linking Echo/Fire devices.
- **Boundary Rule**:
  - Billing/account level Prime questions $\rightarrow$ `PRIME_MEMBERSHIP_MANAGEMENT`.
  - Media playback, device compatibility, app error codes $\rightarrow$ `DIGITAL_CONTENT_ACCESS`.
- **Examples**:
  - `PRIME_MEMBERSHIP_MANAGEMENT`: *"Did not mean to sign up for Prime auto-renewal, please cancel and refund the £79."* (case `amazon_case_0025122`)
  - `DIGITAL_CONTENT_ACCESS`: *"Prime Video app keeps giving error code 5004 on my Samsung TV."* (case `amazon_case_0024894`)
- **When Evidence is Insufficient**: If customer says *"Prime Video isn't working because of my subscription"*, evaluate if primary issue is expired subscription (`PRIME_MEMBERSHIP_MANAGEMENT`) or software error (`DIGITAL_CONTENT_ACCESS`). If both, flag as multi-intent.

---

### Boundary 8: `ACCOUNT_LOGIN_ISSUES`

- **Positive Rule for `ACCOUNT_LOGIN_ISSUES`**: Customer is unable to log in due to OTP verification codes not arriving, expired password reset links, locked accounts, or forgotten credentials.
- **Boundary Rule**:
  - Authentication barriers (OTP, password, sign-in lockout) $\rightarrow$ `ACCOUNT_LOGIN_ISSUES`.
  - Suspected account compromise where unauthorized orders were placed $\rightarrow$ label `ACCOUNT_LOGIN_ISSUES` and flag for security escalation.
- **Examples**:
  - *"Cannot log in. OTP verification SMS is never delivered to my phone."* (case `amazon_case_0017954`)
  - *"Password reset link expired before I received it."* (case `amazon_case_0114638`)
- **When Evidence is Insufficient**: If customer says *"Cannot access my account"*, verify if it is credential/login related (`ACCOUNT_LOGIN_ISSUES`) or closed account policy. If no detail, mark `classification_status: AMBIGUOUS`.

---

## 4. Summary Table of 14 Frozen Leaf Intents

| Area | Frozen Leaf Intent | Concise Definition |
|---|---|---|
| `DELIVERY_AND_FULFILLMENT` | `WHERE_IS_MY_ORDER` | Customer asks where an order/package is or requests tracking status without a clearly established missed promised date. |
| `DELIVERY_AND_FULFILLMENT` | `DELIVERY_DELAYED` | Customer reports that the expected/promised delivery time has passed or the shipment is explicitly delayed. |
| `DELIVERY_AND_FULFILLMENT` | `MARKED_DELIVERED_NOT_RECEIVED` | Tracking indicates delivery, but customer states the physical package was not received. |
| `DELIVERY_AND_FULFILLMENT` | `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | Customer provides feedback, complaints, or instructions regarding courier driver conduct, property placement, gate access, or customs/KYC clearance. |
| `RETURNS_AND_REPLACEMENTS` | `DAMAGED_OR_DEFECTIVE_ITEM` | Customer received the correct ordered item, but it is physically broken, crushed, leaking, defective, or non-functional out of the box. |
| `RETURNS_AND_REPLACEMENTS` | `WRONG_ITEM_RECEIVED` | Customer received a shipment containing an incorrect item, wrong size, or different product variant than what was ordered. |
| `RETURNS_AND_REPLACEMENTS` | `RETURN_PICKUP_ISSUE` | Customer has an authorized return/replacement, but the carrier missed/failed scheduled pickup or drop-off code failed. |
| `REFUNDS_AND_BILLING` | `REFUND_STATUS_INQUIRY` | Customer inquires about the status, timeline, or bank credit of a refund for an already returned item or cancelled order. |
| `REFUNDS_AND_BILLING` | `UNRECOGNIZED_OR_DUPLICATE_CHARGE` | Customer reports duplicate charges, unrecognized deductions, or unexpected billing debits on their bank or credit card statement. |
| `ORDER_MANAGEMENT` | `CANCEL_ORDER_REQUEST` | Customer requests to cancel an active order prior to dispatch/shipment. |
| `ORDER_MANAGEMENT` | `MODIFY_ORDER_DETAILS` | Customer requests modifications to order attributes (such as shipping address, payment method, or delivery slot) while keeping the order active. |
| `DIGITAL_SERVICES_AND_PRIME` | `PRIME_MEMBERSHIP_MANAGEMENT` | Customer inquires about Prime membership renewal, trial conversion fees, plan cancellation, or membership billing adjustments. |
| `DIGITAL_SERVICES_AND_PRIME` | `DIGITAL_CONTENT_ACCESS` | Customer reports technical barriers or playback failures accessing digital services such as Prime Video, Kindle ebooks, Amazon Music, or digital apps. |
| `ACCOUNT_ACCESS_AND_SECURITY` | `ACCOUNT_LOGIN_ISSUES` | Customer is unable to log in due to OTP verification code delivery failures, expired reset links, forgotten credentials, or account access lockouts. |
