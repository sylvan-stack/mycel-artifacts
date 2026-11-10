---
role: authored
spec: MYC-20
status: accepted
---
# Mycel · 20 The Feature Course

## Purpose

A new feature in a [Mycel-enabled](../../arbol/GLOSSARY.md#mycel-enabled)
repository should start as a conversation and end as Beats that an agent can
implement, with nothing implemented that no specification says. The
[Feature Course](../../arbol/GLOSSARY.md#feature-course) is that path. The
owner talks about the feature in their own words; the agent researches the
code, writes the specification, plans the Sagas, Arcs and Beats, and writes
each Beat's implementation plan. Mycel holds what the course knows: its
stages, the standards of its documents and the procedures, as guides, skills
and one command. [Forester](../../arbol/GLOSSARY.md#forester) only enforces
its rules ([FOR-1](../../forester/specs/01-forester.md)).

## Scope

From the owner's first words about a feature to Beats with plans, and the
review that closes each Arc. Out of scope: implementing a Beat
([Working in Sagas](../../forester/operations/sagas.md)), testing
([Test Strategy](../operations/test-strategy.md)), and what Forester checks
and records ([FOR-1](../../forester/specs/01-forester.md#2--planning) and
[FOR-3](../../forester/specs/03-data-formats.md)).

## Behaviour

### The six stages

| # | Stage | What happens | Its result |
|---|---|---|---|
| 1 | [Idea Discussion](../../arbol/GLOSSARY.md#idea-discussion) | The owner describes the feature in any form; the agent asks and restates | the idea, clear enough to research |
| 2 | [Initial Research](../../arbol/GLOSSARY.md#initial-research) | The agent studies the current architecture and the related code, with file-and-line evidence | the feature's research document |
| 3 | [Feature Triage](../../arbol/GLOSSARY.md#feature-triage) | The owner adds requirements, limits and priorities; the agent works out what the feature reuses, changes or conflicts with, researching again as needed | the research document, extended |
| 4 | [Spec Writing](../../arbol/GLOSSARY.md#spec-writing) | The agent writes or extends a specification | Spec Requirements and Decisions |
| 5 | [Saga Planning](../../arbol/GLOSSARY.md#saga-planning) | The Saga Planner splits the specified work into Sagas, Arcs and Beats | Sagas and Arcs with their Approaches, and Beats |
| 6 | [Implementation Planning](../../arbol/GLOSSARY.md#implementation-planning) | The agent writes Beats' implementation plans | Beats with plans |

Stages 1 to 3 may repeat in any order until the feature is understood; each
answer of the owner may send the agent back into the code. Nothing is
planned from what no specification says: a behaviour the specification lacks
sends the work back to stage 4, and only the owner decides it. A Beat's plan
may also be written later, when the Beat's implementation starts
([FOR-D121](../../forester/specs/01-forester.md#3--steering)).

### Saga Planning

1. **Read** the specification's requirements and decisions and the feature's
   research document.
2. **Choose the Saga.** Among the Sagas that are not Done, extend the one
   whose goal already covers this kind of work; otherwise create a Saga.
3. **Choose the Arcs.** Put work in an existing Arc that is not Done when it
   belongs to the same part of the system; otherwise create Arcs, split so
   that each works mostly in files of its own and all can run in parallel.
4. **Find dependencies.** Sagas and Arcs that are ready never wait for each
   other. Where an Arc truly needs another's result, first split off the part
   that is needed, so that the rest stays independent; failing that, the Arc
   depends on a whole Saga or Arc being Done, never on a single Beat, and has
   the status Depends On.
5. **Write** the Beats whose requirements are fully described (FOR-D34), the
   [Approach](../../arbol/GLOSSARY.md#approach) of every Saga and Arc, and in
   each Arc's Approach the `### Order` of its Beats
   ([FOR-3](../../forester/specs/03-data-formats.md#the-order-of-an-arcs-beats)).
   The last Beat of each Arc tests its work (FOR-D120). Foreseen work stays in
   the Approach's prose.
6. **Check** that no dependency forms a loop, that no ready unit waits for
   anything, and that Beats wait only for Beats of their own Arc.
7. **Ask the owner** to confirm a new Saga and its priority in the Sagas'
   `INDEX.md`. Nothing else in Saga Planning needs the owner's approval.

A Done Saga or Arc is never reopened: new work gets a new one, which links
to the old.

### Statuses of Sagas and Arcs

A status line under the title of `saga.md` and `arc.md` holds one of these
([FOR-D124](../../forester/specs/01-forester.md#2--planning)):

| Status | Meaning | Set by |
|---|---|---|
| Draft | still being planned; nothing can be taken | the planner |
| Depends On | waits for the named Sagas or Arcs to be Done | the planner; Forester lifts it |
| Ready to Plan | a Beat can start now, but has no plan yet | Forester, computed |
| Partly Ready | a Beat with a plan can start now, but the unit cannot be finished in one run | Forester, computed |
| Fully Ready | every unfinished Beat has a plan and waits only for Beats inside the unit | Forester, computed |
| In Review | the Arc has finished its Beats and its review runs, or the Saga has finished its Beats and an Arc is in review | Forester |
| Ready to Close | all Arcs of the Saga are Done and the owner has yet to close the Saga | Forester |
| Done | an Arc: its review passed; a Saga: the owner closed it | the reviewer; the owner |

When several Ready statuses apply, the strongest is shown with the number of
Beats that still need a plan, so that planning work stays visible.

### Implementation plans

A Beat's plan is a checkbox tree in its `## Plan` section
([FOR-3](../../forester/specs/03-data-formats.md#marks-in-a-beats-file)).
What a step is was decided as FOR-D119:

- A leaf is one logical, atomic step in implementing the task, neither too
  big nor trivial. A small change gets a step of its own when its impact is
  large, so that it stands out as one logical unit.
- A plan has as many levels and steps as its planning gives it. Beats differ
  in size; there is no default number or size of steps.
- A step may be of any kind, and no step needs a commit that names it.
- A step that changes code names the files it expects to change and the
  requirements or decisions it serves, so that `forester intend --origin`
  can be filled from it. Another step says what it produces: a
  specification row, an owner's acceptance, a hand-over.
- The Beat's territory is the union of the files its code steps name.
- No step tests; testing is the Arc's last Beat (FOR-D120).

### Planning a Beat

The procedure starts when Forester answers that a Beat has no plan
(FOR-D121), when a Feature Course reaches stage 6, or when the owner asks.

1. **Read the inputs:** the Beat's goal and the requirements and decisions it
   owns; the Arc's Approach; the hand-overs of the Beats it waits for; the
   Owner Goals that apply; the feature's research document.
2. **Look for gaps in the specification.** A behaviour the Beat would build
   that no specification states stops planning and goes back to Spec Writing.
3. **Research the code** of the Beat's part of the system, reusing the
   feature's research document. Findings enter the Beat only where they shape
   a step.
4. **Write the steps** to the standard above, in the order they will be done.
5. **Write the territory** from the files the code steps name.
6. **Check the plan:** `mycel plan check` for its form, files and
   identifiers; then a reviewer with fresh context reads it against the
   standard and records `accepted` or its numbered problems in the Beat's
   file. Problems are fixed and the review repeated.
7. **Declare the plan done** and commit the Beat's file.

A plan written in the Feature Course is checked again when an agent takes
its Beat, since earlier Beats may have changed the code; it is amended if it
no longer fits, ticked steps unchanged. Forester checks only that a plan
exists; its quality is Mycel's standard and the reviewer's judgement.

### The Arc Review

When an Arc's last Beat, its testing Beat, is finished, the Arc is In Review
and Forester makes the action item "review Arc" (FOR-D126). A session that
took none of the Arc's Beats reviews the Arc's combined result: whether its
commits together do what its Approach and its Spec Requirements say. It ends
with the Arc Done, or with its findings as new Beats in the Arc's `### Order`,
a fix Beat and a new testing Beat, after which the review runs again. A Saga
has no review of its own.

### Where the course lives

| Part | Form |
|---|---|
| The course and its stages 1 to 4 | the guide `operations/feature-course.md` |
| Saga Planning and the Arc Review | the guide `operations/saga-planning.md` |
| Planning a Beat | the guide `operations/implementation-planning.md` and the skill `/plan-beat`, for Claude Code and native Codex |
| The plan's deterministic check | `mycel plan check` |
| The feature's research document | the repository's resolved corpus, as the [deep-research guide](../operations/deep-research.md) places it |

## Requirements

| ID | Mycel shall | From v1 | Verified by |
|---|---|---|---|
| MYC-20.1 <!-- 6bee7157-80d8-4a7d-bdc8-242b513532dc --> | provide a guide that leads an agent with the owner through the six stages of the Feature Course, from Idea Discussion to Implementation Planning, letting stages 1 to 3 repeat | New | review |
| MYC-20.2 <!-- 0190fb7d-135d-4820-a367-3c821c8d4441 --> | keep the findings of Initial Research and Feature Triage in one research document of the feature in the repository's resolved corpus, with file-and-line evidence, for the later stages and Beats to read | New | review |
| MYC-20.3 <!-- 74b49f92-0e31-4e39-bcc8-353670f0dbd3 --> | let no Saga, Arc, Beat or plan be written for behaviour that no specification states, and send such a gap back to Spec Writing for the owner's decision | New | review |
| MYC-20.4 <!-- 26fc1dc3-6e3e-4f32-84d3-a66d69468f2b --> | in Saga Planning, extend a related Saga or Arc that is not Done before creating one, and never reopen a Done Saga or Arc | New | review |
| MYC-20.5 <!-- ed957522-f7fc-4373-b6f9-52678facaf8f --> | in Saga Planning, split work so that ready Sagas and Arcs never wait for each other, and record any remaining dependency as the status Depends On, on whole Sagas or Arcs being Done | New | review |
| MYC-20.6 <!-- bc360ba8-ca83-4c62-9f5c-aa27abf81b2c --> | write an Approach for every Saga and Arc, giving in each Arc's Approach the `### Order` of its Beats, with the Arc's testing Beat last | New | review |
| MYC-20.7 <!-- 6c7b683d-3825-4bc6-ab2e-e337c532de65 --> | keep a Saga or Arc Draft until its Approach and Beats are written, and ask the owner to confirm only a new Saga and its priority | New | review |
| MYC-20.8 <!-- 6cd116e3-0a48-40a8-9fcc-2ba5c4892cc7 --> | hold implementation plans to the standard of FOR-D119: logical, atomic leaves of any kind, with no default number or depth of steps and no testing step | New | review |
| MYC-20.9 <!-- 41578b42-b3b3-4bbf-a626-829408c9221a --> | have each code step of a plan name the files it expects to change and the requirements or decisions it serves, and derive the Beat's territory from those files | New | review |
| MYC-20.10 <!-- 482f87a8-4eab-40a8-b8ce-2374af0cddaa --> | provide the guide and the skill `/plan-beat` for planning a Beat, for Claude Code and native Codex, to which Forester's answer for a Beat without a plan points | New | review |
| MYC-20.11 <!-- 1427d1e7-2dbc-4069-ac3a-7a20d07b1cd9 --> | have a reviewer with fresh context accept a plan, or record its numbered problems in the Beat's file, before the plan is declared done, without the owner's approval | New | review |
| MYC-20.12 <!-- b77d1bc4-17a3-41ad-b1f2-e9c07c871fd8 --> | check a plan again when its Beat is taken, and amend it with its ticked steps unchanged when it no longer fits | New | review |
| MYC-20.13 <!-- 2d75fc11-3e17-4efb-b417-ea69f3c0dd3a --> | report, for a Beat's file, every problem of its plan's form, every file a code step names that neither exists nor has an existing folder, and every named requirement or decision that resolves to no entity, without a model and without changing anything | New | unit |
| MYC-20.14 <!-- 1eddb8cc-5ae8-4a78-956c-96d2b227589c --> | have the Arc Review done after the Arc's testing Beat by a session that took none of its Beats, ending in Done or in new Beats that include a testing Beat | New | review |

## Interface

```sh
mycel plan check ~/Artifacts/forester/sagas/cellar/retries/policy/SYL-900.md
```

The reply names the Beat and its steps, and lists problems, each with the
step's number, a kind (`form`, `file` or `origin`) and a detail. An empty list
means the plan passes. A file is read from the repository's configured code
checkout; an identifier such as `MYC-20.9` or `FOR-D119` resolves through the
Index Store's requirement and decision entities (MYC-17).

## Known problems

Most requirements are met by guides and skills, which no automated check
verifies; they are checked by the kind `review` (MYC-D81). Forester's statuses,
readiness and Arc Review action item are specified in FOR-1 and not yet
built.

## Decisions

| ID | Question | Outcome |
|---|---|---|
| MYC-D77 <!-- 5285b58d-47ff-497c-88a7-0a2c053aa771 --> | Is the Feature Course Mycel's or Forester's? | Decided by the owner on 9 November 2026: "This is not Forester but Mycel feature. Mycel has knowledge and Forester just enforce rules and processes." The course is the everyday way to develop any feature in a Mycel-enabled repository, and every feature has a specification before it is implemented. |
| MYC-D78 <!-- c338857a-827a-4f68-ba2d-ff2c59f5976d --> | How is a Beat planned? | Decided by the owner on 9 November 2026 ("Agreed"), accepting the agent's seven proposals: a specification gap stops planning; a code step names its files and the requirements or decisions it serves; a reviewer with fresh context judges the plan and Forester checks only that it exists; the owner does not approve plans; `mycel plan check` comes as a later Beat; a guide with the skill `/plan-beat`, and a separate Saga Planning guide; the rules are specified here. |
| MYC-D79 <!-- 4db3c315-39f1-4ab9-8086-15efbfb382f8 --> | How are Sagas and Arcs planned? | Decided by the owner on 9 November 2026: an agent first looks for an existing Saga the feature belongs to, else creates one, then decides between existing and new Arcs; ready Sagas and Arcs can run in parallel, and a dependency is allowed only through a status that keeps the unit out of work until it is resolved; "splitting feature into sagas/arcs and thinking about order and dependencies is the main function of planning process". The agent's proposals accepted the same day: dependencies on whole Sagas or Arcs only, Done units never reopened, the owner confirms new Sagas and their priority. |
| MYC-D80 <!-- f2d31b01-f2b5-47c7-8111-7d6b31762675 --> | Which statuses do Sagas and Arcs have, and when is an Arc Done? | Decided by the owner on 9 November 2026: three Ready statuses, for a unit with one Beat ready, a unit that can be worked from start to end without stopping, and a unit that still needs plans; an Arc is not closed only because its Beats are Done, but after a critical review by a fresh agent. The agent's proposals accepted the same day ("Agreed"): the statuses of the table above, the strongest Ready shown with the number of Beats needing plans, the review after the testing Beat, no Saga review. |
| MYC-D81 <!-- 6a82b51f-9759-4018-b34a-c6e5c2bf0f6c --> | How is a requirement met by a guide or skill verified? | Decided by the owner on 9 November 2026 ("Accept review kind"), accepting the agent's proposal: a new kind of check, `review`, in which the owner or a reviewer with fresh context reads the guide or skill against the requirement; the Named checks section names who read it and when. |
| MYC-D95 <!-- caa1b304-c0dd-4439-a395-bdca86dd4471 --> | What does a Saga show between its last Beat and closure? | Decided by the owner on 10 November 2026. Once all its Beats are finished, the Saga shows In Review while an Arc is in review and then Ready to Close when all its Arcs are Done. The owner alone closes it. Extends MYC-D80. Forester refreshes the status under [FOR-D133](../../forester/specs/01-forester.md#2--planning). |
