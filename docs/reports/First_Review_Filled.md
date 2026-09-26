# First Review Content with Offline Scope Revision

Course: CB23721. Department: Computer Science and Engineering. Revised 25 September 2026. This content updates the project narrative; it does not retrospectively assert approval or alter the existing Review I slide deck.

## Slide 1 Project title

VeritasRAG Offline Evidence Grounding Middleware.

Insert verified team, institution and supervisor details. Describe the submission as a prototype plus offline completion plan.

## Slide 2 Problem and purpose

Generated text can misstate local documents. Users need to inspect which factual claims are supported, contradicted or unresolved. The project checks source-relative faithfulness and does not establish universal truth.

The full project must work without internet access. Evidence, verification models, generator for the end-to-end demo, UI assets and dependencies must be local. Missing knowledge produces insufficient evidence.

## Slide 3 Research context

Discuss RAG, semantic embeddings, NLI, atomic factual evaluation and hallucination benchmarks. Use [the literature review](LITERATURE_REVIEW.md) for the retained catalogue.

Research involving online search is background only. Avoid claiming that every competing tool is coarse, slow or incapable of explanations. No state-of-the-art superiority is established.

## Slide 4 Proposed system

A local application supplies the answer and exact generation evidence. The verifier identifies factual claims, checks support and contradiction, preserves sources and returns a structured result. A browser served on localhost shows claims and evidence.

A second explicitly labelled mode may search additional passages in a selected local corpus. It must not be confused with faithfulness to the generator's original context.

## Slide 5 Work currently present

- Local MiniLM and DeBERTa assets and a local spaCy model installation.
- Embedding, sentence NLI, atomic and hybrid verification source.
- Result models, in-memory cache, API source and callback prototype.
- Generated sentence-level HTML report.
- A 40-example local dataset and saved results.

These are source-inspection findings, not a fresh successful offline test run. The existing demo uses fixed text rather than a local generator.

## Slide 6 Unresolved issues

Missing evidence is conflated with hallucination; source conflict is not fully implemented; numerical matching and decomposition need correction. The current renderer lacks atomic drilldown and requests remote fonts.

Offline dependency packaging, API startup, local evidence import, complete UI and real local RAG integration remain. All original design concerns are tracked in [the issue register](../DESIGN_ISSUES_AND_RESOLUTIONS.md).

## Slide 7 Preliminary evaluation

Report saved NLI F1 of 97.56% and hybrid F1 of 90.91% on the 40-example set, clearly labelled preliminary and not rerun. NLI performs better on aggregate F1 and recorded latency here.

Do not compare these values with hard-coded literature scores as proof of superiority. Provenance, held-out testing and local component comparisons are pending.

## Slide 8 Plan and effort

The completion plan covers local packaging, verification corrections, evidence handling, the full UI, one local generator integration, evaluation and release testing. Planning estimate: 27–44 focused developer days under the bounded scope in [the audit](../OFFLINE_REQUIREMENTS_AND_COMPLETION_AUDIT.md).

The old calendar milestones are superseded by acceptance gates. State required outcomes rather than marking all phases complete.

## Slide 9 Demonstration and acceptance

Demonstrate support, numerical contradiction, missing evidence, conflicting sources, mixed claims and a controlled failure. Show actual evidence and checking status. The final walkthrough must run disconnected, including startup, local generation, verification and export.

Explain that local source freshness is limited to imported versions. Do not imply real-world harm prevention has been established.

## Slide 10 References and next decisions

Use the retained paper catalogue and locally stored PDFs; bibliography identifiers are not runtime network dependencies. Settle verdict semantics, evidence boundaries, local generator/hardware selection and delivery policy before implementation.

See [the task board](../../tasks.md) and [UI requirements](../UI_REQUIREMENTS.md). This Markdown revision adds no implementation code.
