---
role: authored
spec: MYC-9
status: accepted
---
# Mycel · 09 The code overview

Some questions are about the shape of the code and not about one function: which services exist in the billing part, what is in this folder. The code overview answers them. For each directory of a repository's code it lists the files with the classes, methods and functions in each, made from the chunks Mycel already holds and with no model. This specification fixes what the overview contains, when it is made, where it is kept and how it is found. It matters because version 1 wrote the overview as a file into the repository's document folder, which changed a checkout nobody had touched, and it listed no file that held only loose code.

The Glossary has it under [Code Map](../../arbol/GLOSSARY.md#code-map).

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: what a section of the overview lists, when it is made, where it is kept, how it takes part in a search, how it is read.

Not covered: how code is split into chunks and named ([MYC-1](01-corpora-and-ingest.md#splitting-code)); summaries, which a model writes ([MYC-8](08-summaries.md)).

## Behaviour

### What the overview lists

Observed in version 1: one Markdown file for each repository, with one section for each directory of its code. A section had one line per file: the file's classes, each with up to eight of its methods, and up to eight of its other named symbols; what did not fit was shown as a count. A file appeared only through a named symbol. A file that held only loose code, or that was not parsed at all, such as a shell script, a property list or a Swift file, was not in the overview.

The same lines are kept, and every indexed code file on disk has one, including an empty file or a file with no named symbol. Such a file is listed by its name alone. Directories and files are ordered by their relative path, compared as Unicode code points; classes by name, with source position breaking a tie; methods and other symbols by source position, then name. This decides which eight are shown. Counts include every named class, method and other declaration, including those omitted from the text; module runs are not named symbols.

```markdown
## src/net

- **client.py** — Client (open, close, get, head, post, put, patch, delete, +3 more); connect
- **retry.py** — RetryPolicy (allow, next_pause, reset); backoff, jitter
- **run.sh**
```

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/code_map.py#build_markdown`

### When it is made

Observed in version 1: the pass over all repositories built the whole text for each of them every time and wrote the file when the text differed from the one on disk. The pass that a search starts for one repository did not. A new overview was read into the index as a document only by the pass after the one that wrote it.

Every pass reconciles the overview as its last step for a repository. It computes each directory's rendered outline from the stored on-disk code file and chunk records, compares that complete text with the stored section, and changes only sections whose rendered text differs. Added, removed, moved or renamed files and symbols, a change of declaration kind or class membership, and a reordering that changes the displayed symbols all participate. An edit inside a function that leaves its displayed outline unchanged changes no overview section and invalidates no vector. An empty directory's section is deleted.

Updated sections are published in one repository transaction, after the pass's applied code changes, and are pending for embedding like any changed chunk (MYC-3). A stopped or partial pass reconciles only the code state it successfully applied; it never publishes an outline inferred from unapplied scan results. The next pass can rebuild a missing overview without treating unchanged files as new.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/code_map.py#write_map`
- `mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked`
- `mycel_deprecated_v1:mycel/syncpass.py#run_repo_pass`

### Where it is kept

Observed in version 1: the file was `generated/code-map.md` in the repository's document folder. Mycel created that folder, and the document folder itself when there was none. The file declared itself `generated`, so it was never marked stale and was left out of summaries. Each section ended with a Source Ref to every file it listed; through these, every code file was shown in search results as documented in the overview.

Decided: the overview is kept in the index store and nowhere else ([MYC-D32](#decisions)). Each section is a chunk of its repository with the origin `overview`. Its place is `overview`, with the directory as its name: `cellar:overview#src/net`. Mycel writes into no folder that it reads (MYC-0, State), so a pass leaves every checkout as it found it.

- An overview section is never stale and opens no Drift: the pass that changes what it lists makes it again.
- It has no edges. It repeats names and says nothing about them, so no code result is shown as documented in the overview. A ref to an overview section in a file is reported as a fault, as for a summary (MYC-8.23).
- It comes from no file and has no location. For a search and for `mycel read` it counts as on disk. It is deleted when its directory holds no code file any more, and with its repository.
- It is left out of summaries (MYC-8.1).
- It describes what is on disk. What a branch or a stash holds is not in it.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/code_map.py#write_map`
- `mycel_deprecated_v1:mycel/knowledge/code_map.py#build_markdown`

### Finding and reading it

Observed in version 1: the file was a document like any other. Its sections competed with code in a search under the rules for documents, and it was read by opening the file.

In a search that includes documents, the overview sections of the searched repository compete as documents do, under the margin and the limit of MYC-4.13. A search for code only leaves them out. A result has the origin `overview` and names no file. The text is read with `mycel read` ([MYC-11](11-reading-a-chunk.md)), and `mycel overview` prints the stored sections of a repository, or of one directory. This reporting command runs no pass, generates no section and writes nothing. A valid directory with no indexed section returns an empty `sections` list and status 0. `--dir` is a normalized relative directory inside the code root, with `.` naming the root; an absolute path or a path escaping the root is `invalid_input`.

## Requirements

| ID | Mycel must… | Origin | Verified by |
|---|---|---|---|
| MYC-9.1 | hold for every directory of a repository's code corpus on disk one overview section that lists each of its code files | Changed | store |
| MYC-9.2 | give for a file its classes, each with up to eight methods, and up to eight other named symbols, classes in the order of their names and methods and other symbols in the order of the file, with a count of what did not fit; and list a file without a named symbol by its name alone | Changed | unit |
| MYC-9.3 | make the overview from stored on-disk code file and chunk records alone, with no model and no network | Kept | unit |
| MYC-9.4 | reconcile the rendered outline as the last step of a pass, updating exactly the directory sections whose displayed text changed, including changes of symbol order, declaration kind, class membership and file path, and leave unchanged text and its embedding intact | Changed | store |
| MYC-9.5 | keep the overview in the index store as chunks with the origin `overview`, and write no file for it | Changed | store |
| MYC-9.6 | never mark an overview section stale, open no Drift for it, hold no edge from or to it, and delete it when its directory holds no code file any more | Changed | store |
| MYC-9.7 | embed an overview section by the rules of MYC-3 | Kept | store |
| MYC-9.8 | let the overview sections of the searched repository compete in a search as documents do, leave them out of a search for code only, and return one with the origin `overview` and without a file | Kept | store |
| MYC-9.9 | print on request the overview sections of a repository, or of one directory of it | New | store |
| MYC-9.10 | not show a code result as documented in the overview | Dropped | store |
| MYC-9.11 | list every indexed code file, including empty files, in deterministic path/name/source-position order, and count all named declarations whether displayed or omitted | New | unit |
| MYC-9.12 | publish overview changes atomically from the code state the pass applied, delete empty directory sections and rebuild missing sections on a later pass without rereading unchanged files | New | store |
| MYC-9.13 | have `overview` report only stored sections without a pass or writes, return an empty list normally for a valid absent directory, and refuse absolute or escaping `--dir` paths | New | unit |

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

```sh
mycel overview --repo cellar                 # every directory
mycel overview --repo cellar --dir src/net   # one
```

```ts
interface OverviewReply {
  repository: string;
  sections: Array<{
    directory: string;                 // relative to the code folder; "." for the folder itself
    files: number;
    symbols: number;
    text: string;                      // the section as Markdown, as it is embedded
  }>;
}

// SearchResult of MYC-4 gains:
//   origin: also "overview"
```

## Known problems in version 1

- **A pass wrote into the document folder.** The overview appeared there as a changed file after every change to the code, in a checkout nobody had touched, and Mycel created folders for it.
- **Files without a named symbol were missing.** Shell scripts, property lists and Swift files never appeared, and neither did a file that held only loose code.
- **Only the pass over all repositories made it.** That pass also reset checkouts ([MYC-1](01-corpora-and-ingest.md#the-pass)), so the safe way of bringing one repository up to date left its overview behind.
- **It was searchable one pass late.** The pass that wrote the file did not read it.
- **The whole text was built on every pass,** whether or not any code had changed.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/code_map.py#build_markdown`
- `mycel_deprecated_v1:mycel/knowledge/code_map.py#write_map`
- `mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D32 | Is the code overview a file in the repository's document folder, or is it kept in the index only? | In the index only. A search finds it and `mycel overview` prints it, and Mycel never writes into a folder it reads. Version 1 wrote the file `generated/code-map.md`: it can be opened in an editor and is kept by git, but every change to the code then leaves a changed file in the documents' checkout that somebody has to commit or ignore | Decided 8 October 2026 by the owner: resolved; keep the code overview in the index only, searchable and printable with `mycel overview`, without writing a file in a checkout |
