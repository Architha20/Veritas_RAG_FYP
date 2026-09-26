# Project Report Draft Chapters 1 and 2

## VeritasRAG Offline Evidence Grounding Middleware

Course: CB23721. Department: Computer Science and Engineering. Revised 25 September 2026. Team and supervisor details remain to be completed by the project team. This is a revised draft, not evidence of submission or approval.

## Chapter 1 Introduction

### Background

Generated answers can misstate evidence even when the relevant documents are available. A verifier can help a user inspect whether a claim is supported by selected sources, contradicted by them, or unresolved. This is distinct from establishing independent world truth.

The project must work completely offline. It therefore relies on local documents, local models and local software. A missing fact cannot be sought on the internet. The correct behaviour is to make the evidence limitation visible.

### Problem statement

Design an offline middleware and user interface that connect an answer to its local evidence, identify factual claims, report support and disagreement, and communicate uncertainty and processing failures without overstating confidence.

The middleware must integrate with a local RAG example and also allow direct verification of supplied text. It requires an application that can expose the answer and corresponding evidence. It cannot attach to an arbitrary inaccessible chatbot and reconstruct unseen context.

### Objectives

1. Define a source-relative contract and explicit evidence/operational verdicts.
2. Preserve existing embedding, NLI and atomic prototypes while correcting known semantic and numeric failure cases.
3. Build an usable local interface for evidence selection, answer input, claim review and export.
4. Integrate one local generator and local corpus with request-bound evidence.
5. Package all required assets for disconnected installation and operation.
6. Evaluate detection, explanation, coverage, latency and offline behaviour reproducibly.
7. Report limitations and results without unsupported superiority claims.

These are target objectives. They are not completed merely because relevant modules exist.

### Scope

The initial target is English text, one operating system, a small selected local corpus, pasted passages, TXT/Markdown and text-based PDF import, completed-answer verification, JSON export and self-contained HTML export. Localhost communication is allowed.

A complete demonstration uses a locally provisioned generator. Model choice and resource limits remain to be decided based on available hardware. The existing fixed-answer demo is a fixture rather than a full RAG integration.

Excluded initial capabilities are internet verification, cloud APIs, runtime downloads, token-level verified streaming, multilingual support, scanned-document OCR, arbitrary mathematical proof, broad multimodal checking and deployment across multiple operating systems.

### Limitations

A locally supported statement can still be wrong because its source is wrong or stale. The verifier does not establish answer completeness or relevance. Claims requiring unsupported combined-evidence reasoning must remain uncertain or insufficiently supported. Model agreement is not independent confirmation when both paths reuse the same NLI model.

The offline condition limits knowledge to the imported evidence snapshot. Manual source updates are allowed; automatic online refresh is not part of operation.

### Current status and completion

A verification prototype, local assets and generated sentence report exist. Complete UI, offline packaging, semantic corrections, local generator integration and defensible evaluation remain. The audit estimates 27–44 focused developer days under a bounded single-machine scope; this is a planning estimate rather than a completion measurement.

## Chapter 2 Literature Survey

### Research foundation

RAG separates a model's generated answer from an evidence collection. Sentence embeddings support semantic matching; natural language inference models compare a premise and claim; atomic factual evaluation motivates inspecting smaller assertions. RAG failure analyses help distinguish absent knowledge, retrieval failures and generation errors.

The retained paper catalogue and qualified summaries are maintained in [the literature review](LITERATURE_REVIEW.md). That review replaces earlier universal statements about competitor limitations and project novelty.

### Offline relevance

Methods involving external search can inform the design but cannot be adopted as runtime dependencies. Locally executable verifiers and locally stored evaluation data are suitable candidates only after package, model and resource checks. A tool that permits a local model configuration is not automatically installed or tested in this repository.

Source-relative support should remain separate from source authority, currentness, correctness, relevance and completeness. A three-colour display cannot replace those distinctions.

### Research questions

- Does sentence NLI provide a stronger local detection baseline than embedding similarity?
- Do quantity/entity checks improve relevant error categories without excessive false positives?
- Does atomic decomposition improve explanation and localization while preserving meaning?
- Can the complete local UI help users identify the reason for a flag?
- What are the accuracy, coverage and latency tradeoffs under disconnected operation?

### Evaluation approach

Use locally provisioned data with traceable provenance and separated development/test groups. Run local baselines and component comparisons on identical examples. Record errors and exclusions. Measure explanations, checking coverage and uncertainty alongside detection.

The saved 40-example results are preliminary. Sentence NLI records 97.56% F1 and hybrid 90.91%; this does not establish general superiority, universal recall or a calibrated score. The full evaluation protocol is in [the evaluation report](Experimental_Evaluation_Results.md).

### Proposed contribution

The defensible contribution is an evaluated offline evidence-grounding workflow with claim-level explanations and explicit failure boundaries. The project does not need an unsupported claim of being the first or best system to provide a useful engineering result.

## Document relationship

[The consolidated report](PROJECT_REPORT_COMPLETE_CH1_TO_CH5.md) summarizes all six chapters. [The architecture](../architecture.md), [UI requirements](../UI_REQUIREMENTS.md), [issue register](../DESIGN_ISSUES_AND_RESOLUTIONS.md) and [task board](../../tasks.md) contain the implementation boundaries and remaining work. Original drafts are preserved in the documentation revision backup; this rewrite does not alter submitted slide decks or PDFs.
