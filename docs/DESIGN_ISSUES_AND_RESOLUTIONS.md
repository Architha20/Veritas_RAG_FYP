# Design Issues and Offline Resolutions

Reviewed 25 September 2026 against the current source tree. The completely offline requirement is confirmed by the project owner. Resolutions below are required or recommended future behaviours, not claims of implementation.

## Operating promise

Check generated factual claims relative to explicitly selected local evidence. No internet searches, cloud verification, runtime model downloads or remote UI assets are permitted. If the local evidence cannot settle a claim, the correct outcome is a visible limitation.

Offline operation does not remove the need for evidence. It changes the allowed evidence boundary. It also means fresh information cannot be discovered until someone imports updated local sources.

## Issue register

| ID | Issue and current gap | Offline resolution | Acceptance evidence |
|---|---|---|---|
| I01 | Needing documents appears to defeat independent checking | Compare answer with local evidence; distinguish model independence from evidence independence | Same verifier accepts two local-generator outputs; missing evidence is explicit |
| I02 | Missing evidence becomes confident hallucination | Separate insufficient evidence from contradiction | Same claim tested with support, contradiction, unrelated and absent passages |
| I03 | Sources may be wrong or outdated | Record source origin/version/date and application responsibility; no automatic freshness claim | Old/new source scenario with visible versions |
| I04 | Conflicting sources can be hidden by best-match support | Preserve both sides and produce conflict absent justified precedence | Genuine conflict and different-date/product nonconflict cases |
| I05 | Support may require combining separate passages | Bound combined-evidence reasoning; abstain beyond capability; use only selected local passages | Valid and misleading two-passage inferences evaluated separately |
| I06 | Grounded answers can be irrelevant or incomplete | State that relevance and completeness are separate; do not imply they were checked | Supported off-topic answer and omitted-qualification scenario |
| I07 | Questions, advice and hypotheticals are treated as facts | Identify eligible claims and not-evaluated text; preserve factual premises in mixed sentences | Pure nonclaims and mixed factual/advisory examples |
| I08 | Model confidence and hybrid agreement can overstate certainty | Call values support scores; recognize shared NLI errors; calibrate only with held-out local data if claimed | Error by score range, abstention rate and coverage |
| I09 | Streaming can expose an answer before checking | Completed-answer annotation first; show unchecked status or gate display explicitly | Observe display order and forced failure/timeout |
| I10 | Any-model integration assumes context access | Require request-bound text and evidence; demonstrate one local RAG integration | Exact evidence snapshot and interleaved-request isolation |
| I11 | Red labels lack actual contradicting evidence; atomic details are not shown | Preserve reasons, contradictory citations, claim breakdown and source location | User can inspect what the answer says and what the source says |
| I12 | Average score hides an important error | Show claim problems and coverage before averages | One contradiction remains prominent among many supported claims |

I01 is the original evidence-dependency concern. I02–I12 correspond to the eleven subsequent design gaps.

## Additional implementation corrections

**Numbers and entities.** Numeric substring and digit-only matches can confuse 500 with 5000, ignore units or associate a value with the wrong subject. Overly broad aliases also require correction. Test signs, scales, units, strict/inclusive comparisons, entity/date binding and alias ambiguity. Searching more local documents cannot fix an incorrect matching rule.

**Decomposition.** Conjunction splitting can lose negation, conditions or subjects. Preserve mappings to original text and evaluate omitted or altered claims. A missing local parser must produce a capability error or clearly reduced mode, not a claim that full atomic checking happened.

**Long inputs.** NLI truncation and candidate growth need explicit limits and coverage reporting. Evaluate supporting evidence near the end of long passages, long individual sentences and growing chunk counts. No online service may be used to bypass local limits.

**Failure handling.** The benchmark can inspect an undefined or previous result after an exception. Correct request/result isolation and explicitly count failures. UI state must not retain an earlier successful result as if it belongs to a failed new request.

**Packaging.** Local weights are present, but remote-name fallback, external fonts and missing portable dependencies remain. A clean disconnected installation test is required. Asset absence must not trigger network access.

**Local generator.** The existing demo supplies fixed answers and passages. Integrate a separately provisioned local generator and retriever for the final complete demonstration. Keep fixture verification available but label it accurately.

## Evaluation and academic corrections

The saved evaluation uses 40 local examples with 20 labels in each binary class. Provenance and independent test status remain unresolved. NLI F1 is 97.56%; hybrid F1 is 90.91%. The hybrid has four false positives against NLI's one, with no false negatives for either on this small set. These are preliminary saved results, not new observations.

External baseline values are hard-coded in the harness and were not produced on the same examples. Remove superiority claims. Choose locally executable baselines, provision them locally and evaluate identical held-out inputs. Cloud-only judges are excluded from the required evaluation; their literature results may be discussed without calling them.

Earlier paper ablation values, including a 95.2% full-hybrid F1, conflict with the saved main result and lack supporting per-configuration artifacts in the inspected materials. Treat the ablation study as pending. Do not infer actual contribution of guards or windows from those numbers.

Preserve dataset IDs, source versions, transformation steps, annotation guidelines and grouped development/test splits. Measure detection, explanation quality, coverage and latency separately. The existence of paper drafts does not mean publication readiness, and no conference acceptance is assumed.

## Security and service boundary findings

The current HTML renderer inserts query text, answer sentences, evidence excerpts, chunk IDs, and the title directly into markup. Treat all of these as untrusted and escape them for HTML text/attribute contexts before rendering. Add regression cases containing markup and script-like strings. The API currently configures wildcard CORS with credentials enabled and returns raw exception text in HTTP 500 details. Restrict origins to the local UI that is actually shipped, avoid exposing internal exception messages, and set explicit request/input limits. Bind the service to loopback in the documented launcher and verify the listening address; loopback should be the default trust boundary, not a substitute for output escaping.

These findings were confirmed by static inspection on 25 September 2026. No exploit testing or runtime exposure test was performed.

## Required verdict meanings

Supported means supported by the identified local evidence. Contradicted means applicable evidence conflicts with the claim. Insufficient evidence means the selected sources do not settle it. Conflicting evidence means relevant sources disagree. Not evaluated identifies nonclaims or excluded capabilities. Uncertain reflects checker limitations. Unchecked reflects operational failure or missing processing rather than a factual verdict.

Do not label middle-range scores as verified reasoning. Do not display a percentage as probability of truth without relevant calibration evidence. Do not interpret source support as proof of source quality.

## Decisions and completion

The owner has fixed the offline constraint. Remaining design choices include source/version precedence, the exact eligibility policy, the bounded reasoning scope, method selection after evaluation, local generator/hardware choice and whether a protected display mode is necessary beyond annotation.

Use [the task board](../tasks.md), [UI requirements](UI_REQUIREMENTS.md) and [offline audit](OFFLINE_REQUIREMENTS_AND_COMPLETION_AUDIT.md) to track completion. Documenting a resolution closes neither the implementation task nor the validation gate. Excluded capabilities require clear interface/report boundaries; in-scope capabilities require observable implementation and targeted tests.
