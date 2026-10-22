# DEV-875: Final Recommendation — Local LLM Orchestration & Model-Swapping

## 1. Executive Summary

The goal of DEV-875 is to identify an open-source, self-hosted solution that allows applications to switch between locally hosted language models without changing application code.

Based on the current research and hands-on tests, **Ollama is the recommended starting point for the team's local model-serving baseline**. It provides simple model management, local inference, and a consistent API for selecting different models.

The project also integrates FastAPI with OmniRoute and Ollama. Qwen 2.5 1.5B inference works through the complete request pipeline. Llama 3.2 3B is configured but has experienced intermittent inference failures.

The evaluation of vLLM, LocalAI, and llama.cpp remains preliminary because these tools have not been installed and tested hands-on in this project.

## 2. Requirements

The solution is evaluated against the eight Docker-like model-swapping criteria:

1. **Local-first inference:** Models run on infrastructure controlled by the team.
2. **Swap without rewriting:** Model selection does not require application-code changes.
3. **Consistent interface:** Applications use a common interface regardless of the selected model.
4. **One interface, multiple models:** A common API can expose multiple local models.
5. **Hot-swapping:** Models can be switched without rebuilding the entire application stack.
6. **Model groups and pools:** Multiple models can be grouped for aliases, fallback, or load balancing.
7. **Open source:** The solution is open source and self-hostable.
8. **Optional third-party fallback:** External providers may be used as an optional fallback, not as the primary serving architecture.

## 3. Comparison Matrix

Scores range from 1 (poor) to 5 (excellent). The scores below are preliminary qualitative assessments, not benchmark results.

| Criterion | Ollama | vLLM | LocalAI | llama.cpp |
|---|---:|---:|---:|---:|
| 1. Local-first inference | 5 | 5 | 5 | 5 |
| 2. Swap without application-code changes | 5 | 3 | 4 | 4 |
| 3. Consistent interface | 5 | 3 | 4 | 3 |
| 4. One API for multiple local models | 4 | 3 | 5 | 4 |
| 5. Hot-swapping and lifecycle | 4 | 2 | 4 | 5 |
| 6. Model groups, pools, aliases, and balancing | 2 | 4 | 4 | 3 |
| 7. Open source and self-hostable | 5 | 5 | 5 | 5 |
| 8. Optional third-party fallback | 3 | 1 | 2 | 1 |
| **Total / 40** | **33** | **26** | **33** | **30** |

**Important:** These totals are preliminary qualitative assessments based on research and the limited hands-on evidence available. They are not benchmark results or proof that any tool meets every requirement. Ollama has hands-on evidence from this project; vLLM, LocalAI, and llama.cpp remain research-based candidates. The optional-fallback scores reflect the current evaluation's assessment of native integration, not the ability to add an external proxy.

## 4. Tool Assessments

### 4.1 Ollama

**License:** MIT  
**Evaluation status:** Hands-on testing completed for the baseline workflow.


**Advantages**
- Simple local model installation and management.
- Model selection through model names.
- Local inference and model discovery APIs.
- Docker deployment is straightforward.
- Supports an OpenAI-compatible API.

**Limitations**
- Advanced routing and model pools may require an additional component.
- Sequential loading and unloading does not prove zero-downtime hot-swapping.
- Runtime stability depends on available hardware resources.
- Production load balancing and multi-model serving require further evaluation.

**Recommendation:** Use Ollama as the initial local inference backend because it is the most thoroughly tested option in this project.

Official references:
- https://ollama.com/
- https://docs.ollama.com/api/openai-compatibility
- https://github.com/ollama/ollama

### 4.2 vLLM

**License:** Apache 2.0  
**Evaluation status:** Research only; hands-on validation pending.

**Advantages**
- Designed for efficient model serving and high-throughput workloads.
- Supports an OpenAI-compatible API.
- Provides batching and concurrency capabilities.
- Suitable for self-managed GPU infrastructure.

**Limitations**
- Typically requires more demanding infrastructure than a lightweight laptop-based setup.
- Changing the served model may require configuration changes or restarting a serving process.
- Multi-model routing and fallback may require additional orchestration.

**Recommendation:** Evaluate vLLM when GPU-backed throughput and serving performance are more important than simple local model management.

Official references:
- https://docs.vllm.ai/en/latest/serving/openai_compatible_server/
- https://github.com/vllm-project/vllm

### 4.3 LocalAI

**License:** MIT  
**Evaluation status:** Research only; hands-on validation pending.

**Advantages**
- Provides a unified API across supported inference backends.
- Supports different model types and hardware configurations.
- Offers configurable model-serving options.
- Can reduce application changes when replacing compatible model endpoints.

**Limitations**
- Backend and model configuration can introduce operational complexity.
- Capabilities vary by backend and model.
- Advanced fallback and load balancing need verification against the intended configuration.

**Recommendation:** Evaluate LocalAI when a unified API across multiple local inference backends is a priority.

Official references:
- https://localai.io/docs/
- https://github.com/mudler/LocalAI

### 4.4 llama.cpp

**License:** MIT  
**Evaluation status:** Research only; hands-on validation pending.

**Advantages**
- Supports efficient CPU and quantized-model inference.
- Provides a lightweight HTTP server.
- Exposes OpenAI-compatible endpoints.
- Router mode can dynamically load and unload supported models.
- Offers direct control over model files and serving configuration.

**Limitations**
- More manual configuration may be required.
- Model formats and hardware optimizations need attention.
- Production model pools, fallback, and load balancing may require additional components.

**Recommendation:** Evaluate llama.cpp router mode specifically for dynamic model loading and unloading, especially when GGUF models are suitable.

Official references:
- https://github.com/ggml-org/llama.cpp
- https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md

## 5. Current Architecture

The prototype uses the following request flow:

`Client → FastAPI → OmniRoute → Ollama → Selected Local Model`

FastAPI provides a simple application-facing API. OmniRoute handles the configured model-routing layer, while Ollama serves the local models.

Current endpoints:

- `GET /health` — checks API service health.
- `GET /models` — lists configured supported models.
- `POST /generate` — generates a response using the selected model.

Configured models:

- `ollama/qwen2.5:1.5b`
- `ollama/llama3.2:latest`

Model selection is supplied through the request's `model` field. The application can therefore select a configured model without changing the API implementation.

## 6. Hands-On Evidence

### Verified results

- Ollama model discovery and local inference were tested.
- Sequential loading and unloading of Qwen and Llama were previously successful.
- FastAPI model listing and request validation were tested.
- Qwen inference through FastAPI and OmniRoute succeeded.
- Three sequential Qwen requests passed.
- Three concurrent Qwen requests passed.
- Unsupported model requests and empty prompts were rejected.
- An upstream Llama inference failure was surfaced by FastAPI as HTTP 502.

### Limitations

Llama 3.2 3B inference has intermittently failed with:

`llama-server process has terminated: signal: killed`

Docker Desktop memory pressure is a plausible contributing factor, but the exact cause has not been confirmed.

The current tests do not establish:
- Zero-downtime hot-swapping.
- Simultaneous inference across different models.
- Production-scale model pooling or load balancing.
- Successful fallback between local models.
- Hands-on equivalence of vLLM, LocalAI, or llama.cpp.

Qwen is the currently validated model for the complete FastAPI-to-OmniRoute-to-Ollama request path.

## 7. Final Recommendation

### Recommended starting point: Ollama

Ollama is the most practical starting point for the current prototype because it is already integrated and has the strongest hands-on evidence in this project.

Use FastAPI as the application's stable interface and OmniRoute as the configured routing layer. Keep model selection in configuration or request parameters rather than hard-coding model-specific application logic.

### Alternatives to investigate

- **LocalAI:** Investigate if supporting multiple local inference backends through a unified API becomes the primary requirement.
- **llama.cpp:** Investigate if dynamic model loading and unloading are the most important requirements.
- **vLLM:** Investigate if the workload moves toward GPU-backed, high-throughput serving.

These are conditional recommendations based on the current research, not the outcome of equivalent hands-on benchmarks.

No tool has yet been proven to satisfy all eight requirements in the team's target environment. The final production choice should follow additional validation against the actual hardware and OmniRoute configuration.

## 8. Remaining Work

- [ ] Confirm that the team's intended OmniRoute implementation and configuration match the working prototype. Investigate the intermittent Llama runtime failure.
- [ ] Verify model aliases and model selection across the intended deployment.
- [ ] Test switching models without rebuilding the application stack.
- [ ] Evaluate model pools, fallback, and load balancing.
- [ ] Test at least one alternative serving tool hands-on if required by the epic.
- [ ] Verify all license and capability claims against the official references.
- [ ] Update preliminary scores when additional evidence is available.
- [ ] Review every DEV-875 sub-task and confirm its documentation is complete.

## 9. Conclusion

Ollama currently offers the simplest validated baseline for local model serving in this project. FastAPI and OmniRoute provide a common request path for configured local models, with successful end-to-end Qwen inference.

The remaining work is to validate the unresolved model-switching and routing requirements, investigate Llama runtime stability, and decide whether alternative serving tools need hands-on testing before the final production recommendation.

This document distinguishes current test evidence from preliminary research and should be updated as the remaining validation work is completed.

## Retest Update — 2026-10-22

Both Qwen and Llama returned successful responses through FastAPI → OmniRoute → Ollama. Llama also failed intermittently with `signal: killed`. After Qwen was unloaded, Llama direct inference and the end-to-end API request succeeded. This is consistent with possible memory pressure, but the root cause is unconfirmed. Zero-downtime switching, simultaneous multi-model serving, and repeated switching reliability remain unverified.
