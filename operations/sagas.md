---
role: authored
---
# Guide: Working in Sagas

Use this guide to organize work so that several agents can work at the same
time without changing the same files, and so that the owner can see what is
being done, by whom, and what comes next. Work is grouped in three tiers:

- a **[Saga](../../arbol/GLOSSARY.md#saga)** is a direction of work, such as
  building the first parts of Arbol 2;
- an **[Arc](../../arbol/GLOSSARY.md#arc)** is a lane inside a Saga whose
  tasks run one after another, such as the Trivial Trunk;
- a **[Beat](../../arbol/GLOSSARY.md#beat)** is one task, such as one Linear
  issue.

Each Arc lists the folders and files it changes, its *territory*. An agent
that works on a Beat *holds* it, and no other agent starts a Beat whose
territory overlaps a held one. Agents of any tool take part: Claude Code and
Codex, in a terminal or in their apps, and agents that Arbol runs.

This guide is authoritative for how Sagas are kept, territories, holds, and
how a Beat is taken, worked, stopped and finished. The terms are defined in
the [glossary](../../arbol/GLOSSARY.md#saga). The Sagas themselves are files
in the corpus `~/Artifacts/sagas/`: the rules of each Saga's work are in that
Saga's file, and what a Beat must achieve is in that Beat's file.

**Contents:** when to use · where state lives · territories · holds · order
and progress · taking the next Beat · the plan of a Beat · while working ·
stopping and finishing · planning a Saga · not built yet.

## When to use

- The owner says "continue working on tasks", "continue the `<name>` Saga",
  "continue the `<name>` Arc" or "take the next Beat".
- The owner asks to plan new work as a Saga, or to add an Arc or Beats.
- An agent stops or finishes a Beat.

Not for answering the owner's open questions
([Answer Open Questions from Linear](linear-open-questions.md)) or their
comments ([Resolve Linear Comments](linear-resolve.md)).

## Where state lives

| What | Where | Source of truth for |
|---|---|---|
| The list of Sagas | `~/Artifacts/sagas/INDEX.md` | which Sagas there are, and their priority: the order in which they are worked |
| Saga | The file `saga.md` in its folder `~/Artifacts/sagas/<saga>/`, and a Linear project of the same name in the workspace Sylvan Stack | the file: the rules of its work, the recommended order of its Arcs, and the progress of each Arc |
| Arc | The file `arc.md` in its own folder `~/Artifacts/sagas/<saga>/<arc>/`, and a parent issue titled `<Name> Arc` in the Saga's Linear project | the file: its goal, its territory, the recommended order of its Beats, and its progress |
| Beat | The file `<ID>.md` in its Arc's folder, named after its Linear issue (such as `SYL-170.md`), and that issue, a sub-issue of its Arc's issue | the file: what it must achieve, its plan, and its own territory when it names one. Linear: its status, its comments, and what it waits for (*blocked by*) |
| Repository of a Beat | A label of the label group `Repository` | — |
| Hold | One file per held Beat in `~/.sagas/holds/` on this Mac | who works on a Beat right now |

**The files are the originals.** The page in a Saga's Linear project is a
one-way copy of its `saga.md`, the description of an Arc's issue a copy of
its `arc.md`, and the description of a Beat's issue a copy of its file. Each copy starts with a line that names its file. An
edit made only in Linear is overwritten by the next copy. After changing a
file, commit and push it, then bring its copy in line as the corpus's
`README.md` says. `~/Artifacts/sagas/` is a private repository, because it
names the work of every project on this computer.

Specification copies in Linear stay in the projects they are in now. A
project may hold such copies without being a Saga.

Progress is read in Linear: its project list shows how far each Saga is, and
each Arc shows how many of its Beats are done. Each parent also keeps a short
written account of its children, as [Order and progress](#order-and-progress)
says. The live overview of all work,
the [Radar](../../arbol/GLOSSARY.md#radar), is a planned Arbol feature that
will read the same holds.

## Territories

An Arc's territory is a reservation made before work starts, not a record of
the files being edited at the moment. While a Beat is held, no other Beat
whose territory overlaps it may start, even when the two would edit
different files in a reserved folder.

- **Written as full paths, one per line**, in a code block in the section
  `Territory` of the Arc's file. A folder ends with `/`:

  ```
  ~/repos/sylvan-stack/arbol-trunk/trunks/trivial/
  ~/Artifacts/arbol-trunk/trunks/trivial/specs/00-the-trivial-trunk.md
  ```

- **Folders and files, chosen per place.** Hold a whole folder when the
  folder serves only this Arc. In a folder whose files serve different
  purposes, such as a repository's `tests/`, hold only the files the Arc
  needs.
- **A Beat uses its Arc's territory.** So the Beats of one Arc run one after
  another. A Beat may name a smaller territory in a section `Territory` of
  its own file; then two Beats of one Arc may run at once when their
  territories do not overlap.
- **A Saga has no territory of its own.** It is the territories of its Arcs
  together.
- **Overlap:** two territories overlap when an entry of one is the same as,
  or lies inside, an entry of the other: a file inside a held folder, or a
  folder that contains a held file.

### Files every Beat may add to

These files are touched by almost every Beat. Any Beat may **add** a line or
an entry to them without holding them:

- `~/Artifacts/arbol/GLOSSARY.md`;
- the `INDEX.md` and `README.md` tables of every corpus;
- the Linear page "Specifications";
- the Source Ref comments (`<!-- sources: … -->`) at the end of a
  specification section;
- the `Progress` and `Territory` sections of the files in
  `~/Artifacts/sagas/`, as [Order and progress](#order-and-progress) and
  [While working](#while-working) say, and the plan in the file of the Beat
  being worked, as [The plan of a Beat](#the-plan-of-a-beat) says.

Anything more than an addition, such as rewording an entry or correcting a
requirement, needs the file in the Beat's territory.

## Holds

A hold says that an agent works on a Beat now. It is a file
`~/.sagas/holds/<Beat>.json`, for example `~/.sagas/holds/SYL-171.json`,
created in a way that fails when the file already exists, so exactly one
agent can take a Beat. It holds:

```json
{
  "beat": "SYL-171",
  "arc": "<the Arc's issue id>",
  "saga": "<the Saga's folder in ~/Artifacts/sagas>",
  "territory": ["~/repos/sylvan-stack/arbol-trunk/trunks/trivial/"],
  "agent": {
    "tool": "claude-code",
    "session": "<the tool's session or thread id>",
    "owner": { "pid": 48213, "startedAt": "2026-10-15T09:30:00Z" },
    "threadFile": null
  },
  "takenAt": "2026-10-15T09:41:00Z"
}
```

The Linear comment on the Beat is the readable trace; the file decides.

### Who owns a hold

A hold names its owner the way the Driver Contract names the owner of a run
([DRV-6](../../arbol/driver-contract/06-state-and-simultaneous-calls.md)): by
a process number and the time that process was started. The owner is alive
when a process with that number exists and was started at that time, give or
take two seconds, as `ps -o lstart= -p <pid>` prints it. The start time keeps
a new process that happens to get the same number from being taken for the
owner.

| The agent runs in | Its owner | Alive when |
|---|---|---|
| Claude Code, terminal or app | The session's own program: its number is in `CLAUDE_PID`, its session in `CLAUDE_CODE_SESSION_ID` | the process lives |
| Codex, terminal or app | All threads share one program, so the thread is named too: `CODEX_THREAD_ID`, and its record file `~/.codex/sessions/…/rollout-…-<thread id>.jsonl` as `threadFile` | a Codex process has the thread's record file open (`lsof`); Codex keeps it open exactly while the thread is loaded |
| A Chat Exchange of an Arbol Trunk | The Exchange's `record.json` | its process lives, as [RCT-1](../../arbol-root/contract/01-the-exchange-folder.md) says |

<!-- sources:
arbol:driver-contract/06-state-and-simultaneous-calls.md#Knowing that a process is alive
arbol-root:contract/01-the-exchange-folder.md#The record
-->

### What happens to a hold

| The owner… | The hold |
|---|---|
| is gone: its program ended, its thread was closed, or its Exchange ended | is released at the next check |
| waits for the owner's answer | stays |
| waits for a command it runs, however long | stays |
| is silent: no sign of life for 15 minutes while no command runs and no question is open | stays, and is shown as silent; the owner decides |

These are the cases of
[ARC-3 "Slow is not stuck"](../../arbol/architecture/03-stuck-trunks.md#slow-is-not-stuck)
and the Driver's idle limit
([DRV-4](../../arbol/driver-contract/04-errors-and-limits.md#time-limits-of-a-run)).
A silent session is never released, because it may go on and edit files it
no longer holds.

<!-- sources:
arbol:architecture/03-stuck-trunks.md#Slow is not stuck
arbol:driver-contract/04-errors-and-limits.md#Time limits of a run
-->

### The check

Before taking a Beat, an agent checks every file in `~/.sagas/holds/`. For
each hold whose owner is gone, it deletes the file and comments on the Beat:
`**Agent:** Released automatically: <the reason, such as "the Claude Code
session's program ended" or "the Codex thread was closed">.` The Beat keeps
its status: its last `**Agent:**` comment says where the work stopped.

## Order and progress

A parent says in which order its children should be worked, and a child
tells its parent how far it got.

- **A parent recommends the order of its children.** `INDEX.md` gives the
  order of the Sagas, a Saga's file the recommended order of its Arcs, and an
  Arc's file the recommended order of its Beats, each with the reason where
  it is not obvious. The order guides the choice of the
  next Beat. What a Beat must wait for is still a *blocked by* relation, and
  Arcs whose territories do not overlap may run at the same time.
- **A Beat reports to its Arc.** When a Beat is finished or stopped, its agent
  adds one line at the top of the `Progress` section of its Arc's `arc.md`,
  and creates the section if it is missing. The line gives the date, the Beat,
  `Done` or `stopped`, and in a few words what works now and what comes next:

  ```
  2026-10-16 · SYL-170 · Done · the suite's frame and layout.sql; next SYL-171
  ```

- **An Arc reports to its Saga.** When a Beat's end changes what its Arc has
  reached, such as the Arc's first Beat Done, a Beat that another Arc waits
  for Done, or the Arc Done, the agent also rewrites that Arc's one line in
  the `Progress` section of the Saga's file. The line says how many of the
  Arc's Beats are Done, what the Arc has reached, and what comes next. An
  agent changes only its own Arc's line, so two agents that finish at the
  same time do not overwrite each other.
- **Then publish it.** Commit only the files you changed in
  `~/Artifacts/sagas/`, push, and bring their Linear copies in line.

## Taking the next Beat

1. **Choose where to look.** A request that names a Saga or an Arc looks
   there only. Otherwise go through the Sagas in the order of
   `~/Artifacts/sagas/INDEX.md`, and through each Saga's Arcs in the order of
   its `saga.md`.
2. **Read the Saga's file.** Its rules apply to every Beat of the Saga.
3. **Run [the check](#the-check).**
4. **Find the Arc's next Beat:** the first Beat in the order of the Arc's
   file that is not Done. It can start when all of these hold:
   - no hold names it;
   - every Beat it is *blocked by* in Linear is Done;
   - its territory overlaps no hold. A hold of the same Arc counts too,
     unless both Beats name smaller territories that do not overlap.

   When it cannot start, go to the next Arc.
5. **Take it.** Create its hold file. If the file exists, another agent took
   it a moment ago: go back to step 3.
6. **Mark it in Linear.** Set the Beat to In Progress and comment:
   `**Agent:** Took this Beat. <tool> session <id>. Territory: <paths>.`
7. **Write its plan** before any other change, as
   [The plan of a Beat](#the-plan-of-a-beat) says.
8. **Say which Beat you took, and why,** in the first line of the reply. A
   Beat that was In Progress without a hold is taken over: read its comments
   and its plan first, since they say where the work stopped.

When nothing can start, say for each Arc what its next Beat waits for: a Beat
it is blocked by, or a hold and the session that has it.

## The plan of a Beat

The plan is the agent's commitment for its Beat: the steps it will take to
meet the Beat's "Done when", written where the owner, other agents and other
programs can read it. It is not the agent's own working notes. It also
measures progress without guessing sizes: a Beat's progress is how many of
its steps are done out of all of them.

- **A draft when the Beat is created.** The agent that creates a Beat writes
  a section `## Draft plan` in its file, in the same form and with steps of
  the same size as well as it can judge from the specification. It is an
  estimate, not a commitment: it gives the Beat a size before anyone works
  on it.
- **The plan when the work starts.** The agent that takes a Beat writes its
  plan in the Beat's file before any other change, replacing the draft;
  git keeps the draft, so drafts and plans can be compared later. An agent
  that finds a Beat in work without a plan writes it then, with the steps
  already done ticked. Beats that were Done before plans existed get none.
- **A section `## Plan` in the Beat's file.** One step per line, numbered by
  its place in the tree, a sub-step indented two spaces under its parent:

  ```
  ## Plan

  - [x] 1. Write contract/1/layout.sql as RCT-3 gives it
  - [ ] 2. The frame of the conformance suite
    - [x] 2.1 rct-conformance.py with --trunk, --root-contract and --only
    - [ ] 2.2 The home folder and the server of a scenario
    - [ ] 2.3 The stand-in Driver
    - [ ] 2.4 Bring 2.1 to 2.3 together: one scenario runs from start to end
  - [ ] 3. The requirement tables name the checks
  ```

- **A leaf is one safe commit.** A step without sub-steps is a leaf: the
  smallest change that can be committed on its own without breaking
  anything. A feature flag may keep unfinished work switched off. So leaves
  are about the same size in every Beat, and can be counted together across
  an Arc or a Saga: step 1 above counts the same as step 2.2.
- **Ticking.** A leaf is ticked together with its commit. A parent step is
  ticked when all its sub-steps are ticked and the pieces work together.
  When bringing them together is work of its own, it is written as the
  parent's last sub-step, as 2.4 above, so it is counted like any other
  step.
- **Progress** of a Beat is its ticked leaves out of all its leaves: 2 of 6
  above.
- **Keeping it true.** When the work shows that the plan is wrong, change
  the plan in the file first, and say why in the next `**Agent:**` comment.
- **Publishing.** After writing the plan and after each tick, commit the
  Beat's file in `~/Artifacts/sagas/`, push, and bring its Linear copy in
  line.

## While working

- **Grow the territory when needed.** When the Beat needs a file or folder
  outside its territory, add it to the hold if no other hold covers it, and
  to the `Territory` section of the Arc's file, so that later Beats know. When another
  hold covers it, stop the Beat as below and say what it waits for. Never
  edit it anyway.
- **Commit only your own files.** Add the files to a commit by name, never
  "everything". Before each commit, compare the files in it with the hold's
  territory and the files every Beat may add to. A file outside both is not
  committed: grow the territory, or stop.
- **Another Beat's unfinished edits are not yours.** Agents work directly in
  the repository folders, so they see each other's uncommitted changes. A
  check that fails in another Beat's territory is not yours to fix; say so in
  your report.

## Stopping and finishing

- **Stopping in the middle:** follow the Saga's rules (commit what
  works, leave the `**Agent:**` comment that says what is done and what comes
  next), then delete the hold file and end the comment with `Released.`
- **Finishing:** set the Beat to Done as the Saga's rules say, then delete
  the hold file.
- **Either way, report the progress** to the Arc, and when needed to the
  Saga, as [Order and progress](#order-and-progress) says.
- **An Arc is Done** when all its Beats are Done. **A Saga is Done** when the
  owner says so: its line in `INDEX.md` and its Linear project are closed.

## Planning a Saga

- **The owner decides the Sagas** and their priority. An agent proposes the
  Arcs, each with its territory, and the Beats, such as the tasks of an
  accepted specification, and writes them once the owner agrees.
- **A Saga is a folder** `~/Artifacts/sagas/<saga>/` with its `saga.md`: the
  rules of its work, the recommended order of its Arcs, and a `Progress`
  section with one line for each Arc. It has a line in `INDEX.md`, and a
  Linear project of the same name whose page is a copy of `saga.md`.
- **An Arc is a folder** `~/Artifacts/sagas/<saga>/<arc>/` with its `arc.md`:
  its goal and its `Territory`, `Order` and `Progress` sections. It has a
  parent issue titled `<Name> Arc` in the Saga's Linear project, whose
  description is a copy of `arc.md`. `.linear.json` in the corpus names the
  copy of every Saga and Arc file.
- **A Beat is a file** `<ID>.md` in its Arc's folder, and a sub-issue of its
  Arc's issue, labelled with its repository. The file holds what the Beat
  must achieve and its draft plan; the issue's description is its copy. Linear gives the
  identifier, so a new Beat starts as an issue: create it, write its file
  under that identifier, then replace the issue's description with the
  file's copy. What a Beat waits for in another Arc is a *blocked by*
  relation in Linear.
- **Names:** a specific unit is named by its own name followed by its tier
  word, as the [glossary](../../arbol/GLOSSARY.md#saga) says. Use only names
  the owner gave to real work.

## Not built yet

- **One shared record per agent session.** Each tool's own hooks will write
  it: Claude Code's and Codex's hooks, set once in their settings, and
  Arbol's Trunks through their Exchange record. It will say who the agent is,
  its owner, what it waits for and since when, and when it ended. It is
  Arbol's design and still needs its specification. Once it exists, a hold
  names that record, and the check reads it the same way for every tool. It
  will also tell *waiting for the owner* and *silent* apart. Until then the
  owners above are used, and a hold shows neither.
- **The check as a command.** Until it exists, the agent does it by hand:
  `ps -o lstart= -p <pid>` for a process, and `lsof <threadFile>` for a Codex
  thread.
- **Not tried yet:** whether `CODEX_THREAD_ID` is set in a Codex app thread
  and in the codex CLI, and whether the codex CLI in a terminal keeps the
  thread's record file open as the Codex app does.
