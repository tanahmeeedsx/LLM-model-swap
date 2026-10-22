import json
import os
import urllib.error
import urllib.request

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Local LLM Orchestration API",
    description="A local API for selecting and using models through OmniRoute.",
    version="0.2.0",
)

OMNIROUTE_URL = os.getenv("OMNIROUTE_URL", "http://127.0.0.1:20128/v1").rstrip("/")
OMNIROUTE_API_KEY = os.getenv("OMNIROUTE_API_KEY", "")

ALLOWED_MODELS = {
    "ollama/qwen2.5:1.5b",
    "ollama/llama3.2:latest",
}


class GenerateRequest(BaseModel):
    model: str = "ollama/llama3.2:latest"
    prompt: str = Field(min_length=1, max_length=10000)


def omni_request(path: str, payload: dict | None = None):
    if not OMNIROUTE_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OMNIROUTE_API_KEY environment variable is not set.",
        )

    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {OMNIROUTE_API_KEY}",
        "Accept": "application/json",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        f"{OMNIROUTE_URL}{path}",
        data=data,
        headers=headers,
        method="POST" if data is not None else "GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        status_code = error.code if 400 <= error.code < 500 else 502
        raise HTTPException(
            status_code=status_code,
            detail=f"OmniRoute returned HTTP {error.code}: {detail[:1000]}",
        )
    except (urllib.error.URLError, TimeoutError) as error:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to OmniRoute: {error}",
        )


@app.get("/health")
def health():
    return {"status": "ok", "service": "local-llm-api"}


@app.get("/models")
def list_models():
    result = omni_request("/models")
    models = result.get("data", [])
    return {
        "object": "list",
        "data": [
            model for model in models
            if model.get("id") in ALLOWED_MODELS
        ],
    }


@app.post("/generate")
def generate(request_data: GenerateRequest):
    if request_data.model not in ALLOWED_MODELS:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Unsupported model.",
                "allowed_models": sorted(ALLOWED_MODELS),
            },
        )

    result = omni_request(
        "/chat/completions",
        {
            "model": request_data.model,
            "messages": [{"role": "user", "content": request_data.prompt}],
            "stream": False,
            "max_tokens": 100,
        },
    )

    try:
        return {
            "model": result["model"],
            "response": result["choices"][0]["message"]["content"],
        }
    except (KeyError, IndexError, TypeError):
        raise HTTPException(
            status_code=502,
            detail="OmniRoute returned an unexpected response format.",
        )
