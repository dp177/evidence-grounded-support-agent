import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from support_agent.classification.llm_classifier import LLMIntentClassifier

clf = LLMIntentClassifier()
sample_msg = "My package was supposed to arrive yesterday and is delayed. Can you check where it is?"
sample_ctx = "CUSTOMER: My package was supposed to arrive yesterday and is delayed. Can you check where it is?"

res = clf.classify_case(sample_msg, sample_ctx, gold_id="test_sample_001", use_cache=False)
print("Result:")
print(res)
