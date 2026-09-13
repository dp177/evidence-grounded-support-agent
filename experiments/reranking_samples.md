# Reranking Query Samples

## Query 1: gold_0001
**Query**: rude & disrespectful delivery person who refused 2 deliver to the mentioned address until someone comes down and collects it.(1/2)
**Predicted Intent**: CARRIER_FEEDBACK_AND_INSTRUCTIONS

### Semantic Top 5
1. [Grade 0] Score: 0.7307 | Conv: 2267134 | I'm so sorry to hear about this! Please reach out to us here: <URL>
2. [Grade 0] Score: 0.6853 | Conv: 236602 | I'm sorry for the bad behaviour of the delivery associate. This is certainly not what we want our customers (1/3)
3. [Grade 1] Score: 0.6693 | Conv: 1687779 | Sorry about the bad experience. Please connect with us here: <URL> so we can get this escalated.
4. [Grade 1] Score: 0.6686 | Conv: 1068738 | Sorry to hear that. Have you reported this to our support team here: <URL>
5. [Grade 1] Score: 0.6668 | Conv: 563939 | I'm so sorry to hear this! That's definitely not the service we pride ourselves in providing. We'd like to take a look into this with you. When you have the chance, please get in contact with us here: <URL>

### Reranked Top 5
1. [Grade 0] Rerank: 0.7213 (Sem: 0.6853) | Conv: 236602 | I'm sorry for the bad behaviour of the delivery associate. This is certainly not what we want our customers (1/3)
2. [Grade 1] Rerank: 0.7001 (Sem: 0.6693) | Conv: 1687779 | Sorry about the bad experience. Please connect with us here: <URL> so we can get this escalated.
3. [Grade 1] Rerank: 0.6921 (Sem: 0.6341) | Conv: 1490296 | I understand your frustration, we definitely don't want to let you down. My team would like to escalate this. Please provide more order details here: <URL>
4. [Grade 1] Rerank: 0.6630 (Sem: 0.6537) | Conv: 2956972 | Looks like you had an unpleasant delivery experience and I'm sorry about it, Afridi. Please tell us more about the issue so we can assist accordingly.
5. [Grade 1] Rerank: 0.6563 (Sem: 0.6385) | Conv: 1625994 | Apologies for the delay, Shivanand. I understand how upsetting this can get. We'd like to look into it. Kindly report 1/2

---

## Query 2: gold_0002
**Query**: worst experience .your authorized agent refused to deliver my parcel at address.He want me to pickup from store. So canceled order from you .
**Predicted Intent**: CARRIER_FEEDBACK_AND_INSTRUCTIONS

### Semantic Top 5
1. [Grade 1] Score: 0.6940 | Conv: 1068738 | Sorry to hear that. Have you reported this to our support team here: <URL>
2. [Grade 1] Score: 0.6665 | Conv: 2267134 | I'm so sorry to hear about this! Please reach out to us here: <URL>
3. [Grade 1] Score: 0.6457 | Conv: 1099768 | Please reply to our email correspondence so that we could get this checked for you.
4. [Grade 1] Score: 0.6433 | Conv: 1490296 | I understand your frustration, we definitely don't want to let you down. My team would like to escalate this. Please provide more order details here: <URL>
5. [Grade 1] Score: 0.6263 | Conv: 1210705 | I understand your concern. I’d like to take a closer look & help you with the delivery of your package, please fill this(1/3)^SY

### Reranked Top 5
1. [Grade 1] Rerank: 0.6732 (Sem: 0.6457) | Conv: 1099768 | Please reply to our email correspondence so that we could get this checked for you.
2. [Grade 1] Rerank: 0.6698 (Sem: 0.6263) | Conv: 1210705 | I understand your concern. I’d like to take a closer look & help you with the delivery of your package, please fill this(1/3)^SY
3. [Grade 1] Rerank: 0.6543 (Sem: 0.6123) | Conv: 832370 | here: <URL> we'll get back to you soon. 2/2^AP
4. [Grade 1] Rerank: 0.6519 (Sem: 0.6433) | Conv: 1490296 | I understand your frustration, we definitely don't want to let you down. My team would like to escalate this. Please provide more order details here: <URL>
5. [Grade 1] Rerank: 0.6468 (Sem: 0.5875) | Conv: 1020076 | I'm sorry you don't have your parcel! Please reach out to us via phone/chat here: <URL> and we can help with this!

---

## Query 3: gold_0003
**Query**: So Amazon decided an order I placed was suspicious and locked my account. Password reset appears to work but still can't log in. Ugh.
**Predicted Intent**: ACCOUNT_LOGIN_ISSUES

### Semantic Top 5
1. [Grade 2] Score: 0.8480 | Conv: 141988 | Thanks for the update! We'd be happy to help, can you let us know which site you're using ( <URL> <URL> Amazon.cn, etc.)?
2. [Grade 0] Score: 0.7800 | Conv: 1227120 | I'm sorry for the log-in issues! Our Account Specialists will be in the best position to assist: <URL>
3. [Grade 2] Score: 0.7614 | Conv: 1692613 | Hello, John! I'm sorry to hear of your issue. We have no account access but are waiting to help here: <URL>
4. [Grade 3] Score: 0.7563 | Conv: 701314 | Hello Steve, sorry you're having login issues. If you navigate here: <URL> and enter your email or mobile number the webpage will guide you through the steps to reset your password.
5. [Grade 3] Score: 0.7552 | Conv: 2931386 | As we can't see any of your details on social media, please press the link provided by and we will be happy to help further.^BZ

### Reranked Top 5
1. [Grade 2] Rerank: 0.8917 (Sem: 0.8480) | Conv: 141988 | Thanks for the update! We'd be happy to help, can you let us know which site you're using ( <URL> <URL> Amazon.cn, etc.)?
2. [Grade 3] Rerank: 0.8331 (Sem: 0.7543) | Conv: 2435007 | When you click on the link, it will take you to a sign in page. Under where it says keep me signed in, you will see if you don't have an account or can't access your account, you can skip sign in. Just click the blue skip sign in.
3. [Grade 0] Rerank: 0.8285 (Sem: 0.7800) | Conv: 1227120 | I'm sorry for the log-in issues! Our Account Specialists will be in the best position to assist: <URL>
4. [Grade 0] Rerank: 0.7969 (Sem: 0.7452) | Conv: 1616054 | Oh gosh! Have you tried using the "Forgot your password" feature on the website? Check it out: <URL>
5. [Grade 3] Rerank: 0.7916 (Sem: 0.7563) | Conv: 701314 | Hello Steve, sorry you're having login issues. If you navigate here: <URL> and enter your email or mobile number the webpage will guide you through the steps to reset your password.

---

## Query 4: gold_0004
**Query**: Unable to access my Amazon Account, contacted Customer care more than 5 times, still no luck, can some one help me here!
**Predicted Intent**: ACCOUNT_LOGIN_ISSUES

### Semantic Top 5
1. [Grade 0] Score: 0.7457 | Conv: 2298791 | I'm sorry for the trouble, Kelsea! Without giving specific account or personal information, as we don't have access via Twitter, can you tell us a bit more about the issue and what's happening? We're here to help!
2. [Grade 0] Score: 0.7405 | Conv: 1238990 | I'm so sorry, Heath! Without sharing personal information, can you please tell us a little more about what's happening?
3. [Grade 0] Score: 0.7388 | Conv: 29490 | Without giving account specifics, can you tell us a little more about the issue you're experiencing?
4. [Grade 0] Score: 0.7344 | Conv: 1223600 | I'm sorry about the hassle. Could you let us know what went wrong? We'd like to help.
5. [Grade 0] Score: 0.7303 | Conv: 246963 | We're unable to contact you over Twitter. Fill in your details here: <URL> and we'll contact you.

### Reranked Top 5
1. [Grade 0] Rerank: 0.7942 (Sem: 0.7405) | Conv: 1238990 | I'm so sorry, Heath! Without sharing personal information, can you please tell us a little more about what's happening?
2. [Grade 0] Rerank: 0.7906 (Sem: 0.7196) | Conv: 2724564 | Sure thing! What can I help you with?
3. [Grade 0] Rerank: 0.7602 (Sem: 0.7457) | Conv: 2298791 | I'm sorry for the trouble, Kelsea! Without giving specific account or personal information, as we don't have access via Twitter, can you tell us a bit more about the issue and what's happening? We're here to help!
4. [Grade 0] Rerank: 0.7558 (Sem: 0.7303) | Conv: 246963 | We're unable to contact you over Twitter. Fill in your details here: <URL> and we'll contact you.
5. [Grade 0] Rerank: 0.7542 (Sem: 0.7282) | Conv: 2950853 | I'm sorry for any frustration! Please reach out to us about the account by e-mail or phone: <URL>

---

## Query 5: gold_0005
**Query**: I can not access my amazon account.I have not made any request to change my password and email.But they have been changed.What to do
**Predicted Intent**: ACCOUNT_LOGIN_ISSUES

### Semantic Top 5
1. [Grade 3] Score: 0.7630 | Conv: 49919 | We'd like to help get this looked into for you. Please reach out to us by phone at this link here: <URL>
2. [Grade 2] Score: 0.7497 | Conv: 1936449 | I am sorry about the troubles with your account! Let's see what we can do to help! Try this: <URL>
3. [Grade 2] Score: 0.7449 | Conv: 721438 | I'm sorry about this e-mail issue. We'd like to assist. Please reach out to us here: <URL>
4. [Grade 2] Score: 0.7388 | Conv: 1838888 | If you are unable to access your account, please get in touch via <URL>
5. [Grade 2] Score: 0.7245 | Conv: 1278109 | Oh no! When you spoke with us, what insights were provided? Have you been able to check junk and spam folders as well?

### Reranked Top 5
1. [Grade 2] Rerank: 0.8435 (Sem: 0.7497) | Conv: 1936449 | I am sorry about the troubles with your account! Let's see what we can do to help! Try this: <URL>
2. [Grade 2] Rerank: 0.7852 (Sem: 0.7388) | Conv: 1838888 | If you are unable to access your account, please get in touch via <URL>
3. [Grade 2] Rerank: 0.7800 (Sem: 0.7449) | Conv: 721438 | I'm sorry about this e-mail issue. We'd like to assist. Please reach out to us here: <URL>
4. [Grade 3] Rerank: 0.7676 (Sem: 0.6964) | Conv: 2931386 | As we can't see any of your details on social media, please press the link provided by and we will be happy to help further.^BZ
5. [Grade 0] Rerank: 0.7622 (Sem: 0.6888) | Conv: 2915845 | I'm sorry for the trouble with your account. For security reasons, we recommend not sharing your e-mail address through Twitter. Have you received any e-mails from our Account Specialists?

---

## Query 6: gold_0006
**Query**: account hacked , my email account linked with amazon changed without authorisation. Need immediate help.
**Predicted Intent**: ACCOUNT_LOGIN_ISSUES

### Semantic Top 5
1. [Grade 3] Score: 0.8447 | Conv: 49919 | We'd like to help get this looked into for you. Please reach out to us by phone at this link here: <URL>
2. [Grade 2] Score: 0.8365 | Conv: 1838888 | If you are unable to access your account, please get in touch via <URL>
3. [Grade 2] Score: 0.8338 | Conv: 2324479 | Hello, I will be replying to your DM straight away.
4. [Grade 3] Score: 0.8059 | Conv: 1445502 | I'm sorry for the account troubles. Have you received an e-mail from our Account Specialist? Check spam folder as well
5. [Grade 0] Score: 0.8027 | Conv: 2950853 | I'm sorry for any frustration! Please reach out to us about the account by e-mail or phone: <URL>

### Reranked Top 5
1. [Grade 2] Rerank: 0.9059 (Sem: 0.8338) | Conv: 2324479 | Hello, I will be replying to your DM straight away.
2. [Grade 2] Rerank: 0.8895 (Sem: 0.8365) | Conv: 1838888 | If you are unable to access your account, please get in touch via <URL>
3. [Grade 2] Rerank: 0.8338 (Sem: 0.7919) | Conv: 1936449 | I am sorry about the troubles with your account! Let's see what we can do to help! Try this: <URL>
4. [Grade 3] Rerank: 0.8302 (Sem: 0.8059) | Conv: 1445502 | I'm sorry for the account troubles. Have you received an e-mail from our Account Specialist? Check spam folder as well
5. [Grade 0] Rerank: 0.8225 (Sem: 0.8027) | Conv: 2950853 | I'm sorry for any frustration! Please reach out to us about the account by e-mail or phone: <URL>

---

## Query 7: gold_0007
**Query**: my amazon account got hacked wtf
**Predicted Intent**: ACCOUNT_LOGIN_ISSUES

### Semantic Top 5
1. [Grade 3] Score: 0.8436 | Conv: 49919 | We'd like to help get this looked into for you. Please reach out to us by phone at this link here: <URL>
2. [Grade 2] Score: 0.8319 | Conv: 1936449 | I am sorry about the troubles with your account! Let's see what we can do to help! Try this: <URL>
3. [Grade 3] Score: 0.7957 | Conv: 1445502 | I'm sorry for the account troubles. Have you received an e-mail from our Account Specialist? Check spam folder as well
4. [Grade 2] Score: 0.7901 | Conv: 2664954 | We'd like to check that for you. Get in touch here: <URL> and we'll be happy to help.
5. [Grade 0] Score: 0.7901 | Conv: 302603 | Sorry to hear about your account! Please get in touch with us here: <URL> for further assistance.

### Reranked Top 5
1. [Grade 2] Rerank: 0.8783 (Sem: 0.8319) | Conv: 1936449 | I am sorry about the troubles with your account! Let's see what we can do to help! Try this: <URL>
2. [Grade 3] Rerank: 0.8254 (Sem: 0.7329) | Conv: 1773801 | (2/2) If you haven't provided your info for our account specialist, please do so via the link: <URL>
3. [Grade 2] Rerank: 0.8221 (Sem: 0.7901) | Conv: 2664954 | We'd like to check that for you. Get in touch here: <URL> and we'll be happy to help.
4. [Grade 3] Rerank: 0.8202 (Sem: 0.7957) | Conv: 1445502 | I'm sorry for the account troubles. Have you received an e-mail from our Account Specialist? Check spam folder as well
5. [Grade 2] Rerank: 0.8064 (Sem: 0.7854) | Conv: 1587290 | Please get in touch with my colleagues from our customer service: <URL> They are pleased to assist you.

---

## Query 8: gold_0008
**Query**: how can I get my account back???? Someone hacked my amaZon is there a number I can contact you.
**Predicted Intent**: ACCOUNT_LOGIN_ISSUES

### Semantic Top 5
1. [Grade 0] Score: 0.8515 | Conv: 2950853 | I'm sorry for any frustration! Please reach out to us about the account by e-mail or phone: <URL>
2. [Grade 0] Score: 0.8477 | Conv: 302603 | Sorry to hear about your account! Please get in touch with us here: <URL> for further assistance.
3. [Grade 3] Score: 0.8287 | Conv: 49919 | We'd like to help get this looked into for you. Please reach out to us by phone at this link here: <URL>
4. [Grade 2] Score: 0.8099 | Conv: 1936449 | I am sorry about the troubles with your account! Let's see what we can do to help! Try this: <URL>
5. [Grade 3] Score: 0.8095 | Conv: 352791 | Sorry to hear that, please call us on the number found via this link: <URL> so it can be escalated.

### Reranked Top 5
1. [Grade 0] Rerank: 0.9512 (Sem: 0.8515) | Conv: 2950853 | I'm sorry for any frustration! Please reach out to us about the account by e-mail or phone: <URL>
2. [Grade 0] Rerank: 0.8871 (Sem: 0.7889) | Conv: 306170 | We'd like to be sure there isn't! Just to confirm, what information and options were provided to you when you called us?
3. [Grade 2] Rerank: 0.8575 (Sem: 0.8099) | Conv: 1936449 | I am sorry about the troubles with your account! Let's see what we can do to help! Try this: <URL>
4. [Grade 2] Rerank: 0.8204 (Sem: 0.7740) | Conv: 2664954 | We'd like to check that for you. Get in touch here: <URL> and we'll be happy to help.
5. [Grade 0] Rerank: 0.8152 (Sem: 0.7810) | Conv: 2377209 | You're welcome! Please keep us updated on the outcome!

---

## Query 9: gold_0009
**Query**: I can't sign in because my account has been locked... That's what I'm trying to solve
**Predicted Intent**: ACCOUNT_LOGIN_ISSUES

### Semantic Top 5
1. [Grade 0] Score: 0.7840 | Conv: 889429 | Were you able to send the Account Specialist the requested information? Please let us know!
2. [Grade 0] Score: 0.7835 | Conv: 1800829 | Please contact us by phone to discuss this issue using the number found here: <URL>
3. [Grade 2] Score: 0.7778 | Conv: 783804 | it and the team would reach out to you. (2/2)
4. [Grade 3] Score: 0.7748 | Conv: 2281468 | Have you received an email asking you for more details? Please make sure to check your spam/junk folder.
5. [Grade 0] Score: 0.7726 | Conv: 222653 | You may respond to that email and our specialist team will be getting back to you. Appreciate your understanding. (2/2)

### Reranked Top 5
1. [Grade 2] Rerank: 0.8529 (Sem: 0.7778) | Conv: 783804 | it and the team would reach out to you. (2/2)
2. [Grade 0] Rerank: 0.8363 (Sem: 0.7395) | Conv: 1890553 | If you reply to the account specialists email directly with the required info, they will be able to assist.^ES
3. [Grade 3] Rerank: 0.8351 (Sem: 0.7463) | Conv: 2230056 | Sorry about that, please use this link instead: <URL>
4. [Grade 0] Rerank: 0.8338 (Sem: 0.7840) | Conv: 889429 | Were you able to send the Account Specialist the requested information? Please let us know!
5. [Grade 3] Rerank: 0.8289 (Sem: 0.7473) | Conv: 2435007 | When you click on the link, it will take you to a sign in page. Under where it says keep me signed in, you will see if you don't have an account or can't access your account, you can skip sign in. Just click the blue skip sign in.

---

## Query 10: gold_0010
**Query**: My amazon account is locked since 27 of October, I sent four faxes, about 12 emails and called 9 times already. The account specialist send me the same email over and over again. Im tired of this, loosing prime days and I just have about 20 more days in the US.. Thanks .
**Predicted Intent**: ACCOUNT_LOGIN_ISSUES

### Semantic Top 5
1. [Grade 0] Score: 0.7696 | Conv: 1015653 | Have you had a chance to check your junk/spam folders in case your e-mail provider automatically filters them there?
2. [Grade 0] Score: 0.7448 | Conv: 2722602 | I'm sorry this is happening, Casey! When you have a free moment, please contact us here directly so that one of my teammates can research this for you: <URL>
3. [Grade 0] Score: 0.7433 | Conv: 1223637 | I understand your concern regarding your account. Please fill out this form: <URL> and we'll look into this for you.
4. [Grade 3] Score: 0.7124 | Conv: 404086 | The account specialist team will be in the best position to help. Please respond to their email for further assistance.
5. [Grade 0] Score: 0.6555 | Conv: 1572924 | I'm sorry for the troubles! Have you received an e-mail asking for info to be faxed? Be sure to check your spam/junk folder.

### Reranked Top 5
1. [Grade 0] Rerank: 0.8103 (Sem: 0.7696) | Conv: 1015653 | Have you had a chance to check your junk/spam folders in case your e-mail provider automatically filters them there?
2. [Grade 0] Rerank: 0.7983 (Sem: 0.7433) | Conv: 1223637 | I understand your concern regarding your account. Please fill out this form: <URL> and we'll look into this for you.
3. [Grade 0] Rerank: 0.7973 (Sem: 0.7448) | Conv: 2722602 | I'm sorry this is happening, Casey! When you have a free moment, please contact us here directly so that one of my teammates can research this for you: <URL>
4. [Grade 3] Rerank: 0.7469 (Sem: 0.7124) | Conv: 404086 | The account specialist team will be in the best position to help. Please respond to their email for further assistance.
5. [Grade 3] Rerank: 0.6878 (Sem: 0.6193) | Conv: 787125 | Please check your spam folder as you should have received an email from an Account Specialist by now.

---

## Query 11: gold_0011
**Query**: Is it necessary to send fax ?? Can't we send email with supporting documents ??
**Predicted Intent**: OUT_OF_SCOPE

### Semantic Top 5
1. [Grade 1] Score: 0.7582 | Conv: 2722602 | I'm sorry this is happening, Casey! When you have a free moment, please contact us here directly so that one of my teammates can research this for you: <URL>
2. [Grade 0] Score: 0.7553 | Conv: 856569 | I'm afraid our team would need the details to be sent via fax so that they can take it further & help un-hold the account.
3. [Grade 1] Score: 0.7206 | Conv: 404086 | The account specialist team will be in the best position to help. Please respond to their email for further assistance.
4. [Grade 1] Score: 0.7070 | Conv: 1015653 | Have you had a chance to check your junk/spam folders in case your e-mail provider automatically filters them there?
5. [Grade 0] Score: 0.6946 | Conv: 836906 | In order to regain access to your account you will need to fax in the required documents, thanks.

### Reranked Top 5
1. [Grade 1] Rerank: 0.8202 (Sem: 0.7582) | Conv: 2722602 | I'm sorry this is happening, Casey! When you have a free moment, please contact us here directly so that one of my teammates can research this for you: <URL>
2. [Grade 1] Rerank: 0.8034 (Sem: 0.7206) | Conv: 404086 | The account specialist team will be in the best position to help. Please respond to their email for further assistance.
3. [Grade 0] Rerank: 0.7864 (Sem: 0.7553) | Conv: 856569 | I'm afraid our team would need the details to be sent via fax so that they can take it further & help un-hold the account.
4. [Grade 1] Rerank: 0.7847 (Sem: 0.6918) | Conv: 2216627 | As informed earlier, you would have received an email from our Specialist team to your registered email ID. Please reply to that email with your concerns.
5. [Grade 0] Rerank: 0.7748 (Sem: 0.6946) | Conv: 836906 | In order to regain access to your account you will need to fax in the required documents, thanks.

---

## Query 12: gold_0012
**Query**: was expecting 2 packages by 16/10/17 - still not received. Ordered 10/10/17. Can you help?
**Predicted Intent**: OUT_OF_SCOPE

### Semantic Top 5
1. [Grade 0] Score: 0.7003 | Conv: 777173 | We'd like to assist you with this via phone or chat, please reach us directly using this link: <URL>
2. [Grade 0] Score: 0.6839 | Conv: 227095 | Sorry about that. Kindly get in touch with us here: <URL> and we’ll be glad to help you.
3. [Grade 1] Score: 0.6791 | Conv: 2300782 | Oh no! Were both packages expected to be delivered today? Let us know! We'd like to help!
4. [Grade 0] Score: 0.6615 | Conv: 712494 | We always strive to deliver by the date provided in your confirmation e-mail. Please let us know if it hasn't arrived by 10/17!^ML
5. [Grade 0] Score: 0.6613 | Conv: 2283454 | We don't want to speculate, however by 15th if you indicate 15th of November, we'd request you to kindly wait till then.

### Reranked Top 5
1. [Grade 0] Rerank: 0.8215 (Sem: 0.6615) | Conv: 712494 | We always strive to deliver by the date provided in your confirmation e-mail. Please let us know if it hasn't arrived by 10/17!^ML
2. [Grade 0] Rerank: 0.7689 (Sem: 0.7003) | Conv: 777173 | We'd like to assist you with this via phone or chat, please reach us directly using this link: <URL>
3. [Grade 1] Rerank: 0.7496 (Sem: 0.6421) | Conv: 1434040 | We're here to help! Are we missing the delivery date provided at checkout on these orders, Mickloud? If so, who's the carrier?
4. [Grade 1] Rerank: 0.7454 (Sem: 0.6298) | Conv: 717027 | Hey! I'm sorry you haven't received your package yet. We'd love to help! Has the delivery date listed on the order passed yet?
5. [Grade 0] Rerank: 0.6905 (Sem: 0.6839) | Conv: 227095 | Sorry about that. Kindly get in touch with us here: <URL> and we’ll be glad to help you.

---

## Query 13: gold_0013
**Query**: people at +12062662992 not helpful at all.
**Predicted Intent**: OUT_OF_SCOPE

### Semantic Top 5
1. [Grade 0] Score: 0.6612 | Conv: 2980917 | We do not have access to your order/account details on social platform. Please fill this form: <URL> and I’ll contact you at the earliest.
2. [Grade 0] Score: 0.6451 | Conv: 832122 | look into the issue and get back to you. 2/3
3. [Grade 0] Score: 0.6350 | Conv: 676965 | we consider it to be personal information. Our page is visible to the public.2/2^AR
4. [Grade 0] Score: 0.6331 | Conv: 1061334 | Please don't provide your order details, as we consider it to be personal information. Our Twitter page is public. 3/3
5. [Grade 0] Score: 0.6303 | Conv: 2614114 | As we don't have access to your Amazon account over Twitter, please share the details in the link provided above and we'll assist you. Also, Please don't provide your order details, we consider it to be personal information.Our page is visible to the public.^SU

### Reranked Top 5
1. [Grade 0] Rerank: 0.6700 (Sem: 0.6451) | Conv: 832122 | look into the issue and get back to you. 2/3
2. [Grade 0] Rerank: 0.6612 (Sem: 0.6612) | Conv: 2980917 | We do not have access to your order/account details on social platform. Please fill this form: <URL> and I’ll contact you at the earliest.
3. [Grade 0] Rerank: 0.6596 (Sem: 0.6232) | Conv: 232341 | Apologies for not getting connected via phone. You may connect using chat or email and report the same.
4. [Grade 0] Rerank: 0.6565 (Sem: 0.6076) | Conv: 2216610 | Please don't provide your order details, as we consider it to be personal information. Our Twitter page is visible to the public. 2/2
5. [Grade 0] Rerank: 0.6510 (Sem: 0.5998) | Conv: 291754 | Sorry for the delay. We're working on the issue. We'll get back to you at the earliest.

---

## Query 14: gold_0014
**Query**: can I DM you instead?
**Predicted Intent**: OUT_OF_SCOPE

### Semantic Top 5
1. [Grade 0] Score: 0.6115 | Conv: 2668792 | Hi Kat, you can get in touch with us here: <URL>
2. [Grade 0] Score: 0.5938 | Conv: 2102467 | Absolutely! Feel free to send us a DM, we'd love to help! <URL>
3. [Grade 0] Score: 0.5891 | Conv: 1919856 | You can DM us, or contact us directly at: <URL> <URL>
4. [Grade 0] Score: 0.5848 | Conv: 686662 | Yup, we received the DM, we'll get back to you shortly!
5. [Grade 0] Score: 0.5713 | Conv: 1043156 | I am so sorry about that, Mitesh! Without giving account information, can you tell us more about what's going on?

### Reranked Top 5
1. [Grade 0] Rerank: 0.7019 (Sem: 0.6115) | Conv: 2668792 | Hi Kat, you can get in touch with us here: <URL>
2. [Grade 0] Rerank: 0.6195 (Sem: 0.5848) | Conv: 686662 | Yup, we received the DM, we'll get back to you shortly!
3. [Grade 0] Rerank: 0.6061 (Sem: 0.5671) | Conv: 1456300 | You can Private Message us here. <URL>
4. [Grade 0] Rerank: 0.6013 (Sem: 0.5713) | Conv: 1043156 | I am so sorry about that, Mitesh! Without giving account information, can you tell us more about what's going on?
5. [Grade 0] Rerank: 0.5595 (Sem: 0.4930) | Conv: 390805 | We've responded to you via DM.

---

## Query 15: gold_0015
**Query**: I got it sorted. Thanks for the help.
**Predicted Intent**: OUT_OF_SCOPE

### Semantic Top 5
1. [Grade 0] Score: 0.6942 | Conv: 38828 | We've sent the correspondence to your registered email ID. Kindly check it here: <URL>
2. [Grade 0] Score: 0.6770 | Conv: 2761261 | I'm sorry for the delay. That's not the type of service that we aim to provide. Please let us know if you don't receive your order by Thursday.
3. [Grade 0] Score: 0.6654 | Conv: 2679762 | Apologies for the trouble with delivery. Please share your details here: <URL> & we'll help you.
4. [Grade 0] Score: 0.6654 | Conv: 1303775 | Sorry for the trouble you've had. Kindly fill in your details here: <URL> and I'll help you with it.
5. [Grade 0] Score: 0.6649 | Conv: 1237575 | I'm sorry for the wait! What order status and delivery date(s) are you currently seeing here: <URL>

### Reranked Top 5
1. [Grade 0] Rerank: 0.7420 (Sem: 0.6770) | Conv: 2761261 | I'm sorry for the delay. That's not the type of service that we aim to provide. Please let us know if you don't receive your order by Thursday.
2. [Grade 0] Rerank: 0.7053 (Sem: 0.6942) | Conv: 38828 | We've sent the correspondence to your registered email ID. Kindly check it here: <URL>
3. [Grade 0] Rerank: 0.7046 (Sem: 0.6436) | Conv: 1184730 | Thanks for clarifying. The email received, can you see if it's from Amazon .com or .co.uk ?
4. [Grade 0] Rerank: 0.6930 (Sem: 0.6110) | Conv: 1252578 | Kindly fill this form: <URL> and I’ll contact you soon. 2/3
5. [Grade 0] Rerank: 0.6928 (Sem: 0.6654) | Conv: 1303775 | Sorry for the trouble you've had. Kindly fill in your details here: <URL> and I'll help you with it.

---

