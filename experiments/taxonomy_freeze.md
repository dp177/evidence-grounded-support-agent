# Taxonomy v1 — Frozen

**Brand:** AmazonHelp  
**Version:** 1.0  
**Status:** FROZEN  
**Freeze Date:** 2026-09-12  

## Decision
The human reviewer has approved the business taxonomy for downstream evaluation and classification.

- **14 leaf business intents are frozen** across 6 business areas.
- **Multi-intent** is represented as a multi-label property (`is_multi_intent: true`, `active_intents: [...]`).
- **AMBIGUOUS** is a classification status indicating insufficient information for routing.
- **OUT_OF_SCOPE** is handled by an upstream domain/scope gate prior to business-intent classification.
- **Conversation states** and **outcomes** are modeled separately from business intents.

> [!IMPORTANT]
> **Changes after this point require a new taxonomy version (e.g. Taxonomy v1.1 or v2.0) rather than silently modifying Taxonomy v1.**

---

## Frozen Taxonomy Structure

### Broad Areas & Leaf Intents (14 Total)

1. **DELIVERY_AND_FULFILLMENT**
   - `WHERE_IS_MY_ORDER`
   - `DELIVERY_DELAYED`
   - `MARKED_DELIVERED_NOT_RECEIVED`
   - `CARRIER_FEEDBACK_AND_INSTRUCTIONS`

2. **RETURNS_AND_REPLACEMENTS**
   - `DAMAGED_OR_DEFECTIVE_ITEM`
   - `WRONG_ITEM_RECEIVED`
   - `RETURN_PICKUP_ISSUE`

3. **REFUNDS_AND_BILLING**
   - `REFUND_STATUS_INQUIRY`
   - `UNRECOGNIZED_OR_DUPLICATE_CHARGE`

4. **ORDER_MANAGEMENT**
   - `CANCEL_ORDER_REQUEST`
   - `MODIFY_ORDER_DETAILS`

5. **DIGITAL_SERVICES_AND_PRIME**
   - `PRIME_MEMBERSHIP_MANAGEMENT`
   - `DIGITAL_CONTENT_ACCESS`

6. **ACCOUNT_ACCESS_AND_SECURITY**
   - `ACCOUNT_LOGIN_ISSUES`

### Non-Intent Control Concepts

- **Classification Statuses**: `NORMAL`, `AMBIGUOUS`, `OUT_OF_SCOPE`
- **Multi-Intent Property**: `type: boolean` (`is_multi_intent: true|false`)
- **Conversation States**:
  - `INITIAL_INQUIRY`
  - `TRACKING_ALREADY_CHECKED`
  - `CARRIER_ALREADY_CONTACTED`
  - `DETAILS_ALREADY_PROVIDED`
  - `WAITING_WINDOW_EXCEEDED`
- **Outcomes**:
  - `RESOLVED_CLOSURE`
  - `ESCALATED_HUMAN_TIER2`
  - `DEFLECTED_SELF_SERVICE`
  - `CONCESSION_ISSUED`
  - `ABANDONED_UNRESPONSIVE`

---

## Governance and Downstream Artifacts

- Canonical Configuration: [`configs/taxonomy_v1.yaml`](file:///e:/Intern_Presentation/Hiver%20Project/configs/taxonomy_v1.yaml)
- Human Annotation Guide: [`configs/annotation_guide.md`](file:///e:/Intern_Presentation/Hiver%20Project/configs/annotation_guide.md)
- Human Sign-Off Checklist: [`experiments/taxonomy_human_review_checklist.md`](file:///e:/Intern_Presentation/Hiver%20Project/experiments/taxonomy_human_review_checklist.md)
- Automated Taxonomy Verification Test: [`tests/test_taxonomy_v1.py`](file:///e:/Intern_Presentation/Hiver%20Project/tests/test_taxonomy_v1.py)
