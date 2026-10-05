---
role: blueprint
name: deep-research
summary: Long-running multi-angle research producing or updating ref-carrying research artifacts
inputs:
  - name: repo
    type: repo
    required: true
  - name: ticket_dir
    type: string
    required: false
    description: ticket workspace (ticket mode) — its ticket.md/objectives.md/code-scout.md are the brief; give this or topic
  - name: topic
    type: string
    required: false
    description: the task or domain to build context for (topic mode) — required when ticket_dir is not given
  - name: depth
    type: enum [survey, standard, exhaustive]
    required: false
    default: standard
outputs:
  - artifact: "{ticket_dir}/research.md — or ~/Artifacts/{repo}/research/{slug(topic)}.md in topic mode"
    must: [source-refs-resolve, every-claim-referenced, open-questions-listed]
done_when: the artifact exists (or an existing one was updated), every claim
  carries a resolving Source Ref, all planned angles are covered or carried as
  explicit open questions, and the update-don't-duplicate rule was honored
restrictions: [no-repo-edit, no-git-mutations]
recipe: inherit          # hard pin; "inherit" = defer to caller/default
default-recipe: bro-opus-max
---
# Blueprint: Deep Research

Level 4 of the research ladder
([code-research-levels](../operations/code-research-levels.md)): reach for it
when the deliverable is an **artifact**, not a chat answer, and the scope is a
**task**, not a question.

## Goal

Durable task context: everything the topic touches — implementation, data
flow, configuration, cross-repo edges — persisted as a research artifact that
future sessions and retrieval bridges build on instead of rediscovering.

## Process

1. **Read the brief.** With `ticket_dir`: read `ticket.md`, `objectives.md`,
   `jira-context.md`, and `code-scout.md` — this folder IS your research
   brief. The **objectives drive the angles** (step 3); the scout doc tells
   you where to dig first (never rediscover what it already located); the
   context doc carries constraints and decisions from Jira/Confluence. With
   `topic` only: the topic string is the brief. If neither `ticket_dir` nor
   `topic` is bound, stop with an error instead of inventing a brief.
2. **Consume Mycel first.** Query Mycel directly with `mycel search
   --repo {repo} --only code "<the question, as asked>"` and read the repo's
   surfaced research/glossary docs before exploring by hand. Prior research
   surfaced via bridges is context to build on, not to rediscover. Mycel is the
   retrieval owner; do not route this step through an Arbol command or service.
3. **Plan the angles.** Decompose the topic into research angles
   (implementation, data flow, config/feature toggles, tests, cross-repo
   edges, history). Depth binds the plan: `survey` = the 2–3 load-bearing
   angles; `standard` = every main angle; `exhaustive` = edge cases, error
   paths, and history included.
4. **Research each angle** with the level-3 loop
   ([code-research](../operations/code-research.md)): retrieval-first,
   `better-grep` for exactness and absence claims, widening only where
   retrieval runs dry. Every finding is backed by code evidence — a 3–15 line
   snippet with path and line range.
5. **Evaluate and loop.** After each angle, check it against the Quality bar;
   an angle that misses gets another iteration. An angle that stays dry after
   honest effort becomes an explicit open question, never a silent omission.
6. **Persist the research.** Follow the
   [authoring guide](../operations/source-refs-authoring.md). In ticket
   mode write `{ticket_dir}/research.md`; in topic mode write to
   `~/Artifacts/{repo}/research/`. Updating an existing research doc beats
   creating a sibling — it repairs drift and keeps the corpus curated; new
   documents are for genuinely new topics.

## Output contract

- Lead with a summary a task-executor can act on without reading the rest.
- One section per angle, each claim carrying [Source
  Refs](../../arbol/GLOSSARY.md#source-ref) — refs point at **files** (optionally
  `#Symbol`); directory refs resolve to no edges.
- An **Open questions** section listing what was not established and why.

## Quality bar

Before declaring done, verify `done_when` honestly:

- every claim traces to a resolving Source Ref;
- no planned angle is silently missing — covered or an open question;
- an existing doc was updated rather than duplicated, where one existed;
- the artifact is retrievable by its own vocabulary (jargon the code never
  spells out earns a glossary entry with refs, per the
  [embedding habits](../operations/embedding.md)).

## Manual run (degraded mode)

State the input bindings ("repo=Arbol, topic=withdrawal limits,
depth=standard"), follow Process top to bottom, and self-check `done_when`
before reporting completion. This is how every run works today.

<!-- sources:
mycel:mycel/knowledge/embedder.py#code_search
mycel:tools/mycel.md
mycel:tools/better-grep.md
-->

## Output

Your final message must report the artifact you wrote — a clickable markdown link to it (absolute path), plus the 2–3 findings that most change how the work should proceed. Do not paste the file's contents back.
