---
role: authored
chain: start-new-ticket
summary: Jira key → a full ticket workspace, built in 7 Cells (mirror, format, objectives, jira-context, subtask split, code scout, deep research).
default-recipe: jira-agent
---
# Runbook: start-new-ticket (Blueprint Chain)

## Why it exists

The one command that turns a Jira key into a **ticket workspace** — everything
needed to start real work: the mirrored raw ticket, a clean statement,
verifiable [Objectives](../../arbol_deprecated_v1/GLOSSARY.md#objectives), curated Jira/Confluence
context, an optional subtask split, a codebase scout, and a deep-research
brief-driven artifact. The first [Blueprint
Chain](../../arbol_deprecated_v1/GLOSSARY.md#blueprint-chain): deterministic Python composing Tool
calls, Blueprint runs, and inline `infer` lambdas — an unmet `done_when`
ABORTS the chain (the guarantee a chain adds over instructions).

## Use

```
python3 ~/Artifacts/mycel/chains/start-new-ticket.py <DEMO-KEY> --repo <repo>
        [--until N]          # stop after step N — the run stays RESUMABLE
        [--fresh]            # ignore any unfinished run; start from step 1
        [--dry-run]          # print the Cell plan + resume state, run nothing
        [--recipe NAME]      # Brain Recipe for ALL steps (from ~/.mycel/config.toml)
        [--depth survey|standard|exhaustive]
```

## Cells

Seven [Cells](../../arbol_deprecated_v1/GLOSSARY.md#cell) build the workspace in order (each
writes into `~/Artifacts/jira/<KEY>-<slug>/`, shown below as `{ws}`); `--until N`
stops after Cell N and the run stays resumable. Kinds — *Tool*: deterministic
code; *Blueprint*: a named Blueprint run gated by `done_when`; *lambda*: an
inline anonymous agent. Every Blueprint/lambda Cell runs as its own fresh Chat
Session.

1. **Mirror fetch** · *Tool* · in: Jira key `<KEY>` · out: raw mirror `~/Artifacts/mirrors/jira/<KEY>.{md,json}` + workspace `{ws}` · gate: exit 0 · note: re-runs on resume, for freshness
2. **format-ticket** · *Blueprint* · in: raw mirror · out: `{ws}/ticket.md` · gate: `done_when` · note: clean statement, scope, images folded in
3. **objectives** · *lambda* · in: `ticket.md` + raw `<KEY>.json` · out: `{ws}/objectives.md` · gate: session completes · note: 3–8 verifiable completion conditions
4. **gather-jira-context** · *Blueprint* · in: `objectives.md` + the Jira/Confluence graph · out: `{ws}/jira-context.md` · gate: `done_when` · note: curated, per-item provenance · ≤20 min
5. **subtask split** · *lambda* · in: `ticket.md` + `objectives.md` + `jira-context.md` · out: `{ws}/subtasks.md` (only if warranted) · gate: session completes · note: else no file — "NO SPLIT — <reason>"
6. **scout-codebase** · *Blueprint* · in: objectives + `--repo` · out: `{ws}/code-scout.md` · gate: `done_when` · note: where to dig, unverified hunches · ≤20 min
7. **deep-research** · *Blueprint* · in: the whole workspace as its brief + `--repo` + `--depth` · out: `{ws}/research.md` · gate: `done_when` · note: ref-carrying angles · ≤60 min

## Operation

- Output: `~/Artifacts/jira/<KEY>-<slug>/` per the workspace schema
  (ticket.md, objectives.md, jira-context.md, subtasks.md?, code-scout.md,
  research.md) — all indexed by Mycel, all Source-Ref'd to their mirrors.
- **Resume is the default**: re-running the same key picks up the latest
  unfinished run and skips completed agent Cells (the cheap mirror fetch
  re-runs for freshness). So the incremental pattern is just: `--until 3`,
  inspect the workspace, run again — Cells 1–3 cost ~nothing the second time.
- **Process log** (chainlib): `~/.infer/chains/<run-id>/chain.jsonl` — every
  Cell start/finish/skip (rendered `Cell N/total · kind · title`) with session
  ids and the Brain Recipe each ran on; `tail -f` it for a live view;
  `chain.json` holds run status + completed Cells. Every session is labeled
  `chain=start-new-ticket, chain_run=<id>, chain_step=N` — `infer sessions`
  shows the grouped story; the final JSON summarizes per-Cell sessions and the
  Brain Recipe(s) used.
- **Recipe policy**: `--recipe NAME` is the caller input; the chain also
  declares `PIN_RECIPE` (hard pin; `inherit` = none) and `DEFAULT_RECIPE` as
  constants near the top of the script — the script's equivalent of a
  blueprint's frontmatter. Resolution: pin → `--recipe` → default. A blueprint
  with its own pin (e.g. deep-research pinning a strong model) still wins over
  the chain; every Cell reports its recipe.
- Prereqs: Jira PAT set (`mycel secrets`), `mirrors.jira_url` configured,
  VPN up. Failure mode: any tool error or unmet blueprint `done_when` aborts
  with the Cell number and session id to inspect (`infer show <id>`); the
  aborted run is closed — the next invocation starts fresh.
- Preparation-only sibling: [prepare-ticket](prepare-ticket.md) — the same
  first four Cells as an independent chain (fetch, format, objectives,
  jira-context), no scout, no research, no `--repo`.

The script: [`./start-new-ticket.py`](start-new-ticket.py) — same folder,
same name; scripts are not indexed (corpus ingests `*.md` only), proximity
is the link. Shared plumbing: `./chainlib.py` (log, resume, parallel,
nesting — see plans/blueprints.md "Chain plumbing").
