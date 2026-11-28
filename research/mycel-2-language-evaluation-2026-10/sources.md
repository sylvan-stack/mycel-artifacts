---
role: authored
---
# Primary-source notes for the Mycel 2 language evaluation

Retrieved on 7 October 2026. These are time-pinned, paraphrased notes of the specific claims used in the evaluation, rather than copies of whole external documents. Links may evolve after this date. Local empirical evidence records the actual runtime versions separately.

## Contracts and concurrency

- [TypeScript narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html): a shared literal discriminator narrows a union; `never` can support an exhaustive switch. This is useful for identity and result states.
- [TypeScript erased types](https://www.typescriptlang.org/docs/handbook/2/basic-types.html#erased-types): annotations disappear from emitted JavaScript. A declared interface does not validate incoming JSON.
- [Node 24 TypeScript execution](https://nodejs.org/docs/latest-v24.x/api/typescript.html): native type stripping executes supported syntax and does not type-check. CI still needs a checker; unsupported transforms and package conventions need attention.
- [mypy tagged unions and exhaustiveness](https://mypy.readthedocs.io/en/stable/literal_types.html#tagged-unions): Literal-tagged TypedDict unions can narrow; `assert_never` and exhaustive-match checking detect missing cases.
- [mypy strict options](https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict): strict checking enables a family of checks. Its exact options are version-sensitive, so pin the checker in the build.
- [Pyright configuration](https://github.com/microsoft/pyright/blob/main/docs/configuration.md): strict checking is available, including diagnostics for unknown and incompatible types.
- [Python typing](https://docs.python.org/3/library/typing.html): annotations and TypedDict expectations are not generally enforced by the Python runtime. External values require validation.
- [Python asyncio](https://docs.python.org/3/library/asyncio.html) and [task documentation](https://docs.python.org/3/library/asyncio-task.html): async/await supports concurrent I/O; task groups, cancellation and timeouts are supported.
- [Node 24 filesystem](https://nodejs.org/docs/latest-v24.x/api/fs.html): asynchronous filesystem interfaces exist. Concurrent mutation ordering is the application's responsibility.
- [Node 24 workers](https://nodejs.org/docs/latest-v24.x/api/worker_threads.html): workers can execute CPU-intensive JavaScript in parallel; a pool can avoid repeated startup overhead. Async I/O generally does not need workers.

## Database clients

- [Psycopg concurrency](https://www.psycopg.org/psycopg3/docs/advanced/async.html): synchronous and asynchronous use are supported. Operations sharing one connection serialize and share its transaction; independent database concurrency requires appropriate connections.
- [Psycopg transactions](https://www.psycopg.org/psycopg3/docs/basic/transactions.html#transaction-contexts): transaction contexts support committing a completed block and rolling it back after an exception. Their existence does not make separately autocommitted application statements atomic.
- [node-postgres transactions](https://node-postgres.com/features/transactions): transactions use explicit BEGIN/COMMIT/ROLLBACK and must use one client for all statements. Calls through an unpinned pool are not an equivalent transaction boundary.
- [pgvector Python](https://github.com/pgvector/pgvector-python): supported clients include Psycopg 3 and asyncpg, with vector registration and query examples.
- [pgvector Node](https://github.com/pgvector/pgvector-node): supported clients include node-postgres and several other Node/TypeScript integrations. This establishes client support in both ecosystems.

## Packaging

- [PyInstaller operating modes](https://pyinstaller.org/en/stable/operating-mode.html#how-the-one-file-program-works), documentation observed as 6.22.3: one-file bootloaders extract non-Python support files into a temporary directory. The documentation explains their slower startup relative to one-folder deployment.
- [uv installing Python](https://docs.astral.sh/uv/guides/install-python/): uv detects existing interpreters and can install managed Python distributions. CPython distributions are obtained from Astral's python-build-standalone project.
- [uv tools](https://docs.astral.sh/uv/concepts/tools/): tool installation places entry points on PATH while retaining an isolated environment. Tool execution and persistent installation differ.
- [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/): `--locked` refuses an outdated lock, `--frozen` skips that currency check, synchronization is exact by default, and installation can be non-editable. Default execution can synchronize the environment; use a preinstalled entry point for an immutable application build.
- [Node 24 single executables](https://github.com/nodejs/node/blob/v24.x/doc/api/single-executable-applications.md): applications are injected into a Node executable. The observed documentation marks the mechanism as active development and supports an embedded CommonJS script. Its native-addon example writes an asset to a temporary file before loading it. This is evidence that bundling and addons still need a deployment design, not a measured Mycel performance comparison.
- [node-tree-sitter package](https://github.com/tree-sitter/node-tree-sitter/blob/master/package.json): the inspected package uses native-addon tooling, including node-addon-api and node-gyp-build. Prebuilt artifacts reduce some compilation needs, but architecture/runtime and grammar compatibility still require verification.
- [Web Tree-sitter](https://github.com/tree-sitter/tree-sitter/blob/master/lib/binding_web/README.md): WebAssembly bindings provide another execution path with a runtime WASM asset and language grammar loading. Availability alone establishes no startup/throughput advantage.

## Parsing and numerical work

- [TypeScript compiler API](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API), wiki updated 17 August 2026: SourceFile exposes an AST, traversal and source positions; parsing/traversal can be performed without requesting semantic type checking. The page covers TypeScript 6 and earlier and warns that 7.1 introduces a different API. Any prototype must pin the API version.
- [Svelte compiler parsing](https://svelte.dev/docs/svelte/svelte-compiler#parse): the compiler exposes a parsing API and AST types, including component script and styling structure. Direct access is a prospective extraction advantage for Node users; no Mycel accuracy or throughput comparison was run.
- [Python ast](https://docs.python.org/3/library/ast.html), observed Python 3.14.8 documentation: parse trees expose function/class declarations, decorator lists and source spans. Grammar evolves with Python releases; column offsets use UTF-8 byte positions.
- [Python tokenize](https://docs.python.org/3/library/tokenize.html): comment tokens are retained. Its documented use is for syntactically valid Python, so malformed-file fallback still needs a policy.
- [Tree-sitter parser bindings](https://tree-sitter.github.io/tree-sitter/using-parsers/index.html): official bindings include Python and Node.js. Multi-language source parsing is not exclusive to either candidate language.
- [scikit-learn Gaussian mixtures](https://scikit-learn.org/stable/modules/mixture.html): GaussianMixture supports probabilistic clustering and BIC-based model selection. The legacy implementation uses this API; the evaluation does not claim other ecosystems cannot implement it.
- [NumPy thread safety](https://numpy.org/doc/stable/reference/thread_safety.html): many NumPy operations release the GIL, but shared mutable arrays require care. This does not imply arbitrary Python loops execute in parallel.

## Unicode behavior

- [Python regular expressions](https://docs.python.org/3/library/re.html): default string-pattern word characters include Unicode alphanumerics, and whitespace follows Python's Unicode whitespace semantics. ASCII mode is an explicit alternative.
- [ECMAScript WordCharacters](https://tc39.es/ecma262/multipage/text-processing.html#sec-wordcharacters): default word characters are the ASCII word set; case-folding flags have further specified behavior. The comparison probes use the default flags found in a straightforward translation.
- [ECMAScript WhiteSpace](https://tc39.es/ecma262/multipage/ecmascript-language-lexical-grammar.html#sec-white-space): the language defines its whitespace and line-terminator sets, including U+FEFF. They are not identical to Python's set. The actual U+0085/U+FEFF results are recorded by the local probe rather than assumed from these notes.
