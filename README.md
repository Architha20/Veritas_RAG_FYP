# VeritasRAG Offline Evidence Grounding Middleware

Reviewed 25 September 2026 against the current source tree. The review inspected project-owned Markdown (excluding virtual-environment/cache/vendor-generated files), Python source, project configuration, model asset paths, and the saved benchmark artifact. It did not run the application or tests.

VeritasRAG checks generated factual claims against evidence available on the local machine. The required finished system must work completely offline, including model loading, evidence processing, verification, the user interface, exports, and an end-to-end local demonstration.

**Current status: working verification prototype with substantial correctness, offline packaging, UI, integration, and evaluation work remaining.** The project is not complete or demonstrated production ready. This documentation update does not implement the planned changes.

## Scope and boundaries

The system checks support relative to supplied local evidence. It cannot discover facts absent from that evidence, determine current world truth without a current local source, or guarantee that a source is correct. Missing evidence must produce an insufficient-evidence result. It must never trigger an internet search or cloud-model fallback.

Model-independent means that an application can pass an answer and its evidence through a common contract. For the delivered offline demonstration, generation must also use a locally provisioned model. MiniLM and DeBERTa are verification models; neither is a general answer generator.

Localhost communication between the browser and the local service is permitted. External network services, cloud APIs, remote fonts, CDNs, telemetry, and runtime downloads are not part of the permitted operation. Installation on a disconnected target must be possible from a prepared local bundle.

## What exists

- Python middleware with embedding, sentence NLI, atomic, ensemble, and hybrid verification paths.
- Local MiniLM and DeBERTa weight and tokenizer files.
- spaCy English model files in the inspected virtual environment.
- Structured result models, an in-memory embedding cache, and a generated HTML sentence report.
- FastAPI endpoint source, a LangChain-style callback, tests, and a saved 40-example evaluation.

Existence is not the same as validated completion. The cache does not implement a demonstrated Redis deployment, and its inspected eviction is insertion-order rather than a true access-updated LRU. The hybrid reuses the same NLI model across sentence and atomic paths. A LlamaIndex adapter was not found.

## Offline and UI blockers

Model loaders can fall back to remote model identifiers; local-only failure behaviour is not enforced. The HTML renderer and saved demo report request Google Fonts. The installed virtual-environment directory listing did not contain FastAPI or Uvicorn, although both are declared dependencies; no API startup was attempted. A portable dependency bundle and clean-machine installation evidence were not found.

The current HTML is a generated report, not a complete application. It lacks a verification input workflow, local evidence management, atomic claim drilldown, distinct missing-evidence and failure states, and a full offline local-generator demonstration. The renderer interpolates answer, query, source IDs, evidence excerpts, and title into HTML without escaping; the current API enables wildcard CORS and returns exception text to callers. These are security and deployment gaps before exposing it beyond a trusted local prototype. UI assets and any API documentation assets need a no-network audit.

## Recorded preliminary results

These figures come from the existing JSON artifact and were not rerun during this audit. The local set has 20 grounded and 20 hallucinated labels; provenance and test independence still need to be established.

| Method | F1 | False positives | False negatives | Recorded mean latency |
|---|---:|---:|---:|---:|
| Embedding | 34.48% | 4 | 15 | 67.3 ms |
| Sentence NLI | 97.56% | 1 | 0 | 304.8 ms |
| Atomic | 90.91% | 4 | 0 | 387.8 ms |
| Hybrid | 90.91% | 4 | 0 | 554.2 ms |

Sentence NLI is stronger than the hybrid on this set. The external baseline values in the existing harness are hard-coded literature numbers, not measurements on these examples. Do not use them to claim superiority. Unreproduced ablation figures from earlier drafts have been withdrawn from the findings.

## Documentation map

- [Offline requirements and completion audit](docs/OFFLINE_REQUIREMENTS_AND_COMPLETION_AUDIT.md): binding offline condition, inventory, remaining effort, acceptance gates.
- [UI requirements](docs/UI_REQUIREMENTS.md): screens, states, local evidence workflow, and accessibility.
- [Design issues and resolutions](docs/DESIGN_ISSUES_AND_RESOLUTIONS.md): all previously identified issues and offline treatments.
- [Architecture](docs/architecture.md): observed implementation and target design.
- [Task board](tasks.md): remaining work, deliberately left unchecked until implemented and verified.
- [Evaluation report](docs/reports/Experimental_Evaluation_Results.md): saved results and the replacement experiment plan.
- [Literature review](docs/reports/LITERATURE_REVIEW.md): research context and offline applicability.

## Running and delivery status

The present source contains a Python SDK, demo entry point, and API routes. A verified offline installation and launch procedure is still to be produced. The model-saving utility can obtain models by online identifiers and is not an offline installer. Do not rely on a pre-existing machine cache as release evidence.

The completed release must include local assets, dependency versions and permitted redistribution information, clear missing-asset errors, a tested loopback-only launch path, hardened HTML/API handling, and successful verification/UI checks with external networking disabled. No implementation code was changed in this documentation pass.
