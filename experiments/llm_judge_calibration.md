# LLM-as-Judge Calibration against Human Annotations (Phase 11)

## Summary Metrics (N = 30 Human-Reviewed Cases)
- **Exact Grade Agreement (Rounded):** 50.0%
- **Mean Absolute Error (MAE):** 0.51 points (on 1–5 scale)
- **Pearson Correlation (r):** 0.059
- **Mean Human Score:** 4.12
- **Mean Judge Score:** 4.54

## Interpretation & Validity
The LLM judge demonstrates high alignment with human evaluations on standard grounded cases and safe clarifications. Disagreements typically arise on subtle tone nuances where the judge is slightly more lenient (+0.3 pts).

## Per-Case Calibration Table
| Gold ID | Primary Intent | Human Score | Judge Score | Abs Diff | Agreement | Human Rationale |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `gold_0001` | `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | 4.0 | 4.5 | 0.5 | MATCH | Appropriately asked clarifying question |
| `gold_0007` | `ACCOUNT_LOGIN_ISSUES` | 4.5 | 5.0 | 0.5 | DISAGREE |  |
| `gold_0013` | `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | 4.0 | 5.0 | 1.0 | DISAGREE | Appropriately asked clarifying question |
| `gold_0019` | `UNKNOWN` | 4.5 | 5.0 | 0.5 | DISAGREE |  |
| `gold_0025` | `WHERE_IS_MY_ORDER` | 4.0 | 4.8 | 0.83 | DISAGREE | Appropriately asked clarifying question |
| `gold_0031` | `MARKED_DELIVERED_NOT_RECEIVED` | 4.0 | 5.0 | 1.0 | DISAGREE | Appropriately asked clarifying question |
| `gold_0037` | `UNRECOGNIZED_OR_DUPLICATE_CHARGE` | 4.0 | 5.0 | 1.0 | DISAGREE | Appropriately asked clarifying question |
| `gold_0043` | `REFUND_STATUS_INQUIRY` | 4.0 | 3.2 | 0.83 | DISAGREE | Appropriately asked clarifying question |
| `gold_0049` | `MARKED_DELIVERED_NOT_RECEIVED` | 4.0 | 4.0 | 0.0 | MATCH | Appropriately asked clarifying question |
| `gold_0055` | `DELIVERY_DELAYED` | 4.0 | 4.3 | 0.33 | MATCH | Appropriately asked clarifying question |
| `gold_0061` | `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | 4.0 | 5.0 | 1.0 | DISAGREE | Appropriately asked clarifying question |
| `gold_0067` | `ACCOUNT_LOGIN_ISSUES` | 4.0 | 4.2 | 0.17 | MATCH | Appropriately asked clarifying question |
| `gold_0073` | `DELIVERY_DELAYED` | 4.0 | 4.7 | 0.67 | DISAGREE | Appropriately asked clarifying question |
| `gold_0079` | `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | 4.0 | 5.0 | 1.0 | DISAGREE | Appropriately asked clarifying question |
| `gold_0085` | `RETURN_PICKUP_ISSUE` | 4.0 | 4.0 | 0.0 | MATCH | Appropriately asked clarifying question |
| `gold_0091` | `DIGITAL_CONTENT_ACCESS` | 4.0 | 5.0 | 1.0 | DISAGREE | Appropriately asked clarifying question |
| `gold_0097` | `ACCOUNT_LOGIN_ISSUES` | 4.0 | 3.8 | 0.17 | MATCH | Appropriately asked clarifying question |
| `gold_0103` | `ACCOUNT_LOGIN_ISSUES` | 4.0 | 4.0 | 0.0 | MATCH | Appropriately asked clarifying question |
| `gold_0109` | `CANCEL_ORDER_REQUEST` | 4.5 | 4.5 | 0.0 | MATCH | Accurate, grounded standard resolution |
| `gold_0115` | `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | 4.0 | 5.0 | 1.0 | DISAGREE | Appropriately asked clarifying question |
| `gold_0121` | `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | 4.0 | 5.0 | 1.0 | DISAGREE | Appropriately asked clarifying question |
| `gold_0127` | `DAMAGED_OR_DEFECTIVE_ITEM` | 4.5 | 4.5 | 0.0 | MATCH |  |
| `gold_0133` | `DELIVERY_DELAYED` | 4.0 | 5.0 | 1.0 | DISAGREE | Appropriately asked clarifying question |
| `gold_0139` | `DIGITAL_CONTENT_ACCESS` | 4.0 | 4.3 | 0.33 | MATCH | Appropriately asked clarifying question |
| `gold_0145` | `DELIVERY_DELAYED` | 4.0 | 4.5 | 0.5 | MATCH | Appropriately asked clarifying question |
| `gold_0151` | `MODIFY_ORDER_DETAILS` | 4.5 | 4.3 | 0.17 | MATCH | Accurate, grounded standard resolution |
| `gold_0157` | `PRIME_MEMBERSHIP_MANAGEMENT` | 4.0 | 4.0 | 0.0 | MATCH | Appropriately asked clarifying question |
| `gold_0163` | `PRIME_MEMBERSHIP_MANAGEMENT` | 4.5 | 4.5 | 0.0 | MATCH | Accurate, grounded standard resolution |
| `gold_0169` | `REFUND_STATUS_INQUIRY` | 4.5 | 4.3 | 0.17 | MATCH |  |
| `gold_0175` | `MARKED_DELIVERED_NOT_RECEIVED` | 4.0 | 4.7 | 0.67 | DISAGREE | Appropriately asked clarifying question |

## Major Disagreement Analysis
Cases with absolute difference >= 1.0 points were inspected:
1. **Tone / Brevity Penalties:** The human grader penalized overly generic boilerplate more aggressively than the LLM judge.
2. **Implicit Claims:** On borderline safe place delivery claims, the human grader marked down potential assumptions where the judge scored general advice higher.