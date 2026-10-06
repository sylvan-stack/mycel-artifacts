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
operations, tool runbooks and skills. The **product** — Arbol's
specifications and the shared glossary — lives one corpus over in
`~/Artifacts/arbol/` ([its catalog](../arbol/INDEX.md)).

The engine guides and the `mycel` runbook describe Mycel 1, the executable
installed today. Mycel 2 is a rewrite with no implementation yet. The complete
Mycel 1 corpus, including the chapters that were not carried over, is frozen
at `~/Artifacts/mycel_deprecated_v1/`.

## Route by need

| You need | Go to |
|---|---|
| choose a text-search tool, or the research level that fits | [operations/code-research-levels.md](operations/code-research-levels.md) |
| find where something is implemented or documented, in one search | `mycel search` — [runbook](tools/mycel.md) |
| an answer to "how/where/why" about a codebase | [operations/code-research.md](operations/code-research.md) (level 2) |
| durable multi-angle task context (an artifact) | [operations/deep-research.md](operations/deep-research.md) (level 3) |
| start or continue an in-depth review of a large pull request: find its next issues, review new commits, verify the author's fixes, weigh the author's replies | [operations/pr-deep-review.md](operations/pr-deep-review.md) — state file per pull request, ranked areas, verified findings queued for the human reviewer; never posts. Named run limits: [operations/stints.md](operations/stints.md) |
| Mycel CLI syntax, flags, defaults | [tools/mycel.md](tools/mycel.md) |
| how retrieval ranks / why a result won | [operations/retrieval.md](operations/retrieval.md) |
| administer Mycel indexing, freshness, embeddings, or configuration | [tools/mycel.md](tools/mycel.md) · [operations/embedding.md](operations/embedding.md) |
| investigate Reservble places-api Syrve integration logs | [operations/places-api-logs.md](operations/places-api-logs.md) — verified read-only SFTP and event correlation |
| integrate authored artifacts, code, and tests “according to Mycel” | [operations/authored-work-integration.md](operations/authored-work-integration.md) — coverage → ingest → edges → Detection → embeddings → verify |
| create, update, or install Mycel Skills for native Codex CLI and Claude Code CLI | [operations/create-skill.md](operations/create-skill.md) |
| what a term means | [../arbol/GLOSSARY.md](../arbol/GLOSSARY.md) |
| the full catalog | [INDEX.md](INDEX.md) (operations) · [../arbol/INDEX.md](../arbol/INDEX.md) (product) |

*Rows are task shapes, never individual documents — if this table outgrows
one screen, a family is missing; add a family, not rows.*

## Rules that bite

- **Dependency direction:** Mycel must not depend on Arbol code or instructions. Never import, invoke, or prescribe Arbol code, repository scripts, `arbol-cli`, or an Arbol artifact as a required procedure. Mycel may read Arbol-owned databases, logs, and other data as inputs; data access is not a code/instructions dependency. Keep Mycel code and required process truth in Mycel.
- **Before creating or changing an artifact, read the README in its destination folder.** The category READMEs in `operations/` and `skills/` are the authoring contracts for format, placement, validation, and catalog updates. Their rules apply to descendants too (for example each `skills/<name>/` directory).
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
