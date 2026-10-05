---
status: heartwood
implemented: 2026-03
outdated: 2026-07-05
---
# Deep Research — Cursor-era engine (snapshot)

Heartwood snapshot of the ENGINE that powered the deep-research workflow from
2026-03 to 2026-07 (orchestrate.js spawning the Cursor agent CLI; Cursor lost
company support). The workflow itself lives on — see the living
[deep-research](../deep-research.md) — this snapshot preserves how this
implementation worked: its phase loop, steering files, and quality contract
are the design the successor engine inherits.

Long-running autonomous codebase research (5–30+ min): a cheap worker model
drafts and researches, an expensive steerer reviews and scores, looping until
the report clears a quality threshold. Produces `research-final.md` in a
session directory.

> **Freshness.** The orchestrator (`~/.cursor/skills/deep-research/scripts/orchestrate.js`)
> lives OUTSIDE every Mycel corpus, so Detection cannot watch it — claims below
> about its flags and defaults rot silently. Last verified: 2026-07-05 (script
> present; flags/model defaults NOT re-verified — the worker/steerer defaults
> mention models that may be outdated). When in doubt run
> `node ~/.cursor/skills/deep-research/scripts/orchestrate.js --list` and read
> the usage output before trusting the tables below. To put the orchestrator
> under Detection, move it into a Mycel-enabled repo and add refs here.

## Quick start

Extract the **topic** from the user's message and launch the orchestrator —
always in the background (it runs 5–30+ minutes):

```bash
node ~/.cursor/skills/deep-research/scripts/orchestrate.js "<topic>" [options]
```

Capture the **session directory** from launch output (`Session dir: …`,
typically under `~/Artifacts/research-sessions/<session-id>`) and use that
exact path for all later commands.

## Monitoring

- Quick status: `cat "<session-dir>/status.txt"` (overwritten each phase)
- Detailed log: `tail -30 "<session-dir>/progress.log"` (append-only)

Poll every 30–60s when feasible and report phase transitions. If continuous
polling isn't feasible: launch, share the session dir, do 1–2 quick checks,
and tell the user they can ask "check research status" / "show research
result" later.

## Presenting results

When `status.txt` is terminal (`completed`, `converged`, `max-iterations`,
`user-stopped`, `error`): read `<session-dir>/research-final.md`, summarize the
key findings, include the report path.

**Then close the loop with Mycel** (this step post-dates the original skill):
if the research is worth keeping, persist it per
[Source Refs — authoring guide](../source-refs-authoring.md) — copy the
useful parts into the owning repo's artifact corpus
(`~/Artifacts/<repo>/research/<topic>.md`) with frontmatter and per-section
`<!-- sources: -->` refs. That turns the session's one-off report into a
permanent retrieval bridge; the raw session directory is disposable.

## Commands and options

```bash
node ~/.cursor/skills/deep-research/scripts/orchestrate.js "<topic>"                      # new
node ~/.cursor/skills/deep-research/scripts/orchestrate.js "<topic>" --bundle --parallel  # all features
node ~/.cursor/skills/deep-research/scripts/orchestrate.js --resume <session-id>
node ~/.cursor/skills/deep-research/scripts/orchestrate.js --list
```

| Flag | Default | Description |
| --- | --- | --- |
| `--worker <model>` | `gpt-5.3-codex-spark` | worker model (⚠ verify — may be outdated) |
| `--steerer <model>` | `opus-4.6` | steering model (⚠ verify — may be outdated) |
| `--threshold <n>` | `7` | score threshold (1–10) to stop |
| `--max-iterations <n>` | `5` | max research–eval cycles |
| `--timeout <ms>` | `900000` | per-agent-call timeout |
| `--bundle` | off | Phase 0 context bundle (broad topics spanning many files) |
| `--parallel` | off | split plan topics across parallel workers (3+ independent areas) |

## User steering (between iterations)

Control files in the session directory: `pause` (touch to pause; delete to
resume), `stop` (terminate, save progress as final), `user-feedback.md`
(injected into the next iteration's prompt, then archived to
`user-feedback-used-vN.md`). Quick pause from anywhere: `ops pause research`.

**Feedback is replace, not append** — each `user-feedback.md` is consumed and
archived; write the complete steering you want for the upcoming iteration. The
worker also sees the previous research document, so state only the new
direction.

## How it works

```
Phase 0: CONTEXT BUNDLE (worker, optional)        → context-bundle.md
Phase 1: PLAN (worker)                            → plan.md
Phase 2: PLAN REVIEW (steerer)                    → feedback-v0.md
Phase 3: RESEARCH (worker, seq or parallel)       → research-vN.md   ◄──┐
Phase 4: EVALUATE (steerer)                       → eval-vN.md          │
         [check pause/stop/feedback]                                    │
         score ≥ threshold or stagnated → DONE, else loop ──────────────┘
```

Session artifacts: `session.json`, `status.txt`, `progress.log`,
`context-bundle.md`, `plan.md`, `feedback-v0.md`, `research-vN[-pM].md`,
`eval-vN.md`, `user-feedback-used-vN.md`, `research-final.md`.

## Quality contract

Reports must include **code evidence**: each significant finding carries a
3–15 line snippet with file path and line range. The steerer penalizes
statement-only reports.

## Tips

- All repos are reachable by the workers.
- `--bundle` for broad topics; `--parallel` for 3+ independent areas; combine
  for large tasks.
- Threshold 5–6 for quick overviews, 8–9 for thorough research.
- Before launching, consider whether prior research already covers part of the
  topic: `mycel search --repo <repo> --only code "<topic>"` — bridge hits with
  `via …/research/…` mean a document already exists; feed it to the worker
  instead of re-discovering.
