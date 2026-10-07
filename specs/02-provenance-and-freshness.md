---
role: authored
spec: MYC-2
status: draft
---
# Mycel · 02 Provenance and freshness

A document says what it rests on, and Mycel tells its reader when that has changed. A section names its sources with [Source Refs](../../arbol/GLOSSARY.md#source-ref); Mycel turns each into an edge that remembers the source as it was; when the source moves on, the section is marked stale. This specification fixes how sources are declared, how a ref finds its target, what an edge remembers, and what makes a chunk stale and fresh again. It matters because in version 1 a stale section became fresh when anything else in its file was edited, a removed source never made anything stale, and the list of work it was meant to produce was never filled.

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: declarations in a document, Source Refs and how they resolve, edges and what they pin, roles, detection of staleness and its reasons, how a chunk becomes fresh again, what is reported.

Not covered: how chunks get their identity ([MYC-1](01-corpora-and-ingest.md)); how edges are used in search ([MYC-4](04-retrieval.md)); summaries generated from clusters of chunks, scoring of how much a source changed, relations without authority and recorded verification, none of which is part of the first version ([MYC-D13](#decisions)).

## Behaviour

### What a document declares

Observed in version 1, and kept: a document speaks about itself in the block of settings at its top.

| Key | Values | Effect |
|---|---|---|
| `role` | `authored`, `derived` | The role of the document's chunks unless an edge says otherwise |
| `status` | `heartwood`, with optional `implemented` and `outdated` | A record of a past state ([Heartwood](../../arbol/GLOSSARY.md#heartwood)): never stale, still searchable, marked as such in results |
| `generated` | `true` | Rewritten by a program, not maintained by hand: never stale |
| `sources` | A list of Source Refs | What the whole document answers to; attached to its first chunk |

The reader of that block was written by hand. It looked at the first 80 lines only, did not understand a quoted value or a list in brackets, and gave up without a word when the block was longer or the file began with a byte-order mark.

Proposed: the same keys, read as YAML. A block that cannot be read, and a known key with a value it does not take, are reported for the file.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/chunker.py#parse_frontmatter
mycel_deprecated_v1:mycel/knowledge/store.py#ingest
-->

### Source Refs

Observed in version 1, and kept: a section names its sources in a comment at its end, one ref per line. The comment does not show in the rendered document. A ref is a repository, a path and optionally a name.

```markdown
## Retry policy

Requests are retried three times, with a longer pause each time.

<!-- sources:
cellar:src/net/retry.py#RetryPolicy
cellar:docs/limits.md#Limits > Backoff
-->
```

| Ref | Finds |
|---|---|
| `repo:path` | The file as a whole |
| `repo:path#Symbol` | One symbol of a code file. A class name also finds every method of the class |
| `repo:path#Heading path` | One section of a document, by its heading path or by its bare title |

What deserves a ref is a claim: a section cites what it says something about, not everything that was read to write it.

Three things were loose. A piece of the comment that did not look like a ref was dropped without a record. A bare title that occurred several times in the target file found all of them. A ref that found nothing was written into the chunk's own record, which no command showed; the guides called this loud.

A ref was compared with the repository names stored in the index, exactly as written. Nothing checked whether the repository was switched on, or known to the settings.

Proposed: the same forms. A piece that is not a ref, a ref that finds nothing and a bare title that fits several sections are each reported: in the reply of the pass, and in a list that can be asked for. A ref into a repository the settings do not list is an outside reference: it is kept as written, never becomes an edge and is not a fault ([MYC-D11](#decisions)).

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/chunker.py#parse_source_refs
mycel_deprecated_v1:mycel/knowledge/store.py#_resolve_source_ref
mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges
-->

### Edges

Observed in version 1: an edge joins a source to the chunk that rests on it and stores the source's content hash at the moment the edge was written. There were three kinds.

| Kind | Made by | Meaning |
|---|---|---|
| `declared` | A Source Ref in a file | The file's own claim. Removing the ref removes the edge |
| `asserted` | The command `mycel derive` | A claim made outside the file |
| `generated` | The summariser | The chunk was produced from the source by a program |

A source could be a chunk or a whole file. For a section, the hash covered the text directly under its heading, not its subsections. For a file, it covered every byte.

Between one source and one chunk the store held one edge, so the kinds overwrote each other: a ref in the file turned an asserted edge into a declared one, and removing the ref then deleted the assertion with it.

Proposed: declared and asserted edges in the first version, kept apart, so that a file can never remove what a person asserted. An edge that would close a circle is refused.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges
mycel_deprecated_v1:mycel/knowledge/store.py#derive
mycel_deprecated_v1:mycel/knowledge/store.py#assert_derivation
mycel_deprecated_v1:mycel/knowledge/store.py#_parent_hash
-->

### Roles

Observed in version 1: a chunk's role says whether anything governs it. A chunk with at least one edge pointing at it was `derived`. Without one, a code chunk was `authored`, and a section of a document was whatever its file declared, or `unclassified`. The file's declaration took effect only when a chunk was first created; changing it later changed nothing, and a chunk that lost its edges fell to `unclassified` whatever the file said.

Proposed: the role is worked out on every pass from the edges and the file's declaration, and never remembered against them.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/store.py#ingest
mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges
-->

### Detection

Observed in version 1: after documents were ingested, every edge of the whole index was compared with its source, and the stale marks of the whole index were cleared and written again.

| Reason | When |
|---|---|
| Source changed | The source's hash is no longer the one the edge stores |
| Source removed | The source's row no longer exists |
| Upstream stale | A source of this chunk is itself stale. This passes on along every edge |

Heartwood and generated chunks were never marked, and nothing passed on through them. The comparison used hashes only and no model.

Three things kept it from doing its work.

- **An edit anywhere in a file made its stale sections fresh.** Whenever a file changed in any byte, every edge of every section in it was written again with the source's current hash. So a stale section turned fresh when another section of its file was edited; an edge between two sections of one file could never be stale; and a section with one ref that found nothing had all its edges written again on every pass.
- **A removed source made nothing stale.** Rows were never deleted, and the comparison did not look at whether a source was still present. The edge kept pointing at the retired row and its frozen hash.
- **Changes to code were seen one pass late.** Detection ran before the code of the same pass was ingested.

The reason text ended with the first eight characters of the source's identifier. Those characters are a time stamp, shared by everything created in the same second, and did not identify the source.

Proposed: detection covers the edges that touch the repositories of the pass, after both of their corpora are ingested. A source that is gone makes its dependants stale. A reason names the source by its place.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/store.py#detect
mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges
mycel_deprecated_v1:mycel/knowledge/store.py#_parent_hash
mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked
-->

### Becoming fresh again

Observed in version 1: nothing said "this was checked". A stale chunk became fresh when its edge was written again, which happened for any change to its file, or when the source went back to what it had been, or when the ref was removed.

Proposed: an edge is pinned to the source's current state in three cases only: when it is first made; when the chunk that rests on it is itself edited; and when its owner confirms, with a command, that the chunk was checked against its sources and still holds ([MYC-D12](#decisions)). An edit to another part of the file changes nothing.

### The list of work

Observed in version 1: a stale chunk was meant to open a [Drift](../../arbol/GLOSSARY.md#drift), a stored item of work that names every source that contributed. The function that opens them existed and nothing called it. The command that lists them read a table nothing filled. A Drift was closed only when its chunk became Heartwood or generated, never when it stopped being stale.

Proposed: no stored items in the first version. The stale chunks of a repository, each with its reasons and the sources behind them, are the list of work, worked out when asked for.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/store.py#open_drifts
mycel_deprecated_v1:mycel/knowledge/store.py#list_drifts
mycel_deprecated_v1:mycel/knowledge/store.py#_drift_sources
mycel_deprecated_v1:mycel/cli.py#_cmd_drifts
-->

## Requirements

| ID | Mycel must… | Origin | Verified by |
|---|---|---|---|
| MYC-2.1 | read `role`, `status: heartwood` with `implemented` and `outdated`, `generated` and `sources` from a document's frontmatter as YAML, and ignore every other key | Changed | unit |
| MYC-2.2 | report a frontmatter block it cannot read and a known key with a value it does not take, for the file they are in | Changed | unit |
| MYC-2.3 | read the Source Refs of a section from the sources comment in its text, one per line, and attach the frontmatter's `sources` to the document's first chunk | Kept | unit |
| MYC-2.4 | ignore a sources comment inside a code fence or inline code | Changed | unit |
| MYC-2.5 | resolve `repo:path` to a file, `repo:path#Symbol` to a symbol and, for a class, its methods, and `repo:path#Heading path` to a section by its heading path or by a bare title that occurs once | Changed | store |
| MYC-2.6 | report every piece of a sources comment that is not a ref, every ref that finds nothing and every bare title that fits several sections: in the reply of the pass and in a list on request | Changed | store |
| MYC-2.7 | keep a ref into a repository the settings do not list as an outside reference: no edge, no fault, never tried again | New | store |
| MYC-2.8 | try an unresolved ref again on every pass of its repository and of the repository it points into | Kept | store |
| MYC-2.9 | hold for each resolved ref an edge from the source to the chunk, storing the source's content hash, and remove the edge when the ref leaves the file | Kept | store |
| MYC-2.10 | hold an asserted edge apart from a declared one between the same two ends, so that neither a file nor a command removes the other's | Changed | store |
| MYC-2.11 | refuse an edge from a chunk to itself and an edge that would close a circle, and report it | New | store |
| MYC-2.12 | work out a chunk's role on every pass: `derived` with at least one edge pointing at it; otherwise what its file declares; otherwise `authored` for code and `unclassified` for a section | Changed | store |
| MYC-2.13 | mark a chunk stale when a source of it has a content hash other than the one its edge stores, with a reason that names the source by repository, path and name | Changed | store |
| MYC-2.14 | mark a chunk stale when a source of it is gone, with a reason that says so | Changed | store |
| MYC-2.15 | pass staleness on along every edge, and keep for each chunk every reason that applies, direct ones before passed-on ones | Changed | store |
| MYC-2.16 | never mark a Heartwood or generated chunk stale, and pass nothing on through it | Kept | store |
| MYC-2.17 | decide staleness by comparing hashes, with no model and no network | Kept | unit |
| MYC-2.18 | run detection for the edges that touch the repositories of a pass, after both corpora of each were ingested, and leave the marks of other repositories alone except where an edge from a changed source leads into them | Changed | store |
| MYC-2.19 | write a new hash into an edge only when the edge is made, when the chunk that rests on it is itself edited, or when its owner confirms the chunk. A change elsewhere in the chunk's file writes none | Changed | store |
| MYC-2.20 | list on request the stale chunks of a repository, each with its reasons and the sources behind them, without storing an item per chunk | Changed | store |
| MYC-2.21 | state in the status of a repository how many of its chunks are stale and how many of its refs are unresolved | Changed | store |

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

```sh
mycel stale --repo cellar                                  # the stale chunks, with reasons and sources
mycel refs --repo cellar --unresolved                      # refs that found nothing, and other faults
mycel derive 'cellar:tests/test_retry.py#test_backoff' 'cellar:docs/limits.md#Limits > Backoff'
                                                           # assert: the second governs the first
mycel confirm 'cellar:docs/net.md#Retry policy'            # checked against its sources: still holds
```

```ts
interface StaleChunk {
  chunk: Place;
  reasons: Array<{
    kind: "source_changed" | "source_removed" | "upstream_stale";
    source: Place;                     // the source this reason is about
    edge: "declared" | "asserted";
  }>;
}

interface Place { repository: string; path: string; name?: string }   // name: symbol or heading path

interface RefFault {
  chunk: Place;
  ref: string;                         // as written in the file
  fault: "not_a_ref" | "not_found" | "ambiguous_title";
}
```

## Known problems in version 1

- **Stale did not stay stale.** Any edit to a file renewed every edge of every section in it.
- **A removed source was not noticed.** Neither a deleted file nor a renamed heading or function made the sections that cited it stale.
- **The work list was empty by construction.** Nothing opened a Drift, and nothing closed one when its chunk recovered.
- **Kinds of edge overwrote each other.** A declared ref could replace an assertion, and removing the ref then removed both.
- **Faults in refs were silent.** A ref that found nothing was stored where no command showed it. A malformed line was dropped. A comment inside inline code made edges.
- **Detection ignored the scope of a pass.** A pass for one repository rewrote the marks of all, and two such passes could do so at once.
- **Code changes showed one pass late.**
- **A role, once given, stuck.** A file's declaration applied only to chunks made while it was there.
- **A reason could not be followed.** It named its source by characters that many rows share.
- **Circles were possible.** Nothing refused an edge from a chunk to itself, and the two functions that walk edges had no guard.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges
mycel_deprecated_v1:mycel/knowledge/store.py#detect
mycel_deprecated_v1:mycel/knowledge/store.py#open_drifts
mycel_deprecated_v1:mycel/knowledge/store.py#derive
mycel_deprecated_v1:mycel/knowledge/store.py#impact
mycel_deprecated_v1:mycel/knowledge/chunker.py#parse_source_refs
-->

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D11 | What is a ref into a repository that is not indexed? | An outside reference: kept as written, no edge, no fault. The specifications of this corpus cite the deprecated source this way | Open |
| MYC-D12 | What makes a stale chunk fresh again? | An edit to the chunk itself, or the command that confirms it. An edit to another part of its file does not. The stricter choice, confirmation only, would leave a section stale after its prose was repaired | Open |
| MYC-D13 | Which of the designs version 1 did not build are taken up? | None in the first version: no stored Drifts, no scoring of how much a source changed, no relations without authority, no recorded verification, no generated edges. Staleness stays a yes or no with reasons | Open |
