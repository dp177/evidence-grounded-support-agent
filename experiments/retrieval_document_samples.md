# Historical Retrieval Document Inspection Samples (30 Examples)

This document presents **30 real historical support decision points** selected across multi-turn customer interactions.
For each document, the selected context is displayed alongside the exact, deterministic reasons and relevance scores calculated by the context selector.

---
## Example 1: [retrieval_doc_0000005] (Case: `amazon_case_0000409` | Conversation: `617`)
- **Thread Length**: 5 turns | **Turn Index**: 3

### CUSTOMER:
"3 different people have given 3 different answers and I still don't have my order. Says delivered Saturday, was not, I was home all day"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: Way to drop the ball on customer service so pissed right now!
BRAND: I'm sorry we've let you down! Without providing any personal information, will you describe the issue? We'd love to help.
```

### HISTORICAL AMAZON RESPONSE:
"We'd like to take a further look into this with you! Please reach us by phone or chat here: <URL>"

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **4.18** | Reasons: `recency:0.88, postal_code_present, root_customer_problem_anchor` | Text: *"Way to drop the ball on customer service @115821 so pissed right now!..."*
- **Turn 1** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@115820 I'm sorry we've let you down! Without providing any personal i..."*

---
## Example 2: [retrieval_doc_0004260] (Case: `amazon_case_0051766` | Conversation: `74787`)
- **Thread Length**: 17 turns | **Turn Index**: 8

### CUSTOMER:
"Dear , I am going to install the product ( as it is very delayed now☹️) and send you the charges for the same. Kindly reimburse the balance in form of amazon pay balance. Thank you."

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: I have replied to that mail but there is no response from the team.
CUSTOMER: Dear please mention complete info for product ( <URL> Accessories price not mentioned. take 22 days to respond for installation request (after multiple calls) and engineer charges Rs. 800.(Reg. No. 7840045107). #disappointed #badservice
BRAND: I get your disappointment, Raju. I have checked and can see that the product has inbuilt accessories. However, please report this to our support team here: <URL> for further assistance. 1/2
BRAND: Please don't provide your order details as we consider it personal information. Our twitter page is visible to public. 2/2
CUSTOMER: Waiting for further update.
BRAND: We've sent a correspondence regarding this here: <URL> Kindly check and reply so that we can check further on this.
```

### HISTORICAL AMAZON RESPONSE:
"I understand your concern regarding the installation of your product. Twitter being a social platform, we do not have access to your account. As informed earlier, kindly reply to the email you received from social media team for further assistance."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **2.08** | Reasons: `recency:0.28, root_customer_problem_anchor` | Text: *"@AmazonHelp I have replied to that mail but there is no response from ..."*
- **Turn 2** (`CUSTOMER`): Score **2.49** | Reasons: `recency:0.52, postal_code_present, lexical_overlap:0.47(charges,product,dear)` | Text: *"Dear @115821 please mention complete info for product (https://t.co/Mh..."*
- **Turn 3** (`BRAND`): Score **2.14** | Reasons: `recency:0.64, postal_code_present` | Text: *"@132737 I get your disappointment, Raju. I have checked and can see th..."*
- **Turn 4** (`BRAND`): Score **2.26** | Reasons: `recency:0.76, postal_code_present` | Text: *"@132737 Please don't provide your order details as we consider it pers..."*
- **Turn 5** (`CUSTOMER`): Score **3.38** | Reasons: `recency:0.88, waiting_window_exceeded` | Text: *"@AmazonHelp Waiting for further update...."*
- **Turn 6** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@132737 We've sent a correspondence regarding this here: https://t.co/..."*

---
## Example 3: [retrieval_doc_0009557] (Case: `amazon_case_0097014` | Conversation: `149305`)
- **Thread Length**: 8 turns | **Turn Index**: 3

### CUSTOMER:
"I have forwarded the details on the above link! Hope this time , issue will be resolved"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: Even after sending request so many times , no one came to receive my product which I got defective! I am really pissed off with your services!
BRAND: We apologize for the experience you had regarding the return of your order. Request you to share details here: <URL> and we'll get back to you soon.
```

### HISTORICAL AMAZON RESPONSE:
"Thanks for confirming that you've shared your details. Please allow us some time and we'll reach out to you soon with an update."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **4.18** | Reasons: `recency:0.88, postal_code_present, root_customer_problem_anchor` | Text: *"@115850 Even after sending request so many times , no one came to rece..."*
- **Turn 1** (`BRAND`): Score **4.28** | Reasons: `recency:1.00, postal_code_present, lexical_overlap:0.28(details), immediate_preceding_brand_prompt` | Text: *"@150015 We apologize for the experience you had regarding the return o..."*

---
## Example 4: [retrieval_doc_0014214] (Case: `amazon_case_0145069` | Conversation: `222712`)
- **Thread Length**: 16 turns | **Turn Index**: 7

### CUSTOMER:
"It seems that it is an issue with ISP, wid mob data it works. Can u investigate if isp can block. Issue is with Amazon only"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: This link is not opening either, page can't be loaded error is getting displayed
BRAND: Sorry for the trouble you've had. Could you please help us with the screenshot of the error you're facing.
CUSTOMER: This error is coming for all 3 devices and issue is only with Amazon app <URL>
BRAND: I'll be sure to pass your comments as feedback to our concerned team for review.
CUSTOMER: hav done all still issue persist. I have 3 phones a nd all 3 hav same issues. Even new app doesn't work.
BRAND: Sorry about that. Kindly fill in your details here: <URL> and we'll get in touch with you.
```

### HISTORICAL AMAZON RESPONSE:
"You may reach out to service provider for more information."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **2.20** | Reasons: `recency:0.40, root_customer_problem_anchor` | Text: *"@AmazonHelp This link is not opening either, page can't be loaded erro..."*
- **Turn 1** (`BRAND`): Score **2.02** | Reasons: `recency:0.52, postal_code_present` | Text: *"@169201 Sorry for the trouble you've had. Could you please help us wit..."*
- **Turn 2** (`CUSTOMER`): Score **1.09** | Reasons: `recency:0.64, lexical_overlap:0.46(only,issue)` | Text: *"@AmazonHelp This error is coming for all 3 devices and issue is only w..."*
- **Turn 3** (`BRAND`): Score **2.26** | Reasons: `recency:0.76, postal_code_present` | Text: *"@169201 I'll be sure to pass your comments as feedback to our concerne..."*
- **Turn 4** (`CUSTOMER`): Score **0.88** | Reasons: `recency:0.88` | Text: *"@AmazonHelp hav done all still issue persist. I have 3 phones a nd all..."*
- **Turn 5** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@169201 Sorry about that. Kindly fill in your details here:https://t.c..."*

---
## Example 5: [retrieval_doc_0019009] (Case: `amazon_case_0008694` | Conversation: `274870`)
- **Thread Length**: 5 turns | **Turn Index**: 4

### CUSTOMER:
"Ordr nt delivered or updated for last one week. Even support response was generic. I sent another email today and it's out for delivery now."

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: U use to deliver things like Flash ⚡ but now it seems my order is moving like the White Walkers. Can you update me on my order ?
BRAND: We always prepare ourselves when we receive an order. Could you let us know if we had a miss on your delivery?
```

### HISTORICAL AMAZON RESPONSE:
"I request you to kindly wait till the time and I'm positive that the order would be delivered. 2/2"

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **3.94** | Reasons: `recency:0.64, postal_code_present, root_customer_problem_anchor` | Text: *"@115850  U use to deliver things like Flash ⚡ but now it seems my orde..."*
- **Turn 1** (`BRAND`): Score **2.26** | Reasons: `recency:0.76, postal_code_present` | Text: *"@181667 We always prepare ourselves when we receive an order. Could yo..."*
- **Turn 2** (`CUSTOMER`): Score **6.08** | Reasons: `recency:0.88, delivery_tracking_terms, temporal_deadline_anchor, lexical_overlap:2.50(now,delivered,ordr)` | Text: *"@AmazonHelp Ordr nt delivered or updated for last one week. Even suppo..."*
- **Turn 3** (`BRAND`): Score **5.20** | Reasons: `recency:1.00, postal_code_present, temporal_deadline_anchor, immediate_preceding_brand_prompt` | Text: *"@181667 I'm sorry about the delay, Harsh. We deliver orders on or befo..."*

---
## Example 6: [retrieval_doc_0023612] (Case: `amazon_case_0038891` | Conversation: `318660`)
- **Thread Length**: 11 turns | **Turn Index**: 4

### CUSTOMER:
"How do you find that out? This is what it says. We don’t even live in dartford! And attempting delivery at nearly 11? Very very poor <URL>"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: Once again. lie again. Someone was in all day, no attempt at delivery was made. <URL>
BRAND: Hi, sorry to see that. What carrier was used for the delivery?
```

### HISTORICAL AMAZON RESPONSE:
"Hi Talia- Can you get in touch with us via: <URL> we can investigate these 'attempts' for you."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **4.06** | Reasons: `recency:0.76, postal_code_present, root_customer_problem_anchor` | Text: *"Once again. @115830 lie again. Someone was in all day, no attempt at d..."*
- **Turn 1** (`CUSTOMER`): Score **2.38** | Reasons: `recency:0.88, postal_code_present` | Text: *"@115830 @AmazonHelp..."*
- **Turn 2** (`BRAND`): Score **6.11** | Reasons: `recency:1.00, carrier_courier_mention, postal_code_present, lexical_overlap:0.31(what,delivery), immediate_preceding_brand_prompt` | Text: *"@192019 Hi, sorry to see that. What carrier was used for the delivery?..."*

---
## Example 7: [retrieval_doc_0028230] (Case: `amazon_case_0070230` | Conversation: `365220`)
- **Thread Length**: 37 turns | **Turn Index**: 16

### CUSTOMER:
"TODAY not more than that .. period"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: I bought it from Amazon .. and sent my invoice IMEI NUMBERS already
CUSTOMER: Same was told to me 14 days before and am still waiting .. Samsung is worst
CUSTOMER: I need solution not a call back as a formality. I mentioned the issue very clearly.. as per the agreement within 4 days of registration I
CUSTOMER: Sounds good.. expecting the solution latest by today.. else i would have to return tue product and file a consumer petition for the
CUSTOMER: Hardship and mental agony I have experienced with you and Samsung mobile india
BRAND: Sorry about the bad experience. We'll get in touch with you as soon as we have an update.
```

### HISTORICAL AMAZON RESPONSE:
"We're working on your concern. We shall get in touch with you shortly."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **1.80** | Reasons: `recency:0.00, root_customer_problem_anchor` | Text: *"@AmazonHelp I bought it from Amazon .. and sent my invoice IMEI NUMBER..."*
- **Turn 3** (`CUSTOMER`): Score **2.50** | Reasons: `recency:0.00, waiting_window_exceeded` | Text: *"@AmazonHelp Same was told to me 14 days before and am still waiting ....."*
- **Turn 8** (`BRAND`): Score **1.78** | Reasons: `recency:0.28, postal_code_present` | Text: *"@202516 Thanks for sharing your details. We'll reach out to you at the..."*
- **Turn 11** (`BRAND`): Score **2.14** | Reasons: `recency:0.64, postal_code_present` | Text: *"@202516 We're working on the issue and shall get back to you with an u..."*
- **Turn 12** (`CUSTOMER`): Score **2.46** | Reasons: `recency:0.76, temporal_deadline_anchor, lexical_overlap:0.50(today)` | Text: *"@AmazonHelp Sounds good.. expecting the solution latest by today..  el..."*
- **Turn 14** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@202516 Sorry about the bad experience. We'll get in touch with you as..."*

---
## Example 8: [retrieval_doc_0033087] (Case: `amazon_case_0103569` | Conversation: `422278`)
- **Thread Length**: 11 turns | **Turn Index**: 3

### CUSTOMER:
"I have shared requested info. Please review let me know the status."

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: Did you get my order details and let me know if i can get my money back ?? Coz I'm not gonna buy anything from Amazon
BRAND: Apologies for the ordeal Anant. Please share your details here: <URL> and I'll get back to you.
```

### HISTORICAL AMAZON RESPONSE:
"Thank you for dropping in your details. Our team will look into the issue and get in touch with you."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **3.39** | Reasons: `recency:0.88, lexical_overlap:0.71(let,know), root_customer_problem_anchor` | Text: *"@AmazonHelp Did you get my order details and let me know if i can get ..."*
- **Turn 1** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@215577 Apologies for the ordeal Anant. Please share your details here..."*

---
## Example 9: [retrieval_doc_0037784] (Case: `amazon_case_0136962` | Conversation: `471487`)
- **Thread Length**: 11 turns | **Turn Index**: 4

### CUSTOMER:
"Sir i have submitted the Details... Kindly contact me soon... I dont want more delay in my cheque... Refund me soon.. Its one week late for refund... Will you Provide me Interest also on my late Money Refund Amount..😑 Contact Me Soon"

### SELECTED PRECEDING CONTEXT:
```text
BRAND: Apologies for the incorrect name on the refund cheque, Rinku. As this is social media, we will be unable to connect with you or access your details from here. Kindly fill in your details here: <URL> and we'll get this checked for you. (1/2)
CUSTOMER: i have received the cheque with wrong name on 17th Nov 2017. I told amazon to give me a cheque with correct name... They told me till 25th Nov i will get it. Nor i am able to talk to your team on phone.. Call me Back i want to talk:-8447502439
BRAND: Please don’t provide your order/account details as we consider them to be personal information. Our Twitter page is visible to public. (2/2)
```

### HISTORICAL AMAZON RESPONSE:
"Thank you for sharing the details in the link, Rinku. We'll check and get back to you with an update soon."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **2.92** | Reasons: `recency:0.76, lexical_overlap:0.36(will,cheque,want), root_customer_problem_anchor` | Text: *"@AmazonHelp 
i have received the cheque with wrong name on 17th Nov 20..."*
- **Turn 1** (`BRAND`): Score **4.97** | Reasons: `recency:0.88, financial_terms, postal_code_present, lexical_overlap:0.59(refund,will,details)` | Text: *"@227272 Apologies for the incorrect name on the refund cheque, Rinku. ..."*
- **Turn 2** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@227272 Please don’t provide your order/account details as we consider..."*

---
## Example 10: [retrieval_doc_0043659] (Case: `amazon_case_0021789` | Conversation: `555291`)
- **Thread Length**: 10 turns | **Turn Index**: 7

### CUSTOMER:
"That link just sends me to my account??"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: I pay $100+/year for Prime and in 5+ years I’ve never had any issues. Until yesterday, when a Prime package was “Guaranteed” to arrive by the 1st and now it’s not until the 3rd?? Wtf do I pay for?! Guarantee means nothing to
BRAND: Oh no! I know how frustrating this can be. Did you receive an email regarding the delay?
CUSTOMER: No, I didn’t receive an email saying it would be delayed. I had to check myself through the apps
BRAND: Thank you for that. Can you please tell us who the carrier is? You can see that info here: <URL>
CUSTOMER: UPS Sure Post
BRAND: We'd like to look into this with you. Please reach us here: <URL>
```

### HISTORICAL AMAZON RESPONSE:
"After you sign-in to your account, you will then be prompted to ask a few questions and then will be directed to choose, phone or chat! Let us know if you are still having difficulty."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **8.40** | Reasons: `recency:0.40, financial_terms, postal_code_present, delivery_tracking_terms, temporal_deadline_anchor, root_customer_problem_anchor` | Text: *"I pay $100+/year for @115821 Prime and in 5+ years I’ve never had any ..."*
- **Turn 1** (`BRAND`): Score **2.02** | Reasons: `recency:0.52, postal_code_present` | Text: *"@249648 Oh no! I know how frustrating this can be. Did you receive an ..."*
- **Turn 2** (`CUSTOMER`): Score **0.64** | Reasons: `recency:0.64` | Text: *"@AmazonHelp No, I didn’t receive an email saying it would be delayed. ..."*
- **Turn 3** (`BRAND`): Score **4.06** | Reasons: `recency:0.76, carrier_courier_mention, postal_code_present` | Text: *"@249648 Thank you for that. Can you please tell us who the carrier is?..."*
- **Turn 4** (`CUSTOMER`): Score **2.68** | Reasons: `recency:0.88, carrier_courier_mention` | Text: *"@AmazonHelp UPS Sure Post..."*
- **Turn 5** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@249648 We'd like to look into this with you. Please reach us here: ht..."*

---
## Example 11: [retrieval_doc_0049233] (Case: `amazon_case_0089892` | Conversation: `661477`)
- **Thread Length**: 6 turns | **Turn Index**: 5

### CUSTOMER:
"that's just it, I can't get a tracking number from your website."

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: what is up with your tracking lately. My order says will deliver today by 8. But status says prepping to ship? #Amazon
BRAND: I'm sorry for the wait! Packages can still show up by 8 PM. Please keep us posted.
CUSTOMER: package never arrived and I cannot get a tracking number form the site. Second time this gas happened in 2 mo's. Please help.
BRAND: I'm sorry your package has not yet arrived. We're here to help! Please let us know current tracking information and who the carrier is. You can find that here: <URL>
```

### HISTORICAL AMAZON RESPONSE:
"We'd like to look into this further with you. At your nearest convenience please reach out to us here: <URL>"

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **5.56** | Reasons: `recency:0.64, delivery_tracking_terms, temporal_deadline_anchor, lexical_overlap:0.42(tracking), root_customer_problem_anchor` | Text: *"@AmazonHelp what is up with your tracking lately. My order says will d..."*
- **Turn 1** (`BRAND`): Score **2.68** | Reasons: `recency:0.76, postal_code_present, lexical_overlap:0.42(can)` | Text: *"@277609 I'm sorry for the wait! Packages can still show up by 8 PM. Pl..."*
- **Turn 2** (`CUSTOMER`): Score **3.63** | Reasons: `recency:0.88, delivery_tracking_terms, lexical_overlap:1.25(number,tracking,get)` | Text: *"@AmazonHelp package never arrived and I cannot get a tracking number f..."*
- **Turn 3** (`BRAND`): Score **8.13** | Reasons: `recency:1.00, carrier_courier_mention, postal_code_present, delivery_tracking_terms, lexical_overlap:0.83(can,tracking), immediate_preceding_brand_prompt` | Text: *"@277609 I'm sorry your package has not yet arrived. We're here to help..."*

---
## Example 12: [retrieval_doc_0054633] (Case: `amazon_case_0150544` | Conversation: `756416`)
- **Thread Length**: 14 turns | **Turn Index**: 12

### CUSTOMER:
"Person receiving the gift access to the set up. I've wasted an incredible amount of time trying to get my crib and dresser set up"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: you have the worst customer service ever. I will never use you for a registry ever again!
CUSTOMER: I've been out of town and now I'm trying to get the crib assembled and unable because it's not under my account even though it has been sent
BRAND: I can certainly understand the frustration. Have you had a chance to contact by phone? If so, which options did we provide?
CUSTOMER: I had her information but it needed second verification and she's out of the country. I was able to get it but bc it's not my account
CUSTOMER: I can't be emailed or make changes to my set up. You all need to work on people especially pregnant people being able to have their gift
CUSTOMER: Cribs set up especially after the tech didn't show up the first time. I will have my family and friends use a provider that allows the
```

### HISTORICAL AMAZON RESPONSE:
"I'm sorry for the poor experience this has been. We appreciate you taking the time to share your feedback with us."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **3.30** | Reasons: `recency:0.00, postal_code_present, root_customer_problem_anchor` | Text: *"@115821 you have the worst customer service ever. I will never use you..."*
- **Turn 1** (`BRAND`): Score **1.50** | Reasons: `recency:0.00, postal_code_present` | Text: *"@300787 I'm sorry to hear this! Without sharing any account details, c..."*
- **Turn 4** (`CUSTOMER`): Score **0.95** | Reasons: `recency:0.28, lexical_overlap:0.67(ve,trying,crib)` | Text: *"@AmazonHelp I've been out of town and now I'm trying to get the crib a..."*
- **Turn 7** (`BRAND`): Score **2.14** | Reasons: `recency:0.64, postal_code_present` | Text: *"@300787 I can certainly understand the frustration. Have you had a cha..."*
- **Turn 9** (`CUSTOMER`): Score **1.38** | Reasons: `recency:0.88, lexical_overlap:0.50(up,gift,set)` | Text: *"@AmazonHelp I can't be emailed or make changes to my set up. You all n..."*
- **Turn 10** (`CUSTOMER`): Score **1.50** | Reasons: `recency:1.00, lexical_overlap:0.50(up,time,set)` | Text: *"@AmazonHelp Cribs set up especially after the tech didn't show up the ..."*

---
## Example 13: [retrieval_doc_0059769] (Case: `amazon_case_0032716` | Conversation: `835127`)
- **Thread Length**: 20 turns | **Turn Index**: 19

### CUSTOMER:
"i filled this form long back"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: Order # 408-9746877-3993920 issues never resolve, money never comes back, executive don't provide proper resolution
CUSTOMER: Your delivery boy suggests that he delivered the product to someone in my society. That's not right. I'm paying penalty for non-paying bank
BRAND: Please share your details here: <URL> & we'll get back to you.
BRAND: Sorry about that, Manuj. You can request a callback with your preferred time by writing back to the e-mail sent by our team.
BRAND: Have you reverted our email with your request for call back?
BRAND: Here it is, <URL>
```

### HISTORICAL AMAZON RESPONSE:
"In that case, you should've received a correspondence from us here: <URL> Kindly check and revert."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **6.42** | Reasons: `recency:0.00, order_number_present, postal_code_present, lexical_overlap:0.62(back), root_customer_problem_anchor` | Text: *"Order # 408-9746877-3993920 issues never resolve, money never comes ba..."*
- **Turn 2** (`BRAND`): Score **2.12** | Reasons: `recency:0.00, postal_code_present, lexical_overlap:0.62(form)` | Text: *"@318840 I'm sorry about that. I’d like to help you, please fill this f..."*
- **Turn 11** (`BRAND`): Score **2.40** | Reasons: `recency:0.28, postal_code_present, lexical_overlap:0.62(back)` | Text: *"@318840 Please share your details here: https://t.co/GIJyeYqKE0 &amp; ..."*
- **Turn 13** (`BRAND`): Score **2.65** | Reasons: `recency:0.52, postal_code_present, lexical_overlap:0.62(back)` | Text: *"@318840 Sorry about that, Manuj. You can request a callback with your ..."*
- **Turn 15** (`BRAND`): Score **2.88** | Reasons: `recency:0.76, postal_code_present, lexical_overlap:0.62(back)` | Text: *"@318840 Have you reverted our email with your request for call back? ^..."*
- **Turn 17** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@318840 Here it is, https://t.co/cQVomR1pWz. ^HA..."*

---
## Example 14: [retrieval_doc_0064554] (Case: `amazon_case_0083981` | Conversation: `913843`)
- **Thread Length**: 10 turns | **Turn Index**: 4

### CUSTOMER:
"#AmazonIndia I already registered the complaint. I want replacement but amazon will give me refund only as watch is out of stock."

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: Thanks for ruining my Diwali gift. I ordered a watch(Casio EX247) worth INR 24,296 but received completely different model :( #AmazonIndia
BRAND: Sorry about the trouble with the order. Please report this to our support team from here: <URL>
```

### HISTORICAL AMAZON RESPONSE:
"a refund to the original payment method. Appreciate your understanding. (2/2)"

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **2.80** | Reasons: `recency:0.64, lexical_overlap:0.36(amazonindia,watch), root_customer_problem_anchor` | Text: *"Thanks for ruining my Diwali gift. I ordered a watch(Casio  EX247) wor..."*
- **Turn 1** (`BRAND`): Score **2.26** | Reasons: `recency:0.76, postal_code_present` | Text: *"@120039 Sorry about the trouble with the order.  Please report this to..."*
- **Turn 2** (`CUSTOMER`): Score **5.38** | Reasons: `recency:0.88, financial_terms, lexical_overlap:2.50(refund,out,stock)` | Text: *"#AmazonIndia I already registered the complaint. I want replacement bu..."*
- **Turn 3** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@120039 Replacements can be sent only if the same item is available wi..."*

---
## Example 15: [retrieval_doc_0069240] (Case: `amazon_case_0127562` | Conversation: `982029`)
- **Thread Length**: 12 turns | **Turn Index**: 7

### CUSTOMER:
"in tht case, investigate plz. Becuz I recved another email frm custmr service with NO TIMELINE for order #AmazonIndia #Amazon"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: #Amazonindia wrst dlvry service. Waiting for nxt day dlvry order from 17 Oct. Not received till date. #Amazon
BRAND: Apologies for the delay in delivery. Did you happen to escalate this to our support team here: <URL>
CUSTOMER: talking to customer service from last 4 days, same response every time. Tomorrow it will be delivered
BRAND: Do keep us posted. We'll be more than happy to help.
CUSTOMER: what I need post that still I am waiting for order??? #AmazonIndia #Amazon
BRAND: Please let us know if you've successfully received the order, Vikas. If not, we'll investigate this further.
```

### HISTORICAL AMAZON RESPONSE:
"Sure, Vikas. Before we take an action, could you let us know If we have missed the estimated delivery date of the order?"

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **5.20** | Reasons: `recency:0.40, waiting_window_exceeded, lexical_overlap:0.50(service,amazonindia,order), root_customer_problem_anchor` | Text: *"#Amazonindia wrst dlvry service. Waiting for nxt day dlvry order from ..."*
- **Turn 1** (`BRAND`): Score **2.02** | Reasons: `recency:0.52, postal_code_present` | Text: *"@352833 Apologies for the delay in delivery. Did you happen to escalat..."*
- **Turn 2** (`CUSTOMER`): Score **3.34** | Reasons: `recency:0.64, delivery_tracking_terms, temporal_deadline_anchor` | Text: *"@AmazonHelp talking to customer service from last 4 days, same respons..."*
- **Turn 3** (`BRAND`): Score **2.26** | Reasons: `recency:0.76, postal_code_present` | Text: *"@352833 Do keep us posted. We'll be more than happy to help. ^CB..."*
- **Turn 4** (`CUSTOMER`): Score **3.71** | Reasons: `recency:0.88, waiting_window_exceeded, lexical_overlap:0.33(amazonindia,order)` | Text: *"@AmazonHelp what I need post that still I am waiting for order??? #Ama..."*
- **Turn 5** (`BRAND`): Score **5.83** | Reasons: `recency:1.00, postal_code_present, lexical_overlap:0.33(investigate,order), immediate_preceding_brand_prompt, brand_commitment_instruction` | Text: *"@352833 Please let us know if you've successfully received the order, ..."*

---
## Example 16: [retrieval_doc_0074225] (Case: `amazon_case_0014111` | Conversation: `1068744`)
- **Thread Length**: 6 turns | **Turn Index**: 3

### CUSTOMER:
"No, you shipped a 2 day item as "UPS 3 DAY SELECT". Thats not giving me what I pay for. Exactly why I cancelled prime last time."

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: Why am I a prime member, membership includes free 2 day shipping and sent ups 3 day select. Order 10/19, eta 10/25 <URL>
BRAND: Terribly sorry for the delay, len! Have we missed the delivery date given at checkout?
```

### HISTORICAL AMAZON RESPONSE:
"Two-Day shipping refers to the time in transit after the order ships. Feel free to keep us posted on the order."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **5.17** | Reasons: `recency:0.88, carrier_courier_mention, lexical_overlap:0.69(why,select,prime), root_customer_problem_anchor` | Text: *"Why am I a prime member, membership includes free 2 day shipping and s..."*
- **Turn 1** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@205104 Terribly sorry for the delay, len! Have we missed the delivery..."*

---
## Example 17: [retrieval_doc_0079473] (Case: `amazon_case_0068750` | Conversation: `1149803`)
- **Thread Length**: 6 turns | **Turn Index**: 5

### CUSTOMER:
"Hopeless utterly disappointed what's the point of using"

### SELECTED PRECEDING CONTEXT:
```text
BRAND: We'd like to help you with this. Please report this to our support team here: <URL> Please don't 1/2
CUSTOMER: kindly refund money for order 404-2396392-7886725 via Amazon pay as I have to place an order before sale ends
BRAND: provide your order details, we consider it personal information. Our Twitter page is visible to public. 2/2
```

### HISTORICAL AMAZON RESPONSE:
"Sorry to know you've not received the refund. Please share your details here: <URL> I'll assist."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **8.44** | Reasons: `recency:0.64, order_number_present, financial_terms, postal_code_present, root_customer_problem_anchor` | Text: *"@115850 @AmazonHelp kindly refund money for order 404-2396392-7886725 ..."*
- **Turn 1** (`BRAND`): Score **2.26** | Reasons: `recency:0.76, postal_code_present` | Text: *"@323710 We'd like to help you with this. Please report this to our sup..."*
- **Turn 2** (`BRAND`): Score **2.38** | Reasons: `recency:0.88, postal_code_present` | Text: *"@323710 provide your order details, we consider it personal informatio..."*
- **Turn 3** (`CUSTOMER`): Score **5.00** | Reasons: `recency:1.00, postal_code_present, lexical_overlap:2.50(hopeless,point,utterly)` | Text: *"@115850 @AmazonHelp Hopeless utterly disappointed what's the point of ..."*

---
## Example 18: [retrieval_doc_0085235] (Case: `amazon_case_0133721` | Conversation: `1252975`)
- **Thread Length**: 15 turns | **Turn Index**: 3

### CUSTOMER:
"Yes. See attached... <URL>"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: fail!!! 2 day shipping is really 4 days to deliver... and I'm getting a bunch of mumbo jumbo from your customer service! <URL>
BRAND: Hey, I am sorry to hear this. Have we missed the delivery date given in the order confirmation email?
```

### HISTORICAL AMAZON RESPONSE:
"Hi Glen, what carrier is your order with as we don't have access to account details here?"

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **4.18** | Reasons: `recency:0.88, postal_code_present, root_customer_problem_anchor` | Text: *"@115821 fail!!! 2 day shipping is really 4 days to deliver... and I'm ..."*
- **Turn 1** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@413926 Hey, I am sorry to hear this. Have we missed the delivery date..."*

---
## Example 19: [retrieval_doc_0090937] (Case: `amazon_case_0021007` | Conversation: `1340688`)
- **Thread Length**: 6 turns | **Turn Index**: 3

### CUSTOMER:
"When the email eventually came, up to 23rd November but that was just the 1 issue I had as item stock changed. I was then told 25th to 27th. <URL>"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: Ordered 21st, est. 25th to 27th... still not dispatched. Is the delay because I'm not a #Prime customer? CSR wouldn't answer....
BRAND: I'm sorry for the wait. Some items aren't able to dispatch immediately. What date is on the order confirmation e-mail?
```

### HISTORICAL AMAZON RESPONSE:
"I can understand how this is frustrating, Simon! Orders may dispatch at any time to arrive on del day. Keep us posted!"

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **5.96** | Reasons: `recency:0.88, postal_code_present, delivery_tracking_terms, lexical_overlap:0.28(27th,25th), root_customer_problem_anchor` | Text: *"Ordered 21st, est. 25th to 27th... still not dispatched. Is the delay ..."*
- **Turn 1** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@432701 I'm sorry for the wait. Some items aren't able to dispatch imm..."*

---
## Example 20: [retrieval_doc_0096350] (Case: `amazon_case_0077610` | Conversation: `1427893`)
- **Thread Length**: 7 turns | **Turn Index**: 3

### CUSTOMER:
"No one has reached out to contact me."

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: Hoping my order gets here before I leave for work... its already late.
BRAND: Hey Josh, sorry to hear of the delay. Have you been in touch? If so, what was advised?
```

### HISTORICAL AMAZON RESPONSE:
"If your order missed the delivery window, please contact us here: <URL>"

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **4.18** | Reasons: `recency:0.88, postal_code_present, root_customer_problem_anchor` | Text: *"Hoping my @117093 order gets here before I leave for work... its alrea..."*
- **Turn 1** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@451680 Hey Josh, sorry to hear of the delay. Have you been in touch? ..."*

---
## Example 21: [retrieval_doc_0102522] (Case: `amazon_case_0151322` | Conversation: `1544131`)
- **Thread Length**: 7 turns | **Turn Index**: 4

### CUSTOMER:
"I am loyal prime fan. But please update some good movie . Also big bang theory t.v show"

### SELECTED PRECEDING CONTEXT:
```text
BRAND: We will continue to add new content. Keeping checking <URL> where we highlight the latest movies 1/2
CUSTOMER: no surprise why you update such a flop movie... upload some good movie amd new.
BRAND: and TV shows we have available. 2/2
```

### HISTORICAL AMAZON RESPONSE:
"Be assured, I've noted your comments and have forwarded your feedback internally."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **4.89** | Reasons: `recency:0.76, postal_code_present, lexical_overlap:0.83(some,update,movie), root_customer_problem_anchor` | Text: *"@119625  no surprise why you update such a flop movie... upload some g..."*
- **Turn 1** (`BRAND`): Score **2.38** | Reasons: `recency:0.88, postal_code_present` | Text: *"@426420 We will continue to add new content. Keeping checking https://..."*
- **Turn 2** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@426420 and TV shows we have available. 2/2 ^SH..."*

---
## Example 22: [retrieval_doc_0108473] (Case: `amazon_case_0054414` | Conversation: `1651590`)
- **Thread Length**: 6 turns | **Turn Index**: 3

### CUSTOMER:
"I am based in Nigeria. I don't understand your question."

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: . I need a text not currently in Nigeria's Bookshop. Story Engineering by Larry Brooks. What's the price and how do I get it. Thanks.
BRAND: We are happy to help you find the book! Could you tell us which site you are ordering the book from? .com? .co.uk?
```

### HISTORICAL AMAZON RESPONSE:
"If you are looking to order from our U.S. website (.com), here is a link to the book: <URL>"

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **4.68** | Reasons: `recency:0.88, postal_code_present, lexical_overlap:0.50(nigeria), root_customer_problem_anchor` | Text: *"@115821. I need a text not currently in Nigeria's Bookshop. Story Engi..."*
- **Turn 1** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@504357 We are happy to help you find the book! Could you tell us whic..."*

---
## Example 23: [retrieval_doc_0114437] (Case: `amazon_case_0123971` | Conversation: `1763195`)
- **Thread Length**: 35 turns | **Turn Index**: 4

### CUSTOMER:
"That was even more useless than chat. Give me my refund"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: Back on chat. You're now saying I can't have refund because the item I returned is 'materially different'. I haven't returned anything as you won't provide return address. You literally make no sense
CUSTOMER: Seriously, how am I supposed to resolve this when you just talk bollocks?
CUSTOMER: 'Pick out all the broken glass before returning' FYI, that's not happening
```

### HISTORICAL AMAZON RESPONSE:
"As we're unable to view your account via Twitter, pls contact request a call back here <URL>"

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **5.27** | Reasons: `recency:0.76, financial_terms, lexical_overlap:0.71(refund,chat), root_customer_problem_anchor` | Text: *"@AmazonHelp Back on chat. You're now saying I can't have refund becaus..."*
- **Turn 1** (`CUSTOMER`): Score **0.88** | Reasons: `recency:0.88` | Text: *"@AmazonHelp Seriously, how am I supposed to resolve this when you just..."*
- **Turn 2** (`CUSTOMER`): Score **1.00** | Reasons: `recency:1.00` | Text: *"@AmazonHelp 'Pick out all the broken glass before returning' 

FYI, th..."*

---
## Example 24: [retrieval_doc_0120716] (Case: `amazon_case_0162960` | Conversation: `2089288`)
- **Thread Length**: 10 turns | **Turn Index**: 9

### CUSTOMER:
"I’ve got the exact same thing, plus another item that should’ve arrived last Friday…"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: ordered something on Sunday, it has been “Out for delivery” since Monday morning but still not arrived
CUSTOMER: Hi , to quote the email “Arriving: Monday, November 6” and used prime One-Day Delivery option. Thanks
BRAND: Do you know who the carrier is and if tracking was provided? If so when was the last delivery scan?
CUSTOMER: Carrier is Amazon Shipping and the last delivery update to “Out for delivery” was at 10:50am Monday from Camberley
CUSTOMER: Thanks, email sent.
BRAND: Great! Keep us posted
```

### HISTORICAL AMAZON RESPONSE:
"I'm sorry it hasn't arrived! We'd like to look into this. Please reach us via phone or chat here: <URL>"

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **6.16** | Reasons: `recency:0.16, postal_code_present, delivery_tracking_terms, temporal_deadline_anchor, root_customer_problem_anchor` | Text: *"@115830 ordered something on Sunday, it has been “Out for delivery” si..."*
- **Turn 1** (`BRAND`): Score **1.78** | Reasons: `recency:0.28, postal_code_present` | Text: *"@617609 Hi Andy, what delivery date was listed in your order confirmat..."*
- **Turn 3** (`BRAND`): Score **5.32** | Reasons: `recency:0.52, carrier_courier_mention, postal_code_present, delivery_tracking_terms` | Text: *"@617609 Do you know who the carrier is and if tracking was provided? I..."*
- **Turn 4** (`CUSTOMER`): Score **5.14** | Reasons: `recency:0.64, carrier_courier_mention, delivery_tracking_terms, temporal_deadline_anchor` | Text: *"@AmazonHelp Carrier is Amazon Shipping and the last delivery update to..."*
- **Turn 5** (`BRAND`): Score **2.26** | Reasons: `recency:0.76, postal_code_present` | Text: *"@617609 I am sorry to hear this! Can I ask for you to contact our Cust..."*
- **Turn 7** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@617609 Great! Keep us posted ^BD..."*

---
## Example 25: [retrieval_doc_0126835] (Case: `amazon_case_0105992` | Conversation: `2260636`)
- **Thread Length**: 4 turns | **Turn Index**: 3

### CUSTOMER:
"The order did change to say “We’re sorry your package is late…” at least. Doesn’t show any additional from that. Asks me to return by Wednesday if still not here."

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: My Prime package was supposed to be delivered today, but it has been no where to be seen! What’s up with that? 🤷🏻‍♂️
BRAND: Uh oh! Sorry to hear you haven't received your order, Jason! What's the most recent tracking updated? You can check that info here: <URL>
```

### HISTORICAL AMAZON RESPONSE:
"Thank you for the update. Please let us know if this doesn't arrive by Wednesday."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **5.38** | Reasons: `recency:0.88, delivery_tracking_terms, temporal_deadline_anchor, root_customer_problem_anchor` | Text: *"@AmazonHelp My Prime package was supposed to be delivered today, but i..."*
- **Turn 1** (`BRAND`): Score **5.92** | Reasons: `recency:1.00, postal_code_present, delivery_tracking_terms, lexical_overlap:0.42(here,order,sorry), immediate_preceding_brand_prompt` | Text: *"@176784 Uh oh! Sorry to hear you haven't received your order, Jason! W..."*

---
## Example 26: [retrieval_doc_0132904] (Case: `amazon_case_0157669` | Conversation: `2342095`)
- **Thread Length**: 6 turns | **Turn Index**: 5

### CUSTOMER:
"I ve already filled all the deatils on the same day you replied i.e. 5 days back but unfortunately you're not doing your service."

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: 10% cashback on Email Gift Card is such a scam...cashback of which should have received in 10 days has not received in 20 days yet. Contacted Customer Care for 3 times in 10 days. No Resolution. Fake Commitment
BRAND: Sorry about the pending cash-back, Rajat. Kindly fill in your details here: <URL> and we'll get this checked for you.
CUSTOMER: Wow....what a customer service no help received yet
BRAND: I'm sorry you feel that way. Could you let us know if you have filled in your details through the link provided earlier by my colleague '^PB' through this link here <URL>
```

### HISTORICAL AMAZON RESPONSE:
"I just checked and we haven't received your details yet. Kindly resubmit your details here: <URL> and I'll contact you."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **4.27** | Reasons: `recency:0.64, postal_code_present, lexical_overlap:0.33(days,not), root_customer_problem_anchor` | Text: *"@AmazonHelp @115850 
10% cashback on Email Gift Card is such a scam......"*
- **Turn 1** (`BRAND`): Score **2.26** | Reasons: `recency:0.76, postal_code_present` | Text: *"@677448 Sorry about the pending cash-back, Rajat. Kindly fill in your ..."*
- **Turn 2** (`CUSTOMER`): Score **2.38** | Reasons: `recency:0.88, postal_code_present` | Text: *"@AmazonHelp @115850 Wow....what a customer service no help received ye..."*
- **Turn 3** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@677448 I'm sorry you feel that way. Could you let us know if you have..."*

---
## Example 27: [retrieval_doc_0139179] (Case: `amazon_case_0070789` | Conversation: `2463107`)
- **Thread Length**: 4 turns | **Turn Index**: 3

### CUSTOMER:
"Today was the estimated date. It still hasn't been dispatched and i needed the item for a birthday today. Not impressed."

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: ordered an item monday night via prime next day delivery. Was due to be delivered today but it has not even been dispatched....
BRAND: I am sorry to hear this Jenny. Can I ask, what was the estimated delivery date given on the confirmation email? Thanks.
```

### HISTORICAL AMAZON RESPONSE:
"I'm very sorry your order hasn't arrived as expected! Please reach out to us here: <URL> so we can get eyes on this order with you."

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **6.29** | Reasons: `recency:0.88, delivery_tracking_terms, temporal_deadline_anchor, lexical_overlap:0.91(item,dispatched,not), root_customer_problem_anchor` | Text: *"@AmazonHelp  ordered an item monday night via prime next day delivery...."*
- **Turn 1** (`BRAND`): Score **5.66** | Reasons: `recency:1.00, postal_code_present, temporal_deadline_anchor, lexical_overlap:0.46(date,estimated), immediate_preceding_brand_prompt` | Text: *"@258122 I am sorry to hear this Jenny. Can I ask, what was the estimat..."*

---
## Example 28: [retrieval_doc_0145909] (Case: `amazon_case_0154976` | Conversation: `2599086`)
- **Thread Length**: 22 turns | **Turn Index**: 10

### CUSTOMER:
"I don't have a fax machine (who does these days?). And how did you charge an "unverified account"? Does that make any sense?"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: I made an account with , and they offered a free trial for #amazonPrime, long story short, I'm locked out of my account, they are charging me for amazon prime, I can't cancel it or even use it. Nice going .
BRAND: Did you receive any email notification from our Account Specialists regarding the account be locked?
CUSTOMER: I received the notification about my order being cancelled (major disappointment), and some confusing email about faxing in my bank statement(?) to unfreeze my account. Not sure about any "specialist", all I know is the people on the phone when i called were completely useless.
BRAND: I'm sorry about the poor experience, it is understandably frustrating to be locked out of your account. Following the steps provided in the email from our Account Specialists, you'll be able to have your account unlocked and reset your password.
CUSTOMER: I don't care about the account at this point. I've given up on Amazon. I just want the charge cancelled and the account destroyed so that this doesn't keep happening every month.
BRAND: In order to take action on the account it would first need to be verified by sending in the required information. The email that you received has the instructions to verify the account, you can find more info here: <URL>
```

### HISTORICAL AMAZON RESPONSE:
"We can't check payments or account details through social media. When you called us directly what were you advised?"

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **3.34** | Reasons: `recency:0.04, postal_code_present, root_customer_problem_anchor` | Text: *"I made an account with @115821, and they offered a free trial for #ama..."*
- **Turn 3** (`BRAND`): Score **2.32** | Reasons: `recency:0.40, postal_code_present, lexical_overlap:0.42(any,account)` | Text: *"@735817 Did you receive any email notification from our Account Specia..."*
- **Turn 5** (`BRAND`): Score **2.14** | Reasons: `recency:0.64, postal_code_present` | Text: *"@735817 I'm sorry about the poor experience, it is understandably frus..."*
- **Turn 6** (`CUSTOMER`): Score **3.38** | Reasons: `recency:0.76, financial_terms, lexical_overlap:0.62(charge,don,account)` | Text: *"@AmazonHelp I don't care about the account at this point. I've given u..."*
- **Turn 7** (`BRAND`): Score **2.38** | Reasons: `recency:0.88, postal_code_present` | Text: *"@735817 In order to take action on the account it would first need to ..."*
- **Turn 8** (`CUSTOMER`): Score **5.50** | Reasons: `recency:1.00, financial_terms, lexical_overlap:2.50(sense,make,how)` | Text: *"@AmazonHelp I don't have a fax machine (who does these days?). And how..."*

---
## Example 29: [retrieval_doc_0153122] (Case: `amazon_case_0086265` | Conversation: `2752408`)
- **Thread Length**: 4 turns | **Turn Index**: 3

### CUSTOMER:
"This is when I ordered an item from Germany. Wondering if I should order all eletronics/gadgets from Amazon now. 🤔"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: . ; I dont tweet about personal stuff a lot here but you beat in service, variety, price and time saved.
BRAND: Thank you :)
```

### HISTORICAL AMAZON RESPONSE:
"Don't just wonder, we count on you ;)"

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **4.06** | Reasons: `recency:0.76, postal_code_present, root_customer_problem_anchor` | Text: *".@116316; 
I dont tweet about personal stuff a lot here but you beat @..."*
- **Turn 1** (`CUSTOMER`): Score **4.88** | Reasons: `recency:0.88, postal_code_present, lexical_overlap:2.50(now,item,order)` | Text: *"@116316 @40456 This is when I ordered an item from Germany. Wondering ..."*
- **Turn 2** (`BRAND`): Score **4.00** | Reasons: `recency:1.00, postal_code_present, immediate_preceding_brand_prompt` | Text: *"@770536 Thank you :) ^NW..."*

---
## Example 30: [retrieval_doc_0160596] (Case: `amazon_case_0165642` | Conversation: `2879444`)
- **Thread Length**: 21 turns | **Turn Index**: 5

### CUSTOMER:
"How can I get my November membership refunded please ?"

### SELECTED PRECEDING CONTEXT:
```text
CUSTOMER: so if a NEXT DAY amazon prime takes 3 days, how is this different from standard free delivery and what am I paying for ??
BRAND: Apologies - Prime Next-Day Shipping refers to transit time, in business days, once shipped, but we do aim to meet the delivery date provided
CUSTOMER: so theres literally no advantage to paying the monthly fee then ?
CUSTOMER: I’m glad it’s not just me that had that same issue then . Bit of a con I think 🤔
```

### HISTORICAL AMAZON RESPONSE:
"If the benefits of the membership have not been used, you can cancel your membership and get a refund here: <URL>"

### WHY CONTEXT WAS SELECTED:
- **Turn 0** (`CUSTOMER`): Score **2.86** | Reasons: `recency:0.64, lexical_overlap:0.42(how), root_customer_problem_anchor` | Text: *"@AmazonHelp so if a NEXT DAY amazon prime takes 3 days, how is this di..."*
- **Turn 1** (`BRAND`): Score **3.76** | Reasons: `recency:0.76, postal_code_present, delivery_tracking_terms` | Text: *"@147110 Apologies - Prime Next-Day Shipping refers to transit time, in..."*
- **Turn 2** (`CUSTOMER`): Score **0.88** | Reasons: `recency:0.88` | Text: *"@AmazonHelp so theres literally no advantage to paying the monthly fee..."*
- **Turn 3** (`CUSTOMER`): Score **2.50** | Reasons: `recency:1.00, postal_code_present` | Text: *"@147110 @AmazonHelp I’m glad it’s not just me that had that same issue..."*

---