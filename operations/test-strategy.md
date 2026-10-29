---
role: authored
---
# Guide: Test Strategy

Use this guide when implementing changes, reviewing tests, or performing a testing task in Sylvan Stack. **All test work belongs to a separate task explicitly requested by the owner. There is no top-tier exception during implementation.** The owner prefers to write and polish implementation code first, then request tests when ready. Only the owner decides readiness and starts that testing phase. Test count and coverage percentage are not quality goals.

## The owner decides when testing starts

During implementation, do not add, edit, repair, refactor, classify, retire,
restore or run tests of any tier. This includes fixtures, snapshots, test data,
test runners and test inventories. Do not bundle test maintenance with a feature,
bugfix, refactor or implementation review, even if it seems small, useful or
necessary to keep existing tests in sync. Reading existing tests as source
reference is allowed; it does not authorize changing or running them.

Finish the requested code and polish within the implementation task. Report
relevant test impact and unexecuted checks honestly, then leave testing for the
owner. Do not decide that the code is ready, automatically transition into a
testing phase, create or dispatch a testing task, or treat your own checklist as
the owner's readiness decision. Do not repeatedly prompt the owner to authorize
tests. A separate testing task starts only when the owner explicitly requests
the test work and defines its scope. Merely calling part of an implementation
task a “testing phase” or giving it a new task ID does not make it separate.

This instruction of 29 October 2026 supersedes the earlier allowance to write
or selectively run top-tier cases during implementation. It also governs
indirect test execution: inspect commands and hooks first. A Build whose gate
runs tests must be done in a separately requested testing/Build task, not as
implementation validation. Do not bypass, disable or weaken that gate. A truly
test-free syntax, type or compilation check remains available when useful.

This policy supersedes older instructions to run affected tests at every step, full suites at task entry or completion, or suites again after merging. The owner subsequently requested a physical reset: comment existing tests, restore only individually justified top-tier cases, and keep a test inventory with tier reasons in every repository. The reset was merged into main in ten repositories under SYL-316 and is documented in the [reset report](../../sylvan-stack/research/test-tier-reset-2026-10-28.md). MiMo was deferred during that reset; SYL-327 includes its current repository after SYL-314 completed. The old backup is not its current inventory. This is not installed-package or runtime qualification.

**Builds run the top tier only** (the owner, 29 October 2026, SYL-329). In a separately requested testing/Build task, a Build's gate runs every top-tier test of its repository and no other test. It refuses when a top-tier test fails, or when a top-tier source is missing or commented. A passing Build says nothing about the mid tier, and its report never replaces requirement proofs or named checks that came from an earlier complete run. **The mid tier runs only when the owner asks for a mid-tier run.** No agent starts one on its own: not for a Build, a merge, a fix, a review, or a testing task it widened.

Each repository's `TESTS.md` owns its active selection and links the complete inventory, `test-tiers.json` and `MID_TIER.md`. Read it before writing or running tests. The owner subsequently requested that retained mid-tier source stay uncommented (SYL-326). Writing or running it still requires an explicitly requested testing task. Broad qualification entry points must refuse while required tests are disabled; a smaller active inventory must never silently become a full qualification pass.

## Separate tier folders

Keep top-tier case bodies in `tests/top/` and mid-tier bodies in `tests/mid/`, relative to the suite root. Arbol Trunk uses `trunks/trivial/tests/`. Shared fixture classes and helpers may retain their existing paths; they contain no active inventoried test methods. Select the exact top-tier method or program documented in `TESTS.md` rather than using discovery.

Every repository with retained mid-tier cases has a `MID_TIER.md` describing each inventory entry, its tier reason and its review status. Provisional classifications must remain visibly provisional: a generated description or an assertion example does not establish useful coverage. Keep source locations and the machine-readable inventory current. Preserve previous source addresses when moving cases; relocation alone does not authorize indexed Origin migration or ingest.

Mid-tier code stays uncommented in its own folder at the owner's request in the ten SYL-326 repositories. MiMo retains its existing mixed-file layout and commented mid selections; SYL-327 does not authorize their restoration or relocation. Keep necessary imports, shared-fixture links and compatibility entry points intact. A separately requested testing task selects the relevant cases; do not re-comment them afterwards. Broad qualification must refuse incomplete inventories or missing test sources. Folder separation and source restoration do not turn a focused result into full qualification.

## The three tiers

| Tier | What belongs here | Writing | Running |
| --- | --- | --- | --- |
| **Top** | A small set of high-value, non-obvious edge cases that resolve a concrete uncertainty, or regression tests that reproduce a specific bug. | Only in a separate testing task explicitly requested by the owner. Extend an existing case if possible. | Only within the owner’s separately requested testing scope. Every authorized Build runs the whole top tier; never run it as part of implementation. |
| **Mid** | A small, deliberately selected set of consequential integration, compatibility or workflow checks, or difficult invariants with independent expected results. Every case must meet the admission bar below; ordinary functional coverage is insufficient. | Only in a separate testing task explicitly requested by the owner. | Only when the owner asks for a mid-tier run. Never as part of a Build. |
| **Low** | Straightforward behavior whose result is obvious from reading the code; copied constants or defaults, trivial accessors/forwarders, tests of fixture construction, tautological or vacuous assertions, or repeated checks with no distinct failure mode. This includes superficially useful cases that fail the mid-tier admission bar. | Do not add new cases. Preserve existing rejected cases as comments at the end of their test files. | Never run while classified low. Comments are historical examples to consult, not a dormant suite to enable. |

A short test can expose a subtle defect. A long browser or database test can be low value. Classify by information gained and distinct failure detected, not length, speed, framework, assertion count, author, or words in its name. A successful workflow qualifies only when the real interaction between components is itself uncertain and consequential. Merely crossing a function or module boundary is insufficient. Prefer one representative workflow to a collection of routine permutations.

Unclassified retained tests are **mid tier for execution purposes** until reviewed. Do not label a whole file or suite top tier to avoid this policy. For a selected top-tier case, identify the bug or uncertainty and inspect its setup and dependencies so the command does not also run mid-tier checks.

That execution default is not a quality verdict. Calling production code, checking real behavior, or imagining a change that would make an assertion fail does not by itself justify keeping a test. A routine field mapping, default, argument record or schema-membership check can be correct and still be low tier. State what running the case reveals beyond reading that implementation.

## Higher mid-tier admission bar

On 29 October 2026 the owner explicitly raised the bar to substantially reduce
the retained running test surface. The earlier broad “meaningful behavior” rule
retained too much. Mid tier is selective evidence, not the destination for every
case that is not top tier.

A retained mid-tier case must satisfy **all** of these criteria:

1. **Consequential risk.** Name the concrete user-visible or operational failure:
   lost/corrupted data, broken protocol or installation, wrong cross-component
   outcome, leaked authority, unrecoverable work, or another material defect.
   “This might regress” and “it checks real code” are not reasons.
2. **Execution adds information.** The observation depends on a real interaction
   between production components and their filesystem, database, process, wire,
   browser or packaged environment; alternatively it checks a difficult
   algorithm/state invariant against an independent expected result. A local
   branch, field projection, fixed reply, ordinary parser example or forwarding
   call is insufficient even when it is correct and covered by a requirement.
3. **Distinct evidence.** State what this case reveals beyond the nearest retained
   case. Keep a representative case for a failure mechanism; retire routine
   variations in fields, commands, formats, types or error messages. A second
   implementation counts only when its real differing behavior is exercised.
4. **Trustworthy observation.** The assertion observes the claimed outcome across
   the relevant boundary. Fixture-only results, a mock returning the expected
   answer, SQL/text spelling, copied implementation calculations and generic
   “some error occurred” assertions do not qualify.
5. **Proportionate cost.** The unique evidence warrants its fixtures, maintenance,
   execution time and debugging burden. Prefer the smaller representative case
   when the larger one adds no distinct failure detection.

Record the risk, observed boundary/result and incremental value in `MID_TIER.md`
and the inventory. The keep decision needs affirmative evidence. An old tier,
name, framework, use of a database/browser, or provisional label grants no
exemption. Inspect bodies, shared helpers and the exercised implementation before
retirement; uncertainty is not evidence that a case is low tier. Resolve it in the
requested review and report any genuinely unresolved scope explicitly.

Preserve the small individually justified top tier. Do not promote ordinary unit
cases to top tier to evade the new bar, hide removed cases in helpers, or merge
hundreds of variants into one test to make the headline count look smaller.
Report definitions and internal scenarios separately when they differ. The aim
is materially less low-information execution and maintenance, not a quota or
higher coverage percentage. Do not weaken a release gate or reinterpret historical
qualification because the retained suite is smaller.

## Keep runnable suites small

The default is **no new test** unless a concrete uncertainty or consequential
failure justifies one under the tier rules. A new function, branch, option,
command, requirement row or bugfix does not automatically need a new test. A
bugfix merits top tier when the case reproduces the actual failure and rejects
the broken behavior. Small suites with distinct evidence are the goal; adding
coverage, matching production-file structure or increasing the count is not.

Before adding a case, read the nearest retained tests, their helpers and the
low-tier comments at the ends of relevant files. Search the inventory for the
same behavior, including historical identifiers and rejection reasons. Explain
what a new case would reveal beyond those cases and reading the implementation.
Prefer extending an appropriate existing case when it preserves its purpose.
Do not replace many tests with one giant loop to disguise the same volume.

Keep one representative per failure mechanism unless a second case has a
different consequential boundary or independent oracle. Keep fixtures and
permutations proportionate. Reassess overlap when a stronger case is admitted.
Retire weak cases into the low-tier comment section; do not generate extra low
tests just to fill that section. There is no numerical deletion target and no
requirement to make a suite smaller at every edit.

### Apparently useful cases that are still low tier

These examples describe why execution adds too little information. A different
case with an actual race, regression or independent difficult invariant must be
judged on that evidence. “Low mid” is not a fourth tier: a case that fails the
mid-tier bar is low tier after review.

| Tempting test | Why it is low tier in this form | Evidence that could justify a different case |
| --- | --- | --- |
| Construct a request and assert every supplied field appears in the output dictionary. | Mirrors a readable field projection; repeating it for every optional field adds no distinct mechanism. | A real protocol peer rejects an otherwise plausible encoding, or a recorded serialization bug loses data. |
| Verify every default timeout, label, enum member or configuration constant. | Copies implementation constants into another file. The assertion changes whenever the obvious declaration changes. | An independently specified compatibility boundary whose mismatch causes a consequential failure. |
| Mock the transport to return success and assert that the wrapper returns success or forwards the same arguments. | Confirms mock setup and straightforward forwarding. Calling production code does not make it integration evidence. | The real transport exposes framing, cancellation or retry ordering that a local call cannot establish. |
| Create a database row and read the same fields back for each entity. | Ordinary CRUD repeats framework/database behavior or an already retained persistence workflow. A real database alone is insufficient. | A transaction rollback, migration or concurrent update with independently verified preservation of data. |
| Repeat a real browser workflow for every theme, button label, command alias or harmless input value. | Adds costly permutations without a different failure mechanism; screenshots with no meaningful assertion add little. | A distinct keyboard, focus, layout or accessibility failure that the representative workflow cannot detect. |
| Exercise every ordinary parser rejection and compare the exact prose of its error. | Enumerates readable guards and incidental wording. Merely expecting an exception does not establish safe recovery. | A specific ambiguous/truncated input that previously corrupted state, with an independent state-preservation assertion. |
| Compute an expected result with the same production helper, or reconstruct its algorithm in the test. | Repeats the implementation's assumptions rather than providing an independent oracle. | A difficult invariant checked against an independent reference or known counterexample. |
| Assert source text contains a call, SQL fragment, decorator or private helper name. | Freezes source spelling and cannot prove the claimed runtime effect. | An independently observed packaging or dependency boundary, or bytes that are themselves the public contract. |
| Add another mocked cancellation/ownership case beside an existing real-process regression. | A serious topic does not give every related test value; the local simulation may add no evidence. | A distinct interleaving or fault not exercised by the retained case, with trustworthy ownership/cleanup observations. |

## During implementation

1. Implement and polish the requested code. Existing tests may be read as reference; leave their source, fixtures and inventories unchanged.
2. If a bug or uncertainty suggests a useful future test, record the concrete gap briefly in the hand-over. Do not write or run it, including a top-tier regression, and do not declare that testing should now start.
3. Do not perform test maintenance or execute selected tests, suites, baselines or post-merge checks. The owner must request a separate testing task. Test review or archival work requested separately does not itself authorize execution.
4. Review the diff and use proportionate test-free static validation such as syntax, types, links or compilation when useful. Do not disguise behavioral tests as probes or validation scripts. Inspect commands and hooks for indirect test execution.
5. Report what was checked and what was not. “Implementation complete; tests not changed or run under the separate-task policy” is an honest outcome. Do not call unexecuted checks passed or claim runtime qualification from static review.

Do not repeatedly ask the owner for permission to run suites during ordinary work.
If an action requires a test gate, explain that dependency and leave the action
pending for a separate owner-requested testing task. Never bypass its gate.

## In a separately requested testing task

The owner's request decides when this task starts and defines its scope: test
review, archival maintenance, writing tests, selected execution, a component,
all repositories, or a named qualification. Do only the requested test work.
A review, writing or archival request does not imply permission to run tests;
a top-tier run does not authorize the mid tier. Keep inventories current and
retained source in its documented state. A bugfix regression should reproduce
the actual failure, not restate the repaired implementation.

For an authorized run, permission persists through useful failure investigation
and reruns within scope; it does not authorize unrelated live services, spending
or owner-data changes. Do not fold implementation work into the testing task
beyond fixes explicitly included in the owner's request.

Before running, inspect discovery, prerequisites, skips and indirect execution.
Record revisions, selections, elapsed time, results and limitations in existing
run output outside Git. Distinguish passed, failed, skipped and unavailable.
Zero selected tests is not successful qualification. A focused pass establishes
only the selected behavior; live-provider or installed-package proof requires
its actual boundary to be exercised.

## Assess value before adding or retaining a test

Ask what plausible wrong behavior the assertion rejects, what new information running it supplies, and whether a retained test already exposes that defect. Record that concrete reason in the repository's test inventory. A short entry is enough. Mark unreviewed mid-tier assignments as provisional rather than inventing a quality justification.

- Keep non-obvious boundary, race, cancellation, rollback, ownership and data preservation cases when they genuinely observe the claimed failure. Relevant risk does not automatically make every related test top tier.
- Use an independent expected result. Calling the production algorithm to compute both sides does not establish correctness. Comparing two references to the same mutable object cannot prove its contents stayed unchanged.
- Follow helper assertions and fixtures before declaring a test empty. The same method against different implementations or configurations can provide distinct information. Accidental inheritance against identical setup cannot.
- Preserve exact-byte checks when bytes are the contract, such as a protocol, migration, retained payload, or secret-redaction boundary. Source spelling, quote style and private helper names usually supply little useful evidence.
- Architectural checks may be useful if they enforce an explicit dependency or packaging boundary. A source substring cannot establish runtime absence of writes or calls.
- Prefer disposable resources and independent starting states. Mock the external boundary or failure point, not the behavior being claimed. A test of a mock's configured return value is low tier.
- Compare overlapping unit and integration cases. If a dictionary-based database simulation repeats a retained real transaction, lock or persistence case without exposing a distinct edge, retire the simulation into low-tier comments. Preserve targeted fault injection or a separate algorithmic uncertainty when it adds information.

## Preserve low-tier examples as comments

On 29 October 2026 the owner replaced deletion with commented preservation.
Keep existing cases judged low tier in their source files so later agents can
see the rejected idea and avoid recreating it. The owner also requested recovery
of earlier removals from Git. Historical deletion reports remain historical;
recovered comments are not restored runnable coverage.

Move each confirmed low-tier body, including decorators and parameter rows, into
a clearly labelled **LOW TIER — DO NOT ENABLE OR RECREATE** section at the end of
the same test file, after runnable definitions and entry-point guards. If the
whole file is low tier, keep a comment-only file at that test path. Comment every
line with the language's line-comment syntax (`#` in Python, `//` in JavaScript
or TypeScript). Do not use skipped tests, disabled suites, dead branches or
multiline strings: the archived material must define and execute nothing. Keep
archived imports, registrations and case-specific helper context commented too;
do not restore runtime dependencies merely to support an archive.

For each case record its original identifier, the concrete rejection reason,
the nearest retained evidence when applicable, and the source revision. Preserve
the body faithfully; link shared historical context rather than manufacturing a
new implementation. Keep it classified **low** and explicitly **commented** in
the inventory, with the footer location. Report archived counts separately from
retained top/mid selections and runtime-discovered cases. Preserve earlier
deletion metadata as history when recording recovery.

Example format (the body is historical source, not a template for a new test):

```python
# LOW TIER — DO NOT ENABLE OR RECREATE
# Original: ConfigTests.test_default_timeout
# Reason: duplicates the explicit default in Config; no independent boundary.
# Source: <commit containing the original test>
# def test_default_timeout(self):
#     self.assertEqual(Config().timeout, 30)
```

Read these sections before proposing or adding a related test. Do not recreate
the same assertion elsewhere, rename it, or uncomment it just because a testing
task is requested. Re-admission needs new evidence meeting the top/mid bar and
the authorization required for that tier; update the reason and inventory first.
Comments need not track routine implementation changes: they document a rejected
test idea and its historical source, not a promise that the old code still runs.

If a mixed case has a useful edge and weak assertions, preserve the useful edge
and archive the rejected fragment with its reason. Do not retire meaningful
coverage to meet a quota. Investigate uncertain cases against their code and
fixtures, and record unresolved judgments honestly.

Check references, runner selection and comment-only preservation statically.
Keep retained case bodies unchanged during archival recovery. Do not update
historical run records to imply a new pass, add archives to runners, weaken a
qualification guard, or run the remaining mid tier unless explicitly requested.

The [October review](../../sylvan-stack/research/test-quality-2026-10-27.md) contains the earlier inventory and examples. It is dated evidence; this guide owns the current testing policy.

## SYL-327 retention result · 29 October 2026

The raised bar reduces the mid-tier inventory from **3,810 to 605 entries**: **3,205 removed (84.1%)**. The **75 existing top-tier entries are unchanged**. These are source-inventory counts, not runtime-discovered tests or a measured speedup. The removed entries comprise 3,070 Python definitions, 8 Node test definitions, 100 scenario entries and 27 whole programs. Programs, scenarios and orchestration can overlap; do not add their internals as separate cases. No tests ran.

| Repository | Mid before | Mid retained | Removed | Top unchanged |
| --- | ---: | ---: | ---: | ---: |
| [arbol](/Users/msix/repos/sylvan-stack/readonly/arbol/MID_TIER.md) | 656 | 151 | 505 | 3 |
| [arbol-classifier](/Users/msix/repos/sylvan-stack/readonly/arbol-classifier/MID_TIER.md) | 142 | 26 | 116 | 2 |
| [arbol-claude-driver](/Users/msix/repos/sylvan-stack/readonly/arbol-claude-driver/MID_TIER.md) | 44 | 21 | 23 | 2 |
| [arbol-codex-driver](/Users/msix/repos/sylvan-stack/readonly/arbol-codex-driver/MID_TIER.md) | 137 | 49 | 88 | 2 |
| [arbol-design-system](/Users/msix/repos/sylvan-stack/readonly/arbol-design-system/MID_TIER.md) | 17 | 9 | 8 | 0 |
| [arbol-mimo-driver](/Users/msix/repos/sylvan-stack/readonly/arbol-mimo-driver/MID_TIER.md) | 70 | 21 | 49 | 44 |
| [arbol-pi-driver](/Users/msix/repos/sylvan-stack/readonly/arbol-pi-driver/MID_TIER.md) | 198 | 70 | 128 | 4 |
| [arbol-root](/Users/msix/repos/sylvan-stack/readonly/arbol-root/MID_TIER.md) | 267 | 52 | 215 | 3 |
| [arbol-trunk](/Users/msix/repos/sylvan-stack/readonly/arbol-trunk/MID_TIER.md) | 240 | 18 | 222 | 3 |
| [mycel](/Users/msix/repos/sylvan-stack/readonly/mycel/MID_TIER.md) | 1788 | 135 | 1653 | 8 |
| [workspace-ledger](/Users/msix/repos/sylvan-stack/readonly/workspace-ledger/MID_TIER.md) | 251 | 53 | 198 | 4 |

MiMo also has a vendored shared-conformance copy: 38 commented scenarios became 12, removing 26 duplicate scenario entries. They are reported separately and not added to the 3,205 headline. Its 21 retained mid-tier definitions/program remain commented under its existing policy. The other ten repositories retain 584 uncommented mid-tier entries; execution still requires a separately requested testing task. MiMo is now included in the review after SYL-314 completed, and is no longer deferred.

Each repository has updated `MID_TIER.md`, `TESTS.md`, `test-tiers.json` and `docs/test-inventory.md` with kept reasons, removals and source revisions. Source and helper inspection drove retention; Mycel used an AST census of calls, assertions and patch boundaries with targeted case/fixture inspection. This is a risk-based reduction in coverage, not evidence that every removed defect is still detected. Retained bodies were compared statically with their original source; no cases were promoted to top tier or hidden in helpers to lower the count.

Historical full Build qualification remains unavailable where its test selection or requirement map was reduced. Packaged unit gates in Classifier, Claude, Codex, Pi, Root and Trunk refuse; Mycel refuses frozen full qualification; Workspace Ledger refuses its old requirement-map qualification. Arbol shared conformance requires explicit selections and reports reduced evidence. Restoring a full gate requires a separately requested qualification task; neither this review nor a future selected pass supplies historical full-suite proof.

No runtime, provider, Build, installed-package, owner-store, ingest or embedding qualification is claimed. Static syntax, source preservation, inventory hashes, references and diff checks are the validation for this change.

## Builds after SYL-329 · 29 October 2026

The Build gates named above no longer refuse for the reduced selection: they run the top tier only, as the rule at the top of this guide says. Mycel's Build gate selects `tests/top/` (MYC-D73). The Arbol `unit` checks of Classifier, Claude, Codex, Pi, MiMo, Root, Trunk and Arbol run their top-tier cases; their `contract` checks run no scenario and say so in the Build log, because no contract scenario is top tier. Root's layout and migration checks and Trunk's Root Contract suite are mid tier and no longer listed in their `arbol-build.json`. The `live` checks, one real message through the vendor tool (BLD-0.5), are unchanged. Full qualification of the reduced selections still needs an owner-requested qualification task, and no Build supplies it.
