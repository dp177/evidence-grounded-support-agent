# Human Sign-Off Instructions: Golden Evaluation Set v1

**Benchmark Version:** `golden_v1` (200 cases)  
**Status:** `PENDING HUMAN SIGN-OFF`  
**Taxonomy Reference:** `configs/taxonomy_v1.yaml` (FROZEN)  
**Priority Review Workspace:** `data/golden/priority_human_signoff.csv` (24 cases)  
**Full Review Workspace:** `data/golden/golden_v1_human_signoff.csv` (200 cases)  

---

## 1. Overview & Human Review Philosophy

> [!IMPORTANT]
> All labels in the `assistant_*_recommendation` columns are **assistant-reviewed recommendations** and do **NOT** constitute final ground truth until you explicitly sign off.
>
> **Golden Evaluation Set v1 will remain UNLOCKED until all human decisions are recorded and validated.**

---

## 2. Review Workflow: Start with the 24 Priority Cases

To minimize cognitive load, review the **24 priority cases** in [`data/golden/priority_human_signoff.csv`](file:///e:/Intern_Presentation/Hiver%20Project/data/golden/priority_human_signoff.csv) first:

1. **Inspect Each Row**:
   - Read `customer_message` and the full dialogue in `context`.
   - Read the assistant recommendations:
     - `assistant_status_recommendation`
     - `assistant_intents_recommendation`
     - `assistant_primary_intent_recommendation`
     - `assistant_states_recommendation`
     - `assistant_should_escalate_recommendation`
     - `assistant_escalation_reason_recommendation`
     - `assistant_notes_recommendation`

2. **Choose Decision**:
   For the `human_decision` column, enter either:
   - **`ACCEPT`**: You agree with the assistant recommendation. The assistant recommendation will become the definitive human ground truth.
   - **`OVERRIDE`**: You disagree with one or more fields.

3. **If You Choose `OVERRIDE`**:
   - In `human_override_reason`, state clearly what you are overriding (e.g. `OVERRIDE: status=AMBIGUOUS` or `OVERRIDE: primary_intent=DELIVERY_DELAYED; escalate=True`).
   - In `human_notes`, provide a brief justification explaining why the assistant recommendation was overturned.

---

## 3. Strict Taxonomy Rules for Overrides

If you override an intent or status, you must adhere strictly to [`configs/taxonomy_v1.yaml`](file:///e:/Intern_Presentation/Hiver%20Project/configs/taxonomy_v1.yaml):

1. **Do NOT Invent New Intents**:
   Use **ONLY** the 14 approved leaf intents listed below.

2. **`AMBIGUOUS` Handling**:
   - `human_status = AMBIGUOUS`
   - `human_areas = ""` (empty)
   - `human_intents = ""` (empty)
   - `human_primary_intent = ""` (empty)

3. **`OUT_OF_SCOPE` Handling**:
   - `human_status = OUT_OF_SCOPE`
   - `human_areas = ""` (empty)
   - `human_intents = ""` (empty)
   - `human_primary_intent = ""` (empty)

4. **Multi-Intent Handling**:
   - If a customer message expresses multiple distinct actionable needs, separate valid leaf intents with a pipe character (`|`), e.g.:
     `DELIVERY_DELAYED|REFUND_STATUS_INQUIRY`
   - Never use `MULTI_INTENT` as an intent name (it is a property, not a business category).
   - Set `primary_intent` to the single most operationally urgent leaf intent from the multi-intent set.

5. **Escalation Rules**:
   - `human_should_escalate` must be `True` or `False`.
   - If `human_should_escalate == True`, `human_escalation_reason` must be provided (e.g. `ACCOUNT_SECURITY_COMPROMISE`, `REPEATED_FAILED_SUPPORT_ATTEMPTS`, `SAFETY_LEGAL_THREAT`).

---

## 4. Frozen Taxonomy Reference Vocabulary

### 6 Broad Business Areas:
- `DELIVERY_AND_FULFILLMENT`
- `RETURNS_AND_REPLACEMENTS`
- `REFUNDS_AND_BILLING`
- `ORDER_MANAGEMENT`
- `DIGITAL_SERVICES_AND_PRIME`
- `ACCOUNT_ACCESS_AND_SECURITY`

### 14 Leaf Intents:
1. `WHERE_IS_MY_ORDER`
2. `DELIVERY_DELAYED`
3. `MARKED_DELIVERED_NOT_RECEIVED`
4. `CARRIER_FEEDBACK_AND_INSTRUCTIONS`
5. `DAMAGED_OR_DEFECTIVE_ITEM`
6. `WRONG_ITEM_RECEIVED`
7. `RETURN_PICKUP_ISSUE`
8. `REFUND_STATUS_INQUIRY`
9. `UNRECOGNIZED_OR_DUPLICATE_CHARGE`
10. `CANCEL_ORDER_REQUEST`
11. `MODIFY_ORDER_DETAILS`
12. `PRIME_MEMBERSHIP_MANAGEMENT`
13. `DIGITAL_CONTENT_ACCESS`
14. `ACCOUNT_LOGIN_ISSUES`

### 5 Conversation States:
- `INITIAL_INQUIRY`
- `TRACKING_ALREADY_CHECKED`
- `CARRIER_ALREADY_CONTACTED`
- `DETAILS_ALREADY_PROVIDED`
- `WAITING_WINDOW_EXCEEDED`

---

## 5. Reviewing the Full 200 Cases (`golden_v1_human_signoff.csv`)

- The **176 non-priority cases** have high-confidence assistant recommendations that follow standard operational rules.
- Once you have reviewed the 24 priority cases, you can review the remaining 176 cases in [`data/golden/golden_v1_human_signoff.csv`](file:///e:/Intern_Presentation/Hiver%20Project/data/golden/golden_v1_human_signoff.csv).
- For batch acceptance of the remaining cases, mark `human_decision = ACCEPT`.

---

## 6. Verification Command

At any time during or after your review, run the automated validation script:

```bash
python scripts/check_human_signoff.py
```

- When fields are blank: reports `HUMAN SIGN-OFF STATUS = PENDING`.
- When fields are filled: validates all taxonomy constraints and reports whether sign-off is complete and valid.
