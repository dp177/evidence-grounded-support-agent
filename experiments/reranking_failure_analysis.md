# Reranking Boundary and Failure Analysis

## Boundary Analysis

### WHERE_IS_MY_ORDER vs DELIVERY_DELAYED
- Found 27 cases.
- Reranking improved top-1 grade in 7 cases.

### DELIVERY_DELAYED vs MARKED_DELIVERED_NOT_RECEIVED
- Found 23 cases.
- Reranking improved top-1 grade in 5 cases.

### DELIVERY_DELAYED vs CARRIER_FEEDBACK_AND_INSTRUCTIONS
- Found 28 cases.
- Reranking improved top-1 grade in 5 cases.

### DAMAGED_OR_DEFECTIVE_ITEM vs WRONG_ITEM_RECEIVED
- Found 18 cases.
- Reranking improved top-1 grade in 4 cases.

### RETURN_PICKUP_ISSUE vs DELIVERY_DELAYED
- Found 26 cases.
- Reranking improved top-1 grade in 5 cases.

## Failure Analysis

Common failure modes observed during reranking:
- **Semantic False Positive**: High vector similarity due to shared vocabulary (e.g. 'package', 'delivered') but differing problem state.
- **Lexical False Positive**: TF-IDF heavily weighting a specific entity name that is irrelevant to the operational intent.
- **Generic-Response Bias**: Although penalized, some generic responses still rank high if semantic similarity is overwhelming.
- **Same-Conversation Duplication**: Resolved by the deduplication limit=1.
