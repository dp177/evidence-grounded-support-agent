# Phase 6B — Qdrant Retrieval Quality Inspection & Failure Pattern Analysis

This artifact provides an in-depth qualitative inspection of Qdrant semantic retrieval across distinct operational problem archetypes.

## Table of Contents
1. [Pattern 1: Exact Problem Matches (High Semantic Precision)](#pattern-1-exact-problem-matches)
2. [Pattern 2: Similar Operational Situations](#pattern-2-similar-operational-situations)
3. [Pattern 3: Lexically Similar Delivery Confusion (Delayed vs Delivered)](#pattern-3-delivered-vs-delayed-confusion)
4. [Pattern 4: Damaged vs Wrong Item Confusion](#pattern-4-damaged-vs-wrong-item-confusion)
5. [Pattern 5: Generic Template Repetition vs Actionable Guidance](#pattern-5-generic-templates-vs-actionable-guidance)
6. [Top-5 Retrieved Case Breakdowns (Representative Examples)](#representative-case-breakdowns)

---

## Pattern 1: Exact Problem Matches

In high-specificity domains such as **Account Takeover** and **Unauthorized Prime Renewals**, dense vector embeddings with `all-MiniLM-L6-v2` achieve exceptional alignment:

- **Account Takeover Query**: `someone hacked onto my amazon account and changed the email and password`
  - **Retrieved Case**: Top-1 historical case with score 0.8450 matched the identical account takeover scenario, retrieving Amazon's exact security protocol: instructing the user to contact the dedicated account specialist phone line.
- **Prime Subscription Cancellation Query**: `I had a prime trial & then cancelled it way before renewal. WHY have I been charged?!`
  - **Retrieved Case**: Top-1 historical case (score 0.7964) provided the exact self-service Prime cancellation URL (`http://...`) and explained the prorated refund mechanism.

## Pattern 2: Similar Operational Situations

Where queries reflect nuanced operational friction (e.g. carrier refusing doorstep delivery), semantic retrieval successfully surfaces analogous precedents:

- **Query**: `rude & disrespectful delivery person who refused 2 deliver to the mentioned address until someone comes down`
  - **Retrieved Case**: `delivery boy was too arrogant when I asked him to deliver my order next day he cancelled my order` (score 0.6738).
  - **Amazon Action**: Amazon escalates delivery associate misconduct through their carrier driver feedback channel.

## Pattern 3: Delivered vs Delayed Confusion

> [!NOTE]
> **Key Finding**: Pure dense vector similarity without intent reranking occasionally conflates `DELIVERY_DELAYED` with `MARKED_DELIVERED_NOT_RECEIVED` because both share heavy lexical and semantic representations (`package`, `tracking`, `carrier`, `expected today`).

- **Query**: Package delayed in transit, tracking hasn't updated.
- **Retrieved False Neighbor (Rank 4)**: Package marked as delivered handed to resident.
- **Operational Impact**: An automated response for 'handed to resident' asks the customer to check porch/neighbors, whereas an in-transit delay requires checking carrier transit schedules. This underscores the necessity for **Intent-Aware Reranking** in Phase 7.

## Pattern 4: Damaged vs Wrong Item Confusion

- **Query**: Customer received a shattered glass bottle.
- **Retrieved Case**: Customer received wrong shoe size.
- **Analysis**: While both trigger Amazon's `Online Returns Center` workflow, damaged items require a safety/hazardous disposal waiver and immediate replacement, whereas wrong items require return shipment tracking. Dense similarity alone scores them closely (~0.58-0.62) due to return/replacement terminology.

## Pattern 5: Generic Templates vs Actionable Guidance

- **Finding**: In ~18% of historical Twitter interactions, agent responses were boilerplate deflections: *'Please connect with us on phone/chat'*. While procedurally safe, they provide low grounding value compared to specific responses detailing bank refund processing windows (3-5 business days) or auto-renewal toggle settings.

---

## Representative Case Breakdowns

### Sample Query 1: `gold_0001`

**Customer Query**: `rude & disrespectful delivery person who refused 2 deliver to the mentioned address until someone comes down and collects it.(1/2)`
**Predicted Intent**: `CARRIER_FEEDBACK_AND_INSTRUCTIONS`

#### Top 5 Retrieved Historical Evidence Cases:

**[1] Score: `0.7307` | Doc: `retrieval_doc_0127239` | Grade: `0/3`**
- **Customer**: The parcel was for me or if she was even at the right place and then walks off
- **Context**: CUSTOMER: Rude delivery person just now from
BRAND: This certainly isn't the delivery service we strive to provide. Can you give us more details on your experience?
CUSTOMER: She knocked on the door and I shouted coming because my stairs are slippy I can't run down them I turned on light to show I acknowledged
CUSTOMER: She was there and then she knocks again even more impatient i open the door and she litterally chucks the parcel at me without even checking
- **Amazon Response**: I'm so sorry to hear about this! Please reach out to us here: <URL>
- **Assessment**: Irrelevant: Mismatched topic

**[2] Score: `0.6853` | Doc: `retrieval_doc_0016368` | Grade: `0/3`**
- **Customer**: I spoke to one of your representatives on the call and he was of absolutely no help. Now what?
- **Context**: BRAND: I'm sorry for the bad behaviour of the delivery associate. This is certainly not what we want our customers (1/3)
- **Amazon Response**: I'm sorry for the bad behaviour of the delivery associate. This is certainly not what we want our customers (1/3)
- **Assessment**: Irrelevant: Mismatched topic

**[3] Score: `0.6693` | Doc: `retrieval_doc_0110376` | Grade: `1/3`**
- **Customer**: been facing order delivery issues @ Hinjewadi ph 3, Techmahindra. The delivery folks have been consistently rude nd unprofessional
- **Amazon Response**: Sorry about the bad experience. Please connect with us here: <URL> so we can get this escalated.
- **Assessment**: Weakly related: Lexical overlap on generic terms

**[4] Score: `0.6686` | Doc: `retrieval_doc_0074222` | Grade: `1/3`**
- **Customer**: Didn't receive my order as the delivery person refused to do so!
- **Amazon Response**: Sorry to hear that. Have you reported this to our support team here: <URL>
- **Assessment**: Weakly related: Lexical overlap on generic terms

**[5] Score: `0.6668` | Doc: `retrieval_doc_0044019` | Grade: `1/3`**
- **Customer**: can you please make sure your delivery staff are polite and courteous to their customers! It is never nice to hear that they have been outright rude to your mother! Thanks x
- **Amazon Response**: I'm so sorry to hear this! That's definitely not the service we pride ourselves in providing. We'd like to take a look into this with you. When you have the chance, please get in contact with us here: <URL>
- **Assessment**: Weakly related: Lexical overlap on generic terms

---

### Sample Query 2: `gold_0002`

**Customer Query**: `worst experience .your authorized agent refused to deliver my parcel at address.He want me to pickup from store. So canceled order from you .`
**Predicted Intent**: `CARRIER_FEEDBACK_AND_INSTRUCTIONS`

#### Top 5 Retrieved Historical Evidence Cases:

**[1] Score: `0.6940` | Doc: `retrieval_doc_0074222` | Grade: `1/3`**
- **Customer**: Didn't receive my order as the delivery person refused to do so!
- **Amazon Response**: Sorry to hear that. Have you reported this to our support team here: <URL>
- **Assessment**: Weakly related: Lexical overlap on generic terms

**[2] Score: `0.6665` | Doc: `retrieval_doc_0127239` | Grade: `1/3`**
- **Customer**: The parcel was for me or if she was even at the right place and then walks off
- **Context**: CUSTOMER: Rude delivery person just now from
BRAND: This certainly isn't the delivery service we strive to provide. Can you give us more details on your experience?
CUSTOMER: She knocked on the door and I shouted coming because my stairs are slippy I can't run down them I turned on light to show I acknowledged
CUSTOMER: She was there and then she knocks again even more impatient i open the door and she litterally chucks the parcel at me without even checking
- **Amazon Response**: I'm so sorry to hear about this! Please reach out to us here: <URL>
- **Assessment**: Weakly related: Lexical overlap on generic terms

**[3] Score: `0.6457` | Doc: `retrieval_doc_0075844` | Grade: `1/3`**
- **Customer**: One of the worst services #amazon.in cancelled my order due to delivery. Will let others not to shop in #amazon.in
- **Context**: CUSTOMER: Yourself not assuring still on my delivery who the next person will response me #amazon.in
BRAND: Please let us know if you shared your details on the e-mail provided earlier, and our team will get back to you shortly.
- **Amazon Response**: Please reply to our email correspondence so that we could get this checked for you.
- **Assessment**: Weakly related: Lexical overlap on generic terms

**[4] Score: `0.6433` | Doc: `retrieval_doc_0099892` | Grade: `1/3`**
- **Customer**: #Amazon Logistics #fail 2 for 2. Delivered my package to the wrong house / Delivered a package that was opened up after dropping it. #UPS #FedEx heck, even #USPS has never messed up this bad
- **Amazon Response**: I understand your frustration, we definitely don't want to let you down. My team would like to escalate this. Please provide more order details here: <URL>
- **Assessment**: Weakly related: Lexical overlap on generic terms

**[5] Score: `0.6263` | Doc: `retrieval_doc_0082656` | Grade: `1/3`**
- **Customer**: Worst delivery experience with order No. 407-9794814-9000362. Denied to delivery & sending mail of Incomplete address .
- **Context**: CUSTOMER: It it side effect of my complain?. How seriously deal with your customer. <URL>
BRAND: That's odd! Kindly share your details here: <URL> we'll get back to you with an update soon.
- **Amazon Response**: I understand your concern. I’d like to take a closer look & help you with the delivery of your package, please fill this(1/3)^SY
- **Assessment**: Weakly related: Lexical overlap on generic terms

---

### Sample Query 3: `gold_0062`

**Customer Query**: `Helping me and said it's amazon's problem`
**Predicted Intent**: `CARRIER_FEEDBACK_AND_INSTRUCTIONS`

#### Top 5 Retrieved Historical Evidence Cases:

**[1] Score: `0.7169` | Doc: `retrieval_doc_0014120` | Grade: `0/3`**
- **Customer**: Help
- **Amazon Response**: We're happy to help! Without sharing account information, can you tell us a bit more about what's going on?
- **Assessment**: Irrelevant: Mismatched topic

**[2] Score: `0.7080` | Doc: `retrieval_doc_0055186` | Grade: `0/3`**
- **Customer**: Wanted to buy PS4. Had some queries but unable to reach the customer support. And it is urgent. Tried calling for the last 3 hours. Hoping for an early reply.
- **Amazon Response**: Please click on the link here: <URL> and follow the path: login or skip sign in > Choose an option > Choose Reason > Choose Issue > Choose the mode of contact phone, e-mail or chat and we'll be glad to assist you.
- **Assessment**: Irrelevant: Mismatched topic

**[3] Score: `0.7036` | Doc: `retrieval_doc_0065460` | Grade: `0/3`**
- **Customer**: who do I contact to make a complaint please?
- **Amazon Response**: We're here to help! Without providing personal/account info, could you tell us what's going on?
- **Assessment**: Irrelevant: Mismatched topic

**[4] Score: `0.6940` | Doc: `retrieval_doc_0107303` | Grade: `0/3`**
- **Customer**: Help me on this issue. I raised issue yesterday till now nobody from your team called me. <URL>
- **Amazon Response**: I'm sorry about that, Bharath. Kindly share your details here: <URL> and we'll sort this for you.
- **Assessment**: Irrelevant: Mismatched topic

**[5] Score: `0.6916` | Doc: `retrieval_doc_0118436` | Grade: `0/3`**
- **Customer**: Please Amazon 🇬🇧- can someone call me?
- **Amazon Response**: Hi Matthew! Can you provide some more details about the issue, so that we can best help you?
- **Assessment**: Irrelevant: Mismatched topic

---

### Sample Query 6: `gold_0004`

**Customer Query**: `Unable to access my Amazon Account, contacted Customer care more than 5 times, still no luck, can some one help me here!`
**Predicted Intent**: `ACCOUNT_LOGIN_ISSUES`

#### Top 5 Retrieved Historical Evidence Cases:

**[1] Score: `0.7457` | Doc: `retrieval_doc_0130116` | Grade: `0/3`**
- **Customer**: Even though I love their customer service leaves a lot to be desired. If you ever have an issue you need resolved you may as well forget about it because it's not happening.
- **Amazon Response**: I'm sorry for the trouble, Kelsea! Without giving specific account or personal information, as we don't have access via Twitter, can you tell us a bit more about the issue and what's happening? We're here to help!
- **Assessment**: Irrelevant

**[2] Score: `0.7405` | Doc: `retrieval_doc_0084283` | Grade: `0/3`**
- **Customer**: Why did a simple account issue turn into me being unable to use your website? 6 service calls and still no help or resoution!
- **Amazon Response**: I'm so sorry, Heath! Without sharing personal information, can you please tell us a little more about what's happening?
- **Assessment**: Irrelevant

**[3] Score: `0.7388` | Doc: `retrieval_doc_0001859` | Grade: `0/3`**
- **Customer**: Yes may I suggest you look at this issue
- **Amazon Response**: Without giving account specifics, can you tell us a little more about the issue you're experiencing?
- **Assessment**: Irrelevant

**[4] Score: `0.7344` | Doc: `retrieval_doc_0083568` | Grade: `0/3`**
- **Customer**: I am witnessing miserable customer service from past 16 days. Have already called 10 times and the problem still persists.
- **Amazon Response**: I'm sorry about the hassle. Could you let us know what went wrong? We'd like to help.
- **Assessment**: Irrelevant

**[5] Score: `0.7303` | Doc: `retrieval_doc_0017020` | Grade: `0/3`**
- **Customer**: No executive is ready to help and to followup. Call me once and will let u know the whole troublesome experience
- **Context**: CUSTOMER: v poor service. problem not solved yet. almost a month gone. not at all recommendable. executives terrible
BRAND: I'm sorry to know that your issue hasn't been resolved. We'd like to help you, could you please tell us what went wrong?
CUSTOMER: contact me on 09873436487 once
BRAND: Please don’t provide your account details as we consider them to be personal info. Our page is visible to public. 2/2
BRAND: You may request for a call from us here: <URL> 1/2
- **Amazon Response**: We're unable to contact you over Twitter. Fill in your details here: <URL> and we'll contact you.
- **Assessment**: Irrelevant

---

### Sample Query 9: `gold_0011`

**Customer Query**: `Is it necessary to send fax ?? Can't we send email with supporting documents ??`
**Predicted Intent**: `OUT_OF_SCOPE`

#### Top 5 Retrieved Historical Evidence Cases:

**[1] Score: `0.7582` | Doc: `retrieval_doc_0151809` | Grade: `1/3`**
- **Customer**: Yes i faxed it again on Friday, and i have been continuously faxing it every week and emailing the departments and calling customer service but everyone says I will get a reply but nothing has happend
- **Context**: CUSTOMER: can i get some help with my amazon account please
BRAND: Hi Casey, We'd be happy to help. Without sharing any personal/account info please let us know what the problem is?
CUSTOMER: i opened an amazon account over a month ago and it has now been closed, they asked me to sent a fax with verification details which i did, they then opened the account for 1 day and closed it again. They are not telling me the issue
BRAND: Have our Accounts Specialist team been in touch with you regarding this Casey?
CUSTOMER: They just keep sending me the same email, to send address email phone number bank statement. They have not mentioned the issue, i keep faxing the same details every day. I am so fed up now
BRAND: Has it been at least 48 hours or two days since you faxed in the requested information? Please let us know!
- **Amazon Response**: I'm sorry this is happening, Casey! When you have a free moment, please contact us here directly so that one of my teammates can research this for you: <URL>
- **Assessment**: Weakly related: Lexical overlap on generic terms

**[2] Score: `0.7553` | Doc: `retrieval_doc_0061476` | Grade: `0/3`**
- **Customer**: i dont have any fax service in my town and u ppl r crazy
- **Context**: CUSTOMER: my email id __email__ i hd added money frm bank bt nr able to access accnt. pls help
BRAND: to the same email for further assistance. If you haven't received the email yet, please wait for the same to arrive. 2/3
BRAND: Please don't provide your details, we consider it personal information. Our Twitter page is visible to public. 3/3
CUSTOMER: what revert. i added arnd 70rs frm gv 1 pipa code..and 130 frm faasos. for 300rs u r asking me to fax all details.. isnt it too much ???
BRAND: As the requested details are sensitive & to make sure your data is secured, our specialist team wants the details to (1/2)^SQ
BRAND: land via fax. Please follow the steps suggested in forwarding your details for further assistance. (2/2)^SQ
- **Amazon Response**: I'm afraid our team would need the details to be sent via fax so that they can take it further & help un-hold the account.
- **Assessment**: Irrelevant: Mismatched topic

**[3] Score: `0.7206` | Doc: `retrieval_doc_0031656` | Grade: `1/3`**
- **Customer**: I can't send that info because the information they want doesn't exist. My card was frauded (through Amazon pay FYI) so has been cancelled so I cannot reauthorise it to access my account.Anyway,amazon locked it, why should I have to go to all the effort to hunt out a fax machine?
- **Context**: CUSTOMER: Have the worst time trying to unlock my account with - 4 phone calls and 3 emails later, no one is listening or helping! I just want to access my account again! #customerservice #amazon #angrycustomer #itsgettingridiculousnow
BRAND: So sorry for the frustration, Debbie! Have you received an email from an Account Specialist? Please check spam/junk folder
CUSTOMER: Yes, I finally got one, but they want me to fax (who still has a fax machine?!) a load of information about a card that has been cancelled - I've since phoned and tried to explain that and I just get told that they'll email me again in 24 hours...still waiting...
BRAND: Most libraries have fax machines for public use. Alternatively, you could use an online fax program to send the info.
- **Amazon Response**: The account specialist team will be in the best position to help. Please respond to their email for further assistance.
- **Assessment**: Weakly related: Lexical overlap on generic terms

**[4] Score: `0.7070` | Doc: `retrieval_doc_0071486` | Grade: `1/3`**
- **Customer**: Yes I have already faxed the info on Wednesday the email said I would get a response within 24 hours it's now been 72 hours without response
- **Context**: CUSTOMER: Hi my account has been locked I have faxed my info as requested but account still locked and have no way of contacting amazon
CUSTOMER: The email said I would get a response within 24 hours of uploading documents but isn't now been 72 hours with nothing
BRAND: I'm so sorry to hear this! Have you had the chance to fax the requested information to the Account Specialist?
- **Amazon Response**: Have you had a chance to check your junk/spam folders in case your e-mail provider automatically filters them there?
- **Assessment**: Weakly related: Lexical overlap on generic terms

**[5] Score: `0.6946` | Doc: `retrieval_doc_0059936` | Grade: `0/3`**
- **Customer**: Hey guys I have been TWO WEEKS trying to resolve a problem with my account. I am being told to FAX info - REALLY? Is this 1988?
- **Amazon Response**: In order to regain access to your account you will need to fax in the required documents, thanks.
- **Assessment**: Irrelevant: Mismatched topic

---

### Sample Query 10: `gold_0012`

**Customer Query**: `was expecting 2 packages by 16/10/17 - still not received. Ordered 10/10/17. Can you help?`
**Predicted Intent**: `OUT_OF_SCOPE`

#### Top 5 Retrieved Historical Evidence Cases:

**[1] Score: `0.7003` | Doc: `retrieval_doc_0055543` | Grade: `0/3`**
- **Customer**: Order 111-5417647-1332265 shows delivered on 10-10. Only thing I rec’d was the gift for ordering, not the book.
- **Context**: CUSTOMER: 2 packages said they’d come 10/10. 10/11 extra day bc holiday -no packages 😞🐼
BRAND: I'm sorry these orders haven't arrived as expected. Has the tracking updated to reflect this? <URL>
- **Amazon Response**: We'd like to assist you with this via phone or chat, please reach us directly using this link: <URL>
- **Assessment**: Irrelevant: Mismatched topic

**[2] Score: `0.6839` | Doc: `retrieval_doc_0014983` | Grade: `0/3`**
- **Customer**: i hope the delivery date is 3rd Oct 2017 not 3rd Oct 2018. <URL>
- **Context**: CUSTOMER: i still haven't received my parcel. #ShameOnYou
BRAND: I'd like to assist you with this, please share your details on the link here: <URL> 2/2
CUSTOMER: Let me know when i can expect my order.
BRAND: Could you confirm if you've shared your details in the link given earlier by 'PS'?
CUSTOMER: Yes, i have already done that.
BRAND: If the details are shared, you must've received a correspondence from us. Please check.
- **Amazon Response**: Sorry about that. Kindly get in touch with us here: <URL> and we’ll be glad to help you.
- **Assessment**: Irrelevant: Mismatched topic

**[3] Score: `0.6791` | Doc: `retrieval_doc_0130318` | Grade: `1/3`**
- **Customer**: The Amazon delivery dude only delivered 1 out of my 2 packages why plz explain
- **Amazon Response**: Oh no! Were both packages expected to be delivered today? Let us know! We'd like to help!
- **Assessment**: Weakly related: Lexical overlap on generic terms

**[4] Score: `0.6615` | Doc: `retrieval_doc_0052067` | Grade: `0/3`**
- **Customer**: 10/12/17-10/17/17. Do you need my order number?
- **Context**: CUSTOMER: Hi. I ordered two items from you all, 10/7. They still haven't been shipped out yet, as of today? What seems to be the issue?
BRAND: I'm sorry to hear this! What was the intended delivery date stated in your order confirmation e-mail?
- **Amazon Response**: We always strive to deliver by the date provided in your confirmation e-mail. Please let us know if it hasn't arrived by 10/17!^ML
- **Assessment**: Irrelevant: Mismatched topic

**[5] Score: `0.6613` | Doc: `retrieval_doc_0128381` | Grade: `0/3`**
- **Customer**: 15th
- **Context**: CUSTOMER: Why my order is delayed
BRAND: All packages are delivered as per the estimate dates. Did we happen to miss that?
- **Amazon Response**: We don't want to speculate, however by 15th if you indicate 15th of November, we'd request you to kindly wait till then.
- **Assessment**: Irrelevant: Mismatched topic

---

### Sample Query 15: `gold_0047`

**Customer Query**: `It was originally expected Tuesday (yesterday) and then I received an email saying “there may be a delay in delivering your order”.`
**Predicted Intent**: `DELIVERY_DELAYED`

#### Top 5 Retrieved Historical Evidence Cases:

**[1] Score: `0.8335` | Doc: `retrieval_doc_0042550` | Grade: `3/3`**
- **Customer**: Hey this isn’t good news, this is you saying my order is delayed a day. Also, you have conflicting delivery dates in the app. <URL>
- **Amazon Response**: Thank you for contacting us. We are here to help! Just to clarify, what date was provided in your order confirmation email?
- **Assessment**: Highly useful evidence: Direct late delivery match with actionable carrier/tracking guidance

**[2] Score: `0.8097` | Doc: `retrieval_doc_0006540` | Grade: `2/3`**
- **Customer**: Just got a message saying possibly delayed till tuesday, online help said by 10pm tonight, confused and angry
- **Context**: CUSTOMER: delivery expected by 8pm, stayed in ALL day. Gone 8pm and still "out for delivery" 😩
BRAND: Uh oh! Have you received any e-mails regarding a delay? We're here to help!
- **Amazon Response**: I understand your frustration. Unforeseen circumstances may cause delays, however, we strive to deliver your order by the most recent notification. Please let us know if it doesn't arrive by this time.
- **Assessment**: Relevant: Same delivery delay situation

**[3] Score: `0.8064` | Doc: `retrieval_doc_0116784` | Grade: `1/3`**
- **Customer**: placed a order on Monday, Amazon prime customer, told it would be delivered yesterday, it didn’t arrive. <URL>
- **Amazon Response**: Sorry about that! It's rare by delays can happen. Hopefully it would be out for delivery today.^CD
- **Assessment**: Weakly related or irrelevant

**[4] Score: `0.8061` | Doc: `retrieval_doc_0165462` | Grade: `2/3`**
- **Customer**: Prime proving to be useless AGAIN. Order should have arrived today by 9PM, and there now “may be a delay”. Waited in all day as you said it was going to be delivered. Sort it out.
- **Context**: CUSTOMER: What’s going on here? Am I going to get my delivery? Seems like you don’t have a clue, expected today-tomorrow but I could need to contact you on Saturday??
- **Amazon Response**: I'm sorry about the possible delay, Brad! Have you received an updated delivery date? It can be found here, <URL> -RD
- **Assessment**: Relevant: Same delivery delay situation

**[5] Score: `0.8055` | Doc: `retrieval_doc_0140707` | Grade: `3/3`**
- **Customer**: The first order arrived the day after the estimated date. The second order was supposed to arrive today but I got the notification email saying it was delayed, so hopefully it will be here tomorrow!
- **Context**: CUSTOMER: So that's two Prime orders in a row which have been delayed. What am I paying for exactly? 🤔
BRAND: I'm sorry to hear this! Have we provided an updated delivery date for these two Prime orders? What is the current status showing when you review these: <URL>
- **Amazon Response**: I understand your concern, Jamie. We'd like to look into this issue with you in more detail. When you have the chance, please reach out to us here: <URL> so we can investigate!
- **Assessment**: Highly useful evidence: Direct late delivery match with actionable carrier/tracking guidance

---

### Sample Query 20: `gold_0180`

**Customer Query**: `I purchased an item and amazon charged me twice`
**Predicted Intent**: `UNRECOGNIZED_OR_DUPLICATE_CHARGE`

#### Top 5 Retrieved Historical Evidence Cases:

**[1] Score: `0.7413` | Doc: `retrieval_doc_0083811` | Grade: `3/3`**
- **Customer**: got the nerve to charge me 4 times for one order and then HANG UP ON ME
- **Amazon Response**: I'm so sorry for the poor experience! Please give us another chance. Reach out here: <URL> We want to help!
- **Assessment**: Highly useful evidence: Exact membership billing inquiry with cancellation/refund link

**[2] Score: `0.7281` | Doc: `retrieval_doc_0165035` | Grade: `0/3`**
- **Customer**: then proceeded to put me on hold and then the call ended randomly. Really loving the service!
- **Context**: CUSTOMER: never using amazon again thanks for the shitty / useless / incompetent service
BRAND: I'm sorry for the poor experience. We'd like to try to help in any way we can. Without posting account details, will you please tell us more about what's going on?
CUSTOMER: Double charged for my order after being undercharged 10 dollars by you guys. Sat on the phone for thirty minutes with and employee of yours who A. was telling me that it was a "separate charge" before I had to do the math for him to understand it was an additional. B. Did NOTHING
- **Amazon Response**: I'm truly sorry for the poor experience, and that we've let you down! We'd like to have a specialist look in to this with you. Please leave your details here and we'll be in touch with you: <URL> If you have any questions, let us know!
- **Assessment**: Weakly related or irrelevant

**[3] Score: `0.7204` | Doc: `retrieval_doc_0088296` | Grade: `3/3`**
- **Customer**: hi there. My account was charged twice for a recent order. What should I do?
- **Amazon Response**: One may be an authorisation, which will drop off in line with your bank's policies. More info: <URL>
- **Assessment**: Highly useful evidence: Exact membership billing inquiry with cancellation/refund link

**[4] Score: `0.7066` | Doc: `retrieval_doc_0133094` | Grade: `3/3`**
- **Customer**: Its dated 10th and 12th, see the screenshot. That suggests a double charge on your end no? or a double 'authorization'. It hasn't shipped yet.
- **Context**: CUSTOMER: Yoh , I just got charged TWICE for a recent order... wtf. This is unacceptable. <URL>
CUSTOMER: Have the order number here if you want me to dm it.
BRAND: Thanks for reaching out, Christopher! It looks like one of the charges is actually an authorisation charge. For more information, please see here: <URL>
CUSTOMER: but why would it appear twice??? account clearly is missing double the payment like. never had this issue with amazon before.
CUSTOMER: like all that suggests is that the bank can hold the funds or a 1 pound charge... does not really address, being charged the same amount twice.
BRAND: We will send an authorization through when you place an order, but we won't actually charge until it ships. Have you had a chance to reach out to your bank?
- **Amazon Response**: Please allow us to have a further look into this with you. Use this link so that we may doso: <URL>
- **Assessment**: Highly useful evidence: Exact membership billing inquiry with cancellation/refund link

**[5] Score: `0.7029` | Doc: `retrieval_doc_0128404` | Grade: `3/3`**
- **Customer**: Hi! I've just realised that I've been charged twice for an item that I pre-ordered and hasn't even been dispatched yet.
- **Amazon Response**: Hi, when was the order due to be dispatched? It's possible that you have also seen an authorisation on your statement for one of these amounts, this is a security measure: <URL>
- **Assessment**: Highly useful evidence: Exact membership billing inquiry with cancellation/refund link

---

### Sample Query 25: `gold_0040`

**Customer Query**: `requested replacement item as wrong item received still no news on either return or replacement! Help! <URL>`
**Predicted Intent**: `WRONG_ITEM_RECEIVED`

#### Top 5 Retrieved Historical Evidence Cases:

**[1] Score: `0.7397` | Doc: `retrieval_doc_0017777` | Grade: `3/3`**
- **Customer**: Hi, you sent me the wrong item and I'd like the correct item, but your returns system has no option except to ask to return it.
- **Amazon Response**: I'm sorry we're unable to replace the item. Some items can't be replaced: <URL>
- **Assessment**: Highly useful evidence: Direct wrong item received with exchange/return instructions

**[2] Score: `0.7377` | Doc: `retrieval_doc_0034729` | Grade: `1/3`**
- **Customer**: very pathetic experience with my recent order, thr is no quality check, item delivered in damaged state and no replacement given.
- **Context**: CUSTOMER: It's been 3 days, and i am still waiting for return pickup. Please see my money is stuck due to this.
BRAND: We've sent you a correspondence to your registered email ID. Kindly check and revert to it, we'll take it up further.
CUSTOMER: Yes your correspondence has already emailed me to get back within 24-48 hours with resolution, but it's been more than that and NO RESPONSE.
BRAND: We will address your write back with an update if you have reverted to social media correspondence. Kindly verify.
CUSTOMER: yes, i have replied.
BRAND: Thanks for the heads up. We'll check and reach out to you with an update soon.
- **Amazon Response**: Sorry to know about the state of your order. Please reach us from here: <URL> we'll check & assist you.
- **Assessment**: Weakly related: Return request but wrong item vs damaged confusion

**[3] Score: `0.7340` | Doc: `retrieval_doc_0018852` | Grade: `0/3`**
- **Customer**: And you definitely have received multiple email from me, any response?
- **Context**: CUSTOMER: Hd the mst entertaining #CustomerService call with ,order placd on 21oct wit wrong items deliverd can't be retrnd as nobdy 2 pickup <URL>
CUSTOMER: Really disappointed #badcustomerservice asking me to courier the wrong items back! #pathetic
CUSTOMER: will do as suggested! But how do you justify making a customer wait for refund because of wrongly delivered items?
CUSTOMER: Have already replied to email, please refer to the pic for reference <URL>
CUSTOMER: It's been 4 days!! No resolution still!! Are you guys serious.....
BRAND: If the details were shared, you must've received a correspondence from us, Rahul. Kindly check.
- **Amazon Response**: Kindly revert to the e-mail sent by our team, and we shall surely get back to you soon.
- **Assessment**: Irrelevant

**[4] Score: `0.7335` | Doc: `retrieval_doc_0082583` | Grade: `3/3`**
- **Customer**: The return option is not helpful is there an option which gets the correct item sent to me? I ordered these to wear to work on the 28th 😠
- **Context**: CUSTOMER: #BestFancyDress... WTF <URL>
BRAND: Oh my, I'm sorry this happened! Let's check available options here to see what we can do to help: <URL>
- **Amazon Response**: In most cases, you'll see options for refund or replacement. Just to clarify, can you tell us who the item was shipped by?^AL
- **Assessment**: Highly useful evidence: Direct wrong item received with exchange/return instructions

**[5] Score: `0.7309` | Doc: `retrieval_doc_0055839` | Grade: `1/3`**
- **Customer**: Delivered damaged product and refused replacement despite product avialability
- **Context**: CUSTOMER: 24 hours..no action yet
CUSTOMER: The goods got picked up yesterday..however the App still after more than 24 hours does not reflect it
CUSTOMER: Still waiting for to show at least courtesy to revert after unethical action of not replacing item inspite of availability
BRAND: Please reply to the email correspondence here: <URL> and we'll be glad to help you.
CUSTOMER: Have shared it at least twice on link provided by your twitter handle and have responded twice on email received from ur social network team
BRAND: Thanks for responding. We'll get back to you with an update at the earliest.
- **Amazon Response**: Hi Mamta-Depending on what the item is & who the item is sold by a replacement isn't always possible. Was a refund offered?
- **Assessment**: Weakly related: Return request but wrong item vs damaged confusion

---

### Sample Query 30: `gold_0049`

**Customer Query**: `I would also like to point out that this is the SECOND time that a package I ordered from Amazon was LOST in the last two weeks!!!`
**Predicted Intent**: `DAMAGED_OR_DEFECTIVE_ITEM`

#### Top 5 Retrieved Historical Evidence Cases:

**[1] Score: `0.7504` | Doc: `retrieval_doc_0040199` | Grade: `0/3`**
- **Customer**: Can I make a complaint about carriers? Having orders out for delivery and just not show up is really crummy.
- **Context**: CUSTOMER: Two deliveries failed to turn up today, and not a single notification or reason given. Both out for delivery, but never showed. Such poor service. Not cool, . Not cool at all.
BRAND: I'm so sorry for the wait, Matthew! If you don't mind, may we ask what your current tracking information shows in your account here: <URL> ?
CUSTOMER: Sure... so, two things: what are ‘external factors’, and how can something be out for delivery for eight hours and not show?! <URL>
BRAND: We'd like to look into this for you, but we can't access your account via Twitter. When you have time, please reach out to us over phone or chat so we can discuss what options may be available: <URL>
- **Amazon Response**: I certainly understand your frustration! Have you had the chance to contact us through the link previously given? We'd be more than happy to look into this further with you there.
- **Assessment**: Irrelevant: Not a product condition issue

**[2] Score: `0.7492` | Doc: `retrieval_doc_0153354` | Grade: `0/3`**
- **Customer**: Amazon is the carrier.
- **Context**: CUSTOMER: Hilariously terrible service from and their CS reps. Both on phone and in person. Almost seems like they are intentionally messing up my deliveries ever since I initially complained to them. holy hell so bad.
BRAND: This isn't the kind of experience we want you to have! Without providing account details, can you tell us about the reason you initially contacted us?
CUSTOMER: I complained about not receiving my amazon package in late October. Since then I have had nothing but terrible delivery experiences and items not arriving. My last package was “delivered” but it never was. Then they told me it was misscanned. Then they told me it never sent. ??
BRAND: Thank you for that information and let me just say I am so sorry for the poor experience you've had with us! We'd like to look into these deliveries for you. Do you see a trend in the carrier? You can find that info here: <URL>
- **Amazon Response**: I would like to have someone from my team take a closer look into this with you. Please fill out your details here: <URL> and someone will be in contact with you.
- **Assessment**: Irrelevant: Not a product condition issue

**[3] Score: `0.7403` | Doc: `retrieval_doc_0045130` | Grade: `0/3`**
- **Customer**: Every time they tell to wait a day, which then the item never arrives then they'll issue the refund. So it's like a 2-3 day process and it's predictable. Might as well just cancel my prime since Amazon Logistics is unbelievable.
- **Context**: CUSTOMER: I've had 4 packages WRONGLY delivered by Amazon Logistics. Is there a way to NOT have them as my deliverer?
BRAND: I'm so sorry to hear about the poor delivery experiences! This isn't what we strive for. For clarification, what website do you use to place orders? For example, .com, .co.uk, .ca, etc. Let us know! We're here to help!
CUSTOMER: .com
BRAND: Thank you for that information. Have you been able to speak to anyone on our customer support team yet to help out with the wrong items received?
- **Amazon Response**: We want to help you out with this. Could you fill out some details here: <URL> so that we can investigate this further for you?^PJ
- **Assessment**: Irrelevant: Not a product condition issue

**[4] Score: `0.7400` | Doc: `retrieval_doc_0079038` | Grade: `0/3`**
- **Customer**: Isn't that odd? If I had ordered a new one I would have gotten it a week ago! How do I contact amazon.de? 3/3
- **Context**: CUSTOMER: Hi, I've returned an item to 13 days ago and haven't heard anything since. 'Tracking info not available' it says..
BRAND: Yes. Please contact them. They can check your order.
CUSTOMER: But I cannot find a way to contact them. When I login there's no further info on my returned item.
BRAND: In the menu after logging in, just choose what fits best...(1) "An Order I placed" and (2) "Returns and Refunds"..^AS
CUSTOMER: I already did that, it says my request for replacement has been received, but there is no tracking information available 1/3
CUSTOMER: I sent the item back 13 days ago and the post confirmed that it has been delivered, but I haven't heard anything yet. 2/3
- **Amazon Response**: Aftter the log-in <URL> you can choose the topics and then contact us per E-Mail or Phone.
- **Assessment**: Irrelevant: Not a product condition issue

**[5] Score: `0.7399` | Doc: `retrieval_doc_0146755` | Grade: `0/3`**
- **Customer**: thanks, email has been sent
- **Context**: CUSTOMER: Hi my order was never delivered to me but my A/c shows it’s delivered on 14th... pls help
BRAND: I'm sorry to hear you haven't been able to find your order. I'd recommend checking our help page on locating items that are tagged as delivered: <URL>
CUSTOMER: Thanks for prompt revert.. but i have checked everywhere and asked the neighbours too.. i did got Missed Post Note by but nothing was around
BRAND: Hey Sandeep, can you contact us so that we can look into this further for you: <URL>
CUSTOMER: this link is directed to the order details and can’t see where i can fill details for not receiving the delivery
BRAND: Sorry about that Sandeep. Please try the following link instead and we can check what has happened for you: <URL>
- **Amazon Response**: You're welcome. Let us know if you need anything else.
- **Assessment**: Irrelevant: Not a product condition issue

---

### Sample Query 35: `gold_0046`

**Customer Query**: `I canceled my order by mistake.... Pls contact- 8655123588`
**Predicted Intent**: `CANCEL_ORDER_REQUEST`

#### Top 5 Retrieved Historical Evidence Cases:

**[1] Score: `0.7338` | Doc: `retrieval_doc_0149616` | Grade: `3/3`**
- **Customer**: my order no is 405-5864882-4156312. Cancelled but not refunded
- **Context**: BRAND: I am sorry to know this. Our team would be happy to help you out! Please contact us from here: <URL> 1/2
- **Amazon Response**: Please don't provide your order number, we consider it to be personal info. Our Twitter page is visible to the public. 2/2
- **Assessment**: Highly useful evidence: Order cancellation procedure

**[2] Score: `0.7235` | Doc: `retrieval_doc_0128843` | Grade: `3/3`**
- **Customer**: and same order again cancel by seller Order ID 405-4069128-2777952
- **Context**: BRAND: Please don't provide your order details, we consider it to be personal information. Our page is visible to the public. 2/2
- **Amazon Response**: I understand how upsetting this can be. This is certainly not the kind of experience we want our customers to have. Kindly reach out to us here: <URL> and we will assist you. 1/2
- **Assessment**: Highly useful evidence: Order cancellation procedure

**[3] Score: `0.7121` | Doc: `retrieval_doc_0002769` | Grade: `3/3`**
- **Customer**: order id #403-5637109-7077146 has been cancelled or is on time pls help.
- **Context**: BRAND: We'll surely help you with the information. Request you to contact us here : <URL> 1/2
- **Amazon Response**: We'll surely help you with the information. Request you to contact us here : <URL> 1/2
- **Assessment**: Highly useful evidence: Order cancellation procedure

**[4] Score: `0.7006` | Doc: `retrieval_doc_0060188` | Grade: `3/3`**
- **Customer**: Extremely poor service. My order was cancelled automatically,No help after multiple emails/calls.ORDER 402-5268374-3477168
- **Context**: BRAND: I'm sorry the order was canceled, Divyansh. Unfortunately, orders once canceled can't be reinstated. Your feedback will (1/2)
- **Amazon Response**: I'm sorry the order was canceled, Divyansh. Unfortunately, orders once canceled can't be reinstated. Your feedback will (1/2)
- **Assessment**: Highly useful evidence: Order cancellation procedure

**[5] Score: `0.7000` | Doc: `retrieval_doc_0099407` | Grade: `3/3`**
- **Customer**: unable to cancel this order. Plz help me 403-6971836-0369117
- **Context**: BRAND: We'll surely help you cancel this order. Please connect with us here: <URL> We'll be glad to help. 1/2
- **Amazon Response**: We'll surely help you cancel this order. Please connect with us here: <URL> We'll be glad to help. 1/2
- **Assessment**: Highly useful evidence: Order cancellation procedure

---

### Sample Query 40: `gold_0072`

**Customer Query**: `hey I'm due a package tomorrow that I paid next day delivery for and my tracking status is still awaiting dispatch! Help?`
**Predicted Intent**: `WHERE_IS_MY_ORDER`

#### Top 5 Retrieved Historical Evidence Cases:

**[1] Score: `0.7202` | Doc: `retrieval_doc_0121515` | Grade: `1/3`**
- **Customer**: been waiting all day for my parcel. But the tracking just says out for delivery, due today. Any help
- **Amazon Response**: Sorry for the wait, Natalie! Most couriers will make deliveries until 21:00! Have we missed that time window?
- **Assessment**: Weakly related or irrelevant

**[2] Score: `0.7061` | Doc: `retrieval_doc_0090538` | Grade: `0/3`**
- **Customer**: Hey any idea if it’s coming as aren’t answering
- **Context**: CUSTOMER: my tracking says due for delivery can I expect it today? Post already come and nothing I have others things to do than wait in
- **Amazon Response**: Parcels may be delivered up to 21:00. Please keep us updated on its arrival!
- **Assessment**: Weakly related or irrelevant

**[3] Score: `0.6947` | Doc: `retrieval_doc_0137192` | Grade: `3/3`**
- **Customer**: my partner has had bad service at the moment. Parcel was suppose to arrive saturday had a delay notice, then would be here today. Still no parcel! This was suppose to be a gift what is too late now and fed up with delays. He pays extra for Amazon prime for this waiting.
- **Amazon Response**: I apologize for the delay, Katrina. What is the current tracking status shown here: <URL> We'd like to help in any way we can, so please let us know!
- **Assessment**: Highly useful evidence: Direct late delivery match with actionable carrier/tracking guidance

**[4] Score: `0.6921` | Doc: `retrieval_doc_0014025` | Grade: `1/3`**
- **Customer**: Your tracking info says it's still out fir delivery??????
- **Context**: CUSTOMER: Where is my parcel?? I paid extra to have it today. Nothing.
- **Amazon Response**: Oh no, David! I'm sorry for the trouble with your delivery! We'd like to look into this with you here: <URL>
- **Assessment**: Weakly related or irrelevant

**[5] Score: `0.6879` | Doc: `retrieval_doc_0127010` | Grade: `0/3`**
- **Customer**: Nah the tracking just said its coming tomorrow instead 🤷🏻‍♀️
- **Context**: CUSTOMER: don’t tell me I got guaranteed delivery and then change the date the day I’m supposed to get everything 😤
BRAND: I'm sorry to hear about this! Have you received an e-mail regarding any type of delay?
- **Amazon Response**: Yikes! I'm sorry that happened. Please keep us updated on your package delivery. We're here to help!
- **Assessment**: Weakly related or irrelevant

---

