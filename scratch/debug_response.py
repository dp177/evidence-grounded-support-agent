import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from support_agent.llm.client import get_llm_client

client = get_llm_client()
prompt = "Classify: My package was supposed to arrive yesterday and is delayed. Can you check where it is? Output valid JSON only."
resp = client.generate(prompt=prompt, max_tokens=1000)
print("Finish reason:", resp.raw.get("choices", [{}])[0].get("finish_reason"))
print("Raw content:")
print(repr(resp.content))
print("Usage:", resp.usage)
