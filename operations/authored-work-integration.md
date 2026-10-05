---
role: authored
---
# Guide: Integrate authored work into Mycel

Use this guide whenever a person or agent creates or changes an Artifact,
implementation code, or tests and asks whether the result is **according to
Mycel**. Passing tests and using Mycel for research are necessary but do not
integrate the resulting knowledge by themselves.

## Contract

Work is integrated into Mycel only when all relevant outputs satisfy this loop:

```text
corpus coverage
→ ingest into stable chunks
→ establish real authority/coupling edges
→ run Detection
→ embed changed chunks
→ verify retrieval and reverse context
```

The unit is the [Chunk](../../arbol/GLOSSARY.md#chunk), not merely a file. Edges
must follow actual claims and consistency obligations; never connect chunks only
because they were edited in the same task.

## 1. Corpus coverage

Every relevant Artifact, implementation file, and test file must be under an
enabled repo's Artifact or Code Corpus. Tests are code knowledge: when they
encode behavioral contracts or regression scenarios, the repository's
`code_subdirs` must include their test tree.

Check and edit `~/.mycel/config.toml`; it is the source of truth for enabled
repos, code roots, and `code_subdirs`. Do not report Mycel completion while a
relevant output is outside all configured corpora.

## 2. Ingest and chunk

Run:

```bash
mycel sync
```

The Sync Pass ingests Artifact sections and code/test symbols, runs Detection,
and embeds the delta unless `--no-embed` was explicitly requested. Use
`mycel status --repo <repo>` to confirm there is no unexplained pending embed
work.

A file existing on disk is not enough. Verify that retrieval can find the new
section or symbol by its meaning and, where useful, by its exact identifier.

## 3. Establish edges

Choose the relationship by meaning:

- **Derivation** — a source/governor defines a contract that the child must
  conform to. Examples: architecture section → implementation symbol;
  acceptance contract → regression test.
- **Coupling** — neither side governs, but a change on either side requires
  checking the other.
- **No edge** — the chunks are merely adjacent, were read together, or have no
  consistency obligation.

For a derived Markdown section, put Source Refs inside the derived section as
specified by the Source Refs authoring guide. For implementation/test chunks
that derive from an authoritative Artifact section, assert the edge with stable
natural refs:

```bash
mycel derive   'Arbol:tests/unit/test_example.py#test_behavior'   'Arbol:architecture/example.md#Acceptance Contract'
```

The first argument is the **derived child**; the second is the **governing
source**. Use `repo:path#symbol` for code/tests and
`repo:path#Heading` for Artifact sections. Never store chunk ULIDs in source
files or task instructions.

One broad file-level edge is not a substitute for precise symbol/section edges.
A class-family ref is appropriate only when the whole family conforms to the
same contract.

## 4. Detect and embed

`mycel derive` runs Detection after asserting an edge. After all source and child
edits are final, run `mycel sync` again so content hashes, declarations,
staleness, and embeddings all describe the completed work.

A new edge should be fresh. If it is immediately stale, the source or child
changed after reconciliation; re-check conformance before reasserting it. Never
silence staleness merely to make the status green.

## 5. Verify

Before reporting completion, verify all of the following:

1. semantic search finds the new Artifact, implementation, and tests;
2. exact symbol search finds named contracts and scenarios;
3. implementation/test results expose their governing Artifact through reverse
   context (`documented_in` or lineage in the Chunks Viewer);
4. Detection reports no unexplained stale dependent;
5. changed chunks have embeddings, unless embedding was deliberately deferred
   and reported.

## Completion report

State separately:

- executable validation (tests/build);
- corpus coverage and Sync Pass result;
- authority/coupling edges established;
- Detection/freshness result;
- embedding and retrieval verification.

Do not collapse these into “tests pass.” Tests prove executable behavior; Mycel
integration keeps the knowledge graph able to find and refresh the contract,
implementation, and evidence together.

<!-- sources:
mycel:operations/knowledge-model.md#Derivation edges
mycel:operations/source-refs-authoring.md#Rules
mycel:mycel/knowledge/store.py#assert_derivation
mycel:mycel/syncpass.py#run_pass
-->
