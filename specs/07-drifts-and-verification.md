---
role: authored
spec: MYC-7
status: accepted
---
# Mycel · 07 Drifts and verification

[MYC-2](02-provenance-and-freshness.md) marks a section stale when something it rests on has changed. This specification records relations between chunks where neither governs the other, who checked a section against its sources, edges for text a program produced, and retained links to deleted sources. These are part of the five designs required by [MYC-D13](02-provenance-and-freshness.md#decisions). Dependency classification and stored Drifts are specified separately in [MYC-14](14-drift-detection.md), extracted on 8 October 2026 at the owner's request. Exact addresses and retained evidence are specified in [MYC-16](16-source-addresses-and-evidence.md). These contracts are accepted for implementation; the runtime and provider qualification checks have not yet run.

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: relations without authority, recorded verification, generated edges, what remains of an edge whose source is deleted.

Not covered: what a document declares, Source Refs, the three reasons for staleness and what makes a chunk fresh again ([MYC-2](02-provenance-and-freshness.md)); versions of a chunk and the locations they are found in ([MYC-1](01-corpora-and-ingest.md#branches-and-stashes)); the program that produces generated text ([MYC-8](08-summaries.md)); dependency classification, Drift policy, lifecycle and reporting ([MYC-14](14-drift-detection.md)).

## Behaviour

### How much a source changed

Moved to [MYC-14 · How much a source changed](14-drift-detection.md#how-much-a-source-changed) on 8 October 2026. That section preserves the rejected word-score and accumulation proposal as history. The owner now selects Jev classification without a change-size threshold, five-minute debounce and low-confidence smarter-model review; the detailed classification and review contract is specified there. This forwarding entry defines no competing policy.

### Drifts

Moved to [MYC-14 · Drifts](14-drift-detection.md#drift-lifecycle-and-retained-evidence), with the classification rules, lifecycle, interface and historical evidence. [MYC-D28 and MYC-D29](14-drift-detection.md#decisions) are discussed there. The change-size threshold was rejected; Jev is selected, with five-minute debounce and low-confidence smarter-model review. Its accepted lifecycle contract closes semantic work only for the exact classified inputs; it does not repin an edge or restore freshness. MYC-D12's accepted baseline remains in MYC-2.

### Relations without authority

Observed in version 1: designed in the Glossary under the name [Coupling](../../arbol/GLOSSARY.md#coupling), with no table and no code. Two chunks can have to agree while neither governs the other: the section that describes the form of a request and the section that describes the form of its reply; a test and the fixture file it reads.

Proposed: a relation says "when that chunk changes, look at this one". It is made in the same two ways as an edge ([MYC-D30](#decisions)):

```markdown
## Reply format

A reply repeats the identifier of its request.

<!-- related:
cellar:docs/api.md#Request format
-->
```

or, from outside the file:

```sh
mycel relate 'cellar:docs/api.md#Reply format' 'cellar:docs/api.md#Request format'
```

The refs use the single resolver and portable root-qualified addresses of [MYC-16](16-source-addresses-and-evidence.md): only repositories that are registered and enabled, and every fault reported (MYC-2.5 to MYC-2.8). A declared relation may name a file, one chunk or a class family. Its immutable baseline manifest pins every resolved member, their exact text snapshots and the selection membership. A changed member hash or membership marks the dependant `related_changed`; a missing member is `source_removed`. Classification follows [MYC-14](14-drift-detection.md). Freshness follows MYC-D12: edited or confirmed.

`mycel relate` takes the dependant first and the source selection second. Both endpoints must resolve to exactly one current on-disk chunk; a class endpoint means its header, not a silently expanded family. The relation is directed from the second chunk to the first, with no implicit reverse relation. Declared related comments may still use the file/family selections above. Resolve and validate the whole selection before atomically asserting it. Repeating an identical assertion is a no-op and never renews the baseline; editing or confirmation renews it. `--remove` removes only the matching asserted selection, including a retained selection whose source is now absent. Removing an absent assertion is a successful no-op. Declared relations remain untouched.

A relation differs from an edge in four ways:

| | Edge | Relation |
|---|---|---|
| Staleness is passed on to chunks that rest on the marked one | Yes | No: one step only |
| It makes the chunk `derived` (MYC-2.12) | Yes | No |
| A circle is refused (MYC-2.11) | Yes | No: two chunks may each name the other |
| Search follows it from a document to code, and lists it in `documentedIn` | Yes | No |

Relations are for the few pairs that cannot be reduced to one source. When two sections rest on the same fact, the fact is written once and both cite it.

**Historical evidence (unindexed):**

- `arbol_deprecated_v1:GLOSSARY.md#Coupling`
- `arbol_deprecated_v1:GLOSSARY.md#Reference`

### Recorded verification

Observed in version 1: nothing said "this was checked". The Glossary designed it under the name [Attestation](../../arbol/GLOSSARY.md#attestation): a record of who vouched for a text, how, and against which state, which stops applying when the text or what it was checked against changes.

Proposed: the command `mycel confirm` (MYC-D12) atomically renews the chunk's dependency and relation baselines and leaves a verification record. The MYC-16 current-input check runs under the required repository locks before committing either. Its indexed dependant text must equal the exact current disk text, and every required source is re-read. Changed disk inputs return `invalid_input` with detail `changed_since_ingest`, so the caller ingests explicitly and retries; confirmation never silently ingests. A new malformed, ambiguous, disabled or unresolved reference prevents confirmation and changes no baseline or record. A previously resolved source that was deleted may be explicitly withdrawn by confirmation under MYC-7.24; any remaining declared reference to it stays a visible fault.

| The record holds | Example |
|---|---|
| The chunk and the hash of its text | `cellar:docs/net.md#Retry policy` |
| The hash of every source and every related chunk at that moment | |
| Who vouches | `ana`, `claude`, `ci`. Given with `--by`; without it, the login name of whoever ran the command |
| How | `read`: a person or an agent read the chunk beside its sources. `check`: a program checked it: tests passed, it compiled. Given with `--how`; without it, `read` |
| When | |

A chunk is *verified* while the newest record for its exact dependant version still fits: its own text, every source member and selection membership match the record. Changed, missing or presently uncheckable inputs make `current` false. Switching a branch considers only records for the resulting exact dependant version. `current` means this record matches the checked state; it does not independently verify every upstream claim. Records and their exact dependant/source evidence are retained as history until the owning chunk or repository is deleted (MYC-16). Nothing else ends a verification: there is no expiry period.

A chunk with no sources, relations or reference faults can be confirmed too. The record then vouches for its text alone.

Unverified is the ordinary state of a chunk and not a fault. A `check` counts for more than a `read`; Mycel stores which of the two it was and works out no number from it.

**Historical evidence (unindexed):**

- `arbol_deprecated_v1:GLOSSARY.md#Attestation`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges`

### Generated edges

Observed in version 1: the summariser joined each summary to the chunks it was written from with edges of the kind `generated`. Between two ends the store held one edge, so a Source Ref or an assertion between the same two turned a generated edge into another kind. Every edge also carried a field `policy`, `auto` for generated edges and `review` for the others, which no code read.

Proposed: a generated edge says that the dependant's text was produced from the source by a program and is produced again when the source changes. Nobody repairs such text by hand.

- **Made by generation only.** The program that writes summaries makes them ([MYC-8](08-summaries.md)). No file declares one and no command asserts one.
- **Held apart.** Between the same two ends a generated edge stands beside a declared and an asserted one. None of the three replaces another (MYC-2.10).
- **Pinned at successful publication.** The generation transaction pins the exact request members, their membership and snapshots with the published text (MYC-16). A failed request or abandoned staged build creates no live generated edge. `mycel confirm` is refused with `refused` for generated text.
- **Stale like any other.** Detection marks generated text by the same rules and passes staleness on through it, so a summary of summaries follows its members. Stale generated text is regeneration work for MYC-8; it is never submitted to Jev or manual semantic Drift review. MYC-14 reports that work without opening a duplicate semantic Drift.
- **No field for policy.** The kind of the edge says what a stale dependant needs.

This is not the declaration `generated: true` in a document (MYC-2.1). That marks a file some other program rewrites; Mycel never marks it stale.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#derive`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#build_tree`

### When a source is deleted

Observed in version 1: no row was ever deleted, so an edge kept pointing at the row of a source that had left the disk, and the dependant was never marked ([MYC-2](02-provenance-and-freshness.md#detection)).

Proposed: Mycel 2 deletes a chunk that is found in no location (MYC-1.21), and a dependant of it must then be stale (MYC-2.14). So the edge stays when its source is deleted. It keeps the place the source had, its repository, path and name, and the hash it was pinned to, and the dependant is stale with `source_removed`. The same holds for a relation.

- When a chunk appears at that place again, the edge joins it. If its text is the pinned one, that stale reason ends; if not, the reason becomes `source_changed`. Other reasons may still make the dependant stale. Classification and work-list treatment follow [MYC-14](14-drift-detection.md), with MYC-16 retaining the exact old source evidence.
- The edge is dropped when the dependant is edited or confirmed, when its ref leaves the file, or when the assertion is withdrawn. A ref that still stands in the file and finds nothing stays in the list of faults (MYC-2.6).

The sentence of MYC-1 that a deleted chunk goes "and its edges with it" therefore means the edges on which the deleted chunk itself rested.

An assertion can also be withdrawn on purpose. `mycel derive` and `mycel relate` take `--remove`, which deletes the matching asserted source selection and dependant and nothing a file declares.

## Requirements

| ID | Mycel must… | Origin | Verified by |
|---|---|---|---|
| MYC-7.14 | read the relations of a section from a `related` comment in its text, one ref per line, with the forms, the rules and the fault reports of Source Refs | New | store |
| MYC-7.15 | hold a relation that was asserted with `mycel relate` apart from one a file declares, so that neither removes the other | New | store |
| MYC-7.16 | mark a chunk stale with `related_changed` when a chunk it is related to no longer has the stored hash, and clear the mark by the rule of MYC-2.19 | New | store |
| MYC-7.17 | pass nothing on from a relation, give no role by it, refuse no circle of relations, and leave relations out of the search's bridge and of `documentedIn` | New | store |
| MYC-7.18 | record with every `mycel confirm` the hash of the chunk's text, the hash of every source and related chunk, who vouches, whether by `read` or by `check`, and when | New | store |
| MYC-7.19 | treat a chunk as verified exactly while its newest record matches its text and the text of everything it was checked against, and keep records that no longer apply as history | New | store |
| MYC-7.20 | confirm a chunk that has no source, and list the verifications of a repository on request | New | store |
| MYC-7.21 | hold a generated edge apart from a declared and an asserted one between the same two ends, and accept none from a file or from a command | Changed | store |
| MYC-7.22 | pin a generated edge only when its text is produced, and refuse `mycel confirm` for generated text with `refused` | New | store |
| MYC-7.23 | mark generated text stale by the rules of detection and pass staleness on through it | Kept | store |
| MYC-7.24 | keep an edge or a relation whose source was deleted, with the source's place and the pinned hash; mark the dependant with `source_removed`; join the edge to a chunk that appears at that place again; and drop it when the dependant is edited or confirmed or the link is taken away | New | store |
| MYC-7.25 | delete the matching asserted source selection and dependant on `--remove`, and nothing a file declares | New | store |
| MYC-7.26 | resolve relations through MYC-16, pin all selected members and membership atomically, preserve assertion baselines on an identical no-op, and renew them only by edit or confirmation | New | store |
| MYC-7.27 | confirm one exact current on-disk dependant version atomically with its pins and verification; refuse changed-since-ingest inputs and new invalid references without mutation | New | store |
| MYC-7.28 | determine verification applicability from the exact dependant version, source text and selection membership, and retain record-owned evidence for the verification history | New | store |
| MYC-7.29 | publish generated pins only with successfully generated text, retain the exact request evidence, and expose stale generated text as regeneration work without semantic classification | New | store |
| MYC-7.30 | return the relation assertion/removal result and complete verification evidence; make verification listing read-only, deterministically ordered and successful when empty | New | store |

On 8 October 2026, at the owner's request to research Drift detection separately, MYC-7.1 through MYC-7.13 moved out of this active requirements table to the candidate requirements of [MYC-14](14-drift-detection.md#requirements). Their numbers remain reserved and are never reused. The map is MYC-7.1 → MYC-14.1, MYC-7.2 → MYC-14.2, MYC-7.3 → MYC-14.3, MYC-7.4 → MYC-14.4, MYC-7.5 → MYC-14.5, MYC-7.6 → MYC-14.6, MYC-7.7 → MYC-14.7, MYC-7.8 → MYC-14.8, MYC-7.9 → MYC-14.9, MYC-7.10 → MYC-14.10, MYC-7.11 → MYC-14.11, MYC-7.12 → MYC-14.12 and MYC-7.13 → MYC-14.13. Their completed implementation defaults are accepted under MYC-D28/MYC-D29 on 8 October 2026; [the extraction map](14-drift-detection.md#extraction-and-identifier-map) preserves this history.

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line). The Drift commands, `Drift` and `DriftSource` reply shapes, classification evidence and repository Drift count moved to [MYC-14's interface](14-drift-detection.md#interface).

```sh
mycel confirm 'cellar:docs/net.md#Retry policy' --by ana --how read
mycel relate 'cellar:docs/api.md#Reply format' 'cellar:docs/api.md#Request format'
                                           # look at the first when the second changes
mycel relate --remove 'cellar:docs/api.md#Reply format' 'cellar:docs/api.md#Request format'
mycel derive --remove 'cellar:tests/test_retry.py#test_backoff' 'cellar:docs/limits.md#Limits > Backoff'
mycel verifications --repo cellar          # those that still apply; --history for the earlier ones too
```

```ts
interface Verification {
  id: string;
  chunk: Place;
  chunkId: string;
  version: string;
  textHash: string;
  dependantSnapshot: string;            // exact verification-owned text
  baselineManifests: string[];           // one immutable MYC-16 manifest per checked link
  sources: Array<{ place: Place; hash: string; comparisonHash: string; snapshot: string }>;
                                       // hash is exact bytes; comparisonHash is the pin comparison
  by: string;
  how: "read" | "check";
  at: string;
  current: boolean;                    // false once the chunk or anything it was checked against changed
}

interface RelationReply {
  dependant: Place;
  dependantVersion: string;
  source: Place;                       // canonical selection, not an arbitrary member
  action: "assert" | "remove";
  changed: boolean;
  members: number;
  baselineManifest?: string;
}

// StaleChunk of MYC-2 gains, in each reason:
//   kind:  also "related_changed"
//   edge:  also "related" | "generated"
//
// RepositoryStatus of MYC-1 gains:
//   chunks.verified: number;          // chunks on disk whose newest verification still applies
```

`mycel verifications` replies `{ repository, verifications: Verification[] }`: by default the newest applicable record for each current on-disk dependant version; `--history` includes all retained records. Sort by canonical root, path and chunk name, then newest time and record ID. An empty list succeeds. Listing runs no freshness pass and writes nothing; a record whose evidence cannot presently be established is not reported as current. `mycel confirm` replies with the `Verification` it recorded; `mycel relate` replies with `RelationReply`. Linked Drift closure follows [MYC-14](14-drift-detection.md#interface), without changing the accepted MYC-D12 freshness rule.

## Known problems in version 1

- **The list of work was empty by construction.** Nothing called the function that opens a Drift, and nothing closed one when its chunk recovered.
- **One path could not be stored.** A Drift for a chunk with no source left to name wrote a row the table refused, after the Drift itself was written.
- **Every change weighed the same.** A corrected typo in a source and a rewritten source gave the same mark.
- **A check left no trace.** The only way to say "this still holds" was to edit something in the file.
- **Kinds of edge replaced each other.** A ref in a file turned a generated or an asserted edge between the same two chunks into a declared one.
- **A field recorded what a stale chunk needs, and nothing read it.**
- **The step that was to check a dependant with a model rested on parts of Arbol that were never built.**

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#open_drifts`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_drift_sources`
- `mycel_deprecated_v1:mycel/knowledge/store.py#detect`
- `mycel_deprecated_v1:mycel/knowledge/store.py#derive`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges`
- `arbol_deprecated_v1:GLOSSARY.md#Drift Candidate`
- `arbol_deprecated_v1:GLOSSARY.md#Ladder`

## Decisions

MYC-D28 and MYC-D29 moved on 8 October 2026 to [MYC-14 · Decisions](14-drift-detection.md#decisions), at the owner's request for separate research and discussion. That document is their sole current record, including MYC-D29's earlier acceptance and subsequent reopening for research. MYC-D12's accepted freshness baseline remains in MYC-2. The owner subsequently selected Jev without a change-size threshold, five-minute debounce and low-confidence smarter-model review; MYC-14 now records the owner's 8 October 2026 acceptance of the completed confidence/execution and lifecycle contracts, with the smarter-model command specified in settings. Runtime qualification remains to be executed; a classifier never changes MYC-D12's pins or freshness.

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D30 | How is a relation between two chunks made, where neither governs the other? | Such a pair is, for example, the description of a request and the description of its reply: when one changes, the other needs a look. The relation is made in the same two ways as an edge: a `related` comment in the section, which travels with the file, and the command `mycel relate` for chunks that cannot carry a comment, such as a function. The smaller choice is the command alone; such a relation would then exist only in the index store and be lost when the store is made again | Decided 8 October 2026 by the owner: agreed. A `related` comment in the section, and the command `mycel relate` |
