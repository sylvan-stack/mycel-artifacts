---
role: authored
---
# Version 1 as installed: observations of 6 to 8 October 2026

What the installed Mycel 1 did on the owner's machine while its corpus was being cleaned up. The three inventories beside this file say what the source does; this file says what was seen running. Every item names the day it was seen. It is evidence for the [specifications](../specs/README.md).

Nothing here was provoked on purpose: the items were met while searching, checking status, switching a repository off and removing its rows.

## The installation

- `~/bin/mycel` and `~/bin/better-grep`, each a single program of about 80 MB built on 23 September 2026. `mycel --version` prints `mycel 0.1.0`.
- The index lived in a PostgreSQL 17 with ParadeDB 0.24.1, in a container named `arbol-postgres`, in a database named `arbol`. Mycel's ten `kn_` tables shared that database with 92 tables of Arbol 1. The database took 9.8 GB; `kn_chunks` took 218 MB for 24,157 rows.
- `mycel --help` listed 17 commands. Seven belonged to workflows that were already retired.
- The service on port 7331 that embedded text on the machine was a service of Arbol 1. The folder for its model held no model. Every repository used the external embedding service.

## Commands

| Day | Seen |
|---|---|
| 6 October | `mycel sync` accepts one option, `--no-embed`. No option names a repository |
| 6 October | `mycel embed` accepts no option at all. The runbook of the day described two options for it that neither the program nor its source had |
| 6 October | A search reply carries `schema_version: 2` with the keys `schema_version`, `repo`, `overlay`, `results`, `dense`, `bm25`, `timings`, `freshness`, `transport`. The runbook said version 1 |
| 6 October | A search of the usual kind in a repository whose files had changed replied with `freshness.refreshed: true` after about one second. The same search with `--only docs` replied `checked: false` and returned three documents that had been deleted from disk that day |
| 7 October | From a folder that belongs to no repository, a search without `--repo` reported `repo: Arbol` |
| 7 October | `status`, `drifts` and `raptor` fall back to the repository `Arbol` when none is named |

## Counts

| Day | Seen |
|---|---|
| 6 October | `mycel status --repo mycel` reported 76 documents while 30 files existed; the number included documents no longer on disk |
| 7 October | `embedder.pending` was 13,707 for every repository asked about. After the repository that held 11,973 of them was switched off, it stayed 13,707 |
| 7 October | A search in a corpus of documents only always showed `dense: 0`, because that number counts code chunks. It was first read as a failure of the search by meaning, which it was not |

Chunks by repository on 7 October, read from the index:

| Repository | Present | With a vector | Without | No longer on disk |
|---|---|---|---|---|
| `arbol` (the deprecated Arbol 1) | 16,851 | 4,878 | 11,973 | 4,803 |
| `core` | 1,997 | 379 | 1,618 | 2 |
| `mycel` | 162 | 46 | 116 | 334 |
| `blueprint`, `infer` | 4 each | 4 each | 0 | 0 |

## Switching a repository off, and removing it

- 7 October: `enabled = false` for a repository stopped its ingest and its embedding. Its 16,851 chunks kept answering searches.
- 7 October: no command removes a repository's rows. They were deleted with SQL, in this order because of the references between the tables: drifts, edges, chunks, documents. 21,654 chunk rows of one repository and 334 rows of another that were no longer on disk went that way. The table kept its size on disk afterwards.
- 7 October: rows of documents and sections that left the disk were never removed by the tool. A fifth of the rows of the largest repository were of that kind.
- 7 October: the table of repositories held 38 rows, among them both `arbol` and `Arbol`.

## Checkouts

- 7 October: the history of one working checkout that was configured as a code corpus showed 61 resets to the tip of its remote's default branch between 30 September and 1 October, about one every eleven minutes while Arbol 1's resident service ran its passes. None of them moved the branch, because nothing local was ahead of the remote at the time. The source says why they happened: a full pass fetches the default branch and resets the checkout to it whenever the checkout has no uncommitted or untracked files, whatever branch is checked out.

## The settings file

- 8 October: the owner's `~/.mycel/config.toml`, written for version 1, held `profile` in 11 of its 35 repository entries, one `[providers]` table and `url` in two organizations. It held no `[database]` table. The keys were counted without printing a value.

## Files the program reads from this corpus

- 6 October: `mycel raptor` reads two prompt files from `system-instructions/` in this corpus. Deleting the folder as part of a clean-up would have stopped that command; the folder was restored.

## Guides against the program

On 6 October the guides of this corpus described these things that the program did not do, or did differently: two options of `embed`; a reply version; a command for listing work trees that had been retired; summaries of pending chunks per branch. They were corrected the same day. The source inventories list further places where comments in the code state rules the code does not follow.
