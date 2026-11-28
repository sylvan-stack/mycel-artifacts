---
role: derived
sources:
  - mycel:specs/00-overview-and-legacy-map.md
  - mycel:specs/01-corpora-and-ingest.md
  - mycel:specs/04-retrieval.md
---
# Python or TypeScript for Mycel 2

Research date: 7 October 2026. Bindings: `repo=mycel`, `topic=Mycel 2 implementation language`, `depth=standard`.

## Recommendation

Keep Python as the provisional default for Mycel 2 pending a demonstrated continuing advantage from TypeScript. The current requirements contain no demonstrated Python limitation that warrants switching languages. TypeScript is suitable; its strongest prospective advantages are lower maintenance cost within the surrounding stack and direct access to its languages' first-party compiler tools. Neither has yet been established against the cost of translating retained behavior and accommodating future numerical work.

An 80 MB executable is not a reason to discard Python. Repeated extraction, slow command startup, unreliable dependency installation and maintenance effort are legitimate concerns. They must be compared between realistic deployment designs for both languages. Version 1's defects also require a redesign in either language: compare Mycel 2 implemented with strict typing and tests in Python against Mycel 2 implemented with strict typing and tests in TypeScript, rather than old Python with an idealized new TypeScript program.

This is a research recommendation, not an accepted language decision or an implementation change. MYC-D1 is still Open. Detailed external claims are time-pinned in [source notes](mycel-2-language-evaluation-2026-10/sources.md). Reproduction material belongs in the [evidence folder](mycel-2-language-evaluation-2026-10/README.md).

<!-- sources:
mycel:specs/00-overview-and-legacy-map.md#Decisions
mycel:specs/01-corpora-and-ingest.md#The pass
mycel:research/mycel-2-language-evaluation-2026-10/sources.md
-->

## What the original proposal actually establishes

MYC-D1 proposes TypeScript on Node.js 24, citing the Drivers, the existing npm package, and version 1's bundled Python programs. The Drivers' decision separately cites generated Codex TypeScript bindings and recurring Python service bundling failures. The Codex protocol argument is specific to those Drivers: Mycel's planned network dependency is its embedding provider. It does not establish a Mycel-specific benefit.

The new Mycel repository is an empty scaffold. Its package.json contains metadata and no implementation, dependency list, build script or TypeScript configuration. Consequently, the npm package is an administrative convenience, not existing TypeScript code that must be preserved. The build contract leaves compilation to each component; a Node launcher executing another program does not require that program to be written in TypeScript.

MYC-0 further specifies a command-line interface, one JSON result and no library for callers. An Arbol caller can consume that contract from either implementation. Internal TypeScript interfaces can be useful, but matching the caller's language does not remove serialization, versioning or runtime validation at the process boundary.

Evidence locators:

- MYC-0:71–76 describes the process boundary and independence; :238 records MYC-D1 as Open.
- [the new repository README](/Users/example/repos/sylvan-stack/mycel/README.md:5) states that no implementation exists; [package.json](/Users/example/repos/sylvan-stack/mycel/package.json:1) supplies metadata only. Both are captured in the local evidence snapshot.
- Driver Contract:208 gives DRV-D1's rationale; Builds:16 leaves compilation to each repository and :124 describes the Node launcher.

<!-- sources:
mycel:specs/00-overview-and-legacy-map.md#Form and hosting
mycel:specs/00-overview-and-legacy-map.md#Decisions
mycel:research/mycel-2-language-evaluation-2026-10/local-evidence.md#The new Mycel scaffold
arbol:driver-contract/00-overview-and-boundary.md#Decisions
arbol:builds/00-builds-and-versions.md#Scope
arbol:builds/00-builds-and-versions.md#Where the build tool and the launchers are
-->

## The workload that matters

| Mycel responsibility | Where the work runs | Consequence for the language choice |
|---|---|---|
| Scan files, hash contents, split Markdown and source code | Filesystem, hash implementation, parsers and application logic | Both languages support it; parser correctness and throughput must be measured |
| Reconcile identity, track provenance, mark stale chunks | Application algorithms and transactional PostgreSQL statements | Neither language proves the algorithms or transaction boundaries correct |
| Produce embeddings | An external provider, in the first release | Python's local model ecosystem is not needed for this release; Node async I/O is suitable but not unique |
| Vector similarity and BM25 search | PostgreSQL extensions | The client language does not implement the main search indexes |
| Combine rankings, follow provenance, build JSON results | Application logic and SQL round trips | Query shape, deterministic ordering, result validation and tests matter more than a language label |
| RAPTOR clustering and summaries | Later functionality; existing numerical implementation uses NumPy and scikit-learn | A material future Python advantage, given low weight in the first-release decision |

The legacy embedder's vector query uses the SQL distance operator, and its lexical query calls ParadeDB's match and score functions (embedder.py:476–493). Rank fusion is a short application loop (embedder.py:584–594). MYC-3 proposes an outside embedding provider, and MYC-D4 defers cluster summaries. No representative CPU profile establishes that application-language execution is the dominant cost across Mycel's workloads.

These observations do not mean performance never matters. Large scans, source parsing, identity matching and graph walks can become CPU-heavy. They mean the burden is on a representative measurement, rather than a generic claim that Node is faster or Python is an ML language.

<!-- sources:
mycel:specs/03-embedding.md#The model and the provider
mycel:specs/04-retrieval.md#Two arms
mycel:specs/04-retrieval.md#Two routes
mycel:specs/00-overview-and-legacy-map.md#Decisions
-->

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`
- `mycel_deprecated_v1:mycel/knowledge/clustering.py#cluster`

## The strongest substantive case for TypeScript

**Lower recurring maintenance cost is the main case.** If the same people maintain Mycel and the TypeScript Drivers, one runtime family, compiler, debugger, dependency workflow and release discipline can reduce the knowledge and machinery they must maintain. That can be worth more than migration cost over the product's life. However, no staffing, familiarity, maintenance-hours or incident comparison establishes that saving here. Sharing workflow conventions need not mean importing Arbol code: Mycel must retain its specified independence.

**Explicit state modelling is a concrete fit.** Mycel has identity outcomes such as edited, renamed and returned; embedding outcomes such as pending and failed; and retrieval routes, fallback outcomes and freshness states. TypeScript discriminated unions and exhaustive checks can make it harder to add a state without updating its consumers, and can associate each state with the fields it requires. This is a useful design approach for the rewrite. It is not exclusive to TypeScript: strict Python checkers support typed tagged unions and exhaustiveness too. Both need behavioral tests for transitions and runtime checks for external inputs.

**Direct compiler access is a Mycel-specific option worth evaluating.** A TypeScript implementation can use the first-party TypeScript AST API for TS/JS declarations and the Svelte compiler's parsing API for Svelte structure. This could simplify maintaining correct extraction as those languages evolve, particularly compared with version 1's regex-based Svelte block splitter. It is a prospective integration advantage, not a measured accuracy gain. Python already has Tree-sitter for TS/JS, and Node still needs a parser for Python and the other supported languages. The APIs also require version pinning: the TypeScript compiler wiki currently documents version 6 and earlier and warns that 7.1 has a different API. [TypeScript compiler API](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API), [Svelte compiler parsing](https://svelte.dev/docs/svelte/svelte-compiler#parse).

**Node is technically suitable for the first-release orchestration.** Asynchronous filesystem and network interfaces and PostgreSQL/vector clients cover the needed integrations. Suitability is established by the available APIs; superior throughput or simpler implementation for this particular program is not. CPU-heavy parsing does not become concurrent merely because the orchestration uses promises. Node worker pools add initialization and communication costs; Python asyncio similarly does not make CPU loops parallel. Use bounded concurrency and profile before adding either.

Primary evidence: [TypeScript narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html), [mypy tagged unions](https://mypy.readthedocs.io/en/stable/literal_types.html#tagged-unions), [Node workers](https://nodejs.org/docs/latest-v24.x/api/worker_threads.html), [Python asyncio](https://docs.python.org/3/library/asyncio.html), and [pgvector Node bindings](https://github.com/pgvector/pgvector-node).

<!-- sources:
mycel:specs/01-corpora-and-ingest.md#Identity
mycel:specs/03-embedding.md#Requirements
mycel:specs/04-retrieval.md#What a result says
mycel:research/mycel-2-language-evaluation-2026-10/sources.md#Contracts and concurrency
mycel:research/mycel-2-language-evaluation-2026-10/sources.md#Parsing and numerical work
-->

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_svelte`

## Why packaging does not settle the language choice

PyInstaller documents that a one-file bundle extracts support files into a temporary directory before the application starts; one-folder deployment avoids that repeated extraction. Since Mycel starts a process for each operation, startup is a real usability concern. The concern is latency and reliability, not the disk space occupied by the executable. [PyInstaller operating modes](https://pyinstaller.org/en/stable/operating-mode.html#how-the-one-file-program-works).

A credible Python alternative is a pinned interpreter and a locked, non-editable environment installed once for each immutable numbered build, then direct execution of its installed entry point. uv supports managed interpreters, lockfiles and exact synchronization. Installation happens when creating the build; an ordinary search should not resolve packages, download a runtime or synchronize its environment. A per-build installer must also account for path stability because installed entry-point shebangs and virtual environments may refer to absolute interpreter paths. The benchmark's broken old editable mapping is evidence of that requirement, not a reason to reuse an editable development environment for deployment. [uv runtime management](https://docs.astral.sh/uv/guides/install-python/) and [lock/sync behavior](https://docs.astral.sh/uv/concepts/projects/sync/).

Node also needs a runtime and dependencies. Native Tree-sitter bindings retain compiled-addon concerns. WASM changes those tradeoffs but adds grammar assets and initialization. Node's single-executable mechanism embeds the application into a Node binary; its native-addon example writes the addon to a temporary file before loading it. Thus replacing one bundled runtime with another does not inherently remove the packaging failure class. This is a deployment consideration, not a recommendation to use Node's single-executable mechanism. [Node 24 single executables](https://github.com/nodejs/node/blob/v24.x/doc/api/single-executable-applications.md).

<!-- sources:
mycel:research/mycel-2-language-evaluation-2026-10/sources.md#Packaging
mycel:research/mycel-2-language-evaluation-2026-10/startup-results.json
-->

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel.spec`
- `mycel_deprecated_v1:pyproject.toml`

## Measured command startup

Twenty measurements per target after two warmups gave the following results on the owner's arm64 Mac. The benchmark randomized order within each round, used a sanitized environment and a nonexistent configuration path, and reached help without dispatching a database or provider operation.

| Target | Median | p95 | Range |
|---|---:|---:|---:|
| Installed frozen Python Mycel 1, `--help` | 3,628.2 ms | 3,734.2 ms | 3,428.6–3,825.9 ms |
| Current deprecated Python checkout, unbundled `--help` | 79.9 ms | 87.2 ms | 75.4–101.6 ms |
| Python 3.12.14, interpreter only | 17.6 ms | 18.3 ms | 16.6–19.9 ms |
| Node 24.21.0, interpreter only | 19.1 ms | 22.6 ms | 17.9–22.7 ms |

This demonstrates that seconds-long command-readiness overhead is avoidable while retaining Python. It does not establish a Python or TypeScript application speed advantage. The installed executable was built on 23 September; the checked-out version 1 source has later changes, so the difference cannot be attributed entirely to extraction. Filesystem caches were not flushed, and these trials measure spawn, imports, help generation and teardown rather than a search or ingest. Empty-interpreter timings cannot predict either complete application.

The [raw records](mycel-2-language-evaluation-2026-10/startup-results.json) contain every measurement, runtime versions, binary/source hashes, command arguments, environment isolation and limits. The [runner](mycel-2-language-evaluation-2026-10/startup-benchmark.py) and [method report](mycel-2-language-evaluation-2026-10/startup-method.md) are preserved. All 88 timed subprocesses, including warmups, exited successfully with no stderr.

<!-- sources:
mycel:research/mycel-2-language-evaluation-2026-10/startup-results.json
mycel:research/mycel-2-language-evaluation-2026-10/startup-benchmark.py
mycel:research/mycel-2-language-evaluation-2026-10/startup-method.md
-->

## Python-specific advantages and the cost of translation

The existing Python engine already indexes multiple source languages. code_chunker.py:72–106 uses Python's AST; :141–158 uses Python Tree-sitter bindings for TypeScript/TSX/JavaScript. Python is not restricted to indexing Python. Both Python and Node have official Tree-sitter bindings. Python's AST includes declarations, decorators and source spans, while ordinary comments require tokenization, a concrete syntax tree or source association. MYC-1's corrected decorator/comment ownership therefore still needs work. AST grammar support also follows the selected interpreter version. [Python ast](https://docs.python.org/3/library/ast.html), [tokenize](https://docs.python.org/3/library/tokenize.html), [Tree-sitter bindings](https://tree-sitter.github.io/tree-sitter/using-parsers/index.html).

Keeping Python avoids changing both architecture and the language semantics of every retained text algorithm at the same time. That is a risk reduction, not an estimate that some percentage of version 1 can be reused unchanged. Version 1's identity matching, transaction handling and ranking must be repaired; a Python rewrite should preserve verified behavior and parser knowledge rather than copy the old implementation blindly.

Future RAPTOR work strengthens the Python case. clustering.py:10–12 imports NumPy, PCA and GaussianMixture; :40–62 performs dimension reduction, a BIC component sweep and soft membership. TypeScript would require selecting and validating numerical equivalents or adding another execution boundary later. This matters for lifecycle planning, but MYC-D4 puts it after the first release, so it cannot be treated as an immediate requirement.

<!-- sources:
mycel:specs/01-corpora-and-ingest.md#Splitting code
mycel:specs/00-overview-and-legacy-map.md#Decisions
mycel:research/mycel-2-language-evaluation-2026-10/sources.md#Parsing and numerical work
-->

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_python`
- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py#chunk_typescript`
- `mycel_deprecated_v1:mycel/knowledge/clustering.py#cluster`

## Two verified semantic changes in a straightforward port

The legacy query classifier uses `^[\w.#/-]+$` (embedder.py:500). Python and JavaScript assign different default meanings to `\w`: `café` is an identifier-shaped query in Python but takes the question route with the same JavaScript pattern. The port needs an explicit character policy; copying the expression is insufficient.

The legacy section hash normalizes NFKC, then collapses `\s+` (chunker.py:118–128). The whitespace sets also differ. For text containing U+0085, Python collapses the separator while JavaScript retains it. For U+FEFF, JavaScript collapses it while Python retains it. Different normalized bytes produce different hashes and can change unchanged/edited decisions, content-based identity reconciliation and staleness. These differences were reproduced on the local runtimes; they are not predicted benchmark performance.

| Input | Python result | JavaScript result |
|---|---|---|
| Query `café` | Identifier route | Question route |
| Hash text `a\u0085b` | `a b` | `a\u0085b` |
| Hash text `a\ufeffb` | `a\ufeffb` | `a b` |

A language switch can still be correct. Define the required semantics and test the Unicode, parser and ranking boundaries against those definitions. Mycel 2 is a clean rewrite, so a deliberate semantic change can be accepted; an accidental one cannot be justified as an improvement merely because it is in a new language. The same principle applies to a Python rewrite.

<!-- sources:
mycel:research/mycel-2-language-evaluation-2026-10/unicode-results.json
mycel:research/mycel-2-language-evaluation-2026-10/sources.md#Unicode behavior
-->

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#norm`
- `mycel_deprecated_v1:mycel/knowledge/chunker.py#content_hash`

## What a language switch will not fix

Version 1's database connection uses autocommit (database.py:76–77). Updating file hashes and chunks in separate statements does not become atomic through TypeScript types. A correct implementation must put the complete file reconciliation in a transaction; node-postgres requires all transaction statements on the same client, and Psycopg provides transaction contexts.

The observed wrong repository scope, precommitted source hashes, checkout resets, greedy identity assignment and repeated ranking bonuses are algorithm and boundary defects. Both implementations need explicit scope, state transitions, cancellation, locking and store-backed tests. MYC-0.11 already requires automated verification against a disposable store. The source inventories also identify query-shape opportunities: a materialized exact-distance document search, one bridge SQL query per selected document, and per-result provenance hydration. These are candidates to profile and improve, not findings that they dominate every production request.

<!-- sources:
mycel:specs/01-corpora-and-ingest.md#The pass
mycel:specs/00-overview-and-legacy-map.md#Requirements
mycel:research/v1-inventory-embedding-and-retrieval.md
mycel:research/mycel-2-language-evaluation-2026-10/sources.md#Database clients
-->

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/database.py#connect`
- `mycel_deprecated_v1:mycel/knowledge/store.py#detect`

## Decision matrix

| Criterion | What the evidence favors |
|---|---|
| First-release feature feasibility | Both |
| CLI/process compatibility with Arbol | Both; the contract is JSON |
| Strict state/result contracts | Both; TypeScript offers a natural fit with the stack's existing conventions |
| Single-runtime maintenance | TypeScript, if an organizational standard is genuinely desired and enforced |
| Direct first-party TypeScript/Svelte compiler integration | TypeScript offers a credible option; its benefit over existing bindings remains unmeasured |
| Preserve existing parser and algorithm knowledge | Python |
| Future numerical clustering | Python, but deferred |
| Avoid the old one-file extraction | Both, with appropriate deployment |
| Better ingest or search performance | Undetermined without representative prototypes |
| Correct transactions, scoping and ranking | Neither by itself; design and verification determine this |

This is a qualitative comparison, not an arbitrary points score. The deciding variable is the value placed on one runtime and one set of maintenance skills relative to translation risk and numerical-library needs.

<!-- sources:
mycel:research/mycel-2-language-evaluation-2026-10/sources.md
mycel:specs/00-overview-and-legacy-map.md
mycel:specs/01-corpora-and-ingest.md
mycel:specs/03-embedding.md
mycel:specs/04-retrieval.md
-->

## Better wording for MYC-D1

Suggested proposal, not applied to the specification:

> Python and TypeScript both support Mycel's required workload. TypeScript would standardize implementation and release tooling with the Drivers, which may lower recurring maintenance cost. Python preserves existing parsing and algorithm knowledge and provides the numerical libraries needed for later clustering. The choice should compare those lifecycle costs and realistic deployment paths. Binary size and version 1's correctness defects do not establish a language preference. Pending that comparison, Python remains a viable provisional default.

If the owner deliberately chooses a one-language stack, an honest acceptance rationale can instead say that reducing recurring runtime, dependency, debugging and release maintenance outweighs the porting cost, subject to demonstrating parser/normalization correctness and a reliable deployment path. It should not promise better retrieval accuracy or speed without evidence.

<!-- sources:
mycel:specs/00-overview-and-legacy-map.md#Decisions
mycel:research/mycel-2-language-evaluation-2026-10/sources.md
-->

## Open questions and a useful acceptance experiment

The following were not established by this research:

1. Whether maintainers are materially more productive with TypeScript, or whether supporting pinned Python actually costs more. No staffing or maintenance record was provided.
2. Which implementation is faster or uses less memory on representative scans and searches. The startup experiment measures packaging/runtime readiness, not an implemented TypeScript Mycel.
3. Whether every required grammar and native dependency installs reliably on the intended architectures. Documentation proves availability, not this release's build reliability.
4. Which behavior changes should intentionally be accepted for Unicode classification, normalization and parser fallbacks. They must be specified rather than inherited accidentally.
5. The eventual scope and timing of clustering and on-device inference. Both are outside the immediate release.

A useful comparison is a small vertical slice in each language using the same files, database schema, query and embedding response: validated settings, Markdown/Python/TypeScript/Svelte extraction including decorators and comments, one file's transactional reconciliation, and search into versioned JSON. Allow each ecosystem's credible parser choices for the product comparison; a separate matched-parser experiment can isolate runtime effects. First require agreement on the specified outputs and fault behavior; then compare startup p50/p95, scan and parse throughput, changed-file ingest, SQL round trips, peak memory, cancellation and install reliability. Record implementation and debugging effort as well as runtime numbers. Include Unicode and duplicate-name cases, an interrupted file transaction, an unavailable provider and a busy repository. Use an installed Python environment and prebuilt JavaScript on equivalent runtime provisioning; testing PyInstaller extraction against an unbundled Node program would confound deployment with language.

The choice is ready when a specific continuing benefit justifies its continuing costs. At present, Python cannot reasonably be rejected on the stated 80 MB rationale.

<!-- sources:
mycel:specs/00-overview-and-legacy-map.md#Requirements
mycel:specs/01-corpora-and-ingest.md#Requirements
mycel:specs/03-embedding.md#Requirements
mycel:specs/04-retrieval.md#Requirements
mycel:research/mycel-2-language-evaluation-2026-10/sources.md
-->
