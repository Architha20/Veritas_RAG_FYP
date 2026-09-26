# VeritasRAG Offline Architecture

Updated 25 September 2026. This document distinguishes inspected implementation from the required target. No architecture change described here has been implemented by this documentation update.

## System responsibility

VeritasRAG checks factual claims against supplied local evidence. It does not independently establish world truth, source authenticity, answer completeness or currentness. Missing knowledge remains insufficient evidence. The verifier must never search the internet or call a cloud model.

The complete delivery uses a local browser, loopback service, local models and local evidence. A locally provisioned generator is required for the end-to-end RAG demonstration. Manual answer verification remains a useful separate mode.

## Observed implementation

| Component | Current behaviour | Remaining limitation |
|---|---|---|
| Middleware | Splits response; dispatches embedding, NLI, ensemble, atomic or hybrid | Query stored but not used for relevance checking; completed responses only |
| Embeddings | MiniLM claim/chunk similarity | Similarity is not entailment; absent model directory selects remote identifier |
| NLI | DeBERTa chunk/claim pairs, batched with 512-token limit | Missing-evidence conflation, truncation and source-conflict policy |
| Atomic path | Syntactic heuristics, conjunction splitting, within-chunk windows, NLI plus guard | Meaning preservation and complex inference not established |
| Hybrid | Sentence NLI plus atomic results through shared aggregator | Correlated model errors; no proven improvement over NLI |
| Guard | Entity aliases and numeric presence/approximation penalties | Substrings, unit loss, broad aliases and unrelated numbers |
| Cache | Local dictionary with first-inserted eviction | Not Redis, distributed caching or true access-based LRU |
| Output | Pydantic data, JSON and HTML sentence cards | Missing operational states, atomic UI and contradictory citations |
| API | Health, JSON verification and HTML routes | Wildcard CORS, raw exception detail, loopback launch not established; startup and offline delivery not verified |
| Adapter | Captures query, documents and generation result | Real framework compatibility and request isolation unverified |

The actual hybrid does not run an independent three-model voting system. It reuses the NLI model in both paths, and the atomic path applies the entity guard. Algorithm scores and thresholds are heuristics until evaluated and, if claimed, calibrated.

## Target local data flow

1. The user selects a local corpus or supplies explicit passages.
2. In manual mode, the user supplies the answer. In local RAG mode, local retrieval supplies passages to a local generator.
3. The application records a request ID, original answer and exact evidence snapshot.
4. The verifier identifies eligible factual claims while retaining links to original text.
5. It checks claims against bounded local evidence, preserving support and contradiction separately.
6. It reports verdicts, reasons, coverage and operational status.
7. The UI presents claim-level evidence and exceptions; exports contain the same result.
8. Any additional local lookup is explicit and labelled as evidence added after generation.

The generator and verifier have different responsibilities. The verifier's MiniLM and DeBERTa weights do not supply answer generation. The local generator must be selected after hardware and asset availability are assessed.

## Two evidence modes

**Generation-context faithfulness:** check only the passages recorded as supplied to the generator. This identifies claims that deviate from the provided context.

**Selected-corpus support:** allow additional search of a user-selected local collection. An answer can be supported by that collection while still having been unsupported by the original generation context. Preserve that distinction in the result rather than silently upgrading faithfulness.

No corpus selection means no broader lookup. Do not treat the entire user filesystem as permission to search. No local support means insufficient evidence, never an external fallback.

## Target result contract

Each result should identify the request, answer, mode, corpus/evidence version, verifier version and model versions. Each claim should retain original text/spans, factual-check eligibility, verdict, reason, supporting and contradicting evidence references, and whether evidence came from generation context or later local lookup.

Required evidence verdicts are supported, contradicted, insufficient evidence, conflicting evidence, not evaluated and uncertain. Operational status must separately represent checked, partial, failed, timed out or otherwise unchecked content. The precise schema remains to be implemented.

Sources should preserve local document ID, original origin when known, version/date, extraction location and import time. Imported file timestamps are not publication dates. Missing metadata remains unknown.

## Aggregation and explanation

Present per-claim verdicts and coverage first. Counts may summarize an answer; an average support score must not imply truth or safety. Preserve a material contradiction even if many other claims are supported.

For source disagreement, compare applicability to entity, attribute, date and conditions. Return conflict unless documented precedence resolves it. Do not simply select the highest entailment score.

For uncertain decomposition, reasoning beyond supported capability, or incomplete context processing, retain the original sentence and explain the limitation. Do not force uncertainty into a plausible-inference label.

## Offline deployment

The intended release contains the runtime, complete dependencies, local model/tokenizer/parser assets, local generator assets for the demo, locally served UI resources and local evaluation fixtures. It must install and start with external networking disabled and relevant caches empty.

The existing model-saving script is a provisioning helper, not a disconnected installer. Current model loader fallbacks, remote HTML fonts and any externally hosted API-doc assets require correction. Use local-only loading with explicit asset checks. Review optional library network behaviour and telemetry through no-network testing. The generated HTML interpolates untrusted values without escaping; API CORS is wildcarded and HTTP 500 responses expose exception text. Escape rendered values, restrict the local UI origin, return safe errors, and bind the launcher explicitly to loopback.

Bind services to loopback for the initial single-machine deployment. Cloud hosting, external vector services, Redis clusters, Celery, GPU worker pools, remote dashboards and production monitoring platforms are not implemented requirements. Add complexity only when a measured need justifies it.

## UI and delivery

The target UI is defined in [UI requirements](UI_REQUIREMENTS.md). Completed-answer annotation is the initial delivery design. A result shown before checking finishes must be labelled unchecked. Strict pre-display protection requires explicit application gating and timeout policy; the current callback does not establish that behaviour.

All user and source text must be safely rendered as text. Reports must be self-contained and never automatically fetch remote assets or source URLs. Exports should preserve verdicts and evidence without requiring internet access.

## Validation

Use gates G1–G9 in [the completion audit](OFFLINE_REQUIREMENTS_AND_COMPLETION_AUDIT.md). Include local asset failure, evidence absence/conflict, interleaved requests, long inputs, claim mapping, offline export and local generation. Architecture drawings and file existence do not substitute for execution evidence.
