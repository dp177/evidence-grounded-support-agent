# Evidence-Grounded Amazon Support Agent

> A safety-first AI customer-support agent built from real AmazonHelp Twitter conversations.
>
> **Core idea:** automate routine, repeatable support interactions when the system has enough evidence and a grounded response; route personalized, sensitive, ambiguous, contradictory, or unsupported situations to a human.

---

## 1. Executive Summary

Hiver's take-home asks us to turn a noisy real-world customer-support dataset into an AI support system that can:

1. **Classify** incoming support messages into a small taxonomy of intents.
2. **Draft a reply** grounded in how the selected brand historically resolved similar issues.
3. **Decide** whether to auto-handle the case or escalate it to a human, with a reason.
4. **Prove the system works** through a hand-labelled golden set, baselines, automated metrics, failure analysis, and LLM-as-judge calibration.

This project implements the complete pipeline for **AmazonHelp**:

```text
Customer message
      |
      v
+------------------+
| Classifier V2    |
| intent + state   |
| + confidence     |
+--------+---------+
         |
         v
+------------------+
| Qdrant Retrieval |
| historical cases |
+--------+---------+
         |
         v
+------------------+
| Candidate        |
| Reranker         |
+--------+---------+
         |
         v
+------------------+
| Response         |
| Generator        |
+--------+---------+
         |
         v
+------------------+
| Grounding V1.1   |
| safety verifier  |
+--------+---------+
         |
         v
+------------------+
| Escalation       |
| Policy Engine    |
+----+---------+---+
     |         |
     v         v
   AUTO       HUMAN
```

The key product principle is **not "automate everything."**

It is:

> **Automate safely when the answer is supported; preserve human intervention when the case requires personalized judgment or facts the system cannot verify.**

---

# 2. What Hiver Asked For — and What We Built

| Hiver requirement | Our implementation |
|---|---|
| Pick one brand | **AmazonHelp** |
| Classify messages into a small intent set | Frozen **Taxonomy V1** with 14 leaf intents across 6 areas |
| Historical-grounded reply | Qdrant retrieval of historical Amazon customer→response interactions |
| Human escalation decision | Deterministic escalation policy |
| Golden evaluation set | **200 hand-reviewed cases** |
| At least two baselines | Majority baseline + TF-IDF baseline |
| Automated evaluation | Classification, retrieval, grounding, safety, end-to-end metrics |
| LLM-as-judge | 7-dimensional reply-quality rubric + 30-case human calibration |
| Human agreement evidence | Exact agreement, MAE, correlation + disagreement analysis |
| Failure analysis | Component-level and end-to-end failure analysis |
| Misleading headline metric | Explicit analysis of raw auto-handle vs actual resolution |
| Decision log | Non-obvious design decisions documented |
| Reproducible repo | Deterministic sampling, manifests, caches, tests, scripted evaluation |

Hiver explicitly says the proof is more important than the system and allows/encourages a subsample of the full dataset.

---

# 3. Problem Framing

## What does "good support" mean?

For this project, a good response must be:

**Relevant**
- addresses the customer's actual problem

**Operationally useful**
- gives a concrete next step when one is supported

**Grounded**
- does not invent refunds, delivery promises, account changes, eligibility, or actions already taken

**State-aware**
- does not repeat things the customer already did

**Conservative**
- escalates when personalized information or sensitive judgment is required

**Auditable**
- every generated answer can be traced back to its classification, retrieved evidence, grounding result, and escalation decision

---

# 4. What We Chose NOT to Build

This is intentional.

We did **not** try to build:

- a universal customer-support agent for every brand
- a huge flat taxonomy containing hundreds/thousands of intents
- a fully supervised classifier trained on millions of manually labelled examples
- a hosted vector database as a hard dependency
- unrestricted account/CRM actions
- an agent that automatically resolves every ticket
- an LLM that freely decides whether a case is safe
- an LLM judge that becomes part of the production decision path

Instead, we focused on one brand and built a modular, evidence-grounded system.

---

# 5. How We Got Here

## Phase 1 — Start with messy real-world data

The source dataset is the Kaggle **Customer Support on Twitter** dataset containing multi-turn support conversations.

The raw data is noisy:

```text
Twitter handles
URLs
HTML entities
multiple reply relationships
long conversations
short fragments
mixed languages
duplicate/low-value interactions
```

Rather than blindly embedding tweets, we first created a canonical AmazonHelp processed dataset.

---

# 6. Canonical Data Pipeline

```text
Raw Kaggle dataset
        |
        v
Brand filtering
        |
        v
AmazonHelp processed dataset
        |
        +------------------------------+
        |                              |
        v                              v
Taxonomy discovery              Retrieval document builder
        |                              |
        v                              v
Taxonomy V1                    Customer + relevant context
                                      + Amazon response
                                      |
                                      v
                              Retrieval corpus
```

The original raw source is preserved. Model-facing representations use the cleaned fields created during preprocessing.

---

# 7. Why We Did NOT Create One Vector Per Tweet

A raw conversation may look like:

```text
T1 Customer: Where is my order?
T2 Amazon: Please check tracking.
T3 Customer: I already checked.
T4 Amazon: What does tracking say?
T5 Customer: It says delayed.
T6 Amazon: Please provide order number.
T7 Customer: 123...
T8 Amazon: ...
```

If we create one vector per tweet, the relationship between:

> customer problem → support state → Amazon action

is lost.

If we create one giant vector for the whole conversation, unrelated turns can dilute the representation.

### Our retrieval unit

We therefore use one **support decision point**:

```text
CUSTOMER:
My package is late.

RELEVANT CONTEXT:
Tracking says delayed.
Customer already contacted the carrier.
Promised delivery date has passed.

AMAZON RESPONSE:
Please confirm the delivery date in your order confirmation.
```

That entire support interaction becomes **one vector**.

The original conversation remains traceable through:

```text
conversation_id
customer_tweet_id
brand_response_tweet_id
turn_index
selected_context_tweet_ids
```

This is the core retrieval design.

---

# 8. How We Handle Long Conversations

We do **not** assume the previous four turns are always the important ones.

For a 15-turn conversation:

```text
T1 ... unrelated
T2 ... unrelated
T3 tracking is delayed
T4 ...
T5 order number
T6 ...
T7 promised delivery date
T8 ...
T9 already contacted carrier
T10 wait 48h
T11 waiting window exceeded
T12 ...
T13 ...
T14 ...
T15 current complaint
```

the relevant context may be:

```text
T3  -> tracking state
T7  -> promised date
T9  -> carrier already contacted
T10 -> waiting instruction
T11 -> waiting window exceeded
T15 -> current complaint
```

### Context selection

The system uses deterministic relevance signals such as:

- recency
- problem/entity overlap
- delivery/tracking/refund indicators
- date/deadline information
- previous actions
- state-related phrases
- relationship to the current turn

The context is bounded so long conversations do not create huge model inputs.

---

# 9. Taxonomy Discovery

Instead of forcing the LLM to invent thousands of intents at runtime, we first discovered a compact operational taxonomy from AmazonHelp data.

### Taxonomy structure

```text
Area
 |
 +-- Intent
       |
       +-- State
```

The important distinction is:

```text
INTENT  = What problem does the customer have?

STATE   = What has already happened in this conversation?

OUTCOME = How did the case eventually end?
```

Examples:

```text
Intent:
DELIVERY_DELAYED

State:
TRACKING_ALREADY_CHECKED
WAITING_WINDOW_EXCEEDED
```

This prevents the common mistake of creating labels such as:

```text
DELIVERY_DELAYED_AND_TRACKING_ALREADY_CHECKED
```

which causes combinatorial taxonomy explosion.

---

# 10. Multi-Intent Design

Multi-intent is a **property**, not a new combinatorial intent.

Example:

```text
"My order is late and I was charged twice."
```

becomes:

```json
{
  "intents": [
    "DELIVERY_DELAYED",
    "UNRECOGNIZED_OR_DUPLICATE_CHARGE"
  ],
  "is_multi_intent": true
}
```

We do not create:

```text
DELIVERY_DELAYED_AND_DUPLICATE_CHARGE
```

---

# 11. Classifier V1 → V2

## Initial approach: zero-shot

The LLM received:

```text
Taxonomy definitions
+
decision rules
+
conversation
```

and produced structured classification.

This established a functional baseline.

## Improvement: few-shot Classifier V2

We then selected **55 development-only demonstrations**.

Important:

```text
Golden V1
    X
Development demonstrations
    OK
```

No Golden V1 case was used as a demonstration.

The classifier therefore became:

```text
Taxonomy
+
decision rules
+
real development examples
+
current conversation
        |
        v
LLM
        |
        v
intent + state + confidence
```

### Classifier V2 result

| Metric | V2 |
|---|---:|
| Primary accuracy | **77.14%** |
| Primary Macro F1 | **0.7713** |
| Weighted F1 | **0.7801** |
| Multi-intent Micro F1 | **0.7147** |
| Multi-intent Exact Match | **67.0%** |

This was an improvement over the zero-shot configuration.

---

# 12. The Classifier Prompt

The production classification prompt is versioned at:

```text
prompts/classification_v2.md
```

Conceptually, it tells the model:

```text
You are an Amazon customer-support classifier.

Use ONLY the supplied taxonomy.

Read the full conversation.

Do not invent intents.

Return structured JSON.

Distinguish:
- current problem
- multiple independent problems
- conversational state
- ambiguity
- out-of-scope requests
```

The model receives the live conversation:

```text
CONVERSATION HISTORY
+
CURRENT CUSTOMER MESSAGE
```

It does not receive Golden answers.

---

# 13. Historical RAG

The historical corpus is **not generic Amazon documentation**.

It is:

> **real Amazon customer-support interactions and the corresponding historical Amazon responses.**

This directly supports Hiver's requirement to draft a reply grounded in how the brand historically resolved similar issues.

---

# 14. Vector Store

We chose **Qdrant** as the vector-store abstraction.

### Current development mode

```text
Qdrant Local
    |
    +-- persistent on disk
```

### Future deployment

The code is designed to support:

```text
Qdrant Local
       ↕
Qdrant Cloud
```

without changing the retrieval interface.

Configuration controls the backend.

---

# 15. Retrieval Corpus Size

The processed corpus contains approximately:

```text
167,764 retrieval documents
```

For fast development/evaluation, the agent indexes a **representative deterministic 10,000-document sample**.

This is permitted by Hiver's submission rules, which explicitly allow/encourage a subsample.

The original naive approach was:

```python
df.head(10000)
```

We rejected that.

The final development sample is:

- stratified
- deterministic
- Golden-isolated
- capped by conversation contribution
- designed to better represent language/thread-depth/quality distributions

It covers:

```text
9,401 unique conversations
```

rather than concentrating heavily on a few long threads.

---

# 16. Qdrant Data Model

One Qdrant point contains:

```text
VECTOR
  |
  +-- embedding of:
      CUSTOMER
      +
      RELEVANT CONTEXT
      +
      AMAZON RESPONSE

PAYLOAD
  |
  +-- document_id
  +-- case_id
  +-- conversation_id
  +-- turn_index
  +-- customer message
  +-- relevant context
  +-- Amazon response
  +-- provenance
```

This gives us:

```text
semantic retrieval
        +
exact evidence
        +
provenance
```

---

# 17. Retrieval Pipeline

```text
Current customer message
        |
        v
Current conversation context
        |
        v
Query embedding
        |
        v
Qdrant
        |
        v
Top 30 semantic candidates
        |
        v
Candidate Reranker
        |
        +-- semantic similarity
        +-- lexical similarity
        +-- intent compatibility
        +-- state compatibility
        +-- response/action usefulness
        +-- conversation deduplication
        |
        v
Top 5 historical evidence cases
```

---

# 18. Why We Added Reranking

Pure embedding similarity can make mistakes like:

```text
CURRENT:
Package is late and tracking is stalled.

RETRIEVED:
Package marked delivered but customer did not receive it.
```

Both mention:

```text
package
delivery
carrier
```

but operationally:

```text
DELIVERY_DELAYED
        !=
MARKED_DELIVERED_NOT_RECEIVED
```

The reranker introduces additional signals.

### Results

| Metric | Semantic | Reranked |
|---|---:|---:|
| Recall@1 | 29.5% | **31.5%** |
| Recall@5 | 48.5% | **50.5%** |
| MRR | 0.3628 | **0.3816** |

The reranker also reduced generic boilerplate historical responses in Top-5 from roughly 6.8% to 1.8%.

---

# 19. Why Conversation Deduplication Matters

A long historical conversation may contain multiple support decision points.

Without deduplication:

```text
Top 5
 ├── Case A, conversation 123
 ├── Case B, conversation 123
 ├── Case C, conversation 123
 ├── Case D, conversation 481
 └── Case E, conversation 912
```

That wastes evidence slots.

We therefore limit repeated results from the same conversation.

---

# 20. Response Generation

Once we have:

```text
CURRENT CONVERSATION
+
CLASSIFICATION
+
TOP HISTORICAL EVIDENCE
```

the response generator creates a new customer-facing draft.

It is explicitly told:

```text
Historical evidence is an example of how Amazon handled
a similar historical situation.

It does NOT prove that Amazon has already performed
the same action for the current customer.
```

This distinction is critical.

---

# 21. State-Aware Responses

The system uses state as an operational constraint.

### Example

If:

```text
state = TRACKING_ALREADY_CHECKED
```

then the agent should not say:

```text
"Please check your tracking."
```

If:

```text
state = CARRIER_ALREADY_CONTACTED
```

it should not blindly say:

```text
"Please contact the carrier."
```

If:

```text
state = DETAILS_ALREADY_PROVIDED
```

it should not repeatedly ask for the same information.

This is where the taxonomy's state dimension becomes operationally valuable.

---

# 22. Grounding Verification

The generated response is **not trusted automatically**.

It passes through a grounding layer:

```text
Draft reply
    |
    v
Deterministic safety checks
    |
    v
Semantic claim verification
    |
    v
SUPPORTED?
 /        YES        NO
 |          |
 v          v
Done      Revise
             |
             v
          Max 2 tries
             |
             v
          Still unsafe?
             |
             v
           HUMAN
```

The verifier checks especially:

- refunds
- refund amounts
- refund timing
- delivery promises
- order status
- compensation
- eligibility
- account changes
- unsupported actions
- contradictions

---

# 23. The Important Grounding Rule

A historical statement:

```text
"Amazon refunded this historical customer."
```

does NOT justify:

```text
"Your refund has been issued."
```

Similarly:

```text
"Safe-place delivery was available in a historical case."
```

does not justify:

```text
"We can offer you safe-place delivery tomorrow."
```

unless the current case establishes that.

Phase 9.1 made this distinction strict.

---

# 24. Grounding Results

On a 40-case development evaluation:

```text
First-pass grounded:       87.5%
Successfully repaired:     12.5%
Final grounding failures:   0%
False approvals:            0%
```

The system became stricter about claims such as:

```text
"We've received your order number."

"Your refund has been issued."

"We can offer you delivery tomorrow."

"I've escalated your case."
```

when those current actions were not actually established.

---

# 25. Human Intervention is a Feature

We deliberately do **not** try to automate personalized account-level support without the required evidence.

The production decision engine is deterministic:

```text
Grounding
+
Classification
+
State
+
Risk
+
Evidence
        |
        v
AUTO-HANDLE
or
HUMAN REVIEW
```

This is not a fallback we added at the end.

It is part of the product design.

---

# 26. Escalation Policy

Hard blockers include examples such as:

```text
AMBIGUOUS_CLASSIFICATION
HIGH_RISK_SECURITY
FRAUD_CONCERN
GROUNDING_FAILURE
CONTRADICTED_RESPONSE
INSUFFICIENT_EVIDENCE
INCONSISTENT_WITH_STATE
MALFORMED_RESPONSE
```

The LLM does **not** get to override these deterministic gates.

---

# 27. Live Conversations vs Historical Knowledge

This distinction is fundamental.

## Live conversation

Belongs to the current customer:

```text
conversation_id = current session

previous messages
+
previous agent replies
+
current message
+
current state
```

## Historical knowledge

Shared across customers:

```text
Qdrant
   |
   +-- old Amazon conversation
   +-- old Amazon response
   +-- old Amazon conversation
   +-- old Amazon response
```

Therefore:

```text
LIVE HISTORY
     +
CLASSIFICATION
     +
HISTORICAL EVIDENCE
```

come together only at runtime.

---

# 28. Concurrent Chat Architecture

For simultaneous customers:

```text
              Shared Historical Qdrant
                 /        |                        /         |                        v          v          v
          Session A   Session B   Session C
             |           |           |
             v           v           v
          History      History      History
             |           |           |
             v           v           v
          State A      State B      State C
```

Each session has isolated current history/state.

Qdrant is shared because historical support interactions are common knowledge.

This prevents User A's live conversation from leaking into User B's context.

---

# 29. End-to-End Golden Evaluation

The final frozen system was evaluated on:

```text
200 Golden V1 cases
```

with no tuning against the benchmark.

### Headline results

| Component | Result |
|---|---:|
| Intent Accuracy | **77.14%** |
| Primary Macro F1 | **0.7713** |
| Multi-intent Micro F1 | **0.7147** |
| Reranked Recall@5 | **50.50%** |
| Reranked MRR | **0.3816** |
| Mean Relevance | **4.52 / 5** |
| Mean Correctness | **4.42 / 5** |
| Mean Groundedness | **4.37 / 5** |
| Unsafe Auto-handle | **0.00%** |
| Raw Auto-handle | **88.5%** |
| Full Resolve | **21.5%** |
| Safe Clarification | **67.0%** |
| Human Review | **11.5%** |
| Strict End-to-End Pass | **85.0%** |
| Regression Tests | **149 / 149** |

---

# 30. The Most Important Interpretation of 88.5%

Do **not** say:

> "The agent resolves 88.5% of support cases."

That would be misleading.

The actual breakdown is:

```text
200 total

177  → avoided immediate human escalation
43   → full RESOLVE
134  → safe CLARIFY
23   → HUMAN
```

Therefore:

```text
Raw auto-handle = 88.5%
Full resolution  = 21.5%
Clarification     = 67.0%
Human review      = 11.5%
```

The 88.5% figure means:

> **the system can safely handle the interaction without immediately sending it to a human.**

It does not mean it fully resolves the customer's issue.

This is the project's required **"misleading headline number"** analysis.

---

# 31. LLM-as-Judge — Important Limitation

We built the required LLM-as-judge evaluation and calibrated it against humans.

However, the calibration produced:

```text
Exact agreement = 50%
MAE             = 0.51 points
Pearson r       = 0.059
```

The judge tended to compress scores toward the 4–5 range.

Therefore:

> **Judge-derived response-quality averages should be treated as evaluation signals, not ground truth.**

This is intentionally disclosed rather than hidden.

---

# 32. Why the 85% End-to-End Number Needs Context

The strict end-to-end pass rate is:

```text
85% = 170 / 200
```

under the defined benchmark criteria.

However, one criterion uses the LLM-as-judge response-quality evaluation, and the judge's human correlation is weak.

Therefore the correct interpretation is:

> **85% strict benchmark pass rate under our defined evaluation protocol, not proof of 85% real-world customer resolution.**

This is why the project includes separate component metrics and human-calibration evidence.

---

# 33. Why Human Escalation is Correct Product Behavior

Consider:

```text
"My Amazon account was hacked and someone used my card."
```

The historical corpus may show how Amazon handled similar cases.

It does **not** prove what happened to this customer's current account.

Therefore:

```text
HIGH_RISK_SECURITY
        ↓
HUMAN
```

Likewise:

```text
"My refund has been missing for months and I've contacted support 5 times."
```

may require account-specific information unavailable in the historical corpus.

The correct behavior is not to hallucinate a resolution.

It is to escalate.

---

# 34. Full Decision Logic

```text
                NEW MESSAGE
                     |
                     v
              CLASSIFIER V2
                     |
             +-------+-------+
             |       |       |
           intent   state  confidence
                     |
                     v
                QDRANT TOP 30
                     |
                     v
                  RERANK
                     |
                     v
                  TOP 5
                     |
                     v
               GENERATOR
                     |
                     v
              GROUNDING CHECK
                     |
                +----+----+
                |         |
              PASS       FAIL
                |         |
                |       REVISE
                |         |
                |      PASS? ---- NO ---> HUMAN
                |         |
                +---------+
                     |
                     v
             ESCALATION POLICY
                     |
              +------+------+
              |             |
             AUTO          HUMAN
              |             |
              v             v
          Customer      Support Agent
```

---

# 35. Key Design Decisions

1. **One brand** — AmazonHelp, to keep the problem operationally focused.
2. **Compact taxonomy** — areas + leaf intents + states instead of a flat explosion.
3. **Multi-intent as a property** — avoids combinatorial labels.
4. **Few-shot classifier** — development examples improve application of taxonomy.
5. **Interaction-level retrieval** — customer problem + relevant context + Amazon response as one vector.
6. **Provenance preservation** — every retrieved case maps to its original conversation.
7. **Qdrant** — vector-database architecture with local-first development and cloud-ready abstraction.
8. **Representative 10K retrieval corpus** — deterministic, stratified, reproducible development subset.
9. **Reranking** — semantic similarity alone was not operationally precise enough.
10. **Grounding as a hard gate** — historical precedent is not proof of current account state.
11. **Deterministic escalation** — human routing must be explainable and auditable.
12. **Human calibration of judge** — judge quality is measured rather than assumed.

---

# 36. Repository Structure

```text
.
├── configs/
│   ├── taxonomy_v1.yaml
│   ├── classifier_v2.yaml
│   ├── retrieval.yaml
│   ├── reranking.yaml
│   ├── response_generation.yaml
│   └── escalation.yaml
│
├── data/
│   ├── processed/
│   │   ├── amazon_support_cases.parquet
│   │   ├── retrieval_documents.parquet
│   │   ├── qdrant_development_sample.parquet
│   │   └── qdrant_development_sample_ids.json
│   │
│   ├── development/
│   │   └── classification_demos.jsonl
│   │
│   └── golden/
│       └── golden_set.jsonl
│
├── prompts/
│   ├── classification_v2.md
│   ├── response_generation_v1.md
│   └── grounding_v1.md
│
├── src/
│   └── support_agent/
│       ├── llm/
│       ├── preprocessing/
│       ├── taxonomy/
│       ├── retrieval/
│       ├── generation/
│       ├── grounding/
│       └── escalation/
│
├── scripts/
│   ├── sample_qdrant_corpus.py
│   ├── build_qdrant_index.py
│   ├── demo_qdrant_retrieval.py
│   ├── evaluate_qdrant_retrieval.py
│   ├── evaluate_grounding.py
│   ├── evaluate_escalation.py
│   └── evaluate_golden_e2e.py
│
├── experiments/
│   ├── final_system_results.md
│   ├── e2e_failure_analysis.md
│   ├── misleading_headline_number.md
│   ├── llm_judge_calibration.md
│   ├── reranking_failure_analysis.md
│   └── escalation_failure_analysis.md
│
├── results/
│   ├── e2e_predictions.jsonl
│   ├── final_system_metrics.json
│   └── ...
│
└── tests/
    └── ...
```

---

# 37. Reproducibility

The evaluation is designed around deterministic artifacts:

```text
Frozen Taxonomy
+
Frozen Golden Set
+
Versioned Prompts
+
Development-only demonstrations
+
Corpus/sample hashes
+
Qdrant manifest
+
Cached predictions
+
Automated tests
```

A future rebuild should not silently use a different corpus or model configuration.

---

# 38. Environment

The project uses:

```text
LLM provider:
OpenRouter

Classifier / generator model:
Configured OpenRouter LLaMA 3.1 8B Instruct

Embeddings:
all-MiniLM-L6-v2

Vector store:
Qdrant

Development vector mode:
local persistent

Future deployment:
Qdrant Cloud-compatible
```

Credentials are supplied through environment variables, never committed to the repository.

Example:

```bash
OPENROUTER_API_KEY=...
QDRANT_MODE=local
QDRANT_PATH=artifacts/retrieval/qdrant
```

---

# 39. Quick Start

The exact commands should follow the repository's current dependency setup.

```bash
# install dependencies
pip install -r requirements.txt

# run tests
pytest -v

# build / verify the retrieval development sample
python scripts/sample_qdrant_corpus.py

# build the local Qdrant index
python scripts/build_qdrant_index.py

# run retrieval demo
python scripts/demo_qdrant_retrieval.py

# run the final benchmark
python scripts/evaluate_golden_e2e.py
```

For the submitted repository, the README should keep the default path within Hiver's requested reproduction window by relying on existing/cached development artifacts rather than requiring a full 167K-document re-embedding.

---

# 40. Testing

The project ended Phase 11 with:

```text
149 / 149 tests passing
```

The tests cover:

- dataset loading
- schema validation
- taxonomy invariants
- Golden isolation
- few-shot isolation
- retrieval document construction
- context selection
- Qdrant operations
- embedding cache invalidation
- reranking
- generation
- grounding
- escalation

---

# 41. Known Limitations

This project is intentionally honest about its limitations.

### Retrieval is imperfect

Reranked Recall@5 is **50.5%**.

This means historical evidence retrieval is useful but not universally reliable.

### Classifier is imperfect

Intent accuracy is **77.14%**.

Boundary cases remain difficult.

### State prediction is weaker than intent prediction

The V2 prompt improved intent classification more strongly than state recognition.

### LLM judge calibration is weak

Pearson correlation with human scoring was only **0.059**.

### The 10K retrieval corpus is a development subset

The full processed retrieval corpus is much larger.

### No live CRM/account integration

Therefore the system cannot independently verify arbitrary customer-specific account facts.

### Historical support data is not policy truth

Historical responses can be outdated or inconsistent.

That is why grounding and human escalation exist.

---

# 42. What We Would Do With One More Week

## 1. Improve retrieval

Evaluate a stronger embedding model and/or hybrid lexical + dense retrieval.

## 2. Learn reranking weights

Use a larger development evidence set rather than manually chosen initial weights.

## 3. Better state tracking

Replace purely classification-time state inference with a persistent conversation-state tracker.

## 4. Better live-session architecture

Add a production-style conversation store and concurrency-safe session management.

## 5. Human-review workflow

Provide a small UI showing:

```text
customer
classification
historical evidence
draft
grounding flags
escalation reason
```

so a human can take over quickly.

## 6. Improve judge calibration

Expand the human calibration set and redesign the rubric to increase score variance and agreement.

---

# 43. Business Value

The system is designed around a realistic customer-support operating model.

### Routine cases

```text
Known problem
+
strong historical precedent
+
safe state
+
grounded response
        ↓
AUTO
```

### Personalized/sensitive cases

```text
Account-specific facts
OR
security/fraud
OR
contradiction
OR
insufficient evidence
        ↓
HUMAN
```

This creates a **human-in-the-loop support system**, not an unsafe autonomous chatbot.

The objective is therefore not:

> maximize automation at any cost.

It is:

> **maximize safe automation while preserving human judgment where it matters.**

---

# 44. Best Interview Explanation

### "What did you build?"

> I built an evidence-grounded Amazon support agent over real multi-turn customer-support conversations. It first classifies the issue and dialogue state, retrieves similar historical Amazon resolutions from Qdrant, reranks the evidence, generates a response, verifies the response for unsupported claims, and finally makes a deterministic auto-handle vs human-review decision.

### "Why not just use an LLM?"

> Because a generic LLM can answer but cannot reliably know what Amazon historically did in this dataset, and it can invent account-specific actions. We separate classification, retrieval, generation, grounding, and escalation so every stage can be evaluated and audited.

### "Why human escalation?"

> Historical support cases are evidence of past handling, not proof of a customer's current account state. When the answer requires personalized or sensitive information the system cannot verify, human intervention is the correct behavior.

### "What is your most important evaluation insight?"

> The raw 88.5% auto-handle rate is misleading. Only 21.5% are full resolutions; 67% are safe clarification interactions. I therefore report strict end-to-end success and unsafe auto-handle rate separately.

---

# 45. Final Architecture in One Diagram

```text
                    ┌─────────────────────┐
                    │   LIVE CUSTOMER     │
                    │     CONVERSATION    │
                    └──────────┬──────────┘
                               |
                               v
                    ┌─────────────────────┐
                    │     CLASSIFIER V2   │
                    │                     │
                    │ intent              │
                    │ multi-intent        │
                    │ state               │
                    │ confidence          │
                    └──────────┬──────────┘
                               |
                               v
                    ┌─────────────────────┐
                    │   QUERY BUILDER     │
                    │ current message +   │
                    │ relevant live       │
                    │ context             │
                    └──────────┬──────────┘
                               |
                               v
                    ┌─────────────────────┐
                    │   QDRANT VECTOR DB  │
                    │ historical Amazon   │
                    │ support interactions│
                    └──────────┬──────────┘
                               |
                           Top 30
                               |
                               v
                    ┌─────────────────────┐
                    │     RERANKER        │
                    │ semantic            │
                    │ lexical             │
                    │ intent/state        │
                    │ action usefulness   │
                    │ conversation dedup  │
                    └──────────┬──────────┘
                               |
                            Top 5
                               |
                               v
                    ┌─────────────────────┐
                    │ RESPONSE GENERATOR  │
                    │ grounded synthesis  │
                    └──────────┬──────────┘
                               |
                               v
                    ┌─────────────────────┐
                    │ GROUNDING V1.1      │
                    │ claim verification  │
                    │ safety checks       │
                    └──────────┬──────────┘
                               |
                     ┌─────────┴─────────┐
                     |                   |
                   PASS                FAIL
                     |                   |
                     |              revision
                     |                   |
                     |             still failing
                     |                   |
                     |                   v
                     |                HUMAN
                     |
                     v
              ┌────────────────┐
              │ ESCALATION     │
              │ POLICY ENGINE  │
              └───────┬────────┘
                      |
               ┌──────┴──────┐
               |             |
             AUTO           HUMAN
               |             |
               v             v
           Customer      Support Agent
```

---

# 46. Final Takeaway

The strongest part of this project is not a single model score.

It is the **system design and proof structure**:

```text
Messy Data
   ↓
Compact Operational Taxonomy
   ↓
Development-Only Few-Shot Classification
   ↓
Historical Resolution Retrieval
   ↓
Intent/State-Aware Reranking
   ↓
Grounded Response Generation
   ↓
Claim-Level Safety Verification
   ↓
Deterministic Human Escalation
   ↓
Auditable Outcome
```

The system answers three different questions separately:

```text
1. WHAT is the customer asking?
        ↓
2. HOW has Amazon historically handled similar situations?
        ↓
3. IS it safe to answer automatically?
```

That separation makes the agent explainable, testable, and suitable for controlled customer-support automation.

---

## Submission Status

**Core implementation:** complete

**Golden benchmark:** 200 cases

**Automated evaluation:** complete

**Human calibration:** complete, with limitations disclosed

**Failure analysis:** complete

**Safety policy:** complete

**Final report:** prepared

**Remaining work:** polish README/repo, verify the 15-minute reproduction path, and package the submission.
