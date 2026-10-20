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
  Profile](../../arbol/GLOSSARY.md#embedder-profile) per repo.
- **[Code Map](code-map.md)** — a mechanical per-repo overview
  (`generated/code-map.md`) rebuilt from chunks on every code-changing sync:
  no LLM, gives overview queries a landing place and every file a
  `documented_in` pointer.
- **Sync** — one mechanical pass (docs refresh → code ingest → embed delta).
  Mycel has no daemon: `mycel search` runs the delta for the searched
  repository when its source changed (fresh-on-read), without embedding.
  `mycel sync` runs the pass over every enabled repository and first resets
  configured checkouts to their remote; read the runbook's warning before
  using it.
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

## Working in Linear

- **[Organize Linear Navigation](linear-organize.md)** — a prominent
  **Needs your attention** entry shows individual open questions, pending
  decisions, reviews, and actions with the next step and source link.
  Tidying project references supports that outcome; the guide verifies both
  actionable content and visible access, while the [runbook](../tools/linear.md)
  covers connector and UI mechanics.

- **[Resolve Linear Comments](linear-resolve.md)** — the owner comments on
  specifications, issues and project pages in Linear; a run collects every
  open thread, makes the change a comment recommends or answers it, and gives
  the user a numbered list of comments and responses in the session. The
  discussion stays in the session; a thread gets `Resolved. Resolution: …`
  only after the user says `Resolved`, and the owner closes it in Linear.

- **[Answer Open Questions from Linear](linear-open-questions.md)** — the
  questions and pending decisions that wait for the owner are spread over
  specifications, issues and comments; a run collects them and gives one
  numbered list in the session, each item written so it can be answered
  without opening Linear. The user answers by number, and each answer is
  written to the place its question is recorded in.

- **[Working in Sagas](sagas.md)** — work is grouped as Sagas, Arcs and
  Beats, kept as files in the private corpus `~/Artifacts/sagas/` and copied
  one way to Linear, where Beats keep their status and comments. A parent
  gives the order of its children, and a child reports its progress to its
  parent. Each Arc reserves the folders and files it changes, and an agent of
  any tool holds the Beat it works on, so several agents work at once without
  changing the same files; a hold is released automatically when its agent's
  program or thread is gone. What a later Beat must know, a Beat leaves in its
  own file, its hand-over, never where only one tool or one group of sessions
  sees it. [Radar statistics](radar-stats.md) show how far each Saga is in
  plan steps and which agents work on it now. [The check from
  outside](agent-watch.md) measures every 5 minutes what each working agent
  did since its last progress and raises the signals that call for a review.

## Learning at the owner's depth

- **[Nex Colab](nex-colab.md)** — the owner asks to learn something with
  `/colab "prompt"`, and the agent answers one level above what the owner's
  Nex Knowledge Map, a private corpus of topics and levels, says they know,
  skipping what they know and offering the ways deeper as numbered options.
  Every explanation is logged, levels rise or fall only on the owner's own
  words judged by fixed tests, and the map is written and pushed after each
  reply; with `(use colab)` the same map pitches the explanations of any
  other work.

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

Mycel is a **per-task CLI** (`mycel …`): one process per job and no daemon.
Its settings live in `~/.mycel/config.toml`, and RAPTOR generation calls the
independent `infer` executable.

## Mycel Skill dispatchers

[Mycel Skills](../../arbol/GLOSSARY.md#mycel-skill) are provider-agnostic
activation contracts implemented by thin provider adapters. Follow the
[creation guide](create-skill.md) to add every available adapter from one shared
trigger contract; native Codex CLI and Claude Code CLI are supported.
Both CLIs link to canonical sources; explicit-only invocation
policy is represented in each provider's supported metadata.

Distinct task shapes have thin skills
routing through the Hub: `/code-research`, `/deep-research`,
`/mycel-search`, `/corpus-admin`, `/authored-work-integration`,
`/pr-deep-review`, `/create-mycel-skill`,
`/linear-resolve`, `/linear-organize`, `/linear-open-questions`, `/radar-stats`,
`/arbol-chat-prepared-folder`, `/colab`, `/use-colab`.
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
installed contracts, including authored-work integration. Explicit invocation is
`$<name>` in Codex and `/<name>` in Claude.
