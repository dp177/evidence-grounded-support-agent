# TAXONOMY BOUNDARY REVIEW

**Review Mode:** `openrouter`  
**Model:** `nvidia/nemotron-3-super-120b-a12b:free`  
**Date:** `2026-09-11 20:45:00 UTC`  

This document reviews pairwise intent boundaries to ensure distinctions are operationally meaningful, prevent fragmentation, and establish clear annotation guidelines.

## Boundary Pair 1: `WHERE_IS_MY_ORDER` vs `DELIVERY_DELAYED`

- **Intent A**: `WHERE_IS_MY_ORDER`
- **Intent B**: `DELIVERY_DELAYED`
- **LLM Recommendation**: **KEEP** (Confidence: 0.90)
- **Operational Distinction**: WHERE_IS_MY_ORDER focuses on locating an order when tracking shows delivered but the item is not received (or status unknown), requiring investigation/possible claim. DELIVERY_DELAYED addresses orders that are late relative to the promised delivery date while still in transit, typically requiring apology, expedite, or shipping compensation.
- **Ambiguous Cases**: Edge cases where the user mentions a missed expected delivery date but provides no tracking status or says they have not received an update, making it unclear whether the order is lost (WHERE_IS_MY_ORDER) or merely delayed (DELIVERY_DELAYED).
- **Resolving Context**: Clarify the current tracking status and timestamps: if tracking shows 'delivered' or carrier confirms receipt but customer hasn't got it → WHERE_IS_MY_ORDER; if tracking shows 'in transit', 'out for delivery', or a past estimated delivery date with no delivery yet → DELIVERY_DELAYED; if no tracking info is available, ask for the tracking number or carrier details to determine the correct intent.
- **Operational Guidance**: Agents should first request the tracking number and check the carrier status. Use the status to route: delivered/not received → WHERE_IS_MY_ORDER (investigate loss, possible refund/replacement); in transit with missed estimate → DELIVERY_DELAYED (apologize, offer expedite/shipping credit). When status is unavailable, treat as ambiguous and gather more info before deciding.

---

## Boundary Pair 2: `DELIVERY_DELAYED` vs `MARKED_DELIVERED_NOT_RECEIVED`

- **Intent A**: `DELIVERY_DELAYED`
- **Intent B**: `MARKED_DELIVERED_NOT_RECEIVED`
- **LLM Recommendation**: **KEEP** (Confidence: 0.92)
- **Operational Distinction**: DELIVERY_DELAYED covers cases where the package is still in transit and the expected delivery date has passed or been updated; MARKED_DELIVERED_NOT_RECEIVED covers cases where the tracking/status shows the item as delivered but the customer confirms they did not receive it.
- **Ambiguous Cases**: Ambiguity arises when the customer only states they have not received the package without specifying whether tracking shows it as delivered or still in transit (e.g., 'I have not received my package which was to be delivered yesterday.' or vague loss notifications).
- **Resolving Context**: Clarify the current tracking status: if the carrier/marketplace shows 'Delivered' (with timestamp, location, or proof of delivery) → MARKED_DELIVERED_NOT_RECEIVED; if it shows 'In transit', 'Delayed', 'No estimated delivery date', or a revised future date → DELIVERY_DELAYED.
- **Operational Guidance**: Agents should first ask for the latest tracking status or carrier confirmation. Use that to route to the appropriate intent. For MARKED_DELIVERED_NOT_RECEIVED, initiate a carrier investigation and consider refund/replacement after verification. For DELIVERY_DELAYED, provide updated ETA, offer shipping refund or expedited replacement if applicable, and set expectations.

---

## Boundary Pair 3: `DELIVERY_DELAYED` vs `CARRIER_FEEDBACK_AND_INSTRUCTIONS`

- **Intent A**: `DELIVERY_DELAYED`
- **Intent B**: `CARRIER_FEEDBACK_AND_INSTRUCTIONS`
- **LLM Recommendation**: **KEEP** (Confidence: 0.95)
- **Operational Distinction**: DELIVERY_DELAYED concerns missed or late delivery timelines; CARRIER_FEEDBACK_AND_INSTRUCTIONS concerns driver conduct, service quality, or requests for carrier-specific instructions/feedback.
- **Ambiguous Cases**: Ambiguity arises when a delayed delivery is explicitly attributed to carrier behavior (e.g., driver not delivering, marking falsely delivered), blending timing complaints with service feedback.
- **Resolving Context**: Clarify whether the user's primary issue is the lateness of the package (check tracking timestamps, estimated vs actual delivery) versus dissatisfaction with how the carrier handled the parcel (driver actions, delivery instructions, feedback requests).
- **Operational Guidance**: Maintain separate intents to route delayed‑delivery cases to compensation/refund workflows and carrier‑feedback cases to carrier‑relations or quality‑assurance teams. When both aspects appear, prioritize the delay intent for resolution but log carrier feedback for follow‑up.

---

## Boundary Pair 4: `DAMAGED_OR_DEFECTIVE_ITEM` vs `WRONG_ITEM_RECEIVED`

- **Intent A**: `DAMAGED_OR_DEFECTIVE_ITEM`
- **Intent B**: `WRONG_ITEM_RECEIVED`
- **LLM Recommendation**: **KEEP** (Confidence: 0.85)
- **Operational Distinction**: DAMAGED_OR_DEFECTIVE_ITEM concerns items that match the order but are physically damaged, non‑functional, or defective. WRONG_ITEM_RECEIVED concerns items that do not match the order (different SKU, model, color, etc.), regardless of their condition.
- **Ambiguous Cases**: Edge cases arise when a wrong item is also damaged, or when a damaged item is described as 'wrong' by the user (e.g., 'wrong item sent to me' when the item is the correct one but broken). Reviews that mention both damage and wrongness, or vague dissatisfaction without clear condition details, create ambiguity.
- **Resolving Context**: Clarify whether the received item matches the ordered product details (SKU/model/description) and whether it shows physical damage or malfunction. Carrier confirmation, product photos, or user statements about correctness vs. condition resolve the ambiguity.
- **Operational Guidance**: Maintain separate intents to guide appropriate workflows: for wrong items prioritize shipping the correct item and returning the mistaken one; for damaged items prioritize replacement/refund or repair. Use clarifying questions (e.g., 'Is the item you received the one you ordered?' and 'Does it work/show any damage?') to disambiguate before routing.

---

## Boundary Pair 5: `REFUND_STATUS_INQUIRY` vs `UNRECOGNIZED_OR_DUPLICATE_CHARGE`

- **Intent A**: `REFUND_STATUS_INQUIRY`
- **Intent B**: `UNRECOGNIZED_OR_DUPLICATE_CHARGE`
- **LLM Recommendation**: **KEEP** (Confidence: 0.95)
- **Operational Distinction**: REFUND_STATUS_INQUIRY concerns the status/timing of a refund that has already been initiated; UNRECOGNIZED_OR_DUPLICATE_CHARGE concerns an erroneous or duplicate charge that needs investigation or reversal.
- **Ambiguous Cases**: Ambiguity could arise if a user mentions both a duplicate charge and a missing refund (e.g., 'I was charged twice and still haven't seen the refund for the duplicate'), blending charge error with refund status.
- **Resolving Context**: Clarifying whether the user is reporting an unexpected charge (duplicate/unrecognized) versus asking about the progress or expected timing of a refund resolves the intent. Mentions of bank statements, transaction dates, or 'charged twice' point to B; mentions of 'refund issued', 'waiting for refund', or 'when will I get my refund' point to A.
- **Operational Guidance**: Route to B when the primary complaint is an unrecognized or duplicate charge; route to A when the user is seeking updates on a refund that has already been processed or is expected. If both aspects are present, prioritize the charge issue (B) and then follow up on refund status after charge resolution.

---

## Boundary Pair 6: `CANCEL_ORDER_REQUEST` vs `MODIFY_ORDER_DETAILS`

- **Intent A**: `CANCEL_ORDER_REQUEST`
- **Intent B**: `MODIFY_ORDER_DETAILS`
- **LLM Recommendation**: **KEEP** (Confidence: 0.90)
- **Operational Distinction**: Cancel order requests seek to stop the order entirely and issue a refund, while modify order requests aim to change specific order attributes (e.g., shipping address, payment method) without cancelling the purchase.
- **Ambiguous Cases**: Edge cases involve situations where the user reports a problem like a wrong‑address delivery or missing payment‑edit option; these could be interpreted as either wanting to cancel the order due to the error or to correct the detail (address/payment) to fulfill the order.
- **Resolving Context**: Clarify the order's current status: if the order is still in processing or not yet shipped, cancellation is appropriate; if it has shipped but not yet delivered, address or payment modifications are feasible; if already delivered incorrectly, the remedy is typically a replacement/refund rather than a simple modification.
- **Operational Guidance**: Use order status (processing/shipped/delivered) and carrier confirmation to decide the correct workflow. For cancel, invoke cancellation/refund tool; for modify, invoke address/payment update tool. If the user insists on cancellation after a delivery error, treat as a separate 'REPLACE_OR_REFUND' flow.

---

## Boundary Pair 7: `PRIME_MEMBERSHIP_MANAGEMENT` vs `DIGITAL_CONTENT_ACCESS`

- **Intent A**: `PRIME_MEMBERSHIP_MANAGEMENT`
- **Intent B**: `DIGITAL_CONTENT_ACCESS`
- **LLM Recommendation**: **KEEP** (Confidence: 0.90)
- **Operational Distinction**: Intent A handles Prime subscription lifecycle (billing, cancellation, refunds, account status). Intent B handles access to Prime digital content (video streaming, app availability, playback issues).
- **Ambiguous Cases**: Edge cases involve general Prime service complaints (e.g., delivery delays, payment module errors, vague service issues) that do not clearly mention subscription management nor content access, making it hard to assign to either intent.
- **Resolving Context**: If the user mentions billing, charges, cancellation, refund, or membership status → Intent A. If they mention streaming, video playback, app installation, device compatibility, or content availability → Intent B. Delivery or order‑related complaints point to a different intent altogether.
- **Operational Guidance**: Maintain separate workflows: A uses subscription management tools and refund processing; B uses streaming troubleshooting, device compatibility checks, and service status verification. Add a catch‑all 'PRIME_GENERAL_ISSUE' intent for ambiguous service‑only complaints to reduce misclassification.

---

## Boundary Pair 8: `ACCOUNT_LOGIN_OR_OTP` vs `BROADER_SECURITY_AND_ACCOUNT_ISSUES`

- **Intent A**: `ACCOUNT_LOGIN_OR_OTP`
- **Intent B**: `BROADER_SECURITY_AND_ACCOUNT_ISSUES`
- **LLM Recommendation**: **KEEP** (Confidence: 0.78)
- **Operational Distinction**: Intent A covers specific sign‑in barriers such as incorrect password handling, OTP not received, or login failures after password reset. Intent B encompasses wider account‑security concerns like suspicious activity locks, security alerts, unauthorized access, or account compromise that may or may not block login.
- **Ambiguous Cases**: Edge cases arise when a login failure is caused by a security lock (e.g., account locked due to suspicious activity). In such scenarios the user’s primary complaint is ‘cannot log in’, which fits both intents.
- **Resolving Context**: Clarifying language distinguishes them: mentions of OTP, password reset steps, or ‘I entered the correct password but still can’t log in’ point to Intent A; references to security alerts, ‘Amazon flagged my order as suspicious’, ‘account locked for security reasons’, or concerns about unauthorized access point to Intent B.
- **Operational Guidance**: Ensure Intent B’s definition and training examples explicitly include security‑related lockouts, suspicious activity notifications, and compromised‑account scenarios to reduce overlap. Consider renaming Intent B to ACCOUNT_SECURITY_ISSUES for clarity.

---

