---
role: authored
---
# Guide: Owner Goals

How to record, change, withdraw and look up the owner's
[Owner Goals](../../arbol/GLOSSARY.md#owner-goal), how to check that they do not
contradict each other, and how to read them in any other work. The owner asks
in their own words with `/owner-goals "<anything>"` (in Codex
`$owner-goals`), for example `/owner-goals "drivers must be written in Python,
never TypeScript"`, `/owner-goals "drop the TypeScript goal"` or
`/owner-goals "what do my goals say about the drivers?"`.

This guide owns the process. The corpus README owns the file of a goal; the
`goals-cli` README owns the commands, their options and exit codes.

| | |
|---|---|
| Terms | [Owner Goal](../../arbol/GLOSSARY.md#owner-goal); one of kind `requirement` is an [Owner Requirement](../../arbol/GLOSSARY.md#owner-requirement), one of the two places a [Requirement](../../arbol/GLOSSARY.md#requirement) is recorded |
| Where the goals live | `~/Artifacts/goals/`, one `OG-<n>.md` per goal; its [README](../../goals/README.md) is the contract of a goal file; `INDEX.md` is generated |
| Tool | `goals` in `~/.local/bin`, installed from `~/repos/goals-cli`; every command is in `~/repos/goals-cli/README.md` |
| History | the goals corpus is a git repository of its own, kept on this Mac only, with no remote |

Contents: the rules · reading the request · adding · changing, replacing and
withdrawing · answering questions · checking · after a change · the reply ·
Owner Goals in other work.

## The rules

- **The files are the truth.** Read the goals with `goals list` (or
  `goals list --all --json` for every field) before every answer and every
  change, never from memory or an earlier reply. `INDEX.md` is a generated
  table and is never edited.
- **Change goals only with `goals`.** It writes the file and `INDEX.md`, and
  it refuses a change that would break the graph: a link to a goal that does
  not exist, a loop of refinements, two goals with one id. Never write, edit
  or remove a goal file by hand.
- **A goal is never deleted.** "Delete", "remove" or "forget" a goal means
  withdraw it: `goals delete` keeps the file with the date and the reason,
  and its id is never given again.
- **Only the owner puts a goal in force.** A goal the owner states firmly in
  the request is added `active`. Everything the agent concludes on its own is
  added `--proposed` and put to the owner as a question with a proposed
  answer: a goal read out of tentative words ("maybe", "let's consider"), a
  goal the agent suggests, and a replacement the owner did not name.

## Reading the request

One prompt may ask for several of these at once, such as "drivers are now in
Rust, not Python, and show me the list". Do them in the order the owner gave.

| The owner says | Do |
|---|---|
| a wish, a rule, a must or a must not: "drivers must be in Python" | [add](#adding-a-goal) |
| they changed their mind: "drivers are in Rust now, not Python" | [add](#adding-a-goal) with `--replaces` |
| better wording, kind, scope or links for a goal, with the same meaning | [edit](#changing-replacing-and-withdrawing) |
| a goal no longer holds: "drop OG-3", "we don't need the TypeScript rule" | [withdraw](#changing-replacing-and-withdrawing) |
| yes or no to a proposal: "accept OG-6", "no to the proposals" | `goals edit OG-6 --status active`, or withdraw it |
| a question: "what applies to the drivers?", "show OG-2", "what did I decide about languages?" | [answer](#answering-questions) |
| "check my goals", "do any of them contradict?" | [check](#checking) |
| how Owner Goals work | explain from this guide and the corpus README, with one example |
| nothing: a bare `/owner-goals` | list the current goals, the proposals waiting for them, and what they can ask |

## Adding a goal

1. **Read the current goals** with `goals list`.
2. **Write each statement.**
   - One thing that must hold, in one sentence in the present tense:
     "Drivers are implemented in Python", not "We should probably use Python
     for the drivers".
   - Complete on its own: whoever reads only the statement understands it,
     so "it" and "this" become what they stand for.
   - The owner's meaning and no more. A vague goal is a valid goal: "Setting
     up a new machine takes one command" stays as the owner said it; never
     sharpen it with a number, a technology or a detail they did not give.
   - One sentence with two wishes becomes two goals: "drivers in Python,
     never TypeScript" is "Drivers are implemented in Python" and "Drivers
     are not implemented in TypeScript".
3. **Choose the kind.** `requirement` when the goal says something must be
   included or done; `constraint` when it says something must not be; no kind
   when the words read as neither.
4. **Give a scope only if the owner named one**, in their words: "drivers",
   "Arbol". No scope means everywhere; never add one to look tidy.
5. **Link it.** `--refines` the current goals it makes more concrete: "Drivers
   are implemented in Python" refines "The whole stack is written in one
   language". This is the agent's judgment; say it in the reply, and the
   owner can change it with `edit`.
6. **Compare it with every current goal by meaning** before writing:
   - It says what `OG-n` already says: add nothing, tell the owner, and offer
     their new words as better wording for `OG-n` when they are.
   - It cannot hold together with `OG-n`: if the owner said it takes its place
     ("now", "instead", "no longer"), add it with `--replaces OG-n`. If they
     did not, add it `--proposed --replaces OG-n` and ask: "OG-n says X, the
     new goal says Y: does Y replace OG-n? Proposed: yes." A yes is
     `goals edit <new> --status active`, which puts `OG-n` out of force; a no
     withdraws the new goal with the owner's reason.
7. **Write it:**

   ```sh
   goals add "<statement>" [--kind requirement|constraint] [--scope "<scope>"] \
     [--refines OG-1 ...] [--replaces OG-2 ...] [--source "<where>"] [--proposed] \
     --body "<the owner's words, quoted exactly, then any explanation>"
   ```

   The body keeps the owner's own words, so the statement can always be
   compared with what they said. `--source` names where they said it when it
   has a stable address, such as an Arbol chat's
   [Entity URI](../../arbol/GLOSSARY.md#entity-uri) or a Linear comment link;
   leave it out otherwise.

## Changing, replacing and withdrawing

- **Same meaning, better form** is `goals edit OG-n` with `--statement`,
  `--kind` (`none` removes it), `--scope` (`""` removes it), `--source` or
  `--refines`, which takes the complete new list.
- **A new meaning is a new goal.** "Drivers are implemented in Python" becoming
  "Drivers are implemented in Rust" is `goals add "…" --replaces OG-n`, so the
  old goal stays readable as history; a typo fixed in a statement is an edit.
- **Withdraw** with `goals delete OG-n --reason "<reason>"`. The reason is the
  owner's words; if they gave none, it is their request, quoted.
- **A withdrawn goal that others refine** leaves those goals pointing at a goal
  out of force (the warning `stale-parent`). Name them in the reply, with the
  proposed answer "keep them; they hold on their own", and on a yes remove the
  link with `goals edit OG-k --refines <the other ids>`.
- **Confirm a proposal** with `goals edit OG-n --status active`; refuse it by
  withdrawing it with the owner's reason.

## Answering questions

- **What applies to X:** every current goal whose scope covers X, and every
  goal without a scope whose statement or body bears on X. Read the
  statements and bodies, not only the scopes.
- **One goal:** `goals show OG-n` gives its file and the goals that refine or
  replace it.
- **History:** `goals list --all`, following each `replaces` back to the goal
  it took the place of.
- Answer only from the files, with ids and statements. Mark a `proposed` goal
  as not yet in force. When no goal covers the question, say so; if the owner
  then states one, add it.

## Checking

`goals check` checks the structure of the graph, then asks a model whether any
current goals, proposed ones included, cannot all hold at once. It runs
`claude -p` in the owner's login shell itself and takes about ten seconds.

- Run `goals check` after every addition or edit, and `goals check
  --deterministic` after a withdrawal, which can only remove a contradiction.
- For each contradiction, give the goals, the model's explanation and its
  confidence, and a proposed resolution: withdraw one, let one replace the
  other, or a scope or wording that separates them. Change nothing until the
  owner answers.
- The tool keeps no record of a finding the owner judged harmless, so it is
  reported again at the next check. A clearer scope or wording settles it for
  good; propose one.
- Exit status 2 means the model gave no usable answer. Report it with the
  structural result of `goals check --deterministic`; do not present your own
  judgment as the check.

## After a change

1. **Commit** the files this change wrote in the goals corpus, and nothing
   else:

   ```sh
   git -C ~/Artifacts/goals add OG-4.md OG-2.md INDEX.md
   git -C ~/Artifacts/goals commit -m "Owner Goals: add OG-4, withdraw OG-2"
   ```

   The corpus has no remote by the owner's decision: do not push it or add one.
2. **Index it for search** with `mycel ingest --repo goals`, without
   embedding; embedding waits for the owner's approval of its cost. If the
   ingest is refused as busy, say so; the next ingest catches up.

## The reply

- One line saying what changed, in plain words.
- A table of every goal the request added, changed or withdrew, and the goals
  it links to: Id · Statement · Kind · Scope · Status.
- The result of the check: clean, or each contradiction and warning with its
  proposed resolution.
- Every question as a numbered item with its proposed answer, so the owner can
  answer by number.

## Owner Goals in other work

- An instruction that speaks of *a requirement* without saying which means
  both places: the Spec Requirements of the work and the Owner Goals, the
  constraints among them too.
- Before writing a specification, a plan or code, read the current goals whose
  scope covers the work and those without a scope. An active goal binds the
  work; a proposed one is not yet in force. Work that would contradict an
  active goal stops, and the agent asks the owner, giving the goal's id.
- When the owner states a lasting wish during other work, an agent may record
  it with `goals add … --proposed` and say so in its reply; only the owner
  makes it active.

<!-- sources:
goals-cli:@code/src/goals_cli/cli.py
goals-cli:@code/src/goals_cli/check.py
goals-cli:@code/src/goals_cli/store.py
goals:README.md
-->
