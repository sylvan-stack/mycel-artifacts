---
role: authored
---
# Narrator summary quality benchmark protocol

Private working artifact for [SYL-423](/Users/msix/Artifacts/forester/sagas/sylvan-stack/narrator-summarization-quality/evaluation/SYL-423.md). Keep it local. This procedure covers [MYC-22.6 and MYC-22.8](../../specs/22-narrator-summary-quality.md#requirements) under the accepted MYC-22 contract. It defines the evidence to collect and how to compare it.

## Development baseline

Use the retained [cited-unit trial](</Users/msix/Library/Application Support/Narrator/runs/raptor-units.PV710y/REPORT.md>). The following paths are relative to the [private run directory](</Users/msix/Library/Application Support/Narrator/runs/raptor-units.PV710y>). Use these copies rather than the working prototype, which may have changed. All digests are SHA-256.

| Pinned file | Digest |
|---|---|
| `narrator.py` | `3247659eeded7f06463c963758d32cad836c8164a5a4ba14c07e479a3f24521e` |
| `voyage_embeddings.py` | `a4d1035273770fba2cdb366ebf98da25dd72df2ffc861b81456d055780fba8c1` |
| `pinned.sha256` | `34432d569c55dd560d7382ccb49932f30e08120d1639e78784564f0dd4a609e4` |
| `inputs/01-meridian-transfer.txt` | `2177b8049e4653e2a1ba4d9c2d653c7f41d8d5ad964aa4be165871986cbda067` |
| `inputs/02-breakwater-telemetry.txt` | `ff439851097c3823e95898e6067d0a33b785e74de20b3e0a9d1657b0c20a7c91` |
| `inputs/03-arbol-installation.txt` | `ec602909a96acb9ea1407842469160aa6c2b5fcfdf3b0e4bfe9eac06080e9b81` |
| `inputs/04-mycel-summary-lifecycle.txt` | `62adaf8436760b1eebd5963c39e1038cba144be61a370a5ef67a76bb77add85f` |
| `artifact-sources.json` | `de13a93ffb9994db0d91783fb3c04fd1b385c75855e0b0b966c9deacd27ee13c` |
| `rubric.json` | `ea8c012fe44b47875504d2d200ec1e3a4f54b6f0934d46e43599a026ba6813d5` |
| `01-meridian-transfer.json` | `e3cb69e4cd7a372e240a744680ea731b975b6857974760deef178b220504fe44` |
| `02-breakwater-telemetry.json` | `7334dd8114ae0c615586d0c74618f30205b6f506e6d05c547cc35e8fdd1abb00` |
| `03-arbol-installation.json` | `5aeed8fde9baaea1b0312d5ff467349a963b1a543dab695734d2db004499713c` |
| `04-mycel-summary-lifecycle.json` | `15e4ce52c8b70a1ab70cf075148d721d1b75f78448b9779bda743ee9b05e3914` |
| `review/scores.json` | `3f26bd7918a4af34046ef921ffa00f95594010eca79998f11c6fa45b74d23dc2` |
| `review/key.json` | `e6a8edff9ac8aa036b4a5b899201fa010ad982842706ffceb3ac0ef9a8c16250` |
| `REPORT.md` | `9dd11120556d9d2bad7d8b5a162b86f7d04dbecd6e79c2b9ce4e4eb6617a991b` |

The archived run used Claude Sonnet 5.5 at medium effort (resolved ID `claude-sonnet-5-5`), Voyage `voyage-4-lite` for similarity hints, and a 220-word cap measured in whitespace-delimited words. It shared one extraction across the reasoned and semantic arms for each input. The mode key identifies each masked draft. The four completed pairs covered 5/26 and 6/26 grouped claims in full, respectively. The score includes claims only when all operative conditions are present. Both arms had 11 additional partial claims. These are historical development results, not choices for the future qualification run.

Before a later run, use the run directory's `pinned.sha256` to verify the copied writer, inputs, and rubric. Record digests of the actual runner and model wrappers, the requested and resolved model identities, and any departure from the archived settings. The evaluation harness for the retained run is `compare.py`, `writer.py`, and `embed.py`. Its masked review and structural-check helpers are `blind.py` and `verify-results.py`. The earlier [300-word diagnostic](</Users/msix/Library/Application Support/Narrator/runs/raptor-long.dr5s2K/REPORT.md#diagnostic-comparison>) used recovered or rejected drafts and wider outputs. It is not a baseline for the matched 220-word comparison.

## Held-out cases and custody

SYL-424 prepares independent cases. The four development cases are visible for tuning and may not later count as held out. Select long-form cases with coverage across the collection of independent topics competing for words, repeated promotion language masking one consequential exception, nonadjacent evidence, conflicting scopes or superseded proposals, numeric and temporal boundaries, and a qualification that must survive from actual child Summary Nodes into a parent.

Each case record contains a stable case ID, exact ordered input and source-snapshot digests, source identifier and revision, and passage IDs with start/end offsets and exact excerpt text. Record offset units and the input encoding. Each requirement has a claim ID, its applicable scope and all material conditions, and supporting source excerpts. Predeclare case-specific critical distortions and probe questions, with expected supported answers or distinctions, before seeing outputs. Verify the expected claims against the source, identify the evidence that would expose each critical distortion, and check that the required facts can fit the intended word cap.

An independent custodian records the private location and hashes of the input, source manifest, rubric, and any multi-level retrieval fixture in a freeze manifest. Keep the scoring key out of the writer and out of tuning. Before the candidate is pinned, the tuning agent may see scenario categories and aggregate counts, but not held-out texts or expected answers. After pinning, give authorized held-out inputs to the runner and give the rubric and exact sources to the masked reviewers. Keep the key that maps masked labels to modes or writers separate until scores are saved. A leaked or edited case moves out of the held-out set. Retain the original frozen record and freeze a replacement before the next comparison.

Before any use of a held-out input, record its permitted audience, storage location, approved provider disposition, and restrictions on transmission and retained excerpts. Missing or prohibited provider disposition prevents sending that input or an excerpt derived from it. SYL-424 supplies the completed case custody records and freeze manifest. This protocol records no approval.

## Pre-run record

Record and freeze these fields before comparison or scoring, with a digest and reviewer:

- Candidate and baseline identities, exact input and source pins, rubric, case order, and review criteria.
- Fixed writer, verifier and embedding model IDs and settings, and the repair and similarity policies.
- Shared output word cap and count method, per-request deadline, model-call budget including retries and rechecks, repeat count and allocation, and treatment of failure. Use the same applicable limits for paired arms.
- Accepted coverage and critical-error criteria, how repeats aggregate for the decision, and the retrieval probes and acceptance criteria for the disposable tree.
- Provider disposition for the exact inputs, masking plan, adjudication rule, and private result directory.

The owner accepted MYC-D97 and MYC-D98 on 17 November 2026. Freeze the 220-word cap, two held-out rounds, complete and correct critical-group coverage, no material unsupported claims, and at least 75% full coverage exceeding the matched baseline in each round. Freeze the accepted repair limits and reasoned default. Record the exact model choices and overall run allowance before requesting any live work. Record the decision revision. Keep unset values pending and do not score a run as qualification against them. Changing a frozen field starts a new recorded comparison and leaves the earlier outcomes intact.

## Comparisons and masked review

1. **Writer improvement on the four known cases.** Pair the revised contender with the pinned cited-unit baseline per case and predeclared repeat. Use the same input, rubric, writer-model settings, measured word cap, and the same hint condition for both writers. Each writer version performs its own extraction. Report completion status and per-case differences in full coverage, partial coverage, critical distortions, unsupported additions, redundancy, citation validity, and measured words. Keep any intermediate extraction changes visible for diagnosis. Do not interpret the result as isolating the effect of similarity.
2. **Writer improvement on held-out cases.** Run the paired candidate and pinned baseline on the same frozen held-out inputs and repeat schedule under the accepted default-mode policy. Keep those results separate from the known-case results. Use the held-out comparison for the accepted qualification gate.
3. **Similarity contribution within the revised contender.** For each input and repeat, freeze a single extraction and pass it to the contender with hints on and hints off. Hold the candidate revision, input, writer and verifier settings, measured word cap, and review rubric fixed. Apply the same treatment to the held-out evaluation under the agreed policy. Report the paired differences separately from the writer comparison. Use frozen held-out results to support any routine-use recommendation, with the known cases serving as development evidence.
4. **Independent scoring.** Give reviewers randomized, consistently formatted labels, the rubric, and the exact source. Hide writer version, hint mode, and pairing key. Reviewers score independently and save their per-claim worksheets before adjudication. Reconcile disagreements against an exact excerpt. Record both initial labels and the source supporting the adjudicated label. Leave unresolved disagreement visible and apply the frozen review rule. Unmask after the scores are recorded.
5. **Incomplete evidence.** Keep timed-out, failed, over-budget, malformed and otherwise invalid attempts in the run log with a reason, meter values, and any retained draft clearly marked invalid. Show the denominator of scheduled pairs, completed valid pairs, invalid or missing arms, and retries. Compute descriptive paired score differences only from valid matching pairs. Apply the qualification gate to all scheduled cases per arm, separate from those descriptive scores. Under MYC-D97, an invalid or missing result contributes zero full groups and all expected groups remain in the gate denominator. Preserve failed outcomes and the original settings with every repeat.

## Scoring worksheet

For each arm and repeat record case ID, masked label, output word count, completion, and a row for every expected claim. Keep the criteria fixed across reviewers.

| Field | How to score |
|---|---|
| Full | The output states the claim and preserves all operative conditions, authority, scope, polarity, and applicable exceptions. |
| Partial | The output conveys some supported material, without contradicting the claim, but omits an operative condition or exception needed for full credit. |
| Missing | No statement preserves the expected claim. |
| Distorted | The output contradicts, reverses, weakens or broadens the claim, or attributes a fact to the wrong authority or time. Cite the output and source. If the same claim appears both correctly and with a material contradiction, mark it distorted. |
| Critical distortion | Flag a distortion that meets a predeclared case criterion, such as reversing a release prerequisite, rendering an exception unconditional, or selecting the wrong authority. Record critical flags separately from coverage totals. |
| Unsupported additions | Record each distinct factual assertion in the output that the pinned source does not support. Capture the exact output text, check the full admitted source, and count the additions separately from expected-group coverage and distortions. Flag material additions separately for the qualification gate. |
| Redundancy | Count repeated statements beyond the first when they add no operative fact, qualification, or distinct supporting context. Record which passage could have used that space if the trace supports it. |
| Citation validity | Count how many emitted units have references that resolve to the pinned request and whose stored spans reproduce the exact excerpt. A valid locator does not establish semantic support. |
| Completion | Record whether the writer emitted usable summary prose within the declared cap and deadline, with the required evidence diagnostics. Record measured words and failure reason separately from claim coverage. |

Summarize counts by case, mode and repeat. Report complete-claim coverage as full claims divided by expected claims for valid outputs. Report partial, missing and distorted expected groups separately from unsupported additions, including material additions, in both the development and held-out comparisons. Include per-status counts for failed requests and incomplete pairs. Match the claim to exact output text and source evidence before inspecting the writer trace.

Attribute an omission or distortion to the earliest stage established by the trace:

- **Extraction:** No retained candidate covers the claim and its operative conditions. Inspect extracted candidates and rejected references.
- **Selection:** A supported candidate existed, but no ranked unit preserves the claim distinctly, or a merge loses its operative condition. Inspect ranked units, citations, and merge or deduplication notes.
- **Verification:** A proposed unit was rejected, or an emitted unit remained distorted despite a positive verdict. Inspect the unit, verdict and cited evidence.
- **Repair:** A rejected unit was never recovered, or the repair weakened a condition or failed recheck. Inspect repair input, revised text, verdict and disposition.
- **Budget assembly:** A supported unit was still eligible after verification or repair but was excluded from the assembled output. Inspect selection and exclusion records and the word meter.
- **Unattributed:** The available traces do not establish the stage. Record what evidence is missing rather than inferring a cause.

## Qualification report and hand-over

The qualification report records the frozen pre-run manifest, writer and model pins, raw attempt counts, masked scores and adjudication, valid matched differences, and traced losses. Apply the accepted criteria to the measured evidence and distinguish evidence for routine use from any activation decision. Retain disagreements, failed attempts and limits outside Git.

For MYC-22.8, use a disposable Mycel workflow under the [MYC-8 writer boundary](../../specs/08-summaries.md#who-writes-the-text). Record the exact writer and settings, isolated store, source corpus, command outcomes, and child and parent Summary Node IDs, levels, memberships and source hashes. Verify that the parent was generated from the actual children in that build, rather than a separate text simulation. Trace predeclared qualifications across the source, child and parent. Execute the frozen retrieval probes and record the returned Summary Node, evidence links and matching result according to the declared criteria. A one-level build, independently composed parent, or result retrieved from an unrelated document does not establish this qualification.

[SYL-424](/Users/msix/Artifacts/forester/sagas/sylvan-stack/narrator-summarization-quality/evaluation/SYL-424.md) uses the case and freeze requirements to prepare and validate the held-out collection. The RAPTOR Qualification Beat uses the approved frozen cases and settings to run the later comparisons and disposable build.
