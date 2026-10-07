---
role: derived
sources:
  - mycel_deprecated_v1:mycel/syncpass.py
  - mycel_deprecated_v1:mycel/knowledge/store.py
  - mycel_deprecated_v1:mycel/knowledge/embedder.py
  - mycel_deprecated_v1:mycel/retrieval.py
  - mycel_deprecated_v1:mycel/cli.py
  - mycel_deprecated_v1:tests/test_command_executor.py
  - mycel_deprecated_v1:mycel/command_executor.py
  - mycel_deprecated_v1:mycel/knowledge/code_map.py
  - mycel_deprecated_v1:mycel/knowledge/raptor.py
  - mycel_deprecated_v1:mycel/config.py
  - mycel_deprecated_v1:mycel/knowledge/local_embedder.py
  - mycel_deprecated_v1:mycel/organizations.py
  - mycel_deprecated_v1:tests/test_config_ownership.py
  - mycel_deprecated_v1:tests/test_organizations.py
  - mycel_deprecated_v1:mycel/database.py
  - mycel_deprecated_v1:mycel/repo_identity.py
  - mycel_deprecated_v1:tests/test_database_connection_file.py
  - mycel_deprecated_v1:mycel/scope.py
  - mycel_deprecated_v1:mycel/locations.py
  - mycel_deprecated_v1:tests/test_repository_locations.py
  - mycel_deprecated_v1:mycel/better_grep.py
  - mycel_deprecated_v1:tests/test_cli_metadata.py
  - mycel_deprecated_v1:tests/test_worktree_cli.py
  - mycel_deprecated_v1:mycel/knowledge/clustering.py
  - mycel_deprecated_v1:mycel/completion_client.py
  - mycel_deprecated_v1:mycel/knowledge/chunker.py
  - mycel_deprecated_v1:tests/test_completion_routing.py
  - mycel_deprecated_v1:pyproject.toml
  - mycel_deprecated_v1:Makefile
  - mycel_deprecated_v1:README.md
  - mycel_deprecated_v1:mycel.spec
  - mycel_deprecated_v1:better-grep.spec
  - mycel_deprecated_v1:mycel_entry.py
  - mycel_deprecated_v1:better_grep_entry.py
  - mycel_deprecated_v1:mycel/__main__.py
---
# v1 Mycel inventory: the sync pass, settings, repository scope, commands and summaries

What Mycel version 1 does, read from the deprecated source on 7 October 2026. It is evidence for the [specifications](../specs/README.md), not a description of Mycel 2. Source Refs name the deprecated repository as `mycel_deprecated_v1:`; that repository is not indexed, so they are locators for a reader and do not become edges.

Source: `~/repos/sylvan-stack/mycel_deprecated_v1`, commit `b3125d0`, working tree clean.

Method: every statement below was read from the source files. Nothing was executed: no `mycel`, `infer` or `git` command that changes anything, no database connection, no network. Where a statement is a consequence I derived rather than a line I read, it is marked "inferred". Locations are given as `(file:line)`; file names are unique inside `mycel/` (`store.py`, `embedder.py`, `raptor.py`, `clustering.py`, `code_map.py`, `local_embedder.py` live in `mycel/knowledge/`).

Files read completely: `syncpass.py`, `config.py`, `database.py`, `scope.py`, `locations.py`, `organizations.py`, `repo_identity.py`, `cli.py`, `knowledge/raptor.py`, `knowledge/clustering.py`, `completion_client.py`, `command_executor.py`, `better_grep.py`, `retrieval.py`, `knowledge/code_map.py`, `knowledge/local_embedder.py`, `pyproject.toml`, `Makefile`, `README.md`, both `.spec` files, both entry files, and the nine test files outside the retired browser transport. Read in part, only for the functions the above call: `knowledge/store.py`, `knowledge/embedder.py`, `knowledge/chunker.py`, `knowledge/fs.py`.

---

## 1. The sync pass

### Entry points and callers

| Function | Signature | Callers in v1 |
|---|---|---|
| `run_pass` | `run_pass(conn, *, status=None) -> (dict, int)` (syncpass.py:188) | `mycel sync` (cli.py:102); retired `mycel pull` (cli.py:534) |
| `run_repo_pass` | `run_repo_pass(conn, repo, *, status=None, refresh_remotes=False) -> (dict, int)` (syncpass.py:197) | `retrieval.search` fresh-on-read, always with `refresh_remotes=False` (retrieval.py:157) |

Both wrap the same body, `_run_pass_locked` (syncpass.py:216), inside `_run_coalesced` (syncpass.py:157).

### Locking and coalescing

All locks are PostgreSQL session-level advisory locks, taken with the non-waiting `pg_try_*` forms. Nothing waits and nothing retries.

| Constant | Value | Location |
|---|---|---|
| `_GLOBAL_LOCK_KEY` | `0x4D5943454C` = decimal `332210062668` (the ASCII bytes `MYCEL`) | syncpass.py:147 |
| per-repository key | first 8 bytes of `sha256("mycel-repo:" + canonical_repo(repo))`, big-endian, masked with `0x7FFF_FFFF_FFFF_FFFF` | syncpass.py:150-154 |

| Step | `run_pass` | `run_repo_pass` |
|---|---|---|
| 1 | not taken | `SELECT pg_try_advisory_lock_shared(global key)`; on failure return coalesced with reason `"full sync pass is running"` (syncpass.py:164-170) |
| 2 | `SELECT pg_try_advisory_lock(global key)` (exclusive) | `SELECT pg_try_advisory_lock(repo key)` (exclusive); on failure the shared global lock is released first (syncpass.py:171-177) |
| on failure of step 2 | return coalesced with reason `"another sync pass is running"` | same reason string |
| on success | run the pass, then in `finally`: `pg_advisory_unlock(key)` and, if held, `pg_advisory_unlock_shared(global key)` (syncpass.py:178-185) | same |

Resulting exclusions (inferred from the lock modes): two full passes exclude each other; a full pass and any repository pass exclude each other in both directions; two repository passes exclude each other only when they name the same repository.

"Coalesced" means: this call did no work at all. The caller receives, instead of the counters, the tuple `({"coalesced": True, "reason": <string>}, n)` where `n = embedder.pending_count(conn, pending_repo)` (syncpass.py:169-170, 176-177). For `run_pass` `pending_repo` is `None`, so `n` counts every present chunk without an embedding in every namespace; for `run_repo_pass` it counts rows with `repo = <that repo>` exactly (embedder.py:113-118). This is a different quantity from the pending count of a pass that ran (step 9 below).

What callers do with a coalesced result:
- `mycel sync` prints `{"coalesced": true, "reason": "...", "pending_embed": n}`, still embeds if `n > 0` and `--no-embed` is absent, and exits 0 (cli.py:102-109).
- `retrieval.search` records `{"refreshed": false, "coalesced": true}` for that repository and searches the index as it is (retrieval.py:157-162).

### Which repositories a pass covers

- The candidate set is every row of table `kn_repos` as returned by `store.list_repo_flags` (syncpass.py:234; store.py:1059-1068). The query has no `ORDER BY`, so the processing order is not defined by the code.
- A row is processed only if `mycel_enabled` is true (syncpass.py:242, 288).
- `run_repo_pass` keeps only the row whose name equals the canonical repository name (syncpass.py:235-237). If there is no such row, or it is disabled, the pass does nothing and returns all-zero counters.
- Rows reach `kn_repos` from the `[repos]` table of the configuration file (section 5). Organization members that are not also listed under `[repos]` have no row and are not synced (inferred from `config.apply`, config.py:137-152, which iterates `[repos]` only).

### Steps of `_run_pass_locked`, in order

`run_pass` calls it with `refresh_remotes=True, write_code_maps=True, repos=None`; `run_repo_pass` with `repos=[repo], refresh_remotes=<argument>, write_code_maps=False`.

1. Record start time; use the caller's `status` dict or a new one (syncpass.py:222-223).
2. Configuration: `config.ensure_seeded(conn)` then `config.load_apply(conn)` (not forced). On success remove `status["config_error"]`. On `ValueError` log a warning, set `status["config_error"] = str(e)` and continue with the flags already in the database (syncpass.py:225-232).
3. `ALTER TABLE kn_repos ADD COLUMN IF NOT EXISTS last_sync_ms BIGINT`, once per process (syncpass.py:139-144, 233).
4. Load all repository flags; select the rows to process (syncpass.py:234-237).
5. For each selected, enabled repository `name` with flags `f` (syncpass.py:241-277):
   1. Resolve `aroot = artifact_root(name, f)` and `croot = code_root(name, f)` (section 7).
   2. If `aroot` is a directory: `store.refresh(conn, aroot, name, code_root=croot if it is a directory else None)`. That call ingests the Markdown corpus, re-hashes the repository's tracked code documents against `croot`, runs `store.detect(conn)`, and returns counters plus item lists (store.py:658-687). The pass adds `docs["edited"]` to `docs_edited`, `docs["new"]` to `docs_new`, `docs["stale"]` to `stale` (syncpass.py:246-252).
   3. If `refresh_remotes` is true and `f["code_root"]` is set and `<croot>/.git` exists (file or directory): `refresh_mirror(name, croot)` (section 2). A returned string is logged as a warning and stored in `status["mirror_warning"]`; a `None` result removes `status["mirror_warning"]` (syncpass.py:253-261).
   4. If `croot` is a directory: `store.ingest_code(conn, croot, f["code_subdirs"], name)`; add `added`, `updated`, `removed` to `code_added`, `code_updated`, `code_removed` (syncpass.py:262-267).
   5. Still inside "croot is a directory", if `write_code_maps`: `code_map.write_map(conn, name, aroot)`. Any exception is logged as a warning and swallowed, except a host "unsettled" error (syncpass.py:268-275).
   6. `UPDATE kn_repos SET last_sync_ms=<now in ms> WHERE name=<name>`. This runs for every enabled selected repository, also when neither root exists (syncpass.py:276-277).
6. Branch Overlay maintenance (the worktree model whose commands are retired is still executed here; syncpass.py:278-334):
   1. Load registered overlays (`store.list_overlays`), filtered to the selected repositories.
   2. For each selected, enabled repository: `container = ~/repo/<name>` (hard-coded, syncpass.py:290). If `<container>/.bare` is a directory, list worktrees with `git --git-dir <container>/.bare worktree list --porcelain` (timeout 15 s; syncpass.py:46-48). Skip the corpus worktree (`<container>/master`, else `<container>/main`; syncpass.py:66-72) and worktrees whose directory is missing. Every other worktree with a branch and no registered overlay is registered with `store.ingest_overlay` (activity row written).
   3. For each previously registered overlay: if its `worktree_path` is no longer a directory, `store.drop_overlay`; otherwise `store.ingest_overlay(..., log_event=False)` (re-diff, no activity row). Failures are logged as warnings and do not stop the pass.
7. Compute `usable`: the selected repositories (enabled or not) whose `embedder_profile` (default `"voyage"`) is `"voyage"` and a Voyage API key exists, or is `"local"` and the local model files exist (syncpass.py:338-342).
8. `pending = SELECT count(*) FROM kn_chunks WHERE state='present' AND embedding IS NULL AND split_part(repo, '@', 1) = ANY(usable)`; `0` when `usable` is empty (syncpass.py:345-347).
9. If any counter is non-zero or any item was collected, write one `kn_activity` row of kind `sync` (section 4) (syncpass.py:350-355).
10. Return `(agg, pending)` (syncpass.py:356).

### Return value

`agg` is a dict with exactly these keys, all integers (syncpass.py:238-239):

| Key | What is summed |
|---|---|
| `docs_edited` | Markdown chunks whose text changed (the `edited` chunk-status counter of `store.ingest`, store.py:250, 298, 307) |
| `docs_new` | new Markdown chunks (the `new` chunk-status counter; not the `docs_new` document counter that `ingest` also returns) |
| `stale` | `detect()["stale"]` after each repository's refresh (store.py:566) |
| `code_added`, `code_updated`, `code_removed` | code chunks inserted, changed, set to `state='absent'` (store.py:901, 907, 915) |

The second element is the pending-embedding count of step 8. The pass itself embeds nothing.

### Every difference between `run_pass` and `run_repo_pass`

| Aspect | `run_pass` | `run_repo_pass` |
|---|---|---|
| Repositories | all enabled rows | one named row |
| Locks | exclusive global | shared global + exclusive per-repository |
| Remote refresh (`refresh_mirror`) | always attempted for eligible repositories | off by default; the only caller passes `False` |
| Code map file | written when changed | never written |
| Overlays examined | all registered overlays | those whose `base_repo` is the repository |
| Activity `summary.repos` | key absent | `[<repo>]` (syncpass.py:353) |
| Pending count when coalesced | all namespaces | exact `repo` match |
| Reason strings when coalesced | `"another sync pass is running"` | that, or `"full sync pass is running"` |

Identical in both: configuration seed and apply, the `last_sync_ms` column check, the documents refresh including the database-wide `detect()`, code ingest, the `last_sync_ms` stamp, the pending count formula, the activity rule.

<!-- sources:
mycel_deprecated_v1:mycel/syncpass.py#run_pass
mycel_deprecated_v1:mycel/syncpass.py#run_repo_pass
mycel_deprecated_v1:mycel/syncpass.py#_run_coalesced
mycel_deprecated_v1:mycel/syncpass.py#_repo_lock_key
mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked
mycel_deprecated_v1:mycel/syncpass.py#_ensure_last_sync_col
mycel_deprecated_v1:mycel/syncpass.py#is_container
mycel_deprecated_v1:mycel/syncpass.py#list_worktrees
mycel_deprecated_v1:mycel/syncpass.py#corpus_worktree
mycel_deprecated_v1:mycel/knowledge/store.py#refresh
mycel_deprecated_v1:mycel/knowledge/store.py#ingest
mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code
mycel_deprecated_v1:mycel/knowledge/store.py#detect
mycel_deprecated_v1:mycel/knowledge/store.py#list_repo_flags
mycel_deprecated_v1:mycel/knowledge/embedder.py#pending_count
mycel_deprecated_v1:mycel/retrieval.py#search
mycel_deprecated_v1:mycel/cli.py#_cmd_sync
mycel_deprecated_v1:tests/test_command_executor.py#test_sync_pass_never_swallows_overlay_cleanup_debt
-->

---

## 2. Remote refresh

`refresh_mirror(repo, root)` (syncpass.py:94-133) is the only code in the pass that changes a checkout. Its only caller is step 5.3 of the pass (syncpass.py:256).

### When it is called

All three must hold (syncpass.py:254-255):
1. the pass runs with `refresh_remotes=True` (in v1: `mycel sync` and the retired `mycel pull`);
2. the database flag `kn_repos.code_root` of the repository is non-empty, meaning an explicit `code_root` was configured; repositories located by convention or by organization membership are never refreshed;
3. `<croot>/.git` exists, where `croot` is the resolved code root (it can differ from the flag, see section 7).

### Minimum interval

- `_MIRROR_REFRESH_SECONDS = 600` (syncpass.py:91). Bookkeeping is the module-level dict `_mirror_last` keyed by canonical repository name, compared against `time.monotonic()` (syncpass.py:90, 103-107).
- If `now - _mirror_last.get(repo, 0) < 600` the function returns `None` without running git.
- The timestamp is stored before any git command runs, so a failed attempt also starts the interval (syncpass.py:107).
- The dict lives in process memory only. Inferred: a per-task command starts with an empty dict, so the interval never limits two separate `mycel sync` invocations.

### Git commands, in order

Every command is run through `command_executor.run` with `purpose="syncpass-git"`, `text=True`, and the environment `os.environ` plus `GIT_TERMINAL_PROMPT=0` (syncpass.py:108). All use `git -C <root>`.

| # | Command | Timeout | Handling of the result |
|---|---|---|---|
| 1 | `git -C <root> remote get-url origin` | 15 s | non-zero exit: return `None` (no remote, nothing to refresh) (syncpass.py:110-113) |
| 2 | `git -C <root> status --porcelain` | 30 s | exit 0 and non-empty output: return the dirty warning (below). A non-zero exit does not stop the refresh (syncpass.py:114-118) |
| 3 | `git -C <root> symbolic-ref refs/remotes/origin/HEAD` | 15 s | `branch` = text after the last `/` of stdout; empty output gives `"master"`; the exit code is not checked (syncpass.py:119-121) |
| 4 | `git -C <root> fetch origin <branch>` | 120 s | non-zero exit: return `"mirror fetch failed (<repo>): <last 200 chars of stderr>"` (syncpass.py:122-125) |
| 5 | `git -C <root> reset --hard FETCH_HEAD` | 60 s | non-zero exit: return `"mirror reset failed (<repo>): <last 200 chars of stderr>"` (syncpass.py:126-129) |

After command 5 succeeds the function returns `None`.

### Dirty guard

- The guard is command 2. Its warning text is `"master worktree dirty (<repo>): corpus refresh frozen until local changes in <root> are resolved"` (syncpass.py:117-118). The word "master" is fixed text; the branch actually checked out is not inspected.
- `git status --porcelain` reports modified, staged and untracked files, so any of them freezes the refresh. Ignored files do not (git behaviour, inferred).
- The guard does not look at commits. Command 5 moves whatever is checked out in `<root>` to the fetched tip of the remote default branch.

### Failure

- Any exception (timeout, missing git, OS error) returns `"mirror refresh error (<repo>): <exception>"` (syncpass.py:131-133). With a host executor installed, exceptions of the host's "unsettled" types are re-raised instead (command_executor.py:40-44); the standalone command line installs none.
- All failures are non-fatal: the caller logs the string, stores it in `status["mirror_warning"]`, and continues to code ingest on the unchanged checkout (syncpass.py:256-262).
- Tests state: an `OSError` from the runner yields a returned string containing the error text; an "unsettled" error escapes (tests/test_command_executor.py:67-83).

### Other git commands a pass runs (read-only)

- `git --git-dir <container>/.bare worktree list --porcelain` (syncpass.py:46-48).
- Inside `store.ingest_overlay`, for each overlay worktree: `git -C <wt> merge-base master HEAD`, `git -C <wt> diff --name-status -M <merge-base>`, `git -C <wt> ls-files --others --exclude-standard`, `git -C <wt> merge-base --is-ancestor HEAD master` (store.py:956-1000).

<!-- sources:
mycel_deprecated_v1:mycel/syncpass.py#refresh_mirror
mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked
mycel_deprecated_v1:mycel/syncpass.py#list_worktrees
mycel_deprecated_v1:mycel/command_executor.py#run
mycel_deprecated_v1:mycel/command_executor.py#raise_if_unsettled
mycel_deprecated_v1:mycel/knowledge/store.py#ingest_overlay
mycel_deprecated_v1:tests/test_command_executor.py#test_settled_git_failure_remains_best_effort
mycel_deprecated_v1:tests/test_command_executor.py#test_cleanup_uncertainty_escapes_best_effort_and_completion_fallbacks
-->

---

## 3. Staleness scan

### `repo_stale(conn, repo, *, deadline=None) -> bool` (syncpass.py:398-424)

1. Canonicalise the name; ensure the `last_sync_ms` column exists.
2. `SELECT last_sync_ms, code_subdirs, code_root, mycel_enabled FROM kn_repos WHERE name=%s`. No row, or `mycel_enabled` false: return `False` (syncpass.py:406-409).
3. `last_sync_ms` null or 0: return `True` (never synced) (syncpass.py:410-412).
4. Resolve the code root from the flags. If it is a directory, scan it with `newer_than(croot, last, flags["code_subdirs"], deadline=deadline)`. Result `True`: return `True`. Result `None`: return `False` without scanning the corpus (syncpass.py:413-420).
5. Resolve the artifact root. Not a directory: return `False`. Otherwise return `newer_than(aroot, last, deadline=deadline) is True` (syncpass.py:421-424).

### `newer_than(root, since_ms, subdirs=None, *, deadline=None) -> bool | None` (syncpass.py:365-395)

- Scanned roots: `root/<subdir>` for each configured subdirectory, or `root` itself when none are configured (syncpass.py:376).
- Walk: `os.walk`, top-down. Directories whose name is in `_SCAN_SKIP` are not entered. `_SCAN_SKIP = {"node_modules", ".git", ".bare", "dist", "build", ".venv", "__pycache__", ".next", "coverage", ".idea"}` (syncpass.py:361-362).
- mtime rule: return `True` at the first directory or file whose `os.path.getmtime(...)` is strictly greater than `since_ms / 1000.0` (syncpass.py:385-392). Every file counts, regardless of extension. A directory's own mtime counts.
- `OSError` on a directory skips that directory's files (its subdirectories are still walked); `OSError` on a file skips the file (syncpass.py:384-394).
- Deadline: a caller-supplied `time.monotonic()` value. It is checked once every 32 visited directories (`checked % 32 == 0`); when reached, the function returns `None` (syncpass.py:380-382).
- Nothing newer found: `False`.

### "Not proven stale"

A `None` from the scan (deadline reached) is treated by `repo_stale` as `False`: the repository is not refreshed by this query. The docstrings assign eventual reconciliation to "watcher/scheduled maintenance" (syncpass.py:369-372, 401-402); no watcher or scheduler exists in this repository.

The only caller, `retrieval.search`, passes no deadline (retrieval.py:152), and no code in the repository passes `deadline=` to either function. In v1 the scan is therefore unbounded and the `None` path is not reached.

### `last_sync_ms`

- Column `kn_repos.last_sync_ms BIGINT`, added lazily by `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` (syncpass.py:143); it is not in the schema DDL of `store.py`.
- Written only by the pass: `store.now_ms()` (wall clock, `int(time.time() * 1000)`, store.py:25-26) after each enabled repository has been processed (syncpass.py:276-277).
- Read only by `repo_stale`.

### Where staleness is checked

`retrieval.search(..., freshness=True)` checks the base repository of the request and, unless the search is code-only or the base repository is `mycel`, also the repository named `mycel` (retrieval.py:143-148). A stale repository gets `run_repo_pass(conn, repo, refresh_remotes=False)` (retrieval.py:157-158). `mycel search --only docs` and `better-grep` never run this check (cli.py:52-56; better_grep.py:73).

<!-- sources:
mycel_deprecated_v1:mycel/syncpass.py#repo_stale
mycel_deprecated_v1:mycel/syncpass.py#newer_than
mycel_deprecated_v1:mycel/syncpass.py#_ensure_last_sync_col
mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked
mycel_deprecated_v1:mycel/retrieval.py#search
mycel_deprecated_v1:mycel/knowledge/store.py#now_ms
-->

---

## 4. What a pass writes besides chunks

### Files

| File | Written by | Condition |
|---|---|---|
| `~/.mycel/config.toml` (or `MYCEL_CONFIG`) | `config.ensure_seeded` | the file does not exist (config.py:158-162) |
| `<artifact_root>/generated/code-map.md` | `code_map.write_map` | full pass only; code root is a directory; rendered content differs from the file on disk (code_map.py:81-99) |
| the checkout at the code root | `refresh_mirror` | section 2 |

Code map details:
- Content is built from `kn_chunks` rows with `repo=<name>`, `origin='code'`, `state='present'`, `symbol_kind NOT IN ('module','markup','style','file')`, ordered by path and ordinal (code_map.py:24-29).
- Layout: frontmatter `generated: true`; title `# Code Map: <repo>`; one `## <directory>` section per directory; one bullet per file listing classes with up to 8 methods and up to 8 top-level names (`_MAX_NAMES_PER_FILE = 8`, code_map.py:20), then a Source Ref block listing `<repo>:<path>` for every file of the directory (code_map.py:48-77).
- Writing creates `<artifact_root>/generated/` with `os.makedirs(..., exist_ok=True)`, writes `code-map.md.tmp`, then `os.replace` (code_map.py:94-98). Inferred: this creates the artifact root itself when it did not exist.
- The map is written after the documents refresh of the same pass, and the `last_sync_ms` stamp follows it. Inferred: a new map is ingested as a document only by a later pass, and its own mtime does not make the repository stale.

### Database rows other than documents and chunks

| Table / column | Writer | Note |
|---|---|---|
| schema DDL | `store.ensure_schema` | once per process, section 6 |
| `kn_repos` flags | `config.apply` via `store.set_repo_flags` | section 5 |
| `kn_repos.last_sync_ms` | pass step 5.6 | section 3 |
| `kn_ingest_runs` | `store.ingest` | one row per repository per documents refresh, unconditionally: `(id, ts, corpus, summary)` with the counters as JSON (store.py:362-363) |
| `kn_identity_log` | `store.ingest` | one row per document/chunk identity decision of changed documents (store.py:360-361) |
| `kn_derivations` | `store.ingest` (`declared` edges from Source Refs) | store.py:442-455 |
| `kn_chunks.stale`, `stale_because` | `store.detect` | clears every stale flag in the database, then sets the recomputed set (store.py:560-562) |
| `kn_drifts.status='closed'` | `store.detect` | only for chunks whose meta has `heartwood` or `generated` true (store.py:563-565) |
| `kn_overlays` and overlay-namespace rows | `store.ingest_overlay`, `store.drop_overlay` | step 6 of the pass |
| `kn_activity` | `store.log_activity` | below |

### `kn_activity`

Table definition (store.py:174-178): `id text PRIMARY KEY, ts bigint NOT NULL, kind text NOT NULL, repo text, actor text NOT NULL DEFAULT 'cli', summary jsonb NOT NULL DEFAULT '{}', duration_ms bigint, error text`; index `kn_activity_ts ON kn_activity(ts DESC)`.

`store.log_activity(conn, kind, *, repo=None, summary=None, duration_ms=None, error=None)` inserts one row with `id = ulid()`, `ts = now_ms()`, `actor = store.ACTOR` (module global, `"cli"`, store.py:1135). Every exception from the insert is swallowed (store.py:1138-1151).

| Kind | Writer | `repo` column | `summary` keys | `error` | Condition |
|---|---|---|---|---|---|
| `sync` | `_run_pass_locked` (syncpass.py:350-355) | null | `docs_edited`, `docs_new`, `stale`, `code_added`, `code_updated`, `code_removed`, `pending_embed`, `items`, and `repos` (repository pass only) | `status["config_error"]`, else `status["mirror_warning"]` | any counter non-zero or any item present |
| `embed` | `embedder.embed_pending` (embedder.py:206-210, 229-233) | null | `embedded`, `total`, `skipped`, `items`, and `stopped: true` when interrupted | null | at least one chunk embedded |
| `overlay_ingest` | `store.ingest_overlay` (store.py:1006-1011) | base repository | `overlay`, `changed_files`, `deleted_files`, `merged`, `items` | null | `log_event=True` (auto-registration in a pass; not the per-pass re-diff) |
| `raptor_build` | `raptor.build_tree` (raptor.py:295-296) | repository | `cleared`, `tiers`, `summaries`, `top_nodes`, `cancelled`, `model`, `items` | null | always, when the build returns |
| `raptor_regen` | `raptor.regen_stale` (raptor.py:407-409) | repository | `regenerated`, `stale`, `tiers`, `cancelled`, `model`, `items` | null | `regenerated > 0` |
| `pull` | retired `mycel pull` (cli.py:518-528) | null | `repos`, `items` | joined error strings | something changed or failed |

`items` entries of a `sync` row:
- from the documents refresh: `{repo, path, action, file_path}` with `action` in `added`, `renamed`, `edited`; `{repo, path, action: "removed"}` (store.py:274-275, 354);
- one entry per stale present chunk of the repository after detection: `{repo, path, detail: <natural_key>, reason: <stale_because>, action: "stale", file_path?}` (store.py:677-686);
- from code ingest: `{repo, path, action: "edited"|"added", file_path}`, `{repo, path, action: "removed"}` (store.py:872-873, 921).

### Status fields

The `status` dict passed by the caller is mutated in place:

| Key | Set when | Cleared when |
|---|---|---|
| `config_error` | `ensure_seeded` or `load_apply` raised `ValueError` (syncpass.py:230-232) | they succeeded (syncpass.py:229) |
| `mirror_warning` | `refresh_mirror` returned a string (syncpass.py:257-259) | a later eligible repository in the same pass refreshed without warning (syncpass.py:260-261) |

`mycel sync` merges this dict into its printed JSON (cli.py:103).

### Log output

The pass logs through `logging.getLogger("mycel")` (syncpass.py:25). No code in the command line configures logging. Inferred from the Python standard library default: warnings reach stderr as bare text; `info` lines (`"mycel config applied: ..."`, `"code map regenerated: ..."`, overlay messages) are discarded.

<!-- sources:
mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked
mycel_deprecated_v1:mycel/knowledge/code_map.py#build_markdown
mycel_deprecated_v1:mycel/knowledge/code_map.py#write_map
mycel_deprecated_v1:mycel/knowledge/store.py#log_activity
mycel_deprecated_v1:mycel/knowledge/store.py#ingest
mycel_deprecated_v1:mycel/knowledge/store.py#refresh
mycel_deprecated_v1:mycel/knowledge/store.py#detect
mycel_deprecated_v1:mycel/knowledge/store.py#ingest_overlay
mycel_deprecated_v1:mycel/knowledge/embedder.py#embed_pending
mycel_deprecated_v1:mycel/knowledge/raptor.py#build_tree
mycel_deprecated_v1:mycel/knowledge/raptor.py#regen_stale
mycel_deprecated_v1:mycel/config.py#ensure_seeded
-->

---

## 5. Configuration

### The file

- Path: `os.path.expanduser(os.environ.get("MYCEL_CONFIG", "~/.mycel/config.toml"))` (config.py:36-37; the same expression is repeated in database.py:64).
- Format: TOML, parsed with the standard library `tomllib` (config.py:48).
- `config.load()` returns `None` when the file is missing, raises `ValueError("mycel config unreadable (<path>): <error>")` on a TOML or OS error, and otherwise returns the parsed dict with `cfg["repos"]` replaced by `canonical_repos(...)` (config.py:40-52).
- No key is validated for type by `load` or `apply`.

### Keys the code reads

| Table | Key | Default | Read at | Meaning |
|---|---|---|---|---|
| `[database]` | `dsn` | none | database.py:46-53, 64-72; config.py:193-202 | PostgreSQL connection string |
| `[database]` | `connection_file` | none | same | absolute path of a private JSON file holding the DSN |
| `[database]` | `connection_sha256` | none | same | 64 lowercase hex digits pinning that file's content |
| `[providers]` | `embedder_url` | `http://127.0.0.1:7331` | config.py:184-190; local_embedder.py:30-35 | address of the local embedding provider |
| `[organizations.<name>]` | `root` | required, non-empty string | organizations.py:17-19 | folder whose direct children are the member checkouts |
| `[organizations.<name>]` | `url` | `""` | organizations.py:24 | carried, not used by the files read |
| `[organizations.<name>]` | `artifact_root` | `~/Artifacts/<basename of root>` | organizations.py:20-21, 45-48 | corpus folder of the organization; must be absolute after `~` expansion |
| `[repos.<name>]` | `enabled` | `false` | config.py:144 | becomes `kn_repos.mycel_enabled` (through `bool()`) |
| `[repos.<name>]` | `profile` | `"voyage"` | config.py:145 | becomes `kn_repos.embedder_profile`; the code distinguishes `"voyage"` and `"local"` |
| `[repos.<name>]` | `code_subdirs` | none (whole tree) | config.py:146 | list of subfolders that form the code corpus |
| `[repos.<name>]` | `code_root` | none (section 7) | config.py:147; locations.py:62-65 | where the code is read from |
| `[repos.<name>]` | `artifact_root` | none (section 7) | config.py:148; locations.py:74-77 | where the document corpus is read from |
| `[mirrors]` | any | none | written by config.py:82-87 | read only by the retired mirror modules (not inventoried) |

Any other top-level table is ignored by the readers and dropped by `dumps` (test: a `recipes` table is not serialised, tests/test_config_ownership.py:4-12). An `alias` key inside an organization is ignored (tests/test_organizations.py:31-35).

### Environment variables

| Variable | Effect | Location |
|---|---|---|
| `MYCEL_CONFIG` | path of the configuration file | config.py:37; database.py:64 |
| `MYCEL_EMBEDDER_URL` | local embedding provider address; wins over `providers.embedder_url`; also the value written when the file is seeded | local_embedder.py:31-33; config.py:132-133 |
| `MYCEL_PG_CONNECTION_FILE`, `MYCEL_PG_CONNECTION_SHA256` | private connection reference; highest precedence | database.py:57-60 |
| `MYCEL_PG_DSN`, then `ARBOL_PG_DSN` | explicit DSN | database.py:61-63 |
| `MYCEL_PG_SCHEMA`, then `ARBOL_PG_SCHEMA` | PostgreSQL schema to create and use | database.py:79-84 |
| `ARBOL_REPO` | forces the resolved repository | scope.py:29-32 |
| `ARBOL_OVERLAY` | forces or clears (empty string) the overlay branch | scope.py:30, 72-76 |
| `ARBOL_KN_CODE_ROOT` | code root, only for repository `arbol` | locations.py:62 |
| `ARBOL_KN_CORPUS` | artifact root, only for repository `arbol` | locations.py:74 |
| `ARBOL_LOCAL_EMBEDDER_DIR` | local model directory; default `~/Library/Application Support/Arbol/models/Qwen3-Embedding-0.6B` | local_embedder.py:38-41 |
| `INFER_BIN` | path of the `infer` executable | completion_client.py:24-27 |
| `MYCEL_SYSTEM_INSTRUCTIONS` | folder of the RAPTOR prompt files | raptor.py:47-48 |
| `BETTER_GREP_PLAIN` | `"1"` disables the semantic tail of `better-grep` | better_grep.py:66 |
| `GIT_TERMINAL_PROMPT` | set to `0` for every git child process | syncpass.py:108; store.py:954 |

The command line also writes one variable: `_export_dsn()` sets `ARBOL_PG_DSN` in its own process environment to the DSN resolved from `[database]`, when that DSN is non-empty and `ARBOL_PG_DSN` is not already set (cli.py:76-81).

### `load_apply(conn, *, force=False) -> bool` (config.py:165-181)

1. File missing: return `False`.
2. Read the file's mtime. Not forced and equal to the module global `_last_applied_mtime`: return `False`.
3. `cfg = load()` (may raise `ValueError`).
4. `apply(conn, cfg)`; store the mtime; return `True`.

Call sites:

| Caller | Seeds first | Forced | On `ValueError` |
|---|---|---|---|
| `cli._connect_with_config` (cli.py:84-93), used by `sync`, `embed`, `raptor`, `status`, `drifts`, `derive`, `repos`, `activity` and the retired `overlay`, `pull` | yes | yes | prints `warning: <message>` to stderr and continues |
| `cli.search_payload` (cli.py:47-51) | no | yes | same warning |
| `syncpass._run_pass_locked` (syncpass.py:225-232) | yes | no | `status["config_error"]` |

### `apply(conn, cfg)` (config.py:137-152)

Direction is file to database only.

- For each `[repos.<name>]` (names canonicalised): `store.set_repo_flags(conn, name, mycel_enabled=r.get("enabled", False), embedder_profile=r.get("profile") or "voyage", code_subdirs=r.get("code_subdirs"), code_root=r.get("code_root"), artifact_root=r.get("artifact_root"))`.
- `set_repo_flags` inserts the row if missing and updates only arguments that are not `None` (store.py:1080-1095). An empty list for `code_subdirs`, or an empty string for `code_root` / `artifact_root`, stores SQL `NULL`. A key that is absent from the file leaves the stored value unchanged.
- Every `kn_repos` row that is not in the file and is currently enabled is set to `mycel_enabled=false`; the row is kept (config.py:149-151).
- Ends with `conn.commit()`.

Nothing else is copied: `[database]`, `[providers]`, `[organizations]`, `[mirrors]` stay file-only.

### `dumps(cfg) -> str` and `write(cfg)` (config.py:59-117)

`dumps` renders a fixed schema by hand, in this order:
1. a four-line comment header (`_HEADER`, config.py:29-33);
2. `[database]`, only if `dsn` or `connection_file` is present: either `connection_file` + `connection_sha256`, or `dsn` followed by the comment `# Mycel's OWN database (Arbol's stays separate)`. It raises `ValueError("private database connection path is missing")` for a digest without a file, and `ValueError("private database connection requires one path and its digest")` for a file with a `dsn` or without a digest (config.py:63-75);
3. `[providers]`, keys sorted, every value written as a quoted string;
4. `[mirrors]`, same treatment;
5. `[organizations."<name>"]` sorted by name, keys `root`, `url`, `artifact_root` when present;
6. `[repos.<name>]` sorted by canonical name (bare key when `name.isalnum()`, otherwise quoted): `enabled = true|false` always; `profile`, `code_subdirs`, `code_root`, `artifact_root` only when truthy.

`write` creates the parent folder, writes `<path>.tmp`, then `os.replace` onto the path (config.py:110-117).

### Who writes the file

In the non-retired code the only writer is `ensure_seeded` (config.py:158-162): when the file does not exist it writes `generate_from_db(conn)`, which is `{"providers": {"embedder_url": <MYCEL_EMBEDDER_URL or "http://127.0.0.1:7331">}, "repos": {<name>: {enabled, profile, code_subdirs?, code_root?, artifact_root?}}}` built from `kn_repos` (config.py:120-134; test: the seed has exactly the keys `providers` and `repos`, tests/test_config_ownership.py:15-25).

The file header and module docstring state that any editor, any agent, or "Seqoya Lab" may edit the file (config.py:5-7, 29-33). No such external writer is in this repository.

<!-- sources:
mycel_deprecated_v1:mycel/config.py#path
mycel_deprecated_v1:mycel/config.py#load
mycel_deprecated_v1:mycel/config.py#dumps
mycel_deprecated_v1:mycel/config.py#write
mycel_deprecated_v1:mycel/config.py#generate_from_db
mycel_deprecated_v1:mycel/config.py#apply
mycel_deprecated_v1:mycel/config.py#ensure_seeded
mycel_deprecated_v1:mycel/config.py#load_apply
mycel_deprecated_v1:mycel/config.py#provider_embedder_url
mycel_deprecated_v1:mycel/config.py#database_dsn
mycel_deprecated_v1:mycel/knowledge/store.py#set_repo_flags
mycel_deprecated_v1:mycel/knowledge/local_embedder.py#provider_url
mycel_deprecated_v1:mycel/knowledge/local_embedder.py#model_dir
mycel_deprecated_v1:mycel/organizations.py#configured
mycel_deprecated_v1:mycel/cli.py#_connect_with_config
mycel_deprecated_v1:mycel/cli.py#_export_dsn
mycel_deprecated_v1:tests/test_config_ownership.py#test_mycel_config_does_not_serialize_infer_recipes
mycel_deprecated_v1:tests/test_organizations.py#test_config_roundtrip_preserves_organizations
-->

---

## 6. Database connection

### Where the DSN comes from

`database.dsn()` (database.py:56-73), first match wins:

1. `MYCEL_PG_CONNECTION_FILE` or `MYCEL_PG_CONNECTION_SHA256` set: `configured_dsn({"connection_file": ..., "connection_sha256": ...})`. A missing path raises `ValueError("private database connection path is missing")`.
2. `MYCEL_PG_DSN`, else `ARBOL_PG_DSN`.
3. The `[database]` table of the configuration file, through `configured_dsn`. A missing, unreadable or malformed file is treated as an empty table (database.py:65-69).
4. `DEFAULT_DSN = "postgresql://arbol:arbol@localhost:5432/arbol"` (database.py:17).

`configured_dsn(settings)` (database.py:46-53): if `connection_file` or `connection_sha256` is present, a `dsn` in the same table raises `ValueError("database configuration has both DSN and private connection reference")`; otherwise it returns `private_dsn(path, digest)`. Without a private reference it returns `settings["dsn"]` or `None`.

Before any command runs, `cli.main` calls `_export_dsn()` (cli.py:719), which resolves `[database]` through `config.database_dsn()` and exports it as `ARBOL_PG_DSN` (section 5). `config.database_dsn()` returns `None` when the file is malformed, and lets errors of the private reference propagate (config.py:193-202).

### `private_dsn(path, expected_digest)` (database.py:21-43)

Checks, in order; any failure raises and there is no fallback:

| Check | Error |
|---|---|
| path is absolute and equals its own `resolve()` (no symlink or `..` in it); digest is a string of 64 characters from `0-9a-f` | `ValueError("invalid private database connection reference")` |
| opened read-only with the flags `O_NOFOLLOW` and `O_NONBLOCK` | `OSError` (missing file, symlink) |
| regular file, owned by the current uid, no group/other permission bits (`mode & 0o077 == 0`), size at most 16384 bytes | `ValueError("database connection must be a private owned regular file")` |
| content read is at most 16384 characters | `ValueError("private database connection exceeds size limit")` |
| JSON parses | `json.JSONDecodeError` (a `ValueError`) |
| `sha256` of the canonical re-serialisation (`json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)`, UTF-8) equals the digest; value is an object with `format == "mycel.postgres-connection/1"` (`CONNECTION_FORMAT`, database.py:18) and a non-empty string `dsn` | `ValueError("private database connection differs from its pinned configuration")` |

Returns `value["dsn"]`. The digest covers the parsed content, not the file bytes.

Tests state: the configuration file with a private reference does not contain the DSN; `config.database_dsn()` and `database.dsn()` return the same value; a missing file, a symlink, mode `0644`, changed content, a wrong pin, or an added `dsn` key all raise from both readers; the `MYCEL_PG_CONNECTION_*` variables win over `ARBOL_PG_DSN` (tests/test_database_connection_file.py).

### `connect(conn_dsn=None)` (database.py:76-85)

- `psycopg.connect(conn_dsn or dsn(), autocommit=True, row_factory=dict_row)`.
- If `MYCEL_PG_SCHEMA` or `ARBOL_PG_SCHEMA` is set: the name must satisfy `schema.replace("_", "").isalnum()`, else `ValueError("invalid PostgreSQL schema name: ...")`; then `CREATE SCHEMA IF NOT EXISTS "<schema>"` and `SET search_path TO "<schema>"`.
- Every connection is in autocommit mode. Explicit `conn.commit()` calls in the code (config.py:152; cli.py:204, 206) have nothing to commit (inferred).

### Schema creation

`store.ensure_schema(conn)` (store.py:186-206) runs once per process (module flag guarded by a thread lock). In one transaction it:
1. executes the `DDL` string (store.py:38-179): `CREATE TABLE IF NOT EXISTS` for `kn_documents`, `kn_chunks`, `kn_derivations`, `kn_identity_log`, `kn_ingest_runs`, `kn_drifts`, `kn_drift_sources`, `kn_repos`, `kn_overlays`, `kn_activity`; `CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public`; `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` for later columns (`embedding public.vector(1024)`, `origin`, `tier`, `lang`, `symbol_kind`, `line_start`, `line_end`, `repo`, `meta`, `code_subdirs`, `code_root`); indexes including an HNSW index on `embedding`; `DROP INDEX IF EXISTS kn_documents_path_present`;
2. inserts a `kn_repos` row `('arbol', true, 'voyage', now)` unless a row named `Arbol` exists (`ON CONFLICT DO NOTHING`) (store.py:134-137);
3. sets `code_subdirs = ["daemons","drivers","renderer/apps","cli","tests"]` on row `arbol` when it is null (store.py:142-143);
4. `LOCK TABLE kn_documents, kn_chunks, kn_repos IN SHARE ROW EXCLUSIVE MODE`, then `repo_identity.migrate_arbol(conn)`;
5. sets the column default of `kn_documents.repo` and `kn_chunks.repo` to `'arbol'`.

Schema statements outside that block:
- `ALTER TABLE kn_repos ADD COLUMN IF NOT EXISTS artifact_root TEXT`, on every call of `list_repo_flags` and up to twice per `set_repo_flags` (store.py:1063, 1093, 1096);
- `ALTER TABLE kn_repos ADD COLUMN IF NOT EXISTS last_sync_ms BIGINT` (syncpass.py:143);
- `CREATE INDEX IF NOT EXISTS kn_chunks_bm25 ON kn_chunks USING bm25 (id, raw_text, natural_key) WITH (key_field='id')`, attempted on every search and ignored on failure (embedder.py:313-323).

Tables are unqualified `kn_*` names and live in whatever schema the connection's `search_path` selects (store.py:4-6).

<!-- sources:
mycel_deprecated_v1:mycel/database.py#dsn
mycel_deprecated_v1:mycel/database.py#configured_dsn
mycel_deprecated_v1:mycel/database.py#private_dsn
mycel_deprecated_v1:mycel/database.py#connect
mycel_deprecated_v1:mycel/config.py#database_dsn
mycel_deprecated_v1:mycel/cli.py#_export_dsn
mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema
mycel_deprecated_v1:mycel/knowledge/store.py#list_repo_flags
mycel_deprecated_v1:mycel/knowledge/embedder.py#ensure_bm25_index
mycel_deprecated_v1:mycel/repo_identity.py#migrate_arbol
mycel_deprecated_v1:tests/test_database_connection_file.py#test_invalid_private_configuration_never_falls_back
mycel_deprecated_v1:tests/test_database_connection_file.py#test_explicit_pinned_environment_selects_connection_before_legacy_dsn
-->

---

## 7. Repository identity and scope

### Repository key

- `canonical_repo(name)` (repo_identity.py:8-12): an empty value is returned unchanged; otherwise the name is split at the first `@`, and a base that is exactly `Arbol` becomes `arbol`. Nothing else is changed. Keys are case-sensitive: `ARBOL` stays `ARBOL`.
- A key may carry an overlay suffix `<repo>@<branch>`; the suffix is preserved.
- `canonical_repos(dict)` (repo_identity.py:15-23) merges entries that collapse to the same key; fields of the entry already spelled canonically win, fields that exist only under the legacy spelling survive.
- `migrate_arbol(conn)` (repo_identity.py:26-66) runs inside `ensure_schema`. It moves `Arbol` and `Arbol@*` documents, chunks and overlays to `arbol`. It raises `ValueError` when both spellings hold a present document at the same path with a different hash or source type, or conflicting overlays. Where both hold the same present path, the `arbol` copy is set to `orphaned` (its chunks to `absent`) and the `Arbol` copy is kept and renamed.

### Organizations

- Declared under `[organizations.<name>]` (section 5). `organizations.configured(cfg)` (organizations.py:9-27) raises `ValueError` for a blank name, two names equal under `casefold()`, a missing `root`, or a relative `artifact_root`. It returns dicts `{name, root, url, artifact_root?}` with `root` expanded and resolved to an absolute path.
- `organizations.resolve(value)`: lookup by name, case-insensitive (organizations.py:30-33).
- Membership, `organizations.members(org)` (organizations.py:36-42): the direct children of `root` that are directories, are not symlinks, and contain `.git` (file or directory) or a `.bare` directory. Hidden names are included (for example a member named `.github`, tests/test_organizations.py:46-51). The repository key of a member is its folder name. Membership is recomputed from the file system each time.
- Organization corpus, `organizations.artifact_root(org)` (organizations.py:45-48): the configured `artifact_root`, else `~/Artifacts/<basename of root>`.
- `organizations.for_path(path)`: the organization with the longest root that contains the resolved path (organizations.py:51-56).

### `RepositoryLocations` (locations.py:16-81)

One instance reads the configuration file once and enumerates the members of every organization. The module-level helpers `locations.code_root` / `locations.artifact_root` build a new instance on every call (locations.py:84-89).

- `settings(repo, flags)`: `{**flags, **file settings}`; a key present in the file wins over the database flag (locations.py:42-44; test at tests/test_repository_locations.py:35-43).
- `organization(repo, flags)` (locations.py:46-58): with an explicit `code_root`, the organization whose root is exactly the parent folder of that path, else none. Without one, the organization that has a member of that name; more than one raises `ValueError("repository '<name>' belongs to multiple organizations; set code_root")`.

Code root precedence, `code_root(repo, flags)` (locations.py:60-70), first match wins:

| # | Source |
|---|---|
| 1 | `ARBOL_KN_CODE_ROOT`, only when the repository is `arbol` |
| 2 | `code_root` from the file, else from the database flag (`~` expanded) |
| 3 | the member checkout of the repository's organization |
| 4 | `~/repo/sylvan-stack/<repo>` if that directory exists |
| 5 | `~/repo/<repo>` |

`syncpass.code_root` adds one rule on top (syncpass.py:75-85): for repository `arbol`, when the result ends with `/Arbol/main` and does not exist, and its parent contains a `.git` directory, the parent is returned.

Artifact root precedence, `artifact_root(repo, flags)` (locations.py:72-81), first match wins:

| # | Source |
|---|---|
| 1 | `ARBOL_KN_CORPUS`, only when the repository is `arbol` |
| 2 | `artifact_root` from the file, else from the database flag |
| 3 | `<organization corpus>/repos/<repo>` when the repository has an organization |
| 4 | `~/Artifacts/Arbol` when the repository is `arbol` |
| 5 | `~/Artifacts/<repo>` |

### `scope.resolve(paths=None) -> (repo, overlay)` (scope.py:28-47)

Precedence, first match wins:

1. `ARBOL_REPO` (stripped, non-empty): return `(canonical_repo(value), ARBOL_OVERLAY or None)`.
2. For each candidate in the given `paths` and then the current directory, each expanded and resolved:
   1. the first binding whose root contains the candidate. Bindings come from `RepositoryLocations.scope_bindings()` (locations.py:31-40): for every repository name (configured repositories plus organization members) its resolved code root (marked as code) and its resolved artifact root; for every organization its root and its corpus. They are ordered by number of path components, longest first. A code binding returns `(repo, _branch(...))`; any other binding returns `(name, None)`. A path inside an organization root but outside every member resolves to the organization's name (tests/test_organizations.py:54-57).
   2. otherwise the legacy rule `_legacy_scope` (scope.py:50-62): if the candidate lies under `~/repo` or `~/.arbol/mirrors` (both resolved), the repository is the first path component, or the second when the first is `sylvan-stack`.
3. Fallback: `("arbol", None)` (scope.py:47).

Overlay branch, `_branch(path, container, env_overlay)` (scope.py:65-76):
- `<container>/.bare` is not a directory: `None`.
- Otherwise walk upward from the path to the first directory containing a `.git` file. If `ARBOL_OVERLAY` is set, return it (empty string gives `None`). Else return the directory path relative to the container, or `None` when that is `master` or `main`.
- No such directory: `ARBOL_OVERLAY or None`.

### Hard-coded roots and names

| Literal | Use | Location |
|---|---|---|
| `Arbol` → `arbol` | the only alias | repo_identity.py:12 |
| `"arbol"` | fallback repository of scope resolution | scope.py:47 |
| `~/repo`, `~/.arbol/mirrors` | legacy scope roots | scope.py:25 |
| `sylvan-stack` | transparent grouping folder | scope.py:55; locations.py:69; organizations.py:73 |
| `~/repo/sylvan-stack/<repo>`, `~/repo/<repo>` | default code root | locations.py:69-70 |
| `~/repo/<name>` | worktree container looked up by the pass | syncpass.py:290; also retrieval.py:37 |
| `~/Artifacts/Arbol`, `~/Artifacts/<repo>` | default artifact root | locations.py:81 |
| `~/Artifacts/<org root basename>` | default organization corpus | organizations.py:47-48 |
| `master`, `main` | corpus worktree / non-overlay branches | syncpass.py:69; scope.py:74 |
| `/Arbol/main` | retired layout repaired for `arbol` | syncpass.py:81 |
| `mycel` | shared artifact repository added to every unified search | embedder.py:383; retrieval.py:147-148 |
| `'arbol'` row with `code_subdirs` `daemons, drivers, renderer/apps, cli, tests` | seeded by the schema DDL | store.py:134-143 |

<!-- sources:
mycel_deprecated_v1:mycel/repo_identity.py#canonical_repo
mycel_deprecated_v1:mycel/repo_identity.py#canonical_repos
mycel_deprecated_v1:mycel/repo_identity.py#migrate_arbol
mycel_deprecated_v1:mycel/scope.py#resolve
mycel_deprecated_v1:mycel/scope.py#_legacy_scope
mycel_deprecated_v1:mycel/scope.py#_branch
mycel_deprecated_v1:mycel/scope.py#_roots
mycel_deprecated_v1:mycel/locations.py#RepositoryLocations
mycel_deprecated_v1:mycel/locations.py#RepositoryLocations.scope_bindings
mycel_deprecated_v1:mycel/locations.py#RepositoryLocations.settings
mycel_deprecated_v1:mycel/locations.py#RepositoryLocations.organization
mycel_deprecated_v1:mycel/locations.py#RepositoryLocations.code_root
mycel_deprecated_v1:mycel/locations.py#RepositoryLocations.artifact_root
mycel_deprecated_v1:mycel/organizations.py#configured
mycel_deprecated_v1:mycel/organizations.py#resolve
mycel_deprecated_v1:mycel/organizations.py#members
mycel_deprecated_v1:mycel/organizations.py#artifact_root
mycel_deprecated_v1:mycel/organizations.py#for_path
mycel_deprecated_v1:mycel/organizations.py#repo_dirs
mycel_deprecated_v1:mycel/syncpass.py#code_root
mycel_deprecated_v1:mycel/syncpass.py#artifact_root
mycel_deprecated_v1:tests/test_repository_locations.py#test_file_overrides_win_over_organization_and_stale_database_flags
mycel_deprecated_v1:tests/test_repository_locations.py#test_scope_uses_configured_repos_outside_legacy_roots
mycel_deprecated_v1:tests/test_repository_locations.py#test_duplicate_members_require_explicit_code_root
mycel_deprecated_v1:tests/test_organizations.py#test_scope_distinguishes_member_and_organization
-->

---

## 8. Command line

### Common behaviour of `main(argv=None)` (cli.py:709-884)

1. `truststore.inject_into_ssl()` is attempted; any failure is ignored (cli.py:714-718).
2. `_export_dsn()` (cli.py:719).
3. Dispatch to `better-grep` before argument parsing: when `os.path.basename(sys.argv[0]) == "better-grep"`, run `better_grep.run(<all arguments>)`; when the first argument is `better-grep`, run `better_grep.run(<remaining arguments>)` (cli.py:720-725).
4. `argparse` parser `prog="mycel"`; `--version` prints `mycel 0.1.0` and exits 0; a subcommand is required.
5. The command function's return value is the exit code. `KeyboardInterrupt` returns 130. Any other `Exception` prints one line `{"error": "<str(e)>"}` to stderr and returns 1 (cli.py:878-884).

Output convention: one JSON document on stdout, printed with `indent=2`; progress and warnings on stderr.

| Exit code | Meaning |
|---|---|
| 0 | command completed |
| 1 | an exception, or an explicit error of `raptor` |
| 2 | argparse usage error; `wt` |
| 130 | interrupted |
| grep's own code | `better-grep` |

### `search`

| Argument | Default | Note |
|---|---|---|
| `query` | required | |
| `--k` | `12` | maximum number of results |
| `--repo` | `""` | empty means: resolve from `--path` / current directory, fallback `arbol` |
| `--path P` | none, repeatable | resolve repository and overlay from this path |
| `--overlay` | `""` | overlay branch |
| `--only` | none; choices `code`, `docs` | |
| `--no-fresh` | off | skip the staleness check and repository pass |

Behaviour (`search_payload`, cli.py:22-64):
1. With `--repo`: that repository, overlay `None`. Without: `scope.resolve(paths)`. A non-empty `--overlay` replaces the overlay in both cases.
2. If the repository name matches an organization name (case-insensitive): an overlay raises `ValueError("an organization search requires per-repository overlay selection")`; otherwise the command runs one complete search per member, in member-name order, and returns the organization shape below.
3. Connect; `config.load_apply(conn, force=True)`.
4. `--only docs`: `embedder.doc_search(conn, query, k, repo=...)`, wrapped by `retrieval._payload`. No freshness check, no validation of `query` or `k`.
5. Otherwise `retrieval.search(conn, query, repo=..., overlay=..., k=k, code_only=(only == "code"), freshness=not no_fresh)`. It raises `ValueError("missing query")` for a blank query and `ValueError("k must be between 1 and 100")` (retrieval.py:137-141).
6. Add `"transport": "cli"`.

Printed shape, single repository (retrieval.py:111-129; embedder.py:623-636; retrieval.py:102-107):

```
{
  "schema_version": 2,
  "repo": "<canonical repo>",
  "overlay": null | "<branch>",
  "results": [
    {
      "id", "path", "natural_key", "origin", "repo", "overlay": bool,
      "symbol": "<symbol>" | null, "lang", "symbol_kind",
      "line_start", "line_end", "score",
      "dense_rank": int | null, "bm25_rank": int | null,
      "via": null | {"doc", "repo", "stale", "heartwood"},
      "documented_in": [{"doc", "stale"}],
      "preview": "<first 240 chars, then … when longer>",
      "read_path": "<absolute path>" | null,
      "readable": bool,
      "unavailable_reason": "<text>"        (only when read_path is null)
    }
  ],
  "dense": int, "bm25": int,
  "timings": {"bm25_index_ms", "query_embedding_ms", "dense_sql_ms", "bm25_sql_ms",
              "ranking_bridge_ms", "hydrate_ms", "total_ms"},
  "freshness": {"checked": bool, "refreshed": bool,
                "coalesced": bool, "repos": {"<repo>": {"refreshed": bool, "coalesced": bool}},
                "wait_ms": int},
  "transport": "cli"
}
```

- `freshness` is `{"checked": false, "refreshed": false}` with `--no-fresh` and with `--only docs`; the keys `coalesced`, `repos`, `wait_ms` exist only when the check ran (retrieval.py:142, 163-166).
- `repos[<name>].refreshed` is true whenever a repository pass ran, whether or not it changed anything (retrieval.py:159-162).
- `timings.hydrate_ms` is absent when there are no results (embedder.py:606-609).
- With `--only docs` a result has only `id, path, natural_key, origin, stale, heartwood, preview` plus the three read fields, and `timings` is `{}` (embedder.py:304-308).
- `unavailable_reason` values: `"synthetic search result"`, `"overlay worktree is unavailable"`, `"indexed path is not a relative file path"`, `"indexed path escapes its configured root"`, `"indexed source no longer exists"`, `"search origin is not filesystem-readable: <origin>"` (retrieval.py:53-100).

Printed shape, organization (cli.py:40-44): `{"schema_version": 2, "organization": "<name>", "transport": "cli", "repositories": [<one single-repository payload per member>]}`.

Exit code 0, also with zero results.

### `better-grep`

Reached as `mycel better-grep ...`, or as an executable named `better-grep` (better_grep.py:47-98).

| Input | Behaviour | Exit |
|---|---|---|
| exactly `-h` or `--help` | prints two usage lines on stdout | 0 |
| exactly `--version` | prints `better-grep 0.1.0` | 0 |
| no arguments | prints usage on stderr | 2 |
| anything else | see below | grep's code |

1. The pattern and paths are guessed from the arguments: flags are skipped, flags listed in `_VALUE_FLAGS` consume the next argument, `--flag=value` is skipped, the first remaining word is the pattern unless `-e` / `--regexp` was seen, the rest are paths (better_grep.py:9-39).
2. With no paths, a terminal on stdin, and one of the exact arguments `-r`, `-R`, `--recursive`, a `.` is appended (better_grep.py:61-63).
3. Runs `/usr/bin/grep <arguments>` (fixed path) with inherited standard streams (better_grep.py:65).
4. `BETTER_GREP_PLAIN=1`: return.
5. The semantic query is the pattern with each of `\ ^ $ . | ? * + ( ) [ ] { }` replaced by a space and whitespace collapsed. Shorter than 3 characters: return (better_grep.py:42-44, 68-70).
6. `search_payload(query, k=5, paths=<grep paths>, no_fresh=True)`. Any exception prints `(mycel tail unavailable: <error>)` on stderr (better_grep.py:71-76).
7. With results, prints on stdout: a header `── mycel: related by meaning (not literal matches) ` followed by 20 `─`; one line per result `  <path>#<symbol>  L<start>-<end>  score <score>` with an optional `  ⇐ via <doc>` suffix (plus ` ⚠stale`, ` heartwood`); then, if any, a header `── mycel: documented in ` followed by 47 `─` and one line per document (better_grep.py:78-97).

The tail does not depend on grep's exit code or output flags.

### `sync`

| Argument | Default |
|---|---|
| `--no-embed` | off |

Runs `run_pass`; then, when the pending count is non-zero and `--no-embed` is absent, `embedder.embed_pending(conn)` with progress lines `  embed <done>/<total>` on stderr (cli.py:96-112).

Printed shape: `{"docs_edited", "docs_new", "stale", "code_added", "code_updated", "code_removed", "pending_embed", "config_error"?, "mirror_warning"?, "embedded"?, "embed_skipped"?}`, or for a coalesced pass `{"coalesced": true, "reason", "pending_embed", "embedded"?, "embed_skipped"?}`. Exit 0.

### `embed`

No arguments. Prints the result of `embedder.embed_pending(conn)`: `{"embedded": int, "total": int, "skipped": {"disabled"?: int, "voyage"?: int, "local"?: int, "<other profile>"?: int}}` (embedder.py:229). Exit 0.

Scope of `embed_pending` without arguments: present chunks without an embedding whose `repo` contains no `@` (embedder.py:168-181). Chunks of disabled repositories are counted under `skipped.disabled`; chunks whose profile's embedder is unavailable are counted under the profile name (embedder.py:185-195).

### `status`

| Argument | Default |
|---|---|
| `--repo` | `"Arbol"` (cli.py:768; an empty value also becomes `"Arbol"`, cli.py:176) |

Printed shape (store.py:1112-1126; cli.py:176-181; local_embedder.py:60-68):

```
{
  "documents": int,     all kn_documents rows of the repo, any state or source type
  "chunks": int,        chunks with state='present'
  "stale": int,         of those, stale
  "edges": int,         derivations whose child chunk is in the repo
  "open_drifts": int,
  "heartwood": int,     present documents with meta.heartwood true
  "embedder": {
    "has_key": bool,    a Voyage key exists in the macOS Keychain (service com.arbol.embedder, account voyage)
    "embedded": int,    present chunks with an embedding, all repositories
    "pending": int,     present chunks without one, all repositories
    "local_model": {"model": "Qwen3-Embedding-0.6B", "dim": 1024, "available": bool,
                    "dir": str, "bytes": int,
                    "provider": {"up": bool, "loaded": bool | null, "url": str}}
  }
}
```

`provider` is obtained with an HTTP GET to `<provider url>/healthz`, timeout 2 s (local_embedder.py:50-57). Exit 0.

### `activity`

| Argument | Default |
|---|---|
| `--k` | `25` |
| `--repo` | `""` (no filter) |
| `--kind` | `""` (no filter) |

Prints `{"activity": [{"id", "ts", "kind", "repo", "actor", "summary", "duration_ms", "error"}]}`, newest first; the limit is clamped to 1..500; filters are exact matches on the `repo` and `kind` columns (store.py:1154-1171). Exit 0.

### `drifts`

| Argument | Default |
|---|---|
| `--repo` | `"Arbol"` (cli.py:772, 191) |

Prints `{"drifts": [{"id", "chunk_id", "chunk": "<path> › <natural_key>", "path", "natural_key", "source", "source_id", "sources": [{"id", "label", "reason"}], "reason", "opened_at"}]}` for rows of `kn_drifts` with `status='open'` whose chunk belongs to the repository, newest first (store.py:636-653). Exit 0.

### `derive`

| Argument | Meaning |
|---|---|
| `child` | Source Ref of the derived chunk: `repo:path#symbol` or `repo:path#Heading` |
| `source` | Source Ref of the governing chunk or file: `repo:path`, `repo:path#symbol` or `repo:path#Heading` |

Calls `store.assert_derivation(conn, child, source)`, which writes one `asserted` derivation per resolved child and source pair, then `store.detect(conn)` (cli.py:198-210).

Prints `{"child_ref", "source_ref", "children": [{"id", "label"}], "sources": [{"id", "label"}], "edges": int, "detect": {"edges", "direct", "stale"}}`.

Errors (exit 1, JSON on stderr): `"child Source Ref did not resolve: <ref>"`, `"source Source Ref did not resolve: <ref>"`, `"child Source Ref must identify a chunk; add #symbol or #Heading: <ref>"` (store.py:501-515).

### `repos`

| Argument | Default |
|---|---|
| `action` | `list` (the only choice, optional) |
| `--root` | `""`, meaning `~/repo` (cli.py:268) |
| `--organization` | `""`; when given, its root replaces `--root` |

An unknown organization raises `ValueError("unknown organization: <value>")` before any database connection (cli.py:270-274; test at tests/test_organizations.py:69-72).

Listed folders, `organizations.repo_dirs(root)` (organizations.py:59-78): when the root is an organization root, its members; otherwise each direct child folder that is not a symlink and not hidden, where a child that is an organization root is replaced by its members and a child named `sylvan-stack` (any case) is replaced by its own non-hidden, non-symlink child folders.

Prints `{"root": str, "repos": [{"name", "path", "mtime", "mycel_enabled", "embedder_profile", "has_artifacts", "artifact_root", "container", "organization"?, "worktrees"?}]}`, sorted by `mtime` descending, then lower-cased name (cli.py:280-302). `worktrees` (entries `{branch, path, exists}`) appears only when `<path>/.bare` exists. Exit 0.

### `raptor`

| Argument | Default |
|---|---|
| `action` | required; `status`, `plan`, `regen`, `build` |
| `--recipe` | `""`, meaning `raptor-agent` (raptor.py:16; cli.py:146) |
| `--repo` | `"Arbol"` (cli.py:762) |
| `--regen` | off; only read by `plan` |

| Action | What the code does | Output |
|---|---|---|
| `status` | counts stale summaries; checks whether an `infer` executable is found | `{"stale_summaries": int, "completion_provider": bool}`, exit 0 |
| `plan` | `raptor.plan_build`, with progress lines on stderr | `{"corpus_chunks", "total_summaries", "top_nodes", "tiers": [{"tier", "nodes_in", "summaries", "carried"}]}`, exit 0 |
| `plan --regen` | `raptor.plan_regen` | `{"stale_summaries", "members", "by_tier": [{"tier", "count"}]}`, exit 0 |
| `regen`, `build` | no `infer` executable: prints `{"error": <UNAVAILABLE>}` on stderr, exit 1 (cli.py:143-145). Otherwise the code reaches `subprocess.run([binary, "resolve", "--recipe", name], ...)` (cli.py:151) | see below |

`UNAVAILABLE` is the fixed text (completion_client.py:15-16):

```
no completion provider: the `infer` executable was not found; RAPTOR generation is disabled while retrieval and embedding remain available
```

`cli.py` does not import `subprocess` at module level and `_cmd_raptor` does not import it either (cli.py:14-17, 127-130). As written, line 151 raises `NameError`; `main` reports `{"error": "name 'subprocess' is not defined"}` and exits 1. The code after that line (cli.py:152-166) would: parse the stdout of `infer resolve --recipe <name>` as JSON; on `ok` false print `{"error": ...}` and exit 1; call `raptor.regen_stale` or `raptor.build_tree` with `ip_name = recipe["ip"] or ""`, `model = recipe["model"]`, `thinking = recipe["thinking"] or "none"`, progress lines `  tier <t>: <done>/<total> (<n> summaries)` on stderr; and print the result without its `tiers` key.

### Retired commands (one line each)

- `wt`: prints `{"error": "Worktree management is deprecated. Use the repository folder directly."}` on stderr and returns 2 (cli.py:424-426).
- `pull`: fast-forwards `master` of a worktree container under `~/repo`, then runs a full pass (cli.py:481-547).
- `overlay`: registers, lists, refreshes or drops Branch Overlays (cli.py:213-255).
- `mirror` and two tracker-specific commands: fetched and wrote content of the previous project's issue tracker, wiki and code host (cli.py:594-706).
- `secrets`: stores, tests, lists or deletes tokens (cli.py:564-591).

### Defaults that name a specific repository

| Where | Default | Location |
|---|---|---|
| `status --repo` | `Arbol` | cli.py:768, 176 |
| `drifts --repo` | `Arbol` | cli.py:772, 191 |
| `raptor --repo` | `Arbol` | cli.py:762 |
| `search` without a resolvable path | `arbol` | scope.py:47 (help text at cli.py:740) |
| unified `search` | also checks freshness of, and reads documents from, `mycel` | retrieval.py:147-148; embedder.py:383, 400-405 |
| function parameters `repo: str = "Arbol"` | 25 signatures in `store.py`, `embedder.py`, `raptor.py`, `fs.py` | for example raptor.py:175, store.py:658 |

<!-- sources:
mycel_deprecated_v1:mycel/cli.py#main
mycel_deprecated_v1:mycel/cli.py#search_payload
mycel_deprecated_v1:mycel/cli.py#_cmd_search
mycel_deprecated_v1:mycel/cli.py#_cmd_sync
mycel_deprecated_v1:mycel/cli.py#_cmd_embed
mycel_deprecated_v1:mycel/cli.py#_cmd_status
mycel_deprecated_v1:mycel/cli.py#_cmd_activity
mycel_deprecated_v1:mycel/cli.py#_cmd_drifts
mycel_deprecated_v1:mycel/cli.py#_cmd_derive
mycel_deprecated_v1:mycel/cli.py#_cmd_repos
mycel_deprecated_v1:mycel/cli.py#_cmd_raptor
mycel_deprecated_v1:mycel/cli.py#_cmd_wt
mycel_deprecated_v1:mycel/cli.py#_connect_with_config
mycel_deprecated_v1:mycel/better_grep.py#run
mycel_deprecated_v1:mycel/better_grep.py#_parse
mycel_deprecated_v1:mycel/better_grep.py#_semantic_query
mycel_deprecated_v1:mycel/better_grep.py#main
mycel_deprecated_v1:mycel/retrieval.py#search
mycel_deprecated_v1:mycel/retrieval.py#_payload
mycel_deprecated_v1:mycel/retrieval.py#_read_location
mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search
mycel_deprecated_v1:mycel/knowledge/embedder.py#doc_search
mycel_deprecated_v1:mycel/knowledge/embedder.py#embed_pending
mycel_deprecated_v1:mycel/knowledge/store.py#status
mycel_deprecated_v1:mycel/knowledge/store.py#list_activity
mycel_deprecated_v1:mycel/knowledge/store.py#list_drifts
mycel_deprecated_v1:mycel/knowledge/store.py#assert_derivation
mycel_deprecated_v1:mycel/knowledge/local_embedder.py#status
mycel_deprecated_v1:mycel/organizations.py#repo_dirs
mycel_deprecated_v1:tests/test_cli_metadata.py#test_mycel_version
mycel_deprecated_v1:tests/test_organizations.py#test_search_organization_fans_out_to_each_member
mycel_deprecated_v1:tests/test_worktree_cli.py#test_worktree_commands_retired_without_connecting
-->

---

## 9. RAPTOR summaries

### Constants

| Constant | Value | Location |
|---|---|---|
| `DEFAULT_RECIPE` | `"raptor-agent"` | raptor.py:16 |
| `SUMMARY_DOC_PATH` | `"synthetic/raptor"` | raptor.py:34 |
| `_STOP_NODES` | `10` | raptor.py:35 |
| `_MAX_TIERS` | `5` | raptor.py:36 |
| `_MEMBER_CHARS` | `1200` | raptor.py:37 |
| `_TOTAL_CHARS` | `48000` | raptor.py:38 |
| `_MAX_CONCURRENCY` | `24` | raptor.py:44 |
| `_MAX_COMPONENTS` | `150` | clustering.py:17 |
| `_PCA_DIMS` | `10` | clustering.py:18 |
| `_COVARIANCE` | `"spherical"` | clustering.py:19 |
| `_PROB_THRESHOLD` | `0.10` | clustering.py:20 |
| `_TARGET_BRANCHING` | `8` | clustering.py:26 |

### Clustering: `clustering.cluster(ids, vectors, ...)` (clustering.py:29-71)

1. `n <= 2`: one cluster holding all ids (or none for an empty input).
2. Dimension reduction: PCA to `min(10, vector length, n - 1)` dimensions, `random_state=0`, applied only when the vectors are longer than that.
3. Component count: for `k` from 1 to `max_k = max(1, min(150, n - 1, ceil(n / 8)))`, fit `GaussianMixture(n_components=k, covariance_type="spherical", reg_covar=1e-4, random_state=0)` and keep the fit with the lowest BIC (strictly lower, so the smallest `k` wins a tie).
4. Soft membership: each item joins every component whose posterior probability is at least `0.10`; an item with none joins its most likely component. Empty components are dropped.
5. Result: a list of clusters (lists of ids). One id can appear in several clusters.

### What is clustered, and what is excluded

Leaves are selected by (raptor.py:196-199, repeated at 424-428):

```
state='present' AND origin='corpus' AND embedding IS NOT NULL AND repo=<repo>
AND NOT COALESCE((meta->>'heartwood')::boolean, false)
AND NOT COALESCE((meta->>'generated')::boolean, false)
```

Excluded as a consequence:
- code chunks (`origin='code'`) and earlier summaries (`origin='summary'`);
- chunks without an embedding;
- chunks of documents whose frontmatter has `status: heartwood` (chunk meta `heartwood: true`) or `generated: true|1|yes` (chunk meta `generated: true`), which includes the code map (chunker.py:66-76; store.py:284);
- overlay namespaces (`repo` is matched exactly).

### Tiers: `raptor.build_tree(conn, *, ip_name, model, thinking="none", repo="Arbol", progress, on_live, on_stage, cancel)` (raptor.py:175-297)

1. `ensure_schema`; `_clear(conn, repo)`: delete every derivation whose parent or child is a summary chunk of the repository, then delete all `kn_chunks` rows with `origin='summary' AND repo=<repo>` (raptor.py:83-90).
2. Find or create the synthetic document `(path='synthetic/raptor', source_type='summary', state='present', repo=<repo>)` with `content_hash = sha("synthetic/raptor")` (raptor.py:69-80).
3. Load the leaves as `(id, raw_text, vector)`.
4. For `tier` from 1 to 5:
   1. stop when the node count is `<= 10`; stop with `cancelled=True` when `cancel()` returns true;
   2. cluster the current nodes;
   3. clusters with exactly one member are carried to the next tier unchanged; each cluster with more than one member becomes one summary job, its `ordinal` being the cluster's index (raptor.py:222-223);
   4. run the jobs on a thread pool of `min(24, number of jobs)` workers (at least 1). Each worker opens its own database connection, builds the prompt, and requests one completion (raptor.py:229-250);
   5. if any job raised `CompletionError`: set `cancelled=True`, discard every result of this tier, stop. Any other exception is re-raised after the pool has finished (raptor.py:260-276);
   6. persist, in ordinal order, on the caller's connection (raptor.py:279-289): insert the summary chunk; embed its text with `embedder.embed([text], input_type="document")`; store the vector; write one generation edge per member; the next tier's nodes are the carried singletons plus the new summaries with their vectors.
5. Return `{"cleared": int, "tiers": <highest tier completed>, "summaries": int, "top_nodes": <nodes left at the top>, "cancelled": bool}` and write a `raptor_build` activity row.

### Prompts

- `_instruction(name)` (raptor.py:46-56) reads `<root>/<name>` as UTF-8 and strips it, where `root = expanduser(os.environ.get("MYCEL_SYSTEM_INSTRUCTIONS", "~/Artifacts/mycel/system-instructions"))`. An unreadable file raises `RuntimeError("required Mycel system instruction is unavailable: <path>")`; an empty one raises `RuntimeError("required Mycel system instruction is empty: <path>")`.
- `_raptor_prompts(sections)` (raptor.py:59-62): the system text is the file `raptor-summary.md`; the request is `string.Template(<content of raptor-request.md.tmpl>).substitute(sections=sections)`.
- `_prompt_sections(members)` (raptor.py:93-103): each member's `raw_text` cut to 1200 characters; members are appended in order until the next one would take the total above 48000 characters, at which point the rest are left out; parts are joined with `"\n\n---\n\n"`.
- Both files are read again for every summary job.

### Completions

`completion_client` (completion_client.py:1-66):

- Executable lookup, `_infer_bin()`: `INFER_BIN` (after `~` expansion; if set but not a file the result is "not found", with no further lookup); else `~/bin/infer`; else a file named `infer` next to `sys.executable`; else `shutil.which("infer")`.
- `run(params, *, timeout=300.0)`: no executable raises `CompletionError(UNAVAILABLE)`.
- Command line built by `_run_infer`: `[<infer>, "complete", "--recipe", "<descriptor>", "--max-minutes", "<n>"]`, plus `["--system", <system text>]` when a system text is given. The descriptor is `<ip_name lower-cased>:<model>:<thinking or "none">`, without the first part when `ip_name` is empty. `n = max(1, int(timeout // 60))`, so 5 for the default. The request text is passed on standard input (completion_client.py:41-51).
- Result: `{"text": <stdout, unmodified>}`.
- Errors, all `CompletionError`: timeout (`"infer complete timed out after <s>s"`), launch failure (`"infer failed to launch: <error>"`), non-zero exit (`"infer complete: <last line of stderr, or 'exit N'>"`).
- The parameter `max_tokens: 1024` that `raptor.py` passes (raptor.py:244, 348) is not forwarded to `infer`.
- Retries: none in this code.
- Concurrency: up to 24 `infer` processes at once per tier.
- Recipe: the `--recipe` option of `mycel raptor` is a name handed to `infer resolve --recipe <name>`; the fields `ip`, `model`, `thinking` of its JSON answer become the descriptor (cli.py:146-160; see section 8 for why this is not reached).

`command_executor.run` executes all of these with `subprocess.run(argv, capture_output=True, timeout=..., input=..., text=..., env=..., cwd=...)` unless a host has installed its own executor with `install_executor`; nothing in this repository installs one (command_executor.py:47-54; tests/test_command_executor.py:25-34).

### Storage

Summary chunk, `_insert_summary` (raptor.py:106-114): one `kn_chunks` row with

| Column | Value |
|---|---|
| `id` | new ULID |
| `document_id` | the synthetic document |
| `natural_key` | `raptor/L<tier>/<id>` |
| `ordinal` | cluster index |
| `level` | `0` |
| `raw_text` | the completion text |
| `content_hash` | `sha(text)` |
| `role` | `'derived'` |
| `state` | `'present'` |
| `origin` | `'summary'` |
| `tier` | 1..5 |
| `repo` | canonical repository |
| `embedding` | set by a separate `UPDATE` after embedding |

Generation edge, `store.derive(conn, summary_id, member_id, kind="generated")` (store.py:472-484): one `kn_derivations` row with `parent_id = <member>`, `child_id = <summary>`, `kind = 'generated'`, `policy = 'auto'`, `hash_at_gen = <member's content hash now>`; an existing `(parent_id, child_id)` pair is updated.

### How stale summaries are found

- `store.detect(conn)` (store.py:528-566) walks every derivation in the database. A child is stale when a parent row no longer exists (`"source removed (<id prefix>)"`) or the parent's current `content_hash` differs from the edge's `hash_at_gen` (`"source changed since generation (<id prefix>)"`). Staleness then spreads to every descendant (`"upstream chunk is stale (<id prefix>)"`). Chunks with meta `heartwood` or `generated` are never marked.
- `detect` runs in every documents refresh of a pass, in `mycel derive`, and at the end of `regen_stale`.
- A stale summary is a `kn_chunks` row with `origin='summary' AND state='present' AND stale=true AND repo=<repo>` (store.py:1106-1107; raptor.py:326-328).

### What each action does

| Action | Function | Behaviour |
|---|---|---|
| `status` | `store.count_stale_summaries`, `completion_client.available` | counts stale summaries; reports whether `infer` is found |
| `plan` | `raptor.plan_build` (raptor.py:413-464) | loads the same leaves, clusters tier by tier, and uses the mean vector of each multi-member cluster as a stand-in for its summary. Writes nothing. Returns counts per tier |
| `plan --regen` | `raptor.plan_regen` (raptor.py:467-486) | counts stale summaries by tier and the distinct present chunks that feed them. No clustering |
| `build` | `raptor.build_tree` | clear and rebuild, as above |
| `regen` | `raptor.regen_stale` (raptor.py:311-410) | see below |

`regen_stale`:
1. Select the stale summaries ordered by tier and ordinal. None: return `{"regenerated": 0, "stale": 0, "tiers": [], "cancelled": False}`.
2. For each tier, ascending: for each stale summary load its present members through its `generated` edges (`_stale_members`, ordered by tier and ordinal). A summary with no present member is skipped. Request the new texts concurrently, as in a build. A `CompletionError` sets `cancelled=True` and stops.
3. Persist: embed the text; `UPDATE kn_chunks SET raw_text, content_hash, embedding, stale=false, stale_because=NULL, last_seen` in place (same id, natural key and membership); re-run `derive` for each present member so `hash_at_gen` matches the member's current hash.
4. `detect(conn)`.
5. Return `{"regenerated": int, "stale": <number selected in step 1>, "tiers": [<tier numbers>], "cancelled": bool}`; write a `raptor_regen` activity row when `regenerated > 0`.

Membership is fixed between builds: new corpus chunks join no summary until the next `build` (raptor.py:318-320).

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/clustering.py#cluster
mycel_deprecated_v1:mycel/knowledge/raptor.py#build_tree
mycel_deprecated_v1:mycel/knowledge/raptor.py#regen_stale
mycel_deprecated_v1:mycel/knowledge/raptor.py#plan_build
mycel_deprecated_v1:mycel/knowledge/raptor.py#plan_regen
mycel_deprecated_v1:mycel/knowledge/raptor.py#_instruction
mycel_deprecated_v1:mycel/knowledge/raptor.py#_raptor_prompts
mycel_deprecated_v1:mycel/knowledge/raptor.py#_prompt_sections
mycel_deprecated_v1:mycel/knowledge/raptor.py#_clear
mycel_deprecated_v1:mycel/knowledge/raptor.py#_summary_doc_id
mycel_deprecated_v1:mycel/knowledge/raptor.py#_insert_summary
mycel_deprecated_v1:mycel/knowledge/raptor.py#_stale_members
mycel_deprecated_v1:mycel/knowledge/raptor.py#_worker_connection
mycel_deprecated_v1:mycel/completion_client.py#_infer_bin
mycel_deprecated_v1:mycel/completion_client.py#_run_infer
mycel_deprecated_v1:mycel/completion_client.py#run
mycel_deprecated_v1:mycel/completion_client.py#available
mycel_deprecated_v1:mycel/command_executor.py#run
mycel_deprecated_v1:mycel/command_executor.py#install_executor
mycel_deprecated_v1:mycel/knowledge/store.py#derive
mycel_deprecated_v1:mycel/knowledge/store.py#detect
mycel_deprecated_v1:mycel/knowledge/store.py#count_stale_summaries
mycel_deprecated_v1:mycel/knowledge/embedder.py#embed
mycel_deprecated_v1:mycel/knowledge/chunker.py#parse_frontmatter
mycel_deprecated_v1:mycel/cli.py#_cmd_raptor
mycel_deprecated_v1:tests/test_completion_routing.py#test_run_infer_contract
mycel_deprecated_v1:tests/test_command_executor.py#test_completion_keeps_recipe_input_and_output_contract
-->

---

## 10. Build and packaging

### Declared package (`pyproject.toml`)

| Field | Value |
|---|---|
| build backend | `setuptools.build_meta`, `setuptools>=68` |
| name, version | `mycel`, `0.1.0` (also `__version__ = "0.1.0"` in `mycel/__init__.py:3`) |
| `requires-python` | `>=3.12` |
| dependencies | `psycopg[binary]>=3.2`, `truststore>=0.9`, `numpy>=1.26`, `scikit-learn>=1.4`, `tree-sitter>=0.23`, `tree-sitter-typescript>=0.23`, `tree-sitter-javascript>=0.23`, `html2text>=2024.2`, `markdown>=3.6` |
| optional `browser` | `playwright>=1.62,<1.63` |
| console scripts | `mycel = mycel.cli:main`, `better-grep = mycel.better_grep:main` |
| packages | `mycel*` |

Where the dependencies are imported: `psycopg` in `database.py`; `truststore` in `cli.main`; `numpy` and `scikit-learn` in `clustering.py` and `raptor.py`; `tree-sitter*` in `code_chunker.py`; `html2text` only in the retired `mirror.py`; `markdown` only in the retired wiki-writing module; `playwright` only in the retired `browser_fetch.py`. `pytest` and `pyinstaller` are not declared; `README.md` installs them by hand.

### Executables (`Makefile`, `*.spec`, entry files)

- `PYTHON` is `.venv/bin/python` when it exists, else `python3`. `PREFIX` defaults to `$(HOME)`.
- `make build`: for each of `mycel.spec` and `better-grep.spec`, `PYINSTALLER_CONFIG_DIR=$(CURDIR)/.pyinstaller-cache $(PYTHON) -m PyInstaller --noconfirm --clean <spec>`.
- Both specs are one-file console builds without hidden imports, data files or UPX. `mycel.spec` builds `dist/mycel` from `mycel_entry.py` (`raise SystemExit(main())`). `better-grep.spec` builds `dist/better-grep` from `better_grep_entry.py` (`raise SystemExit(better_grep.run(sys.argv[1:]))`).
- `make install`: creates `$(PREFIX)/bin`; runs `dist/mycel --help`, `dist/mycel --version`, `dist/better-grep --help`, `dist/better-grep --version`; writes `needle` to `/tmp/mycel-better-grep-smoke.txt` and runs `BETTER_GREP_PLAIN=1 dist/better-grep -q needle <that file>`; then for each binary copies it to `<name>.new`, `chmod 755`, and `mv -f` onto `$(PREFIX)/bin/<name>`.
- `make test`: `$(PYTHON) -m pytest -q`. `make all`: `test build install`. `make clean`: removes `build`, `dist`, `.pyinstaller-cache`, `*.spec.bak`.
- `python -m mycel` also runs `cli.main` (`mycel/__main__.py`).

### Tests

Ten files under `tests/`, no `conftest.py`, no pytest configuration. Contracts they state, by area:
- command metadata: the version and help lines of both executables (test_cli_metadata.py);
- command executor: the standalone `subprocess.run` contract; one executor per process; "unsettled" errors escape best-effort handlers in `list_worktrees`, `refresh_mirror`, `_run_infer` and the overlay steps of the pass (test_command_executor.py);
- completions: a missing `infer` makes `available()` false and `run` raise; the `ip:model:thinking` descriptor (test_completion_routing.py);
- configuration: `recipes` is never serialised; the seed has only `providers` and `repos` (test_config_ownership.py);
- private database connection (test_database_connection_file.py);
- organizations, repository folders, locations and scope (test_organizations.py, test_repo_groups.py, test_repository_locations.py);
- the retired `wt` command returns 2 without connecting (test_worktree_cli.py).

No test exercises `run_pass` or `run_repo_pass` on their normal path, the git sequence of `refresh_mirror`, `repo_stale`, `newer_than`, `clustering`, `raptor`, or the commands `sync`, `embed`, `status`, `activity`, `drifts`, `derive`, `raptor`.

### Continuous integration

`README.md` (lines 30-32) says `.github/workflows/test-and-build.yml` runs the tests, enforces "the Arbol implementation boundary", builds the executables and smoke-tests their metadata. The repository contains no `.github` directory, and `git log --all -- .github` lists no commit. What CI enforced cannot be read from this repository.

<!-- sources:
mycel_deprecated_v1:pyproject.toml
mycel_deprecated_v1:Makefile
mycel_deprecated_v1:README.md
mycel_deprecated_v1:mycel.spec
mycel_deprecated_v1:better-grep.spec
mycel_deprecated_v1:mycel_entry.py
mycel_deprecated_v1:better_grep_entry.py
mycel_deprecated_v1:mycel/__main__.py
mycel_deprecated_v1:mycel/cli.py#main
mycel_deprecated_v1:mycel/better_grep.py#main
mycel_deprecated_v1:tests/test_cli_metadata.py#test_better_grep_version
-->

---

## Surprises and defects

Each item says what the code does and where. "Inferred" marks a consequence I derived; nothing here was observed at run time.

### Data-changing behaviour

1. **The remote refresh resets whatever is checked out.** `refresh_mirror` runs `git reset --hard FETCH_HEAD` in the configured code root after fetching the remote's default branch (syncpass.py:122-127). It never checks which branch is checked out. Inferred: when `code_root` points at a working checkout on another branch with a clean tree, that branch is moved to the remote default-branch tip and its unpushed commits leave the branch. The guard covers only uncommitted and untracked files.
2. **The dirty guard is skipped when `git status` fails.** The guard requires `returncode == 0 and stdout` (syncpass.py:116); a failing `git status` falls through to fetch and reset.
3. **The 600-second interval does not span invocations.** `_mirror_last` is process memory (syncpass.py:90). The comment "at most one git fetch per repo per interval" (syncpass.py:88-89) holds only inside one long-lived process. Inferred: because the first comparison is against `0` on the `time.monotonic()` clock, a fresh process skips the refresh while that clock reads below 600.
4. **Default branch names containing `/` are truncated.** `head.stdout.strip().rsplit("/", 1)[-1]` (syncpass.py:121) keeps only the last path component of `refs/remotes/origin/<branch>`.
5. **`mirror_warning` of one repository is erased by the next.** `status` holds one key; a later repository that refreshes cleanly, is throttled, or has no `origin` pops it (syncpass.py:256-261). The warning also selects the `error` column of the activity row, so that is lost too.
6. **`raptor build` deletes before it can fail.** `_clear` removes all summaries and their edges first (raptor.py:190), on an autocommit connection. Inferred: a later failure (missing prompt file, missing Voyage key, a non-completion exception) leaves the repository without summaries. A failure between `_insert_summary` and the embedding call (raptor.py:281-282) leaves a summary row with no embedding and no edges.
7. **A full pass creates folders under the artifact root.** `write_map` calls `os.makedirs(<artifact_root>/generated)` (code_map.py:94) even when the artifact root did not exist (syncpass.py:268-271 does not test for it).
8. **Read-looking commands write.** `status`, `activity`, `drifts`, `repos` all go through `_connect_with_config` (cli.py:84-93): they may create the configuration file, run the schema DDL, and apply the file to `kn_repos`. Every process also re-runs the DDL block once and several `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` statements (store.py:1063, 1093, 1096; syncpass.py:143).

### Commands that do not work as written

9. **`mycel raptor regen` and `mycel raptor build` raise `NameError`.** `subprocess` is used at cli.py:151 but is imported only inside other functions (cli.py:311, 340, 457). With an `infer` executable present, both actions end with `{"error": "name 'subprocess' is not defined"}` and exit 1.
10. **The `better-grep` console script passes its own name to grep.** `better_grep.main` calls `cli.main(["better-grep", *sys.argv[1:]])` (better_grep.py:101-104). In `cli.main` the check `os.path.basename(sys.argv[0]) == "better-grep"` comes first and calls `better_grep.run(raw)` with the list that still starts with `"better-grep"` (cli.py:720-722). Inferred: installed through the `pyproject.toml` script entry, the command searches for the literal pattern `better-grep`. The PyInstaller binary is unaffected because `better_grep_entry.py` calls `run` directly.
11. **The PyInstaller `better-grep` skips the common start-up.** `better_grep_entry.py` bypasses `cli.main`, so no `truststore` injection and no `_export_dsn` happen, although the comment at better_grep.py:102 says the console entry is routed "through Mycel's standard TLS/DSN setup".
12. **The semantic tail of `better-grep` ignores grep's mode.** It is written to stdout after grep regardless of `-q`, `-c`, `-l` or grep's exit code (better_grep.py:65-97). The install smoke test sets `BETTER_GREP_PLAIN=1` to avoid it (Makefile:17).
13. **An invalid private database reference crashes every command with a traceback.** `_export_dsn()` runs outside the `try` of `main` (cli.py:719, 878-884) and `config.database_dsn` only catches the malformed-file error (config.py:197-202). This includes `mycel --version` and `mycel better-grep`. The separate `better-grep` binary does not pass through `main`; there the same error is caught and printed as `(mycel tail unavailable: ...)` (better_grep.py:74-76).

### Counters and reporting that mean something else

14. **`stale` in the sync result is database-wide and summed per repository.** `detect()` processes every derivation of every repository and returns the global count (store.py:530, 566); the pass adds that number once per repository that has an artifact folder (syncpass.py:252).
15. **`docs_edited` and `docs_new` count chunks, not documents.** They read the chunk-status counters `edited` and `new` (syncpass.py:250-251; store.py:250, 307).
16. **The "only passes that did something" rule does not hold while anything is stale.** The activity row is written when any counter is non-zero or any item exists (syncpass.py:350); `stale` is non-zero whenever a stale chunk exists anywhere, and every stale chunk of the repository is appended as an item (store.py:677-687). The comment at syncpass.py:348-349 and the DDL comment at store.py:171-173 say no-op passes are not logged.
17. **`mycel activity --repo` hides sync, embed and pull rows.** Those rows are written with a null `repo` column (syncpass.py:351-355; embedder.py:209, 232; cli.py:518), and the filter is `repo=%s` (store.py:1161-1163).
18. **Pending counts disagree.** The pass counts overlay namespaces and disabled repositories (`split_part(repo,'@',1) = ANY(usable)`, with `usable` built without an enabled check, syncpass.py:338-347). `embed_pending` skips overlay namespaces and disabled repositories (embedder.py:168-169, 188-190). `status.embedder.pending` and `.embedded` are global, not per `--repo` (cli.py:178-179). The coalesced return uses a third formula (syncpass.py:170).
19. **`status.documents` includes orphaned rows.** The query counts every `kn_documents` row of the repository; the orphan count it also computes is not returned (store.py:1115-1116, 1125).
20. **A failed completion is reported as a cancellation.** Any `CompletionError` in a tier sets `cancelled=True` and discards the tier (raptor.py:271-276, 384-389). The error text is not returned, logged or stored.
21. **`freshness.refreshed` means "a pass ran".** It is `not coalesced`, independent of whether anything changed (retrieval.py:159-160).

### Scope of effects

22. **A repository pass is not repository-scoped in what it writes.** It runs the global `detect()`, which first clears every stale flag in the database and then sets the recomputed set (store.py:560-562). Inferred: two repository passes for different repositories, which the locks allow to run together, perform this clear-and-set concurrently in autocommit mode.
23. **Detection runs before code ingest in the same repository step.** Order is documents refresh with `detect`, then remote refresh, then code ingest (syncpass.py:246-267). Inferred: staleness caused by the code changes of this pass is found by the next `detect` call, which for the last repository of a pass is the next pass.
24. **`track_source` is not repository-scoped (seen while tracing the pass; outside my assigned files).** The lookup is `WHERE path=%s AND source_type=%s` without `repo`, and the insert names no `repo` (store.py:397-404). Inferred: two repositories with the same relative code path can overwrite each other's document hash during `store.refresh`.
25. **No code opens a Drift.** `store.open_drifts` (store.py:610-633) has no caller in the repository. `mycel drifts` and `status.open_drifts` only read `kn_drifts`. The only writer of `kn_drifts` on the paths read is `detect`, which closes drifts of heartwood and generated chunks (store.py:563-565).
26. **The staleness scan and the ingest use different skip lists.** `_SCAN_SKIP` (syncpass.py:361-362) lacks `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `venv`, `.svelte-kit`, `.turbo`, `site-packages`, `releases`, `.arbol`, `.arco`, `storybook-static`, which `_CODE_SKIP` has (store.py:788-790), and counts files of every extension. Inferred: tool caches and other non-indexed files make a repository stale and trigger a pass on the next search.
27. **Fresh-on-read does not embed.** `retrieval.search` runs the repository pass and searches at once (retrieval.py:157-169). Inferred: chunks added by that pass have no embedding until `mycel embed` or `mycel sync` runs.
28. **Remote refresh depends on the database flag, not on the resolved root.** The condition is `f.get("code_root")` (syncpass.py:254), so repositories located by organization membership or by the `~/repo` convention are never refreshed, and a repository whose root comes from `ARBOL_KN_CODE_ROOT` is refreshed at that root only when the flag is also set.

### Configuration

29. **Removing a key from the file does not clear it in the database.** `apply` passes `None` for absent keys and `set_repo_flags` ignores `None` (config.py:146-148; store.py:1086-1095). `RepositoryLocations.settings` then still sees the old database value (locations.py:42-44). Clearing requires an explicit empty list or empty string. The docstring calls the table a "synced cache" (config.py:9).
30. **A repository missing from `[repos]` is disabled.** Every enabled row not in the file is switched off on each apply (config.py:149-151). `enabled` defaults to `false` (config.py:144).
31. **`arbol` cannot have a whole-tree code corpus.** The DDL sets `code_subdirs` of row `arbol` to five fixed folders whenever it is null, in every process (store.py:142-143).
32. **A malformed configuration file changes the database silently.** `database.dsn()` treats a TOML error as an empty `[database]` table and falls back to `DEFAULT_DSN` (database.py:65-73). Other readers raise: `RepositoryLocations()` and `organizations.configured()` call `config.load()` (locations.py:20; organizations.py:12). Inferred: with a malformed file, `mycel search` fails in scope or organization resolution and `mycel sync` fails when it resolves the first repository's roots, while commands that resolve no location run against the default database. The docstring says a malformed file "keeps last-good state" (config.py:16-17).
33. **`enabled` is coerced with `bool()`.** A string value such as `"false"` enables the repository (config.py:144; store.py:1083). No key is type-checked.
34. **`dumps` loses information.** Unknown tables and unknown organization keys are dropped; `[providers]` and `[mirrors]` values are rewritten as strings; a repository name that is alphanumeric but not ASCII is written as a bare key (config.py:76-96).
35. **A DSN with a password is written into the file.** `dumps` writes `dsn = "..."` (config.py:74) while the header says "Secrets do NOT belong here" (config.py:31). `DEFAULT_DSN` itself carries the credentials `arbol:arbol` (database.py:17).
36. **The resolved DSN is exported to child processes.** `_export_dsn` places it in `os.environ["ARBOL_PG_DSN"]` (cli.py:80-81); git, grep and `infer` children inherit the environment, including a DSN read from a private connection file.
37. **One ambiguous organization member breaks scope resolution for everything.** `scope_bindings` computes the code root of every known name (locations.py:34-36); a name present in two organizations without an explicit `code_root` raises `ValueError` (locations.py:56-57). Inferred: every `mycel search` without `--repo` then fails.
38. **Configuration is re-read many times per command.** `syncpass.code_root` and `syncpass.artifact_root` build a new `RepositoryLocations` (file parse plus a directory listing per organization) on each call (locations.py:84-89), which happens per repository in a pass and per result in a search (retrieval.py:91-98). The class docstring describes a reusable snapshot (locations.py:17).

### RAPTOR

39. **Summaries are always embedded with the Voyage API.** `build_tree` and `regen_stale` call `embedder.embed`, the Voyage client, without looking at the repository's profile (raptor.py:282, 395; embedder.py:50-69). Inferred: for a `local`-profile repository the summary text leaves the machine, its vector lives in a different model's space than the repository's other vectors, and upper tiers cluster vectors from two models. The comment at embedder.py:156-158 calls the profile "the interlock".
40. **`max_tokens` is not forwarded.** `raptor.py` passes `"max_tokens": 1024`; `_run_infer` never reads it (completion_client.py:41-48).
41. **The system prompt travels as a command-line argument.** `--system <text>` (completion_client.py:47-48).
42. **Large clusters are summarised from a prefix.** At 1200 characters per member and a 48000-character cap, at most 40 full-size members reach the prompt (raptor.py:37-38, 96-100); every member still gets a generation edge (raptor.py:285-286). The leaf query has no `ORDER BY` (raptor.py:196-199), so which members are cut is not fixed by the code.
43. **The comment about rate limiting names a mechanism that is not here.** raptor.py:42-43 refers to "completion's 429 backoff"; `completion_client` has no retry or backoff.
44. **No early exit when a tier produces no summary.** If every cluster is a singleton, the node list is unchanged and the loop repeats the same clustering until tier 5 (raptor.py:207-291) (inferred).
45. **A summary whose members were deleted is skipped by `regen` and stays stale.** raptor.py:355-356.
46. **Orphaned members do not make a summary stale (inferred, from `store.py`).** `detect` compares hashes of rows that still exist; document ingest marks removed chunks `orphaned` without changing their hash (store.py:332, 550-553).
47. **Prompt files live outside the source tree.** The default folder is `~/Artifacts/mycel/system-instructions` (raptor.py:48), inside the artifact corpus of the repository named `mycel`.
48. **One database connection per summary job is opened for a label the command line discards.** `_worker_connection` and `_node_label` feed `on_live`, which `mycel raptor` sets to a no-op (raptor.py:235-237; cli.py:163).

### Dead or unreachable code, and stale text

49. **Deadline handling is unreachable.** No caller passes `deadline` (section 3).
50. **Host seams without a host.** `command_executor.install_executor`, `embedder.request_stop`, `store.ACTOR = "daemon"`, and the `on_live` / `on_stage` / `cancel` hooks have no caller or setter in the repository. Docstrings refer to `mycel_client.server`, a watcher, a scheduler, launchd and "Seqoya Lab" (syncpass.py:1-11; config.py:5-7; store.py:1131-1134).
51. **Retired model still executed.** The pass discovers, re-diffs and drops Branch Overlays under the fixed path `~/repo/<name>` (syncpass.py:278-334) although the `wt` command is retired; `list_worktrees` and worktree fields remain in `mycel repos` (cli.py:297-298).
52. **`repo_stale` selects columns it does not use.** `code_subdirs` and `code_root` are fetched and then replaced by a second full flag query (syncpass.py:406-413).
53. **`mycel repos` looks flags up by folder name.** `flags.get(name)` uses the directory name unchanged (cli.py:286). Inferred: a checkout folder named `Arbol` shows `mycel_enabled: false` because its row is keyed `arbol`.
54. **`--overlay` help is wrong when `--repo` is given.** The help says the default is "the CWD's worktree branch" (cli.py:743-744); with `--repo` the overlay is `None` and the current directory is not consulted (cli.py:30-34).
55. **`--only docs` differs from unified search in more than the result type.** It skips freshness, skips validation of `query` and `k`, and searches only the named repository, not the shared `mycel` documents (cli.py:52-56; embedder.py:265-308).
56. **`sync --no-embed` help says "the delta".** Without the flag the command embeds every pending chunk of every base repository (cli.py:104-106, 752).
57. **`README.md` names a CI workflow that is not in the repository** (section 10) and lists three `infer` lookup locations where the code has four (README.md:25; completion_client.py:23-34).
58. **The version is declared twice** (`pyproject.toml:7`, `mycel/__init__.py:3`).
59. **`.venv/pyvenv.cfg` records a creation path of `.../sylvan-stack/mycel/.venv`**, the directory name before the repository was renamed; this is an environment artefact, not source.

<!-- sources:
mycel_deprecated_v1:mycel/syncpass.py#refresh_mirror
mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked
mycel_deprecated_v1:mycel/syncpass.py#newer_than
mycel_deprecated_v1:mycel/syncpass.py#repo_stale
mycel_deprecated_v1:mycel/cli.py#main
mycel_deprecated_v1:mycel/cli.py#_cmd_raptor
mycel_deprecated_v1:mycel/cli.py#_cmd_repos
mycel_deprecated_v1:mycel/cli.py#_export_dsn
mycel_deprecated_v1:mycel/cli.py#_connect_with_config
mycel_deprecated_v1:mycel/cli.py#search_payload
mycel_deprecated_v1:mycel/better_grep.py#main
mycel_deprecated_v1:mycel/better_grep.py#run
mycel_deprecated_v1:better_grep_entry.py
mycel_deprecated_v1:mycel/config.py#apply
mycel_deprecated_v1:mycel/config.py#dumps
mycel_deprecated_v1:mycel/config.py#database_dsn
mycel_deprecated_v1:mycel/database.py#dsn
mycel_deprecated_v1:mycel/locations.py#RepositoryLocations.scope_bindings
mycel_deprecated_v1:mycel/locations.py#RepositoryLocations.settings
mycel_deprecated_v1:mycel/knowledge/raptor.py#build_tree
mycel_deprecated_v1:mycel/knowledge/raptor.py#regen_stale
mycel_deprecated_v1:mycel/knowledge/raptor.py#_prompt_sections
mycel_deprecated_v1:mycel/completion_client.py#_run_infer
mycel_deprecated_v1:mycel/knowledge/code_map.py#write_map
mycel_deprecated_v1:mycel/knowledge/store.py#detect
mycel_deprecated_v1:mycel/knowledge/store.py#refresh
mycel_deprecated_v1:mycel/knowledge/store.py#track_source
mycel_deprecated_v1:mycel/knowledge/store.py#open_drifts
mycel_deprecated_v1:mycel/knowledge/store.py#set_repo_flags
mycel_deprecated_v1:mycel/knowledge/store.py#status
mycel_deprecated_v1:mycel/knowledge/store.py#list_activity
mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema
mycel_deprecated_v1:mycel/knowledge/embedder.py#embed
mycel_deprecated_v1:mycel/knowledge/embedder.py#embed_pending
mycel_deprecated_v1:mycel/retrieval.py#search
mycel_deprecated_v1:README.md
-->

---

## Not established

1. What `infer resolve --recipe <name>` returns beyond the fields the code reads (`ok`, `error`, `ip`, `model`, `thinking`), which recipes exist, and whether `infer complete` retries or backs off. `infer` is outside this repository.
2. The content of `raptor-summary.md` and `raptor-request.md.tmpl`. They are outside the source repository; I did not treat `~/Artifacts/` as evidence.
3. What continuous integration enforced, including the "Arbol implementation boundary" check. The workflow file is absent.
4. Whether `dist/mycel` and `dist/better-grep` (built 23 September) match the source at `b3125d0`, and therefore whether the installed binaries show items 9 and 10.
5. Run-time confirmation of every item marked "inferred". In particular: the `NameError` in `raptor`, the console-script dispatch of `better-grep`, the effect of `git reset --hard FETCH_HEAD` on a non-default branch, and the `time.monotonic()` start value.
6. Which rows exist in `kn_repos` on any machine, and whether any has `code_root` set, which decides whether the remote refresh ever runs.
7. The order in which a pass processes repositories (the flag query has no `ORDER BY`).
8. Who was meant to call `store.open_drifts`, `install_executor` and `request_stop`, and how a host used the `status` dict across passes.
9. Which keys the retired modules read from `[mirrors]`; those modules were not inventoried.
10. Whether advisory lock keys collide between isolated schemas of one database (`MYCEL_PG_SCHEMA`); advisory locks are not schema-scoped in PostgreSQL, but no code here addresses it.
11. The PostgreSQL extensions actually required at run time. The code creates `vector` in schema `public` and tries a ParadeDB `bm25` index; required versions and privileges are not stated anywhere in the files read.
12. How chunk boundaries, embedding batches and ranking work in detail. `store.py`, `embedder.py`, `chunker.py` and `code_chunker.py` were read only where the commands in this inventory call them.
13. Whether `psycopg` accepts the multi-statement `DDL` string in one `execute` under all configurations; the code relies on it (store.py:201).

<!-- sources:
mycel_deprecated_v1:mycel/cli.py#_cmd_raptor
mycel_deprecated_v1:mycel/completion_client.py#_run_infer
mycel_deprecated_v1:mycel/knowledge/raptor.py#_instruction
mycel_deprecated_v1:mycel/knowledge/store.py#open_drifts
mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema
mycel_deprecated_v1:mycel/knowledge/store.py#list_repo_flags
mycel_deprecated_v1:mycel/command_executor.py#install_executor
mycel_deprecated_v1:mycel/database.py#connect
mycel_deprecated_v1:README.md
-->
