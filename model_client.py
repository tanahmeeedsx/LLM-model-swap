import argparse
import json
import os
import urllib.request
import urllib.error

parser = argparse.ArgumentParser(description="Local LLM Model Client")
parser.add_argument(
    "--model",
    default=os.getenv("OLLAMA_MODEL", "llama3.2"),
    help="Model name to use (default: llama3.2)",
)
parser.add_argument(
    "--prompt",
    default="Explain Docker in one sentence.",
    help="Prompt to send to the model",
)
args = parser.parse_args()

MODEL = args.model
API_URL = "http://localhost:11434/api/generate"

payload = {
    "model": MODEL,
    "prompt": args.prompt,
    "stream": False,
    "options": {
        "num_ctx": 2048,
        "num_predict": 50,
    },
}

request = urllib.request.Request(
    API_URL,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)

try:
    with urllib.request.urlopen(request, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))

    print(f"Model: {result['model']}")
    print(f"Response: {result['response']}")

except urllib.error.HTTPError as error:
    print(f"HTTP Error: {error.code}")
    print(error.read().decode("utf-8"))

except urllib.error.URLError as error:
    print(f"Connection error: {error.reason}")
    print("Make sure the Ollama container is running.")
