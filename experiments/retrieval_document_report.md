# Historical Retrieval Documents Construction & Graph Audit Report

## 1. Executive Summary
This report details the construction and verification of the historical customer support retrieval document corpus for AmazonHelp.
Each retrieval document encapsulates **one historical support decision point** (`Customer Message` + `Relevant Previous Context` + `Historical Amazon Support Response`), with full provenance metadata maintained.

---
## 2. Core Quantitative Inventory
| Metric | Value | Description |
| :--- | :---: | :--- |
| **Raw AmazonHelp Cases** | 168,439 | Total rows in `amazon_support_cases.parquet` |
| **Reconstructed Conversations** | 82,555 | Distinct conversation trees |
| **Total Tweet Graph Nodes** | 323,097 | Individual tweet nodes reconstructed |
| **Customer Tweet Nodes** | 154,658 | Distinct customer tweets |
| **Brand Tweet Nodes** | 168,439 | Distinct AmazonHelp replies |
| **Root Tweet Nodes** | 82,555 | Conversation initiations (inbound or broadcast) |
| **Golden V1 Cases Excluded** | **510** | Belongs to the 200 locked Golden conversations |
| **Golden Conversation Leakage** | **0 (VERIFIED)** | Strict disjointness assertion passed |
| **Missing Customer Message Exclusions** | 163 | Empty customer text |
| **Missing Brand Response Exclusions** | 2 | Empty brand reply |
| **Duplicate Interaction Exclusions** | 0 | Identical customer->brand pair |
| **Final Valid Retrieval Documents** | **167,764** | Available for embedding & retrieval |

---
## 3. Conversation Graph Structural Dynamics
- **Multiple Responses to Same Customer Tweet**: 12,224 customer tweets received multiple brand replies (e.g. multi-part replies `1/2`, `2/2` or agent follow-ups).
- **Branching Conversations**: 9,868 conversations had branching reply threads.
- **Unresolved Parent Pointers**: 0 (0.0% of non-root nodes had missing parents within threads).

---
## 4. Preceding Context Statistics
- **Average Preceding Context Turns**: 1.93 turns
- **Median Preceding Context Turns**: 1.0 turns
- **Maximum Preceding Context Turns Capped**: 6 turns
- **Single-Turn Interactions (0 Preceding Turns)**: 69,668 (41.5%)

---
## 5. Corpus Quality & Linguistic Distribution
- **English (`en`) Documents**: 123,602 (73.7%)
- **Non-English Documents Flagged**: 44,162
- **`OK` Quality Documents**: 161,161 (96.1%)
- **Low Quality / Short Text Flagged**: 6,603

---
## 6. Output Artifact Verification
- **Target File**: `data/processed/retrieval_documents.parquet`
- **Total Rows Saved**: 167,764
- **Columns (16)**: `document_id, case_id, conversation_id, turn_index, customer_tweet_id, brand_response_tweet_id, customer_message, relevant_context, brand_response, selected_context_tweet_ids, selected_context_scores, created_at, thread_length, language, quality_status, embedding_text`
- **Embedding Field**: `embedding_text` (contains formatted `CUSTOMER:` + `RELEVANT CONTEXT:` + `AMAZON RESPONSE:`)