# Mycel Operations Catalog

> **Start at the [Instructions Hub](./README.md)** — the routing table. This
> INDEX is the full catalog of the Mycel corpus (`~/Artifacts/mycel/`, repo
> `mycel`, its own git repo): everything about **how to work**. The product it
> documents — architecture, plans, glossary — is one corpus over in
> [`~/Artifacts/arbol_deprecated_v1/`](../arbol_deprecated_v1/INDEX.md). Shared vocabulary:
> [GLOSSARY](../arbol_deprecated_v1/GLOSSARY.md).

Everything here passes the **VS Code Test**: usable without Arbol installed.

## Chapters

### `operations/` — Mycel Operations: frontend-agnostic process descriptions
What must happen, in Mycel vocabulary — the invariant behind every invocation surface (Arbol RPCs, CLI agents, the [Blueprint](../arbol_deprecated_v1/GLOSSARY.md#blueprint) engine).
- [`OVERVIEW.md`](./operations/OVERVIEW.md) — the readable one-page summary of all operations (for humans; agents use the Hub).
- [`external-mirrors.md`](./operations/external-mirrors.md) — Jira/Confluence/GitLab → local mirror corpus: fetch on events, mirror class, closure rule.
- [`ticket-workflow.md`](./operations/ticket-workflow.md) — the Jira+git ticket workflow, read whole: prep and subtask phases, transition policy, worktree-model hold/switch.
- [`ticket-workflow-reference.md`](./operations/ticket-workflow-reference.md) — its lookup companion, consulted per section: Jira CLI payloads + JQL, transition IDs, NJ compliance keys, wiki markup, git conventions (source of truth for CLAUDE.md's copy).
- [`code-research-levels.md`](./operations/code-research-levels.md) — grep → better-grep → code-research → deep-research: which tool when.
- [`claude-source-investigation.md`](./operations/claude-source-investigation.md) — Claude-specific guide: Mycel through native `Bash`, `better-grep` for exact search, and bounded native reads.
- [`codex-source-investigation.md`](./operations/codex-source-investigation.md) — native Codex CLI shell/filesystem search and reading; Universe is deprecated.
- [`universe-source-investigation.md`](./operations/universe-source-investigation.md) — historical Universe guide, superseded by the Codex guide.
- [`code-research.md`](./operations/code-research.md) — the level-3 loop. Skills are thin dispatchers pointing here.
- [`deep-research.md`](./operations/deep-research.md) — level-4 entry point; the definition lives in the [deep-research Blueprint](./blueprints/deep-research.md).
- [`branch-checkout.md`](./operations/branch-checkout.md) — branch context and updates in the standard checkout.
- [`worktree-lifecycle.md`](./operations/worktree-lifecycle.md) — historical, deprecated worktree lifecycle.
- [`embedding.md`](./operations/embedding.md) — profiles/interlock, the identity-header recipe, iron rules, compounding habits.
- [`retrieval.md`](./operations/retrieval.md) — the read path: route decision, doc bridge, noise down-weights, via/documented_in annotations.
- [`code-map.md`](./operations/code-map.md) — the mechanical per-repo overview artifact and its `generated: true` semantics.
- [`knowledge-model.md`](./operations/knowledge-model.md) — the value reference: in-band declarations (`role:` / `status: heartwood` / `generated:` / `sources:`), chunk roles/states, Derivation kinds/policies, Detection reasons, Drift lifecycle.
- [`authored-work-integration.md`](./operations/authored-work-integration.md) — completion loop for new artifacts, implementation, and tests: corpus coverage, chunk ingest, authority edges, Detection, embeddings, and retrieval verification.
- [`ipad-dashboard.md`](./operations/ipad-dashboard.md) — `/ipad` and iPad Dashboard mentions: verified mailbox pickup, correlated replies, safe resume, and activation/dispatch boundaries.
- [`create-skill.md`](./operations/create-skill.md) — create one provider-agnostic Mycel Skill and its thin provider adapters; covers native Codex CLI and Claude Code CLI discovery, symlinks, and invocation policy.
- [`tool-call-observability.md`](./operations/tool-call-observability.md) — investigate recent tool calls or one Chat Session for failures, suspicious results, telemetry gaps, and latency by reading operational data directly.
- [`turn-composition-testing.md`](./operations/turn-composition-testing.md) — run a Turn Composition validation session: select a history-backed request, inspect the newest persisted Turn Inspector result, and finalize per-session plus cumulative evidence.
- [`troubleshooting.md`](./operations/troubleshooting.md) — preserve and resume difficult implementation or bug-fix investigations through indexed session records, curated findings, failed directions, and explicit handoff state.
- [`pr-deep-review.md`](./operations/pr-deep-review.md) — multi-session review of a large pull request: sync with the head, ranked areas, verified and independently challenged findings, a queue of drafted comments for the human reviewer, commands for the recurring steps (next, commits, verify, replies, check, summary, status), stop criteria on findings, time, tokens and coverage; never posts.
- [`pr-deep-review-reference.md`](./operations/pr-deep-review-reference.md) — its lookup companion: `state.json` schema, area and finding statuses, templates for the reviewer's page, finding card and run report, stop-criteria measures and kinds, reading token spend, commands for reading a GitHub pull request.
- [`stints.md`](./operations/stints.md) — named sets of stop criteria for a run: the defined stints, how a run resolves its stint and limits, how to add or change one.
- [`living-topics.md`](./operations/living-topics.md) — recurring-subject continuity: the repo-agnostic topic folder contract (FINDINGS / FALSE-POSITIVES / NEXT-STEPS / SUMMARIES / TIMELINE), Chat Note hydration for new sessions, incremental write-back, wrap-up.
- [`source-refs-authoring.md`](./operations/source-refs-authoring.md) — author durable provenance and section-level Source Refs without relying on instructions from another corpus.
- [`places-api-logs.md`](./operations/places-api-logs.md) — Reservble Syrve production-log access and investigation through read-only SFTP.
- `archive/` — heartwood snapshots of superseded engines.

### `blueprints/` — executable agent-work definitions ([Blueprints](../arbol_deprecated_v1/GLOSSARY.md#blueprint))
Typed contract in frontmatter + agent instructions in the body; run detached via `blueprint run <name>` or by any agent manually.
- [`deep-research.md`](./blueprints/deep-research.md) — level-4 research producing/updating ref-carrying artifacts (topic mode or ticket-workspace mode).
- [`code-review.md`](./blueprints/code-review.md) / [`implementation-plan.md`](./blueprints/implementation-plan.md) / [`spike-doc.md`](./blueprints/spike-doc.md) — the daily composites.
- [`format-ticket.md`](./blueprints/format-ticket.md) / [`gather-jira-context.md`](./blueprints/gather-jira-context.md) / [`scout-codebase.md`](./blueprints/scout-codebase.md) — the ticket-workspace builders the chains compose.
- [`review-diff.md`](./blueprints/review-diff.md) / [`verify-findings.md`](./blueprints/verify-findings.md) — the code-review chain's executor + adversarial-verifier Cells (verify-findings is the reusable findings→verdicts seam).

### `chains/` — Blueprint Chains: scripts AND their runbooks, side by side
Each `<name>.py` has its runbook `<name>.md` next to it (runbook-near-file rule); shared plumbing is `chainlib.py` (process log, resume, parallel, nesting — [../arbol_deprecated_v1/plans/blueprints.md](../arbol_deprecated_v1/plans/blueprints.md) "Chain plumbing"). Scripts aren't indexed (`*.md` only); same-folder-same-name proximity is the link.
- [`start-new-ticket.md`](./chains/start-new-ticket.md) — Jira key → full ticket workspace (7 [Cells](../arbol_deprecated_v1/GLOSSARY.md#cell) incl. code scout + deep research).
- [`prepare-ticket.md`](./chains/prepare-ticket.md) — preparation only: fetch, format, objectives, jira context; no research. Duplicates Cells on purpose.
- [`code-review.md`](./chains/code-review.md) — MR URL → verified review (8 Cells): mirrors → coverage contract → review-diff with a code-enforced coverage gate → fresh-context verify-findings → publish to the ticket workspace (`code-review-<datetime>.md`: [BLOCKING] markers, clickable file:line, evidence per point).

### `tools/` — technical manuals for the client-agnostic CLIs
One [Runbook](../arbol_deprecated_v1/GLOSSARY.md#runbook) per [Tool](../arbol_deprecated_v1/GLOSSARY.md#tool); Arbol-only tools (arbol-cli, deployment) keep theirs in the [Arbol corpus](../arbol_deprecated_v1/tools/).
- [`mycel.md`](./tools/mycel.md) — knowledge CLI: search, sync, embed, wt, raptor, secrets, mirror.
- [`infer.md`](./tools/infer.md) — the agent-session substrate (recipe-pinned, brokered, recorded).
- [`blueprint.md`](./tools/blueprint.md) — run a Blueprint as a typed function (a Delegate via infer).
- [`arbol-agent.md`](./tools/arbol-agent.md) — independently invocable encrypted work-mailbox CLI: observation, explicit read, and correlated replies; no Arbol host/RPC dependency.
- [`better-grep.md`](./tools/better-grep.md) — grep passthrough + Mycel tail.
- Arbol-only tool manuals remain in the [Arbol tools catalog](../arbol_deprecated_v1/INDEX.md#tools--technical-manuals-for-arbols-own-product-tools); cross-repository operating procedures live in `operations/`.

### `skills/` — Mycel Skill provider adapters
Shared activation contracts and thin Hub dispatchers for native Codex CLI and Claude Code CLI. Canonical sources are linked into `~/.agents/skills/` (Codex) and `~/.claude/skills/` (Claude). Universe is deprecated. See [authoring rules](skills/README.md) and the [creation guide](operations/create-skill.md).

- [`authored-work-integration`](./skills/authored-work-integration/SKILL.md)
- [`branch-context`](./skills/branch-context/SKILL.md)
- [`branch-update`](./skills/branch-update/SKILL.md)
- [`code-research`](./skills/code-research/SKILL.md)
- [`corpus-admin`](./skills/corpus-admin/SKILL.md)
- [`create-mycel-skill`](./skills/create-mycel-skill/SKILL.md)
- [`deep-research`](./skills/deep-research/SKILL.md)
- [`ipad`](./skills/ipad/SKILL.md)
- [`living-topic`](./skills/living-topic/SKILL.md)
- [`mycel-search`](./skills/mycel-search/SKILL.md)
- [`places-api-logs`](./skills/places-api-logs/SKILL.md)
- [`pr-deep-review`](./skills/pr-deep-review/SKILL.md)
- [`tool-call-monitor`](./skills/tool-call-monitor/SKILL.md)
- [`troubleshooting`](./skills/troubleshooting/SKILL.md)
- [`turn-test`](./skills/turn-test/SKILL.md)

`providers/claude/turn-test/` preserves Claude's explicit-only frontmatter; Codex uses the matching `agents/openai.yaml` policy. All other adapters share the same source directory. The obsolete `deploy-stand` entry was removed: no Mycel-owned procedure or adapter exists; Arbol deployment remains in its own corpus. Personal and third-party skills remain outside this catalog.

The Example organization workflow adapters were removed on 2026-09-29: `ticket-context`,
`ticket-workflow`, `prepare-ticket`, `start-ticket`, `implementation-plan`,
`spike-doc`, `code-scout`, `code-review`, and `confluence`. Their historical
process documents remain in this corpus; they are not installed skills.
The active catalog contains 15 Mycel skills for both providers.
