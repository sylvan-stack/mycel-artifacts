# Mycel Operations Catalog

> **Start at the [Instructions Hub](./README.md)** — the routing table. This
> INDEX is the full catalog of the Mycel corpus (`~/Artifacts/mycel/`, repo
> `mycel`, its own git repo): everything about **how to work**. The product —
> Arbol's specifications — is one corpus over in
> [`~/Artifacts/arbol/`](../arbol/INDEX.md). Shared vocabulary:
> [GLOSSARY](../arbol/GLOSSARY.md).

Everything here passes the **VS Code Test**: usable without Arbol installed.

## Chapters

### `operations/` — Mycel Operations: frontend-agnostic process descriptions
What must happen, in Mycel vocabulary — the invariant behind every invocation surface (skills, CLI agents, Arbol RPCs).
- [`OVERVIEW.md`](./operations/OVERVIEW.md) — the readable one-page summary of all operations (for humans; agents use the Hub).
- [`code-research-levels.md`](./operations/code-research-levels.md) — better-grep → code-research → deep-research: which tool when.
- [`code-research.md`](./operations/code-research.md) — the level-2 loop. Skills are thin dispatchers pointing here.
- [`deep-research.md`](./operations/deep-research.md) — the level-3 process: inputs, angles, output contract, quality bar.
- [`embedding.md`](./operations/embedding.md) — profiles/interlock, the identity-header recipe, iron rules, compounding habits.
- [`retrieval.md`](./operations/retrieval.md) — the read path: route decision, doc bridge, noise down-weights, via/documented_in annotations.
- [`code-map.md`](./operations/code-map.md) — the mechanical per-repo overview artifact and its `generated: true` semantics.
- [`knowledge-model.md`](./operations/knowledge-model.md) — the value reference: in-band declarations (`role:` / `status: heartwood` / `generated:` / `sources:`), chunk roles/states, Derivation kinds/policies, Detection reasons, Drift lifecycle.
- [`authored-work-integration.md`](./operations/authored-work-integration.md) — completion loop for new artifacts, implementation, and tests: corpus coverage, chunk ingest, authority edges, Detection, embeddings, and retrieval verification.
- [`create-skill.md`](./operations/create-skill.md) — create one provider-agnostic Mycel Skill and its thin provider adapters; covers native Codex CLI and Claude Code CLI discovery, symlinks, and invocation policy.
- [`pr-deep-review.md`](./operations/pr-deep-review.md) — multi-session review of a large pull request: sync with the head, ranked areas, verified and independently challenged findings, a queue of drafted comments for the human reviewer, commands for the recurring steps (next, commits, verify, replies, check, summary, status), stop criteria on findings, time, tokens and coverage; never posts.
- [`pr-deep-review-reference.md`](./operations/pr-deep-review-reference.md) — its lookup companion: `state.json` schema, area and finding statuses, templates for the reviewer's page, finding card and run report, stop-criteria measures and kinds, reading token spend, commands for reading a GitHub pull request.
- [`stints.md`](./operations/stints.md) — named sets of stop criteria for a run: the defined stints, how a run resolves its stint and limits, how to add or change one.
- [`source-refs-authoring.md`](./operations/source-refs-authoring.md) — author durable provenance and section-level Source Refs without relying on instructions from another corpus.
- [`places-api-logs.md`](./operations/places-api-logs.md) — Reservble Syrve production-log access and investigation through read-only SFTP.

### `tools/` — technical manuals for the client-agnostic CLIs
One [Runbook](../arbol/GLOSSARY.md#runbook) per [Tool](../arbol/GLOSSARY.md#tool).
- [`mycel.md`](./tools/mycel.md) — knowledge CLI: search, sync, embed, status, drifts, derive, overlay, repos, raptor; repository corpus binding.

### `system-instructions/` — prompt files the `mycel` executable reads
Not process guides: `mycel raptor regen|build` loads both files from this folder and stops with an error when either is missing or empty.
- [`raptor-summary.md`](./system-instructions/raptor-summary.md) — the system prompt for RAPTOR cluster summaries.
- [`raptor-request.md.tmpl`](./system-instructions/raptor-request.md.tmpl) — the request template; `$sections` receives the clustered sections.

### `skills/` — Mycel Skill provider adapters
Shared activation contracts and thin Hub dispatchers for native Codex CLI and Claude Code CLI. Canonical sources are linked into `~/.agents/skills/` (Codex) and `~/.claude/skills/` (Claude). Universe is deprecated. See [authoring rules](skills/README.md) and the [creation guide](operations/create-skill.md).

- [`authored-work-integration`](./skills/authored-work-integration/SKILL.md)
- [`code-research`](./skills/code-research/SKILL.md)
- [`corpus-admin`](./skills/corpus-admin/SKILL.md)
- [`create-mycel-skill`](./skills/create-mycel-skill/SKILL.md)
- [`deep-research`](./skills/deep-research/SKILL.md)
- [`mycel-search`](./skills/mycel-search/SKILL.md)
- [`places-api-logs`](./skills/places-api-logs/SKILL.md)
- [`pr-deep-review`](./skills/pr-deep-review/SKILL.md)

The active catalog contains 8 Mycel skills for both providers. Personal and
third-party skills remain outside this catalog.
