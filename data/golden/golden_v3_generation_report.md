# Golden V3 Generation and Validation Report

**Dataset File:** `E:/Intern_Presentation/Hiver Project/data/golden/golden_v3_assistant_adjudicated.csv`  
**Total Cases:** 200  
**Adjudication Status:** 100% human-adjudicated to frozen Taxonomy V1.0  

---

## 1. Executive Summary
Golden V3 is an independent, unseen 200-case evaluation benchmark designed to evaluate whether Policy Iteration 2 improvements generalize to unseen customer inquiries. Golden V3 adheres strictly to the frozen 32-column schema, frozen Taxonomy V1 leaf intents, and validated human ground-truth standards, with zero data leakage from Golden V1 or Golden V2.

## 2. Dataset Distribution

### Status Distribution
- `NORMAL`: **165** (82.5%)
- `AMBIGUOUS`: **23** (11.5%)
- `OUT_OF_SCOPE`: **12** (6.0%)

### Escalation Distribution
- `Should Escalate = True`: **51** (25.5%)
- `Should Escalate = False`: **149** (74.5%)

### Escalation Reason Breakdown (Escalated Cases)
- `ACCOUNT_SECURITY_COMPROMISE`: **19**
- `REPEATED_FAILED_SUPPORT_ATTEMPTS`: **19**
- `CARRIER_MISCONDUCT_AND_REFUSAL`: **13**

### Operational State Distribution
- `INITIAL_INQUIRY`: **160** (80.0%)
- `WAITING_WINDOW_EXCEEDED`: **27** (13.5%)
- `TRACKING_ALREADY_CHECKED`: **9** (4.5%)
- `DETAILS_ALREADY_PROVIDED`: **4** (2.0%)

### Primary Intent Distribution (NORMAL cases)
- `ACCOUNT_LOGIN_ISSUES`: **30**
- `CARRIER_FEEDBACK_AND_INSTRUCTIONS`: **23**
- `DELIVERY_DELAYED`: **14**
- `DAMAGED_OR_DEFECTIVE_ITEM`: **13**
- `RETURN_PICKUP_ISSUE`: **12**
- `WRONG_ITEM_RECEIVED`: **12**
- `WHERE_IS_MY_ORDER`: **11**
- `MARKED_DELIVERED_NOT_RECEIVED`: **11**
- `REFUND_STATUS_INQUIRY`: **10**
- `CANCEL_ORDER_REQUEST`: **7**
- `PRIME_MEMBERSHIP_MANAGEMENT`: **7**
- `MODIFY_ORDER_DETAILS`: **6**
- `DIGITAL_CONTENT_ACCESS`: **6**
- `UNRECOGNIZED_OR_DUPLICATE_CHARGE`: **3**

## 3. Structural Statistics
- **Multi-Intent Cases:** **20** cases (10.0%)
- **Multi-Turn Conversations:** **114** cases (57.0%)
- **Single-Turn Cases:** **86** cases (43.0%)

## 4. Challenge Category Coverage
Golden V3 systematically covers the challenge areas targeted by Policy Iteration 2:

| Challenge Dimension | Cases | Description |
| :--- | :---: | :--- |
| **Carrier Misconduct & Refusal** | 10 | Driver refusal, abusive language, delivery ultimatum, package throwing, forged signatures |
| **Routine Carrier Negative Controls** | 10 | Gate codes, delivery notes, positive feedback, carrier contact requests (MUST NOT escalate) |
| **Repeated Failed Support** | 17 | Multi-contact across attempts, circular transfers, broken callback promises |
| **Single Contact Negative Controls** | 4 | Single prior support contact asking for follow-up (MUST NOT escalate) |
| **Account Security & Compromise** | 14 | Account takeover, unauthorized credential updates, fraud from compromise |
| **Account Lock & Failed Recovery** | 4 | Suspended/locked profile with broken verification or password loop |
| **Routine Login & Password Controls** | 10 | Normal password reset, 2FA configuration, biometric login assistance |
| **Tracking Edge Cases & Inquiries** | 5 | 'Where is tracking' vs already checked tracking |
| **State Consistency Controls** | 2 | Valid follow-ups after checking tracking / details provided |
| **Delivery Delays & Disputes** | 15 | Transit delays, marked delivered but missing |
| **Returns & Damaged Goods** | 30 | Defective items, wrong merchandise, missed return pickup, refund arrival |
| **Order Management & Prime** | 19 | Cancellations, address modification, Prime fee refund, Kindle/Video sync |
| **Multi-Intent Combinations** | 20 | Complex realistic multi-issue inquiries spanning multiple categories |
| **Ambiguous Cases** | 23 | Genuinely ambiguous prompts requiring clarification |
| **Out-of-Scope Requests** | 12 | Non-retail queries (weather, coding, stocks, medical, legal) safely declined |

## 5. Anti-Leakage & Novelty Verification
- **Exact Message Leakage vs V1:** **0** matching customer messages.
- **Exact Message Leakage vs V2:** **0** matching customer messages.
- **Conversation ID Collisions:** **0** overlapping IDs with V1 or V2 (`conv_id` range 3600001–3600200).
- **Case ID Collisions:** **0** overlapping IDs with V1 or V2 (`amazon_v3_case_*`).
- **Internal Duplicates in V3:** **0** duplicate customer messages; all 200 inquiries are distinct.

## 6. Schema & Contract Adherence
- Exactly 200 rows and 32 columns.
- All statuses conform strictly to `NORMAL`, `AMBIGUOUS`, or `OUT_OF_SCOPE`.
- For `AMBIGUOUS` and `OUT_OF_SCOPE`, intents, areas, and primary intents are null/empty.
- For `NORMAL`, every intent is validated against the 14 frozen Taxonomy V1 leaf intents, and primary intent belongs to the declared set.
- All operational states strictly conform to the 5 permitted taxonomy states.
- All escalation decisions are binary booleans (`True` or `False`), with valid reason codes recorded for escalated cases.

---
*Golden V3 dataset generation and validation complete. Dataset is locked and ready for independent evaluation.*