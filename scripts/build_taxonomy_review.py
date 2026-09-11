#!/usr/bin/env python3
"""
Taxonomy Review and Boundary Dataset Builder for AmazonHelp Support Agent.

Extracts representative review cases across all 14 candidate leaf intents,
plus ambiguous, multi-intent, and out-of-scope categories. Also discovers
concrete boundary cases between highly confusable intent pairs.

Outputs:
- data/processed/taxonomy_review_cases.jsonl
- data/processed/taxonomy_boundaries.jsonl

Usage:
    python scripts/build_taxonomy_review.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import numpy as np
import pandas as pd

# Fix console encoding on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DISCOVERY_DATA = PROJECT_ROOT / "data" / "processed" / "intent_discovery_cases.parquet"
DEFAULT_EMBEDDINGS = PROJECT_ROOT / "generated" / "embeddings" / "intent_discovery_minilm.npy"
OUTPUT_REVIEW_CASES = PROJECT_ROOT / "data" / "processed" / "taxonomy_review_cases.jsonl"
OUTPUT_BOUNDARIES = PROJECT_ROOT / "data" / "processed" / "taxonomy_boundaries.jsonl"

# 14 Candidate Leaf Intents with prototypical query anchors & keyword filters
INTENT_CONFIGS: Dict[str, Dict[str, Any]] = {
    "WHERE_IS_MY_ORDER": {
        "cluster": "DELIVERY_AND_FULFILLMENT",
        "prototype": "Where is my order? Can I get a tracking update on my shipment status?",
        "keywords": [r"where is", r"tracking", r"track my", r"out for delivery", r"status of my order", r"when will it arrive", r"where's my", r"update on"],
        "quota": 25,
    },
    "DELIVERY_DELAYED": {
        "cluster": "DELIVERY_AND_FULFILLMENT",
        "prototype": "My package was supposed to arrive yesterday and is delayed. Still waiting for delivery.",
        "keywords": [r"delay", r"late", r"supposed to arrive", r"still waiting", r"past due", r"not yet arrived", r"overdue", r"expected by", r"hasn't arrived"],
        "quota": 25,
    },
    "MARKED_DELIVERED_NOT_RECEIVED": {
        "cluster": "DELIVERY_AND_FULFILLMENT",
        "prototype": "The app says my package was delivered today but I never received it and it's missing.",
        "keywords": [r"marked.*delivered", r"says.*delivered", r"shows.*delivered", r"stated.*delivered", r"not received.*delivered", r"delivered.*haven't received", r"delivered.*not here"],
        "quota": 25,
    },
    "CARRIER_FEEDBACK_AND_INSTRUCTIONS": {
        "cluster": "DELIVERY_AND_FULFILLMENT",
        "prototype": "The delivery driver left my parcel in the rain and was rude. Courier did not follow delivery instructions.",
        "keywords": [r"driver", r"courier", r"carrier", r"left.*rain", r"left.*bin", r"safe place", r"customs", r"hermes", r"usps", r"royal mail", r"gate code", r"porch"],
        "quota": 25,
    },
    "DAMAGED_OR_DEFECTIVE_ITEM": {
        "cluster": "RETURNS_AND_REPLACEMENTS",
        "prototype": "The item I received is broken, cracked, defective, and not working properly.",
        "keywords": [r"damaged", r"broken", r"cracked", r"shattered", r"defective", r"faulty", r"torn", r"not working", r"leaking", r"poor quality", r"scratched"],
        "quota": 25,
    },
    "WRONG_ITEM_RECEIVED": {
        "cluster": "RETURNS_AND_REPLACEMENTS",
        "prototype": "I opened the box and received the wrong item. This is completely different from what I ordered.",
        "keywords": [r"wrong item", r"wrong product", r"different item", r"ordered.*received", r"sent me the wrong", r"incorrect item", r"wrong size", r"wrong color", r"not what i ordered", r"received a different"],
        "quota": 25,
    },
    "RETURN_PICKUP_ISSUE": {
        "cluster": "RETURNS_AND_REPLACEMENTS",
        "prototype": "I requested a return pickup but the courier never showed up to collect the package.",
        "keywords": [r"pickup", r"pick up", r"return.*collect", r"pickup.*courier", r"return label", r"return.*arrived to pick", r"drop off", r"return request"],
        "quota": 25,
    },
    "REFUND_STATUS_INQUIRY": {
        "cluster": "REFUNDS_AND_BILLING",
        "prototype": "I returned my order last week. Where is my refund and when will the money be credited to my bank?",
        "keywords": [r"where is.*refund", r"when.*refund", r"refund.*credited", r"refund not received", r"refund.*initiated", r"money back", r"refund processed", r"get my refund"],
        "quota": 25,
    },
    "UNAUTHORIZED_OR_DUPLICATE_CHARGE": {
        "cluster": "REFUNDS_AND_BILLING",
        "prototype": "I was charged twice on my credit card for a single order. Unrecognized transaction on my bank account.",
        "keywords": [r"charged twice", r"double charged", r"unauthorized charge", r"extra charge", r"deducted twice", r"overcharged", r"why.*charged", r"charged my card", r"charged me for", r"billing error"],
        "quota": 25,
    },
    "CANCEL_ORDER_REQUEST": {
        "cluster": "ORDER_MANAGEMENT",
        "prototype": "I ordered by mistake and want to cancel this order immediately before it ships.",
        "keywords": [r"cancel.*order", r"cancellation", r"cancel this", r"stop shipment", r"ordered by mistake", r"cancel my item", r"cancel it"],
        "quota": 25,
    },
    "MODIFY_ORDER_DETAILS": {
        "cluster": "ORDER_MANAGEMENT",
        "prototype": "Can I change the delivery address or payment method on my existing order?",
        "keywords": [r"change.*address", r"wrong address", r"update address", r"change payment", r"change.*delivery date", r"change phone", r"modify order", r"correct the address", r"edit address"],
        "quota": 25,
    },
    "PRIME_MEMBERSHIP_MANAGEMENT": {
        "cluster": "DIGITAL_SERVICES_AND_PRIME",
        "prototype": "I want to cancel my Amazon Prime membership subscription and stop the renewal fee.",
        "keywords": [r"cancel.*prime", r"prime membership", r"prime subscription", r"prime auto", r"charged for prime", r"renew.*prime", r"prime account fee", r"prime trial"],
        "quota": 25,
    },
    "DIGITAL_CONTENT_ACCESS": {
        "cluster": "DIGITAL_SERVICES_AND_PRIME",
        "prototype": "Having trouble streaming video on Prime Video and downloading my Kindle ebook.",
        "keywords": [r"prime video", r"kindle", r"ebook", r"audible", r"streaming", r"fire tv", r"fire stick", r"alexa", r"app error", r"digital content", r"movie"],
        "quota": 25,
    },
    "ACCOUNT_LOGIN_OR_OTP": {
        "cluster": "ACCOUNT_ACCESS_AND_SECURITY",
        "prototype": "Cannot log into my Amazon account. The OTP verification code is not sending and password reset failed.",
        "keywords": [r"login", r"log in", r"password", r"otp", r"verification code", r"account.*locked", r"hacked", r"access my account", r"sign in", r"two factor"],
        "quota": 25,
    },
}

BOUNDARY_PAIRS: List[Dict[str, Any]] = [
    {
        "intent_a": "WHERE_IS_MY_ORDER",
        "intent_b": "DELIVERY_DELAYED",
        "reason": (
            "Both inquiries seek package whereabouts. 'WHERE_IS_MY_ORDER' occurs within or near the "
            "promised delivery window, whereas 'DELIVERY_DELAYED' involves an explicitly passed estimated date."
        ),
    },
    {
        "intent_a": "DELIVERY_DELAYED",
        "intent_b": "MARKED_DELIVERED_NOT_RECEIVED",
        "reason": (
            "In 'DELIVERY_DELAYED', tracking shows in-transit or delayed status. In 'MARKED_DELIVERED_NOT_RECEIVED', "
            "the system marks the package as delivered, creating a discrepancy between digital status and physical reality."
        ),
    },
    {
        "intent_a": "REFUND_STATUS_INQUIRY",
        "intent_b": "UNAUTHORIZED_OR_DUPLICATE_CHARGE",
        "reason": (
            "Both involve monetary transactions. 'REFUND_STATUS_INQUIRY' tracks legitimate post-return credits, "
            "whereas 'UNAUTHORIZED_OR_DUPLICATE_CHARGE' involves disputed, erroneous, or unexpected debits."
        ),
    },
    {
        "intent_a": "CANCEL_ORDER_REQUEST",
        "intent_b": "MODIFY_ORDER_DETAILS",
        "reason": (
            "Both occur prior to dispatch. 'CANCEL_ORDER_REQUEST' seeks complete order termination, "
            "while 'MODIFY_ORDER_DETAILS' seeks to keep the order alive while changing delivery address, speed, or payment."
        ),
    },
    {
        "intent_a": "DAMAGED_OR_DEFECTIVE_ITEM",
        "intent_b": "WRONG_ITEM_RECEIVED",
        "reason": (
            "Both represent fulfillment defects upon unboxing. 'DAMAGED_OR_DEFECTIVE_ITEM' involves the correct "
            "product arriving broken/faulty, while 'WRONG_ITEM_RECEIVED' involves an intact but completely mismatched SKU."
        ),
    },
    {
        "intent_a": "PRIME_MEMBERSHIP_MANAGEMENT",
        "intent_b": "DIGITAL_CONTENT_ACCESS",
        "reason": (
            "Both mention Prime. 'PRIME_MEMBERSHIP_MANAGEMENT' relates to subscription billing, renewal, and fees. "
            "'DIGITAL_CONTENT_ACCESS' relates to viewing media or accessing Kindle content on Prime Video or devices."
        ),
    },
    {
        "intent_a": "CANCEL_ORDER_REQUEST",
        "intent_b": "DELIVERY_DELAYED",
        "reason": (
            "Order management addresses cancellation requests; delivery delayed addresses late shipments in carrier transit. "
            "Boundary cases involve customers demanding cancellation specifically because delivery is delayed."
        ),
    },
]


def extract_fallback_cases(df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
    """Extract 30-50 ambiguous, 30-50 multi-intent, and 20-30 out-of-scope candidate cases."""
    ambiguous: List[Dict[str, Any]] = []
    multi_intent: List[Dict[str, Any]] = []
    out_of_scope: List[Dict[str, Any]] = []

    # Ambiguous: under-specified inquiries lacking order ID, item name, or clear problem domain
    ambiguous_patterns = [
        r"can someone (please )?(help|assist) me",
        r"having (a problem|an issue) with my (order|account)",
        r"(please )?(check|respond to|look at) (my )?dm",
        r"no one is (replying|responding|answering)",
        r"why (is )?no one helping me",
        r"need urgent (help|assistance)",
        r"someone please contact me",
        r"customer service (is not|won't) (reply|help)",
    ]

    # Multi-intent: independent actionable conjunctions
    multi_patterns = [
        (r"\b(cancel|cancellation)\b.*\b(refund|money back)\b", "CANCEL_ORDER_REQUEST + REFUND_STATUS_INQUIRY"),
        (r"\b(late|not delivered|delayed)\b.*\b(cancel|refund)\b", "DELIVERY_DELAYED + CANCEL_ORDER_REQUEST"),
        (r"\b(broken|damaged|defective)\b.*\b(replacement|replace|refund)\b", "DAMAGED_OR_DEFECTIVE_ITEM + RETURN_OR_REPLACEMENT"),
        (r"\b(charged twice|double charged)\b.*\b(cancel|refund)\b", "UNAUTHORIZED_OR_DUPLICATE_CHARGE + REFUND_STATUS_INQUIRY"),
        (r"\b(wrong item|different item)\b.*\b(refund|return)\b", "WRONG_ITEM_RECEIVED + RETURN_OR_REPLACEMENT"),
    ]

    # Out of scope: brand compliments, news/stock commentary, hiring, or non-support rants
    oos_patterns = [
        r"\b(jeff bezos|stock price|shares|boycott|trump|politics|great job|thank you amazon|love amazon)\b",
        r"\b(congratulations|happy birthday|christmas wish|hiring|internship|job application|kudos|shout out)\b",
        r"\b(amazon is the best|amazing service|thanks for the quick|happy holidays)\b",
    ]

    used_convs: Set[int] = set()

    for _, row in df.iterrows():
        conv_id = int(row["conversation_id"])
        if conv_id in used_convs:
            continue

        text = str(row["customer_message_clean"]).strip()
        lower_text = text.lower()

        # Multi-intent check first
        if len(multi_intent) < 40:
            for pat, combo in multi_patterns:
                if re.search(pat, lower_text):
                    multi_intent.append({
                        "case_id": row["case_id"],
                        "conversation_id": conv_id,
                        "customer_message_clean": text,
                        "context_clean": row["context_clean"],
                        "brand_response_clean": row["brand_response_clean"],
                        "thread_length": int(row["thread_length"]),
                        "candidate_cluster": "CONTROLLED_FALLBACK",
                        "proposed_intent": "MULTI_INTENT",
                        "selection_reason": f"Expresses multiple independent actionable intents: {combo}",
                    })
                    used_convs.add(conv_id)
                    break
            if conv_id in used_convs:
                continue

        # Ambiguous check: lacks order number, problem details, asks for help/dm/contact vaguely
        if len(ambiguous) < 35 and not re.search(r"\b\d{3}-\d{7}-\d{7}\b", text):
            is_vague_help = (
                len(text) < 95
                and any(w in lower_text for w in ["help", "assist", "dm", "issue", "problem", "reply", "contact", "support", "anyone", "call me"])
                and not any(w in lower_text for w in ["tracking", "refund", "damaged", "broken", "cancel", "prime", "login", "password", "delivered", "courier", "driver"])
            )
            if is_vague_help or any(re.search(pat, lower_text) for pat in ambiguous_patterns):
                ambiguous.append({
                    "case_id": row["case_id"],
                    "conversation_id": conv_id,
                    "customer_message_clean": text,
                    "context_clean": row["context_clean"],
                    "brand_response_clean": row["brand_response_clean"],
                    "thread_length": int(row["thread_length"]),
                    "candidate_cluster": "CONTROLLED_FALLBACK",
                    "proposed_intent": "AMBIGUOUS_INQUIRY",
                    "selection_reason": "Under-specified inquiry lacking order number or problem domain details",
                })
                used_convs.add(conv_id)
                continue

        # Out of scope
        if len(out_of_scope) < 25:
            if any(re.search(pat, lower_text) for pat in oos_patterns):
                out_of_scope.append({
                    "case_id": row["case_id"],
                    "conversation_id": conv_id,
                    "customer_message_clean": text,
                    "context_clean": row["context_clean"],
                    "brand_response_clean": row["brand_response_clean"],
                    "thread_length": int(row["thread_length"]),
                    "candidate_cluster": "CONTROLLED_FALLBACK",
                    "proposed_intent": "OUT_OF_SCOPE",
                    "selection_reason": "Non-support commentary, compliment, or general feedback lacking a support issue",
                })
                used_convs.add(conv_id)
                continue

    return {
        "AMBIGUOUS_INQUIRY": ambiguous,
        "MULTI_INTENT": multi_intent,
        "OUT_OF_SCOPE": out_of_scope,
    }


def build_taxonomy_review_dataset(
    discovery_path: Path,
    embeddings_path: Path,
    output_cases_path: Path,
    output_boundaries_path: Path,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Construct representative review cases and boundary sets."""
    print("=" * 65)
    print("BUILDING TAXONOMY REVIEW & BOUNDARY DATASETS")
    print("=" * 65)

    df = pd.read_parquet(discovery_path)
    embeddings = np.load(embeddings_path)
    print(f"Loaded {len(df):,} discovery cases, embeddings {embeddings.shape}.")

    src_dir = PROJECT_ROOT / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    from support_agent.taxonomy.embeddings import encode_texts

    intent_names = list(INTENT_CONFIGS.keys())
    prototypes = [INTENT_CONFIGS[name]["prototype"] for name in intent_names]

    # Encode all prototypes in ONE batched call
    print(f"Encoding {len(prototypes)} intent prototypes in a single batch...")
    proto_matrix = encode_texts(prototypes, show_progress_bar=False)

    review_cases: List[Dict[str, Any]] = []
    used_convs: Set[int] = set()

    print("\n1. Selecting 20-30 diverse representative cases per candidate leaf intent:")
    for i, intent_name in enumerate(intent_names):
        cfg = INTENT_CONFIGS[intent_name]
        proto_vec = proto_matrix[i]
        sims = np.dot(embeddings, proto_vec)

        cluster_name = cfg["cluster"]
        kw_patterns = cfg["keywords"]
        target_quota = cfg["quota"]

        ranked_indices = np.argsort(sims)[::-1]
        intent_cases = []

        for idx in ranked_indices:
            row = df.iloc[idx]
            conv_id = int(row["conversation_id"])
            if conv_id in used_convs:
                continue

            msg = str(row["customer_message_clean"])
            lower_msg = msg.lower()
            kw_match = any(re.search(pat, lower_msg) for pat in kw_patterns)
            score = sims[idx]

            # Primary match condition: semantic score >= 0.40 with kw_match, or high semantic score >= 0.65
            if (score >= 0.40 and kw_match) or score >= 0.65:
                intent_cases.append({
                    "case_id": row["case_id"],
                    "conversation_id": conv_id,
                    "customer_message_clean": msg,
                    "context_clean": row["context_clean"],
                    "brand_response_clean": row["brand_response_clean"],
                    "thread_length": int(row["thread_length"]),
                    "candidate_cluster": cluster_name,
                    "proposed_intent": intent_name,
                    "selection_reason": (
                        f"High semantic alignment (score: {score:.3f}) with {intent_name} prototype "
                        f"and verified domain keywords"
                    ),
                })
                used_convs.add(conv_id)
                if len(intent_cases) >= target_quota:
                    break

        # Fallback if strict threshold didn't reach target: accept top semantic matches matching at least 1 keyword
        if len(intent_cases) < 20:
            for idx in ranked_indices:
                row = df.iloc[idx]
                conv_id = int(row["conversation_id"])
                if conv_id in used_convs:
                    continue
                msg = str(row["customer_message_clean"])
                if any(re.search(pat, msg.lower()) for pat in kw_patterns):
                    score = sims[idx]
                    intent_cases.append({
                        "case_id": row["case_id"],
                        "conversation_id": conv_id,
                        "customer_message_clean": msg,
                        "context_clean": row["context_clean"],
                        "brand_response_clean": row["brand_response_clean"],
                        "thread_length": int(row["thread_length"]),
                        "candidate_cluster": cluster_name,
                        "proposed_intent": intent_name,
                        "selection_reason": f"Semantic alignment (score: {score:.3f}) with keyword verification",
                    })
                    used_convs.add(conv_id)
                    if len(intent_cases) >= target_quota:
                        break

        print(f"  - {intent_name:<34}: {len(intent_cases)} cases selected")
        review_cases.extend(intent_cases)

    # 2. Extract fallbacks
    print("\n2. Extracting fallback categories (ambiguous, multi-intent, out-of-scope):")
    fallbacks = extract_fallback_cases(df)
    for fb_name, fb_cases in fallbacks.items():
        print(f"  - {fb_name:<34}: {len(fb_cases)} cases selected")
        review_cases.extend(fb_cases)

    print(f"\nTotal taxonomy review cases selected: {len(review_cases):,}")

    # 3. Extract Boundary Cases using prototype similarity proximity
    print("\n" + "-" * 65)
    print("3. EXTRACTING CONFUSABLE BOUNDARY CASES")
    print("-" * 65)

    boundaries: List[Dict[str, Any]] = []

    for b_cfg in BOUNDARY_PAIRS:
        intent_a = b_cfg["intent_a"]
        intent_b = b_cfg["intent_b"]
        reason = b_cfg["reason"]

        idx_a = intent_names.index(intent_a) if intent_a in intent_names else None
        idx_b = intent_names.index(intent_b) if intent_b in intent_names else None

        boundary_matches = []

        if idx_a is not None and idx_b is not None:
            vec_a = proto_matrix[idx_a]
            vec_b = proto_matrix[idx_b]
            sims_a = np.dot(embeddings, vec_a)
            sims_b = np.dot(embeddings, vec_b)

            # Proximity metric: candidate cases with high similarity to both prototypes
            # |sim_a - sim_b| < 0.08 and min(sim_a, sim_b) > 0.40
            proximity = np.abs(sims_a - sims_b)
            joint_sim = (sims_a + sims_b) / 2.0
            eligible_idx = np.where((proximity < 0.08) & (joint_sim > 0.42))[0]
            ranked_boundary = eligible_idx[np.argsort(joint_sim[eligible_idx])[::-1]]

            for idx in ranked_boundary[:5]:
                r = df.iloc[idx]
                boundary_matches.append({
                    "case_id": r["case_id"],
                    "conversation_id": int(r["conversation_id"]),
                    "customer_message_clean": r["customer_message_clean"],
                    "brand_response_clean": r["brand_response_clean"],
                    "sim_intent_a": round(float(sims_a[idx]), 3),
                    "sim_intent_b": round(float(sims_b[idx]), 3),
                })

        record = {
            "intent_a": intent_a,
            "intent_b": intent_b,
            "why_potentially_confused": reason,
            "boundary_case_count": len(boundary_matches),
            "example_cases": boundary_matches,
        }
        boundaries.append(record)
        print(f"  * Boundary: {intent_a} vs {intent_b} ({len(boundary_matches)} example cases)")

    # 4. Save files
    output_cases_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_cases_path, "w", encoding="utf-8") as f:
        for rec in review_cases:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"\nSaved {len(review_cases):,} review cases to: {output_cases_path.as_posix()}")

    with open(output_boundaries_path, "w", encoding="utf-8") as f:
        for rec in boundaries:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Saved {len(boundaries)} boundary records to: {output_boundaries_path.as_posix()}")

    return review_cases, boundaries


def main() -> None:
    parser = argparse.ArgumentParser(description="Build taxonomy review cases and boundary datasets.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DISCOVERY_DATA)
    parser.add_argument("--embeddings", type=Path, default=DEFAULT_EMBEDDINGS)
    parser.add_argument("--output-cases", type=Path, default=OUTPUT_REVIEW_CASES)
    parser.add_argument("--output-boundaries", type=Path, default=OUTPUT_BOUNDARIES)
    args = parser.parse_args()

    build_taxonomy_review_dataset(args.data, args.embeddings, args.output_cases, args.output_boundaries)


if __name__ == "__main__":
    main()
