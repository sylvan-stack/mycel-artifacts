---
role: authored
---
# Guide: Code Retrieval

How [Mycel](../../arbol_deprecated_v1/GLOSSARY.md#mycel) answers a code query — the **read path**.
[Embedding](embedding.md) is the write side; this is what happens between a
query and its ranked results, identical for every invocation surface
(`code-search` RPC/CLI, the [better-grep](../../arbol_deprecated_v1/GLOSSARY.md#better-grep) tail,
agents in a [code-research](code-research.md) loop).

## The substrate

Both arms live in one Postgres: dense = pgvector (HNSW, cosine, one
`vector(1024)` column shared by every [Embedder
Profile](../../arbol_deprecated_v1/GLOSSARY.md#embedder-profile)); lexical = true BM25 via
**`pg_search`** (Tantivy) — the database image is **ParadeDB's** (bundles
pg_search + pgvector), pinned by tag; image bumps are deliberate. Code enters
the corpus through **code-aware chunking** (`code_chunker.py`): Python via
stdlib `ast`, Svelte block-aware, TypeScript/TSX/JavaScript via tree-sitter —
one chunk per symbol (`natural_key = path#symbol`, with lang/kind/line span),
falling back to a whole-file chunk on parse failure so nothing is silently
dropped.

## The route decision

A single-token query (`RealityCheckProcessor`) is **identifier-shaped**:
dense cosine and BM25 fuse by balanced RRF — exact-token evidence deserves
equal weight. Anything phrase-like is a **natural-language question**: raw
cosine is the authority, and BM25 only appends a rescue tail (exact-token
hits dense missed, ranked below everything scored).

## The doc bridge (NL route)

The repo's doc chunks are searched alongside its code; each of the top 8 doc
sections expands **one hop along its [Source Ref](../../arbol_deprecated_v1/GLOSSARY.md#source-ref)
edges** to the code it cites (file-level refs expand through the file's
chunks, capped to the best 3 by the code's own query cosine). Bridged code
inherits the doc's similarity × 0.92; when the direct and bridge routes agree,
the chunk earns a small bonus. Results delivered by a doc carry a `via:`
annotation with stale/[Heartwood](../../arbol_deprecated_v1/GLOSSARY.md#heartwood) trust flags —
prose matches the question, edges deliver the code. This is why
[per-repo glossaries](embedding.md#the-compounding-habits) pay off.

## Noise down-weights

Two file families lexically mirror feature prose ("should renew MFA when…")
and would otherwise outrank the implementation they shadow:

- **tests** (`.spec.`/`.test.`/`__tests__`/`test_*.py`) — down-weighted on
  both routes, unless the query itself mentions tests;
- **codegen** (`*.generated.*`, `gql/types.ts`) — down-weighted on the NL
  route only: identifier queries legitimately target generated types.

Module/markup/style/file-level chunks take a small structural down-weight on
both routes.

## Annotations on the way out

Each result may carry `via` (the doc section that delivered it) and
`documented_in` (doc sections whose Source Refs cite this code — the recorded
WHY, stale-flagged). Searches from inside a worktree see the repo **as that
branch sees it** — [Branch Overlay](../../arbol_deprecated_v1/GLOSSARY.md#branch-overlay) shadowing
applies before any ranking.

## Numbers that justify the shape

Bridge research: prod queries 15/22 → 19/22 @3, code jargon 3/6 → 6/6.
Down-weights + code glossaries: 19/20 @3 across the code repos.

<!-- sources:
mycel:mycel/knowledge/embedder.py#code_search
mycel:mycel/knowledge/embedder.py#_bridge_expand
mycel:mycel/knowledge/code_chunker.py
-->
