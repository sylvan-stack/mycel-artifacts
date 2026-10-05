---
role: authored
---
# Mycel — Instructions Hub

*(Human-readable tour of everything below: [operations/OVERVIEW.md](operations/OVERVIEW.md).)*

The **one address every consumer needs to know**: Claude Code and native Codex CLI skills,
agents, Arbol's own Chat Sessions, and humans all start here. Consumers point
at this file and never change; documents move freely underneath because only
this router tracks where they live.

Everything about **how to work** lives in this corpus (`~/Artifacts/mycel/`):
operations, tools, blueprints, chains, skills. The **product** it documents —
Arbol's architecture, plans, glossary — lives one corpus over in
`~/Artifacts/arbol_deprecated_v1/` ([its catalog](../arbol_deprecated_v1/INDEX.md)).

## Retired Example organization workflow

The Example organization Jira/Confluence/GitLab skill suite was uninstalled on
2026-09-29. Its ticket preparation, planning, spike, scouting, review, and
external-mirror procedures remain for historical reference. Do not apply
Example organization endpoints, compliance rules, or infrastructure defaults to
current projects. These historical routes do not imply installed skills.

## Route by need

| You need | Go to |
|---|---|
| choose code/text search tools | Follow the provider source-investigation guide below and effective runtime rules; [better-grep runbook](tools/better-grep.md) |
| give an agent provider-specific code-search and source-reading rules | [Claude guide](operations/claude-source-investigation.md) · [Codex guide](operations/codex-source-investigation.md) |
| an answer to "how/where/why" about a codebase | [operations/code-research.md](operations/code-research.md) (level 3) |
| scout a codebase for ticket objectives | [scout-codebase](blueprints/scout-codebase.md) — shallow reconnaissance, not verified conclusions |
| durable multi-angle task context (an artifact) | [deep-research](blueprints/deep-research.md) — a [Blueprint](../arbol/GLOSSARY.md#blueprint) |
| start, resume, or hand off troubleshooting for a difficult implementation or bug-fix issue | [operations/troubleshooting.md](operations/troubleshooting.md) — persistent sessions, findings, failed directions, and a copyable continuation prompt |
| start or continue an in-depth review of a large pull request: find its next issues, review new commits, verify the author's fixes, weigh the author's replies | [operations/pr-deep-review.md](operations/pr-deep-review.md) — state file per pull request, ranked areas, verified findings queued for the human reviewer; never posts. Named run limits: [operations/stints.md](operations/stints.md) |
| continue a recurring subject in a new Chat Session (Living Topic) | [operations/living-topics.md](operations/living-topics.md) — topic folder + Chat Note hydration + incremental write-back |
| run a blueprint detached (typed function → a Delegate) | `blueprint run <name> --input k=v` — [runbook](tools/blueprint.md) |
| run one recipe-pinned agent session (the substrate) | `infer run "…" --recipe NAME` — [runbook](tools/infer.md) |
| ticket → deliverable: review an MR / implementation plan / spike doc | [code-review chain](chains/code-review.md) (detached, verified) · [code-review](blueprints/code-review.md) (in-session) · [implementation-plan](blueprints/implementation-plan.md) · [spike-doc](blueprints/spike-doc.md) |
| start a ticket: workspace pipeline (full or prep-only) | [start-new-ticket](chains/start-new-ticket.md) · [prepare-ticket](chains/prepare-ticket.md) — Blueprint Chains |
| drive a ticket through Jira/git: subtasks, transitions, branches, MRs, compliance | [operations/ticket-workflow.md](operations/ticket-workflow.md) — the ticket-workflow skill |
| which research level fits | [operations/code-research-levels.md](operations/code-research-levels.md) |
| Mycel CLI syntax, flags, exit codes | [tools/mycel.md](tools/mycel.md) |
| pull external context (ticket / page / MR), or create/update Confluence pages | [operations/external-mirrors.md](operations/external-mirrors.md) — `mycel mirror fetch` |
| inspect branch context or update the current branch with its base | [operations/branch-checkout.md](operations/branch-checkout.md) — standard checkout, preserve edits, explicit approval before switching |
| how retrieval ranks / why a result won | [operations/retrieval.md](operations/retrieval.md) |
| administer Mycel indexing, freshness, embeddings, or configuration | [tools/mycel.md](tools/mycel.md) · [operations/embedding.md](operations/embedding.md) |
| investigate Reservble places-api Syrve integration logs | [operations/places-api-logs.md](operations/places-api-logs.md) — verified read-only SFTP and event correlation |
| inspect recent tool-call logs or investigate a Chat Session | [operations/tool-call-observability.md](operations/tool-call-observability.md) — database/log evidence for failures, result quality, telemetry, and performance |
| run a Turn Composition test session: choose a catalog request, inspect the newest Turn Inspector evidence, and finalize validation findings | [operations/turn-composition-testing.md](operations/turn-composition-testing.md) — the `/turn-test [case-id]` workflow |
| integrate authored artifacts, code, and tests “according to Mycel” | [operations/authored-work-integration.md](operations/authored-work-integration.md) — coverage → ingest → edges → Detection → embeddings → verify |
| user message mentions **iPad Dashboard** or invokes **/ipad**: verify the incoming mailbox identity and return a correlated reply | [operations/ipad-dashboard.md](operations/ipad-dashboard.md) — mention loads guidance, not execution authority |
| create, update, or install Mycel Skills for native Codex CLI and Claude Code CLI | [operations/create-skill.md](operations/create-skill.md) |
| what a term means | [../arbol/GLOSSARY.md](../arbol/GLOSSARY.md) |
| the full catalog | [INDEX.md](INDEX.md) (operations) · [../arbol_deprecated_v1/INDEX.md](../arbol_deprecated_v1/INDEX.md) (product) |

*Rows are task shapes, never individual documents — if this table outgrows
one screen, a family is missing; add a family, not rows.*

## Rules that bite

- **Dependency direction:** Mycel must not depend on Arbol code or instructions. Never import, invoke, or prescribe Arbol code, repository scripts, `arbol-cli`, or an Arbol artifact as a required procedure. Mycel may read Arbol-owned databases, logs, and other data as inputs; data access is not a code/instructions dependency. Keep Mycel code and required process truth in Mycel.
- **Before creating or changing an artifact, read the README in its destination folder.** The category READMEs in `operations/`, `blueprints/`, `chains/`, `tools/`, and `skills/` are the authoring contracts for format, placement, validation, and catalog updates. Their rules apply to descendants too (for example `operations/archive/` and each `skills/<name>/` directory).
- **Retrieval is repo-scoped by CWD.** Knowledge lives in two corpora: repo
  `mycel` (this folder — how to work: operations, tools, blueprints, chains,
  skills) and repo `Arbol` (`~/Artifacts/Arbol` — the product: architecture,
  plans, glossary). From a container-repo worktree use `mycel search --repo mycel
  "…"` (or `--repo Arbol`) — or read the files above directly (absolute paths
  always work; `mycel` needs no daemon at all).
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
- **Blueprints run detached** via `blueprint run <name> --input k=v` — or any
  agent runs one manually: bind the inputs, follow the Process, self-check
  `done_when` before reporting done.
- **Recipes never inherit from your chat session.** When you (an agent)
  launch a blueprint or chain, pass `--recipe` ONLY if the user named a
  specific recipe. Your own session's model is not a caller recipe — omit
  the flag and let resolution run pin → caller → default. (Manual/inline
  execution is the one exception by nature: there, your session IS the
  brain.)
