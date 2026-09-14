# Golden V2 Generation and Validation Report

**Dataset File:** `E:/Intern_Presentation/Hiver Project/data/golden/golden_v2_assistant_adjudicated.csv`  
**Total Cases:** 200  
**Adjudication Status:** 100% human-adjudicated to frozen Taxonomy V1.0  

---

## 1. Executive Summary
Golden V2 is a completely fresh, independent 200-case evaluation benchmark built to test whether policy and state extraction improvements generalize to unseen customer inquiries. Golden V2 preserves the exact 32-column schema and frozen taxonomy of Golden V1, with zero message or conversation leakage.

## 2. Dataset Distribution

### Status Distribution
- `NORMAL`: **165** (82.5%)
- `AMBIGUOUS`: **25** (12.5%)
- `OUT_OF_SCOPE`: **10** (5.0%)

### Escalation Distribution
- `Should Escalate = True`: **43** (21.5%)
- `Should Escalate = False`: **157** (78.5%)

### Escalation Reason Breakdown (Escalated Cases)
- `ACCOUNT_SECURITY_COMPROMISE`: **18**
- `REPEATED_FAILED_SUPPORT_ATTEMPTS`: **15**
- `CARRIER_MISCONDUCT_AND_REFUSAL`: **8**
- `HIGH_RISK_SECURITY`: **2**

### Operational State Distribution
- `INITIAL_INQUIRY`: **136** (68.0%)
- `WAITING_WINDOW_EXCEEDED`: **23** (11.5%)
- `TRACKING_ALREADY_CHECKED`: **20** (10.0%)
- `DETAILS_ALREADY_PROVIDED`: **11** (5.5%)
- `CARRIER_ALREADY_CONTACTED`: **10** (5.0%)

### Primary Intent Distribution (NORMAL cases)
- `ACCOUNT_LOGIN_ISSUES`: **31**
- `DELIVERY_DELAYED`: **20**
- `MARKED_DELIVERED_NOT_RECEIVED`: **15**
- `WHERE_IS_MY_ORDER`: **12**
- `DAMAGED_OR_DEFECTIVE_ITEM`: **12**
- `WRONG_ITEM_RECEIVED`: **12**
- `REFUND_STATUS_INQUIRY`: **12**
- `RETURN_PICKUP_ISSUE`: **12**
- `CARRIER_FEEDBACK_AND_INSTRUCTIONS`: **11**
- `CANCEL_ORDER_REQUEST`: **7**
- `PRIME_MEMBERSHIP_MANAGEMENT`: **7**
- `MODIFY_ORDER_DETAILS`: **5**
- `DIGITAL_CONTENT_ACCESS`: **5**
- `UNRECOGNIZED_OR_DUPLICATE_CHARGE`: **4**

## 3. Structural Statistics
- **Multi-Intent Cases:** **20** cases (10.0%)
- **Multi-Turn Conversations:** **92** cases (46.0%)
- **Single-Turn Cases:** **108** cases (54.0%)

## 4. Challenge Category Coverage
Golden V2 specifically covers the key challenge dimensions identified during Golden V1 analysis:

| Challenge Dimension | Cases | Description |
| :--- | :---: | :--- |
| **Account Security & Compromise** | 13 | Account takeover, unauthorized email/password changes, suspicious foreign login alerts |
| **Account Lock & Failed Recovery** | 6 | Account locks persisting through password resets, unresponsive verification reviews |
| **Routine Login & Password Inquiries** | 10 | Normal password resets and 2FA queries that MUST NOT escalate |
| **Repeated Failed Support** | 13 | Customer service contacted multiple/5 times, reps hung up, no resolution offered |
| **Carrier Misconduct & Delivery Refusal** | 6 | Drivers refusing doorstep delivery, demanding pickup, verbal hostility |
| **Tracking Number Edge Cases** | 13 | 'Where can I find tracking number' vs TRACKING_ALREADY_CHECKED vs premature delivery scans |
| **Multi-Turn Conversational State** | 31 | Conversations where state depends on prior turns (order ID/evidence already provided) |
| **Multi-Intent Combinations** | 15 | Complex realistic multi-issue inquiries spanning multiple categories |
| **Ambiguous Cases** | 25 | Vague greetings, unanchored help requests, emotional venting without issue details |
| **Out-of-Scope Requests** | 10 | Coding, weather, stock prices, Seller Central corporate tax, medical advice |

## 5. Anti-Leakage & Novelty Verification
- **Exact Message Leakage:** **0** matching customer messages between Golden V1 and Golden V2.
- **Conversation ID Collisions:** **0** overlapping conversation IDs between Golden V1 and Golden V2.
- **Case ID Collisions:** **0** overlapping case IDs.
- **Internal Duplicates in V2:** **0** duplicate customer messages; all 200 inquiries are distinct.

## 6. Schema & Contract Adherence
- Exactly 200 rows and 32 columns.
- All statuses conform strictly to `NORMAL`, `AMBIGUOUS`, or `OUT_OF_SCOPE`.
- For `AMBIGUOUS` and `OUT_OF_SCOPE`, intents, areas, and primary intents are verified null/empty.
- For `NORMAL`, every intent is validated against the 14 frozen Taxonomy V1 leaf intents, and primary intent belongs to the declared set.
- All operational states strictly conform to the 5 permitted taxonomy states.
- All escalation decisions are binary booleans (`True` or `False`), with valid reason codes recorded for escalated cases.

---
*Golden V2 dataset generation and validation complete. Dataset is locked and ready for un-tuned evaluation.*