# DEV-875: Local LLM Orchestration & Model-Swapping

## Objective

Research and evaluate self-hosted LLM tools for running local AI models, switching between models without changing application code, and providing a consistent API for applications.

## Work Completed — 10 October 2026

### 1. Local LLM Setup

- Ran Ollama using Docker on Ubuntu Linux.
- Downloaded and tested two local AI models:
  - `llama3.2`
  - `qwen2.5:1.5b`
- Verified that both models could generate responses locally.

### 2. Model Switching

Created `model_client.py` to send prompts to the Ollama API.

Tested the default model:

```bash
python3 model_client.py
```

Switched to Qwen using an environment variable:

```bash
OLLAMA_MODEL=qwen2.5:1.5b python3 model_client.py
```

Both models worked with the same Python client without changing the application code.

### 3. API Compatibility Testing

Tested Ollama's native generation endpoint:

`http://localhost:11434/api/generate`

Also tested the OpenAI-compatible chat completions endpoint:

`http://localhost:11434/v1/chat/completions`

The API successfully returned the expected response:

`local API works`

This confirms that the local model can be accessed through an OpenAI-compatible API format.

### 4. Container and Model Validation

- Successfully restarted the Ollama Docker container.
- Verified that both models remained available after the restart.
- Used `docker exec ollama ollama ps` to inspect loaded models.
- Observed both models loaded simultaneously during testing.

### 5. Tool Research and Comparison

Researched and compared four self-hosted LLM tools:

| Tool | Primary Use |
|---|---|
| Ollama | Simple local model deployment and management |
| vLLM | High-throughput LLM serving |
| LocalAI | OpenAI-compatible API across supported inference backends |
| llama.cpp | Lightweight and quantized local inference |

Compared the tools against eight criteria:

1. Local-first and self-hosted inference
2. Model switching without application code changes
3. Consistent API support
4. Multi-model access through one interface
5. Hot-swapping capabilities
6. Model pooling, aliases, fallback, and load balancing
7. Open-source availability and self-hosting
8. Optional third-party provider fallback

The preliminary scoring and comparison are research-based assessments, not benchmark results. Ollama was tested hands-on; the other tools were not installed or benchmarked in this project.

## Recommendation

Ollama is the recommended starting point for this prototype because local inference, model switching, and OpenAI-compatible API access were successfully tested.

The proposed architecture is:

**Application → OmniRoute → Ollama → Local Models**

OmniRoute can be evaluated as the routing layer, while Ollama provides local model inference. Integration with the existing OmniRoute setup must be verified before confirming the complete architecture.

## FastAPI Orchestration Service

A FastAPI service provides a common HTTP interface for local Ollama models.

### Start the API

Activate the virtual environment and run:

    source .venv/bin/activate
    python -m uvicorn api:app --host 127.0.0.1 --port 8000

Interactive API documentation: http://127.0.0.1:8000/docs

### Available Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check API health |
| GET | `/models` | List available Ollama models |
| POST | `/generate` | Generate a response using a selected model |

### Test Model Switching

Generate a response using Qwen:

    curl -X POST http://127.0.0.1:8000/generate \
      -H "Content-Type: application/json" \
      -d '{"model":"qwen2.5:1.5b","prompt":"Explain Kubernetes in one sentence."}'

Generate a response using Llama:

    curl -X POST http://127.0.0.1:8000/generate \
      -H "Content-Type: application/json" \
      -d '{"model":"llama3.2","prompt":"Explain Docker in one sentence."}'

### Validation Results

- Tested both models using the Python CLI.
- Verified custom prompts and environment-based model selection.
- Tested API health and model-list endpoints.
- Successfully generated responses from both models through FastAPI.

The current API forwards requests to Ollama and allows the caller to select a model. OmniRoute integration, true hot-swapping, fallback, and load balancing remain future work.

## Remaining Work

- Integrate Ollama with the existing OmniRoute setup.
- Test end-to-end requests through OmniRoute.
- Verify fallback and load-balancing behavior.
- Evaluate alternative tools hands-on if required.
- Benchmark response latency and resource usage if production performance is required.

## References

- Ollama OpenAI Compatibility: https://docs.ollama.com/api/openai-compatibility
- vLLM Documentation: https://docs.vllm.ai/
- LocalAI Documentation: https://localai.io/docs/
- llama.cpp Repository: https://github.com/ggml-org/llama.cpp

## Conclusion

The prototype demonstrates local inference using two models, configuration-based model switching with a reusable Python client, and a working OpenAI-compatible API.

Ollama is the recommended baseline for the current environment. OmniRoute integration, fallback, and load-balancing behavior remain to be validated.
