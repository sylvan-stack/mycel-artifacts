---
role: authored
---
# Knowledge Model — declarations, roles, edges, freshness

The value reference for Mycel's knowledge graph: every in-band declaration a
document can carry, every stored value a [Chunk](../../arbol_deprecated_v1/GLOSSARY.md#chunk)
or [Derivation](../../arbol_deprecated_v1/GLOSSARY.md#derivation) can take, and how they
combine into [Detection](../../arbol_deprecated_v1/GLOSSARY.md#detection) and
[Drifts](../../arbol_deprecated_v1/GLOSSARY.md#drift). The [GLOSSARY](../../arbol_deprecated_v1/GLOSSARY.md)
defines each term once; this page is the *system* view — all possible values,
their defaults, and the transitions between them. Every claim here cites the
implementing code.

## The two axes (the FAQ this page exists for)

**`role:` answers "who holds the truth of this prose"; Source Refs answer
"what do these claims depend on".** They are orthogonal, and the standard
pattern for a living document is BOTH: `role: authored` (original content —
a person or agent wrote these claims; nothing can regenerate them) plus
`<!-- sources: … -->` per section (each claim pinned to the thing it
describes, so the system knows exactly when to doubt it). An authored doc
with refs means: *maintained original claims with a freshness contract* —
when a cited source changes, the section is flagged for **re-verification**,
never regeneration.

At chunk granularity the axes do interact: a section that declares refs is
recorded `role=derived` in the graph (something governs it), while refless
sections keep the document's `authored` default. The file stays the truth —
remove the ref and the chunk drops back. So read `role: authored` as
"authored, *unless a section declares otherwise by citing sources*".

## In-band declarations (document frontmatter)

Parsed from the leading `---` block. Ingest recognizes exactly these; every
other frontmatter key is inert for the graph (surfaces may still display it —
Arbol's doc views render all frontmatter as a metadata strip).

| Declaration | Values | Effect on ingest |
|---|---|---|
| `role:` | `authored` \| `derived` | Default role for the document's chunks. **Any other value is ignored** — `role: blueprint` is a *document class* for the renderer/engine, not a chunk role; a blueprint's chunks default `unclassified`. |
| `status: heartwood` | + optional `implemented:` / `outdated:` time pins | Time-frozen record: never marked stale, open Drifts auto-closed, excluded from RAPTOR clustering; still ingested and searchable ([Heartwood](../../arbol_deprecated_v1/GLOSSARY.md#heartwood)). |
| `generated:` | `true` / `1` / `yes` | Regenerated-not-maintained (e.g. the [Code Map](code-map.md)): same exemptions as heartwood — Detection and RAPTOR skip it. |
| `sources:` | YAML list, or comma-separated scalar | Document-wide governors: materialized as `declared` edges on the document's **first chunk** (the [Detection-parent trick](../../arbol_deprecated_v1/GLOSSARY.md#source-ref) — e.g. `ticket.md` answering to its jira mirror). |

<!-- sources:
mycel:mycel/knowledge/chunker.py
-->

## Section-level declaration: `<!-- sources: … -->`

One HTML comment per section, one ref per line (single-line form works too).
Invisible in a rendered document by design — provenance must not pollute
reading (Arbol's doc views strip comments and offer a Sources toggle that
reveals them as chips, in place). Ingest materializes each into a `declared`
Derivation attached to **that section's chunk**.

Ref grammar is the chunk **natural key**, never a ULID: `repo:path#symbol`
pins one function, `repo:path#ClassName` the class family, bare `repo:path`
the whole file, `file.md#Heading` a section of another artifact. The rule for
what deserves a ref: **an edge follows a claim, not attention** — cite what a
section says something about, never everything that was merely read.

A ref that fails to resolve is recorded **loudly** on the chunk
(`meta.unresolved_sources`, visible in the Chunks Viewer), retried on later
passes, never silently dropped. The file is the truth: removing a ref removes
its edge on the next ingest.

<!-- sources:
mycel:mycel/knowledge/store.py
-->

## Chunk values

| Field | Values | Meaning |
|---|---|---|
| `role` | `authored` | Nothing governs it — it may govern others, or stand [Free-standing](../../arbol_deprecated_v1/GLOSSARY.md#free-standing). |
| | `derived` | At least one Derivation points at it; freshness is tracked against its parents. |
| | `unclassified` | A leather bag hasn't decided (docs-only state — a section may be an original decision or a restatement; unknowable without judgment). |
| `state` | `present` \| `orphaned` | Whether the last ingest still found it (documents carry the same pair). |
| `last_status` | `unchanged` \| `edited` \| `renamed` \| `new` \| `orphaned` | The identity decision of the last ingest pass ([Identity Reconciliation](../../arbol_deprecated_v1/GLOSSARY.md#identity-reconciliation)); document-level log adds `doc_new` / `doc_renamed` / `doc_orphaned`. |
| `origin` | `doc` \| `code` \| `summary` | Which corpus/process produced it. |
| `tier` | `0` = leaf, `1+` = summary tier | RAPTOR level — distinct from `level`, the markdown heading depth. |
| `stale` + `stale_because` | boolean + reason text | Set by Detection (below). |
| `meta` | `heartwood`, `implemented`, `outdated`, `generated`, `unresolved_sources` | The in-band declarations + loud ref failures. |

**Role defaults follow origin.** A doc chunk starts `unclassified` unless the
frontmatter `role:` overrides; a code chunk starts `authored` (undocumented
code is de-facto self-authoritative — the only truth about what the system
does); a RAPTOR summary node is born `derived` (created by its generation
edges).

**Role transitions.** Creating any Derivation flips the child to `derived` —
via in-file refs at ingest or via an asserted/generated edge. When a chunk's
declared edges all disappear and nothing else governs it, it drops back to
`unclassified` (not to `authored` — that requires a decision).

**Embedding freshness rides ingest:** an `edited` chunk's vector is cleared
(pending re-embed); `unchanged`/`renamed` chunks keep theirs.

<!-- sources:
mycel:mycel/knowledge/store.py
mycel:mycel/knowledge/raptor.py
-->

## Derivation edges

Direction: **parent = the source/governor** (the cited code, mirror, or
child-cluster member), **child = the governed chunk**. Each edge stores
`hash_at_gen` — the parent's content hash when the edge was created/updated —
which is what makes "changed since" answerable.

| `kind` | Created by | `policy` | Meaning |
|---|---|---|---|
| `declared` | In-file Source Refs at ingest | `review` | The file's own provenance claims. Synced exactly to the file — ingest never touches edges of other kinds. |
| `asserted` | RPC (a leather bag or agent asserting "this governs that") | `review` | Judgment recorded outside the file. |
| `generated` | RAPTOR summarization | `auto` | The summary was mechanically produced from its children. |

`policy` states what a stale child needs: `review` = a person/agent must
re-verify and repair the prose (it cannot be regenerated); `auto` = safe to
regenerate mechanically.

<!-- sources:
mycel:mycel/knowledge/store.py
-->

## Detection → stale → Drift

Detection walks every edge and marks children stale, with the reason recorded
verbatim on the chunk:

| `stale_because` | Trigger |
|---|---|
| `source removed (…)` | The parent no longer resolves. |
| `source changed since generation (…)` | Parent's current hash ≠ `hash_at_gen`. |
| `upstream chunk is stale (…)` | Transitive: a parent anywhere up the chain went stale. |

Heartwood and generated chunks are **never** marked stale — their truth is
indexed to a past moment or regenerated wholesale, so "changed since" is a
category error; any open Drift on them is auto-closed.

A [Drift](../../arbol_deprecated_v1/GLOSSARY.md#drift) is the *work item* opened for a
stale chunk: `status` `open` → `closed`, one open Drift per chunk, recording
**every** contributing source (`kn_drift_sources`), not just the first.
Stale is the adjective; Drift is the assignment.

<!-- sources:
mycel:mycel/knowledge/store.py
-->

## Not a Derivation: References

A [Reference](../../arbol_deprecated_v1/GLOSSARY.md#reference) is a mere locator (a link, a
"see also") — its only integrity question is *does it still resolve*, checked
cheaply without hashes or models. Using a term's **meaning** is the thing
that warrants a Derivation instead: meaning-dependencies are checked by
re-verification, pointers by resolution. When deciding whether to add a
Source Ref, ask which failure you care about: "the target moved" (Reference —
just link it) or "the target changed and my claim may now be wrong"
(Derivation — cite it in `sources`).

## Worked example

`tools/better-grep.md` is `role: authored` and its *Why it exists* section
carries `<!-- sources: Arbol:cli/arbol_cli/better_grep.py -->`:

- Ingest: that section's chunk gets a `declared`/`review` edge from the code
  file's chunk, `hash_at_gen` pinned, and its role flips to `derived`; the
  runbook's other sections stay `authored` per the frontmatter.
- `better_grep.py` changes → Detection: the section goes
  `stale: source changed since generation (…)` → a Drift opens naming the file.
- An agent re-reads tool + section, repairs the prose (or confirms it),
  commits; the next ingest re-pins `hash_at_gen`; the Drift closes.
- Nobody regenerates the runbook from the code — `review`, not `auto`.
