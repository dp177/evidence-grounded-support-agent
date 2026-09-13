"""Interactive runtime demonstration of Qdrant semantic retrieval.

Demonstrates historical support evidence retrieval for realistic customer inquiries.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import List, Tuple

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from support_agent.retrieval.retriever import QdrantRetriever, format_query_text

DEMO_QUERIES: List[Tuple[str, str, str]] = [
    (
        "Late Delivery Inquiry",
        "My order was supposed to arrive yesterday by 8 PM. Tracking hasn't updated since 3 days ago. Where is my package?",
        "Order #112-8726391-9281928, carrier shows delayed at sorting facility.",
    ),
    (
        "Damaged Item on Arrival",
        "I just opened the package and the glass bottle inside is completely shattered. Liquid leaked everywhere. Can I get a replacement or refund?",
        "Delivered today. Customer reported item arrived damaged.",
    ),
    (
        "Wrong Item Delivered",
        "I ordered black running shoes in size 10, but you sent me a blue t-shirt instead. How do I exchange this?",
        "Package received 2 hours ago. Customer unpacked incorrect merchandise.",
    ),
    (
        "Refund Status & Delay",
        "I returned my item more than 2 weeks ago and tracking confirms it reached your warehouse, but I still have not received my refund to my bank.",
        "Return tracking shows received on the 28th. No credit posted yet.",
    ),
    (
        "Unauthorized Account Charge",
        "I was just charged $14.99 for Prime but I never signed up for it or authorized this renewal. Please cancel and refund immediately.",
        "Customer noticed unexpected Prime subscription fee on bank statement.",
    ),
]


def run_demo(top_k: int = 3) -> None:
    print("\n" + "=" * 60)
    print("      QDRANT HISTORICAL EVIDENCE RETRIEVAL DEMO")
    print("=" * 60)

    retriever = QdrantRetriever()
    print(f"Connected to Qdrant collection: {retriever.collection_name}")
    print(f"Mode: {retriever.vector_store.mode}")

    for idx, (title, customer_msg, context) in enumerate(DEMO_QUERIES, 1):
        print("\n" + "#" * 60)
        print(f"CASE {idx}: {title}")
        print("#" * 60)

        query_text = format_query_text(customer_msg, context)

        print("\n" + "=" * 40)
        print("CUSTOMER")
        print("=" * 40)
        print(customer_msg.strip())
        if context:
            print(f"\n[Context provided: {context.strip()}]")

        print("\n" + "=" * 40)
        print("TOP HISTORICAL EVIDENCE")
        print("=" * 40)

        results = retriever.search(query_text=query_text, top_k=top_k)

        for rank, res in enumerate(results, 1):
            score = res["score"]
            doc_id = res["document_id"]
            case_id = res["case_id"]
            c_msg = res["customer_message"]
            r_ctx = res["relevant_context"]
            b_resp = res["brand_response"]

            print(f"\n[{rank}] score={score:.4f}  (doc={doc_id}, case={case_id})")
            print("CUSTOMER:")
            print(c_msg if c_msg else "[No customer text]")

            if r_ctx and r_ctx.strip():
                print("\nRELEVANT CONTEXT:")
                print(r_ctx.strip())

            print("\nAMAZON RESPONSE:")
            print(b_resp if b_resp else "[No response text]")
            print("-" * 40)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Qdrant retrieval demo")
    parser.add_argument("--top-k", type=int, default=3, help="Number of evidence cases to display per query")
    args = parser.parse_args()
    run_demo(top_k=args.top_k)


if __name__ == "__main__":
    main()
