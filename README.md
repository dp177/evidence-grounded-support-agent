<p align="center">
  <strong>🛡️ Evidence-Grounded AI Support Agent for @AmazonHelp</strong><br>
  <em>Hiver SDE Intern — Take-Home Assignment</em>
</p>

<p align="center">
  <code>Classification → Retrieval → Generation → Grounding → Safety → Escalation</code>
</p>

---

# 📖 Table of Contents

| # | Chapter | Section |
|---|---------|---------|
| **I** | [**The Problem**](#i-the-problem) | [1.1 Assignment Brief](#11-assignment-brief) · [1.2 Brand Selection](#12-brand-selection-amazonhelp) · [1.3 Operational Definition of "Good"](#13-operational-definition-of-good) · [1.4 What We Chose NOT to Build](#14-what-we-chose-not-to-build) |
| **II** | [**Data & EDA**](#ii-data--eda) | [2.1 Raw Dataset](#21-raw-dataset) · [2.2 EDA Notebook](#22-eda--brand-selection-analysis) · [2.3 Amazon Sub-Corpus](#23-amazon-sub-corpus-extraction) · [2.4 Data Pipeline](#24-data-processing-pipeline) · [2.5 Decision: Why Amazon?](#25-decision-why-amazon) |
| **III** | [**Taxonomy Design**](#iii-taxonomy-design) | [3.1 Intent Discovery](#31-intent-discovery-from-data) · [3.2 Frozen 14-Intent Taxonomy](#32-frozen-14-intent-taxonomy) · [3.3 Areas, States & Outcomes](#33-areas-states--outcomes) · [3.4 Multi-Intent Handling](#34-multi-intent-handling) · [3.5 Key Decisions](#35-taxonomy-decisions) |
| **IV** | [**System Architecture**](#iv-system-architecture) | [4.1 Pipeline Overview](#41-pipeline-overview) · [4.2 Stage 1: Triage](#42-stage-1-semantic-triage--state-extraction) · [4.3 Stage 2: Retrieval](#43-stage-2-hybrid-retrieval-rag--rrf) · [4.4 Stage 3: Generation](#44-stage-3-grounded-generation--nli-verification) · [4.5 Stage 4: Safety Engine](#45-stage-4-deterministic-4-gate-safety-engine) |
| **V** | [**Golden Evaluation Sets**](#v-golden-evaluation-sets) | [5.1 Sampling Strategy](#51-sampling-strategy) · [5.2 32-Column Schema](#52-32-column-annotation-schema) · [5.3 V1 → V2 → V3 Governance](#53-3-generation-benchmark-governance-v1--v2--v3) · [5.4 Dataset Files](#54-dataset-files) |
| **VI** | [**Evaluation Harness**](#vi-evaluation-harness) | [6.1 Metric Contracts](#61-metric-contracts) · [6.2 Graders](#62-grader-modules) · [6.3 LLM-as-Judge](#63-llm-as-judge-rubric) · [6.4 Baselines](#64-baselines) |
| **VII** | [**Results**](#vii-results) | [7.1 Headline Numbers](#71-headline-numbers-golden-v3) · [7.2 Longitudinal Table](#72-longitudinal-benchmark-v1--v2--v3) · [7.3 V3 Challenge Breakdown](#73-v3-challenge-group-breakdown) · [7.4 Response Quality](#74-response-quality-llm-judge) |
| **VIII** | [**Failure Analysis**](#viii-failure-analysis) | [8.1 Top 5 Failure Modes](#81-top-5-failure-modes) · [8.2 What Is Misleading](#82-what-is-misleading-about-my-headline-number) |
| **IX** | [**Decision Log**](#ix-decision-log) | [15 Non-Obvious Engineering Decisions](#ix-decision-log) |
| **X** | [**Policy Iterations**](#x-policy-iterations) | [10.1 Iteration 1 (V1 → V2)](#101-policy-iteration-1-v1--v2) · [10.2 Iteration 2 (V2 → V3)](#102-policy-iteration-2-v2--v3) |
| **XI** | [**Productionizing on Hiver**](#xi-productionizing-on-hiver) | [11.1 Integration Plan](#111-native-hiver-integration) · [11.2 Week-2 Roadmap](#112-week-2-technical-roadmap) |
| **XII** | [**Reproducibility**](#xii-reproducibility) | [12.1 Quick Start](#121-quick-start-reproduce-in-15-minutes) · [12.2 Environment](#122-environment) · [12.3 Repository Map](#123-repository-map) · [12.4 Test Suite](#124-test-suite) |

---

# I. The Problem

## 1.1 Assignment Brief

> **What we are testing:** whether you can turn a messy real-world dataset into a working AI system **and prove it works**. The proof is worth more than the system.

Build an AI support agent for one brand from the [Customer Support on Twitter](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter) dataset (~3M tweets) that can:

1. **Classify** each incoming customer message into intents you define from the data.
2. **Draft a reply** grounded in how that brand has historically resolved similar issues.
3. **Decide** whether the message should be auto-handled or escalated to a human — with a stated reason.

## 1.2 Brand Selection: @AmazonHelp

We selected **Amazon** from dozens of available brands. The selection process is documented in the EDA notebook ([`notebooks/Hiver_Brand_Selection_Analysis.ipynb`](notebooks/Hiver_Brand_Selection_Analysis.ipynb)).

**Why Amazon?**
| Criterion | Amazon | Typical Brand |
|-----------|--------|---------------|
| Thread volume | ~150k threads | 5k–30k |
| Topic diversity | Delivery, returns, billing, security, digital, Prime | 1–3 narrow topics |
| Multi-turn depth | 43% single, 36% two-turn, 21% ≥3 turns | Mostly single-turn |
| Escalation complexity | Account takeover, carrier misconduct, fraud signals | Rarely safety-critical |
| Resolution patterns | Rich, diverse historical responses | Templated FAQ |

**Decision:** Amazon provides the widest intent surface, deepest multi-turn complexity, and most challenging safety requirements — exactly the stress test needed to prove the system works.

## 1.3 Operational Definition of "Good"

Within Hiver's product philosophy of empowering human teams with reliable AI, an autonomous support agent succeeds if and only if it satisfies four non-negotiable operational invariants:

1. **Factual Grounding over Fluency** — Every assertion must be verifiable against retrieved historical brand resolutions or current conversation state. Fabricating a carrier status or claiming "I processed your refund" is an unacceptable failure.

2. **High-Confidence Intent & State Triage** — Correctly parsing multi-intent issues and extracting customer progress (e.g., tracking already checked, carrier already contacted) to avoid repetitive, frustrating interactions.

3. **Safety-First Escalation** — Account hijacking, carrier misconduct, and repeated failed support contacts **must** route to human specialists with structured context — regardless of model confidence.

4. **Queue Protection** — Routine, unambiguous issues (delivery updates, return windows, subscription cancellations) must auto-resolve cleanly without flooding Hiver's shared inboxes.

## 1.4 What We Chose NOT to Build

| Excluded Capability | Reason |
|---------------------|--------|
| **Autonomous action execution** (refunds, address changes) | Identity cannot be verified on public Twitter. Executing unverified actions invites fraud. |
| **Monolithic single-prompt LLM** | Empirical testing yielded 14.5% capability hallucination rate and unreliable safety gates. |
| **Canned FAQ template matching** | Real support is conversational; static templates fail on multi-turn context. |
| **Fake human handoff simulation** | Claiming "I've transferred you to a specialist" when no handoff occurs is dishonest. |

---

# II. Data & EDA

## 2.1 Raw Dataset

- **Source:** [Customer Support on Twitter (Kaggle)](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter)
- **Size:** ~3 million tweets across dozens of brands
- **Format:** Tweet-level rows with `author_id`, `text`, `in_response_to_tweet_id`, `created_at`
- **Location:** `data/raw/` (not committed due to size; download from Kaggle)

## 2.2 EDA & Brand Selection Analysis

📓 **Notebook:** [`notebooks/Hiver_Brand_Selection_Analysis.ipynb`](notebooks/Hiver_Brand_Selection_Analysis.ipynb)

This notebook performs:
- Brand frequency distribution analysis
- Thread-depth distribution per brand
- Topic diversity scoring (unique trigram entropy)
- Multi-turn conversation reconstruction
- Final brand selection justification

**Key EDA findings:**
- Amazon has the highest thread volume (~150k) with the broadest intent surface
- 21% of Amazon threads are 3+ turns deep — critical for testing state consistency
- Amazon support responses contain rich, specific resolution language (not just "DM us")

## 2.3 Amazon Sub-Corpus Extraction

**Script:** [`scripts/validate_data.py`](scripts/validate_data.py)

From the raw 3M tweets, we filter and reconstruct Amazon-specific threaded conversations:
- Filter for `@AmazonHelp` brand author IDs
- Reconstruct parent-child tweet chains into multi-turn threads
- Flatten into customer/brand role-tagged transcripts
- **Output:** `data/processed/amazon_support_cases.parquet` (~190 MB, ~150k cases)

## 2.4 Data Processing Pipeline

| Step | Script | Input | Output |
|------|--------|-------|--------|
| 1. Validate & clean | `scripts/validate_data.py` | Raw CSV | `data/processed/amazon_support_cases.parquet` |
| 2. Intent discovery sampling | `scripts/build_intent_discovery.py` | Parquet | `data/processed/intent_discovery_cases.parquet` |
| 3. Broad area clustering | `scripts/discover_broad_areas.py` | Discovery cases | `data/processed/intent_discovery_clusters.jsonl` |
| 4. Hierarchical intent discovery | `scripts/discover_hierarchical_intents.py` | Clusters | `data/processed/hierarchical_sub_intents.jsonl` |
| 5. Taxonomy review & freeze | `scripts/build_taxonomy_review.py` | Sub-intents | `configs/taxonomy_v1.yaml` (FROZEN) |
| 6. Retrieval document building | `scripts/build_retrieval_documents.py` | Parquet + taxonomy | `data/processed/retrieval_documents.parquet` |
| 7. Vector index creation | `scripts/build_qdrant_index.py` | Retrieval docs | `artifacts/retrieval/qdrant/` |
| 8. Golden set construction | `scripts/build_golden_set.py` | Parquet | `data/golden/golden_v1_assistant_adjudicated.csv` |

## 2.5 Decision: Why Amazon?

> **Decision #1 of 15:** Amazon selected for support variety, multi-turn depth, and safety-critical edge cases (account security, carrier misconduct). Most other brands in the dataset have narrow, repetitive issue spaces that wouldn't stress-test escalation logic.

---

# III. Taxonomy Design

## 3.1 Intent Discovery from Data

We did not pre-define intents. We discovered them from the data using a bottom-up process:

1. **Broad Area Clustering** (`scripts/discover_broad_areas.py`) — LLM-assisted semantic clustering over 5,000 sampled cases identified 6 macro operational areas.
2. **Hierarchical Sub-Intent Discovery** (`scripts/discover_hierarchical_intents.py`) — Within each area, further clustering decomposed themes into fine-grained intents.
3. **Taxonomy Review & Boundary Testing** (`scripts/build_taxonomy_review.py`) — LLM-generated boundary cases for each candidate intent; ambiguous or overlapping intents were merged or split.
4. **Human Freeze** — Final 14-intent taxonomy locked in `configs/taxonomy_v1.yaml` with status `FROZEN`.

## 3.2 Frozen 14-Intent Taxonomy

**Config:** [`configs/taxonomy_v1.yaml`](configs/taxonomy_v1.yaml)

| Area | Intents |
|------|---------|
| **Delivery & Fulfillment** | `WHERE_IS_MY_ORDER` · `DELIVERY_DELAYED` · `MARKED_DELIVERED_NOT_RECEIVED` · `CARRIER_FEEDBACK_AND_INSTRUCTIONS` |
| **Returns & Replacements** | `DAMAGED_OR_DEFECTIVE_ITEM` · `WRONG_ITEM_RECEIVED` · `RETURN_PICKUP_ISSUE` |
| **Refunds & Billing** | `REFUND_STATUS_INQUIRY` · `UNRECOGNIZED_OR_DUPLICATE_CHARGE` |
| **Order Management** | `CANCEL_ORDER_REQUEST` · `MODIFY_ORDER_DETAILS` |
| **Digital Services & Prime** | `PRIME_MEMBERSHIP_MANAGEMENT` · `DIGITAL_CONTENT_ACCESS` |
| **Account Access & Security** | `ACCOUNT_LOGIN_ISSUES` |

Each intent has a formal definition in the YAML config that anchors classifier behavior.

## 3.3 Areas, States & Outcomes

We deliberately separate three orthogonal concepts:

| Concept | Definition | Values |
|---------|------------|--------|
| **Status** | Is this a classifiable support issue? | `NORMAL`, `AMBIGUOUS`, `OUT_OF_SCOPE` |
| **State** | What has already happened in the conversation? | `INITIAL_INQUIRY`, `TRACKING_ALREADY_CHECKED`, `CARRIER_ALREADY_CONTACTED`, `DETAILS_ALREADY_PROVIDED`, `WAITING_WINDOW_EXCEEDED` |
| **Outcome** | How should/did the case end? | `RESOLVED_CLOSURE`, `ESCALATED_HUMAN_TIER2`, `DEFLECTED_SELF_SERVICE`, `CONCESSION_ISSUED`, `ABANDONED_UNRESPONSIVE` |

**Decision:** Separating intent (what), state (context), and outcome (disposition) prevents combinatorial label explosion and keeps each classification surface small and measurable.

## 3.4 Multi-Intent Handling

Multi-intent is handled as **multi-label classification**, not a new combinatorial intent. A customer saying *"My item arrived broken AND I haven't received my refund yet"* is tagged with both `DAMAGED_OR_DEFECTIVE_ITEM` and `REFUND_STATUS_INQUIRY`, with a single `primary_intent` denoting the dominant driver.

**Decision:** This preserves taxonomy coverage and interpretability. Creating combo intents like `DAMAGED_AND_REFUND` would cause exponential label explosion.

## 3.5 Taxonomy Decisions

> **Decision #2:** Freeze 14 leaf intents — small enough to be measurable, broad enough to cover 95%+ of Amazon support traffic.
>
> **Decision #3:** Multi-intent is multi-label, not a new combinatorial intent.
>
> **Decision #4:** Intent / state / outcome separated into orthogonal axes.
>
> **Decision #5:** State keyed by `conversation_id` — extracted from the live thread, not from historical memory.

---

# IV. System Architecture

## 4.1 Pipeline Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                    INCOMING CUSTOMER MESSAGE                         │
│              (+ conversation history if multi-turn)                  │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 1: SEMANTIC TRIAGE & STATE EXTRACTION                         │
│  ┌─────────────────────┐  ┌────────────────────────────────────┐    │
│  │ LLM Classifier       │  │ Deterministic StateExtractor       │    │
│  │ → status             │  │ → conversation_states              │    │
│  │ → areas              │  │   (TRACKING_ALREADY_CHECKED,       │    │
│  │ → intents (multi)    │  │    CARRIER_ALREADY_CONTACTED, ...) │    │
│  │ → primary_intent     │  │                                    │    │
│  └─────────────────────┘  └────────────────────────────────────┘    │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 2: HYBRID EVIDENCE RETRIEVAL (RAG + RRF)                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │ Dense Embeddings  │  │ Sparse BM25      │  │ RRF Fusion       │   │
│  │ (MiniLM-L6-v2)   │  │ (lexical match)  │  │ (k=60) → Top-5  │   │
│  │ → Top-30          │  │ → Top-30         │  │                  │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
│  ⚠️ Hard gating: zero retrieval on AMBIGUOUS / OUT_OF_SCOPE         │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 3: GROUNDED GENERATION + NLI VERIFICATION LOOP                │
│  ┌───────────────────┐  ┌──────────────────────────────────────┐    │
│  │ LLM Generator      │  │ Claim-Level NLI Grounding Grader    │    │
│  │ → draft response   │  │ → decompose into atomic claims       │    │
│  │                     │  │ → verify each vs evidence + context  │    │
│  │                     │  │ → if CONTRADICTED → revise (max 2)   │    │
│  │                     │  │ → if still fails → GROUNDING_FAILURE │    │
│  └───────────────────┘  └──────────────────────────────────────┘    │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  STAGE 4: DETERMINISTIC 4-GATE SAFETY ESCALATION ENGINE              │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ Gate 1a: Triage Gating (confidence < 0.55 → escalate)       │    │
│  │ Gate 1b: High-Risk Overrides (security/misconduct regex)    │    │
│  │ Gate 2:  NLI Grounding Failure → escalate                   │    │
│  │ Gate 3:  State Inconsistency → escalate                     │    │
│  │ Gate 4:  Out-of-Scope → polite auto-decline (no human cost) │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────┬───────────────────────────────────────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
       ✅ AUTO-HANDLE     🚨 ESCALATE TO HUMAN
       (grounded reply)   (with structured reason)
```

## 4.2 Stage 1: Semantic Triage & State Extraction

**Source files:**
- [`src/support_agent/classification/llm_classifier.py`](src/support_agent/classification/llm_classifier.py) — Zero-shot LLM classifier producing status, areas, intents, and primary intent
- [`src/support_agent/classification/state_extractor.py`](src/support_agent/classification/state_extractor.py) — Deterministic regex-based state extraction from dialogue history
- [`prompts/classification_v2.md`](prompts/classification_v2.md) — Structured classification prompt

**What it does:**
1. Parses the customer message (and multi-turn context) into a structured classification output
2. Determines `status` (NORMAL / AMBIGUOUS / OUT_OF_SCOPE)
3. Assigns one or more `areas` and `intents` from the frozen taxonomy
4. Selects the `primary_intent` (dominant contact driver)
5. In parallel, the `StateExtractor` inspects dialogue history for progress markers (e.g., customer says "I already checked the tracking" → `TRACKING_ALREADY_CHECKED`)

**Baselines also available:**
- [`src/support_agent/classification/majority.py`](src/support_agent/classification/majority.py) — Majority-class baseline
- [`src/support_agent/classification/tfidf_classifier.py`](src/support_agent/classification/tfidf_classifier.py) — TF-IDF + logistic regression baseline

## 4.3 Stage 2: Hybrid Retrieval (RAG + RRF)

**Source files:**
- [`src/support_agent/retrieval/embeddings.py`](src/support_agent/retrieval/embeddings.py) — `all-MiniLM-L6-v2` embedding engine (384-dim, runs locally)
- [`src/support_agent/retrieval/vector_store.py`](src/support_agent/retrieval/vector_store.py) — Qdrant vector store (local mode)
- [`src/support_agent/retrieval/lexical_retriever.py`](src/support_agent/retrieval/lexical_retriever.py) — BM25 sparse retrieval
- [`src/support_agent/retrieval/reranker.py`](src/support_agent/retrieval/reranker.py) — Reciprocal Rank Fusion (RRF) combining dense + sparse
- [`src/support_agent/retrieval/context_selector.py`](src/support_agent/retrieval/context_selector.py) — Evidence context selection and formatting
- [`src/support_agent/retrieval/conversation_builder.py`](src/support_agent/retrieval/conversation_builder.py) — Multi-turn conversation reconstruction
- [`src/support_agent/retrieval/document_builder.py`](src/support_agent/retrieval/document_builder.py) — Retrieval document preparation from raw corpus
- **Config:** [`configs/retrieval.yaml`](configs/retrieval.yaml) · [`configs/reranking.yaml`](configs/reranking.yaml)

**RRF Formula:**
```
RRF_Score(d) = Σ  1 / (k + Rank_m(d))    where m ∈ {Dense, BM25}, k = 60
```

**Why hybrid?**
- **Dense** captures semantic paraphrasing (e.g., "my package is lost" ≈ "delivery not received")
- **BM25** handles exact lexical matches (order IDs like `111-7654321-0987654`, carrier codes like `TBA...`)
- Neither alone is sufficient; RRF fuses both ranking signals

**Hard gating rule:** Zero retrieval candidates for AMBIGUOUS and OUT_OF_SCOPE statuses. Retrieving knowledge for vague queries forces irrelevant context into prompt windows, inducing hallucinated assumptions.

## 4.4 Stage 3: Grounded Generation & NLI Verification

**Source files:**
- [`src/support_agent/generation/response_generator.py`](src/support_agent/generation/response_generator.py) — LLM-based response generation conditioned on conversation + evidence
- [`src/support_agent/generation/revise_response.py`](src/support_agent/generation/revise_response.py) — Revision loop for ungrounded responses
- [`src/support_agent/grounding/grounding_checker.py`](src/support_agent/grounding/grounding_checker.py) — Claim-level NLI grounding verification
- **Prompt:** [`prompts/response_generation_v1.md`](prompts/response_generation_v1.md) · [`prompts/grounding_v1.md`](prompts/grounding_v1.md)

**Grounding verification loop:**
1. Response is decomposed into discrete atomic factual propositions
2. Each proposition is verified against conversation context + retrieved evidence via NLI
3. If any claim is `CONTRADICTED` or unsupported → revision loop (max 2 retries)
4. If verification still fails after 2 retries → `GROUNDING_FAILURE` → safe escalation

**Decision:** Two-strike revision limit. Caps latency tail; if NLI fails twice, the underlying retrieved evidence is simply insufficient — more retries won't help.

## 4.5 Stage 4: Deterministic 4-Gate Safety Engine

**Source files:**
- [`src/support_agent/escalation/decision.py`](src/support_agent/escalation/decision.py) — Main escalation decision orchestrator
- [`src/support_agent/escalation/escalation_policy.py`](src/support_agent/escalation/escalation_policy.py) — Policy rules from config
- [`src/support_agent/escalation/high_risk.py`](src/support_agent/escalation/high_risk.py) — High-risk pattern detection (regex + heuristics)
- **Config:** [`configs/escalation.yaml`](configs/escalation.yaml)

**Gate cascade:**

| Gate | Name | Trigger | Reason Code |
|------|------|---------|-------------|
| **1a** | Triage Gating | Status unclassifiable or confidence < τ=0.55 | `LOW_CLASSIFICATION_CONFIDENCE` |
| **1b** | High-Risk Overrides | Account compromise, carrier misconduct, repeated failed contacts (≥3) | `ACCOUNT_SECURITY_COMPROMISE`, `CARRIER_MISCONDUCT_AND_REFUSAL`, `REPEATED_FAILED_SUPPORT_ATTEMPTS` |
| **2** | Grounding Fail-Safe | NLI loop exhausted without 100% verification | `GROUNDING_FAILURE` |
| **3** | State Inconsistency | Draft asks customer to repeat a completed action | `INCONSISTENT_WITH_STATE` |
| **4** | Out-of-Scope | Non-brand queries (math, general knowledge, competitors) | Polite auto-decline — **no human queue cost** |

**Decision:** Escalation is **never** left to LLM discretion. Deterministic Python gates ensure safety compliance doesn't depend on prompt wording or model temperature.

**17 Reason Codes:** `SAFE_TO_AUTO_HANDLE`, `SAFE_CLARIFICATION`, `ACCOUNT_SECURITY_COMPROMISE`, `REPEATED_FAILED_SUPPORT_ATTEMPTS`, `CARRIER_MISCONDUCT_AND_REFUSAL`, `GROUNDING_FAILURE`, `CONTRADICTED_RESPONSE`, `UNSUPPORTED_CURRENT_ACTION`, `HIGH_RISK_SECURITY`, `FRAUD_CONCERN`, `OUT_OF_SCOPE`, `AMBIGUOUS_CLASSIFICATION`, `LOW_CLASSIFICATION_CONFIDENCE`, `INSUFFICIENT_EVIDENCE`, `INCONSISTENT_WITH_STATE`, `MALFORMED_RESPONSE`, `INVALID_EVIDENCE_IDS`

---

# V. Golden Evaluation Sets

## 5.1 Sampling Strategy

Instead of uniform random sampling (which yields 85% routine delivery delays), we used **stratified adversarial sampling**:

- **Turn-depth stratification:** single-turn (43%), two-turn (36%), multi-turn ≥3 (21%)
- **Stress-scenario over-indexing:** account takeovers, carrier abuse, repeated transfers, out-of-scope queries
- **Multi-intent enrichment:** 10% of cases have composite issues
- **Token Jaccard similarity** between V1/V2/V3 is < 0.60 across all records, confirming independence

## 5.2 32-Column Annotation Schema

Every case is adjudicated across 7 foundational ground-truth fields:

| # | Field | Values | Purpose |
|---|-------|--------|---------|
| 1 | `human_status` | `NORMAL`, `AMBIGUOUS`, `OUT_OF_SCOPE` | Is this a classifiable support issue? |
| 2 | `human_areas` | 7 macro areas (pipe-delimited) | Operational routing area |
| 3 | `human_intents` | Multi-label from 14-intent taxonomy (pipe-delimited) | Underlying customer problems |
| 4 | `human_primary_intent` | Single intent | Dominant contact driver |
| 5 | `human_states` | 5 conversation states (pipe-delimited) | Customer progress markers |
| 6 | `human_should_escalate` | `1` or `0` | Binary ground truth |
| 7 | `human_escalation_reason` | Taxonomy reason code | Why escalation is needed |

Full schema documentation: [`data/golden/README.md`](data/golden/README.md)

## 5.3 3-Generation Benchmark Governance (V1 → V2 → V3)

| Generation | Cases | Purpose | Key Finding | Status |
|------------|-------|---------|-------------|--------|
| **V1** | 200 | Diagnostic baseline | 60% unsafe auto-handle rate on edge cases | 🔒 LOCKED |
| **V2** | 200 | Test Policy Iteration 1 | Over-escalation on out-of-scope (40% false-positive escalation rate) | 🔒 LOCKED |
| **V3** | 200 | Final frozen independent benchmark | Evaluated blindly with zero post-hoc tuning | 🔒 LOCKED |

**Why 3 generations?** Modifying benchmarks after seeing failures turns evaluation into an unscientific moving target. Each generation tests whether improvements **generalize** to unseen wording and scenarios.

## 5.4 Dataset Files

| File | Description |
|------|-------------|
| [`data/golden/golden_v1_assistant_adjudicated.csv`](data/golden/golden_v1_assistant_adjudicated.csv) | Golden V1 (200 cases) |
| [`data/golden/golden_v2_assistant_adjudicated.csv`](data/golden/golden_v2_assistant_adjudicated.csv) | Golden V2 (200 cases) |
| [`data/golden/golden_v3_assistant_adjudicated.csv`](data/golden/golden_v3_assistant_adjudicated.csv) | Golden V3 (200 cases, SHA-256: `4049dfe0...`) |
| [`data/golden/ANNOTATION_INSTRUCTIONS.md`](data/golden/ANNOTATION_INSTRUCTIONS.md) | Labeling instructions |
| [`data/golden/LOCKED.md`](data/golden/LOCKED.md) | Dataset lock governance record |

---

# VI. Evaluation Harness

## 6.1 Metric Contracts

**Source:** [`evaluation/metrics.py`](evaluation/metrics.py)

| Contract | Rule | Why |
|----------|------|-----|
| **Null Consistency** | On AMBIGUOUS / OUT_OF_SCOPE cases, predicted intents must evaluate as null | Predicting a phantom intent on out-of-scope queries is penalized |
| **Set-Based F1** | Multi-intent sets use true micro/macro set intersections | Concatenated string matches artificially inflate scores |
| **Critical Risk Accounting** | `Unsafe Auto-Handle = FN / Total Gold Escalated` | Measures hazardous situations that silently bypass human supervision |

## 6.2 Grader Modules

| Grader | File | What It Scores |
|--------|------|----------------|
| Classification | [`evaluation/graders/classification.py`](evaluation/graders/classification.py) | Status, areas, intents, primary intent, state accuracy |
| Escalation | [`evaluation/graders/escalation.py`](evaluation/graders/escalation.py) | Precision, recall, F1, unsafe auto-handle rate, unnecessary escalation rate |
| Behavior | [`evaluation/graders/behavior.py`](evaluation/graders/behavior.py) | Capability hallucination, grounding compliance, policy invariants |
| Response Quality | [`evaluation/graders/response.py`](evaluation/graders/response.py) | LLM-as-judge 6-dimension rubric |
| Retrieval | [`evaluation/graders/retrieval.py`](evaluation/graders/retrieval.py) | Evidence relevance scoring |

**Harness runner:** [`evaluation/run_golden_eval.py`](evaluation/run_golden_eval.py) — Runs all 200 cases with the real pipeline, supports `--concurrency 5`, emits raw JSONL trajectories + summary JSON + markdown report.

## 6.3 LLM-as-Judge Rubric

Response quality scored on 6 orthogonal dimensions (1–5 Likert):

| Dimension | What It Measures | V3 Score | Human Agreement (r) |
|-----------|-----------------|----------|---------------------|
| Relevance | Does the reply address the customer's actual problem? | 4.17 / 5 | 0.82 |
| Factual Correctness | Are stated facts accurate? | 4.44 / 5 | 0.88 |
| Groundedness | Is every claim backed by retrieved evidence? | 4.92 / 5 | 0.91 |
| Actionability | Does the reply give a concrete next step? | 3.63 / 5 | 0.78 |
| Safety & Honesty | Does it avoid capability claims and acknowledge limits? | 4.96 / 5 | 0.94 |
| Conversation Awareness | Does it account for multi-turn context? | 2.21 / 5 | 0.81 |
| **Overall Composite** | | **4.05 / 5** | **0.86 (κ=0.79)** |

Human--judge correlation computed over 50 hand-calibrated audit samples.

## 6.4 Baselines

| Baseline | Behavior | Purpose |
|----------|----------|---------|
| **Trivial Majority-Class** | Predicts NORMAL, never escalates, BM25 top-1 ungrounded | Floor — shows minimum possible scores |
| **Simple Monolithic LLM** | Single zero-shot prompt for all tasks; no safety gates or NLI | Tests value of decoupled architecture |
| **Escalate Everything** | Every case goes to human review | Ceiling for recall; zero automation value |

---

# VII. Results

## 7.1 Headline Numbers (Golden V3)

| Metric | Value |
|--------|-------|
| **Status Accuracy** | **95.50%** |
| **Escalation F1** | **74.47%** |
| **Unsafe Auto-Handle Rate** ↓ | **31.37%** |
| **Unnecessary Escalation Rate** ↓ | **5.37%** |
| **Grounding Pass Rate** | **99.00%** |
| **Capability Hallucination Rate** ↓ | **0.00%** |
| **LLM Judge Composite** | **4.05 / 5** |
| **Execution Success Rate** | **100% (200/200)** |

## 7.2 Longitudinal Benchmark (V1 → V2 → V3)

| Metric | Trivial | Simple LLM | Agent V1 | Agent V2 | **Agent V3** | Δ V2→V3 |
|--------|---------|------------|----------|----------|-------------|---------|
| **Classification** | | | | | | |
| Status Accuracy | 82.50% | 85.00% | 91.00% | 95.50% | **95.50%** | +0.00% |
| Status Macro F1 | 0.301 | 0.624 | 0.487 | 0.882 | **0.888** | +0.005 |
| Primary Intent Acc. | 17.50% | 62.00% | 74.50% | 83.50% | **80.50%** | −3.00% |
| Primary Intent Macro F1 | 0.025 | 0.584 | 0.755 | 0.819 | **0.784** | −0.035 |
| Multi-Intent Exact Match | 12.00% | 51.50% | 68.00% | 81.00% | **76.00%** | −5.00% |
| State Accuracy | 41.50% | 54.00% | 67.00% | 84.50% | **82.00%** | −2.50% |
| **Escalation & Safety** | | | | | | |
| Escalation Precision | 0.00% | 42.10% | 75.00% | 54.05% | **81.40%** | **+27.35%** |
| Escalation Recall | 0.00% | 35.29% | 40.00% | 46.51% | **68.63%** | **+22.12%** |
| Escalation F1 | 0.00% | 38.37% | 52.17% | 50.00% | **74.47%** | **+24.47%** |
| Unsafe Auto-Handle ↓ | 100.0% | 64.71% | 60.00% | 53.49% | **31.37%** | **−22.12%** |
| Unnec. Escalation ↓ | 0.00% | 19.46% | 1.08% | 10.83% | **5.37%** | **−5.46%** |
| **Grounding & Behavioral** | | | | | | |
| Behavioral Pass Rate | 64.00% | 71.50% | 90.50% | 90.50% | **93.00%** | +2.50% |
| Grounding Pass Rate | 52.00% | 68.50% | 99.50% | 99.00% | **99.00%** | +0.00% |
| Hallucination Rate ↓ | 18.50% | 14.50% | 0.50% | 0.00% | **0.00%** | +0.00% |
| **Latency** | | | | | | |
| Median (p50) | 1.20s | 14.20s | 24.45s | 24.85s | **22.24s** | −2.61s |
| p95 | 3.10s | 36.50s | 64.13s | 90.68s | **70.99s** | −19.69s |

## 7.3 V3 Challenge-Group Breakdown

| Challenge Group | N | Status Acc. | State Acc. | Esc. Recall |
|----------------|---|-------------|------------|-------------|
| Carrier Misconduct | 13 | 100% | 38.5% | 46.2% |
| Routine Carrier Controls | 10 | 90% | 100% | — (0 FP) |
| Repeated Failed Support | 19 | 100% | 89.5% | 68.4% |
| Single Contact Controls | 3 | 100% | 33.3% | 0.0% |
| Account Security | 19 | 100% | 78.9% | **84.2%** |
| Lockout + Failed Recovery | 7 | 100% | 57.1% | **85.7%** |
| Routine Login Controls | 11 | 81.8% | 100% | — (1 FP) |
| Tracking Edge Cases | 14 | 100% | 92.9% | — (1 FP) |
| State Consistency Controls | 40 | 100% | 82.5% | 68.2% |
| Multi-Intent Composition | 20 | 100% | 75.0% | 33.3% |
| Ambiguous Inquiries | 23 | 91.3% | 95.7% | — (0 FP) |
| Out-of-Scope Queries | 12 | 75.0% | 100% | — (**0 FP**) |

## 7.4 Response Quality (LLM Judge)

| Dimension | Score | Observation |
|-----------|-------|-------------|
| Groundedness | 4.92 / 5 | Near-perfect — NLI loop catches unsupported claims |
| Safety & Honesty | 4.96 / 5 | Zero capability hallucinations |
| Factual Correctness | 4.44 / 5 | Strong factual accuracy from evidence grounding |
| Relevance | 4.17 / 5 | Good problem-targeting |
| Actionability | 3.63 / 5 | Some responses lack specific next steps |
| Conversation Awareness | 2.21 / 5 | Known weakness — multi-turn context utilization needs improvement |

---

# VIII. Failure Analysis

## 8.1 Top 5 Failure Modes

### F1. Colloquial Carrier-Misconduct Lexicon ⚠️ Safety-Critical: High

**Customer:** *"Delivery person chucked my fragile computer monitor box over the 7-foot driveway gate, smashing it directly against the concrete!"*

| | Value |
|---|---|
| **Gold** | `CARRIER_MISCONDUCT_AND_REFUSAL`, Escalate: True |
| **Agent** | `CARRIER_FEEDBACK`, Escalate: False |
| **Root Cause** | Gate 1b regex covered *threw, tossed, refused* but missed slang: *chucked, dumped, cursed at me* |
| **Fix Path** | Zero-shot aggression classifier alongside regex dictionaries |

### F2. Brand-Utterance Keyword Leakage — Safety: Low

**Context:** Brand asked *"Was the external carton also compromised?"* → Customer replied about leaking shampoo.

| | Value |
|---|---|
| **Gold** | `DAMAGED_ITEM`, Escalate: False |
| **Agent** | Escalate: True (`ACCOUNT_SECURITY_COMPROMISE`) |
| **Root Cause** | Gate 1b scanned aggregated thread text for `\bcompromised\b`, matching the *brand's* carton inquiry |
| **Fix Path** | Restrict security regex to customer-authored turns only |

### F3. Single Contact → Repeated Failure Misclassification — Safety: Low

**Customer:** *"I contacted support yesterday once and they told me it might arrive today."*

| | Value |
|---|---|
| **Gold** | `INITIAL_INQUIRY`, Escalate: False |
| **Agent** | Escalate: True (`REPEATED_FAILED_SUPPORT`) |
| **Root Cause** | State extractor matched *"contacted support ... yesterday"* without respecting the negative limiter *"once"* |
| **Fix Path** | Negative lookahead guards for singular markers (*once, first time, just*) |

### F4. Non-Standard Multi-Agent Phrasing — Safety: Medium-High

**Customer:** *"I've been passed between six different representatives across multiple calls and nobody has provided a straight answer!"*

| | Value |
|---|---|
| **Gold** | `REPEATED_FAILED_SUPPORT_ATTEMPTS`, Escalate: True |
| **Agent** | `SAFE_CLARIFICATION`, Escalate: False |
| **Root Cause** | Regex covered *transferred between agents* and *called X times*, but missed *passed between representatives* |
| **Fix Path** | Expand capture groups to transitive routing verbs (*passed, shuffled, bounced between*) |

### F5. NLI Grounding Timeout — Safety: Zero (Intended Fail-Safe) ✅

**Customer:** *"How do I sign out of all active devices from my Amazon account after using a hotel business center computer?"*

| | Value |
|---|---|
| **Gold** | `ACCOUNT_LOGIN_ISSUES`, Escalate: False |
| **Agent** | Escalate: True (`GROUNDING_FAILURE`) |
| **Root Cause** | Retrieved passages lacked exact device sign-out steps; NLI grader flagged after 2 retries |
| **Verdict** | **Intended fail-safe.** Over-escalating when ungrounded is infinitely preferable to hallucinating security instructions. |

## 8.2 What Is Misleading About My Headline Number?

> **Mandatory critical reflection section.**

### The Headline Sounds Great. Here's Why It's Dangerous.

*"88.0% Escalation Accuracy and 95.5% Status Accuracy!"*

**Problem 1: Class Imbalance Masks Risk**
Non-escalated cases dominate (74.5% of V3). A dummy model that **never escalates anything** achieves 74.5% escalation accuracy instantly. The 88.0% headline hides the real operational risk.

**Problem 2: Asymmetric Error Costs**

| Error Type | Rate | Real-World Cost |
|------------|------|-----------------|
| **False Positive** (unnecessary escalation) | 5.37% | ~$4.50 in human labor + slight queue delay |
| **False Negative** (unsafe auto-handle) | **31.37%** | Account fraud, brand reputation loss, customer churn (>$500 LTV per incident) |

Our **31.37% Unsafe Auto-Handle Rate** means ~3 of every 10 genuinely hazardous situations slipped past safety gates. Massive progress over Baseline (64.7%) and V1 (60.0%), but **claiming full autonomy would be negligent.**

**Problem 3: The True North Star**
The real metric is **Escalation Recall (68.63%)** and **Escalation F1 (74.47%)**. Closing the remaining 31.37% tail is the mandatory hurdle before production autonomy.

---

# IX. Decision Log

> 15 non-obvious engineering decisions, grouped by theme.

### Taxonomy & Data

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | **Amazon selected** for support variety | Most other brands have narrow, repetitive issue spaces that wouldn't stress-test escalation |
| 2 | **Freeze 14 leaf intents** | Small enough to be measurable, broad enough to cover 95%+ of traffic |
| 3 | **Multi-intent is multi-label**, not combinatorial | Prevents exponential label explosion |
| 4 | **Intent / state / outcome separated** | Orthogonal axes keep each classification surface small |
| 5 | **State keyed by `conversation_id`** | Extracted from live thread, not historical memory |

### Evidence & Retrieval

| # | Decision | Rationale |
|---|----------|-----------|
| 6 | **Retrieve decision points**, not full threads | Historical cases support the answer; they don't become facts about the current customer |
| 7 | **RRF (k=60)** for semantic + lexical fusion | Dense cosine distance collapses on alphanumeric order IDs; BM25 misses paraphrases |
| 8 | **No fabricated retrieval ground truth** | We don't pretend to have relevance labels we don't have |

### Safety & Escalation

| # | Decision | Rationale |
|---|----------|-----------|
| 9 | **Deterministic high-risk overrides** | LLMs exhibit prompt drift on safety edges; deterministic gates guarantee compliance |
| 10 | **Safe out-of-scope decline** via Gate 4 | Prevents trivial non-brand queries from exhausting human SLAs |
| 11 | **Action-based state consistency** | Gate 3 prevents asking for tracking when already provided — #1 driver of CSAT drops |
| 12 | **No fake human handoff** | Claiming "I've transferred you" when no handoff occurs is dishonest |

### Evaluation & Release

| # | Decision | Rationale |
|---|----------|-----------|
| 13 | **Reference-free response rubric** over BLEU/ROUGE | Historical tweets are terse; n-gram overlap penalizes superior explanations |
| 14 | **Fresh V2/V3 Golden sets** test policy generalization | Prevents overfitting to specific failure examples |
| 15 | **Freeze V3 as the reproducible submission candidate** | The final number is the frozen number; no post-hoc tuning allowed |

---

# X. Policy Iterations

## 10.1 Policy Iteration 1 (V1 → V2)

**Triggered by V1 failures:**
- 60% unsafe auto-handle rate on edge cases
- Missing detection for account security compromise
- No tracking-number lookup vs `TRACKING_ALREADY_CHECKED` distinction
- No conversation-aware state extraction

**Changes implemented:**
- Added deterministic high-risk override patterns for account compromise, carrier misconduct, and repeated failed support
- Implemented `StateExtractor` for evidence-based conversation state
- Added capability honesty filters (zero-tolerance for first-person action verbs)
- Conversation-aware response generation conditioning

**Result:** V2 showed improved recall but introduced over-escalation on out-of-scope queries (40% FP rate).

## 10.2 Policy Iteration 2 (V2 → V3)

**Triggered by V2 failures:**
- Over-escalation on out-of-scope queries
- Spurious state-inconsistency flags on routine tracking
- `block_out_of_scope` was set to `true`, forcing human review of trivial non-brand queries

**Changes implemented:**
- Gate 4: Converted out-of-scope from escalation to polite auto-decline
- Narrowed state-inconsistency regex to reduce false positives
- Tuned `block_out_of_scope: false` in escalation config
- Added `SAFE_CLARIFICATION` reason code for ambiguous cases

**Result:** V3 achieved +24.47% Escalation F1 improvement while reducing unnecessary escalations from 10.83% to 5.37%.

---

# XI. Productionizing on Hiver

## 11.1 Native Hiver Integration

| Integration Point | Implementation |
|-------------------|----------------|
| **Shared Mailbox Auto-Tagging** | Map predicted `areas` and `primary_intent` to native **Hiver Tags** (`#Urgent-Security`, `#Logistics-Delay`) |
| **Harvey AI Copilot Drafts** | Surface NLI-grounded resolutions in Gmail compose as 1-click agent drafts |
| **Collision Avoidance + Round-Robin** | Escalated tickets trigger automated round-robin assignment to tier-2 specialists |
| **Active Learning Feedback Loop** | Agent edits to Harvey drafts feed a weekly DPO fine-tuning pipeline |

## 11.2 Week-2 Technical Roadmap

| Day | Task |
|-----|------|
| **1–2** | Replace Gate 1b regex with fine-tuned SetFit/ModernBERT aggression classifier (resolves F1: colloquial verbs) |
| **3–4** | FastAPI webhook service listening to Hiver Shared Inbox events, emitting tagged tickets + SLA flags |
| **5** | Conformal prediction for confidence-calibrated selective classification (guarantee 95% security recall) |
| **6–7** | Real-time NLI grounding telemetry dashboard with latency percentile monitoring |

---

# XII. Reproducibility

## 12.1 Quick Start: Reproduce in <15 Minutes

```bash
# 1. Clone and install
git clone <REPO_URL> && cd hiver-support-agent
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# 3. Run the full frozen Golden V3 evaluation
python evaluation/run_golden_eval.py \
  --input data/golden/golden_v3_assistant_adjudicated.csv \
  --concurrency 5

# Output: evaluation/results/golden_v3_raw.jsonl
#         evaluation/results/golden_v3_results.json
#         evaluation/results/golden_v3_report.md
```

## 12.2 Environment

| Dependency | Version |
|------------|---------|
| Python | ≥ 3.10 |
| pandas | ≥ 2.2.0 |
| torch | ≥ 2.2.0 |
| sentence-transformers | ≥ 3.0.0 |
| scikit-learn | ≥ 1.4.0 |
| PyYAML | ≥ 6.0.0 |
| pytest | ≥ 8.0.0 |
| pyarrow | ≥ 15.0.0 |

**Embedding model:** `all-MiniLM-L6-v2` (384-dim, runs fully locally)
**Vector store:** Qdrant (local mode, no cloud dependency)
**LLM:** Gemini API (requires `GEMINI_API_KEY` in `.env`)

## 12.3 Repository Map

```
hiver-support-agent/
│
├── configs/                          # All configuration (YAML)
│   ├── taxonomy_v1.yaml              #   Frozen 14-intent taxonomy
│   ├── escalation.yaml               #   4-gate safety policy rules
│   ├── retrieval.yaml                #   Vector store + embedding config
│   ├── reranking.yaml                #   RRF parameters
│   ├── classifier_v2.yaml            #   Classifier settings
│   ├── response_generation.yaml      #   Generation parameters
│   └── annotation_guide.md           #   Labeling instructions
│
├── data/
│   ├── raw/                          # Raw Kaggle CSV (not committed)
│   ├── processed/                    # Cleaned Amazon parquet + discovery artifacts
│   │   ├── amazon_support_cases.parquet
│   │   ├── retrieval_documents.parquet
│   │   ├── intent_discovery_clusters.jsonl
│   │   └── taxonomy_review.md
│   ├── golden/                       # 🔒 LOCKED evaluation datasets
│   │   ├── golden_v1_assistant_adjudicated.csv   (200 cases)
│   │   ├── golden_v2_assistant_adjudicated.csv   (200 cases)
│   │   └── golden_v3_assistant_adjudicated.csv   (200 cases)
│   └── splits/
│       └── split_manifest.json
│
├── src/support_agent/                # Core agent implementation
│   ├── agent.py                      #   Main orchestrator (4-stage pipeline)
│   ├── server.py                     #   SSE streaming server
│   ├── classification/
│   │   ├── llm_classifier.py         #   Zero-shot LLM classifier
│   │   ├── state_extractor.py        #   Deterministic state extraction
│   │   ├── majority.py               #   Majority-class baseline
│   │   └── tfidf_classifier.py       #   TF-IDF baseline
│   ├── retrieval/
│   │   ├── embeddings.py             #   all-MiniLM-L6-v2 embeddings
│   │   ├── vector_store.py           #   Qdrant local vector store
│   │   ├── lexical_retriever.py      #   BM25 sparse retrieval
│   │   ├── reranker.py               #   RRF fusion (k=60)
│   │   ├── context_selector.py       #   Evidence context formatting
│   │   ├── conversation_builder.py   #   Multi-turn reconstruction
│   │   ├── document_builder.py       #   Retrieval doc preparation
│   │   ├── retriever.py              #   Retrieval orchestrator
│   │   ├── sampler.py                #   Development sampling
│   │   └── service.py                #   Retrieval service
│   ├── generation/
│   │   ├── response_generator.py     #   LLM response generation
│   │   └── revise_response.py        #   Grounding revision loop
│   ├── grounding/
│   │   └── grounding_checker.py      #   Claim-level NLI verification
│   ├── escalation/
│   │   ├── decision.py               #   Escalation decision orchestrator
│   │   ├── escalation_policy.py      #   Policy from config
│   │   └── high_risk.py              #   High-risk pattern detection
│   ├── llm/
│   │   └── client.py                 #   Gemini API client
│   ├── taxonomy/
│   │   └── embeddings.py             #   Taxonomy embedding utilities
│   └── data/
│       ├── loader.py                 #   Data loading utilities
│       └── schema.py                 #   Pydantic schema definitions
│
├── prompts/                          # LLM prompt templates
│   ├── classification_v2.md          #   Structured classification prompt
│   ├── response_generation_v1.md     #   Response generation prompt
│   └── grounding_v1.md              #   Grounding verification prompt
│
├── evaluation/                       # Evaluation harness
│   ├── run_golden_eval.py            #   Main harness runner
│   ├── metrics.py                    #   Metric computation
│   ├── compare.py                    #   Cross-generation comparison
│   ├── graders/
│   │   ├── classification.py         #   Classification grader
│   │   ├── escalation.py             #   Escalation grader
│   │   ├── behavior.py               #   Behavioral invariant grader
│   │   ├── response.py               #   LLM-as-judge grader
│   │   └── retrieval.py              #   Retrieval quality grader
│   └── results/                      # Output trajectories & reports
│       ├── golden_v1_raw.jsonl
│       ├── golden_v2_raw.jsonl
│       ├── golden_v3_raw.jsonl       #   ← Submission candidate
│       ├── golden_v3_results.json
│       └── golden_v3_report.md
│
├── scripts/                          # Data pipeline & experiment scripts
│   ├── validate_data.py
│   ├── build_intent_discovery.py
│   ├── discover_broad_areas.py
│   ├── discover_hierarchical_intents.py
│   ├── build_taxonomy_review.py
│   ├── build_retrieval_documents.py
│   ├── build_qdrant_index.py
│   ├── build_golden_set.py
│   ├── build_golden_v2.py
│   ├── build_golden_v3.py
│   └── ... (34 scripts total)
│
├── tests/                            # 212 automated tests
│   ├── test_classification.py
│   ├── test_escalation.py
│   ├── test_escalation_overrides.py
│   ├── test_grounding.py
│   ├── test_evaluation_harness.py
│   ├── test_rrf_reranker.py
│   ├── test_ambiguous_gate.py
│   └── ... (20 test files total)
│
├── notebooks/
│   └── Hiver_Brand_Selection_Analysis.ipynb
│
├── report/
│   └── hiver_sde_intern_report.tex   # 6-page LaTeX technical report
│
├── artifacts/                        # Model artifacts & caches
│   ├── retrieval/qdrant/             #   Local Qdrant vector index
│   ├── tfidf/                        #   TF-IDF baseline models
│   └── frozen_system_manifest.json   #   Frozen system state
│
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md                         # ← You are here
```

## 12.4 Test Suite

```bash
# Run all 212 tests
pytest tests/ -v

# Run specific test modules
pytest tests/test_escalation_overrides.py -v   # Safety gate tests
pytest tests/test_grounding.py -v              # NLI grounding tests
pytest tests/test_classification.py -v         # Classifier tests
pytest tests/test_rrf_reranker.py -v           # RRF fusion tests
```

All 212 tests pass on the frozen codebase.

---

<p align="center">
  <em>Built with engineering rigor, architectural curiosity, and user-centric pragmatism.</em><br>
  <strong>Daksh Patel</strong> · SDE Intern Candidate · Hiver
</p>
