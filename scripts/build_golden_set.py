"""Build the locked Golden Evaluation Set (200 cases) for AmazonHelp support agent.

Enforces:
- Conversation-level isolation (no duplicate conversation_ids, complete disjointness from dev set)
- Strict compliance with configs/taxonomy_v1.yaml (14 frozen leaf intents)
- Target composition:
    100 common normal cases
    25 rare / underrepresented cases
    20 boundary cases
    20 multi-intent cases
    15 ambiguous cases
    10 high-risk / escalation cases
    10 out-of-scope cases
    Total: 200 cases
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import sys
import pandas as pd
import pyarrow.parquet as pq
import yaml

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

GOLDEN_DIR = Path("data/golden")
SPLITS_DIR = Path("data/splits")
GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
SPLITS_DIR.mkdir(parents=True, exist_ok=True)

# 1. Load taxonomy
with open("configs/taxonomy_v1.yaml", encoding="utf-8") as f:
    tax = yaml.safe_load(f)

INTENT_TO_AREA = {}
for area, data in tax["areas"].items():
    for intent in data["intents"]:
        INTENT_TO_AREA[intent] = area

FROZEN_INTENTS = set(INTENT_TO_AREA.keys())

# Normalization mapping for historical labels in review files
NORMALIZATION = {
    "UNAUTHORIZED_OR_DUPLICATE_CHARGE": "UNRECOGNIZED_OR_DUPLICATE_CHARGE",
    "ACCOUNT_LOGIN_OR_OTP": "ACCOUNT_LOGIN_ISSUES",
    "DUPLICATE_CHARGE": "UNRECOGNIZED_OR_DUPLICATE_CHARGE",
    "CHANGE_DELIVERY_ADDRESS": "MODIFY_ORDER_DETAILS",
}

# 2. Load canonical metadata for customer_id mapping
print("Loading canonical dataset metadata...")
table = pq.read_table("data/processed/amazon_support_cases.parquet", columns=["case_id", "conversation_id", "customer_author_id", "thread_length", "customer_message_clean", "context_clean", "language"])
df_canonical = table.to_pandas()
case_meta = {}
for _, row in df_canonical.iterrows():
    case_meta[row["case_id"]] = {
        "customer_id": str(row["customer_author_id"]),
        "conversation_id": str(row["conversation_id"]),
        "thread_length": int(row["thread_length"]),
        "customer_message": str(row["customer_message_clean"]),
        "context": str(row["context_clean"]) if str(row["context_clean"]).strip() else f"CUSTOMER: {row['customer_message_clean']}",
        "language": str(row["language"]),
    }
all_canonical_conv_ids = set(str(cid) for cid in df_canonical["conversation_id"].unique())
print(f"Loaded {len(case_meta)} cases across {len(all_canonical_conv_ids)} canonical conversations.")

# 3. Load review cases and boundary cases
with open("data/processed/taxonomy_review_cases.jsonl", encoding="utf-8") as f:
    review_cases = [json.loads(line) for line in f]

with open("data/processed/taxonomy_boundaries.jsonl", encoding="utf-8") as f:
    boundary_records = [json.loads(line) for line in f]

# Group review cases
cases_by_cat = defaultdict(list)
for c in review_cases:
    prop = c.get("proposed_intent")
    norm_intent = NORMALIZATION.get(prop, prop)
    c["normalized_intent"] = norm_intent
    cases_by_cat[norm_intent].append(c)

used_conv_ids = set()
used_case_ids = set()

golden_cases = []

def add_case(record: dict) -> bool:
    cid = str(record["conversation_id"])
    cs_id = record["case_id"]
    if cid in used_conv_ids or cs_id in used_case_ids:
        return False
    used_conv_ids.add(cid)
    used_case_ids.add(cs_id)
    golden_cases.append(record)
    return True

# -------------------------------------------------------------
# Category A: 10 HIGH-RISK / ESCALATION CANDIDATES
# -------------------------------------------------------------
print("Selecting 10 HIGH_RISK cases...")
high_risk_reasons = {
    "amazon_case_0042701": (["ACCOUNT_LOGIN_ISSUES"], "SECURITY_LOCKOUT", "Account flagged as suspicious and locked; password reset loop."),
    "amazon_case_0058654": (["ACCOUNT_LOGIN_ISSUES"], "ACCOUNT_SECURITY_COMPROMISE", "Unauthorized credential modification (email/password changed)."),
    "amazon_case_0063275": (["ACCOUNT_LOGIN_ISSUES"], "REPEATED_FAILED_SUPPORT_ATTEMPTS", "Customer unable to access account, contacted support >5 times without luck."),
    "amazon_case_0027359": (["ACCOUNT_LOGIN_ISSUES"], "ACCOUNT_SECURITY_COMPROMISE", "Account hacked, linked email changed without authorization."),
    "amazon_case_0163147": (["ACCOUNT_LOGIN_ISSUES"], "ACCOUNT_SECURITY_COMPROMISE", "Account hacked requiring urgent security team escalation."),
    "amazon_case_0057021": (["ACCOUNT_LOGIN_ISSUES"], "ACCOUNT_SECURITY_COMPROMISE", "Account hijacked and locked out, requiring identity verification."),
    "amazon_case_0048011": (["ACCOUNT_LOGIN_ISSUES"], "SECURITY_LOCKOUT", "Account locked preventing sign-in."),
    "amazon_case_0073376": (["ACCOUNT_LOGIN_ISSUES"], "REPEATED_FAILED_SUPPORT_ATTEMPTS", "Account locked since October; sent 4 faxes and 12 emails without resolution."),
    "amazon_case_0055972": (["CARRIER_FEEDBACK_AND_INSTRUCTIONS"], "CARRIER_MISCONDUCT_SEVERE", "Delivery driver refused delivery to customer address with abusive conduct."),
    "amazon_case_0132156": (["CARRIER_FEEDBACK_AND_INSTRUCTIONS"], "CARRIER_MISCONDUCT_SEVERE", "Authorized delivery agent refused to deliver parcel to residential address."),
}

for c in review_cases:
    if len([x for x in golden_cases if x.get("sampling_category") == "HIGH_RISK"]) >= 10:
        break
    cs_id = c["case_id"]
    if cs_id in high_risk_reasons:
        intents, esc_reason, notes = high_risk_reasons[cs_id]
        meta = case_meta.get(cs_id, {})
        add_case({
            "case_id": cs_id,
            "conversation_id": str(c["conversation_id"]),
            "customer_id": meta.get("customer_id", "unknown"),
            "context": meta.get("context", c.get("context_clean", "")),
            "customer_message": meta.get("customer_message", c.get("customer_message_clean", "")),
            "areas": [INTENT_TO_AREA[i] for i in intents],
            "intents": intents,
            "primary_intent": intents[0],
            "is_multi_intent": len(intents) > 1,
            "classification_status": "NORMAL",
            "states": ["WAITING_WINDOW_EXCEEDED" if "REPEATED" in esc_reason or "SLA" in esc_reason else "INITIAL_INQUIRY"],
            "should_escalate": True,
            "escalation_reason": [esc_reason],
            "difficulty": "HARD",
            "sampling_category": "HIGH_RISK",
            "annotator_notes": notes,
        })

print(f"High risk selected: {len([x for x in golden_cases if x['sampling_category'] == 'HIGH_RISK'])}")

# -------------------------------------------------------------
# Category B: 15 AMBIGUOUS INQUIRIES
# -------------------------------------------------------------
print("Selecting 15 AMBIGUOUS cases...")
ambiguous_pool = cases_by_cat.get("AMBIGUOUS_INQUIRY", [])
for c in ambiguous_pool:
    if len([x for x in golden_cases if x.get("sampling_category") == "AMBIGUOUS"]) >= 15:
        break
    cs_id = c["case_id"]
    meta = case_meta.get(cs_id, {})
    add_case({
        "case_id": cs_id,
        "conversation_id": str(c["conversation_id"]),
        "customer_id": meta.get("customer_id", "unknown"),
        "context": meta.get("context", c.get("context_clean", "")),
        "customer_message": meta.get("customer_message", c.get("customer_message_clean", "")),
        "areas": [],
        "intents": [],
        "primary_intent": None,
        "is_multi_intent": False,
        "classification_status": "AMBIGUOUS",
        "states": ["INITIAL_INQUIRY"],
        "should_escalate": False,
        "escalation_reason": [],
        "difficulty": "MEDIUM",
        "sampling_category": "AMBIGUOUS",
        "annotator_notes": "Underspecified inquiry lacking order details or actionable problem statement; requires clarifying turn.",
    })
print(f"Ambiguous selected: {len([x for x in golden_cases if x['sampling_category'] == 'AMBIGUOUS'])}")

# -------------------------------------------------------------
# Category C: 10 OUT-OF-SCOPE CASES
# -------------------------------------------------------------
print("Selecting 10 OUT_OF_SCOPE cases...")
oos_pool = cases_by_cat.get("OUT_OF_SCOPE", [])
for c in oos_pool:
    if len([x for x in golden_cases if x.get("sampling_category") == "OUT_OF_SCOPE"]) >= 10:
        break
    cs_id = c["case_id"]
    meta = case_meta.get(cs_id, {})
    add_case({
        "case_id": cs_id,
        "conversation_id": str(c["conversation_id"]),
        "customer_id": meta.get("customer_id", "unknown"),
        "context": meta.get("context", c.get("context_clean", "")),
        "customer_message": meta.get("customer_message", c.get("customer_message_clean", "")),
        "areas": [],
        "intents": [],
        "primary_intent": None,
        "is_multi_intent": False,
        "classification_status": "OUT_OF_SCOPE",
        "states": ["INITIAL_INQUIRY"],
        "should_escalate": False,
        "escalation_reason": [],
        "difficulty": "EASY",
        "sampling_category": "OUT_OF_SCOPE",
        "annotator_notes": "Non-support dialogue, marketing comment, or general banter filtered out by domain gate.",
    })
print(f"Out of scope selected: {len([x for x in golden_cases if x['sampling_category'] == 'OUT_OF_SCOPE'])}")

# -------------------------------------------------------------
# Category D: 20 MULTI-INTENT CASES
# -------------------------------------------------------------
print("Selecting 20 MULTI_INTENT cases...")
# Concrete human annotations for multi-intent cases from the pool
multi_intent_annotations = {
    "amazon_case_0015921": (["DELIVERY_DELAYED", "CANCEL_ORDER_REQUEST", "REFUND_STATUS_INQUIRY"], "DELIVERY_DELAYED", "Order delayed; requesting cancel and refund inquiry."),
    "amazon_case_0051568": (["UNRECOGNIZED_OR_DUPLICATE_CHARGE", "CANCEL_ORDER_REQUEST"], "UNRECOGNIZED_OR_DUPLICATE_CHARGE", "Duplicate charge pending and customer asking to cancel."),
    "amazon_case_0080300": (["PRIME_MEMBERSHIP_MANAGEMENT", "REFUND_STATUS_INQUIRY"], "PRIME_MEMBERSHIP_MANAGEMENT", "Requesting early Prime cancellation and partial refund."),
    "amazon_case_0110457": (["PRIME_MEMBERSHIP_MANAGEMENT", "UNRECOGNIZED_OR_DUPLICATE_CHARGE"], "PRIME_MEMBERSHIP_MANAGEMENT", "Meant to cancel Prime, charged auto-renewal fee."),
    "amazon_case_0151424": (["WRONG_ITEM_RECEIVED", "RETURN_PICKUP_ISSUE"], "WRONG_ITEM_RECEIVED", "Wrong item sent and no update on return pickup or replacement."),
    "amazon_case_0001590": (["DAMAGED_OR_DEFECTIVE_ITEM", "RETURN_PICKUP_ISSUE"], "DAMAGED_OR_DEFECTIVE_ITEM", "Defective product replacement ordered but courier missed pickup."),
    "amazon_case_0052083": (["PRIME_MEMBERSHIP_MANAGEMENT", "ACCOUNT_LOGIN_ISSUES"], "ACCOUNT_LOGIN_ISSUES", "Charged for Prime but unable to access account to manage subscription."),
    "amazon_case_0015056": (["WHERE_IS_MY_ORDER", "CANCEL_ORDER_REQUEST"], "CANCEL_ORDER_REQUEST", "Order undelivered and canceled, follow-up on fulfillment status."),
    "amazon_case_0050697": (["CANCEL_ORDER_REQUEST", "REFUND_STATUS_INQUIRY"], "CANCEL_ORDER_REQUEST", "Canceling replacement exchange and inquiring about refund."),
    "amazon_case_0025122": (["DELIVERY_DELAYED", "PRIME_MEMBERSHIP_MANAGEMENT"], "DELIVERY_DELAYED", "Prime next-day delivery delayed by several days."),
    "amazon_case_0034643": (["CANCEL_ORDER_REQUEST", "UNRECOGNIZED_OR_DUPLICATE_CHARGE"], "CANCEL_ORDER_REQUEST", "Card debited after order was already canceled."),
    "amazon_case_0036794": (["DELIVERY_DELAYED", "MODIFY_ORDER_DETAILS"], "DELIVERY_DELAYED", "Delayed shipment and customer asking to change delivery day."),
    "amazon_case_0098653": (["WHERE_IS_MY_ORDER", "MODIFY_ORDER_DETAILS"], "WHERE_IS_MY_ORDER", "Inquiring about order status and asking to switch payment card."),
    "amazon_case_0112122": (["DAMAGED_OR_DEFECTIVE_ITEM", "REFUND_STATUS_INQUIRY"], "DAMAGED_OR_DEFECTIVE_ITEM", "Damaged leaking shampoo bottle and asking for refund timeline."),
    "amazon_case_0109139": (["RETURN_PICKUP_ISSUE", "REFUND_STATUS_INQUIRY"], "RETURN_PICKUP_ISSUE", "Drop-off barcode failed and inquiring when refund will credit."),
    "amazon_case_0094446": (["REFUND_STATUS_INQUIRY", "CANCEL_ORDER_REQUEST"], "REFUND_STATUS_INQUIRY", "Canceled order inquiring about Amazon gift card refund speed."),
    "amazon_case_0086351": (["DIGITAL_CONTENT_ACCESS", "PRIME_MEMBERSHIP_MANAGEMENT"], "DIGITAL_CONTENT_ACCESS", "Echo Dot failing to link to Amazon Prime Music account."),
    "amazon_case_0024894": (["DIGITAL_CONTENT_ACCESS", "PRIME_MEMBERSHIP_MANAGEMENT"], "DIGITAL_CONTENT_ACCESS", "Prime Video app error on Smart TV during active subscription."),
    "amazon_case_0131432": (["DIGITAL_CONTENT_ACCESS", "REFUND_STATUS_INQUIRY"], "DIGITAL_CONTENT_ACCESS", "Purchased Kindle ebook not downloading and requesting refund."),
    "amazon_case_0132871": (["RETURN_PICKUP_ISSUE", "REFUND_STATUS_INQUIRY"], "RETURN_PICKUP_ISSUE", "Scheduled pickup missed yesterday, asking about refund issuance."),
}

for cs_id, (intents, primary, notes) in multi_intent_annotations.items():
    if len([x for x in golden_cases if x.get("sampling_category") == "MULTI_INTENT"]) >= 20:
        break
    meta = case_meta.get(cs_id)
    if not meta:
        continue
    add_case({
        "case_id": cs_id,
        "conversation_id": meta["conversation_id"],
        "customer_id": meta["customer_id"],
        "context": meta["context"],
        "customer_message": meta["customer_message"],
        "areas": list(set(INTENT_TO_AREA[i] for i in intents)),
        "intents": intents,
        "primary_intent": primary,
        "is_multi_intent": True,
        "classification_status": "NORMAL",
        "states": ["INITIAL_INQUIRY"],
        "should_escalate": False,
        "escalation_reason": [],
        "difficulty": "HARD",
        "sampling_category": "MULTI_INTENT",
        "annotator_notes": notes,
    })

print(f"Multi-intent selected: {len([x for x in golden_cases if x['sampling_category'] == 'MULTI_INTENT'])}")

# -------------------------------------------------------------
# Category E: 20 BOUNDARY CASES
# -------------------------------------------------------------
print("Selecting 20 BOUNDARY cases...")
boundary_targets = [
    # pair, intent, primary, notes
    ("amazon_case_0110234", "DELIVERY_DELAYED", "Near delivery estimate, customer reporting delay"),
    ("amazon_case_0048826", "WHERE_IS_MY_ORDER", "Order in dispatch preparation, status check"),
    ("amazon_case_0152499", "WHERE_IS_MY_ORDER", "Order status check asking for delivery date"),
    ("amazon_case_0005594", "MARKED_DELIVERED_NOT_RECEIVED", "Marked delivered but physical item missing"),
    ("amazon_case_0164697", "MARKED_DELIVERED_NOT_RECEIVED", "App alert says delivered to door, customer present no package"),
    ("amazon_case_0015604", "MARKED_DELIVERED_NOT_RECEIVED", "Says delivered front porch, porch empty"),
    ("amazon_case_0042191", "CARRIER_FEEDBACK_AND_INSTRUCTIONS", "Package left in rain by courier driver"),
    ("amazon_case_0067847", "CARRIER_FEEDBACK_AND_INSTRUCTIONS", "Customs clearance KYC document upload request"),
    ("amazon_case_0112122", "DAMAGED_OR_DEFECTIVE_ITEM", "Crushed package and leaking contents"),
    ("amazon_case_0036089", "MARKED_DELIVERED_NOT_RECEIVED", "Tracking says delivered without delivering"),
    ("amazon_case_0017954", "ACCOUNT_LOGIN_ISSUES", "OTP verification SMS code never arrives"),
    ("amazon_case_0000162", "ACCOUNT_LOGIN_ISSUES", "Cannot log into Prime or Amazon account credentials fail"),
    ("amazon_case_0000279", "ACCOUNT_LOGIN_ISSUES", "Forgot account password, requesting reset assistance"),
    ("amazon_case_0115845", "ACCOUNT_LOGIN_ISSUES", "App rejecting password on new device setup"),
    ("amazon_case_0108266", "ACCOUNT_LOGIN_ISSUES", "Unable to log in to account general access barrier"),
    ("amazon_case_0142156", "ACCOUNT_LOGIN_ISSUES", "Cannot login even with correct password"),
    ("amazon_case_0106491", "WRONG_ITEM_RECEIVED", "Repeatedly received wrong product SKU"),
    ("amazon_case_0109139", "RETURN_PICKUP_ISSUE", "Return drop-off barcode scanning error at post office"),
    ("amazon_case_0042701", "ACCOUNT_LOGIN_ISSUES", "Account flagged security lock, login barrier"),
    ("amazon_case_0019408", "CARRIER_FEEDBACK_AND_INSTRUCTIONS", "Driver threw package over fence instead of opening gate"),
]

for cs_id, intent, notes in boundary_targets:
    if len([x for x in golden_cases if x.get("sampling_category") == "BOUNDARY"]) >= 20:
        break
    meta = case_meta.get(cs_id)
    if not meta:
        continue
    add_case({
        "case_id": cs_id,
        "conversation_id": meta["conversation_id"],
        "customer_id": meta["customer_id"],
        "context": meta["context"],
        "customer_message": meta["customer_message"],
        "areas": [INTENT_TO_AREA[intent]],
        "intents": [intent],
        "primary_intent": intent,
        "is_multi_intent": False,
        "classification_status": "NORMAL",
        "states": ["INITIAL_INQUIRY"],
        "should_escalate": False,
        "escalation_reason": [],
        "difficulty": "HARD",
        "sampling_category": "BOUNDARY",
        "annotator_notes": f"Boundary evaluation case: {notes}",
    })

# If boundary count < 20 due to conv collision, grab extra boundary cases from boundary records
if len([x for x in golden_cases if x.get("sampling_category") == "BOUNDARY"]) < 20:
    for b in boundary_records:
        if len([x for x in golden_cases if x.get("sampling_category") == "BOUNDARY"]) >= 20:
            break
        for ex in b.get("example_cases", []):
            if len([x for x in golden_cases if x.get("sampling_category") == "BOUNDARY"]) >= 20:
                break
            cs_id = ex["case_id"]
            meta = case_meta.get(cs_id)
            if not meta:
                continue
            intent = b["intent_a"]
            norm_intent = NORMALIZATION.get(intent, intent)
            if norm_intent not in FROZEN_INTENTS:
                continue
            add_case({
                "case_id": cs_id,
                "conversation_id": meta["conversation_id"],
                "customer_id": meta["customer_id"],
                "context": meta["context"],
                "customer_message": meta["customer_message"],
                "areas": [INTENT_TO_AREA[norm_intent]],
                "intents": [norm_intent],
                "primary_intent": norm_intent,
                "is_multi_intent": False,
                "classification_status": "NORMAL",
                "states": ["INITIAL_INQUIRY"],
                "should_escalate": False,
                "escalation_reason": [],
                "difficulty": "HARD",
                "sampling_category": "BOUNDARY",
                "annotator_notes": f"Boundary pair {b.get('intent_a')} vs {b.get('intent_b')}",
            })

print(f"Boundary selected: {len([x for x in golden_cases if x['sampling_category'] == 'BOUNDARY'])}")

# -------------------------------------------------------------
# Category F: 25 RARE / UNDERREPRESENTED INTENT CASES
# -------------------------------------------------------------
print("Selecting 25 RARE intent cases (5 per intent for 5 specialized intents)...")
rare_intents = [
    "CARRIER_FEEDBACK_AND_INSTRUCTIONS",
    "RETURN_PICKUP_ISSUE",
    "MODIFY_ORDER_DETAILS",
    "DIGITAL_CONTENT_ACCESS",
    "ACCOUNT_LOGIN_ISSUES",
]

for r_intent in rare_intents:
    pool = cases_by_cat.get(r_intent, [])
    added = 0
    for c in pool:
        if added >= 5:
            break
        cs_id = c["case_id"]
        meta = case_meta.get(cs_id)
        if not meta:
            continue
        success = add_case({
            "case_id": cs_id,
            "conversation_id": meta["conversation_id"],
            "customer_id": meta["customer_id"],
            "context": meta["context"],
            "customer_message": meta["customer_message"],
            "areas": [INTENT_TO_AREA[r_intent]],
            "intents": [r_intent],
            "primary_intent": r_intent,
            "is_multi_intent": False,
            "classification_status": "NORMAL",
            "states": ["INITIAL_INQUIRY"],
            "should_escalate": False,
            "escalation_reason": [],
            "difficulty": "MEDIUM",
            "sampling_category": "RARE",
            "annotator_notes": f"Underrepresented specialized intent: {r_intent}",
        })
        if success:
            added += 1

print(f"Rare selected: {len([x for x in golden_cases if x['sampling_category'] == 'RARE'])}")

# -------------------------------------------------------------
# Category G: 100 COMMON NORMAL CASES
# -------------------------------------------------------------
print("Selecting 100 COMMON normal cases...")
# Target 7 cases for each of the 14 intents (14 * 7 = 98) + 2 extra for highest volume = 100
common_counts = defaultdict(int)
all_14_intents = sorted(list(FROZEN_INTENTS))

# First pass: try 7 per intent
for intent in all_14_intents:
    target_count = 7
    pool = cases_by_cat.get(intent, [])
    for c in pool:
        if common_counts[intent] >= target_count:
            break
        cs_id = c["case_id"]
        meta = case_meta.get(cs_id)
        if not meta:
            continue
        success = add_case({
            "case_id": cs_id,
            "conversation_id": meta["conversation_id"],
            "customer_id": meta["customer_id"],
            "context": meta["context"],
            "customer_message": meta["customer_message"],
            "areas": [INTENT_TO_AREA[intent]],
            "intents": [intent],
            "primary_intent": intent,
            "is_multi_intent": False,
            "classification_status": "NORMAL",
            "states": ["TRACKING_ALREADY_CHECKED" if "check" in meta["customer_message"].lower() and "track" in meta["customer_message"].lower() else "INITIAL_INQUIRY"],
            "should_escalate": False,
            "escalation_reason": [],
            "difficulty": "EASY" if common_counts[intent] < 4 else "MEDIUM",
            "sampling_category": "COMMON",
            "annotator_notes": f"Standard representative example for {intent}.",
        })
        if success:
            common_counts[intent] += 1

# Top up to exactly 100 common cases using remaining cases from pool
current_common = len([x for x in golden_cases if x["sampling_category"] == "COMMON"])
if current_common < 100:
    needed = 100 - current_common
    print(f"Topping up {needed} common cases...")
    for intent in ["WHERE_IS_MY_ORDER", "DELIVERY_DELAYED", "REFUND_STATUS_INQUIRY", "CANCEL_ORDER_REQUEST", "PRIME_MEMBERSHIP_MANAGEMENT"]:
        if len([x for x in golden_cases if x["sampling_category"] == "COMMON"]) >= 100:
            break
        pool = cases_by_cat.get(intent, [])
        for c in pool:
            if len([x for x in golden_cases if x["sampling_category"] == "COMMON"]) >= 100:
                break
            cs_id = c["case_id"]
            meta = case_meta.get(cs_id)
            if not meta:
                continue
            success = add_case({
                "case_id": cs_id,
                "conversation_id": meta["conversation_id"],
                "customer_id": meta["customer_id"],
                "context": meta["context"],
                "customer_message": meta["customer_message"],
                "areas": [INTENT_TO_AREA[intent]],
                "intents": [intent],
                "primary_intent": intent,
                "is_multi_intent": False,
                "classification_status": "NORMAL",
                "states": ["INITIAL_INQUIRY"],
                "should_escalate": False,
                "escalation_reason": [],
                "difficulty": "MEDIUM",
                "sampling_category": "COMMON",
                "annotator_notes": f"Supplemental common representative case for {intent}.",
            })

print(f"Total golden cases gathered: {len(golden_cases)}")
counts_by_category = defaultdict(int)
for g in golden_cases:
    counts_by_category[g["sampling_category"]] += 1
print("Counts by category:")
for cat, cnt in sorted(counts_by_category.items()):
    print(f"  {cat}: {cnt}")

assert len(golden_cases) == 200, f"Expected 200 cases, got {len(golden_cases)}"
assert len(used_conv_ids) == 200, f"Expected 200 unique conversations, got {len(used_conv_ids)}"
assert len(used_case_ids) == 200, f"Expected 200 unique cases, got {len(used_case_ids)}"

# Assign sequential gold_id
for idx, g in enumerate(golden_cases, 1):
    g["gold_id"] = f"gold_{idx:04d}"

# Re-order dict keys cleanly
ordered_golden = []
field_order = [
    "gold_id", "case_id", "conversation_id", "customer_id", "context", "customer_message",
    "areas", "intents", "primary_intent", "is_multi_intent", "classification_status",
    "states", "should_escalate", "escalation_reason", "difficulty", "sampling_category", "annotator_notes"
]
for g in golden_cases:
    ordered_golden.append({k: g.get(k) for k in field_order})

# 4. Save data/golden/golden_set.jsonl
golden_jsonl_path = GOLDEN_DIR / "golden_set.jsonl"
with open(golden_jsonl_path, "w", encoding="utf-8") as f:
    for g in ordered_golden:
        f.write(json.dumps(g, ensure_ascii=False) + "\n")
print(f"Saved {golden_jsonl_path} ({golden_jsonl_path.stat().st_size:,} bytes).")

# 5. Save data/golden/annotation_template.csv
csv_rows = []
for g in ordered_golden:
    csv_rows.append({
        "gold_id": g["gold_id"],
        "case_id": g["case_id"],
        "conversation_id": g["conversation_id"],
        "customer_id": g["customer_id"],
        "customer_message": g["customer_message"],
        "classification_status": g["classification_status"],
        "is_multi_intent": g["is_multi_intent"],
        "areas": "|".join(g["areas"]),
        "intents": "|".join(g["intents"]),
        "primary_intent": g["primary_intent"] or "",
        "states": "|".join(g["states"]),
        "should_escalate": g["should_escalate"],
        "escalation_reason": "|".join(g["escalation_reason"]),
        "difficulty": g["difficulty"],
        "sampling_category": g["sampling_category"],
        "annotator_notes": g["annotator_notes"],
    })
df_csv = pd.DataFrame(csv_rows)
csv_path = GOLDEN_DIR / "annotation_template.csv"
df_csv.to_csv(csv_path, index=False, encoding="utf-8")
print(f"Saved {csv_path} ({csv_path.stat().st_size:,} bytes).")

# 6. Build and Save data/splits/split_manifest.json
dev_conv_ids = sorted(list(all_canonical_conv_ids - used_conv_ids))
golden_conv_ids_sorted = sorted(list(used_conv_ids))

# Verify disjointness
assert set(golden_conv_ids_sorted).isdisjoint(set(dev_conv_ids)), "Leakage detected between golden and dev sets!"

manifest = {
    "taxonomy_version": "1.0",
    "golden_set_version": "golden_v1",
    "creation_timestamp": datetime.now(timezone.utc).isoformat(),
    "random_seed": RANDOM_SEED,
    "sampling_strategy": "stratified_conversation_isolation",
    "total_canonical_conversations": len(all_canonical_conv_ids),
    "total_golden_conversations": len(golden_conv_ids_sorted),
    "total_development_conversations": len(dev_conv_ids),
    "conversation_leakage_detected": False,
    "golden_conversation_ids": golden_conv_ids_sorted,
    "development_conversation_id_count": len(dev_conv_ids),
    "notes": "Strict conversation-level isolation. Golden conversations are barred from training and RAG retrieval corpus."
}

manifest_path = SPLITS_DIR / "split_manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)
print(f"Saved {manifest_path} ({manifest_path.stat().st_size:,} bytes).")
