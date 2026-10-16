---
role: authored
---
# Guide: Radar Statistics

Use this guide to show the owner, in the session, every Saga with how much of
its work is Done, In progress and left, how many agents work on it now, and
how much context those agents hold. It stands in for the
[Radar](../../arbol/GLOSSARY.md#radar), the live overview Arbol will have.
The Sagas, their Arcs and the plans of their Beats are files in
`~/Artifacts/sagas/`, kept as [Working in Sagas](sagas.md) says.

This guide is authoritative for which numbers are shown and how each is
counted. The tool `~/Artifacts/sagas/tools/radar_stats.py` does the
counting; it reads files and runs `ps` and `lsof`, and writes nothing.

**Contents:** when to use · what is shown · a run · not counted yet.

## When to use

The owner asks how far the Sagas are, or which agents are working now and on
what: "/radar-stats", "How far are the Sagas?", "Show the radar with Arcs".

Not for taking, planning or finishing a Beat ([Working in Sagas](sagas.md)),
nor for what waits for the owner in Linear
([Organize Linear Navigation](linear-organize.md),
[Answer Open Questions from Linear](linear-open-questions.md)).

## What is shown

One row for each Saga, in the order of `~/Artifacts/sagas/INDEX.md`, and on
request one row for each of its Arcs under it:

| Column | What it counts |
|---|---|
| Steps | The leaves of the plans of the Saga's Beats: `## Plan`, or `## Draft plan` before the work starts. A Beat with neither, such as one Done before plans existed, counts as the average of its Saga's Beats that have one, and the Saga's numbers then carry `~` |
| Done | Every step of a Beat whose Linear status is Done, and the ticked steps of every other Beat |
| In progress | The steps not yet ticked of a Beat that is In Progress in Linear, or held |
| Other | Every remaining step: Beats not started, blocked or waiting. Canceled and Duplicate Beats are left out |
| Agents | The holds on the Saga's Beats whose agent is alive: the agents working on it now |
| Context | Those agents' context, added up: the input of each one's last model call, which Claude Code's session file and Codex's thread file record |

A last row, **Not in any Saga**, counts the agents working now that hold no
Beat: Codex threads in the middle of a turn, with their context, and Claude
Code programs that are running, whose context is unknown (see below).

## A run

1. **Statuses from Linear.** For every Arc issue that
   `~/Artifacts/sagas/.linear.json` names, list its sub-issues with their
   identifier and status (the Linear tool's issue list, by parent, with the
   fields `id` and `status`). Write them as one JSON object of identifier to
   status, such as `{"SYL-170": "Done"}`, to a temporary file outside the
   corpus. If Linear cannot be reached, run without it and say that Done then
   counts only Beats whose plan is fully ticked.
2. **Count.** Run
   `python3 -I ~/Artifacts/sagas/tools/radar_stats.py --statuses <file>`.
   Add `--arcs` when the owner asks for Arcs or names a Saga, and `--json`
   when a program reads the result.
3. **Show** the table as printed, in a code block, with its note on `~`.
   Then say in one or two plain sentences what stands out, such as a Saga
   with agents but no step in progress, or agents working outside any Saga.
4. **Change nothing.** No file, no Linear item, no hold.

## Not counted yet

- **Claude Code programs.** From outside, a running `claude` program does not
  show which session it runs, so every running program is counted, and its
  context and whether it works or waits are unknown. A Claude Code session
  that holds a Beat is known exactly, through its hold. The agent records
  that Claude Code's and Codex's hooks will write give every session's state
  and session file; once they exist (the Agent Records Arc in
  `~/Artifacts/sagas/arbol-2-foundation/agent-records/`), the tool reads them
  instead.
- **Agreed metrics not counted yet:** the last 1, 4 and 24 hours of agents,
  context and generated tokens; waiting on the owner; idle lanes (Beats ready
  to take that no agent holds); Subscription headroom.
