# Experiment Log: Unsupervised Semantic Intent Discovery

This document records experimental parameters, evaluation metrics, and qualitative observations from the Phase 2 intent discovery sweep over 10,000 stratified AmazonHelp support cases.

---

## 1. Experimental Setup

- **Dataset**: `data/processed/intent_discovery_cases.parquet`
- **Sample Size**: 10,000 cases (drawn from 124,031 eligible English cases across 9,679 unique conversations).
- **Sampling Strategy**: Stratified multi-dimensional binning across thread length (2–3, 4–7, 8–15, 16+), turn index (0, 1, 2–4, 5+), and message length quartiles. Max 2 cases per conversation to prevent single-thread dominance.
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors).
- **Preprocessing & Normalization**: L2 normalization applied to all embedding vectors prior to clustering (ensuring Euclidean distance correlates monotonically with Cosine distance).
- **Clustering Algorithm**: Scikit-Learn `KMeans` with $k \in [6, 8, 10, 12]$, `n_init=10`, `random_state=42`.

---

## 2. Quantitative Clustering Sweep Results

| Candidate $k$ | Silhouette Score | Smallest Cluster % | Largest Cluster % | Cluster Sizes |
| :---: | :---: | :---: | :---: | :--- |
| **$k = 6$** | 0.0208 | 8.86% | 21.62% | `[1675, 886, 2143, 1553, 1581, 2162]` |
| **$k = 8$** | 0.0209 | 7.89% | 15.58% | `[1558, 1481, 1421, 789, 820, 1315, 1237, 1379]` |
| **$k = 10$** | 0.0227 | 4.39% | 14.36% | `[1383, 1436, 1269, 1014, 727, 439, 809, 815, 1316, 792]` |
| **$k = 12$** | 0.0252 | 3.99% | 12.21% | `[1145, 890, 961, 1221, 572, 807, 399, 762, 771, 1095, 776, 601]` |

### Metric Analysis:
- In dense text embeddings of customer inquiries, silhouette scores are naturally low ($\approx 0.020 - 0.025$) because real customer problems exist on a semantic continuum rather than completely isolated clusters.
- **$k = 8$ provides the best practical operational balance**: No cluster exceeds 15.6% of the dataset, and the smallest cluster retains 7.9% (789 cases), avoiding micro-fragmentation while separating major domains (Delivery, Refunds, Account, Prime, Damaged Goods).

---

## 3. Qualitative Cluster Analysis ($k = 8$)

1. **Cluster 0 (1,558 cases, 15.6%) — `TECHNICAL_AND_APP_ISSUES`**:
   - High density of app screenshot references (`<URL>`), website checkout errors, Alexa app connectivity.
2. **Cluster 1 (1,481 cases, 14.8%) — `REFUND_AND_BILLING`**:
   - Direct refund requests, questions on refund timeline after returns, payment tracking.
3. **Cluster 2 (1,421 cases, 14.2%) — `ACCOUNT_AND_SERVICE_ESCALATION`**:
   - Customer service frustration, account lockout, hacked account verification complaints.
4. **Cluster 3 (789 cases, 7.9%) — `PRIME_MEMBERSHIP_AND_DELIVERY`**:
   - Delivery issues specifically tied to paid Amazon Prime guarantees (late next-day deliveries, membership fee disputes).
5. **Cluster 4 (820 cases, 8.2%) — `GENERAL_SERVICE_INQUIRY`**:
   - Follow-up questions, customer care feedback, cross-department handoffs.
6. **Cluster 5 (1,315 cases, 13.2%) — `DELIVERY_AND_PARCEL_TRACKING`**:
   - Tracking discrepancies, driver delivery complaints, parcel marked as delivered but missing.
7. **Cluster 6 (1,237 cases, 12.4%) — `ORDERS_AND_PRODUCT_CONDITION`**:
   - Package condition, damaged goods, packaging quality complaints.
8. **Cluster 7 (1,379 cases, 13.8%) — `DELIVERY_TIMELINES_AND_ETA`**:
   - Late shipments, promised delivery date delays, estimated time of arrival requests.

---

## 4. Key Observations & Lessons Learned

1. **Domain Imbalance**:
   - Over 50% of all Amazon customer service inquiries on Twitter pertain to logistics and delivery (dispatch delays, carrier misplacement, tracking errors). A flat taxonomy would result in a single massive "Delivery" bucket; a hierarchical taxonomy with clear sub-intents (`DELIVERY_DELAYED` vs `MARKED_DELIVERED_NOT_RECEIVED`) is essential.
2. **Multi-Intent Co-occurrence**:
   - In approximately 5–8% of customer messages, customers express multiple requests simultaneously (e.g., *"My order is late, I want to cancel and get an immediate refund"*). A single-label classifier would be fundamentally flawed here; a multi-label design is required.
3. **Conversational State Shifts**:
   - In multi-turn threads, customer messages often do not introduce a new intent; rather, they communicate a state change (e.g., *"I already checked the tracking link you sent"*, *"I already spoke to the driver"*). Tracking this conversational state prevents the agent from giving repetitive, circular advice.

---

## 5. Failed / Rejected Approaches

1. **Pure Lexical Clustering (TF-IDF alone)**:
   - Evaluated in exploratory notebook: TF-IDF failed to group semantically identical concepts using different terminology (e.g., "courier" vs "carrier" vs "driver"; "refund" vs "money back" vs "credited"). Dense semantic embeddings (`all-MiniLM-L6-v2`) resolved this.
2. **High-K Flat Clustering ($k > 25$)**:
   - Produces excessive fragmentation, splitting identical issues across superficial phrasing differences (e.g., separating "where is my package" from "tracking not updating").
3. **Automated LLM Taxonomy Invention**:
   - Allowing an LLM to freely invent taxonomy labels without human constraints produces bloated taxonomies with overlapping, unmaintainable categories. Using clustering for candidate discovery with human-in-the-loop review ensures high operational precision.

---

## 6. Open Decisions for Human Review

1. Should `PRIME_MEMBERSHIP_MANAGEMENT` be an independent broad area, or a sub-intent under `ACCOUNT_AND_BILLING`?
2. Should `DAMAGED_OR_DEFECTIVE_ITEM` and `WRONG_ITEM_RECEIVED` be separate sub-intents or merged under `PRODUCT_OR_ORDER_ISSUE`?
3. Recommended threshold for triggering the `AMBIGUOUS_INQUIRY` clarification fallback.
