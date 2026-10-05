---
role: authored
---
# Guide: Deep Research (level 4)

Long-running background research that **produces or updates research
artifacts** — task-context building, multi-angle coverage of everything a task
might touch. Level 4 of [code-research-levels](code-research-levels.md): reach
for it when the deliverable is an *artifact* (not a chat answer) and the scope
is a *task*, not a question.

**Defined by the [deep-research Blueprint](../blueprints/deep-research.md)** —
the first [Blueprint](../../arbol/GLOSSARY.md#blueprint): inputs/outputs, process, and
quality bar live there. Single source — this doc is only the research
ladder's entry point.

## Running it today

Run detached via `blueprint run deep-research --input k=v` — or **manually**: an agent
reads the Blueprint, binds the inputs, follows its Process, and self-checks
`done_when`. The automated engine — and the plan → execute → verify
[Blueprint Chain](../../arbol/GLOSSARY.md#blueprint-chain) that will gate quality —
is designed in [plans/blueprints.md](../../arbol_deprecated_v1/plans/blueprints.md) and parked with
[plans/deep-research-engine](../../arbol_deprecated_v1/plans/deep-research-engine.md). The Cursor-era
engine remains archived: [snapshot](archive/deep-research-cursor-era.md).
