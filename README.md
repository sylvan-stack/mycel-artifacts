---
role: authored
---
# Mycel — Instructions Hub

*(Human-readable tour of everything below: [operations/OVERVIEW.md](operations/OVERVIEW.md).)*

The **one address every consumer needs to know**: Claude Code and native Codex CLI skills,
agents, and humans all start here. Consumers point
at this file and never change; documents move freely underneath because only
this router tracks where they live.

Everything about **how to work** lives in this corpus (`~/Artifacts/mycel/`):
operations, tool runbooks and skills. It also holds the specifications of
Mycel 2 and the research they rest on. The **product** — Arbol's
specifications and the shared glossary — lives one corpus over in
`~/Artifacts/arbol/` ([its catalog](../arbol/INDEX.md)).

The engine guides and the `mycel` runbook describe Mycel 1, the executable
installed today. Mycel 2 has a local Python CLI foundation in progress. Strict settings,
repository resolution/listing, private credentials, offline embedding plans and
lossless parser preparation, explicit private-store init and store diagnostics
are implemented. Complete scoped `ingest` now publishes disk, local branches
and stashes with dependency reconciliation, Detection and collection; explicit
`--embed` adds embedding. Entry-only activity reads expose recorded identity
decisions. Exact `confirm` and read-only `verifications` now compose guarded
pin renewal, record-owned evidence, current applicability and retained history;
store format 2 keeps history across old-version collection. Configured
disposable-store acceptance covers the implemented surfaces; general activity
history, stale/status, search replies and full installed release qualification
remain pending. Its current guides are `tools/mycel-2.md`,
`tools/mycel-2-checks.md`, `tools/mycel-2-settings.md`,
`tools/mycel-2-embedding.md`, `tools/mycel-2-parsing.md` and
`tools/mycel-2-store.md`, `tools/mycel-2-capture.md`,
`tools/mycel-2-evidence.md`, `tools/mycel-2-identity.md`,
`tools/mycel-2-pin-observation.md`, `tools/mycel-2-reconciliation.md` and
`tools/mycel-2-relations.md`. The evaluation file validator and offline snapshot harness are described in `tools/mycel-2-evaluation.md`; normal search and Drift adapters remain pending. The complete
Mycel 1 corpus, including the chapters that were not carried over, is frozen
at `~/Artifacts/mycel_deprecated_v1/`.

`tools/mycel-2-retrieval.md` describes current-disk wording and meaning
candidates, configured shared selections, separate organization-member lists
and internal deterministic ranking with exact disk-owned document bridges.
Internal recursive freshness checks the exact explicit upstream closure under one existing invocation deadline; public search replies retain their task owner.

`tools/mycel-2-drifts.md` describes internal exact-pair Drift work, categorical
results, reason-level closure and independently retained evidence. Public
classification, canonical requests and provider adapters retain their task owners.
`tools/mycel-2-classification.md` describes canonical complete classification
evidence, reviewer command identity, quiet-period observations and fresh
stage/application/cache guards. `tools/mycel-2-jev.md` describes the internal
bounded Jev attempt, strict pinned-model/confidence validation and complete
review handoff; the reviewer process, public execution and live qualification
remain pending.

## Route by need

| You need | Go to |
|---|---|
| choose a text-search tool, or the research level that fits | [operations/code-research-levels.md](operations/code-research-levels.md) |
| find where something is implemented or documented, in one search | `mycel search` — [runbook](tools/mycel.md) |
| an answer to "how/where/why" about a codebase | [operations/code-research.md](operations/code-research.md) (level 2) |
| durable multi-angle task context (an artifact) | [operations/deep-research.md](operations/deep-research.md) (level 3) |
| start or continue an in-depth review of a large pull request: find its next issues, review new commits, verify the author's fixes, weigh the author's replies | [operations/pr-deep-review.md](operations/pr-deep-review.md) — state file per pull request, ranked areas, verified findings queued for the human reviewer; never posts. Named run limits: [operations/stints.md](operations/stints.md) |
| go through the owner's unresolved comments in Linear: make the change a comment recommends, answer what it asks, or only list them | [operations/linear-resolve.md](operations/linear-resolve.md) — reads every open thread of the Sylvan Stack workspace, changes the original then its Linear copy, and settles each comment with the user in the session; posts `Resolved. Resolution: …` in Linear only after the user says `Resolved` |
| list the open questions and pending decisions that wait for the owner in Linear, so they can be answered in the session and not by commenting in Linear | [operations/linear-open-questions.md](operations/linear-open-questions.md) — collects the open rows of the specifications' Decisions tables, the issues that ask the owner to decide and the questions agents asked in comments, gives one numbered list in the session, and writes each answer the user gives there to the place its question is recorded in |
| take the next task of a Saga, Arc or Beat ("continue working on tasks"), stop or finish one, or plan new work as a Saga | [operations/sagas.md](operations/sagas.md) — Sagas, Arcs and Beats as files in the private corpus `~/Artifacts/sagas/`, copied one way to Linear projects and issues; an Arc's territory of folders and files; a hold file per Beat in work, released automatically when its agent is gone |
| see how far every Saga is and which agents work now (`/radar-stats`) | [operations/radar-stats.md](operations/radar-stats.md) — Done, In progress and Other in plan steps, the agents holding each Saga's Beats and their context, and the agents outside any Saga |
| see what each working agent did since its last progress, and which of them a signal calls for a review | [operations/agent-watch.md](operations/agent-watch.md) — the check from outside, every 5 minutes with no AI: time and tokens since the last tick, commit or owner's message, files outside git, repeated drafts, the agreed signals |
| make what needs the owner's attention now easy to find in Linear, then organize project navigation | [operations/linear-organize.md](operations/linear-organize.md) — publish a prominent attention entry with individual open questions, pending decisions, reviews, and next actions; then remove obsolete shortcuts |
| Mycel CLI syntax, flags, defaults | [tools/mycel.md](tools/mycel.md) |
| what Mycel 2 must do: its function, requirements and open decisions | [specs/README.md](specs/README.md) |
| what Mycel 1 actually did, with the place in its source | the inventories listed in [specs/README.md](specs/README.md) |
| how retrieval ranks / why a result won | [operations/retrieval.md](operations/retrieval.md) |
| administer Mycel indexing, freshness, embeddings, or configuration | [tools/mycel.md](tools/mycel.md) · [operations/embedding.md](operations/embedding.md) |
| integrate authored artifacts, code, and tests “according to Mycel” | [operations/authored-work-integration.md](operations/authored-work-integration.md) — coverage → ingest → edges → Detection → embeddings → verify |
| create, update, or install Mycel Skills for native Codex CLI and Claude Code CLI | [operations/create-skill.md](operations/create-skill.md) |
| work in a Euro-Office repository, or in Linear for Euro-Office | `~/Artifacts/euro-office/README.md` — where its corpora are, how the local clones relate to the upstream repositories, and the conventions of its Linear workspace |
| what a term means | [../arbol/GLOSSARY.md](../arbol/GLOSSARY.md) |
| the full catalog | [INDEX.md](INDEX.md) (operations) · [../arbol/INDEX.md](../arbol/INDEX.md) (product) |

*Rows are task shapes, never individual documents — if this table outgrows
one screen, a family is missing; add a family, not rows.*

## Rules that bite

- **Dependency direction:** Mycel must not depend on Arbol code or instructions. Never import, invoke, or prescribe Arbol code, repository scripts, `arbol-cli`, or an Arbol artifact as a required procedure. Mycel may read Arbol-owned databases, logs, and other data as inputs; data access is not a code/instructions dependency. Keep Mycel code and required process truth in Mycel.
- **Before creating or changing an artifact, read the README in its destination folder.** The category READMEs in `operations/`, `skills/` and `specs/` are the authoring contracts for format, placement, validation, and catalog updates. Their rules apply to descendants too (for example each `skills/<name>/` directory).
- **Retrieval is repo-scoped by CWD.** Each repository has its own corpus, and
  this folder is the corpus of repo `mycel` (how to work). From another
  repository's checkout use `mycel search --repo mycel "…"` to search it — or
  read the files above directly (absolute paths always work; `mycel` needs no
  daemon at all). `mycel repos` lists the repositories and which are enabled.
- **Outputs are artifacts**: resolve the repository's `artifact_root` in
  `~/.mycel/config.toml` before placing work. Organization member repositories
  use `~/Artifacts/<org-directory>/repos/<repo>/`; standalone repositories
  retain `~/Artifacts/<repo>/`. Organization-wide research stays under the
  organization root. In guides, legacy `~/Artifacts/<repo>/…` examples mean
  the resolved per-repository root, not a requirement to create a flat folder.
  The repository's `code_root` links its source checkout to that corpus; see
  [repository corpus binding](tools/mycel.md#repository-corpus-binding).
  Follow the [authoring guide](operations/source-refs-authoring.md) and update
  existing docs rather than adding siblings. Current source uses the shared
  organization-aware resolver; installed applications need the corresponding
  rebuilt executables. See the runbook for precedence and remaining limits.

## Working rules for every task

These hold for every agent on this Mac, whatever the task and the tool.

**Working with the owner**

- **Do the work yourself.** You have every permission: install software, start
  servers and launch agents, and run any command, checks and probes included,
  without asking. Do not hand the owner commands to run. Keep a backup of
  anything a change replaces.
- **Ask only what only the owner can decide**, and give a proposed answer, so
  that silence means "go". Settle everything else from code and documents. A
  specification of something that already exists says what it does; it does
  not end with questions about it.
- **Plain words.** Say what a thing is in everyday terms before naming it, and
  give one concrete example: a directory tree, a table with real names, one
  case followed step by step. Use the [glossary](../arbol/GLOSSARY.md)'s exact
  terms, and never one word for two things.
- **Smallest change.** Carry out a direction with the smallest change that does
  it. Your own additions go into the reply as suggestions, not into the work.
- **Reviews.** Read a specification in review yourself. Give the owner a
  verdict, the problems as a numbered list they can answer by number, the few
  consequences they would agree to, and at most a few sections worth their own
  read. Never ask them to read it all.
- **Names and numbers.** Use only names the owner gave to real things;
  describe anything else or use a placeholder such as `<root>`. Numbers the
  owner gives "for example" are not defaults: recommend a value with its basis
  and write it only after they agree.
- **Processes, not trackers.** Recurring multi-step work becomes a guide with a
  thin skill ([create-skill.md](operations/create-skill.md)). Never stand in
  for a missing feature with a hand-kept tracking document in Linear.
- **No native memory.** The memory of Claude Code and of Codex is switched off.
  What must outlast a session goes into a corpus: this Hub, a guide, a
  specification or a Saga's files.

**Repositories and publishing**

- **Push every commit** in a current Sylvan Stack repository or corpus, never
  in a `*_deprecated_v1` one. Before a push, check what it publishes for
  credentials, real account data, other people, employer or client context and
  server access details. Private work material never goes into a public
  corpus. Recorded results of tests, probes and benchmarks stay out of git;
  test code and fixtures are tracked.
- **Another agent may work in the same checkout.** Commit only your own files,
  never revert or tidy a change you did not make, and report drift you cannot
  explain.
- **Mycel 2 is worked as Beats of the Mycel Specs Implementation Saga**
  (`~/Artifacts/sagas/mycel-2-implementation/`). Change its code in
  `~/repos/sylvan-stack/mycel`, its specifications in `specs/` and its guides
  only within a Beat you hold. Write no run results into `research/`.
- **Version 1 is not run and not a source.** No `*_deprecated_v1` code, and no
  Mycel 1: neither the `mycel` command the rows above name nor the skills built
  on it (mycel-search, code-research, deep-research, corpus-admin,
  authored-work-integration). Search with grep and by reading files until
  Mycel 2 is installed.
- **A new Sylvan Stack repository** starts at version 1.0.0; its corpus is
  `~/Artifacts/<repo>`, published as `sylvan-stack/<repo>-artifacts`; add it to
  the "Sylvan Stack 2" table of every code README.
- **Leftovers.** Jira, Confluence, GitLab and Slack material in the Mycel and
  Arbol corpora is left over from an earlier project and may be removed.
  Telegram is the only integration that stays.

**Tools on this Mac**

- **Run `claude`, `codex` and other CLIs with the owner's terminal settings**:
  in the Terminal panel, or from a clean login shell,
  `env -i HOME="$HOME" USER="$USER" LOGNAME="$LOGNAME" TERM=xterm-256color /bin/zsh -l -i -c '<command>'`.
  The variables a session inherits from its app can make the CLI overwrite its
  own login. Say beforehand when a command writes a CLI's own state. Plain
  `claude` uses `~/.claude`; the alias `claude-zai` runs it on other models
  through `~/.claude/settings-zai.json`; never recreate `~/.claude-anthropic`.
- **Sign-in pages** open in the built-in browser pane. The owner types the
  credentials and approves; never enter them.
- **Linear.** Every comment an agent posts begins with `**Agent:**`. The two
  workspaces and what the connector cannot do are in the
  [Linear runbook](tools/linear.md).

**How this file reaches every agent.** Claude Code imports it from
`~/.claude/CLAUDE.md` at the start of every session. Codex gets a copy as
`developer_instructions` in `~/.codex/config.toml`, rewritten whenever this
file changes. Everything here costs context in every session: keep it short,
and put detail in the guide a row above points to.
