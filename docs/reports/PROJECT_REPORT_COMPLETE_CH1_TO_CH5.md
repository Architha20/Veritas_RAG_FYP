# VeritasRAG Consolidated Project Report

## Offline Evidence Grounding Middleware

Course: CB23721. Department: Computer Science and Engineering. Academic year: 2026–2027. Revised 25 September 2026. Team names, roll numbers, institution and supervisor details require project-team completion.

Status: revised six-chapter draft. The legacy filename is retained for compatibility; neither the filename nor this document establishes project completion.

## Abstract

VeritasRAG is a prototype middleware for checking generated factual claims against supplied evidence. The revised project requires a complete offline workflow: local models, local evidence processing, local generation for an end-to-end demonstration, a local browser interface and disconnected installation. Its purpose is to explain support and disagreement relative to identified sources, not to establish universal truth.

The repository contains embedding, sentence NLI, atomic and hybrid verification paths and preliminary results on 40 local examples. Saved hallucination F1 is 97.56% for sentence NLI and 90.91% for the hybrid. These results favour the simpler method on this set, while the possible explanation benefits of decomposition need separate measurement. Dataset provenance, fair local baselines, component comparisons and offline acceptance testing remain incomplete.

## Chapter 1 Introduction

The problem is the gap between fluent generated text and inspectable evidence. Even with correct passages, a generator can change dates, reverse relations or add unsupported details. A checker can expose such mismatches while acknowledging that the source itself may be wrong.

The offline requirement is mandatory. No cloud model, web search, runtime download, remote font or CDN is allowed in the operating workflow. Localhost communication is allowed. Missing local knowledge remains insufficient evidence.

Objectives include correct verdict meanings, traceable evidence, an usable UI, one complete local RAG integration and reproducible evaluation. The project does not claim relevance/completeness checking, source authentication or general mathematical reasoning.

## Chapter 2 Literature Context

The project draws on RAG, sentence representations, NLI, atomic factual evaluation, hallucination taxonomies and failure analysis. The paper catalogue is preserved in [the literature review](LITERATURE_REVIEW.md).

Research methods using internet search are background only. Locally executable variants and datasets must be provisioned before disconnected use. Literature numbers cannot be compared directly with this project's local scores as evidence of superiority. Novelty and universal competitor limitations have not been established.

## Chapter 3 System Architecture

The target flow is local corpus selection, optional local generation, answer/evidence snapshot, factual-claim identification, verification, evidence-preserving aggregation, UI review and local export.

Manual verification accepts an answer with local passages. Local RAG mode uses a separately provisioned generator and retriever. The verifier's existing MiniLM and DeBERTa assets are not answer-generation models.

Generation-context faithfulness and support from later local-corpus search are separate modes. The result must identify which evidence was available to the generator and which was added afterward.

Target verdicts distinguish supported, contradicted, insufficient evidence, conflicting evidence, not evaluated and uncertain. Operational status separately identifies unchecked or incomplete processing. The average score is not a probability of truth.

## Chapter 4 Implementation and UI Status

Existing code includes the Python middleware, four principal verification approaches, an in-memory embedding cache, Pydantic output models, API route source, a callback prototype and an HTML sentence report.

The hybrid combines sentence NLI with atomic verification that reuses the same NLI model and applies a heuristic guard. It is not an independent three-model confirmation system. Numeric substring matching, broad aliases, decomposition semantics, source conflict, evidence loss and error handling require correction.

The current UI does not provide a full input and evidence workflow. Required screens cover readiness, verification, local corpus management, claim/evidence drilldown and export. The report's external fonts must be removed, all statuses made visible and user/source text rendered safely.

Local model and English parser files are present, but no disconnected installation or network-disabled end-to-end test was performed in this audit. FastAPI/Uvicorn were not found in the inspected virtual-environment package listing despite being declared. A portable dependency bundle and tested API launch are still required.

## Chapter 5 Preliminary Results and Evaluation

| Method | Saved F1 | False positives | False negatives | Saved mean latency |
|---|---:|---:|---:|---:|
| Embedding | 34.48% | 4 | 15 | 67.3 ms |
| Sentence NLI | 97.56% | 1 | 0 | 304.8 ms |
| Atomic | 90.91% | 4 | 0 | 387.8 ms |
| Hybrid | 90.91% | 4 | 0 | 554.2 ms |

These are existing saved results on 20 grounded and 20 hallucinated labels, not newly reproduced findings. They do not validate the expanded verdict taxonomy, calibration, production reliability or full offline operation.

The external baseline table in the harness uses constants. Earlier ablation values lack matching supporting artifacts and conflict with the main result; they are not retained as established findings.

Required work includes provenance, grouped development/test separation, local comparators, component removals, explanation assessment, failure/coverage reporting, hardware-specific latency and resource measurement, UI testing and disconnected installation. See [the evaluation plan](Experimental_Evaluation_Results.md).

## Chapter 6 Remaining Work and Conclusion

The prototype is worth developing, but complete offline operation and the user interface remain substantial deliverables. The planning range is 27–44 focused developer days under the scope and assumptions in [the completion audit](../OFFLINE_REQUIREMENTS_AND_COMPLETION_AUDIT.md).

Completion requires gates G1–G9: disconnected installation, no external traffic, controlled asset failure, correct verdicts, evidence/request integrity, usable UI, local RAG, reproducible evaluation and accurate reporting.

Potential educational or societal usefulness is a motivation, not measured prevention of medical, legal or other real-world harm. The final contribution should be stated in terms of demonstrated support checking, explanations and operating limitations.

## Supporting documents

- [Introduction and literature chapters](Project_Report_Draft_Ch1_Ch2.md)
- [Architecture](../architecture.md)
- [UI specification](../UI_REQUIREMENTS.md)
- [Issue resolutions](../DESIGN_ISSUES_AND_RESOLUTIONS.md)
- [Task board](../../tasks.md)

This is a documentation revision only. Implementation, models, datasets and presentation files were not changed.
