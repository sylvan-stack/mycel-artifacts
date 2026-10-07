---
role: authored
spec: MYC-0
status: draft
---
# Mycel · 00 Overview and legacy map

[Mycel](../../arbol/GLOSSARY.md#mycel) is the knowledge engine of the Sylvan Stack. It turns the documents and the code of each repository into an index that is kept current, knows what each part rests on, and can be searched by meaning and by exact wording. This specification fixes what Mycel 2 does and what it leaves to others, the form it takes, the rules every command follows, and where each part of version 1 went. It matters because version 1 had grown well past that function, managing work trees, fetching from outside trackers and resetting checkouts, while the function itself had defects that neither its comments nor its guides knew about.

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: what Mycel is for and the four parts of its function, the boundary, form and hosting, the rules of the command line, the settings file, the legacy map, the Glossary entries that need new wording.

Not covered: the four parts themselves: ingest ([MYC-1](01-corpora-and-ingest.md)), provenance and freshness ([MYC-2](02-provenance-and-freshness.md)), embedding ([MYC-3](03-embedding.md)), retrieval ([MYC-4](04-retrieval.md)).

## What Mycel is for

An agent that works in a repository asks many times a day where something is, how it works and what was already found out about it. Reading the raw files for every question is slow and blind to what belongs together. And knowledge written down once goes out of date without a sign: a guide keeps describing code that has changed under it.

Mycel answers both. Its function has four parts, each resting on the one before.

| Part | From | To | Specified in |
|---|---|---|---|
| Ingest | The files of a repository | [Chunks](../../arbol/GLOSSARY.md#chunk) with a stable identity | MYC-1 |
| Provenance and freshness | The sources a section names | Edges that remember each source, and a mark on what went out of date | MYC-2 |
| Embedding | The text of a chunk | A vector | MYC-3 |
| Retrieval | A question or a name | The chunks that answer it, ranked | MYC-4 |

Observed in version 1's design record, and kept as the principles of Mycel 2:

- **Identity is not a place.** A chunk has an identifier that survives edits, renames and moves. Its name and path are an address that may change.
- **Finding out what is stale never uses a model.** It compares hashes. Models appear only where text is produced or embedded.
- **One store, divided by repository.** Repositories share the store and never mix in a result.
- **Git owns history.** Mycel holds the current state of the files and no earlier versions.
- **Retrieval is a tool an agent calls,** and its reply is a contract.

<!-- sources:
arbol_deprecated_v1:research/RETRIEVAL-RESEARCH.md#1.1 The problem
arbol_deprecated_v1:research/RETRIEVAL-RESEARCH.md#1.2 Core principles
-->

## What stays and what goes

| Responsibility | Version 1 owner | Mycel 2 owner |
|---|---|---|
| Reading a repository's files, splitting them into chunks, keeping their identity | Mycel | Mycel |
| Recording what a section rests on, marking what is stale | Mycel | Mycel |
| Embedding chunks | Mycel, through an outside service; for one profile through a resident service of Arbol 1 | Mycel, through one outside service ([MYC-D16](03-embedding.md#decisions)) |
| Search | Mycel | Mycel |
| Saying which repositories exist and where they are | The owner, in Mycel's settings file; copied into the store | The owner, in the settings file alone |
| Keeping the index current without being asked | A resident service of Arbol 1, which watched folders and ran passes on a timer | Nobody. A search checks the repository it searches, and a pass can be started at any time. A caller that wants a schedule runs one |
| Keeping a checkout up to date with its remote | Mycel, as part of every full pass | The checkout's owner. Mycel changes no checkout ([MYC-D9](01-corpora-and-ingest.md#decisions)) |
| Showing chunks, edges and stale sections in a window | Arbol 1 | A caller, from Mycel's replies |
| Summaries of clusters of chunks, a generated overview of the code, a grep replacement with a search tail | Mycel | Mycel, after the first version ([MYC-D4](#decisions)) |
| Work trees and a view of the index per branch | Mycel | Nobody ([MYC-D6](#decisions)) |
| Fetching tickets, wiki pages and code reviews from outside trackers, and writing to them | Mycel | Nobody. Content from outside reaches Mycel as files in a corpus ([MYC-D5](#decisions)) |

<!-- sources:
mycel_deprecated_v1:mycel/cli.py#main
mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked
mycel_deprecated_v1:mycel/config.py#apply
arbol_deprecated_v1:architecture/external-tools.md#Dependency law
-->

## Form and hosting

Proposed.

- **Form.** Mycel is one command-line program, `mycel`. Its command line is its only interface: a caller starts the program and reads the result from standard output. There is no library to load, so no other program contains Mycel's code ([MYC-D1](#decisions)). Version 1 was also a library, which Arbol 1's resident service loaded.
- **No resident service.** Mycel is not a daemon and has no socket, launch agent or watcher. Every invocation is one process that does one thing and ends. This was the strict rule of version 1 and is kept.
- **Builds.** Mycel is built into numbered Builds that are kept side by side ([BLD-0](../../arbol/builds/00-builds-and-versions.md), which names `mycel` among the components). The name on the search path is a launcher: without a build number it starts the newest working Build.
- **State.** Mycel keeps the index store ([MYC-D2](#decisions)) and nothing else. Its settings are a file the owner writes ([MYC-D3](#decisions)). The store carries the format number of BLD-0, so that a Build that meets a newer format refuses to run.
- **Independence.** Mycel uses no code and no instructions of Arbol, and nothing in Mycel is named for another product. It may read the files and data of any product as data.
- **Network.** The only service Mycel calls is the embedding provider (MYC-3). It runs no git command that changes anything.

<!-- sources:
mycel_deprecated_v1:pyproject.toml
mycel_deprecated_v1:Makefile
arbol_deprecated_v1:architecture/external-tools.md#Runtime contracts
-->

## The command line

Proposed. The rules below hold for every command. The commands themselves are specified with their subject.

| Command | Does | Specified in |
|---|---|---|
| `mycel search` | Answers a question or finds a name | MYC-4 |
| `mycel sync` | Brings the index of a repository up to date with its files | MYC-1 |
| `mycel embed` | Embeds the pending chunks of a repository | MYC-3 |
| `mycel status`, `mycel repos` | Report on repositories; `mycel repos remove` deletes one from the index | MYC-1 |
| `mycel stale`, `mycel refs`, `mycel derive`, `mycel confirm` | The list of stale chunks, faults in refs, asserting an edge, confirming a chunk | MYC-2 |
| `mycel init` | Creates the index store's structure, or brings it to the format of the Build that runs | here |
| `mycel info` | Says which Build runs and what it found | here |

| Rule | Detail |
|---|---|
| One invocation, one operation | The program starts, does what the command says and ends. Nothing is kept between invocations except in the index store |
| Build | `-v <build number>` as the first argument runs that Build. Without it the default Build runs: the newest working one (BLD-0) |
| Repository | `--repo <name>` names it; without it the repository of the current directory is meant; when there is none the command is refused (MYC-1.4) |
| Output | One JSON document on standard output. A caller ignores fields it does not know |
| Errors | A command that is refused or fails writes `{ "error": { "code", "message" } }` as its result. The codes are a closed list: `invalid_input`, `settings`, `unknown_repository`, `store_unavailable`, `store_format`, `busy`, `refused`, `internal` |
| Exit status | 0: done as asked. 1: refused or failed. 2: stopped by the caller |
| Standard error | Progress and diagnostics for a person. A caller never needs it to understand a result, and no secret is written there |
| Secrets | Mycel is never given a secret, neither as an argument nor on standard input nor in its settings file (MYC-3.14) |
| Reports | A command that only reports writes nothing (MYC-1.28). The store's structure changes only in `mycel init` |
| `info` | Prints the package version and the build number of the Build that runs, the version of the search reply it produces, the settings file, the index store and its format number, and the embedding model |

```ts
interface MycelInfo {
  version: string;                     // the package version, e.g. "2.0.0"
  build: string;                       // the build number of the Build that runs (BLD-0)
  searchReply: number;                 // the version of the search reply (MYC-4)
  settingsFile: string;                // whether or not it exists
  store: { location: string; format: number; reachable: boolean };
  embedding: { provider: string; model: string; dimensions: number; keyFound: boolean };
}
```

## Requirements

| ID | Mycel must… | Origin | Verified by |
|---|---|---|---|
| MYC-0.1 | be one command-line program whose command line is its only interface: no library for callers, no socket, and every invocation ends by itself when its operation is done | Changed | unit |
| MYC-0.2 | run no resident process of any kind: no daemon, no watcher, no launch agent, no timer | Kept | unit |
| MYC-0.3 | work with nothing of Arbol installed or running, and contain no name, path, variable or message of another product | Changed | unit |
| MYC-0.4 | keep nothing between invocations except in the index store, and read its settings file at the start of every invocation | Changed | store |
| MYC-0.5 | never write its settings file | Changed | unit |
| MYC-0.6 | follow the command-line rules above for the repository, output, errors and exit status | Changed | unit |
| MYC-0.7 | report every failure as one error object with a code from the closed list, and never ask a caller to match error text | New | unit |
| MYC-0.8 | change the structure of the index store only in `mycel init`, and refuse every other command with `store_format` when the store's format is not the one its Build knows | Changed | store |
| MYC-0.9 | be built into numbered Builds as BLD-0 says and report the build number of the Build that runs in `info` | New | unit |
| MYC-0.10 | call no service except the embedding provider, and run no git command that changes a repository | Changed | unit |
| MYC-0.11 | have an automated check for every requirement of MYC-1 to MYC-4 before that requirement counts as implemented, the store-backed ones against a store made for the test and discarded after it | New | store |
| MYC-0.12 | keep the guides of this corpus true to the program: a change to a command, an option or a reply changes the guide that describes it in the same change | New | unit |

## Legacy map

Fate is one of: **Kept** (same behaviour, rewritten), **Changed** (same purpose, different behaviour), **Later** (the purpose remains and is specified after the first version), **Caller** (the purpose remains and belongs to whoever calls Mycel), **Dropped**.

### The engine

| Version 1 part | What it did | Fate | Specified in |
|---|---|---|---|
| `knowledge/chunker.py` | Split Markdown at headings, read frontmatter and Source Refs | Kept, with corrections to names and to how frontmatter is read | MYC-1, MYC-2 |
| `knowledge/code_chunker.py` | Split Python, TypeScript, JavaScript and Svelte along their structure | Kept, with corrections to names and decorators | MYC-1 |
| `knowledge/store.py`: scan and ingest | Two separate scans and two ways of matching, one for documents and one for code | Changed: one scan, one way of matching, each file in one transaction | MYC-1 |
| `knowledge/store.py`: edges and detection | Declared, asserted and generated edges; stale marks for the whole index | Changed: what renews an edge, what a removed source does, the scope of a pass | MYC-2 |
| `knowledge/store.py`: Drifts | Tables and functions for stored items of work, never filled | Dropped | MYC-D13 |
| `knowledge/embedder.py`: embedding | Sent pending chunks of all repositories to the embedding service, one attempt each | Changed: per repository, with retries and honest counts | MYC-3 |
| `knowledge/local_embedder.py` | Client of an on-device embedding service that belonged to Arbol 1 | Dropped for the first version | MYC-D16 |
| `knowledge/embedder.py`: search; `retrieval.py` | Two arms, two routes, the bridge from documents to code, the reply | Changed: the rules hold as stated, results say what they are | MYC-4 |
| `syncpass.py`: the pass | Ingest, detection, overview, for all repositories or one | Changed | MYC-1 |
| `syncpass.py`: `refresh_mirror` | Fetched the remote's default branch and reset the checkout to it | Dropped | MYC-D9 |
| `syncpass.py`: `repo_stale`, `newer_than` | Looked for files changed since the last pass, with no time limit | Changed: a time limit, and the same folders skipped as the scan | MYC-4 |

### Settings and scope

| Version 1 part | What it did | Fate | Specified in |
|---|---|---|---|
| `config.py` | Read the settings file and copied its repositories into the store on every command; created the file when missing | Changed: the file alone holds the settings, and Mycel never writes it | MYC-1 |
| `organizations.py` | Treated the direct children of a configured folder as member repositories | Kept | MYC-1 |
| `locations.py`, `scope.py` | Found a repository's folders and the repository of a path, with fall-backs to two older folder layouts and to a built-in repository name | Changed: configured folders only, no fall-back | MYC-1 |
| `repo_identity.py` | Rewrote one repository's name and moved its rows at every start | Dropped | MYC-1.5 |
| `database.py` | Took the store's address from a pinned private file, from two environment variables, from the settings file, or from a built-in address in another product's database | Changed | MYC-D2 |
| Environment variables named for Arbol | Forced the repository, the branch view, two folders and the model folder | Dropped | MYC-0.3 |

### Commands

| Version 1 part | What it did | Fate | Specified in |
|---|---|---|---|
| `search`, `sync`, `embed`, `status`, `repos`, `derive` | The commands of the function | Changed, each as its specification says | MYC-1 to MYC-4 |
| `drifts` | Listed stored Drifts, of which there were none | Changed: `stale` lists the stale chunks | MYC-2 |
| `activity` and its table | A feed of passes and embeds | Later | MYC-D4 |
| `better-grep`, as a command and as a program of its own | Ran grep unchanged and appended search results | Later | MYC-D4 |
| `raptor`, with `knowledge/raptor.py`, `knowledge/clustering.py`, `completion_client.py` and the two prompt files in this corpus | Summaries of clusters of chunks, written by a model through another program. As read from the source, the two actions that write summaries could not run | Later | MYC-D4 |
| `knowledge/code_map.py` | Wrote an overview of a repository's code into its document corpus | Later | MYC-D4 |
| `retrieval.py`: `symbol_read`, `capabilities` | Read one symbol's source; described what the engine offers. Neither had a caller | Later | MYC-D4 |
| `knowledge/fs.py`: writing, renaming and removing corpus files | For a caller that edited documents through Mycel. No caller existed | Dropped | none |
| `wt`, `pull`, `overlay`, and the rows of branch views | Work trees and a view of the index per branch | Dropped | MYC-D6 |
| `mirror` and two tracker commands, `secrets`, with their four modules | Fetched from and wrote to the trackers of an earlier project, and stored their tokens | Dropped | MYC-D5 |

### Around the program

| Version 1 part | What it did | Fate | Specified in |
|---|---|---|---|
| Arbol 1's resident service that loaded Mycel's library | Watched folders, ran passes on a timer, served a window that showed chunks | Caller | here |
| The build into single programs under `~/bin` | One file per command, replaced in place | Changed: numbered Builds | BLD-0 |
| The tests | Ten files on settings, scope, the store's address and command names. None exercised a pass, a search, an embed or the ranking | Changed | MYC-0.11 |
| The guides of this corpus | Described version 1, in places as it was meant to be and not as it was | Changed: rewritten with each part as it is implemented | MYC-0.12 |

<!-- sources:
mycel_deprecated_v1:mycel/cli.py#main
mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema
mycel_deprecated_v1:mycel/knowledge/fs.py#write
mycel_deprecated_v1:mycel/retrieval.py#symbol_read
mycel_deprecated_v1:mycel/repo_identity.py#migrate_arbol
mycel_deprecated_v1:mycel/database.py#dsn
mycel_deprecated_v1:mycel/cli.py#_cmd_raptor
-->

## Known problems in version 1

- **It did much more than its function.** Of the 17 commands the installed program listed on 6 October 2026, seven belonged to workflows that had been retired, and their code still ran inside every pass.
- **A pass changed working checkouts.** See MYC-1.
- **It lived in another product's house.** Its tables were in Arbol 1's database, its built-in store address, its fall-back repository, its Keychain item and several messages carried Arbol's names, and one embedding profile needed a service of Arbol 1.
- **Its words and its behaviour had parted.** Comments in the source state ranking rules, guarantees about staleness and limits that the code does not keep; the inventories list them. The guides repeated them.
- **Its main paths had no tests.** No test ran a pass, a search, an embed or a ranking.
- **Reading wrote.** Every command, the reporting ones included, ran the statements that define the store's structure and rewrote the store's copy of the settings.
- **Nothing could be removed.** Neither a repository nor the rows of files long gone.

<!-- sources:
mycel_deprecated_v1:mycel/cli.py#main
mycel_deprecated_v1:mycel/cli.py#_connect_with_config
mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema
mycel_deprecated_v1:mycel/database.py#dsn
-->

## Vocabulary changes this specification requires

The Glossary entries below describe version 1. They need new wording once these specifications are accepted; they are not edited yet.

| Entry | Change |
|---|---|
| [Mycel](../../arbol/GLOSSARY.md#mycel) | No longer "a pure library + per-task CLI": a command-line program only. The resident service of Arbol 1 that it names is history, and so are the older folder and its tables' place in Arbol's database |
| [Sync Pass](../../arbol/GLOSSARY.md#sync-pass) | Covers the repositories it names and embeds only when asked. It is not started by a watcher |
| [Corpus Watcher](../../arbol/GLOSSARY.md#corpus-watcher) | History. Nothing watches folders; a search checks the repository it searches |
| [Embedder Profile](../../arbol/GLOSSARY.md#embedder-profile), [Embedding Provider](../../arbol/GLOSSARY.md#embedding-provider) | One provider and one model in the first version. The on-device provider is history unless MYC-D16 is decided otherwise |
| [Drift](../../arbol/GLOSSARY.md#drift), [Drift Candidate](../../arbol/GLOSSARY.md#drift-candidate) | Not built in version 1 and not part of the first version: the stale chunks with their reasons are the list of work |
| [Branch Overlay](../../arbol/GLOSSARY.md#branch-overlay) | History |

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D1 | In what form does Mycel exist, and in which language? | One command-line program and nothing else, in TypeScript on Node.js 24, as the Drivers (DRV-D1, DRV-D2). The repository is an npm package already. Version 1's Python programs of 80 MB each took their whole runtime along | Open |
| MYC-D2 | Where does the index live? | In PostgreSQL with ParadeDB, which gives vectors and BM25 in one store as in version 1, but in a database of Mycel's own, at an address the settings name. Version 1 shared a database with Arbol 1, which made its rows hard to tell apart, to back up and to remove | Open |
| MYC-D3 | Where are the settings kept? | In `~/.mycel/config.toml`, as in version 1, so that the owner's file stays valid. Mycel is not a component of Arbol and does not use `~/.arbol`. It reads the file and never writes it | Open |
| MYC-D4 | Which further functions of version 1 follow the first version, and in what order? | The grep replacement with a search tail first, because the research guides start from it; then reading one symbol's source; then the generated overview of a repository's code; then the feed of passes; summaries of clusters last, since they need a model and version 1's never ran as written. Each gets a specification of its own | Open |
| MYC-D5 | Does Mycel fetch content from outside? | No. The trackers of the earlier project are gone. The one integration that remains, Telegram, was never Mycel's: a service of Arbol 1 wrote its messages as files. Whoever writes them in the new stack, Mycel indexes the folder they are in like any corpus | Open |
| MYC-D6 | Are work trees and a view of the index per branch carried over? | No. Version 1 had already retired its work-tree commands, no view was registered on 7 October 2026, and MYC-D9 has Mycel read a checkout as it is | Open |
