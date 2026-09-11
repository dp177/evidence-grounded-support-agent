import os
import sys
sys.path.insert(0, 'src')
from support_agent.llm.client import get_llm_client

client = get_llm_client()
print("Client:", type(client).__name__)
resp = client.generate("Respond with valid JSON only: {\"hello\": \"world\"}", temperature=0.0)
print("Response content:", resp.content)
print("Parsed JSON:", resp.json())
