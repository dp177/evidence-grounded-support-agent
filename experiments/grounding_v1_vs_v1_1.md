# Phase 9 vs Phase 9.1: Grounding Verification Tightening Comparison

This document provides a comparative analysis of the baseline Phase 9 grounding verifier (**Grounding V1**) versus the tightened Phase 9.1 verifier and generator guardrails (**Grounding V1.1**) across the identical 40 stratified development cases (`RANDOM_SEED=42`, excluding Golden V1).

---

## 1. Summary Metrics Comparison

| Metric | Phase 9 (Grounding V1) | Phase 9.1 (Grounding V1.1) | Delta / Improvement |
|---|:---:|:---:|:---:|
| **Cases Evaluated** | 40 | 40 | Identical dev cohort |
| **Grounded on First Attempt** | 28 (70.0%) | **35 (87.5%)** | **+17.5%** |
| **Passed After Revision** | 9 (22.5%) | 5 (12.5%) | -10.0% (fewer needed revision) |
| **Failed Grounding → Human Review** | 3 (7.5%) | **0 (0.0%)** | **-7.5% (Zero hard failures)** |
| **Escalated by Revision Loop** | 0 (0.0%) | 0 (0.0%) | 0% |
| **Total Requiring Human Review** | 3 (7.5%) | **0 (0.0%)** | **-7.5%** |
| **Revision Loop Trigger Rate** | 12 (30.0%) | **5 (12.5%)** | **-17.5% (60% fewer revisions)** |
| **Avg. Revision Attempts per Case** | 0.47 | **0.17** | **-63.8% reduction in latency/calls** |
| **Average Final Grounding Score** | 0.938 | **1.000** | **+0.062** |
| **Invented Evidence IDs Detected** | 0 | 0 | 100% genuine evidence IDs |

---

## 2. False Approvals Fixed

In Phase 9, historical support evidence was frequently promoted into assertive current-case actions or promises without confirmation in the current conversation. Phase 9.1 eliminated these false approvals:

### A. Promotion of Historical Safe-Place Evidence to Current Promises (Case `1519816`)
- **Customer:** *"I got no options on the matter. They said it will be delivered tomorrow even though your policy says delivery till 9pm"*
- **Phase 9 (False Approval):**
  > Draft: *"We apologize for the inconvenience. Since our delivery window has been exceeded, we can offer you safe place options for delivery tomorrow. Please visit this link to explore your options: <URL>"*
  > *Decision:* PASSED (Score: 1.0) — Historical evidence of safe-place options was incorrectly promoted into *"we can offer you safe place options for delivery tomorrow"*.
- **Phase 9.1 (Fixed):**
  > Draft: *"I understand that you're concerned about the delivery time, and I'm happy to help. According to our policy, delivery should be made by 9pm. Since the waiting window has exceeded, I recommend reaching out to us directly so we can explore available options with you. We can discuss safe place options or other alternatives to ensure your package is delivered at a time that suits you. Please let me know if you'd like to proceed."*
  > *Decision:* Grounded in `retrieval_doc_0114711` and `retrieval_doc_0003756` as general guidance, avoiding unauthorized delivery promises.

### B. Invention of Current Action Taken (Case `1412522`)
- **Customer:** *"can't answer in 140 characters. Can you call me at number in my account - __email__"*
- **Phase 9 (Hallucinated Action Failure):**
  > Draft: *"I've sent you a secure message with a call link. Please click on it to initiate a call."*
  > *Decision:* FAILED after 2 revision attempts — Escalated to human because the model kept asserting outbound messaging actions.
- **Phase 9.1 (Fixed):**
  > Final Reply: *"Thank you for reaching out about your account issue. You can contact our customer service team via email or through our website. If you'd like to speak with someone directly, you may explore our chat or phone support options in your account. Please note that we consider personal details to be sensitive information and cannot request them."*
  > *Decision:* PASSED (Score: 1.0) — Properly transformed into safe channel guidance (`HISTORICAL_EVIDENCE_SUPPORTED`) without claiming that an outbound call or message was already dispatched.

### C. Asserting Action on Fraud Claims (Case `434623`)
- **Customer:** *"has done fraud with me. Have all the written proofs Please take action against them!!!"*
- **Phase 9 (Failed Revision):**
  > Draft claimed affirmative stances on fraud without evidence; revision was unable to find evidence and failed to human review.
- **Phase 9.1 (Fixed):**
  > Revision safely converted the response into an information request:
  > *"I'm sorry to hear that you've been a victim of fraud. To assist you further, I'll need you to provide the written proofs of the incident. Please share them with me, and I'll guide you through the next steps."*
  > *Decision:* PASSED (Score: 1.0).

---

## 3. False Rejections Analysis

Under Phase 9.1, tightening the deterministic current-action patterns reduced unwarranted rejections while maintaining safety:
- **Phase 9 Potential False Rejections:** 8 cases (rejections triggered on benign customer service courtesies).
- **Phase 9.1 Potential False Rejections:** 5 cases.
  - Case `1191342`: Draft included *"However, I couldn't confirm if the prices are $30 less as mentioned in the previous sale."* The verifier flagged this uncertainty hedge as unsupported. Revision replaced it cleanly with general deal guidance.
  - Case `1204948`: Draft included *"I'd like to offer an alternative solution. Please fill out this form..."* Flagged due to the phrase *"offer an alternative solution"*. Revision replaced it with *"To better assist you, please fill out this form: <URL> so we can investigate your issue further"*, which passed immediately.
  - Case `872275`: Draft included *"I've checked on your case, and I'll make sure to escalate this to a specialist for you."* The deterministic check correctly caught *"I've checked on your case"* because the agent had not actually inspected the account. Revision cleanly replaced this with a factual request for details.

In each instance, the revision loop successfully converted the rejected statement into a safe, compliant instruction without dead-ending into human escalation.

---

## 4. Representative Claim-Source Classification Examples

Every atomic claim in Phase 9.1 is explicitly categorized into its evidence source:

### Example 1: `CURRENT_CONVERSATION_SUPPORTED`
- **Context/Message:** Customer states *"Amazon emailed me saying my refund was issued."*
- **Generated Claim:** *"Your refund has been issued."*
- **Source Type:** `CURRENT_CONVERSATION_SUPPORTED`
- **Support Status:** `SUPPORTED`
- **Evidence IDs:** `["CURRENT_CONVERSATION"]`
- **Reason:** Explicitly established in the active customer conversation; permissible to acknowledge.

### Example 2: `HISTORICAL_EVIDENCE_SUPPORTED` (Safe Generalization)
- **Historical Evidence:** Document `retrieval_doc_003` states *"Support can be reached by phone."*
- **Generated Claim:** *"You can contact support by phone."*
- **Source Type:** `HISTORICAL_EVIDENCE_SUPPORTED`
- **Support Status:** `SUPPORTED`
- **Evidence IDs:** `["retrieval_doc_003"]`
- **Reason:** Permissible general support channel guidance derived from historical precedent.

### Example 3: `UNSUPPORTED` (Historical Promotion Blocked)
- **Historical Evidence:** Document `retrieval_doc_002` states *"Customer was refunded once the item was inspected."*
- **Generated Claim:** *"Your refund has been issued."*
- **Source Type:** `UNSUPPORTED`
- **Support Status:** `UNSUPPORTED`
- **Evidence IDs:** `[]`
- **Risk Flag:** `Unsupported current action/promise: 'Your refund has been' not confirmed in current conversation`
- **Reason:** Historical evidence demonstrates past precedent, not that the current user's refund was issued.

### Example 4: `BOTH`
- **Customer Message:** *"I am waiting for my delivery, order #123."*
- **Historical Evidence:** `retrieval_doc_0114711` discusses deliveries delayed past 9 PM.
- **Generated Claim:** *"Since delivery is expected by 9pm, you may reach out directly to check options for order #123."*
- **Source Type:** `BOTH`
- **Support Status:** `SUPPORTED`
- **Evidence IDs:** `["CURRENT_CONVERSATION", "retrieval_doc_0114711"]`

---

## 5. Remaining Failure Modes & Limitations

1. **Overly Cautious Revisions on Complex Cases:**
   In rare multi-turn cases (e.g. `434623`), the model required two revision attempts to fully strip out proactive claims before adopting a strictly safe informational stance.
2. **Generic URL Placeholders:**
   Historical evidence frequently contains `<URL>` tokens. The generator preserves these placeholders accurately, but runtime deployment will require dynamic link hydration from live Amazon service catalogs.
3. **Absence of Tool State Grounding:**
   The current pipeline evaluates conversational context and retrieval text. It does not yet connect to live CRM database lookups (e.g., verifying actual order tracking APIs), meaning all current-action confirmations must reside in the customer conversation thread.

---

## 6. Final Decision

### **Decision: `USE_GROUNDING_V1_1`**

**Justification:**
1. **Higher First-Pass Accuracy (87.5% vs 70.0%):** Prompt constraints in `prompts/response_generation_v1.md` prevent the generator from hallucinating current actions up front.
2. **Zero Hard Failures (0.0% vs 7.5%):** All 40 development cases successfully produced grounded, compliant responses (35 on attempt 0, 5 on attempt 1/2).
3. **63.8% Reduction in Revision Overhead:** Average revision attempts dropped from 0.47 to 0.17, drastically reducing LLM inference costs and response latency.
4. **Deterministic Protection Against Current-Case Promotion:** Strict regex checks deterministically block high-risk phrases (*"We've received..."*, *"We can offer you..."*, *"Your refund is..."*) unless explicitly verified by the current conversation.
5. **Full Regression Suite Verified:** All 135 unit, integration, and regression tests pass cleanly in `pytest`.
