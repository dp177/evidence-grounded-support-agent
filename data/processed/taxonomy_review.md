# Human Review Table: AmazonHelp Hierarchical Intent Taxonomy

This reference table outlines the candidate intent taxonomy derived from 10,000 AmazonHelp support cases for pair-programming and human review.

---

## Broad Area: DELIVERY_AND_FULFILLMENT

### Candidate Intent: WHERE_IS_MY_ORDER
- **Definition**: Customer requests the current tracking location, carrier dispatch status, or estimated delivery date of an order that is within or near the promised delivery window.
- **Positive Examples**:
  - *"Where is my package? The tracking number hasn't updated since yesterday morning."* (case `amazon_case_0098653`)
  - *"Can you please tell me when order #408-5604067 will be delivered?"* (case `amazon_case_0152499`)
  - *"Is my item out for delivery today? Tracking says preparing for dispatch."* (case `amazon_case_0048826`)
- **Confusable With**: `DELIVERY_DELAYED` (when tracking estimate has already elapsed).
- **Decision**: **KEEP**

---

### Candidate Intent: DELIVERY_DELAYED
- **Definition**: Customer reports that the guaranteed or estimated delivery date has passed without arrival, and the package is overdue.
- **Positive Examples**:
  - *"My order was supposed to arrive yesterday. Tracker now says 'delayed, we are sorry'. When is it coming?"* (case `amazon_case_0036794`)
  - *"Paid for next day Prime delivery on Friday, it is now Tuesday and still nothing."* (case `amazon_case_0025122`)
  - *"Still waiting on package 3 weeks later! Absolutely unacceptable delay."* (case `amazon_case_0000000`)
- **Confusable With**: `WHERE_IS_MY_ORDER` (when customer asks where order is without stating it is past due), `MARKED_DELIVERED_NOT_RECEIVED` (when delivery status is digitally completed).
- **Decision**: **KEEP**

---

### Candidate Intent: MARKED_DELIVERED_NOT_RECEIVED
- **Definition**: Carrier tracking records show the parcel was delivered (e.g. "handed to resident" or "left on porch"), but the customer physically did not receive it.
- **Positive Examples**:
  - *"Fed up with this, parcel is marked as delivered but no delivery was made."* (case `amazon_case_0005594`)
  - *"Amazon app alert just stated delivery at door, but I was sitting right here and no one came."* (case `amazon_case_0164697`)
  - *"Says delivered to front porch at 2pm. Nothing is on my porch. Please investigate."* (case `amazon_case_0015604`)
- **Confusable With**: `DELIVERY_DELAYED` (customer assumes delayed shipment was prematurely marked delivered).
- **Decision**: **KEEP**

---

### Candidate Intent: CARRIER_FEEDBACK_AND_INSTRUCTIONS
- **Definition**: Specific complaints or instructions regarding carrier personnel, courier damage to property, safe-place placement, gate codes, or international customs clearance.
- **Positive Examples**:
  - *"Your courier left my package out in the pouring rain instead of putting it in the porch."* (case `amazon_case_0042191`)
  - *"Driver was extremely rude and refused to bring heavy parcel upstairs."* (case `amazon_case_0143327`)
  - *"Ordered an Alexa and it is stuck in customs asking for KYC upload document."* (case `amazon_case_0067847`)
- **Confusable With**: `DELIVERY_DELAYED` (customs delay vs carrier conduct).
- **Decision**: **KEEP**

---

## Broad Area: RETURNS_AND_REPLACEMENTS

### Candidate Intent: DAMAGED_OR_DEFECTIVE_ITEM
- **Definition**: The correct ordered item arrived, but is physically broken, cracked, leaking, expired, or non-functional.
- **Positive Examples**:
  - *"The screen on my Kindle arrived shattered inside the box."* (case `amazon_case_0042191`)
  - *"Package arrived crushed and the shampoo bottle had spilled all over everything."* (case `amazon_case_0112122`)
  - *"Item won't turn on even after charging. Defective out of the box."* (case `amazon_case_0015604`)
- **Confusable With**: `WRONG_ITEM_RECEIVED` (damaged item vs incorrect item).
- **Decision**: **KEEP**

---

### Candidate Intent: WRONG_ITEM_RECEIVED
- **Definition**: The package arrived in good condition, but contained a completely different item, incorrect size, or different color/variant than what was purchased.
- **Positive Examples**:
  - *"I ordered a blue winter coat size L and received a red pair of sneakers."* (case `amazon_case_0015604`)
  - *"You sent me the wrong book completely. Invoice says chemistry, box had a novel."* (case `amazon_case_0036794`)
  - *"Received wrong model of headphones, ordered wireless version."* (case `amazon_case_0098653`)
- **Confusable With**: `DAMAGED_OR_DEFECTIVE_ITEM`.
- **Decision**: **KEEP**

---

### Candidate Intent: RETURN_PICKUP_ISSUE
- **Definition**: Customer has already initiated a return or replacement, but the logistics carrier failed to pick up the return package or the return drop-off label failed.
- **Positive Examples**:
  - *"Courier never showed up today for the scheduled return pickup for order #405-7027."* (case `amazon_case_0001850`)
  - *"Return pickup was supposed to happen yesterday, waited home all day."* (case `amazon_case_0132871`)
  - *"The return drop-off barcode is not scanning at the post office."* (case `amazon_case_0109139`)
- **Confusable With**: `REFUND_STATUS_INQUIRY` (return process vs refund credit).
- **Decision**: **KEEP**

---

## Broad Area: REFUNDS_AND_BILLING

### Candidate Intent: REFUND_STATUS_INQUIRY
- **Definition**: Customer returned an item or cancelled an order and is inquiring about the timeline, status, or bank credit of their refund.
- **Positive Examples**:
  - *"I returned order #405-7027922 a week ago. When will the refund credit my bank?"* (case `amazon_case_0001850`)
  - *"Your email said refund issued on Monday, still not showing in my account."* (case `amazon_case_0132871`)
  - *"How many business days does an Amazon gift card refund take?"* (case `amazon_case_0094446`)
- **Confusable With**: `UNAUTHORIZED_OR_DUPLICATE_CHARGE`.
- **Decision**: **KEEP**

---

### Candidate Intent: UNAUTHORIZED_OR_DUPLICATE_CHARGE
- **Definition**: Customer discovers duplicate charges, unauthorized credit card deductions, or unexplained billing amounts on their statement.
- **Positive Examples**:
  - *"I was charged twice on my Visa card for the exact same order #403-728."* (case `amazon_case_0001850`)
  - *"There is a £7.99 charge from Amazon on my statement that I never authorized."* (case `amazon_case_0114638`)
  - *"Why was my card debited after I cancelled the order?"* (case `amazon_case_0034643`)
- **Confusable With**: `REFUND_STATUS_INQUIRY`, `PRIME_MEMBERSHIP_MANAGEMENT` (when unrecognized charge is Prime fee).
- **Decision**: **RENAME** $\rightarrow$ `UNRECOGNIZED_OR_DUPLICATE_CHARGE`

---

## Broad Area: ORDER_MANAGEMENT

### Candidate Intent: CANCEL_ORDER_REQUEST
- **Definition**: Customer requests cancellation of an active order prior to shipment dispatch.
- **Positive Examples**:
  - *"I accidentally ordered two of these. Please cancel order #104-569 immediately."* (case `amazon_case_0034643`)
  - *"Need to cancel my order before it ships out, please assist."* (case `amazon_case_0132871`)
  - *"Cancel button is missing on the app, stop this order!"* (case `amazon_case_0001850`)
- **Confusable With**: `MODIFY_ORDER_DETAILS`, `DELIVERY_DELAYED` (demanding cancellation due to delay).
- **Decision**: **KEEP**

---

### Candidate Intent: MODIFY_ORDER_DETAILS
- **Definition**: Customer wishes to change delivery address, payment method, delivery instructions, or shipping speed on an active order while keeping it open.
- **Positive Examples**:
  - *"I put in my old apartment address by mistake. Can I update the shipping address?"* (case `amazon_case_0034643`)
  - *"Can I switch payment method from debit to credit card on pending order?"* (case `amazon_case_0098653`)
  - *"Need to change delivery day to Saturday when I will be home."* (case `amazon_case_0036794`)
- **Confusable With**: `CANCEL_ORDER_REQUEST` (when customer threatens to cancel if address cannot be changed).
- **Decision**: **KEEP**

---

## Broad Area: DIGITAL_SERVICES_AND_PRIME

### Candidate Intent: PRIME_MEMBERSHIP_MANAGEMENT
- **Definition**: Inquiries concerning Amazon Prime benefits, unwanted subscription auto-renewals, student Prime status, or membership cancellations.
- **Positive Examples**:
  - *"Did not mean to sign up for Prime auto-renewal, please cancel and refund the £79."* (case `amazon_case_0025122`)
  - *"How do I transfer my Prime membership to my new email?"* (case `amazon_case_0001276`)
  - *"Why am I paying for Prime if next day shipping is never available?"* (case `amazon_case_0164697`)
- **Confusable With**: `DIGITAL_CONTENT_ACCESS`.
- **Decision**: **KEEP**

---

### Candidate Intent: DIGITAL_CONTENT_ACCESS
- **Definition**: Technical issues with digital streaming, Kindle ebooks, Audible audiobooks, Fire TV devices, or app purchase errors.
- **Positive Examples**:
  - *"Prime Video app keeps giving error code 5004 on my Samsung TV."* (case `amazon_case_0024894`)
  - *"Purchased Kindle book is not downloading to my device."* (case `amazon_case_0131432`)
  - *"Echo Dot won't link to my Amazon Music account."* (case `amazon_case_0086351`)
- **Confusable With**: `PRIME_MEMBERSHIP_MANAGEMENT`.
- **Decision**: **KEEP**

---

## Broad Area: ACCOUNT_ACCESS_AND_SECURITY

### Candidate Intent: ACCOUNT_LOGIN_OR_OTP
- **Definition**: Problems logging into Amazon account, OTP verification code not arriving, account lockout, suspected hacked account, or password resets.
- **Positive Examples**:
  - *"Cannot log in. OTP verification SMS is never delivered to my phone."* (case `amazon_case_0017954`)
  - *"My account was compromised/hacked and someone changed the email address."* (case `amazon_case_0012827`)
  - *"Password reset link expired before I received it."* (case `amazon_case_0114638`)
- **Confusable With**: `UNRECOGNIZED_OR_DUPLICATE_CHARGE` (when hack involves unauthorized orders).
- **Decision**: **RENAME** $\rightarrow$ `ACCOUNT_ACCESS_AND_LOGIN`

---

## Multi-Intent

In approximately 6–8% of support cases, customers express multiple distinct actionable needs in a single message.
**Design Principle:** Never create combinatorial hybrid labels (e.g. `CANCEL_AND_REFUND` is prohibited). Model as a set of active intents:

1. **`CANCEL_ORDER_REQUEST` + `REFUND_STATUS_INQUIRY`**:
   - *"Please cancel my order #403-7284574 and let me know when the refund will hit my card."*
2. **`DELIVERY_DELAYED` + `CANCEL_ORDER_REQUEST`**:
   - *"Package is a week late, please cancel the order, I don't want it anymore."*
3. **`DAMAGED_OR_DEFECTIVE_ITEM` + `WRONG_ITEM_RECEIVED`**:
   - *"Not only did you send the wrong model, but the box was also damaged and torn open."*
4. **`UNRECOGNIZED_OR_DUPLICATE_CHARGE` + `PRIME_MEMBERSHIP_MANAGEMENT`**:
   - *"You charged me twice for Prime membership renewal; cancel Prime and refund the extra debit."*

---

## Fallbacks

1. **`AMBIGUOUS_INQUIRY`**:
   - Inquiries that are under-specified and require follow-up clarification before routing.
   - *Example:* *"Can someone please help me with an issue?"*, *"Please check my DM sent an hour ago."*
   - *Action:* Agent asks for order number, product name, or issue description.
2. **`MULTI_INTENT`**:
   - Handled via multi-label classification output (`active_intents: [intent_a, intent_b]`).
3. **`OUT_OF_SCOPE`**:
   - Comments, compliments, political commentary, stock inquiries, or brand feedback that does not constitute an actionable customer support ticket.
   - *Example:* *"Amazon stock is soaring today, congratulations Jeff Bezos!"*

---

## Conversation States

In multi-turn dialogues, the customer's state progresses even if the core intent remains unchanged:

1. **`INITIAL_INQUIRY`**: First turn presenting the problem statement.
2. **`TRACKING_ALREADY_CHECKED`**: Customer has already consulted tracking link and reports that it does not answer their question (*"I already checked tracking, it's stuck in transit"*).
   - *Agent Rule:* Do not repetitively advise checking the tracking link; initiate carrier trace.
3. **`CARRIER_ALREADY_CONTACTED`**: Customer has already spoken with the carrier (*"The courier told me they lost the package and to contact Amazon"*).
   - *Agent Rule:* Do not deflect to carrier; initiate replacement or refund.
4. **`DETAILS_ALREADY_PROVIDED`**: Customer has already provided order ID or DM info (*"I already sent my order number twice"*).
   - *Agent Rule:* Do not ask for order ID again; check queue and acknowledge.
5. **`WAITING_WINDOW_EXCEEDED`**: Promised waiting window has passed (*"I was told to wait 48 hours; it has now been 4 days"*).
   - *Agent Rule:* Immediate human escalation / concession review.
6. **`RESOLVED_CLOSURE`**: Issue resolved; customer expressing thanks.
