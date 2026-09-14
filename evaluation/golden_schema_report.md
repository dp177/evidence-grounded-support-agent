# Dataset Inspection & Schema Report: `golden_v1_assistant_adjudicated.csv`

**Target File:** `data/golden/golden_v1_assistant_adjudicated.csv`  
**Row Count:** `200`  
**Column Count:** `32`  

---

## 1. Executive Summary

- **Total Rows:** 200 rows (exactly 200 cases conforming to the locked golden v1 size).
- **Total Columns:** 32 columns covering conversation inputs, machine proposals, assistant recommendations, human adjudication fields, review metadata, and adjudication status.
- **Memory Usage:** ~236.91 KB.

## 2. Column Schema, Datatypes & Null Statistics

| # | Column Name | Datatype | Non-Null Count | Null Count | Unique Count |
|---|---|---|:---:|:---:|:---:|
| 1 | `gold_id` | `str` | 200 | 0 | 200 |
| 2 | `case_id` | `str` | 200 | 0 | 200 |
| 3 | `conversation_id` | `int64` | 200 | 0 | 200 |
| 4 | `customer_message` | `str` | 200 | 0 | 200 |
| 5 | `context` | `str` | 200 | 0 | 200 |
| 6 | `proposed_status` | `str` | 200 | 0 | 3 |
| 7 | `proposed_areas` | `str` | 175 | 25 | 14 |
| 8 | `proposed_intents` | `str` | 175 | 25 | 33 |
| 9 | `proposed_primary_intent` | `str` | 175 | 25 | 15 |
| 10 | `proposed_states` | `str` | 200 | 0 | 3 |
| 11 | `proposed_should_escalate` | `bool` | 200 | 0 | 2 |
| 12 | `human_status` | `str` | 200 | 0 | 3 |
| 13 | `human_areas` | `str` | 181 | 19 | 14 |
| 14 | `human_intents` | `str` | 181 | 19 | 25 |
| 15 | `human_primary_intent` | `str` | 181 | 19 | 15 |
| 16 | `human_states` | `str` | 200 | 0 | 3 |
| 17 | `human_should_escalate` | `bool` | 200 | 0 | 2 |
| 18 | `human_escalation_reason` | `str` | 8 | 192 | 3 |
| 19 | `human_notes` | `str` | 200 | 0 | 91 |
| 20 | `review_flags` | `str` | 22 | 178 | 6 |
| 21 | `assistant_outcome` | `str` | 21 | 179 | 5 |
| 22 | `review_priority` | `str` | 200 | 0 | 3 |
| 23 | `assistant_status_recommendation` | `str` | 200 | 0 | 3 |
| 24 | `assistant_areas_recommendation` | `str` | 181 | 19 | 14 |
| 25 | `assistant_intents_recommendation` | `str` | 181 | 19 | 25 |
| 26 | `assistant_primary_intent_recommendation` | `str` | 181 | 19 | 15 |
| 27 | `assistant_states_recommendation` | `str` | 200 | 0 | 3 |
| 28 | `assistant_should_escalate_recommendation` | `bool` | 200 | 0 | 2 |
| 29 | `assistant_escalation_reason_recommendation` | `str` | 8 | 192 | 3 |
| 30 | `assistant_notes_recommendation` | `str` | 200 | 0 | 91 |
| 31 | `human_action` | `str` | 200 | 0 | 3 |
| 32 | `adjudication_status` | `str` | 200 | 0 | 2 |

---

## 3. Unique Values for Categorical Columns

### `proposed_status` (3 unique values, 200/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `NORMAL` | 175 | 87.5% |
| `AMBIGUOUS` | 15 | 7.5% |
| `OUT_OF_SCOPE` | 10 | 5.0% |


### `proposed_areas` (14 unique values, 175/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `DELIVERY_AND_FULFILLMENT` | 50 | 25.0% |
| `RETURNS_AND_REPLACEMENTS` | 29 | 14.5% |
| `ACCOUNT_ACCESS_AND_SECURITY` | 26 | 13.0% |
| `None` (NaN) | 25 | 12.5% |
| `DIGITAL_SERVICES_AND_PRIME` | 21 | 10.5% |
| `ORDER_MANAGEMENT` | 19 | 9.5% |
| `REFUNDS_AND_BILLING` | 14 | 7.0% |
| `ORDER_MANAGEMENT|REFUNDS_AND_BILLING` | 4 | 2.0% |
| `DIGITAL_SERVICES_AND_PRIME|REFUNDS_AND_BILLING` | 3 | 1.5% |
| `ORDER_MANAGEMENT|DELIVERY_AND_FULFILLMENT` | 3 | 1.5% |
| `REFUNDS_AND_BILLING|RETURNS_AND_REPLACEMENTS` | 3 | 1.5% |
| `REFUNDS_AND_BILLING|ORDER_MANAGEMENT|DELIVERY_AND_FULFILLMENT` | 1 | 0.5% |
| `DIGITAL_SERVICES_AND_PRIME|ACCOUNT_ACCESS_AND_SECURITY` | 1 | 0.5% |
| `DIGITAL_SERVICES_AND_PRIME|DELIVERY_AND_FULFILLMENT` | 1 | 0.5% |


### `proposed_intents` (33 unique values, 175/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `ACCOUNT_LOGIN_ISSUES` | 26 | 13.0% |
| `None` (NaN) | 25 | 12.5% |
| `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | 16 | 8.0% |
| `WHERE_IS_MY_ORDER` | 14 | 7.0% |
| `RETURN_PICKUP_ISSUE` | 12 | 6.0% |
| `MODIFY_ORDER_DETAILS` | 12 | 6.0% |
| `DIGITAL_CONTENT_ACCESS` | 12 | 6.0% |
| `MARKED_DELIVERED_NOT_RECEIVED` | 11 | 5.5% |
| `DELIVERY_DELAYED` | 9 | 4.5% |
| `WRONG_ITEM_RECEIVED` | 8 | 4.0% |
| `CANCEL_ORDER_REQUEST` | 7 | 3.5% |
| `DAMAGED_OR_DEFECTIVE_ITEM` | 7 | 3.5% |
| `PRIME_MEMBERSHIP_MANAGEMENT` | 7 | 3.5% |
| `REFUND_STATUS_INQUIRY` | 7 | 3.5% |
| `UNRECOGNIZED_OR_DUPLICATE_CHARGE` | 7 | 3.5% |
| `RETURN_PICKUP_ISSUE|REFUND_STATUS_INQUIRY` | 2 | 1.0% |
| `DIGITAL_CONTENT_ACCESS|PRIME_MEMBERSHIP_MANAGEMENT` | 2 | 1.0% |
| `DELIVERY_DELAYED|CANCEL_ORDER_REQUEST|REFUND_STATUS_INQUIRY` | 1 | 0.5% |
| `UNRECOGNIZED_OR_DUPLICATE_CHARGE|CANCEL_ORDER_REQUEST` | 1 | 0.5% |
| `PRIME_MEMBERSHIP_MANAGEMENT|REFUND_STATUS_INQUIRY` | 1 | 0.5% |
| `PRIME_MEMBERSHIP_MANAGEMENT|UNRECOGNIZED_OR_DUPLICATE_CHARGE` | 1 | 0.5% |
| `WRONG_ITEM_RECEIVED|RETURN_PICKUP_ISSUE` | 1 | 0.5% |
| `DAMAGED_OR_DEFECTIVE_ITEM|RETURN_PICKUP_ISSUE` | 1 | 0.5% |
| `PRIME_MEMBERSHIP_MANAGEMENT|ACCOUNT_LOGIN_ISSUES` | 1 | 0.5% |
| `WHERE_IS_MY_ORDER|CANCEL_ORDER_REQUEST` | 1 | 0.5% |
| `CANCEL_ORDER_REQUEST|REFUND_STATUS_INQUIRY` | 1 | 0.5% |
| `DELIVERY_DELAYED|PRIME_MEMBERSHIP_MANAGEMENT` | 1 | 0.5% |
| `CANCEL_ORDER_REQUEST|UNRECOGNIZED_OR_DUPLICATE_CHARGE` | 1 | 0.5% |
| `DELIVERY_DELAYED|MODIFY_ORDER_DETAILS` | 1 | 0.5% |
| `WHERE_IS_MY_ORDER|MODIFY_ORDER_DETAILS` | 1 | 0.5% |
| `DAMAGED_OR_DEFECTIVE_ITEM|REFUND_STATUS_INQUIRY` | 1 | 0.5% |
| `REFUND_STATUS_INQUIRY|CANCEL_ORDER_REQUEST` | 1 | 0.5% |
| `DIGITAL_CONTENT_ACCESS|REFUND_STATUS_INQUIRY` | 1 | 0.5% |


### `proposed_primary_intent` (15 unique values, 175/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `ACCOUNT_LOGIN_ISSUES` | 27 | 13.5% |
| `None` (NaN) | 25 | 12.5% |
| `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | 16 | 8.0% |
| `WHERE_IS_MY_ORDER` | 15 | 7.5% |
| `DIGITAL_CONTENT_ACCESS` | 15 | 7.5% |
| `RETURN_PICKUP_ISSUE` | 14 | 7.0% |
| `DELIVERY_DELAYED` | 12 | 6.0% |
| `MODIFY_ORDER_DETAILS` | 12 | 6.0% |
| `MARKED_DELIVERED_NOT_RECEIVED` | 11 | 5.5% |
| `CANCEL_ORDER_REQUEST` | 10 | 5.0% |
| `PRIME_MEMBERSHIP_MANAGEMENT` | 9 | 4.5% |
| `WRONG_ITEM_RECEIVED` | 9 | 4.5% |
| `DAMAGED_OR_DEFECTIVE_ITEM` | 9 | 4.5% |
| `UNRECOGNIZED_OR_DUPLICATE_CHARGE` | 8 | 4.0% |
| `REFUND_STATUS_INQUIRY` | 8 | 4.0% |


### `proposed_states` (3 unique values, 200/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `INITIAL_INQUIRY` | 197 | 98.5% |
| `WAITING_WINDOW_EXCEEDED` | 2 | 1.0% |
| `TRACKING_ALREADY_CHECKED` | 1 | 0.5% |


### `proposed_should_escalate` (2 unique values, 200/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `False` | 190 | 95.0% |
| `True` | 10 | 5.0% |


### `human_status` (3 unique values, 200/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `NORMAL` | 181 | 90.5% |
| `AMBIGUOUS` | 11 | 5.5% |
| `OUT_OF_SCOPE` | 8 | 4.0% |


### `human_areas` (14 unique values, 181/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `DELIVERY_AND_FULFILLMENT` | 68 | 34.0% |
| `ACCOUNT_ACCESS_AND_SECURITY` | 25 | 12.5% |
| `RETURNS_AND_REPLACEMENTS` | 21 | 10.5% |
| `None` (NaN) | 19 | 9.5% |
| `REFUNDS_AND_BILLING` | 18 | 9.0% |
| `DIGITAL_SERVICES_AND_PRIME` | 18 | 9.0% |
| `ORDER_MANAGEMENT` | 18 | 9.0% |
| `DIGITAL_SERVICES_AND_PRIME|REFUNDS_AND_BILLING` | 3 | 1.5% |
| `DELIVERY_AND_FULFILLMENT|ORDER_MANAGEMENT|REFUNDS_AND_BILLING` | 2 | 1.0% |
| `DIGITAL_SERVICES_AND_PRIME|ACCOUNT_ACCESS_AND_SECURITY` | 2 | 1.0% |
| `ORDER_MANAGEMENT|REFUNDS_AND_BILLING` | 2 | 1.0% |
| `DELIVERY_AND_FULFILLMENT|REFUNDS_AND_BILLING` | 2 | 1.0% |
| `DIGITAL_SERVICES_AND_PRIME|DELIVERY_AND_FULFILLMENT` | 1 | 0.5% |
| `RETURNS_AND_REPLACEMENTS|REFUNDS_AND_BILLING` | 1 | 0.5% |


### `human_intents` (25 unique values, 181/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `ACCOUNT_LOGIN_ISSUES` | 25 | 12.5% |
| `DELIVERY_DELAYED` | 25 | 12.5% |
| `None` (NaN) | 19 | 9.5% |
| `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | 16 | 8.0% |
| `WHERE_IS_MY_ORDER` | 15 | 7.5% |
| `MARKED_DELIVERED_NOT_RECEIVED` | 12 | 6.0% |
| `DIGITAL_CONTENT_ACCESS` | 12 | 6.0% |
| `MODIFY_ORDER_DETAILS` | 11 | 5.5% |
| `REFUND_STATUS_INQUIRY` | 10 | 5.0% |
| `UNRECOGNIZED_OR_DUPLICATE_CHARGE` | 8 | 4.0% |
| `CANCEL_ORDER_REQUEST` | 7 | 3.5% |
| `WRONG_ITEM_RECEIVED` | 7 | 3.5% |
| `RETURN_PICKUP_ISSUE` | 6 | 3.0% |
| `PRIME_MEMBERSHIP_MANAGEMENT` | 5 | 2.5% |
| `DAMAGED_OR_DEFECTIVE_ITEM` | 5 | 2.5% |
| `DELIVERY_DELAYED|CANCEL_ORDER_REQUEST|REFUND_STATUS_INQUIRY` | 2 | 1.0% |
| `PRIME_MEMBERSHIP_MANAGEMENT|REFUND_STATUS_INQUIRY` | 2 | 1.0% |
| `PRIME_MEMBERSHIP_MANAGEMENT|UNRECOGNIZED_OR_DUPLICATE_CHARGE` | 2 | 1.0% |
| `DAMAGED_OR_DEFECTIVE_ITEM|RETURN_PICKUP_ISSUE` | 2 | 1.0% |
| `PRIME_MEMBERSHIP_MANAGEMENT|ACCOUNT_LOGIN_ISSUES` | 2 | 1.0% |
| `CANCEL_ORDER_REQUEST|REFUND_STATUS_INQUIRY` | 2 | 1.0% |
| `DELIVERY_DELAYED|REFUND_STATUS_INQUIRY` | 2 | 1.0% |
| `WRONG_ITEM_RECEIVED|RETURN_PICKUP_ISSUE` | 1 | 0.5% |
| `DELIVERY_DELAYED|PRIME_MEMBERSHIP_MANAGEMENT` | 1 | 0.5% |
| `WRONG_ITEM_RECEIVED|REFUND_STATUS_INQUIRY` | 1 | 0.5% |


### `human_primary_intent` (15 unique values, 181/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `DELIVERY_DELAYED` | 29 | 14.5% |
| `ACCOUNT_LOGIN_ISSUES` | 26 | 13.0% |
| `None` (NaN) | 19 | 9.5% |
| `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | 16 | 8.0% |
| `WHERE_IS_MY_ORDER` | 15 | 7.5% |
| `REFUND_STATUS_INQUIRY` | 12 | 6.0% |
| `MARKED_DELIVERED_NOT_RECEIVED` | 12 | 6.0% |
| `DIGITAL_CONTENT_ACCESS` | 12 | 6.0% |
| `MODIFY_ORDER_DETAILS` | 11 | 5.5% |
| `PRIME_MEMBERSHIP_MANAGEMENT` | 10 | 5.0% |
| `WRONG_ITEM_RECEIVED` | 9 | 4.5% |
| `UNRECOGNIZED_OR_DUPLICATE_CHARGE` | 8 | 4.0% |
| `RETURN_PICKUP_ISSUE` | 8 | 4.0% |
| `CANCEL_ORDER_REQUEST` | 8 | 4.0% |
| `DAMAGED_OR_DEFECTIVE_ITEM` | 5 | 2.5% |


### `human_states` (3 unique values, 200/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `INITIAL_INQUIRY` | 184 | 92.0% |
| `WAITING_WINDOW_EXCEEDED` | 14 | 7.0% |
| `TRACKING_ALREADY_CHECKED` | 2 | 1.0% |


### `human_should_escalate` (2 unique values, 200/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `False` | 185 | 92.5% |
| `True` | 15 | 7.5% |


### `human_escalation_reason` (3 unique values, 8/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `None` (NaN) | 192 | 96.0% |
| `ACCOUNT_SECURITY_COMPROMISE` | 6 | 3.0% |
| `REPEATED_FAILED_SUPPORT_ATTEMPTS` | 2 | 1.0% |


### `review_flags` (6 unique values, 22/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `None` (NaN) | 178 | 89.0% |
| `CONTEXT_MAY_DISAMBIGUATE` | 9 | 4.5% |
| `ACCOUNT_COMPROMISE_REVIEW` | 5 | 2.5% |
| `TAXONOMY_GAP_REVIEW` | 5 | 2.5% |
| `OUT_OF_SCOPE_DECISION_REVIEW` | 2 | 1.0% |
| `OUT_OF_SCOPE_DECISION_REVIEW|TAXONOMY_GAP_REVIEW` | 1 | 0.5% |


### `assistant_outcome` (5 unique values, 21/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `None` (NaN) | 179 | 89.5% |
| `UNRESOLVED` | 11 | 5.5% |
| `OUT_OF_TAXONOMY` | 6 | 3.0% |
| `RESOLVED_CLOSURE` | 3 | 1.5% |
| `NO_ACTIONABLE_SUPPORT_REQUEST` | 1 | 0.5% |


### `review_priority` (3 unique values, 200/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `NORMAL` | 176 | 88.0% |
| `TAXONOMY_REVIEW` | 14 | 7.0% |
| `HUMAN_REVIEW` | 10 | 5.0% |


### `assistant_status_recommendation` (3 unique values, 200/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `NORMAL` | 181 | 90.5% |
| `AMBIGUOUS` | 11 | 5.5% |
| `OUT_OF_SCOPE` | 8 | 4.0% |


### `assistant_areas_recommendation` (14 unique values, 181/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `DELIVERY_AND_FULFILLMENT` | 68 | 34.0% |
| `ACCOUNT_ACCESS_AND_SECURITY` | 25 | 12.5% |
| `RETURNS_AND_REPLACEMENTS` | 21 | 10.5% |
| `None` (NaN) | 19 | 9.5% |
| `REFUNDS_AND_BILLING` | 18 | 9.0% |
| `DIGITAL_SERVICES_AND_PRIME` | 18 | 9.0% |
| `ORDER_MANAGEMENT` | 18 | 9.0% |
| `DIGITAL_SERVICES_AND_PRIME|REFUNDS_AND_BILLING` | 3 | 1.5% |
| `DELIVERY_AND_FULFILLMENT|ORDER_MANAGEMENT|REFUNDS_AND_BILLING` | 2 | 1.0% |
| `DIGITAL_SERVICES_AND_PRIME|ACCOUNT_ACCESS_AND_SECURITY` | 2 | 1.0% |
| `ORDER_MANAGEMENT|REFUNDS_AND_BILLING` | 2 | 1.0% |
| `DELIVERY_AND_FULFILLMENT|REFUNDS_AND_BILLING` | 2 | 1.0% |
| `DIGITAL_SERVICES_AND_PRIME|DELIVERY_AND_FULFILLMENT` | 1 | 0.5% |
| `RETURNS_AND_REPLACEMENTS|REFUNDS_AND_BILLING` | 1 | 0.5% |


### `assistant_intents_recommendation` (25 unique values, 181/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `ACCOUNT_LOGIN_ISSUES` | 25 | 12.5% |
| `DELIVERY_DELAYED` | 25 | 12.5% |
| `None` (NaN) | 19 | 9.5% |
| `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | 16 | 8.0% |
| `WHERE_IS_MY_ORDER` | 15 | 7.5% |
| `MARKED_DELIVERED_NOT_RECEIVED` | 12 | 6.0% |
| `DIGITAL_CONTENT_ACCESS` | 12 | 6.0% |
| `MODIFY_ORDER_DETAILS` | 11 | 5.5% |
| `REFUND_STATUS_INQUIRY` | 10 | 5.0% |
| `UNRECOGNIZED_OR_DUPLICATE_CHARGE` | 8 | 4.0% |
| `CANCEL_ORDER_REQUEST` | 7 | 3.5% |
| `WRONG_ITEM_RECEIVED` | 7 | 3.5% |
| `RETURN_PICKUP_ISSUE` | 6 | 3.0% |
| `PRIME_MEMBERSHIP_MANAGEMENT` | 5 | 2.5% |
| `DAMAGED_OR_DEFECTIVE_ITEM` | 5 | 2.5% |
| `DELIVERY_DELAYED|CANCEL_ORDER_REQUEST|REFUND_STATUS_INQUIRY` | 2 | 1.0% |
| `PRIME_MEMBERSHIP_MANAGEMENT|REFUND_STATUS_INQUIRY` | 2 | 1.0% |
| `PRIME_MEMBERSHIP_MANAGEMENT|UNRECOGNIZED_OR_DUPLICATE_CHARGE` | 2 | 1.0% |
| `DAMAGED_OR_DEFECTIVE_ITEM|RETURN_PICKUP_ISSUE` | 2 | 1.0% |
| `PRIME_MEMBERSHIP_MANAGEMENT|ACCOUNT_LOGIN_ISSUES` | 2 | 1.0% |
| `CANCEL_ORDER_REQUEST|REFUND_STATUS_INQUIRY` | 2 | 1.0% |
| `DELIVERY_DELAYED|REFUND_STATUS_INQUIRY` | 2 | 1.0% |
| `WRONG_ITEM_RECEIVED|RETURN_PICKUP_ISSUE` | 1 | 0.5% |
| `DELIVERY_DELAYED|PRIME_MEMBERSHIP_MANAGEMENT` | 1 | 0.5% |
| `WRONG_ITEM_RECEIVED|REFUND_STATUS_INQUIRY` | 1 | 0.5% |


### `assistant_primary_intent_recommendation` (15 unique values, 181/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `DELIVERY_DELAYED` | 29 | 14.5% |
| `ACCOUNT_LOGIN_ISSUES` | 26 | 13.0% |
| `None` (NaN) | 19 | 9.5% |
| `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | 16 | 8.0% |
| `WHERE_IS_MY_ORDER` | 15 | 7.5% |
| `REFUND_STATUS_INQUIRY` | 12 | 6.0% |
| `MARKED_DELIVERED_NOT_RECEIVED` | 12 | 6.0% |
| `DIGITAL_CONTENT_ACCESS` | 12 | 6.0% |
| `MODIFY_ORDER_DETAILS` | 11 | 5.5% |
| `PRIME_MEMBERSHIP_MANAGEMENT` | 10 | 5.0% |
| `WRONG_ITEM_RECEIVED` | 9 | 4.5% |
| `UNRECOGNIZED_OR_DUPLICATE_CHARGE` | 8 | 4.0% |
| `RETURN_PICKUP_ISSUE` | 8 | 4.0% |
| `CANCEL_ORDER_REQUEST` | 8 | 4.0% |
| `DAMAGED_OR_DEFECTIVE_ITEM` | 5 | 2.5% |


### `assistant_states_recommendation` (3 unique values, 200/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `INITIAL_INQUIRY` | 184 | 92.0% |
| `WAITING_WINDOW_EXCEEDED` | 14 | 7.0% |
| `TRACKING_ALREADY_CHECKED` | 2 | 1.0% |


### `assistant_should_escalate_recommendation` (2 unique values, 200/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `False` | 185 | 92.5% |
| `True` | 15 | 7.5% |


### `assistant_escalation_reason_recommendation` (3 unique values, 8/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `None` (NaN) | 192 | 96.0% |
| `ACCOUNT_SECURITY_COMPROMISE` | 6 | 3.0% |
| `REPEATED_FAILED_SUPPORT_ATTEMPTS` | 2 | 1.0% |


### `human_action` (3 unique values, 200/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `Verify recommendation; accept/correct.` | 176 | 88.0% |
| `Decide taxonomy-gap handling before final gold lock.` | 14 | 7.0% |
| `Inspect context carefully before accepting.` | 10 | 5.0% |


### `adjudication_status` (2 unique values, 200/200 non-null)

| Value | Frequency | Percentage |
|---|:---:|:---:|
| `ASSISTANT_RECOMMENDATION_PENDING_HUMAN_SIGNOFF` | 176 | 88.0% |
| `PRIORITY_CASE_ASSISTANT_ADJUDICATED_NEEDS_HUMAN_CONFIRMATION` | 24 | 12.0% |


---

## 4. Column Role Classification

Based on the dataset semantics, documentation, and data lineage, the columns are categorized as follows:

### A. Immutable Ground Truth / Conversation Input
These columns represent the fixed, unmodifiable benchmark inputs extracted directly from historical customer interactions:
- `gold_id`: Immutable benchmark identifier (e.g., `gold_0001` through `gold_0200`).
- `case_id`: Original AmazonHelp case identifier (e.g., `amazon_case_0055972`).
- `conversation_id`: Original customer conversation thread ID (e.g., `1391472`).
- `customer_message`: Verbatim customer utterance to be evaluated.
- `context`: Verbatim multi-turn conversation context including preceding and succeeding turns.

### B. Human Adjudication / Review Fields
These fields are designed to hold the definitive ground-truth evaluation labels signed off by human annotators:
- `human_status`: Ground-truth domain gate status (`NORMAL`, `AMBIGUOUS`, `OUT_OF_SCOPE`).
- `human_areas`: Ground-truth area taxonomy classifications (pipe-delimited for multi-area).
- `human_intents`: Ground-truth intent taxonomy classifications (pipe-delimited for multi-intent).
- `human_primary_intent`: Ground-truth primary actionable intent.
- `human_states`: Ground-truth conversation progression state (`INITIAL_INQUIRY`, `WAITING_WINDOW_EXCEEDED`, `TRACKING_ALREADY_CHECKED`).
- `human_should_escalate`: Ground-truth boolean flag indicating if case requires human escalation.
- `human_escalation_reason`: Ground-truth reason code when escalation is triggered (`ACCOUNT_SECURITY_COMPROMISE`, `REPEATED_FAILED_SUPPORT_ATTEMPTS`).
- `human_notes`: Human annotation justification, edge case explanations, or acceptance notes.
- `human_action`: Specific action required from the human annotator during review.

> [!NOTE]
> In this specific file (`golden_v1_assistant_adjudicated.csv`), the `human_*` columns are pre-populated with the assistant's proposed adjudications pending final human sign-off approval (as indicated by `adjudication_status`). Once signed off via `golden_v1_human_signoff.csv`, these represent official human ground truth.

### C. Model / Assistant Recommendations
These columns contain machine-generated or LLM assistant-reviewed suggestions and MUST NOT be conflated with independent human ground truth:
- **Initial Machine Proposals (`proposed_*`):**
  - `proposed_status`
  - `proposed_areas`
  - `proposed_intents`
  - `proposed_primary_intent`
  - `proposed_states`
  - `proposed_should_escalate`
- **Assistant Adjudication Recommendations (`assistant_*_recommendation`):**
  - `assistant_status_recommendation`
  - `assistant_areas_recommendation`
  - `assistant_intents_recommendation`
  - `assistant_primary_intent_recommendation`
  - `assistant_states_recommendation`
  - `assistant_should_escalate_recommendation`
  - `assistant_escalation_reason_recommendation`
  - `assistant_notes_recommendation`
- **Assistant Outcome Categorization:**
  - `assistant_outcome` (`UNRESOLVED`, `OUT_OF_TAXONOMY`, `RESOLVED_CLOSURE`, `NO_ACTIONABLE_SUPPORT_REQUEST`)

### D. Free-Text Input & Text Fields
- `customer_message`: Customer query text.
- `context`: Dialogue history text.
- `human_notes`: Annotation notes text.
- `assistant_notes_recommendation`: Generated assistant justification text.
- `human_action`: Free-text instruction to human reviewers.

### E. Workflow & Review Metadata
- `gold_id`: Benchmark identifier.
- `case_id`: Case source identifier.
- `conversation_id`: Thread identifier.
- `review_flags`: Flags marking ambiguous, out-of-scope, taxonomy gaps, or account compromise issues (`CONTEXT_MAY_DISAMBIGUATE`, `ACCOUNT_COMPROMISE_REVIEW`, `TAXONOMY_GAP_REVIEW`, `OUT_OF_SCOPE_DECISION_REVIEW`).
- `review_priority`: Triage tier for human review (`NORMAL`, `TAXONOMY_REVIEW`, `HUMAN_REVIEW`).
- `adjudication_status`: Overall sign-off workflow status (`ASSISTANT_RECOMMENDATION_PENDING_HUMAN_SIGNOFF`, `PRIORITY_CASE_ASSISTANT_ADJUDICATED_NEEDS_HUMAN_CONFIRMATION`).

---

## 5. Columns That Should NOT Be Used as Ground Truth

> [!WARNING]
> The following columns **must NOT be used as ground-truth targets** when evaluating production models, because they are machine-generated proposals, assistant recommendations, or workflow operational metadata:

| Column Name | Category | Reason to Exclude from Ground Truth |
|---|---|---|
| `proposed_status` | Assistant / Machine / Workflow | Initial heuristic/machine classification proposal; contains errors that human/assistant review corrected. |
| `proposed_areas` | Assistant / Machine / Workflow | Initial machine proposal; unverified. |
| `proposed_intents` | Assistant / Machine / Workflow | Initial machine proposal; unverified. |
| `proposed_primary_intent` | Assistant / Machine / Workflow | Initial machine proposal; unverified. |
| `proposed_states` | Assistant / Machine / Workflow | Initial machine proposal; unverified. |
| `proposed_should_escalate` | Assistant / Machine / Workflow | Initial machine proposal; unverified. |
| `assistant_status_recommendation` | Assistant / Machine / Workflow | Assistant LLM suggestion; must not evaluate models against another model's suggestion without official human sign-off lock. |
| `assistant_areas_recommendation` | Assistant / Machine / Workflow | Assistant LLM suggestion. |
| `assistant_intents_recommendation` | Assistant / Machine / Workflow | Assistant LLM suggestion. |
| `assistant_primary_intent_recommendation` | Assistant / Machine / Workflow | Assistant LLM suggestion. |
| `assistant_states_recommendation` | Assistant / Machine / Workflow | Assistant LLM suggestion. |
| `assistant_should_escalate_recommendation` | Assistant / Machine / Workflow | Assistant LLM suggestion. |
| `assistant_escalation_reason_recommendation` | Assistant / Machine / Workflow | Assistant LLM suggestion. |
| `assistant_notes_recommendation` | Assistant / Machine / Workflow | Free-form LLM explanation accompanying assistant recommendation. |
| `assistant_outcome` | Assistant / Machine / Workflow | Intermediate assistant audit classification code, not a ground-truth label. |
| `review_flags` | Assistant / Machine / Workflow | Internal workflow triage flags indicating boundary difficulty; not an evaluation target. |
| `review_priority` | Assistant / Machine / Workflow | Triage tier used to sequence human annotator review queue. |
| `human_action` | Assistant / Machine / Workflow | Instructional string guiding human reviewers on what action to take. |
| `adjudication_status` | Assistant / Machine / Workflow | Workflow status of the sign-off pipeline. |


---

## 6. Representative Rows (5 Cases Across Key Profiles)

### Representative Case: Standard Single-Intent (NORMAL, Non-Escalated) (`gold_0012` / `amazon_case_0028664`)

| Field | Value |
|---|---|
| `gold_id` | gold_0012 |
| `case_id` | amazon_case_0028664 |
| `conversation_id` | `42519` |
| `customer_message` | was expecting 2 packages by 16/10/17 - still not received. Ordered 10/10/17. Can you help? |
| `context` | CUSTOMER: was expecting 2 packages by 16/10/17 - still not received. Ordered 10/10/17. Can you help? |
| `proposed_status` | AMBIGUOUS |
| `proposed_areas` | *null (NaN)* |
| `proposed_intents` | *null (NaN)* |
| `proposed_primary_intent` | *null (NaN)* |
| `proposed_states` | INITIAL_INQUIRY |
| `proposed_should_escalate` | `False` |
| `human_status` | NORMAL |
| `human_areas` | DELIVERY_AND_FULFILLMENT |
| `human_intents` | DELIVERY_DELAYED |
| `human_primary_intent` | DELIVERY_DELAYED |
| `human_states` | WAITING_WINDOW_EXCEEDED |
| `human_should_escalate` | `False` |
| `human_escalation_reason` | *null (NaN)* |
| `human_notes` | Expected delivery date had passed. |
| `review_flags` | *null (NaN)* |
| `assistant_outcome` | *null (NaN)* |
| `review_priority` | NORMAL |
| `assistant_status_recommendation` | NORMAL |
| `assistant_areas_recommendation` | DELIVERY_AND_FULFILLMENT |
| `assistant_intents_recommendation` | DELIVERY_DELAYED |
| `assistant_primary_intent_recommendation` | DELIVERY_DELAYED |
| `assistant_states_recommendation` | WAITING_WINDOW_EXCEEDED |
| `assistant_should_escalate_recommendation` | `False` |
| `assistant_escalation_reason_recommendation` | *null (NaN)* |
| `assistant_notes_recommendation` | Expected delivery date had passed. |
| `human_action` | Verify recommendation; accept/correct. |
| `adjudication_status` | ASSISTANT_RECOMMENDATION_PENDING_HUMAN_SIGNOFF |


### Representative Case: Multi-Intent Order & Refund (NORMAL, Non-Escalated) (`gold_0036` / `amazon_case_0015921`)

| Field | Value |
|---|---|
| `gold_id` | gold_0036 |
| `case_id` | amazon_case_0015921 |
| `conversation_id` | `22571` |
| `customer_message` | Ordered on 7 October 2017 Order# 403-7284574-6433108 not yet delivered. No way to cancel and get refund. |
| `context` | CUSTOMER: Ordered on 7 October 2017 Order# 403-7284574-6433108 not yet delivered. No way to cancel and get refund.<br/>BRAND: Sorry for the delay. I’d like to help you; please fill this form: <URL> and I’ll contact you soon. 1/2 |
| `proposed_status` | NORMAL |
| `proposed_areas` | REFUNDS_AND_BILLING\|ORDER_MANAGEMENT\|DELIVERY_AND_FULFILLMENT |
| `proposed_intents` | DELIVERY_DELAYED\|CANCEL_ORDER_REQUEST\|REFUND_STATUS_INQUIRY |
| `proposed_primary_intent` | DELIVERY_DELAYED |
| `proposed_states` | INITIAL_INQUIRY |
| `proposed_should_escalate` | `False` |
| `human_status` | NORMAL |
| `human_areas` | DELIVERY_AND_FULFILLMENT\|ORDER_MANAGEMENT\|REFUNDS_AND_BILLING |
| `human_intents` | DELIVERY_DELAYED\|CANCEL_ORDER_REQUEST\|REFUND_STATUS_INQUIRY |
| `human_primary_intent` | DELIVERY_DELAYED |
| `human_states` | WAITING_WINDOW_EXCEEDED |
| `human_should_escalate` | `False` |
| `human_escalation_reason` | *null (NaN)* |
| `human_notes` | Compound overdue-order + cancellation + refund request; refund intent is the closest available taxonomy label. |
| `review_flags` | *null (NaN)* |
| `assistant_outcome` | *null (NaN)* |
| `review_priority` | NORMAL |
| `assistant_status_recommendation` | NORMAL |
| `assistant_areas_recommendation` | DELIVERY_AND_FULFILLMENT\|ORDER_MANAGEMENT\|REFUNDS_AND_BILLING |
| `assistant_intents_recommendation` | DELIVERY_DELAYED\|CANCEL_ORDER_REQUEST\|REFUND_STATUS_INQUIRY |
| `assistant_primary_intent_recommendation` | DELIVERY_DELAYED |
| `assistant_states_recommendation` | WAITING_WINDOW_EXCEEDED |
| `assistant_should_escalate_recommendation` | `False` |
| `assistant_escalation_reason_recommendation` | *null (NaN)* |
| `assistant_notes_recommendation` | Compound overdue-order + cancellation + refund request; refund intent is the closest available taxonomy label. |
| `human_action` | Verify recommendation; accept/correct. |
| `adjudication_status` | ASSISTANT_RECOMMENDATION_PENDING_HUMAN_SIGNOFF |


### Representative Case: Ambiguous Message (Vague Support Inquiry) (`gold_0014` / `amazon_case_0040497`)

| Field | Value |
|---|---|
| `gold_id` | gold_0014 |
| `case_id` | amazon_case_0040497 |
| `conversation_id` | `58087` |
| `customer_message` | can I DM you instead? |
| `context` | CUSTOMER: I replied a while ago<br/>CUSTOMER: can I DM you instead? |
| `proposed_status` | AMBIGUOUS |
| `proposed_areas` | *null (NaN)* |
| `proposed_intents` | *null (NaN)* |
| `proposed_primary_intent` | *null (NaN)* |
| `proposed_states` | INITIAL_INQUIRY |
| `proposed_should_escalate` | `False` |
| `human_status` | AMBIGUOUS |
| `human_areas` | *null (NaN)* |
| `human_intents` | *null (NaN)* |
| `human_primary_intent` | *null (NaN)* |
| `human_states` | INITIAL_INQUIRY |
| `human_should_escalate` | `False` |
| `human_escalation_reason` | *null (NaN)* |
| `human_notes` | Assistant-reviewed pre-annotation; human sign-off still required. |
| `review_flags` | *null (NaN)* |
| `assistant_outcome` | *null (NaN)* |
| `review_priority` | NORMAL |
| `assistant_status_recommendation` | AMBIGUOUS |
| `assistant_areas_recommendation` | *null (NaN)* |
| `assistant_intents_recommendation` | *null (NaN)* |
| `assistant_primary_intent_recommendation` | *null (NaN)* |
| `assistant_states_recommendation` | INITIAL_INQUIRY |
| `assistant_should_escalate_recommendation` | `False` |
| `assistant_escalation_reason_recommendation` | *null (NaN)* |
| `assistant_notes_recommendation` | Assistant-reviewed pre-annotation; human sign-off still required. |
| `human_action` | Verify recommendation; accept/correct. |
| `adjudication_status` | ASSISTANT_RECOMMENDATION_PENDING_HUMAN_SIGNOFF |


### Representative Case: Out-of-Scope Inquiry (Non-Support Message) (`gold_0020` / `amazon_case_0055864`)

| Field | Value |
|---|---|
| `gold_id` | gold_0020 |
| `case_id` | amazon_case_0055864 |
| `conversation_id` | `80637` |
| `customer_message` | Need support on seller central |
| `context` | CUSTOMER: If you are paying for a premium rate call you at least expect to get someone who speaks English<br/>BRAND: Can I ask what number you contacted? And where you found it? Our contact number is not a premium rate number but freephone within the UK. Additionally, if you contact us through the website we'll call you back rather than you call us: <URL><br/>CUSTOMER: This is the number 0870 042 0479<br/>BRAND: Thank you for providing that for us. If you contact us via our website, we will call you back. You can do so via this link: <URL> As per previous correspondence, we have a freephone within the UK..<br/>CUSTOMER: Need support on seller central |
| `proposed_status` | AMBIGUOUS |
| `proposed_areas` | *null (NaN)* |
| `proposed_intents` | *null (NaN)* |
| `proposed_primary_intent` | *null (NaN)* |
| `proposed_states` | INITIAL_INQUIRY |
| `proposed_should_escalate` | `False` |
| `human_status` | OUT_OF_SCOPE |
| `human_areas` | *null (NaN)* |
| `human_intents` | *null (NaN)* |
| `human_primary_intent` | *null (NaN)* |
| `human_states` | INITIAL_INQUIRY |
| `human_should_escalate` | `False` |
| `human_escalation_reason` | *null (NaN)* |
| `human_notes` | Seller Central is merchant support outside the chosen consumer-support scope. |
| `review_flags` | TAXONOMY_GAP_REVIEW |
| `assistant_outcome` | OUT_OF_TAXONOMY |
| `review_priority` | HUMAN_REVIEW |
| `assistant_status_recommendation` | OUT_OF_SCOPE |
| `assistant_areas_recommendation` | *null (NaN)* |
| `assistant_intents_recommendation` | *null (NaN)* |
| `assistant_primary_intent_recommendation` | *null (NaN)* |
| `assistant_states_recommendation` | INITIAL_INQUIRY |
| `assistant_should_escalate_recommendation` | `False` |
| `assistant_escalation_reason_recommendation` | *null (NaN)* |
| `assistant_notes_recommendation` | Seller Central is merchant support outside the chosen consumer-support scope. |
| `human_action` | Inspect context carefully before accepting. |
| `adjudication_status` | PRIORITY_CASE_ASSISTANT_ADJUDICATED_NEEDS_HUMAN_CONFIRMATION |


### Representative Case: Security Escalation (Account Compromised) (`gold_0001` / `amazon_case_0055972`)

| Field | Value |
|---|---|
| `gold_id` | gold_0001 |
| `case_id` | amazon_case_0055972 |
| `conversation_id` | `1391472` |
| `customer_message` | rude & disrespectful delivery person who refused 2 deliver to the mentioned address until someone comes down and collects it.(1/2) |
| `context` | CUSTOMER: rude & disrespectful delivery person who refused 2 deliver to the mentioned address until someone comes down and collects it.(1/2)<br/>BRAND: I apologize for the inappropriate behavior of the delivery agent.1/3<br/>BRAND: I've noted your comments and have forwarded your feedback internally. 2/3 |
| `proposed_status` | NORMAL |
| `proposed_areas` | DELIVERY_AND_FULFILLMENT |
| `proposed_intents` | CARRIER_FEEDBACK_AND_INSTRUCTIONS |
| `proposed_primary_intent` | CARRIER_FEEDBACK_AND_INSTRUCTIONS |
| `proposed_states` | INITIAL_INQUIRY |
| `proposed_should_escalate` | `True` |
| `human_status` | NORMAL |
| `human_areas` | DELIVERY_AND_FULFILLMENT |
| `human_intents` | CARRIER_FEEDBACK_AND_INSTRUCTIONS |
| `human_primary_intent` | CARRIER_FEEDBACK_AND_INSTRUCTIONS |
| `human_states` | INITIAL_INQUIRY |
| `human_should_escalate` | `True` |
| `human_escalation_reason` | *null (NaN)* |
| `human_notes` | Assistant-reviewed pre-annotation; human sign-off still required. |
| `review_flags` | *null (NaN)* |
| `assistant_outcome` | *null (NaN)* |
| `review_priority` | NORMAL |
| `assistant_status_recommendation` | NORMAL |
| `assistant_areas_recommendation` | DELIVERY_AND_FULFILLMENT |
| `assistant_intents_recommendation` | CARRIER_FEEDBACK_AND_INSTRUCTIONS |
| `assistant_primary_intent_recommendation` | CARRIER_FEEDBACK_AND_INSTRUCTIONS |
| `assistant_states_recommendation` | INITIAL_INQUIRY |
| `assistant_should_escalate_recommendation` | `True` |
| `assistant_escalation_reason_recommendation` | *null (NaN)* |
| `assistant_notes_recommendation` | Assistant-reviewed pre-annotation; human sign-off still required. |
| `human_action` | Verify recommendation; accept/correct. |
| `adjudication_status` | ASSISTANT_RECOMMENDATION_PENDING_HUMAN_SIGNOFF |

