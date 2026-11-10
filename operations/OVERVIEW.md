---
role: authored
---
# Mycel Process Guides — the readable summary

One page to (re)load the whole mental model. Each section is two sentences of
*what and why*; the linked guide holds the process. Agents route via the
[Instructions Hub](../README.md); this overview is for humans.

## The write side — how knowledge gets in

Follow the [Hub's dated pre-ingest instruction](../README.md): the owner has
not yet filled the index, so current research uses grep and file reads.

- **[Embedding](embedding.md)** — retained exact-text versions become vectors
  under the configured model and dimensions. Complete part plans preserve the
  body and its place line; explicit repository scope keeps work bounded.
- **Stored code overview** — ingest maintains index-only directory outlines;
  `mycel overview --repo <repo>` reads them. The
  [overview manual](../tools/mycel-2-overview.md) describes their counts and
  search behavior.
- **Ingest** — `mycel ingest --repo <repo>` captures both corpora and local
  branches/stashes, reconciles identities and dependencies, and runs mechanical
  Detection without changing the checkout. It embeds only with explicit
  `--embed`; normal search can perform bounded freshness work without embedding
  pending corpus text.
- **[Authored-work integration](authored-work-integration.md)** — integration
  requires coverage, ingest, real dependency/relation declarations, mechanical
  freshness, explicit embedding and retrieval verification. Deferred steps are
  reported separately from passing tests.

- **[Justify code and documents](justification.md)** — identifiable requirements and decisions let existing declarations become stored Origin claims before recovery and audit inspect the gaps. Reports for new work are optional; owner-store writes and paid calls follow the current operator boundary.

## The read side — how knowledge comes out

- **[Code Retrieval](retrieval.md)** — search ranks current code, documents
  and generated sections with separate meaning/wording candidates, exact
  document bridges and visible freshness evidence. The schema-3 reply keeps
  each repository's results separate.
- **[Research levels](code-research-levels.md)** — exact text lookup and optional
  `mycel grep` recall → [code-research](code-research.md), a question answered
  with citations → [deep research](deep-research.md), durable task context.

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

## Working in Sagas

- **[Working in Sagas](sagas.md)** — work is grouped as Sagas, Arcs and
  Beats, kept as files in the private corpus `~/Artifacts/forester/sagas/`, where
  completed IDs and hand-over survive. A parent
  gives the order of its children, and a child reports its progress to its
  parent. Each Arc reserves the folders and files it changes, and an agent of
  any tool holds the Beat it works on, so several agents work at once without
  changing the same files; a hold is released automatically when its agent's
  program or thread is gone. What a later Beat must know, a Beat leaves in its
  own file, its hand-over, never where only one tool or one group of sessions
  sees it. [Radar statistics](../../forester/operations/forester-stats.md) show how far each Saga is in
  plan steps and which agents work on it now. [The check from
  outside](agent-watch.md) measures every 5 minutes what each working agent
  did since its last progress and raises the signals that call for a review.

## Developing a new feature

- **[Feature Course](feature-course.md)** — the owner and agent work through six
  stages from the first idea to Beats with implementation plans. One research
  document carries the evidence into planning, and a gap in the specification
  sends that behavior back to Spec Writing for the owner’s decision.

## Saga Planning and Arc Review

- **[Saga Planning and Arc Review](saga-planning.md)** — turn a specification
  into Sagas, Arcs and ordered Beats. Once an Arc’s testing Beat finishes,
  a session that took none of its Beats reviews the combined result.

## Planning a Beat

- **[Planning a Beat](implementation-planning.md)** — before a Beat is
  implemented it gets a plan: logical, atomic steps of any kind, each code
  step naming its files and the requirements it serves. A gap in the
  specification stops planning and goes to the owner; a reviewer with fresh
  context accepts the plan, not the owner. `/plan-beat` starts it, and
  Forester sends an agent there when a Beat has no plan.

## Learning at the owner's depth

- **[Nex Colab](nex-colab.md)** — the owner asks to learn something with
  `/colab "prompt"`, and the agent answers one level above what the owner's
  Nex Knowledge Map, a private corpus of topics and levels, says they know,
  skipping what they know and offering the ways deeper as numbered options.
  Every explanation is logged and closed by a short quiz, levels rise or
  fall only on the owner's own words and quiz answers judged by fixed tests,
  each change listed in the reply, and the map is written and pushed after
  each reply; with `(use colab)` the same map pitches the explanations of any
  other work. With `/colab showup "<words>"` the owner states their own level,
  which goes into the map as their entry once every choice the words leave is
  settled. With `/learn` a whole session becomes learn mode: one piece per
  reply, closed by its quiz and options to go on in any direction, the map
  kept current, and no other work until the owner leaves it.

## The owner's goals

- **[Owner Goals](owner-goals.md)** — what the owner wants of their
  software, one statement per file in the private corpus `~/Artifacts/goals`.
  The owner records, changes and withdraws them in their own words with
  `/owner-goals "<words>"`; the agent writes them with the `goals` command,
  which refuses a change that breaks the graph, and checks that no two of them
  contradict each other. Every other piece of work reads them as requirements.

## Reservble places-api logs

- **[Places API Logs](places-api-logs.md)** — `/places-api-logs` diagnoses
  Reservble's side of the Syrve integration from the daily logs on a read-only
  SFTP server: list a day's files, pick the log types, search them locally and
  correlate IDs into a UTC timeline with guest details redacted. The
  [SFTP manual](../tools/places-api-sftp.md) owns the connection and the
  sign-in on this Mac.

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
Its settings live in `~/.mycel/config.toml`; `mycel summaries` uses the
explicitly configured writer command for generation. The installed launcher
selects an immutable working Build; see the [runbook](../tools/mycel.md).

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
`/forester-stats`,
`/arbol-chat-booking`, `/colab`, `/use-colab`, `/learn`,
`/owner-goals`, `/places-api-logs`, `/plan-beat`.
Skills carry only *when to trigger*; the process always lives here, in Mycel.

<!-- sources:
mycel:operations/embedding.md
mycel:@code/src/mycel/_overview.py
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
