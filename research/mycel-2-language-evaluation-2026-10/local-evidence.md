---
role: authored
---
# Local evidence snapshot

Captured on 7 October 2026. Each excerpt has 3–15 source lines. Arbol documents are read as architectural evidence, not prescribed instructions or code dependencies.

Deprecated source HEAD: c3bde9d2bfce17253f122fe01e9038f9a09fadd7


## The new Mycel scaffold


Source: [README.md:1–11](/Users/example/repos/sylvan-stack/mycel/README.md:1); SHA-256 `58da3c89e7546f60fd66dff0fc41202fec806d8b891fe8e46ed7fa7affa199a0`.

```text
1: # Mycel
2: 
3: Mycel 2: the rewrite of Mycel, the knowledge engine of the Sylvan Stack.
4: 
5: This repository is an empty scaffold created on 2026-10-05. No implementation exists yet.
6: 
7: | | |
8: |---|---|
9: | Package | `@sylvan-stack/mycel` 2.0.0 |
10: | Artifact corpus | `~/Artifacts/mycel` (GitHub `sylvan-stack/mycel-artifacts`) |
11: | Predecessor | `sylvan-stack/mycel_deprecated_v1`, frozen. This repository starts at 2.0.0 because version 1 is that deprecated code base |
```

<!-- sources:
mycel:README.md
-->


Source: [package.json:1–10](/Users/example/repos/sylvan-stack/mycel/package.json:1); SHA-256 `28b3b9948afcbf3e194b864c9e9015e3bc7b7050d71f1f93c4a9853315390899`.

```text
1: {
2:   "name": "@sylvan-stack/mycel",
3:   "version": "2.0.0",
4:   "private": true,
5:   "description": "Mycel 2: the rewrite of Mycel, the knowledge engine of the Sylvan Stack.",
6:   "repository": {
7:     "type": "git",
8:     "url": "git+https://github.com/sylvan-stack/mycel.git"
9:   }
10: }
```

<!-- sources:
mycel:package.json
-->


## The process boundary


Source: [00-overview-and-legacy-map.md:69–76](/Users/example/Artifacts/mycel/specs/00-overview-and-legacy-map.md:69); SHA-256 `96c9dca9da1e42d080a227cd34a51771b51bf9dd514f017294853fd2571156b2`.

```text
69: Proposed.
70: 
71: - **Form.** Mycel is one command-line program, `mycel`. Its command line is its only interface: a caller starts the program and reads the result from standard output. There is no library to load, so no other program contains Mycel's code ([MYC-D1](#decisions)). Version 1 was also a library, which Arbol 1's resident service loaded.
72: - **No resident service.** Mycel is not a daemon and has no socket, launch agent or watcher. Every invocation is one process that does one thing and ends. This was the strict rule of version 1 and is kept.
73: - **Builds.** Mycel is built into numbered Builds that are kept side by side ([BLD-0](../../arbol/builds/00-builds-and-versions.md), which names `mycel` among the components). The name on the search path is a launcher: without a build number it starts the newest working Build.
74: - **State.** Mycel keeps the index store ([MYC-D2](#decisions)) and nothing else. Its settings are a file the owner writes ([MYC-D3](#decisions)). The store carries the format number of BLD-0, so that a Build that meets a newer format refuses to run.
75: - **Independence.** Mycel uses no code and no instructions of Arbol, and nothing in Mycel is named for another product. It may read the files and data of any product as data.
76: - **Network.** The only service Mycel calls is the embedding provider (MYC-3). It runs no git command that changes anything.
```

<!-- sources:
mycel:specs/00-overview-and-legacy-map.md#Form and hosting
-->


## The proposed language


Source: [00-overview-and-legacy-map.md:234–241](/Users/example/Artifacts/mycel/specs/00-overview-and-legacy-map.md:234); SHA-256 `96c9dca9da1e42d080a227cd34a51771b51bf9dd514f017294853fd2571156b2`.

```text
234: ## Decisions
235: 
236: | ID | Question | Proposed default | Outcome |
237: |---|---|---|---|
238: | MYC-D1 | In what form does Mycel exist, and in which language? | One command-line program and nothing else, in TypeScript on Node.js 24, as the Drivers (DRV-D1, DRV-D2). The repository is an npm package already. Version 1's Python programs of 80 MB each took their whole runtime along | Open |
239: | MYC-D2 | Where does the index live? | In PostgreSQL with ParadeDB, which gives vectors and BM25 in one store as in version 1, but in a database of Mycel's own, at an address the settings name. Version 1 shared a database with Arbol 1, which made its rows hard to tell apart, to back up and to remove | Open |
240: | MYC-D3 | Where are the settings kept? | In `~/.mycel/config.toml`, as in version 1, so that the owner's file stays valid. Mycel is not a component of Arbol and does not use `~/.arbol`. It reads the file and never writes it | Open |
241: | MYC-D4 | Which further functions of version 1 follow the first version, and in what order? | The grep replacement with a search tail first, because the research guides start from it; then reading one symbol's source; then the generated overview of a repository's code; then the feed of passes; summaries of clusters last, since they need a model and version 1's never ran as written. Each gets a specification of its own | Open |
```

<!-- sources:
mycel:specs/00-overview-and-legacy-map.md#Decisions
-->


## Driver rationale as context


Source: [00-overview-and-boundary.md:204–209](/Users/example/Artifacts/arbol/driver-contract/00-overview-and-boundary.md:204); SHA-256 `1a0116df818a2cfd3ab0acfbf25ed92c16ee68c9f701b1bec5c73411af70141e`.

```text
204: ## Decisions
205: 
206: | ID | Question | Proposed default | Outcome |
207: |---|---|---|---|
208: | DRV-D1 | Implementation language | TypeScript on Node.js 24. Codex publishes TypeScript bindings and a JSON Schema for its app-server protocol (`codex app-server generate-ts`), the repositories are npm packages already, and version 1's bundling of Python services was a recurring source of failures | Decided 5 October 2026, delegated by the owner |
209: | DRV-D2 | In what form does a Driver exist, and where does it run? | Each Driver is one command-line program and nothing else. Arbol holds none of its code and starts it once per operation. A run is one process and lasts only as long as the process that started it stays, so the product guarantee that work in progress survives closed windows and a restart of the coordinator is met by starting runs from an execution process separate from both. The contract has no command for finding and rejoining a run after that process itself restarts | Decided 6 October 2026 by the owner. It replaces the decision of the day before for a library (SYL-8) |
```

<!-- sources:
arbol:driver-contract/00-overview-and-boundary.md#Decisions
-->


## Compilation and launcher boundaries


Source: [00-builds-and-versions.md:12–16](/Users/example/Artifacts/arbol/builds/00-builds-and-versions.md:12); SHA-256 `b250b65257451e2eb39f2ca6adc8f0f38881eef3a8d39040fcacd2c3c245dcb2`.

```text
12: ## Scope
13: 
14: Covered: components and Builds, build numbers and package versions, the registry and its records, when a Build counts as working, the default Build, running a named Build, building, withdrawing and pruning, data shared by several Builds.
15: 
16: Not covered: how each component is compiled, which belongs to its repository; replacing an application or a coordinator while it runs, which belongs to that component; the version of the Driver Contract, which numbers an interface and not a Build ([DRV-0](../driver-contract/00-overview-and-boundary.md#the-command-line)).
```

<!-- sources:
arbol:builds/00-builds-and-versions.md#Scope
-->


Source: [00-builds-and-versions.md:120–124](/Users/example/Artifacts/arbol/builds/00-builds-and-versions.md:120); SHA-256 `b250b65257451e2eb39f2ca6adc8f0f38881eef3a8d39040fcacd2c3c245dcb2`.

```text
120: ### Where the build tool and the launchers are
121: 
122: `arbol-builds` belongs to the `arbol` repository and is installed from there by that repository's install script. It is not itself a Build: there is one of it, and it is replaced when it is installed again.
123: 
124: A launcher is a small Node.js program without dependencies. `arbol-builds` writes one per component, when the component is first built, into the folder `~/.local/bin`, or into the folder named with `--bin-dir`. The folder has to be on the owner's search path. The repository install command is `npm run install:builds -- --bin-dir <folder>`; it compiles the tool and installs a standalone copy without runtime npm dependencies. On macOS and other POSIX systems the launcher uses Node.js 24's `process.execve` to replace itself with the Build's executable, preserving its process identity, arguments, environment, working folder and open standard streams.
```

<!-- sources:
arbol:builds/00-builds-and-versions.md#Where the build tool and the launchers are
-->


## Database search work


Source: [embedder.py:473–482](/Users/example/repos/sylvan-stack/mycel_deprecated_v1/mycel/knowledge/embedder.py:473); SHA-256 `5c26e2a7cb815f5cdd377c600c9313d62255baca4e6120d836775b12134b716a`.

```text
473:     phase_started = _mark("query_embedding_ms", phase_started)
474:     code_rows = []
475:     if qv is not None:
476:         code_rows = conn.execute(
477:             f"SELECT c.id, c.repo, c.symbol_kind, 1-(c.embedding <=> %s::public.vector) AS cos "
478:             f"FROM kn_chunks c WHERE c.origin='code' AND c.state='present' AND c.embedding IS NOT NULL "
479:             f"AND {_SCOPE} ORDER BY c.embedding <=> %s::public.vector LIMIT %s",
480:             (qv, repos, repo, repo, shadowed, qv, pool)).fetchall()
481:         dense_ids = [r["id"] for r in code_rows]
482:     phase_started = _mark("dense_sql_ms", phase_started)
```

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`


Source: [embedder.py:484–496](/Users/example/repos/sylvan-stack/mycel_deprecated_v1/mycel/knowledge/embedder.py:484); SHA-256 `5c26e2a7cb815f5cdd377c600c9313d62255baca4e6120d836775b12134b716a`.

```text
484:     bm25_ids: list[str] = []
485:     try:
486:         bm25_ids = [r["id"] for r in conn.execute(
487:             f"SELECT c.id FROM kn_chunks c WHERE c.id @@@ paradedb.match('raw_text', %s) "
488:             f"AND c.origin = ANY(%s) AND c.state='present' AND "
489:             f"((c.origin='code' AND {_SCOPE}) OR "
490:             f" (c.origin <> 'code' AND c.repo = ANY(%s))) "
491:             f"ORDER BY paradedb.score(c.id) DESC LIMIT %s",
492:             (query, list(_bm25_origins), repos, repo, repo, shadowed,
493:              doc_repos, pool)).fetchall()]
494:     except Exception:  # noqa: BLE001 — parser hiccup / no pg_search → dense carries it
495:         bm25_ids = []
496:     phase_started = _mark("bm25_sql_ms", phase_started)
```

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`


## Python parsing


Source: [code_chunker.py:72–86](/Users/example/repos/sylvan-stack/mycel_deprecated_v1/mycel/knowledge/code_chunker.py:72); SHA-256 `daa0a59a1df4d99c96bec7b959a2dda7b5e8e01de6aba05feb8c778e878d2d74`.

```text
72: def chunk_python(rel_path: str, source: str) -> list[dict]:
73:     try:
74:         tree = ast.parse(source)
75:     except SyntaxError:
76:         return _whole_file(source)
77:     lines = source.split("\n")
78:     covered = [False] * (len(lines) + 2)
79: 
80:     def mark(s: int, e: int) -> None:
81:         for k in range(s, min(e, len(lines)) + 1):
82:             covered[k] = True
83: 
84:     chunks: list[dict] = []
85:     for node in tree.body:
86:         if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
```

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_python`


Source: [code_chunker.py:149–158](/Users/example/repos/sylvan-stack/mycel_deprecated_v1/mycel/knowledge/code_chunker.py:149); SHA-256 `daa0a59a1df4d99c96bec7b959a2dda7b5e8e01de6aba05feb8c778e878d2d74`.

```text
149:     if key not in _ts_parsers:
150:         from tree_sitter import Language, Parser
151:         if key == "js":
152:             import tree_sitter_javascript as g
153:             lang = Language(g.language())
154:         else:
155:             import tree_sitter_typescript as g
156:             lang = Language(g.language_tsx() if key == "tsx" else g.language_typescript())
157:         _ts_parsers[key] = Parser(lang)
158:     return _ts_parsers[key]
```

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#_ts_parser`


## Text semantics


Source: [chunker.py:118–128](/Users/example/repos/sylvan-stack/mycel_deprecated_v1/mycel/knowledge/chunker.py:118); SHA-256 `6b6792a25f80b77803d90359f17488ecb69b787b5a98c6023cc53cd0f67256d7`.

```text
118: def norm(text: str) -> str:
119:     """v1 canonical-ish normalization: NFKC + collapse whitespace."""
120:     return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip()
121: 
122: 
123: def sha(text: str) -> str:
124:     return hashlib.sha256(text.encode("utf-8")).hexdigest()
125: 
126: 
127: def content_hash(text: str) -> str:
128:     return sha(norm(text))
```

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/chunker.py#norm`


Source: [embedder.py:498–508](/Users/example/repos/sylvan-stack/mycel_deprecated_v1/mycel/knowledge/embedder.py:498); SHA-256 `5c26e2a7cb815f5cdd377c600c9313d62255baca4e6120d836775b12134b716a`.

```text
498:     dr = {cid: i for i, cid in enumerate(dense_ids)}
499:     br = {cid: i for i, cid in enumerate(bm25_ids)}
500:     nl_query = not re.match(r"^[\w.#/-]+$", query.strip())
501:     scores: dict = {}
502:     via: dict = {}
503: 
504:     test_ids: set = set()
505:     gen_ids: set = set()
506:     cand = list({*dense_ids, *bm25_ids})
507:     if cand:
508:         want_tests = re.search(r"\b(tests?|specs?|e2e|mocks?|fixtures?)\b", query, re.I)
```

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`


## Future numerical work


Source: [clustering.py:8–20](/Users/example/repos/sylvan-stack/mycel_deprecated_v1/mycel/knowledge/clustering.py:8); SHA-256 `2a4499591881cf1459f28b7cb70fee52085406b8c11c60edb55d99ffb3014ee5`.

```text
8: from __future__ import annotations
9: 
10: import numpy as np
11: from sklearn.decomposition import PCA
12: from sklearn.mixture import GaussianMixture
13: 
14: # Tuned on the real corpus (raptor.md §7 open items). Spherical covariance in a
15: # low PCA space: `full` covariance makes BIC underfit badly (3–5 giant, incoherent
16: # clusters); spherical at ~10 dims yields fine, coherent clusters.
17: _MAX_COMPONENTS = 150  # BIC picks ≤ this; high cap so BIC isn't the bottleneck
18: _PCA_DIMS = 10         # reduce 1024-d embeddings before GMM
19: _COVARIANCE = "spherical"
20: _PROB_THRESHOLD = 0.10 # soft membership: join every cluster with prob ≥ this
```

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/clustering.py#cluster`


Source: [clustering.py:40–54](/Users/example/repos/sylvan-stack/mycel_deprecated_v1/mycel/knowledge/clustering.py:40); SHA-256 `2a4499591881cf1459f28b7cb70fee52085406b8c11c60edb55d99ffb3014ee5`.

```text
40:     X = np.asarray(vectors, dtype=np.float64)
41: 
42:     # Light PCA reduction (GMM is unstable in high dimensions).
43:     dims = min(pca_dims, X.shape[1], n - 1)
44:     if X.shape[1] > dims:
45:         X = PCA(n_components=dims, random_state=random_state).fit_transform(X)
46: 
47:     # Pick component count by BIC (lowest wins), but never more than ~n/branching
48:     # so every tier reduces (see _TARGET_BRANCHING).
49:     branch_cap = (n + target_branching - 1) // target_branching
50:     max_k = max(1, min(max_components, n - 1, branch_cap))
51:     best_gmm, best_bic = None, np.inf
52:     for k in range(1, max_k + 1):
53:         if progress:
54:             progress(k, max_k)
```

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/clustering.py#cluster`


## Correctness and test requirements


Source: [database.py:74–83](/Users/example/repos/sylvan-stack/mycel_deprecated_v1/mycel/database.py:74); SHA-256 `43a02a96c39bad2808be9aacc2a32fe377aa397c5a6f01b51847d154b727f338`.

```text
74: 
75: 
76: def connect(conn_dsn: str | None = None) -> psycopg.Connection:
77:     conn = psycopg.connect(conn_dsn or dsn(), autocommit=True, row_factory=dict_row)
78:     # Compatibility for isolated databases supplied as data by an Arbol test host.
79:     schema = os.environ.get("MYCEL_PG_SCHEMA") or os.environ.get("ARBOL_PG_SCHEMA")
80:     if schema:
81:         if not schema.replace("_", "").isalnum():
82:             raise ValueError(f"invalid PostgreSQL schema name: {schema!r}")
83:         conn.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
```

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/database.py#connect`


Source: [01-corpora-and-ingest.md:144–152](/Users/example/Artifacts/mycel/specs/01-corpora-and-ingest.md:144); SHA-256 `bc84c278e36babf4ec6528271c8fa22e569ccb37b96b136b5ec7eb81601f6d72`.

```text
144: Observed in version 1: one routine brought the store up to date. For each enabled repository it ingested the documents, compared the stored hashes of the repository's code files with the files on disk, marked stale chunks, optionally reset the checkout to its remote, ingested the code, and wrote a generated overview. `mycel sync` ran it for all repositories at once and then embedded everything pending; a search ran it for one repository, without the reset and without the overview.
145: 
146: - **It could miss an edit to a code file.** The comparison of code files stored the new hash of each. The code ingest that followed skipped every file whose stored hash matched, which by then was every file. Read from the source and reproduced with a stand-in for the store, not on a real index. An edit was picked up only when the file changed between the two steps, which is where the reset to the remote sat.
147: - **It changed checkouts.** For a repository with a configured code folder that had a remote and no uncommitted or untracked files, it fetched the remote's default branch and ran `git reset --hard` to it, whatever branch was checked out. Observed on 7 October 2026: the history of one working checkout held 61 such resets from two days.
148: - **It was not atomic.** A file's new hash was stored before its chunks, each statement on its own. A failure in between left a file that the next pass skipped as unchanged, with its chunks half reconciled.
149: - **A pass for one repository wrote to all.** Marking stale chunks cleared and rewrote the marks of every repository.
150: - **Two passes could not run together,** which was right, and a pass that found another one running did nothing and said so.
151: 
152: Proposed: a pass covers the repositories it names. For each it scans, splits, reconciles identity, and then updates edges and staleness for that repository ([MYC-2](02-provenance-and-freshness.md)). Each file is applied in one transaction. A pass never runs a command that changes a checkout, and it reads the files as they are on disk ([MYC-D9](#decisions)). It embeds only when asked ([MYC-3](03-embedding.md)).
```

<!-- sources:
mycel:specs/01-corpora-and-ingest.md#The pass
-->


Source: [00-overview-and-legacy-map.md:133–137](/Users/example/Artifacts/mycel/specs/00-overview-and-legacy-map.md:133); SHA-256 `96c9dca9da1e42d080a227cd34a51771b51bf9dd514f017294853fd2571156b2`.

```text
133: | MYC-0.8 | change the structure of the index store only in `mycel init`, and refuse every other command with `store_format` when the store's format is not the one its Build knows | Changed | store |
134: | MYC-0.9 | be built into numbered Builds as BLD-0 says and report the build number of the Build that runs in `info` | New | unit |
135: | MYC-0.10 | call no service except the embedding provider, and run no git command that changes a repository | Changed | unit |
136: | MYC-0.11 | have an automated check for every requirement of MYC-1 to MYC-4 before that requirement counts as implemented, the store-backed ones against a store made for the test and discarded after it | New | store |
137: | MYC-0.12 | keep the guides of this corpus true to the program: a change to a command, an option or a reply changes the guide that describes it in the same change | New | unit |
```

<!-- sources:
mycel:specs/00-overview-and-legacy-map.md#Requirements
-->
