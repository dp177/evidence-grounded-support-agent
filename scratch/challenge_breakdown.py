import json
from collections import defaultdict

with open("evaluation/results/golden_v2_raw.jsonl", encoding="utf-8") as f:
    records = [json.loads(line) for line in f]

# Group by human category notes/tags if available or by intent/challenge slice
categories = defaultdict(list)

for r in records:
    gid = r["gold_id"]
    gold = r["gold"]
    agent = r["agent"]
    msg = r["input"]["customer_message"].lower()
    ctx = r["input"]["context"].lower()
    
    # 1. Ambiguous
    if gold["status"] == "AMBIGUOUS":
        categories["Ambiguous"].append(r)
    # 2. Out of Scope
    elif gold["status"] == "OUT_OF_SCOPE":
        categories["Out-of-Scope"].append(r)
    else:
        # Normal categories
        it = gold.get("primary_intent")
        all_it = gold.get("intents") or ""
        
        # Multi-intent
        if "|" in all_it:
            categories["Multi-Intent"].append(r)
            
        # Account Security
        if gold.get("escalation_reason") == "ACCOUNT_SECURITY_COMPROMISE":
            categories["Account Security Compromise"].append(r)
        elif it == "ACCOUNT_LOGIN_ISSUES" and not gold.get("should_escalate"):
            categories["Normal Login / Password Reset"].append(r)
        elif it == "ACCOUNT_LOGIN_ISSUES" and gold.get("should_escalate"):
            categories["Account Lock + Failed Recovery"].append(r)
            
        # Repeated Failed Support
        if gold.get("escalation_reason") == "REPEATED_FAILED_SUPPORT_ATTEMPTS":
            categories["Repeated Failed Support"].append(r)
            
        # Carrier Misconduct vs Routine
        if it == "CARRIER_FEEDBACK_AND_INSTRUCTIONS":
            if gold.get("should_escalate"):
                categories["Carrier Misconduct / Refusal"].append(r)
            else:
                categories["Routine Carrier Instructions"].append(r)
                
        # Tracking Number Location vs Tracking Already Checked
        if it == "WHERE_IS_MY_ORDER" and "tracking number" in msg and gold.get("state") == "INITIAL_INQUIRY":
            categories["Tracking Number Location Query"].append(r)
        elif gold.get("state") == "TRACKING_ALREADY_CHECKED":
            categories["Tracking Already Checked"].append(r)
            
        # Conversational state
        if "\n" in r["input"]["context"] or "brand:" in ctx:
            categories["Multi-Turn Conversational State"].append(r)

print("=== CHALLENGE CATEGORY PERFORMANCE IN GOLDEN V2 ===")
for cat, recs in sorted(categories.items()):
    n = len(recs)
    status_acc = sum(1 for r in recs if r["graders"]["classification"]["status_match"]) / n
    primary_acc = sum(1 for r in recs if r["graders"]["classification"]["primary_intent_match"]) / n
    state_acc = sum(1 for r in recs if r["graders"]["classification"]["state_match"]) / n
    esc_match = sum(1 for r in recs if r["graders"]["escalation"]["escalation_match"]) / n
    gold_esc_count = sum(1 for r in recs if r["gold"]["should_escalate"])
    agent_esc_count = sum(1 for r in recs if r["agent"]["should_escalate"])
    
    print(f"\n[{cat}] (N={n}):")
    print(f"  Status Acc: {status_acc:.1%}")
    print(f"  Primary Intent Acc: {primary_acc:.1%}")
    print(f"  State Acc: {state_acc:.1%}")
    print(f"  Escalation Match: {esc_match:.1%} (Gold Esc: {gold_esc_count}, Agent Esc: {agent_esc_count})")
