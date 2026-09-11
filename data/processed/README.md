# AmazonHelp Support Cases Dataset (Processed Canonical Layer)

This directory contains the canonical processed support case dataset for the **evidence-grounded AI customer-support agent** built for the Hiver SDE Intern take-home assignment.

---

## 1. Provenance and Origin

- **Source Dataset:** *Customer Support on Twitter* (`twcs/twcs.csv` on Kaggle, ~2.8 million tweets).
- **Target Brand Selected:** `@AmazonHelp`.
- **Selection Rationale:** Chosen based on rigorous quantitative and qualitative evaluation in [`notebooks/Hiver_Brand_Selection_Analysis.ipynb`](../../notebooks/Hiver_Brand_Selection_Analysis.ipynb), demonstrating the highest combination of customer interaction volume, deep multi-turn conversational threads, rich semantic variety, and strong response reuse potential.
- **Preprocessing Environment:** Reconstructed and preprocessed on Kaggle; the exported files in this directory represent the official local implementation baseline.
- **Raw Data Policy:** The ~700MB raw Twitter dataset is intentionally **not** committed to Git to respect repository size limits. It is excluded via `.gitignore`.

---

## 2. Granularity and Unit of Analysis

Unlike the raw Twitter dataset where each record is an isolated tweet, **one row in this dataset represents a complete Support Case (Interaction Turn)**:

$$\text{Prior Conversation Context} + \text{Current Customer Message} \longrightarrow \text{Historical Amazon Support Response}$$

Each record captures a concrete agent decision point: given what has happened so far in the interaction, how did Amazon respond?

---

## 3. Dataset Files in this Directory

| File | Size | Format | Status in Git | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `amazon_support_cases.parquet` | ~190 MB | Apache Parquet (Snappy) | Ignored (`.gitignore`) | **Canonical Local Dataset**: Fast columnar reads, preserves nested context structs. |
| `amazon_support_cases.csv` | ~583 MB | CSV (UTF-8) | Ignored (`.gitignore`) | Legacy tabular format for external inspection. |
| `sample_cases.jsonl` | ~150 KB | JSON Lines | **Tracked in Git** | Balanced 100-case test slice for unit tests and offline CI/CD. |

Both `amazon_support_cases.parquet` and `amazon_support_cases.csv` contain **168,439 rows** and **25 columns** with **0 missing values**.

---

## 4. Schema Overview

The dataset adheres to the schema defined in [`src/support_agent/data/schema.py`](../../src/support_agent/data/schema.py):

### A. Primary Identifiers
- `case_id` (`str`): Unique case identifier (`amazon_case_0000000` to `amazon_case_0168438`). 100% unique (168,439 unique).
- `conversation_id` (`int64`): ID of the root tweet initiating the thread. 82,555 unique threads.
- `response_tweet_id` (`int64`): ID of the Amazon support reply. 100% unique (168,439 unique).
- `customer_tweet_id` (`int64`): ID of the customer message being answered.
- `customer_author_id` (`str`): Anonymized identifier of the customer.

### B. Conversational History & Context
- `turn_index` (`int64`): 0-indexed position within the thread (mean: 4.23, median: 2).
- `context` (`list[dict]` in Parquet): Structured chronological history of turns preceding and including this case:
  ```json
  [
    {"role": "CUSTOMER", "author": "184337", "text": "..."},
    {"role": "BRAND", "author": "AmazonHelp", "text": "..."}
  ]
  ```
- `context_clean` (`str`): Multi-turn dialogue string formatted with role labels (`CUSTOMER: ... \n BRAND: ...`).

### C. Message Content (Original & Clean)
- `customer_message_original` / `brand_response_original` (`str`): Raw tweet text as captured from Twitter.
- `customer_message_clean` / `brand_response_clean` (`str`): Preprocessed text:
  - Leading `@mentions` removed.
  - HTML entities unescaped (`&amp;` $\rightarrow$ `&`).
  - URLs normalized to `<URL>`.
  - Agent sign-offs (e.g. `^CR`, `^SM`) removed from brand responses.
  - Excess whitespace normalized.

### D. Thread Metadata
- `thread_length` (`int64`): Total tweets in the conversational thread (min 2, max 100).
- `thread_customer_turns` (`int64`): Number of customer messages in the thread.
- `thread_brand_turns` (`int64`): Number of Amazon responses in the thread.

### E. Quality & Linguistic Signals
- `language` (`str`): Detected ISO language code (`en`: 124,093 cases, `ja`: 9,361, `fr`: 8,245, `es`: 8,188, `unknown`: 6,495, etc.).
- `quality_status` (`str`): Data hygiene classification:
  - `OK` (161,655 cases, 95.97%): Standard clean cases.
  - Quality flags: `SHORT_CUSTOMER|UNKNOWN_LANGUAGE` (3,992), `UNKNOWN_LANGUAGE` (2,422), `SHORT_RESPONSE` (289), `SHORT_CUSTOMER|SHORT_RESPONSE|UNKNOWN_LANGUAGE` (48).
- `is_short_customer` / `is_short_response` (`bool`): Text length flags.

### F. Pipeline Retrieval Fields
- `model_input` (`str`): Formatted context ready for direct LLM prompting.
- `rag_document` (`str`): Structured representation optimized for vector retrieval chunking.

---

## 5. Known Limitations & Edge Cases

When designing downstream retrieval, classification, and generation systems, keep these constraints in mind:

1. **Absent `response_type` Field:**
   - The raw dataset does not provide labeled intent categories or response types (e.g., `direct_answer`, `request_info`, `escalate_to_dm`). This taxonomy must be synthesized and classified in downstream project stages.
2. **Private DM Deflection ("DM Handoff"):**
   - Because Twitter is a public platform, Amazon customer support frequently asks customers to transition to direct messages for sensitive account info (e.g., *"Please send us your order details via DM: <URL>"*). As a result, the ultimate resolution of account-specific issues is often omitted from the public conversation graph.
3. **URL Masking:**
   - Hyperlinks were masked to `<URL>` during cleaning. The agent cannot fetch external landing page contents from historical URLs, so grounding must rely on historical tweet text and domain policies.
4. **Multilingual Presence:**
   - 26.3% of the cases are in non-English languages (`ja`, `fr`, `es`, etc.). For English-focused pipelines, filters must specify `language == "en"`.
5. **Short / Ambiguous Inquiries:**
   - Approximately 2.4% of customer messages consist of one or two words (e.g., *"hello?", "thanks"*). Downstream intent classification should account for or filter `quality_status != "OK"`.
6. **Thread Branching:**
   - 13,781 cases share a `customer_tweet_id` where Amazon sent multiple distinct replies (e.g., clarifying two different questions or responding across two tweets due to character limits).

---

## 6. How to Load the Dataset

Use the project's centralized loader in [`src/support_agent/data/loader.py`](../../src/support_agent/data/loader.py):

```python
from support_agent.data import load_cases, load_cases_df, load_sample_cases

# 1. High performance filtered DataFrame (English, OK quality)
df = load_cases_df(language="en", quality_ok_only=True)
print(f"Loaded {len(df):,} clean English cases.")

# 2. Iterate memory-efficiently over validated SupportCase domain objects
for case in load_cases(limit=100):
    print(case.case_id, case.customer_message_clean, "->", case.brand_response_clean)

# 3. Fast offline test slice (100 cases, no large files needed)
sample_cases = load_sample_cases()
```
