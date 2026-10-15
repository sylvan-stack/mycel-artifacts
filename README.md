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
| take the next task of a Saga, Arc or Beat ("continue working on tasks"), stop or finish one, or plan new work as a Saga | [operations/sagas.md](operations/sagas.md) — Sagas as Linear projects, Arcs as parent issues with a territory of folders and files, Beats as their sub-issues; a hold file per Beat in work, released automatically when its agent is gone |
| make what needs the owner's attention now easy to find in Linear, then organize project navigation | [operations/linear-organize.md](operations/linear-organize.md) — publish a prominent attention entry with individual open questions, pending decisions, reviews, and next actions; then remove obsolete shortcuts |
| Mycel CLI syntax, flags, defaults | [tools/mycel.md](tools/mycel.md) |
| what Mycel 2 must do: its function, requirements and open decisions | [specs/README.md](specs/README.md) |
| what Mycel 1 actually did, with the place in its source | the inventories listed in [specs/README.md](specs/README.md) |
| how retrieval ranks / why a result won | [operations/retrieval.md](operations/retrieval.md) |
| administer Mycel indexing, freshness, embeddings, or configuration | [tools/mycel.md](tools/mycel.md) · [operations/embedding.md](operations/embedding.md) |
| integrate authored artifacts, code, and tests “according to Mycel” | [operations/authored-work-integration.md](operations/authored-work-integration.md) — coverage → ingest → edges → Detection → embeddings → verify |
| create, update, or install Mycel Skills for native Codex CLI and Claude Code CLI | [operations/create-skill.md](operations/create-skill.md) |
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
