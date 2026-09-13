"""Find clean, verified non-golden demonstration cases across all 14 intents + controls."""

import json
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent

manifest = json.load(open(ROOT_DIR / "data" / "splits" / "split_manifest.json"))
golden_convs = set(str(c) for c in manifest["golden_conversation_ids"])

df = pd.read_parquet(ROOT_DIR / "data" / "processed" / "amazon_support_cases.parquet")
dev_df = df[~df["conversation_id"].astype(str).isin(golden_convs)].copy()

patterns = {
    "WHERE_IS_MY_ORDER": [
        "track my package",
        "tracking update on my order",
        "status of my parcel",
        "where is my order",
    ],
    "DELIVERY_DELAYED": [
        "package was supposed to arrive yesterday",
        "past the delivery date",
        "delivery is delayed",
    ],
    "MARKED_DELIVERED_NOT_RECEIVED": [
        "says delivered but i did not receive",
        "shows delivered and i have not received",
        "marked as delivered but i have not received",
    ],
    "CARRIER_FEEDBACK_AND_INSTRUCTIONS": [
        "courier refused to deliver",
        "delivery driver threw",
        "safe place",
    ],
    "DAMAGED_OR_DEFECTIVE_ITEM": [
        "arrived broken",
        "arrived cracked",
        "defective item",
        "packaging was damaged",
    ],
    "WRONG_ITEM_RECEIVED": [
        "sent the wrong item",
        "wrong item sent",
        "received completely different product",
    ],
    "RETURN_PICKUP_ISSUE": [
        "return pickup",
        "pick up the return",
        "return label",
    ],
    "REFUND_STATUS_INQUIRY": [
        "where is my refund",
        "when will my refund",
        "refund status",
    ],
    "UNRECOGNIZED_OR_DUPLICATE_CHARGE": [
        "charged twice",
        "double charged",
        "unauthorized charge",
    ],
    "CANCEL_ORDER_REQUEST": [
        "cancel my order",
        "cancel this order",
        "cancellation request",
    ],
    "MODIFY_ORDER_DETAILS": [
        "change the delivery address",
        "change shipping address",
        "change payment method",
    ],
    "PRIME_MEMBERSHIP_MANAGEMENT": [
        "cancel prime",
        "prime membership",
        "prime subscription",
    ],
    "DIGITAL_CONTENT_ACCESS": [
        "kindle book",
        "prime video",
        "fire stick",
    ],
    "ACCOUNT_LOGIN_ISSUES": [
        "account locked",
        "can't log in",
        "password reset",
        "account hacked",
    ],
}

selected = {}
used_convs = set()

for intent, pats in patterns.items():
    selected[intent] = []
    for pat in pats:
        if len(selected[intent]) >= 3:
            break
        matches = dev_df[
            dev_df["customer_message_clean"].str.contains(pat, case=False, na=False)
            & ~dev_df["conversation_id"].astype(str).isin(used_convs)
        ]
        for _, r in matches.iterrows():
            msg = r["customer_message_clean"]
            if 6 <= len(msg.split()) <= 35 and not msg.startswith("http") and "<URL>" not in msg[:20]:
                selected[intent].append({
                    "case_id": r["case_id"],
                    "conversation_id": str(r["conversation_id"]),
                    "msg": msg,
                })
                used_convs.add(str(r["conversation_id"]))
                if len(selected[intent]) >= 3:
                    break

print("Extraction results:")
for intent, items in selected.items():
    print(f"=== {intent}: {len(items)} cases ===")
    for it in items:
        print(f"  [{it['case_id']}] (conv {it['conversation_id']}): {it['msg'][:90]}")

# Save json for inspection
with open(ROOT_DIR / "scratch" / "extracted_demos.json", "w", encoding="utf-8") as f:
    json.dump(selected, f, indent=2)
