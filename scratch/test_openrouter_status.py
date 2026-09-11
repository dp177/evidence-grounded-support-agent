import requests
from pathlib import Path

env = {}
for line in Path(".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip("\"'")

headers = {
    "Authorization": f"Bearer {env['OPENROUTER_API_KEY']}",
    "Content-Type": "application/json",
}
payload = {
    "model": "meta-llama/llama-3.1-8b-instruct",
    "messages": [{"role": "user", "content": "hi"}],
}
r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
print("Non-free status:", r.status_code)
print("Response JSON:", r.json())
