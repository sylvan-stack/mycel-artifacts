---
role: authored
---
# Guide: Radar Statistics

Use this guide to show the owner, in the session, every Saga or one selected
Saga, and every Arc under it, with how much of its work is Done, In progress
and left, how many agents work on it now, and how much context those agents
hold. It stands in for the [Radar](../../arbol/GLOSSARY.md#radar), the live
overview Arbol will have.
The Sagas, their Arcs and the plans of their Beats are files in
`~/Artifacts/sagas/`, kept as [Working in Sagas](sagas.md) says.

This guide is authoritative for which numbers are shown and how each is
counted. The tool `~/Artifacts/sagas/tools/radar_stats.py` does the
counting; it reads files and runs `ps` and `lsof`, and writes nothing.

**Contents:** when to use · scope · what is shown · a run · not counted yet.

## When to use

The owner asks how far the Sagas are, or which agents are working on them now:
"/radar-stats", "/radar-stats arbol-2-specs-implementation",
"How far are the Sagas?", "Show the radar with Arcs".

Not for taking, planning or finishing a Beat ([Working in Sagas](sagas.md)),
nor for what waits for the owner in Linear
([Organize Linear Navigation](linear-organize.md),
[Answer Open Questions from Linear](linear-open-questions.md)).

## Scope

The optional parameter selects a Saga listed in `~/Artifacts/sagas/INDEX.md`
by its folder name or the full name heading in its `saga.md`, matched exactly
without regard to case or surrounding whitespace. For example,
`/radar-stats arbol-2-specs-implementation` and
`/radar-stats "Arbol 2 Specs Implementation Saga"` select the same Saga. A
natural-language request naming that Saga uses the same scope. With no
parameter or named Saga, show every Saga as before.

When a Saga is selected, show only that Saga and its Arcs. Do not query Linear
for other Sagas.
An unknown or ambiguous selection must identify the available names and folders
instead of falling back to all Sagas; resolve the choice before collecting
statuses or counting.

## What is shown

One row for each Saga in scope, in the order of `~/Artifacts/sagas/INDEX.md`,
and under it one row for each of its Arcs, in the order its `saga.md` names
them. An Arc's row counts its own Beats the same way. An Arc whose steps are
all Done and that no agent works on is left out, such as the Drivers Arc once
its last Beat is Done:

| Column | What it counts |
|---|---|
| Steps | The leaves of the plans of the Saga's Beats: `## Plan`, or `## Draft plan` before the work starts. A Beat with neither, such as one Done before plans existed, counts as the average of its Saga's Beats that have one, and the Saga's numbers then carry `~` |
| Done | Every step of a Beat whose Linear status is Done, and the ticked steps of every other Beat |
| In progress | The steps not yet ticked of a Beat that is In Progress in Linear, or held |
| Other | Every remaining step: Beats not started, blocked or waiting. Canceled and Duplicate Beats are left out |
| Agents | The holds on the Saga's Beats whose agent is alive: the agents working on it now |
| Context | Those agents' context, added up: the input of each one's last model call, which Claude Code's session file and Codex's thread file record |

Agents that hold no Beat are not shown. From outside, a running `claude`
program does not show which session it runs or whether it works or waits: the
desktop app keeps one alive, idle, for every session that Remote Control
serves. So a count of them says nothing about work on the Sagas.

## A run

1. **Resolve scope.** Match the optional Saga parameter or named Saga as above.
   Use its folder name for the counter's `--saga` option.
2. **Statuses from Linear.** For every Arc issue in scope that
   `~/Artifacts/sagas/.linear.json` names (only paths under the selected Saga's
   folder when scoped), list its sub-issues with their
   identifier and status (the Linear tool's issue list, by parent, with the
   fields `id` and `status`). Write them as one JSON object of identifier to
   status, such as `{"SYL-170": "Done"}`, to a temporary file outside the
   corpus. If Linear cannot be reached, run without it and say that Done then
   counts only Beats whose plan is fully ticked.
3. **Count.** Run
   `python3 -I ~/Artifacts/sagas/tools/radar_stats.py --statuses <file> --arcs --markdown`.
   For a selected Saga, add `--saga <folder>`; for example,
   `python3 -I ~/Artifacts/sagas/tools/radar_stats.py --statuses <file> --arcs --markdown --saga arbol-2-specs-implementation`.
   Without `--markdown` the tool prints a plain-text table for a terminal.
   Use `--json` instead when a program reads the result; the JSON lists every
   Arc, finished ones too.
4. **Show** the Markdown table as printed, with its note on `~`, as Markdown
   and not in a code block, so that it fits any window. Saga names are in
   bold, Arcs are marked `↳`, and an Arc that an agent works on now is in
   bold across its row. Then say in one or two plain sentences what stands out, such as a Saga
   with agents but no step in progress, or a Beat In Progress that no agent
   holds.
5. **Change nothing.** No corpus file, no Linear item, no hold. Remove the
   temporary statuses file after counting.

## Not counted yet

- **Agreed metrics not counted yet:** the last 1, 4 and 24 hours of agents,
  context and generated tokens; waiting on the owner; idle lanes (Beats ready
  to take that no agent holds); Subscription headroom.
