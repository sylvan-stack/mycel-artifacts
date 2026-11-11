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
Beats, and the Arc Review, are in [saga-planning.md](saga-planning.md).
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
- **Steps of any kind.** Code, a specification row, the owner's acceptance,
  a guide, a hand-over. No step needs a commit that names it.
- **A code step names its files**, as `<repo>:<path>`, and the requirements
  or decisions it serves, such as `MYC-18.1` or `FOR-D124`. These become the
  `--files` and `--origin` of the step's Intention. A step is never itself
  an Origin ([FOR-D114](../../forester/decisions.md)).
- **Any other step says what it produces.**
- **No testing step in an implementation Beat.** Testing is the Arc's last
  Beat and starts under the usual Beat eligibility rules. See the
  [Test Strategy](test-strategy.md#when-testing-starts).
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
5. **Write the territory.** The Beat's `## Territory` is the files and
   folders its code steps name, as `<repo>:<path>`; a folder ends in `/`.
   Keep files that many agents change, such as an `AGENTS.md`, out of it
   (they are booked briefly, as [Working in Sagas](../../forester/operations/sagas.md)
   says).
6. **Check the plan** (next section).
7. **Declare the plan done**: commit and push the Beat's file in the
   Forester corpus with the subject `<saga>/<arc>/<ID>: plan`. If you are
   continuing into implementation, check that your booking covers the
   planned code paths. Keep an existing booking that covers them, or
   reserve the needed paths under [Working in Sagas](../../forester/operations/sagas.md#book-code-before-changing-it).
   Then start step 1. If you only planned, hand over the Beat.

## Checking the plan

**Deterministic check.** `mycel plan check <Beat file>` reports problems of
form, files a code step names that neither exist nor have an existing folder,
and requirements or decisions that resolve to nothing (MYC-20.13). Until the
command is released (SYL-349), make the same three checks by hand: the tree
parses and its numbers match their places; every named file or its folder
exists in the repository's configured checkout; every named ID is a row of a
specification or a decision index.

**Review with fresh context.** Give a reviewer that took no part in writing
the plan the Beat's file, this guide and the specification rows the Beat
owns: a subagent of your session, or another session. Ask for a verdict,
`accepted` or numbered problems, each tied to a step, against the standard
above and against the Beat's requirements: is every owned requirement
covered, and is nothing planned outside the Beat's goal? Do not hand the
reviewer your own reasoning; it reads the plan cold. Fix the problems and ask
again until it accepts. Record the verdict under the plan:

```markdown
Plan review · 9 November 2026 · accepted after one round (2 problems fixed:
step 3 split in two; step 5 now names its files).
```

The owner does not approve plans. The owner is asked only about a gap in
the specification.

## A plan written earlier

A plan written in a Feature Course, or by an agent that stopped, may be
stale when the Beat is taken: the Beats it waited for have changed the code
since. Before step 1, check it again: read the hand-overs of the Beats
finished since the plan was written, confirm the named files and IDs still
hold (the deterministic check), and confirm the steps still fit the code. If
they do not, change the plan as below.

## Changing a plan

A plan may change while the Beat is in work ([FOR-D56](../../forester/decisions.md)).

- Ticked steps stay exactly as they are.
- The step of the open Intention stays; close the Intention first if it
  must change.
- Any other step may be changed, renumbered, split or removed.
- New files outside the territory join it with the Intention that needs
  them (`forester intend --widen`); note the widening in the Territory.
- Add one line under the plan saying what changed and why, and run the
  fresh-context review again on the changed steps only.

## What Forester does

Forester checks only that a plan exists. Today `forester intend --step <n>`
refuses a Step Intention when the Beat's file has no `## Plan` section, or no
unticked leaf *n*, and says to write the plan first. When you book a Beat
without a plan, Forester directs you to `/plan-beat` (`$plan-beat` in native
Codex) to write it ([FOR-D121, FOR-D127](../../forester/decisions.md)). The
reviewer judges the plan against this guide. The
agent ticks a step itself until `forester step --done` is built
([Working in Sagas](../../forester/operations/sagas.md)).

<!-- sources:
forester:@code/src/forester/intention.py#_step_problem
forester:@code/src/forester/booking.py#plan_guidance
-->

