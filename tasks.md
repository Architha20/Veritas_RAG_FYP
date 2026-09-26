# VeritasRAG Offline Completion Task Board

Reviewed 25 September 2026 against source, configuration, assets, and saved results. The offline requirement is mandatory. This board replaces the earlier all-phases-completed statement. Checkboxes below are intentionally open until implementation and execution evidence support completion.

## Existing starting point

The repository contains local verifier weights, a local English parser installation, verification source, an in-memory cache, output models, report rendering, API source, an adapter prototype, tests and a saved 40-case evaluation. These are reusable foundations, not evidence that the complete offline application is finished.

## P0 Scope and evidence contract

- [ ] Adopt the source-relative promise and prohibit external claim verification.
- [ ] Define supported, contradicted, insufficient evidence, conflicting evidence, not evaluated, uncertain and unchecked.
- [ ] Separate evidence verdicts from operational status and checking coverage.
- [ ] Associate request, answer, original generation context and optional later local evidence.
- [ ] Define source quality/version ownership and selected local-corpus boundaries.
- [ ] Select completed-answer delivery and explicit timeout/failure behaviour.
- [ ] Record unsupported modalities, languages, OCR and complex reasoning limits.

## P0 Offline runtime and packaging

- [ ] Inventory complete model/tokenizer/parser assets, versions, checksums and licenses.
- [ ] Enforce local-only model loading and remove remote-name fallback behaviour.
- [ ] Fail clearly when assets are missing or incompatible; never download automatically.
- [ ] Prepare a reproducible local Python/dependency bundle, including API dependencies.
- [ ] Package the English parser rather than relying on this machine's environment.
- [ ] Remove remote fonts/assets from the renderer and reports.
- [ ] Audit API documentation, dependency telemetry and UI requests; bundle or disable remote assets.
- [ ] Provide a local launch path bound to loopback.
- [ ] Pass clean disconnected installation and empty-cache startup checks.

## P0 Verification correctness

- [ ] Treat no evidence as insufficient evidence rather than confident hallucination.
- [ ] Detect applicable source conflicts and retain both supporting and contradicting evidence.
- [ ] Distinguish nonfactual statements and mixed factual/advisory sentences.
- [ ] Correct quantity matching for units, magnitudes, signs, boundaries, entities and time.
- [ ] Replace overly broad entity aliases with justified, context-sensitive matching.
- [ ] Evaluate decomposition for negation, conditions, shared subjects, dropped facts and pronouns.
- [ ] Handle unsupported combined-evidence reasoning explicitly.
- [ ] Preserve exact evidence locators and original answer offsets where supported.
- [ ] Keep support scores separate from unvalidated truth probabilities.
- [ ] Make truncation, incomplete processing and unavailable NLP capability explicit.
- [ ] Prevent a high average from concealing problematic claims.

## P1 Local evidence and UI

- [ ] Implement the local readiness view and verification input workflow.
- [ ] Support pasted evidence and reviewed TXT/Markdown/text-PDF import.
- [ ] Add extraction previews, document IDs, available dates/versions and corpus selection.
- [ ] Provide bounded local lookup without internet or automatic whole-disk search.
- [ ] Show answer highlights, atomic claims and evidence drilldown.
- [ ] Implement every verdict and operational state with text labels, not colour alone.
- [ ] Mark results stale after answer or corpus changes.
- [ ] Add local JSON and self-contained HTML exports.
- [ ] Escape untrusted content and test keyboard navigation, zoom and long text.
- [ ] Restrict API CORS to the intended local UI origin, avoid returning internal exception details, and bound request/input sizes.
- [ ] Test malformed files, duplicates, unsupported scans, oversized inputs and service failures.

## P1 Local RAG and application integration

- [ ] Select a locally runnable generator according to available hardware and permitted assets.
- [ ] Integrate one local corpus, retriever and generator with the verifier.
- [ ] Keep the fixed-response demo labelled as a fixture, not live generation.
- [ ] Validate the actual framework callback interface or use a tested direct integration.
- [ ] Isolate interleaved requests and retain the exact corresponding evidence.
- [ ] Verify display order and protected-delivery behaviour if provided.
- [ ] Do not advertise additional adapters until implemented and tested.

## P1 Evaluation and research evidence

- [ ] Fix benchmark exception handling so old results cannot be reused.
- [ ] Record original dataset identifiers, transformations, labels and source-group splits.
- [ ] Separate rule/threshold development from untouched test examples.
- [ ] Evaluate locally executable baselines on identical examples; exclude cloud-only evaluation dependencies.
- [ ] Run NLI, NLI plus guard, atomic without guard and full hybrid component comparisons.
- [ ] Measure claim localization and explanation quality in addition to detection.
- [ ] Report failed/unchecked examples, coverage, uncertainty and error breakdowns.
- [ ] Measure cold/warm median and tail latency, input-size scaling and memory on specified hardware.
- [ ] Run targeted regression checks for offline, verdict, source, UI and integration failures.
- [ ] Replace preliminary results only after reproducible runs exist.

## P2 Release and final review

- [ ] Complete gates G1 through G9 in the offline completion audit.
- [ ] Rehearse support, contradiction, missing evidence, conflict and failure scenarios disconnected.
- [ ] Finalize the offline installation, operation and troubleshooting guide.
- [ ] Align all reports and presentation content with verified results.
- [ ] Preserve acceptance logs and asset provenance in the final deliverable.
- [ ] Claim project completion only after the complete UI and local pipeline pass.

## Planning range and boundaries

Estimated remaining effort is 27–44 focused developer days, approximately 6–9 full-time weeks, under the assumptions in [the audit](docs/OFFLINE_REQUIREMENTS_AND_COMPLETION_AUDIT.md). This is a planning range, not a measured completion percentage.

The documentation review and revision were checked against the current source tree on 25 September 2026. That does not close any implementation item above. Existing Python, HTML, configuration, model files, datasets and slide decks were not modified in this documentation-only task.
