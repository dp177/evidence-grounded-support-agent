"""Enrich Golden V3 cases with multi-turn dialogues to achieve 90-100 multi-turn cases."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 1. Update security_and_login.py
sec_path = ROOT / "scripts/golden_v3_data/security_and_login.py"
sec_content = sec_path.read_text(encoding="utf-8")

# Replace single-turn contexts with realistic multi-turn context where appropriate
sec_replacements = [
    (
        '"context": "CUSTOMER: Got a notification that my primary login email was switched to a yopmail address. I never authorized this! Please help recover my account."',
        '"context": "CUSTOMER: Received a critical security notification on my smartphone.\\nBRAND: Did the alert specify any unauthorized changes to your credentials?\\nCUSTOMER: Got a notification that my primary login email was switched to a yopmail address. I never authorized this! Please help recover my account."'
    ),
    (
        '"context": "CUSTOMER: My account was hijacked while I was on vacation and multiple orders were dispatched to a locker in Miami that isn\'t mine."',
        '"context": "CUSTOMER: Need urgent investigation on unexpected delivery dispatch emails.\\nBRAND: Can you check if those orders reflect on your recent order history?\\nCUSTOMER: My account was hijacked while I was on vacation and multiple orders were dispatched to a locker in Miami that isn\'t mine."'
    ),
    (
        '"context": "CUSTOMER: I never requested that password change notification I got at 3 AM. Now I\'m locked out and terrified someone stole my payment cards."',
        '"context": "CUSTOMER: Something is wrong, my account password stopped working overnight.\\nBRAND: Did you receive any security emails regarding your credentials?\\nCUSTOMER: I never requested that password change notification I got at 3 AM. Now I\'m locked out and terrified someone stole my payment cards."'
    ),
    (
        '"context": "CUSTOMER: There are unauthorized transactions showing on my account from yesterday that weren\'t me. Someone has breached my login."',
        '"context": "CUSTOMER: Fraud alert on my registered debit card from Amazon.\\nBRAND: Have you verified the purchase history under Your Orders?\\nCUSTOMER: There are unauthorized transactions showing on my account from yesterday that weren\'t me. Someone has breached my login."'
    ),
    (
        '"context": "CUSTOMER: Someone broke into my Amazon account and added an unknown phone number for two-step verification so I can\'t receive the OTP!"',
        '"context": "CUSTOMER: I am unable to receive my login verification code.\\nBRAND: Is your primary phone number showing on the 2FA prompt?\\nCUSTOMER: Someone broke into my Amazon account and added an unknown phone number for two-step verification so I can\'t receive the OTP!"'
    ),
    (
        '"context": "CUSTOMER: I think my credentials were compromised in a data leak. Someone is currently logged into my account changing my shipping addresses."',
        '"context": "CUSTOMER: Seeing address changes in my account settings right now.\\nBRAND: Did you recently update any shipping preferences?\\nCUSTOMER: I think my credentials were compromised in a data leak. Someone is currently logged into my account changing my shipping addresses."'
    ),
    (
        '"context": "CUSTOMER: My Amazon account has been taken over by a scammer who changed my recovery credentials without my consent."',
        '"context": "CUSTOMER: Emergency: account locked out and recovery options altered.\\nBRAND: Have you tried resetting via your original recovery email?\\nCUSTOMER: My Amazon account has been taken over by a scammer who changed my recovery credentials without my consent."'
    ),
    (
        '"context": "CUSTOMER: Received an alert saying my password and security phone were updated. It was not me! Please freeze the account before they buy anything."',
        '"context": "CUSTOMER: Security alert received 5 minutes ago.\\nBRAND: Did you initiate a credential update recently?\\nCUSTOMER: Received an alert saying my password and security phone were updated. It was not me! Please freeze the account before they buy anything."'
    ),
    (
        '"context": "CUSTOMER: My account was compromised, the hacker changed the email address, and customer service locked the profile, but I haven\'t received recovery instructions."',
        '"context": "CUSTOMER: Following up on security ticket #SEC-882194.\\nBRAND: Did you check your secondary email inbox for the verification link?\\nCUSTOMER: My account was compromised, the hacker changed the email address, and customer service locked the profile, but I haven\'t received recovery instructions."'
    ),
    (
        '"context": "CUSTOMER: I never made any request to change my password or phone, but both were updated 20 minutes ago and now my sign-in fails."',
        '"context": "CUSTOMER: Suddenly logged out while browsing on the shopping app.\\nBRAND: What message appears when you re-enter your credentials?\\nCUSTOMER: I never made any request to change my password or phone, but both were updated 20 minutes ago and now my sign-in fails."'
    ),
    (
        '"context": "CUSTOMER: Account has been suspended for address verification. Sent the requested bank statement a week ago and still can\'t log in despite waiting."',
        '"context": "CUSTOMER: Account suspended pending document verification.\\nBRAND: Have you uploaded the utility bill or bank statement via the secure portal?\\nCUSTOMER: Account has been suspended for address verification. Sent the requested bank statement a week ago and still can\'t log in despite waiting."'
    ),
    (
        '"context": "CUSTOMER: Having trouble signing in because my password manager filled an old password. Where is login assistance?"',
        '"context": "CUSTOMER: Trouble accessing my account this morning.\\nBRAND: Are you receiving an incorrect password prompt?\\nCUSTOMER: Having trouble signing in because my password manager filled an old password. Where is login assistance?"'
    ),
    (
        '"context": "CUSTOMER: How do I switch the primary email address on my Amazon account to my new work email?"',
        '"context": "CUSTOMER: Account settings question.\\nBRAND: Are you currently logged into your Amazon profile?\\nCUSTOMER: How do I switch the primary email address on my Amazon account to my new work email?"'
    ),
]

for old, new in sec_replacements:
    assert old in sec_content, f"Missing in sec: {old}"
    sec_content = sec_content.replace(old, new)
sec_path.write_text(sec_content, encoding="utf-8")
print("Updated security_and_login.py multi-turn contexts")


# 2. Update carrier_and_delivery.py
car_path = ROOT / "scripts/golden_v3_data/carrier_and_delivery.py"
car_content = car_path.read_text(encoding="utf-8")

car_replacements = [
    (
        '"context": "CUSTOMER: The delivery driver refused to carry my air conditioner up a short flight of stairs despite explicit accessibility instructions and left it in the rain."',
        '"context": "CUSTOMER: Complaint about delivery driver conduct today.\\nBRAND: Could you describe what occurred with your delivery?\\nCUSTOMER: The delivery driver refused to carry my air conditioner up a short flight of stairs despite explicit accessibility instructions and left it in the rain."'
    ),
    (
        '"context": "CUSTOMER: Courier called from the street demanding that I walk two blocks to his van to pick up my heavy parcel because he didn\'t want to find street parking."',
        '"context": "CUSTOMER: Issue with driver on delivery of order #112-9018247.\\nBRAND: Did the carrier attempt delivery at your physical address?\\nCUSTOMER: Courier called from the street demanding that I walk two blocks to his van to pick up my heavy parcel because he didn\'t want to find street parking."'
    ),
    (
        '"context": "CUSTOMER: The delivery driver became extremely belligerent, screamed at me, and rudely shouted profanities when I asked him to place the box behind the porch pillar."',
        '"context": "CUSTOMER: Extremely unacceptable driver behavior outside my home.\\nBRAND: What happened when the delivery driver arrived?\\nCUSTOMER: The delivery driver became extremely belligerent, screamed at me, and rudely shouted profanities when I asked him to place the box behind the porch pillar."'
    ),
    (
        '"context": "CUSTOMER: Delivery person chucked my fragile computer monitor box over the 7-foot driveway gate, smashing it directly against the concrete driveway!"',
        '"context": "CUSTOMER: Reporting serious parcel damage caused by delivery driver.\\nBRAND: How was the package handled upon arrival?\\nCUSTOMER: Delivery person chucked my fragile computer monitor box over the 7-foot driveway gate, smashing it directly against the concrete driveway!"'
    ),
    (
        '"context": "CUSTOMER: Driver refused to deliver my order because I asked him to buzz the intercom number provided on the delivery instructions."',
        '"context": "CUSTOMER: Courier refused to drop off parcel at my unit.\\nBRAND: Were specific access codes provided for your building?\\nCUSTOMER: Driver refused to deliver my order because I asked him to buzz the intercom number provided on the delivery instructions."'
    ),
    (
        '"context": "CUSTOMER: Driver aggressively banged on my front door, shouted rudely, and demanded a cash tip before handing over the parcel."',
        '"context": "CUSTOMER: Driver demanded extra payment at my doorstep.\\nBRAND: Did the carrier driver specify why they requested payment?\\nCUSTOMER: Driver aggressively banged on my front door, shouted rudely, and demanded a cash tip before handing over the parcel."'
    ),
    (
        '"context": "CUSTOMER: Courier refused entry through security desk despite being provided an official guest badge and drove off, marking chronic delivery refusal."',
        '"context": "CUSTOMER: Commercial delivery failed today.\\nBRAND: Did security grant the carrier authorized facility access?\\nCUSTOMER: Courier refused entry through security desk despite being provided an official guest badge and drove off, marking chronic delivery refusal."'
    ),
    (
        '"context": "CUSTOMER: Driver forged my signature on a high-value laptop delivery while I was away at work, leaving the package exposed on the sidewalk."',
        '"context": "CUSTOMER: Signature verification discrepancy on delivery.\\nBRAND: Did tracking show signed by resident?\\nCUSTOMER: Driver forged my signature on a high-value laptop delivery while I was away at work, leaving the package exposed on the sidewalk."'
    ),
    (
        '"context": "CUSTOMER: Delivery agent refused to complete delivery, telling me over the phone to come down to the parking lot or he would take it back to the hub."',
        '"context": "CUSTOMER: Driver refused to come to the building.\\nBRAND: Did you speak directly with the courier?\\nCUSTOMER: Delivery agent refused to complete delivery, telling me over the phone to come down to the parking lot or he would take it back to the hub."'
    ),
    (
        '"context": "CUSTOMER: Please add gate access code #5521 for the Amazon logistics delivery driver."',
        '"context": "CUSTOMER: Adding access information for delivery today.\\nBRAND: What gate code or entry instructions would you like provided?\\nCUSTOMER: Please add gate access code #5521 for the Amazon logistics delivery driver."'
    ),
    (
        '"context": "CUSTOMER: Can I request that packages be placed inside the screened back porch rather than the front steps?"',
        '"context": "CUSTOMER: Delivery location preference question.\\nBRAND: Are you looking to update default delivery preferences for your address?\\nCUSTOMER: Can I request that packages be placed inside the screened back porch rather than the front steps?"'
    ),
    (
        '"context": "CUSTOMER: Where can I provide instructions to ring the front doorbell upon parcel arrival?"',
        '"context": "CUSTOMER: Notification instruction inquiry.\\nBRAND: Do you want this noted on a specific order or for all future deliveries?\\nCUSTOMER: Where can I provide instructions to ring the front doorbell upon parcel arrival?"'
    ),
    (
        '"context": "CUSTOMER: How do I contact the local carrier facility to arrange an evening delivery window?"',
        '"context": "CUSTOMER: Need to adjust delivery timing with courier.\\nBRAND: Has your order already been assigned to a local carrier facility?\\nCUSTOMER: How do I contact the local carrier facility to arrange an evening delivery window?"'
    ),
    (
        '"context": "CUSTOMER: I have contacted customer care four separate times about this delayed parcel and each representative transfers me to someone else with no answer!"',
        '"context": "CUSTOMER: Following up on overdue package.\\nBRAND: Have you checked the latest carrier scan update?\\nCUSTOMER: I have contacted customer care four separate times about this delayed parcel and each representative transfers me to someone else with no answer!"'
    ),
    (
        '"context": "CUSTOMER: Called support across 5 attempts over 10 days for my delayed medication and nobody has been able to sort this out."',
        '"context": "CUSTOMER: Chronic delay on urgent medication order.\\nBRAND: What did previous representatives advise regarding shipment status?\\nCUSTOMER: Called support across 5 attempts over 10 days for my delayed medication and nobody has been able to sort this out."'
    ),
    (
        '"context": "CUSTOMER: A supervisor promised a guaranteed callback within 4 hours regarding my delayed furniture that never happened and now it\'s been 3 days."',
        '"context": "CUSTOMER: Awaiting promised support escalation callback.\\nBRAND: Did the previous supervisor provide a ticket reference number?\\nCUSTOMER: A supervisor promised a guaranteed callback within 4 hours regarding my delayed furniture that never happened and now it\'s been 3 days."'
    ),
    (
        '"context": "CUSTOMER: My package was expected yesterday by 8 PM and still hasn\'t arrived. Can you check status?"',
        '"context": "CUSTOMER: Inquiry regarding order #113-8821940.\\nBRAND: Did tracking indicate out for delivery yesterday?\\nCUSTOMER: My package was expected yesterday by 8 PM and still hasn\'t arrived. Can you check status?"'
    ),
    (
        '"context": "CUSTOMER: Package has been stuck at the regional distribution center for 3 days without movement."',
        '"context": "CUSTOMER: Package transit inquiry.\\nBRAND: Has the estimated delivery date passed?\\nCUSTOMER: Package has been stuck at the regional distribution center for 3 days without movement."'
    ),
    (
        '"context": "CUSTOMER: Ordered with same-day shipping this morning but tracking indicates it won\'t arrive until tomorrow afternoon."',
        '"context": "CUSTOMER: Same-day shipping timeline question.\\nBRAND: Did you select same-day checkout before the daily cutoff window?\\nCUSTOMER: Ordered with same-day shipping this morning but tracking indicates it won\'t arrive until tomorrow afternoon."'
    ),
    (
        '"context": "CUSTOMER: I contacted support yesterday once and they told me it might arrive today, but still hasn\'t shown up."',
        '"context": "CUSTOMER: Delivery delay follow-up.\\nBRAND: What advice did our representative provide on yesterday\'s contact?\\nCUSTOMER: I contacted support yesterday once and they told me it might arrive today, but still hasn\'t shown up."'
    ),
    (
        '"context": "CUSTOMER: Tracking says delivered to mailbox at 2 PM but my mailbox is completely empty."',
        '"context": "CUSTOMER: Package delivery scan issue.\\nBRAND: Have you verified the delivery confirmation details in Your Orders?\\nCUSTOMER: Tracking says delivered to mailbox at 2 PM but my mailbox is completely empty."'
    ),
    (
        '"context": "CUSTOMER: App shows parcel left in resident lobby, but building management confirmed no deliveries arrived today."',
        '"context": "CUSTOMER: Delivery location dispute on order #114-7721849.\\nBRAND: Did the delivery photo show the lobby mail table?\\nCUSTOMER: App shows parcel left in resident lobby, but building management confirmed no deliveries arrived today."'
    ),
    (
        '"context": "CUSTOMER: Carrier marked parcel delivered yesterday. Checked with neighbors and building security, no sign of it."',
        '"context": "CUSTOMER: 24 hours passed since delivery scan.\\nBRAND: Have you checked alternative drop locations around your property?\\nCUSTOMER: Carrier marked parcel delivered yesterday. Checked with neighbors and building security, no sign of it."'
    ),
    (
        '"context": "CUSTOMER: Driver photo shows package dropped near public street sidewalk instead of my door and it\'s gone."',
        '"context": "CUSTOMER: Delivery photo inspection on missing package.\\nBRAND: Was the package left inside your front gate perimeter?\\nCUSTOMER: Driver photo shows package dropped near public street sidewalk instead of my door and it\'s gone."'
    ),
    (
        '"context": "CUSTOMER: I called support 3 times already about this order marked delivered that never arrived, and each rep hung up or transferred me!"',
        '"context": "CUSTOMER: Calling about missing order marked delivered.\\nBRAND: Did previous agents open an investigation with the logistics carrier?\\nCUSTOMER: I called support 3 times already about this order marked delivered that never arrived, and each rep hung up or transferred me!"'
    ),
    (
        '"context": "CUSTOMER: Where can I find the tracking number for my order dispatched this morning?"',
        '"context": "CUSTOMER: Tracking lookup assistance needed.\\nBRAND: Have you received your dispatch confirmation notification?\\nCUSTOMER: Where can I find the tracking number for my order dispatched this morning?"'
    ),
    (
        '"context": "CUSTOMER: Can you tell me the current location of order #114-8829103-9920194?"',
        '"context": "CUSTOMER: Inquiring about shipping progress.\\nBRAND: Could you provide the order ID you want tracked?\\nCUSTOMER: Can you tell me the current location of order #114-8829103-9920194?"'
    ),
    (
        '"context": "CUSTOMER: Order shows shipped three days ago, when will detailed tracking scans appear?"',
        '"context": "CUSTOMER: Dispatch scan question.\\nBRAND: Has the carrier scanned the parcel at the regional sorting hub?\\nCUSTOMER: Order shows shipped three days ago, when will detailed tracking scans appear?"'
    ),
]

for old, new in car_replacements:
    assert old in car_content, f"Missing in car: {old}"
    car_content = car_content.replace(old, new)
car_path.write_text(car_content, encoding="utf-8")
print("Updated carrier_and_delivery.py multi-turn contexts")


# 3. Update returns_and_refunds.py
ret_path = ROOT / "scripts/golden_v3_data/returns_and_refunds.py"
ret_content = ret_path.read_text(encoding="utf-8")

ret_replacements = [
    (
        '"context": "CUSTOMER: I have contacted support 4 separate times about this cracked television and every agent promises a replacement pickup that never happens!"',
        '"context": "CUSTOMER: Following up on damaged television replacement.\\nBRAND: Have you received confirmation of the replacement dispatch?\\nCUSTOMER: I have contacted support 4 separate times about this cracked television and every agent promises a replacement pickup that never happens!"'
    ),
    (
        '"context": "CUSTOMER: I\'ve tried getting help several times across 3 weeks for this defective blender and no resolution was offered by customer service."',
        '"context": "CUSTOMER: Ongoing problem with non-functional kitchen appliance.\\nBRAND: Did previous representatives initiate a warranty exchange?\\nCUSTOMER: I\'ve tried getting help several times across 3 weeks for this defective blender and no resolution was offered by customer service."'
    ),
    (
        '"context": "CUSTOMER: Received ceramic dinner set today but three of the bowls were completely shattered in transit."',
        '"context": "CUSTOMER: Order damaged upon opening.\\nBRAND: What specific items were broken inside the parcel?\\nCUSTOMER: Received ceramic dinner set today but three of the bowls were completely shattered in transit."'
    ),
    (
        '"context": "CUSTOMER: Brand new cordless vacuum turns on for 5 seconds and immediately shuts off with a red battery error indicator."',
        '"context": "CUSTOMER: Technical defect on newly delivered vacuum.\\nBRAND: Have you performed a full overnight charge cycle?\\nCUSTOMER: Brand new cordless vacuum turns on for 5 seconds and immediately shuts off with a red battery error indicator."'
    ),
    (
        '"context": "CUSTOMER: My electric kettle arrived with a dent in the stainless steel base and doesn\'t boil water properly."',
        '"context": "CUSTOMER: Appliance arrived damaged in box.\\nBRAND: Does the unit heat water when plugged into a different outlet?\\nCUSTOMER: My electric kettle arrived with a dent in the stainless steel base and doesn\'t boil water properly."'
    ),
    (
        '"context": "CUSTOMER: The wooden study desk has a deep gouge across the top surface. How do I get a replacement part sent?"',
        '"context": "CUSTOMER: Furniture package opened today.\\nBRAND: Was the outer packaging carton pierced or torn?\\nCUSTOMER: The wooden study desk has a deep gouge across the top surface. How do I get a replacement part sent?"'
    ),
    (
        '"context": "CUSTOMER: The glass vase arrived broken into dozens of sharp fragments. Can I get a refund without shipping broken glass back?"',
        '"context": "CUSTOMER: Glass shipment arrived shattered.\\nBRAND: For safety reasons, please do not handle broken glass.\\nCUSTOMER: The glass vase arrived broken into dozens of sharp fragments. Can I get a refund without shipping broken glass back?"'
    ),
    (
        '"context": "CUSTOMER: I\'ve been passed from agent to agent five times trying to get the right textbook sent for my semester!"',
        '"context": "CUSTOMER: Urgent book exchange needed.\\nBRAND: What did the last agent advise regarding the re-order?\\nCUSTOMER: I\'ve been passed from agent to agent five times trying to get the right textbook sent for my semester!"'
    ),
    (
        '"context": "CUSTOMER: Support promised someone would contact me within 24 hours regarding the wrong laptop shipped, but nobody did and it\'s been four days."',
        '"context": "CUSTOMER: Awaiting callback on wrong computer delivery.\\nBRAND: Do you have the prior support case ID handy?\\nCUSTOMER: Support promised someone would contact me within 24 hours regarding the wrong laptop shipped, but nobody did and it\'s been four days."'
    ),
    (
        '"context": "CUSTOMER: Ordered men\'s size 11 running shoes but received size 7 in the box."',
        '"context": "CUSTOMER: Wrong item received on order #111-8849102.\\nBRAND: What size did you receive in the manufacturer packaging?\\nCUSTOMER: Ordered men\'s size 11 running shoes but received size 7 in the box."'
    ),
    (
        '"context": "CUSTOMER: I ordered an espresso coffee machine but received a box containing stainless steel cookware instead."',
        '"context": "CUSTOMER: Incorrect parcel contents received.\\nBRAND: What item was inside the package delivered today?\\nCUSTOMER: I ordered an espresso coffee machine but received a box containing stainless steel cookware instead."'
    ),
    (
        '"context": "CUSTOMER: Ordered a 500GB SSD drive but received a 128GB version instead."',
        '"context": "CUSTOMER: Computer component variant mismatch.\\nBRAND: What model specification is printed on the barcode label?\\nCUSTOMER: Ordered a 500GB SSD drive but received a 128GB version instead."'
    ),
    (
        '"context": "CUSTOMER: Box contained an air purifier filter replacement instead of the actual air purifier unit I paid for."',
        '"context": "CUSTOMER: Incomplete or incorrect shipment received.\\nBRAND: Does the packing slip indicate a multi-box shipment?\\nCUSTOMER: Box contained an air purifier filter replacement instead of the actual air purifier unit I paid for."'
    ),
    (
        '"context": "CUSTOMER: Courier failed the scheduled return pickup 4 separate times and customer care just reschedules without fixing the courier problem!"',
        '"context": "CUSTOMER: Ongoing failure with return pickup service.\\nBRAND: Did the carrier leave any missed pickup door-tags?\\nCUSTOMER: Courier failed the scheduled return pickup 4 separate times and customer care just reschedules without fixing the courier problem!"'
    ),
    (
        '"context": "CUSTOMER: I\'ve spent days trying to get this mattress return picked up; driver never showed up across three separate appointments."',
        '"context": "CUSTOMER: Bulky mattress return collection issue.\\nBRAND: Have our logistics partners provided an updated pickup window?\\nCUSTOMER: I\'ve spent days trying to get this mattress return picked up; driver never showed up across three separate appointments."'
    ),
    (
        '"context": "CUSTOMER: Called support 3 times about courier not showing up for return pickup and each rep told me someone would call, but nobody called."',
        '"context": "CUSTOMER: Checking on rescheduled return pickup.\\nBRAND: What did previous agents confirm regarding carrier dispatch?\\nCUSTOMER: Called support 3 times about courier not showing up for return pickup and each rep told me someone would call, but nobody called."'
    ),
    (
        '"context": "CUSTOMER: UPS driver did not show up for my scheduled return pickup between 9 AM and 1 PM today."',
        '"context": "CUSTOMER: Return pickup appointment status inquiry.\\nBRAND: Was a return pickup window scheduled for this morning?\\nCUSTOMER: UPS driver did not show up for my scheduled return pickup between 9 AM and 1 PM today."'
    ),
    (
        '"context": "CUSTOMER: The QR drop-off code generated for The UPS Store shows expired on my phone. How do I regenerate it?"',
        '"context": "CUSTOMER: Return drop-off code problem.\\nBRAND: Has the 30-day return drop-off window elapsed?\\nCUSTOMER: The QR drop-off code generated for The UPS Store shows expired on my phone. How do I regenerate it?"'
    ),
    (
        '"context": "CUSTOMER: Can I change my return method from home pickup to drop-off at a Whole Foods location?"',
        '"context": "CUSTOMER: Modifying return drop-off selection.\\nBRAND: Would you prefer an instant QR code return at a nearby store?\\nCUSTOMER: Can I change my return method from home pickup to drop-off at a Whole Foods location?"'
    ),
    (
        '"context": "CUSTOMER: I have contacted support 4 times over 3 weeks for my refund after the return was confirmed received, and still no credit or explanation!"',
        '"context": "CUSTOMER: Missing refund on returned merchandise.\\nBRAND: Have you verified the return delivery confirmation tracking?\\nCUSTOMER: I have contacted support 4 times over 3 weeks for my refund after the return was confirmed received, and still no credit or explanation!"'
    ),
    (
        '"context": "CUSTOMER: Representative promised my refund would be processed in 48 hours, but that window passed a week ago and nobody can tell me what happened."',
        '"context": "CUSTOMER: Following up on promised refund processing.\\nBRAND: Did our billing specialist confirm a manual refund authorization?\\nCUSTOMER: Representative promised my refund would be processed in 48 hours, but that window passed a week ago and nobody can tell me what happened."'
    ),
    (
        '"context": "CUSTOMER: Cancelled an order before dispatch. How many business days does it take for the funds to release back to my debit card?"',
        '"context": "CUSTOMER: Refund timeline inquiry on cancelled order.\\nBRAND: Was the cancellation completed before shipping authorization?\\nCUSTOMER: Cancelled an order before dispatch. How many business days does it take for the funds to release back to my debit card?"'
    ),
    (
        '"context": "CUSTOMER: My return was approved for Amazon gift card balance credit, where can I verify the balance in my wallet?"',
        '"context": "CUSTOMER: Checking gift card credit from return.\\nBRAND: Did you select gift card balance as your preferred refund method?\\nCUSTOMER: My return was approved for Amazon gift card balance credit, where can I verify the balance in my wallet?"'
    ),
]

for old, new in ret_replacements:
    assert old in ret_content, f"Missing in ret: {old}"
    ret_content = ret_content.replace(old, new)
ret_path.write_text(ret_content, encoding="utf-8")
print("Updated returns_and_refunds.py multi-turn contexts")


# 4. Update orders_prime_digital.py
ord_path = ROOT / "scripts/golden_v3_data/orders_prime_digital.py"
ord_content = ord_path.read_text(encoding="utf-8")

ord_replacements = [
    (
        '"context": "CUSTOMER: I placed an order accidentally 5 minutes ago, where is the cancel button in Your Orders?"',
        '"context": "CUSTOMER: Accidental order placed just now.\\nBRAND: Have you checked the order status in Your Orders?\\nCUSTOMER: I placed an order accidentally 5 minutes ago, where is the cancel button in Your Orders?"'
    ),
    (
        '"context": "CUSTOMER: Requested cancellation 2 hours ago but status still shows \'Cancellation Pending\'. Did it go through?"',
        '"context": "CUSTOMER: Cancellation status inquiry.\\nBRAND: Did you submit the request prior to the order entering dispatch preparation?\\nCUSTOMER: Requested cancellation 2 hours ago but status still shows \'Cancellation Pending\'. Did it go through?"'
    ),
    (
        '"context": "CUSTOMER: I moved yesterday and need to update the delivery address on order #114-9920194-2201948 before it dispatches."',
        '"context": "CUSTOMER: Address modification request.\\nBRAND: What is the current status shown on the order details page?\\nCUSTOMER: I moved yesterday and need to update the delivery address on order #114-9920194-2201948 before it dispatches."'
    ),
    (
        '"context": "CUSTOMER: Can I change the payment card used on an active order that hasn\'t shipped yet?"',
        '"context": "CUSTOMER: Updating payment details.\\nBRAND: Has your payment already been authorized by your bank?\\nCUSTOMER: Can I change the payment card used on an active order that hasn\'t shipped yet?"'
    ),
    (
        '"context": "CUSTOMER: Need to update the delivery day to Saturday for my upcoming scheduled Amazon Day pantry order."',
        '"context": "CUSTOMER: Scheduled delivery adjustment.\\nBRAND: Are you managing your Amazon Day delivery settings?\\nCUSTOMER: Need to update the delivery day to Saturday for my upcoming scheduled Amazon Day pantry order."'
    ),
    (
        '"context": "CUSTOMER: I was charged $139 for an annual Prime membership renewal that I did not intend to renew. Can I get a refund?"',
        '"context": "CUSTOMER: Prime membership charge inquiry.\\nBRAND: Have any Prime benefits been used since the renewal date?\\nCUSTOMER: I was charged $139 for an annual Prime membership renewal that I did not intend to renew. Can I get a refund?"'
    ),
    (
        '"context": "CUSTOMER: How do I turn off automatic renewal for my Prime student trial before it converts next week?"',
        '"context": "CUSTOMER: Student trial renewal management.\\nBRAND: Are you looking to cancel before the trial period ends?\\nCUSTOMER: How do I turn off automatic renewal for my Prime student trial before it converts next week?"'
    ),
    (
        '"context": "CUSTOMER: Prime Video gives error code 7031 on my smart TV when trying to play any title."',
        '"context": "CUSTOMER: Streaming video error on TV.\\nBRAND: Does this error occur across all devices or only your smart TV?\\nCUSTOMER: Prime Video gives error code 7031 on my smart TV when trying to play any title."'
    ),
    (
        '"context": "CUSTOMER: Purchased a Kindle ebook 30 minutes ago but it has not synchronized to my Paperwhite reader."',
        '"context": "CUSTOMER: Kindle digital delivery question.\\nBRAND: Have you performed a manual Sync and Check for Items on your device?\\nCUSTOMER: Purchased a Kindle ebook 30 minutes ago but it has not synchronized to my Paperwhite reader."'
    ),
    (
        '"context": "CUSTOMER: Amazon Music Unlimited app says my subscription is inactive even though payment was billed yesterday."',
        '"context": "CUSTOMER: Music subscription access issue.\\nBRAND: Are you signed in with the same Amazon account used for billing?\\nCUSTOMER: Amazon Music Unlimited app says my subscription is inactive even though payment was billed yesterday."'
    ),
    (
        '"context": "CUSTOMER: Rented a movie on Prime Video by mistake, haven\'t started streaming it, can I cancel for a refund?"',
        '"context": "CUSTOMER: Video rental cancellation.\\nBRAND: Have you pressed play or downloaded any portion of the title?\\nCUSTOMER: Rented a movie on Prime Video by mistake, haven\'t started streaming it, can I cancel for a refund?"'
    ),
]

for old, new in ord_replacements:
    assert old in ord_content, f"Missing in ord: {old}"
    ord_content = ord_content.replace(old, new)
ord_path.write_text(ord_content, encoding="utf-8")
print("Updated orders_prime_digital.py multi-turn contexts")


# 5. Update multi_intent.py
mul_path = ROOT / "scripts/golden_v3_data/multi_intent.py"
mul_content = mul_path.read_text(encoding="utf-8")

mul_replacements = [
    (
        '"context": "CUSTOMER: My package is 4 days late, and when the driver finally showed up he refused to walk to the porch and yelled insults at me from the street!"',
        '"context": "CUSTOMER: Terrible delivery experience with courier.\\nBRAND: Did the package eventually get dropped at your residence?\\nCUSTOMER: My package is 4 days late, and when the driver finally showed up he refused to walk to the porch and yelled insults at me from the street!"'
    ),
    (
        '"context": "CUSTOMER: I received the wrong blender model, returned it last week, and now I need to check when the refund will hit my credit card."',
        '"context": "CUSTOMER: Following up on incorrect item return.\\nBRAND: Has the item been scanned as received at our returns hub?\\nCUSTOMER: I received the wrong blender model, returned it last week, and now I need to check when the refund will hit my credit card."'
    ),
    (
        '"context": "CUSTOMER: There is an unexpected $14.99 charge on my credit card from Amazon Prime even though I cancelled my subscription last month."',
        '"context": "CUSTOMER: Unrecognized subscription debit on statement.\\nBRAND: Did you receive a confirmation email when you cancelled Prime?\\nCUSTOMER: There is an unexpected $14.99 charge on my credit card from Amazon Prime even though I cancelled my subscription last month."'
    ),
    (
        '"context": "CUSTOMER: I cancelled order #112-9840192 yesterday prior to shipment, how long until the authorization hold drops from my debit card?"',
        '"context": "CUSTOMER: Bank debit hold question after order cancellation.\\nBRAND: Was the cancellation confirmed before warehouse fulfillment?\\nCUSTOMER: I cancelled order #112-9840192 yesterday prior to shipment, how long until the authorization hold drops from my debit card?"'
    ),
    (
        '"context": "CUSTOMER: This birthday gift was supposed to arrive two days ago and is now delayed until next week. I want to cancel it immediately."',
        '"context": "CUSTOMER: Delayed birthday present inquiry.\\nBRAND: Would you like us to look into expedited replacement options?\\nCUSTOMER: This birthday gift was supposed to arrive two days ago and is now delayed until next week. I want to cancel it immediately."'
    ),
    (
        '"context": "CUSTOMER: Sent the wrong size shoes on Monday, requested replacement, and the replacement shipment is now also delayed in transit."',
        '"context": "CUSTOMER: Checking status on shoe exchange.\\nBRAND: Do you have the tracking ID for the replacement package?\\nCUSTOMER: Sent the wrong size shoes on Monday, requested replacement, and the replacement shipment is now also delayed in transit."'
    ),
    (
        '"context": "CUSTOMER: My Prime Video app says I need to renew Prime, but my Prime membership annual receipt shows active through December."',
        '"context": "CUSTOMER: Digital streaming app billing prompt.\\nBRAND: Have you checked your active subscriptions under Account Settings?\\nCUSTOMER: My Prime Video app says I need to renew Prime, but my Prime membership annual receipt shows active through December."'
    ),
    (
        '"context": "CUSTOMER: Saw two identical charges for $89 on my statement for order #111-9201948, please remove the duplicate charge."',
        '"context": "CUSTOMER: Double charge noticed on bank statement.\\nBRAND: Did you receive two distinct order confirmation numbers?\\nCUSTOMER: Saw two identical charges for $89 on my statement for order #111-9201948, please remove the duplicate charge."'
    ),
    (
        '"context": "CUSTOMER: Where is my package currently located, and can you provide gate instructions for the delivery driver?"',
        '"context": "CUSTOMER: Checking delivery progress for incoming parcel.\\nBRAND: Have you reviewed the delivery tracker in Your Orders?\\nCUSTOMER: Where is my package currently located, and can you provide gate instructions for the delivery driver?"'
    ),
    (
        '"context": "CUSTOMER: Driver brought the wrong heavy box, and when I pointed out the name mismatch he cursed at me and dumped it in my driveway anyway."',
        '"context": "CUSTOMER: Courier delivered someone else\'s package abusively.\\nBRAND: Did the delivery driver take the incorrect parcel back?\\nCUSTOMER: Driver brought the wrong heavy box, and when I pointed out the name mismatch he cursed at me and dumped it in my driveway anyway."'
    ),
]

for old, new in mul_replacements:
    assert old in mul_content, f"Missing in mul: {old}"
    mul_content = mul_content.replace(old, new)
mul_path.write_text(mul_content, encoding="utf-8")
print("Updated multi_intent.py multi-turn contexts")


# 6. Update ambiguous_and_oos.py
amb_path = ROOT / "scripts/golden_v3_data/ambiguous_and_oos.py"
amb_content = amb_path.read_text(encoding="utf-8")

amb_replacements = [
    (
        '"context": "CUSTOMER: What should I do next?"',
        '"context": "CUSTOMER: Hello\\nBRAND: Hello! How can I assist you with Amazon today?\\nCUSTOMER: What should I do next?"'
    ),
    (
        '"context": "CUSTOMER: This isn\'t working"',
        '"context": "CUSTOMER: I\'m on the website.\\nBRAND: Which page or tool are you currently viewing?\\nCUSTOMER: This isn\'t working"'
    ) if '"context": "CUSTOMER: This isn\'t working"' in amb_content else (
        '"context": "CUSTOMER: It is simply not functioning"',
        '"context": "CUSTOMER: Trying to use the portal.\\nBRAND: Which feature are you currently using?\\nCUSTOMER: It is simply not functioning"'
    ),
    (
        '"context": "CUSTOMER: Still nothing"',
        '"context": "CUSTOMER: Checking on an update.\\nBRAND: Could you tell me what you are waiting for?\\nCUSTOMER: Still nothing"'
    ),
    (
        '"context": "CUSTOMER: Can you fix this?"',
        '"context": "CUSTOMER: Having an issue.\\nBRAND: Can you tell me what order or item you need help with?\\nCUSTOMER: Can you fix this?"'
    ),
    (
        '"context": "CUSTOMER: Why did this happen?"',
        '"context": "CUSTOMER: I saw a change on my screen.\\nBRAND: What change or message appeared?\\nCUSTOMER: Why did this happen?"'
    ),
    (
        '"context": "CUSTOMER: Please review my situation"',
        '"context": "CUSTOMER: Customer service help needed.\\nBRAND: Hi, what can I assist you with today?\\nCUSTOMER: Please review my situation"'
    ),
    (
        '"context": "CUSTOMER: Is this normal?"',
        '"context": "CUSTOMER: Something seems strange.\\nBRAND: Could you describe what you are seeing?\\nCUSTOMER: Is this normal?"'
    ),
    (
        '"context": "CUSTOMER: Order issue"',
        '"context": "CUSTOMER: Hi\\nBRAND: Hello, how can Amazon help you today?\\nCUSTOMER: Order issue"'
    ),
]

for old, new in amb_replacements:
    assert old in amb_content, f"Missing in amb: {old}"
    amb_content = amb_content.replace(old, new)
amb_path.write_text(amb_content, encoding="utf-8")
print("Updated ambiguous_and_oos.py multi-turn contexts")
print("All files successfully enriched with multi-turn dialogues!")
