---
role: authored
---
# Guide: Deep Research (level 3)

Long-running research that **produces or updates a research artifact** —
task-context building, multi-angle coverage of everything a task might touch.
Level 3 of [code-research-levels](code-research-levels.md): reach for it when
the deliverable is an *artifact* (not a chat answer) and the scope is a
*task*, not a question.

This guide is authoritative for the inputs, the process, the output and the
quality bar. An agent runs it in its own session, from top to bottom.

## Goal

Durable task context: everything the topic touches — implementation, data
flow, configuration, cross-repository edges — persisted as a research
artifact that later sessions and retrieval bridges build on instead of
rediscovering.

## Inputs

State the bindings before starting (`repo=<repo>, topic=<topic>,
depth=standard`).

| Input | Required | Meaning |
|---|---|---|
| `repo` | yes | The repository whose code and corpus are researched |
| `topic` | yes | The task or domain to build context for |
| `depth` | no, default `standard` | `survey`, `standard` or `exhaustive` |

If the request names no topic, stop and ask instead of inventing a brief.

## Constraints

- Research only. Do not edit the repository under research and do not change
  its Git state.
- Every finding is backed by code evidence. A claim that cannot be shown is
  an open question, not a finding.

## Process

1. **Consume Mycel first.** Run `mycel search --repo <repo> "<the question,
   as asked>"` and read the research and glossary documents it surfaces
   before exploring by hand. Prior research is context to build on, not to
   rediscover.
2. **Plan the angles.** Decompose the topic into research angles:
   implementation, data flow, configuration and feature toggles, tests,
   cross-repository edges, history. Depth binds the plan: `survey` covers the
   two or three load-bearing angles; `standard` covers every main angle;
   `exhaustive` adds edge cases, error paths and history.
3. **Research each angle** with the [code-research](code-research.md) loop:
   retrieval first, `better-grep` for exactness and for claims of absence,
   widening only where retrieval runs dry. Each finding carries a 3–15 line
   snippet with its path and line range.
4. **Evaluate and loop.** After each angle, check it against the quality bar.
   An angle that misses gets another iteration. An angle that stays dry after
   honest effort becomes an explicit open question, never a silent omission.
5. **Persist the research.** Follow the
   [Source Refs authoring guide](source-refs-authoring.md) and write to
   `research/` under the repository's artifact root; resolve it first, see
   [repository corpus binding](../tools/mycel.md#repository-corpus-binding).
   Updating an existing research document beats creating a sibling: it
   repairs drift and keeps the corpus curated. New documents are for
   genuinely new topics.

## Output contract

- Lead with a summary a task executor can act on without reading the rest.
- One section per angle, each claim carrying
  [Source Refs](../../arbol/GLOSSARY.md#source-ref). Refs point at **files**,
  optionally with `#Symbol`; directory refs resolve to no edges.
- An **Open questions** section listing what was not established and why.

## Quality bar

Before reporting completion, check honestly:

- every claim traces to a resolving Source Ref;
- no planned angle is silently missing — each is covered or carried as an
  open question;
- an existing document was updated rather than duplicated, where one existed;
- the artifact is retrievable by its own vocabulary: jargon the code never
  spells out earns a glossary entry with refs, per the
  [embedding habits](embedding.md#the-compounding-habits).

## Reporting

The final message links to the artifact that was written or updated and names
the two or three findings that most change how the work should proceed. Do
not paste the file's contents back.
