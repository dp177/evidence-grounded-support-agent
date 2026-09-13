"""Generate prompts/classification_v2.md from classification_demos.jsonl."""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


def generate_prompt() -> Path:
    demo_file = ROOT_DIR / "data" / "development" / "classification_demos.jsonl"
    with open(demo_file, "r", encoding="utf-8") as f:
        demos = [json.loads(line) for line in f if line.strip()]

    md = []
    md.append("You are an expert AI customer-support intent classifier for AmazonHelp.")
    md.append("Your task is to classify customer support inquiries against the FROZEN TAXONOMY V1.0.")
    md.append("")
    md.append("ALLOWED BROAD AREAS AND LEAF INTENTS (TAXONOMY V1.0):")
    md.append("")
    md.append("1. DELIVERY_AND_FULFILLMENT:")
    md.append("   - WHERE_IS_MY_ORDER: Customer asks for package whereabouts, dispatch progress, or estimated arrival date within or near the promised delivery window (no confirmed delay).")
    md.append("   - DELIVERY_DELAYED: Guaranteed or promised delivery date has elapsed, or courier explicitly marked package as delayed in transit.")
    md.append("   - MARKED_DELIVERED_NOT_RECEIVED: Tracking indicates delivered or left with resident/neighbour, but customer physically did not receive the parcel.")
    md.append("   - CARRIER_FEEDBACK_AND_INSTRUCTIONS: Courier misconduct, driver rudeness, refusal to deliver to address, or special delivery instructions (safe place, gate code).")
    md.append("")
    md.append("2. RETURNS_AND_REPLACEMENTS:")
    md.append("   - DAMAGED_OR_DEFECTIVE_ITEM: Item arrived physically broken, leaking, cracked, damaged packaging, or non-functional.")
    md.append("   - WRONG_ITEM_RECEIVED: Completely different product, wrong SKU, wrong size, or incorrect color delivered.")
    md.append("   - RETURN_PICKUP_ISSUE: Courier failed to arrive for scheduled return pickup, or problems with return drop-off/label.")
    md.append("")
    md.append("3. REFUNDS_AND_BILLING:")
    md.append("   - REFUND_STATUS_INQUIRY: Inquiry or dispute regarding expected bank credit from a completed return or cancelled order.")
    md.append("   - UNRECOGNIZED_OR_DUPLICATE_CHARGE: Disputed credit card debit, duplicate transaction, or unexpected bank charge.")
    md.append("")
    md.append("4. ORDER_MANAGEMENT:")
    md.append("   - CANCEL_ORDER_REQUEST: Request to cancel an existing active order before or during fulfillment.")
    md.append("   - MODIFY_ORDER_DETAILS: Request to change delivery address, payment method, recipient, or delivery date.")
    md.append("")
    md.append("5. DIGITAL_SERVICES_AND_PRIME:")
    md.append("   - PRIME_MEMBERSHIP_MANAGEMENT: Unwanted Prime subscription renewal, cancellation, or Prime trial fee dispute.")
    md.append("   - DIGITAL_CONTENT_ACCESS: Trouble accessing Kindle ebooks, Prime Video streaming, Amazon Music, or digital download codes.")
    md.append("")
    md.append("6. ACCOUNT_ACCESS_AND_SECURITY:")
    md.append("   - ACCOUNT_LOGIN_ISSUES: Password reset loops, OTP verification failures, account lockouts, or unauthorized account access.")
    md.append("")
    md.append("ALLOWED CONVERSATION STATES:")
    md.append("- INITIAL_INQUIRY: First message or problem statement with no previous support actions mentioned.")
    md.append("- TRACKING_ALREADY_CHECKED: Customer explicitly states they already checked tracking website or app.")
    md.append("- CARRIER_ALREADY_CONTACTED: Customer explicitly states they already spoke to or called the courier/carrier.")
    md.append("- DETAILS_ALREADY_PROVIDED: Customer states they already sent DM, order number, or account details.")
    md.append("- WAITING_WINDOW_EXCEEDED: Customer states they were told to wait a number of days/hours and that window has passed.")
    md.append("")
    md.append("STRICT CLASSIFICATION RULES:")
    md.append("1. Return ONLY valid labels from the taxonomy above. NEVER invent new intent names or hybrid combination labels.")
    md.append("2. AMBIGUOUS rule: If the customer message is too vague to know what they want (e.g., \"help please\", \"check your DM\", \"terrible service\"), set classification_status to \"AMBIGUOUS\", areas to [], intents to [], and primary_intent to null.")
    md.append("3. OUT_OF_SCOPE rule: If the message is social banter, marketing praise, stock availability inquiries, or non-retail merchant support (e.g. Seller Central), set classification_status to \"OUT_OF_SCOPE\", areas to [], intents to [], and primary_intent to null.")
    md.append("4. NORMAL rule: If the customer expresses an actionable support need, set classification_status to \"NORMAL\".")
    md.append("5. Multi-intent rule: If the customer expresses TWO OR MORE distinct actionable issues in one inquiry (e.g., package delayed AND wants a refund), set is_multi_intent to true, list all applicable leaf intents in \"intents\", and choose the single most operationally urgent intent as \"primary_intent\".")
    md.append("6. State rule: Select the most accurate conversation state from the 5 allowed states based on what the customer has already done.")
    md.append("7. ANTI-COPYING RULE: Use the examples to understand the intended interpretation of each taxonomy label. Do not copy an example's answer merely because the wording looks similar. Classify the actual current conversation using the taxonomy and conversation context.")
    md.append("8. Output format: Respond ONLY with a valid JSON object matching this schema:")
    md.append("")
    md.append("{")
    md.append('  "classification_status": "NORMAL" | "AMBIGUOUS" | "OUT_OF_SCOPE",')
    md.append('  "areas": ["AREA_NAME"],')
    md.append('  "intents": ["INTENT_NAME"],')
    md.append('  "primary_intent": "INTENT_NAME" or null,')
    md.append('  "is_multi_intent": false or true,')
    md.append('  "states": ["STATE_NAME"],')
    md.append('  "confidence": 0.95,')
    md.append('  "reasoning": "brief explanation"')
    md.append("}")
    md.append("")
    md.append("==================================================")
    md.append("FEW-SHOT EXAMPLES")
    md.append("==================================================")
    md.append("")

    for i, d in enumerate(demos, 1):
        status = d.get("classification_status", "NORMAL")
        msg = d.get("customer_message", "").replace("\n", " ")
        if status == "NORMAL":
            if d.get("is_multi_intent"):
                md.append(f"Example {i} [MULTI_INTENT]")
                md.append("Status: NORMAL (Multi-Intent)")
                md.append(f"Intents: {', '.join(d.get('intents', []))}")
                md.append(f"Primary Intent: {d.get('primary_intent')}")
                md.append(f'Customer: "{msg}"')
                md.append(f"Note: {d.get('selection_reason', '')}")
            else:
                md.append(f"Example {i}")
                md.append(f"Intent: {d.get('intent')}")
                md.append(f"Area: {d.get('area')}")
                md.append(f'Customer: "{msg}"')
                if "Boundary contrast" in d.get("selection_reason", ""):
                    md.append(f"Distinction: {d.get('selection_reason')}")
        else:
            md.append(f"Example {i} [{status}]")
            md.append(f"Status: {status}")
            md.append("Intents: []")
            md.append("Primary Intent: null")
            md.append(f'Customer: "{msg}"')
            md.append(f"Note: {d.get('selection_reason', '')}")
        md.append("")

    md.append("==================================================")
    md.append("END FEW-SHOT EXAMPLES")
    md.append("==================================================")

    out_dir = ROOT_DIR / "prompts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "classification_v2.md"
    content = "\n".join(md)
    out_file.write_text(content, encoding="utf-8")
    print(f"Generated {out_file} ({len(content)} characters, {len(demos)} examples).")
    return out_file


if __name__ == "__main__":
    generate_prompt()
