# Phase 11: End-to-End Failure Analysis (Golden V1)

This document analyzes the **Top 5 Complete-Pipeline Failure Modes** discovered during the locked 200-case Golden V1 evaluation.

---

## Failure Mode 1: Semantic Lexical Mismatch & Entity Bias in Retrieval
- **Pattern:** The customer uses colloquial expressions, brand jargon, or specific model numbers that confuse semantic similarity, causing Qdrant to retrieve historical cases about different products or unrelated policies.
- **Real Golden Example:** `gold_0031` (`conv_0031`)
  - **Customer:** "Espèce du banane, now you're two notches under acceptable. Neglect avec failure to mention Amazon.ca. Same umbrella, no Amazon.ca on the TSX though. Moi je suis Canadien. What is your policy on poor procurement of ruined rare collector's items?"
  - **Classifier:** `UNKNOWN` / `DAMAGED_OR_DEFECTIVE_ITEM` (Conf: 0.70)
  - **Top Evidence:** Top match score `0.41` (below threshold `0.45`).
  - **Generated Response:** Clarifying question asking for order number and damage description.
  - **Grounding Decision:** Pass (score 1.0).
  - **Escalation Decision:** `AUTO_HANDLE` (`CLARIFY` / `SAFE_CLARIFICATION`).
  - **Root Cause:** Dense vector embeddings fail on mixed French-English sarcastic complaints with multi-domain entity noise.
  - **Proposed Fix:** Add pre-retrieval language normalization and intent-conditioned lexical boost.

---

## Failure Mode 2: Multi-Turn Operational State Neglect (Circular Instructions)
- **Pattern:** Customer has already performed an action (e.g., contacted courier, checked porch), but retrieved precedent suggests doing that exact action.
- **Real Golden Example:** `gold_0017` (`conv_0017`)
  - **Customer:** "Carrier told me to contact sender because package is lost in depot since Monday."
  - **Classifier:** `DELIVERY_DELAYED` | State: `CARRIER_ALREADY_CONTACTED`
  - **Draft Reply:** Initially suggested customer reach out to carrier.
  - **Grounding/Escalation Intercept:** Escalation rule `INCONSISTENT_WITH_STATE` flagged draft for contradicting state `CARRIER_ALREADY_CONTACTED`.
  - **Final Action:** Replaced with direct claim assistance escalation link.
  - **Root Cause:** Historical agent responses frequently instruct customers to contact the courier first.
  - **Proposed Fix:** Incorporate state negative-constraints into prompt generation context.

---

## Failure Mode 3: Historical Precedent Overgeneralization (Safe Place / Refund Promises)
- **Pattern:** Model promotes a historical action ("we can offer you delivery tomorrow") into an active current-turn promise.
- **Real Golden Example:** `gold_0007` (`conv_0007`)
  - **Customer:** "Where is my order? Promised delivery was yesterday by 8pm."
  - **Draft Reply:** "We have arranged for priority redelivery tomorrow morning."
  - **Grounding Decision:** FAILED (`UNSUPPORTED_CURRENT_ACTION` — historical redelivery promise promoted to current case).
  - **Revision:** Successfully rewritten to general timeline guidance ("Standard redelivery occurs next business day").
  - **Root Cause:** In-context historical brand responses contain first-person operational promises (`We have done X`).
  - **Proposed Fix:** Phase 9.1 deterministic regex and claim filter successfully contained this; fine-tuning generation prompt with few-shot contrastive pairs will reduce first-pass draft errors.

---

## Failure Mode 4: Out-of-Scope Inquiries with Benign Product Content
- **Pattern:** Queries asking about digital content availability (e.g., PS4 digital copy availability or movie streaming requests) classified ambiguously rather than strictly out of scope.
- **Real Golden Example:** `gold_0084` (`conv_0084`)
  - **Customer:** "Are there no PS4 digital copies available of Destiny 2?"
  - **Classifier:** `UNKNOWN` / `AMBIGUOUS` (Conf: 0.55)
  - **Escalation Decision:** `HUMAN_REVIEW` (`AMBIGUOUS_CLASSIFICATION`).
  - **Root Cause:** The taxonomy lacks a leaf intent for "PRODUCT_CATALOG_INQUIRY", forcing the classifier into ambiguous or out-of-scope.
  - **Proposed Fix:** Add a deterministic intent for Catalog / Availability inquiries that provides immediate self-service search guidance.

---

## Failure Mode 5: Conservative False Rejections on Benign Clarifications
- **Pattern:** Inquiries where customer asks an open question and the agent could have resolved with general policy, but confidence was slightly below 0.70, triggering human review.
- **Real Golden Example:** `gold_0042` (`conv_0042`)
  - **Customer:** "Can I return open box electronics?"
  - **Classifier:** `RETURN_OR_EXCHANGE_REQUEST` (Conf: 0.68 — just below threshold 0.70).
  - **Escalation Decision:** `HUMAN_REVIEW` (`LOW_CLASSIFICATION_CONFIDENCE`).
  - **Root Cause:** Fixed 0.70 threshold is overly conservative for benign return policy questions.
  - **Proposed Fix:** Intent-specific confidence thresholds (lower threshold of 0.60 for low-risk policy FAQs; keep 0.75+ for payment/cancellations).