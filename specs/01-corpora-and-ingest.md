---
role: authored
spec: MYC-1
status: draft
---
# Mycel · 01 Corpora and ingest

Ingest turns the files of a repository into [Chunks](../../arbol/GLOSSARY.md#chunk) with a stable identity: a section of a document or a symbol of a code file keeps its identifier through edits and renames, so that everything attached to it survives. This specification fixes which files are read, how they are split, how a chunk is recognised again, and what one pass over a repository does. It matters because version 1 could miss an edit to a code file altogether, reset a working checkout to its remote, and never removed a row.

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: repositories and their two corpora, the settings that name them, which repository a command means, the scan, splitting documents and code into chunks, identity, what happens to files that leave the disk, the pass, status, removing a repository.

Not covered: edges between chunks and staleness ([MYC-2](02-provenance-and-freshness.md)); vectors ([MYC-3](03-embedding.md)); search and the freshness check that starts a pass ([MYC-4](04-retrieval.md)); the generated overview of a repository's code, which is not part of the first version ([MYC-D4](00-overview-and-legacy-map.md#decisions)).

## Behaviour

### Repositories and corpora

Observed in version 1, and kept: a repository is known by a short name and has two [corpora](../../arbol/GLOSSARY.md#corpus). Its document corpus is the Markdown files under its document folder. Its code corpus is the source files under its code folder, or under the subfolders of it that the settings list. Either may be missing: a repository can have documents only.

Observed in version 1: the settings file `~/.mycel/config.toml` named the repositories. For each one it could give whether it is enabled, its code folder, its document folder and the subfolders that form the code corpus. A repository that is a direct child of a configured organization folder needed no folders of its own: its code was its checkout, and its documents lay under the organization's document folder. Every command copied the repositories from the file into the index store, and the store's copy then took part in decisions. A key removed from the file stayed in the store. `enabled` was not checked for its type, so the text `"false"` switched a repository on.

Proposed: the settings file is the only place that says which repositories exist and where they are. Nothing in the store stands in for it. A file that cannot be read, or a key of the wrong type, refuses the command and names the fault.

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

<!-- sources:
mycel_deprecated_v1:mycel/config.py#load
mycel_deprecated_v1:mycel/config.py#apply
mycel_deprecated_v1:mycel/locations.py#RepositoryLocations
mycel_deprecated_v1:mycel/organizations.py#members
mycel_deprecated_v1:mycel/knowledge/store.py#set_repo_flags
-->

### Which repository a command means

Observed in version 1: a command took the repository it was given, or else the one whose code or document folder contained the current directory, the longest folder winning. When neither gave one, it took a repository called `arbol`. Two older folder layouts were still searched, and one environment variable overrode everything. The name `Arbol` was rewritten to `arbol`; no other name was touched.

Proposed: the named repository, or the one the current directory belongs to. Otherwise the command is refused. Names are used as written, and none is built in.

<!-- sources:
mycel_deprecated_v1:mycel/scope.py#resolve
mycel_deprecated_v1:mycel/locations.py#RepositoryLocations.scope_bindings
mycel_deprecated_v1:mycel/repo_identity.py#canonical_repo
-->

### The scan

Observed in version 1: the two corpora were scanned by separate code with different rules.

| | Documents | Code |
|---|---|---|
| Files taken | Every `*.md` | `.py`, `.svelte`, `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs`, `.cjs`, `.sh`, `.bash`, `.plist`, `.plist.in`, `.swift` |
| Folders skipped | `.git` only | `.git`, `node_modules`, `.venv`, `venv`, `__pycache__`, `build`, `dist`, `coverage` and a dozen more, at any depth |
| Unchanged file | Skipped when its SHA-256 equals the stored one | The same |
| Size limit, `.gitignore` | None | None |

A file that left the disk had its document and chunks marked as gone. Nothing guarded against a scan that found nothing: a wrong folder or a narrowed list of subfolders marked every row of the repository as gone.

Proposed: one scan for both corpora with one list of skipped folders, which also honours the repository's `.gitignore`. The file types are settings with version 1's lists as defaults ([MYC-D7](#decisions)). A pass that would mark every document of a corpus as gone, while the store holds some, is refused unless the caller confirms it.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/store.py#_scan_corpus
mycel_deprecated_v1:mycel/knowledge/store.py#_scan_code
mycel_deprecated_v1:mycel/knowledge/store.py#ingest
mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code
-->

### Splitting a document

Observed in version 1, and kept: a Markdown file is split at its headings. Each heading owns its own line and the text down to the next heading of any level; a subsection is a chunk of its own and not part of its parent's text. Text before the first heading is one chunk. Lines inside a code fence are never headings. The chunk's name is its heading path, the titles from the top joined by ` > `, such as `Setup > Database > Backups`.

Two hashes are kept for a section. The content hash covers the body without the heading line, after Unicode normalisation and with every run of white space reduced to one space, so that re-wrapping a paragraph changes nothing. The title hash covers the heading alone, so that a renamed heading with the same body is recognised as the same section.

There was no limit on the size of a section.

Proposed: kept, with two corrections. A name is unique within its file: the second section with the same heading path gets a number. The leading block of settings at the top of a file (the frontmatter) is read as settings and is not part of the first chunk's text.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/chunker.py#chunk_markdown
mycel_deprecated_v1:mycel/knowledge/chunker.py#content_hash
mycel_deprecated_v1:mycel/knowledge/chunker.py#norm
-->

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

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_code
mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_python
mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_typescript
mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_svelte
mycel_deprecated_v1:mycel/knowledge/code_chunker.py#_uncovered_runs
-->

### Identity

Observed in version 1, for documents: a chunk of a changed file was matched against the stored chunks of the same file. A stored chunk with the same name was the same chunk: unchanged when the content hash matched, edited when not. Failing that, a stored chunk with the same content hash was the same chunk under a new name: renamed. What matched nothing was new; stored chunks nothing matched were marked as gone. A file moved without a change kept its document and all its chunks. Every decision was written to a log that nothing ever read.

The matching went through the file once, and a chunk without a name match took the first stored chunk with the same content. Every section without body text has the same content hash, so a new empty section could take over the identity of an existing one, and the sections after it shifted. Everything attached to an identifier moved with it.

Observed in version 1, for code: a chunk was matched by name only. A renamed function was a removed chunk and a new one. Nothing was logged.

A row marked as gone was never matched again and never deleted. A section removed and restored got a new identity. Observed on 7 October 2026: a fifth of the rows of the largest repository were rows that had left the disk.

Proposed: one way of matching for documents and code, in two rounds over the whole file: every name match first, then content matches among what is left. A chunk with no body never matches by content. A chunk that returns within the retention time, with the name and content it had, gets its identity back. Rows that stay gone past that time are deleted ([MYC-D8](#decisions)).

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/store.py#ingest
mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code
-->

### The pass

Observed in version 1: one routine brought the store up to date. For each enabled repository it ingested the documents, compared the stored hashes of the repository's code files with the files on disk, marked stale chunks, optionally reset the checkout to its remote, ingested the code, and wrote a generated overview. `mycel sync` ran it for all repositories at once and then embedded everything pending; a search ran it for one repository, without the reset and without the overview.

- **It could miss an edit to a code file.** The comparison of code files stored the new hash of each. The code ingest that followed skipped every file whose stored hash matched, which by then was every file. Read from the source and reproduced with a stand-in for the store, not on a real index. An edit was picked up only when the file changed between the two steps, which is where the reset to the remote sat.
- **It changed checkouts.** For a repository with a configured code folder that had a remote and no uncommitted or untracked files, it fetched the remote's default branch and ran `git reset --hard` to it, whatever branch was checked out. Observed on 7 October 2026: the history of one working checkout held 61 such resets from two days.
- **It was not atomic.** A file's new hash was stored before its chunks, each statement on its own. A failure in between left a file that the next pass skipped as unchanged, with its chunks half reconciled.
- **A pass for one repository wrote to all.** Marking stale chunks cleared and rewrote the marks of every repository.
- **Two passes could not run together,** which was right, and a pass that found another one running did nothing and said so.

Proposed: a pass covers the repositories it names. For each it scans, splits, reconciles identity, and then updates edges and staleness for that repository ([MYC-2](02-provenance-and-freshness.md)). Each file is applied in one transaction. A pass never runs a command that changes a checkout, and it reads the files as they are on disk ([MYC-D9](#decisions)). It embeds only when asked ([MYC-3](03-embedding.md)).

<!-- sources:
mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked
mycel_deprecated_v1:mycel/syncpass.py#run_pass
mycel_deprecated_v1:mycel/syncpass.py#run_repo_pass
mycel_deprecated_v1:mycel/syncpass.py#refresh_mirror
mycel_deprecated_v1:mycel/syncpass.py#_run_coalesced
mycel_deprecated_v1:mycel/knowledge/store.py#refresh
mycel_deprecated_v1:mycel/knowledge/store.py#track_source
mycel_deprecated_v1:mycel/knowledge/store.py#detect
-->

### Status, and removing a repository

Observed in version 1: the status report counted documents of every state, so it could show more documents than there were files. Observed on 7 October 2026: switching a repository off stopped its ingest and embedding but left its chunks answering searches, and no command removed them; 21,988 rows were deleted with SQL.

Commands that only report also wrote: each created the settings file when it was missing, ran the statements that define the store's structure, and copied the settings into the store.

Proposed: status counts what is present, per repository. A command removes a repository's rows. A command that reports writes nothing.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/store.py#status
mycel_deprecated_v1:mycel/cli.py#_connect_with_config
mycel_deprecated_v1:mycel/config.py#ensure_seeded
-->

## Requirements

| ID | Mycel must… | Origin | Verified by |
|---|---|---|---|
| MYC-1.1 | take the repositories, their folders and whether each is enabled from the settings file alone, and keep no second copy that a command consults | Changed | unit |
| MYC-1.2 | refuse a command when the settings file cannot be read or a known key has the wrong type, naming the file and the fault | Changed | unit |
| MYC-1.3 | derive the folders of an organization's member from the organization, and let folders given for the repository itself win | Kept | unit |
| MYC-1.4 | act on the repository a command names, or on the one whose configured folder contains the current directory, the longest folder winning, and refuse the command when neither gives one | Changed | unit |
| MYC-1.5 | use repository names as written in the settings; no name, folder or alias is built in | Changed | unit |
| MYC-1.6 | read the document corpus and the code corpus with one scan that skips the same folders in both, skips what the repository's `.gitignore` excludes, and takes the file types the settings list | Changed | unit |
| MYC-1.7 | skip a file whose content is unchanged since the last pass, and notice every changed file whatever other step ran before | Changed | store |
| MYC-1.8 | refuse a pass that would mark every document of a corpus as gone while the store holds some, unless the caller confirms it | New | store |
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
| MYC-1.20 | record every decision about identity (unchanged, edited, renamed, new, gone, returned) with the pass that made it, and show them on request | Changed | store |
| MYC-1.21 | mark the rows of files, sections and symbols that left the disk as gone with one word for both corpora, give a chunk its identity back when it returns unchanged within the retention time, and delete rows that stay gone longer | Changed | store |
| MYC-1.22 | apply each file in one transaction: its hash, its chunks and its identity decisions together or not at all | Changed | store |
| MYC-1.23 | run a pass only for the repositories an invocation names, or for all enabled ones when it says so, and write only rows of those repositories | Changed | store |
| MYC-1.24 | never run a command that changes a checkout, and read the files of a repository as they are on disk | Changed | unit |
| MYC-1.25 | let one pass at a time work on a repository, and tell a second caller plainly that it did nothing because another pass is running | Kept | store |
| MYC-1.26 | report per repository the documents and chunks that are present, those marked as gone, and when the last pass ran | Changed | store |
| MYC-1.27 | remove every row of a repository on request, and nothing of any other repository | New | store |
| MYC-1.28 | write nothing in a command that only reports | Changed | store |

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

```sh
mycel sync --repo cellar            # scan, split, reconcile; then edges and staleness (MYC-2)
mycel sync --repo cellar --embed    # and embed what is pending in that repository (MYC-3)
mycel sync --all                    # every enabled repository
mycel status --repo cellar          # counts of one repository; --all for every one
mycel repos                         # the repositories of the settings file, their folders, enabled or not
mycel repos remove cellar           # delete every row of one repository
```

`mycel sync` without `--repo` or `--all` takes the repository of the current directory.

```ts
interface SyncReply {
  repositories: Record<string, {
    ran: boolean;                      // false when another pass was running
    files: { scanned: number; changed: number; gone: number };
    chunks: { unchanged: number; edited: number; renamed: number; new: number; gone: number; returned: number };
    stale: number;                     // present chunks of this repository that are stale afterwards (MYC-2)
    pending: number;                   // present chunks without a vector afterwards (MYC-3)
    refused?: string;                  // the reason, when the pass was refused (MYC-1.8)
  }>;
}

interface RepositoryStatus {
  repository: string;
  enabled: boolean;
  folders: { code?: string; documents?: string };
  documents: { present: number; gone: number };
  chunks: { present: number; gone: number; stale: number };
  vectors: { embedded: number; pending: number; failed: number };   // MYC-3.12
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
- **One pass, all or nothing.** The only command for a pass covered every repository and embedded everything pending afterwards.
- **Reports wrote.** Status and the other read-only commands changed the store's structure and its copy of the settings.
- **Language labels were wrong for some files.** Shell scripts, property lists and Swift files were recorded as JavaScript.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/store.py#refresh
mycel_deprecated_v1:mycel/knowledge/store.py#ingest
mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code
mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema
mycel_deprecated_v1:mycel/knowledge/store.py#_lang_of
mycel_deprecated_v1:mycel/syncpass.py#refresh_mirror
mycel_deprecated_v1:mycel/config.py#apply
mycel_deprecated_v1:mycel/cli.py#_cmd_sync
-->

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D7 | Which files are read, and which folders are skipped? | Version 1's lists as the defaults of two settings: Markdown for documents, and its fifteen endings for code. One list of skipped folders for both corpora, version 1's for code, plus whatever the repository's `.gitignore` excludes | Open |
| MYC-D8 | How long do rows of what left the disk stay? | 30 days, as a setting. Within that time a chunk that returns unchanged gets its identity back; after it the rows are deleted | Open |
| MYC-D9 | Does Mycel ever fetch from a remote or reset a checkout? | No. It reads the files as they are on disk, on whatever branch is checked out. Keeping a checkout up to date belongs to its owner | Open |
| MYC-D10 | How are the chunks between symbols named? | After the symbol that follows them, such as `<before renew>`, and `<end>` for the last, so that no name depends on a position. A second symbol with the same name gets a number, in file order | Open |
