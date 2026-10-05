---
role: authored
chain: prepare-ticket
summary: Jira key → the light half of a ticket workspace in 4 Cells (mirror, format, objectives, jira-context) — preparation without the research.
default-recipe: jira-agent
---
# Runbook: prepare-ticket (Blueprint Chain)

## Why it exists

The **preparation slice without the research**: mirrored raw ticket →
formatted `ticket.md` → verifiable [Objectives](../../arbol/GLOSSARY.md#objectives) →
curated `jira-context.md`, then stop. For the times the ticket should be
understood and its context curated, but the codebase work (scout, deep
research) is deferred — or never wanted. Deliberately **duplicates** steps
1–4 of [start-new-ticket](start-new-ticket.md) instead of sharing a
sub-chain: the two chains evolve independently and each reads whole (DRY
rejected on purpose; only chainlib plumbing is shared).

## Use

```
python3 ~/Artifacts/mycel/chains/prepare-ticket.py <DEMO-KEY>
        [--until N]     # stop after step N — the run stays RESUMABLE
        [--fresh]       # ignore any unfinished run; start from step 1
        [--dry-run]     # print the Cell plan + resume state, run nothing
        [--recipe NAME] # Brain Recipe for ALL steps (from ~/.mycel/config.toml)
```

## Cells

Four [Cells](../../arbol/GLOSSARY.md#cell) — the same first four
[start-new-ticket](start-new-ticket.md) runs, minus scout and research (each
writes into `~/Artifacts/jira/<KEY>-<slug>/`, shown as `{ws}`). No `--repo` —
preparation never touches code; `--until N` stops after Cell N, resumable.
Kinds — *Tool*: deterministic code; *Blueprint*: a named Blueprint run gated by
`done_when`; *lambda*: an inline anonymous agent (its own fresh Chat Session).

1. **Mirror fetch** · *Tool* · in: Jira key `<KEY>` · out: raw mirror `~/Artifacts/mirrors/jira/<KEY>.{md,json}` + workspace `{ws}` · gate: exit 0 · note: re-runs on resume, for freshness
2. **format-ticket** · *Blueprint* · in: raw mirror · out: `{ws}/ticket.md` · gate: `done_when`
3. **objectives** · *lambda* · in: `ticket.md` + raw `<KEY>.json` · out: `{ws}/objectives.md` · gate: session completes · note: 3–8 verifiable completion conditions
4. **gather-jira-context** · *Blueprint* · in: `objectives.md` + the Jira/Confluence graph · out: `{ws}/jira-context.md` · gate: `done_when` · note: ≤20 min

## Operation

- Output: `~/Artifacts/jira/<KEY>-<slug>/` with `ticket.md`, `objectives.md`,
  `jira-context.md` — the same workspace start-new-ticket builds, minus
  `code-scout.md`/`research.md`. Running start-new-ticket later on the same
  key does NOT resume this chain (different chain name) — it re-runs its own
  steps 1–4 over the same workspace files, which is idempotent-by-content
  (each blueprint updates its artifact rather than duplicating).
- Resume, process log, labels, abort semantics: identical to
  [start-new-ticket](start-new-ticket.md) — chainlib provides them
  (`~/.infer/chains/<run-id>/chain.jsonl`, `tail -f` for live view).
- **Recipe policy**: `--recipe NAME` is the caller input; the chain also
  declares `PIN_RECIPE` (hard pin; `inherit` = none) and `DEFAULT_RECIPE` as
  constants near the top of the script — the script's equivalent of a
  blueprint's frontmatter. Resolution: pin → `--recipe` → default. A blueprint
  with its own pin still wins over the chain; every step reports its recipe.
- Prereqs: Jira PAT set (write-only, `mycel secrets`), `mirrors.jira_url`
  configured, VPN up.

The script: [`./prepare-ticket.py`](prepare-ticket.py) — same folder, same
name; scripts are not indexed (corpus ingests `*.md` only), proximity is the
link.
