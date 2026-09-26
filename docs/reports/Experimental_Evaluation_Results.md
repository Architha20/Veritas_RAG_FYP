# Preliminary Results and Offline Evaluation Plan

Updated 25 September 2026. This report supersedes the earlier external-superiority and publication-readiness claims. No experiments were executed in the documentation audit.

## Evidence available

The existing benchmark JSON records four local verification modes on 40 examples: 20 grounded and 20 hallucinated. The dataset's benchmark-name fields do not by themselves establish extraction from the original published records. Provenance, modifications and development/test separation need documentation.

| Method | Accuracy | Precision | Recall | F1 | TP | FP | FN | TN | Mean ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Embedding | 52.50% | 55.56% | 25.00% | 34.48% | 5 | 4 | 15 | 16 | 67.3 |
| Sentence NLI | 97.50% | 95.24% | 100.00% | 97.56% | 20 | 1 | 0 | 19 | 304.8 |
| Atomic | 90.00% | 83.33% | 100.00% | 90.91% | 20 | 4 | 0 | 16 | 387.8 |
| Hybrid | 90.00% | 83.33% | 100.00% | 90.91% | 20 | 4 | 0 | 16 | 554.2 |

The positive class in this preliminary binary evaluation is hallucinated. The harness maps several output conditions to a binary flag. This does not evaluate the newly required distinctions among contradiction, insufficient evidence, conflict and operational uncertainty.

Sentence NLI is the strongest method on the saved aggregate metrics. The hybrid may offer finer explanations, but this set does not demonstrate a detection advantage. Zero misses among 20 labelled examples is not a universal recall guarantee. The recorded averages are not P95 latency, streaming delay or disconnected-system performance.

## Results withdrawn from supported findings

The Vectara, Ragas, GPT-4 and AlignScore entries are constants in the harness, not locally executed baselines on the same examples. Do not infer performance or speed superiority from them. Their numerical provenance has not been validated here.

The older paper ablation table includes a full-hybrid F1 of 95.2%, inconsistent with the saved 90.91%. The inspected harness does not produce the claimed component-removal experiments. The ablation figures and claims of measured component benefits are withdrawn until configuration-specific data and reproducible runs exist.

Other unsupported hardware-specific speed and memory statements from earlier drafts are not retained as findings. The report does not establish actual runtime memory, GPU latency, statistical significance or production suitability.

## Offline experimental contract

All required evaluation runs must execute locally with no internet calls. Use pre-provisioned datasets, tokenizers, models and metric dependencies. External URLs in bibliographic references are identifiers, not runtime inputs.

Select locally executable comparators after compatibility, licensing and resource checks. Candidate families include another locally runnable grounding classifier or alignment metric; selection does not imply those models are currently bundled. Cloud-only judges are excluded. An unavailable comparator should be reported as not run, never replaced with a literature number in the measured-results table.

## Data and labels

Retain original source-record IDs, dataset version, source documents, transformation history and annotation rationale. Describe custom examples as custom. Keep source-related variants within the same split to reduce contamination. Freeze a held-out set before rule or threshold tuning is complete.

Build labels for supported, contradicted, insufficient evidence, conflicting evidence and nonclaims. Record uncertain annotations rather than forcing agreement. Operational errors are run outcomes, not ground-truth semantic labels. Use independent review where feasible and document disagreements.

Include natural generator errors and targeted examples for negation, quantities, aliases, source dates, missing context, mixed claims, cross-passage reasoning and long evidence. A balanced binary demonstration suite alone does not establish realistic deployment performance.

## Required comparisons

Compare sentence NLI, NLI with guard, atomic verification without guard, and full hybrid. Keep inputs, data split, hardware and timing boundaries consistent. Label heuristic thresholds explicitly and tune them only on development data.

Measure response-level and claim-level detection, false-positive burden, evidence attribution, decomposition fidelity, explanation usefulness and coverage. Evaluate conflict detection and missing-evidence classification separately. If confidence calibration is claimed, measure it on held-out data and report error among accepted claims at different coverage levels.

## Failure handling and reproducibility

Fix the harness exception path before reporting new runs. A failed example must not reuse the preceding result. Save raw verdicts, binary mappings when used, per-example errors and the chosen failure accounting policy. Report evaluated coverage and failures alongside metrics, including any excluded examples.

Record dataset and model checksums, dependency versions, settings, device, input-size distribution, cache conditions, timing boundaries and run repetitions. Separate startup from warmed inference. Measure median and P95 latency, resource use and concurrent-request behaviour where relevant.

## Offline and UI tests

Perform clean disconnected installation with empty relevant model caches. Deny external network access and observe attempted requests during startup, document import, local generation, verification, result drilldown and export. Localhost is permitted. Test missing assets, unsupported documents and timeouts.

Test that displayed verdicts and evidence agree with the machine-readable result, that atomic details appear, and that result state becomes stale after input changes. Reopen HTML exports offline and inspect them for external asset dependencies and unsafe source-text rendering.

## Publication boundary

Until these experiments exist, report this work as a prototype with preliminary local results and a planned offline evaluation. Use the project issue register and acceptance gates as limitations. A strong final report can explain why a simpler NLI method performs better; it need not claim hybrid superiority.
