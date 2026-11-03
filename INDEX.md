# Mycel Operations Catalog

- [Justify code and documents](operations/justification.md) — normalize requirement identities, preserve existing claims, recover gaps and audit them; optional Origin Coverage for new work.

> **Start at the [Instructions Hub](./README.md)** — the routing table. This
> INDEX is the full catalog of the Mycel corpus (`~/Artifacts/mycel/`, repo
> `mycel`, its own git repo): everything about **how to work**. The product —
> Arbol's specifications — is one corpus over in
> [`~/Artifacts/arbol/`](../arbol/INDEX.md). Shared vocabulary:
> [GLOSSARY](../arbol/GLOSSARY.md).

Everything here passes the **VS Code Test**: usable without Arbol installed.

## Chapters

### `specs/` — what Mycel 2 does
The specifications of the rewrite, written from what version 1 did. Start at the chapter's [README](./specs/README.md), which also states their conventions.
- [`00-overview-and-legacy-map.md`](./specs/00-overview-and-legacy-map.md) (MYC-0) — what Mycel is for, what it leaves to others, its form, the rules of its command line, and where each part of the version 1 code went.
- [`01-corpora-and-ingest.md`](./specs/01-corpora-and-ingest.md) (MYC-1) — repositories and their two corpora, the scan, splitting documents and code into chunks, identity, the pass, status, removing a repository.
- [`02-provenance-and-freshness.md`](./specs/02-provenance-and-freshness.md) (MYC-2) — what a document declares, Source Refs and how they resolve, edges, roles, staleness and its reasons, becoming fresh again.
- [`03-embedding.md`](./specs/03-embedding.md) (MYC-3) — the model, the text that is embedded, which chunks are pending, the embed operation, failures, counts, the key.
- [`04-retrieval.md`](./specs/04-retrieval.md) (MYC-4) — the scope of a search, its two arms and two routes, the bridge from documents to code, documents among results, the reply, freshness on read.
- [`05-settings.md`](./specs/05-settings.md) (MYC-5) — the settings file and how it is found, every key with its type and default, keys Mycel does not know, environment variables, the two secrets and the Keychain item.
- [`06-index-store.md`](./specs/06-index-store.md) (MYC-6) — what the store holds and what only it holds, its address, `mycel init` and the format number, transactions, two invocations at once, rows of repositories the settings no longer name.
- [`07-drifts-and-verification.md`](./specs/07-drifts-and-verification.md) (MYC-7) — relations without authority, recorded verification, generated edges and an edge whose source is deleted; forwards classification and the Drift lifecycle to MYC-14.
- [`08-summaries.md`](./specs/08-summaries.md) (MYC-8) — summaries of groups of sections: what is grouped and how, the command that writes the text, the request, building, writing stale ones again, summaries in a search.
- [`09-code-overview.md`](./specs/09-code-overview.md) (MYC-9) — the overview of a repository's code: what a section lists, when it is made, where it is kept, how it is found and read.
- [`10-grep-replacement.md`](./specs/10-grep-replacement.md) (MYC-10) — `mycel grep`: running grep unchanged, finding the pattern, the tail and when it is left out, where the command departs from the command-line rules.
- [`11-reading-a-chunk.md`](./specs/11-reading-a-chunk.md) (MYC-11) — `mycel read`: naming a chunk, the reply, lines around a symbol, and what `mycel info` says the program offers.
- [`12-record-of-work.md`](./specs/12-record-of-work.md) (MYC-12) — which invocations leave an entry, what it holds, identity decisions, an invocation that was cut short, how long entries are kept.
- [`13-checks-and-evaluation.md`](./specs/13-checks-and-evaluation.md) (MYC-13) — the checks of every build, the store of a check, the stand-in for the embedding service, the live check, the evaluation set and its report.
- [`14-drift-detection.md`](./specs/14-drift-detection.md) (MYC-14) — Jev classification, five-minute debounce, independent smarter review, finite execution, exact-pair work lifecycle and provider qualification.
- [`15-distribution-and-replacement.md`](./specs/15-distribution-and-replacement.md) (MYC-15) — independent Python runtime, immutable Builds, launcher and selection, release checks, leases, pruning and staged version 1 removal.
- [`16-source-addresses-and-evidence.md`](./specs/16-source-addresses-and-evidence.md) (MYC-16) — portable root-qualified addresses, exact versions, dependant-owned baseline snapshots, complete classifier evidence, retention and reconstruction.

### `research/` — evidence the specifications rest on

The receipts of the Mycel 2 implementation runs of 9 to 17 October 2026, which were
never committed, were removed on 2 November 2026 at the owner's direction: recorded
results of tests, probes and benchmarks stay out of Git.

- [`retrieval-evaluation.toml`](./research/retrieval-evaluation.toml) — five real Mycel questions with exact parsed artifact-section expectations. Not yet configured or measured; no ranking change or MYC-4.25 acceptance is inferred.
- [`mycel-2-language-evaluation-2026-10.md`](./research/mycel-2-language-evaluation-2026-10.md) — Python versus TypeScript for Mycel 2: workload fit, maintenance tradeoffs, modern deployment, measured startup and verified Unicode port risks; recommendation and open evidence gaps for MYC-D1.
- [`v1-inventory-ingest-and-graph.md`](./research/v1-inventory-ingest-and-graph.md) — what the version 1 source does for the scan, chunking, identity, Source Refs, edges and detection, with ordinary historical evidence locators into the unindexed deprecated repository.
- [`v1-inventory-embedding-and-retrieval.md`](./research/v1-inventory-embedding-and-retrieval.md) — the same for embedding, the two indexes, the search algorithm, the reply and the grep replacement.
- [`v1-inventory-sync-settings-commands.md`](./research/v1-inventory-sync-settings-commands.md) — the same for the sync pass, the remote refresh, settings, the store's address, repository scope, every command and the summaries.
- [`v1-observations-2026-10.md`](./research/v1-observations-2026-10.md) — what the installed version 1 was seen doing on 6 to 8 October 2026.
- [`v1-probes-2026-10-07/`](./research/v1-probes-2026-10-07/README.md) — the scripts behind the inventory statements that were run and not only read.

### `operations/` — Mycel Operations: frontend-agnostic process descriptions
What must happen, in Mycel vocabulary — the invariant behind every invocation surface (skills, CLI agents, humans).
- [`OVERVIEW.md`](./operations/OVERVIEW.md) — the readable one-page summary of all operations (for humans; agents use the Hub).
- [`code-research-levels.md`](./operations/code-research-levels.md) — exact lookup, cited explanations and durable task context: which tool when.
- [`code-research.md`](./operations/code-research.md) — the level-2 loop. Skills are thin dispatchers pointing here.
- [`deep-research.md`](./operations/deep-research.md) — the level-3 process: inputs, angles, output contract, quality bar.
- [`embedding.md`](./operations/embedding.md) — scoped ingest and embedding plans, retained progress, retries and the owner-first-ingest boundary.
- [`retrieval.md`](./operations/retrieval.md) — schema-3 wording/meaning results, document bridges, freshness and source citations.
- [`code-map.md`](./operations/code-map.md) — the mechanical per-repo overview artifact and its `generated: true` semantics.
- [`knowledge-model.md`](./operations/knowledge-model.md) — the value reference: in-band declarations (`role:` / `status: heartwood` / `generated:` / `sources:`), chunk roles/states, Derivation kinds/policies, Detection reasons, Drift lifecycle.
- [`authored-work-integration.md`](./operations/authored-work-integration.md) — corpus coverage, Source Refs before authorized ingest, assertion exceptions, Detection, embedding and retrieval verification.
- [`create-skill.md`](./operations/create-skill.md) — create one provider-agnostic Mycel Skill and its thin provider adapters; covers native Codex CLI and Claude Code CLI discovery, symlinks, and invocation policy.
- [`initiative.md`](./operations/initiative.md) — own a delegated goal's plan, decisions and experiments, conserve the owner's attention, and keep progress and results inspectable without expanding narrowly assigned work.
- [`pr-deep-review.md`](./operations/pr-deep-review.md) — multi-session review of a large pull request: sync with the head, ranked areas, verified and independently challenged findings, a queue of drafted comments for the human reviewer, commands for the recurring steps (next, commits, verify, replies, check, summary, status), stop criteria on findings, time, tokens and coverage; never posts.
- [`pr-deep-review-reference.md`](./operations/pr-deep-review-reference.md) — its lookup companion: `state.json` schema, area and finding statuses, templates for the reviewer's page, finding card and run report, stop-criteria measures and kinds, reading token spend, commands for reading a GitHub pull request.
- [`stints.md`](./operations/stints.md) — named sets of stop criteria for a run: the defined stints, how a run resolves its stint and limits, how to add or change one.
- [`linear-resolve.md`](./operations/linear-resolve.md) — go through the owner's unresolved comments in the Linear workspace: which threads a run takes, what a comment may ask for, changing the original and then its Linear copy, the numbered list of comments and responses given in the session, the user's answers, the `Resolved. Resolution: …` reply posted only after the user says `Resolved`, and what the Linear connector can and cannot do.
- [`linear-open-questions.md`](./operations/linear-open-questions.md) — answer in the session the questions and pending decisions that wait for the owner in the Linear workspace: what counts as an open question, the numbered list a run gives, how the user answers by number, and what is written to the specification, the issue or the thread once they have answered.
- [`linear-organize.md`](./operations/linear-organize.md) — make the owner's current attention items visible through a prominent document/view with individual open questions, pending decisions, reviews, and next actions; then organize project references and remove obsolete shortcuts.
- [`linear-completion.md`](./operations/linear-completion.md) — finish a task by preserving its ID and hand-over in private weekly files of at most 100 tasks, then deleting its Linear issue; resume failed removals and recognize completed prerequisites after deletion.
- [`sagas.md`](./operations/sagas.md) — organize work as Sagas, Arcs and Beats, with Sagas, Arcs and Beats as files in `~/Artifacts/sagas/` and their copies in Linear: order and progress, territories of folders and files, the files every Beat may add to, hold files and who owns them, automatic release of a gone agent's hold, taking the next Beat, the plan of a Beat and how its ticked steps measure progress, working, stopping and finishing, planning a Saga, and what is not built yet.
- [`workspace-ledger.md`](./operations/workspace-ledger.md) — territory bookings in a Workspace for a Saga or ad-hoc work, shared across Chat Sessions and subagents; `.ledger/bookings.json`, one event file per booking and `history.jsonl` in every Workspace; precise net results inside each territory from Git-backed boundary snapshots, supplementary tool/watcher history, private configuration and the single switch-over from hold files; links to the standalone `workspace-ledger` specifications. Decided 30 October 2026, not yet implemented.
- [`radar-stats.md`](./operations/radar-stats.md) — show unfinished Sagas or one selected by name or folder, each with its unfinished Arcs: its share of work Done, In progress and Other in plan steps, the agents working on it now and their context; open with names of Sagas finished within three days, omit older completions, and end with recently worked-on Sagas and Arcs under unfinished Sagas; how each number is counted, and what is not counted yet.
- [`background-jobs.md`](./operations/background-jobs.md) — long work split into the smallest steps its tool allows, each step that may run more than 5 minutes recorded with `bgjob`, so the menu bar shows it under the chat that started it with elapsed time and progress, and macOS notifies when it ends; the states, attaching to a running process, and what to do when a job is lost.
- [`agent-watch.md`](./operations/agent-watch.md) — the check from outside: every 5 minutes, with no AI, what each working agent did since its last tick, commit or message from the owner; how tokens, owner's messages, ticks, commits, changed files and repeated drafts are counted; the signals and their agreed numbers; how a signal is raised and ended; what a run leaves in `~/.sagas/watch/`; the replay and the LaunchAgent.
- [`nex-colab.md`](./operations/nex-colab.md) — Nex Colab: answer what the owner wants to learn (`/colab "prompt"`) at the depth their Nex Knowledge Map says is missing, and pitch the explanations of other work by it (`(use colab)`): the rounds of an exchange, finding the topics, the depth one level up, the skipped line and the numbered ways deeper, the `attempt` line, the assessment by the tests, raising and lowering a level, the `Shown` line, writing, checking, committing and pushing the map and the log after each reply, the subagent's brief, and showup, the owner's own statement of their level (`/colab showup`), from the words and the question to the reply; and learn mode (`/learn`), a whole session of learning and no other work, one piece per reply with the ways on, until the owner leaves it. The map is data in the private corpus `~/Artifacts/colab/`.
- [`owner-goals.md`](./operations/owner-goals.md) — record, change, replace and withdraw the owner's Owner Goals from their own words (`/owner-goals "<words>"`), answer which goals apply to something, and check that they do not contradict each other: how a statement is written, kind, scope and links, comparing with the current goals, proposals the owner confirms, the check and its findings, the commit in the local goals corpus `~/Artifacts/goals`, the reply, and reading the goals in other work.
- [`source-refs-authoring.md`](./operations/source-refs-authoring.md) — author durable provenance and section-level Source Refs without relying on instructions from another corpus.
- [`places-api-logs.md`](./operations/places-api-logs.md) — diagnose Reservble's side of the Syrve integration from the places-api daily logs: incident time in UTC, choosing log types, local search and correlation of request, order and reservation IDs, guest-data handling; the connection lives in its SFTP manual.

### `tools/` — technical manuals for the client-agnostic CLIs

- [`mycel-2-origins.md`](./tools/mycel-2-origins.md) — atomic stated Origin Links and verification, JSON-lines batches, Origin Coverage, clone changes and reasoned requirement marks.
- [`mycel-2-recovery.md`](./tools/mycel-2-recovery.md) — local Origin candidates, guarded pair judgement, capped model scores, isolated review and recovery replies.
- [`mycel-2-audit.md`](./tools/mycel-2-audit.md) — deterministic and semantic Origin findings, guarded score lowering, human settlement, bounded history and audit replies.

- [`mycel-2-drifts.md`](./tools/mycel-2-drifts.md) — internal exact-pair work, categorical results, answered-reason closure and retained evidence; public classification and reporting remain pending.
- [`mycel-2-classification.md`](./tools/mycel-2-classification.md) — canonical complete decision evidence, immutable reviewer command identity, quiet-period observations and fresh call/application/cache guards; reviewer execution and public classification remain pending.
- [`mycel-2-jev.md`](./tools/mycel-2-jev.md) — one bounded pinned-model Jev attempt, exact confidence validation and complete independent-review handoff; public orchestration and live qualification remain pending.

- [`mycel-2-retrieval.md`](./tools/mycel-2-retrieval.md) — scoped current-disk BM25 and best-part cosine candidates, deterministic ranking, exact disk-owned bridges, configured weights, document margins and stable citation order; recursive freshness and public search replies remain pending.
One [Runbook](../arbol/GLOSSARY.md#runbook) per [Tool](../arbol/GLOSSARY.md#tool).
- [`mycel-2.md`](./tools/mycel-2.md) — current Mycel 2 command boundary, complete scoped ingest, entry-only activity, settings diagnostics and plain grep fallback; reserved commands retain their owners.
- [`mycel-2-checks.md`](./tools/mycel-2-checks.md) — requirement declarations, named proofs, real disposable-store checks and staged/full gates for Mycel 2.
- [`mycel-2-settings.md`](./tools/mycel-2-settings.md) — complete strict TOML schema/defaults, safe diagnostics and independent protocol-1 reviewer configuration.
- [`mycel-2-embedding.md`](./tools/mycel-2-embedding.md) — official pinned offline tokenizer, lossless UTF-8 plans and durable receipts, with scoped public embedding, resumable progress, dry-run estimates and exact final counts; live provider qualification remains explicit.
- [`mycel-2-parsing.md`](./tools/mycel-2-parsing.md) — complete Markdown sections, frontmatter, structural source chunks, original spans and comparison hashes.
- [`mycel-2-source-refs.md`](./tools/mycel-2-source-refs.md) — location-owned declarations, durable faults/retries, typed pins and complete disk/branch/stash publication with physical/Git moves and guarded public ingest/derive.
- [`mycel-2-activity.md`](./tools/mycel-2-activity.md) — transaction-bound mutations, exact invocation liveness, readable pass identity decisions and complete ingest auditing with exact replies and rollback; general history and retention remain pending.
- [`mycel-2-builds.md`](./tools/mycel-2-builds.md) — pinned offline macOS staging, verified wheel/archive installation, durable registry and immutable manifests; full installed-release and working publication qualification remain pending.
- [`mycel-2-store.md`](./tools/mycel-2-store.md) — configured acceptance for initialization, format/catalogue guards, generation identity, atomic snapshots and nonblocking locks; full feature integration remains pending.
- [`mycel-2-capture.md`](./tools/mycel-2-capture.md) — complete read-only disk/branch/stash acquisition and public ingest publication with exact parse validation, stable identities, location-owned corpus and safe retirement.
- [`mycel-2-evidence.md`](./tools/mycel-2-evidence.md) — exact immutable comparison/snapshot manifests, dependant-owned evidence, guarded pins and reconstruction composed by complete ingest.
- [`mycel-2-identity.md`](./tools/mycel-2-identity.md) — whole-file matching, exact-version restoration, pin inheritance, parser-derived rename identity and complete located publication/collection composed by ingest.
- [`mycel-2-pin-observation.md`](./tools/mycel-2-pin-observation.md) — real fresh disk/catalog observations for guarded pins and source-missing inheritance, including exact parser projections, aliases and physical observation guards; complete commands remain pending.
- [`mycel-2-reconciliation.md`](./tools/mycel-2-reconciliation.md) — guarded dependency ownership/pins, source-only foreign refresh, mechanical propagation, public derive/relate and complete scoped ingest with busy retry and exact activity.
- [`mycel-2-evaluation.md`](./tools/mycel-2-evaluation.md) — strict versioned evaluation files, one-repository dispatch, offline recall/fault accounting and read-only snapshot comparisons; normal search/Drift execution remains pending.
- [`mycel.md`](./tools/mycel.md) — installed Mycel 2 command/manual router and repository corpus binding.
- [`linear.md`](./tools/linear.md) — connector capabilities and UI mechanics for Linear favorites, folders, sidebar customization, and question/decision navigation targets.
- [`places-api-sftp.md`](./tools/places-api-sftp.md) — the places-api log server: where the connection settings live, host key verification, unattended `sftp` sign-in on this Mac, interactive and curl access.

### `system-instructions/` — prompt files the `mycel` executable reads
Not process guides: `mycel raptor regen|build` loads both files from this folder and stops with an error when either is missing or empty.
- [`raptor-summary.md`](./system-instructions/raptor-summary.md) — the system prompt for RAPTOR cluster summaries.
- [`raptor-request.md.tmpl`](./system-instructions/raptor-request.md.tmpl) — the request template; `$sections` receives the clustered sections.

### `skills/` — Mycel Skill provider adapters
Shared activation contracts and thin Hub dispatchers for native Codex CLI and Claude Code CLI. Canonical sources are linked into `~/.agents/skills/` (Codex) and `~/.claude/skills/` (Claude). See [authoring rules](skills/README.md) and the [creation guide](operations/create-skill.md).

- [`arbol-chat-prepared-folder`](./skills/arbol-chat-prepared-folder/SKILL.md)
- [`authored-work-integration`](./skills/authored-work-integration/SKILL.md) — Source Ref-first integration into Mycel 2, with authorized indexing and explicit deferred checks.
- [`code-research`](./skills/code-research/SKILL.md) — cross-file explanations with file-and-line evidence; retrieval readiness follows the Hub.
- [`colab`](./skills/colab/SKILL.md) — explicit-only; its Claude Code adapter is [`providers/claude/colab`](./skills/providers/claude/colab/SKILL.md)
- [`corpus-admin`](./skills/corpus-admin/SKILL.md) — Mycel 2 configuration, ingest, embedding plans, summaries and index health.
- [`create-mycel-skill`](./skills/create-mycel-skill/SKILL.md)
- [`deep-research`](./skills/deep-research/SKILL.md) — durable task-context artifacts with source evidence; Mycel 2 retrieval follows Hub readiness.
- [`initiative`](./skills/initiative/SKILL.md) — ownership of a delegated broad goal with minimal demands on the owner's attention; excludes narrowly assigned tasks and subagent work with fixed deliverables.
- [`learn`](./skills/learn/SKILL.md) — explicit-only; its Claude Code adapter is [`providers/claude/learn`](./skills/providers/claude/learn/SKILL.md)
- [`linear-open-questions`](./skills/linear-open-questions/SKILL.md)
- [`linear-organize`](./skills/linear-organize/SKILL.md)
- [`linear-resolve`](./skills/linear-resolve/SKILL.md)
- [`radar-stats`](./skills/radar-stats/SKILL.md)
- [`mycel-search`](./skills/mycel-search/SKILL.md) — Mycel 2 location and document lookup with source citations.
- [`owner-goals`](./skills/owner-goals/SKILL.md) — the owner's Owner Goals managed from their own words; not Spec Requirements.
- [`places-api-logs`](./skills/places-api-logs/SKILL.md) — Reservble places-api Syrve integration logs over read-only SFTP.
- [`pr-deep-review`](./skills/pr-deep-review/SKILL.md)
- [`use-colab`](./skills/use-colab/SKILL.md)

The active catalog contains 18 Mycel skills for both providers. Personal and
third-party skills remain outside this catalog.

## Conventions

- Every artifact goes into a chapter folder, never directly into the corpus root. `README.md`, `INDEX.md` and a `GLOSSARY.md` are the exceptions.
- List a chapter here when it is created.
- Tasks are tracked in Linear, not in this corpus: project [Mycel](https://linear.app/amorphius/project/mycel-6bbdbce253fb) in the Linear workspace amorphius. Specifications are copied there as documents; `.linear.json` maps each file to its copy. The files here are the originals.
