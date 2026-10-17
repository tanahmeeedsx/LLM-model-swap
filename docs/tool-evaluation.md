# DEV-875: Local LLM Serving Tool Evaluation

**Evaluation date:** 17 October 2026

## 1. Objective

Evaluate open-source, self-hosted tools for running local language models and switching models without changing application code.

The evaluation focuses on the eight Docker-like local model-swapping criteria defined in DEV-875. Local inference is the primary requirement; third-party providers are optional.

## 2. Scoring Method

Each criterion receives a score from 1 to 5.

- **1 — Poor:** Little or no native support.
- **2 — Limited:** Significant additional configuration or components required.
- **3 — Partial:** Supported with limitations or external components.
- **4 — Strong:** Good support with some limitations.
- **5 — Excellent:** Strong native support for the requirement.

Scores are qualitative research assessments, not benchmark results. Ollama has been tested hands-on in this project. vLLM, LocalAI, and llama.cpp have not yet been installed or benchmarked here.

## 3. Comparison Matrix

| Criterion | Ollama | vLLM | LocalAI | llama.cpp |
|---|---:|---:|---:|---:|
| 1. Local-first inference | 5 | 5 | 5 | 5 |
| 2. Swap without application-code changes | 5 | 3 | 4 | 4 |
| 3. Simple, consistent interface | 5 | 3 | 4 | 3 |
| 4. One API for multiple local models | 4 | 3 | 5 | 4 |
| 5. Hot-swapping and model lifecycle | 4 | 2 | 4 | 5 |
| 6. Model groups, pools, aliases, and load balancing | 2 | 4 | 4 | 3 |
| 7. Open source and self-hostable | 5 | 5 | 5 | 5 |
| 8. Optional third-party provider fallback | 3 | 1 | 2 | 1 |
| **Total / 40** | **33** | **26** | **33** | **30** |

Scores are preliminary and should be revised when hands-on testing or additional configuration demonstrates different capabilities. The scores for third-party fallback reflect native integration, not whether an external proxy could be added.

## 4. Tool Evaluations

### 4.1 Ollama

**License:** MIT  
**Local inference:** Yes  
**OpenAI-compatible API:** Yes

**Pros**
- Simple installation and local model management.
- Straightforward model selection using model names.
- Native API for generation and model discovery.
- Docker-based deployment is convenient.
- Already tested successfully with Llama 3.2 and Qwen 2.5 1.5B in this project.

**Cons**
- Advanced routing, model pools, and load balancing may require additional infrastructure.
- Model loading and unloading behavior must be tested for the target workload.
- Production orchestration and high-throughput serving may need a separate routing layer.

**Assessment:** Best starting point for this prototype because it is already working and has a low setup burden.

Official references:
- https://ollama.com/
- https://docs.ollama.com/api/openai-compatibility
- https://github.com/ollama/ollama

### 4.2 vLLM

**License:** Apache 2.0  
**Local inference:** Yes  
**OpenAI-compatible API:** Yes

**Pros**
- Designed for efficient model serving and high-throughput workloads.
- Supports OpenAI-compatible inference endpoints.
- Offers batching and concurrency features suited to server deployments.
- Can be deployed on self-managed GPU infrastructure.

**Cons**
- Setup and resource requirements are generally more demanding than a lightweight local prototype.
- Serving and switching arbitrary model weights may require deployment or configuration changes.
- Multi-model routing, fallback, and balancing may require additional infrastructure.

**Assessment:** A strong candidate when throughput and GPU serving are more important than simple laptop-based model swapping.

Official references:
- https://docs.vllm.ai/en/latest/serving/openai_compatible_server/
- https://github.com/vllm-project/vllm

### 4.3 LocalAI

**License:** MIT  
**Local inference:** Yes  
**OpenAI-compatible API:** Yes

**Pros**
- Provides a unified API over multiple inference backends.
- Supports a broad range of model types and hardware configurations.
- Includes model management and configurable serving options.
- Can reduce application changes when replacing an OpenAI-compatible endpoint.

**Cons**
- Backend and model configuration can add operational complexity.
- Capabilities depend on the selected backend and model.
- Provider fallback and advanced load balancing should not be assumed without testing.

**Assessment:** A strong candidate when API compatibility and support for different local inference backends are priorities.

Official references:
- https://localai.io/docs/
- https://github.com/mudler/LocalAI

### 4.4 llama.cpp

**License:** MIT  
**Local inference:** Yes  
**OpenAI-compatible API:** Yes

**Pros**
- Efficient CPU and quantized-model inference.
- Supports a lightweight HTTP server.
- Provides OpenAI-compatible endpoints.
- Router mode supports dynamically loading and unloading models.
- Offers direct control over model files and serving configuration.

**Cons**
- More manual configuration may be required than with Ollama.
- Hardware-specific optimization and model compatibility require attention.
- Full production model pools, provider fallback, and load balancing may need extra components.

**Assessment:** Particularly interesting for investigating Docker-like model loading and unloading, especially with compatible GGUF models.

Official references:
- https://github.com/ggml-org/llama.cpp
- https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md

## 5. Fit With OmniRoute

The current project does not yet have a verified OmniRoute integration. The architecture below is therefore a proposal, not a confirmed deployment:

**Application → OmniRoute → Local model-serving backend → Local models**

Potential integration approaches:

1. Configure OmniRoute to route requests to an OpenAI-compatible local endpoint, if supported by the team's existing configuration.
2. Keep Ollama as the local inference backend for the initial integration test.
3. Evaluate LocalAI or llama.cpp router mode if more flexible backend selection or dynamic model loading is required.
4. Verify model aliases, routing behavior, errors, authentication, and compatibility with the actual OmniRoute implementation.

The precise OmniRoute repository, configuration format, and supported routing features must be confirmed with the team before selecting the final integration design.

## 6. Recommendation

Use **Ollama as the initial baseline** because it is already running and has been verified with two local models through both a Python client and a FastAPI service.

Evaluate **LocalAI** as an alternative for a unified API across different backends. Evaluate **llama.cpp router mode** specifically for dynamic model loading and unloading. Consider **vLLM** if the workload requires higher-throughput GPU serving.

No tool should be selected solely from the preliminary scores. The final decision should consider actual hardware, memory requirements, operational complexity, API compatibility, and measured behavior.

## 7. Remaining Validation

- [ ] Verify the exact OmniRoute implementation used by the team.
- [ ] Test end-to-end requests through OmniRoute to a local model.
- [ ] Verify whether changing a model requires a service restart.
- [ ] Test multiple model endpoints and model aliases.
- [ ] Evaluate fallback and load balancing.
- [ ] Record latency and resource usage if required.
- [ ] Update the scores using evidence from hands-on testing.

## 8. Conclusion

Ollama currently provides the simplest working baseline for local model selection in this project. LocalAI and llama.cpp deserve further investigation for broader backend support and dynamic model management, while vLLM is a candidate for performance-oriented serving.

The final recommendation depends on validating the required OmniRoute integration and the Docker-like model-swapping behavior against the DEV-875 acceptance criteria.

## 9. Hands-on Validation: Ollama Model Lifecycle

**Environment:** Existing Ollama Docker container with `qwen2.5:1.5b` and `llama3.2:latest`.

### Test Results

| Test | Result | Evidence |
|---|---|---|
| List locally available models | PASS | `docker exec ollama ollama list` showed both models |
| Generate a response with Qwen | PASS | Returned `QWEN_OK` |
| Verify Qwen is loaded | PASS | `GET /api/ps` listed `qwen2.5:1.5b` |
| Unload Qwen | PASS | Generate API returned `done_reason: unload` |
| Verify Qwen is unloaded | PASS | `GET /api/ps` returned an empty models list |
| Generate a response with Llama | PASS | Returned `LLAMA_OK` |
| Verify Llama is loaded | PASS | `GET /api/ps` listed `llama3.2:latest` |
| Unload Llama | PASS | Generate API returned `done_reason: unload` |
| Verify final cleanup | PASS | `GET /api/ps` returned an empty models list |

### Findings and Limitations

- Both local models successfully generated responses through the same Ollama service.
- A model could be unloaded without deleting its model files from disk.
- The model lifecycle was verified using Ollama's process-status API.
- This confirms sequential model loading and unloading, not zero-downtime hot-swapping.
- Concurrent requests were tested against the same Qwen model, but simultaneous multi-model serving and memory pressure were not tested.
- FastAPI sequential model selection was verified separately. Zero-downtime hot-swapping and end-to-end OmniRoute integration remain unverified.

### Updated Evaluation Status

Ollama has now been tested hands-on for CLI inference, model selection, FastAPI requests, and sequential model lifecycle operations. The evaluations of vLLM, LocalAI, and llama.cpp remain preliminary until equivalent hands-on tests are performed.

## 10. FastAPI Orchestration and API Validation

**Environment:** FastAPI on `127.0.0.1:8000`, backed by the existing Ollama service on port `11434`. Models tested: `qwen2.5:1.5b` and `llama3.2:latest`.

### Test Results

| Test | Result | Evidence |
|---|---|---|
| Health endpoint | PASS | `GET /health` returned HTTP 200 with service status `ok` |
| Model listing | PASS | `GET /models` returned HTTP 200 and listed both models |
| Qwen generation | PASS | Returned `QWEN_OK` and `SWITCH_QWEN_OK` |
| Llama generation | PASS | Returned `LLAMA_OK` and `SWITCH_LLAMA_OK` |
| Sequential model selection | PASS | Same `/generate` endpoint selected Qwen and Llama through the request `model` field |
| Invalid model | PASS | Returned HTTP 404 for `nonexistent-model:latest` |
| Empty prompt | PASS | Returned HTTP 422; minimum prompt length is enforced |
| Missing prompt | PASS | Returned HTTP 422 because `prompt` is required |
| Oversized prompt | PASS — Python-level validation | A 10,001-character prompt was rejected; maximum length is 10,000 |
| Concurrent requests | PASS | Two concurrent Qwen requests returned `CONCURRENT_A_OK` and `CONCURRENT_B_OK` |
| Malformed JSON | PASS | Returned HTTP 422 with a JSON decode error |
| Ollama connection failure | PASS — mocked | Mocked `URLError` caused `list_models()` to raise HTTP 503 |
| Temporary server cleanup | PASS | Server on port 8001 was stopped; main server on port 8000 remained running |

### Findings and Limitations

- Sequential model selection works without changing application code; the requested model is supplied in each request.
- Concurrent requests were tested only with Qwen. Simultaneous serving of different models was not tested.
- Oversized-prompt validation was tested directly against the Pydantic model, not through HTTP.
- Connection-failure behavior was tested with a mocked Python call, not by taking the actual Ollama service offline.
- An attempt to use FastAPI `TestClient` could not run because the installed Starlette test client requires `httpx2`. No dependency was installed; a mocked direct function call was used instead.
- Invalid-model errors are returned as HTTP 404, but the current `detail` contains a JSON-encoded error string that could be formatted more cleanly.
- Zero-downtime hot-swapping and end-to-end OmniRoute integration remain unverified.

### Remaining Work

- Confirm the team's exact OmniRoute repository and configuration.
- Test end-to-end requests through OmniRoute.
- Investigate aliases, fallback, load balancing, and service restart requirements.
- If hardware permits, test simultaneous different-model serving and record memory and latency.

### Validation Conclusion

The Ollama baseline and FastAPI model-selection path were exercised with both available local models. Basic request validation, invalid-model handling, concurrent same-model requests, and simulated connection failure were also checked. These tests do not prove zero-downtime hot-swapping, simultaneous multi-model serving, or completed OmniRoute integration.
