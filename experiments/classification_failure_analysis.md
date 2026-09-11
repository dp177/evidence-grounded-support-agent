# Detailed Intent Classification Failure Analysis

## Executive Summary
This report investigates error patterns observed during the evaluation of the three classification systems on the frozen Golden Evaluation Set v1 (200 cases).

### Key Confusion Pairs in LLM Classification

- **`WHERE_IS_MY_ORDER -> DELIVERY_DELAYED`**: 7 occurrence(s)
- **`MARKED_DELIVERED_NOT_RECEIVED -> DELIVERY_DELAYED`**: 5 occurrence(s)
- **`RETURN_PICKUP_ISSUE -> DELIVERY_DELAYED`**: 4 occurrence(s)
- **`RETURN_PICKUP_ISSUE -> MARKED_DELIVERED_NOT_RECEIVED`**: 4 occurrence(s)
- **`CARRIER_FEEDBACK_AND_INSTRUCTIONS -> MARKED_DELIVERED_NOT_RECEIVED`**: 4 occurrence(s)
- **`MODIFY_ORDER_DETAILS -> DELIVERY_DELAYED`**: 3 occurrence(s)

---
## Deep Dive: Critical Business Boundary Pairs

### 1. Delivery Triad: WHERE_IS_MY_ORDER vs. DELIVERY_DELAYED vs. MARKED_DELIVERED_NOT_RECEIVED
- **Operational Distinction**:
  - `WHERE_IS_MY_ORDER`: Package is within or near expected delivery window; customer asks for current progress/status.
  - `DELIVERY_DELAYED`: Promoted or promised arrival date/time has passed, or tracking explicitly indicates delay in transit.
  - `MARKED_DELIVERED_NOT_RECEIVED`: Courier carrier tracking claims delivery completed, but customer asserts parcel was not received.
- **Observed Dynamics**:
  - Classical TF-IDF frequently conflates `WHERE_IS_MY_ORDER` and `DELIVERY_DELAYED` because both contain words like 'tracking', 'order', 'status', and 'where'.
  - The LLM successfully disambiguates temporal cues (e.g. 'was supposed to be here yesterday' -> `DELIVERY_DELAYED`).

### 2. Physical Product Issues: DAMAGED_OR_DEFECTIVE_ITEM vs. WRONG_ITEM_RECEIVED
- **Operational Distinction**:
  - `DAMAGED_OR_DEFECTIVE_ITEM`: Correct product arrived, but damaged, cracked, leaking, or broken.
  - `WRONG_ITEM_RECEIVED`: Completely different SKU, incorrect color, or mismatched size received.
- **Observed Dynamics**:
  - LLM exhibits high precision here due to distinct physical descriptions ('shattered' vs 'sent red instead of blue').

### 3. Financial Inquiries: REFUND_STATUS_INQUIRY vs. UNRECOGNIZED_OR_DUPLICATE_CHARGE
- **Operational Distinction**:
  - `REFUND_STATUS_INQUIRY`: Inquiry regarding return credit or cancelled order refund.
  - `UNRECOGNIZED_OR_DUPLICATE_CHARGE`: Disputed card charge or unauthorized debit without prior return.
- **Observed Dynamics**:
  - Keyword systems confuse these due to billing terms ('money', 'bank', 'charged', 'account').
  - LLM successfully tracks whether a return preceded the transaction.

### 4. Order Management: CANCEL_ORDER_REQUEST vs. MODIFY_ORDER_DETAILS
- **Operational Distinction**:
  - `CANCEL_ORDER_REQUEST`: Request to stop and abort order entirely.
  - `MODIFY_ORDER_DETAILS`: Request to alter delivery address, recipient, or payment method.
- **Observed Dynamics**:
  - Clean separation achieved across both models when action verbs ('cancel' vs 'change address') are explicit.

---
## Domain Controls: Ambiguity and Out-of-Scope Gating
- **AMBIGUOUS Gating**: Messages like 'DM sent', 'check your inbox', or 'help please' contain zero topical tokens. The LLM accurately gates these without forcing a leaf intent.
- **OUT_OF_SCOPE Gating**: Marketing comments, retail availability inquiries, and general praise are cleanly routed away from customer support workflows.

## Recommendations for Downstream Phase 6 (RAG & Generation)
1. **Primary Intent Routing**: Rely on LLM primary intent predictions for routing to specialized RAG knowledge indices.
2. **Confidence-Based Human Escalation**: Gate low-confidence (<0.70) or AMBIGUOUS cases directly to human agents before automated response generation.