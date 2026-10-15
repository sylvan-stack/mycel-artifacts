---
role: derived
---
# v1 Mycel inventory: embedding and retrieval

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py`
- `mycel_deprecated_v1:mycel/macos_keychain.py`
- `mycel_deprecated_v1:mycel/knowledge/store.py`
- `mycel_deprecated_v1:mycel/database.py`
- `mycel_deprecated_v1:mycel/repo_identity.py`
- `mycel_deprecated_v1:mycel/cli.py`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py`
- `mycel_deprecated_v1:mycel/knowledge/local_embedder.py`
- `mycel_deprecated_v1:mycel/config.py`
- `mycel_deprecated_v1:mycel/retrieval.py`
- `mycel_deprecated_v1:mycel/syncpass.py`
- `mycel_deprecated_v1:mycel/scope.py`
- `mycel_deprecated_v1:mycel/organizations.py`
- `mycel_deprecated_v1:mycel/better_grep.py`
- `mycel_deprecated_v1:better_grep_entry.py`
- `mycel_deprecated_v1:mycel/locations.py`

What Mycel version 1 does, read from the deprecated source on 7 October 2026. It is evidence for the [specifications](../specs/README.md), not a description of Mycel 2. Historical evidence locators name the frozen source as `mycel_deprecated_v1:`. They are ordinary citations outside Source Ref declarations, because deprecated repositories are not indexed and Source Refs may target only enabled repositories.

Evidence read from the frozen source at `~/repos/sylvan-stack/mycel_deprecated_v1` (HEAD `b3125d0`, clean tree). Line numbers refer to that snapshot.

Read completely: `mycel/knowledge/embedder.py`, `mycel/knowledge/local_embedder.py`, `mycel/retrieval.py`, `mycel/better_grep.py`, `better_grep_entry.py`, `mycel/macos_keychain.py`.
Read in part, only to settle what the files above call: `mycel/cli.py` (`search_payload`, `_cmd_search`, `_cmd_embed`, `_cmd_status`, `main`, and the other `embed_pending` call sites), `mycel/knowledge/store.py` (DDL, `ingest`, `ingest_code`, overlay helpers, `list_repo_flags`, `status`), `mycel/syncpass.py`, `mycel/scope.py`, `mycel/database.py`, `mycel/config.py`, `mycel/locations.py`, `mycel/organizations.py`, `mycel/repo_identity.py`, and the two places in `mycel/knowledge/raptor.py` that embed summaries.

Nothing was executed against a database, the network, or the `mycel` / `better-grep` commands. Regular expressions and the `better-grep` argument parser were checked by copying them into a standalone Python snippet with fictional inputs. Statements marked "inferred" are conclusions drawn from the code, not behaviour that was observed running.

Vocabulary used below: a *chunk* is a row of `kn_chunks`; its `origin` is `code`, `corpus` (a section of a Markdown document) or `summary` (a RAPTOR summary). "Unified" search is `include_docs=True`; "code-only" is `include_docs=False`.

---

## 1. Embedding a chunk

### Voyage profile (external API)

| Item | Value | Location |
|---|---|---|
| Model | `voyage-code-3` | embedder.py:25 |
| Vector dimension | `1024` | embedder.py:26 |
| Endpoint | `POST https://api.voyageai.com/v1/embeddings` | embedder.py:27, :57 |
| Request body (JSON) | `{"input": [texts], "model": "voyage-code-3", "input_type": <type>, "output_dimension": 1024}` | embedder.py:54-56 |
| Request headers | `Authorization: Bearer <key>`, `Content-Type: application/json` | embedder.py:57-59 |
| Input types | `"document"` for chunks (default), `"query"` for search queries | embedder.py:50, :110, :213 |
| Batch size | 64 texts per request (`_BATCH`) | embedder.py:28, :203 |
| Timeout | 60 seconds per request (`urlopen(..., timeout=60)`) | embedder.py:61 |
| Retries / backoff | None. One attempt per batch. | embedder.py:60-65 |
| Client-side truncation | None. No character cap, no token count, no `truncation` field in the request. | embedder.py:54-56 |

- An empty input list returns `[]` without a request (embedder.py:52-53).
- An HTTP error status is turned into `RuntimeError("Voyage API error <code>: <first 300 chars of the body>")` (embedder.py:63-65). Other failures (`URLError`, timeouts, malformed JSON) are not caught and propagate as raised.
- The response is read as `data["data"]`, a list of items with `index` and `embedding`; each embedding is placed at `out[item["index"]]` (embedder.py:66-68). The length of the returned vector is not checked on this path.
- The only statement about truncation is a docstring: "the token-window truncation drops the tail" (embedder.py:142-143). The code sends no truncation setting, so any truncation is whatever the API does by default (inferred).

### API key

- The key is read from the macOS Keychain as a generic-password item with service `com.arbol.embedder` and account `voyage` (embedder.py:23-24, :41-45).
- The read uses `Security.framework` through `ctypes` (`SecItemCopyMatching` with `kSecClassGenericPassword`, `kSecReturnData`, `kSecMatchLimitOne`) and returns the bytes decoded as UTF-8, or `None` when the item does not exist (macos_keychain.py:192-227).
- `has_api_key()` is `bool(get_password(...))`; `_api_key()` raises `RuntimeError("Voyage API key not set — add it in Seqoya Lab → Retrieval.")` when absent (embedder.py:37-45).
- There is no environment variable or configuration-file source for the key in these files. `set_api_key()` exists (embedder.py:33-34) but nothing in this repository calls it.
- The key is read again for every request (`_api_key()` inside `embed`, embedder.py:58), and `has_api_key()` is a separate Keychain read.

### The text that is embedded (identity header)

`_embed_text(r)` builds the text from the chunk row (embedder.py:138-150):

| `origin` | Text sent to the embedder |
|---|---|
| `code` | `"{path} — {sym} ({symbol_kind or 'code'})\n{raw_text}"`, where `path` and `sym` are the two halves of `natural_key` split at the first `#` |
| `corpus` | `"{doc_path} › {natural_key}\n{raw_text}"`, where `doc_path` is `kn_documents.path` |
| anything else (in practice `summary`) | `raw_text` alone, no header |

- The separators are an em dash with spaces (` — `) for code and a single right angle quote with spaces (` › `) for documents.
- For code, the path in the header comes from `natural_key`, not from `kn_documents.path`. `ingest_code` writes `natural_key` as `"{relpath}#{symbol}"` (store.py:889), so the two agree.
- Fictional examples: a code chunk with `natural_key = "billing/invoice.py#compute_total"` and `symbol_kind = "function"` embeds as `billing/invoice.py — compute_total (function)` followed by a newline and the chunk text. A document chunk at `guides/billing.md` with `natural_key = "Billing > Refunds"` embeds as `guides/billing.md › Billing > Refunds` followed by a newline and the section text.
- `raw_text` itself is not modified; the header exists only in the text sent for embedding.
- Search queries are embedded as the bare query string, one text per request, with `input_type="query"` (embedder.py:103, :110).

### How the vector is stored

- Column: `kn_chunks.embedding public.vector(1024)` (store.py:95).
- Write: one statement per chunk, `UPDATE kn_chunks SET embedding = %s::public.vector WHERE id=%s` (embedder.py:215-216).
- The value is passed as text in the form `[f1,f2,...]`, each component rendered with `repr(float(x))` (embedder.py:72-74). No pgvector client adapter is used.
- Connections are opened with `autocommit=True` (database.py:77), so each chunk's vector is committed as soon as its `UPDATE` runs.
- The vector is cleared (`embedding = NULL`) by ingestion when a chunk's content hash changes: for document chunks by the upsert's `CASE` (store.py:322-323), for code chunks by the update (store.py:905). A renamed but unchanged document chunk keeps its vector.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embed`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_api_key`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#has_api_key`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_embed_text`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_vec_literal`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embed_pending`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_query_vec`
- `mycel_deprecated_v1:mycel/macos_keychain.py#get_password`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code`
- `mycel_deprecated_v1:mycel/database.py#connect`

---

## 2. Which chunks get embedded

### The pending predicate

`embed_pending` selects, in one `fetchall` (embedder.py:177-181):

```sql
SELECT c.id, c.raw_text, c.repo, c.origin, c.natural_key, c.symbol_kind, d.path AS doc_path
FROM kn_chunks c JOIN kn_documents d ON d.id=c.document_id
WHERE c.state='present' AND c.embedding IS NULL
  <scope>
ORDER BY c.id
```

- Default scope (`only_repos=None`): `AND c.repo NOT LIKE '%@%'` — every repository except overlay namespaces (embedder.py:168-169).
- With `only_repos=[...]`: `AND c.repo IN (...)` after canonicalising each name; with an empty list: `AND 1=0`, which selects nothing (embedder.py:170-176).
- There is no filter on `origin`, `tier`, `stale`, or `meta`. A `summary` chunk with a NULL vector is selected like any other.
- No caller in this repository passes `only_repos` (the four call sites are cli.py:105, :119, :246, :537).

### Profile routing

- Profiles and the enabled flag are read once per pass from `SELECT * FROM kn_repos` (embedder.py:164-167). The profile of a row is `embedder_profile or "voyage"`.
- For each pending chunk the *base* repository name is used (the part before `@`, after `canonical_repo`, which maps the base `Arbol` to `arbol`) (embedder.py:77-82, :187).
- A repository with no `kn_repos` row is treated as profile `voyage` and as enabled (`prof_of.get(..., "voyage")`, `enabled_of.get(..., True)`) (embedder.py:187-188).
- Usability is decided once per pass: `voyage_ok = has_api_key()`, `local_ok = local_embedder.is_available()` (embedder.py:182).
- A chunk is queued when `voyage_ok` for profile `voyage`, or `local_ok` for profile `local`. Any other profile string is never queued. Unqueued chunks are counted in `skipped[<profile>]` (embedder.py:191-195).
- All `voyage` jobs run first, then all `local` jobs (embedder.py:199). Batch step is 64 for `voyage` and 16 for `local` (embedder.py:203).
- Every text of a batch is sent with `input_type="document"` (embedder.py:213).
- An exception from the embedder (API error, provider down) is not caught in `embed_pending`; it ends the pass. Vectors already written stay written.

### Disabled repositories

- A chunk whose base repository has `mycel_enabled` false is not embedded and is counted in `skipped["disabled"]` (embedder.py:188-190).
- Disabled repositories are still counted by `pending_count` and are still searchable: no search query in embedder.py reads `mycel_enabled`.

### Overlay namespaces (retired feature, three lines)

- An overlay namespace (`repo@branch`) inherits the profile and the enabled flag of its base repository (embedder.py:77-89, :187-188).
- The default pass excludes overlays (`c.repo NOT LIKE '%@%'`); they are embedded only when named in `only_repos` (embedder.py:168-176).
- No caller in this repository passes `only_repos`, so the v1 CLI never embeds overlay chunks.

### Stop request

- A module-level `threading.Event` (`_stop`) is checked before each batch. When set, the pass returns early with `"stopped": True` and writes the activity row if anything was embedded (embedder.py:131, :205-211).
- `request_stop()` sets the event (embedder.py:134-135). Nothing in this repository calls it.

### `pending_count` and `embedded_count`

- `pending_count(conn, repo=None)`: `SELECT count(*) n FROM kn_chunks WHERE state='present' AND embedding IS NULL`, plus `AND repo=%s` when a repository is given (embedder.py:113-118). Without a repository it counts every repository, including overlays and disabled repositories, so it can exceed what `embed_pending` would process.
- `embedded_count(conn)`: `SELECT count(*) n FROM kn_chunks WHERE state='present' AND embedding IS NOT NULL`, always global (embedder.py:121-123).

### What `embed_pending` returns

```
{"embedded": <chunks written>, "total": <chunks queued>, "skipped": {<"disabled" | profile name>: <count>}}
```

- `"stopped": True` is added when the stop event ended the pass (embedder.py:206).
- `total` counts queued chunks only; skipped chunks are not part of it (embedder.py:196).
- `progress(done, total)` is called after each batch when a callback is given (embedder.py:227-228).
- When at least one chunk was embedded, one activity row of kind `embed` is written with the result plus an `items` list holding one entry per embedded chunk: `{"repo", "path", "detail": natural_key, "action": "embedded"}` and, for non-overlay `code`/`corpus` chunks, an absolute `file_path` (embedder.py:217-225, :229-233).

### Commands that run the pass

- `mycel embed` takes no arguments. It connects, applies the configuration file, calls `embed_pending(conn, progress=...)`, prints progress lines `  embed <done>/<total>` on stderr and the result as indented JSON on stdout, and returns 0 (cli.py:115-124, :755-756).
- `mycel sync` and `mycel pull` call it when the sync pass reports pending chunks and `--no-embed` is absent (cli.py:104-108, :536-540). `mycel overlay add|refresh` calls it unless `--no-embed` (cli.py:243-251).
- `mycel status` prints `store.status(conn, repo)` plus `"embedder": {"has_key", "embedded", "pending", "local_model"}` (cli.py:172-184). `embedded` and `pending` are the global counts; the `--repo` argument (default `Arbol`) does not narrow them. `local_model` is `local_embedder.status()`.

### RAPTOR summaries are embedded outside this pass

- The RAPTOR build and regeneration embed each summary directly with `embedder.embed([text], input_type="document")` — the Voyage function — and write the vector themselves (raptor.py:282-284, :395-399). `raptor.py` contains no reference to the repository profile.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embed_pending`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_base_repo`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_profile_for`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#pending_count`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embedded_count`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#request_stop`
- `mycel_deprecated_v1:mycel/repo_identity.py#canonical_repo`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_embed`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_status`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_sync`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_overlay`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_pull`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#build_tree`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#regen_stale`

---

## 3. Local profile

- `local_embedder.py` holds no model. It is an HTTP client of a separate provider process, plus file management for the model files (local_embedder.py:1-11).
- Model name `Qwen3-Embedding-0.6B`, dimension `1024` (local_embedder.py:19-20).
- Provider address: environment `MYCEL_EMBEDDER_URL`, else `providers.embedder_url` in the configuration file, else `http://127.0.0.1:7331` (local_embedder.py:30-35).
- Embedding: `POST {url}/embed` with JSON `{"texts": [...], "input_type": "document"|"query"}`, at most 64 texts per request, timeout 600 seconds; the reply is read as `{"vectors": [...]}` (local_embedder.py:27, :112-131). The first returned vector's length must equal 1024, else `RuntimeError` (local_embedder.py:132-133).
- Health: `GET {url}/healthz`, timeout 2 seconds, read as `{"loaded": bool}`; any exception yields `{"up": False, "loaded": None, "url": ...}` (local_embedder.py:50-57).
- Availability check `is_available()`: both files `model_quantized.onnx` and `tokenizer.json` exist in the model directory. It does not contact the provider (local_embedder.py:23-26, :44-47).
- Model directory: environment `ARBOL_LOCAL_EMBEDDER_DIR`, else `~/Library/Application Support/Arbol/models/Qwen3-Embedding-0.6B` (local_embedder.py:38-41).
- `download()` fetches the two files from `https://huggingface.co/onnx-community/Qwen3-Embedding-0.6B-ONNX/resolve/main` with `urllib`, writing to `<name>.part` and renaming on completion (local_embedder.py:22-26, :71-100). No command in the files read calls it.
- Errors: missing model files, an HTTP error from the provider, and an unreachable provider each raise `RuntimeError`; the unreachable message names `python -m mycel_embedder serve` (local_embedder.py:108-110, :120-130).
- At query time a `RuntimeError` from the local provider is logged as a warning and the search continues without a query vector; missing model files give the same result without a log line (embedder.py:99-107).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/local_embedder.py#provider_url`
- `mycel_deprecated_v1:mycel/knowledge/local_embedder.py#model_dir`
- `mycel_deprecated_v1:mycel/knowledge/local_embedder.py#is_available`
- `mycel_deprecated_v1:mycel/knowledge/local_embedder.py#provider_status`
- `mycel_deprecated_v1:mycel/knowledge/local_embedder.py#status`
- `mycel_deprecated_v1:mycel/knowledge/local_embedder.py#download`
- `mycel_deprecated_v1:mycel/knowledge/local_embedder.py#embed`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_query_vec`
- `mycel_deprecated_v1:mycel/config.py#provider_embedder_url`

---

## 4. Lexical index

### DDL

```sql
CREATE INDEX IF NOT EXISTS kn_chunks_bm25 ON kn_chunks
USING bm25 (id, raw_text, natural_key) WITH (key_field='id')
```

(embedder.py:313-314)

- Indexed columns: `id` (the key field, a text identifier), `raw_text`, `natural_key`. No tokenizer or per-field options are given.
- The index is not part of the schema DDL in `store.py`. It is created by `ensure_bm25_index`, which runs the statement at the start of every `code_search` and every `doc_search` call (embedder.py:269, :317-323, :440).
- Any exception from the statement is swallowed and the function returns `False`; the return value is not used by the callers.
- No statement in the repository creates the `pg_search` extension.

### How lexical queries are built

Unified / code search (embedder.py:486-493):

```sql
SELECT c.id FROM kn_chunks c
WHERE c.id @@@ paradedb.match('raw_text', %s)
  AND c.origin = ANY(%s) AND c.state='present'
  AND ((c.origin='code' AND <code scope>) OR (c.origin <> 'code' AND c.repo = ANY(%s)))
ORDER BY paradedb.score(c.id) DESC LIMIT %s
```

Docs-only search (embedder.py:281-285):

```sql
SELECT c.id FROM kn_chunks c
WHERE c.id @@@ paradedb.match('raw_text', %s)
  AND c.origin = ANY(%s) AND c.state='present' AND c.repo=%s
ORDER BY paradedb.score(c.id) DESC LIMIT %s
```

- Only the field `raw_text` is matched. `natural_key` is in the index but no query uses it.
- The query text is passed as one bound parameter to `paradedb.match`. Mycel does no tokenising, quoting, or escaping of its own.
- Origins: `("code",)` for code-only; `("code", "corpus", "summary")` for unified; `["corpus", "summary"]` for docs-only (embedder.py:270, :450-451).
- `LIMIT` is the candidate pool, `max(k, 20)` (embedder.py:272, :442).
- Any exception from the lexical query sets the lexical list to empty and the search continues (embedder.py:286-287, :494-495).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#ensure_bm25_index`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#doc_search`

---

## 5. Dense index

### Column and index

```sql
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;
ALTER TABLE kn_chunks ADD COLUMN IF NOT EXISTS embedding public.vector(1024);
CREATE INDEX IF NOT EXISTS kn_chunks_embedding ON kn_chunks USING hnsw (embedding public.vector_cosine_ops);
```

(store.py:94-95, :98)

- Type `vector(1024)`, access method `hnsw`, operator class `vector_cosine_ops`. No `WITH (...)` parameters, and no session setting such as `hnsw.ef_search` appears anywhere in the repository.
- It is one column and one index for all repositories and both profiles. Vectors from `voyage-code-3` and from `Qwen3-Embedding-0.6B` are stored side by side; the `repo` predicate is the only thing that separates them.
- Similarity is always computed as `1 - (embedding <=> query)`, cosine similarity.

### Query shapes

Code arm of `code_search` — ordered by the distance operator, so the HNSW index can serve it (embedder.py:476-480):

```sql
SELECT c.id, c.repo, c.symbol_kind, 1-(c.embedding <=> %s::public.vector) AS cos
FROM kn_chunks c
WHERE c.origin='code' AND c.state='present' AND c.embedding IS NOT NULL AND <code scope>
ORDER BY c.embedding <=> %s::public.vector LIMIT <pool>
```

`<code scope>` is (embedder.py:447-448):

```sql
c.repo = ANY(<repos>) AND NOT (c.repo = <repo> AND c.document_id IN
  (SELECT id FROM kn_documents WHERE repo = <repo> AND path = ANY(<shadowed paths>)))
```

Without an overlay, `<repos>` is `[repo]` and `<shadowed paths>` is empty.

Document arm of `code_search` and the dense arm of `doc_search` — an exact scan through a materialized common table expression, ordered by the computed value (embedder.py:275-279, :539-546):

```sql
WITH t AS MATERIALIZED (
  SELECT c.id, ..., 1-(c.embedding <=> %s::public.vector) AS cos
  FROM kn_chunks c [JOIN kn_documents d ON d.id=c.document_id]
  WHERE c.origin = ANY(%s) AND c.state='present' AND c.embedding IS NOT NULL AND c.repo=%s)
SELECT ... FROM t ORDER BY cos DESC LIMIT %s
```

The comment beside it gives the reason: "the HNSW scan under-returns (to zero) under selective filters" (embedder.py:531-532).

Bridge expansion computes `1-(p.embedding <=> query)` for the parent code chunks of one document section and orders by it (embedder.py:355-367; see section 6).

### Filters on dense queries

- `state='present'` and `embedding IS NOT NULL` on every dense query.
- `origin` restricted per arm. `repo` restricted to the requested repository (code arm: plus its overlay namespace; document arm: one query per document repository).
- No filter on `stale`, `tier`, `role`, or `meta`.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#doc_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_bridge_expand`

---

## 6. Search algorithm

Two functions are reachable from the CLI:

- `code_search(conn, query, k=10, *, repo="Arbol", rrf_k=60, overlay=None, include_docs=False)` — used for `mycel search` (unified, `include_docs=True`) and `mycel search --only code` (`include_docs=False`) (embedder.py:408-409; retrieval.py:167-168).
- `doc_search(conn, query, k=10, *, repo="Arbol", rrf_k=60)` — used for `mycel search --only docs` (embedder.py:265; cli.py:52-54).

A third function, `search` (embedder.py:239-262), has no caller in this repository.

### 6.1 Setup common to `code_search`

1. `repo = canonical_repo(repo)` (embedder.py:430).
2. `ensure_bm25_index(conn)` (embedder.py:440).
3. Candidate pool: `pool = max(k, 20)` (embedder.py:442).
4. Code scope: `[repo]`, or `[repo, "repo@branch"]` with the overlay's shadowed paths (embedder.py:386-397, :443).
5. Document scope (`_doc_scope`): `[repo]` when code-only or when `repo == "mycel"`; otherwise `[repo, "mycel"]`. The name `mycel` is the constant `SHARED_ARTIFACT_REPO` (embedder.py:383, :400-405, :444).
6. Query vector for the requested repository. It is computed only if at least one chunk of the searched origins in the code scope has a vector (`SELECT 1 ... WHERE origin = ANY(...) AND embedding IS NOT NULL AND repo = ANY(...) LIMIT 1`; this probe does not test `state`) (embedder.py:456-459). `_query_vec` then returns `None` when the profile's embedder is unusable (embedder.py:92-110):
   - profile `local`: `None` if the model files are absent, or if the provider call raises `RuntimeError`;
   - any other profile: `None` if there is no API key; otherwise `embed([query], input_type="query")[0]`, and an exception from that call is not caught.
7. Query vector for each other document repository (embedder.py:460-472): the same vector if its profile equals the requested repository's profile; otherwise, if it has an embedded `corpus` or `summary` chunk, a second query embedding with its own profile; otherwise none.
8. Dense code candidates: the code-arm query of section 5, `LIMIT pool`. Skipped when there is no query vector (embedder.py:474-481).
9. Lexical candidates: the query of section 4, `LIMIT pool` (embedder.py:484-495).
10. Ranks: `dr[id]` and `br[id]` are the zero-based positions in the dense and lexical lists (embedder.py:498-499).

### 6.2 Query classification

```python
nl_query = not re.match(r"^[\w.#/-]+$", query.strip())
```

(embedder.py:500)

- A query is *identifier-shaped* when, after stripping, it consists only of word characters (`\w`, Unicode-aware), `.`, `#`, `/` and `-`. Everything else is *natural language*.
- Any whitespace inside the query makes it natural language. So do `:`, `@`, `(`, `)` and similar characters.
- Fictional examples: `renewSession`, `auth/session.ts#renew`, `a-b.c` and the single plain word `payments` are identifier-shaped. `how does renewal work`, `Foo::bar`, `foo(bar)` and `@scope/pkg` are natural language.

The route actually taken is decided by a second condition (embedder.py:520):

```python
if nl_query and (code_rows or include_docs):   # natural-language route
else:                                           # rank-fusion route
```

A natural-language query in code-only mode that got no dense code rows therefore runs through the rank-fusion route.

### 6.3 Down-weights: which candidates are marked

Computed once for the union of dense and lexical candidates, when that union is not empty (embedder.py:504-517):

```python
want_tests = re.search(r"\b(tests?|specs?|e2e|mocks?|fixtures?)\b", query, re.I)
want_gen   = re.search(r"\b(types?|schemas?|graphql|gql|codegen|generated)\b", query, re.I)
```

Path patterns, matched in SQL with `d.path ~ <pattern>` against `kn_documents.path`:

```
test:      (\.(spec|test)\.[jt]sx?$)|(/__tests__/)|((^|/)test_[^/]*\.py$)|(conftest\.py$)|(_test\.(py|go)$)
generated: (\.generated\.[jt]sx?$)|((^|/)gql/types\.ts$)
```

(embedder.py:330-331, :337)

- `test_ids` = candidates whose path matches the test pattern, unless `want_tests`.
- `gen_ids` = candidates whose path matches the generated pattern, unless `want_gen`.
- When both words are wanted the SQL is skipped and both sets are empty (embedder.py:510).
- Checked on fictional paths: `src/a.spec.ts`, `src/a.test.jsx`, `src/__tests__/a.ts`, `tests/test_a.py`, `test_a.py`, `tests/a_test.go`, `pkg/conftest.py` match the test pattern. `__tests__/a.ts` (no leading directory), `tests/helpers.py`, `src/a.e2e-spec.ts`, `src/a.spec.mts`, `e2e/login.cy.ts` do not. `src/x.generated.ts`, `src/gql/types.ts`, `gql/types.ts` match the generated pattern; `src/gql/types.tsx` and `src/graphql/types.ts` do not.
- Because of `\b`, the query words must stand alone: fictional `renew test` and `Spec for renewal` count as asking for tests; `test_renew` and `renewTest` do not.

Factors:

| Down-weight | Applies to | Natural-language route | Rank-fusion route | Location |
|---|---|---|---|---|
| Structural chunk: `symbol_kind` in `("module", "markup", "style", "file")` | dense code candidates only | × 0.9 | × 0.75 | embedder.py:523-524, :588-589 |
| Test path (`test_ids`) | see below | × 0.93 (`_TEST_DISCOUNT_NL`) | × 0.85 (`_TEST_DISCOUNT_RRF`) | embedder.py:332-333, :525-526, :590-591 |
| Generated path (`gen_ids`) | dense code candidates | × 0.93 (`_GEN_DISCOUNT_NL`) | not applied | embedder.py:338, :527-528 |

- Factors multiply when several apply.
- On the natural-language route all three are applied only inside the loop over dense code rows. Chunks that enter through the bridge or the lexical tail receive none of them.
- On the rank-fusion route the structural factor depends on a `symbol_kind` lookup built from the dense code rows only (`kinds`, embedder.py:584), so a lexical-only candidate never receives it. The test factor is applied to any candidate in `test_ids`.

### 6.4 Natural-language route, step by step

1. **Direct scores.** For every dense code row, `score = cos`, multiplied by the down-weights of 6.3. `direct` is the set of these chunk ids (embedder.py:521-530).
2. **Document sections.** For each document repository that has a query vector, fetch the top `_BRIDGE_DOCS = 8` chunks by exact cosine, with origins `["corpus", "summary"]` in unified mode or `["corpus"]` in code-only mode. Merge the lists, sort by cosine descending, keep the top 8 overall (embedder.py:347, :533-547).
3. **Bridge.** For each of those sections, in descending cosine order (embedder.py:548-566):
   - Build the label `{"doc": "<path> › <natural_key>", "repo": <section repo>, "stale": <chunk stale flag>, "heartwood": bool(meta.heartwood)}`.
   - If the section's repository is not the requested repository, do nothing more with it (shared `mycel` sections never bridge).
   - Otherwise call `_bridge_expand` (below) and, for each returned code chunk, let `s = section_cos × 0.92` (`_BRIDGE_DISCOUNT`, embedder.py:326):
     - chunk already in `direct`: if `s` is greater than its current score, record the label as its `via` unless one is already recorded; then `score = max(score, s) + 0.05` (`_BRIDGE_AGREEMENT`, embedder.py:327);
     - chunk not in `direct`: if `s` is greater than its current score (0 if none), `score = s` and `via = label`.
4. **Documents as results (unified only).** `best_code = max(scores)` taken after the bridge step, or `0.0` if there are no scores. For each of the top-8 sections: skip it if the basename of its path is `INDEX.md` or `README.md` (`_DOC_ROUTERS`, exact match); otherwise it becomes a result with `score = cos` when `cos >= best_code + 0.03` (`_DOC_MARGIN`) or when the score dictionary is empty at that moment (embedder.py:340, :345, :567-577). `best_code` is computed once, before the loop; documents added by the loop do not raise it.
5. **Rescue tail.** `floor = min(scores) - 0.001`, or `1.0 - 0.001` if there are no scores. Each lexical candidate not yet scored gets `floor - i × 0.0005`, where `i` is its zero-based position in the whole lexical list (embedder.py:578-582).
6. **Order and cut.** Sort all scored ids by score descending. In unified mode, if step 4 added any document, walk the list and drop every step-4 document after the second (`_DOC_CAP = 2`, embedder.py:344, :594-603). Then keep the first `k` (embedder.py:604).

#### `_bridge_expand`

One query per document section, two arms joined with `UNION ALL`, ordered by the code chunk's own cosine to the query, `LIMIT 3` (`_BRIDGE_CAP`) (embedder.py:339, :350-367):

- arm 1: `kn_derivations` rows with `child_id = <section id>` and `kind IN ('declared','asserted')` whose `parent_id` is a chunk with `origin='code'`, `state='present'`, `embedding IS NOT NULL`;
- arm 2: rows with the same child and kinds whose `parent_id` is a `kn_documents` row with `source_type='code'`; every `code` chunk of that document that is present and embedded.

Observed properties:

- The cap of 3 is per section, across both arms together.
- The code chunk's own cosine (`own`) decides which three are kept. It is not used in the score; the score is the section's cosine × 0.92.
- Edges of kind `generated` (the RAPTOR member-to-summary edges) are not followed, so a summary chunk among the sections never bridges.
- The query has no repository predicate and no overlay shadowing on the parent chunks.
- With at most 8 sections and 3 chunks each, the bridge can contribute up to 24 code chunks.

### 6.5 Rank-fusion route

For every id in the union of dense and lexical candidates (embedder.py:583-592):

```
score = 1/(rrf_k + dense_rank0 + 1)   if in the dense list, else 0
      + 1/(rrf_k + bm25_rank0 + 1)    if in the lexical list, else 0
```

- `rrf_k = 60`; both lists have weight 1. A first-place hit in one list contributes `1/61`.
- Then × 0.75 for a structural chunk (dense candidates only) and × 0.85 for a test path.
- No bridge, no document sections, no rescue tail, no document margin, no document cap, and `via` is always `None`.
- In unified mode the dense list holds code chunks only, while the lexical list holds `code`, `corpus` and `summary` chunks of the requested repository and of `mycel`. A document or summary can therefore score through the lexical term only.
- The result is sorted by score descending and cut to `k` (embedder.py:594, :604).

### 6.6 How documents compete with code (summary)

| Mode and route | How a document or summary chunk can become a result |
|---|---|
| Unified, natural-language | (a) through the margin gate: cosine at least 0.03 above the best code score after bridging, not a router file, at most 2 such results; (b) through the rescue tail as a lexical hit, with no margin, no cap and no router exclusion |
| Unified, rank-fusion | as a lexical candidate, with its lexical term only |
| Code-only, either route | never. Document sections are used only as bridges, and only `corpus` sections |
| Docs-only (`doc_search`) | every result is a `corpus` or `summary` chunk |

Router files (`INDEX.md`, `README.md`) are excluded only at the margin gate. They still occupy places among the 8 sections, still bridge, can still arrive through the rescue tail or the rank-fusion route, and are not excluded by `doc_search`.

### 6.7 RAPTOR summary chunks in search

- A summary is a `kn_chunks` row with `origin='summary'`, `natural_key = "raptor/L<tier>/<id>"`, attached to one synthetic document per repository with path `synthetic/raptor` (raptor.py:34, :69-80, :106-114).
- Unified search includes summaries in the lexical candidates and among the 8 document sections; they can become results through the margin gate, the rescue tail, or the rank-fusion route. They never bridge (see 6.4).
- Code-only search excludes them entirely (embedder.py:451, :533).
- `doc_search` searches `corpus` and `summary` together.
- A summary result has `symbol = None`, and `read_path = None` with `unavailable_reason = "synthetic search result"` (retrieval.py:88-89).
- No query looks at `tier`.

### 6.8 What is filtered out, and how stale / heartwood are flagged

Filtered:

- chunks whose `state` is not `'present'` (every candidate query, the bridge parents, the `documented_in` children);
- chunks without a vector, from the dense arms only — they remain reachable through the lexical arm;
- chunks outside the repository scope; base chunks under overlay-covered paths when an overlay is given.

Not filtered anywhere in the search code: `stale`, `meta.heartwood`, `meta.generated`, `tier`, `role`, and the repository's `mycel_enabled` flag.

Flags on results:

- A `code_search` result has no `stale` key and no `heartwood` key, including when the result is itself a document or summary chunk (embedder.py:623-636).
- Stale and heartwood appear only inside annotations: `via.stale`, `via.heartwood`, and `documented_in[].stale`.
- A `doc_search` result has `"stale"` (the column) and `"heartwood"` (`bool(meta.heartwood)`) (embedder.py:303-307).

### 6.9 `via` and `documented_in`

`via` (natural-language route only):

- shape `{"doc": "<path> › <natural_key>", "repo": <repo>, "stale": <bool>, "heartwood": <bool>}` or `None` (embedder.py:549-551, :633);
- set for a bridge-only chunk to the label of the highest-cosine section that reached it;
- set for a chunk that also has a direct score only when a section's `cos × 0.92` exceeded the chunk's score at that moment; the first such label is kept.

`documented_in`:

- computed only when `nl_query` is true (the classification, not the route taken); otherwise `[]` (embedder.py:621-622);
- one query per result (embedder.py:370-380):

```sql
SELECT dc.natural_key, dd.path, dc.stale FROM kn_derivations dv
JOIN kn_chunks dc ON dc.id=dv.child_id JOIN kn_documents dd ON dd.id=dc.document_id
WHERE dv.parent_id IN (<chunk id>, <chunk's document id>) AND dv.kind IN ('declared','asserted')
  AND dc.origin='corpus' AND dc.state='present' LIMIT 2
```

- shape: a list of at most two `{"doc": "<path> › <natural_key>", "stale": <bool>}`;
- the query has no `ORDER BY`, so which two are returned is up to the database;
- an entry whose `doc` string equals `via.doc` is removed;
- it runs for every result, including document and summary results.

### 6.10 `k`, ordering, de-duplication, return value

- `k` defaults: 10 in `code_search`, `doc_search` and `retrieval.search`; 12 for `mycel search` (`--k`, cli.py:738); 5 for the `better-grep` tail.
- `retrieval.search` rejects `k` outside 1..100 with `ValueError("k must be between 1 and 100")` (retrieval.py:140-141). `doc_search` is called directly for `--only docs` and has no such check.
- Ordering: score descending. Python's sort is stable, so ties keep the insertion order of the score dictionary. On the natural-language route that order is deterministic (dense rank, then bridge, then documents, then lexical order). On the rank-fusion route and in `doc_search` the ids are inserted by iterating a Python `set` of strings (embedder.py:292, :585), so the order of equal scores is not fixed by the code (inferred: string hashing varies per process).
- De-duplication: scores are keyed by chunk id, so a chunk appears once. There is no de-duplication by file, path or symbol.
- Hydration reads `id, repo, document_id, natural_key, raw_text, lang, symbol_kind, origin, line_start, line_end` and the document path for the kept ids (embedder.py:611-614).
- Return value: `{"results": [...], "dense": len(dense code candidates), "bm25": len(lexical candidates), "timings": {...}}` (embedder.py:639-640). `dense` does not count document sections.
- Timing keys, in milliseconds: `bm25_index_ms`, `query_embedding_ms`, `dense_sql_ms`, `bm25_sql_ms`, `ranking_bridge_ms`, `hydrate_ms` (absent when there are no results), `total_ms` (embedder.py:431-441, :473, :482, :496, :605-609, :637-638).

### 6.11 `doc_search` (docs-only)

1. `ensure_bm25_index`; origins `["corpus", "summary"]`; `pool = max(k, 20)`; only the requested repository — the shared `mycel` repository is not added (embedder.py:268-272).
2. Dense: the exact materialized query of section 5, top `pool`. Empty when there is no query vector (embedder.py:273-279).
3. Lexical: the docs-only query of section 4, top `pool`; empty on any exception (embedder.py:280-287).
4. Fusion: `1/(60 + rank0 + 1)` from each list, summed; sort descending; keep `k` (embedder.py:288-293).
5. Result fields: `id`, `path`, `natural_key`, `origin`, `stale`, `heartwood`, `preview` (first 240 characters plus `…` when longer). The fused score is not returned (embedder.py:298-307).
6. Return value: `{"results": [...], "dense": <n>, "bm25": <n>}` — no `timings` (embedder.py:308).
7. No bridge, no down-weights, no router exclusion, no query classification.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#doc_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_bridge_expand`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_documented_in`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_overlay_scope`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_doc_scope`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_query_vec`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_profile_for`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#ensure_bm25_index`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#_insert_summary`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#_summary_doc_id`
- `mycel_deprecated_v1:mycel/retrieval.py#search`
- `mycel_deprecated_v1:mycel/retrieval.py#_read_location`

---

## 7. Result contract (`retrieval.py`)

### Payload

Built by `_payload` (retrieval.py:111-129); `transport` is added afterwards by the CLI (cli.py:63).

| Field | Value |
|---|---|
| `schema_version` | `2` (`SCHEMA_VERSION`, retrieval.py:15) |
| `repo` | the canonical repository key that was searched |
| `overlay` | the overlay branch name, or `null` |
| `results` | list of results (below) |
| `dense` | integer, from the search function (`0` when missing) |
| `bm25` | integer, from the search function (`0` when missing) |
| `timings` | the timing dictionary of 6.10; `{}` for docs-only |
| `freshness` | see below; `{"checked": false, "refreshed": false}` when no freshness dictionary is passed |
| `transport` | `"cli"` — set in `cli.search_payload`, not in `retrieval.py` |

When the repository name resolves to a configured organization, the CLI returns a different top level instead (cli.py:35-44):

```
{"schema_version": 2, "organization": <name>, "transport": "cli",
 "repositories": [<one full payload per member repository>]}
```

Each member is searched separately with the same `k`; results are not merged. An overlay together with an organization raises `ValueError("an organization search requires per-repository overlay selection")`.

### `schema_version` values

| Value | Where |
|---|---|
| `2` | every search payload, for both result shapes (unified/code and docs-only) (retrieval.py:121) |
| `2` | the organization wrapper, as a literal (cli.py:40) |
| `1` | a successful `symbol_read` reply (retrieval.py:289); its error replies carry none |
| `{"search": 2, "symbol_read": 1}` | reported by `capabilities()` under `schema_versions` (retrieval.py:176) |

No code path produces a search payload with version 1.

### One result — unified and code-only (`code_search`)

| Field | Value | Location |
|---|---|---|
| `id` | chunk id | embedder.py:624 |
| `path` | `kn_documents.path`, relative | :624 |
| `natural_key` | chunk natural key | :624 |
| `origin` | `code`, `corpus` or `summary` | :625 |
| `repo` | the namespace the chunk is stored under | :625 |
| `overlay` | `true` when the chunk belongs to the overlay namespace | :626 |
| `symbol` | for `code`: the part of `natural_key` after the first `#`; otherwise `null` | :627 |
| `lang` | chunk language, may be `null` | :628 |
| `symbol_kind` | chunk kind, may be `null` | :628 |
| `line_start`, `line_end` | source line span, may be `null` | :629 |
| `score` | `round(score, 5)`; a cosine-based value on the natural-language route, a rank-fusion value on the other | :630 |
| `dense_rank` | 1-based rank among dense code candidates, or `null` | :631 |
| `bm25_rank` | 1-based rank among lexical candidates, or `null` | :632 |
| `via` | label dictionary or `null` (6.9) | :633 |
| `documented_in` | list (6.9) | :634 |
| `preview` | first 240 characters of `raw_text`, plus `…` when longer | :635 |
| `read_path` | absolute path of the file, or `null` | retrieval.py:102 |
| `readable` | `read_path is not None` | retrieval.py:103 |
| `unavailable_reason` | present only when there is a reason | retrieval.py:104-107 |

### One result — docs-only (`doc_search`)

`id`, `path`, `natural_key`, `origin`, `stale`, `heartwood`, `preview`, plus `read_path`, `readable` and optionally `unavailable_reason`. There is no `repo`, `score`, rank, line span, `via` or `documented_in`.

### `read_path` and `readable`

`_read_location` (retrieval.py:66-108):

1. The hit's repository is `hit["repo"]`, or the requested repository when the hit has none. Its base name (before `@`) selects the configured roots; if it differs from the requested base, that repository's flags are loaded separately (retrieval.py:83-86).
2. By origin:
   - `summary`: no path; reason `"synthetic search result"`.
   - `code`: root is the repository's code root (`syncpass.code_root`), or the overlay worktree when an overlay is given. A missing overlay root gives reason `"overlay worktree is unavailable"`.
   - `corpus`: root is the repository's artifact root (`syncpass.artifact_root`).
   - any other origin: reason `"search origin is not filesystem-readable: <origin or 'unknown'>"`.
3. `_resolved_file(root, rel)` (retrieval.py:53-63): the root is expanded and resolved with `realpath`; then
   - empty or absolute `rel` → `"indexed path is not a relative file path"`;
   - `realpath(root/rel)` not equal to the root and not under `root + separator` → `"indexed path escapes its configured root"`;
   - not an existing regular file → `"indexed source no longer exists"`;
   - otherwise the resolved absolute path (symbolic links resolved).
4. `readable` is true exactly when a path was produced.

### `freshness`

- Not requested: `{"checked": false, "refreshed": false}` (retrieval.py:142).
- Requested: `{"checked": true, "refreshed": <any repository refreshed>, "coalesced": <any repository coalesced>, "repos": {<repo>: {"refreshed": bool, "coalesced": bool}}, "wait_ms": <milliseconds spent on the check and refresh>}` (retrieval.py:163-166).

### `capabilities(conn=None)`

(retrieval.py:172-192)

| Field | Value |
|---|---|
| `protocol_version` | `1` |
| `schema_versions` | `{"search": 2, "symbol_read": 1}` |
| `operations` | `["code_search", "unified_search", "symbol_read"]` |
| `index_available` | without a connection `false`; with one, whether any chunk with `state='present'` exists; `false` if the query raises |
| `dense_available` | without a connection `null`; with one, whether any present chunk has a vector (any repository) |
| `lexical_fallback` | `true`, constant |

Nothing in this repository calls `capabilities()`.

### Also in this file: `symbol_read`

`symbol_read(conn, *, path, symbol, repo, overlay=None, context_lines=2, max_bytes=5 MiB)` (retrieval.py:195-295) looks up `code` chunks of one file whose `natural_key` equals the wanted symbol or ends with `#<symbol>` or `.<symbol>`, requires exactly one match (exact matches preferred), and returns the file's lines for that chunk plus up to 50 context lines each side. Success reply: `ok`, `schema_version: 1`, `encoding: "utf-8"`, `contents`, `path`, `symbol`, `canonical_symbol`, `definition_start_line`, `definition_end_line`, `start_line`, `end_line`, `truncated`, `overlay`. Failure replies: `{"ok": false, "error": ..., ["candidates": up to 20], ["suggestion": ...]}`. Nothing in this repository calls it.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/retrieval.py#_payload`
- `mycel_deprecated_v1:mycel/retrieval.py#_read_location`
- `mycel_deprecated_v1:mycel/retrieval.py#_resolved_file`
- `mycel_deprecated_v1:mycel/retrieval.py#_code_root_for_view`
- `mycel_deprecated_v1:mycel/retrieval.py#_overlay_root`
- `mycel_deprecated_v1:mycel/retrieval.py#_repo_flags`
- `mycel_deprecated_v1:mycel/retrieval.py#search`
- `mycel_deprecated_v1:mycel/retrieval.py#capabilities`
- `mycel_deprecated_v1:mycel/retrieval.py#symbol_read`
- `mycel_deprecated_v1:mycel/cli.py#search_payload`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#doc_search`
- `mycel_deprecated_v1:mycel/syncpass.py#code_root`
- `mycel_deprecated_v1:mycel/syncpass.py#artifact_root`

---

## 8. Fresh-on-read

### Entry through the CLI

`search_payload` (cli.py:22-64) does, in order:

1. Resolve the repository and overlay: `--repo` if given, else `scope.resolve(paths)`; `--overlay` overrides the overlay.
2. If the name is an organization, fan out (section 7) and return.
3. Open a database connection and call `config.load_apply(conn, force=True)`, which copies the per-repository settings of the configuration file into `kn_repos`. A malformed file prints `warning: ...` on stderr and the search continues.
4. `--only docs`: call `embedder.doc_search` and `retrieval._payload` directly. `retrieval.search` is not called.
5. Otherwise: `retrieval.search(conn, query, repo=..., overlay=..., k=k, code_only=(only == "code"), freshness=not no_fresh)`.
6. Close the connection; set `transport = "cli"`.

`mycel search` prints the payload as indented JSON and returns 0 (cli.py:67-73). An exception is printed as `{"error": "<message>"}` on stderr with exit code 1; an interrupt returns 130 (cli.py:877-884).

### When freshness is checked

| Invocation | Freshness check |
|---|---|
| `mycel search <q>` | yes, for the base repository and, when that is not `mycel` itself, also for `mycel` |
| `mycel search --only code <q>` | yes, for the base repository only |
| `mycel search --only docs <q>` | never, with or without `--no-fresh` |
| `mycel search --no-fresh <q>` | no |
| the `better-grep` tail | no (`no_fresh=True`) |
| organization search | per member repository, same rules |

### What the check runs

`retrieval.search` (retrieval.py:132-169):

1. Strip the query; empty → `ValueError("missing query")`. Validate `k`.
2. When `freshness` is true: `fresh_repos = [base_repo]`, plus `"mycel"` when the search is not code-only and the base repository is not `mycel` (retrieval.py:145-148).
3. For each: `syncpass.repo_stale(conn, repo)`. No deadline is passed.
   - Not stale → `{"refreshed": false, "coalesced": false}`.
   - Stale → `syncpass.run_repo_pass(conn, repo, refresh_remotes=False)`; `refreshed` is true unless the pass reports `coalesced`.
4. Then `embedder.code_search(...)` and `_payload(...)`.

`repo_stale` (syncpass.py:398-424) returns:

- `False` when the repository has no `kn_repos` row or is not enabled;
- `True` when `last_sync_ms` is empty;
- otherwise the result of a modification-time scan: `True` as soon as any directory or file under the code root (limited to `code_subdirs` when set) or under the artifact root has an mtime later than `last_sync_ms`. Directories named `node_modules`, `.git`, `.bare`, `dist`, `build`, `.venv`, `__pycache__`, `.next`, `coverage`, `.idea` are not entered (syncpass.py:361-362).

`run_repo_pass` (syncpass.py:197-213, :216-356) for that one repository:

- takes a shared advisory lock on the global key `0x4D5943454C` and an exclusive advisory lock on a per-repository key, both with the non-waiting `pg_try_...` functions; if either is unavailable it returns `{"coalesced": true, "reason": ...}` and the search proceeds on the existing index;
- re-reads the configuration file, ingests the documents under the artifact root, ingests the code under the code root, stamps `kn_repos.last_sync_ms`, and re-diffs that repository's overlays;
- does not fetch remotes and does not write the code map;
- does not embed. Chunks that the pass adds or changes have a NULL vector, so in the search that follows they can be found by the lexical arm only.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/cli.py#search_payload`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_search`
- `mycel_deprecated_v1:mycel/cli.py#main`
- `mycel_deprecated_v1:mycel/retrieval.py#search`
- `mycel_deprecated_v1:mycel/syncpass.py#repo_stale`
- `mycel_deprecated_v1:mycel/syncpass.py#newer_than`
- `mycel_deprecated_v1:mycel/syncpass.py#run_repo_pass`
- `mycel_deprecated_v1:mycel/syncpass.py#_run_coalesced`
- `mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked`
- `mycel_deprecated_v1:mycel/config.py#load_apply`
- `mycel_deprecated_v1:mycel/scope.py#resolve`
- `mycel_deprecated_v1:mycel/organizations.py#resolve`

---

## 9. better-grep

### Entry points

| How it is started | Path taken |
|---|---|
| console script `better-grep` (`mycel.better_grep:main`, pyproject.toml) | `cli.main(["better-grep", ...])` → `better_grep.run` (better_grep.py:101-104) |
| `mycel better-grep ...` | `cli.main` sees `raw[0] == "better-grep"` → `better_grep.run(raw[1:])` (cli.py:723-725) |
| a process whose `argv[0]` basename is `better-grep`, entering `cli.main` | `better_grep.run(raw)` (cli.py:720-722) |
| the PyInstaller binary built from `better_grep_entry.py` (better-grep.spec:5; installed by the Makefile) | `better_grep.run(sys.argv[1:])` directly, without `cli.main` |

`cli.main` injects the system trust store (`truststore.inject_into_ssl()`) and exports the configured database address before dispatching (cli.py:712-719). The PyInstaller entry skips both.

The dispatch happens before `argparse`, so every grep flag is passed through unchanged. The `argparse` entry for `better-grep` exists only so the command shows in `mycel --help` (cli.py:732-734).

### `run(argv)` step by step

(better_grep.py:47-98)

1. `argv` is exactly `["-h"]` or `["--help"]`: print the usage text on stdout, return 0.
2. `argv` is exactly `["--version"]`: print `better-grep <version>`, return 0.
3. `argv` is empty: print the usage line on stderr, return 2.
4. `_parse(argv)` extracts a pattern and a list of paths (below).
5. If no path was found, stdin is a terminal, and one of the arguments is exactly `-r`, `-R` or `--recursive`: append `.` to the grep arguments.
6. **Exact arm:** `subprocess.run(["/usr/bin/grep", *grep_argv])`. No shell, no timeout, standard streams inherited. Its return code is kept as `rc`.
7. If the environment has `BETTER_GREP_PLAIN=1`: return `rc`.
8. `query = _semantic_query(pattern)`: every character of ``\ ^ $ . | ? * + ( ) [ ] { }`` is replaced by a space, runs of whitespace are collapsed, the result is stripped (better_grep.py:42-44). If the query is shorter than 3 characters: return `rc`.
9. **Tail:** `search_payload(query, k=5, paths=paths, no_fresh=True)` — a unified search of at most 5 results with no freshness check. Any exception prints `(mycel tail unavailable: <message>)` on stderr and returns `rc`.
10. Print the tail (below) on stdout and return `rc`.

### Exit codes

- `0` for help and version; `2` for no arguments.
- Otherwise always the return code of `/usr/bin/grep`. The tail never changes it.

### `_parse`

(better_grep.py:9-39)

- Flags that take a value in the next argument (`_VALUE_FLAGS`): `-e -f -A -B -C -m -d -D --include --exclude --exclude-dir --label --binary-files --devices --directories --max-count --regexp --file --after-context --before-context --context`. The following argument is skipped.
- An argument starting with `--` and containing `=` is skipped.
- Any other argument starting with `-` (except a lone `-`) is skipped as a flag.
- The first remaining argument is the pattern, unless `-e` / `--regexp` was seen; all later remaining arguments are paths.
- If no pattern was found, the value after the first `-e` / `--regexp` is used.
- Checked on fictional arguments: `-rn needle src` → pattern `needle`, paths `[src]`; `-e needle src lib` → `needle`, `[src, lib]`; `-A3 needle src` → `needle`, `[src]`.

### Tail format

Printed only when the payload has a non-empty `results` list (better_grep.py:78-97):

```
── mycel: related by meaning (not literal matches) ────────────────────
  <path>#<symbol or empty>  <L<start>-<end> or empty>  score <score>[  ⇐ via <doc>[ ⚠stale][ heartwood]]
  ...
── mycel: documented in ───────────────────────────────────────────────
  <doc>[  ⚠ stale]
  ...
```

- The first header is the text followed by 20 `─` characters; the second is followed by 47.
- One line per result. The span is shown only when `line_start` is set. The `via` suffix is shown only when the result has one.
- The second block lists each distinct `documented_in[].doc` string once, in first-seen order, with the stale flag of its first occurrence. It is omitted when there are none.
- A document or summary result prints as `<path>#` with an empty symbol and span.
- When the scope resolves to an organization, the payload has no `results` key and no tail is printed.

### Scope inference

`search_payload` is called without a repository, so `scope.resolve(paths)` decides (scope.py:28-47):

1. Environment `ARBOL_REPO` set: that repository, with overlay `ARBOL_OVERLAY` or none.
2. Otherwise, for each grep path and then the current directory: resolve it to an absolute path and test it against the configured roots, longest root first — each repository's code root and artifact root, each organization's root and artifact root. The first containing root names the repository (or organization).
3. Otherwise the legacy layout: a path under `~/repo` or `~/.arbol/mirrors` names the repository by its first directory, or by the second when the first is `sylvan-stack`.
4. Otherwise `arbol`.

### Environment variables

| Variable | Effect | Location |
|---|---|---|
| `BETTER_GREP_PLAIN` | `1` disables the tail | better_grep.py:66 |
| `ARBOL_REPO`, `ARBOL_OVERLAY` | force the repository / overlay | scope.py:29-32 |
| `MYCEL_PG_CONNECTION_FILE`, `MYCEL_PG_CONNECTION_SHA256`, `MYCEL_PG_DSN`, `ARBOL_PG_DSN` | database address | database.py:56-63 |
| `MYCEL_PG_SCHEMA`, `ARBOL_PG_SCHEMA` | database schema | database.py:79 |
| `MYCEL_CONFIG` | configuration file path (default `~/.mycel/config.toml`) | config.py:37 |
| `MYCEL_EMBEDDER_URL`, `ARBOL_LOCAL_EMBEDDER_DIR` | local provider address, model directory | local_embedder.py:31, :39-41 |
| `ARBOL_KN_CODE_ROOT`, `ARBOL_KN_CORPUS` | code / artifact root of the `arbol` repository | locations.py:62, :74 |

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/better_grep.py#run`
- `mycel_deprecated_v1:mycel/better_grep.py#_parse`
- `mycel_deprecated_v1:mycel/better_grep.py#_semantic_query`
- `mycel_deprecated_v1:mycel/better_grep.py#main`
- `mycel_deprecated_v1:better_grep_entry.py`
- `mycel_deprecated_v1:mycel/cli.py#main`
- `mycel_deprecated_v1:mycel/cli.py#search_payload`
- `mycel_deprecated_v1:mycel/scope.py#resolve`
- `mycel_deprecated_v1:mycel/scope.py#_legacy_scope`
- `mycel_deprecated_v1:mycel/locations.py#RepositoryLocations`
- `mycel_deprecated_v1:mycel/database.py#dsn`

---

## Surprises and defects

Ordered roughly by how much they would mislead a specification written from the docstrings.

### Ranking

1. **The agreement bonus accumulates.** The `+0.05` is added once for every (document section, bridged edge) pair that reaches a chunk already in the dense list, not once per chunk: `scores[cid] = max(scores[cid], s) + _BRIDGE_AGREEMENT` runs inside the loop over sections and edges (embedder.py:557-563). With 8 sections a chunk can gain up to `+0.40`, and more when the same chunk is returned by both arms of `_bridge_expand`, which are joined with `UNION ALL` and not de-duplicated (embedder.py:355-367). The docstring describes a single bonus.
2. **Documents bypass the margin gate through the rescue tail.** In unified mode the lexical query includes `corpus` and `summary` chunks, and the rescue tail appends every unscored lexical hit (embedder.py:451, :579-582). Such documents are not in `doc_added`, so neither the 0.03 margin, nor the cap of 2, nor the `INDEX.md` / `README.md` exclusion applies to them. The comments on `_DOC_MARGIN`, `_DOC_CAP` and `_DOC_ROUTERS` (embedder.py:340-346) state these as general rules.
3. **"Equal footing in identifier RRF" does not hold.** The docstring (embedder.py:425-427) says documents join the rank-fusion route at equal footing. The dense list contains code chunks only (embedder.py:476-481), so a document can score at most `1/61` while a code chunk can score up to `2/61`.
4. **Down-weights are skipped for some entry paths.** Bridge-injected chunks get no structural, test or generated factor (embedder.py:557-566). When a bridge score replaces a direct score, the discounts already applied to the direct score are lost (`max(...)`). On the rank-fusion route the structural factor is never applied to lexical-only hits, because `kinds` is built from dense rows (embedder.py:584, :588).
5. **`best_code` for the margin gate includes bridge scores and accumulated bonuses** (embedder.py:571), so the bar a document must clear can be above any real cosine, including above 1.0.
6. **Lexical-only scores look like strong cosines.** In unified mode with no query vector, a natural-language query has no scores when the tail starts, so `floor = 1.0 - 0.001` and results are scored `0.999, 0.9985, ...` (embedder.py:579-582). The same field holds a cosine-based value when a vector exists and a value of at most `2/61` (about 0.033) on the rank-fusion route. The payload does not say which scale a score is on.
7. **The route can differ from the classification.** A natural-language query in code-only mode with no dense rows is ranked by rank fusion (embedder.py:520), yet still gets `documented_in` (embedder.py:621-622).
8. **A single ordinary word is "identifier-shaped".** The classifier is purely lexical (embedder.py:500); a one-word prose query takes the rank-fusion route and gets no bridge, no document gate and no `via`.
9. **Tie order is not fixed** on the rank-fusion route and in `doc_search`, where ties are common (a dense-only hit and a lexical-only hit at the same rank have the same score) and insertion order comes from a `set` (embedder.py:292, :585). Inferred from Python's per-process string hashing.
10. **`_bridge_expand` and `_documented_in` have no repository predicate** (embedder.py:355-367, :374-379). A document section that cites code in another repository would inject that code into this repository's results; the code only guards the opposite case, shared `mycel` sections (embedder.py:555-556). Inferred; depends on whether such cross-repository edges exist.
11. **Cosines from different models are merged in one ranking.** When the shared `mycel` repository has a different profile, its sections are scored with a second query vector and then sorted together with the requested repository's sections (embedder.py:464-470, :547), and compared with code scores at the margin gate.
12. **Shared `mycel` documents are not dense-searched when the requested repository has no vectors.** If the profiles are equal, the shared repository reuses the requested repository's query vector, which is `None` when the probe at embedder.py:456 finds nothing (embedder.py:464-465).
13. **The code arm uses the query shape its own comment warns about.** The comment says the HNSW scan under-returns under selective filters and uses an exact scan for documents (embedder.py:531-532); the code arm still orders by the distance operator with `origin`, `state` and `repo` filters over an index shared by all repositories (embedder.py:476-480). Whether it under-returns in practice was not tested.
14. **`natural_key` is indexed for BM25 but never queried** (embedder.py:313-314 against :487, :282). A symbol or path name matches lexically only when it also occurs in the chunk body.

### Flags and filters

15. **Unified results carry no `stale` or `heartwood` field**, even when the result is a document chunk (embedder.py:623-636). Only `doc_search` results and the `via` / `documented_in` annotations carry them. Nothing is filtered on `stale`, `meta.heartwood` or `meta.generated`.
16. **Two result shapes share `schema_version` 2.** Docs-only results have a different field set (no `repo`, `score`, ranks, line span, `via`, `documented_in`; extra `stale`, `heartwood`) and the payload has empty `timings` (embedder.py:304-308; retrieval.py:121).
17. **`--only docs` differs from unified search in more than the result set**: no freshness check even without `--no-fresh` (cli.py:52-56), no shared `mycel` repository (embedder.py:276-285), no router exclusion, the overlay is ignored by the search but still echoed in the payload, the query is not stripped, an empty query is not rejected, and `k` is not validated. With a negative `k`, `sorted(...)[:k]` (embedder.py:293) returns all but the last `|k|` fused candidates (inferred).

### Embedding

18. **A Voyage failure at query time fails the whole search; a local-provider failure degrades it.** `_query_vec` catches `RuntimeError` only on the local branch (embedder.py:99-110). On the Voyage branch an API or network error propagates and `mycel search` exits 1.
19. **Degradation is invisible in the payload.** A missing API key or missing model files give `None` silently (embedder.py:100-101, :108-109). The only sign is `dense: 0`. The `cli.py` module docstring says search "says how to start it" (cli.py:5-6); that text is produced only as a log warning, and only when the model files exist but the provider is down (embedder.py:104-107).
20. **A repository without a `kn_repos` row is treated as enabled and as `voyage`** in `embed_pending` (embedder.py:187-188). The schema comment calls the enabled flag "the interlock that keeps company code away from external APIs" (store.py:126-128), and new rows default to profile `voyage` (store.py:132).
21. **RAPTOR summaries are always embedded through Voyage**, whatever the repository's profile (raptor.py:282, :395). For a `local` repository this sends summary text to the external API and stores vectors from a different model than the one used for that repository's queries.
22. **Unknown profile names are handled inconsistently.** `embed_pending` skips them (embedder.py:191); `_query_vec` treats anything other than `local` as Voyage (embedder.py:99, :108-110).
23. **The embedder is not consulted for the enabled flag at query time.** A disabled repository's query text is still sent to its profile's embedder, and its chunks are still searchable.
24. **Fresh-on-read does not embed.** After a refresh, new and edited chunks have NULL vectors (store.py:322-323, :905) and are found only lexically until an embed pass runs; `freshness.refreshed: true` does not signal this.
25. **`is_available()` for the local profile checks local files, not the provider** (local_embedder.py:44-47). Mycel requires the model files on its own disk although it never loads them.
26. **No batch-size or length protection on the Voyage path.** There is no truncation setting, no token accounting and no retry (embedder.py:54-65). Because pending chunks are selected in a fixed order (`ORDER BY c.id`) and an error ends the pass, a batch the API rejects would be retried first on every later pass (inferred).
27. **The cli.py comment at :240-241 says the post-overlay embed "embeds ALL pending chunks, not just this overlay's".** The call uses the default scope, which excludes every overlay namespace (embedder.py:168-169), so the overlay's own chunks are the ones it does not embed.
28. **`pending_count` and `embed_pending` disagree on scope** (embedder.py:113-118 against :168-195): the count includes overlays, disabled repositories and repositories whose embedder is unusable. `mycel status --repo X` reports the global counts (cli.py:177-179).

### Side effects of a read

29. **Every search runs DDL and writes configuration.** `code_search` and `doc_search` execute `CREATE INDEX IF NOT EXISTS kn_chunks_bm25` on each call and time it (embedder.py:440-441, :269). `search_payload` applies the configuration file to `kn_repos` on each call (cli.py:49). Through `store.set_repo_flags` / `list_repo_flags` the whole schema DDL block runs once per process, that is once per CLI invocation (store.py:186-206, :1062-1063). Inferred from the call chain.
30. **The stale check walks the tree with no deadline.** `newer_than` and `repo_stale` accept a `deadline` and document why (syncpass.py:365-373), but their only caller passes none (retrieval.py:152). A unified search also walks the shared `mycel` repository.

### better-grep

31. **The tail is written to stdout after grep's output, unconditionally.** There is no check that stdout is a terminal (better_grep.py:78-97). Piped or counted output includes the tail lines unless `BETTER_GREP_PLAIN=1`.
32. **`/usr/bin/grep` is hard-coded** (better_grep.py:65).
33. **The argument parser misreads some forms** (checked on fictional arguments): `--regexp=needle src` yields pattern `src`; `-rA 3 needle src` yields pattern `3`; `-r -- -needle src` yields pattern `src`. Combined short flags such as `-rn` do not trigger the automatic `.` (better_grep.py:61-63).
34. **A regular expression becomes a natural-language query.** `foo.bar` turns into `foo bar` (better_grep.py:42-44), which the classifier sends down the natural-language route; a bare identifier stays on the rank-fusion route.
35. **The installed binary skips `cli.main`.** `better_grep_entry.py` calls `run` directly, so the system trust store is not injected before a Voyage query request (cli.py:712-718). The console-script entry does go through `cli.main` (better_grep.py:101-104).
36. **An organization scope silently yields no tail**, because the wrapper payload has no `results` key (better_grep.py:78; cli.py:40-44).

### Dead code and hard-coded names

37. No caller in this repository for: `embedder.search` (embedder.py:239-262), `embedder.request_stop` (:134), `embedder.set_api_key` (:33), `local_embedder.download` (local_embedder.py:71), `retrieval.capabilities` (retrieval.py:172), `retrieval.symbol_read` (retrieval.py:195), and the `only_repos` parameter of `embed_pending`. Module docstrings refer to a server, a daemon and an RPC host that are not in this repository (embedder.py:6-8; retrieval.py:1).
38. Hard-coded names: shared repository `mycel` (embedder.py:383; retrieval.py:147); default repository `"Arbol"` in function signatures (embedder.py:239, :265, :408); Keychain service `com.arbol.embedder` (embedder.py:23); the product name "Seqoya Lab" in error messages (embedder.py:44; local_embedder.py:110); model directory under `~/Library/Application Support/Arbol/models/` (local_embedder.py:41); router file names `INDEX.md`, `README.md` (embedder.py:345); the `sylvan-stack` directory name (scope.py:55; locations.py:69).
39. The embedder.py module docstring says "One unified vector space for docs and (later) code" (embedder.py:1-2). The code stores vectors of two different models in the same column, separated only by repository.
40. The Voyage path depends on the macOS Keychain with no alternative; `has_api_key()` is called unconditionally by `embed_pending` and `mycel status` (embedder.py:182; cli.py:177). Off macOS the framework load would raise (inferred from macos_keychain.py:36-37, :62-63).
41. Outside this area but seen while reading `cli.py`: `_cmd_raptor` calls `subprocess.run` (cli.py:151) and the module has no top-level `import subprocess` (cli.py:14-17); the other uses import it locally. `mycel raptor regen|build` would raise `NameError` at that line (inferred).
42. If an organization contains a member repository whose directory name equals the organization's name (case-insensitive), `search_payload` would recurse without end, because the recursive call resolves the member name as the organization again (cli.py:36-44; organizations.py:30-33). Inferred; not covered by `tests/test_organizations.py`.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#doc_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_bridge_expand`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_documented_in`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_query_vec`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embed`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embed_pending`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#pending_count`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#ensure_bm25_index`
- `mycel_deprecated_v1:mycel/knowledge/local_embedder.py#is_available`
- `mycel_deprecated_v1:mycel/retrieval.py#search`
- `mycel_deprecated_v1:mycel/retrieval.py#_payload`
- `mycel_deprecated_v1:mycel/retrieval.py#capabilities`
- `mycel_deprecated_v1:mycel/retrieval.py#symbol_read`
- `mycel_deprecated_v1:mycel/better_grep.py#run`
- `mycel_deprecated_v1:mycel/better_grep.py#_parse`
- `mycel_deprecated_v1:mycel/better_grep.py#_semantic_query`
- `mycel_deprecated_v1:better_grep_entry.py`
- `mycel_deprecated_v1:mycel/cli.py#search_payload`
- `mycel_deprecated_v1:mycel/cli.py#main`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_overlay`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_raptor`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_status`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#build_tree`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#regen_stale`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema`
- `mycel_deprecated_v1:mycel/knowledge/store.py#list_repo_flags`
- `mycel_deprecated_v1:mycel/syncpass.py#repo_stale`
- `mycel_deprecated_v1:mycel/syncpass.py#newer_than`
- `mycel_deprecated_v1:mycel/organizations.py#resolve`
- `mycel_deprecated_v1:mycel/macos_keychain.py#_get_bindings`

---

## Not established

1. **Voyage server behaviour.** Whether the API truncates over-long inputs when no `truncation` field is sent, what its per-request token limit is, and what it returns for an over-size batch. The code relies on a default it never states.
2. **`pg_search` specifics.** Which tokenizer the index uses with no options, how `paradedb.match` treats punctuation, case and multi-word queries, and which extension version the DDL and `@@@` syntax target. Nothing in the repository creates the extension or pins a version.
3. **HNSW parameters in effect.** No `m`, `ef_construction` or `ef_search` is set in the code; the effective values are the database defaults, which were not read. Whether the filtered code-arm query actually under-returns on the real index was not tested.
4. **Whether cross-repository derivation edges exist**, which decides whether item 10 of the surprises is reachable. That depends on how Source Refs are resolved at ingest (`store._resolve_source_ref`), outside this area.
5. **The resident transport.** `retrieval.py` says it is shared with "Arbol's RPC host". That host is not in this repository, so the value of `transport` there, how it calls `capabilities()` and `symbol_read`, and whether it passes `only_repos` or calls `request_stop()` are unknown.
6. **The local provider.** Its batching ("batches at 8 internally" is a comment, local_embedder.py:27), its truncation, how it uses `input_type` (for example a query instruction prefix), and its exact error format are in the separate `mycel-embedder` program.
7. **Where the numbers come from.** The constants 0.92, 0.05, 0.93, 0.85, 0.9, 0.75, 0.03, the caps 3 / 8 / 2 and the docstring's "prod 15/22 → 19/22 @3, jargon 3/6 → 6/6" refer to "bridge research" that is not in the files read. No evaluation set or test covers ranking in `tests/`.
8. **Regular-expression dialect.** The test and generated path patterns were checked with Python's `re`; in production they run under PostgreSQL's `~` operator. The constructs used appear to mean the same in both, but this was not run against a database.
9. **The `stale` flag's meaning for code chunks** and when `meta.heartwood` is set on chunks are decided at ingest and detection (`store.ingest`, `store.detect`), outside this area; this inventory only records where search reads them.
10. **Logging output.** No logging configuration exists in the repository; that the "dense search degraded" warning reaches stderr rests on Python's default last-resort handler (inferred, not run).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embed`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_bridge_expand`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#ensure_bm25_index`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_query_vec`
- `mycel_deprecated_v1:mycel/knowledge/local_embedder.py#embed`
- `mycel_deprecated_v1:mycel/retrieval.py#capabilities`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema`
