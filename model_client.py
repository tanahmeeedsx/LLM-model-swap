import json
import os
import urllib.request

MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
API_URL = "http://localhost:11434/api/generate"

payload = {
    "model": MODEL,
    "prompt": "Explain Docker in one sentence.",
    "stream": False,
}

request = urllib.request.Request(
    API_URL,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)

with urllib.request.urlopen(request, timeout=180) as response:
    result = json.loads(response.read().decode("utf-8"))

print(f"Model: {result['model']}")
print(f"Response: {result['response']}")
