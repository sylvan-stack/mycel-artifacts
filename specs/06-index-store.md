---
role: authored
spec: MYC-6
status: implemented
---
# Mycel · 06 The index store

Everything Mycel knows between two invocations is in its index store: the chunks, their versions and vectors, the edges, the marks, the record of its work. This specification fixes what the store holds, where it is and how Mycel reaches it, how its structure is made and changed, what happens when two invocations work at the same time, and what becomes of rows whose repository left the settings. It matters because version 1 kept its tables inside another product's database at an address built into its code, ran the statements that define the structure in every command, and let two passes rewrite the same marks at once.

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: what the store holds and what only it holds, its address, `mycel init` and the format number, transactions, two invocations at once, a command over several repositories, rows of repositories the settings no longer name, what is carried over from version 1.

Not covered: what the rows mean, which is specified with their subject ([MYC-1](01-corpora-and-ingest.md) to [MYC-4](04-retrieval.md), [MYC-7](07-drifts-and-verification.md) to [MYC-12](12-record-of-work.md), and Drift classification in [MYC-14](14-drift-detection.md) and evidence in [MYC-16](16-source-addresses-and-evidence.md)); the settings keys ([MYC-5](05-settings.md)); the stores that the automatic checks make for themselves ([MYC-13](13-checks-and-evaluation.md)).

## Behaviour

### What the store holds

Observed in version 1: ten tables whose names begin with `kn_`. They held documents, chunks with one text and one vector each, edges, a log of identity decisions and a log of ingest runs that nothing read, Drifts that nothing wrote, a copy of the repositories of the settings file, the views of branches, and a feed of passes. Observed on 7 October 2026: they shared a database of 9.8 GB with 92 tables of Arbol 1.

Proposed:

| Record | Written by | Specified in |
|---|---|---|
| Documents and chunks; for each chunk its versions and the locations each version is found in | `ingest` | MYC-1 |
| Requirement and decision entities: chunks of kind `req` and `dec` whose identifier is the UUID of their row, with their versions and locations; the entity row is never deleted | `ingest` | MYC-17 |
| For each repository: when its last pass ran, and which branch and stash commits were already read | `ingest` | MYC-1 |
| Edges, relations, faults in refs, stale reasons and classification evidence, including pending debounce and LLM review | `ingest`, `derive`, `relate`, `confirm`, `classify` | MYC-2, MYC-7, MYC-14 |
| Drifts and recorded verifications | reconciliation, `classify`, `confirm` | MYC-14, MYC-7 |
| Dependant-owned snapshots, baseline/request manifests, owning references and in-flight evidence leases | the invocation that pins, captures, applies or prunes their owner under its repository lock | MYC-16 |
| Index generation UUID and invocation/session liveness identities | `init`, mutating invocations | MYC-12, MYC-16 |
| Embedding plans, parts, vectors and failures | `embed` | MYC-3 |
| Summaries and the sections of the code overview | `summaries`, `ingest` | MYC-8, MYC-9 |
| The record of work, with the identity decisions of each pass | every command that changes the store | MYC-12 |
| The format number and the number of dimensions of a vector | `init` | here |

The store holds no settings copy (MYC-1.1), no secret and no operational state of another product. Searchable chunk/version rows contain only text found in a current disk, local branch or stash location (MYC-1.21). The explicit exception is MYC-16's dependant-owned immutable evidence: snapshots and manifests may retain exact before text after the source's indexed rows are deleted, with no searchable chunk, locations or vector. Every pin, work/verification bundle and in-flight lease owns its evidence in the dependant repository. Pin/repin and owning-reference changes commit in the same transaction as their operation; garbage collection deletes only unreferenced blobs under that owner repository's lock.

Most of the store can be made again from the files with `mycel ingest`. The following cannot, because they exist nowhere else:

- edges and relations that were asserted with a command, not written in a file;
- confirmations and recorded verifications;
- summaries, which cost calls to a model;
- vectors, which cost quota of the embedding service;
- the record of work and the history of Drifts;
- former pinned source snapshots and exact request evidence whose bytes no live location retains.

Keeping a copy of the store is the owner's affair, with the tools of the database. Mycel has no command for it.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema`
- `mycel_deprecated_v1:mycel/knowledge/store.py#log_activity`
- `mycel_deprecated_v1:mycel/knowledge/store.py#open_drifts`

MYC-D55, decided 19 October 2026 by the owner: Mycel's and Arbol's databases live on the local PostgreSQL and share one backup. Stated Origin Links are the unique authored content of the Index Store: recovered links regenerate, declared links come from files, and chat content remains Arbol's. Retained evidence, confirmations, vectors and history remain valuable stored results with the ownership and retention rules above; this wording does not delete them or turn them into files. Mycel provides no backup command.

### Where the store is

Observed in version 1: the address came from the first of four places that gave one: two environment variables that named a private file and its checksum; two more that held the address itself; the settings file; and an address built into the code, which pointed into Arbol 1's database and carried a user name and a password. A further pair of variables chose a schema inside that database.

Decided: the store is a PostgreSQL database of Mycel's own, with ParadeDB for vectors and BM25 ([MYC-D2](00-overview-and-legacy-map.md#decisions)). Its address is the setting `store.address` and nothing else: no address is built in, and no variable overrides it. The address names host, port, database and user. The password, when the store asks for one, comes from Mycel's Keychain item ([MYC-5](05-settings.md#credentials), [MYC-D25](#decisions)); the earlier Keychain-only decision remains in force.

A store that cannot be reached refuses the command with `store_unavailable`. `mycel info` says so in its report and is not refused, and `mycel grep` still runs grep (MYC-10.11). Mycel hands the address to no other program: it is not placed into the environment of `git`, `grep` or the command that writes summaries.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/database.py#dsn`
- `mycel_deprecated_v1:mycel/database.py#private_dsn`
- `mycel_deprecated_v1:mycel/database.py#connect`
- `mycel_deprecated_v1:mycel/cli.py#_export_dsn`

### Making and changing the structure

Observed in version 1: every process ran the statements that create the tables, and several statements that add columns ran on every call of two functions. There was no record of which structure a database had. The same statements wrote data: they created a repository named `arbol`, switched on, whenever it was missing. The index by wording was created by whichever search came first, and was left out without a word when its extension was missing.

Proposed: the structure is made and changed by `mycel init` and by no other command (MYC-0.8). The store carries a format number, which starts at 1 and is raised only by a change that an older Build cannot read ([MYC-15](15-distribution-and-replacement.md)).

| The database | `mycel init` | Every other command |
|---|---|---|
| is empty | makes the structure of the Build that runs, both search indexes included | is refused with `store_format` |
| has the format of the Build that runs | changes nothing and says so | runs |
| has an older format | brings it forward one format at a time, each step in one transaction | is refused with `store_format`, naming both numbers |
| has a newer format | is refused with `store_format` | is refused with `store_format` |
| holds tables that are not Mycel's | is refused with `refused`: Mycel shares its database with nothing | is refused with `store_format` |

`mycel info` runs in every one of these states and reports the format it found. `mycel grep` runs grep and leaves out its tail.

Format 3, of 19 October 2026, admits the chunk kinds `req` and `dec` of [MYC-17](17-justification.md) and keeps their rows out of collection; `mycel init` brings a format 2 store forward in one step, with no row to rewrite.

Format 4, of 26 October 2026, adds to each repository's state how far a pass run in steps has refreshed its unchanged files ([MYC-1.40](01-corpora-and-ingest.md)); `mycel init` brings a format 3 store forward in one step, adding an empty column.

Format 5, of 27 October 2026, adds a table of judgements: each recovery or model-audit judgement that changed nothing, under its repository, question, exact chunk version, candidate and judgement policy, so that a series of steps never pays for it again ([MYC-D68](17-justification.md#decisions)). A row goes with its repository or its chunk version. `mycel init` brings a format 4 store forward in one step, adding the empty table.

Builds are kept side by side, and each can be started by its number (MYC-0). Once a newer Build has raised the format, the older Builds refuse this store, and there is no way back to the earlier format.

`mycel init` needs the extensions to be available in the database server. When one is missing it ends with the error `refused` and names the extension. Beyond the structure it writes the format number and the number of dimensions, and no repository and no default row.

The number of dimensions of a vector is part of the structure. When the settings name another number than the store has, `mycel init` changes the structure and removes the vectors of the old size. Until it has run, `mycel embed` is refused with `store_format`, and a search answers by wording alone and says why (MYC-4.16).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema`
- `mycel_deprecated_v1:mycel/knowledge/store.py#list_repo_flags`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#ensure_bm25_index`
- `mycel_deprecated_v1:mycel/syncpass.py#_ensure_last_sync_col`

### Transactions

Observed in version 1: every statement was committed by itself. A file's new hash was stored before its chunks, so a failure in between left a file that later passes skipped, half applied. Marking stale chunks first cleared every mark of the whole index and then wrote the new ones, one statement each.

Proposed: what belongs together is written together or not at all.

| Change | One transaction holds |
|---|---|
| A file in a pass | Its hash, its chunks and versions, and its identity decisions (MYC-1.22) |
| Detection for a repository | Every mark it sets and every mark it clears |
| `derive`, `relate`, `confirm`, `repos remove` | The whole change of the command |
| New summaries taking the place of old ones | The whole exchange (MYC-8) |
| A batch of an embed | The vectors of that batch (MYC-3.7) |

A command that only reads sees one state of the store from its first row to its last, whatever is written meanwhile.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/database.py#connect`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/store.py#detect`

### Two invocations at once

Observed in version 1: a pass took its locks in the database without waiting. A pass for all repositories shut out every other pass, and a pass for one repository shut out a second one for the same repository. A pass that found itself shut out did nothing and said so. Marking stale chunks was not covered by the lock of one repository: two passes for different repositories could both clear and rewrite the marks of the whole index at the same time. The inventories name no lock around an embed.

Proposed: nothing waits. An invocation that cannot do its work because of another one says so at once.

| While this runs | A second invocation that asks for | Gets |
|---|---|---|
| A pass on a repository | a pass on the same repository | Nothing done for that repository, and the reply says a pass is running (MYC-1.25) |
| A pass on a repository | a search of it | The answer from the store as it is; the reply says the freshness check was not finished (MYC-4.19) |
| A pass on a repository | an embed of it | The embed runs. A vector for a version that the pass deleted meanwhile is discarded |
| An embed of a repository | an embed of the same repository | Nothing done for that repository, and the reply says an embed is running. Two embeds would send the same parts and pay for them twice |
| Any pass, embed, classification, summary operation or pinning/evidence mutation of a repository | `repos remove` of it | Refused with `busy` |
| Classification of a repository | classification of the same repository | Refused with `busy` |
| Classification holding immutable input leases | a normal ingest pass | It runs; changed inputs obsolete the classifier result |
| A pass/pinning transaction on a repository | classifier snapshot or result-application transaction | Nonblocking lock failure leaves affected classification pending |
| Writing or rewriting summaries of a repository | the same for that repository | Refused with `busy` |
| `mycel init` changing the structure | anything but `info` and `grep` | Refused with `busy` |
| Anything | `mycel init` that has to change the structure | Refused with `busy` |
| Anything | a command that only reports | It runs |

Passes on different repositories run side by side. A pass writes only dependency records and stale marks affected by the sources it checked. Where a changed source affects dependants in another repository (MYC-2.18), it takes that repository's pass lock without waiting before applying those updates. If the lock is unavailable, it leaves the affected updates pending and reports that propagation is incomplete. It does not rewrite unrelated dependency records or marks.

A lock is held in the store by the connection of the invocation that took it. It ends with that process, however the process ends. There is no lock file and nothing to clear after a crash. Repository operation keys and MYC-12's exact-invocation liveness keys occupy distinct collision-free advisory-lock namespaces. Classification and MYC-8 summary operations keep their operation/liveness key while model calls run, but release the pass lock between input capture and guarded result publication. Every operation that creates owning evidence or pins participates in the repository mutation/removal lock protocol; `repos remove` cannot delete a live lease.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/syncpass.py#_run_coalesced`
- `mycel_deprecated_v1:mycel/syncpass.py#run_repo_pass`
- `mycel_deprecated_v1:mycel/knowledge/store.py#detect`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embed_pending`

MYC-D60 changes the pass reservation from repository to location. Each clone's capture and pass reservation are independent; short guarded publication protects shared identities, dependencies, evidence and collection. Repository removal still excludes every live location operation. Contention on shared writes is reported without waiting or partial commit, and a pass on one clone never collects another clone's locations.

### A command over several repositories

Observed in version 1: a search of an organization returned one reply for each member. A full pass and an embed gave one set of numbers for all repositories together, so nothing said which repository a failure belonged to.

Decided: a command that covers several repositories, by `--all`, by several `--repo` or by an organization, gives each repository an entry of its own. An entry says that the work was done, or that it was refused and why, or that it was not run because another invocation was at work. The exit status is 0 only when every repository was done as asked. Otherwise it is 1, and standard output still holds the full reply with every entry ([MYC-D27](#decisions)). An error object alone is the result only when nothing could be started for any repository: the settings cannot be read, or the store cannot be reached or has another format.

The rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line) therefore have three outcomes: a result with the status 0, an error object with the status 1, and a full reply with the status 1. The third holds for a command that names one repository as well: when the entry of that repository says refused or not run, the status is 1.

Where a specification gives the reply of a command for one repository only, the reply for several is `{ repositories: [ … ] }`. It holds one such reply for each repository, or `{ repository, refused }` for one that was refused.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/cli.py#search_payload`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_sync`

### Rows of a repository the settings no longer name

Observed on 7 October 2026: the table of repositories held 38 rows, among them both `arbol` and `Arbol`. A repository that was switched off kept answering searches, and no command removed its rows; they were deleted with SQL, table by table, in the order the references between the tables require.

Proposed: the settings file alone says which repositories exist (MYC-1.1). Rows in the store whose repository the file no longer names, or names as switched off, take part in nothing: no search returns them (MYC-4.2), no embed sends them (MYC-3.13), no pass touches them. They are not deleted by themselves, because an entry can leave the file by a slip. `mycel status --all` lists every name that has rows, and says for each whether the settings know it. `mycel repos remove` removes the rows of any name that has some, whether or not the settings know it (MYC-1.27).

### Nothing is carried over from version 1

Observed in version 1: the store was part of Arbol 1's database. Its rows have one text and one vector per chunk, no versions, no locations, no parts, and no record of which model made a vector.

Decided: Mycel 2 reads none of version 1's tables and writes into none, and nothing is copied across ([MYC-D26](#decisions)). Its store is a new database, filled from the files by `mycel ingest` and `mycel embed`. This costs one embedding of everything, which the new model asks for in any case (MYC-D14). Edges that were asserted with `mycel derive` and the summaries are not made again by that; whoever wants one makes it anew.

Everything of version 1 is removed: its ten tables in Arbol 1's database, its two programs, and its keys in the settings file, which went on 8 October 2026 ([MYC-5](05-settings.md#a-key-mycel-does-not-know)). The inventoried cutover/removal is done once through MYC-15's explicit operator procedure. It is not a function of Mycel 2, which never touches those tables (MYC-6.17).

## Requirements

| ID | Mycel must… | From v1 | Verified by |
|---|---|---|---|
| MYC-6.1 <!-- 8e776c03-204a-4aea-8b57-610d9a5001e5 --> | keep mutable knowledge and invocation state between runs in one index store, with distribution/build files owned separately by MYC-15, and keep in it no copy of the settings, no secret and nothing of another product | Changed | store |
| MYC-6.2 <!-- 7ead0660-13bf-4d0a-a181-ed81104b9fb3 --> | take the store's address from the setting `store.address` alone, with no address built in and no variable that overrides it | Changed | unit |
| MYC-6.3 <!-- 83603bd2-717e-4b02-ad3c-6638407c2edc --> | refuse a command with `store_unavailable` when the store cannot be reached, say so in `mycel info` without refusing it, and run grep in `mycel grep` without the store | Changed | store |
| MYC-6.4 <!-- 427116ee-f106-4a27-8fa4-d540c0bdc61f --> | hand the store's address and password to no program it starts | Changed | unit |
| MYC-6.5 <!-- 22227db0-4c6c-4f4f-9c6b-a0033a94ffbc --> | make the structure, both search indexes included, only in `mycel init`, and write no repository and no default row there | Changed | store |
| MYC-6.6 <!-- d8270b2a-d3e1-4923-81a4-a08ef3b7a84d --> | write a format number into the store, and bring an older format forward in `mycel init`, one format at a time, each step in one transaction | New | store |
| MYC-6.7 <!-- f287849b-f1bb-4df5-8ac5-6a4da6316b6a --> | refuse `mycel init` with `store_format` on a store with a newer format, and with `refused` on a database that holds tables that are not Mycel's or when a needed extension is missing, naming the reason | New | store |
| MYC-6.8 <!-- 0a7de3ad-4d33-469e-b7a9-1d5cc01b3e43 --> | hold the number of dimensions of a vector as part of the structure; when the settings name another number, change it only in `mycel init`, removing the vectors of the old size, and until then refuse `embed` with `store_format` and answer a search by wording alone | New | store |
| MYC-6.9 <!-- 0faa236b-444a-4b72-a032-b652e4a1a9e1 --> | write each change of the table above in one transaction, and let a command that only reads see one state of the store | Changed | store |
| MYC-6.10 <!-- 63c8fd4c-82dc-41ca-b62b-328ad9cee110 --> | let one pass at a time work on each repository location and one embed at a time work on a repository; passes on different locations, including clones of one repository, run side by side | Changed | store |
| MYC-6.11 <!-- 939b7468-241b-47ea-9cad-f9ae479b34d7 --> | never wait for another invocation: say at once that the work was not done and why | Kept | store |
| MYC-6.12 <!-- 674e48a2-ccf5-44e3-969f-759dffed9c0f --> | hold every lock in the store through the connection of the invocation that took it, so that it ends with the process | Kept | store |
| MYC-6.13 <!-- 700a986a-160b-4aa5-982c-4e0c592e47a0 --> | refuse with `busy` a `repos remove` for a repository on which a pass, embed, classification, summary operation or pinning/evidence mutation is at work, and every command except `info` and `grep` while `mycel init` changes the structure | New | store |
| MYC-6.14 <!-- c410ce4c-7f21-4ed2-9564-b0278d7893d0 --> | give each repository its own entry in the reply of a command over one or several, end with status 1 when any was not done as asked, and write the full reply in that case too | New | unit |
| MYC-6.15 <!-- 37e94571-8126-4d2b-920b-92e6d1747abe --> | leave rows whose repository the settings do not name, or name as switched off, out of every search, embed and pass, and delete them only on `repos remove` | Changed | store |
| MYC-6.16 <!-- 1c0c5212-bc9a-4923-a98f-d7f6848d4e6d --> | list in `mycel status --all` every repository name that has rows in the store, and say for each whether the settings know it | New | store |
| MYC-6.17 <!-- 807ceca9-1997-4ede-b9cf-cae11a750564 --> | read and write no table of version 1 | New | store |
| MYC-6.18 <!-- 29a24b88-2edf-4b38-ae7b-271740d8c9f0 --> | retain only MYC-16 owning-reference-protected evidence outside searchable located versions, capture/repin it atomically, and collect only unreferenced owner-repository blobs | New | store |
| MYC-6.19 <!-- 438ddec9-e61a-4f96-8cad-62ef6728e0a7 --> | create a unique index-generation UUID when initializing an empty store, preserve it through ordinary ingest and migrations, and report it in init/info/activity so a lost-store rebuild cannot impersonate old evidence | New | store |
| MYC-6.20 <!-- 514f9f27-f56a-4296-ba16-f72567b16e93 --> | implement nonblocking classification, summary, pinning and evidence-lease/removal locks with distinct advisory namespaces and exact invocation liveness; hold no pass lock during model calls | New | store |
| MYC-6.21 <!-- cd556fea-d33e-4baa-999e-bf60ee625640 --> | hold requirement and decision entities as chunks of kind `req` and `dec` in store format 3, bring a format 2 store forward in one step, report the format in `mycel info`, and never delete an entity row in collection | New | store |
| MYC-6.22 <!-- 92bc6b25-6f4d-404d-a139-9e0e5bf9fcb2 --> | reserve passes per configured clone location, allow capture on two clones of one repository concurrently, guard shared identity and evidence publication, and exclude repository removal while any location operation is live | New | store |
| MYC-6.23 <!-- b911eee1-ec41-46e1-886e-e81db83057e3 --> | persist stated Origin Links in the Index Store without writing a copy into source files or another product database, and provide no backup command because the owner backs up the shared local PostgreSQL | New | store |

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

```sh
mycel init                     # make the structure, or bring it to the format of the Build that runs
mycel status --all             # every repository, also names the settings no longer know
mycel repos remove old-cellar  # works for any name that has rows
```

```ts
interface InitReply {
  store: string;                                      // the address, which holds no secret
  format: { before: number | null; after: number };   // null: the database was empty
  dimensions: { before: number | null; after: number };
  indexGeneration: string;                            // UUID, new only for an empty store
  changed: boolean;                                   // false when nothing had to be done
  vectorsRemoved: number;                             // above 0 only when the number of dimensions changed
}

interface RemoveReply {
  repository: string;
  known: boolean;                                     // whether the settings name it
  removed: { documents: number; chunks: number; versions: number; vectors: number; edges: number;
    evidenceBlobs: number; evidenceManifests: number; drifts: number; verifications: number };
}

// RepositoryStatus of MYC-1 gains:
//   known: boolean;                                  // false: the settings no longer name this repository
//
// EmbedResult of MYC-3 gains, for each repository:
//   ran: boolean;                                    // false when another embed was at work on it
//   refused?: string;                                // the reason, when the embed was refused for it
```

## Known problems in version 1

- **It lived in another product's database.** Its tables stood among 92 of Arbol 1, at an address built into the code together with a user name and a password.
- **Every command changed the structure.** The statements that create tables and add columns ran in each process, the reporting commands included, and they created a repository row as well.
- **Nothing recorded which structure a database had.** A program of another version had no way to tell.
- **The index by wording could be missing without a sign.** A search tried to create it and went on without it when that failed.
- **Nothing was written together.** Each statement was committed by itself, so a failure left files half applied and marks half written.
- **A pass for one repository wrote to all.** Two such passes could clear and rewrite every stale mark at the same time.
- **Nothing kept two embeds apart.** No lock around an embed is named in the inventories, so two could send the same chunks (inferred, not seen happening).
- **Rows could only be removed with SQL.** A repository that left the settings kept its rows and kept answering.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/database.py#dsn`
- `mycel_deprecated_v1:mycel/database.py#connect`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema`
- `mycel_deprecated_v1:mycel/knowledge/store.py#detect`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#ensure_bm25_index`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embed_pending`
- `mycel_deprecated_v1:mycel/syncpass.py#_run_coalesced`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D25 <!-- cfad382a-4370-4b73-a176-d5700eea2928 --> | How does the password of the store reach Mycel? | The same two ways as the key of the embedding service: a Keychain item of Mycel's own, or a command of the owner's that prints it. The address in the settings file never holds it. A store on the same machine that asks for no password needs neither | Decided 8 October 2026 by the owner: the Keychain. The password comes from Mycel's Keychain item; no setting names a command for it |
| MYC-D26 <!-- 8aa46186-dd94-4206-b831-1a816f886fc3 --> | Is anything carried over from the index of version 1? | No. The new store is a new database and is filled from the files. Every chunk is embedded once more, which the new model requires anyway. Edges that were asserted with `mycel derive` and the summaries are lost and are made again by hand where they are wanted. The other choice is a one-time program that copies the asserted edges across; it would have to read Arbol 1's database, and the number of such edges is not known | Decided 8 October 2026 by the owner: no, and everything of version 1 is removed. Nothing is copied across |
| MYC-D27 <!-- 6f458876-ea7c-429f-b4bc-40fe16854f48 --> | What does a command report when it covers several repositories and only some could be done? | One entry for each repository, saying done, refused or not run, and the exit status 1 as soon as one was not done. The full reply is written in that case too, so the caller sees what did happen. The other choice is status 0 whenever at least one repository was done; a script that checks only the status would then miss a repository that was skipped | Decided 8 October 2026 by the owner: agreed. One entry for each repository, the status 1 as soon as one was not done, and the full reply in that case too |
| MYC-D55 <!-- 4aeb1b40-133a-4026-99b4-5138de847ce9 --> | Where is the copy of a stated Origin Link? | In the Index Store, backed up with the local PostgreSQL databases | Decided 19 October 2026 by the owner: Mycel and Arbol use separate databases on the local PostgreSQL and share one backup. Stated Origin Links are the only unique authored content in the Index Store; recovered links regenerate, declared links come from files and Arbol owns the chats |

## Named checks

Written by `scripts/name_checks.py` from the `proven` and `stated` Origin Links of the tests and a complete check report in which they passed. Each requirement keeps its kind in its Verified by cell and names here up to three of its passing checks: those of its own kind first, then those that rest on the fewest requirements. `mycel origins --repo mycel --path tests` lists every link. Do not edit this section by hand: run the script again.

| Requirement | Kind | Checks |
|---|---|---|
| `MYC-6.1` | store | `test_store_acceptance.ProductStoreTests.test_product_init_has_both_indexes_only_metadata_and_stable_generation` |
| `MYC-6.2` | unit | `test_database.DatabaseTests.test_hostname_resolution_preserves_all_explicit_ips_under_one_deadline`, `test_database.DatabaseTests.test_literal_ipv6_skips_dns_and_encoded_target_names_remain_separate_parameters`, `test_credentials.CredentialsTests.test_store_address_is_only_the_password_free_setting_not_parent_environment` and 8 more |
| `MYC-6.3` | store | `test_store_acceptance.ProductStoreTests.test_unreachable_target_refuses_init_but_info_and_plain_grep_remain_available`, `test_classify.FiniteClassifyStoreTests.test_public_dry_run_reaches_the_store_as_every_command_and_reads_only_its_password` |
| `MYC-6.4` | unit | `test_credentials.CredentialsTests.test_plain_grep_receives_neither_store_target_nor_parent_credentials`, `test_database.DatabaseTests.test_cancellation_immediately_after_environment_lock_preserves_original_parameters`, `test_database.DatabaseTests.test_context_failure_interrupt_and_normal_exit_all_close_connection` and 9 more |
| `MYC-6.5` | store | `test_store_acceptance.ProductStoreTests.test_compatible_init_and_read_guards_issue_no_ddl`, `test_store_acceptance.ProductStoreTests.test_exact_utf8_nul_bytes_projection_and_hash_guards_roundtrip`, `test_store_acceptance.EmptyProductStoreTests.test_empty_store_is_refused_by_read_and_created_only_by_explicit_product_init` and 1 more |
| `MYC-6.6` | store | `test_entities.EntityStoreTests.test_init_brings_a_format_2_store_forward_in_one_step_and_info_reports_the_format`, `test_store_acceptance.ProductStoreTests.test_migration_step_rolls_back_ddl_and_format_while_preserving_generation`, `test_verification_history.VerificationHistoryStoreTests.test_empty_and_valid_predecessors_migrate_preserving_record_evidence_and_generation` and 2 more |
| `MYC-6.7` | store | `test_store_acceptance.EmptyProductStoreTests.test_empty_store_is_refused_by_read_and_created_only_by_explicit_product_init`, `test_store_acceptance.ProductStoreTests.test_newer_and_foreign_stores_refuse_without_reading_foreign_or_v1_tables` |
| `MYC-6.8` | store | `test_search_store.SearchStoreTests.test_dimension_mismatch_discards_supplied_query_vector_and_answers_by_wording_without_writes`, `test_store_acceptance.ProductStoreTests.test_dimension_change_removes_only_vectors_retaining_complete_text_parts_and_failures` |
| `MYC-6.9` | store | `test_locks.LockStoreTests.test_atomic_change_rolls_back_all_rows_and_commits_complete_changes`, `test_locks.LockStoreTests.test_snapshot_keeps_first_committed_state_and_rejects_writes` |
| `MYC-6.10` | store | `test_repository_removal.RepositoryRemovalStoreTests.test_failure_after_cascading_deletion_rolls_back_every_feature_row_and_releases_guards`, `test_clone_locations.CloneStoreTests.test_two_public_passes_capture_concurrently_and_publish_both_clones`, `test_locks.LockStoreTests.test_pass_embed_and_distinct_repositories_follow_conflict_matrix` |
| `MYC-6.11` | store | `test_locks.LockStoreTests.test_allocator_guard_and_uncommitted_unique_conflict_refuse_without_waiting`, `test_locks.LockStoreTests.test_paid_model_interval_retains_operation_liveness_and_releases_pass_lock`, `test_clone_locations.CloneStoreTests.test_location_reservations_are_distinct_and_both_exclude_removal` and 2 more |
| `MYC-6.12` | store | `test_locks.LockStoreTests.test_exact_liveness_uses_full_bigint_session_start_and_not_other_lock_holders`, `test_locks.LockStoreTests.test_killed_owning_process_releases_every_lock_without_cleanup_files` |
| `MYC-6.13` | store | `test_repository_removal.RepositoryRemovalStoreTests.test_busy_foreign_dependant_blocks_edge_cascade_without_partial_removal`, `test_repository_removal.RepositoryRemovalStoreTests.test_every_active_operation_and_evidence_mutation_refuses_without_feature_changes`, `test_repository_removal.RepositoryRemovalStoreTests.test_live_lease_and_running_activity_prevent_removal_until_the_invocation_ends` and 2 more |
| `MYC-6.14` | unit | `test_diagnostics_cli.DiagnosticsCliTests.test_interrupted_removal_keeps_committed_result_and_never_starts_later_names`, `test_diagnostics_cli.DiagnosticsCliTests.test_mixed_and_entirely_refused_scopes_keep_exact_individual_results`, `test_diagnostics_cli.DiagnosticsCliTests.test_removal_connection_close_failure_keeps_all_acknowledged_member_counts` and 4 more |
| `MYC-6.15` | store | `test_repository_removal.RepositoryRemovalStoreTests.test_disabled_forgotten_and_receipt_only_repository_owners_are_removable`, `test_repository_status.RepositoryStatusStoreTests.test_all_lists_disabled_orphan_and_enabled_empty_without_requiring_available_folders` |
| `MYC-6.16` | store | `test_repository_status.RepositoryStatusStoreTests.test_all_lists_disabled_orphan_and_enabled_empty_without_requiring_available_folders` |
| `MYC-6.17` | store | `test_store_acceptance.ProductStoreTests.test_newer_and_foreign_stores_refuse_without_reading_foreign_or_v1_tables` |
| `MYC-6.18` | store | `test_repository_removal.RepositoryRemovalEvidenceStoreTests.test_removed_source_keeps_dependant_baseline_and_projects_missing_source_without_writing`, `test_repository_removal.RepositoryRemovalEvidenceStoreTests.test_repin_and_evidence_collection_roll_back_together_and_keep_protected_history`, `test_repository_removal.RepositoryRemovalStoreTests.test_removal_counts_complete_owned_state_and_preserves_files_and_foreign_rows` |
| `MYC-6.19` | store | `test_store_acceptance.ProductStoreTests.test_dimension_change_removes_only_vectors_retaining_complete_text_parts_and_failures`, `test_store_acceptance.ProductStoreTests.test_exact_utf8_nul_bytes_projection_and_hash_guards_roundtrip`, `test_store_acceptance.ProductStoreTests.test_migration_step_rolls_back_ddl_and_format_while_preserving_generation` and 4 more |
| `MYC-6.20` | store | `test_locks.LockStoreTests.test_allocator_guard_and_uncommitted_unique_conflict_refuse_without_waiting`, `test_locks.LockStoreTests.test_exact_liveness_uses_full_bigint_session_start_and_not_other_lock_holders`, `test_locks.LockStoreTests.test_killed_owning_process_releases_every_lock_without_cleanup_files` and 2 more |
| `MYC-6.21` | store | `test_entities.EntityStoreTests.test_init_brings_a_format_2_store_forward_in_one_step_and_info_reports_the_format`, `test_entities.EntityStoreTests.test_pass_publishes_entity_rows_keyed_by_uuid_and_keeps_them_through_edits_and_moves` |
| `MYC-6.22` | store | `test_justify.CloneAbsenceStoreTests.test_absence_guard_compares_only_the_selected_clones_retained_witnesses`, `test_clone_locations.CloneStoreTests.test_location_reservations_are_distinct_and_both_exclude_removal`, `test_clone_locations.CloneStoreTests.test_two_public_passes_capture_concurrently_and_publish_both_clones` and 1 more |
| `MYC-6.23` | store | `test_justify.JustifyStoreTests.test_atomic_stated_link_and_verification_persist_only_in_index_store` |
