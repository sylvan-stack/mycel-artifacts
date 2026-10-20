---
role: authored
spec: MYC-1
status: accepted
---
# Mycel · 01 Corpora and ingest

Ingest turns the files of a repository into [Chunks](../../arbol/GLOSSARY.md#chunk) with a stable identity: a section of a document or a symbol of a code file keeps its identifier through edits and renames, so that everything attached to it survives. This specification fixes which files are read, how they are split, how a chunk is recognised again, and what one pass over a repository does. It matters because version 1 could miss an edit to a code file altogether, reset a working checkout to its remote, and never removed a row.

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: repositories and their two corpora, the settings that name them, which repository a command means, the scan, branches and stashes, splitting documents and code into chunks, identity, what happens to files that leave the disk, the pass, status, removing a repository.

Not covered: edges between chunks and staleness ([MYC-2](02-provenance-and-freshness.md)); vectors ([MYC-3](03-embedding.md)); search and the freshness check that starts a pass ([MYC-4](04-retrieval.md)); the generated overview of a repository's code ([MYC-9](09-code-overview.md)); the settings file as a whole ([MYC-5](05-settings.md)); the index store ([MYC-6](06-index-store.md)); the record of a pass and its identity decisions ([MYC-12](12-record-of-work.md)).

## Behaviour

### Repositories and corpora

Observed in version 1: a repository is known by a short name and has two [corpora](../../arbol/GLOSSARY.md#corpus). Its document corpus is the Markdown files under its document folder. Its code corpus is the source files under its code folder, or under the subfolders of it that the settings list. Either may be missing: a repository can have documents only.

Decided under MYC-D7: the document corpus includes Markdown under both `artifact_root` and `code_root`, including a checkout's `README.md` and `docs/`. These files are documents wherever they live: they are split at headings and returned with document origin. The code corpus still contains the configured source file types under the code folder or its `code_subdirs`. Restricting source-code subfolders does not exclude Markdown elsewhere in `code_root`. Either root may be absent.

A document retains the actual configured root it was read under and its path there. Checkout documents are not assigned paths under `artifact_root`. If the roots overlap and reach the same file, it is indexed once per disk, branch or stash location. Different files in different roots remain distinct even when their relative paths or contents match; neither is silently merged with or preferred over the other. The ordinary identity rules for genuine moves still apply. Search results, reads and Source Refs identify the actual root and path, and report a bare path that fits different files as ambiguous. [MYC-16](16-source-addresses-and-evidence.md#portable-addresses) defines portable `repo:@code/path#name` and `repo:@artifact/path#name` addresses, preserving unambiguous legacy refs and stable chunk identifiers. Its root-alias rule keeps one primary address for an overlapping-root file.

Observed in version 1: the settings file `~/.mycel/config.toml` named the repositories. For each one it could give whether it is enabled, its code folder, its document folder and the subfolders that form the code corpus. A repository that is a direct child of a configured organization folder needed no folders of its own: its code was its checkout, and its documents lay under the organization's document folder. Every command copied the repositories from the file into the index store, and the store's copy then took part in decisions. A key removed from the file stayed in the store. `enabled` was not checked for its type, so the text `"false"` switched a repository on.

Observed in version 1: no setting said which organization a repository belongs to. Mycel found it by folder. A repository without a code folder was a member of the organization whose folder had a direct child of that name with a git checkout in it. A repository with a code folder was a member of the organization whose folder was the parent of that folder, and of none otherwise. A name found under two organizations stopped the command with a request to set `code_root`. It also stopped every other command that had to find its repository from the current directory.

Proposed: the settings file is the only place that says which repositories exist and where they are. Nothing in the store stands in for it. A file that cannot be read, an unknown table or key, or a key of the wrong type refuses commands that need valid settings and names the fault. Unknown-key errors identify the file and fully qualified key and explain how to correct it ([MYC-D23](05-settings.md#decisions)); `info` remains diagnostic and `grep` still runs grep. A repository's organization is still found by folder. A name found under several organizations, in a repository that gives no code folder, is a fault of that repository alone: a command that needs its folders is refused and names the organizations, and commands for other repositories go on.

```toml
[organizations."Orchard"]
root = "~/repos/orchard"

[repos.presses]                 # a member of the organization: folders follow from it
enabled = true

[repos.cellar]                  # a repository of its own
enabled = true
code_root = "~/repos/cellar"
artifact_root = "~/Artifacts/cellar"
code_subdirs = ["src", "tests"]
```

`presses` gives no folders. Mycel looks for a folder of that name directly under the folder of each organization and finds `~/repos/orchard/presses`: `presses` is a member of Orchard, and its documents lie in the folder `repos/presses` of Orchard's document folder. `cellar` gives its own folders and is a member of no organization.

If a second organization also had a folder `presses`, the name would not say which one is meant. `code_root` says it, and the other checkout is listed under a name of its own:

```toml
[repos.presses]                 # the checkout under Orchard
enabled = true
code_root = "~/repos/orchard/presses"

[repos.vineyard-presses]        # the checkout under Vineyard
enabled = true
code_root = "~/repos/vineyard/presses"
```

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/config.py#load`
- `mycel_deprecated_v1:mycel/config.py#apply`
- `mycel_deprecated_v1:mycel/locations.py#RepositoryLocations`
- `mycel_deprecated_v1:mycel/locations.py#RepositoryLocations.organization`
- `mycel_deprecated_v1:mycel/organizations.py#members`
- `mycel_deprecated_v1:mycel/knowledge/store.py#set_repo_flags`
- `mycel_deprecated_v1:tests/test_repository_locations.py#test_duplicate_members_require_explicit_code_root`

### Which repository a command means

Observed in version 1: a command took the repository it was given, or else the one whose code or document folder contained the current directory, the longest folder winning. When neither gave one, it took a repository called `arbol`. Two older folder layouts were still searched, and one environment variable overrode everything. The name `Arbol` was rewritten to `arbol`; no other name was touched. A directory in an organization's folder but in none of its members gave the organization's name, and a search then ran once for each member.

Proposed: the named repository, or the one the current directory belongs to. Names are used as written. The MYC-D37 packaged shared selections and scan exclusion are explicit data exceptions; they create no repository, alias or folder fallback. An organization stands for every enabled member of it: a command that names the organization, or that is run without a name in a directory of the organization's folder that is in none of its members, acts on each of them in turn. When nothing gives a repository, or the organization has no enabled member, the command is refused.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/scope.py#resolve`
- `mycel_deprecated_v1:mycel/locations.py#RepositoryLocations.scope_bindings`
- `mycel_deprecated_v1:mycel/repo_identity.py#canonical_repo`
- `mycel_deprecated_v1:mycel/cli.py#search_payload`
- `mycel_deprecated_v1:tests/test_organizations.py#test_scope_distinguishes_member_and_organization`

### The scan

Observed in version 1: the two corpora were scanned by separate code with different rules.

| | Documents | Code |
|---|---|---|
| Files taken | Every `*.md` | `.py`, `.svelte`, `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs`, `.cjs`, `.sh`, `.bash`, `.plist`, `.plist.in`, `.swift` |
| Folders skipped | `.git` only | `.git`, `node_modules`, `.venv`, `venv`, `__pycache__`, `build`, `dist`, `coverage` and a dozen more, at any depth |
| Unchanged file | Skipped when its SHA-256 equals the stored one | The same |
| Size limit, `.gitignore` | None | None |

A file that left the disk had its document and chunks marked as gone. Nothing guarded against a scan that found nothing: a wrong folder or a narrowed list of subfolders marked every row of the repository as gone.

Decided under [MYC-D7](#decisions): one scan for both corpora with one list of skipped folders, which also honours the repository's `.gitignore`. The file types are settings with version 1's lists as defaults. Markdown is read from both `artifact_root` and `code_root` as documents, independently of source-code `code_subdirs`, with the same exclusions. Overlapping roots do not produce duplicate files or chunks.

Proposed: a pass that would find none of a corpus's documents on disk, while the store holds some that were there, is refused unless the caller confirms it.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#_scan_corpus`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_scan_code`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code`

### Branches and stashes

Observed in version 1: the index held the files as they lay on disk and nothing else. By the rules of the scan and of identity, a switch to another branch was read as removals and edits: what the branch lacked was marked as gone and got a new identity when it came back, and what differed lost its vector and was embedded again (inferred from those rules, not seen happening). Beside this, version 1 could keep a view of the index per work tree; its commands were retired, and no view was registered on 7 October 2026 ([MYC-D6](00-overview-and-legacy-map.md#decisions)).

Proposed: Mycel reads a repository in every location where its files are on this machine ([MYC-D8](#decisions)).

| Location | What is read |
|---|---|
| The disk | The files of the folder as they are, uncommitted changes included |
| A local branch | The files of the branch's last commit |
| A stash | The files as the stash holds them, untracked ones included |

Branches and stashes are read from the git store of the checkout a folder lies in, with commands that change nothing: nothing is checked out and nothing is fetched ([MYC-D9](#decisions)). The branches of a remote are not read. The rules of the scan hold in every location. A folder that lies in no git checkout has one location, the disk. A stash is known by its commit, because its number in the list shifts.

These rules also hold for Markdown under either root. A document keeps its actual root/path address and stable chunk identifiers through its disk, local-branch and stash versions, and a file reached through overlapping roots is not duplicated within the same location. Search, edges and staleness continue to use only the versions on disk.

A chunk is stored once for each text it has. Each of these is a version of the chunk, and a version records the locations it is found in. Most files are the same on every branch, so most chunks have one version, found everywhere. In the fictional checkout below the branch `feature` is checked out; `renew` is the same on both branches and `expire` differs.

| Chunk | Version | Found in |
|---|---|---|
| `renew` | The only one | The disk, `main`, `feature` |
| `expire` | As on `main` | `main` |
| `expire` | As on `feature` | The disk, `feature` |

A switch to `main` changes one thing: which version of `expire` is on disk. Nothing is split again and nothing is embedded again ([MYC-3.5](03-embedding.md#requirements)). Search, edges and staleness look at the versions on disk ([MYC-4.26](04-retrieval.md#requirements), [MYC-2.22](02-provenance-and-freshness.md#requirements)).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_overlay`

### Splitting a document

Observed in version 1, and kept: a Markdown file is split at its headings. Each heading owns its own line and the text down to the next heading of any level; a subsection is a chunk of its own and not part of its parent's text. Text before the first heading is one chunk. Lines inside a code fence are never headings. The chunk's name is its heading path, the titles from the top joined by ` > `, such as `Setup > Database > Backups`.

Two comparison hashes are kept for a section. The content hash covers the body without the heading line, after NFKC Unicode normalisation and with every run of Unicode white space reduced to one space and outer whitespace stripped, so that re-wrapping a paragraph changes no body comparison. The title hash covers the parsed heading title with the same normalization, so that a renamed heading with the same body is recognised as the same section. These are SHA-256 hashes of UTF-8 normalized text. The exact snapshot hash separately covers every byte of the complete stored text; [MYC-16](16-source-addresses-and-evidence.md#comparison-hashes-and-exact-versions) records comparison revisions and distinguishes identity/comparison from exact versions and evidence.

There was no limit on the size of a section.

Proposed: kept, with two corrections. A name is unique within its file: the second section with the same heading path gets a number. The leading block of settings at the top of a file (the frontmatter) is read as settings and is not part of the first chunk's text.

Decided on 19 October 2026 ([MYC-D45](17-justification.md#decisions)): a row of a Requirements or Decisions table whose first cell is exactly a human id, `MYC-2.13` or `MYC-D45`, followed by an HTML comment with the row's UUID, is split out as a chunk of its own beside the section that holds it, of kind `req` or `dec`, named by the human id and keyed by the UUID. The section keeps its own chunk with its complete text and hashes. A recognised row without a UUID, and two rows with one UUID, are reported faults of the file, and no entity is made of them. [MYC-17](17-justification.md#requirements-and-decisions-are-entities) says what the row holds.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/chunker.py#chunk_markdown`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#content_hash`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#norm`

### Splitting code

Observed in version 1: a code file is split along its own structure, and each chunk carries its language, kind and line span. Its name is the file's path, `#`, and the symbol.

| Language | Parsed with | Chunks |
|---|---|---|
| Python | The language's own syntax tree | Each top-level function; each class as a header and one chunk per method (`Class.method`); what lies between as module chunks |
| TypeScript, TSX, JavaScript | tree-sitter | Functions, classes with their methods, interfaces, types, enums, namespaces; module chunks between them |
| Svelte | A pattern for its blocks | Each `script` and `style` block; the markup between |
| Shell, property lists, Swift | Not parsed | The whole file as one chunk |

A file that cannot be parsed becomes one whole-file chunk, so nothing is dropped. There was no limit on the size of a chunk.

Three things made names unreliable. Chunks between symbols were numbered by position, so a new one early in a file renumbered all that followed, and each then took over its predecessor's stored row. Two symbols with the same name, such as a getter and its setter, got the same name, and one of the two rows was never updated again. A decorator was not part of what it decorates: it fell into the chunk before it, or became a chunk of one line.

Proposed: the same structure, with names that are unique within a file and do not depend on position ([MYC-D10](#decisions)), and with decorators and leading comments inside the chunk of what they belong to.

A chunk between symbols is a run of lines that belongs to no function and no class: imports, constants, statements at the top level. In the fictional file below, each comment gives the part of the chunk's name after `#`, as proposed and as version 1 had it.

```python
import time                     # <before renew>      version 1: <module>
LIMIT = 3

def renew(key):                 # renew
    ...

RETRIES = {}                    # <before expire>     version 1: <module:1>

def expire(key):                # expire
    ...

if __name__ == "__main__":      # <end>               version 1: <module:2>
    renew("a")
```

`<before renew>` is the run that stands before the function `renew`, and `<end>` is the run after the last symbol. Suppose the file began with `def renew` and its first two lines are added later. Version 1 moves every number up by one: the row stored as `<module>` receives the imports and the row stored as `<module:1>` receives `RETRIES = {}`. Both lose their vectors, though neither chunk was edited. With the proposed names the pass finds one new chunk, `<before renew>`, and no other name changes.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_code`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_python`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_typescript`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_svelte`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#_uncovered_runs`

The model's input limit does not change these logical chunks. Embedding may divide a chunk version's complete text into several inputs, each with its own vector, without creating new chunk identities or changing its heading or symbol name ([MYC-3](03-embedding.md#embedding-parts)).

### Identity

Observed in version 1, for documents: a chunk of a changed file was matched against the stored chunks of the same file. A stored chunk with the same name was the same chunk: unchanged when the content hash matched, edited when not. Failing that, a stored chunk with the same content hash was the same chunk under a new name: renamed. What matched nothing was new; stored chunks nothing matched were marked as gone. A file moved without a change kept its document and all its chunks. Every decision was written to a log that nothing ever read.

The matching went through the file once, and a chunk without a name match took the first stored chunk with the same content. Every section without body text has the same content hash, so a new empty section could take over the identity of an existing one, and the sections after it shifted. Everything attached to an identifier moved with it.

Observed in version 1, for code: a chunk was matched by name only. A renamed function was a removed chunk and a new one. Nothing was logged.

A row marked as gone was never matched again and never deleted. A section removed and restored got a new identity. Observed on 7 October 2026: a fifth of the rows of the largest repository were rows that had left the disk.

Proposed: one way of matching for documents and code, in two rounds over the whole file: every name match first, then content matches among what is left. A chunk with no body never matches by content. A separate parser-derived code identity key is permitted under MYC-D38. It erases only the structurally identified declaration name from the complete chunk; it retains the signature, body, comments and all other bytes. This conservative body/signature projection lets a name-only function or method rename match in round two while a changed signature/body cannot supply that match. Its revision, language and structural kind are bound into the key. Chunks without a structurally identified declaration name use their complete-code comparison. The complete-code hash, exact source bytes, versions, evidence comparisons and vectors remain independently unchanged in meaning. A chunk is recognised by the same rules in every location, the disk first and the branches and stashes after it in a stated order, so it has one identifier wherever it is found ([Branches and stashes](#branches-and-stashes)). A `req` or `dec` chunk takes no part in the two rounds: its identifier is the UUID of its row, in whichever section, file or chapter the row stands, and its row is never deleted (MYC-D45).

A version that is found in no location is removed, and the pass that finds it so deletes its rows. A chunk with no version left is deleted, and its resolved edges with it. A surviving dependant retains the source's natural place, the hash it last answered to and its exact pinned evidence in its own dependency record, so the deleted source remains a reportable missing source and can be resolved again ([MYC-2](02-provenance-and-freshness.md#edges), [MYC-16](16-source-addresses-and-evidence.md#a-baseline-owned-by-the-dependant)). Evidence blobs have no searchable chunk/version row, locations or vectors. This retains no deleted source chunk or version. No row of a removed chunk is kept for a time and none is marked as gone ([MYC-D8](#decisions)). A file that is only absent from the disk, because another branch is checked out or its changes are stashed, is still found in that branch or stash: its chunks keep their identifiers, their vectors and the edges a person asserted.

Exact versions are distinguished by complete stored text, not by normalized body equality. A recognized move or name change preserves the chunk identifier. It preserves an exact version and its vectors only when that version's stored text is unchanged; a heading rename or whitespace-only edit creates a new exact text version when the stored bytes differ. A normalized-equivalent or renamed version inherits its applicable baseline rather than being treated as a new confirmation. Restoring a previously known disk/branch/stash version restores that version's own pins. Comparison hashes still serve the two-round identity matcher; [MYC-16](16-source-addresses-and-evidence.md#comparison-hashes-and-exact-versions) fixes exact evidence and pin inheritance.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code`

### The pass

Observed in version 1: one routine brought the store up to date. For each enabled repository it ingested the documents, compared the stored hashes of the repository's code files with the files on disk, marked stale chunks, optionally reset the checkout to its remote, ingested the code, and wrote a generated overview. `mycel sync` ran it for all repositories at once and then embedded everything pending; a search ran it for one repository, without the reset and without the overview.

- **It could miss an edit to a code file.** The comparison of code files stored the new hash of each. The code ingest that followed skipped every file whose stored hash matched, which by then was every file. Read from the source and reproduced with a stand-in for the store, not on a real index. An edit was picked up only when the file changed between the two steps, which is where the reset to the remote sat.
- **It changed checkouts.** For a repository with a configured code folder that had a remote and no uncommitted or untracked files, it fetched the remote's default branch and ran `git reset --hard` to it, whatever branch was checked out. Observed on 7 October 2026: the history of one working checkout held 61 such resets from two days.
- **It was not atomic.** A file's new hash was stored before its chunks, each statement on its own. A failure in between left a file that the next pass skipped as unchanged, with its chunks half reconciled.
- **A pass for one repository wrote to all.** Marking stale chunks cleared and rewrote the marks of every repository.
- **Two passes could not run together,** which was right, and a pass that found another one running did nothing and said so.

Proposed: a pass reconciles files only in the repositories it names. For each it reads every location, skipping a branch or a stash whose commit an earlier pass has read; splits; reconciles identity; deletes what is found in no location; and then updates edges and staleness ([MYC-2](02-provenance-and-freshness.md)). A change to a source may update dependency records and stale marks in every downstream dependant, across repositories, and retry valid refs targeting the reconciled repository; it does not ingest those dependants' files unless they are also named. Those changes and their activity entries obey the repository locks of MYC-6. Unrelated repositories' rows are left alone.

A search or read determines the repositories whose files must be checked from its result scope and the explicit upstream dependencies, by [MYC-4](04-retrieval.md#freshness-on-read), and names them for reconciliation. Each file is applied in one transaction. A pass that did not read every location, because it was refused or cut short, deletes nothing. A pass never runs a command that changes a checkout, and it reads the disk as it is ([MYC-D9](#decisions)). It embeds only when asked ([MYC-3](03-embedding.md)).

**A pass publishes the capture it read** ([MYC-D64](#decisions), proposed 20 October 2026). The capture is the state of one moment, and every identity decision, dependency record, pin and stale mark the pass writes is bound to that capture, as [MYC-16](16-source-addresses-and-evidence.md#exact-request-evidence-and-result-guards) binds a confirmation to its recorded observation. A file that changes on disk after the capture and before the pass is saved does not stop the pass, and the pass neither retries it nor waits for it: before it saves, the pass reads the disk once more and names in its reply, under `changedDuringPass`, every file whose bytes or presence differ from the capture and every branch or stash that appeared, disappeared or moved to another commit. The pass is done all the same, with status 0; the next pass picks those files up, because their stored bytes differ from the disk (MYC-1.7), and a file that changed and changed back needs nothing. For the sources a chunk refers to, a pass takes the index as it stands and never compares another repository's disk with its index: that repository's own pass does, and a change there marks the dependants stale ([MYC-2](02-provenance-and-freshness.md)). A pass still refuses when its settings change while it runs, when the store's rows of the repository changed under it, and when another pass holds a repository it needs ([MYC-6](06-index-store.md)). For example, while the pass of `mycel` runs, an agent commits `specs/17-justification.md` to the corpus: the pass saves the chapter as it read it, replies with `changedDuringPass: ["mycel:@artifact/specs/17-justification.md"]`, and the next pass splits the new text. Before 20 October 2026 the pass compared the disk with its capture at every step and threw the whole pass away on the first difference: on 17 October 2026 a pass of three hours over `mycel` ended with nothing saved, because another agent had committed to the corpus meanwhile.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked`
- `mycel_deprecated_v1:mycel/syncpass.py#run_pass`
- `mycel_deprecated_v1:mycel/syncpass.py#run_repo_pass`
- `mycel_deprecated_v1:mycel/syncpass.py#refresh_mirror`
- `mycel_deprecated_v1:mycel/syncpass.py#_run_coalesced`
- `mycel_deprecated_v1:mycel/knowledge/store.py#refresh`
- `mycel_deprecated_v1:mycel/knowledge/store.py#track_source`
- `mycel_deprecated_v1:mycel/knowledge/store.py#detect`

### Status, and removing a repository

Observed in version 1: the status report counted documents of every state, so it could show more documents than there were files. Observed on 7 October 2026: switching a repository off stopped its ingest and embedding but left its chunks answering searches, and no command removed them; 21,988 rows were deleted with SQL.

Commands that only report also wrote: each created the settings file when it was missing, ran the statements that define the store's structure, and copied the settings into the store.

Proposed: status counts per repository what is on disk and, apart from it, what is found only in a branch or a stash. A command removes a repository's rows. Deprecated repositories have no index data or settings registrations: removing them deletes their indexed documents, chunks, vectors, edges and other repository-owned index state, while retaining their source checkouts and artifact files as historical evidence. Current repositories use their current names and configured folders. A command that reports writes nothing.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#status`
- `mycel_deprecated_v1:mycel/cli.py#_connect_with_config`
- `mycel_deprecated_v1:mycel/config.py#ensure_seeded`

## Requirements

| ID | Mycel must… | Origin | Verified by |
|---|---|---|---|
| MYC-1.1 | take the repositories, their folders and whether each is enabled from the settings file alone, and keep no second copy that a command consults | Changed | unit |
| MYC-1.2 | refuse commands that need valid settings when the file cannot be read, a table or key is unknown, or a known key has the wrong type; name the file and fault, and give detailed unknown-key diagnostics as MYC-5.3 specifies | Changed | unit |
| MYC-1.3 | derive the folders of an organization's member from the organization, and let folders given for the repository itself win | Kept | unit |
| MYC-1.4 | act on the repository a command names, or on the one whose configured folder contains the current directory, the longest folder winning, and refuse the command when neither gives one. An organization's name, or a directory in an organization's folder but in none of its members, gives every enabled member of that organization | Changed | unit |
| MYC-1.5 | use repository names as written in the settings; no repository, folder or alias is built in, apart from the explicit packaged shared selections and scan exclusion of MYC-D37, which create no repository, alias or folder fallback | Changed | unit |
| MYC-1.6 | read the document corpus and the code corpus with one scan that skips the same folders in both, skips what the repository's `.gitignore` excludes, and takes the file types the settings list | Changed | unit |
| MYC-1.7 | skip a file whose content is unchanged since the last pass, and notice every changed file whatever other step ran before | Changed | store |
| MYC-1.8 | refuse a pass that would find none of a corpus's documents on disk while the store holds some that were there, unless the caller confirms it | New | store |
| MYC-1.9 | split a Markdown file at its headings, each heading owning the text down to the next heading of any level, with text before the first heading as a chunk of its own and no heading recognised inside a code fence | Kept | unit |
| MYC-1.10 | name a section by its heading path and keep that name unique within the file | Changed | unit |
| MYC-1.11 | hash a section's body without its heading, after Unicode normalisation and with white space collapsed, and hash its title separately | Kept | unit |
| MYC-1.12 | read the frontmatter of a document as settings and keep it out of the chunks' text | Changed | unit |
| MYC-1.13 | split a code file along its structure: functions, classes as a header plus one chunk per method, and the other top-level declarations of its language, each with language, kind and line span | Kept | unit |
| MYC-1.14 | keep a decorator and a leading comment in the chunk of the symbol they belong to | Changed | unit |
| MYC-1.15 | name every chunk of a code file uniquely within the file, and so that adding or removing one chunk changes no other chunk's name | Changed | unit |
| MYC-1.16 | keep a file that cannot be parsed as one whole-file chunk | Kept | unit |
| MYC-1.17 | recognise a chunk again in two rounds over its file: by name first, then by content among what is left. A chunk with no body is never matched by content | Changed | unit |
| MYC-1.18 | recognise chunks of code and of documents by the same rules, a renamed function included | Changed | unit |
| MYC-1.19 | keep a document's and its chunks' identity when the file is moved without a change | Kept | store |
| MYC-1.20 | record every decision about identity (unchanged, edited, renamed, new, removed) with the pass that made it, and show them on request | Changed | store |
| MYC-1.21 | delete the rows of a version that is found in no location, and of a chunk that has no version left, in the pass that finds it so, and only when that pass read every location of the repository. Keep no removed chunk row for a time or marked as gone; retain missing-source evidence only in surviving dependants as MYC-2.24 specifies | Changed | store |
| MYC-1.22 | apply each file in one transaction: its hash, its chunks and its identity decisions together or not at all | Changed | store |
| MYC-1.23 | reconcile files only in the repositories an invocation names, or all enabled ones when it says so; permit dependency records, stale marks, retries of valid refs targeting those repositories and their activity entries in affected dependants under their repository locks, and change no unrelated rows | Changed | store |
| MYC-1.24 | never run a command that changes a checkout or fetches from a remote, and read the files of a repository as they are: the disk as it lies, branches and stashes from the git store | Changed | unit |
| MYC-1.25 | let one pass at a time work on a repository, and tell a second caller plainly that it did nothing because another pass is running | Kept | store |
| MYC-1.26 | report per repository the documents and chunks that are on disk, those found only in a branch or a stash, and when the last pass ran | Changed | store |
| MYC-1.27 | remove every row of a repository on request, and nothing of any other repository | New | store |
| MYC-1.28 | write nothing in a command that only reports | Changed | store |
| MYC-1.29 | refuse a command that needs the folders of a repository whose name is found under several organizations and that gives no code folder, naming the organizations, and let commands for other repositories go on | Changed | unit |
| MYC-1.30 | read, besides the files on disk, the files of every local branch and of every stash of the checkout a folder lies in, by the rules of the scan, and read no branch of a remote | New | store |
| MYC-1.31 | store one version of a chunk for each text it has, record for every version the locations it is found in, and give a chunk one identifier in all of them | New | store |
| MYC-1.32 | include Markdown under both `artifact_root` and `code_root` in the document corpus, independently of source-code `code_subdirs`, applying the common skip list and `.gitignore`; split it at headings and keep document origin in search and read replies | New | store |
| MYC-1.33 | retain a document's actual root and path for identity, Source Refs and reads; index a file reached through overlapping roots once per disk, branch or stash location, distinguish different files sharing a relative path, report ambiguous addresses and silently merge none; preserve existing unambiguous source identities and the identity rules for genuine moves | New | store |
| MYC-1.34 | retain exact text versions separately from normalized comparison hashes under MYC-16; keep identity through recognized renames/moves, reuse a version only for identical stored text, preserve inherited pins for normalized-equivalent/renamed text and retain deleted-source evidence solely in surviving dependant-owned blobs | New | store |
| MYC-1.35 | split a recognised requirement or decision row out as a chunk of kind `req` or `dec` beside its section, named by its human id and keyed by the UUID of the HTML comment in its first cell, and keep the section's own chunk with its complete text and hashes | New | unit |
| MYC-1.36 | report a recognised row without a UUID, and two rows with one UUID, as faults of the file, make no entity of them, and give a `req` or `dec` chunk its UUID as identifier in every location without the two matching rounds | New | store |
| MYC-1.37 <!-- 388fc246-1b89-4683-a8b7-479bcc6d57c4 --> | save the capture a pass read even when a file of the repository changes before the pass is saved, bind what the pass writes to that capture, name in the reply every file and location that differs from it, retry nothing within the pass, and take the sources of other repositories from the index without comparing their disk | New | store |

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

```sh
mycel ingest --repo cellar          # scan, split, reconcile; then edges and staleness (MYC-2)
mycel ingest --repo cellar --embed  # and embed what is pending in that repository (MYC-3)
mycel ingest --repo Orchard         # every enabled member of an organization
mycel ingest --all                  # every enabled repository
mycel status --repo cellar          # counts of one repository; --all for every one
mycel repos                         # the repositories of the settings file, their folders, enabled or not
mycel repos remove cellar           # delete every row of one repository
```

`mycel ingest` without `--repo` or `--all` takes the repository of the current directory.

In the folder of an organization, outside its members, it takes every enabled member of that organization (MYC-1.4): run in `~/repos/orchard`, it brings `presses` and every other enabled repository under Orchard up to date. In a directory that belongs to neither a repository nor an organization it is refused.

```ts
interface IngestReply {
  repositories: Record<string, {
    ran: boolean;                      // false when another pass was running
    files: { scanned: number; changed: number; removed: number };
    chunks: { unchanged: number; edited: number; renamed: number; new: number; removed: number };
    stale: number;                     // chunks on disk of this repository that are stale afterwards (MYC-2)
    pending: number;                   // versions with at least one pending embedding part afterwards (MYC-3)
    refused?: string;                  // the reason, when the pass was refused (MYC-1.8)
    changedDuringPass?: string[];      // files and locations that differ from the saved capture (MYC-1.37); the next pass picks them up
  }>;
}

interface RepositoryStatus {
  repository: string;
  enabled: boolean;
  folders: { code?: string; documents?: string };
  documents: { onDisk: number; elsewhere: number };                 // elsewhere: found only in a branch or a stash
  chunks: { onDisk: number; elsewhere: number; stale: number };
  vectors: { embedded: number; pending: number; failed: number };   // version counts by complete coverage (MYC-3.12)
  parts: { embedded: number; pending: number; failed: number };     // input-part counts, separate from versions
  lastPass?: string;                   // time of the last pass that ran
}
```

## Known problems in version 1

- **An edit to a code file could be missed.** The step that compared code files with the store hid the change from the step that would have re-split them.
- **A pass reset working checkouts.** A clean checkout was moved to the tip of its remote's default branch on every full pass, whatever branch it was on. Commits that were not on that branch left it.
- **Identity could shift.** Matching in one pass let an empty section take another's identity. Chunks between symbols were numbered by position. Symbols with the same name shared one name.
- **Nothing was ever removed.** Rows of what left the disk stayed for good, and a repository could be switched off but not removed.
- **An empty scan emptied a repository.** A wrong folder marked everything as gone.
- **Ingest was not atomic.** A failure left a file that later passes skipped, half applied.
- **The store disagreed with the settings file.** Settings were copied into the store on every command and removed keys stayed there. The schema itself created a repository named `arbol`, switched on, whenever it was missing.
- **One ambiguous name stopped every command.** A repository name found under two organizations made every command fail that had to find its repository from the current directory, in whichever repository it was run.
- **One pass, all or nothing.** The only command for a pass covered every repository and embedded everything pending afterwards.
- **Reports wrote.** Status and the other read-only commands changed the store's structure and its copy of the settings.
- **Language labels were wrong for some files.** Shell scripts, property lists and Swift files were recorded as JavaScript.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#refresh`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_lang_of`
- `mycel_deprecated_v1:mycel/syncpass.py#refresh_mirror`
- `mycel_deprecated_v1:mycel/config.py#apply`
- `mycel_deprecated_v1:mycel/locations.py#RepositoryLocations.organization`
- `mycel_deprecated_v1:mycel/locations.py#RepositoryLocations.scope_bindings`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_sync`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D7 | Which files are read, and which folders are skipped? | Version 1's lists as the defaults of two settings: Markdown for documents, and its fifteen endings for code. One list of skipped folders for both corpora, version 1's for code, plus whatever the repository's `.gitignore` excludes | Decided 8 October 2026 by the owner: resolved for the proposed default file types, the common skip list and `.gitignore`; include Markdown beside code, such as `README.md` and `docs/`, in the document corpus as well as Markdown under `artifact_root`. Keep each document's actual root/path and index overlapping-root files once; different files with colliding relative paths remain distinct |
| MYC-D8 | How long do rows of what left the disk stay? | 30 days, as a setting. Within that time a chunk that returns unchanged gets its identity back; after it the rows are deleted. Rows are kept because a file that left the disk may only be absent, on another branch for example, and deleting at once would cost a new identifier, a new embedding and the asserted edges at every return. The 30 days are a first value and not a measured one | Decided 8 October 2026 by the owner: no time limit. Mycel reads the disk, every local branch and every stash, and no branch of a remote, and records for each version of a chunk the locations it is found in ([Branches and stashes](#branches-and-stashes)). What is found in none is deleted by that pass. Search, edges and staleness look at the disk |
| MYC-D9 | Does Mycel ever fetch from a remote or reset a checkout? | No. It reads the files as they are on disk, on whatever branch is checked out, and the local branches and stashes from the git store, which changes nothing ([MYC-D8](#decisions)). Keeping a checkout up to date belongs to its owner | Decided 8 October 2026 by the owner: agreed. Mycel never fetches remote changes or resets a checkout; it reads disk, local branches and stashes without changing them |
| MYC-D10 | How are the chunks between symbols named? | After the symbol that follows them, such as `<before renew>`, and `<end>` for the last, so that no name depends on a position. `<before renew>` is the chunk of the lines that stand before the function `renew` and belong to no symbol, such as imports and constants. `<end>` is the chunk of such lines after the last symbol of the file. Version 1 numbered them in file order: `<module>`, `<module:1>`, `<module:2>`. [Splitting code](#splitting-code) shows a file with both sets of names. A second symbol with the same name gets a number, in file order | Decided 8 October 2026 by the owner: agreed. Name loose code after the following symbol as `<before name>`, and use `<end>` after the final symbol |

| MYC-D38 | May a function rename use a separate parser-derived body identity key? | Preserve identity for a name-only rename with a conservative parsed body/signature key, while retaining the complete-code hash for change tracking and exact versions | Decided 9 October 2026 by the owner: use that approach. The parser-derived identity projection erases only the declaration name and is versioned separately; it never supplies exact text or dependency comparison evidence |
| MYC-D64 | What does a pass do with a file that changes after the pass read it and before the pass is saved? | The pass publishes the capture it read, as [The pass](#the-pass) says: what it writes is bound to that capture, it retries nothing and waits for nothing, it reads the disk once more before it saves and names every file and location that differs under `changedDuringPass` with status 0, and the next pass picks those files up by MYC-1.7. For the sources a chunk refers to it takes the index as it stands and never compares another repository's disk with its index. Rejected: retrying the file inside the pass, because the guard is the capture of the whole repository and a repository that is edited all day would never settle; the previous rule, which compared the disk at every step and threw a pass of three hours away for one commit to a corpus | Open. Proposed 20 October 2026 by SYL-232 of the Mycel Specs Implementation Saga; the code follows the proposed default until the owner decides |
