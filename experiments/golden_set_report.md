# Golden Evaluation Set (`golden_v1`) Distribution Report

**Status:** LOCKED  
**Total Cases:** 200  
**Taxonomy Reference:** Taxonomy v1 (`configs/taxonomy_v1.yaml`)  
**Evaluation File:** `data/golden/golden_set.jsonl`  
**Manifest:** `data/splits/split_manifest.json`  
**Date:** 2026-09-12  

---

## 1. Overview & Sampling Strategy

The Golden Evaluation Set consists of **exactly 200 unique cases** selected from the canonical AmazonHelp support dataset (`data/processed/amazon_support_cases.parquet`).
All sampling was executed strictly at the **conversation level**, ensuring 100% isolation between the golden evaluation benchmark and all downstream training, development, and retrieval sets.

### Sampling Category Breakdown

| Category | Count | Percentage | Operational Focus |
|---|:---:|:---:|---|
| `COMMON` | 100 | 50.0% | Core high-volume single-intent cases across the 14 frozen leaf intents. |
| `RARE` | 25 | 12.5% | Underrepresented specialized leaf intents (`CARRIER_FEEDBACK`, `RETURN_PICKUP`, etc.). |
| `BOUNDARY` | 20 | 10.0% | Subtle pairwise edge cases testing intent distinguishing boundaries. |
| `MULTI_INTENT` | 20 | 10.0% | Compound inquiries containing $\ge 2$ independently actionable problems. |
| `AMBIGUOUS` | 15 | 7.5% | Underspecified inquiries requiring a clarifying conversational turn. |
| `HIGH_RISK` | 10 | 5.0% | Account security locks, severe disputes, or repeated failed support cycles. |
| `OUT_OF_SCOPE` | 10 | 5.0% | Social banter, marketing comments, or non-support inquiries. |
| **Total** | **200** | **100.0%** | **Comprehensive benchmark across all support challenges.** |

---

## 2. Classification Status Distribution

| Classification Status | Case Count | Percentage | Operational Handling |
|---|:---:|:---:|---|
| `NORMAL` | 175 | 87.5% | Standard support routing to one or more business intents. |
| `AMBIGUOUS` | 15 | 7.5% | Clarification protocol; agent asks for order ID or problem specifics. |
| `OUT_OF_SCOPE` | 10 | 5.0% | Upstream domain safety gate; polite deflection or conversational exit. |

---

## 3. Business Area Distribution

Every business area in Taxonomy v1 is robustly represented across the 175 in-scope cases (including multi-intent cases spanning multiple areas):

| Broad Business Area | Active Intent Mentions | Percentage of In-Scope Turns |
|---|:---:|:---:|
| `DELIVERY_AND_FULFILLMENT` | 55 | 27.2% |
| `RETURNS_AND_REPLACEMENTS` | 32 | 15.8% |
| `ORDER_MANAGEMENT` | 27 | 13.4% |
| `ACCOUNT_ACCESS_AND_SECURITY` | 27 | 13.4% |
| `DIGITAL_SERVICES_AND_PRIME` | 26 | 12.9% |
| `REFUNDS_AND_BILLING` | 25 | 12.4% |

---

## 4. Leaf Intent Distribution (Primary & Total Mentions)

The golden set intentionally stratifies across all **14 frozen leaf intents**, avoiding monopoly by standard delivery inquiries:

| Frozen Leaf Intent | Primary Intent Count | Total Mentions (inc. Multi-Intent) | Sampling Difficulty Profile |
|---|:---:|:---:|---|
| `ACCOUNT_LOGIN_ISSUES` | 27 | 27 | Easy (10) / Medium (8) / Hard (9) |
| `WHERE_IS_MY_ORDER` | 15 | 16 | Easy (11) / Medium (4) / Hard (1) |
| `DIGITAL_CONTENT_ACCESS` | 15 | 15 | Easy (7) / Medium (6) / Hard (2) |
| `RETURN_PICKUP_ISSUE` | 14 | 16 | Easy (6) / Medium (7) / Hard (3) |
| `DELIVERY_DELAYED` | 12 | 12 | Easy (4) / Medium (5) / Hard (3) |
| `MODIFY_ORDER_DETAILS` | 12 | 14 | Easy (4) / Medium (7) / Hard (3) |
| `MARKED_DELIVERED_NOT_RECEIVED` | 11 | 11 | Easy (4) / Medium (4) / Hard (3) |
| `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | 16 | 16 | Medium (9) / Hard (7) |
| `CANCEL_ORDER_REQUEST` | 10 | 13 | Easy (5) / Medium (4) / Hard (4) |
| `DAMAGED_OR_DEFECTIVE_ITEM` | 9 | 9 | Easy (4) / Medium (3) / Hard (2) |
| `WRONG_ITEM_RECEIVED` | 9 | 9 | Easy (4) / Medium (3) / Hard (2) |
| `PRIME_MEMBERSHIP_MANAGEMENT` | 9 | 13 | Easy (3) / Medium (7) / Hard (3) |
| `REFUND_STATUS_INQUIRY` | 8 | 15 | Easy (4) / Medium (5) / Hard (6) |
| `UNRECOGNIZED_OR_DUPLICATE_CHARGE` | 8 | 10 | Easy (4) / Medium (3) / Hard (3) |
| *(None / Ambiguous or Out-of-Scope)* | 25 | — | Medium (15) / Easy (10) |

---

## 5. Multi-Intent Breakdown (20 Cases, 10.0%)

20 cases feature compound, orthogonal customer requests where $\ge 2$ business intents are active:
- **Dual Intents**: 18 cases (e.g. `PRIME_MEMBERSHIP_MANAGEMENT` + `UNRECOGNIZED_OR_DUPLICATE_CHARGE`, `WRONG_ITEM_RECEIVED` + `RETURN_PICKUP_ISSUE`).
- **Triple Intents**: 2 cases (e.g. `DELIVERY_DELAYED` + `CANCEL_ORDER_REQUEST` + `REFUND_STATUS_INQUIRY`).
- **Cross-Area Composition**: 16 of the 20 multi-intent cases span multiple broad areas (e.g. Fulfillment + Billing).

---

## 6. High-Risk & Escalation Distribution (10 Cases, 5.0%)

Escalation decisions are justified by verifiable policy and risk factors rather than customer emotion:

| Escalation Reason | Count | Operational Impact |
|---|:---:|---|
| `ACCOUNT_SECURITY_COMPROMISE` | 4 | Unauthorized credential/email change; immediate account freeze required. |
| `SECURITY_LOCKOUT` | 2 | Account flagged for suspicious activity; automated password reset failing. |
| `REPEATED_FAILED_SUPPORT_ATTEMPTS` | 2 | Customer contacted support >5 times or sent multiple faxes/emails without resolution. |
| `CARRIER_MISCONDUCT_SEVERE` | 2 | Physical delivery refusal or aggressive courier conduct. |

---

## 7. Dialogue Context & Structural Diversity

### Conversation Length Distribution
The benchmark includes early-turn interactions, standard resolutions, and extended multi-turn dialogues:
- **Short Conversations (2 turns)**: 55 cases (27.5%)
- **Medium Conversations (3–5 turns)**: 77 cases (38.5%)
- **Long Conversations (6–10 turns)**: 54 cases (27.0%)
- **Deep Thread Conversations (11–100 turns)**: 14 cases (7.0%)

### Conversation States
- `INITIAL_INQUIRY`: 197 cases (standard opening problem statements)
- `WAITING_WINDOW_EXCEEDED`: 2 cases (escalation SLA breaches)
- `TRACKING_ALREADY_CHECKED`: 1 case (customer reports tracking checked)

### Difficulty Distribution
- `EASY`: 66 cases (33.0%) — Clean, prototypical single-intent statements.
- `MEDIUM`: 84 cases (42.0%) — Realistic inquiries with minor ambiguity, longer descriptions, or subtle terminology.
- `HARD`: 50 cases (25.0%) — Multi-intent turns, boundary edge cases, and high-risk security compromises.

### Language Distribution
- `en` (English): 200 cases (100.0%)

---

## 8. Data Leakage & Isolation Verification

- **Total Canonical Conversations:** 82,555
- **Golden Conversations:** 200 (0.24%)
- **Development / Training Pool:** 82,355 (99.76%)
- **Intersection Verification:**
  $$\text{golden\_conversation\_ids} \cap \text{development\_conversation\_ids} = \emptyset$$
- **Leakage Status:** **0% LEAKAGE DETECTED (Strictly Isolated).**
