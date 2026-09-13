"""Inspect and select high-precision demonstration candidates."""

import json
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent

manifest = json.load(open(ROOT_DIR / "data" / "splits" / "split_manifest.json"))
golden_convs = set(str(c) for c in manifest["golden_conversation_ids"])

dev_df = pd.read_parquet(ROOT_DIR / "data" / "processed" / "amazon_support_cases.parquet")
dev_df = dev_df[~dev_df["conversation_id"].astype(str).isin(golden_convs)].copy()

patterns = {
    "WHERE_IS_MY_ORDER": r"\b(?:where is my package|track my order|tracking update on my order|when will my parcel arrive|current status of my order)\b",
    "DELIVERY_DELAYED": r"\b(?:supposed to arrive yesterday|past the delivery date|was due yesterday|delivery is delayed|guaranteed delivery was)\b",
    "MARKED_DELIVERED_NOT_RECEIVED": r"\b(?:says delivered but i (?:never|didn't|did not) receive|shows delivered.*not received|marked delivered.*nowhere to be found)\b",
    "CARRIER_FEEDBACK_AND_INSTRUCTIONS": r"\b(?:delivery driver was rude|courier refused to deliver|driver threw package|please leave in safe place|gate code)\b",
    "DAMAGED_OR_DEFECTIVE_ITEM": r"\b(?:arrived (?:broken|damaged|cracked|smashed|leaking)|defective item|packaging was torn and item damaged)\b",
    "WRONG_ITEM_RECEIVED": r"\b(?:sent the wrong item|received completely different product|wrong color received|wrong size delivered)\b",
    "RETURN_PICKUP_ISSUE": r"\b(?:courier did not show up for return|return pickup was not done|nobody came to pick up return|scheduled return pickup)\b",
    "REFUND_STATUS_INQUIRY": r"\b(?:when will my refund be credited|where is my refund|refund status for returned|refund has not arrived in bank)\b",
    "UNRECOGNIZED_OR_DUPLICATE_CHARGE": r"\b(?:charged twice for the same|charged my card twice|double charged|unrecognized charge on my account|unauthorized debit)\b",
    "CANCEL_ORDER_REQUEST": r"\b(?:cancel my order|i want to cancel this order|cancellation request for order|ordered by mistake please cancel)\b",
    "MODIFY_ORDER_DETAILS": r"\b(?:change the delivery address|update my shipping address|change recipient name|change payment method for order)\b",
    "PRIME_MEMBERSHIP_MANAGEMENT": r"\b(?:cancel my prime membership|prime membership renewed without permission|charged for prime subscription|cancel amazon prime)\b",
    "DIGITAL_CONTENT_ACCESS": r"\b(?:cannot download kindle book|prime video streaming error|fire stick won't connect|digital content not appearing)\b",
    "ACCOUNT_LOGIN_ISSUES": r"\b(?:account is locked|can't log into my account|password reset email not received|otp not received|someone hacked my account)\b",
}

for intent, pat in patterns.items():
    matches = dev_df[dev_df["customer_message_clean"].str.contains(pat, case=False, regex=True, na=False)]
    print(f"=== {intent}: {len(matches)} matches ===")
    for _, r in matches.head(3).iterrows():
        print(f"  [{r['case_id']}] (conv {r['conversation_id']}): {r['customer_message_clean']}")
