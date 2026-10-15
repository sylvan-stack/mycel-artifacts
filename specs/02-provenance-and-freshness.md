---
role: authored
spec: MYC-2
status: accepted
---
# Mycel · 02 Provenance and freshness

A document says what it rests on, and Mycel tells its reader when that has changed. A section names its sources with [Source Refs](../../arbol/GLOSSARY.md#source-ref); Mycel turns each valid, resolved ref into an edge that remembers the source as it was; when the source moves on, the section is marked stale. This specification fixes how sources are declared, how a ref finds its target, what an edge remembers, and what makes a chunk stale and fresh again. It matters because in version 1 a stale section became fresh when anything else in its file was edited, a removed source never made anything stale, and the list of work it was meant to produce was never filled.

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: declarations in a document, Source Refs and how they resolve, edges and what they pin, roles, detection of staleness and its reasons, how a chunk becomes fresh again, what is reported.

Specified elsewhere: how chunks get their identity ([MYC-1](01-corpora-and-ingest.md)); how edges are used in search ([MYC-4](04-retrieval.md)); summaries generated from clusters of chunks ([MYC-8](08-summaries.md)). Stored Drifts, judging changed dependencies, relations without authority, recorded verification and generated edges are all required by [MYC-D13](#decisions). The later MYC-D28 decision replaces numerical source scoring with selected Jev classification without a change-size threshold, with five-minute debounce and low-confidence smarter-model review. [MYC-14](14-drift-detection.md) specifies the accepted Drift classification, execution and lifecycle contract; [MYC-7](07-drifts-and-verification.md) specifies relations, recorded verification and generated edges. Task volume is not a reason to leave any out.

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

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/chunker.py#parse_frontmatter`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`

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

The example requires `cellar` to be registered and enabled in Mycel's settings. If it is unregistered or disabled, both refs are reported as invalid and create no edges. If `cellar` is enabled but `RetryPolicy` is not yet in its index, that ref is unresolved: it remains visible and is tried again on later passes.

| Ref | Finds |
|---|---|
| `repo:path` | The file as a whole |
| `repo:path#Symbol` | One symbol of a code file. A class name also finds every method of the class |
| `repo:path#Heading path` | One section of a document, by its heading path or by its bare title |

Checkout Markdown is document content under MYC-D7. File lookup therefore checks both `code_root` and `artifact_root`, retaining the actual root binding and relative path. A `repo:path` address continues to resolve as before when it identifies one physical file. Aliases through overlapping roots refer to that same file, not two sources. If the path identifies different files in the two roots, report `ambiguous_path` with their root-aware places and canonical qualified addresses, and create no guessed edge. A heading cannot silently choose a file when the file path itself is ambiguous. [MYC-16](16-source-addresses-and-evidence.md#portable-addresses) completes the portable `repo:@code/path#name` and `repo:@artifact/path#name` grammar, escaping and shared resolver. File-wide sources pin complete bytes including frontmatter; class sources pin their member list as well as member hashes, so additions/removals are detected.

What deserves a ref is a claim: a section cites what it says something about, not everything that was read to write it.

Three things were loose. A piece of the comment that did not look like a ref was dropped without a record. A bare title that occurred several times in the target file found all of them. A ref that found nothing was written into the chunk's own record, which no command showed; the guides called this loud.

A ref was compared with the repository names stored in the index, exactly as written. Nothing checked whether the repository was switched on, or known to the settings.

Proposed: the same forms, with targets limited to repositories registered and enabled in Mycel's settings ([MYC-D11](#decisions)). A ref into an unregistered or disabled repository is invalid: it is kept as written and reported, and creates no edge. There is no outside-reference exemption. Enablement is checked on every pass, including for refs that previously resolved. A piece that is not a ref, a valid ref that finds nothing and a bare title that fits several sections are also reported: in the reply of the pass, and in a list that can be asked for. Nothing is silently dropped. A valid unresolved ref remains retryable on every pass of its repository and of the enabled repository it targets; a change to the settings causes previously invalid refs to be checked again.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/chunker.py#parse_source_refs`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_resolve_source_ref`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges`

### Edges

Observed in version 1: an edge joins a source to the chunk that rests on it and stores the source's content hash at the moment the edge was written. There were three kinds.

| Kind | Made by | Meaning |
|---|---|---|
| `declared` | A Source Ref in a file | The file's own claim. Removing the ref removes the edge |
| `asserted` | The command `mycel derive` | A claim made outside the file |
| `generated` | The summariser | The chunk was produced from the source by a program |

A source could be a chunk or a whole file. For a section, the hash covered the text directly under its heading, not its subsections. For a file, it covered every byte.

Between one source and one chunk the store held one edge, so the kinds overwrote each other: a ref in the file turned an asserted edge into a declared one, and removing the ref then deleted the assertion with it.

Proposed: declared and asserted edges are kept apart, so that a file can never remove what a person asserted. An edge that would close a circle is refused. A declared edge whose Source Ref targets an unregistered or disabled repository does not remain active; the ref is retained and reported as invalid. Generated edges are also required ([MYC-D13](#decisions)); their complete behavior is specified by MYC-7 and MYC-8 and awaits implementation.

Deleting a source file or chunk removes its indexed rows and resolved edges, but a surviving dependant retains a dependency record of the source's natural place, edge kind, pinned hash and exact baseline manifest under [MYC-16](16-source-addresses-and-evidence.md#a-baseline-owned-by-the-dependant). That record and its immutable evidence belong to the dependant, not to the deleted source. They supply the `source_removed` reason and retries resolution when the enabled source repository is checked again. Restoring the source reconnects the existing dependency and its pinned hash; it does not create a new baseline by itself. Removing a declared ref or explicitly removing an assertion removes its corresponding dependency record and releases its evidence references, while retained verification/Drift history may still own those bytes. A ref that never resolved is reported as unresolved, rather than as a source that was removed.

Each resolved dependency selection has a baseline manifest recording the source declaration, exact source/dependant snapshots, comparison revision/hash, resolved members and capture location. It is written atomically with the first pin or an authorized repin. Every dependant text version keeps its own existing baseline through branch/stash transitions; normalized-equivalent text and recognized renames inherit pins rather than silently confirming claims. A file/class-family selection compares complete file bytes or the pinned ordered membership plus member comparisons. A disappeared member or newly added method cannot be hidden by comparing only old resolved edges. Snapshot capture, missing/corrupt evidence, exact reconstruction and owner-based retention are fixed in MYC-16.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges`
- `mycel_deprecated_v1:mycel/knowledge/store.py#derive`
- `mycel_deprecated_v1:mycel/knowledge/store.py#assert_derivation`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_parent_hash`

### Roles

Observed in version 1: a chunk's role says whether anything governs it. A chunk with at least one edge pointing at it was `derived`. Without one, a code chunk was `authored`, and a section of a document was whatever its file declared, or `unclassified`. The file's declaration took effect only when a chunk was first created; changing it later changed nothing, and a chunk that lost its edges fell to `unclassified` whatever the file said.

Proposed: the role is worked out on every pass from the edges and the file's declaration, and never remembered against them. A dependency whose previously resolved source is now missing from an enabled repository still governs its dependant through the retained dependency record; deleting the source does not turn the dependant into an authored chunk. A ref made ineligible by the settings retains the invalid-ref treatment above.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges`

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

Decided on 8 October 2026 by the owner: source changes must be reflected in searches of the chunks that depend on them, including dependencies across repositories. After both corpora of each checked repository are ingested, detection compares their explicit declared and asserted dependencies and propagates any change in stale state through every downstream dependant, across repositories. It updates only affected dependency records and marks; unrelated repositories are left alone. Heartwood and generated chunks keep the exception of MYC-2.16. Ingesting a source does not edit its dependants or confirm their claims.

A source that is gone makes its dependants stale using the retained missing-source record. A direct reason names that source by repository, path and heading or symbol. An indirect reason names the original source and the path through the intermediate chunks, so a Driver chunk can report that it is stale because a governing contract depends on a changed Glossary section. This follows only recorded refs and assertions; merely mentioning a term creates no dependency. Detection looks at the versions on disk ([MYC-1](01-corpora-and-ingest.md#branches-and-stashes)): a source that is not on disk is gone, whatever branch or stash still holds it.

Search and read first check the enabled repositories that supply their results and the repositories of their explicit upstream sources recursively ([MYC-4](04-retrieval.md#freshness-on-read)). A check that is disabled, unfinished, busy, refused or failed leaves the applicable dependencies visibly unchecked. Stored marks and reasons are still returned, but absence of a stale mark does not claim that unchecked sources are current. A check never repins an edge merely because it read or ingested the source; MYC-D12 still determines when the dependant becomes fresh again.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#detect`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_parent_hash`
- `mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked`

### Becoming fresh again

Observed in version 1: nothing said "this was checked". A stale chunk became fresh when its edge was written again, which happened for any change to its file, or when the source went back to what it had been, or when the ref was removed.

Proposed: an edge is pinned to the source's current state in three cases only: when it is first made; when the chunk that rests on it is itself edited; and when its owner confirms, with a command, that the chunk was checked against its sources and still holds ([MYC-D12](#decisions)). An edit to another part of the file changes nothing. Nor does a switch of branch: the hash an edge stores is kept for each version of the chunk that rests on it, so a version that leaves the disk and comes back is compared with the hash it had.

An edit or confirmation answers the direct comparison reasons for the evidence it pins. It does not acknowledge an unresolved ref or certify a source's own upstream claims. Detection repropagates any remaining upstream-stale/ref-fault reason under MYC-2.15; classification or a direct confirmation cannot silently override that reason. Exact versions, comparison-equivalent edits and carried pins follow [MYC-16](16-source-addresses-and-evidence.md#comparison-hashes-and-exact-versions).

### The list of work

Observed in version 1: a stale chunk was meant to open a [Drift](../../arbol/GLOSSARY.md#drift), a stored item of work that names every source that contributed. The function that opens them existed and nothing called it. The command that lists them read a table nothing filled. A Drift was closed only when its chunk became Heartwood or generated, never when it stopped being stale.

Required by [MYC-D13](#decisions): implement all five provenance designs. [MYC-14](14-drift-detection.md) now specifies Jev classification, debounce, explicit bounded execution, uncertain-case review, Drift lifecycle and replies; [MYC-7](07-drifts-and-verification.md) specifies relations, verifications and generated edges; [MYC-16](16-source-addresses-and-evidence.md) specifies portable addresses and retained exact evidence. The owner accepted these completed contracts and the final MYC-D28/MYC-D29 proposals on 8 October 2026. Hash detection and stale reporting remain alongside them, and the accepted MYC-D12 edit-or-confirmation baseline is unchanged. No feature is deferred for task volume.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#open_drifts`
- `mycel_deprecated_v1:mycel/knowledge/store.py#list_drifts`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_drift_sources`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_drifts`

### Which documents describe a chunk

Proposed on 14 October 2026, and open until the owner decides [MYC-D39](#decisions). It is not part of the accepted contract before then.

The owner wants important code to be checkable against the document it comes from, and code that no document describes to be easy to find, because such code goes stale without anyone noticing. Mycel already records the links that answer this, but no reply shows them in full. A search names at most two citing sections, and only once they are embedded ([MYC-4](04-retrieval.md#what-a-result-says)). `mycel read` names a source only when it has changed ([MYC-11](11-reading-a-chunk.md#the-reply)).

A document *describes* a chunk when one of its sections is joined to the chunk by a declared or an asserted dependency (Edges), in either direction:

| Direction | Example |
|---|---|
| The chunk rests on the section | `mycel derive 'cellar:src/net/retry.py#RetryPolicy.allow' 'cellar:docs/limits.md#Limits > Backoff'`: the function implements that section of the specification |
| The section rests on the chunk | The Source Refs of `cellar:docs/net.md#Retry policy` cite `cellar:src/net/retry.py#RetryPolicy`: the section describes that class |

Only direct dependencies count. A relation of MYC-7 does not, nor does a summary, an overview or another code chunk. A section that cites a whole file or a class family describes each code chunk of it.

`mycel read` lists every such section for the chunk it reads, and each code result of a search says whether any section describes it. `mycel undocumented` lists the code chunks of a repository that no section describes, optionally only below given paths, so that tests and scripts can be left out. Before it lists, it checks and ingests changes in the repository as a search does (MYC-4.18), with the same option to turn the check off. The list shows the links as they are: it makes no link, and it does not judge which code needs one. Which code is important enough to need a document is decided by the people and agents who write it.

## Requirements

| ID | Mycel must… | Origin | Verified by |
|---|---|---|---|
| MYC-2.1 | read `role`, `status: heartwood` with `implemented` and `outdated`, `generated` and `sources` from a document's frontmatter as YAML, and ignore every other key | Changed | unit |
| MYC-2.2 | report a frontmatter block it cannot read and a known key with a value it does not take, for the file they are in | Changed | unit |
| MYC-2.3 | read the Source Refs of a section from the sources comment in its text, one per line, and attach the frontmatter's `sources` to the document's first chunk | Kept | unit |
| MYC-2.4 | ignore a sources comment inside a code fence or inline code | Changed | unit |
| MYC-2.5 | resolve refs only into registered, enabled repositories: a path to one physical file under its actual code or artifact root, a symbol to that file's code chunk and class family, and a heading to that file's document section by full path or unique bare title; deduplicate overlapping-root aliases and never resolve a colliding file path without an explicit root | Changed | store |
| MYC-2.6 | retain and report malformed refs, unregistered/disabled targets, valid refs finding nothing, colliding file paths and ambiguous headings in the pass reply and list on request; include root-aware candidates for ambiguous paths and silently drop none | Changed | store |
| MYC-2.7 | treat a ref into an unregistered or disabled repository as invalid, create no edge from it, deactivate a previously resolved declared edge when its target becomes ineligible, and retain the ref and its fault for reporting. Check eligibility on every pass; no outside-reference exemption applies | New | store |
| MYC-2.8 | retain a valid unresolved ref and try it again on every pass of its repository and of the enabled repository it points into; recheck invalid refs when the settings change | Changed | store |
| MYC-2.9 | hold for each resolved ref into an enabled repository an edge from the source to the chunk, storing the source's content hash, and remove the edge when the ref leaves the file | Changed | store |
| MYC-2.10 | hold an asserted edge apart from a declared one between the same two ends, so that neither a file nor a command removes the other's | Changed | store |
| MYC-2.11 | refuse an edge from a chunk to itself and an edge that would close a circle, and report it | New | store |
| MYC-2.12 | work out a chunk's role on every pass: `derived` with at least one edge pointing at it or a retained dependency whose previously resolved source is missing from an enabled repository; otherwise what its file declares; otherwise `authored` for code and `unclassified` for a section | Changed | store |
| MYC-2.13 | mark a chunk stale when a source of it has a content hash other than the one its edge stores, with a reason that names the source by repository, path and name | Changed | store |
| MYC-2.14 | mark a chunk stale when a source of it is gone, with a reason that says so | Changed | store |
| MYC-2.15 | pass staleness on through every downstream dependency across repositories, keeping every applicable reason, direct ones before passed-on ones; an indirect reason names the original source and the path through intermediate chunks | Changed | store |
| MYC-2.16 | never mark a Heartwood or generated chunk stale, and pass nothing on through it | Kept | store |
| MYC-2.17 | decide staleness by comparing hashes, with no model and no network | Kept | unit |
| MYC-2.18 | run detection after both corpora of each checked repository were ingested, propagate changed stale state through all downstream dependants across repositories under their locks, and change no unrelated dependency records or marks; report updates that could not be applied as pending | Changed | store |
| MYC-2.19 | write a new hash into an edge only when the edge is made, when the chunk that rests on it is itself edited, or when its owner confirms the chunk. A change elsewhere in the chunk's file writes none | Changed | store |
| MYC-2.20 | list on request the stale chunks of a repository, each with its reasons and the sources behind them, alongside the stored Drifts and exact-evidence lifecycle specified by MYC-14/MYC-16 | Changed | store |
| MYC-2.21 | state in the status of a repository how many of its chunks are stale, how many of its refs are valid but unresolved and how many are invalid because their repository is unregistered or disabled | Changed | store |
| MYC-2.22 | work out edges and staleness for the versions of chunks that are on disk, treat a source that is not on disk as gone, and keep the hash an edge stores for each version of the chunk that rests on it, so that a switch of branch renews none | New | store |
| MYC-2.23 | implement all five designs required by MYC-D13: stored Drifts, judging changed dependencies through selected Jev classification without a change-size threshold and its debounce/review policy under MYC-D28, relations without authority, recorded verification and generated edges. Follow their accepted MYC-7/MYC-14/MYC-16 contracts; defer none merely for task volume | New | store |
| MYC-2.24 | retain in a surviving dependant the natural place, kind and pinned hash of a previously resolved source that is removed, report it as `source_removed`, and retry its resolution without renewing that baseline; retain no deleted source chunk or version for this purpose | New | store |
| MYC-2.25 | use MYC-16's portable qualified addresses and central typed resolver, including file bytes and pinned class-family membership, and return canonical addresses in places and ambiguity candidates | New | store |
| MYC-2.26 | capture exact dependant-owned baseline manifests atomically with authorized pins, preserve per-version/inherited baselines across branches, renames and normalized-equivalent edits, and expose missing/corrupt evidence without substituting a new baseline | New | store |
| MYC-2.27 | list with `mycel undocumented` the code chunks of a repository's on-disk versions that no document section describes by a direct declared or asserted dependency in either direction, optionally only below given paths, sorted by root, path and name | New | store. Proposed under MYC-D39, not active before the owner decides |

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

```sh
mycel stale --repo cellar                                  # the stale chunks, with reasons and sources
mycel refs --repo cellar --unresolved                      # unresolved refs, invalid target repositories and other faults
mycel derive 'cellar:tests/test_retry.py#test_backoff' 'cellar:docs/limits.md#Limits > Backoff'
                                                           # assert: the second governs the first
mycel confirm 'cellar:docs/net.md#Retry policy'            # checked against its sources: still holds
mycel derive 'cellar:@code/tests/test_retry.py#test_backoff' 'cellar:@artifact/docs/limits.md#Limits%20%3E%20Backoff'
mycel undocumented --repo cellar --path src                # proposed, MYC-D39: code below src/ that no document describes
```

```ts
interface StaleChunk {
  chunk: Place;
  reasons: StaleReason[];
}

interface StaleReason {
  kind: "source_changed" | "source_removed" | "upstream_stale";
  source: Place;                       // original source that changed or disappeared
  edge: "declared" | "asserted";       // dependency into the reported chunk
  via?: Place[];                       // upstream_stale: intermediate chunks, source-to-dependant order
  classification?: ClassificationRecord; // MYC-14 exact-pair judgement; does not clear this stale reason
}

interface Place {
  repository: string;
  root: "code" | "artifact" | "index"; // actual configured binding, or generated index-only namespace
  path: string;                        // relative to that root, or an index-only place
  name?: string;                       // symbol or heading path
  address: string;                     // MYC-16 canonical qualified text; portable and copyable
}

interface RefFault {
  chunk: Place;
  ref: string;                         // as written in the file
  fault: "not_a_ref" | "not_found" | "ambiguous_path" | "ambiguous_title" | "unknown_repository" | "disabled_repository";
  candidates?: Place[];                // root-aware candidates for ambiguous_path
}

// Proposed, MYC-D39:
interface DocumentLink {               // a document section that describes a chunk; used by MYC-4 and MYC-11
  section: Place;
  direction: "source" | "dependant";   // source: the chunk rests on the section; dependant: the section rests on the chunk
  edge: "declared" | "asserted";
}

interface UndocumentedReply {          // mycel undocumented
  repository: string;
  paths: string[];                     // the --path filters; empty for the whole repository
  chunks: Place[];                     // code chunks that no document section describes, by root, path and name
  freshness: { checked: boolean; finished: boolean; repositories: RepositoryCheck[] };   // MYC-4
}
```

`not_found` means a ref targets an enabled repository but its file or chunk is not found; it remains retryable. `unknown_repository` and `disabled_repository` make the invalid target visible. The complete proposed interfaces for stored Drifts and dependency classification are in [MYC-14](14-drift-detection.md#interface). Relations, recorded verification and generated edges remain in [MYC-7](07-drifts-and-verification.md#interface) (MYC-D13).

## Known problems in version 1

- **Stale did not stay stale.** Any edit to a file renewed every edge of every section in it.
- **A removed source was not noticed.** Neither a deleted file nor a renamed heading or function made the sections that cited it stale.
- **The work list was empty by construction.** Nothing opened a Drift, and nothing closed one when its chunk recovered.
- **Kinds of edge overwrote each other.** A declared ref could replace an assertion, and removing the ref then removed both.
- **Faults in refs were silent.** A ref that found nothing was stored where no command showed it. A malformed line was dropped. Nothing checked whether its target repository was registered and enabled. A comment inside inline code made edges.
- **Detection ignored the scope of a pass.** A pass for one repository rewrote the marks of all, and two such passes could do so at once.
- **Code changes showed one pass late.**
- **A role, once given, stuck.** A file's declaration applied only to chunks made while it was there.
- **A reason could not be followed.** It named its source by characters that many rows share.
- **Circles were possible.** Nothing refused an edge from a chunk to itself, and the two functions that walk edges had no guard.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges`
- `mycel_deprecated_v1:mycel/knowledge/store.py#detect`
- `mycel_deprecated_v1:mycel/knowledge/store.py#open_drifts`
- `mycel_deprecated_v1:mycel/knowledge/store.py#derive`
- `mycel_deprecated_v1:mycel/knowledge/store.py#impact`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#parse_source_refs`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D11 | Which repositories may Source Refs target? | Only repositories registered and enabled in Mycel. Other targets are invalid and reported; valid unresolved refs remain retryable | Decided 8 October 2026 by the owner: Source Refs may target only Mycel-enabled repositories. No outside-reference exemption; disabled or unregistered targets are invalid and visible, and valid unresolved refs are retained for retry |
| MYC-D12 | What makes a stale chunk fresh again? | An edit to the chunk itself, or the command that confirms it. An edit to another part of its file does not. The stricter choice, confirmation only, would leave a section stale after its prose was repaired | Decided 8 October 2026 by the owner: editing that section or explicitly confirming it clears the stale mark. A file scan or an edit to another section does not |
| MYC-D13 | Which of the designs version 1 did not build are taken up? | All five are required: stored Drifts, scoring of how much a source changed, relations without authority, recorded verification and generated edges. Complete their remaining detailed specifications and implementation | Decided 8 October 2026 by the owner: implement all specifications regardless of the number of tasks, including all five previously deferred designs. Task volume is not a reason to defer them; their remaining detailed specifications and implementation are required follow-up work. The later MYC-D28 decision replaces the former numerical scoring design with selected Jev dependency classification without a change-size threshold, with five-minute debounce and low-confidence smarter-model review |
| MYC-D39 | How does Mycel answer "which document describes this chunk?", and show code that no document describes? | `mycel read` lists every document section joined to the chunk by a direct declared or asserted dependency, in either direction, complete and without waiting for embeddings. Each code result of a search says whether any section describes it. `mycel undocumented` lists a repository's code that no section describes, optionally below given paths. Mycel does not decide which code needs a document. The alternative: keep search's `documentedIn`, at most two citing sections, as the only answer | Open. Raised by the owner on 14 October 2026: "All I really want is to have answer to question 'which document describes this code chunk?' and when there is no origin document I want mycel to be able to find out this easily" |
