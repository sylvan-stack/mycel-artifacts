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

**Contents:** when to use · where state lives · territories · prepared
folders · holds · order and progress · taking the next Beat · the plan of a
Beat · the hand-over of a Beat · while working · stop criteria of a Beat ·
stopping and finishing · reviewing a Beat, an Arc or a Saga · planning a
Saga · not built yet.

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
| The list of Sagas | `~/Artifacts/sagas/INDEX.md` | which Sagas there are, their priority: the order in which they are worked, and which Sagas each one waits for |
| Saga | The file `saga.md` in its folder `~/Artifacts/sagas/<saga>/`, the documents beside it, and a Linear project of the same name in the workspace Sylvan Stack | the files: `saga.md` holds the recommended order of its Arcs, the progress of each Arc, what it waits for in other Sagas and what they wait for in it, and what each of its documents holds; `rules.md` the rules of its work; further documents what one task needs, such as its known gaps |
| Arc | The file `arc.md` in its own folder `~/Artifacts/sagas/<saga>/<arc>/`, and a parent issue titled `<Name> Arc` in the Saga's Linear project | the file: its goal, its territory, the recommended order of its Beats, and its progress |
| Beat | The file `<ID>.md` in its Arc's folder, named after its Linear issue (such as `SYL-170.md`), and that issue, a sub-issue of its Arc's issue | the file: what it must achieve, its plan, its hand-over to later Beats, and its own territory when it names one. Linear: its status, its comments, and what it waits for (*blocked by*) |
| Repository of a Beat | A label of the label group `Repository` | — |
| Hold | One file per held Beat in `~/.sagas/holds/` on this Mac | who works on a Beat right now, and in which prepared folder |
| A Beat's code | The branch `beat/<Beat>` in each repository its territory touches, worked in a prepared folder and merged into `main` as one merge commit | exactly what the Beat changed in code, whichever tool, session or kind of edit made the change |

**The files are the originals.** The page in a Saga's Linear project is a
one-way copy of its `saga.md`, each other document of the Saga a document in
the same project, the description of an Arc's issue a copy of
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
- the `Progress`, `Territory` and `Other Sagas` sections of the files in
  `~/Artifacts/sagas/` and the table of `INDEX.md` there, as
  [Order and progress](#order-and-progress) and
  [While working](#while-working) say, and the plan in the file of the Beat
  being worked, as [The plan of a Beat](#the-plan-of-a-beat) says, and its
  hand-over, as [The hand-over of a Beat](#the-hand-over-of-a-beat) says.

Anything more than an addition, such as rewording an entry or correcting a
requirement, needs the file in the Beat's territory.

## Prepared folders

A Beat's code is changed on a branch of its own, `beat/<Beat>` such as
`beat/SYL-173`, in a *prepared folder*: a folder holding one clone of every
repository, set up once, environments included, and kept from one Beat to the
next. The owner decided this on 16 October 2026, so that many agents can work
at once without making and removing a worktree for each task, and so that a
Beat's changes are exactly its branch.

```
~/repos/sylvan-stack/
  arbol/  arbol-root/  arbol-trunk/  …       the repositories' own folders: the owner's, and
                                             Claude Code or Codex used directly; no Beat works here
  1/  2/  3/  4/  5/                         the prepared folders, each with a clone of every repository
    arbol/  arbol-root/  arbol-trunk/  …     on main while free; on beat/<Beat> while a hold names the folder
  readonly/                                  one more clone of every repository, always the last main;
    arbol/  arbol-root/  arbol-trunk/  …     nobody edits it
```

| Folder | Checked out | Who works in it |
|---|---|---|
| `~/repos/sylvan-stack/<repo>/` | whatever its user chose | the owner, and Claude Code or Codex started there |
| `~/repos/sylvan-stack/<n>/<repo>/` | `main` while free; `beat/<Beat>` while a hold names the folder | the agent of that hold, and nobody else |
| `~/repos/sylvan-stack/readonly/<repo>/` | `main`, brought up to date after every merge | nobody; it is read, for the last merged state |

- **Free.** A prepared folder is free when no hold names it, and every
  repository in it is on `main` with nothing uncommitted and no file that git
  does not ignore. A folder that is not clean is never taken; say which and
  what is in it.
- **Territories keep their paths.** An entry under
  `~/repos/sylvan-stack/<repo>/` means the same path in the prepared folder
  the hold names: `~/repos/sylvan-stack/arbol-trunk/trunks/trivial/` is worked
  in `~/repos/sylvan-stack/3/arbol-trunk/trunks/trivial/`. Overlap is judged as
  before, because every branch is merged into the one `main`.
- **Several repositories, one folder.** A Beat whose territory spans
  repositories uses their clones in the same prepared folder, so that a check
  of one against another, such as a suite in one repository run against a
  program in another, uses the Beat's own copies.
- **Corpora stay on `main`.** The specification corpora in `~/Artifacts/` and
  `~/Artifacts/sagas/` are not cloned: a Beat commits to them on `main`, as
  before, and names itself at the start of each commit's subject, such as
  `SYL-173: …`.
- **Nothing installed from a branch.** A program installed on this Mac, such
  as a launcher in `~/.local/bin`, is made only from merged work, never from a
  Beat's branch.
- **Setting one up.** A new prepared folder, or a repository new to the stack,
  is a clone whose `origin` is the repository's GitHub address, on `main`, with
  every environment its lockfiles name installed once: `uv sync --locked
  --group dev` beside each `uv.lock`, `npm ci` beside each
  `package-lock.json`, and `uv venv` with `uv pip install -e .` beside a
  `pyproject.toml` that has no `uv.lock`, as `mycel`'s has none. Every prepared folder and `readonly` holds the same
  repositories. When all five are taken, an agent may set up `6/` the same
  way.

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
  "folder": "~/repos/sylvan-stack/3",
  "stint": { "name": "beat", "limits": [ { "measure": "quiet", "kind": "soft-max", "value": 60 },
                                          { "measure": "time", "kind": "hard-max", "value": 240 } ] },
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
- **Sagas know each other.** Every `saga.md` has a section `Other Sagas`.
  It names each Saga this one waits for and each Saga that waits for it,
  with a link to its `saga.md`, and says Beat by Beat what waits for what,
  for example `SYL-195 (First Roots Arc) is blocked by SYL-190 of the Arbol 2
  Specifications Saga`. Where the order between two Sagas matters, it gives
  the recommended order and the reason, for example "SYL-190 is accepted
  before the First Roots Arc reaches SYL-195". A Saga with no such link
  says `None.`. Each Beat-to-Beat dependency is also a *blocked by* relation
  in Linear, which is what [Taking the next Beat](#taking-the-next-beat)
  checks; the section lets an agent see them without searching Linear.
  `INDEX.md` gives, for each Saga, the Sagas it waits for. Its order of the
  Sagas stays the owner's priority, because a dependency between two Sagas
  holds back only the Beats it names.
- **A dependency is written on both sides.** The agent that creates,
  changes or removes a dependency between Sagas, or finishes a Beat that
  another Saga waits for, writes it in the `Other Sagas` sections of both
  Sagas and in `INDEX.md` in the same commit, and sets the *blocked by*
  relation in Linear. A dependency that is met stays listed, marked `Done`
  with its date, until the Beat that waited for it is Done.
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
2. **Read the Saga's `saga.md` and its `rules.md`.** The rules apply to every
   Beat of the Saga; `saga.md` says which other document your Beat needs.
3. **Run [the check](#the-check).**
4. **Find the Arc's next Beat:** the first Beat in the order of the Arc's
   file that is not Done. It can start when all of these hold:
   - no hold names it;
   - every Beat it is *blocked by* in Linear is Done;
   - its territory overlaps no hold. A hold of the same Arc counts too,
     unless both Beats name smaller territories that do not overlap.

   When it cannot start, go to the next Arc.
5. **Take it.** Create its hold file, naming the first free
   [prepared folder](#prepared-folders) as `folder`. If the file exists,
   another agent took it a moment ago: go back to step 3.
6. **Make its branch** in each repository its territory touches, in the
   prepared folder: `git fetch origin`, then `git switch -c beat/<Beat>
   origin/main`, or `git switch beat/<Beat>` when the Beat is taken over and
   its branch is on GitHub. Run the folder's environment setup again; it takes
   a moment when nothing changed.
7. **Mark it in Linear.** Set the Beat to In Progress and comment:
   `**Agent:** Took this Beat. <tool> session <id>. Folder: <folder>.
   Territory: <paths>. Stint: <name> (<its limits>).`
8. **Read what earlier Beats left for it:** the hand-over of each Beat it is
   blocked by, and of the Beat before it in its Arc's order, as
   [The hand-over of a Beat](#the-hand-over-of-a-beat) says.
9. **Write its plan** before any other change, as
   [The plan of a Beat](#the-plan-of-a-beat) says.
10. **Say which Beat you took, and why,** in the first line of the reply. A
   Beat that was In Progress without a hold is taken over: read its comments,
   its plan and its hand-over first, since they say where the work stopped.

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
- **Tests in the plan.** The last leaf of every plan runs the repository's
  complete suite, then merges and records the hand-over. Every earlier leaf
  runs only the tests of the files it changes, and after a failure only the
  failed tests until they pass. No other step runs the complete suite: a
  Beat runs it when it is taken, to know where it starts, and in its last
  leaf. A run that takes longer than about a minute is started in the
  background, and the work goes on while it runs. The Saga's `rules.md`
  names the commands of its repository.
- **Keeping it true.** When the work shows that the plan is wrong, change
  the plan in the file first, and say why in the next `**Agent:**` comment.
- **Publishing.** After writing the plan and after each tick, commit the
  Beat's file in `~/Artifacts/sagas/`, push, and bring its Linear copy in
  line.

## The hand-over of a Beat

What a later Beat must know from this one, and finds in no specification, is
the Beat's *hand-over*: a section `## Hand-over` at the end of the Beat's
file, after its plan. The Beat's file is the original and its Linear issue a
copy, so every agent finds the hand-over, whichever tool it runs in and
whichever session started it.

- **What goes in.** Only what a later Beat needs and cannot read anywhere
  else: where the new code is and how its parts fit together, what the Beat
  left on this Mac (something installed, a copy of what it replaced), a
  choice that would be easy to undo by mistake, and each open point with the
  Beat or file it belongs to. Each item names the Beat it is for when it is
  for one, and links to the specification section or decision that says the
  rest instead of repeating it.
- **What does not go in.** What a specification should say: change the
  specification. A point for the whole Saga: the Saga's document for it, such
  as its known gaps. The account of the work: the `**Agent:**` comment.
- **When.** When the Beat is finished or stopped, before its hold is deleted;
  commit and push the Beat's file and bring its Linear copy in line, as for
  its plan. A stopped Beat's hand-over says where the work stopped and what
  comes next, for the agent that takes it over. A Beat with nothing to hand
  over has no section.
- **Nowhere else.** Never leave a hand-over where only one tool or one group
  of sessions can see it: a tool's memory, a notes folder that an app gives
  the sessions one session started, a session's scratch folder. An agent of
  another tool, or a session started later, never finds it there. When an
  instruction names such a place for notes, write the hand-over in the Beat's
  file instead.

For example, at the end of `SYL-179.md`:

```
## Hand-over

- For SYL-158: `src/arbol_builds/roots.py` reads the Root records and picks the
  current Root (BLD-D17); give the launchers of `arbol` and `arbol-root` its
  text after `launcher.py`, as `arbol-trunk` has it.
- For SYL-180: the installed `arbol-builds` is current, so the first build of
  `arbol-trunk/trivial` writes `~/.local/bin/arbol-trunk`.
- Open: `known-gaps.md` still lists the point BLD-D17 settles.
```

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
- **Work only in your prepared folder,** on the Beat's branch, for code; the
  corpora on `main`, as [Prepared folders](#prepared-folders) says. Push the
  branch with each commit (`git push -u origin beat/<Beat>` the first time),
  so the work is on GitHub before it is merged.
- **Another Beat's unfinished work is not yours.** It lives on another branch
  in another folder. A check that fails in another Beat's territory is not
  yours to fix; say so in your report.

## Stop criteria of a Beat

Every run of a Beat has a [stint](stints.md): the stint the owner names when
asking for the work, else `beat`, the default for every Beat (the owner, 16
October 2026). A *run* is one hold: it starts at the hold's `takenAt`, and
taking a Beat over starts a new run. The hold records the stint's name and
its resolved limits, and so does the comment that takes the Beat, so a later
change to the stint does not change what a past run reports.

| Measure | Unit | Counting rule |
|---|---|---|
| `quiet` | minutes | Wall clock since the last plan step of the Beat was ticked in this run, or since its plan was written when none is ticked yet. The time the owner takes to answer a question is left out |
| `time` | minutes | Wall clock since the hold's `takenAt` |

| Kind | What the agent does when the limit is reached |
|---|---|
| `soft-max` | Stops at the next point where the work is safe to leave: after the command that runs, with what works committed and pushed. It says in Linear and in its reply where the Beat stands, what is stuck and what it proposes, and asks the owner whether to go on. An answer to go on starts the `quiet` count again |
| `hard-max` | Stops the Beat as [Stopping and finishing](#stopping-and-finishing) says: commits and pushes what works, writes the hand-over, returns its prepared folder and releases the hold, whatever is left. The Beat can be taken again in a new run |

The agent checks both counts after each tick and before it starts any
command that may take long. Neither limit is a target: a Beat that is done
early finishes early. From outside, [the check from outside](agent-watch.md)
measures every run each 5 minutes and raises a signal, such as when a Beat
goes 15 minutes without a tick while its agent spends tokens, or passes its
hard stop.

## Stopping and finishing

- **Stopping in the middle:** follow the Saga's rules (commit what
  works, leave the `**Agent:**` comment that says what is done and what comes
  next), push the branch unmerged, write the Beat's hand-over, return the
  prepared folder (below), then delete the hold file and end the comment with
  `Released.` The agent that takes the Beat over switches to its branch.
- **Finishing:** when the Beat's checks pass, merge it, in each repository it
  changed:
  1. Bring the branch up to date: `git fetch origin`, `git merge
     origin/main`, run the checks again, push the branch.
  2. Merge it into `main` as one merge commit named after the Beat:
     `git switch --detach origin/main`, `git merge --no-ff beat/<Beat> -m
     "<Beat>: <the Beat's title>"`, `git push origin HEAD:main`. When the push
     is refused because another merge came first, repeat from step 1.
  3. Bring `readonly` up to date: `git -C ~/repos/sylvan-stack/readonly/<repo>
     pull --ff-only`.

  Then set the Beat to Done as the Saga's rules say, write its hand-over,
  return the prepared folder, and delete the hold file.
- **Returning the prepared folder,** in each repository the Beat used:
  `git fetch origin`, `git switch main`, `git merge --ff-only origin/main`,
  then `git branch -d beat/<Beat>` and `git push origin --delete
  beat/<Beat>` once the branch is merged. `git status` then shows nothing; a
  folder that does not end clean is not released, and the hold stays until it
  is.
- **Either way, report the progress** to the Arc, and when needed to the
  Saga, as [Order and progress](#order-and-progress) says.
- **An Arc is Done** when all its Beats are Done. **A Saga is Done** when the
  owner says so: its line in `INDEX.md` and its Linear project are closed.

## Reviewing a Beat, an Arc or a Saga

In each repository, `git log --first-parent main` lists one merge commit for
each Beat, named after it, and `git diff <merge>^1 <merge>` is exactly what
that Beat changed there. An Arc's changes are the merges of the Beats its
`arc.md` lists, and a Saga's are those of its Arcs. A Beat's commits in the
corpora name the Beat at the start of their subject. Beats finished before
16 October 2026 committed straight to `main` and are found by their dates and
territory instead.

## Planning a Saga

- **The owner decides the Sagas** and their priority. An agent proposes the
  Arcs, each with its territory, and the Beats, such as the tasks of an
  accepted specification, and writes them once the owner agrees.
- **A Saga is a folder** `~/Artifacts/sagas/<saga>/` with its `saga.md`,
  where the Saga starts: which Beat is next, the recommended order of its
  Arcs, a `Progress` section with one line for each Arc, and its documents,
  each with a line on what it holds and when to read it. The rules of its
  work are `rules.md` beside it. What only some tasks need, such as the
  Saga's known gaps or which Beat covers which requirement, is a document of
  its own, so that an agent reads what its task needs and no more. The Saga
  has a line in `INDEX.md`, and a Linear project of the same name whose page
  is a copy of `saga.md` and whose other documents are copies of the Saga's
  other documents.
- **A new Saga is placed among the others.** Read the `saga.md` of every
  Saga in `INDEX.md` first. Write the new Saga's `Other Sagas` section, the
  matching lines in the Sagas it touches, and its row in `INDEX.md`, with
  the *blocked by* relations in Linear, before its first Beat starts.
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
- **What the check from outside does with its signals.**
  [The check from outside](agent-watch.md) reads the holds, the Beat files'
  ticks and the agents' token spend every 5 minutes, raises its signals, and
  has a fresh agent of the other tool review what each signal points at.
  Steering through a hook of the check's own, by the reviews' answers, and
  reports to the owner on Telegram are still to be built (SYL-221 and
  SYL-222).
- **The check as a command.** Until it exists, the agent does it by hand:
  `ps -o lstart= -p <pid>` for a process, and `lsof <threadFile>` for a Codex
  thread.
- **Not tried yet:** whether `CODEX_THREAD_ID` is set in a Codex app thread
  and in the codex CLI, and whether the codex CLI in a terminal keeps the
  thread's record file open as the Codex app does.
