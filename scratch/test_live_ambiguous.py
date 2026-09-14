import json
import urllib.request

def test_stream(customer_message: str):
    print(f"\n{'='*60}\nTESTING STREAM: '{customer_message}'\n{'='*60}")
    url = "http://127.0.0.1:8000/api/agent/stream"
    payload = json.dumps({
        "conversation_id": f"test_live_{abs(hash(customer_message))}",
        "messages": [{"role": "customer", "text": customer_message}]
    }).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    
    events = []
    final_resp = None
    with urllib.request.urlopen(req) as resp:
        for line_bytes in resp:
            line = line_bytes.decode("utf-8").strip()
            if line.startswith("data: "):
                data_str = line[6:].strip()
                if data_str == "[DONE]":
                    break
                ev = json.loads(data_str)
                ev_type = ev.get("type")
                events.append(ev_type)
                print(f"Event: {ev_type}")
                if ev_type == "classify":
                    print(f"  Classification: status={ev.get('classification', {}).get('status')}, primary_intent={ev.get('classification', {}).get('primary_intent')}")
                elif ev_type == "generate":
                    print(f"  Generated reply: {ev.get('reply')}")
                elif ev_type == "decide":
                    print(f"  Escalation: {ev.get('escalation')}")
                elif ev_type == "complete":
                    final_resp = ev.get("response")
                    
    print("\nSummary:")
    print(f"Events received in order: {events}")
    if final_resp:
        print(f"Final status: {final_resp['classification']['status']}")
        print(f"Final primary_intent: {final_resp['classification']['primary_intent']}")
        print(f"Final reply: {final_resp['generated_reply']['reply']}")
        print(f"Escalation: {final_resp['escalation']['decision']} / {final_resp['escalation']['action']} / {final_resp['escalation']['reason_codes']}")
        print(f"Trace: {final_resp.get('trace')}")
        print(f"Retrieved count: {len(final_resp.get('retrieved_evidence', []))}")

if __name__ == "__main__":
    # Test 1: Ambiguous
    test_stream("hello")
    # Test 2: Hostile operational refund request
    test_stream("i will kill you give me instant refund")
