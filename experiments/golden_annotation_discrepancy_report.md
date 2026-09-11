# Golden Annotation Discrepancy Report (Assistant-Reviewed Draft vs Proposed Labels)

> **IMPORTANT NOTICE**: The annotations in the `human_*` columns are an **assistant-reviewed pre-annotation draft** and do **NOT** constitute final human ground truth. `taxonomy_v1.yaml` and `golden_v1` remain strictly unlocked pending human sign-off.

## 1. Executive Summary

- **Total Cases Evaluated**: 200
- **Preserved `proposed_*` Columns**: 100% verified intact across all 200 cases.
- **Total Discrepant Rows (Intent OR Status OR Escalate)**: **63** / 200 (31.5%)
  - **Status Discrepancies** (`proposed_status != human_status`): **23** cases
  - **Intent Discrepancies** (multi-label `proposed_intents != human_intents`): **55** cases
  - **Primary Intent Discrepancies** (`proposed_primary_intent != human_primary_intent`): **48** cases
  - **Escalation Discrepancies** (`proposed_should_escalate != human_should_escalate`): **5** cases
- **Cases with Review Flags (`review_flags`)**: **22** cases
  - Flagged cases with discrepancy: 10
  - Flagged cases with label agreement (flagged for review/taxonomy note): 12
- **Combined Review Focus (Discrepant OR Flagged)**: **75** / 200 cases

## 2. Status Discrepancy Breakdown (23 cases)

| Status Transition | Count | Business Rationale & Pattern |
|---|:---:|---|
| `AMBIGUOUS` -> `NORMAL` | 5 | Prior conversation context or tracking timeline provided enough grounding to resolve specific leaf intents (`DELIVERY_DELAYED`, `ACCOUNT_LOGIN_ISSUES`, `WHERE_IS_MY_ORDER`). |
| `OUT_OF_SCOPE` -> `NORMAL` | 6 | Context showed actionable ecommerce issues (`DELIVERY_DELAYED`, `REFUND_STATUS_INQUIRY`, `CARRIER_FEEDBACK_AND_INSTRUCTIONS`, `PRIME_MEMBERSHIP_MANAGEMENT`) rather than unhandleable inquiries. |
| `NORMAL` -> `OUT_OF_SCOPE` | 5 | Inquiries concerned seller central, general website typo/app glitches, Kindle Fire TV internet connection, or third-party payment/RuPay wallet OTP issues outside consumer retail scope. |
| `NORMAL` -> `AMBIGUOUS` | 2 | Generic dissatisfaction text without actionable detail (`gold_0050`) or ambiguous intent like requesting to *stop* an order cancellation (`gold_0114`). |
| `OUT_OF_SCOPE` -> `AMBIGUOUS` | 2 | Generic customer venting / sarcastic remarks without an actionable goal (`gold_0032`, `gold_0035`). |
| `AMBIGUOUS` -> `OUT_OF_SCOPE` | 2 | Pure seller central support (`gold_0020`) or retail product stock inquiry (`gold_0021`). |

## 3. Escalation Discrepancy Breakdown (5 cases)

All 5 escalation discrepancies transitioned from `proposed_should_escalate: False` to `human_should_escalate: True`:

| Gold ID | Proposed Escalate | Draft Escalate | Draft Escalation Reason | Summary & Customer Message |
|---|:---:|:---:|---|---|
| `gold_0011` | `False` | **`True`** | `REPEATED_FAILED_SUPPORT_ATTEMPTS` | Is it necessary to send fax ?? Can't we send email with supporting docum... |
| `gold_0022` | `False` | **`True`** | `REPEATED_FAILED_SUPPORT_ATTEMPTS` | No, a resolution was not offered, nor did they attempt to call me back. |
| `gold_0064` | `False` | **`True`** | `ACCOUNT_SECURITY_COMPROMISE` | My account was hacked. Way too much time with them trying to get this fi... |
| `gold_0105` | `False` | **`True`** | `ACCOUNT_SECURITY_COMPROMISE` | my seller account has been hacked and I kept getting the same run around... |
| `gold_0106` | `False` | **`True`** | `ACCOUNT_SECURITY_COMPROMISE` | my account has had the email and password changed so i cant log in. |

## 4. Key Intent Shift Patterns (56 cases)

The 56 intent adjustments fall into distinct, recurring systematic patterns:
1. **Delivery Granularity Corrections** (15+ cases): Correcting misattribution between `WHERE_IS_MY_ORDER`, `DELIVERY_DELAYED`, and `MARKED_DELIVERED_NOT_RECEIVED`. E.g., cases where tracking falsely claimed delivery were corrected from `WHERE_IS_MY_ORDER` or `CARRIER_FEEDBACK_AND_INSTRUCTIONS` to `MARKED_DELIVERED_NOT_RECEIVED`.
2. **Carrier Feedback vs Delivery Problem** (6 cases): Messages complaining about courier misconduct, refusal to deliver to address, or asking customer to pick up parcel were corrected to `CARRIER_FEEDBACK_AND_INSTRUCTIONS`.
3. **Return Pickup vs Delivery/Refund** (7 cases): Undelivered parcels returned to sender by courier were corrected from `RETURN_PICKUP_ISSUE` to `DELIVERY_DELAYED`; refund disputes after returns were corrected to `REFUND_STATUS_INQUIRY`.
4. **Secondary Multi-Intent Annotations** (9 cases): Capturing dual customer issues such as Prime renewal + unauthorized charge, or wrong item + refund status.
5. **Domain/Category Disambiguation** (3 cases): Fixing digital content/game DLC mislabeled as carrier feedback, or website glitch mislabeled as digital content.

## 5. Review Flags Breakdown (22 cases)

The assistant review draft added explicit `review_flags` to 22 cases requiring human attention:

| Review Flag | Count | Cases | Meaning & Required Human Action |
|---|:---:|---|---|
| `CONTEXT_MAY_DISAMBIGUATE` | 9 | `gold_0015`, `gold_0016`, `gold_0018`, `gold_0019`, `gold_0024`, `gold_0025`, `gold_0032`, `gold_0050`, `gold_0114` | The isolated customer turn is underspecified, but previous conversation history provides strong clues. Human reviewer must decide whether turn-level or thread-level context governs label. |
| `ACCOUNT_COMPROMISE_REVIEW` | 5 | `gold_0006`, `gold_0007`, `gold_0008`, `gold_0064`, `gold_0105` | Account hacking / compromised account cases. Currently forced into `ACCOUNT_LOGIN_ISSUES` with `should_escalate: True`. Human must confirm whether to keep under login or flag for Taxonomy v2. |
| `TAXONOMY_GAP_REVIEW` | 5 | `gold_0020`, `gold_0113`, `gold_0141`, `gold_0167`, `gold_0182` | Cases highlighting boundaries or missing concepts (e.g. Seller Central, hardware Fire TV connection, reverse order cancellation). |
| `OUT_OF_SCOPE_DECISION_REVIEW` | 2 | `gold_0021`, `gold_0098` | Cases at the edge of scope (product availability inquiry, third-party payment/RuPay OTP). |
| `OUT_OF_SCOPE_DECISION_REVIEW\|TAXONOMY_GAP_REVIEW` | 1 | `gold_0102` | Amazon Pay wallet reload OTP failure — third-party banking/wallet boundary. |

## 6. Complete Table of All 63 Discrepancy Rows

Below is the complete inventory of all 63 cases where proposed labels differ from the assistant-reviewed draft in intent, status, or escalation:

| Gold ID | Customer Message Snippet | Proposed Status | Draft Status | Proposed Intents (Primary) | Draft Intents (Primary) | Prop Esc | Draft Esc | Draft Notes |
|---|---|---|---|---|---|:---:|:---:|---|
| `gold_0011` | Is it necessary to send fax ?? Can't we send email with s... | `AMBIGUOUS` | **NORMAL** | `nan (nan)` | **ACCOUNT_LOGIN_ISSUES (ACCOUNT_LOGIN_ISSUES)** | `False` | **True** | Context shows account held for about two weeks and repeated document/fax atte... |
| `gold_0012` | was expecting 2 packages by 16/10/17 - still not received... | `AMBIGUOUS` | **NORMAL** | `nan (nan)` | **DELIVERY_DELAYED (DELIVERY_DELAYED)** | `False` | False | Expected delivery date had passed. |
| `gold_0013` | people at +12062662992 not helpful at all. | `AMBIGUOUS` | **NORMAL** | `nan (nan)` | **WHERE_IS_MY_ORDER (WHERE_IS_MY_ORDER)** | `False` | False | Context says an item was never received; current message complains about supp... |
| `gold_0017` | UPS website says delayed due to unexpected circumstances.... | `AMBIGUOUS` | **NORMAL** | `nan (nan)` | **DELIVERY_DELAYED (DELIVERY_DELAYED)** | `False` | False | Customer explicitly reports a carrier delay. |
| `gold_0020` | Need support on seller central | `AMBIGUOUS` | **OUT_OF_SCOPE** | `nan (nan)` | nan (nan) | `False` | False | Seller Central support is outside the chosen consumer-support taxonomy. |
| `gold_0021` | when to get redmi5A on amazon? | `AMBIGUOUS` | **OUT_OF_SCOPE** | `nan (nan)` | nan (nan) | `False` | False | Product-availability question is outside the frozen support taxonomy. |
| `gold_0022` | No, a resolution was not offered, nor did they attempt to... | `AMBIGUOUS` | **NORMAL** | `nan (nan)` | **DELIVERY_DELAYED (DELIVERY_DELAYED)** | `False` | **True** | Context shows an overdue Prime order plus a failed prior support interaction;... |
| `gold_0026` | Button popped up today for a refund. I requested it. Than... | `OUT_OF_SCOPE` | **NORMAL** | `nan (nan)` | **DELIVERY_DELAYED (DELIVERY_DELAYED)** | `False` | False | The current turn confirms a refund request, but the active support case is st... |
| `gold_0027` | It looks like its now been remarked as out for delivery, ... | `OUT_OF_SCOPE` | **NORMAL** | `nan (nan)` | **DELIVERY_DELAYED (DELIVERY_DELAYED)** | `False` | False | Context says the order was late/out for delivery for over 48 hours. |
| `gold_0028` | Fake company#wl nt return your money evn aftr returning i... | `OUT_OF_SCOPE` | **NORMAL** | `nan (nan)` | **REFUND_STATUS_INQUIRY (REFUND_STATUS_INQUIRY)** | `False` | False | Explicit refund-not-received complaint. |
| `gold_0029` | I have done yeah. I don't agree with the fact the money w... | `OUT_OF_SCOPE` | **NORMAL** | `nan (nan)` | **REFUND_STATUS_INQUIRY (REFUND_STATUS_INQUIRY)** | `False` | False | Context explicitly discusses waiting for a refund. |
| `gold_0030` | Thanks once again for over promising and under delivering... | `OUT_OF_SCOPE` | **NORMAL** | `nan (nan)` | **DELIVERY_DELAYED (DELIVERY_DELAYED)** | `False` | False | Explicit same-day delivery delay. |
| `gold_0031` | Shout out to for ruining Christmas, delivering my dad's C... | `OUT_OF_SCOPE` | **NORMAL** | `nan (nan)` | **CARRIER_FEEDBACK_AND_INSTRUCTIONS (CARRIER_FEEDBACK_AND_INSTRUCTIONS)** | `False` | False | Complaint concerns delivery handling/packaging and carrier conduct. |
| `gold_0032` | Dear , Great experience. Thank for that waste of time yes... | `OUT_OF_SCOPE` | **AMBIGUOUS** | `nan (nan)` | nan (nan) | `False` | False | Generic sarcastic service complaint without a sufficiently specific actionabl... |
| `gold_0034` | Hey I didn't sign up for Prime, why is my account giving ... | `OUT_OF_SCOPE` | **NORMAL** | `nan (nan)` | **PRIME_MEMBERSHIP_MANAGEMENT (PRIME_MEMBERSHIP_MANAGEMENT)** | `False` | False | Prime membership signup/charge concern. |
| `gold_0035` | worst experience of my online shopping, congratulations o... | `OUT_OF_SCOPE` | **AMBIGUOUS** | `nan (nan)` | nan (nan) | `False` | False | Generic dissatisfaction without a distinct actionable support request. |
| `gold_0037` | Amazon double charged me && the payments have been pendin... | `NORMAL` | NORMAL | `UNRECOGNIZED_OR_DUPLICATE_CHARGE/CANCEL_ORDER_REQUEST (UNRECOGNIZED_OR_DUPLICATE_CHARGE)` | **UNRECOGNIZED_OR_DUPLICATE_CHARGE (UNRECOGNIZED_OR_DUPLICATE_CHARGE)** | `False` | False | Current message describes duplicate charges and pending payment resolution; n... |
| `gold_0041` | delivered defective product on orderid 4__credit_card__ ,... | `NORMAL` | NORMAL | `DAMAGED_OR_DEFECTIVE_ITEM/RETURN_PICKUP_ISSUE (DAMAGED_OR_DEFECTIVE_ITEM)` | **DAMAGED_OR_DEFECTIVE_ITEM/RETURN_PICKUP_ISSUE (RETURN_PICKUP_ISSUE)** | `False` | False | The immediate blocker is the failed pickup; defect is the underlying return c... |
| `gold_0043` | frnd ordered kindle wich was not delivered.He canceled or... | `NORMAL` | NORMAL | `WHERE_IS_MY_ORDER/CANCEL_ORDER_REQUEST (CANCEL_ORDER_REQUEST)` | **DELIVERY_DELAYED/CANCEL_ORDER_REQUEST/REFUND_STATUS_INQUIRY (REFUND_STATUS_INQUIRY)** | `False` | False | Undelivered/cancelled order with refund now being denied; multi-intent. |
| `gold_0046` | I canceled my order by mistake.... Pls contact- 8655123588 | `NORMAL` | NORMAL | `CANCEL_ORDER_REQUEST/UNRECOGNIZED_OR_DUPLICATE_CHARGE (CANCEL_ORDER_REQUEST)` | **CANCEL_ORDER_REQUEST (CANCEL_ORDER_REQUEST)** | `False` | False | Closest available intent is cancellation; note that the customer actually wan... |
| `gold_0047` | It was originally expected Tuesday (yesterday) and then I... | `NORMAL` | NORMAL | `DELIVERY_DELAYED/MODIFY_ORDER_DETAILS (DELIVERY_DELAYED)` | **DELIVERY_DELAYED (DELIVERY_DELAYED)** | `False` | False | Context explicitly states original date passed and a delay notice was received. |
| `gold_0048` | my order#408-5604067-5477926 supposed to be delivered by ... | `NORMAL` | NORMAL | `WHERE_IS_MY_ORDER/MODIFY_ORDER_DETAILS (WHERE_IS_MY_ORDER)` | **WHERE_IS_MY_ORDER (WHERE_IS_MY_ORDER)** | `False` | False | Current turn only asks for status before the promised date. |
| `gold_0049` | I would also like to point out that this is the SECOND ti... | `NORMAL` | NORMAL | `DAMAGED_OR_DEFECTIVE_ITEM/REFUND_STATUS_INQUIRY (DAMAGED_OR_DEFECTIVE_ITEM)` | **MARKED_DELIVERED_NOT_RECEIVED (MARKED_DELIVERED_NOT_RECEIVED)** | `False` | False | Full context clearly describes delivery to the wrong house / proof mismatch; ... |
| `gold_0050` | this is how your executives text ... Horrible service eve... | `NORMAL` | **AMBIGUOUS** | `RETURN_PICKUP_ISSUE/REFUND_STATUS_INQUIRY (RETURN_PICKUP_ISSUE)` | **nan (nan)** | `False` | False | Current turn is a generic service complaint; earlier context indicates a retu... |
| `gold_0051` | Have filled enough forms. Filled this one too. #Amazon cu... | `NORMAL` | NORMAL | `REFUND_STATUS_INQUIRY/CANCEL_ORDER_REQUEST (REFUND_STATUS_INQUIRY)` | **MARKED_DELIVERED_NOT_RECEIVED (MARKED_DELIVERED_NOT_RECEIVED)** | `False` | False | Context is dominated by conflicting delivery status and lack of proof; curren... |
| `gold_0052` | Please check the Echo & Alexa page on the website. May ha... | `NORMAL` | **OUT_OF_SCOPE** | `DIGITAL_CONTENT_ACCESS/PRIME_MEMBERSHIP_MANAGEMENT (DIGITAL_CONTENT_ACCESS)` | **nan (nan)** | `False` | False | Website typo/feedback without a clear support problem is outside the selected... |
| `gold_0053` | this is what the app says <URL> | `NORMAL` | NORMAL | `DIGITAL_CONTENT_ACCESS/PRIME_MEMBERSHIP_MANAGEMENT (DIGITAL_CONTENT_ACCESS)` | **DELIVERY_DELAYED (DELIVERY_DELAYED)** | `False` | False | Context is a preorder that missed its release-day shipping; current message i... |
| `gold_0054` | This is from the app <URL> | `NORMAL` | **OUT_OF_SCOPE** | `DIGITAL_CONTENT_ACCESS/REFUND_STATUS_INQUIRY (DIGITAL_CONTENT_ACCESS)` | **nan (nan)** | `False` | False | Context is general Amazon website/app failure rather than digital-content acc... |
| `gold_0055` | Can't be refunded until the order is despatched and then ... | `NORMAL` | NORMAL | `RETURN_PICKUP_ISSUE/REFUND_STATUS_INQUIRY (RETURN_PICKUP_ISSUE)` | **DELIVERY_DELAYED/REFUND_STATUS_INQUIRY (DELIVERY_DELAYED)** | `False` | False | Context is a delayed order plus refund of a shipping charge. |
| `gold_0060` | i pay for prime, note for delivery was to leave package a... | `NORMAL` | NORMAL | `MARKED_DELIVERED_NOT_RECEIVED (MARKED_DELIVERED_NOT_RECEIVED)` | **DELIVERY_DELAYED (DELIVERY_DELAYED)** | `False` | False | Delivery was attempted and pushed to another day; not marked delivered. |
| `gold_0061` | just delivered a package to our house and the address isn... | `NORMAL` | NORMAL | `MARKED_DELIVERED_NOT_RECEIVED (MARKED_DELIVERED_NOT_RECEIVED)` | **CARRIER_FEEDBACK_AND_INSTRUCTIONS (CARRIER_FEEDBACK_AND_INSTRUCTIONS)** | `False` | False | Complaint concerns misdelivery to the wrong address / carrier behavior, not t... |
| `gold_0062` | Helping me and said it's amazon's problem | `NORMAL` | NORMAL | `CARRIER_FEEDBACK_AND_INSTRUCTIONS (CARRIER_FEEDBACK_AND_INSTRUCTIONS)` | **DIGITAL_CONTENT_ACCESS (DIGITAL_CONTENT_ACCESS)** | `False` | False | Missing FIFA DLC is a digital-content access/support issue, not a carrier pro... |
| `gold_0064` | My account was hacked. Way too much time with them trying... | `NORMAL` | NORMAL | `ACCOUNT_LOGIN_ISSUES (ACCOUNT_LOGIN_ISSUES)` | ACCOUNT_LOGIN_ISSUES (ACCOUNT_LOGIN_ISSUES) | `False` | **True** | The current taxonomy lacks a dedicated compromised-account leaf; retain close... |
| `gold_0081` | The item is being returned undelivered by the courier | `NORMAL` | NORMAL | `RETURN_PICKUP_ISSUE (RETURN_PICKUP_ISSUE)` | **DELIVERY_DELAYED (DELIVERY_DELAYED)** | `False` | False | Item is being returned undelivered by courier; context says no delivery after... |
| `gold_0084` | Returned given to ur courier, have hand written receipt b... | `NORMAL` | NORMAL | `RETURN_PICKUP_ISSUE (RETURN_PICKUP_ISSUE)` | **REFUND_STATUS_INQUIRY (REFUND_STATUS_INQUIRY)** | `False` | False | Current message is about refund denial/non-receipt after a return, not the ph... |
| `gold_0098` | can't use my rupay card to make payments/add balance on a... | `NORMAL` | **OUT_OF_SCOPE** | `ACCOUNT_LOGIN_ISSUES (ACCOUNT_LOGIN_ISSUES)` | **nan (nan)** | `False` | False | Amazon Pay/payment + OTP issue is not represented by the frozen business taxo... |
| `gold_0102` | it takes a lot of time to add Money to Amazon Pay wallet.... | `NORMAL` | **OUT_OF_SCOPE** | `ACCOUNT_LOGIN_ISSUES (ACCOUNT_LOGIN_ISSUES)` | **nan (nan)** | `False` | False | Amazon Pay wallet/OTP issue is outside the frozen business taxonomy. |
| `gold_0105` | my seller account has been hacked and I kept getting the ... | `NORMAL` | NORMAL | `ACCOUNT_LOGIN_ISSUES (ACCOUNT_LOGIN_ISSUES)` | ACCOUNT_LOGIN_ISSUES (ACCOUNT_LOGIN_ISSUES) | `False` | **True** | Compromised seller account; current taxonomy lacks a dedicated security-compr... |
| `gold_0106` | my account has had the email and password changed so i ca... | `NORMAL` | NORMAL | `ACCOUNT_LOGIN_ISSUES (ACCOUNT_LOGIN_ISSUES)` | ACCOUNT_LOGIN_ISSUES (ACCOUNT_LOGIN_ISSUES) | `False` | **True** | Unauthorized email/password change indicates account compromise; current taxo... |
| `gold_0114` | how to stop cancel of order Order # 406-5465885-2121917 | `NORMAL` | **AMBIGUOUS** | `CANCEL_ORDER_REQUEST (CANCEL_ORDER_REQUEST)` | **nan (nan)** | `False` | False | Wording asks to stop a cancellation rather than request a new cancellation; c... |
| `gold_0116` | So claims that I was handed my delivery today at half pas... | `NORMAL` | NORMAL | `CARRIER_FEEDBACK_AND_INSTRUCTIONS (CARRIER_FEEDBACK_AND_INSTRUCTIONS)` | **MARKED_DELIVERED_NOT_RECEIVED (MARKED_DELIVERED_NOT_RECEIVED)** | `False` | False | Tracking claims the order was handed to the customer, but it was not received. |
| `gold_0120` | my parcel was delivered to a neighbour yesterday, I've as... | `NORMAL` | NORMAL | `CARRIER_FEEDBACK_AND_INSTRUCTIONS (CARRIER_FEEDBACK_AND_INSTRUCTIONS)` | **MARKED_DELIVERED_NOT_RECEIVED (MARKED_DELIVERED_NOT_RECEIVED)** | `False` | False | Parcel was marked/delivered to a neighbour but cannot be found. |
| `gold_0124` | just had to make a complaint regarding wrong item sent to... | `NORMAL` | NORMAL | `DAMAGED_OR_DEFECTIVE_ITEM (DAMAGED_OR_DEFECTIVE_ITEM)` | **WRONG_ITEM_RECEIVED (WRONG_ITEM_RECEIVED)** | `False` | False | Customer explicitly says the wrong item was sent. |
| `gold_0125` | Ordered and received a product which is defective.Request... | `NORMAL` | NORMAL | `DAMAGED_OR_DEFECTIVE_ITEM (DAMAGED_OR_DEFECTIVE_ITEM)` | **DAMAGED_OR_DEFECTIVE_ITEM/RETURN_PICKUP_ISSUE (RETURN_PICKUP_ISSUE)** | `False` | False | Defect plus missed return pickup; current complaint is about the pending pickup. |
| `gold_0141` | I hv observed tht kindle fire TV disconnects from interne... | `NORMAL` | **OUT_OF_SCOPE** | `DIGITAL_CONTENT_ACCESS (DIGITAL_CONTENT_ACCESS)` | **nan (nan)** | `False` | False | Kindle Fire TV connectivity problem is device/network support rather than dig... |
| `gold_0144` | The guy that was delivering it cancelled my order saying ... | `NORMAL` | NORMAL | `MARKED_DELIVERED_NOT_RECEIVED (MARKED_DELIVERED_NOT_RECEIVED)` | **CANCEL_ORDER_REQUEST/REFUND_STATUS_INQUIRY (REFUND_STATUS_INQUIRY)** | `False` | False | Order cancellation happened and the customer now disputes refund eligibility. |
| `gold_0145` | I didn’t . The app told me it would come today then chang... | `NORMAL` | NORMAL | `MARKED_DELIVERED_NOT_RECEIVED (MARKED_DELIVERED_NOT_RECEIVED)` | **DELIVERY_DELAYED (DELIVERY_DELAYED)** | `False` | False | Delivery date moved from today to a later range; not a delivered-but-missing ... |
| `gold_0146` | When your app says your order will be delivered today by ... | `NORMAL` | NORMAL | `MARKED_DELIVERED_NOT_RECEIVED (MARKED_DELIVERED_NOT_RECEIVED)` | **DELIVERY_DELAYED (DELIVERY_DELAYED)** | `False` | False | Expected delivery time has passed with no delivery. |
| `gold_0148` | After being told by your support my package will be here ... | `NORMAL` | NORMAL | `MARKED_DELIVERED_NOT_RECEIVED (MARKED_DELIVERED_NOT_RECEIVED)` | **DELIVERY_DELAYED (DELIVERY_DELAYED)** | `False` | False | Explicit six-day delay. |
| `gold_0149` | hi, I ordered 6 of an item and 2 arrived this morning. Th... | `NORMAL` | NORMAL | `MARKED_DELIVERED_NOT_RECEIVED (MARKED_DELIVERED_NOT_RECEIVED)` | **WHERE_IS_MY_ORDER (WHERE_IS_MY_ORDER)** | `False` | False | Customer is trying to track remaining shipments. |
| `gold_0155` | My order was delivered to the wrong address. | `NORMAL` | NORMAL | `MODIFY_ORDER_DETAILS (MODIFY_ORDER_DETAILS)` | **MARKED_DELIVERED_NOT_RECEIVED (MARKED_DELIVERED_NOT_RECEIVED)** | `False` | False | Customer's own order was delivered to the wrong address, so it was not received. |
| `gold_0157` | I keep getting charged for Amazon Prime but when I try to... | `NORMAL` | NORMAL | `PRIME_MEMBERSHIP_MANAGEMENT (PRIME_MEMBERSHIP_MANAGEMENT)` | **PRIME_MEMBERSHIP_MANAGEMENT/ACCOUNT_LOGIN_ISSUES (PRIME_MEMBERSHIP_MANAGEMENT)** | `False` | False | Active Prime billing/cancellation issue plus inability to access the account. |
| `gold_0161` | My prime account just got renewed and I really need to ca... | `NORMAL` | NORMAL | `PRIME_MEMBERSHIP_MANAGEMENT (PRIME_MEMBERSHIP_MANAGEMENT)` | **PRIME_MEMBERSHIP_MANAGEMENT/REFUND_STATUS_INQUIRY (PRIME_MEMBERSHIP_MANAGEMENT)** | `False` | False | Prime renewal cancellation with refund request. |
| `gold_0162` | I was charged for Amazon prime membership but I don't eve... | `NORMAL` | NORMAL | `PRIME_MEMBERSHIP_MANAGEMENT (PRIME_MEMBERSHIP_MANAGEMENT)` | **PRIME_MEMBERSHIP_MANAGEMENT/UNRECOGNIZED_OR_DUPLICATE_CHARGE (PRIME_MEMBERSHIP_MANAGEMENT)** | `False` | False | Prime charge is not recognized, so two actionable aspects are present. |
| `gold_0171` | My courier never came to.my home ordered by amazon. And t... | `NORMAL` | NORMAL | `RETURN_PICKUP_ISSUE (RETURN_PICKUP_ISSUE)` | **DELIVERY_DELAYED (DELIVERY_DELAYED)** | `False` | False | Courier returned the order without delivery; this is an undelivered/failed de... |
| `gold_0174` | Disappointed that a Guaranteed delivery not made! Courier... | `NORMAL` | NORMAL | `RETURN_PICKUP_ISSUE (RETURN_PICKUP_ISSUE)` | **CARRIER_FEEDBACK_AND_INSTRUCTIONS (CARRIER_FEEDBACK_AND_INSTRUCTIONS)** | `False` | False | Courier misconduct/asking customer to collect the package is the central comp... |
| `gold_0175` | Correct. It was scanned as "delivered. Available for pick... | `NORMAL` | NORMAL | `RETURN_PICKUP_ISSUE (RETURN_PICKUP_ISSUE)` | **MARKED_DELIVERED_NOT_RECEIVED (MARKED_DELIVERED_NOT_RECEIVED)** | `False` | False | Tracking status indicates available/delivered while customer still does not h... |
| `gold_0176` | Yeah! I already received a refund for the shipping costs ... | `NORMAL` | NORMAL | `RETURN_PICKUP_ISSUE (RETURN_PICKUP_ISSUE)` | **DELIVERY_DELAYED/REFUND_STATUS_INQUIRY (DELIVERY_DELAYED)** | `False` | False | Delayed order plus shipping-cost refund context. |
| `gold_0186` | pls check, my order # 404-5726716-4364338 not received by... | `NORMAL` | NORMAL | `WHERE_IS_MY_ORDER (WHERE_IS_MY_ORDER)` | **MARKED_DELIVERED_NOT_RECEIVED (MARKED_DELIVERED_NOT_RECEIVED)** | `False` | False | Explicit delivered-but-not-received case. |
| `gold_0187` | I got a message that your order has been delivered but th... | `NORMAL` | NORMAL | `WHERE_IS_MY_ORDER (WHERE_IS_MY_ORDER)` | **MARKED_DELIVERED_NOT_RECEIVED (MARKED_DELIVERED_NOT_RECEIVED)** | `False` | False | Explicit delivered notification but package not received. |
| `gold_0189` | The latest on the tracking details is just out for delive... | `NORMAL` | NORMAL | `WHERE_IS_MY_ORDER (WHERE_IS_MY_ORDER)` | **DELIVERY_DELAYED (DELIVERY_DELAYED)** | `False` | False | Out-for-delivery since yesterday with no delivery. |
| `gold_0193` | refunded me when I returned a product but took the money ... | `NORMAL` | NORMAL | `WRONG_ITEM_RECEIVED (WRONG_ITEM_RECEIVED)` | **WRONG_ITEM_RECEIVED/REFUND_STATUS_INQUIRY (WRONG_ITEM_RECEIVED)** | `False` | False | Wrong item is the root problem; refund reversal is a secondary actionable issue. |
| `gold_0198` | Order no. 171-8264819-8281921. I have ordered the product... | `NORMAL` | NORMAL | `WRONG_ITEM_RECEIVED (WRONG_ITEM_RECEIVED)` | **WHERE_IS_MY_ORDER (WHERE_IS_MY_ORDER)** | `False` | False | Customer is asking for status of an order not yet dispatched; no explicit mis... |

## 7. Additional Flagged Rows Without Discrepancy (12 cases)

| Gold ID | Status | Intents (Primary) | Escalate | Review Flag | Human Notes |
|---|---|---|:---:|---|---|
| `gold_0006` | `NORMAL` | `ACCOUNT_LOGIN_ISSUES (ACCOUNT_LOGIN_ISSUES)` | `True` | `ACCOUNT_COMPROMISE_REVIEW` | Assistant-reviewed pre-annotation; human sign-off still required. |
| `gold_0007` | `NORMAL` | `ACCOUNT_LOGIN_ISSUES (ACCOUNT_LOGIN_ISSUES)` | `True` | `ACCOUNT_COMPROMISE_REVIEW` | Assistant-reviewed pre-annotation; human sign-off still required. |
| `gold_0008` | `NORMAL` | `ACCOUNT_LOGIN_ISSUES (ACCOUNT_LOGIN_ISSUES)` | `True` | `ACCOUNT_COMPROMISE_REVIEW` | Assistant-reviewed pre-annotation; human sign-off still required. |
| `gold_0015` | `AMBIGUOUS` | `nan (nan)` | `False` | `CONTEXT_MAY_DISAMBIGUATE` | Assistant-reviewed pre-annotation; human sign-off still required. |
| `gold_0016` | `AMBIGUOUS` | `nan (nan)` | `False` | `CONTEXT_MAY_DISAMBIGUATE` | Assistant-reviewed pre-annotation; human sign-off still required. |
| `gold_0018` | `AMBIGUOUS` | `nan (nan)` | `False` | `CONTEXT_MAY_DISAMBIGUATE` | Assistant-reviewed pre-annotation; human sign-off still required. |
| `gold_0019` | `AMBIGUOUS` | `nan (nan)` | `False` | `CONTEXT_MAY_DISAMBIGUATE` | Assistant-reviewed pre-annotation; human sign-off still required. |
| `gold_0024` | `AMBIGUOUS` | `nan (nan)` | `False` | `CONTEXT_MAY_DISAMBIGUATE` | Assistant-reviewed pre-annotation; human sign-off still required. |
| `gold_0025` | `AMBIGUOUS` | `nan (nan)` | `False` | `CONTEXT_MAY_DISAMBIGUATE` | Assistant-reviewed pre-annotation; human sign-off still required. |
| `gold_0113` | `NORMAL` | `CANCEL_ORDER_REQUEST (CANCEL_ORDER_REQUEST)` | `False` | `TAXONOMY_GAP_REVIEW` | Assistant-reviewed pre-annotation; human sign-off still required. |
| `gold_0167` | `NORMAL` | `REFUND_STATUS_INQUIRY (REFUND_STATUS_INQUIRY)` | `False` | `TAXONOMY_GAP_REVIEW` | Assistant-reviewed pre-annotation; human sign-off still required. |
| `gold_0182` | `NORMAL` | `UNRECOGNIZED_OR_DUPLICATE_CHARGE (UNRECOGNIZED_OR_DUPLICATE_CHARGE)` | `False` | `TAXONOMY_GAP_REVIEW` | Assistant-reviewed pre-annotation; human sign-off still required. |