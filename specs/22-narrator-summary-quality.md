---
role: authored
spec: MYC-22
status: accepted
---
# Mycel · 22 Narrator summary quality

## Purpose

Produce short RAPTOR summaries that preserve the rules, conditions and exceptions that matter for retrieval. A summary of a long cluster should cover several distinct consequential claims even when one topic occupies most of the source.

The owner accepted this specification and MYC-D96–MYC-D98 on 17 November 2026. Implementation and qualification remain separate work.

## Scope

Narrator is a standalone source-grounded prose writer. It accepts one text and emits a summary to stdout. Its writer and label generation run independently of repository indexing and retrieval.

## Behaviour

### Cited statements

Number passages in source order against the exact decoded request. Identify the request by the digest of its original bytes. Use zero-based Unicode code point offsets with an inclusive start and exclusive end. The passage text at those offsets is the evidence. Candidate and unit identifiers are local to this request. A citation can point to several nonadjacent passages, each resolved separately.

Work from the requested document sections and use the request instructions only to understand the writing task. Exclude the instructions and any cut notice from source evidence. Recognize the exact framing of the supported MYC-8 prompt profile. Support the packaged profile first. An operator override may be used only with its exact framing supplied to the writer, using the same template as Mycel. Refuse a request whose section window cannot be resolved. Exclude any citation whose identifier, offsets or text do not resolve to the exact request. A unit is unsupported if the remaining passages and their context fail to support any material part of it. Keep rules with their prerequisites, exceptions and unresolved conditions. A change to wording or to cited evidence creates a new revision and requires a fresh verdict.

### Selecting what fits

Group assertions only if using either in place of the other would lead to the same decision under the same scope, prerequisites and authority. Keep differences that change an outcome, including different status, narrower authority, superseded rules and unresolved conflicts. Merge or choose a representative among equivalent units. Carry forward the passages that support the resulting text and verify substantive changes before assembly. Similarity may propose pairs to compare. It supplies neither an equivalence decision nor a priority score.

Rank units by how they change a reader's decision or interpretation. Prefer verified units that cover distinct governing rules, exceptions, failure outcomes and unresolved conditions. Give each such rule a chance to fit before spending space on a rule already covered. Use cited source order and unit identifier to break equal ranks. The final summary may use up to the sum of the original source sections' Unicode code point counts. Generated instructions, place labels, section separators and cut notices do not contribute to this count. Count all characters in the finished summary, including the newlines between units. Skip a unit that cannot fit whole, consider later units that can fit, and record the omission. Keep the wording and order within each verified unit. If none fits, return a writer failure with no summary text. The final ceiling sets no minimum compression ratio and imposes no size target on intermediate transformations.

### Checking and repairing statements

Verify all material parts of each proposed unit independently against its cited passages and their context before assembly. Check who or what the rule applies to, exact quantities and time bases, prerequisites, negation, exclusivity, and whether the source establishes a proposal, active rule, observation or unresolved claim. For example, evidence that an approved correction *can* resolve a discrepancy does not support a claim that it is the *only* way to resolve it.

MYC-D98 gives rejected high-priority units one shared repair pass. A unit is eligible if its omission would change an interpretation or resulting action, and its cited evidence and context contain enough information to make a precise correction. Send the rejected unit, its evidence and the verdict reason to repair. Recheck the returned revision before selection. Withhold units that still lack a supported revision, including ones whose repair cannot finish within the shared budget. A remaining verified subset is usable if it fits the writer contract. A retry of the entire command by Mycel under MYC-8.6 is separate from repair within a command attempt.

### Evaluation and handoff

Keep development examples separate from cases reserved for qualification. Freeze case texts and digests, evidence citations, rubrics, critical claims, model settings, budgets, and review criteria before comparing the writer. A critical claim is one whose omission or distortion changes whether an action is permitted or leads to a materially wrong outcome. Verify before the run that the required claims can be expressed within the case budget. Use output labels that do not reveal the writer or comparison arm to the scorer. Score a grouped claim as complete only when all its operative conditions survive. Report partial coverage, distortions, unsupported additions, repeated units, citation validity and request completion separately. Trace each consequential miss to the first stage that lost it when the retained evidence allows that diagnosis.

The historical RAPTOR qualification protocol is retained as evidence. Direct writer comparisons can still score the frozen summaries against their original source.

Use the reasoning adapter selected for the standalone command. The default model decision is recorded in MYC-D99.

## Requirements

| ID | Narrator or its evaluation shall | From v1 | Verified by |
|---|---|---|---|
| MYC-22.1 <!-- 61e45de6-e663-4974-8eb1-92d59680416b --> | Link retained claims and prose units to exact, possibly nonadjacent source passages and exclude unresolved citations from evidence | New | unit |
| MYC-22.2 <!-- f83af82e-af13-4600-acf3-c9050afd3bbb --> | Resolve repeated claims before final assembly, preserving differences in meaning, authority, scope and conditions | New | unit |
| MYC-22.3 <!-- eedd76c2-23c9-4ce7-9677-75d74926d064 --> | Give distinct consequential verified rules priority over overlapping detail and emit complete units within a measured budget without rewriting verified wording | New | unit |
| MYC-22.4 <!-- 4e94d742-ddb4-46fd-996c-993dd26340df --> | Check proposed units for support and for broadened, reversed or weakened conditions before including them | New | live |
| MYC-22.5 <!-- c6eeff3b-50b2-49e7-aa87-311b98347750 --> | Bound repair work, check every revised unit again and withhold any unit that remains unsupported | New | unit |
| MYC-22.6 <!-- 0a5917ed-001b-44db-b14d-501c3e790f4d --> | Pin a held-out collection and a scoring rubric, report paired outcomes and distinguish extraction, selection, verification, repair and budget losses | New | review |
| MYC-22.7 <!-- 53879011-43ca-4ea4-a3b7-53b07618fc06 --> | Withdrawn 19 November 2026 under MYC-8.39. Repository tree integration and qualification are retired. | New | unit |
| MYC-22.8 <!-- 1496f91a-89b1-4d1e-a375-4d5c8fa6a397 --> | Withdrawn 19 November 2026 under MYC-8.39. Repository tree integration and qualification are retired. | New | live |
| MYC-22.9 <!-- cabfb40f-6cbc-40db-adeb-ce5aef69c806 --> | Emit a final summary no longer than its original source text, measured in Unicode code points with generated request framing excluded | New | unit |

| MYC-22.10 <!-- 59378af7-856e-4bd6-9c1b-fa53d2a406dc --> | Accept bounded plain UTF-8 source on standard input in standalone Narrator with `--plain-text`, deriving its character ceiling from the exact input. Keep standalone labels, evidence checking, comparison reports and support for existing framed writer inputs | New | unit |

## Interface

The maintained writer runs directly from `scripts/narrator/narrator.py` and the packaged Python module. For ordinary prose on stdin, use `--plain-text` with a configured `--model-command`. Input is bounded UTF-8 and its exact character count is the output ceiling. The earlier framed format and its explicit source count remain readable by the standalone tool. Keep private comparison evidence outside stdout and retain bounded verified output.

The following hand-off is common to Selection, Verification and Integration. Equivalent internal representations are acceptable if they preserve these fields and dispositions.

| Record | Fields used across components |
|---|---|
| Passage | Request digest, passage ID, exact start and end offsets, original passage text. |
| Candidate | Request-local candidate ID, proposed claim, cited passage IDs, source authority and scope, and originating candidate IDs when claims are combined. |
| Unit revision | Request-local unit ID and revision, exact prose, originating candidate IDs, applicable scope and conditions, cited passage IDs, and consequence rank. |
| Verdict | Unit ID and exact revision, `supported` or `unsupported`, affected part and reason for an unsupported verdict, and the evidence passages consulted. Missing or malformed verdicts cannot authorize output. |
| Disposition | Candidate or unit identity, stage, outcome and reason. Distinguish invalid citations, equivalent units merged or removed, unsupported and repaired revisions, units skipped for budget, and selected verified revisions. |

Selection owns grouping, ranking and final assembly. Verification owns verdicts and bounded repair. Integration owns exchange of the common records, request identity, deadline, model routing, CLI boundary and private comparison report. The split places those responsibilities in `selection.py`, `verification.py`, and the writer entry point and adapters respectively. Selection and Verification can consume this hand-off through plain data fixtures independently of the later entry point. Evaluation runs outside the writer, with its rubric and answers unavailable to the model.

## Known problems

Development trials establish that source-linked verification and measured whole-unit assembly can enforce the word cap. They also expose two quality gaps: repeated details can crowd out supported distinct conditions, and a verifier can accept an unsupported restriction or reject a useful claim that needs precise repair. The trial outputs remain private development evidence. They do not qualify the accepted design.

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D96 <!-- 6bc2e1f3-f2a2-4946-aec8-674f2e354f98 --> | Where should the maintained writer live? | Keep it as a standalone optional executable in `mycel:scripts/narrator/`, with the prototype retained as research evidence. Keep Mycel's existing configured-command interface. The contract assigns and reconciles the component territories before booking code. | Decided 17 November 2026 by the owner: accepted the proposed default. Superseded for RAPTOR by MYC-D102. |
| MYC-D97 <!-- c29d4133-2d87-43e6-afc2-0d8c965b459e --> | What earns a recommendation for routine RAPTOR use? | In each of two fresh held-out rounds, require all requests in the candidate's proposed default mode to complete under MYC-D101, all premarked critical groups to be present and correct, no material unsupported claims, and at least 75% full coverage of required groups overall, exceeding the pinned baseline on the same cases. Also require the disposable two-level build and retrieval check. Freeze budgets before the run and count failures without replacement. | Decided 17 November 2026 by the owner. MYC-D101 replaces the original length criterion. |
| MYC-D98 <!-- d8d5837c-7f1d-4af5-8b08-bd23ea37fcad --> | Which repair and similarity policies should the first candidate use? | Use one batched repair and one fresh verification within a 270-second internal deadline per writer attempt. Bound it to eight text requests, including any format retry, and at most one embedding request in similarity mode. Use the unassisted writer by default. Consider similarity only if it improves full coverage in both held-out rounds and introduces no coverage regression on any case, critical error or failed request. | Decided 17 November 2026 by the owner: accepted the proposed default. |
| MYC-D99 <!-- 59fae84b-6b9d-49ce-b49a-ccc21556132e --> | Which text model and reasoning effort does Narrator use by default? | Use `gpt-6.2-sol` with medium reasoning effort for Label Generation and for summary extraction, consolidation, verification and repair. | Decided 17 November 2026 by the owner. The owner changed the model to GPT-6.2 Sol on 18 November 2026. |
| MYC-D100 <!-- 1a30e4a0-5509-4f7d-9dbd-442e56c87aa2 --> | Which account can qualification use for hosted model work? | Use the current authenticated Codex subscription. API keys are outside the authorized qualification route. | Decided 17 November 2026 by the owner. |
| MYC-D101 <!-- ad309c85-6504-4b7d-b862-7806a298e585 --> | What is the final length limit for Narrator summaries and their qualification? | Use the original source length as the sole hard summary-size limit. Report the source and summary lengths and their ratio. No minimum compression applies. | Decided by the owner. Replaces the 220-word qualification limit. |

The 270-second internal deadline leaves 30 seconds before Mycel's five-minute command ceiling. Eight text requests cover three ordinary stages, one format retry per stage, one batched repair and one recheck. With extraction shared, a paired candidate comparison needs at most 14 text requests and one embedding request. Pin the exact provider configuration and record each comparison arm's actual calls, tokens and elapsed time. Set a total provider allowance for qualification from the frozen case count, the repeat count and the disposable build plan before requesting live calls. No spending estimate is implied by the request count. The three-quarters coverage floor is a minimum bar for routine use alongside complete critical coverage, and two rounds provide a bounded check for repeatability. Neither is a conclusion measured by the earlier trials.

<!-- sources:
mycel:specs/08-summaries.md#Who writes the text
mycel:specs/08-summaries.md#Summaries in a search
-->

## Named checks

Qualification of the standalone writer is pending. The earlier RAPTOR qualification was retired on 19 November 2026.
