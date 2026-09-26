# Second Review Presentation Content

Revised 25 September 2026. Mandatory condition: complete offline operation. This is presentation content only; the existing PPTX files are unchanged.

## Slide 1 Title and accurate status

VeritasRAG Offline Evidence Grounding Middleware.

Status: verification prototype with a documented offline completion plan. Do not use production ready, all phases completed or publication ready.

## Slide 2 What the system checks

The system checks whether generated factual claims are supported by identified local evidence. It can expose wrong numbers, relation reversals and unsupported additions. It does not certify world truth, source freshness, relevance or completeness.

No internet search, cloud judge, runtime download or remote UI asset is allowed. Missing local evidence is a valid unresolved outcome.

## Slide 3 Offline architecture

Local documents and index feed a local retriever and generator. The application supplies the exact answer and evidence snapshot to the verifier. Local NLI and other verification paths produce verdicts and evidence for the local browser UI.

Manual pasted-answer verification is also supported by the target design. Additional selected-corpus lookup is local and visibly distinct from original-context checking.

## Slide 4 Existing prototype and gaps

| Area | Present | Still needed |
|---|---|---|
| Models | MiniLM, DeBERTa and local parser assets | Portable local-only loading and missing-asset handling |
| Verification | Embedding, NLI, atomic and hybrid source | Correct verdicts, conflicts, guards and explanations |
| Service | API source and callback prototype | Installed local service, real integration and request isolation |
| UI | Generated sentence report | Input flow, corpus management, atomic review, states and export |
| Demo | Fixed response and passages | One locally generated answer workflow |
| Evaluation | Saved 40-case results | Provenance, fair local baselines, ablations and offline acceptance |

## Slide 5 Required user interface

Show the planned workflow: readiness, local evidence selection/import, answer or query input, verification, claim/evidence drilldown and offline export.

Text labels accompany colours. Distinguish supported, contradicted, insufficient evidence, conflicting evidence, not evaluated, uncertain and unchecked. Show source versions, coverage and failures. A large average score must not conceal a flagged claim.

## Slide 6 Preliminary results

| Method | Saved F1 | False positives | Recorded mean latency |
|---|---:|---:|---:|
| Embedding | 34.48% | 4 | 67.3 ms |
| Sentence NLI | 97.56% | 1 | 304.8 ms |
| Atomic | 90.91% | 4 | 387.8 ms |
| Hybrid | 90.91% | 4 | 554.2 ms |

Set size: 40, with 20 labels in each binary class. These are existing saved figures, not a current rerun. NLI and hybrid each have zero misses among the 20 labelled hallucinated cases. Do not generalize this to guaranteed recall.

## Slide 7 What the results do not show

External baseline scores in the harness are constants, not comparable local runs. Earlier unsupported ablation figures are withdrawn from the findings. The dataset's provenance and independence remain to be established.

The hybrid's potential benefit is explanation granularity or particular error categories, not demonstrated aggregate superiority. Detection and explanation quality need separate measurements.

## Slide 8 Offline risks and acceptance

Local models alone do not establish offline readiness. Remote fallback identifiers, Google Fonts and a nonportable dependency setup remain. FastAPI/Uvicorn were absent from the inspected environment listing, though declared dependencies.

Show a clean disconnected install, no external traffic, controlled missing assets, all verdict cases, source/request association, UI usability, local RAG and reproducible evaluation. Refer to gates G1–G9 in [the audit](../OFFLINE_REQUIREMENTS_AND_COMPLETION_AUDIT.md).

## Slide 9 Remaining plan

Estimated remaining effort: 27–44 focused developer days, about 6–9 full-time weeks under the stated scope. Prioritize offline packaging and verdict correctness, then local evidence/UI and generator integration, followed by evaluation and release rehearsal.

OCR, multilingual operation, multi-platform installers, broad reasoning and verified token streaming are excluded from the initial estimate. Documentation completion is not implementation completion.

## Slide 10 Demo script for the completed system

Start disconnected. Import local evidence and inspect extraction. Generate an answer locally or use a labelled fixture. Inspect one supported claim, one contradiction and one missing-evidence claim. Show a source conflict and a forced verification failure. Export and reopen the report offline.

Do not present this script as executed until the working system passes it. Existing slide decks require a separate authorized update after final results exist.

## Supporting material

- [Architecture](../architecture.md)
- [UI requirements](../UI_REQUIREMENTS.md)
- [Issue register](../DESIGN_ISSUES_AND_RESOLUTIONS.md)
- [Evaluation report](Experimental_Evaluation_Results.md)
- [Task board](../../tasks.md)
