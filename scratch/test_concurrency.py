import sys
sys.path.insert(0, "src")
import time
from concurrent.futures import ThreadPoolExecutor
from support_agent.classification.llm_classifier import LLMIntentClassifier

clf = LLMIntentClassifier()
t0 = time.time()

def call(i):
    return clf.classify_case(f"Test package delivery issue message {i}", use_cache=False)

with ThreadPoolExecutor(max_workers=2) as ex:
    futs = [ex.submit(call, i) for i in range(2)]
    res = [f.result() for f in futs]

print(f"Done 2 calls in {time.time()-t0:.2f}s, results: {[r['primary_intent'] for r in res]}")
