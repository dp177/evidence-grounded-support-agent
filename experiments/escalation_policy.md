# Phase 10: Deterministic Escalation Policy & Risk Matrix

This document defines the deterministic escalation matrix governing the transition between **Automated Handling** and **Human Review** in the support agent system.

In compliance with the assignment specification, the final decision is **purely deterministic and auditable** — it is computed by rule-driven gating logic defined in `configs/escalation.yaml`, rather than delegated to an uncalibrated LLM.

---

## 1. Safety Principles

1. **Safety Over Coverage:** The highest priority is maintaining an **unsafe auto-handle rate of 0.0%**. An unnecessary human review is a cost; an unsafe auto-handle (e.g., hallucinated refund, security breach, state contradiction) is a catastrophic failure.
2. **Deterministic Hard Gates:** Gating rules cannot be bypassed by high model confidence or plausible language generation.
3. **Operational State Consistency:** AI responses must respect conversational progression (e.g. never telling a customer to check tracking if `TRACKING_ALREADY_CHECKED`).
4. **Safe Clarification Path:** Harmless questions requesting necessary details (e.g. asking which store or order number) are permitted to auto-handle under ambiguity, distinguishing interactive inquiry from ungrounded resolution claims.

---

## 2. Escalation Decision Matrix

| Signal Category | Evaluation Condition | Policy Decision | Sub-Decision | Primary Reason Code | Secondary Reason Codes | Action Taken |
|---|---|:---:|:---:|---|---|---|
| **Response Format** | Empty or < 5 characters | `HUMAN_REVIEW` | `ESCALATE` | `MALFORMED_RESPONSE` | — | Reroute to human queue |
| **Evidence Validation** | Invented document IDs present | `HUMAN_REVIEW` | `ESCALATE` | `INVALID_EVIDENCE_IDS` | — | Immediate human escalation |
| **Grounding Contradiction** | Contradicted claims > 0 | `HUMAN_REVIEW` | `ESCALATE` | `CONTRADICTED_RESPONSE` | `GROUNDING_FAILURE` | Immediate human escalation |
| **Grounding Verification** | Grounded = False or ungrounded claims remain | `HUMAN_REVIEW` | `ESCALATE` | `GROUNDING_FAILURE` | `UNSUPPORTED_CURRENT_ACTION` | Immediate human escalation |
| **Current Action Assertion** | Reply claims action taken without conv support | `HUMAN_REVIEW` | `ESCALATE` | `UNSUPPORTED_CURRENT_ACTION` | `GROUNDING_FAILURE` | Immediate human escalation |
| **Security Risk** | Intent ∈ `{ACCOUNT_ACCESS_RECOVERY, PAYMENT_AND_BILLING_DISPUTES}` | `HUMAN_REVIEW` | `ESCALATE` | `HIGH_RISK_SECURITY` | — | Transfer to specialist queue |
| **Fraud Concern** | Customer text mentions `{fraud, scam, police, hacked, stolen}` | `HUMAN_REVIEW` | `ESCALATE` | `FRAUD_CONCERN` | `HIGH_RISK_SECURITY` | Transfer to investigation queue |
| **Domain Scope** | Classification = `OUT_OF_SCOPE` | `HUMAN_REVIEW` | `ESCALATE` | `OUT_OF_SCOPE` | — | Escalated to retail triage |
| **State: Tracking** | State = `TRACKING_ALREADY_CHECKED` & reply says "check tracking" | `HUMAN_REVIEW` | `ESCALATE` | `INCONSISTENT_WITH_STATE` | — | Block redundant redirect |
| **State: Carrier** | State = `CARRIER_ALREADY_CONTACTED` & reply says "contact carrier" | `HUMAN_REVIEW` | `ESCALATE` | `INCONSISTENT_WITH_STATE` | — | Block redundant redirect |
| **State: Details** | State = `DETAILS_ALREADY_PROVIDED` & reply asks for same details | `HUMAN_REVIEW` | `ESCALATE` | `INCONSISTENT_WITH_STATE` | — | Block redundant prompt |
| **State: Window** | State = `WAITING_WINDOW_EXCEEDED` & reply merely says "wait" | `HUMAN_REVIEW` | `ESCALATE` | `INCONSISTENT_WITH_STATE` | — | Block unhelpful delay |
| **Retrieval Evidence** | Top evidence score < 0.45 (Resolution response) | `HUMAN_REVIEW` | `ESCALATE` | `INSUFFICIENT_EVIDENCE` | — | Reroute due to low retrieval score |
| **Ambiguity / Unknown** | Primary Intent = `UNKNOWN` & reply is safe clarification | `AUTO_HANDLE` | `CLARIFY` | `SAFE_CLARIFICATION` | — | Send clarification question |
| **Ambiguity / Unknown** | Primary Intent = `UNKNOWN` & reply attempts resolution | `HUMAN_REVIEW` | `ESCALATE` | `AMBIGUOUS_CLASSIFICATION` | — | Reroute to human queue |
| **Low Confidence** | Classifier Confidence < 0.70 & reply is safe clarification | `AUTO_HANDLE` | `CLARIFY` | `SAFE_CLARIFICATION` | `LOW_CLASSIFICATION_CONFIDENCE` | Send clarification question |
| **Low Confidence** | Classifier Confidence < 0.70 & reply attempts resolution | `HUMAN_REVIEW` | `ESCALATE` | `LOW_CLASSIFICATION_CONFIDENCE` | — | Reroute to human queue |
| **All Gates Passed** | Grounded + Consistent + Normal Confidence + Non-risky | `AUTO_HANDLE` | `RESOLVE` | `SAFE_TO_AUTO_HANDLE` | — | Dispatch automated reply |

---

## 3. Configuration Mapping (`configs/escalation.yaml`)

All logic adheres strictly to parameters declared in `configs/escalation.yaml`:
```yaml
classification:
  min_confidence: 0.70
  allow_ambiguous_clarification: true
  block_out_of_scope: true

security_and_fraud:
  high_risk_intents:
    - "ACCOUNT_ACCESS_RECOVERY"
    - "PAYMENT_AND_BILLING_DISPUTES"
  risk_keywords:
    - "fraud"
    - "scam"
    - "police"
    - "hacked"
    - "unauthorized"
    - "stolen"

grounding:
  require_grounded: true
  max_contradicted_claims: 0
  max_unsupported_claims: 0
  block_unsupported_current_actions: true

retrieval:
  min_top_evidence_score: 0.45
  require_evidence_for_resolution: true
```
