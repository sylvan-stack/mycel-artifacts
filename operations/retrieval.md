---
role: authored
---
# Guide: Code Retrieval

Use Mycel 2 to find current indexed code and documents, then read the evidence
behind each result. This guide explains how to interpret retrieval; the
[retrieval manual](../tools/mycel-2-retrieval.md) owns exact ranking, fields
and limits. [Embedding](embedding.md) describes how retained text gets vectors.
Follow the [Hub's dated pre-ingest rule](../README.md) before using retrieval.

## Select a repository

`mycel search --repo <repo> "<query>"` searches the named repository. Always
pass the repository from a prepared folder: implicit scope can include the
organization. Repeated selectors and organization scope retain independent
member replies and rankings; never compare scores across repositories.
Use `--only code` or `--only docs` to narrow results and `--k <count>` to set
the count. Search has no path filter; narrow a later file read or exact grep.

## Read the result

Search returns schema 3 with separate meaning/wording candidate counts,
`route`, `meaning`, `freshness` and `results`. Wording matching uses complete
stored text, names and paths even when embeddings are missing or incomplete.
Meaning matching requires complete valid part coverage for the current model
and dimensions. Identifier queries combine both ranked lists; question-shaped
queries place wording-only results after meaning matches.

Documents may deliver code through their exact Source Ref dependencies; `via`
identifies the bridge. `documentedIn` gives ranked document context, while the
separate `described` flag considers all current directly describing sections.
Read a code chunk with `mycel read '<qualified-address>'` for the complete
`documents` list; relations and generated sections do not describe code.

Use each result's qualified `address`, actual root, relative path, optional
readable `file` and retained `lines`. Code and artifact files with the same
relative path remain distinct. Stored overviews and summaries have index
addresses; they need no fabricated file path.

## Check what is current

Normal search performs bounded local freshness work on the selected repository
and its explicit upstream dependencies, with no checkout reset and no pending
corpus embedding. It can embed the query. `--no-fresh` reads the committed
index without freshness writes; it still permits query embedding. Missing
query credentials or failed query preparation leave wording results available
with an explicit reason, rather than supplying meaning evidence.

Inspect `freshness.finished`, required repository states, `withoutVector`,
`staleReasons`, `heartwood` and `dependencyCheck.complete`. A missing stale mark
with incomplete checks is not verification. Mechanical freshness does not
establish semantic correctness. Empty results describe this index and scope,
not absence from the repository; use grep to verify completeness.

<!-- sources:
mycel:@code/src/mycel/_retrieval.py
mycel:@code/src/mycel/_ranking.py
mycel:@code/src/mycel/_search_store.py
mycel:@code/src/mycel/_search_reply.py
-->
