# Offline User Interface Requirements

Reviewed 25 September 2026 against the renderer and API source. Status: target design and gap assessment; no UI code changed.

## Purpose and current state

The user must be able to submit or generate an answer locally, identify the permitted local evidence, run verification, and understand each result without reading JSON or using developer tools.

The existing renderer provides generated sentence cards, score display, and supporting excerpts. It is useful as an output prototype, but it is not a full verification workspace. It requests Google Fonts, omits the atomic claim breakdown, and lacks local document management, input controls, error workflows and a local generator interaction. A saved HTML demo is not a live application.

Use a browser application served on loopback as the recommended initial design. Bundle all UI assets or use system fonts. Do not require online accounts, API keys, remote icons, analytics or CDN packages. This design is a recommendation; a specific frontend framework is not prescribed.

## Screen 1 Local readiness

Show whether the verifier assets, English parser, local service and optional selected generator are available. Distinguish installed, loading, unavailable and failed. “Assets present” must not be presented as proof that the no-network acceptance test has passed.

Missing model or dependency messages must name the local asset needed and its expected location or import action. There must be no download button or automatic external fallback in the delivered offline workflow. Offer the manual verification workflow when a generator is absent, while clearly stating that the end-to-end generator demonstration is unavailable.

## Screen 2 Verification workspace

Provide two paths: paste/import an existing answer for verification, or ask a question of the selected local corpus using the integrated local generator. The first is the simpler initial implementation; both are needed for the planned final demonstration.

The workspace should include a question field, answer area, selected evidence/corpus summary, explicit evidence scope, verification action, progress indicator and result summary. A method selector may be placed in advanced controls. Default selection should follow held-out evaluation, not assume hybrid superiority.

An empty answer should produce a validation message. An answer without evidence may still be inspected, but its unsupported factual claims must not be declared false. If no corpus is selected, do not search all user files automatically.

When evidence or answer text changes, mark earlier results as stale and require a new verification. Keep the original answer alongside the checked result.

## Screen 3 Local evidence library

Initial supported imports: pasted passages, TXT, Markdown and text-based PDF. Each file type remains planned until its parser, failure states and packaging are verified. Image-only PDFs must show that OCR is unsupported in the first release; they must not silently become empty evidence. DOCX and OCR are optional later additions.

Show filename, document identity, available source/version/date, import time, extraction preview, processing status and selected corpus membership. A file timestamp is not automatically the publication date or proof of currency. Let the user correct metadata and review extraction before indexing.

Handle empty, corrupt, unsupported and duplicate documents. Removing a source or changing the corpus must invalidate dependent results or clearly retain them as historical snapshots. Keep documents and indexes local. Saved history, if provided, should be optional with an explicit clear-history action.

Evidence obtained by later local search must be labelled separately from the exact passages supplied to the generator. The user should know whether the test asks “faithful to the supplied context” or “supported somewhere in the selected corpus.”

## Screen 4 Claim and evidence review

Show the original answer with selectable sentence or claim markers. Selecting a claim should reveal the claim text, verdict, reason, evidence excerpts, source name and available page/section locator. Preserve offsets to the original displayed answer; normalization must not highlight the wrong text.

Use text and icons as well as colour. Required verdict presentation:

| State | What the user should understand |
|---|---|
| Supported | This local evidence supports the claim |
| Contradicted | This local evidence conflicts with the claim |
| Insufficient evidence | The selected evidence does not settle the claim |
| Conflicting evidence | Applicable sources disagree |
| Not evaluated | This text was outside the factual checking scope |
| Uncertain | The checker could not reliably choose a verdict |
| Unchecked | Verification failed, timed out or did not cover this content |

For contradictions, show the conflicting passage. For source disagreement, show both sides. For atomic verification, expose the actual claim breakdown; do not reduce it to sentence colour alone.

Present counts of each verdict and coverage before any average support score. A percentage must not imply probability of truth or safety. One problematic central claim must remain prominent even among many supported background sentences. Never use “verified true” as a synonym for source support.

## Screen 5 Export and review

Export JSON and a self-contained HTML report containing the answer, verdicts, evidence references, corpus/version identifiers where available, selected method, relevant model versions, checking coverage, timing and operational status.

The HTML export must open on a disconnected machine without external resources. Escape user and document content so it is displayed as text rather than executed as markup. Do not auto-open external links. A source's original URL may remain inert provenance information; it is not a runtime evidence retrieval mechanism.

PDF export is optional and not part of the initial UI estimate. Persisted history is optional; export and a temporary session are sufficient initially.

## Interaction and failure requirements

Escape user answers, queries, evidence, source labels, and titles before inserting them into HTML. The local API must use an explicit allowed-origin list, safe error messages, bounded request sizes, and a loopback-only launch configuration. Verify these safeguards with hostile markup, oversized input, and failed-request cases.

The initial delivery model is completed-answer verification. If the answer is displayed before checking finishes, label it unchecked. A protected display mode must withhold the answer until verification or an explicit failure decision. Token-by-token verified streaming is not promised.

Display loading, success, no evidence, uncertain, partial coverage, cancelled if supported, timeout and internal failure states. Do not leave a previous result looking current after a failed request. Large inputs need explicit limits and visible truncation or rejection; silent incomplete checking is unacceptable.

Restrict the local API/UI to the intended machine, maintain request isolation, and avoid exposing raw exception internals as the only user message. Broad cross-origin access and non-loopback binding need review before release.

## UI acceptance walkthrough

1. Start disconnected with local assets; confirm all screens load without external requests.
2. Import supported files and review extracted text; select the evidence boundary.
3. Paste an answer, then run the local-generator path on a separate example.
4. Inspect support, contradiction, missing evidence and conflicting evidence examples.
5. Open atomic details and navigate to the correct original source location.
6. Change the source or answer; verify stale results are not represented as current.
7. Trigger a missing asset, malformed document, oversized input and verification failure.
8. Complete the same essential workflow using a keyboard, with readable text at increased zoom.
9. Export and reopen a report offline; verify no remote assets or active untrusted markup.
10. Confirm the final result includes the exact evidence/request association and visible unchecked portions.

All of these are required future checks, not tests performed during this documentation update.
