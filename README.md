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

Mycel 2 is installed as `~/.local/bin/mycel`, with its independent launcher
and working Build `1` (package version 2.0.0). The [runbook](tools/mycel.md)
routes to the current command, settings, search, ingest, embedding, evidence,
classification and Build guides. Search returns schema 3; complete ingest,
scoped embedding, summaries and exact chunk reading are implemented. Live
qualification remains bound to the source and Build that actually passed it;
installation does not supply new provider proof.

## Route by need

| You need | Go to |
|---|---|
| choose a text-search tool, or the research level that fits | [operations/code-research-levels.md](operations/code-research-levels.md) |
| find where something is implemented or documented, in one search | `mycel search` — [runbook](tools/mycel.md) |
| an answer to "how/where/why" about a codebase | [operations/code-research.md](operations/code-research.md) (level 2) |
| durable multi-angle task context (an artifact) | [operations/deep-research.md](operations/deep-research.md) (level 3) |
| decide which tests are worth adding, running, retaining or removing | [operations/test-strategy.md](operations/test-strategy.md) — top-tier edge cases and regressions may be used during implementation; mid-tier testing requires a separate explicit owner request; low-tier tests are removed |
| take initiative on a broad goal: own the plan, decisions and experiments while keeping the owner's involvement optional until their input is needed | [operations/initiative.md](operations/initiative.md) — applies to the delegated goal and its follow-ups; narrowly assigned tasks and subagent deliverables retain their scope |
| start or continue an in-depth review of a large pull request: find its next issues, review new commits, verify the author's fixes, weigh the author's replies | [operations/pr-deep-review.md](operations/pr-deep-review.md) — state file per pull request, ranked areas, verified findings queued for the human reviewer; never posts. Named run limits: [operations/stints.md](operations/stints.md) |
| go through the owner's unresolved comments in Linear: make the change a comment recommends, answer what it asks, or only list them | [operations/linear-resolve.md](operations/linear-resolve.md) — reads every open thread of the Linear workspace, changes the original then its Linear copy, and settles each comment with the user in the session; posts `Resolved. Resolution: …` in Linear only after the user says `Resolved` |
| list the open questions and pending decisions that wait for the owner in Linear, so they can be answered in the session and not by commenting in Linear | [operations/linear-open-questions.md](operations/linear-open-questions.md) — collects the open rows of the specifications' Decisions tables, the issues that ask the owner to decide and the questions agents asked in comments, gives one numbered list in the session, and writes each answer the user gives there to the place its question is recorded in |
| take the next task of a Saga, Arc or Beat ("continue working on tasks"), stop or finish one, or plan new work as a Saga | [operations/sagas.md](operations/sagas.md) — Sagas, Arcs and Beats as files in the private corpus `~/Artifacts/sagas/`, copied one way to Linear projects and issues; an Arc's territory of folders and files; a hold file per Beat in work, released automatically when its agent is gone |
| see how far every Saga is and which agents work on them now (`/radar-stats`) | [operations/radar-stats.md](operations/radar-stats.md) — Done, In progress and Other in plan steps, and the agents holding each Saga's Beats and their context |
| see what each working agent did since its last progress, and which of them a signal calls for a review | [operations/agent-watch.md](operations/agent-watch.md) — the check from outside, every 5 minutes with no AI: time and tokens since the last tick, commit or owner's message, files outside git, repeated drafts, the agreed signals |
| make what needs the owner's attention now easy to find in Linear, then organize project navigation | [operations/linear-organize.md](operations/linear-organize.md) — publish a prominent attention entry with individual open questions, pending decisions, reviews, and next actions; then remove obsolete shortcuts |
| record, change, replace or withdraw an Owner Goal from the owner's own words, answer which goals apply to something, or check that the goals do not contradict each other (`/owner-goals`) | [operations/owner-goals.md](operations/owner-goals.md) — the goals corpus `~/Artifacts/goals`, changed only through the `goals` command; only the owner puts a goal in force |
| learn something at the depth the owner's Nex Knowledge Map says is missing (`/colab "prompt"`), pitch the explanations of other work at the owner's level (`(use colab)`), or study toward a goal in learn mode, a whole session of learning and no other work (`/learn`); each starts only when the owner calls it by name, and a session in learn mode stays in it until the owner leaves it | [operations/nex-colab.md](operations/nex-colab.md) — the map is data in the private corpus `~/Artifacts/colab/`, assessed, written and pushed after each reply |
| Mycel CLI syntax, flags, defaults | [tools/mycel.md](tools/mycel.md) |
| what Mycel 2 must do: its function, requirements and open decisions | [specs/README.md](specs/README.md) |
| what Mycel 1 actually did, with the place in its source | the inventories listed in [specs/README.md](specs/README.md) |
| how retrieval ranks / why a result won | [operations/retrieval.md](operations/retrieval.md) |
| administer Mycel indexing, freshness, embeddings, or configuration | [tools/mycel.md](tools/mycel.md) · [operations/embedding.md](operations/embedding.md) |
| bring an existing repository under Origin Coverage, find what lacks an Origin, or justify changed code and documents | [operations/justification.md](operations/justification.md) — normalize rows, preserve declared claims, recover gaps and inspect the audit; Origin reports are optional |
| integrate authored artifacts, code, and tests “according to Mycel” | [operations/authored-work-integration.md](operations/authored-work-integration.md) — coverage → ingest → edges → Detection → embeddings → verify |
| create, update, or install Mycel Skills for native Codex CLI and Claude Code CLI | [operations/create-skill.md](operations/create-skill.md) |
| work in a Euro-Office repository | `~/Artifacts/euro-office/README.md` — where its corpora are, how the local clones relate to the upstream repositories, and what became of its Linear workspace |
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
  daemon at all). `mycel repos` lists configured repositories and their enabled
  state. From a named work area such as Beaver Workspace pass `--repo <name>`
  explicitly: without it, scope can cover the whole organization (MYC-1.4).
- **Outputs are artifacts**: resolve the repository's `artifact_root` in
  `~/.mycel/config.toml` before placing work. Organization member repositories
  use `~/Artifacts/<org-directory>/repos/<repo>/`; standalone repositories
  retain `~/Artifacts/<repo>/`. Organization-wide research stays under the
  organization root. In guides, legacy `~/Artifacts/<repo>/…` examples mean
  the resolved per-repository root, not a requirement to create a flat folder.
  The repository's `code_root` links its source checkout to that corpus; see
  [repository corpus binding](tools/mycel.md#repository-corpus-binding).
  Follow the [authoring guide](operations/source-refs-authoring.md) and update
  existing docs rather than adding siblings. The [settings guide](tools/mycel-2-settings.md)
  owns current root resolution, clone locations and explicit overrides.

## Working rules for every task

These hold for every agent on this Mac, whatever the task and the tool.

**Working with the owner**

- **Testing in Sylvan Stack.** Follow [Test Strategy](operations/test-strategy.md) and the repository's `TESTS.md` inventory: only individually justified top-tier edge cases and specific bugfix regressions may be written or selectively run during implementation. Mid-tier retention requires consequential risk, execution-dependent information, distinct coverage, an independent observation and proportionate cost; ordinary functional coverage is insufficient. Keep retained mid-tier source uncommented in its own folder at the owner's request; write or run it only in a separate testing task explicitly requested by the owner. Do not re-comment it after a run. Do not write low-tier tests; remove them. Unclassified retained tests are provisionally mid tier, not approved for quality. No default suite at entry, after edits, before completion or after merge. **A Build runs the whole top tier and nothing else; the mid tier runs only when the owner asks for a mid-tier run, never because an agent decides to.** Full qualification must refuse incomplete inventories or missing test sources; a top-only run is not full qualification. This supersedes older automatic-test instructions in repository and Saga guides; report tests not run honestly.

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
  describe anything else or use a placeholder such as `<root>`. Name agent
  work areas with their full animal name, such as **Beaver Workspace** or
  **Owl Workspace**, every time. Numbers the owner gives "for example" are
  not defaults: recommend a value with its basis
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
- **Version 1 is not run and not a source.** Never run Mycel 1 or read
  `*_deprecated_v1` code as current implementation. The installed `mycel` is
  Mycel 2.
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
- **Long work is split and recorded.** Split work that may run more than 5
  minutes into the smallest steps its tool allows (one repository, one path,
  one batch) and run them one after another. Start each step that may still
  run more than 5 minutes as `bgjob run --name "<what it does, in plain words>"
  [--log <file> | --progress-cmd <command>] -- <command>`, or attach one already
  running with `bgjob watch --pid <pid> --name "…"`. The menu bar then shows it
  under the chat that started it, with elapsed time and progress, and macOS
  notifies when it ends; see [background jobs](operations/background-jobs.md).
- **Sign-in pages** open in the built-in browser pane. The owner types the
  credentials and approves; never enter them.
- **Linear.** Every comment an agent posts begins with `**Agent:**`. The
  workspace, how it is reached and what the connector cannot do are in the
  [Linear runbook](tools/linear.md). On task completion, preserve its ID in
  `~/Artifacts/sagas/completed-linear-tasks/` (weekly files, at most 100 tasks
  each), then delete the issue instead
  of setting it to Done; follow [Complete Linear Tasks](operations/linear-completion.md).

**How this file reaches every agent.** Claude Code imports it from
`~/.claude/CLAUDE.md` at the start of every session. Codex gets a copy as
`developer_instructions` in `~/.codex/config.toml`, rewritten whenever this
file changes. Everything here costs context in every session: keep it short,
and put detail in the guide a row above points to.
