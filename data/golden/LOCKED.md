# Golden Evaluation Set — LOCKED

**Version:** `golden_v1`  
**Status:** `LOCKED`  
**Brand:** `AmazonHelp`  
**Taxonomy Reference:** `Taxonomy v1 (configs/taxonomy_v1.yaml)`  
**Creation Date:** `2026-09-12`  
**Case Count:** `200`  
**Conversation Count:** `200`  

---

## Strict Usage & Governance Constraints

1. **Not Training Data**:
   The Golden Evaluation Set (`data/golden/golden_set.jsonl`) must NEVER be used as training data, fine-tuning data, few-shot prompt examples, or model optimization data.

2. **Not Part of Retrieval Corpus**:
   No case and NO conversation appearing in the golden evaluation set may be indexed into any FAISS vector store, BM25 index, lexical index, or RAG retrieval corpus.

3. **Strict Conversation Isolation**:
   All 200 conversation IDs in this set are completely isolated from the development and training pool. No other turns or cases belonging to these 200 conversations may enter downstream pipelines.

4. **Immutability & Versioning**:
   The golden set is frozen and immutable. It may only be modified by establishing a new version identifier (e.g., `golden_v2`).

5. **Taxonomy Alignment**:
   Any future modifications to the taxonomy (e.g., Taxonomy v1.1+) require generating a corresponding new versioned golden evaluation set rather than modifying `golden_v1`.
