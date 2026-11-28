# Mycel language and startup packaging evidence, 7 October 2026

The current v1 Python CLI reaches top-level help in a median of **79.9 ms** without a frozen bundle, compared with **3628.2 ms** for the installed frozen executable. Seconds-long startup is therefore avoidable while keeping Python. This does not establish a TypeScript application speed advantage, an exact extraction-only cost, or the best language for Mycel 2.

## Results

All values are elapsed wall-clock milliseconds, measured by the parent around subprocess creation through child completion. Each measured series follows two warmups. No filesystem or OS cache purge was performed.

| Command | n | Median ms | p95 ms | Range ms |
|---|---:|---:|---:|---:|
| Installed PyInstaller v1 --help | 20 | 3628.2 | 3734.2 | 3428.6–3825.9 |
| Current v1 checkout, unbundled --help | 20 | 79.9 | 87.2 | 75.4–101.6 |
| Python interpreter only | 20 | 17.6 | 18.3 | 16.6–19.9 |
| Node interpreter only | 20 | 19.1 | 22.6 | 17.9–22.7 |

The observed packaged/unbundled median ratio is 45.4×. Because the revisions differ, this is a comparison of the installed distributions, not a controlled attribution of every millisecond to PyInstaller.

Python: `Python 3.12.14`. Node: `v24.21.0`. Both Mycel variants report `mycel 0.1.0`. Host: `macOS-27.0.1-arm64-arm-64bit`, architecture `arm64`. Source repository HEAD: `c3bde9d2bfce17253f122fe01e9038f9a09fadd7`. The installed binary's SHA-256 matches the deprecated repository's `dist/mycel`: `True`.

## Commands and safety inspection

- Frozen executable: `/Users/example/bin/mycel --help`.
- Unbundled entry point: `/Users/example/repos/sylvan-stack/mycel_deprecated_v1/.venv/bin/python3.12 -B /Users/example/repos/sylvan-stack/mycel_deprecated_v1/.venv/bin/mycel --help`, with `PYTHONPATH=/Users/example/repos/sylvan-stack/mycel_deprecated_v1`.
- Interpreter baselines: that Python with `-B -c pass`, and `/Users/example/.nvm/versions/node/v24.21.0/bin/node -e ''`.

The old entry-point shebang and editable-package mapping still point to the pre-rename `.../mycel` directory. Explicitly selecting the preserved interpreter and source path avoids both broken references. Verified imported package: `/Users/example/repos/sylvan-stack/mycel_deprecated_v1/mycel/__init__.py`.

`cli.main` injects system SSL trust and calls `_export_dsn()` before parsing arguments. Therefore every subprocess uses a sanitized environment and `MYCEL_CONFIG=/tmp/mycel-language-startup/nonexistent-config.toml`. This path was checked not to exist; the owner configuration and private database references were never read. No Mycel/Arbol credentials or DB environment settings are inherited. Help exits within argparse before command handlers. Python bytecode writes are disabled; bundled runtime extraction uses the task's temporary directory. No database operation, query, sync, embedding, checkout mutation, or network request was invoked. All measured commands returned 0 without stderr.

The frozen `mycel.cli` and `mycel.config` bytecode were inspected without execution. The installed executable was built on 23 September, while the deprecated checkout has later changes. In particular, the frozen config's `database_dsn` reads the config's plain `dsn`; the current version also imports the PostgreSQL module to resolve a possible private connection reference. Both honor the nonexistent `MYCEL_CONFIG` override. This difference prevents treating the two builds as identical merely because they report version 0.1.0.

## Method and limits

There are 20 measurement rounds. Each round randomizes the order of the packaged/unbundled pair, then randomizes the two interpreter baselines. The reproducible random seed is 20261007. Each target receives two randomized warmups. stdout is discarded; stderr is captured solely to check for errors. Timing uses `time.perf_counter_ns`; p95 is nearest rank, `sorted[ceil(0.95*n)-1]`.

These are warm/cache-uncontrolled process-startup measurements, not cold-cache results. They include spawn, scheduling, imports, help generation, pipe handling and teardown. They do not benchmark corpus parsing, chunk reconciliation, PostgreSQL, a remote provider, or any implemented TypeScript application. Interpreter-only startup is not a proxy for application throughput. Running load and differing source revisions remain limitations.

## Packaging evidence

- `/Users/example/repos/sylvan-stack/mycel_deprecated_v1/mycel.spec:3` calls the distribution a PyInstaller onefile build; lines 16–21 pass Python code, scripts, binaries and data into one EXE. The installed binary is 80,754,144 bytes, but that size by itself is not a language-selection argument.
- `/Users/example/repos/sylvan-stack/mycel_deprecated_v1/pyproject.toml:8` requires Python >=3.12; line 9 lists psycopg, NumPy, scikit-learn, tree-sitter and other dependencies; line 18 already exposes an ordinary Python console entry point. The package can run unbundled today.
- `/Users/example/Artifacts/arbol/driver-contract/00-overview-and-boundary.md:208` gives the Drivers' documented language rationale: generated Codex TypeScript bindings, existing npm repositories, and recurring Python-service bundling failures. Codex bindings are a Driver-specific benefit, not evidence about Mycel ingest.
- `/Users/example/Artifacts/arbol/builds/00-builds-and-versions.md:16` leaves compilation to each component; line 124 specifies a Node24 launcher using process.execve. That launcher can start an executable written in another language.

## Language-independent v1 issues

These are documented source/inventory findings, not production profiles establishing the dominant bottleneck:

- `/Users/example/Artifacts/mycel/research/v1-inventory-embedding-and-retrieval.md:312` shows the document vector arm performs exact-distance scans through a materialized CTE, rather than the code arm's index-friendly ORDER BY shape. The stated reason at line 322 is filtered HNSW under-returning. Changing client language would preserve the SQL workload.
- The same inventory at line 438 issues one bridge query per selected document section, and line 513 one `documented_in` query per result. Batching/query design addresses these round trips.
- `/Users/example/Artifacts/mycel/research/v1-inventory-ingest-and-graph.md:531` describes global staleness detection: load all edges, query each parent's hash, clear global marks, then update per stale chunk (lines 533–539). Repository scoping and database batching address this work.
- `/Users/example/Artifacts/mycel/research/v1-inventory-sync-settings-commands.md:244` walks directory and file mtimes; line 254 says search supplies no deadline. Scan design addresses this cost.
- Ingest/graph inventory line 646 documents a stub-tested correctness defect in which `refresh` updates a code hash before `ingest_code`, hiding the edit. Lines 654–658 cover greedy identity matching, duplicate keys and non-atomic ingest. These require algorithm and transaction changes in either language.

## Reproducible artifacts

- `benchmark.py`: complete benchmark runner.
- `results.json`: metadata, source/binary hashes, sanitized commands, statistics and every measured/warmup record.
- `archive-inspection.json`: names/constants read from frozen CLI/config bytecode.
- `archive-main-disassembly.txt`: frozen pre-dispatch code disassembly.
