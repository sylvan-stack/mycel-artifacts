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
  Profile](../../arbol/GLOSSARY.md#embedder-profile) per repo. The interlock is
  structural: Core-Repo and mirror text embeds on-device (the [Embedding
  Provider](../../arbol/GLOSSARY.md#embedding-provider) app), never via an external
  API.
- **[External Mirrors](external-mirrors.md)** — Jira tickets, Confluence
  pages, and GitLab MRs fetched *on events* into
  `~/Artifacts/mirrors/<surface>/` as raw, never-edited Markdown, then
  ingested like any corpus. Curated derivatives live one layer up and get
  flagged by Detection when the ticket moves underneath them. Mirrors are
  one-way, but surface *writes* live here too for now (`mycel jira …`,
  `mycel confluence create|update`) — every write re-fetches its mirror.
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
- **[Branch Context](branch-checkout.md)** — inspect and update branches in the
  existing repository checkout, preserving edits and requiring approval before
  switching branches. Worktree lifecycle procedures are historical.
- **Source investigation guides:** [Claude](claude-source-investigation.md)
  uses Mycel through native `Bash`; [native Codex CLI](codex-source-investigation.md)
  uses native shell/filesystem tools, `rg` for exact search, and Mycel for
  semantic discovery. Follow each provider's guide and effective runtime rules.
- **[Research levels](code-research-levels.md)** — `better-grep` (exact +
  meaning tail) → [code-research](code-research.md) (question → cited answer)
  → [deep research](deep-research.md) (task → durable artifact, defined by
  the first [Blueprint](../../arbol/GLOSSARY.md#blueprint)).

## Difficult implementation and bug-fix work

- **[Troubleshooting Difficult Tasks](troubleshooting.md)** — when an agent is
  stuck, preserve the investigation under the affected repository with one
  record per Chat Session, curated findings and failed directions, and a short
  current-status handoff. The evidence-first loop makes disproved hypotheses
  and narrowed uncertainty durable progress instead of work that later
  sessions repeat.

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

## Recurring subjects

- **[Living Topics](living-topics.md)** — a repo-agnostic topic folder
  (`~/Artifacts/living-topics/<slug>/`) with FINDINGS / FALSE-POSITIVES /
  NEXT-STEPS / SUMMARIES / TIMELINE carries a recurring subject's context
  across Chat Sessions. Each new session hydrates from a Chat Note (reading
  order, write-back rules) and records conclusions back incrementally, so the
  next manifestation starts from accumulated truth instead of re-derivation.

## Relayed agent messages

- **[iPad Dashboard messages](ipad-dashboard.md)** — `/ipad` and every iPad
  Dashboard mention load identity-verification and correlated-reply guidance.
  The origin label is only a routing hint; actual pickup and response use the
  durable mailbox, and neither skill activation nor read state authorizes task
  execution or implements automatic dispatch.

## Tool-call investigations

- **[Tool-call log investigation](tool-call-observability.md)** — inspect recent
  activity generally or one Chat Session for failures, stuck-looking calls,
  redrives, telemetry anomalies, suspicious results, and latency. It reads
  operational database and log data directly without an application code or
  instructions dependency.

## Turn Composition validation

- **[Turn Composition test sessions](turn-composition-testing.md)** — `/turn-test`
  selects a realistic catalog request by ID or difficulty, then pins the newest
  persisted Turn Inspector trace for evidence-based follow-up. Explicit
  finalization writes one bounded session result and updates cumulative issue
  and proposal registers.

## The work side — how tickets flow

- **[Ticket Workflow](ticket-workflow.md)** — the Jira+git process:
  prep → subtasks → worktree-per-branch → MRs → transitions, with its
  [lookup companion](ticket-workflow-reference.md) for IDs, payloads, and
  conventions. The prepare-ticket / start-new-ticket chains build the
  [Ticket Workspace](../../arbol/GLOSSARY.md#ticket-workspace) it works in.

## How it compounds

Retrieval gets smarter through documents, not tuning: jargon the code never
spells out earns a [GLOSSARY](../../arbol/GLOSSARY.md#source-ref) bridge entry;
research worth keeping is persisted with Source Refs and update-don't-
duplicate; superseded truth freezes as [Heartwood](../../arbol/GLOSSARY.md#heartwood);
mirrors bring the outside world in. [Detection](../../arbol/GLOSSARY.md#detection)
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
`/mycel-search`, `/branch-context`, `/ticket-context`, `/corpus-admin`,
`/code-review`, `/implementation-plan`, `/spike-doc`, `/branch-update`,
`/ticket-workflow`, `/confluence`, `/tool-call-monitor`, `/turn-test`, `/ipad`.
Skills carry only *when to trigger*; the process always lives here, in Mycel.

<!-- sources:
mycel:operations/ipad-dashboard.md
mycel:operations/embedding.md
mycel:operations/external-mirrors.md
mycel:operations/code-map.md
mycel:operations/retrieval.md
mycel:operations/worktree-lifecycle.md
mycel:operations/code-research-levels.md
mycel:operations/code-research.md
mycel:operations/deep-research.md
mycel:operations/ticket-workflow.md
mycel:operations/knowledge-model.md
mycel:operations/authored-work-integration.md
-->

The [skill catalog](../INDEX.md#skills--mycel-skill-provider-adapters) lists all
installed contracts, including Living Topics, authored-work integration, and
[Places API log investigation](places-api-logs.md). Explicit invocation is
`$<name>` in Codex and `/<name>` in Claude.
