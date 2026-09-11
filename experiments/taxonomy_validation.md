# Experiment & Validation Report: Taxonomy Governance & Coherence

This document provides a systematic validation of the 14 candidate leaf intents, 3 controlled fallback categories, and 5 conversation progress states derived from the 10,000-case AmazonHelp intent discovery corpus.

---

## 1. Candidate Intent Evaluation Matrix

| Broad Area | Candidate Intent | Discovery Volume | Coherence | Data Sufficiency | Primary Confusion Vectors | Recommendation |
| :--- | :--- | :---: | :---: | :---: | :--- | :---: |
| **`DELIVERY_AND_FULFILLMENT`** | `WHERE_IS_MY_ORDER` | 1,420 | High | Abundant | `DELIVERY_DELAYED` | **KEEP** |
| | `DELIVERY_DELAYED` | 2,150 | High | Abundant | `WHERE_IS_MY_ORDER`, `MARKED_DELIVERED_NOT_RECEIVED` | **KEEP** |
| | `MARKED_DELIVERED_NOT_RECEIVED` | 640 | Very High | Strong | `DELIVERY_DELAYED` | **KEEP** |
| | `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | 510 | High | Moderate | `DELIVERY_DELAYED` | **KEEP** |
| **`RETURNS_AND_REPLACEMENTS`** | `DAMAGED_OR_DEFECTIVE_ITEM` | 890 | Very High | Strong | `WRONG_ITEM_RECEIVED` | **KEEP** |
| | `WRONG_ITEM_RECEIVED` | 320 | Very High | Moderate | `DAMAGED_OR_DEFECTIVE_ITEM` | **KEEP** |
| | `RETURN_PICKUP_ISSUE` | 410 | High | Moderate | `REFUND_STATUS_INQUIRY` | **KEEP** |
| **`REFUNDS_AND_BILLING`** | `REFUND_STATUS_INQUIRY` | 1,180 | High | Abundant | `UNAUTHORIZED_OR_DUPLICATE_CHARGE` | **KEEP** |
| | `UNAUTHORIZED_OR_DUPLICATE_CHARGE` | 260 | Very High | Moderate | `REFUND_STATUS_INQUIRY` | **RENAME** $\rightarrow$ `UNRECOGNIZED_OR_DUPLICATE_CHARGE` |
| **`ORDER_MANAGEMENT`** | `CANCEL_ORDER_REQUEST` | 680 | High | Strong | `MODIFY_ORDER_DETAILS`, `DELIVERY_DELAYED` | **KEEP** |
| | `MODIFY_ORDER_DETAILS` | 290 | High | Moderate | `CANCEL_ORDER_REQUEST` | **KEEP** |
| **`DIGITAL_SERVICES_AND_PRIME`** | `PRIME_MEMBERSHIP_MANAGEMENT` | 460 | High | Strong | `DIGITAL_CONTENT_ACCESS`, `REFUND_STATUS_INQUIRY` | **KEEP** |
| | `DIGITAL_CONTENT_ACCESS` | 380 | High | Moderate | `PRIME_MEMBERSHIP_MANAGEMENT` | **KEEP** |
| **`ACCOUNT_ACCESS_AND_SECURITY`** | `ACCOUNT_LOGIN_OR_OTP` | 460 | Very High | Strong | `UNAUTHORIZED_OR_DUPLICATE_CHARGE` | **RENAME** $\rightarrow$ `ACCOUNT_ACCESS_AND_LOGIN` |
| **`CONTROLLED_FALLBACKS`** | `AMBIGUOUS_INQUIRY` | ~400 | N/A | Abundant | All intents (under-specified) | **KEEP** |
| | `MULTI_INTENT` | ~600 | N/A | Abundant | Composite pairings | **KEEP** (as multi-label set) |
| | `OUT_OF_SCOPE` | ~250 | N/A | Moderate | Brand sentiment, general rants | **KEEP** |

---

## 2. Deep-Dive Intent Analysis

### 1. `WHERE_IS_MY_ORDER`
- **Volume & Sufficiency**: ~1,420 cases (14.2% of discovery corpus). Abundant data.
- **Common Phrases**: *"where is my order"*, *"tracking says out for delivery"*, *"can you check tracking"*, *"any update on shipment"*.
- **Coherence**: High. Clear user objective seeking spatial/temporal tracking information within expected timeframe.
- **Confusion Vector**: `DELIVERY_DELAYED`. When tracking is vague, customers may ask where an order is even if technically late.
- **Decision**: **KEEP**. Operational boundary: applies when inquiry asks for location/status within or near promised window.

### 2. `DELIVERY_DELAYED`
- **Volume & Sufficiency**: ~2,150 cases (21.5% of discovery corpus). Highest volume operational intent.
- **Common Phrases**: *"order is delayed"*, *"was supposed to arrive yesterday"*, *"running late"*, *"still waiting after 3 days"*.
- **Coherence**: High. Explicit expectation failure regarding promised arrival date.
- **Confusion Vector**: `MARKED_DELIVERED_NOT_RECEIVED`. Customers sometimes assume a late parcel was falsely marked delivered.
- **Decision**: **KEEP**. Crucial for SLA compensation policies and carrier escalation.

### 3. `MARKED_DELIVERED_NOT_RECEIVED`
- **Volume & Sufficiency**: ~640 cases (6.4%). Strong representation.
- **Common Phrases**: *"marked as delivered but not received"*, *"tracking says delivered to resident but i was home"*, *"missing parcel"*.
- **Coherence**: Very High. Sharp operational boundary requiring signature proof, safe-place investigation, or police/theft claims.
- **Confusion Vector**: `DELIVERY_DELAYED`.
- **Decision**: **KEEP**. Must not be merged into general delivery issues due to legal/theft investigation protocols.

### 4. `CARRIER_FEEDBACK_AND_INSTRUCTIONS`
- **Volume & Sufficiency**: ~510 cases (5.1%). Moderate representation.
- **Common Phrases**: *"driver threw package over fence"*, *"courier left in the rain"*, *"customs KYC upload"*, *"courier didn't call"*.
- **Coherence**: High. Centers on carrier conduct, gate access codes, and physical delivery conditions.
- **Decision**: **KEEP**. Actionable for logistics partner feedback and carrier scorecard routing.

### 5. `DAMAGED_OR_DEFECTIVE_ITEM`
- **Volume & Sufficiency**: ~890 cases (8.9%). Strong representation.
- **Common Phrases**: *"arrived broken"*, *"cracked screen"*, *"spilled liquid"*, *"defective out of the box"*, *"poor quality"*.
- **Coherence**: Very High. Concrete physical damage or functional failure.
- **Confusion Vector**: `WRONG_ITEM_RECEIVED`.
- **Decision**: **KEEP**. Triggers instant replacement or damage compensation flow.

### 6. `WRONG_ITEM_RECEIVED`
- **Volume & Sufficiency**: ~320 cases (3.2%). Moderate representation.
- **Common Phrases**: *"ordered shoes received shirt"*, *"sent me wrong product"*, *"wrong size delivered"*, *"completely different item"*.
- **Coherence**: Very High. SKU mismatch rather than product physical condition defect.
- **Decision**: **KEEP**. Distinct inventory discrepancy workflow (requires warehouse bin check).

### 7. `RETURN_PICKUP_ISSUE`
- **Volume & Sufficiency**: ~410 cases (4.1%). Moderate representation.
- **Common Phrases**: *"courier did not come for return pickup"*, *"return pickup delayed"*, *"need return label"*, *"drop off point"*.
- **Coherence**: High. Post-authorization reverse logistics failure.
- **Decision**: **KEEP**. Differentiates reverse-logistics courier failures from forward delivery failures.

### 8. `REFUND_STATUS_INQUIRY`
- **Volume & Sufficiency**: ~1,180 cases (11.8%). Abundant representation.
- **Common Phrases**: *"where is my refund"*, *"returned 5 days ago no refund"*, *"money not credited to bank"*, *"refund processed?"*.
- **Coherence**: High. Tracking financial return credit.
- **Decision**: **KEEP**. Crucial SLA monitoring (standard bank turnaround 3–5 business days).

### 9. `UNAUTHORIZED_OR_DUPLICATE_CHARGE`
- **Volume & Sufficiency**: ~260 cases (2.6%). Moderate representation.
- **Common Phrases**: *"charged twice for one order"*, *"unrecognized debit on card"*, *"money deducted without placing order"*.
- **Coherence**: Very High. Unplanned financial loss.
- **Decision**: **RENAME** to `UNRECOGNIZED_OR_DUPLICATE_CHARGE` to better encompass accidental double charges and mysterious subscription debits.

### 10. `CANCEL_ORDER_REQUEST`
- **Volume & Sufficiency**: ~680 cases (6.8%). Strong representation.
- **Common Phrases**: *"cancel my order"*, *"ordered by mistake"*, *"cancel this item before shipping"*, *"unable to cancel on app"*.
- **Coherence**: High. Pre-dispatch termination request.
- **Decision**: **KEEP**. High-urgency action: stopping warehouse dispatch saves return shipping cost.

### 11. `MODIFY_ORDER_DETAILS`
- **Volume & Sufficiency**: ~290 cases (2.9%). Moderate representation.
- **Common Phrases**: *"change delivery address"*, *"wrong address entered"*, *"change payment method"*, *"update phone number"*.
- **Coherence**: High. Pre-dispatch modification while retaining order validity.
- **Decision**: **KEEP**. Separate from cancellation because customer still desires product fulfillment.

### 12. `PRIME_MEMBERSHIP_MANAGEMENT`
- **Volume & Sufficiency**: ~460 cases (4.6%). Strong representation.
- **Common Phrases**: *"cancel my prime membership"*, *"charged £79 for prime renewal"*, *"did not authorize prime subscription"*.
- **Coherence**: High. Subscription billing and benefit entitlement.
- **Decision**: **KEEP**. Dedicated subscription retention/cancellation workflows.

### 13. `DIGITAL_CONTENT_ACCESS`
- **Volume & Sufficiency**: ~380 cases (3.8%). Moderate representation.
- **Common Phrases**: *"prime video streaming error"*, *"kindle ebook won't download"*, *"audible book missing"*, *"fire stick frozen"*.
- **Coherence**: High. Digital DRM, app functionality, and device streaming playback.
- **Decision**: **KEEP**. Routes to specialized digital/technical support rather than physical retail support.

### 14. `ACCOUNT_LOGIN_OR_OTP`
- **Volume & Sufficiency**: ~460 cases (4.6%). Strong representation.
- **Common Phrases**: *"cannot log in"*, *"otp not received"*, *"account locked"*, *"password reset failed"*, *"hacked account"*.
- **Coherence**: Very High. Security and authentication bottleneck.
- **Decision**: **RENAME** to `ACCOUNT_ACCESS_AND_LOGIN` to encompass broader credential and account recovery issues.

---

## 3. Multi-Intent Architecture Analysis

### Findings:
- Over 6% of customer inquiries contain multiple independently actionable requests.
- **Top Co-occurring Combinations**:
  1. `DELIVERY_DELAYED` + `CANCEL_ORDER_REQUEST` (*"Order is 4 days late, please cancel it immediately"*)
  2. `CANCEL_ORDER_REQUEST` + `REFUND_STATUS_INQUIRY` (*"I cancelled order #123, when will my refund be in my bank?"*)
  3. `DAMAGED_OR_DEFECTIVE_ITEM` + `RETURN_OR_REPLACEMENT` (*"Item arrived broken, can I get a replacement or return?"*)
  4. `UNRECOGNIZED_OR_DUPLICATE_CHARGE` + `CANCEL_ORDER_REQUEST` (*"You charged me twice, cancel the duplicate order"*)

### Design Verdict:
- **Never create composite classes** (e.g. `CANCEL_AND_REFUND` is banned).
- In Phase 3, the multi-label architecture will allow the classifier to output:
  $$\hat{Y} \subseteq \{I_1, I_2, \dots, I_{14}\}$$
  with a minimum threshold per intent, defaulting to `MULTI_INTENT` when $|\hat{Y}| \ge 2$.

---

## 4. Conversation State Architecture Analysis

Tracking conversation progress states is essential to prevent repetitive, circular support interactions.

| State Name | Estimated Frequency | Example Customer Cue | Operational Policy Impact |
| :--- | :---: | :--- | :--- |
| `INITIAL_INQUIRY` | 56.3% | Turn 0/1 problem statement. | Provide standard first-line diagnostic / tracking link. |
| `TRACKING_ALREADY_CHECKED` | ~12.5% | *"I already checked the tracker, it hasn't moved for 3 days"* | **NEVER** ask user to re-check tracking; escalate to carrier tracing. |
| `CARRIER_ALREADY_CONTACTED` | ~4.2% | *"The USPS driver told me they lost the parcel and to call Amazon"* | Bypass carrier redirect; initiate lost-parcel refund/replacement. |
| `DETAILS_ALREADY_PROVIDED` | ~8.7% | *"I already DM'd you my order number twice"* | Do not ask for order ID again; acknowledge receipt and verify DM queue. |
| `WAITING_WINDOW_EXCEEDED` | ~6.1% | *"Your rep told me to wait 48 hours; it has now been 5 days"* | Immediate supervisor escalation; issue courtesy concession if warranted. |
| `RESOLVED_CLOSURE` | ~12.2% | *"Thank you, that worked!"*, *"Got it sorted"* | Close conversation gracefully without reopening issues. |
