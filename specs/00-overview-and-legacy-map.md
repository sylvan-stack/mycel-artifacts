---
role: authored
spec: MYC-0
status: accepted
---
# Mycel · 00 Overview and legacy map

[Mycel](../../arbol/GLOSSARY.md#mycel) is the knowledge engine of the Sylvan Stack. It turns the documents and the code of each repository into an index that is kept current, knows what each part rests on, and can be searched by meaning and by exact wording. This specification fixes what Mycel 2 does and what it leaves to others, the form it takes, the rules every command follows, and where each part of version 1 went. It matters because version 1 had grown well past that function, managing work trees, fetching from outside trackers and resetting checkouts, while the function itself had defects that neither its comments nor its guides knew about.

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: what Mycel is for and the four parts of its function, the boundary, form and hosting, the rules of the command line, the legacy map, the Glossary entries that need new wording.

Not covered: the four parts themselves: ingest ([MYC-1](01-corpora-and-ingest.md)), provenance and freshness ([MYC-2](02-provenance-and-freshness.md)), embedding ([MYC-3](03-embedding.md)), retrieval ([MYC-4](04-retrieval.md)); the settings file ([MYC-5](05-settings.md)) and the index store ([MYC-6](06-index-store.md)); relations and verification, the further functions of version 1 and the checks ([MYC-7](07-drifts-and-verification.md) to [MYC-13](13-checks-and-evaluation.md)); the dedicated Drift detection contract ([MYC-14](14-drift-detection.md)); distribution, numbered Builds and replacing version 1 ([MYC-15](15-distribution-and-replacement.md)).

## What Mycel is for

An agent that works in a repository asks many times a day where something is, how it works and what was already found out about it. Reading the raw files for every question is slow and blind to what belongs together. And knowledge written down once goes out of date without a sign: a guide keeps describing code that has changed under it.

Mycel answers both. Its function has four parts, each resting on the one before.

| Part | From | To | Specified in |
|---|---|---|---|
| Ingest | The files of a repository | [Chunks](../../arbol/GLOSSARY.md#chunk) with a stable identity | MYC-1 |
| Provenance and freshness | The sources a section names | Edges that remember each source, and a mark on what went out of date | MYC-2 |
| Embedding | The complete text of a chunk | One or more vectors covering every part of its text | MYC-3 |
| Retrieval | A question or a name | The chunks that answer it, ranked | MYC-4 |

Observed in version 1's design record, and kept as the principles of Mycel 2:

- **Identity is not a place.** A chunk has an identifier that survives edits, renames and moves. Its name and path are an address that may change.
- **Finding out what is stale never uses a model.** It compares hashes. Models appear only where text is produced or embedded.
- **One store, divided by repository.** Repositories share the store and never mix in a result.
- **Git owns history.** Mycel reads the disk and the current tips of every local branch and stash, and retains the chunk versions found in those locations. It does not retain every commit or a version no location holds. Search, edges and staleness use disk versions (MYC-D8).
- **Retrieval is a tool an agent calls,** and its reply is a contract.

**Historical evidence (unindexed):**

- `arbol_deprecated_v1:research/RETRIEVAL-RESEARCH.md#1.1 The problem`
- `arbol_deprecated_v1:research/RETRIEVAL-RESEARCH.md#1.2 Core principles`

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
| Summaries of clusters of chunks, a generated overview of the code, a grep replacement with a search tail | Mycel | Mycel: [MYC-8](08-summaries.md), [MYC-9](09-code-overview.md) and [MYC-10](10-grep-replacement.md) ([MYC-D4](#decisions)) |
| Work trees and a view of the index per branch | Mycel | Nobody makes work trees ([MYC-D6](#decisions)). Mycel reads every local branch and stash itself and records where each chunk is found ([MYC-D8](01-corpora-and-ingest.md#decisions)) |
| Fetching tickets, wiki pages and code reviews from outside trackers, and writing to them | Mycel | Nobody. Content from outside reaches Mycel as files in a corpus, or as data in an Arbol-owned database that Mycel reads ([MYC-D5](#decisions)) |

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/cli.py#main`
- `mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked`
- `mycel_deprecated_v1:mycel/config.py#apply`
- `arbol_deprecated_v1:architecture/external-tools.md#Dependency law`

## Form and hosting

The owner decided the form and Python implementation language (MYC-D1), the index store (MYC-D2), and the settings location (MYC-D3). Packaging defaults chosen by the agent are specified in MYC-15.

- **Form.** Mycel is one command-line program, `mycel`, implemented in Python. Its command line is its only interface: a caller starts the program and reads the result from standard output. There is no library for callers to load, so no other program contains Mycel's code ([MYC-D1](#decisions)). Internal Python modules and release tools do not create another product interface. Version 1 was also a library, which Arbol 1's resident service loaded.
- **No resident service.** Mycel is not a daemon and has no socket, launch agent or watcher. Every invocation is one process that does one thing and ends. This was the strict rule of version 1 and is kept.
- **Builds.** Mycel is built into numbered Builds kept side by side in its own registry ([MYC-15](15-distribution-and-replacement.md)). Each Build carries its pinned Python runtime and dependencies. The name on the search path is a Mycel launcher: without a build number it starts the newest working Build. Running a Build installs, downloads and extracts nothing.
- **State.** Mycel keeps all mutable knowledge and operation state in PostgreSQL with ParadeDB, in a database of its own at an address supplied by the settings ([MYC-D2](#decisions)). Installed program files, build records and release logs are separate distribution files specified in MYC-15, not another index or invocation cache. Its settings are in `~/.mycel/config.toml`, written by the owner or their editor; Mycel reads the file and never writes it ([MYC-D3](#decisions)). Credentials use the system Keychain as MYC-5 specifies. The store carries Mycel's format number (MYC-6); a Build that does not support that format refuses store operations.
- **Independence.** Mycel uses no code and no instructions of Arbol. Product-specific names are forbidden except the explicit packaged settings data of MYC-D37: the MYC-D18 shared selections (`mycel` documents and `arbol:GLOSSARY.md`) and the MYC-D7 `.arbol` scan exclusion. These data create no repository, alias, folder fallback or runtime dependency, and the shared selections are overridden through settings. It may read the files and data of any product as data.
- **Network.** Mycel calls the embedding provider (MYC-3) and selected Jev API for Drift classification (MYC-D28). Classification uses a five-minute quiet period, and low-confidence results go to a more expensive, smarter review model under [MYC-14](14-drift-detection.md); its exact reviewer is deployment configuration under the completed protocol-1 contract. The settings also name the program that writes summaries ([MYC-8](08-summaries.md#who-writes-the-text), MYC-D31), which may call a service. These calls do not fetch source content or permit a git command that changes anything.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:pyproject.toml`
- `mycel_deprecated_v1:Makefile`
- `arbol_deprecated_v1:architecture/external-tools.md#Runtime contracts`

## The command line

Proposed. The rules below hold for every command. The commands themselves are specified with their subject.

| Command | Does | Specified in |
|---|---|---|
| `mycel search` | Answers a question or finds a name | MYC-4 |
| `mycel ingest` | Brings the index of a repository up to date with its files | MYC-1 |
| `mycel embed` | Embeds the pending chunks of a repository | MYC-3 |
| `mycel status`, `mycel repos` | Report on repositories; `mycel repos remove` deletes one from the index | MYC-1 |
| `mycel stale`, `mycel refs`, `mycel derive`, `mycel confirm` | The list of stale chunks, faults in refs, asserting an edge, confirming a chunk | MYC-2 |
| `mycel drifts`, `mycel relate`, `mycel verifications` | The list of work, relating two chunks, the record of checks | MYC-14, MYC-7 |
| `mycel classify` | Explicit bounded Jev classification and uncertain-case smarter review | MYC-14 |
| `mycel summaries` | Summaries of groups of sections: status, build, regenerate, remove | MYC-8 |
| `mycel overview` | The overview of a repository's code | MYC-9 |
| `mycel grep` | Runs grep as asked and adds related results. It departs from some of the rules below, as MYC-10 says | MYC-10 |
| `mycel read` | Returns one whole chunk | MYC-11 |
| `mycel activity` | The record of what Mycel did | MYC-12 |
| `mycel evaluate` | Runs a repository's evaluation set | MYC-13 |
| `mycel api-key voyage`, `mycel api-key jev` | Prompt without echo and store the API key in its named login-Keychain item | MYC-5 |
| `mycel init` | Creates the index store's structure, or brings it to the format of the Build that runs | here, MYC-6 |
| `mycel info` | Says which Build runs and what it found | here, MYC-5 |

| Rule | Detail |
|---|---|
| One invocation, one operation | The program starts, does what the command says and ends. Mutable knowledge and operation state stay only in the index store; installed distribution files are governed by MYC-15 |
| Build | `-v <build number>` as the first argument runs that Build. Without it the default Build runs: the newest working one (MYC-15) |
| Repository | `--repo <name>` names it; without it the repository of the current directory is meant; when there is none the command is refused. An organization's name, or its folder outside its members, means every enabled member of it (MYC-1.4) |
| Output | One JSON document on standard output. A caller ignores fields it does not know |
| Errors | A command that is refused or fails writes `{ "error": { "code", "message" } }` as its result. The codes are a closed list: `invalid_input`, `io`, `settings`, `unknown_repository`, `store_unavailable`, `store_format`, `busy`, `refused`, `internal` |
| Exit status | 0: done as asked. 1: refused or failed. 2: stopped by the caller |
| Several repositories | A command that covers one or several repositories gives each an entry of its own. When any of them was refused or not run, the status is 1 and the full reply is still written. An error object alone is the result only when nothing could be started for any of them (MYC-6.14, MYC-D27) |
| Standard error | Progress and diagnostics for a person. A caller never needs it to understand a result, and no secret is written there |
| Secrets | Mycel is never given a secret as an argument, on standard input or in its settings file (MYC-3.14). The explicit `api-key` command reads one key from a terminal with echo disabled and writes only its named encrypted Keychain item (MYC-5.16) |
| Reports | A command that only reports writes nothing (MYC-1.28). The store's structure changes only in `mycel init` |
| `info` | Prints the package version and the build number of the Build that runs, the version of the search reply it produces, the settings file, the index store and its format number, and the embedding model |

```ts
interface MycelInfo {
  version: string;                     // the package version, e.g. "2.0.0"
  build: string;                       // the build number of the Build that runs (MYC-15)
  searchReply: number;                 // the version of the search reply (MYC-4)
  settingsFile: string;                // whether or not it exists
  store: { location: string; format?: number; indexGeneration?: string; reachable: boolean };
  embedding: { provider: string; model: string; dimensions: number; keyFound: boolean };
}
```

## Requirements

| ID | Mycel must… | Origin | Verified by |
|---|---|---|---|
| MYC-0.1 | be one command-line program whose command line is its only interface: no library for callers, no socket, and every invocation ends by itself when its operation is done | Changed | unit |
| MYC-0.2 | run no resident process of any kind: no daemon, no watcher, no launch agent, no timer | Kept | unit |
| MYC-0.3 | work with nothing of Arbol installed or running, and contain no built-in product-specific name, path, variable or message except the explicit packaged data of MYC-D37; repository names and shared document selections supplied in settings are data | Changed | unit |
| MYC-0.4 | keep mutable knowledge and operation state only in its own PostgreSQL index database with ParadeDB, at the address supplied by the settings; keep only the distribution files of MYC-15 outside it, and read `~/.mycel/config.toml` at the start of every invocation | Changed | store |
| MYC-0.5 | never write its settings file | Changed | unit |
| MYC-0.6 | follow the command-line rules above for the repository, output, errors and exit status | Changed | unit |
| MYC-0.7 | report every failure as one error object with a code from the closed list, and never ask a caller to match error text | New | unit |
| MYC-0.8 | change the structure of the index store only in `mycel init`, and refuse every other store-dependent command with `store_format` when the store's format is not the one its Build knows; diagnostic `info` and grep without its Mycel tail remain available | Changed | store |
| MYC-0.9 | be built into numbered Builds as MYC-15 says and report the build number of the Build that runs in `info` | New | unit |
| MYC-0.10 | call model services only for embedding, explicit classify or live drift evaluation, and the configured summary-writing operation; make no Jev/reviewer calls from ingest/search/read/reporting or dry-runs, forward no Mycel credentials to child programs, and run no git command that changes a repository | Changed | unit |
| MYC-0.11 | have an automated check for every requirement of MYC-1 to MYC-16 before that requirement counts as implemented, the store-backed ones against a store made for the test and discarded after it | New | store |
| MYC-0.12 | keep the guides of this corpus true to the program: a change to a command, an option or a reply changes the guide that describes it in the same change | New | unit |

## Legacy map

Fate is one of: **Kept** (same behaviour, rewritten), **Changed** (same purpose, different behaviour), **Required follow-up** (the purpose remains and its detailed specification and implementation must be completed), **Caller** (the purpose remains and belongs to whoever calls Mycel), **Dropped**.

### The engine

| Version 1 part | What it did | Fate | Specified in |
|---|---|---|---|
| `knowledge/chunker.py` | Split Markdown at headings, read frontmatter and Source Refs | Kept, with corrections to names and to how frontmatter is read | MYC-1, MYC-2 |
| `knowledge/code_chunker.py` | Split Python, TypeScript, JavaScript and Svelte along their structure | Kept, with corrections to names and decorators | MYC-1 |
| `knowledge/store.py`: scan and ingest | Two separate scans and two ways of matching, one for documents and one for code | Changed: one scan, one way of matching, each file in one transaction | MYC-1 |
| `knowledge/store.py`: edges and detection | Declared, asserted and generated edges; stale marks for the whole index | Changed: what renews an edge, what a removed source does, the scope of a pass | MYC-2 |
| `knowledge/store.py`: Drifts | Tables and functions for stored items of work, never filled | Changed: stored work items and the completed detection/lifecycle contract of MYC-14 are accepted | MYC-14 |
| `knowledge/embedder.py`: embedding | Sent pending chunks of all repositories to the embedding service, one attempt each | Changed: per repository, with retries and honest counts | MYC-3 |
| `knowledge/local_embedder.py` | Client of an on-device embedding service that belonged to Arbol 1 | Dropped: Voyage API is the only embedding provider | MYC-D16 |
| `knowledge/embedder.py`: search; `retrieval.py` | Two arms, two routes, the bridge from documents to code, the reply | Changed: the rules hold as stated, results say what they are | MYC-4 |
| `syncpass.py`: the pass | Ingest, detection, overview, for all repositories or one | Changed | MYC-1 |
| `syncpass.py`: `refresh_mirror` | Fetched the remote's default branch and reset the checkout to it | Dropped | MYC-D9 |
| `syncpass.py`: `repo_stale`, `newer_than` | Looked for files changed since the last pass, with no time limit | Changed: a time limit, and the same folders skipped as the scan | MYC-4 |

### Settings and scope

| Version 1 part | What it did | Fate | Specified in |
|---|---|---|---|
| `config.py` | Read the settings file and copied its repositories into the store on every command; created the file when missing | Changed: the file alone holds the settings, and Mycel never writes it | MYC-1, MYC-5 |
| `organizations.py` | Treated the direct children of a configured folder as member repositories | Kept | MYC-1 |
| `locations.py`, `scope.py` | Found a repository's folders and the repository of a path, with fall-backs to two older folder layouts and to a built-in repository name | Changed: configured folders only, no fall-back | MYC-1 |
| `repo_identity.py` | Rewrote one repository's name and moved its rows at every start | Dropped | MYC-1.5 |
| `database.py` | Took the store's address from a pinned private file, from two environment variables, from the settings file, or from a built-in address in another product's database | Changed | MYC-D2, MYC-6 |
| Environment variables named for Arbol | Forced the repository, the branch view, two folders and the model folder | Dropped | MYC-0.3 |

### Commands

| Version 1 part | What it did | Fate | Specified in |
|---|---|---|---|
| `search`, `sync`, `embed`, `status`, `repos`, `derive` | The commands of the function | Changed, each as its specification says. `sync` is now `ingest` | MYC-1 to MYC-4 |
| `drifts` | Listed stored Drifts, of which there were none | Changed: `stale` lists the stale chunks | MYC-2 |
| `activity` and its table | A feed of passes and embeds | Required follow-up | MYC-12 |
| `better-grep`, as a command and as a program of its own | Ran grep unchanged and appended search results | Required follow-up | MYC-10 |
| `raptor`, with `knowledge/raptor.py`, `knowledge/clustering.py`, `completion_client.py` and the two prompt files in this corpus | Summaries of clusters of chunks, written by a model through another program. As read from the source, the two actions that write summaries could not run | Required follow-up | MYC-8 |
| `knowledge/code_map.py` | Wrote an overview of a repository's code into its document corpus | Required follow-up | MYC-9 |
| `retrieval.py`: `symbol_read`, `capabilities` | Read one symbol's source; described what the engine offers. Neither had a caller | Required follow-up | MYC-11 |
| `knowledge/fs.py`: writing, renaming and removing corpus files | For a caller that edited documents through Mycel. No caller existed | Dropped | none |
| `wt`, `pull`, `overlay`, and the rows of branch views | Work trees and a view of the index per branch | Dropped. What branches and stashes hold is read from git instead | MYC-D6, MYC-D8 |
| `mirror` and two tracker commands, `secrets`, with their four modules | Fetched from and wrote to the trackers of an earlier project, and stored their tokens | Dropped | MYC-D5 |

### Around the program

| Version 1 part | What it did | Fate | Specified in |
|---|---|---|---|
| Arbol 1's resident service that loaded Mycel's library | Watched folders, ran passes on a timer, served a window that showed chunks | Caller | here |
| The build into single programs under `~/bin` | One file per command, replaced in place | Changed: numbered Builds with installed Python runtimes and one Mycel launcher | MYC-15 |
| The tests | Ten files on settings, scope, the store's address and command names. None exercised a pass, a search, an embed or the ranking | Changed | MYC-0.11, MYC-13 |
| The guides of this corpus | Described version 1, in places as it was meant to be and not as it was | Changed: rewritten with each part as it is implemented | MYC-0.12 |

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/cli.py#main`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema`
- `mycel_deprecated_v1:mycel/knowledge/fs.py#write`
- `mycel_deprecated_v1:mycel/retrieval.py#symbol_read`
- `mycel_deprecated_v1:mycel/repo_identity.py#migrate_arbol`
- `mycel_deprecated_v1:mycel/database.py#dsn`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_raptor`

## Known problems in version 1

- **It did much more than its function.** Of the 17 commands the installed program listed on 6 October 2026, seven belonged to workflows that had been retired, and their code still ran inside every pass.
- **A pass changed working checkouts.** See MYC-1.
- **It lived in another product's house.** Its tables were in Arbol 1's database, its built-in store address, its fall-back repository, its Keychain item and several messages carried Arbol's names, and one embedding profile needed a service of Arbol 1.
- **Its words and its behaviour had parted.** Comments in the source state ranking rules, guarantees about staleness and limits that the code does not keep; the inventories list them. The guides repeated them.
- **Its main paths had no tests.** No test ran a pass, a search, an embed or a ranking.
- **Reading wrote.** Every command, the reporting ones included, ran the statements that define the store's structure and rewrote the store's copy of the settings.
- **Nothing could be removed.** Neither a repository nor the rows of files long gone.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/cli.py#main`
- `mycel_deprecated_v1:mycel/cli.py#_connect_with_config`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema`
- `mycel_deprecated_v1:mycel/database.py#dsn`

## Vocabulary changes this specification requires

The Glossary entries below still describe version 1. Aligning their wording with the accepted Mycel 2 contracts remains follow-up work; the entries have not been edited.

| Entry | Change |
|---|---|
| [Mycel](../../arbol/GLOSSARY.md#mycel) | No longer "a pure library + per-task CLI": a command-line program only. The resident service of Arbol 1 that it names is history, and so are the older folder and its tables' place in Arbol's database |
| [Sync Pass](../../arbol/GLOSSARY.md#sync-pass) | Covers the repositories it names and embeds only when asked. It is started with `mycel ingest`, not by a watcher |
| [Corpus Watcher](../../arbol/GLOSSARY.md#corpus-watcher) | History. Nothing watches folders; a search checks the repository it searches |
| [Embedder Profile](../../arbol/GLOSSARY.md#embedder-profile), [Embedding Provider](../../arbol/GLOSSARY.md#embedding-provider) | Voyage API is the only embedding provider. The default model is `voyage-code-4` at 1024 dimensions; the on-device provider is history (MYC-D14, MYC-D16) |
| [Drift](../../arbol/GLOSSARY.md#drift), [Drift Candidate](../../arbol/GLOSSARY.md#drift-candidate) | Not built in version 1; stored work items, dependency classification and the other provenance designs are required, with complete accepted contracts in MYC-7/MYC-14/MYC-16 and implementation still to follow (MYC-D13, MYC-D28) |
| [Branch Overlay](../../arbol/GLOSSARY.md#branch-overlay) | History |
| [Attestation](../../arbol/GLOSSARY.md#attestation), [Coupling](../../arbol/GLOSSARY.md#coupling) | In Mycel they are the recorded verification and the relation without authority of MYC-7. [MYC-14](14-drift-detection.md) records selected Jev classification without a change-size threshold, five-minute debounce and low-confidence smarter-model review (MYC-D28); the complete reviewer and work-closure contracts are accepted under MYC-D28/MYC-D29 |
| [RAPTOR Summarization](../../arbol/GLOSSARY.md#raptor-summarization), [RAPTOR Rebuild](../../arbol/GLOSSARY.md#raptor-rebuild), [Stale Summary Regeneration](../../arbol/GLOSSARY.md#stale-summary-regeneration) | The text of a summary is written by the command the settings name, not through `infer` and a Brain Recipe; the actions are `mycel summaries build` and `regenerate` (MYC-8, MYC-D31) |
| [Code Map](../../arbol/GLOSSARY.md#code-map) | Kept in the index and printed by `mycel overview`; no file is written (MYC-9, MYC-D32) |
| [better-grep](../../arbol/GLOSSARY.md#better-grep) | The command `mycel grep`; no program of its own (MYC-10, MYC-D33) |

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D1 | In what form does Mycel exist, and in which language? | One command-line program and nothing else. The earlier TypeScript/Node.js proposal was superseded by the owner's language choice; distribution and runtime provisioning are specified independently in MYC-15 | Decided 8 October 2026 by the owner: “It should be python.” Mycel is a Python command-line program whose command line is its only caller interface; it has no daemon, watcher or library interface for callers |
| MYC-D2 | Where does the index live? | In PostgreSQL with ParadeDB, which gives vectors and BM25 in one store as in version 1, but in a database of Mycel's own, at an address the settings name. Version 1 shared a database with Arbol 1, which made its rows hard to tell apart, to back up and to remove | Decided 8 October 2026 by the owner: resolved; accept PostgreSQL with ParadeDB in a database of Mycel's own, at an address supplied by the settings |
| MYC-D3 | Where are the settings kept? | In `~/.mycel/config.toml`, as in version 1, so that the owner's file stays valid. Mycel is not a component of Arbol and does not use `~/.arbol`. It reads the file and never writes it | Decided 8 October 2026 by the owner: resolved; keep the settings in `~/.mycel/config.toml`. The owner or their editor writes the file; Mycel only reads it |
| MYC-D4 | Which further functions of version 1 follow the first version, and in what order? | The grep replacement with a search tail; reading one symbol's source; the generated overview of a repository's code; the feed of passes; summaries of clusters. Each gets a specification of its own | Decided 8 October 2026 by the owner: implement all specifications regardless of how many tasks are involved. Every listed function remains required; task volume is not a reason to defer or drop it, and dependency order may guide the work |
| MYC-D5 | Does Mycel fetch content from outside? | No. The trackers of the earlier project are gone. The one integration that remains, Telegram, was never Mycel's: a service of Arbol 1 wrote its messages as files. Whoever writes them in the new stack, Mycel indexes the folder they are in like any corpus | Decided 8 October 2026 by the owner: resolved; Mycel has no integrations that fetch outside content. Another component saves that content as files, and Mycel indexes those files. Amended 19 October 2026 by the owner: Mycel may read Arbol-owned databases, the chat content of the Arbol database among them, and other local data as inputs. Reading data is neither an integration nor a dependency on Arbol code or instructions ([Instructions Hub](../README.md#rules-that-bite)), and Mycel still works with no Arbol database reachable (MYC-0.3). Fetching from outside services stays with another component, which saves the content as files |
| MYC-D6 | Are work trees and a view of the index per branch carried over? | Not in version 1's form. Version 1 had already retired its work-tree commands, and no view was registered on 7 October 2026. Mycel 2 makes no work tree: it reads every local branch and stash from git and records where each chunk is found (MYC-D8) | Decided 8 October 2026 by the owner: resolved; retire the work-tree commands and separate branch indexes. Read local branches and stashes from git and record where each chunk version is found, as decided in MYC-D8; search uses the versions on disk |

| MYC-D37 | Do the previously prescribed named defaults/exclusion remain exceptions to the independence and repository-name prohibitions? | Retain only the named MYC-D18 shared selections and MYC-D7 `.arbol` scan exclusion as explicit packaged data; no implicit repository, alias, path fallback or dependency | Decided 9 October 2026 by the owner: keep the prescribed names as explicit exceptions. All other product-specific naming remains prohibited; MYC-0.3 and MYC-1.5 are reconciled accordingly |
