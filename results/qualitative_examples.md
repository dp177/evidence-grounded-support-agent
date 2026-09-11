# Qualitative Classification Examples on Golden Evaluation Set v1

Demonstrates model predictions across three key evaluation cohorts: Top Successes, Discrepancies / Failures, and Boundary Cases.

## 1. Top 10 Strongest Successes (High Confidence & Perfect Match)

### Success 1: Case [gold_0001]
- **Customer Message**: *"rude & disrespectful delivery person who refused 2 deliver to the mentioned address until someone comes down and collects it.(1/2)"*
- **Ground Truth**: Status: `NORMAL` | Primary Intent: `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | Multi-intents: `['CARRIER_FEEDBACK_AND_INSTRUCTIONS']`
- **LLM Prediction**: Status: `NORMAL` | Primary Intent: `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | Multi-intents: `['CARRIER_FEEDBACK_AND_INSTRUCTIONS']`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer reports rude delivery agent who refused delivery unless someone came down, matching carrier misconduct/refusal intent.

### Success 2: Case [gold_0002]
- **Customer Message**: *"worst experience .your authorized agent refused to deliver my parcel at address.He want me to pickup from store. So canceled order from you ."*
- **Ground Truth**: Status: `NORMAL` | Primary Intent: `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | Multi-intents: `['CARRIER_FEEDBACK_AND_INSTRUCTIONS']`
- **LLM Prediction**: Status: `NORMAL` | Primary Intent: `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | Multi-intents: `['CARRIER_FEEDBACK_AND_INSTRUCTIONS']`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer reports carrier refused to deliver to address and requested pickup from store, which matches carrier misconduct/refusal to deliver intent.

### Success 3: Case [gold_0003]
- **Customer Message**: *"So Amazon decided an order I placed was suspicious and locked my account. Password reset appears to work but still can't log in. Ugh."*
- **Ground Truth**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **LLM Prediction**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer reports account lock and inability to log in despite password reset, matching ACCOUNT_LOGIN_ISSUES under ACCOUNT_ACCESS_AND_SECURITY. No prior actions mentioned, so INITIAL_INQUIRY.

### Success 4: Case [gold_0004]
- **Customer Message**: *"Unable to access my Amazon Account, contacted Customer care more than 5 times, still no luck, can some one help me here!"*
- **Ground Truth**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **LLM Prediction**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer reports inability to access Amazon account after multiple support contacts, indicating a login issue.

### Success 5: Case [gold_0005]
- **Customer Message**: *"I can not access my amazon account.I have not made any request to change my password and email.But they have been changed.What to do"*
- **Ground Truth**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **LLM Prediction**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer reports unauthorized changes to password and email, resulting in inability to access the account, which matches the ACCOUNT_LOGIN_ISSUES intent under ACCOUNT_ACCESS_AND_SECURITY.

### Success 6: Case [gold_0006]
- **Customer Message**: *"account hacked , my email account linked with amazon changed without authorisation. Need immediate help."*
- **Ground Truth**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **LLM Prediction**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer reports unauthorized email change on Amazon account, indicating account compromise, which maps to account login issues under ACCOUNT_ACCESS_AND_SECURITY.

### Success 7: Case [gold_0007]
- **Customer Message**: *"my amazon account got hacked wtf"*
- **Ground Truth**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **LLM Prediction**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer reports unauthorized access to their Amazon account, which matches the ACCOUNT_LOGIN_ISSUES intent under ACCOUNT_ACCESS_AND_SECURITY. No prior actions mentioned, so state is INITIAL_INQUIRY.

### Success 8: Case [gold_0008]
- **Customer Message**: *"how can I get my account back???? Someone hacked my amaZon is there a number I can contact you."*
- **Ground Truth**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **LLM Prediction**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer reports account hack and seeks to regain access, which matches ACCOUNT_LOGIN_ISSUES under ACCOUNT_ACCESS_AND_SECURITY. No prior actions mentioned, so INITIAL_INQUIRY state.

### Success 9: Case [gold_0009]
- **Customer Message**: *"I can't sign in because my account has been locked... That's what I'm trying to solve"*
- **Ground Truth**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **LLM Prediction**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer reports being unable to sign in due to account lockout, which matches ACCOUNT_LOGIN_ISSUES under ACCOUNT_ACCESS_AND_SECURITY. They previously indicated they already provided billing address details via email, satisfying DETAILS_ALREADY_PROVIDED.

### Success 10: Case [gold_0010]
- **Customer Message**: *"My amazon account is locked since 27 of October, I sent four faxes, about 12 emails and called 9 times already. The account specialist send me the same email over and over again. Im tired of this, loosing prime days and I just have about 20 more days in the US.. Thanks ."*
- **Ground Truth**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **LLM Prediction**: Status: `NORMAL` | Primary Intent: `ACCOUNT_LOGIN_ISSUES` | Multi-intents: `['ACCOUNT_LOGIN_ISSUES']`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer reports account lockout despite multiple contact attempts, seeking access restoration; matches ACCOUNT_LOGIN_ISSUES under ACCOUNT_ACCESS_AND_SECURITY. They indicate they already sent faxes, emails, and called, satisfying DETAILS_ALREADY_PROVIDED state.

## 2. Top 10 Discrepancies / Failures (Error Analysis)

### Discrepancy 1: Case [gold_0012]
- **Customer Message**: *"was expecting 2 packages by 16/10/17 - still not received. Ordered 10/10/17. Can you help?"*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary Intent: `None` | Multi-intents: `[]`
- **LLM Prediction**: Status: `NORMAL` | Primary Intent: `DELIVERY_DELAYED` | Multi-intents: `['DELIVERY_DELAYED']`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer states expected delivery date (16/10/17) has passed and packages not received, indicating a delivery delay.

### Discrepancy 2: Case [gold_0015]
- **Customer Message**: *"I got it sorted. Thanks for the help."*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary Intent: `None` | Multi-intents: `[]`
- **LLM Prediction**: Status: `OUT_OF_SCOPE` | Primary Intent: `None` | Multi-intents: `[]`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer indicates the issue is resolved and thanks support; no actionable support request is made.

### Discrepancy 3: Case [gold_0016]
- **Customer Message**: *"Thank you for the quick reply! Have a good week!"*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary Intent: `None` | Multi-intents: `[]`
- **LLM Prediction**: Status: `OUT_OF_SCOPE` | Primary Intent: `None` | Multi-intents: `[]`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer message is a thank-you sign-off with no actionable support request, thus out of scope.

### Discrepancy 4: Case [gold_0017]
- **Customer Message**: *"UPS website says delayed due to unexpected circumstances. Not very helpful."*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary Intent: `None` | Multi-intents: `[]`
- **LLM Prediction**: Status: `NORMAL` | Primary Intent: `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | Multi-intents: `['CARRIER_FEEDBACK_AND_INSTRUCTIONS']`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer is inquiring about the reason for the carrier delay, which is a common issue in delivery and fulfillment. The customer has already checked the carrier's website and found the information unhelpful, indicating a need for further assistance.

### Discrepancy 5: Case [gold_0018]
- **Customer Message**: *"Hope i m not going to get a help from you.Bye"*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary Intent: `None` | Multi-intents: `[]`
- **LLM Prediction**: Status: `OUT_OF_SCOPE` | Primary Intent: `None` | Multi-intents: `[]`
- **Confidence**: `0.95`
- **Model Reasoning**: The customer's message is a farewell statement, indicating they have given up on seeking help. This conversation is no longer about a support issue, but rather a closure.

### Discrepancy 6: Case [gold_0019]
- **Customer Message**: *"Well it turns out are a bunch of unhelpful and lying human beings! #neverbuyfromamazon #amazon"*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary Intent: `None` | Multi-intents: `[]`
- **LLM Prediction**: Status: `OUT_OF_SCOPE` | Primary Intent: `None` | Multi-intents: `[]`
- **Confidence**: `0.95`
- **Model Reasoning**: The customer's message is a social statement expressing dissatisfaction and frustration, which is not a support inquiry. It does not mention any specific issue with an order, product, or service, and is not asking for help or resolution.

### Discrepancy 7: Case [gold_0020]
- **Customer Message**: *"Need support on seller central"*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary Intent: `None` | Multi-intents: `[]`
- **LLM Prediction**: Status: `OUT_OF_SCOPE` | Primary Intent: `None` | Multi-intents: `[]`
- **Confidence**: `0.95`
- **Model Reasoning**: The customer's message is a request for support on Seller Central, which is outside the scope of AmazonHelp's taxonomy. Seller Central is a platform for third-party sellers, and this inquiry should be directed to the relevant support channel.

### Discrepancy 8: Case [gold_0021]
- **Customer Message**: *"when to get redmi5A on amazon?"*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary Intent: `None` | Multi-intents: `[]`
- **LLM Prediction**: Status: `OUT_OF_SCOPE` | Primary Intent: `None` | Multi-intents: `[]`
- **Confidence**: `0.95`
- **Model Reasoning**: The customer is inquiring about a product availability, which is not a support issue but rather a product information query.

### Discrepancy 9: Case [gold_0022]
- **Customer Message**: *"No, a resolution was not offered, nor did they attempt to call me back."*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary Intent: `None` | Multi-intents: `[]`
- **LLM Prediction**: Status: `NORMAL` | Primary Intent: `DELIVERY_DELAYED` | Multi-intents: `['DELIVERY_DELAYED']`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer is frustrated about delayed delivery and lack of resolution from previous customer service interaction, which indicates a delivery issue and a potential carrier issue.

### Discrepancy 10: Case [gold_0023]
- **Customer Message**: *"I private messaged you! And still no reply!"*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary Intent: `None` | Multi-intents: `[]`
- **LLM Prediction**: Status: `OUT_OF_SCOPE` | Primary Intent: `None` | Multi-intents: `[]`
- **Confidence**: `0.95`
- **Model Reasoning**: The customer's message is a complaint about not receiving a reply to a private message, which is not a valid support inquiry in the AmazonHelp taxonomy.

## 3. Top 10 Boundary Cases (Disambiguation & Domain Control)

### Boundary Case 1: Case [gold_0011] (MISMATCH)
- **Customer Message**: *"Is it necessary to send fax ?? Can't we send email with supporting documents ??"*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary: `None` | All: `[]`
- **LLM Prediction**: Status: `NORMAL` | Primary: `ACCOUNT_LOGIN_ISSUES` | All: `['ACCOUNT_LOGIN_ISSUES']`
- **Confidence**: `0.90`
- **Model Reasoning**: Customer asks about fax vs email for submitting documents to resolve account hold, indicating an account access/verification issue; they previously sent details via fax, satisfying DETAILS_ALREADY_PROVIDED.

### Boundary Case 2: Case [gold_0012] (MISMATCH)
- **Customer Message**: *"was expecting 2 packages by 16/10/17 - still not received. Ordered 10/10/17. Can you help?"*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary: `None` | All: `[]`
- **LLM Prediction**: Status: `NORMAL` | Primary: `DELIVERY_DELAYED` | All: `['DELIVERY_DELAYED']`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer states expected delivery date (16/10/17) has passed and packages not received, indicating a delivery delay.

### Boundary Case 3: Case [gold_0013] (MISMATCH)
- **Customer Message**: *"people at +12062662992 not helpful at all."*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary: `None` | All: `[]`
- **LLM Prediction**: Status: `NORMAL` | Primary: `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | All: `['CARRIER_FEEDBACK_AND_INSTRUCTIONS']`
- **Confidence**: `0.90`
- **Model Reasoning**: Customer reports unhelpful service when calling a phone number, indicating they have already contacted the carrier and experienced poor service, matching CARRIER_FEEDBACK_AND_INSTRUCTIONS.

### Boundary Case 4: Case [gold_0014] (MATCH)
- **Customer Message**: *"can I DM you instead?"*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary: `None` | All: `[]`
- **LLM Prediction**: Status: `AMBIGUOUS` | Primary: `None` | All: `[]`
- **Confidence**: `0.85`
- **Model Reasoning**: Customer asks to switch to DM without stating a specific support issue, making the intent ambiguous.

### Boundary Case 5: Case [gold_0015] (MISMATCH)
- **Customer Message**: *"I got it sorted. Thanks for the help."*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary: `None` | All: `[]`
- **LLM Prediction**: Status: `OUT_OF_SCOPE` | Primary: `None` | All: `[]`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer indicates the issue is resolved and thanks support; no actionable support request is made.

### Boundary Case 6: Case [gold_0016] (MISMATCH)
- **Customer Message**: *"Thank you for the quick reply! Have a good week!"*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary: `None` | All: `[]`
- **LLM Prediction**: Status: `OUT_OF_SCOPE` | Primary: `None` | All: `[]`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer message is a thank-you sign-off with no actionable support request, thus out of scope.

### Boundary Case 7: Case [gold_0017] (MISMATCH)
- **Customer Message**: *"UPS website says delayed due to unexpected circumstances. Not very helpful."*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary: `None` | All: `[]`
- **LLM Prediction**: Status: `NORMAL` | Primary: `CARRIER_FEEDBACK_AND_INSTRUCTIONS` | All: `['CARRIER_FEEDBACK_AND_INSTRUCTIONS']`
- **Confidence**: `0.95`
- **Model Reasoning**: Customer is inquiring about the reason for the carrier delay, which is a common issue in delivery and fulfillment. The customer has already checked the carrier's website and found the information unhelpful, indicating a need for further assistance.

### Boundary Case 8: Case [gold_0018] (MISMATCH)
- **Customer Message**: *"Hope i m not going to get a help from you.Bye"*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary: `None` | All: `[]`
- **LLM Prediction**: Status: `OUT_OF_SCOPE` | Primary: `None` | All: `[]`
- **Confidence**: `0.95`
- **Model Reasoning**: The customer's message is a farewell statement, indicating they have given up on seeking help. This conversation is no longer about a support issue, but rather a closure.

### Boundary Case 9: Case [gold_0019] (MISMATCH)
- **Customer Message**: *"Well it turns out are a bunch of unhelpful and lying human beings! #neverbuyfromamazon #amazon"*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary: `None` | All: `[]`
- **LLM Prediction**: Status: `OUT_OF_SCOPE` | Primary: `None` | All: `[]`
- **Confidence**: `0.95`
- **Model Reasoning**: The customer's message is a social statement expressing dissatisfaction and frustration, which is not a support inquiry. It does not mention any specific issue with an order, product, or service, and is not asking for help or resolution.

### Boundary Case 10: Case [gold_0020] (MISMATCH)
- **Customer Message**: *"Need support on seller central"*
- **Ground Truth**: Status: `AMBIGUOUS` | Primary: `None` | All: `[]`
- **LLM Prediction**: Status: `OUT_OF_SCOPE` | Primary: `None` | All: `[]`
- **Confidence**: `0.95`
- **Model Reasoning**: The customer's message is a request for support on Seller Central, which is outside the scope of AmazonHelp's taxonomy. Seller Central is a platform for third-party sellers, and this inquiry should be directed to the relevant support channel.
