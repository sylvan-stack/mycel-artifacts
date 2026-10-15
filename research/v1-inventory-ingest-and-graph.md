---
role: derived
---
# v1 Mycel inventory: ingest, chunking, identity and the knowledge graph

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py`
- `mycel_deprecated_v1:mycel/repo_identity.py`
- `mycel_deprecated_v1:mycel/syncpass.py`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py`
- `mycel_deprecated_v1:mycel/database.py`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py`
- `mycel_deprecated_v1:mycel/knowledge/fs.py`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py`
- `mycel_deprecated_v1:mycel/cli.py`
- `mycel_deprecated_v1:mycel/knowledge/code_map.py`

What Mycel version 1 does, read from the deprecated source on 7 October 2026. It is evidence for the [specifications](../specs/README.md), not a description of Mycel 2. Historical evidence locators name the frozen source as `mycel_deprecated_v1:`. They are ordinary citations outside Source Ref declarations, because deprecated repositories are not indexed and Source Refs may target only enabled repositories. The scripts behind the runs marked **(probe)** and **(stub run)** are in [`v1-probes-2026-10-07/`](v1-probes-2026-10-07/README.md).

Source: `~/repos/sylvan-stack/mycel_deprecated_v1` at commit `b3125d0` (working tree clean). Files read completely: `mycel/knowledge/store.py` (1171 lines), `chunker.py` (190), `code_chunker.py` (251), `fs.py` (120), `code_map.py` (99). Read in part, only where the five files depend on them: `mycel/repo_identity.py` (all), `mycel/locations.py` (all), `mycel/knowledge/__init__.py` (all), `mycel/syncpass.py` (lines 100-116 and 120-340), `mycel/database.py` (60-86), `mycel/knowledge/raptor.py` (60-120, 380-405), `mycel/knowledge/embedder.py` (306-330), `mycel/cli.py` (160-210). Callers were located with text searches over `mycel/` and `tests/`.

How to read the evidence markers:

- No marker: read from the code at the cited lines. No database was contacted and the `mycel` command was not run.
- **(probe)**: additionally confirmed by executing the pure function from the frozen file on a fictional input (`chunker.py` and `code_chunker.py` only, loaded by path, bytecode writing disabled, tree-sitter from the repository's existing `.venv`).
- **(stub run)**: confirmed by executing the real store functions against an in-memory stand-in for the connection that applies the SQL statements as they are written. This checks the Python control flow, not PostgreSQL.
- **inferred**: follows from the code read, but is a consequence I derived, not a line I can point at.

Two facts used throughout: every connection is opened with `autocommit=True` and `row_factory=dict_row` (database.py:77), and every store function takes the caller's `conn` and never commits or opens a transaction itself, except `ensure_schema` (store.py:200).

## 1. Storage schema

All tables are created by one string constant, `DDL` (store.py:38-179), executed by `ensure_schema`. Table names are unqualified, so they land in the connection's current schema. Every id is a 26-character ULID in Crockford base32 built from `now_ms() << 80` plus 80 random bits (store.py:22-35). Every timestamp column is epoch milliseconds (`bigint`).

**`kn_documents`** (store.py:39-42, 113-114): one row per ingested file, plus one synthetic row per repository for RAPTOR.

| Column | Type / constraint | Meaning observed |
|---|---|---|
| `id` | `text PRIMARY KEY` | ULID |
| `path` | `text NOT NULL` | Path relative to the corpus root (Markdown) or the code root (code); `synthetic/raptor` for the summary document (raptor.py:34) |
| `content_hash` | `text NOT NULL` | SHA-256 hex of the whole file text |
| `source_type` | `text NOT NULL DEFAULT 'doc'` | `'doc'`, `'code'`, `'summary'` |
| `state` | `text NOT NULL DEFAULT 'present'` | `'present'`, `'orphaned'` |
| `first_seen`, `last_seen` | `bigint NOT NULL` | ms |
| `last_run` | `text` | Ingest run id for Markdown documents; `NULL` for code and summary documents |
| `repo` | `text NOT NULL DEFAULT 'Arbol'` | Repository key; default reset to `'arbol'` by `ensure_schema` (store.py:204) |
| `meta` | `jsonb NOT NULL DEFAULT '{}'` | Parsed frontmatter for Markdown documents |

Indexes: `kn_documents_repo (repo)` (store.py:117); unique partial index `kn_documents_repo_path_present ON (repo, path) WHERE state = 'present'` (store.py:122-123). The older `kn_documents_path_present` index is dropped on every DDL run (store.py:121). The unique index does not include `source_type`.

**`kn_chunks`** (store.py:48-55, 95-97, 102-105, 115-116).

| Column | Type / constraint | Meaning observed |
|---|---|---|
| `id` | `text PRIMARY KEY` | ULID |
| `document_id` | `text NOT NULL REFERENCES kn_documents(id)` | No `ON DELETE` action |
| `natural_key` | `text NOT NULL` | Markdown: heading path. Code: `relpath#symbol`. Summary: `raptor/L{tier}/{id}` (raptor.py:113). Not unique |
| `prev_natural_key` | `text` | Old key when the last reconcile decided `renamed`, otherwise `NULL` |
| `ordinal` | `int NOT NULL` | Position within the document, from 0 |
| `level` | `int NOT NULL` | Markdown heading depth 1-6, 0 for the preamble; 0 for code and summaries |
| `parent_key` | `text` | Natural key of the enclosing heading; `NULL` at top level and for code |
| `role` | `text NOT NULL DEFAULT 'unclassified'` | `'unclassified'`, `'authored'`, `'derived'` |
| `title` | `text` | Heading text; `''` for the preamble; `NULL` for code |
| `raw_text` | `text NOT NULL` | Chunk text |
| `content_hash` | `text NOT NULL` | Markdown: hash of the normalised body. Code and summary: hash of the raw text |
| `title_hash` | `text` | Markdown: hash of the normalised title, `''` when there is no title |
| `state` | `text NOT NULL DEFAULT 'present'` | `'present'`, `'orphaned'` (Markdown), `'absent'` (code) |
| `last_status` | `text` | Last identity decision (Markdown only) |
| `stale` | `boolean NOT NULL DEFAULT false` | Set by `detect` |
| `stale_because` | `text` | One reason string |
| `first_seen`, `last_seen` | `bigint NOT NULL` | ms |
| `last_run` | `text` | Ingest run id (Markdown only) |
| `embedding` | `public.vector(1024)` | Nullable; `NULL` means "to embed" |
| `origin` | `text NOT NULL DEFAULT 'corpus'` | `'corpus'`, `'code'`, `'summary'` |
| `tier` | `int NOT NULL DEFAULT 0` | RAPTOR level; 0 for leaves |
| `lang`, `symbol_kind` | `text` | Code only |
| `line_start`, `line_end` | `int` | Code only, 1-based inclusive |
| `repo` | `text NOT NULL DEFAULT 'Arbol'` | Denormalised copy of the document's repository; default reset to `'arbol'` (store.py:205) |
| `meta` | `jsonb NOT NULL DEFAULT '{}'` | See section 6 |

Indexes: `kn_chunks_doc (document_id)` (store.py:56); `kn_chunks_embedding USING hnsw (embedding public.vector_cosine_ops)` (store.py:98); `kn_chunks_repo (repo)` (store.py:118). A fourth index, `kn_chunks_bm25 USING bm25 (id, raw_text, natural_key) WITH (key_field='id')`, is created outside the DDL by `embedder.ensure_bm25_index` and silently skipped when the extension is missing (embedder.py:313-322). The DDL runs `CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public` (store.py:94).

**`kn_derivations`** (store.py:58-64): `id text PRIMARY KEY`, `parent_id text NOT NULL` (no foreign key; holds a chunk id or a document id), `child_id text NOT NULL REFERENCES kn_chunks(id)`, `kind text NOT NULL DEFAULT 'asserted'`, `policy text NOT NULL DEFAULT 'review'`, `hash_at_gen text`, `created_at bigint NOT NULL`, `UNIQUE (parent_id, child_id)`. Indexes `kn_derivations_child (child_id)`, `kn_derivations_parent (parent_id)`.

**`kn_identity_log`** (store.py:66-68): `run_id text NOT NULL`, `ts bigint NOT NULL`, `document_id text`, `chunk_id text`, `decision text NOT NULL`, `old_key text`, `new_key text`. No primary key, no index, no foreign key.

**`kn_ingest_runs`** (store.py:70-71): `id text PRIMARY KEY`, `ts bigint NOT NULL`, `corpus text NOT NULL` (the corpus path as a string), `summary jsonb NOT NULL` (the counts of the run).

**`kn_drifts`** (store.py:73-77): `id text PRIMARY KEY`, `chunk_id text NOT NULL REFERENCES kn_chunks(id)`, `source_id text`, `source_label text`, `reason text`, `opened_at bigint NOT NULL`, `status text NOT NULL DEFAULT 'open'`, `closed_at bigint`. Index `kn_drifts_open ON (chunk_id) WHERE status = 'open'`; the index is not unique.

**`kn_drift_sources`** (store.py:83-87): `drift_id text NOT NULL REFERENCES kn_drifts(id) ON DELETE CASCADE`, `source_id text`, `source_label text`, `reason text`, `PRIMARY KEY (drift_id, source_id)`. Index `kn_drift_sources_drift (drift_id)`.

**`kn_repos`** (store.py:129-149): `name text PRIMARY KEY`, `mycel_enabled boolean NOT NULL DEFAULT false`, `embedder_profile text NOT NULL DEFAULT 'voyage'`, `created_at bigint NOT NULL`, `code_subdirs jsonb` (array of relative paths; `NULL` = whole tree), `code_root text`. Two further columns are added outside the DDL: `artifact_root TEXT` (store.py:1063, 1093, 1096) and `last_sync_ms BIGINT` (syncpass.py:143).

**`kn_overlays`** (store.py:157-166): `name text PRIMARY KEY`, `base_repo text NOT NULL`, `branch text NOT NULL`, `worktree_path text NOT NULL`, `deleted_paths jsonb NOT NULL DEFAULT '[]'`, `merged boolean NOT NULL DEFAULT false`, `created_at bigint NOT NULL`, `last_sync bigint`, `UNIQUE (base_repo, branch)`.

**`kn_activity`** (store.py:174-178): `id text PRIMARY KEY`, `ts bigint NOT NULL`, `kind text NOT NULL`, `repo text`, `actor text NOT NULL DEFAULT 'cli'`, `summary jsonb NOT NULL DEFAULT '{}'`, `duration_ms bigint`, `error text`. Index `kn_activity_ts (ts DESC)`. Written by `log_activity`, which swallows every exception (store.py:1144-1151); read by `list_activity`, which clamps `limit` to 1..500 (store.py:1170).

**Migrations and schema helpers.**

- `ensure_schema` runs once per process, guarded by a module-level flag and a `threading.Lock` (store.py:182-206). Inside one transaction it executes `DDL`, takes `LOCK TABLE kn_documents, kn_chunks, kn_repos IN SHARE ROW EXCLUSIVE MODE`, calls `migrate_arbol`, then sets the `repo` column default to `'arbol'` on `kn_documents` and `kn_chunks`.
- Every later column is added with `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` inside `DDL`; there is no version table.
- The DDL seeds data: it inserts a `kn_repos` row `('arbol', true, 'voyage', now)` when no row named `'Arbol'` exists (store.py:134-137), and sets `code_subdirs` to `["daemons","drivers","renderer/apps","cli","tests"]` for `name = 'arbol'` whenever that column is `NULL` (store.py:142-143).
- `migrate_arbol` (repo_identity.py:26-66) folds the legacy namespace `'Arbol'` (and `'Arbol@...'`) into `'arbol'`: it raises `ValueError` when the two namespaces hold a present document at the same path with a different hash or source type, or overlay rows for the same branch that differ; otherwise it marks the `'arbol'` duplicate documents `orphaned` and their chunks `absent`, rewrites `repo` on documents and chunks, merges `kn_overlays` rows, and renames or deletes the `'Arbol'` row in `kn_repos`.
- `list_repo_flags` and `set_repo_flags` execute `ALTER TABLE kn_repos ADD COLUMN IF NOT EXISTS artifact_root TEXT` on every call (store.py:1063, 1093, 1096).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ulid`
- `mycel_deprecated_v1:mycel/knowledge/store.py#now_ms`
- `mycel_deprecated_v1:mycel/knowledge/store.py#list_repo_flags`
- `mycel_deprecated_v1:mycel/knowledge/store.py#set_repo_flags`
- `mycel_deprecated_v1:mycel/knowledge/store.py#log_activity`
- `mycel_deprecated_v1:mycel/knowledge/store.py#list_activity`
- `mycel_deprecated_v1:mycel/repo_identity.py#migrate_arbol`
- `mycel_deprecated_v1:mycel/syncpass.py#_ensure_last_sync_col`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#ensure_bm25_index`
- `mycel_deprecated_v1:mycel/database.py#connect`

## 2. Scan

There are two independent scans: a Markdown scan of the Artifact Corpus (`ingest`) and a code scan of the code root (`ingest_code`). They share no code.

**Markdown scan** (`_scan_corpus`, store.py:211-221).

- Included: every path matched by `Path(corpus).rglob("*.md")`, sorted.
- Excluded: a path is skipped when `".git" in md.parts` (store.py:215). That is the only exclusion. `md.parts` are the parts of the full path, including the corpus root's own ancestors.
- No other directory is ignored (hidden directories, `node_modules` and the like are scanned), no other extension is accepted (`.markdown`, `.mdx`, `.txt` are not), and there is no size limit.
- Each file is read with `read_text(encoding="utf-8", errors="replace")`, then hashed, chunked and frontmatter-parsed. This happens for every file on every ingest, before any comparison with stored state.
- Whole-file hash: `sha(text)` = SHA-256 hex digest of the text re-encoded as UTF-8, with no normalisation (chunker.py:123-124). Inferred from Python text-mode reading: line endings are translated before hashing, so a CRLF and an LF copy hash the same.
- The stored path is `str(md.relative_to(corpus))`.
- `source_type` is not set by the insert, so the column default `'doc'` applies (store.py:277).

**Skipping unchanged Markdown files** (store.py:260-273). A document is skipped when a present stored document with `source_type='doc'` and the same `repo` and `path` has `content_hash` equal to the new whole-file hash. A skipped document gets no row update and no identity-log rows; `docs_skipped` is incremented. One thing still happens for it: chunks of that document whose `meta` has the key `unresolved_sources` have their Source Refs resolved again (section 7).

**Code scan** (`_scan_code`, store.py:803-829, and `ingest_code`, store.py:832-928).

- Roots: `base/sub` for each entry of `subdirs`; `None` or an empty list means the whole tree (`[""]`, store.py:859). A root that does not exist is skipped.
- Included extensions, matched with `name.endswith` (store.py:786-787):

```
.py .svelte .ts .tsx .mts .cts .js .jsx .mjs .cjs .sh .bash .plist .plist.in .swift
```

- Excluded: a file is skipped when any part of its path relative to `base` is in this set, or ends with `.egg-info` (store.py:788-790, 822-824):

```
.git .bare node_modules .venv venv __pycache__ build dist .svelte-kit releases
.mypy_cache .pytest_cache .ruff_cache site-packages .arbol .arco coverage .next
.turbo storybook-static
```

- The match is on directory names anywhere in the relative path, so a source directory named `build`, `dist`, `releases` or `coverage` is excluded at any depth.
- No size limit, no `.gitignore` handling. A file whose read raises any exception is skipped silently (store.py:827-828).
- Whole-file hash: `sha(source)`, same function as for Markdown.
- Stored path: relative to `base`. `source_type='code'` (store.py:880-882). `last_run` is `NULL`.
- `lang` is derived from the extension by `_lang_of` (store.py:793-800): `.py` → `python`; `.svelte` → `svelte`; `.ts .tsx .mts .cts` → `typescript`; everything else → `javascript`.

**Skipping unchanged code files** (store.py:868-871). A file is skipped with zero writes when a present `source_type='code'` document with the same `repo` and `path` has `content_hash == sha(source)`.

**Removed files.** Markdown: stored present documents whose path is no longer scanned are set to `state='orphaned'` and their present chunks to `state='orphaned', last_status='orphaned'` (store.py:353-358). Code: present code documents of the repository whose path was not scanned are set to `state='orphaned'` and their present chunks to `state='absent'` (store.py:917-925). Neither scan has a guard against an empty result: a scan that returns nothing retires every document of the repository (inferred for Markdown; the comment at store.py:817-821 records that it happened for code).

**`source_type` values.** `'doc'` (column default, Markdown ingest), `'code'` (`ingest_code`; default argument of `track_source`), `'summary'` (the synthetic RAPTOR document, raptor.py:77-78). `track_source` accepts any string.

**Callers that trigger a scan.**

- `refresh(conn, corpus, repo, code_root)` (store.py:658-687): `ingest`, then, when `code_root` is given, `track_source` for every present code document of the repository whose file exists under `code_root`, then `detect`. It returns the ingest counts, the detect counts and an `items` list.
- The sync pass calls, per enabled repository and in this order: `refresh` (only when the artifact root is a directory; `code_root` is passed when the code root is a directory), an optional git mirror refresh, `ingest_code` (only when the code root is a directory), `code_map.write_map` (full pass only) (syncpass.py:244-275).
- `fs.write`, `fs.rename` and `fs.remove` change a file under the corpus root, then call `store.ingest` for the whole corpus and `store.detect` (fs.py:62-120). `fs` confines paths with `_safe`, which resolves the path and raises `ValueError("path escapes corpus root: ...")` when the result is outside the root (fs.py:25-32). `fs.tree` lists every non-hidden entry of any file type, directories first, by lower-cased name (fs.py:35-51). `fs.remove` deletes a file with `unlink` or a directory with `shutil.rmtree` (fs.py:115-118).
- `track_source(conn, path, source_type='code', read_path=None)` (store.py:386-405) reads one file, hashes it and writes the hash to a `kn_documents` row found by `path=%s AND source_type=%s ORDER BY (state='present') DESC, last_seen DESC`; it inserts a new row when none exists. The lookup has no `repo` predicate and the insert sets no `repo`.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#_scan_corpus`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_scan_code`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_lang_of`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code`
- `mycel_deprecated_v1:mycel/knowledge/store.py#track_source`
- `mycel_deprecated_v1:mycel/knowledge/store.py#refresh`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#sha`
- `mycel_deprecated_v1:mycel/knowledge/fs.py#_safe`
- `mycel_deprecated_v1:mycel/knowledge/fs.py#tree`
- `mycel_deprecated_v1:mycel/knowledge/fs.py#write`
- `mycel_deprecated_v1:mycel/knowledge/fs.py#rename`
- `mycel_deprecated_v1:mycel/knowledge/fs.py#remove`
- `mycel_deprecated_v1:mycel/knowledge/fs.py#_after_mutation`
- `mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked`

## 3. Markdown chunking

`chunk_markdown(text)` is a pure function (chunker.py:131-190). It receives the whole file text, frontmatter included.

**Regular expressions** (chunker.py:19-23, 86-87).

```
HEADING_RE     ^(#{1,6})\s+(.*?)\s*#*\s*$
FENCE_RE       ^\s*(```+|~~~+)
_FM_LINE       ^([A-Za-z_-]+)\s*:\s*(.+?)\s*$
_FM_LIST_HEAD  ^([A-Za-z_-]+)\s*:\s*$
_FM_LIST_ITEM  ^\s*-\s+(\S.*?)\s*$
_SOURCES_BLOCK <!--\s*sources:\s*(.*?)-->        flags: DOTALL, IGNORECASE
_SOURCE_REF    ^[\w.@-]+:\S.*$
```

**Splitting.**

- Lines come from `text.splitlines()`. Only ATX headings are recognised; a Setext heading is body text **(probe)**.
- A heading needs 1 to 6 `#` at column 0 followed by whitespace. Not headings **(probe)**: `#NoSpace`, seven `#`, a `#` line indented by spaces, a bare `#`. `# ` followed by nothing is a heading with an empty title.
- The title is group 2, stripped. Trailing `#` characters are removed even without a space before them: the line `# C#` yields the title `C` **(probe)**.
- Fences: a line matching `FENCE_RE` opens a fence and records the first three characters of the marker; while in a fence, a line that matches `FENCE_RE` and whose stripped text starts with the recorded three characters closes it (chunker.py:141-148). Any indentation is accepted. A closing line may carry an info string, so a second opening marker of the same kind inside a fence closes it **(probe)**. An unclosed fence swallows the rest of the file **(probe)**.
- Each heading owns its heading line and the lines down to the next heading of any level. Subsections are separate chunks and are not part of the parent's text.
- Preamble: when the text before the first heading is not blank, it becomes one chunk with `natural_key = "(preamble)"`, `level = 0`, `title = ""`, `parent = None` (chunker.py:156-158, 168). A file without headings is one preamble chunk; an empty or blank file yields no chunks **(probe)**.
- Frontmatter is not removed before chunking: a file with frontmatter always has it at the start of its preamble chunk **(probe)**.

**Natural key and structure.**

- A stack of `(level, title)` is kept. For a heading, entries with level `>=` the new level are popped; `parent` is the remaining titles joined by `" > "` (or `None`); the heading is pushed; `natural_key` is all stack titles joined by `" > "` (chunker.py:171-175). Skipped levels are joined as they come **(probe)**: an H4 directly under an H2 gives `H1 > H2 > H4`.
- `ordinal` counts chunks from 0 in file order, the preamble included.
- `level` is the number of `#`.
- `raw_text` is the chunk's lines (heading line included) joined by `"\n"` with trailing `"\n"` removed (chunker.py:177).
- `role` is always `"unclassified"` in the chunker output (chunker.py:184).
- There is no size cap and no splitting of long sections.

**Hashes** (chunker.py:118-128, 186-187).

- `norm(text)` = Unicode NFKC, then every whitespace run replaced by one space, then stripped.
- `content_hash` = SHA-256 of `norm(body)`, where `body` is the chunk without its heading line (for the preamble: the whole chunk). Whitespace-only edits and NFKC-equivalent edits do not change it **(probe)**. A section with no body text hashes to the SHA-256 of the empty string **(probe)**.
- `title_hash` = SHA-256 of `norm(title)`, or `""` when the title is empty.
- The heading text is not part of `content_hash`.

**Frontmatter** (`parse_frontmatter`, chunker.py:26-83).

- The first line, stripped, must be `---`. A byte-order mark before it defeats this **(probe)**.
- Only lines 2 to 80 of the file are examined (`lines[1:80]`). The block ends at a line that is `---` or `...` after stripping. If no such line is found in that window, the result is `{}` **(probe)**.
- A line matching `_FM_LINE` sets a scalar; the key is lower-cased; the value is kept verbatim, quotes included. A line matching `_FM_LIST_HEAD` starts a list; following `_FM_LIST_ITEM` lines append to it; any line that is not a list item (a blank line included) ends the list **(probe)**. A later occurrence of a key replaces the earlier one. Keys must start at column 0 and contain only letters, `_` and `-`.

| Key | Accepted value | Effect on the returned dict |
|---|---|---|
| `status` | `heartwood` (case-insensitive, unquoted) | `heartwood: true` |
| `implemented`, `outdated` | any scalar | copied verbatim, only when `status` is heartwood |
| `role` | `authored` or `derived` (case-insensitive) | `role: <lower-cased value>`; any other value is ignored |
| `generated` | `true`, `1`, `yes` (case-insensitive) | `generated: true` |
| `sources` | a list, or a scalar split on `,` | `sources: [..]`; the list form wins when both exist |

- A quoted value such as `status: "heartwood"` is not recognised **(probe)**. A flow list `sources: [a, b]` keeps the brackets on the first and last item **(probe)**.
- What ingest does with the dict: the whole dict is stored in `kn_documents.meta`; the keys `heartwood`, `implemented`, `outdated`, `generated` are copied to `meta` of every chunk of the document; `role` is the role for newly created chunks; `sources` are Source Refs attached to the document's first chunk (store.py:281-285, 346-348). See sections 6 to 8 for the consequences.

**Per-section sources comment blocks** (`parse_source_refs`, chunker.py:90-115).

- Input is one chunk's `raw_text`. Lines inside fences are removed first, with the same fence rule as above.
- Every match of `_SOURCES_BLOCK` is taken; its inner text is split on commas and newlines; each piece is stripped and kept when it matches `_SOURCE_REF` and is not already in the list. Pieces that do not match are dropped without a record.
- The keyword is case-insensitive; a block may be on one line; several blocks per chunk are merged **(probe)**.
- Inline code is not skipped: a sources comment inside single backticks still yields refs **(probe)**. A list-style line (`- zeta:a.py`) does not match and is dropped **(probe)**. Any `word:non-space` string matches, including a URL **(probe)**. Text after the ref on the same line stays part of the ref **(probe)**.
- A block is attached to the chunk whose text contains it, because the parser runs per chunk (store.py:328).

Fictional example of a section that declares two refs:

```
## Retry policy

Requests are retried three times.

<!-- sources:
zeta:lib/retry.py#RetryPolicy
zeta:docs/limits.md#Backoff
-->
```

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/chunker.py#chunk_markdown`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#parse_frontmatter`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#parse_source_refs`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#norm`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#sha`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#content_hash`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`

## 4. Code chunking

`chunk_code(rel_path, source)` dispatches on the file name ending (code_chunker.py:24-36). Each chunk is `{symbol, kind, line_start, line_end, text}`; `text` is the whole lines `line_start..line_end` (1-based, inclusive) joined by `"\n"` (code_chunker.py:39-41). `ingest_code` turns each into a `kn_chunks` row with `natural_key = f"{rel}#{symbol}"`, `symbol_kind = kind`, `ordinal` = index in the returned list, `content_hash = sha(text)` with no normalisation (store.py:888-900). There is no size cap anywhere in `code_chunker.py`: a long function is one chunk.

| Ending | Chunker | Kinds produced |
|---|---|---|
| `.py` | `chunk_python` (stdlib `ast`) | `function`, `class`, `method`, `module`; `file` on failure |
| `.svelte` | `chunk_svelte` (regular expression) | `script`, `style`, `markup`; `file` when nothing was found |
| `.ts .mts .cts` | `chunk_typescript`, TypeScript grammar | `function`, `class`, `method`, `interface`, `type`, `enum`, `namespace`, `module`; `file` on failure |
| `.tsx` | `chunk_typescript`, TSX grammar | same code path |
| `.js .jsx .mjs .cjs` | `chunk_typescript`, JavaScript grammar | same code path |
| `.sh .bash .plist .plist.in .swift` | `_whole_file` | `file` |
| anything else | none | returns `[]` |

**Shared pieces.**

- `_whole_file` returns one chunk: symbol `<file>`, kind `file`, `line_start = 1`, `line_end = max(1, len(source.split("\n")))`, `text = source` (code_chunker.py:44-47). For a file that ends with a newline, `line_end` is one more than the number of lines **(probe)**.
- `_uncovered_runs` returns maximal runs of lines not claimed by a symbol chunk, with blank lines trimmed from both ends, kept only when at least one non-blank line remains (code_chunker.py:50-69). These become "module run" chunks.
- All chunkers sort their result by `line_start`.

**Python** (code_chunker.py:72-106).

- Only direct children of the module are considered.
- A top-level `def` or `async def` → symbol = function name, kind `function`, lines `lineno..end_lineno`.
- A top-level `class` → a header chunk (symbol = class name, kind `class`) from the `class` line to the line before the first method's `def`, or to the end of the class when it has no methods; plus one chunk per direct method (symbol `Class.method`, kind `method`).
- Uncovered runs → symbol `<module>` for the first run, `<module:1>`, `<module:2>`, ... for the following ones, kind `module`.
- `lineno` is the `def` or `class` line, so decorators are not part of the function or class chunk. A top-level decorator falls into a module run; the decorators of a class's first method fall into the class header; decorators of later methods become module runs of their own **(probe)**.
- Class-body statements after the first method, nested classes, and functions defined inside a top-level `if` or `try` are not chunked individually; they fall into module runs or the class header **(probe)**.
- Two methods with the same name (a property getter and its setter) produce two chunks with the same symbol **(probe)**.
- Failure: `SyntaxError` → one `<file>` chunk **(probe)**. No other exception is caught.
- An empty or blank `.py` file yields no chunks; there is no whole-file fallback for Python **(probe)**.

**Svelte** (code_chunker.py:109-133).

- Pattern: `<(script|style)\b[^>]*>.*?</\1>` with `DOTALL | IGNORECASE`.
- Each match → kind = the tag name; symbol = the tag name for the first block of that tag and `script:2`, `style:2`, ... for later ones.
- Uncovered runs → symbol `markup` for the first, `markup:1`, `markup:2`, ... afterwards, kind `markup` **(probe)**.
- Whole lines are claimed: markup on the same line as a block belongs to the block's chunk **(probe)**.
- No parse step and so no parse failure; a file with no chunks returns `_whole_file` **(probe)**.

**TypeScript, TSX, JavaScript** (code_chunker.py:136-251).

- Parser: tree-sitter, one cached parser per dialect, chosen by extension (code_chunker.py:141-158).
- Only named children of the root node are considered. For an `export_statement`, the declaration is the last child that is a known declaration kind or a `lexical_declaration` / `variable_declaration`; the chunk spans the whole export statement. An export statement with no such child is left to module runs.
- Declaration kinds (code_chunker.py:162-171): `function_declaration` and `generator_function_declaration` → `function`; `class_declaration` and `abstract_class_declaration` → `class`; `interface_declaration` → `interface`; `type_alias_declaration` → `type`; `enum_declaration` → `enum`; `internal_module` → `namespace`.
- `const` / `let` / `var`: only the first declarator is examined. When its value is one of `arrow_function`, `function_expression`, `function`, `generator_function`, or a call whose arguments include one of those, the statement is one `function` chunk named after the first declarator (code_chunker.py:236-245). Other declarations are left to module runs.
- Classes: methods are body children of type `method_definition` or `abstract_method_signature`. Without methods the class is one `class` chunk. With methods: a header chunk from the statement start to the line before the first method, and one `method` chunk per method named `Class.method`; a method chunk starts at its contiguous preceding decorators (code_chunker.py:201-221).
- A symbol without a `name` field is named `<anonymous>` (code_chunker.py:174-176).
- Uncovered runs → `<module>`, `<module:1>`, ... kind `module`.
- Failure: any exception while obtaining the parser or parsing → one `<file>` chunk; observed with the grammar package missing **(probe)**. A file with no chunks also returns `_whole_file`.
- Observed **(probe)** on fictional sources: overload signatures land in a module run and only the implementation is a `function` chunk; `let one = () => 1, two = () => 2;` is one chunk named `one`; a class field declared after the first method is a module run; the closing `}` of a class with methods is a module run of its own; a getter and setter pair gives two chunks with the same symbol; a computed method name is kept verbatim (`Service.[Symbol.iterator]`); a non-exported `namespace`, a `declare` statement, an anonymous `export default function` and an anonymous default class are module runs; a one-line class with two methods gives two method chunks with identical text and no header; a file with syntax errors is still chunked from whatever nodes the parser produced.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_code`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#_chunk`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#_whole_file`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#_uncovered_runs`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_python`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_svelte`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#_ts_parser`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#_ts_name`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_typescript`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code`

## 5. Identity reconciliation

Markdown and code reconcile differently. Only Markdown has rename detection, an identity log and a run record.

**Markdown, document level** (store.py:230-252, 353-358).

1. Load stored documents: `state='present' AND source_type='doc' AND repo=%s`.
2. A current path that equals a stored path keeps that document id.
3. For each current path with no stored match: if a stored document whose path is gone has `content_hash` equal to the current whole-file hash, its id is reused. Log decision `doc_renamed` with `old_key` = old path, `new_key` = new path.
4. Every remaining current path gets a new ULID. Log `doc_new` with `new_key` = path.
5. Every remaining stored document is set to `state='orphaned'`; its present chunks are set to `state='orphaned', last_status='orphaned'`. Log `doc_orphaned` with `old_key` = path. No per-chunk log rows are written for these chunks.

A document that is moved and edited in the same run is not matched: it is `doc_orphaned` plus `doc_new`, and all its chunks get new ids.

**Markdown, chunk level** (store.py:287-333), for every document that was not skipped as unchanged:

1. Upsert the document row first, with the new whole-file hash (store.py:276-281).
2. Load the document's present chunks (`id, natural_key, content_hash, first_seen`; no `ORDER BY`). Build `by_key` (a dict: for duplicate natural keys the last row read wins) and `by_chash` (content hash → list of rows).
3. Walk the current chunks once, in file order. For each chunk:
   - if `by_key` has its natural key and that row is not yet consumed: keep the id; decision `unchanged` when the content hashes are equal, else `edited`;
   - otherwise take the first not-yet-consumed stored row with the same content hash: keep its id; decision `renamed`; `prev_key` = that row's natural key;
   - otherwise: new ULID; decision `new`; `first_seen` = run timestamp.
4. Upsert the chunk row (below) and append a log row `(run_id, ts, document_id, chunk_id, decision, prev_key, natural_key)`.
5. Every stored row not consumed: `UPDATE kn_chunks SET state='orphaned', last_status='orphaned', last_run=%s`; log `orphaned` with `old_key` = its natural key.

The two matching rules are applied per chunk in one pass, not as two rounds over the whole document. The candidates are only the present chunks of the same document.

**What the chunk upsert writes** (store.py:309-327).

- On insert: all chunker fields, `role` (section 6), `state='present'`, `last_status` = decision, `first_seen`, `last_seen`, `last_run`, `repo`, `meta` = the heartwood/generated subset of the frontmatter. `origin` and `tier` take their defaults (`'corpus'`, 0).
- On conflict (same id): `natural_key`, `prev_natural_key`, `ordinal`, `level`, `parent_key`, `title`, `raw_text`, `content_hash`, `title_hash`, `state='present'`, `last_status`, `last_seen`, `last_run`, `meta` are overwritten. `role`, `first_seen`, `repo`, `stale`, `stale_because` are not touched.
- `prev_natural_key` is overwritten on every reconcile of the document: it holds the old key only until the document's file changes again.
- Embedding: `embedding = CASE WHEN kn_chunks.content_hash = EXCLUDED.content_hash THEN kn_chunks.embedding ELSE NULL END` (store.py:322-323). The vector is cleared exactly when the normalised body hash changed, that is, on `edited`. It is kept on `unchanged` and `renamed`, also when the heading text or the whitespace of `raw_text` changed.

**Identity log and run record.** Log rows are collected in memory and written with one `executemany` at the end of `ingest` (store.py:360-361). Decisions written: `doc_new`, `doc_renamed`, `doc_orphaned`, `unchanged`, `edited`, `renamed`, `new`, `orphaned`. Every chunk of a changed document is logged on every run, the unchanged ones included. Then one `kn_ingest_runs` row is inserted on every call, with `summary` = the counts `unchanged, edited, renamed, new, orphaned, docs_new, docs_renamed, docs_orphaned, docs_skipped` (store.py:250-252, 362-363). The chunk count `orphaned` does not include chunks retired through `doc_orphaned`.

**Orphaned rows and revival.** `ingest` never deletes a row. Orphaned documents and chunks keep their id, text, hash and embedding. They are never candidates for matching, so there is no revival: a section or file that is removed and later restored gets a new ULID. The `state='present'` assignments in both upserts are no-ops, because the ids involved always come from present rows or are new. The only hard deletes of documents and chunks in the repository are `drop_overlay` (store.py:1036-1045) and RAPTOR's `_clear` for summary chunks (raptor.py:83-90). The only statement that can turn an orphaned document back to `present` is the upsert in `track_source` (store.py:401-404).

**Code** (store.py:865-925). Per changed or new file:

1. Update the document's `content_hash` and `last_seen`, or insert a new document.
2. Load the document's present chunks with `origin='code'` into a dict by natural key.
3. For each chunk from the chunker: no stored row with that key → insert with a new ULID, `role='authored'`, `origin='code'`, `tier=0`, `level=0`; stored row with a different hash → update `raw_text, content_hash, ordinal, symbol_kind, line_start, line_end, last_seen` and set `embedding=NULL`; same hash → update `ordinal, line_start, line_end, last_seen` only.
4. Stored keys not produced this time → `state='absent', last_seen=ts`.

Matching is by natural key only: there is no rename detection, no identity log, no run record, and `last_status`, `prev_natural_key`, `last_run` stay `NULL`. A symbol that disappears and comes back gets a new id, because only present rows are loaded. The return value is `{files, chunks, added, updated, removed, items}`.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code`
- `mycel_deprecated_v1:mycel/knowledge/store.py#track_source`
- `mycel_deprecated_v1:mycel/knowledge/store.py#drop_overlay`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#chunk_markdown`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#content_hash`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#_clear`

## 6. Roles and states

**`role`.**

| Value | Where it is written |
|---|---|
| `unclassified` | Column default (store.py:51). Markdown chunk inserted while the frontmatter has no valid `role` (store.py:285, 325). Reset target in `_sync_declared_edges` (store.py:461-463) |
| `authored` | Code chunk on insert (store.py:897). Markdown chunk inserted while the frontmatter says `role: authored` |
| `derived` | Summary chunk on insert (raptor.py:112). Markdown chunk inserted while the frontmatter says `role: derived`. Any chunk that has at least one resolved declared parent after a sync (store.py:456-457). Any chunk passed as child to `derive` (store.py:484) |

Transitions:

- The Markdown upsert writes `role` on insert only; the conflict branch does not list it (store.py:314-323). Changing or removing `role:` in the frontmatter does not change chunks that already exist.
- Any role → `derived`: a sync that resolves at least one declared parent, or a call to `derive`.
- `derived` → `unclassified`: a sync of that chunk that resolves no declared parent, when no row in `kn_derivations` has the chunk as child (store.py:461-463).
- Nothing sets `authored` after insert. A chunk that was `authored`, became `derived` and lost its edges ends as `unclassified`.
- Code ingest never updates `role`.

**`state`.** Documents: `present`, `orphaned`. Chunks: `present`; `orphaned` (Markdown, store.py:332, 356); `absent` (code, store.py:914, 924, and `migrate_arbol`, repo_identity.py:51). Retiring a Markdown chunk leaves `last_seen` unchanged; retiring a code chunk sets `last_seen` to the run time.

**`last_status`.** Markdown chunks only: `new`, `unchanged`, `edited`, `renamed`, `orphaned`. It is the decision of the most recent reconcile of the chunk's document. `NULL` for code and summary chunks.

**`origin` and `tier`.** `origin`: `corpus` (default; every Markdown chunk), `code` (store.py:897), `summary` (raptor.py:112). `tier`: 0 for corpus and code chunks; the RAPTOR tier for summary chunks.

**`meta` keys.**

| Row | Key | Written by |
|---|---|---|
| Markdown document | `heartwood`, `implemented`, `outdated`, `role`, `generated`, `sources` | Document upsert, the full frontmatter dict (store.py:281) |
| Markdown chunk | `heartwood`, `implemented`, `outdated`, `generated` | Chunk upsert, replaced as a whole on every reconcile (store.py:284, 319, 327) |
| Markdown chunk | `unresolved_sources` (sorted list of ref strings) | `_sync_declared_edges` (store.py:464-469) |
| Code and summary rows | none | `meta` stays `{}` |

Readers of these keys in the files read: `detect` reads chunk `heartwood` and `generated` (store.py:535-537); `status` counts present documents with `heartwood` (store.py:1123-1124); `chunks_view` returns a document's `implemented` / `outdated` and a chunk's `unresolved_sources` (store.py:775-781); `ingest` selects chunks by `meta ? 'unresolved_sources'` (store.py:266-267, 343-344). RAPTOR excludes chunks with `heartwood` or `generated` from clustering (raptor.py:198, 427).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges`
- `mycel_deprecated_v1:mycel/knowledge/store.py#derive`
- `mycel_deprecated_v1:mycel/knowledge/store.py#detect`
- `mycel_deprecated_v1:mycel/knowledge/store.py#status`
- `mycel_deprecated_v1:mycel/knowledge/store.py#chunks_view`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#parse_frontmatter`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#_insert_summary`
- `mycel_deprecated_v1:mycel/repo_identity.py#migrate_arbol`

## 7. Source Refs and derivations

**Grammar actually accepted.** A ref is `repo:rest`. In a sources comment block the piece must match `^[\w.@-]+:\S.*$` (chunker.py:87). Refs from frontmatter `sources:` are not checked against that pattern. The resolver splits at the first `:`; when `rest` contains `#` it splits at the first `#` into `path` and `symbol` (store.py:413-418). `symbol` may contain spaces, `>` and further `#`. Because blocks are split on commas, a symbol containing a comma cannot be written in a block.

**Repository name.** `canonical_repo` maps the exact base name `Arbol` to `arbol` and leaves every other name unchanged, including case; a `@branch` suffix is preserved (repo_identity.py:8-12). Refs to any repository string stored in the `repo` column resolve; there is no check that the repository is enabled or known. The comparison is exact and case-sensitive.

**Resolution** (`_resolve_source_ref`, store.py:408-439). An empty list means unresolved. Paths are compared verbatim with the stored relative path. There are three cases.

File-level ref, no `#`: `SELECT id FROM kn_documents WHERE repo=%s AND path=%s AND state='present'`. The parent is a document id, of any `source_type`.

Ref with `#`, first query, code chunks:

```
SELECT id FROM kn_chunks WHERE repo=%s AND state='present' AND origin='code'
AND (natural_key = <path#symbol> OR natural_key LIKE <escaped path#symbol> || '.%'
  OR natural_key = <symbol>      OR natural_key LIKE <escaped symbol> || '.%')
```

`\`, `%` and `_` are escaped for `LIKE`. The first two predicates give the symbol itself and its class family: `path#Class` matches the class header chunk and every `path#Class.method` chunk. All matching ids are returned, so one ref can produce several parents.

Ref with `#`, second query, run only when the first returned nothing, document sections:

```
SELECT c.id FROM kn_chunks c JOIN kn_documents d ON d.id=c.document_id
WHERE d.repo=%s AND d.path=%s AND d.state='present' AND c.state='present'
AND (c.natural_key=%s OR c.title=%s)
```

The symbol is compared with the full heading path (`A > B`) or with the bare heading title. Every matching chunk is returned, so a title that repeats in the document yields several parents. The match is exact and case-sensitive.

**Where edges come from.** Per chunk, the refs are those parsed from its `raw_text`; the document's frontmatter `sources` are added to the chunk at index 0 of the document (store.py:346-348), which is the preamble chunk when the file has frontmatter. For a changed document, `_sync_declared_edges` is called for every chunk that has refs, or already has a `declared` edge, or is selected by the `unresolved_sources` query (store.py:340-351). Resolution runs after all chunks of the document were upserted, and documents are processed in sorted path order.

**Syncing declared edges to the file** (`_sync_declared_edges`, store.py:442-469). Given the chunk and a map ref → parent ids:

1. Delete the chunk's edges with `kind='declared'` whose parent is not in the resolved set.
2. For each resolved parent, upsert an edge `kind='declared', policy='review', hash_at_gen = current parent hash, created_at = run timestamp`. On conflict with an existing `(parent_id, child_id)` row, `kind`, `policy`, `hash_at_gen` and `created_at` are all overwritten.
3. Set or reset `role` (section 6).
4. Unresolved refs: write the sorted list to `meta.unresolved_sources`; when every ref resolved, remove the key.

**Unresolved refs.** They are recorded only in the chunk's `meta.unresolved_sources`. Nothing is logged or raised. They are retried on every `ingest` call: for a changed document through the full sync, and for an unchanged document through the retry at store.py:266-272, which re-parses the chunk's refs (adding the frontmatter sources when `ordinal == 0`) and calls `_sync_declared_edges` with all of them.

**Edge kinds and policies.**

| `kind` | Written by | `policy` |
|---|---|---|
| `declared` | `_sync_declared_edges`, from refs in files | `review` |
| `asserted` | `derive` default, `assert_derivation` | `review` |
| `generated` | `derive(kind="generated")`, called by RAPTOR (raptor.py:286, 401) | `auto` |

`policy` is `"auto" if kind == "generated" else "review"` (store.py:479). No code in the files read branches on `policy`.

**`hash_at_gen`.** It is the parent's `content_hash` read at the moment the edge row is written or overwritten (`_parent_hash`, store.py:369-374): for a chunk parent the chunk's `content_hash`, for a document parent the whole-file hash. `_parent_hash` looks up by id only, with no `state` predicate. Consequences of the upsert in step 2:

- A declared edge is re-pinned to the parent's current hash on every sync of its child chunk, that is, whenever the child's file changed in any byte, and on every ingest for a chunk that has an unresolved ref.
- A section ref tracks only the text directly under the cited heading (the body hash excludes subsections and the heading line). A file-level ref tracks every byte of the file.

**`derive(conn, child_id, parent_id, kind="asserted")`** (store.py:472-484): raises `ValueError("child chunk not found: ...")` when the child is not a chunk, `ValueError("parent not found: ...")` when the parent is neither a chunk nor a document; upserts the edge, overwriting `kind`, `policy`, `hash_at_gen`, `created_at` on conflict; sets the child's `role='derived'`. There is no check for self-edges or cycles.

**`assert_derivation(conn, child_ref, source_ref)`** (store.py:487-525): resolves both refs with `_resolve_source_ref`; raises `ValueError` with `child Source Ref did not resolve: ...` or `source Source Ref did not resolve: ...`; raises `child Source Ref must identify a chunk; add #symbol or #Heading: ...` when a resolved child id is not a chunk; calls `derive(..., kind="asserted")` for every child and source pair; returns `{child_ref, source_ref, children: [{id, label}], sources: [{id, label}], edges}`. The CLI command that calls it runs `detect` afterwards (cli.py:203-205).

**Traversal helpers.** `impact(conn, root)` and `lineage(conn, leaf)` are recursive queries over `kn_derivations` returning ids with their minimum depth (store.py:569-580). `_label` renders a chunk as `{document path} › {natural_key}` and a document as `[{source_type}] {path}` (store.py:377-383).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#_resolve_source_ref`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_parent_hash`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_label`
- `mycel_deprecated_v1:mycel/knowledge/store.py#derive`
- `mycel_deprecated_v1:mycel/knowledge/store.py#assert_derivation`
- `mycel_deprecated_v1:mycel/knowledge/store.py#impact`
- `mycel_deprecated_v1:mycel/knowledge/store.py#lineage`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#parse_source_refs`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#parse_frontmatter`
- `mycel_deprecated_v1:mycel/repo_identity.py#canonical_repo`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_derive`

## 8. Detection and drifts

**`detect(conn)`** (store.py:528-566) recomputes the `stale` flag for the whole database. It takes no repository argument.

1. Load every row of `kn_derivations` (no filter, no order).
2. Build the exempt set: chunk ids where `(meta->>'heartwood')::boolean IS TRUE OR (meta->>'generated')::boolean IS TRUE`.
3. For each edge whose child is not exempt, read the parent's current hash with `_parent_hash`:
   - no chunk and no document with that id → the child is directly stale, reason `source removed (<first 8 characters of the parent id>)`;
   - `hash_at_gen IS NOT NULL` and it differs from the current hash → directly stale, reason `source changed since generation (<first 8 characters of the parent id>)`.
4. Propagation: starting from the directly stale chunks, every child of a stale chunk becomes stale unless it is exempt, with reason `upstream chunk is stale (<first 8 characters of the stale parent's id>)`. A direct reason is not overwritten by a propagated one. An exempt chunk is not marked and nothing propagates through it.
5. Write: `UPDATE kn_chunks SET stale=false, stale_because=NULL WHERE stale=true`, then one `UPDATE ... SET stale=true, stale_because=%s` per stale chunk.
6. When the exempt set is not empty: `UPDATE kn_drifts SET status='closed', closed_at=%s WHERE status='open' AND chunk_id = ANY(<exempt ids>)`.
7. Return `{edges, direct, stale}`.

Details of the rules:

- A chunk with several stale edges keeps one reason: the one from the last edge processed.
- The exemption applies to the child side only. A heartwood or generated chunk still acts as a parent, and its edges are still synced.
- The parent's `state` is not consulted. A parent that is `orphaned` or `absent` still has a row and an unchanged hash, so its children are not stale. `source removed` requires the parent row to have been deleted.
- The child's `state` is not consulted either; retired chunks can carry `stale=true`. Consumers filter on `state='present'`.
- Stale flags are cleared only by the next `detect`.

**How a stale chunk becomes fresh again** (all read from the code; there is no explicit "resolve" operation): the parent's hash returns to `hash_at_gen`; the edge is re-pinned (any change to the child's file for declared edges, a new `derive` call for asserted edges, RAPTOR regeneration for generated edges, raptor.py:392-401); the edge is deleted because the ref was removed or no longer resolves; or the chunk becomes heartwood or generated.

**Drifts.**

- `open_drifts(conn, repo)` (store.py:610-633): for each chunk with `stale=true AND state='present' AND repo=%s` that has no row in `kn_drifts` with `status='open'`, insert a drift with `reason` = the chunk's `stale_because`, `source_id` and `source_label` = the first contributing source, and insert every contributing source into `kn_drift_sources` with `ON CONFLICT (drift_id, source_id) DO NOTHING`. Returns `{opened: n}`.
- `_drift_sources(child)` (store.py:585-607) recomputes the contributing sources from the child's edges ordered by `created_at`: `source removed` (no parent row), `source changed since generation` (hash differs), `upstream chunk is stale` (the parent is a chunk with `stale=true AND state='present'`); other parents are left out. The reason strings here have no id suffix.
- When no source contributes, `open_drifts` uses one placeholder source with `source_id = None`.
- Closing: the only statement that sets `status='closed'` is step 6 of `detect`. A drift is not closed when its chunk stops being stale.
- Deleting: `drop_overlay` deletes drifts of an overlay's chunks (store.py:1041).
- `list_drifts(conn, repo)` (store.py:636-653) returns open drifts whose chunk has `repo=%s`, newest first, each with its `kn_drift_sources` rows ordered by `source_label`.
- Within this repository `open_drifts` has no caller; `list_drifts` is called by the CLI (cli.py:191).

**Reporting.** `refresh` returns every present stale chunk of the repository as an item `{repo, path, detail: natural_key, reason: stale_because, action: "stale", file_path}` (store.py:677-687). `fs.write` returns the labels of the repository's present stale chunks (fs.py:72-77). `count_stale_summaries` counts present stale summary chunks (store.py:1102-1109). `status` returns `documents, chunks, stale, edges, open_drifts, heartwood` (store.py:1112-1126).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#detect`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_parent_hash`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_drift_sources`
- `mycel_deprecated_v1:mycel/knowledge/store.py#open_drifts`
- `mycel_deprecated_v1:mycel/knowledge/store.py#list_drifts`
- `mycel_deprecated_v1:mycel/knowledge/store.py#refresh`
- `mycel_deprecated_v1:mycel/knowledge/store.py#count_stale_summaries`
- `mycel_deprecated_v1:mycel/knowledge/store.py#status`
- `mycel_deprecated_v1:mycel/knowledge/store.py#drop_overlay`
- `mycel_deprecated_v1:mycel/knowledge/fs.py#write`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#regen_stale`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_drifts`

## 9. Code map

`code_map.py` produces one Markdown file per repository from rows already in the database. No model is involved.

**Input** (`build_markdown`, code_map.py:23-29):

```
SELECT d.path, c.natural_key, c.symbol_kind
FROM kn_chunks c JOIN kn_documents d ON d.id=c.document_id
WHERE c.repo=%s AND c.origin='code' AND c.state='present'
AND c.symbol_kind NOT IN ('module','markup','style','file')
ORDER BY d.path, c.ordinal
```

A file that has only `module`, `markup`, `style` or `file` chunks does not appear in the map. Svelte `script` chunks do appear, as a symbol named `script`.

**Output text** (code_map.py:31-78).

- The symbol is the natural key after the first `#`. A symbol containing `.` is split at the first `.` into class and method; a symbol of kind `class` is a class with no methods; anything else is a top-level name.
- Header lines: `---`, `generated: true`, `---`, `# Code Map: {repo}`, a blank line, then `Auto-generated structural overview — {files} files, {symbols} symbols. Do not edit; regenerated when the code corpus changes.`
- One `## {directory}` section per directory in sorted order; files in the repository root are under `## .`.
- One line per file in sorted order: `- **{file}** — {parts}`, where parts are the classes in sorted order, each as `Class (m1, m2, ...)` or `Class`, then the top-level names, joined by `; `.
- `_MAX_NAMES_PER_FILE = 8` (code_map.py:20) limits each method list and the top-level list separately; the rest is shown as `, +N more`.
- Each directory section ends with a sources comment block holding one file-level ref per listed file, `{repo}:{directory/}{file}`.

**Writing** (`write_map`, code_map.py:81-99). Destination: `{artifact_root}/generated/code-map.md`. The text is built on every call; when the existing file has identical content the function returns `False` and writes nothing; otherwise it creates the directory, writes `code-map.md.tmp` and replaces the destination, returning `True`.

**When.** The all-repository sync pass calls it for every enabled repository whose code root is a directory, right after `ingest_code`; the repository-scoped pass does not (`write_code_maps=False`). Exceptions are logged and do not stop the pass (syncpass.py:192-193, 210-211, 268-275).

**What ingest then makes of it** (inferred from sections 3, 6 and 7): the file is ingested as an ordinary Markdown document on a later Markdown ingest; its three frontmatter lines form the `(preamble)` chunk; `generated: true` lands in the `meta` of every chunk, which exempts them from `detect` and from RAPTOR clustering; each directory chunk gets one `declared` edge per listed code document and `role='derived'`.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/code_map.py#build_markdown`
- `mycel_deprecated_v1:mycel/knowledge/code_map.py#write_map`
- `mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked`
- `mycel_deprecated_v1:mycel/syncpass.py#run_pass`
- `mycel_deprecated_v1:mycel/syncpass.py#run_repo_pass`

## 10. Branch overlays

Retired feature; summary only.

- An overlay is a second chunk namespace named `{base_repo}@{branch}` (`overlay_ns`, store.py:934-936), stored as the `repo` value of ordinary `kn_documents` / `kn_chunks` rows, plus one registry row in `kn_overlays`.
- `ingest_overlay` computes, in a git worktree, the files that differ from `git merge-base master HEAD` (`git diff --name-status -M`, uncommitted changes included) plus untracked files, filters them by `code_subdirs`, `_CODE_EXTS` and `_CODE_SKIP`, and passes the changed files to `ingest_code(..., repo=ns, only_files=changed)` (store.py:939-991). Code only; no Markdown.
- Deleted and renamed-away paths are stored in `kn_overlays.deleted_paths`. `merged` is set when `HEAD` is an ancestor of `master` and no file changed (store.py:993-1001). The branch name `master` is fixed.
- `overlay_paths` returns the overlay's present document paths plus `deleted_paths`: the set of base paths to hide when searching through the overlay (store.py:1049-1056).
- `drop_overlay` hard-deletes the overlay's identity-log rows, derivations (by child), drifts, chunks, documents and registry row (store.py:1026-1046). `list_overlays` lists registry rows with chunk and embedded counts.
- The sync pass auto-registers an overlay for each worktree it finds, re-diffs every registered overlay on each pass, and drops overlays whose worktree directory is gone (syncpass.py:278-334).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#overlay_ns`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_overlay`
- `mycel_deprecated_v1:mycel/knowledge/store.py#list_overlays`
- `mycel_deprecated_v1:mycel/knowledge/store.py#drop_overlay`
- `mycel_deprecated_v1:mycel/knowledge/store.py#overlay_paths`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code`
- `mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked`

## Surprises and defects

Ordered by how much they change what a reader would assume. Unless marked **(probe)** or **(stub run)**, each item is read from the code and was not executed.

**Change tracking.**

1. **`refresh` hides code edits from `ingest_code`.** `refresh` calls `track_source` for every present code document of the repository, which overwrites that document's `content_hash` with the hash of the file as it is now (store.py:671-675, 401-404). The sync pass then calls `ingest_code` on the same root (syncpass.py:247-263), and `ingest_code` skips every file whose stored document hash equals the file hash (store.py:870-871). Result **(stub run)**: with a fictional one-function file edited between two ingests, `ingest_code` alone reports `updated: 1`; with the `track_source` step of `refresh` in between it reports `chunks: 0, updated: 0` and the stored chunk keeps the old text and its vector. Later passes skip the file as well, because the document hash now matches. New files and removed files are still handled. Edits are picked up only when the file changes between the two calls, which is where the git mirror refresh sits (syncpass.py:254-256), or when the artifact root is not a directory so `refresh` is not called. Inferred side effect: the document hash does change, so chunks citing the file with a file-level ref are flagged stale, while chunks citing a symbol in it are not.
2. **Any edit to a file re-pins all its declared edges.** `_sync_declared_edges` overwrites `hash_at_gen` with the parent's current hash on every call (store.py:451-455), and it is called for every ref-bearing chunk of a document whenever the file changed in any byte (store.py:347-351). Inferred: a stale chunk becomes fresh when anything in its file is edited, even another section; a derivation between two sections of the same file can never be stale; a chunk with one unresolved ref has all its edges re-pinned on every ingest (store.py:266-272) and can never be stale through them. The `fs.py` module docstring says a write "flags exactly the derived chunks whose parent chunk changed"; that holds only for children in other, unchanged files.
3. **A removed source does not make anything stale.** `_parent_hash` has no `state` predicate (store.py:369-374) and ingest never deletes rows, so `source removed` (store.py:550-551) is reachable only after a hard delete, which in this repository means `drop_overlay`. Inferred: after a cited file, section or symbol is removed or renamed, the edge keeps pointing at the retired row and its frozen hash until the citing file changes; then the edge is deleted and the ref moves to `unresolved_sources`. Removal never surfaces as staleness or as a drift.
4. **Nothing opens drifts, and nothing closes them on recovery.** `open_drifts` has no caller in `mycel/` or `tests/`. The only close is for heartwood and generated chunks (store.py:563-565). The module docstring of `store.py` calls a Drift "the work item opened for a stale chunk".
5. **The defensive path in `open_drifts` cannot insert.** The placeholder source has `source_id = None` (store.py:621-622), and `source_id` is part of the primary key of `kn_drift_sources` (store.py:86). Inferred from PostgreSQL primary-key rules: the insert fails with a not-null violation, after the `kn_drifts` row was already written. The placeholder is reachable, for example when a chunk is stale only through a parent that is itself stale but no longer `present`.

**Identity.**

6. **Matching is greedy and single-pass.** A chunk without a key match takes the first unconsumed stored row with the same content hash (store.py:301), before later chunks had the chance to claim that row by key. Every section with no body text has the same content hash. Inferred: when a new heading with no body text is inserted above existing sections that have no body text, the new heading inherits the id of one of them and is logged `renamed`; one existing section ends with a new id and is logged `new`; depending on row order the sections in between exchange ids as well. Derivations and embeddings follow ids, so they move with the shift.
7. **Natural keys are not unique and duplicates are mishandled.** No constraint exists on `(document_id, natural_key)`. Markdown: two sections with the same heading path share a key; `by_key` holds one of them (store.py:289), so on the next change of the file they can swap ids and be logged as `edited` / `renamed`, clearing an embedding. Code: a getter/setter pair or any repeated symbol gives duplicate keys **(probe)**; on first ingest both rows are inserted; on a later change both new chunks are compared with the single row the dict kept, and the other row is neither updated nor marked `absent` (store.py:884-915).
8. **Module-run keys are positional.** `<module:N>`, `markup:N` are numbered by position (code_chunker.py:104, 131, 249). Inferred: a change that creates a new run earlier in a file (for example a decorator added to a function that had none) renumbers the following runs; each is then matched by key to the row of its predecessor, updated, and its embedding cleared.
9. **A renamed section keeps its vector.** The embedding is kept whenever the body hash is unchanged (store.py:322-323), although `raw_text` contains the heading line and so did change.
10. **Ingest is not atomic.** Connections are autocommit (database.py:77), the document row with its new hash is written before its chunks (store.py:276-281), and the identity log is written at the very end (store.py:360-361). Inferred: a failure midway leaves a document that the next run skips as unchanged with partly reconciled chunks, and loses the log rows of what was already applied.
11. **`role` is frozen at insert.** The frontmatter `role` applies only to chunks created while it is present (store.py:314-323, 325). A chunk whose refs all fail to resolve is reset from `derived` to `unclassified` even when `derived` came from the frontmatter (store.py:461-463). `authored` is never restored.

**Source Refs and edges.**

12. **The docstring of `_sync_declared_edges` is contradicted.** It says edges of other kinds "are never touched". The delete respects that, but the upsert's conflict branch sets `kind='declared'` on an existing `asserted` or `generated` edge between the same pair (store.py:453-454); that edge is then deleted when the ref is removed from the file. In the other direction `derive` turns a declared edge into an asserted one until the next sync (store.py:481-482).
13. **Unresolved refs are not reported "loudly".** The docstring of `_resolve_source_ref` says the caller records them loudly. They are written to `meta.unresolved_sources` only; the single reader is `chunks_view`, which has no caller in this repository.
14. **`had_unresolved` is computed too late.** The query at store.py:343-345 runs after every chunk's `meta` was replaced by the upsert (store.py:319), so for current chunks it finds nothing; it can only return retired chunks, which are not in the loop. The outcome is still correct because the upsert already removed the key.
15. **Third and fourth predicate of the symbol query.** `natural_key = <symbol>` and its `LIKE` twin (store.py:424) can match a code chunk only when the text after the first `#` is itself a full `path#symbol` key; the path before the first `#` is then ignored. Inferred: vestigial.
16. **Parser leniency (probe).** Invalid pieces in a sources comment block are dropped silently; list-style lines are dropped; URL-like strings are accepted as refs; a block inside inline code creates edges; frontmatter `sources` bypass the pattern check.
17. **The reason suffix is not an identifier.** The first 8 characters of a ULID encode the creation time divided by 1024 ms (store.py:29-35, 551-559). Rows created in the same second share the prefix, so the suffix in `stale_because` does not identify the parent.
18. **`impact` and `lineage` have no cycle guard.** They use `UNION ALL` recursion (store.py:569-580), and `derive` accepts cycles and self-edges. Neither function has a caller.

**Scan and chunking.**

19. **`_lang_of` labels shell, plist and Swift files `javascript`** (store.py:793-800).
20. **`track_source` is not scoped to a repository.** The lookup is by `path` and `source_type` only (store.py:397-399), and the insert sets no `repo`. Inferred: with the same relative code path in two repositories, one repository's refresh can overwrite the other's document hash.
21. **Decorators are separated from what they decorate (probe).** Python decorators land in module runs or in the class header; a decorator between methods becomes a chunk of its own containing one line.
22. **Other chunker edges (probe).** The closing brace of a TypeScript class with methods is its own chunk. A one-line class yields overlapping method chunks with identical text. Only the first declarator of a multi-declarator statement is examined. `_whole_file.line_end` is one too high for files ending in a newline. An empty `.py` file gives no chunks while an empty `.ts` or `.svelte` file gives one empty `<file>` chunk. Only `SyntaxError` is caught for Python.
23. **Markdown edges (probe).** Frontmatter is kept inside the preamble chunk. A `#` comment line inside frontmatter is treated as a heading and splits the frontmatter across two chunks, while `parse_frontmatter` still reads the whole block. `# C#` becomes the title `C`. A fence is closed by a line that opens another fence of the same marker. Quoted frontmatter values and flow lists are not understood. A closing delimiter after line 80, or a byte-order mark, silently disables the frontmatter. A heading that contains ` > ` is indistinguishable from nesting in the natural key.
24. **`.git` check on the full path.** The Markdown scan tests `".git" in md.parts` on the whole path (store.py:215). The comment at store.py:817-821 describes the same mistake as a fixed bug in the code scan.
25. **No guard against an empty scan** (section 2). A narrowed `code_subdirs`, a wrong root or an unreadable tree retires every row outside the result.
26. **Two words for the same state.** Retired Markdown chunks are `orphaned` and keep `last_seen`; retired code chunks are `absent` and get a new `last_seen`. The docstring of `ingest_code` says "vanished ones go absent" without noting the difference.

**Schema, constants and dead code.**

27. **Hard-coded `arbol`.** The DDL re-creates an enabled `kn_repos` row `arbol` with profile `voyage` at every process start when it is missing, and re-applies five fixed `code_subdirs` whenever that column is `NULL` (store.py:134-143). Inferred: resetting `arbol` to whole-tree with `set_repo_flags(code_subdirs=[])` is undone at the next process start. The default argument `repo="Arbol"` appears on most functions in `store.py` and `fs.py`; column defaults are `'Arbol'` in the DDL and `'arbol'` after `ensure_schema`.
28. **DDL on every call.** The docstring of `ensure_schema` explains that DDL must run once per process to avoid lock contention. `list_repo_flags` and `set_repo_flags` still run `ALTER TABLE` on each call (store.py:1063, 1093, 1096), and `list_repo_flags` is called in every sync pass (syncpass.py:234).
29. **"Zero writes" comment.** The comment at store.py:256-259 says an unchanged corpus does zero writes. Each `ingest` call inserts one `kn_ingest_runs` row (store.py:362-363), and the unresolved-ref retry can write as well.
30. **Write-only tables.** No code in this repository reads `kn_identity_log` or `kn_ingest_runs`. No code branches on `kn_derivations.policy`.
31. **Uncalled functions in this repository.** `open_drifts`, `impact`, `lineage`, `chunks_view`; `track_source` is called only by `refresh`; `fs.write`, `fs.rename`, `fs.remove` have no caller (tests use `fs.read` and `fs.tree`).
32. **`status` counts.** `documents` counts rows of every state and source type; the orphaned count is selected and not returned (store.py:1115-1116, 1125). `edges` has no state filter.
33. **Overlay docstrings contradicted.** `ingest_code` and `ingest_overlay` say files reverted to master drop out through the reconcile, but the removed-file reconcile runs only when `only_files is None` (store.py:839-842, 917, 945-946). The DDL comment says overlays are exempt from detection; `detect` has no namespace filter.
34. **Code map.** The `(no top-level symbols)` branch is unreachable because a file appears only through a symbol row (code_map.py:71). The docstring says the map is written "whenever the code corpus changed"; it is rebuilt and compared on every full pass. `write_map` creates the artifact root directory when it does not exist (inferred from `os.makedirs`, code_map.py:94).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#refresh`
- `mycel_deprecated_v1:mycel/knowledge/store.py#track_source`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_sync_declared_edges`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_resolve_source_ref`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_parent_hash`
- `mycel_deprecated_v1:mycel/knowledge/store.py#derive`
- `mycel_deprecated_v1:mycel/knowledge/store.py#detect`
- `mycel_deprecated_v1:mycel/knowledge/store.py#open_drifts`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_drift_sources`
- `mycel_deprecated_v1:mycel/knowledge/store.py#impact`
- `mycel_deprecated_v1:mycel/knowledge/store.py#lineage`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_scan_corpus`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_scan_code`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_lang_of`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ulid`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema`
- `mycel_deprecated_v1:mycel/knowledge/store.py#list_repo_flags`
- `mycel_deprecated_v1:mycel/knowledge/store.py#set_repo_flags`
- `mycel_deprecated_v1:mycel/knowledge/store.py#status`
- `mycel_deprecated_v1:mycel/knowledge/store.py#chunks_view`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_overlay`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#chunk_markdown`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#parse_frontmatter`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#parse_source_refs`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_python`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_svelte`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_typescript`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#_whole_file`
- `mycel_deprecated_v1:mycel/knowledge/code_map.py#build_markdown`
- `mycel_deprecated_v1:mycel/knowledge/code_map.py#write_map`
- `mycel_deprecated_v1:mycel/knowledge/fs.py#write`
- `mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked`
- `mycel_deprecated_v1:mycel/database.py#connect`

## Not established

- **Behaviour against PostgreSQL.** `ingest`, `_resolve_source_ref`, `_sync_declared_edges`, `detect`, `open_drifts` and `refresh` were read, not run; `track_source` and `ingest_code` were run only against a stand-in connection. Items 2 to 7, 10, 14 and 20 of the previous section are consequences derived from the code, and item 1 was not reproduced on a real database. They should be reproduced there before a specification relies on them.
- **Row order.** Several queries that feed matching have no `ORDER BY` (stored chunks at store.py:287-288, edges at store.py:530, stored documents at store.py:230-232). Which row wins among duplicates in practice was not established.
- **External callers.** Comments mention a `mycel_client` daemon and a Corpus Watcher. Neither is in this repository. Whether something outside it called `open_drifts`, `chunks_view`, `fs.write` or `ingest_code` on a different schedule was not established.
- **Transactions.** Whether any caller wraps a pass in a transaction was not checked beyond `database.connect` (autocommit) and the two `conn.commit()` calls in `cli._cmd_derive`.
- **Embedding side.** What text is embedded for a chunk, whether long chunks are truncated there, and how the fixed `vector(1024)` relates to the embedder profiles are in `embedder.py`, which was not read.
- **RAPTOR.** Only the insert of summary chunks and the re-pin on regeneration were read. How `generated` edges, tiers and stale summaries behave in full is in `raptor.py`.
- **Repository configuration.** How `kn_repos` rows other than `arbol` are created and how the file configuration is applied to them is in `config.py` and `organizations.py`, which were not read.
- **Filesystem details.** Symlink following by `rglob`, case sensitivity of the `*.md` match, and behaviour for a directory whose name ends in `.md` were not established.
- **tree-sitter coverage.** The TypeScript probe covered the constructs listed in section 4 with the grammar versions installed in the repository's `.venv`. Other constructs and other grammar versions were not examined.
- **Git mirror refresh.** It runs between `refresh` and `ingest_code` and decides whether item 1 bites; its conditions and its 600-second throttle (`_MIRROR_REFRESH_SECONDS`, syncpass.py:91) were read only in passing (syncpass.py:94-133, 254-261).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code`
- `mycel_deprecated_v1:mycel/knowledge/store.py#refresh`
- `mycel_deprecated_v1:mycel/knowledge/store.py#detect`
- `mycel_deprecated_v1:mycel/knowledge/store.py#open_drifts`
- `mycel_deprecated_v1:mycel/knowledge/store.py#_scan_corpus`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_typescript`
- `mycel_deprecated_v1:mycel/syncpass.py#refresh_mirror`
- `mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked`
- `mycel_deprecated_v1:mycel/database.py#connect`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_derive`
