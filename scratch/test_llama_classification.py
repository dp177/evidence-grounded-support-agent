import sys
sys.path.insert(0, "src")
import json
from support_agent.classification.llm_classifier import LLMIntentClassifier
from support_agent.llm.client import OpenRouterClient

client = OpenRouterClient(model="meta-llama/llama-3.1-8b-instruct")
clf = LLMIntentClassifier(client=client)

with open("data/golden/golden_set.jsonl", "r", encoding="utf-8") as f:
    sample = json.loads(f.readline())

print("Customer message:", sample["customer_message"])
res = clf.classify_case(sample["customer_message"], sample.get("context"), gold_id="test_llama", use_cache=False)
print("Classification result:")
print(json.dumps(res, indent=2))
