---
role: authored
---
# Guide: Test Strategy

Use this guide when implementing changes, reviewing tests, or performing a testing task in Sylvan Stack. The owner adopted this policy on 28 October 2026: testing is separate work requested explicitly by the owner, except for a small top tier of informative edge cases and regression tests. Do not run tests after each change by default. Test count and coverage percentage are not quality goals.

This policy supersedes older instructions to run affected tests at every step, full suites at task entry or completion, or suites again after merging. The owner subsequently requested a physical reset: comment existing tests, restore only individually justified top-tier cases, and keep a test inventory with tier reasons in every repository. The reset was merged into main in ten repositories under SYL-316 and is documented in the [reset report](../../sylvan-stack/research/test-tier-reset-2026-10-28.md). MiMo is deferred while its separate live Beat owns it; the old backup is not its current inventory. This is not installed-package or runtime qualification.

Each repository's `TESTS.md` owns its active selection and links the complete inventory, `test-tiers.json` and `MID_TIER.md`. Read it before writing or running tests. The owner subsequently requested that retained mid-tier source stay uncommented (SYL-326). Writing or running it still requires an explicitly requested testing task. Broad qualification entry points must refuse while required tests are disabled; a smaller active inventory must never silently become a full qualification pass.

## Separate tier folders

Keep top-tier case bodies in `tests/top/` and mid-tier bodies in `tests/mid/`, relative to the suite root. Arbol Trunk uses `trunks/trivial/tests/`. Shared fixture classes and helpers may retain their existing paths; they contain no active inventoried test methods. Select the exact top-tier method or program documented in `TESTS.md` rather than using discovery.

Every repository with retained mid-tier cases has a `MID_TIER.md` describing each inventory entry, its tier reason and its review status. Provisional classifications must remain visibly provisional: a generated description or an assertion example does not establish useful coverage. Keep source locations and the machine-readable inventory current. Preserve previous source addresses when moving cases; relocation alone does not authorize indexed Origin migration or ingest.

Mid-tier code stays uncommented in its own folder at the owner's request. Keep necessary imports, shared-fixture links and compatibility entry points intact. A separately requested testing task selects the relevant cases; do not re-comment them afterwards. Broad qualification must refuse incomplete inventories or missing test sources. Folder separation and source restoration do not turn a focused result into full qualification.

## The three tiers

| Tier | What belongs here | Writing | Running |
| --- | --- | --- | --- |
| **Top** | A small set of high-value, non-obvious edge cases that resolve a concrete uncertainty, or regression tests that reproduce a specific bug. | May be added during implementation when the information or regression warrants it. Extend an existing case if possible. | Agents may run a precisely selected top-tier test when useful. There is no requirement to run it after each edit. |
| **Mid** | A small, deliberately selected set of consequential integration, compatibility or workflow checks, or difficult invariants with independent expected results. Every case must meet the admission bar below; ordinary functional coverage is insufficient. | Only in a separate testing task explicitly requested by the owner. | Only in a separate testing task explicitly requested by the owner. |
| **Low** | Straightforward behavior whose result is obvious from reading the code; copied constants or defaults, trivial accessors/forwarders, tests of fixture construction, tautological or vacuous assertions, or repeated checks with no distinct failure mode. | Do not write. | Remove rather than maintaining or routinely executing them. |

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
   case. Keep a representative case for a failure mechanism; remove routine
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
removal; uncertainty is not evidence that a case is low tier. Resolve it in the
requested review and report any genuinely unresolved scope explicitly.

Preserve the small individually justified top tier. Do not promote ordinary unit
cases to top tier to evade the new bar, hide removed cases in helpers, or merge
hundreds of variants into one test to make the headline count look smaller.
Report definitions and internal scenarios separately when they differ. The aim
is materially less low-information execution and maintenance, not a quota or
higher coverage percentage. Do not weaken a release gate or reinterpret historical
qualification because the retained suite is smaller.

## During implementation

1. Read the affected code and existing tests. Identify the uncertainty before deciding whether a test would help.
2. If a top-tier case resolves it, select that case explicitly. A bugfix test should reproduce the actual failure, not merely restate the repaired code. A small table is appropriate when its rows cover materially different edges.
3. Do not write or run mid-tier tests, a whole suite, a baseline suite, or a post-merge suite. A request to implement, fix, refactor, review, or prune tests is not by itself a request to execute the mid tier. A pruning request authorizes removal, not execution of the remaining mid-tier suites.
4. Review the diff and use proportionate static validation such as syntax, types, links or build compilation when useful. Do not disguise behavioral tests as probes or validation scripts. Inspect build commands and hooks before invoking them: some run tests indirectly.
5. Report what was checked and what was not. “Implementation complete; mid-tier tests not run under the testing policy” is an honest outcome. Do not call unexecuted checks passed or claim runtime qualification from static review.

Do not repeatedly ask the owner for permission to run suites during ordinary work. Leave testing for an explicit request. If a requested release or other action has a hard technical dependency on a broad test gate, explain that dependency and leave that action pending; never silently bypass the gate or infer permission from an implementation request.

## In a separately requested testing task

The owner's request defines the scope: particular behavior, a component, all repositories, or a named qualification. Reassess the relevant available cases, select useful checks and verify their prerequisites, and write missing mid-tier checks only where they add meaningful information. Keep each repository's inventory current. Leave mid-tier source uncommented after the task. Explicit authorization persists for the requested task, including useful failure investigation and reruns; it does not authorize unrelated live services, spending, or changes to owner data.

Before running, inspect discovery, prerequisites, skips and indirect execution. Record revisions, selections, elapsed time, results and limitations in existing run output outside Git. Distinguish passed, failed, skipped and unavailable. Zero selected tests is not successful qualification. A focused pass establishes only the selected behavior; live-provider or installed-package proof requires its actual boundary to be exercised.

## Assess value before adding or retaining a test

Ask what plausible wrong behavior the assertion rejects, what new information running it supplies, and whether a retained test already exposes that defect. Record that concrete reason in the repository's test inventory. A short entry is enough. Mark unreviewed mid-tier assignments as provisional rather than inventing a quality justification.

- Keep non-obvious boundary, race, cancellation, rollback, ownership and data preservation cases when they genuinely observe the claimed failure. Relevant risk does not automatically make every related test top tier.
- Use an independent expected result. Calling the production algorithm to compute both sides does not establish correctness. Comparing two references to the same mutable object cannot prove its contents stayed unchanged.
- Follow helper assertions and fixtures before declaring a test empty. The same method against different implementations or configurations can provide distinct information. Accidental inheritance against identical setup cannot.
- Preserve exact-byte checks when bytes are the contract, such as a protocol, migration, retained payload, or secret-redaction boundary. Source spelling, quote style and private helper names usually supply little useful evidence.
- Architectural checks may be useful if they enforce an explicit dependency or packaging boundary. A source substring cannot establish runtime absence of writes or calls.
- Prefer disposable resources and independent starting states. Mock the external boundary or failure point, not the behavior being claimed. A test of a mock's configured return value is low tier.
- Compare overlapping unit and integration cases. If a dictionary-based database simulation repeats a retained real transaction, lock or persistence case without exposing a distinct edge, remove the simulation. Preserve targeted fault injection or a separate algorithmic uncertainty when it adds information.

## Remove low-tier tests

Inventory current repositories once, excluding historical archives, generated files and duplicate worktrees. Review candidates with the code and their surviving callers or tests. Do not use test size or a keyword as a deletion rule.

Remove each confirmed low-tier case and unused supporting code. For repeated coverage, name the surviving case or shared fixture. Do not remove meaningful coverage to meet a numerical reduction target. If a mixed case contains a weak assertion and a useful edge, preserve the edge. Investigate uncertain cases against their implementation and fixtures; if a judgment remains unresolved, record that limitation explicitly instead of presenting the execution default as an approval of quality.

Check references and runner selection statically after pruning. Keep deletion reasons and source revisions in the task's review artifact; Git retains removed source. Do not update historical run records to imply a new pass. Do not run the remaining mid tier as part of pruning unless the owner also explicitly requested its execution.

The [October review](../../sylvan-stack/research/test-quality-2026-10-27.md) contains the earlier inventory and examples. It is dated evidence; this guide owns the current testing policy.
