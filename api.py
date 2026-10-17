import json
import urllib.error
import urllib.request

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Local LLM Orchestration API",
    description="A local API for selecting and using Ollama models.",
    version="0.1.0",
)

OLLAMA_URL = "http://localhost:11434"


class GenerateRequest(BaseModel):
    model: str = "llama3.2"
    prompt: str = Field(min_length=1, max_length=10000)


@app.get("/health")
def health():
    return {"status": "ok", "service": "local-llm-api"}


@app.get("/models")
def list_models():
    try:
        request = urllib.request.Request(f"{OLLAMA_URL}/api/tags")

        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))

    except urllib.error.URLError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Ollama is unavailable: {error}",
        )


@app.post("/generate")
def generate(request_data: GenerateRequest):
    payload = {
        "model": request_data.model,
        "prompt": request_data.prompt,
        "stream": False,
        "options": {
            "num_ctx": 2048,
            "num_predict": 100,
        },
    }

    request = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))

        return {
            "model": result["model"],
            "response": result["response"],
        }

    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8")
        raise HTTPException(status_code=error.code, detail=detail)

    except urllib.error.URLError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to Ollama: {error}",
        )
