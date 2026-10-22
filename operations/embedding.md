---
role: authored
---
# Guide: Embedding

Keep retained text and its vectors aligned so meaning search can use the
current version. The [embedding manual](../tools/mycel-2-embedding.md) owns
models, exact plans, request limits, receipts and retries; the
[retrieval guide](retrieval.md) covers the read side.

Follow the [Hub's dated pre-ingest instruction](../README.md). The owner does
the first ingest and embedding by hand after Seqoya Lab exists; a Saga Beat
does not fill the owner's store.

## Choose and plan the work

Mycel 2 uses the validated `embedding.model` and `embedding.dimensions` in its
settings, not a per-repository profile. Each chunk part keeps a saved place
line and complete exact text; splitting preserves every body byte instead of
truncating it. Queries use the same configured model and dimensions and are
submitted without a document place line.

When indexing is authorized, `mycel ingest --repo <repo>` captures changes
without embedding; `mycel embed --repo <repo> --dry-run` reports provisional
version/part plans without a provider call or saved progress. Actual
`mycel embed --repo <repo>` uses retained text in that explicit scope. With no
selector it uses CWD scope, not all repositories. `--all` explicitly selects
all enabled configured repositories. From a prepared folder name the repository.

## Preserve progress

Do not clear vectors as a routine update. Current exact-text/model coverage
determines eligibility. Successful committed batches survive interruption;
retry pending work through the normal command, and select failures explicitly
with `--retry-failed`. Valid paid receipts are reused rather than paid for
again. Inspect separate version, part, failed and deferred counts; partial
versions are not complete embeddings. A dry run supplies no live proof.

## The compounding habits

- Give jargon that the code never spells out a glossary entry under the
  resolved artifact root, with Source Refs to actual files or symbols.
- Persist expensive reusable research through the
  [authoring guide](source-refs-authoring.md), updating an existing document
  before adding a sibling.
- Mark superseded historical material as Heartwood with its retained source
  evidence; do not let old claims masquerade as current instructions.

<!-- sources:
mycel:@code/src/mycel/_embedding_plan.py
mycel:@code/src/mycel/_embed.py
mycel:@code/src/mycel/_search.py
-->
