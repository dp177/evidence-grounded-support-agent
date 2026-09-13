"""Build Development-Only Few-Shot Demonstration Set for Intent Classification.

Strictly excludes all 200 Golden V1 conversation IDs to guarantee zero leakage.
Outputs: data/development/classification_demos.jsonl
"""

import json
from pathlib import Path
import sys
import pandas as pd
from typing import Any, Dict, List, Set

ROOT_DIR = Path(__file__).resolve().parent.parent

INTENT_TO_AREA = {
    "WHERE_IS_MY_ORDER": "DELIVERY_AND_FULFILLMENT",
    "DELIVERY_DELAYED": "DELIVERY_AND_FULFILLMENT",
    "MARKED_DELIVERED_NOT_RECEIVED": "DELIVERY_AND_FULFILLMENT",
    "CARRIER_FEEDBACK_AND_INSTRUCTIONS": "DELIVERY_AND_FULFILLMENT",
    "DAMAGED_OR_DEFECTIVE_ITEM": "RETURNS_AND_REPLACEMENTS",
    "WRONG_ITEM_RECEIVED": "RETURNS_AND_REPLACEMENTS",
    "RETURN_PICKUP_ISSUE": "RETURNS_AND_REPLACEMENTS",
    "REFUND_STATUS_INQUIRY": "REFUNDS_AND_BILLING",
    "UNRECOGNIZED_OR_DUPLICATE_CHARGE": "REFUNDS_AND_BILLING",
    "CANCEL_ORDER_REQUEST": "ORDER_MANAGEMENT",
    "MODIFY_ORDER_DETAILS": "ORDER_MANAGEMENT",
    "PRIME_MEMBERSHIP_MANAGEMENT": "DIGITAL_SERVICES_AND_PRIME",
    "DIGITAL_CONTENT_ACCESS": "DIGITAL_SERVICES_AND_PRIME",
    "ACCOUNT_LOGIN_ISSUES": "ACCOUNT_ACCESS_AND_SECURITY",
}

LEAF_INTENTS = list(INTENT_TO_AREA.keys())


def load_golden_conversation_ids(
    manifest_path: Path = ROOT_DIR / "data" / "splits" / "split_manifest.json",
    golden_path: Path = ROOT_DIR / "data" / "golden" / "golden_set.jsonl",
) -> Set[str]:
    """Load and combine golden conversation IDs from manifest and golden set."""
    golden_ids = set()
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
            golden_ids.update(str(c) for c in manifest.get("golden_conversation_ids", []))

    if golden_path.exists():
        with open(golden_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    case = json.loads(line)
                    golden_ids.add(str(case.get("conversation_id")))

    return golden_ids


def validate_demo_isolation(
    demos_path: Path | str = ROOT_DIR / "data" / "development" / "classification_demos.jsonl",
    golden_manifest_path: Path | str = ROOT_DIR / "data" / "splits" / "split_manifest.json",
) -> bool:
    """Validate that zero demonstration conversations appear in Golden V1."""
    golden_ids = load_golden_conversation_ids(Path(golden_manifest_path))
    demo_file = Path(demos_path)
    if not demo_file.exists():
        raise FileNotFoundError(f"Demonstration file not found: {demo_file}")

    demo_conv_ids = set()
    total_demos = 0
    with open(demo_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                demo_conv_ids.add(str(rec.get("conversation_id")))
                total_demos += 1

    leakage = demo_conv_ids.intersection(golden_ids)
    if leakage:
        raise ValueError(
            f"CRITICAL LEAKAGE: Found {len(leakage)} demonstration conversation IDs in Golden V1: {leakage}"
        )

    print(f"[PASS] Demo Isolation Validated: {total_demos} demonstrations across {len(demo_conv_ids)} conversations. 0 golden overlaps.")
    return True


def select_best_demos() -> List[Dict[str, Any]]:
    golden_ids = load_golden_conversation_ids()

    # Load non-golden review cases
    review_path = ROOT_DIR / "data" / "processed" / "taxonomy_review_cases.jsonl"
    review_cases = []
    with open(review_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                c = json.loads(line)
                if str(c.get("conversation_id")) not in golden_ids:
                    review_cases.append(c)

    # Load non-golden dev pool for login cases
    df_raw = pd.read_parquet(ROOT_DIR / "data" / "processed" / "amazon_support_cases.parquet")
    dev_df = df_raw[~df_raw["conversation_id"].astype(str).isin(golden_ids)].copy()

    demos = []
    used_convs = set()
    demo_counter = 1

    def add(
        case_id: str,
        conv_id: Any,
        intent: str,
        area: str,
        state: str,
        msg: str,
        ctx: str,
        reason: str,
        status: str = "NORMAL",
        is_multi: bool = False,
        all_intents: List[str] = None,
    ) -> bool:
        nonlocal demo_counter
        cid = str(conv_id)
        if cid in golden_ids or cid in used_convs:
            return False
        
        # Clean text
        clean_msg = msg.replace("\n", " ").strip()
        clean_ctx = ctx.strip() if ctx else f"CUSTOMER: {clean_msg}"

        record = {
            "demo_id": f"demo_{demo_counter:04d}",
            "case_id": str(case_id),
            "conversation_id": cid,
            "classification_status": status,
            "area": area,
            "intent": intent,
            "intents": all_intents if all_intents else ([intent] if status == "NORMAL" else []),
            "primary_intent": intent if status == "NORMAL" else None,
            "is_multi_intent": is_multi,
            "state": state,
            "customer_message": clean_msg,
            "context": clean_ctx,
            "selection_reason": reason,
        }
        demos.append(record)
        used_convs.add(cid)
        demo_counter += 1
        return True

    # Group review cases by proposed intent
    review_by_intent = {}
    for c in review_cases:
        p = c.get("proposed_intent")
        if p == "UNAUTHORIZED_OR_DUPLICATE_CHARGE":
            p = "UNRECOGNIZED_OR_DUPLICATE_CHARGE"
        review_by_intent.setdefault(p, []).append(c)

    # 1. 3 Leaf Intent Demos per intent for 13 intents
    for intent in LEAF_INTENTS:
        if intent == "ACCOUNT_LOGIN_ISSUES":
            continue
        area = INTENT_TO_AREA[intent]
        candidates = review_by_intent.get(intent, [])
        count = 0
        for cand in candidates:
            if count >= 3:
                break
            msg = cand.get("customer_message_clean", "")
            # Filter out noisy or overly short messages
            if 6 <= len(msg.split()) <= 40 and not msg.startswith("http"):
                success = add(
                    case_id=cand.get("case_id"),
                    conv_id=cand.get("conversation_id"),
                    intent=intent,
                    area=area,
                    state="INITIAL_INQUIRY",
                    msg=msg,
                    ctx=cand.get("context_clean", ""),
                    reason=f"Canonical {intent} exemplar from vetted development review cases.",
                )
                if success:
                    count += 1

    # 2. ACCOUNT_LOGIN_ISSUES (3 cases from dev_df)
    login_pats = [
        r"account is locked.*cannot log in",
        r"someone hacked my.*account",
        r"password reset.*not working",
    ]
    login_sub = dev_df[
        dev_df["customer_message_clean"].str.contains(r"\b(?:locked|hacked|password reset|otp|can't log in)\b", case=False, regex=True, na=False)
        & ~dev_df["conversation_id"].astype(str).isin(used_convs)
    ]
    login_count = 0
    for _, r in login_sub.iterrows():
        if login_count >= 3:
            break
        msg = r["customer_message_clean"]
        if 8 <= len(msg.split()) <= 35:
            success = add(
                case_id=r["case_id"],
                conv_id=r["conversation_id"],
                intent="ACCOUNT_LOGIN_ISSUES",
                area="ACCOUNT_ACCESS_AND_SECURITY",
                state="INITIAL_INQUIRY",
                msg=msg,
                ctx=r.get("context_clean", f"CUSTOMER: {msg}"),
                reason="Canonical account access / security issue from development pool.",
            )
            if success:
                login_count += 1

    # 3. Important Boundary Contrasts (8 cases)
    # WISMO vs DELIVERY_DELAYED
    wismo_cand = dev_df[
        dev_df["customer_message_clean"].str.contains(r"due to be delivered today.*update please", case=False, regex=True, na=False)
        & ~dev_df["conversation_id"].astype(str).isin(used_convs)
    ]
    for _, r in wismo_cand.head(1).iterrows():
        add(
            case_id=r["case_id"],
            conv_id=r["conversation_id"],
            intent="WHERE_IS_MY_ORDER",
            area="DELIVERY_AND_FULFILLMENT",
            state="INITIAL_INQUIRY",
            msg=r["customer_message_clean"],
            ctx=r.get("context_clean", ""),
            reason="Boundary contrast: Package is due today (promised window still active); asks for whereabouts, NOT a confirmed delay.",
        )

    delay_cand = dev_df[
        dev_df["customer_message_clean"].str.contains(r"was supposed to arrive yesterday", case=False, regex=True, na=False)
        & ~dev_df["conversation_id"].astype(str).isin(used_convs)
    ]
    for _, r in delay_cand.head(1).iterrows():
        add(
            case_id=r["case_id"],
            conv_id=r["conversation_id"],
            intent="DELIVERY_DELAYED",
            area="DELIVERY_AND_FULFILLMENT",
            state="INITIAL_INQUIRY",
            msg=r["customer_message_clean"],
            ctx=r.get("context_clean", ""),
            reason="Boundary contrast: Promised delivery date elapsed ('yesterday'); confirmed transit delay past expected window.",
        )

    # DELIVERY_DELAYED vs MARKED_DELIVERED_NOT_RECEIVED
    dnr_cand = dev_df[
        dev_df["customer_message_clean"].str.contains(r"shows delivered and i have not received", case=False, regex=True, na=False)
        & ~dev_df["conversation_id"].astype(str).isin(used_convs)
    ]
    for _, r in dnr_cand.head(1).iterrows():
        add(
            case_id=r["case_id"],
            conv_id=r["conversation_id"],
            intent="MARKED_DELIVERED_NOT_RECEIVED",
            area="DELIVERY_AND_FULFILLMENT",
            state="INITIAL_INQUIRY",
            msg=r["customer_message_clean"],
            ctx=r.get("context_clean", ""),
            reason="Boundary contrast: Courier tracking claims delivered, but customer asserts parcel was physically not received.",
        )

    # DAMAGED vs WRONG_ITEM
    wrong_cand = dev_df[
        dev_df["customer_message_clean"].str.contains(r"wrong item sent to me", case=False, regex=True, na=False)
        & ~dev_df["conversation_id"].astype(str).isin(used_convs)
    ]
    for _, r in wrong_cand.head(1).iterrows():
        add(
            case_id=r["case_id"],
            conv_id=r["conversation_id"],
            intent="WRONG_ITEM_RECEIVED",
            area="RETURNS_AND_REPLACEMENTS",
            state="INITIAL_INQUIRY",
            msg=r["customer_message_clean"],
            ctx=r.get("context_clean", ""),
            reason="Boundary contrast: Incorrect item/SKU delivered, distinct from physically broken goods.",
        )

    # CANCEL vs MODIFY
    modify_cand = dev_df[
        dev_df["customer_message_clean"].str.contains(r"shipping my order to the wrong address", case=False, regex=True, na=False)
        & ~dev_df["conversation_id"].astype(str).isin(used_convs)
    ]
    for _, r in modify_cand.head(1).iterrows():
        add(
            case_id=r["case_id"],
            conv_id=r["conversation_id"],
            intent="MODIFY_ORDER_DETAILS",
            area="ORDER_MANAGEMENT",
            state="INITIAL_INQUIRY",
            msg=r["customer_message_clean"],
            ctx=r.get("context_clean", ""),
            reason="Boundary contrast: Request to correct shipping address while keeping the order active.",
        )

    # REFUND vs UNRECOGNIZED_CHARGE
    charge_cand = dev_df[
        dev_df["customer_message_clean"].str.contains(r"took payment twice.*money back", case=False, regex=True, na=False)
        & ~dev_df["conversation_id"].astype(str).isin(used_convs)
    ]
    for _, r in charge_cand.head(1).iterrows():
        add(
            case_id=r["case_id"],
            conv_id=r["conversation_id"],
            intent="UNRECOGNIZED_OR_DUPLICATE_CHARGE",
            area="REFUNDS_AND_BILLING",
            state="INITIAL_INQUIRY",
            msg=r["customer_message_clean"],
            ctx=r.get("context_clean", ""),
            reason="Boundary contrast: Erroneous duplicate bank debit, not inquiry about expected return credit.",
        )

    # PRIME vs DIGITAL_CONTENT
    prime_cand = dev_df[
        dev_df["customer_message_clean"].str.contains(r"trying to purchase amazon prime membership", case=False, regex=True, na=False)
        & ~dev_df["conversation_id"].astype(str).isin(used_convs)
    ]
    for _, r in prime_cand.head(1).iterrows():
        add(
            case_id=r["case_id"],
            conv_id=r["conversation_id"],
            intent="PRIME_MEMBERSHIP_MANAGEMENT",
            area="DIGITAL_SERVICES_AND_PRIME",
            state="INITIAL_INQUIRY",
            msg=r["customer_message_clean"],
            ctx=r.get("context_clean", ""),
            reason="Boundary contrast: Subscription purchase problem, not streaming or ebook media access.",
        )

    # LOGIN vs AMBIGUOUS
    login_boundary = dev_df[
        dev_df["customer_message_clean"].str.contains(r"help me page requires a login which you have blocked", case=False, regex=True, na=False)
        & ~dev_df["conversation_id"].astype(str).isin(used_convs)
    ]
    for _, r in login_boundary.head(1).iterrows():
        add(
            case_id=r["case_id"],
            conv_id=r["conversation_id"],
            intent="ACCOUNT_LOGIN_ISSUES",
            area="ACCOUNT_ACCESS_AND_SECURITY",
            state="INITIAL_INQUIRY",
            msg=r["customer_message_clean"],
            ctx=r.get("context_clean", ""),
            reason="Boundary contrast: Account lockout blocks access to support, clearly mapping to login issues rather than generic ambiguity.",
        )

    # 4. Multi-Intent Demonstrations (3 real cases)
    multi_cases = review_by_intent.get("MULTI_INTENT", [])
    multi_count = 0
    for cand in multi_cases:
        if multi_count >= 3:
            break
        msg = cand.get("customer_message_clean", "")
        if "cancel" in msg.lower() and "refund" in msg.lower():
            all_its = ["CANCEL_ORDER_REQUEST", "REFUND_STATUS_INQUIRY"]
            prim = "REFUND_STATUS_INQUIRY"
        elif "deliver" in msg.lower() and "refund" in msg.lower():
            all_its = ["DELIVERY_DELAYED", "REFUND_STATUS_INQUIRY"]
            prim = "DELIVERY_DELAYED"
        else:
            all_its = ["DELIVERY_DELAYED", "CANCEL_ORDER_REQUEST"]
            prim = "DELIVERY_DELAYED"

        success = add(
            case_id=cand.get("case_id"),
            conv_id=cand.get("conversation_id"),
            intent=prim,
            area=INTENT_TO_AREA.get(prim, "DELIVERY_AND_FULFILLMENT"),
            state="INITIAL_INQUIRY",
            msg=msg,
            ctx=cand.get("context_clean", ""),
            reason="Multi-intent demonstration: inquiry contains two distinct actionable issues.",
            is_multi=True,
            all_intents=all_its,
        )
        if success:
            multi_count += 1

    # 5. Domain Controls: AMBIGUOUS (2 cases) & OUT_OF_SCOPE (2 cases)
    ambig_cases = review_by_intent.get("AMBIGUOUS_INQUIRY", [])
    ambig_count = 0
    for cand in ambig_cases:
        if ambig_count >= 2:
            break
        msg = cand.get("customer_message_clean", "")
        if len(msg.split()) >= 4:
            success = add(
                case_id=cand.get("case_id"),
                conv_id=cand.get("conversation_id"),
                intent="",
                area="",
                state="INITIAL_INQUIRY",
                msg=msg,
                ctx=cand.get("context_clean", ""),
                reason="Ambiguity domain control: customer expresses frustration without actionable problem details.",
                status="AMBIGUOUS",
            )
            if success:
                ambig_count += 1

    oos_cases = review_by_intent.get("OUT_OF_SCOPE", [])
    oos_count = 0
    for cand in oos_cases:
        if oos_count >= 2:
            break
        msg = cand.get("customer_message_clean", "")
        if len(msg.split()) >= 3:
            success = add(
                case_id=cand.get("case_id"),
                conv_id=cand.get("conversation_id"),
                intent="",
                area="",
                state="INITIAL_INQUIRY",
                msg=msg,
                ctx=cand.get("context_clean", ""),
                reason="Out-of-scope domain control: social banter or non-retail support request.",
                status="OUT_OF_SCOPE",
            )
            if success:
                oos_count += 1

    return demos


def main() -> None:
    print("=" * 60)
    print("BUILDING CLASSIFICATION DEMONSTRATIONS (DEVELOPMENT ONLY)")
    print("=" * 60)

    out_dir = ROOT_DIR / "data" / "development"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "classification_demos.jsonl"

    demos = select_best_demos()
    print(f"Constructed {len(demos)} demonstration records.")

    with open(out_file, "w", encoding="utf-8") as f:
        for d in demos:
            f.write(json.dumps(d) + "\n")

    print(f"Saved demonstrations to: {out_file}")
    validate_demo_isolation(out_file)
    print("=" * 60)


if __name__ == "__main__":
    main()
