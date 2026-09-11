# TAXONOMY HUMAN REVIEW CHECKLIST

> [!IMPORTANT]
> The LLM review served as advisory input. The Human Support Operations Authority has completed final evaluation and sign-off.
> **All human decisions below are final and govern Taxonomy v1 (FROZEN).**

**Review Mode:** `openrouter` | **Model:** `nvidia/nemotron-3-super-120b-a12b:free` | **Sign-off Date:** `2026-09-12`

| Intent | LLM Decision | Human Decision | Notes |
|---|---|---|---|
| `WHERE_IS_MY_ORDER` | **KEEP** | **KEEP** | Semantically coherent, high-volume WISMO inquiries within or on the promised delivery window. Operationally distinct (routine tracking link vs delay escalation). Consistently annotatable. |
| `DELIVERY_DELAYED` | **KEEP** | **KEEP** | Shipment overdue past promised SLA date. Triggers carrier investigation, revised ETA, or shipping concession rather than standard tracking check. |
| `MARKED_DELIVERED_NOT_RECEIVED` | **KEEP** | **KEEP** | Digital tracking confirms delivery (e.g. handed to resident / front door) but physical parcel missing. Triggers safe-place verification, neighbor check, and loss investigation. |
| `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | **KEEP** | **KEEP** | Specific feedback/complaints regarding courier driver behavior, property damage, gate instructions, or customs/KYC holds. Routed to logistics partner operations. |
| `DAMAGED_OR_DEFECTIVE_ITEM` | **KEEP** | **KEEP** | Correct product delivered but broken, leaking, or non-functional. Operationally distinct from wrong item: eligible for immediate replacement without return requirement in many categories. |
| `WRONG_ITEM_RECEIVED` | **KEEP** | **KEEP** | Incorrect product SKU, model, or variant sent. Operationally distinct: requires return label generation and inventory reconciliation for the mistaken item. |
| `RETURN_PICKUP_ISSUE` | **KEEP** | **KEEP** | Return already authorized, but courier failed scheduled pickup or return label barcode failed at drop-off. Triggers courier re-dispatch workflow. |
| `REFUND_STATUS_INQUIRY` | **KEEP** | **KEEP** | Customer tracking timeline or bank settlement for already returned/cancelled order. Distinct from active dispute; requires payment gateway status lookup. |
| `UNRECOGNIZED_OR_DUPLICATE_CHARGE` | **RENAME** | **KEEP** | **Human Decision: KEEP.** Rejects LLM recommendation to narrow to `DUPLICATE_CHARGE`. The taxonomy must remain broad and stable enough to encompass both dual authorization holds and unrecognized statement charges without premature fragmentation. |
| `CANCEL_ORDER_REQUEST` | **KEEP** | **KEEP** | Pre-dispatch cancellation request prior to warehouse fulfillment. Requires warehouse intercept or cancel eligibility verification. |
| `MODIFY_ORDER_DETAILS` | **RENAME** | **KEEP** | **Human Decision: KEEP.** Rejects LLM recommendation to narrow to `CHANGE_DELIVERY_ADDRESS`. The candidate must remain broad enough to handle shipping address, payment method, and delivery slot changes without prematurely constraining the intent to a single subtype. |
| `PRIME_MEMBERSHIP_MANAGEMENT` | **KEEP** | **KEEP** | Subscription lifecycle inquiries (Prime renewal, unwanted trial conversion, membership fee refund, cancellation). Requires dedicated Prime management tooling. |
| `DIGITAL_CONTENT_ACCESS` | **KEEP** | **KEEP** | Technical barriers accessing Prime Video, Kindle books, Amazon Music, or Fire TV devices. Operationally routed to digital device and content streaming support flows. |
| `ACCOUNT_LOGIN_OR_OTP` | **RENAME** | **RENAME -> ACCOUNT_LOGIN_ISSUES** | **Human Decision: RENAME.** Renamed to `ACCOUNT_LOGIN_ISSUES`. Cleaner, standard nomenclature while maintaining exact operational scope (2FA/OTP SMS delivery failure, password recovery, credential lockouts). |
| `AMBIGUOUS_INQUIRY` | **SPLIT** | **MOVE OUT OF BUSINESS INTENT TAXONOMY -> CLASSIFICATION STATUS** | **Human Decision: Non-Intent Control Concept.** `AMBIGUOUS_INQUIRY` is not a customer business problem. It represents a classification status (`classification_status: AMBIGUOUS`) signifying insufficient evidence to route, requiring a clarifying conversational turn. |
| `MULTI_INTENT` | **SPLIT** | **MOVE OUT OF BUSINESS INTENT TAXONOMY -> MULTI-LABEL PROPERTY** | **Human Decision: Non-Intent Control Concept.** `MULTI_INTENT` is not a business intent. It is modeled as a multi-label output property (`is_multi_intent: true`, `active_intents: [intent1, intent2]`). Combinatorial hybrid labels are strictly prohibited. |
| `OUT_OF_SCOPE` | **DROP** | **MOVE OUT OF BUSINESS INTENT TAXONOMY -> DOMAIN GATE** | **Human Decision: Non-Intent Control Concept.** `OUT_OF_SCOPE` is not a support intent. It is handled by an upstream domain/scope safety gate (`classification_status: OUT_OF_SCOPE`) before business intent classification occurs. |

---

## Human Sign-off

Status: APPROVED

Taxonomy Version: 1.0

Leaf Intent Count: 14

Reviewer: Human project owner

Date: 2026-09-12
