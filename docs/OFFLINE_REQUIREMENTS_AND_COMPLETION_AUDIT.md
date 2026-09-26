# Offline Requirements and Completion Audit

Audit date: 25 September 2026. Evidence basis: static source/configuration/model-path inspection plus the existing saved results. No models, tests, UI server, or API were launched; no exploit/runtime checks or internet verification were performed. Environment-generated Markdown under `.venv` and cache folders was excluded; the bundled MiniLM upstream model card was reviewed but preserved as third-party material.

## Required operating boundary

The project must operate completely offline. This is an explicit requirement, not an optional mode. The delivered workflow includes local installation from a prepared bundle, application startup, local document processing, local generation for the end-to-end demonstration, verification, browser UI, and export.

Allowed resources are locally supplied documents and passages, local databases or indexes, locally installed models and tokenizers, local packages, local static assets, and loopback service traffic. External claim searches, hosted model APIs, telemetry, remote fonts or scripts, licensing calls, and automatic downloads are excluded. Local network sharing is outside the initial single-machine target.

A release may be assembled separately using assets that are already available or obtained in a separate provisioning process, but the disconnected target must never need to download anything. Installation and runtime must be demonstrated from that bundle. A missing dependency must produce an actionable local error, never an online fallback.

No evidence means no factual verdict beyond insufficient evidence. Local retrieval may search a user-selected local corpus; it must never expand its scope to the web. Documents can be stale or wrong. Dates, versions, origins, and corpus boundaries must remain visible.

## What was observed

| Area | Evidence | Readiness |
|---|---|---|
| Embedding assets | MiniLM weight file 90,864,192 bytes plus tokenizer/config files | Present; isolated loading untested |
| NLI assets | DeBERTa weight file 737,722,356 bytes plus tokenizer/config files | Present; isolated loading untested |
| English NLP | en_core_web_sm 3.8.0 directory and package metadata in the inspected environment | Present locally; portable packaging untested |
| Core verification | Embedding, NLI, atomic and hybrid source paths | Prototype exists; semantic defects remain |
| Cache | In-memory dictionary and first-inserted eviction | Present; not demonstrated Redis or true LRU |
| API | Verify, HTML and health endpoint source | Present; startup untested |
| API dependencies | FastAPI/Uvicorn declared, absent from inspected site-packages listing | Environment gap to verify and repair |
| Adapter | LangChain-style callback stores query/chunks/result | Prototype; framework and concurrent-request behaviour untested |
| UI | Static generated sentence cards and a saved report | Output view only |
| Generator | Demo uses a fixed response and fixed chunks | No end-to-end local generator integration found |
| Evidence ingestion | API accepts supplied text chunks | File library, extraction and local retrieval not implemented in inspected flow |
| Evaluation | 40 local examples and saved four-mode results | Preliminary; provenance and fair comparisons unresolved |
| Release | Loose dependency minimums and a machine-specific virtual environment | Disconnected installation not demonstrated |

The two weight files total 828,586,548 bytes, approximately 790 MiB. This excludes tokenizers, Python, libraries, the spaCy model, any generator, documents, indexes and runtime memory. Do not present this number as total installation size or RAM use.

## Concrete offline blockers

1. Both model paths select online identifiers if local directories are absent. Explicit local-only loading and complete asset checks remain to be implemented.
2. The HTML renderer and saved report include Google Fonts links. A fallback font may keep text readable, but external requests still violate the requirement.
3. Dependency installation is not captured as a complete offline bundle. A virtual environment pointing to a machine-specific Python installation is not a portable release.
4. The HTML renderer interpolates untrusted strings without HTML escaping. The API uses wildcard CORS with credentials enabled and includes raw exception details in HTTP 500 responses; the source does not establish a loopback-only launch configuration.
5. The local spaCy model is available on this machine but not yet established as part of a reproducible package. Silent reduced-function fallbacks must not claim full atomic verification.
6. API documentation assets require inspection and local hosting or removal from the delivered offline UI. No successful docs-page test has been performed.
7. No local answer generator is integrated in the inspected demonstration. Prewritten answer verification is useful, but does not demonstrate an offline RAG application.
8. No network-disabled end-to-end acceptance record exists. Local asset presence alone cannot certify offline operation.

## How much remains

A single precise completion percentage would be misleading: old checklist items tracked file creation, whereas the revised requirement includes working offline delivery, correct verdict semantics, and an usable UI. The core prototype is substantially started; the finished offline product is not close to completion merely because all algorithm files exist.

The following is a planning estimate for one developer already familiar with Python and a local web UI. It is not a measured project schedule. It assumes one operating system, English text, text-based PDFs, a small corpus, modest local hardware, and no cloud services.

| Work package | Remaining work | Focused developer days |
|---|---|---:|
| Offline packaging and startup | Bundle dependencies/models; remove remote fallbacks/assets; local readiness checks | 3–5 |
| Verification semantics and correctness | Verdict separation, conflict detection, guards, eligibility, explanations, failure handling | 5–8 |
| Local evidence workflow | TXT/Markdown/text-PDF import, extraction preview, provenance, chunking, bounded local lookup | 3–5 |
| Complete UI | Input flow, corpus view, claim/evidence review, status states, export, accessibility | 6–9 |
| Local generator and adapter integration | One local RAG example, request isolation, exact evidence association, display order | 3–5 |
| Evaluation and regression coverage | Provenance, held-out data, local baselines, ablations, score analysis, latency and offline checks | 5–8 |
| Release verification and documentation | Disconnected-machine rehearsal, packaging fixes, usability review, final report alignment | 2–4 |
| **Total remaining** | **Sequential planning range, not a commitment** | **27–44 days** |

This is approximately 6–9 full-time working weeks after rounding up. Student part-time availability will extend calendar duration. Model compatibility, local generator speed, dataset annotation and unavailable package bundles can increase the estimate. Document editing completed now does not count as implementation completion. Work packages share dependencies; do not subtract time merely because their names appear separable.

OCR, multilingual verification, arbitrary mathematical reasoning, broad multi-document inference, desktop installers for multiple operating systems, token streaming, and general-purpose autonomous agents are outside this estimate.

## Required completion gates

- **G1 Local installation:** install from the supplied release medium on a clean disconnected target with empty relevant model caches; record exact versions, checksums and asset sources.
- **G2 No external traffic:** start, import, generate, verify, inspect and export with external networking denied; record attempted outbound requests as well as successful traffic. Loopback is allowed.
- **G3 Missing assets:** remove or corrupt a required asset in a disposable test copy; show a local corrective message and no download attempt.
- **G4 Verdict integrity:** pass targeted cases for support, contradiction, absent evidence, conflict, nonclaims, uncertainty and unchecked processing.
- **G5 Evidence integrity:** associate claims with the correct source version and request; record whether evidence was supplied to the generator or added by later local lookup.
- **G6 UI usability:** complete the whole workflow without developer tools; show claim details, exceptions, keyboard navigation and offline exports.
- **G7 Local RAG:** use a local generator and local corpus; ensure the middleware result reaches the user at the documented point in delivery.
- **G8 Evaluation:** reproduce held-out results and component comparisons using only locally runnable methods; retain failure counts and uncertainty.
- **G9 Release honesty:** publish supported findings only; mark limitations and unsupported features accurately.

## Priorities

First agree the verdict contract and local evidence boundary. Next address offline blockers and verification correctness. Then build the UI and integrate one local generator. Complete isolated evaluation and disconnected installation tests before describing the project as finished.

The current change is documentation only. All gates remain open until implementation and execution evidence establish otherwise.
