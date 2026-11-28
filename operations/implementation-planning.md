---
role: authored
---
# Guide: Planning a Beat

How to write the implementation plan of a [Beat](../../arbol/GLOSSARY.md#beat):
the numbered steps by which its work will be done. This guide owns the
procedure and the standard a plan is held to. It is the sixth stage of the
[Feature Course](../../arbol/GLOSSARY.md#feature-course), and it also runs on
its own when a Beat is taken without a plan. The course as a whole is in
[feature-course.md](feature-course.md); splitting work into Sagas, Arcs and
Beats are in [saga-planning.md](saga-planning.md).
Agents reach this guide through the skill `/plan-beat` (native Codex
`$plan-beat`). The rules come from
[MYC-20](../specs/20-feature-course.md#implementation-plans); where a plan
lives and how Forester marks it are in
[FOR-3](../../forester/specs/03-data-formats.md#marks-in-a-beats-file).

Contents: when to plan · what a step is · the procedure · checking the plan ·
a plan written earlier · changing a plan · what Forester does.

## When to plan

<!-- mycel:cues
type: literal
match: ["plan-beat", "implementation plan"]
cue_target: none
instructions: >-
  When writing, checking or changing a Beat’s implementation plan,
  ~/Artifacts/mycel/operations/implementation-planning.md is required reading.
-->

- Forester answers that the Beat you booked or took has no plan
  ([FOR-D121, FOR-D127](../../forester/decisions.md)).
- A Feature Course reaches Implementation Planning.
- The owner asks for a Beat's plan.

A Beat is planned by one agent at a time. Check
`~/Artifacts/forester/holds.json` before planning. If another live session
holds the Beat, report who holds it and stop. If your session holds the
Beat, keep the booking and continue planning. You can also write the plan
before booking because the Beat's file is a corpus file.

## What a step is

A plan is a `## Plan` section in the Beat's `<ID>.md`: a checkbox tree, one
step per line, numbered by its place, sub-steps indented two spaces.

```markdown
## Plan

- [ ] 1. Specify the reply of `mycel ids next` in MYC-18. Serves MYC-18.2;
      produces the Interface section.
- [ ] 2. Reserve the next number under the series lock.
      Files: `mycel:src/mycel/_ids.py`, `mycel:src/mycel/_cli.py`.
      Serves MYC-18.1, MYC-18.3.
  - [ ] 2.1 …
```

The standard ([FOR-D119](../../forester/decisions.md)):

- **A leaf is one logical, atomic step** in implementing the task: one
  piece of work that makes sense on its own and is finished in one go. It is
  neither so big that it hides several decisions nor so trivial that it is
  a line of another step. A small change gets a step of its own when its
  impact is large, so that it stands out as one logical unit.
- **As many steps and levels as the work needs.** Beats differ in size;
  there is no default number or depth. Three levels, `4.1.3`, are fine when
  the work is that deep.
- **Delivery steps.** Use steps for the agreed implementation and the work
  needed to produce its deliverable, including compilation, packaging or
  installation where applicable. No step needs a commit that names it.

- **A code step names its files**, as `<repo>:<path>`, and the requirements
  or decisions it serves, such as `MYC-18.1` or `FOR-D124`. These become the
  `--files` and `--origin` of the step's Intention. A step is never itself
  an Origin ([FOR-D114](../../forester/decisions.md)).
- **Any other step says what it produces.**
- **Keep verification outside the plan.** The [delivery workflow](../../forester/operations/sagas.md#scope-and-completion)
  governs tests, qualification and optional follow-up.

- **Steps are in the order they will be done.**

## The procedure

1. **Read the inputs.**
   - The Beat's goal, and the requirements and decisions it owns, in the
     specification itself, not only in the Beat's summary.
   - The Arc's `## Approach` and `### Order`: where the Beat sits and what
     it waits for.
   - The hand-overs of the Beats it waits for, which say what was built.
   - The Owner Goals that apply: `goals list` (see
     [owner-goals.md](owner-goals.md)).
   - The feature's research document, if a Feature Course wrote one.
2. **Look for gaps in the specification.** List what the Beat will make
   happen. A behaviour no specification states is a gap: stop planning,
   tell the owner what is missing with a proposed answer, and continue only
   once the specification says it (Spec Writing). Never settle such a choice
   in a step.
3. **Research the code** of the Beat's part of the system, at the level the
   question needs ([code-research-levels.md](code-research-levels.md)).
   Reuse the feature's research document instead of repeating it. Find the
   files each change will touch and how they work today. A finding enters
   the Beat only where it shapes a step.
4. **Write the steps** to the standard above.
5. **Plan the User Demo, if the Beat has one.** When the Beat builds
   something a Leather Bag can see or follow, a screen or business logic
   whose effect they can watch, write a `## User Demo` section after the
   plan: a short scenario following the specification's use case, with the
   status `not_implemented`. It is optional, it is not a plan step, and it
   never keeps the Beat open. [User Demos](../../forester/operations/user-demos.md#writing-the-demo)
   gives the form and when a Beat has none.
6. **Write the territory.** The Beat's `## Territory` is the files and
   folders its code steps name, as `<repo>:<path>`; a folder ends in `/`.
   Keep files that many agents change, such as an `AGENTS.md`, out of it
   (they are booked briefly, as [Working in Sagas](../../forester/operations/sagas.md)
   says).
7. **Declare the plan done**: commit and push the Beat's file in the
   Forester corpus with the subject `<saga>/<arc>/<ID>: plan`. If you are
   continuing into implementation, check that your booking covers the
   planned code paths. Keep an existing booking that covers them, or
   reserve the needed paths under [Working in Sagas](../../forester/operations/sagas.md#book-code-before-changing-it).
   Then start step 1. If you only planned, hand over the Beat.

## Checking the plan

Write an actionable plan from the agreed requirements and the source needed
to implement them. Give Forester the numbered leaves, files and Origins it
uses. Resolve a concrete formatting or Origin error if it blocks a Step
Intention. The plan can proceed as soon as it has the information needed to
implement the Beat. Review and verification are separate from delivery.

## A plan written earlier

Read relevant predecessor hand-overs as part of the work. Update remaining
steps when their implementation needs to change.

## Changing a plan

A plan may change while the Beat is in work ([FOR-D56](../../forester/decisions.md)).

- Ticked steps stay exactly as they are.
- The step of the open Intention stays; close the Intention first if it
  must change.
- Any other step may be changed, renumbered, split or removed.
- New files outside the territory join it with the Intention that needs
  them (`forester intend --widen`); note the widening in the Territory.
- Add one line under the plan saying what changed and why.

## What Forester does

`forester intend --step <n>` requires an unticked leaf of the plan. If
the plan is missing, Forester tells you to write it first. When you book a Beat
without a plan, Forester directs you to `/plan-beat` (`$plan-beat` in native
Codex) to write it ([FOR-D121, FOR-D127](../../forester/decisions.md)). The agent ticks each step until
`forester step --done` is built
([Working in Sagas](../../forester/operations/sagas.md)).

<!-- sources:
forester:@code/src/forester/intention.py#_step_problem
forester:@code/src/forester/booking.py#plan_guidance
-->

