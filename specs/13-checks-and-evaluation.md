---
role: authored
spec: MYC-13
status: accepted
---
# Mycel · 13 Checks and the evaluation set

A requirement counts as met only when a check proves it (MYC-0.11), and a constant of the ranking changes only with a measurement before and after (MYC-4.25). This specification fixes which checks run on every build and which only when asked for, what the automatic checks use in place of the owner's store and of the embedding service, and what the evaluation set is: where it is kept, what a query in it says, how it is run and what the report holds. It matters because version 1 had ten test files of which none ran a pass, a search, an embed or the ranking, and the numbers of its ranking came from research that is not in its repository.

It follows the conventions of the [specifications chapter](README.md#conventions), which name the four kinds of check: unit, store, eval and live.

## Scope

Covered: the checks of every build, the store a check works on, the stand-in for the embedding service, the live check, the evaluation set, the command that runs it and its report.

Not covered: what each requirement asks for; how a Mycel Build is made, numbered and marked as working ([MYC-15](15-distribution-and-replacement.md)); the rules of the ranking that the evaluation set measures ([MYC-4](04-retrieval.md)).

## Behaviour

### The checks of every build

Observed in version 1: the tests were run by hand. Ten files covered the settings, which repository a directory belongs to, the store's address and the names of commands. Installing a new program checked that both programs printed their help and their version, and ran one grep with the tail switched off. The repository's own description named an automatic check run that the repository did not contain.

Proposed: a Build of Mycel is marked as working only when every top-tier automatic check has passed (MYC-15). For Mycel these are the checks of the kinds `unit` and `store` in `tests/top/`. The mid-tier checks run only when the owner asks for a mid-tier run, never in a Build (MYC-D73). Checks of the kinds `eval` and `live` are run when somebody asks for them and are never part of an automatic Build gate. Retrieval evaluation needs an index with vectors; live embedding and provider qualification spend quota. Packaged relocation and offline-launch checks required by MYC-15 are automatic alongside unit/store checks: they prove that the immutable Build runs without the source checkout, system Python, downloads or Arbol. A failed required check marks the Build failed and records its reason.

MYC-0.11 holds for every specification in this chapter, MYC-0 through MYC-16. The owner accepted MYC-0 through MYC-16 on 8 October 2026, including the final MYC-14 classification/reviewer/lifecycle proposals. Acceptance authorizes implementation; it is not evidence that software has passed its checks or models have completed qualification. Each check names the requirements it proves by their identifiers, and the cell *Verified by* of a requirement names its check once the check exists.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:Makefile`
- `mycel_deprecated_v1:README.md`
- `mycel_deprecated_v1:tests/test_cli_metadata.py#test_mycel_version`

### The store of a check

Observed in version 1: no test worked on a store. An environment variable could point the program at a separate schema of the same database; the inventories name no test that used it.

Decided: a `store` check never works on the owner's store ([MYC-D36](#decisions)). The check run makes a database of its own for each check, under a name that begins with `mycel_check_`, in the database server that the owner's settings name. The address of that server is the one thing the check run takes from the owner's file. It writes a settings file for the run, names it with `MYCEL_CONFIG` ([MYC-5](05-settings.md#the-file)), makes the structure with `mycel init`, and removes the database when the check is over. A check refuses to run on a database whose name does not begin that way. The check run needs permission to create temporary databases on that server.

The files a check works on are fictional repositories that it makes in a folder of its own. Among them is a git checkout with a second branch and a stash, so that reading the locations of MYC-1 is checked on real git data.

Include checkout `README.md` and `docs/` Markdown, an overlapping-root alias of the same file, and different files with the same relative path under different roots. Verify document origin, heading chunks, one identity per physical file/location, root-aware search/read replies and visible ambiguous Source Refs (MYC-1.32, MYC-1.33, MYC-2.5, MYC-2.6, MYC-4.23, MYC-11.7).

Dependency checks include a fictional Glossary section governing a contract that governs an unchanged Driver chunk. Editing or removing the Glossary source must change the Driver's stale reasons in both ordinary and code-only searches, without adding dependency-only documents to code results or rewriting the Driver. Also check source restoration, unrelated repositories, invalid refs and incomplete checks caused by time limits or busy repositories (MYC-2.18, MYC-2.24, MYC-4.14, MYC-4.18, MYC-4.19, MYC-11.6).

When the database server cannot be reached, the `store` checks fail and the Build is `failed`. The MYC-15 Build record names the check that stopped it.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/database.py#connect`

### The stand-in for the embedding service

Observed in version 1: no test embedded anything, with the service or without it.

Proposed: the checks of every build never contact the embedding service. A stand-in takes its place.

| The stand-in | Why |
|---|---|
| gives the same vector for the same text, and nearer vectors for texts that share words | A check of the ranking then has an order to check |
| keeps the limits of the real service: texts per request, tokens per text and per request | The plans and batches of MYC-3.18 are checked against them |
| can be told to fail in each way MYC-3 names: no network, a time limit, a rate limit, a server error, a request rejected for its content | Retries and the search for the part at fault are checked (MYC-3.8, MYC-3.9) |
| counts what it was sent | A check can say that nothing was sent twice, and nothing of a disabled repository (MYC-3.13) |

The stand-in belongs to the checks. A Build as it is installed has no setting, option or variable that changes the address of the embedding service.

### The live check

Decided: one check of the kind `live`, run when asked for. With the owner's key it embeds one short fixed text and one fixed query, and checks that the key is accepted, the model the settings name exists, and a vector has the number of dimensions the settings name. It retains the pinned tokenizer's exact submitted-string count, conservative planning count and provider-reported input-text usage separately. The submitted count excludes the provider-added input-type prompt; the conservative planning count includes that prompt and is checked locally against caps under MYC-3.18. The report states whether provider usage matches the submitted count and retains the signed difference, provider minus submitted. Disagreement is diagnostic and does not fail compatibility; provider usage never replaces the pinned counts used for input/batch limits ([MYC-D42](#decisions)). Invalid provider responses, credentials, model or dimensions still fail. The record of the run names the Build, the model and the date; a new check/report revision distinguishes this contract from the earlier strict-equality check.

Jev classification and smarter-model review are checked with stand-ins in the automatic suite. Use a controlled clock to verify the configured debounce (default 300 seconds), exact file/change guards, fallback observation times, future timestamps, immediate stale visibility, low-confidence and insufficient-evidence routing, bounded retries, missing configuration, timeout/malformed responses and rejection of obsolete results. MYC-16 fixtures verify exact baseline/current/dependant/context bytes and canonical hashes, family membership, deleted sources, per-version branch pins, protected in-flight evidence and pruning 1,001 closed bundles while an older live pin remains. Classification may close exact-input semantic work but must never repin or clear MYC-D12 staleness. An explicitly deleted current source is a valid tombstone input if all pinned/dependant/context evidence remains; missing required baseline or context is a separate unresolved no-call case. Search/read/ingest never make Jev/reviewer calls; dry-runs make no service calls. Paid Jev or LLM calls never enter automatic unit/store checks. The on-demand drift evaluation below measures the selected routing profile and relative reviewer quality; its report is required before claiming provider qualification.


The reviewer boundary is exercised through real executable stand-ins using the production subprocess launcher. Fixtures cover absolute/tilde paths, literal argv and missing/nonexecutable files; stdin LF/EOF, exact canonical hash and transmitted byte cap; fixed environment with parent credential sentinels, unrelated descriptor closure, empty private cwd and opaque citations; full governor/ancestor selections; simultaneous pipe pressure; BOM/duplicate-key/nonfinite/unknown-member/trailing-text rejection; wrong identity/hash/revision/locator and usage booleans; success with exit 1, typed failure with exit 0 and valid JSON followed by a hang; typed transient retry delays and one-provider-call-per-attempt accounting; stdout/stderr overflow, SIGINT, timeouts, descendants that ignore TERM, group reaping and directory cleanup; helper/config changes requiring a new adapter revision and an executable change before application. Dry-run never executes a revision probe. These checks make no real model calls and never read real provider credentials.

### The evaluation set

Observed in version 1: there was none. The design record asked for one: questions with the chunks each should find, and the share that is found among the first results. The factors, margins and limits of the ranking were set without it.

Decided 8 October 2026: each repository can have an evaluation set ([MYC-D35](#decisions)). It is one file in the repository's document folder, named by the setting `evaluation` of that repository, so it is kept and versioned with the documents it asks about. It is not a document itself and is not ingested.

The UTF-8 TOML file has two independent optional sections: `[[query]]` for retrieval and `[[drift]]` for dependency classification. An optional `schema_version` must be 1; absence means 1 for existing retrieval sets. Unknown fields, malformed TOML, non-string text, empty retrieval text/expectations or duplicate drift IDs are `invalid_input` with file and field/line detail before any call. An empty selected section is valid and returns an empty report with undefined shares represented as null. A query says what was asked and which chunks answer it, by their places in the form of a Source Ref:

```toml
[[query]]
text = "how does renewal decide"
expect = ["cellar:src/auth/session.py#renew", "cellar:docs/auth.md#Renewal"]

[[query]]
text = "RetryPolicy"
expect = ["cellar:src/net/retry.py#RetryPolicy"]
only = "code"
```

Each retrieval expectation must resolve to exactly one eligible chunk through MYC-16 in the read/result role; a class name means its header chunk, as for `mycel read`, not a dependency family. File/family selections, malformed or ambiguous refs and missing/ineligible chunks are reported as faults of the set. Duplicate expectations that resolve to the same chunk count once. `only` may be `code` or `docs`; absence selects the ordinary combined search. A query with any expectation fault is excluded from all recall denominators, so a partially broken set never improves its score by dropping only the difficult expectation.

A drift case is a versioned fixture with the exact text a dependency decision concerns, rather than a live reference that silently changes underneath the labels:

```toml
[[drift]]
id = "permission-negation"
before = "Requests may retry after denial."
current = "Requests must not retry after denial."
dependant = "A denied request retries once."
expect = "needs_review"
critical = ["negation", "permission"]

[[drift]]
id = "source-deleted"
before = "RetryPolicy permits three attempts."
source_state = "deleted"
dependant = "Three retries are allowed."
expect = "needs_review"
critical = ["deletion"]
```

`id`, `before`, `dependant` and `expect` are required strings. `source_state` is `present` by default and requires a `current` string (empty text is valid); `deleted` requires `current` to be absent. Optional `context` is an ordered string array. Optional `unavailable` is a unique array of `baseline`, `dependant` or `context`; the harness deliberately withholds that required retained evidence to test the unresolved no-call path, and such a case must expect `unresolved`. `expect` is `still_supported`, `needs_review`, `insufficient_evidence` or `unresolved`. Optional `unchanged = true` marks a labelled `still_supported` unchanged/cosmetic case and is invalid with another expected label. Optional `critical` labels are `negation`, `operator`, `permission` and `deletion`; critical cases expect `needs_review` unless required evidence is deliberately unavailable, in which case they expect `unresolved`. A deleted current source with complete required evidence participates in semantic classification using explicit absence; it is not fabricated empty text. A missing-baseline/context case stays unresolved and causes no semantic API call. The harness wraps these exact fixture strings in the same MYC-16 canonical evidence/protocol used by classification; it never changes live pins or reads a newer source in place of the fixture.

A good set grows from real use: a question somebody asked and the chunks that answered it, or a reviewed dependency pair and its labelled outcome. A person or an agent adds cases and records the label evidence with the versioned file. Labels are evaluation ground truth, never owner verification records.

### Running it

**MYC-D44 decided 19 October 2026 by the owner:** “Use production Jev-only outcomes (Recommended)”. Keep raw tentative-label error/critical-miss comparisons separate from the operational unresolved baseline. The owner separately accepted canonical-confidence routing under MYC-D43 in MYC-14.

Proposed: `mycel evaluate --kind retrieval` (the default) runs every query of the selected repository's set as `mycel search` would, with ten results and without freshness checking. It writes nothing: no ingest, vectors, activity, pins or model-result cache. Required query vectors are computed first by normal search rules, then all retrievals and expectation resolution use one consistent read-only index snapshot and frozen effective settings. The report names the index generation, a fingerprint of relevant chunk versions/vectors/eligibility, evaluation-file hash and query-vector hash. Before/after comparisons are valid only when these inputs match; a changed index requires rerunning both Builds.

The report gives each expected chunk's position, or its absence, and recall at 3 and at 10: found expected chunks divided by all expected chunks of valid queries. It reports both shares overall and by MYC-4 route. A zero denominator is null, not zero or a fabricated perfect score. Faulted queries remain visible with their faults and are excluded. Wording-only searches are counted; a report with any such query does not establish semantic-ranking quality. The report retains the returned top-ten places for diagnosis.

`mycel evaluate --kind drift` runs the drift fixtures through deterministic stand-ins and the real local routing/evidence/lifecycle code, without paid calls or store writes. It validates the suite and pipeline behavior; it does not qualify Jev or a reviewer. Add `--live` explicitly to send eligible complete-evidence fixtures to the pinned Jev model and configured review command. `--live` is valid only with `--kind drift`; unavailable keys/reviewer configuration are reported as a qualification failure, not substituted by the agent's model. Calls obey MYC-14 concurrency, per-stage time, retry and input limits. The fixture runner processes the whole selected set in bounded candidate batches; it is not silently limited to the production default of 100 candidates. Each batch observes the MYC-14 invocation deadline, and stopped/unprocessed cases make qualification inconclusive. SIGINT terminates reviewer process groups and cancels outstanding requests without persisting partial evaluation state. Unavailable-evidence fixtures remain local unresolved no-call checks; a deletion tombstone with complete baseline/dependant/context is a valid semantic case.

A live report records every Jev probability, canonical routing confidence, separately reported provider confidence and exact agreement/signed difference, raw tentative judgement, escalation reason, reviewer judgement and exact returned provider/model, final outcome, expected label, request hash, input bytes, elapsed time, attempts and available usage/cost. Each valid Jev result includes mandatory `exactDecimals` with all three probability values, canonical confidence, reported confidence and signed reported-minus-canonical difference as decimal strings. These preserve validated decimal values and exact derived arithmetic, not original wire number lexemes. Existing numeric values are display projections; qualification, Jev-only baseline reconstruction and deployment validation use the exact companion evidence and verify consistency rather than rebuilding decimal decisions from floats. Missing or inconsistent exact evidence cannot qualify. It separately retains the Jev-only production-policy baseline and its unresolved reason; a raw label is never overwritten with that baseline. Unknown usage or cost remains null; Mycel does not infer prices or pretend a measurement occurred. The revised live report uses `reportVersion = 2` and `qualificationRevision = "mycel-drift-qualification-v2"`; `pipeline.qualificationRevision` also binds this comparison policy into the profile fingerprint. Each valid live Jev reply retains `jevOnlyOutcome` separately from `jev.judgement`; its routing reason stays in `escalation`. The report records `reviewerComparisonBasis` as wrong labels and critical misses from `jev-tentative-label`, and unresolved counts from `jev-only-confidence-routing`. No valid Jev reply means no invented Jev-only outcome. Pipeline identity includes protocol, exact `jev-1.13.0` model, `mycel-dependency-v1` question, Choice ordering, `mycel-drift-routing-v2`, effective confidence floor, reviewer command hash, immutable adapter revision, instruction/environment versions and actual provider/model. Different identities are separate evaluations. A reviewer that changes identity within a run makes qualification fail.

Initial provider qualification requires at least 200 distinct labelled pairs, including at least 50 critical-change and 50 unchanged/cosmetic cases. Critical labels cover negation, operator, permission and deletion. There must be zero incorrectly suppressed critical work: no critical case labelled `needs_review` or `unresolved` may finish as `still_supported`; unavailable-evidence cases must stay unresolved without paid calls. The configured reviewer must be evaluated on at least one common routed, adjudicated case with valid Jev and reviewer replies. On that exact common subset, compare wrong-label counts and critical misses against the raw tentative Jev labels, retaining the existing strict definitions: the reviewer must have no more of either. Separately compare unresolved counts against the actual production Jev-only policy. A valid Jev result routed for low canonical confidence, a tied maximum or `insufficient_evidence` is unresolved without the reviewer, even when its raw tentative label matches ground truth. Retain both the raw label and this separate baseline, without treating uncertainty as a raw-label error or a critical miss. Qualification still requires strict improvement in raw wrong-label count or production-baseline unresolved count; equality on both is insufficient. Provider errors, malformed replies, failed/unprocessed cases and changed identities do not become successful unresolved-baseline cases and still prevent qualification. Otherwise the report is not qualified, including when there are no comparative cases. Duplicate semantic fixtures (same before/current/dependant/context/availability state, excluding ID and label metadata) count only once toward qualification coverage; rerunning them is still useful for variability diagnostics. The report also gives aggregate error/false-positive rates, routing frequency, latency and reported cost; these diagnostics do not replace the critical-case and relative-quality gates. This is a finite-corpus release check, never a claim that a confidence score guarantees correctness. A changed confidence or comparison policy needs a fresh versioned qualification report; old failed records remain failed and cannot be relabelled or retroactively qualified. No evaluation modifies the configured threshold automatically.

Builds are kept side by side by MYC-15, so a ranking measurement before and after is two runs over matching index/file/query-vector inputs. Changes to ranking or grouping constants require both reports (MYC-4.25, MYC-D20), kept with the change record. A provider/routing change likewise records the exact old and new pipeline identity and qualification reports. The CLI returns reports to its caller; retaining them in an authored review or Build record is an explicit caller action, not an evaluation side effect.

**Historical evidence (unindexed):**

- `arbol_deprecated_v1:research/RETRIEVAL-RESEARCH.md#12. Validation`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`

## Requirements

| ID | Mycel must… | From v1 | Verified by |
|---|---|---|---|
| MYC-13.1 <!-- d3331e72-99c6-4820-bca9-d13d5946a5cb --> | run every top-tier check of the kinds `unit` and `store` on each build, and no mid-tier check, and let a Build count as working only when all of them passed (MYC-D73) | New | unit |
| MYC-13.2 <!-- b96f2480-fcbc-4594-a1ad-a0c38cfa8125 --> | keep checks of the kinds `eval` and `live` out of the build and run them only when asked | New | unit |
| MYC-13.3 <!-- 4ee113ba-908b-4375-8a03-4324fd169850 --> | Withdrawn 23 October 2026 under MYC-D56: every check named the requirements it proves, by their identifiers; that claim is now an Origin Link in the Index Store ([MYC-17](17-justification.md)) | New | unit |
| MYC-13.4 <!-- 14f40603-916d-46a2-86d2-702b82241c41 --> | run a `store` check on a database made for it, whose name begins with `mycel_check_`, with a settings file of its own, and remove the database afterwards | New | store |
| MYC-13.5 <!-- f17d15ab-ba6c-4e3e-b6c7-7d89f0fe4e30 --> | refuse to run a `store` check on a database whose name does not begin with `mycel_check_` | New | store |
| MYC-13.6 <!-- d74554cf-39f9-44a9-aa32-2c3353d49873 --> | check the reading of branches and stashes on a git checkout the check makes for itself | New | store |
| MYC-13.7 <!-- 285e70d5-bebe-46ea-b48d-aa0599012360 --> | contact the embedding service in no check of a build, and use a stand-in that gives the same vector for the same text, keeps the service's limits, can fail in each way MYC-3 names, and counts what it was sent | New | unit |
| MYC-13.8 <!-- 7e82f3c8-e997-45f3-80f5-26fbf8616518 --> | have, in a Build as installed, no setting, option or variable that changes the address of the embedding service | New | unit |
| MYC-13.9 <!-- 42b2599f-8c34-4f51-b6d2-e0a2db016f39 --> | check on request, with the owner's key, that the key is accepted, that the model exists and that a vector has the dimensions the settings name; retain the pinned tokenizer's exact submitted-string count, conservative planning count and provider-reported input-text usage separately, report their agreement and signed difference without requiring equality for compatibility, and keep pinned tokenizer counts for input/batch limits | New | live |
| MYC-13.10 <!-- 48fc57c8-8bc4-4dac-8e06-a52163e380f7 --> | read one configured per-repository evaluation file with separate optional retrieval-query and drift-fixture sections, validating their versioned schema before any call | New | unit |
| MYC-13.11 <!-- 27ba1a46-ae44-49ae-885b-6d4c0998e220 --> | run retrieval evaluation as searches with ten results over one read-only index snapshot, without freshness checking or writes, and run drift evaluation only for the explicitly selected kind | New | store |
| MYC-13.12 <!-- 868ad606-158a-4d39-937a-cc712638ef5b --> | report for each expected place the position at which it came or that it did not, and recall at 3 and at 10 over all expected places, in total and for each route | New | store |
| MYC-13.13 <!-- 2e5c52c4-ace7-438b-8f64-73c55a11adfa --> | report an expected place that the index does not hold as a fault of the set, and leave it out of the shares | New | store |
| MYC-13.14 <!-- fb2dcf9e-2ab1-44aa-9563-637243077bcf --> | name in the report the Build, the embedding model, the version of the search reply and the number of queries that were answered by wording alone | New | store |
| MYC-13.15 <!-- 83bebf55-6313-48b4-b009-5bddd02c7d9e --> | have an automated check for every requirement of MYC-0 through MYC-16 before that requirement counts as implemented, distinguishing complete/reviewed specifications from executed runtime and provider acceptance | Changed | unit |
| MYC-13.16 <!-- 3840a207-7efd-4330-a39a-abe06b7af7da --> | automatically check MYC-15 packaged relocation and offline launch, with no source checkout, system Python, downloads or Arbol dependency | New | unit |
| MYC-13.17 <!-- 8e74d465-20c6-4c7c-9e7a-150f8356c85f --> | validate exact retrieval expectations and exclude faulted queries from recall; return null for a zero denominator and record file/index/query-vector fingerprints for comparisons | New | store |
| MYC-13.18 <!-- 0d00dd18-3567-4013-9e57-38e469ac0f89 --> | test MYC-14 and MYC-16 with deterministic classifiers, controlled clocks and exact evidence, including obsolete results, missing review configuration, protected history and separation from freshness | New | store |
| MYC-13.19 <!-- eaf476b9-745e-4ef0-a167-4cfd87b6002d --> | make paid drift evaluation opt-in with `--kind drift --live`, retain exact pipeline/provider identities in its reply, and report errors, routing, latency and known usage/cost without invented measurements | New | live |
| MYC-13.20 <!-- d3196236-5367-4332-8a3e-7c1df529c7b0 --> | qualify a provider profile only against the stated critical-case and relative-reviewer gates, retain raw tentative-label no-more gates separately from the production Jev-only unresolved baseline, require strict improvement and new versioned reports for policy changes, and never let evaluation change pins, freshness or settings | New | eval |
| MYC-13.21 <!-- f21350d7-9973-42cf-8928-b21957df1d04 --> | exercise the real reviewer subprocess boundary with executable stand-ins, strict JSON/exit and environment fixtures, cancellation/cleanup, bounded retries and command/revision cache guards without real credentials or paid calls | New | unit |

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

```sh
mycel evaluate --repo cellar                  # retrieval, default working Build
mycel -v a3 evaluate --repo cellar            # same frozen inputs, earlier Build
mycel evaluate --repo cellar --kind drift    # stand-ins; no paid calls
mycel evaluate --repo cellar --kind drift --live # explicit provider qualification
```

The command takes one repository, not an organization. A missing configured evaluation file is `settings`; an unreadable file is `io`; malformed contents are `invalid_input`. An empty selected section returns normally. Drift reports are successful replies even when `qualified` is false; transport failures and case faults are visible per case rather than reported as support.

```ts
type EvaluationReport = RetrievalEvaluationReport | DriftEvaluationReport;

interface RetrievalEvaluationReport {
  kind: "retrieval";
  evaluationSchema: 1;
  repository: string;
  file: string;
  fileHash: string;
  build: string;                       // MYC-15 build number
  model: string;
  searchReply: number;
  indexGeneration: string;
  indexFingerprint: string;
  queryVectorsHash: string;
  queries: number;
  byWordingAlone: number;
  faultsOfTheSet: number;
  recall: { at3: number | null; at10: number | null };
  byRoute: {
    identifier: { queries: number; at3: number | null; at10: number | null };
    question: { queries: number; at3: number | null; at10: number | null };
  };
  results: Array<{
    text: string;
    route: "identifier" | "question";
    included: boolean;                 // false if any expectation is faulty
    returned: Place[];
    expected: Array<{
      place: string;
      resolved?: Place;
      position?: number;
      fault?: "not_in_index" | "malformed" | "ambiguous" | "ineligible" | "not_one_chunk";
    }>;
  }>;
}

interface DriftEvaluationReport {
  kind: "drift";
  evaluationSchema: 1;
  reportVersion?: 2;                  // required for the revised live qualification path
  qualificationRevision?: "mycel-drift-qualification-v2";
  repository: string;
  file: string;
  fileHash: string;
  build: string;
  live: boolean;
  pipeline: {
    protocol: 1;
    model: string;                      // exact configured versioned Jev ID, default jev-1.13.0
    questionVersion: "mycel-dependency-v1";
    choiceOrder: string[];
    policyRevision: string;
    qualificationRevision?: "mycel-drift-qualification-v2"; // live profile identity
    confidenceFloor: number;
    reviewCommandHash?: string;           // MYC-14 canonical ReviewCommandIdentity SHA-256
    reviewRevision?: string;
    reviewInstructionVersion?: string;
    reviewEnvironmentVersion?: string;
    reviewer?: { provider: string; model: string };
  };
  cases: number;
  distinctCases: number;
  criticalCases: number;
  criticalMisses: number;              // labelled critical work incorrectly suppressed as supported
  unchangedCases: number;
  routedCases: number;
  reviewerComparisonBasis?: {        // required for the revised live qualification path
    wrongLabels: "jev-tentative-label";
    criticalMisses: "jev-tentative-label";
    unresolved: "jev-only-confidence-routing";
  };
  jevUnresolvedOnRouted: number;       // production Jev-only policy baseline, separately retained per case
  reviewerUnresolvedOnRouted: number;
  jevCriticalMissesOnRouted: number;   // raw tentative-label comparison
  reviewerCriticalMissesOnRouted: number;
  jevErrorsOnRouted: number;           // raw tentative-label comparison
  reviewerErrorsOnRouted: number;
  errorRate: number | null;
  falsePositiveRate: number | null;    // needs_review among labelled still_supported cases
  elapsedMs: number;
  usage: unknown | null;
  cost: { amount: number; currency: string } | null;
  qualified: boolean;                 // always false without live provider evaluation
  qualificationFailures: string[];
  results: Array<{
    id: string;
    expect: "still_supported" | "needs_review" | "insufficient_evidence" | "unresolved";
    actual: string;                    // categorical outcome, unresolved or explicit error
    inputHash: string;
    jev?: {                           // raw judgement; keep the production-policy baseline separately
      judgement: string;
      probabilities: Record<string, number>; confidence: number; // numeric display projections
      reportedConfidence: number;                              // numeric display projection
      confidenceComparison: { matches: boolean; reportedMinusCanonical: number }; // delta is display-only
      exactDecimals: {
        probabilities: { needs_review: string; insufficient_evidence: string; still_supported: string };
        confidence: string; reportedConfidence: string; reportedMinusCanonical: string;
      };
    };
    jevOnlyOutcome?: "still_supported" | "needs_review" | "unresolved"; // valid live Jev replies only
    review?: { provider: string; model: string; judgement: string };
    escalation?: string;
    correct: boolean;
    critical: string[];
    attempts: number;
    elapsedMs: number;
    usage: unknown | null;
    cost: { amount: number; currency: string } | null;
    error?: { code: string; message: string };
  }>;
}
```

## Known problems in version 1

- **The main paths had no test.** No test ran a pass, a search, an embed, the ranking or the summariser.
- **Nothing measured the ranking.** Its factors, margins and limits came from research that is not in the repository, and no set of questions told whether a change made a search better or worse.
- **The check on installing proved little.** Help, version and one grep without its tail.
- **The description named a check run that did not exist.** The file it pointed to was not in the repository.
- **The tools for testing and for packaging were not declared.** They were installed by hand.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:Makefile`
- `mycel_deprecated_v1:README.md`
- `mycel_deprecated_v1:pyproject.toml`
- `arbol_deprecated_v1:research/RETRIEVAL-RESEARCH.md#12. Validation`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D35 <!-- 6b2c2b82-488a-4aba-84d6-7c0be8e96700 --> | Where is the evaluation set kept, and who writes it? | The evaluation set is a list of questions with the chunks each should find; it measures whether a change makes search better or worse. One file for each repository, in its document folder, named in that repository's settings. It is versioned with the documents it asks about, and a person or an agent adds a query whenever a real question was answered well or badly. The other choice is one set for all repositories in the Mycel corpus: one place to look, but its queries would name chunks of repositories that change without it | Decided 8 October 2026 by the owner: resolved; one configured evaluation file per repository in its document folder, versioned with its documents. A person or an agent adds real questions and the chunks that should answer them |
| MYC-D36 <!-- 74362b29-8900-4a12-9f8f-f41a7924016b --> | Which store do the automatic checks work on? | The automatic checks are the tests that run on every build. They work on a database the check run makes for itself in the same database server as the owner's store, under a name that begins with `mycel_check_`, removed after each check. The owner's own database is never opened by a check. This needs the right to create databases on that server. The other choice is a database server started only for the checks; it keeps the checks away from the owner's server altogether, at the price of something that starts and stops servers on every build | Decided 8 October 2026 by the owner: resolved; automatic store checks create and remove their own `mycel_check_` databases on the configured server and never open the owner's actual database |
| MYC-D42 <!-- a4b564e1-c5a6-404b-b71c-bf6fcee74932 --> | Should a difference between the official tokenizer's count and Voyage's reported usage fail embedding compatibility? | Retain both local counts and actual provider usage, report agreement and signed difference, and keep pinned tokenizer limits; disagreement alone does not fail compatibility | Decided 18 October 2026 by the owner: “Revise the requirement and continue (Recommended)” in response to the proposal to revise MYC-13.9 and continue full Drift qualification. The current official tokenizer gives eleven tokens while a fresh unchanged fixed-document request reports nine; neither value is adjusted. Keep the fixed text/query, model, dimensions, tokenizer and all planning limits. Preserve old reports and distinguish the revised check/report version |
| MYC-D44 <!-- 7ff7351c-cee8-465d-b60b-91a098d51b17 --> | Which Jev baseline measures the reviewer’s unresolved improvement? | Keep raw tentative-label errors and critical misses for the no-more gates; separately score unresolved outcomes using the actual production Jev-only confidence/tie/insufficient-evidence policy. Retain both views, require strict improvement, and bind them with reportVersion 2 and mycel-drift-qualification-v2; no corpus, labels, floors or critical gates change | Decided 19 October 2026 by the owner: “Use production Jev-only outcomes (Recommended)”. Keep the existing raw tentative-label no-more error/critical-miss gates; use the actual production Jev-only routing outcome for unresolved comparison, retain both views and require strict improvement. Qualification/report v2 requires fresh qualification; failed v5 remains failed |
| MYC-D56 <!-- 3bdaa0af-04b7-4db5-b864-ac3b75ac9c44 --> | What becomes of `requirements.json`, `claims.json`, `check_coverage.py` and `@proves`? | Retire them after a one-time import of the declarations as Origin Links | Decided 19 October 2026 by the owner: MYC-D56 stands. The registry, the claims, the snapshot check and the decorators are retired after the one-time import. Each `@proves('MYC-x.y', …)` on a test method becomes an Origin Link from the test chunk to the requirement's entity with `method: proven`, the band `proven`, and a verification `how: check`; then the decorators are removed from every test file together with `proves`, `load_claims`, `load_registry`, `verify_specification_snapshot` and `--release` in `_coverage.py` and `check_coverage.py`, and `requirements.json` and `checks/claims.json` are deleted. `_coverage.py` keeps what runs the suite: `no_network`, `disposable_store`, the backends and `run_checks` without claims. `make check` runs the suite. Build qualification (MYC-15) runs the suite and verifies no registry fingerprint. The kinds `unit`, `store`, `eval` and `live` stay as the vocabulary of MYC-13, no longer as a decorator argument. Carried out on 23 October 2026 by SYL-261: a check's kind is its class's `check_kind`, an on-demand check names its kind and requirements when it is requested, and MYC-13.3 is withdrawn |
| MYC-D73 <!-- d4eef8b6-92b3-4414-adb4-ef1d7baeeae6 --> | Which tests does a Build run? | Every automatic check of the kinds `unit` and `store` | Decided 29 October 2026 by the owner: "require only top tier tests for build. Mid tier should be only launched occasionally by user not when agent wants". A Build runs every top-tier `unit` and `store` check in `tests/top/` and no other test; it refuses when the top tier is missing or commented. The mid tier runs only when the owner asks for a mid-tier run. A top-only Build's report does not replace the named checks of an earlier complete run (SYL-329) |

## Named checks

Written by `scripts/name_checks.py` from the `proven` and `stated` Origin Links of the tests and a complete check report in which they passed. Each requirement keeps its kind in its Verified by cell and names here up to three of its passing checks: those of its own kind first, then those that rest on the fewest requirements. `mycel origins --repo mycel --path tests` lists every link. Do not edit this section by hand: run the script again.

| Requirement | Kind | Checks |
|---|---|---|
| `MYC-13.1` | unit | `test_automatic_qualification.AutomaticQualificationTests.test_already_delivered_cancellation_is_not_dispatched_again_after_an_ordinary_failure`, `test_automatic_qualification.AutomaticQualificationTests.test_cancellation_queued_during_error_cleanup_is_delivered_after_owned_group_and_pipes_close`, `test_automatic_qualification.AutomaticQualificationTests.test_cleanup_signal_deferral_delivers_with_an_ordinary_exception_in_flight` and 13 more |
| `MYC-13.2` | unit | `test_coverage.CoverageTests.test_previously_requested_acceptance_does_not_run_during_automatic_gate`, `test_coverage.CoverageTests.test_unit_and_store_checks_are_mandatory_eval_and_live_are_excluded`, `test_provider_deployment.ProviderDeploymentTests.test_exact_component_report_retains_quality_cost_and_cannot_be_a_same_build_proof` and 13 more |
| `MYC-13.4` | store | `test_store_gate.StoreGateTests.test_source_runner_cleans_real_store_after_failure_and_cancellation`, `test_fixtures.RepositoryFixtureTests.test_private_store_fixture_has_safe_name_private_settings_and_real_database` |
| `MYC-13.5` | store | `test_fixtures.RepositoryFixtureTests.test_private_store_fixture_has_safe_name_private_settings_and_real_database` |
| `MYC-13.6` | store | `test_fixtures.RepositoryFixtureTests.test_real_git_locations_are_read_without_touching_the_generated_checkout` |
| `MYC-13.7` | unit | `test_fixtures.ServiceFixtureTests.test_deterministic_vectors_keep_word_similarity_and_exact_request_counts`, `test_fixtures.ServiceFixtureTests.test_each_service_failure_is_controllable_and_attempts_remain_counted`, `test_fixtures.ServiceFixtureTests.test_packaged_prompt_counts_enforce_limits_while_usage_counts_submitted_text` and 3 more |
| `MYC-13.8` | unit | `test_fixtures.ServiceFixtureTests.test_installed_settings_and_cli_reject_provider_endpoint_substitution` |
| `MYC-13.9` | live | no on-demand report yet |
| `MYC-13.10` | unit | `test_evaluation.EvaluationFileTests.test_both_sections_are_validated_and_input_failures_have_file_details`, `test_evaluation.EvaluationFileTests.test_drift_context_availability_and_label_consistency`, `test_evaluation.EvaluationFileTests.test_drift_required_strings_deletion_and_empty_present_source` and 11 more |
| `MYC-13.11` | store | `test_evaluation_retrieval.EvaluationRetrievalStoreTests.test_actual_results_resolve_class_headers_and_exclude_every_faulted_ground_truth_query`, `test_evaluation_retrieval.EvaluationRetrievalStoreTests.test_actual_top_ten_matches_normal_routes_scopes_bridges_shared_aliases_and_generated_results`, `test_evaluation_retrieval.EvaluationRetrievalStoreTests.test_dimension_mismatch_keeps_normal_wording_without_calling_query_preparation` and 7 more |
| `MYC-13.12` | store | `test_evaluation_store.EvaluationStoreTests.test_exact_header_positions_faults_and_whole_query_denominators` |
| `MYC-13.13` | store | `test_evaluation_store.EvaluationStoreTests.test_result_scope_uses_stored_corpus_and_only_selected_enabled_shared_documents`, `test_evaluation_store.EvaluationStoreTests.test_shared_artifact_alias_selects_retained_code_primary_without_changing_identity`, `test_evaluation_store.EvaluationStoreTests.test_exact_header_positions_faults_and_whole_query_denominators` |
| `MYC-13.14` | store | `test_evaluation_store.EvaluationStoreTests.test_empty_section_reports_actual_index_and_null_shares_without_search`, `test_evaluation_store.EvaluationStoreTests.test_query_vectors_precede_one_snapshot_and_all_store_rows_remain_exact` |
| `MYC-13.15` | unit | `test_check_store.NativeCheckRunnerTests.test_acknowledged_creation_is_cleaned_after_body_init_and_immediate_cancellation`, `test_check_store.NativeCheckRunnerTests.test_cancellation_before_create_acknowledgement_retains_no_cleanup_permission`, `test_check_store.NativeCheckRunnerTests.test_cleanup_failure_retains_record_and_parent_continues_other_exact_drops` and 257 more |
| `MYC-13.16` | unit | `test_automatic_qualification.AutomaticQualificationTests.test_real_group_preserves_raw_binary_streams_status_arguments_and_cwd`, `test_packaged_release.PackagedReleaseTests.test_actual_case_detects_a_real_write_instead_of_reporting_immutable_execution`, `test_packaged_release.PackagedReleaseTests.test_fixture_group_disappearing_before_signal_is_already_cleaned_up` and 12 more |
| `MYC-13.17` | store | `test_evaluation_store.EvaluationStoreTests.test_current_versions_vectors_and_settings_have_guarded_comparison_fingerprints`, `test_evaluation_store.EvaluationStoreTests.test_concurrent_publication_cannot_mix_resolution_vectors_or_search_versions`, `test_evaluation_store.EvaluationStoreTests.test_empty_section_reports_actual_index_and_null_shares_without_search` and 6 more |
| `MYC-13.18` | store | `test_classification_store.ClassificationEvidenceStoreTests.test_missing_governor_blocks_both_stages_instead_of_silent_context_omission`, `test_evidence.EvidenceStoreTests.test_real_exact_reconstruction_limits_non_utf8_and_unsupported_comparison_never_repin`, `test_classification_store.ClassificationEvidenceStoreTests.test_complete_pinned_current_dependant_governors_and_canonical_bytes_are_owned` and 19 more |
| `MYC-13.19` | live | no on-demand report yet |
| `MYC-13.20` | eval | no on-demand report yet |
| `MYC-13.21` | unit | `test_evaluation_drift.DriftEvaluationTests.test_real_reviewer_retry_exact_cache_and_revision_guards_join_the_finite_runner`, `test_reviewer.ReviewerExecutionTests.test_each_failure_path_removes_its_private_cwd_after_child_cleanup`, `test_reviewer.ReviewerExecutionTests.test_real_executable_malformed_json_and_failure_exit_zero_never_succeed` and 34 more |
