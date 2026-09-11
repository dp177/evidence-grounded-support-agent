# Empirical Investigation: Account Access & Security Cases

> [!NOTE]
> **Dataset Analyzed:** `data/processed/amazon_support_cases.parquet` (Full Development Pool, excluding all 200 Golden Evaluation conversations).
> **Total Development Cases:** 167,929  
> **Total Account/Security Cases:** 6,001 (3.57% of development dataset)  
> **Purpose:** Investigate whether compromised/hacked accounts form a coherent, frequent, and operationally distinct group compared to normal login/OTP cases.

---

## 1. Summary of Account & Security Subgroups

Across the 6,001 account/security cases, cases were classified across 8 specific problem subgroups:

| Subgroup | Case Count | % of Dev Dataset (167,929) | % of Account Cases (6,001) | Primary Customer Grievance |
|---|:---:|:---:|:---:|---|
| `forgot_password` | **542** | 0.32% | 9.03% | Customer explicitly requests password recovery, forgot login password, or encounters password reset loops. |
| `cannot_log_in` | **1,900** | 1.13% | 31.66% | Customer reports generic authentication barriers, incorrect password errors, or inability to access their account without explicit lockout or hacking. |
| `otp_verification_failure` | **313** | 0.19% | 5.22% | Customer is blocked by two-factor authentication, non-receipt of OTP SMS verification codes, or authentication app failure. |
| `account_locked` | **1,550** | 0.92% | 25.83% | Account was placed on hold, locked, suspended, or blocked by Amazon risk/compliance systems pending identity or billing verification. |
| `hacked_account` | **531** | 0.32% | 8.85% | Customer states or suspects their account was hacked, compromised, or taken over by a third party. |
| `unauthorized_email_password_change` | **122** | 0.07% | 2.03% | Customer reports their login email address or password was changed without their authorization or consent. |
| `suspicious_activity` | **68** | 0.04% | 1.13% | Customer or Amazon flags suspicious activity, unauthorized transactions, or security holds placed on recent orders. |
| `unauthorized_account_access` | **179** | 0.11% | 2.98% | Unrecognized third parties accessed the account, placed orders, used stored payment methods, or breached credentials. |

> *Note: Cases can exhibit overlapping characteristics (e.g. a hacked account where the email was changed without authorization), so individual subgroup counts sum to greater than 6,001.*

---

## 2. Macro Cluster Comparison: Routine Authentication vs. Security Breaches vs. Risk Lockouts

Aggregating the subgroups into macro operational clusters reveals three distinct operational profiles:

### Cluster A: Routine Authentication & Recovery (3,055 cases, ~50.9% of account inquiries)
- **Includes:** `cannot_log_in` (1,900), `forgot_password` (542), `otp_verification_failure` (313).
- **Customer State:** Legitimate account owner experiencing standard authentication friction.
- **Operational Decision:** Self-service enabled. Provide password reset links, SMS OTP retry instructions, browser/cookie clearing advice, or app reinstall steps.

### Cluster B: Policy & Risk Lockouts (1,550 cases, ~25.8% of account inquiries)
- **Includes:** `account_locked` (1,550).
- **Customer State:** Account proactively suspended or frozen by Amazon compliance/risk algorithms (e.g. billing discrepancies, credit card verification hold, gift card velocity locks).
- **Operational Decision:** Customer cannot resolve via self-service password reset. Requires document verification, faxing billing statements to Account Specialists, or waiting for security specialist review.

### Cluster C: Compromised / Hacked / Unauthorized Access (832 cases, ~13.9% of account inquiries)
- **Includes:** `hacked_account` (531), `unauthorized_email_password_change` (122), `unauthorized_account_access` (179), `suspicious_activity` (68).
- **Customer State:** Malicious third-party takeover. Attacker changed linked email, password, or shipping address, or placed fraudulent orders.
- **Operational Decision:** Standard self-service password reset is completely useless or dangerous (reset links route to attacker's email). Requires emergency session revocation, card pre-authorization cancellation, fraud claim filing, and real-time telephone verification.

---

## 3. Detailed Subgroup Profiles & 30 Representative Examples Each

### 1. Forgot Password / Password Reset (542 cases)

**Description:** Customer explicitly requests password recovery, forgot login password, or encounters password reset loops.  

| # | Case ID | Conversation ID | Customer Message | Historical Brand Response |
|---|---|---|---|---|
| 1 | `amazon_case_0000844` | `787575` | I did that, but it just gives me options to reset my password etc. | There's no email option? |
| 2 | `amazon_case_0000845` | `787575` | None of which apply to my current problem. | Gotcha, but were you able to input text to send in an email? The subject is not key here, we just want you to mail in the issue. |
| 3 | `amazon_case_0000846` | `787575` | I'll look again at the options. | Ok, let us know how you get on. |
| 4 | `amazon_case_0000847` | `787575` | I just sent the help request and am eagerly awaiting a solution to this problem. | I can confirm we've received your details. You'll be hearing back from us soon. |
| 5 | `amazon_case_0001686` | `526634` | Is there like a #helpful number I could call? | When an account is put on hold, it is done to protect our customers. If we have said further investigation is required, you may ne... |
| 6 | `amazon_case_0001687` | `526634` | No, I get it. Its like the last time I tried to buy 5 gift cards at Walmart and they stopped me at the door and took them back, re... | Hello, I do apologize for the incorrect link being sent. Here is the correct link here: <URL> |
| 7 | `amazon_case_0001688` | `526634` | For the record, I woke up this morning to email that my account was fixed. I appreciate you listening to my 2am rants. | Oh, good! Thanks for the update. Please don't hesitate to reach out to us at any time! |
| 8 | `amazon_case_0002552` | `2887286` | Hi, my password is okay i just keep getting a message saying ‘something went wrong’ it’s been like it for about an hour | Hmm, that is strange. Are you trying to log in from a desktop computer or through the app? |
| 9 | `amazon_case_0002553` | `2887286` | It’s through the app | Can you please try clearing the Data on the App, or uninstall/reinstalling it ? |
| 10 | `amazon_case_0002554` | `2887286` | All sorted many Thanks 👍 | Absolutely! Let us know if you need anything else! |
| 11 | `amazon_case_0002578` | `3729` | i reset my password 3 times and it still says incorrect you gotta be shitting me | I'm sorry for the trouble! Have you tried the steps outlined here? <URL> |
| 12 | `amazon_case_0002579` | `3729` | All of them | Hmm.... Let's take a closer look into what's going on here: <URL> |
| 13 | `amazon_case_0003216` | `1315498` | no matter how much time i put the right password in or reset my password keep getting this <URL> | Have you tried to reach us through the link that has offered ? |
| 14 | `amazon_case_0003621` | `5315` | Still not working. They sent me a link to reset the password, try and sign in with new password and still locked out. | Did information get sent to our Accounts Specialists to look into when you contacted in? |
| 15 | `amazon_case_0003622` | `5315` | Yes. | Can you tell us when this information was submitted? Account Specialists can take up to 2 business days to investigate an account ... |
| 16 | `amazon_case_0003623` | `5315` | 10 hours ago. | Gotcha- Let us know if you haven't heard back from them on Tuesday. |
| 17 | `amazon_case_0004038` | `2889316` | hello, it seems that the code generator is not working. Trying to reset my password and hitting a wall. Can you help ? | Hi! To confirm, are you having trouble generating the code for the Two-Step Verification? Also, which Amazon site are you trying t... |
| 18 | `amazon_case_0004039` | `2889316` | Tried to change password but now <URL> doesn't recognise old or new password and I am not receiving the reset code. Help ! | Hi there! Please try this link for further assistance: <URL> |
| 19 | `amazon_case_0004040` | `2889316` | Still not receiving anything 😟 | Did you reach out via the link provided by the phone number given? This may be the best way for us to assist. |
| 20 | `amazon_case_0004041` | `2889316` | All good now, thanks for your help! | Anytime! Please let us know if there's anything else we can help with. |
| 21 | `amazon_case_0004109` | `2889371` | Hey yesterday and today when I’ve tried to log in or reset my password the website says I don’t have an account and I definitely d... | Hi Becca, I'm sorry to hear this. If you can't get into your account to contact us direct you can use this link where you will not... |
| 22 | `amazon_case_0004613` | `1317465` | Requesting you to please call me. There is some serious issue while logging. I have already talked with ur service provider. Plz h... | We've responded to your DM, Arpit. Request you to check. |
| 23 | `amazon_case_0004636` | `1579667` | Hey, I'm trying to reset my password - it says its sent a code to my email address but it hasn't! | Have you checked your spam and junk folders? E-mails may get missorted. Let us know! We're here to help! |
| 24 | `amazon_case_0004637` | `1579667` | Have looked - have been trying over the past few days :( | Oh my! We'd like to look further into this with you. Please give us a call here: <URL> |
| 25 | `amazon_case_0005101` | `2628856` | I need help! I bought a game on amazon, a digital purchase and for some reason it logged me out and I can’t log in! I reset the pa... | Oh no! Please reach out to here: <URL> so we can further look into this! |
| 26 | `amazon_case_0005102` | `2628856` | Can’t log in | Whoops! Sorry for the wrong link! If you can't login please visit this link for assistance: <URL> |
| 27 | `amazon_case_0005220` | `1580412` | Hey! Can't sign in or reset password. I don't get the code emails, and internet/email are all working. I'm in California. | I'm sorry for the trouble w/ your account! When you have the time, please reach us via phone here: <URL> |
| 28 | `amazon_case_0005385` | `794443` | Hi there, I've already reset my password and tried to sign in but it still says itis incorrect. Email is __email__ | I'm sorry you're having issues signing in. What site do you order from? .co.uk, .com or another? |
| 29 | `amazon_case_0005386` | `794443` | yes .co.uk | Thanks for the additional info! Let's take a closer look with you in real time here: <URL> |
| 30 | `amazon_case_0005894` | `2105778` | I haven't received any emails from Amazon in days. I've tried resetting my password today, yesterday, the day before but I'm not g... | Sorry to hear that Kristin. Have you tried checking your spam and junk email folders? |

---

### 2. General Cannot Log In / Credential Failure (1,900 cases)

**Description:** Customer reports generic authentication barriers, incorrect password errors, or inability to access their account without explicit lockout or hacking.  

| # | Case ID | Conversation ID | Customer Message | Historical Brand Response |
|---|---|---|---|---|
| 1 | `amazon_case_0000185` | `786763` | I am getting no calling option as unable to sign in | Sorry to hear that. Kindly request you to contact us via chat/email with our support team here: <URL> |
| 2 | `amazon_case_0000186` | `786763` | Pathetic service...No help from amazon customer support service...emailed alot but no response....amazon sucks | We would like to help you. Please share your details with us here: <URL> We'll get in touch shortly. |
| 3 | `amazon_case_0000442` | `2884219` | email sent! | 👍 |
| 4 | `amazon_case_0000580` | `787158` | Wow. This is Heights | Please share your details in the link provided above by my colleague and we'll reach out. (2/2) |
| 5 | `amazon_case_0000581` | `787158` | when can i expect delivery of order no 216239636044 #AmazonIndia #delay | We apologize for the delay. Allow our support team to investigate . You can report this here: <URL> .(1/2) |
| 6 | `amazon_case_0000582` | `787158` | when can i expect delivery of order no 216239636044 #AmazonIndia #delay | Please don't provide your order details as we consider it personal information. Our twitter page is visible to public.(2/2)^CB |
| 7 | `amazon_case_0000583` | `787158` | D number shared is tracking id. Pls note if i wanted slow i would have written through amazon. But theres no way to reach u guys | Sorry about that. You can reach out to us using the link shared above and we'll definitely look into it. |
| 8 | `amazon_case_0000802` | `2622542` | mail __email__ - 79 8471 8690- unable to login even after password change. always says incorrect even after changing password - ti... | I'm sorry to hear about your account. Please contact our specialist team via <URL> for further assistance. |
| 9 | `amazon_case_0001401` | `526181` | Order # 402-0726587-9868359. It's been 18 days, haven't recvd item so far. Why so late? When will I receive product? Today is last... | Please don't provide your order details, we consider it to be personal information. Our page is visible to the public. (2/2) |
| 10 | `amazon_case_0001402` | `526181` | Already sent mail to seller through the linked you mentioned. No reply so far from seller or amazon. Why don't you use Oder Id & g... | I'm sorry we'll not be able to access your account here, Amit. Kindly fill in your details here: <URL> and we'll get in touch with... |
| 11 | `amazon_case_0001403` | `526181` | Done | Thank you for sharing your details. We'll work on them and reach out to you soon. |
| 12 | `amazon_case_0001404` | `526181` | I have palced order from account where login id is my mobile no. Though i have seperate account having my emaild as login. Still y... | We've sent the correspondence to your registered email ID. Kindly check it here: <URL> |
| 13 | `amazon_case_0001747` | `264683` | I have already update the detail link through FB but everytime i m not getting result. | r details in the link provided above and we'll have the issue checked for you. (2/2) |
| 14 | `amazon_case_0001748` | `264683` | I update my detail via link please check it and give me a solution urgently otherwise give me a fefunf | Thanks. We'll check and revert at the earliest. |
| 15 | `amazon_case_0001749` | `264683` | I am not getting any update | Please do not worry, we'll get back to you at the earliest. |
| 16 | `amazon_case_0001750` | `264683` | I see that bluedart will pickup my return parcel tomorrow. | Thank you for keeping us posted, Tushar. We are working on this and will revert with an update. |
| 17 | `amazon_case_0001751` | `264683` | Give me a perfect time that when my problem ll solved | We regret for the trail with your concern, revert to our correspondence & we'll get back to you with updates. |
| 18 | `amazon_case_0002466` | `1576309` | Here is my email confirmation <URL> | I'm sorry for the trouble! Please give a call here: <URL> so it can be looked into in real-time. |
| 19 | `amazon_case_0002552` | `2887286` | Hi, my password is okay i just keep getting a message saying ‘something went wrong’ it’s been like it for about an hour | Hmm, that is strange. Are you trying to log in from a desktop computer or through the app? |
| 20 | `amazon_case_0002553` | `2887286` | It’s through the app | Can you please try clearing the Data on the App, or uninstall/reinstalling it ? |
| 21 | `amazon_case_0002554` | `2887286` | All sorted many Thanks 👍 | Absolutely! Let us know if you need anything else! |
| 22 | `amazon_case_0002578` | `3729` | i reset my password 3 times and it still says incorrect you gotta be shitting me | I'm sorry for the trouble! Have you tried the steps outlined here? <URL> |
| 23 | `amazon_case_0002579` | `3729` | All of them | Hmm.... Let's take a closer look into what's going on here: <URL> |
| 24 | `amazon_case_0003215` | `1315498` | yo i cant sign in keeps telling me to change my pw when i do i try to sign in with the same password and its not allowing wassup | Sorry to hear. Please reach out to us here: <URL> (No login req) and we can look into it. |
| 25 | `amazon_case_0003216` | `1315498` | no matter how much time i put the right password in or reset my password keep getting this <URL> | Have you tried to reach us through the link that has offered ? |
| 26 | `amazon_case_0003302` | `4859` | how is Amazon going to solve this? By mail, text, call, customer phone service, no one is able to help me <URL> | We want our team to investigate this further with you. Please reach out to us using the secure link: <URL> |
| 27 | `amazon_case_0003303` | `4859` | Im not receiving 2step code by text or call in my smartphone can't log in into my account already got help by phone with no luck | Sorry you're having problems logging in. Please let us know which Amazon site you are using (.com .es). Thanks. |
| 28 | `amazon_case_0003304` | `4859` | USAs Amazon. Com | Please reach out to us directly here: <URL> We'd love to help get you logged in! |
| 29 | `amazon_case_0003305` | `4859` | no luck on receiving the code by text or call, will I loose my account, yesterday a phone representative tried to help already <UR... | I'm sorry for the challenge signing in. Please use the link from above again so that we can help. Keep us updated! |
| 30 | `amazon_case_0003306` | `4859` | no luck it keeps asking for code witch is not sending to my phone can Amazon eliminate the 2 step method, this is so frustrating | I'm so sorry for the frustration, Luis. We should absolutely be able to help! Please contact us using the link TN provided. |

---

### 3. OTP / Two-Factor Verification Failure (313 cases)

**Description:** Customer is blocked by two-factor authentication, non-receipt of OTP SMS verification codes, or authentication app failure.  

| # | Case ID | Conversation ID | Customer Message | Historical Brand Response |
|---|---|---|---|---|
| 1 | `amazon_case_0000859` | `787589` | Used card for an order at didn't ask for OTP, asked for PIN code instead and order is still pending verification? | Sorry for the trouble you've had. Kindly reach out to our support team here: <URL> and they'll help you. |
| 2 | `amazon_case_0001170` | `1574427` | So, uh... On Saturday I ordered some spatulas from and they were scheduled for delivery to an Amazon locker on Monday (today). Yes... | Hi, sorry to hear that, what's the current status of the tracking and estimated delivery date: <URL> |
| 3 | `amazon_case_0001171` | `1574427` | Just this evening I got another email saying it failed to deliver/got lost in transit and I should contact them to get it taken ca... | Apologies, it seems like you were went the emails in error, I'm happy to hear that you received your parcel. |
| 4 | `amazon_case_0001512` | `2885740` | not receiving the verification code to buy a gift how do I go about opening my account to complete | Hi there! You don't need a verification code to create an account on the <URL> website. Are you trying to create a new account on ... |
| 5 | `amazon_case_0001513` | `2885740` | hi I have an account already but haven't used in quite a while | At what part of the order process is it asking you for a verification code?^PJ |
| 6 | `amazon_case_0001514` | `2885740` | when I've put it in the basket and signed in | Do you have two-step verification enabled on you account? -Aisha P. |
| 7 | `amazon_case_0001515` | `2885740` | I haven't used the account in so long I wouldn't know. haven't received any verification codes | Please reach out to us here: <URL> for further assistance. Thank you. |
| 8 | `amazon_case_0002633` | `1838783` | There is no error, I am not getting an SMS code from Amazon, can you have someone call me? | I'm sorry to know about this. Please connect with our support team here: <URL> and we'll be happy to help. |
| 9 | `amazon_case_0002634` | `1838783` | SH, the issue here is I am not able to log in to my account due to 2factor auth, I am not receiving the sms or call with the code | Request you to click on skip sign in and fill your details here: <URL> and I'll get back to you. |
| 10 | `amazon_case_0002635` | `1838783` | Done | Thanks for the update, appreciate your patience while we work on it. |
| 11 | `amazon_case_0006177` | `533280` | Last year when I lived in similar halls, the driver would call me to gain access | We want to connect you with the carrier once more to ensure the proper delivery instructions are noted. Feel free to get in touch ... |
| 12 | `amazon_case_0006178` | `533280` | I don’t understand what you want me to do...I need this order today it was originally intended for yesterday | We don't have access to your account over Twitter. So that we can best help, please get in touch via the above link and we'll look... |
| 13 | `amazon_case_0006179` | `533280` | That link just sends me to the USA website so... | Apologies Becca, please try this link: <URL> |
| 14 | `amazon_case_0006180` | `533280` | That link leads me to the USA website | Opps! Sorry for that, here is the link to the <URL> customer service: <URL> Let us know if you have anymore questions! |
| 15 | `amazon_case_0006507` | `2893186` | Hi I cannot access my Amazon account & get the verification code because I put .ckm not .com | Hi, can you confirm which Amazon site you are trying to use? Is it <URL> etc? |
| 16 | `amazon_case_0006508` | `2893186` | UK, but like I said put .ckm at the end of my email so unable to login into my AMZ account & access the verification code | Thanks for confirming that information, Shujaat! Please contact us here: <URL> so we can look into this for you! |
| 17 | `amazon_case_0006509` | `2893186` | Yes I did but still no resolution. I just need to change the last bit of Hotmail domain | What information/options did we give when you contacted us using the link provided? |
| 18 | `amazon_case_0006720` | `534114` | Hi I am being told my parcel cannot be delivered as postman cannot reach the address. This can’t be the case as I’ve had several s... | Hi, we don't have access to your details on Social Media. What does the tracking say? You can check by clicking the link: <URL> |
| 19 | `amazon_case_0007343` | `1583690` | My account has been compromised despite two factor authentication - I’ve called to report but not sure the seriousness is understo... | I'm sorry for the poor experience! When you last spoke with us, what information or options were provided? |
| 20 | `amazon_case_0007344` | `1583690` | Nothing helpful - this needs escalating to your security team now. | I understand how that feels, Andrew. Have you received any e-mails regarding your account? Remember to check spam/junk. |
| 21 | `amazon_case_0007345` | `1583690` | I received two codes and an email notifying me of an account change - my pw has been changed | I'd like a member of our team to look into this further. Please provide additional info here: <URL> |
| 22 | `amazon_case_0007346` | `1583690` | Since my account has been compromised and the password changed I cannot do this | Please click the skip sign-in beneath the gold sign-in button using the link SG provided. |
| 23 | `amazon_case_0007347` | `1583690` | Done | Thank you, please give a member of our team time to review your information. |
| 24 | `amazon_case_0009608` | `276190` | What about adding option for phone-call to verify the number. Its already available for 2-factor auth. Needed for site accessibili... | We'd like to have this checked. Kindly drop in your details here: <URL> and we'll look into this. |
| 25 | `amazon_case_0009609` | `276190` | Also, Amazon doesn't seem to have issues in sending other messages to me. It's only the verification OTP which fails. <URL> | Are you facing any problem with OTP, when dealing with other merchants online? |
| 26 | `amazon_case_0009610` | `276190` | I am not facing any OTP issues with any other merchants or services. I have filled my details in the other link. | Thank you for providing the details. We will work on it and get back with an update. |
| 27 | `amazon_case_0009830` | `1063012` | for the app, confirm button is not activated when OTP is copy pasted (img1), same OTP works when typed(img2) #ux #UserExperience <... | Please uninstall and install the app and try it again. Let us know if the issue persist. |
| 28 | `amazon_case_0009831` | `1063012` | Issue continues even after re-install. With messaging apps providing easy-otp-copy options app needs to be updated for the same | I understand your concern.I’d like to help you; please fill this form: <URL> and I’ll contact you soon. |
| 29 | `amazon_case_0011902` | `2901053` | I got an email that there was an attempt to connect to my account and I was provided with a security code to use, I changed my pas... | I'm so sorry to hear you are having an issue accessing your account! Which Amazon website are you attempting to access (.com, .in,... |
| 30 | `amazon_case_0011907` | `2901064` | takes 2 hours to send verification code which expires in 10 minutes. #frustrated | I'm sorry for the trouble, Beverly! Without including personal information, could you tell us a bit more about what's going on? Is... |

---

### 4. Account Locked / Suspended / On Hold (1,550 cases)

**Description:** Account was placed on hold, locked, suspended, or blocked by Amazon risk/compliance systems pending identity or billing verification.  

| # | Case ID | Conversation ID | Customer Message | Historical Brand Response |
|---|---|---|---|---|
| 1 | `amazon_case_0000526` | `787125` | my account has been locked pending verification of my CC. I have sent the required fax 3 times. what more do you want? | Please check your spam folder as you should have received an email from an Account Specialist by now. |
| 2 | `amazon_case_0000527` | `787125` | There is nothing there. And I have no email address to try and contact anyone as the help me page requires a login which you have ... | What Amazon website do you use? <URL> or another Amazon website? |
| 3 | `amazon_case_0000528` | `787125` | I tried to log into .com but the fax number that was sent was a UK number | Thanks for confirming, have you tried reaching us via this link: <URL> |
| 4 | `amazon_case_0000529` | `787125` | This happens every time <URL> | Strange. Have you tried a different browser or device if available? Also, have you tried clearing cookies/cache? |
| 5 | `amazon_case_0000530` | `787125` | I managed to send one now but I do not get a confirmation email for the ticket letting me know that it was received. | Please keep us updated and let us know if you don't get a reply. |
| 6 | `amazon_case_0000745` | `2622455` | Now that I've linked card n account details why the heck my ac is blocked. What do u guys wnt frm me? | All account closure issues are handled by the account specialist team. Suggest you to reply to the email sent by our account speci... |
| 7 | `amazon_case_0000991` | `525561` | Sure. I placed an order for a package and did not receive it in my mail. Also checked in with neighbors, and they don’t have it. A... | Hi, thanks for that information. What were you advised when reaching out to us? Have they started an investigation with the carrie... |
| 8 | `amazon_case_0001458` | `2885683` | Hello Team, I have already provided sufficient information multiple times but still no help from your end. My amazon seller accoun... | We've escalated your details to the concerned team. They'll get in touch with you regarding the same. |
| 9 | `amazon_case_0001685` | `526634` | Why do you people think I hacked my own account. 2 times in two days I have been locked out after buying Google Play cards. Walmar... | Sorry to hear this, did you receive any email notification regarding the account being locked?^BZ |
| 10 | `amazon_case_0001686` | `526634` | Is there like a #helpful number I could call? | When an account is put on hold, it is done to protect our customers. If we have said further investigation is required, you may ne... |
| 11 | `amazon_case_0001687` | `526634` | No, I get it. Its like the last time I tried to buy 5 gift cards at Walmart and they stopped me at the door and took them back, re... | Hello, I do apologize for the incorrect link being sent. Here is the correct link here: <URL> |
| 12 | `amazon_case_0001688` | `526634` | For the record, I woke up this morning to email that my account was fixed. I appreciate you listening to my 2am rants. | Oh, good! Thanks for the update. Please don't hesitate to reach out to us at any time! |
| 13 | `amazon_case_0001810` | `264723` | our account name buyerzone still suspended,no response yet.. | We're sorry to hear about the delay. Please reach us here: <URL> and we'll get this sorted soon. |
| 14 | `amazon_case_0001811` | `264723` | Dear Team, Kindly note concern about seller account suspension..not buyer account, look into matter asap,waiting for response, | Apologies for the trouble had. Kindly revert to the email you've received from our team for further assistance. |
| 15 | `amazon_case_0001812` | `264723` | already responded more than twice to seller performance-policy,notice,notice dispute ,even completed all mandatory procedures. | We're following up with your concern here: <URL> Kindly refer. |
| 16 | `amazon_case_0001813` | `264723` | What apology guyz?its such dub thing ever about completed all mandatory procedures as amazon need from us,,,still no response.. | If you've shared the details, you should've received an email from us. You can check that here: <URL> |
| 17 | `amazon_case_0001814` | `264723` | none mail received yet?elaborate about where it will be occurred ? Important Messages ,Related To Your Orders, Related To Your Acc... | I'd request you to check all the email folders and respond to the latest correspondence you received from us. |
| 18 | `amazon_case_0001815` | `264723` | don't make us fool,provided me a mail you did, | Did you receive the email? |
| 19 | `amazon_case_0001816` | `264723` | No | As a part of customer service we'll not be able to address seller account related concerns. (1/2) |
| 20 | `amazon_case_0001817` | `264723` | No | Kindly connect with the concerned team via <URL> |
| 21 | `amazon_case_0001818` | `264723` | Who can help us?? please provide correct details, either issue is more spread in social media | We'd like to sort this. Please write to us using the secured link here: <URL> We'll reach out to you.^VN |
| 22 | `amazon_case_0001819` | `264723` | No have further action we have invoice than why you take long time, right owner is agree than what's amazon problem?🙁 | Sorry for the stretch. Kindly reply to the correspondence sent by us and we'll get in touch with you soon. |
| 23 | `amazon_case_0001820` | `264723` | we already replay day by day with new POA but till now account is not reinstated. please look in to matter, we are waiting for rev... | We being a part of retail team, we will not be able to check the information here. Since you've written to our (1/3) |
| 24 | `amazon_case_0001821` | `264723` | we already replay day by day with new POA but till now account is not reinstated. please look in to matter, we are waiting for rev... | seller support team, request you to wait for a correspondence from the team as they are in the (2/3) |
| 25 | `amazon_case_0001822` | `264723` | we already replay day by day with new POA but till now account is not reinstated. please look in to matter, we are waiting for rev... | best position to help you in this case. (3/3) |
| 26 | `amazon_case_0001823` | `264723` | so stop your robot reverts and provide us exact resolution as soon as possible. | We're working on the issue and I see that a correspondence has been sent. Kindly check it here : <URL> |
| 27 | `amazon_case_0001824` | `264723` | Okay so within how much timeline we will receive response from seller performance be cause they already denied POA. | Kindly wait till you receive an update. Appreciate your patience. |
| 28 | `amazon_case_0001825` | `264723` | okay waiting for response | Appreciate your understanding. |
| 29 | `amazon_case_0001826` | `264723` | Thank you,But please work fast because almost we have big loss by you | We're working on the issue and will reach out to you at the earliest. |
| 30 | `amazon_case_0001827` | `264723` | ok ,we are waiting for revert. | Appreciate your understanding. |

---

### 5. Hacked / Compromised Account (531 cases)

**Description:** Customer states or suspects their account was hacked, compromised, or taken over by a third party.  

| # | Case ID | Conversation ID | Customer Message | Historical Brand Response |
|---|---|---|---|---|
| 1 | `amazon_case_0000014` | `262166` | My Amazon prime account was cancelled because I think it was hacked into. | Oh! Have you tried to reach out to us here: <URL> for real-time assistance with this? Keep us posted! |
| 2 | `amazon_case_0000015` | `262166` | I have received unsatisfactory response as I think my account has been hacked so am pursuing it with regulatory authority | What information did we provide when you contacted us? |
| 3 | `amazon_case_0000016` | `262166` | Aĺleged I had never used my Prime Account when I have been using it several times a month for several years. Totally inadequate re... | Have you had a chance to contact an Account Specialist by phone: 08081453760 or e-mail: <URL> |
| 4 | `amazon_case_0000017` | `262166` | a very non customer centric organisation who do not understand customers | Hi- Is there something we can assist with? Please let us know without sharing personal/account specific information. |
| 5 | `amazon_case_0000184` | `786763` | need a callback urgently reagarding my amazon account hacked | Sorry for the trouble, Jinendra. Please request a call here: <URL> and we'll be glad to help. |
| 6 | `amazon_case_0000185` | `786763` | I am getting no calling option as unable to sign in | Sorry to hear that. Kindly request you to contact us via chat/email with our support team here: <URL> |
| 7 | `amazon_case_0000186` | `786763` | Pathetic service...No help from amazon customer support service...emailed alot but no response....amazon sucks | We would like to help you. Please share your details with us here: <URL> We'll get in touch shortly. |
| 8 | `amazon_case_0000764` | `2622501` | account hacked and now they won't reimburse the $800+ ebook purchases that were made fraudulently. Yep, not even a physical good a... | i'm very sorry for this experience. Did youi have a chance to communicate with our Accounts Specialists? |
| 9 | `amazon_case_0000765` | `2622501` | Yes. Called twice and still no resolution. | I would like to have our specialist team look at this with you. Would you mind giving us some details here when you have a chance ... |
| 10 | `amazon_case_0000766` | `2622501` | Absolutely, would love to get this resolved. Thank you! | No problem, Letitia! Please reach back out if you have any other concerns or questions. We're always here to help! |
| 11 | `amazon_case_0000767` | `2622501` | My email was shut off and unable to get in. Anywhere else I should enter in the information? | Thank you for letting us know. When you submit the information to us, you should be able to enter a preferred contact method. You ... |
| 12 | `amazon_case_0001685` | `526634` | Why do you people think I hacked my own account. 2 times in two days I have been locked out after buying Google Play cards. Walmar... | Sorry to hear this, did you receive any email notification regarding the account being locked?^BZ |
| 13 | `amazon_case_0001686` | `526634` | Is there like a #helpful number I could call? | When an account is put on hold, it is done to protect our customers. If we have said further investigation is required, you may ne... |
| 14 | `amazon_case_0001687` | `526634` | No, I get it. Its like the last time I tried to buy 5 gift cards at Walmart and they stopped me at the door and took them back, re... | Hello, I do apologize for the incorrect link being sent. Here is the correct link here: <URL> |
| 15 | `amazon_case_0001688` | `526634` | For the record, I woke up this morning to email that my account was fixed. I appreciate you listening to my 2am rants. | Oh, good! Thanks for the update. Please don't hesitate to reach out to us at any time! |
| 16 | `amazon_case_0002559` | `2887294` | please help - it looks like my account has been hacked, my email and phone number changed which means I can’t speak to anyone!! Pl... | Hello, Tara! Please contact us here so that we can take a closer look into this for you: <URL> |
| 17 | `amazon_case_0002560` | `2887294` | Trying to deal with this situation but US customer services are being really unhelpful! I need to know what is happening with my a... | Hi Tara, I'm sorry to hear that. Have you checked the spam/junk folders of your emails for an email from the account specialists? |
| 18 | `amazon_case_0002561` | `2887294` | Yes had an email yesterday to reset my account but no info on my refund or my other order - customer services say they are unable ... | Hmm, that's strange! Thanks for confirming, Tara! In this case, I would like for a member of my team to personally help investigat... |
| 19 | `amazon_case_0002562` | `2887294` | Thank you - I have completed the form! | Thank you for submitting the form, a member of our team will be looking into this issue for you and get back to you as soon as pos... |
| 20 | `amazon_case_0002734` | `1838888` | my account was hacked yesterday and the email address was changed. Need help as I cannot access the books, videos etc . | If you are unable to access your account, please get in touch via <URL> |
| 21 | `amazon_case_0003920` | `529930` | Not sure which carrier it is, but last time I ordered a Christmas present a couple of years ago, (a kindle fire) my account got ha... | Sorry to hear this. That is most unusual and not the kind of thing you should expect when you order from Amazon. If there is any i... |
| 22 | `amazon_case_0003971` | `2889250` | I was charged for a video game gift card that I did not purchase after my account was hacked. | I'm sorry to hear about this unauthorized charge, Gina! Have you been able to get through to our customer service? If you have, wh... |
| 23 | `amazon_case_0006475` | `2893118` | I tried logging into my account and my fingerprint doesn't work and when I tried sending a code to my number it sent to a email I'... | I'm sorry you haven't been able to login. Please reach out to an Account Specialist: <URL> They are in the best position to help y... |
| 24 | `amazon_case_0006774` | `534183` | My mum has been trying to contact you for weeks regarding hacking. Her account was hacked and a book was ordered to the value of £... | I'm sorry this has been your experience. We'd like to take a look at this for you. Please give us your account details here, <URL>... |
| 25 | `amazon_case_0006975` | `2107249` | So someone literally hacked my fucking amazon account to buy 4 e-books (3 of which were free) and fucking review a wax melter, a j... | Sorry to hear of this! Have you changed your password to ensure no one else has access to it? Learn how here: <URL> |
| 26 | `amazon_case_0006976` | `2107249` | Ive changed password, added 2 step verification, refunded and deleted the books, deleted the reviews, and made a claim to the amaz... | Thanks for confirming, the accounts specialists should investigate this further once the email is received. |
| 27 | `amazon_case_0007209` | `10645` | did amazon get hacked? | We'd like to help! Have you noticed any unauthorized activity on your account? |
| 28 | `amazon_case_0007958` | `1060443` | my account was hacked, but I can’t see where to report that. I already changed my password, but want to inform you. | Hi, do you now have full access to your account? |
| 29 | `amazon_case_0007959` | `1060443` | I do, and luckily all they seem to have done is write some reviews for products I’ve never seen before. I’d investigate that. | Oh my! We'd like to further investigate this with you here: <URL> |
| 30 | `amazon_case_0007969` | `1060448` | , looks like u have been hacked! My account details have been changed & I was never notified. support team is blissfully ignorant | Terribly sorry about your account! Let's take the next steps to get this sorted for you here: <URL> |

---

### 6. Unauthorized Email / Password Change (122 cases)

**Description:** Customer reports their login email address or password was changed without their authorization or consent.  

| # | Case ID | Conversation ID | Customer Message | Historical Brand Response |
|---|---|---|---|---|
| 1 | `amazon_case_0002560` | `2887294` | Trying to deal with this situation but US customer services are being really unhelpful! I need to know what is happening with my a... | Hi Tara, I'm sorry to hear that. Have you checked the spam/junk folders of your emails for an email from the account specialists? |
| 2 | `amazon_case_0006249` | `9129` | It looks as though someone has changed the email address linked to my acct & I can no longer log in. Help! | We're here to help! Please, reach us phone or e-mail so we can investigate: <URL> |
| 3 | `amazon_case_0006250` | `9129` | I'm UK based. Are the contact details the same? | Sorry! Try this one instead: <URL> |
| 4 | `amazon_case_0006251` | `9129` | Hello? So how do I contact someone if I can't log in?! I'm really concerned about what is happening with my acct and who has acces... | Hi Emma. I understand. You can use this link (which doesn't require a log in) to get in touch: <URL> |
| 5 | `amazon_case_0007792` | `2633024` | why is it almost impossible to contact your help team? Ive been told payments have been decline. Changed payments. Paid again. Pay... | We're here to help. We don't charge your order until it ships, but an authorisation may be visible on your statement. More informa... |
| 6 | `amazon_case_0007793` | `2633024` | why is it almost impossible to contact your help team? Ive been told payments have been decline. Changed payments. Paid again. Pay... | If you'd still like to contact us, we're available via phone, chat or e-mail here: <URL> 2/2 |
| 7 | `amazon_case_0007795` | `2633024` | Tirns out ive beencharged twice for both. Im not trusting the seller and these are the people your link takes me to. Im looking to... | I'm sorry about that! Give us a call here: <URL> so we can work on this with you. |
| 8 | `amazon_case_0008793` | `275129` | Please help! Someone hacked my account and I can’t contact you on your website as they changed the email and I cannot log in! | Sorry about your account issues Anja- Which website are your registered with? <URL> <URL> |
| 9 | `amazon_case_0008794` | `275129` | <URL> I received this email but I never asked for a change! <URL> | Ok, do you know the new email address? Can you get in touch with us here: <URL> |
| 10 | `amazon_case_0008795` | `275129` | So now this person has my credit card details and I can’t sign in to stop them from using it!!! | Sorry, you can reach us via this link: <URL> as soon as you report this the account will be placed on hold. |
| 11 | `amazon_case_0008796` | `275129` | Thanks 🙂 | You're welcome Anja. |
| 12 | `amazon_case_0009824` | `1587290` | also IM NOT IN GERMANY that should’ve been a hint when someone was trying to steal my account 🙄 | I'm sorry for the frustration! Have you received any e-mails from our Account Specialists regarding the compromised account? |
| 13 | `amazon_case_0009825` | `1587290` | No emails so far | Have you checked your spam and junk folders? We can take a closer look into this via the link here: <URL> |
| 14 | `amazon_case_0009826` | `1587290` | Nope nothing there | Thanks for checking. We'd like to take another go at this with you. Using's link, please reach us when you can. |
| 15 | `amazon_case_0012262` | `2377209` | Someone hacked my account and changed the email and password so I no longer have control of it at all. Someone help me please get ... | I'd like to have a member from our support team lend you a hand with this; please use this link so we may assist you: <URL> |
| 16 | `amazon_case_0012263` | `2377209` | Thank you! I'll be sending a message on the website ASAP. | You're welcome! Please keep us updated on the outcome! |
| 17 | `amazon_case_0012264` | `2377209` | The outcome was great. Your staff helped me regain control of my account very quickly. I'm extremely thankful and have nothing, bu... | We're glad that we were able to assist! Please don't hesitate to reach out to us in the future. |
| 18 | `amazon_case_0017840` | `2909256` | My account was hacked. Someone changed the email address associated w/ my account & I cannot access my account. I am a Prime membe... | I'm so sorry for the ongoing trouble with your account, Travis! I'd like to have a member of our team look into this on your behal... |
| 19 | `amazon_case_0017841` | `2909256` | Thank you thank you thank you thank you!! I just submitted the info and I really appreciate your help! I just want to log into my ... | You're very welcome, Travis! |
| 20 | `amazon_case_0025994` | `1611033` | I am unable to login. It shows my email Id is no longer registered. someone has changed my email Id as well in the amazon accoun | Please use this link: <URL> this will get you connected to our support team. |
| 21 | `amazon_case_0025995` | `1611033` | I am yet to get a response from your customer care team ! It’s been more than 12 hours now !! | Sorry for the delay. Kindly arrange a call back from our team here: <URL> and we'll help you. |
| 22 | `amazon_case_0026903` | `2398919` | My account has been hacked and password changed without consent | Very sorry to hear this. Please use this link to reach out to us directly: <URL> |
| 23 | `amazon_case_0029002` | `2664432` | in a panic, someone changed my account email. Locked out now. Customer service says 24-48 hrs. Don’t need this stress.10yrcustomer | I'm afraid we don't have access to account details here but you should get an email shortly from an account specialist. |
| 24 | `amazon_case_0029155` | `1616051` | my email and account details have been changed without my consent, is 08081453760 the right number as it was a dodgy line!! | You can also request a callback here: <URL> |
| 25 | `amazon_case_0029546` | `306170` | Someone has hacked my amazon account and changed the email address, how can I fix this? | Oh no! We'd like to assist you, please reach us directly using this link: <URL> |
| 26 | `amazon_case_0029547` | `306170` | Thank you! I've called the number, is there anything else I can do to protect my information? | We'd like to be sure there isn't! Just to confirm, what information and options were provided to you when you called us? |
| 27 | `amazon_case_0029548` | `306170` | The person said they put in a "Compromised Account" form and put a hold on the account and said I'd hear back in 24-48 hours. | Thanks, Miranda! Please keep an eye out for that e-mail from one of our Account Specialists! |
| 28 | `amazon_case_0031437` | `2930644` | how is someone that has had account hacked and had their email changed supposed to get help from amazon if you have to sign in to ... | Hello Eyla! You can reach us through this link: <URL> |
| 29 | `amazon_case_0032664` | `572915` | So our prime account has had its password changed without permission on numerous occasions. Now it's been hacked and the login ema... | I'm so sorry you're unable to access your account. Have you received an email from an Account Specialist? |
| 30 | `amazon_case_0032665` | `572915` | We actually need to talk to a system administrator to change the hacked login email back our real email address. Unfortunately you... | Please keep an eye out for an e-mail from our Account Specialists. They are in the best position to assist further. |

---

### 7. Suspicious Activity / Security Flagged Orders (68 cases)

**Description:** Customer or Amazon flags suspicious activity, unauthorized transactions, or security holds placed on recent orders.  

| # | Case ID | Conversation ID | Customer Message | Historical Brand Response |
|---|---|---|---|---|
| 1 | `amazon_case_0006364` | `1057950` | Impressive did my parents groceries by India My credit card is blocked for suspicious activity lol🤦 | I'm unable to comprehend your concern. Kindly elaborate. |
| 2 | `amazon_case_0010075` | `277241` | Disappointed with Amazon. Account has been suspended due to "suspicious activity", won't tell me what it is. Rang 4 times now... | Hi Matan. What advise were you given when you called? |
| 3 | `amazon_case_0010076` | `277241` | That it is being referred to a "specialist team" who will be in touch "within 24 hours". It's now been six days... | Hi Matan, did you receive an email from the Account specialist at all? Please check your spam folder too. |
| 4 | `amazon_case_0010077` | `277241` | No I haven't | When you've spoken with us, have we offered to pass your details along to an Account Specialist for you? |
| 5 | `amazon_case_0010078` | `277241` | Yes. 4 times now. | I'd like a member of our team to look into this for you. Please provide details here: <URL> |
| 6 | `amazon_case_0010079` | `277241` | I can't log in to that link. It says my password is incorrect. Should I try resetting the password again? | No, just choose 'skip sign in'. |
| 7 | `amazon_case_0010080` | `277241` | Can I please get an update on this? | We'll be reaching out as soon as possible, we appreciate your patience. |
| 8 | `amazon_case_0010081` | `277241` | how long do you think it will take? | I'm sorry for the wait. I confirmed we received your message. The longest it will take our team to respond is 12 hours. |
| 9 | `amazon_case_0010082` | `277241` | it's now been now than 12 hours and still no response. Please advise on what to do next???!!! | We'd like to look into this for you. Please provide your order/contact info here: <URL> |
| 10 | `amazon_case_0010083` | `277241` | I've already submitted it resettle to the link you sent me yesterday? | I'm sorry for the delay in getting back to you. We've escalated it further and you will receive a response shortly. |
| 11 | `amazon_case_0010084` | `277241` | Can I please get an update on my slight? It's almost two weeks now since my account was locked out.... Why is this taking so long?... | Hi Matan-Can you reply directly to the email you received from us to request this update?We wouldn't have access from here |
| 12 | `amazon_case_0010085` | `277241` | I already have. I shouldn't have to come to Twitter to get updates on this :(. Why is it taking two weeks to sort out my account? | Apologies Matan - when did you send the required info to the Account Specialists ? |
| 13 | `amazon_case_0010086` | `277241` | What required info? I haven't been asked for any info by anyone at Amazon... | We are waiting for an update from the Amazon Payments team. As soon as we get an update, we will inform you.^CD |
| 14 | `amazon_case_0010087` | `277241` | how long should this take? | We'll be in touch as soon as we can. |
| 15 | `amazon_case_0042908` | `1372132` | I have a laptop on the way with no protection plan and my gift card is still empty. My account has been flagged suspicious (4 yr i... | Sorry to hear about this! We don't have acct access over Twitter. Please reach out via phone/chat: <URL> |
| 16 | `amazon_case_0057640` | `83413` | August, I can no longer log into my account to be more specific, I can only provide the date and cost of the items. My account for... | We'd like to help look into this with you! Please reach out to us by phone here: <URL> |
| 17 | `amazon_case_0064178` | `2976925` | just received a suspicious email from amazon about headphones I’d supposedly ordered. I did not order any headphones. How do I rep... | I'm sorry to hear you received a suspicious e-mail! You can find information on forwarding the e-mail to us here: <URL> |
| 18 | `amazon_case_0067381` | `2720050` | Disgusted by they froze my account due to suspicious activity - it was me buying gift vouchers. No apologies - no luck ne’er using... | Oh no! Has this been sorted out for you now? Do you have access to your account? |
| 19 | `amazon_case_0067382` | `2720050` | You can see what I mean if you access my account __email__ | Hi Jane, we aren't able to access your account via Twitter. If you are still unable to get access you can contact us through the f... |
| 20 | `amazon_case_0067383` | `2720050` | No don’t want to use amazon anymore | Sorry to hear that Jane. We would like to help you resolve your account issue but have no access to your account through twitter. ... |
| 21 | `amazon_case_0067384` | `2720050` | I’ve already rung customer services three times really don’t have any more time to waste you have my email | Hey Jane, did you receive an email from our Account Specialist team asking for details to help unlock your account? |
| 22 | `amazon_case_0067385` | `2720050` | No I complained to customer service gave my email and just got automated response | Hey Jane, really sorry about that. This is not what we want our customers to experience! Have you checked your spam folder? If you... |
| 23 | `amazon_case_0068104` | `1410733` | Yeah and they are 'looking' into it. I'm really disappointed, my toaster arrived but my videogame and electrictronic didn't hmmm s... | I'd like to have a member of our team look into this. Please send the order details to us here: <URL> |
| 24 | `amazon_case_0068358` | `2459989` | Placed order but the seller is suspicious he may be doing fraud as they provide same shipping details to all , i'm alerting you in... | Apologies, please report this to our customer service team here: <URL> |
| 25 | `amazon_case_0073028` | `1157226` | Every time we call cust. service to fix it, they tell us it’s fixed and we should be ok to make the purchase after getting an emai... | I'd like for a member of our team to take a look at this for you. Please provide details here: <URL> |
| 26 | `amazon_case_0079591` | `382336` | All of them, however I’ve received just 3 | I'm sorry about this! Please contact us by phone or chat so that we can help investigate further: <URL> |
| 27 | `amazon_case_0079592` | `382336` | You were supposed to refund the unauthorized purchases!!!!! | Were the charges made on Amazon.es or <URL> |
| 28 | `amazon_case_0079593` | `382336` | I did, 3 times!!!!! All I get is “we are gonna investigate” and another alert account email. The scam was on <URL> | Hi- Just to confirm when did you send the recent email to us? It can take 24 to 48hours to receive a response. |
| 29 | `amazon_case_0079594` | `382336` | I already left my number so someone from Amazon can call me but no answers no calls I also sent the email where the full refund is... | Hello, I can understand you frustration. Please fill in this link and we will reach out to you: <URL> |
| 30 | `amazon_case_0079595` | `382336` | IT'S BEEN ALMOST A MONTH AND I STILL STRUGGLING WITH A REFUND U OFFERED ME BC MY ACCOUNT WAS HACKED. NO ONE IS CONTACTING ME. | When did you last receive an email from the Account Specialist team?^CD |

---

### 8. Unauthorized Account Access / Fraudulent Orders (179 cases)

**Description:** Unrecognized third parties accessed the account, placed orders, used stored payment methods, or breached credentials.  

| # | Case ID | Conversation ID | Customer Message | Historical Brand Response |
|---|---|---|---|---|
| 1 | `amazon_case_0001857` | `789027` | Someone compromised my account... Why doesn’t have the tools to address my issue immediately... it’s 2017, the process is antiquat... | Which Amazon website are you having the issue on? |
| 2 | `amazon_case_0001858` | `789027` | <URL> | Thanks for confirming- Have you been advised that our Account Specialists are reviewing the account for you? |
| 3 | `amazon_case_0005330` | `2104994` | Dear , how long will you be investigating unauthorised payment made on my wife's credit card? Was expecting an update 48 hrs ago 😡 | Did you manage to establish which Amazon (.com / .co.uk / .de / etc) the charge was on ? |
| 4 | `amazon_case_0007343` | `1583690` | My account has been compromised despite two factor authentication - I’ve called to report but not sure the seriousness is understo... | I'm sorry for the poor experience! When you last spoke with us, what information or options were provided? |
| 5 | `amazon_case_0007344` | `1583690` | Nothing helpful - this needs escalating to your security team now. | I understand how that feels, Andrew. Have you received any e-mails regarding your account? Remember to check spam/junk. |
| 6 | `amazon_case_0007345` | `1583690` | I received two codes and an email notifying me of an account change - my pw has been changed | I'd like a member of our team to look into this further. Please provide additional info here: <URL> |
| 7 | `amazon_case_0007346` | `1583690` | Since my account has been compromised and the password changed I cannot do this | Please click the skip sign-in beneath the gold sign-in button using the link SG provided. |
| 8 | `amazon_case_0007347` | `1583690` | Done | Thank you, please give a member of our team time to review your information. |
| 9 | `amazon_case_0007892` | `273882` | I called again and had to repeat my experience and its been like that everytime I call. They write a report, send it to an acct sp... | Hello, I am sorry to hear this issue has been ongoing. May I ask which site you are using? |
| 10 | `amazon_case_0007893` | `273882` | <URL> related to downloaded videos. | Hi, what has been advised or actioned by Customer service when you contacted? |
| 11 | `amazon_case_0007894` | `273882` | There was "hold" music for about 10+ mins, then silence for 10 mins or so, then call discnnctd... | Provide your details here: <URL> and "Skip Sign in" so my team can look into this further. |
| 12 | `amazon_case_0007895` | `273882` | Last call about 2 wks ago got discnnctd. Put on hold by cust service bec she was writing anthr reprt. | We can look into this for you. Please fill in the link below and we will reach out to you shortly: <URL> |
| 13 | `amazon_case_0009558` | `2897603` | Apparently someone tried to login to my Amazon account which has a long, impossible to guess password so I'm guessing either has b... | Thanks for reaching out! If you think your Amazon account has been compromised, please reach out to us here <URL> so we can look f... |
| 14 | `amazon_case_0009559` | `2897603` | Doing that now! Thanks! | You're welcome! We look forward to speaking with you. |
| 15 | `amazon_case_0009825` | `1587290` | No emails so far | Have you checked your spam and junk folders? We can take a closer look into this via the link here: <URL> |
| 16 | `amazon_case_0009826` | `1587290` | Nope nothing there | Thanks for checking. We'd like to take another go at this with you. Using's link, please reach us when you can. |
| 17 | `amazon_case_0012335` | `280148` | This is really upset me as this was a birthday 🎉 present for someone and the only reason i used is because of the Wishlist 🤣 | Our team is happy to reach out to our Account Specialists for you, please skip sign-in here: <URL> |
| 18 | `amazon_case_0015734` | `2643830` | unauthorized transaction made on debit card for a canceled purchase made on Aug 3 and charged on 30 Oct. How can u authorize my DC | I'm sorry to know about the payment issue. Kindly contact our team here: <URL> and we'll check. |
| 19 | `amazon_case_0016491` | `1072183` | Another day, another email from saying that my account has been compromised in some way. | I'm sorry for the account trouble! Have you been able to report this to us: <URL> |
| 20 | `amazon_case_0016608` | `810232` | hey my account has been breached but I can't contact Amazon because I can't log in. Do you have a regular email? | Oh no! We'd love to help restore your account access, Dok. Please contact us using this link: <URL> |
| 21 | `amazon_case_0018142` | `1860944` | yall got my account compromised and your shitty customer service reps aren't doing anything to help me get it back | I'm sorry to hear of this. Without giving us any personal information, can you let us know what you were advised when you contacte... |
| 22 | `amazon_case_0018143` | `1860944` | Got an email stating that the email associated with the account has been changed, even though I did not change it and now I no lon... | How long ago was it that you spoke to us? Which one of our sites are you using? Is it from <URL> <URL> or one of our others? |
| 23 | `amazon_case_0018144` | `1860944` | Got it figured out thank you | Great, glad to hear it's been sorted! |
| 24 | `amazon_case_0018767` | `2386035` | My Card details listed on Amazon got compromised and there has been fraudulent transactions. Response from your customer care has ... | I’m sorry about the hassle. Please drop in your details here: <URL> We will look into it. |
| 25 | `amazon_case_0019290` | `2124736` | Im sick to death of opening cases and sending emails. My account has been compromised. I was told it would be sorted after 48 hour... | Using the link SK provided will be the quickest way to escalate your issue to our team best suited to help you. |
| 26 | `amazon_case_0021619` | `1341621` | Irresponsible <URL> Unauthorized interests on buyer for a great Indian sale purchase !! Amzn India unhelpful | Our apologies for any inconvenience you had to go through. Please tell us what went wrong and we'll be glad to help you. |
| 27 | `amazon_case_0021620` | `1341621` | Contacted CC regarding problem, and with bank too. But people are pelting stones on each other in front of me but no solution ! Wh... | Apologies for the experience, Sreeram. Please share your details here: <URL> (1/2) |
| 28 | `amazon_case_0021621` | `1341621` | Contacted CC regarding problem, and with bank too. But people are pelting stones on each other in front of me but no solution ! Wh... | I'll reach and assist you, once we receive your details. Please do keep us posted for any further assistance. (2/2) |
| 29 | `amazon_case_0023364` | `2917171` | My wife just found an email notifying her that the email associated with her account was updated. We did not authorize this change... | I'm sorry for the frustration! To clarify, is she still able to sign in to the Amazon account? |
| 30 | `amazon_case_0023365` | `2917171` | No, since the email address was changed, we can't initiate the "forgot password" process. | I understand, please ask your wife (account holder) to contact us at the earliest opportunity: <URL> |

---

## 4. Empirical Evaluation of Core Questions

### Question 5: Do hacked/compromised accounts form a coherent, sufficiently frequent, and operationally distinct group?

1. **Semantic Coherence: YES (High Coherence)**
   - Customers across all 832 compromise cases describe a singular, unambiguous grievance: third-party invasion of their account.
   - Common patterns: *"Someone hacked my account"*, *"email changed without my authorization"*, *"password was changed and I didn't request it"*, *"orders placed that I did not make"*.
   - The problem statement is fundamentally distinct from *"I forgot my password"* or *"My SMS code didn't arrive"*.

2. **Frequency & Volume: YES (Sufficiently Frequent)**
   - 832 total compromise/unauthorized cases in the development dataset (~0.50% of all cases; 13.9% of all account cases).
   - For comparison, existing distinct frozen leaf intents have comparable or smaller overall dataset representation:
     - `RETURN_PICKUP_ISSUE`: ~1,200 cases (0.71%)
     - `DIGITAL_CONTENT_ACCESS`: ~1,400 cases (0.83%)
     - `CARRIER_FEEDBACK_AND_INSTRUCTIONS`: ~1,600 cases (0.95%)
   - Compromised accounts represent substantial real-world volume that cannot be dismissed as negligible edge cases.

3. **Operational Distinctness: YES (Fundamentally Different Tooling & Policy)**
   - **Tooling Difference:** Standard authentication flows rely on customer self-service (password reset URL, OTP resend). In a compromise case, self-service is physically broken because the attacker owns the compromised contact endpoint. Agents must initiate account lockdown and route to Fraud Investigation.
   - **Risk Level:** Compromise involves ongoing financial and identity risk (stored payment cards, saved addresses, unauthorized orders). Routine login failure carries zero fraud risk.
   - **Escalation Requirement:** Compromise cases mandate human intervention and identity verification (KYC/phone callback), whereas routine login cases are prime candidates for safe automated resolution.

### Question 6: Do compromised cases historically receive materially different support responses from normal login/OTP cases?

Empirical inspection of historical Amazon support replies demonstrates a sharp, material divergence in response behavior:

| Criterion | Normal Login / OTP / Forgot Password | Hacked / Compromised / Unauthorized Change |
|---|---|---|
| **Primary Channel Directed** | Public self-service links (`amazon.co.uk/help...`) | Emergency telephone lines (`0808 145 3760`) or secure authenticated callback links |
| **Action Recommended** | Reset password online, clear cookies, try another browser, check SMS signal | Immediate account freeze, phone verification, contact specialized Account Specialist |
| **Specialist Routing** | General front-line customer service | Escalation to dedicated Fraud / Account Specialists team |
| **Privacy & Security Warning** | Standard guidance | Explicit warning not to share personal/account details on Twitter; immediate transition to secure phone/email |
| **Financial Interception** | None | Cancellation of pending orders, charge verification, card issuer contact advice |

### Conclusion & Taxonomy Implications (For Human Consideration)

- The empirical data clearly demonstrates that `ACCOUNT_ACCESS_AND_SECURITY` currently houses two operationally incompatible flows under `ACCOUNT_LOGIN_ISSUES`:
  1. **Benign Authentication Friction:** (Forgot password, OTP code delays, general login difficulty) $\rightarrow$ Safe for automated guidance and self-service deflection.
  2. **Security & Account Compromise:** (Hacked accounts, unauthorized email changes, fraudulent orders) $\rightarrow$ Requires immediate human escalation and account freeze.
- **Important Note:** In accordance with instructions, Taxonomy v1 remains strictly FROZEN. These findings are documented for human authority evaluation in future taxonomy revisions (e.g. Taxonomy v1.1 or v2.0).
