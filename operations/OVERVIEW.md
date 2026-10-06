---
role: authored
---
# Mycel Process Guides — the readable summary

One page to (re)load the whole mental model. Each section is two sentences of
*what and why*; the linked guide holds the process. Agents route via the
[Instructions Hub](../README.md); this overview is for humans.

## The write side — how knowledge gets in

- **[Embedding](embedding.md)** — chunks become vectors with an identity
  header (path + symbol first), one [Embedder
  Profile](../../arbol/GLOSSARY.md#embedder-profile) per repo. The profile is
  the interlock: a repository on the `local` profile embeds on-device (the
  [Embedding Provider](../../arbol/GLOSSARY.md#embedding-provider) app),
  never via an external API.
- **[Code Map](code-map.md)** — a mechanical per-repo overview
  (`generated/code-map.md`) rebuilt from chunks on every code-changing sync:
  no LLM, gives overview queries a landing place and every file a
  `documented_in` pointer.
- **Sync** — one mechanical pass (docs refresh → code ingest → overlays →
  embed delta): Arbol's mycel client runs it on file events (Mycel itself has
  no daemon); `mycel sync` runs it as a per-task command; `mycel search` runs
  the delta automatically when the source changed (fresh-on-read).
- **[Authored-work integration](authored-work-integration.md)** — a change is
  “according to Mycel” only after artifacts, code, and tests are in enabled
  corpora, ingested as chunks, connected by real authority/coupling edges,
  checked by Detection, embedded, and verified through retrieval.

## The read side — how knowledge comes out

- **[Code Retrieval](retrieval.md)** — unified search over code + docs +
  summaries: natural-language queries rank by cosine with doc-bridges
  injecting cited code; identifier queries use balanced RRF; tests/codegen
  are down-weighted; docs must clearly beat code to displace it.
- **[Research levels](code-research-levels.md)** — `better-grep` (exact +
  meaning tail) → [code-research](code-research.md) (question → cited answer)
  → [deep research](deep-research.md) (task → durable artifact).

## Large pull-request reviews

- **[Deep Review of a Large Pull Request](pr-deep-review.md)** — a review too
  big for one pass runs across sessions from a per-pull-request state file:
  sync with the head, rank the changed areas, investigate them in order, and
  verify each issue before it reaches the reviewer. The agent queues findings
  with a drafted comment and file:line; the human reviewer decides what is
  posted.
- **[Stints](stints.md)** — a stint is a named set of stop criteria for one
  run: how much work is asked for and how much may be spent, as soft or hard
  minimums and maximums. Defined once, named in a request, overridden limit
  by limit; separate from which model does the work.

## How it compounds

Retrieval gets smarter through documents, not tuning: jargon the code never
spells out earns a [GLOSSARY](../../arbol/GLOSSARY.md#source-ref) bridge entry;
research worth keeping is persisted with Source Refs and update-don't-
duplicate; superseded truth freezes as [Heartwood](../../arbol/GLOSSARY.md#heartwood).
[Detection](../../arbol/GLOSSARY.md#detection)
watches every edge so drift surfaces instead of rotting. The machinery behind
all of this — every declaration, role, edge kind, and staleness reason, with
its exact semantics — is enumerated in the
[Knowledge Model](knowledge-model.md) reference.

## Where each piece runs

Mycel is **per-task CLI first** (`mycel …` — works in VS Code with zero
daemons; the severance acceptance test proves it). Arbol adds the
conveniences: the resident watcher, Seqoya Lab as the settings window, and
the completion provider for RAPTOR generation.

## Mycel Skill dispatchers

[Mycel Skills](../../arbol/GLOSSARY.md#mycel-skill) are provider-agnostic
activation contracts implemented by thin provider adapters. Follow the
[creation guide](create-skill.md) to add every available adapter from one shared
trigger contract; native Codex CLI and Claude Code CLI are supported. Universe
is deprecated. Both CLIs link to canonical sources; explicit-only invocation
policy is represented in each provider's supported metadata.

Distinct task shapes have thin skills
routing through the Hub: `/code-research`, `/deep-research`,
`/mycel-search`, `/corpus-admin`, `/authored-work-integration`,
`/pr-deep-review`, `/create-mycel-skill`, `/places-api-logs`.
Skills carry only *when to trigger*; the process always lives here, in Mycel.

<!-- sources:
mycel:operations/embedding.md
mycel:operations/code-map.md
mycel:operations/retrieval.md
mycel:operations/code-research-levels.md
mycel:operations/code-research.md
mycel:operations/deep-research.md
mycel:operations/knowledge-model.md
mycel:operations/authored-work-integration.md
-->

The [skill catalog](../INDEX.md#skills--mycel-skill-provider-adapters) lists all
installed contracts, including authored-work integration and
[Places API log investigation](places-api-logs.md). Explicit invocation is
`$<name>` in Codex and `/<name>` in Claude.
