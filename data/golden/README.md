# AmazonHelp Golden Evaluation Set (`golden_v1`)

**GOLDEN V1 STATUS:** `PENDING HUMAN SIGN-OFF`  
**Current State:** Golden v1 is waiting for human sign-off. Assistant-reviewed draft recommendations are prepared, but final human adjudication has not occurred.

---

## 1. Overview & Purpose

The golden evaluation set is an isolated benchmark of **exactly 200 cases** sampled from the canonical Amazon dataset (`data/processed/amazon_support_cases.parquet`) and evaluated against **Taxonomy v1** (`configs/taxonomy_v1.yaml`) and the **Human Annotation Guide** (`configs/annotation_guide.md`).

This locked evaluation set serves as the ground truth benchmark for:
- Intent classification performance (micro/macro F1, accuracy)
- Multi-label decomposition accuracy
- Conversation state tracking
- Ambiguity detection & clarification routing
- Out-of-scope domain gating
- Human escalation triggering
- Retrieval groundedness and reply generation evaluation
- LLM-as-a-judge evaluation calibration

---

## 2. Target Composition (200 Total Cases)

| Sampling Category | Target Count | Description |
|---|:---:|---|
| `COMMON` | 100 | Standard, high-volume single-intent cases across the 14 frozen leaf intents. |
| `RARE` | 25 | Specialized/underrepresented leaf intents (e.g. `ACCOUNT_LOGIN_ISSUES`, `RETURN_PICKUP_ISSUE`, `MODIFY_ORDER_DETAILS`, `DIGITAL_CONTENT_ACCESS`, `CARRIER_FEEDBACK_AND_INSTRUCTIONS`). |
| `BOUNDARY` | 20 | Pairwise boundary test cases evaluating subtle distinctions between confusable intents. |
| `MULTI_INTENT` | 20 | Compound inquiries where the customer expresses $\ge 2$ independently actionable problems. |
| `AMBIGUOUS` | 15 | Genuinely underspecified inquiries lacking order details or clear problem statements (`classification_status: AMBIGUOUS`). |
| `HIGH_RISK` | 10 | Security lockouts, account compromise, repeated failed attempts, or severe disputes (`should_escalate: true`). |
| `OUT_OF_SCOPE` | 10 | Non-support dialogue, marketing remarks, or social banter (`classification_status: OUT_OF_SCOPE`). |
| **TOTAL** | **200** | **100% conversation-isolated, unique cases.** |

---

## 3. Data Schema (`golden_set.jsonl`)

Each line in `data/golden/golden_set.jsonl` is a JSON object with the following schema:

```json
{
  "gold_id": "gold_0001",
  "case_id": "amazon_case_0042701",
  "conversation_id": "606016",
  "customer_id": "278484",
  "context": "CUSTOMER: So Amazon decided an order I placed was suspicious...",
  "customer_message": "So Amazon decided an order I placed was suspicious and locked my account. Password reset appears to work but still can't log in. Ugh.",
  "areas": [
    "ACCOUNT_ACCESS_AND_SECURITY"
  ],
  "intents": [
    "ACCOUNT_LOGIN_ISSUES"
  ],
  "primary_intent": "ACCOUNT_LOGIN_ISSUES",
  "is_multi_intent": false,
  "classification_status": "NORMAL",
  "states": [
    "INITIAL_INQUIRY"
  ],
  "should_escalate": true,
  "escalation_reason": [
    "SECURITY_LOCKOUT"
  ],
  "difficulty": "HARD",
  "sampling_category": "HIGH_RISK",
  "annotator_notes": "Account flagged as suspicious and locked; password reset loop."
}
```

---

## 4. Human Annotation Workflow (`annotation_template.csv`)

For human inspection or editing, `annotation_template.csv` provides a tabular view of the 200 cases. Annotators can review:
1. `customer_message` & `context`
2. `classification_status` (`NORMAL`, `AMBIGUOUS`, `OUT_OF_SCOPE`)
3. `is_multi_intent` (`True` / `False`)
4. `areas` (pipe-delimited, e.g. `DELIVERY_AND_FULFILLMENT|REFUNDS_AND_BILLING`)
5. `intents` (pipe-delimited, e.g. `DELIVERY_DELAYED|UNRECOGNIZED_OR_DUPLICATE_CHARGE`)
6. `primary_intent` (primary operational driver)
7. `states` (e.g. `INITIAL_INQUIRY`, `TRACKING_ALREADY_CHECKED`)
8. `should_escalate` (`True` / `False`)
9. `escalation_reason` (e.g. `ACCOUNT_SECURITY_COMPROMISE`)
10. `difficulty` (`EASY`, `MEDIUM`, `HARD`)
11. `annotator_notes`

---

## 5. Quality Assurance & Re-Annotation Protocol

To ensure high inter-annotator reliability:
- A random sample of **40 cases** (stratified across boundary, multi-intent, ambiguous, and high-risk cases) is designated for independent second-review or self-reannotation after a delay.
- Agreement metrics evaluated:
  - Cohen's Kappa ($\kappa$) for Primary Intent
  - F1 / Jaccard similarity for Multi-Intent sets
  - Accuracy for `classification_status`
  - Agreement on `should_escalate`
- Any dispute or discrepancy with $\kappa < 0.85$ requires adjudication against `configs/annotation_guide.md`.

---

## 6. Strict Isolation & Leakage Prevention

- All 200 conversation IDs are isolated from the development and retrieval pools.
- The split manifest is recorded in [`data/splits/split_manifest.json`](file:///e:/Intern_Presentation/Hiver%20Project/data/splits/split_manifest.json).
- Run `python scripts/validate_golden_set.py` to verify all 14 integrity invariants before running downstream benchmarks.
