---
role: authored
---
# Guide: Integrate authored work into Mycel

Use this guide when an authored artifact, implementation or test must become
findable together with its real source obligations. Passing tests alone does
not establish corpus coverage, dependency freshness or retrieval.

Follow the [Hub's dated pre-ingest rule](../README.md). Until the owner fills
the index, prepare coverage and Source Refs, validate the executable work, and
report indexing, embedding and retrieval as deferred. Do not run the owner's
first ingest or embed as part of a Saga Beat.

## 1. Check coverage

Resolve the repository's code and artifact roots from its settings and
`mycel repos`; the [runbook](../tools/mycel.md#repository-corpus-binding) owns
that binding. Include relevant implementation and tests in the configured
`code_subdirs`. Inspect settings before proposing a change; a file on disk
outside the selected corpora is not indexed knowledge.

## 2. Declare the real relationship in the file

A dependency says the dependant must conform to its source. Put Source Refs
inside the derived document section according to the
[authoring guide](source-refs-authoring.md), before ingesting that change.
Read the destination README and keep a backup before editing an artifact.
The file is the maintained truth; its next ingest reconciles the declarations.
Use an assertion only where the dependant cannot hold a parsed Source Ref,
such as a Python test function. Do not replace an editable document's Source
Refs with database-only assertions.

A relation says to review one chunk when another changes, without granting
source authority. `mycel relate '<dependant>' '<source>'` asserts one direction;
reciprocal obligations require both directions. No edge is needed merely
because two chunks were edited or read together. Exact chunk/file/family
selection and retained evidence are described in the
[relation manual](../tools/mycel-2-relations.md).

Keep portable root-qualified addresses in authored text, never saved search
result IDs.

## 3. Capture authorized changes and assertion exceptions

Once indexing is authorized, run `mycel ingest --repo <repo>` for the work's
repository after its files and Source Refs are ready. It captures both roots
and local Git locations, reconciles identities and declarations, and runs
mechanical Detection without changing the checkout. It embeds only with
explicit `--embed`. Check the actual per-repository result, pending work and
any committed-prefix warning before claiming the pass completed. The
[ingest manual](../tools/mycel-2-reconciliation.md#complete-public-ingest)
owns exact guards and partial outcomes. If a declaration is edited afterward,
ingest it again before verifying its stored edge.

For a dependant that cannot hold a Source Ref, assert its dependency after
both endpoints have been ingested. Pass the dependant first and source second:

```sh
mycel derive 'cellar:@code/tests/test_example.py#test_behavior' 'cellar:@artifact/architecture/example.md#Acceptance Contract'
```

`mycel refs --repo <repo>` reports retained declarations;
`mycel refs --repo <repo> --unresolved` isolates their resolution faults.
Check the dependant and resolved source addresses as well as the fault count.
Ordinary `derive` assertions are verified through their reply and the
dependant's read result; they do not become in-file declarations.
Changing pins or confirming a claim must follow an actual conformance review;
do not silence a stale mark to make a report look complete.

## 4. Embed and verify

Run `mycel embed --repo <repo> --dry-run` to plan the scope before an authorized
embedding pass. Actual `mycel embed --repo <repo>` handles retained pending
versions in that scope, not every repository. Inspect its committed progress
and failures; see [embedding](embedding.md).

Check retrieval with `mycel search --repo <repo> "<the new work's meaning>"`
and an exact identifier. Read the result through
`mycel read '<qualified-address>'` for full text and all directly describing
sections in `documents`. Read both the derived section and its source to
verify the stored text. The code chunk's `documents` gives the section address,
edge kind and direction: `source` when code rests on the section, `dependant`
when the section rests on code. Document reads have no separate source list;
use `refs` for their declarations. `documentedIn` in search is separately
ranked and may omit a real dependency without disproving it. Inspect `dependencyCheck`,
`staleReasons` and freshness completion; `mycel stale --repo <repo>` and
`mycel drifts --repo <repo>` expose remaining mechanical/review work.

When query credentials are unavailable, label the lexical fallback and use
`mycel search --repo <repo> --only docs "<the document's words>"` for document
lookup. A lexical match supplies no semantic retrieval proof. `--no-fresh`
skips a search/read freshness pass, not query embedding; neither that flag nor
an empty stored stale report proves the filesystem is current.

## Completion report

Report executable validation, corpus coverage, ingest outcome, real dependency
or relation declarations, freshness, and embedding/retrieval verification
separately. Name deferred steps and their reason. Empty results or passing
tests cannot substitute for an unperformed integration step.

<!-- sources:
mycel:@code/src/mycel/_ingest.py
mycel:@code/src/mycel/_located_dependencies.py
mycel:@code/src/mycel/_relations.py
mycel:@code/src/mycel/_document_links.py
mycel:@code/src/mycel/_search_reply.py
mycel:@code/src/mycel/_read_store.py
-->
