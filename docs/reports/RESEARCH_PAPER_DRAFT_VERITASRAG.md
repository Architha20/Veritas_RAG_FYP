# VeritasRAG Offline Evidence Grounding and Claim Review

Authors: Final Year Project Team; author and affiliation details pending. Revised 25 September 2026. Status: unpublished project manuscript draft. No acceptance, publication readiness or completed offline validation is claimed.

## Abstract

We describe a prototype for checking generated text against supplied local evidence and a target offline workflow for claim-level review. The implementation includes embedding similarity, sentence natural language inference, atomic decomposition with numerical/entity heuristics, and a hybrid of sentence and atomic verification. Local model assets and generated sentence reports exist, but complete offline packaging, UI interaction, verdict semantics and end-to-end local generation remain under development.

Saved results on 40 local examples record 97.56% hallucination F1 for sentence NLI and 90.91% for the hybrid. These preliminary results do not establish hybrid superiority. The paper's intended contribution is an evaluated offline workflow with evidence attribution, explicit uncertainty and usable claim inspection. This manuscript defines the work and experiments still needed to support that contribution.

## 1 Problem and operating boundary

The task is source-relative support assessment, not universal factual truth. A generator may misstate supplied passages; a verifier can identify that mismatch. Correctness, freshness and completeness of the sources remain separate concerns.

All runtime components must operate locally. External search, cloud inference, remote UI assets, telemetry and automatic dependency/model downloads are excluded. When a fact is absent from local evidence, the system reports insufficient evidence. Any local corpus update is a separately supplied input, not automatic web verification.

## 2 Related work

RAG supplies the evidence-conditioned generation setting. Sentence-BERT motivates semantic matching, DeBERTa provides background for the NLI model family, and FActScore motivates smaller claim units. RAGTruth, HaluEval and FaithBench inform evaluation design. RAGAs, SelfCheckGPT, Self-RAG, CRAG and SAFE provide alternative evaluation or intervention perspectives.

Methods with external search or hosted inference are discussed as background, not adopted as runtime requirements. The [literature review](LITERATURE_REVIEW.md) retains the research catalogue. No claim that all other systems lack claim explanations or that this is the first such system is made.

## 3 Task definition

Inputs are an answer, optional question, evidence passages, request identity and evidence provenance. The target output includes eligible claims, verdicts, supporting and contradicting evidence, checking coverage and operational status.

Supported, contradicted, insufficient evidence, conflicting evidence, not evaluated and uncertain have separate meanings. Unchecked identifies processing that did not produce a verdict. A score is a model-derived support signal unless empirical calibration establishes a narrower probabilistic interpretation.

Generation-context faithfulness uses the passages originally supplied to the generator. Optional selected-corpus support uses additional local retrieval and must be identified separately.

## 4 Current method

The embedding path computes semantic similarity between sentences and chunks. The NLI path evaluates passage/claim pairs using local DeBERTa assets and a 512-token input limit. Atomic verification uses syntactic heuristics and conjunction splitting, evaluates full chunks and short within-chunk windows, and applies entity/numerical penalties.

The hybrid combines sentence NLI and atomic outputs through an aggregator. Both use the same underlying NLI verifier. The implementation is a correlated ensemble of processing paths, not independent confirmation or multimodal input processing.

Heuristic checks currently have weaknesses involving substring numbers, unit/subject association, aliases, conditions and decomposition fidelity. The corrected method must preserve applicable contradictions, evidence locations, unsupported claims and operational errors. The proposed UI exposes those distinctions locally.

## 5 Preliminary observations

The existing evaluation set has 40 records with 20 grounded and 20 hallucinated labels. Original-record mappings, transformations and test independence are not established by the reviewed materials.

| Method | Accuracy | Precision | Recall | F1 | Recorded mean ms |
|---|---:|---:|---:|---:|---:|
| Embedding | 52.50% | 55.56% | 25.00% | 34.48% | 67.3 |
| Sentence NLI | 97.50% | 95.24% | 100.00% | 97.56% | 304.8 |
| Atomic | 90.00% | 83.33% | 100.00% | 90.91% | 387.8 |
| Hybrid | 90.00% | 83.33% | 100.00% | 90.91% | 554.2 |

These numbers are taken from a saved artifact, not rerun in this revision. They support only a preliminary within-set comparison. NLI has one false positive and hybrid four; each detects the 20 labelled hallucinated cases. Explanation benefit has not been quantified.

## 6 Comparative and ablation study status

No external comparator was executed by the reviewed harness on these examples. Hard-coded literature values are excluded from the measured-results table.

The earlier manuscript's ablation numbers, including 95.2% full-hybrid F1, are withdrawn from findings because they conflict with the main saved result and lack matching configuration-specific experiment artifacts in the inspected materials. No component benefit is inferred from them.

The required study compares sentence NLI, NLI plus guard, atomic without guard and full hybrid, using fixed local inputs and held-out data. At least one additional locally executable comparator should be selected if feasible; record why unavailable methods were not run. Cloud-only judges are outside the offline evaluation.

## 7 Evaluation protocol

Preserve dataset versions, original IDs, transformations and annotation rules. Group related sources across splits and separate threshold/rule development from final evaluation. Include natural local-generator errors and targeted difficult cases.

Report detection by verdict and claim, false-positive burden, evidence attribution, decomposition errors, explanation usefulness, abstention and coverage. Count failures explicitly. Fix exception handling before collecting new metrics.

Measure startup and warm inference, median and P95 latency, input-size scaling, hardware, memory and cache conditions. Do not infer complexity or throughput solely from fixed-size sample timings. Complete no-network installation, runtime, UI and export checks.

## 8 User interface and offline delivery

The present HTML report is an output prototype. The target interface adds local readiness, answer/query entry, local evidence management, claim/evidence drilldown and self-contained exports. All assets are local and source text is rendered safely.

A local generator and retriever must be integrated for the final offline RAG demonstration. The existing fixed-response demo is not equivalent. A protected output mode requires actual display gating; post-generation annotation alone does not prevent exposure before verification.

## 9 Limitations and intended contribution

The system cannot verify knowledge absent from its local corpus, certify source truth or currentness, or guarantee arbitrary reasoning. Shared model errors, source conflict, decomposition errors and incomplete processing require visible handling. Hardware constrains the local generator and latency.

The intended contribution is a reproducibly evaluated offline checking and review workflow. Whether the hybrid improves particular error categories or user explanations remains an empirical question. A simpler model may remain the preferred detector.

## References and supporting material

Use the paper catalogue in [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md) and verify formal bibliographic details against retained papers before submission. FaithBench's 2024 preprint and NAACL 2025 conference publication should not be conflated.

The [evaluation report](Experimental_Evaluation_Results.md), [offline audit](../OFFLINE_REQUIREMENTS_AND_COMPLETION_AUDIT.md), [architecture](../architecture.md) and [UI specification](../UI_REQUIREMENTS.md) define the current evidence and planned completion work.
