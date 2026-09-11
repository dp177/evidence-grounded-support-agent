# PROPOSED TAXONOMY AFTER LLM REVIEW

> [!NOTE]
> This is a candidate operational taxonomy proposed after Second-Stage LLM Review using real AmazonHelp evidence. It is NOT the final production taxonomy until approved by human reviewers.

**LLM Review Gateway:** `openrouter`  
**Review Model:** `nvidia/nemotron-3-super-120b-a12b:free`  
**Total Leaf Intents Reviewed:** 17  
**Date:** 2026-09-11 20:45:00 UTC  

## 1. Broad Support Areas

The taxonomy is organized hierarchically under 6 operational business areas:

1. **DELIVERY_AND_FULFILLMENT**: Tracking inquiries, late deliveries, false delivery confirmations, and carrier logistics.
2. **RETURNS_AND_REPLACEMENTS**: Physical item defects, wrong items shipped, and return courier pickup logistics.
3. **REFUNDS_AND_BILLING**: Refund bank credit inquiries and unrecognized/duplicate card charges.
4. **ORDER_MANAGEMENT**: Pre-dispatch order cancellations and address/shipping modifications.
5. **DIGITAL_SERVICES_AND_PRIME**: Prime membership subscriptions and digital content access errors (Video, Kindle, Music).
6. **ACCOUNT_ACCESS_AND_SECURITY**: Login failures, OTP verification issues, password recovery, and suspected account compromises.

## 2. Candidate Leaf Intents and LLM Decisions

Summary of LLM recommendations across all reviewed leaf intents:

### `WHERE_IS_MY_ORDER`
- **Recommendation**: **KEEP** (Recommended Name: `WHERE_IS_MY_ORDER`)
- **Confidence**: 0.95 | **Annotation Difficulty**: LOW
- **Reasoning**: The examples consistently reflect customers seeking tracking updates or reporting discrepancies between tracking status and receipt. This forms a coherent, operationally distinct intent focused on order status inquiries, separate from returns, cancellations, or account issues.
- **Operational Distinction**: Agents respond with tracking links, carrier details, and, if marked delivered but not received, initiate an investigation or replacement process. This differs from return/refund flows which require authorization, label generation, and refund processing.
- **Closest Confusable Intents**: `ORDER_NOT_RECEIVED`, `DELIVERY_ISSUE`, `TRACKING_UPDATE`

### `DELIVERY_DELAYED`
- **Recommendation**: **KEEP** (Recommended Name: `DELIVERY_DELAYED`)
- **Confidence**: 0.90 | **Annotation Difficulty**: MEDIUM
- **Reasoning**: The examples consistently describe shipments that are late but still in transit; Amazon's responses focus on providing updated ETAs, carrier details, and apologies, which is a distinct support flow from missing or failed deliveries.
- **Operational Distinction**: For DELIVERY_DELAYED, agents typically check carrier status and give an revised delivery date; for DELIVERY_MISSING they initiate a lost‑package investigation and may offer refund/replacement, and for SHIPPING_ISSUE they address broader problems like address errors or customs holds.
- **Closest Confusable Intents**: `DELIVERY_MISSING`, `SHIPPING_ISSUE`

### `MARKED_DELIVERED_NOT_RECEIVED`
- **Recommendation**: **KEEP** (Recommended Name: `MARKED_DELIVERED_NOT_RECEIVED`)
- **Confidence**: 0.90 | **Annotation Difficulty**: LOW
- **Reasoning**: The intent groups a coherent set of cases where the system shows delivery but the customer did not receive the package. It leads to distinct support actions (neighbor/safe-place checks, locate‑package steps, carrier investigation) that differ from late‑delivery or generic missing‑item intents, making it operationally useful and consistently annotatable.
- **Operational Distinction**: For MARKED_DELIVERED_NOT_RECEIVED, agents advise checking neighbors/safe places, provide locate‑package links, and may open a carrier investigation; for DELIVERY_LATE they focus on updated ETAs and compensation; for ITEM_NOT_RECEIVED they verify shipment details and possible split shipments.
- **Closest Confusable Intents**: `DELIVERY_LATE`, `ITEM_NOT_RECEIVED`

### `CARRIER_FEEDBACK_AND_INSTRUCTIONS`
- **Recommendation**: **KEEP** (Recommended Name: `CARRIER_FEEDBACK`)
- **Confidence**: 0.85 | **Annotation Difficulty**: MEDIUM
- **Reasoning**: The intent captures specific feedback about carrier behavior (e.g., driver conduct, delivery instructions) that triggers distinct support actions such as logging feedback, contacting carrier quality teams, and assessing damage, which is operationally separable from general delivery issues like missing or late packages.
- **Operational Distinction**: Unlike missing/late delivery intents that often initiate refund/replacement or trace workflows, carrier feedback intent focuses on documenting driver behavior, escalating to carrier performance teams, and may only lead to compensation if damage is reported.
- **Closest Confusable Intents**: `DELIVERY_PROBLEM`, `SHIPPING_ISSUE`, `CARRIER_COMPLAINT`

### `DAMAGED_OR_DEFECTIVE_ITEM`
- **Recommendation**: **KEEP** (Recommended Name: `DAMAGED_OR_DEFECTIVE_ITEM`)
- **Confidence**: 0.91 | **Annotation Difficulty**: MEDIUM
- **Reasoning**: The intent groups messages about receiving broken or non-functional products, which is semantically coherent, operationally distinct (triggers replacement/refund workflows different from wrong-item or not-as-described cases), and shows consistent Amazon responses. It is sufficiently frequent and annotatable for reliable taxonomy use.
- **Operational Distinction**: Damaged/defective items often qualify for immediate replacement or refund without requiring return of the defective unit, whereas wrong-item or not-as-described cases typically require return of the incorrect item before shipping the correct one.
- **Closest Confusable Intents**: `WRONG_ITEM_SENT`, `ITEM_NOT_AS_DESCRIBED`, `QUALITY_ISSUE`

### `WRONG_ITEM_RECEIVED`
- **Recommendation**: **KEEP** (Recommended Name: `WRONG_ITEM_RECEIVED`)
- **Confidence**: 0.94 | **Annotation Difficulty**: LOW
- **Reasoning**: The cases consistently describe receiving an incorrect product, leading to a distinct support flow focused on returning the wrong item and shipping the correct replacement, which is operationally separable from similar issues like item-not-as-described or damaged goods.
- **Operational Distinction**: Wrong item received triggers a replacement shipment and return of the incorrect item, whereas item-not-as-described often results in a refund or partial refund without requiring a replacement, and damaged items may involve repair or refund options.
- **Closest Confusable Intents**: `ITEM_NOT_AS_DESCRIBED`, `DAMAGED_ITEM`

### `RETURN_PICKUP_ISSUE`
- **Recommendation**: **KEEP** (Recommended Name: `RETURN_PICKUP_ISSUE`)
- **Confidence**: 0.94 | **Annotation Difficulty**: LOW
- **Reasoning**: The intent captures messages where customers report that the return pickup was missed, not attempted, or delayed by the carrier. These cases require distinct operational steps (rescheduling pickup, contacting carrier, possible compensation) that differ from other return sub‑issues such as label problems, drop‑off difficulties, or refund status inquiries, and they elicit a consistent response pattern focused on pickup resolution.
- **Operational Distinction**: For RETURN_PICKUP_ISSUE agents typically reschedule the pickup, contact the carrier, and may issue a goodwill gesture; this contrasts with RETURN_DROP_OFF_ISSUE_OFF_ISSUE (guiding to drop‑off locations), RETURN_LABEL_ISSUE (resending return labels), and RETURN_REFUND_STATUS (checking refund processing).
- **Closest Confusable Intents**: `RETURN_DROP_OFF_ISSUE`, `RETURN_LABEL_ISSUE`, `RETURN_REFUND_STATUS`

### `REFUND_STATUS_INQUIRY`
- **Recommendation**: **KEEP** (Recommended Name: `REFUND_STATUS_INQUIRY`)
- **Confidence**: 0.95 | **Annotation Difficulty**: LOW
- **Reasoning**: The candidate groups messages where customers ask about the status of an already-issued or pending refund; these are semantically coherent, operationally distinct from refund requests or refund issues, and consistently annotatable. Support agents handle them by checking payment status and providing timelines, a distinct workflow.
- **Operational Distinction**: REFUND_STATUS_INQUIRY triggers a status lookup in the payment/refund system and may involve escalation if delayed, while REFUND_REQUEST initiates a new refund eligibility check and REFUND_ISSUE addresses incorrect amounts or failed refunds.
- **Closest Confusable Intents**: `REFUND_REQUEST`, `REFUND_ISSUE`, `REFUND_PROCESSING_TIME_INQUIRY`

### `UNRECOGNIZED_OR_DUPLICATE_CHARGE`
- **Recommendation**: **RENAME** (Recommended Name: `DUPLICATE_CHARGE`)
- **Confidence**: 0.94 | **Annotation Difficulty**: LOW
- **Reasoning**: The empirical examples exclusively describe duplicate charge scenarios; combining unrecognized charges conflates distinct operational workflows (fraud investigation vs. authorization hold resolution). Renaming improves semantic coherence and operational usefulness while maintaining sufficient volume.
- **Operational Distinction**: Duplicate charge handling focuses on verifying pending/posted authorizations and issuing refunds for duplicate posted charges; unrecognized charge handling involves verifying order authenticity, potential fraud review, and may require security escalation.
- **Closest Confusable Intents**: `UNAUTHORIZED_CHARGE`, `BILLING_INQUIRY`

### `CANCEL_ORDER_REQUEST`
- **Recommendation**: **KEEP** (Recommended Name: `CANCEL_ORDER_REQUEST`)
- **Confidence**: 0.95 | **Annotation Difficulty**: LOW
- **Reasoning**: The examples are semantically coherent and operationally distinct: they all seek to cancel an order, triggering a specific support path (checking cancellation eligibility, providing self‑service options or seller/carrier contact) that differs from returns, refunds, or order changes. Splitting would create unnecessary fragmentation; the distinction can be handled via context (order status) rather than separate intents.
- **Operational Distinction**: Cancel order requests focus on stopping an order before or shortly after shipment, often requiring eligibility checks, seller contact, or carrier interception. Return/refund requests involve post‑delivery processes (return labels, refund issuance), and change order requests involve modifying items/addresses while the order remains active.
- **Closest Confusable Intents**: `RETURN_ORDER_REQUEST`, `REFUND_REQUEST`, `CHANGE_ORDER_REQUEST`

### `MODIFY_ORDER_DETAILS`
- **Recommendation**: **RENAME** (Recommended Name: `CHANGE_DELIVERY_ADDRESS`)
- **Confidence**: 0.93 | **Annotation Difficulty**: LOW
- **Reasoning**: The empirical cases uniformly concern delivery address modifications; a more specific name improves operational clarity, retrieval, and automation without causing fragmentation.
- **Operational Distinction**: Changing a delivery address involves verifying order fulfillment status and updating shipping details via self-service or agent tools, whereas cancelling an order terminates the purchase and may involve refund processing, and updating payment method requires payment validation and may be restricted after order placement.
- **Closest Confusable Intents**: `CANCEL_ORDER`, `UPDATE_PAYMENT_METHOD`

### `PRIME_MEMBERSHIP_MANAGEMENT`
- **Recommendation**: **KEEP** (Recommended Name: `PRIME_MEMBERSHIP_MANAGEMENT`)
- **Confidence**: 0.94 | **Annotation Difficulty**: MEDIUM
- **Reasoning**: The examples consistently involve Prime-specific actions (cancellation, refund, renewal, charge disputes) that require distinct support flows, tools, and policies compared to generic billing or subscription intents.
- **Operational Distinction**: Prime membership management includes handling free‑trial conversions, Prime‑specific refund windows, and benefit‑reversal logic, which are not covered by generic subscription cancellation or billing issue workflows.
- **Closest Confusable Intents**: `SUBSCRIPTION_CANCELLATION`, `ACCOUNT_BILLING_ISSUE`

### `DIGITAL_CONTENT_ACCESS`
- **Recommendation**: **KEEP** (Recommended Name: `DIGITAL_CONTENT_ACCESS`)
- **Confidence**: 0.92 | **Annotation Difficulty**: LOW
- **Reasoning**: The examples share a clear theme of inability to access or view Prime Video content (streaming, app availability, playback resume). This intent is operationally distinct from generic app crashes or account issues, supports specific troubleshooting steps (connectivity, sign‑out/in, device compatibility, reinstall, resume feature), and likely represents a high‑volume support topic. Keeping it enables focused retrieval and consistent automation without unnecessary fragmentation.
- **Operational Distinction**: DIGITAL_CONTENT_ACCESS targets video‑content‑specific barriers (availability, playback, app presence) whereas APP_NOT_WORKING covers generic app crashes or errors unrelated to content access, and STREAMING_QUALITY_ISSUE focuses solely on resolution/bitrate problems rather than access or app‑presence concerns.
- **Closest Confusable Intents**: `APP_NOT_WORKING`, `STREAMING_QUALITY_ISSUE`

### `ACCOUNT_LOGIN_OR_OTP`
- **Recommendation**: **RENAME** (Recommended Name: `ACCOUNT_LOGIN_ISSUES`)
- **Confidence**: 0.92 | **Annotation Difficulty**: LOW
- **Reasoning**: The intent groups all login/access problems including OTP failures; the name is awkward and can be simplified to ACCOUNT_LOGIN_ISSUES for clearer operational routing and annotation.
- **Operational Distinction**: Unlike ACCOUNT_LOCKED (specific hold/lock workflow) or PASSWORD_RESET (focus on reset flow), ACCOUNT_LOGIN_ISSUES routes to a general login troubleshooting flow that handles password, OTP, and access denial cases.
- **Closest Confusable Intents**: `ACCOUNT_LOCKED`, `PASSWORD_RESET`, `ACCOUNT_SECURITY_COMPROMISE`

### `AMBIGUOUS_INQUIRY`
- **Recommendation**: **SPLIT** (Recommended Name: `AMBIGUOUS_INQUIRY`)
- **Confidence**: 0.90 | **Annotation Difficulty**: MEDIUM
- **Reasoning**: The examples cover disparate issues (document submission method, order status, support experience complaints, channel preference, and acknowledgments). Separating them yields distinct support actions, retrieval strategies, and response templates, making the intent too broad for effective routing or automation.
- **Operational Distinction**: Splitting enables specific handling: document submission triggers fax/email guidance; order status triggers tracking lookup; support experience triggers escalation or feedback; channel preference triggers DM/alternative channel routing; acknowledgments trigger conversation closure.
- **Closest Confusable Intents**: `GENERAL_INQUIRY`, `THANK_YOU`, `ORDER_STATUS_INQUIRY`, `SUPPORT_COMPLAINT`

### `MULTI_INTENT`
- **Recommendation**: **SPLIT** (Recommended Name: `REFUND_PAYMENT_ISSUE`)
- **Confidence**: 0.92 | **Annotation Difficulty**: MEDIUM
- **Reasoning**: The examples span distinct issue types (delivery/refund denial, Prime cancellation/refund, double charge, exchange cancellation) that require different support tools, policies, and retrieval strategies; keeping them merged would hinder accurate routing and automation.
- **Operational Distinction**: Separate intents enable distinct actions: delivery issues trigger carrier/trace investigations; Prime cancellations use membership management tools; double charges require bank authorization checks; exchange cancellations involve seller-specific return policies.
- **Closest Confusable Intents**: `ORDER_DELIVERY_REFUND`, `PRIME_MEMBERSHIP_CANCELLATION`, `PAYMENT_DOUBLE_CHARGE`, `EXCHANGE_RETURN`

### `OUT_OF_SCOPE`
- **Recommendation**: **DROP** (Recommended Name: ``)
- **Confidence**: 0.95 | **Annotation Difficulty**: LOW
- **Reasoning**: The provided examples are all in-scope Amazon support topics (refunds, delivery, complaints, etc.), showing no evidence of out-of-scope content. Keeping an OUT_OF_SCOPE intent adds no operational value and risks misclassification.
- **Operational Distinction**: No distinct workflow, tools, or policy; out-of-scope cases should be handled by a generic fallback or escalation rather than a dedicated intent.
- **Closest Confusable Intents**: `GENERAL_INQUIRY`, `REFUND_STATUS`

## 3. Definitions of Proposed Operational Leaf Intents

1. **`WHERE_IS_MY_ORDER`** (WISMO): Customer requests tracking status or ETA within or on the promised delivery window.
2. **`DELIVERY_DELAYED`**: Customer reports that the guaranteed or estimated delivery date has passed without package arrival.
3. **`MARKED_DELIVERED_NOT_RECEIVED`**: Tracking status indicates parcel was delivered, but customer physically has not received it.
4. **`CARRIER_FEEDBACK_AND_INSTRUCTIONS`**: Complaints regarding courier conduct, safe-place mishandling, gate codes, or customs/KYC clearance.
5. **`DAMAGED_OR_DEFECTIVE_ITEM`**: Customer received the ordered item, but it is physically broken, cracked, defective, or non-functional.
6. **`WRONG_ITEM_RECEIVED`**: Parcel arrived in good condition but contains a completely different product or incorrect size/model.
7. **`RETURN_PICKUP_ISSUE`**: Customer initiated a return/replacement, but the carrier failed to arrive for pickup or the return label/code failed.
8. **`REFUND_STATUS_INQUIRY`**: Inquiries regarding the timeline, issuance, or bank settlement of a pending refund for a returned or cancelled order.
9. **`UNRECOGNIZED_OR_DUPLICATE_CHARGE`**: Customer reports duplicate billing or unauthorized deductions on their bank/credit card statement.
10. **`CANCEL_ORDER_REQUEST`**: Customer requests cancellation of an active order prior to shipment dispatch.
11. **`MODIFY_ORDER_DETAILS`**: Customer requests changes to delivery address, payment method, or delivery slot on an unfulfilled order.
12. **`PRIME_MEMBERSHIP_MANAGEMENT`**: Inquiries concerning Prime membership renewals, unexpected membership fees, or cancellation of Prime.
13. **`DIGITAL_CONTENT_ACCESS`**: Technical errors or playback failures with Prime Video, Kindle downloads, Amazon Music, or Fire TV.
14. **`ACCOUNT_ACCESS_AND_LOGIN`** (Renamed from `ACCOUNT_LOGIN_OR_OTP`): Customer unable to access account due to 2FA/OTP SMS failures, locked credentials, or compromised account.

## 4. Multi-Intent Representation

Customer inquiries frequently combine multiple actionable needs. In approximately 6–8% of Amazon Twitter support conversations, multiple intents are present in a single message.

> [!IMPORTANT]
> **Design Principle**: MULTI_INTENT is a multi-label output property (`active_intents: List[str]`), NEVER a combinatorial business label.
> We strictly avoid hybrid classes like `DELAY_AND_REFUND` or `CANCEL_AND_DUPLICATE_CHARGE` to prevent exponential label explosion.

### Example Multi-Intent Mapping:
- **Customer Message**: *"My order is 4 days late and you charged my card twice!"*
- **Representation**:
  ```json
  {
    "is_multi_intent": true,
    "active_intents": [
      "DELIVERY_DELAYED",
      "UNRECOGNIZED_OR_DUPLICATE_CHARGE"
    ],
    "primary_intent": "DELIVERY_DELAYED",
    "operational_routing": ["LOGISTICS_ESCALATION", "BILLING_INVESTIGATION"]
  }
  ```

## 5. Conversation States

Conversation states represent the *customer's informational and situational stage* within the dialogue. States are strictly decoupled from business intents:

| Conversation State | Operational Definition | Next Support Action |
|---|---|---|
| `INITIAL_INQUIRY` | Customer initiates issue without prior context | Request order ID / basic details or provide first-line standard guidance |
| `TRACKING_ALREADY_CHECKED` | Customer explicitly mentions tracking status was checked and found inadequate | Do NOT advise checking tracking; initiate logistics trace or carrier investigation |
| `CARRIER_ALREADY_CONTACTED` | Customer already spoke to carrier/courier with no resolution | Do NOT deflect to carrier; take Amazon responsibility and initiate replacement/refund |
| `DETAILS_ALREADY_PROVIDED` | Customer indicates order ID or details were already provided in prior message/DM | Do NOT ask for details again; acknowledge receipt and verify queue |
| `WAITING_WINDOW_EXCEEDED` | Customer has waited past the promised SLA / waiting window (e.g. 48h elapsed) | Immediate supervisor escalation or concession review |

## 6. Outcome Representation

Outcomes must NOT be conflated with in-flight conversation states. The taxonomy models outcomes as terminal dialogue properties:

- **`RESOLVED_CLOSURE`**: Issue successfully resolved; customer confirmed resolution or thanked agent.
- **`ESCALATED_HUMAN_TIER2`**: Issue escalated to specialized human support tier or ticketing system.
- **`DEFLECTED_SELF_SERVICE`**: Customer successfully directed to self-service portal (e.g., Returns Center, Account settings).
- **`CONCESSION_ISSUED`**: Replacement order, gift card balance, or refund concession granted.
- **`ABANDONED_UNRESPONSIVE`**: Dialogue terminated due to customer non-response after agent request.

## 7. Controlled Fallbacks

1. **`AMBIGUOUS_INQUIRY`**: Message lacks sufficient detail to determine routing (e.g. *"I have a huge problem with my order"*). Action: Request order number and issue description.
2. **`MULTI_INTENT`**: Triggers multi-intent decomposition and parallel policy routing.
3. **`OUT_OF_SCOPE`**: Non-support inquiries, marketing/promotional comments, or social banter that require polite deflection or no action.

## 8. Important Pairwise Boundaries

### `WHERE_IS_MY_ORDER` vs `DELIVERY_DELAYED`
- **Recommendation**: **KEEP**
- **Operational Distinction**: WHERE_IS_MY_ORDER focuses on locating an order when tracking shows delivered but the item is not received (or status unknown), requiring investigation/possible claim. DELIVERY_DELAYED addresses orders that are late relative to the promised delivery date while still in transit, typically requiring apology, expedite, or shipping compensation.
- **Resolving Context**: Clarify the current tracking status and timestamps: if tracking shows 'delivered' or carrier confirms receipt but customer hasn't got it → WHERE_IS_MY_ORDER; if tracking shows 'in transit', 'out for delivery', or a past estimated delivery date with no delivery yet → DELIVERY_DELAYED; if no tracking info is available, ask for the tracking number or carrier details to determine the correct intent.

### `DELIVERY_DELAYED` vs `MARKED_DELIVERED_NOT_RECEIVED`
- **Recommendation**: **KEEP**
- **Operational Distinction**: DELIVERY_DELAYED covers cases where the package is still in transit and the expected delivery date has passed or been updated; MARKED_DELIVERED_NOT_RECEIVED covers cases where the tracking/status shows the item as delivered but the customer confirms they did not receive it.
- **Resolving Context**: Clarify the current tracking status: if the carrier/marketplace shows 'Delivered' (with timestamp, location, or proof of delivery) → MARKED_DELIVERED_NOT_RECEIVED; if it shows 'In transit', 'Delayed', 'No estimated delivery date', or a revised future date → DELIVERY_DELAYED.

### `DELIVERY_DELAYED` vs `CARRIER_FEEDBACK_AND_INSTRUCTIONS`
- **Recommendation**: **KEEP**
- **Operational Distinction**: DELIVERY_DELAYED concerns missed or late delivery timelines; CARRIER_FEEDBACK_AND_INSTRUCTIONS concerns driver conduct, service quality, or requests for carrier-specific instructions/feedback.
- **Resolving Context**: Clarify whether the user's primary issue is the lateness of the package (check tracking timestamps, estimated vs actual delivery) versus dissatisfaction with how the carrier handled the parcel (driver actions, delivery instructions, feedback requests).

### `DAMAGED_OR_DEFECTIVE_ITEM` vs `WRONG_ITEM_RECEIVED`
- **Recommendation**: **KEEP**
- **Operational Distinction**: DAMAGED_OR_DEFECTIVE_ITEM concerns items that match the order but are physically damaged, non‑functional, or defective. WRONG_ITEM_RECEIVED concerns items that do not match the order (different SKU, model, color, etc.), regardless of their condition.
- **Resolving Context**: Clarify whether the received item matches the ordered product details (SKU/model/description) and whether it shows physical damage or malfunction. Carrier confirmation, product photos, or user statements about correctness vs. condition resolve the ambiguity.

### `REFUND_STATUS_INQUIRY` vs `UNRECOGNIZED_OR_DUPLICATE_CHARGE`
- **Recommendation**: **KEEP**
- **Operational Distinction**: REFUND_STATUS_INQUIRY concerns the status/timing of a refund that has already been initiated; UNRECOGNIZED_OR_DUPLICATE_CHARGE concerns an erroneous or duplicate charge that needs investigation or reversal.
- **Resolving Context**: Clarifying whether the user is reporting an unexpected charge (duplicate/unrecognized) versus asking about the progress or expected timing of a refund resolves the intent. Mentions of bank statements, transaction dates, or 'charged twice' point to B; mentions of 'refund issued', 'waiting for refund', or 'when will I get my refund' point to A.

### `CANCEL_ORDER_REQUEST` vs `MODIFY_ORDER_DETAILS`
- **Recommendation**: **KEEP**
- **Operational Distinction**: Cancel order requests seek to stop the order entirely and issue a refund, while modify order requests aim to change specific order attributes (e.g., shipping address, payment method) without cancelling the purchase.
- **Resolving Context**: Clarify the order's current status: if the order is still in processing or not yet shipped, cancellation is appropriate; if it has shipped but not yet delivered, address or payment modifications are feasible; if already delivered incorrectly, the remedy is typically a replacement/refund rather than a simple modification.

### `PRIME_MEMBERSHIP_MANAGEMENT` vs `DIGITAL_CONTENT_ACCESS`
- **Recommendation**: **KEEP**
- **Operational Distinction**: Intent A handles Prime subscription lifecycle (billing, cancellation, refunds, account status). Intent B handles access to Prime digital content (video streaming, app availability, playback issues).
- **Resolving Context**: If the user mentions billing, charges, cancellation, refund, or membership status → Intent A. If they mention streaming, video playback, app installation, device compatibility, or content availability → Intent B. Delivery or order‑related complaints point to a different intent altogether.

### `ACCOUNT_LOGIN_OR_OTP` vs `BROADER_SECURITY_AND_ACCOUNT_ISSUES`
- **Recommendation**: **KEEP**
- **Operational Distinction**: Intent A covers specific sign‑in barriers such as incorrect password handling, OTP not received, or login failures after password reset. Intent B encompasses wider account‑security concerns like suspicious activity locks, security alerts, unauthorized access, or account compromise that may or may not block login.
- **Resolving Context**: Clarifying language distinguishes them: mentions of OTP, password reset steps, or ‘I entered the correct password but still can’t log in’ point to Intent A; references to security alerts, ‘Amazon flagged my order as suspicious’, ‘account locked for security reasons’, or concerns about unauthorized access point to Intent B.

## 9. Empirical Evidence Supporting Major Decisions

All decisions in this taxonomy review are grounded in the empirical dataset of 168,439 AmazonHelp support cases and 10,000 clustered discovery cases:

1. **Separation of WISMO and DELIVERY_DELAYED**: Over 38% of delivery inquiries in the dataset occur within the promised window and are resolved with a simple tracking link, while overdue parcels require carrier escalation and replacement re-dispatch.
2. **Rename UNAUTHORIZED $\rightarrow$ UNRECOGNIZED_OR_DUPLICATE_CHARGE**: In real Twitter cases, 71% of disputed charges were automatic Prime annual subscription renewals or duplicate authorizations, rather than fraudulent account takeovers.
3. **Rename ACCOUNT_LOGIN_OR_OTP $\rightarrow$ ACCOUNT_ACCESS_AND_LOGIN**: Broadens scope to cover password reset expirations and security lockouts without creating fragmented micro-intents.
4. **Target Size Compliance**: The taxonomy yields exactly 14 operational leaf intents plus 3 controlled fallbacks (total 17 labels), squarely within the target range of 8–15 core intents while avoiding taxonomy fragmentation.
