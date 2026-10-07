# Mycel Operations Catalog

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

### `research/` — evidence the specifications rest on
- [`v1-inventory-ingest-and-graph.md`](./research/v1-inventory-ingest-and-graph.md) — what the version 1 source does for the scan, chunking, identity, Source Refs, edges and detection, with Source Refs into the deprecated repository.
- [`v1-inventory-embedding-and-retrieval.md`](./research/v1-inventory-embedding-and-retrieval.md) — the same for embedding, the two indexes, the search algorithm, the reply and the grep replacement.
- [`v1-inventory-sync-settings-commands.md`](./research/v1-inventory-sync-settings-commands.md) — the same for the sync pass, the remote refresh, settings, the store's address, repository scope, every command and the summaries.
- [`v1-observations-2026-10.md`](./research/v1-observations-2026-10.md) — what the installed version 1 was seen doing on 6 and 7 October 2026.
- [`v1-probes-2026-10-07/`](./research/v1-probes-2026-10-07/README.md) — the scripts behind the inventory statements that were run and not only read.

### `operations/` — Mycel Operations: frontend-agnostic process descriptions
What must happen, in Mycel vocabulary — the invariant behind every invocation surface (skills, CLI agents, humans).
- [`OVERVIEW.md`](./operations/OVERVIEW.md) — the readable one-page summary of all operations (for humans; agents use the Hub).
- [`code-research-levels.md`](./operations/code-research-levels.md) — better-grep → code-research → deep-research: which tool when.
- [`code-research.md`](./operations/code-research.md) — the level-2 loop. Skills are thin dispatchers pointing here.
- [`deep-research.md`](./operations/deep-research.md) — the level-3 process: inputs, angles, output contract, quality bar.
- [`embedding.md`](./operations/embedding.md) — profiles, the identity-header recipe, iron rules, compounding habits.
- [`retrieval.md`](./operations/retrieval.md) — the read path: route decision, doc bridge, noise down-weights, via/documented_in annotations.
- [`code-map.md`](./operations/code-map.md) — the mechanical per-repo overview artifact and its `generated: true` semantics.
- [`knowledge-model.md`](./operations/knowledge-model.md) — the value reference: in-band declarations (`role:` / `status: heartwood` / `generated:` / `sources:`), chunk roles/states, Derivation kinds/policies, Detection reasons, Drift lifecycle.
- [`authored-work-integration.md`](./operations/authored-work-integration.md) — completion loop for new artifacts, implementation, and tests: corpus coverage, chunk ingest, authority edges, Detection, embeddings, and retrieval verification.
- [`create-skill.md`](./operations/create-skill.md) — create one provider-agnostic Mycel Skill and its thin provider adapters; covers native Codex CLI and Claude Code CLI discovery, symlinks, and invocation policy.
- [`pr-deep-review.md`](./operations/pr-deep-review.md) — multi-session review of a large pull request: sync with the head, ranked areas, verified and independently challenged findings, a queue of drafted comments for the human reviewer, commands for the recurring steps (next, commits, verify, replies, check, summary, status), stop criteria on findings, time, tokens and coverage; never posts.
- [`pr-deep-review-reference.md`](./operations/pr-deep-review-reference.md) — its lookup companion: `state.json` schema, area and finding statuses, templates for the reviewer's page, finding card and run report, stop-criteria measures and kinds, reading token spend, commands for reading a GitHub pull request.
- [`stints.md`](./operations/stints.md) — named sets of stop criteria for a run: the defined stints, how a run resolves its stint and limits, how to add or change one.
- [`source-refs-authoring.md`](./operations/source-refs-authoring.md) — author durable provenance and section-level Source Refs without relying on instructions from another corpus.

### `tools/` — technical manuals for the client-agnostic CLIs
One [Runbook](../arbol/GLOSSARY.md#runbook) per [Tool](../arbol/GLOSSARY.md#tool).
- [`mycel.md`](./tools/mycel.md) — knowledge CLI: search, sync, embed, status, drifts, derive, repos, raptor; repository corpus binding.

### `system-instructions/` — prompt files the `mycel` executable reads
Not process guides: `mycel raptor regen|build` loads both files from this folder and stops with an error when either is missing or empty.
- [`raptor-summary.md`](./system-instructions/raptor-summary.md) — the system prompt for RAPTOR cluster summaries.
- [`raptor-request.md.tmpl`](./system-instructions/raptor-request.md.tmpl) — the request template; `$sections` receives the clustered sections.

### `skills/` — Mycel Skill provider adapters
Shared activation contracts and thin Hub dispatchers for native Codex CLI and Claude Code CLI. Canonical sources are linked into `~/.agents/skills/` (Codex) and `~/.claude/skills/` (Claude). See [authoring rules](skills/README.md) and the [creation guide](operations/create-skill.md).

- [`authored-work-integration`](./skills/authored-work-integration/SKILL.md)
- [`code-research`](./skills/code-research/SKILL.md)
- [`corpus-admin`](./skills/corpus-admin/SKILL.md)
- [`create-mycel-skill`](./skills/create-mycel-skill/SKILL.md)
- [`deep-research`](./skills/deep-research/SKILL.md)
- [`mycel-search`](./skills/mycel-search/SKILL.md)
- [`pr-deep-review`](./skills/pr-deep-review/SKILL.md)

The active catalog contains 8 Mycel skills for both providers. Personal and
third-party skills remain outside this catalog.

## Conventions

- Every artifact goes into a chapter folder, never directly into the corpus root. `README.md`, `INDEX.md` and a `GLOSSARY.md` are the exceptions.
- List a chapter here when it is created.
- Tasks are tracked in Linear, not in this corpus: project [Mycel](https://linear.app/sylvan-stack/project/mycel-01b43a09de20) in the Sylvan Stack workspace. Specifications are copied there as documents; `.linear.json` maps each file to its copy. The files here are the originals.
