---
role: authored
---
# Guide: Troubleshooting Difficult Tasks

Use this guide when an implementation or bug-fixing task has become difficult
enough that an agent is no longer making measurable progress. Its purpose is
to turn a long investigation into durable, well-linked knowledge that survives
Chat Sessions, prevents repeated dead ends, and gives the next agent an exact
place to resume.

This guide is authoritative for the troubleshooting workspace, its files, and
the investigation loop. It complements, rather than replaces, the normal code
research, implementation, ticket, and testing processes.

## When to start or continue a troubleshooting

Start a troubleshooting when the user explicitly asks, or when one or more of
these conditions hold:

- the same symptom or failed approach has recurred across multiple attempts;
- two bounded investigation loops produced no reduction in uncertainty;
- the task crosses several unfamiliar components and the actual failure
  boundary is still unknown;
- a fix appears to work but cannot be explained or validated reliably;
- the work must be handed to another Chat Session before it is solved.

Do not create a troubleshooting workspace for every ordinary bug. The extra
structure is justified when preserving investigation state is cheaper than
reconstructing it.

“Progress” does not require a fix. A reproducible failure, a disproved
hypothesis, a narrowed boundary, a newly useful observation, or a confirmed
invariant is progress when it is recorded with evidence.

## Location and identity

For troubleshooting that is not attached to a ticket, use:

```text
~/Artifacts/<repo>/troubleshootings/<task-name>/
```

`<task-name>` must be stable, descriptive, unique within that repository's
`troubleshootings/` folder, and written in kebab-case. Do not include a Chat
Session number or date in it. Example:

```text
~/Artifacts/mail-service/troubleshootings/emails-sync/
```

The human title in `README.md` may be `Emails Sync Troubleshooting`. Record
likely user phrasings as aliases there so a later request such as “let's
continue Emails Sync Troubleshooting” resolves to the same folder.

Ticket-backed work remains in the ticket workspace, as required by corpus
placement rules:

```text
~/Artifacts/<repo>/tickets/<TICKET-KEY>/troubleshooting/<task-name>/
```

Link that workspace from any related ticket research, plan, or notes instead
of duplicating investigation content. If a troubleshooting starts without a
ticket and later acquires one, keep its stable location unless the user asks
for a move; add reciprocal links to the ticket workspace.

### Resolving a continuation request

Within the repository implied by the selected checkout or named by the user:

1. inspect troubleshooting folder names and their `README.md` titles and
   aliases;
2. compare case-insensitively and ignore punctuation, whitespace, kebab-case
   differences, and an optional `Troubleshooting` suffix;
3. continue automatically only when exactly one task matches;
4. if several tasks or repositories plausibly match, show the candidates and
   ask the user instead of guessing;
5. if none match, say so and ask whether to create a new task.

## Workspace contract

All troubleshooting artifacts described in this guide are **highly
recommended**. Treat that as “create by default”: they are the expected
workspace contract, but an artifact may be omitted when it genuinely does not
help for this task or lifecycle stage. Record each omission and its reason in
the `README.md` workspace index so a later agent can distinguish an intentional
omission from missing work. Do not omit an artifact merely to save a few lines
or avoid keeping it current.

A complete troubleshooting workspace normally contains:

```text
<task-name>/
├── README.md
├── STATUS.md
├── FINDINGS.md
├── DIDNT-WORK.md
├── REPRODUCTION.md
├── HYPOTHESES.md
├── CODE-MAP.md
├── RESOLUTION.md
├── SESSION-<NNN>-<slug>.md
└── data/
```

At least one session file should exist after work has begun. `RESOLUTION.md`
may be deferred while the task is active, and `data/` need not be created until
there is raw evidence to store; note those lifecycle-based omissions in the
index. Any other omission should have a task-specific reason.

### `README.md` — identity and map

`README.md` is the landing page, not a chronological notebook. It must contain:

- the task title, stable task name, repository, and optional ticket;
- aliases by which a user might refer to the task;
- a concise problem statement and success criteria;
- current lifecycle state: `active`, `blocked`, `paused`, or `resolved`;
- a table linking **every other file and subfolder** in the workspace, with a
  one- or two-sentence summary of each;
- links to related tickets, research, plans, MRs, and external context.

Keep its summary current, but put volatile handoff detail in `STATUS.md`.

Suggested beginning:

```markdown
---
role: authored
---
# Troubleshooting: Emails Sync

| Field | Value |
|---|---|
| Task name | `emails-sync` |
| State | active |
| Repository | `mail-service` |
| Ticket | [MAIL-123](../../tickets/MAIL-123/) |
| Aliases | Emails Sync Troubleshooting; stuck email synchronization |
| Updated | YYYY-MM-DD |

## Problem
...

## Success criteria
- ...

## Workspace index
| Artifact | Summary |
|---|---|
| [STATUS.md](STATUS.md) | Current handoff and next experiment. |
| [FINDINGS.md](FINDINGS.md) | Confirmed facts accumulated across sessions. |
| [DIDNT-WORK.md](DIDNT-WORK.md) | Failed or inconclusive approaches and retry conditions. |
| [SESSION-001-reproduce.md](SESSION-001-reproduce.md) | Established the first reproducible baseline. |
```

### `STATUS.md` — exact resume point

`STATUS.md` is highly recommended because a broad README summary is usually
not enough for a reliable cross-session handoff. Keep it short and replace
stale state rather than appending history. It records:

- when it was last updated and by which session;
- current lifecycle state;
- active symptom and latest verified baseline;
- the leading hypothesis or current uncertainty;
- blockers and unresolved questions;
- the next one to three concrete experiments, in priority order;
- validation still required and the definition of done;
- uncommitted diagnostic or implementation changes that affect resumption.

The first next step must be executable, not “investigate further.” Name the
component, observation, command/test, or comparison that will reduce a stated
uncertainty.

### `FINDINGS.md` — durable positive knowledge

`FINDINGS.md` contains the most important confirmed facts across all sessions.
It is curated, not a dump of observations. Give each finding a stable ID such
as `F-001` and include:

- the precise claim;
- evidence and links to the originating session;
- code, logs, tests, or external sources that support it;
- its implication for the task;
- relevant scope or environment constraints.

Do not promote a plausible explanation to a finding. Open theories remain in
the active session or `HYPOTHESES.md`. Code-dependent claims should carry
narrow Source Refs as described in
[Source Refs authoring](source-refs-authoring.md), so later code changes can
surface stale knowledge.

### `DIDNT-WORK.md` — durable negative knowledge

`DIDNT-WORK.md` prevents later sessions from repeating an approach without
knowing it was already attempted. Give each entry a stable ID such as `DW-001`
and record:

- the approach or hypothesis tested;
- exact preconditions, environment, revision, and inputs that matter;
- expected result and actual observation;
- evidence and the session where it was tried;
- whether it was disproved, ineffective, blocked, or merely inconclusive;
- why it should not be retried now;
- the explicit condition under which retrying would become useful.

Avoid context-free statements such as “caching is not the problem” or “that
command did not work.” Negative results are valid only under the conditions in
which they were observed. If later evidence overturns an entry, mark it
superseded and link the correcting finding/session; do not silently delete it.

### `SESSION-<NNN>-<slug>.md` — one Chat Session's record

Each Chat Session that works on the task owns one session file. Use a
zero-padded, monotonically increasing number (`001`, `002`, ...), followed by
a short kebab-case slug describing that session's objective:

```text
SESSION-001-reproduce-timeout.md
SESSION-002-trace-worker-boundary.md
SESSION-003-validate-fix.md
```

At session start, scan existing names, choose `max + 1`, and create the file
immediately to reserve the number. Never reuse a gap. A session file records:

1. objective and starting state;
2. relevant environment, branch/revision, inputs, and reproduction command;
3. hypotheses and predicted observations;
4. chronological experiments: action, observation, evidence, interpretation;
5. code or configuration changes, including temporary instrumentation;
6. tests and validation results;
7. conclusions and unresolved questions;
8. entries promoted to `FINDINGS.md` or `DIDNT-WORK.md`;
9. a precise handoff and next experiment.

Capture decisions and evidence, not the entire chat transcript. Link large
logs or datasets instead of pasting them into the session file.

## Highly recommended specialized artifacts

These are part of the default workspace contract, not merely optional extras.
Create and maintain each one unless there is a concrete reason it does not
apply; document that reason in `README.md`:

- **`REPRODUCTION.md`** — expected versus actual behavior, prerequisites,
  minimal reproduction steps, known-good/known-bad cases, and a deterministic
  failing test. If deterministic reproduction is impossible, use the file to
  record the best available trigger, frequency, and evidence rather than
  omitting it automatically.
- **`HYPOTHESES.md`** — a table of stable hypothesis IDs, predicted
  observations, evidence for/against, experiments, and status (`open`,
  `confirmed`, `rejected`, `inconclusive`). Even a short table helps prevent
  causal theories from being lost or silently revived across sessions.
- **`RESOLUTION.md`** — root cause, final change, why it works, validation,
  residual risks, rollback, and reusable lessons. It may be deferred while the
  task is active, but should be created when resolving the task rather than
  overloading the final session file.
- **`data/`** — raw logs, traces, query outputs, screenshots, reduced fixtures,
  and other evidence too large for Markdown. Create it when such evidence
  exists, use descriptive names, and link every item from the session that
  interprets it. Never store credentials or unnecessary sensitive data.
- **`CODE-MAP.md`** — task-specific component and data-flow map. Keep it small
  for localized tasks; expand it when failure boundaries span services or
  modules. Link existing repository code maps and research rather than copying
  them.

Do not add `PLAN.md`, `NOTES.md`, or `HANDOFF.md` by default: active plans and
handoff state belong in `STATUS.md`, while chronological notes belong in the
current session. Add a specialized artifact only when it has a distinct owner
and purpose.

## Starting a new troubleshooting

1. Confirm the repository and whether the work is ticket-backed.
2. Search the applicable troubleshooting location for an existing task by
   folder, title, and aliases. Update rather than duplicate.
3. Choose a stable task name and create the folder.
4. Create the highly recommended workspace artifacts: `README.md`,
   `STATUS.md`, `FINDINGS.md`, `DIDNT-WORK.md`, `REPRODUCTION.md`,
   `HYPOTHESES.md`, and `CODE-MAP.md`. Defer `RESOLUTION.md` until resolution
   and `data/` until needed, or create placeholders if they improve clarity.
5. If any recommended artifact is omitted, add an entry to the `README.md`
   workspace index naming it, explaining why, and stating when it should be
   created.
6. Link existing ticket context, research, plans, logs, and relevant MRs; do
   not copy their content into the new workspace.
7. Create `SESSION-001-<slug>.md` and record the current branch/revision,
   environment, symptom, success criteria, and first bounded experiment.
8. Update `README.md` so its workspace index lists every created artifact and
   every intentional omission.

## Resuming in a new Chat Session

Read in this order to avoid replaying the entire history:

1. `README.md` for identity, scope, success criteria, and artifact map;
2. `STATUS.md` for the exact resume point;
3. `FINDINGS.md` and `DIDNT-WORK.md` for accumulated positive and negative
   knowledge;
4. `REPRODUCTION.md`, `HYPOTHESES.md`, and `CODE-MAP.md` for the current model
   of the system and failure;
5. the latest session file;
6. older sessions, `data/`, `RESOLUTION.md`, and linked ticket/research
   material when the current question requires them.

Then verify that the baseline and branch/revision still match reality. If they
have drifted, record the changed condition before relying on an old result.
Create the next session file before beginning new experiments.

## Evidence-first troubleshooting loop

Repeat this loop inside the current session:

1. **State one uncertainty.** Phrase the current blocker as a question with an
   observable answer.
2. **Choose a discriminating experiment.** Prefer the smallest action that
   separates two plausible explanations or localizes a boundary.
3. **Write the prediction first.** Record what each result would imply before
   executing the experiment; this prevents post-hoc storytelling.
4. **Run one bounded experiment.** Keep diagnostic changes reversible and
   distinguish them from the proposed production fix.
5. **Record raw observation before interpretation.** Link the exact test, log,
   trace, diff, or code location.
6. **Update the model.** Confirm, reject, or narrow a hypothesis. Promote only
   durable facts or useful negative results to the curated files.
7. **Select the next highest-information step.** Do not continue a direction
   merely because setup work has already been invested in it.

Prefer observability and a minimal failing test before speculative code edits.
Compare known-good with known-bad behavior, trace data across component
boundaries, inspect history when a regression window exists, and test
assumptions at the narrowest layer that can falsify them.

## Anti-loop and escalation rules

- Never repeat an experiment recorded in `DIDNT-WORK.md` unless its retry
  condition is now true. Link the old entry and state what changed.
- Do not make several causal changes at once unless the combination itself is
  the explicit hypothesis.
- If two consecutive experiments produce no new information, stop the current
  direction. Re-check the reproduction, assumptions, component boundary, and
  available observability before doing more of the same.
- If several hypotheses fail in one layer, move one boundary outward or inward:
  caller/callee, producer/consumer, client/server, persistence/cache, runtime/
  build, or configuration/code.
- When blocked by missing access, unavailable environment, ambiguous product
  behavior, or an irreversible decision, ask the user a precise question.
  Include what was verified, what remains unknowable, and the smallest input or
  permission needed.
- Do not claim progress based only on code churn. If an action neither validates
  behavior nor reduces a named uncertainty, treat it as setup and choose a
  measurable next step.

## Ending and handing off a session

A user may explicitly ask to end the current troubleshooting Chat Session so
work can continue in a fresh one. Treat phrases such as **“wrap it up,” “wrap
this session,” “hand off this session,”** and **“finalize session”**—and clear
variants—as a handoff request when a troubleshooting is active. This request
does not mean the troubleshooting itself is resolved or abandoned. A session
that found no fix is still worth finalizing because it can preserve narrowed
uncertainties, negative results, and better next experiments.

The user may include observations or results from attempts made outside the
agent's tool activity. Preserve those results in the current session and the
appropriate curated artifacts. Clearly label what was **reported by the user**
versus independently reproduced or verified; do not silently upgrade a
reported result into a confirmed finding. Ask a follow-up question only when a
missing detail would make the handoff materially misleading. Otherwise record
the uncertainty and finish the handoff without starting more investigation.

### Handoff procedure

Once a handoff is requested, stop opening new investigative directions. Perform
only the state inspection needed to record the work accurately, then:

1. **Finalize the current session file.** Record its objective, attempts,
   observations, test results, changes, conclusions, unresolved questions, and
   outcome—even when the outcome is “no fix.” Include any user-provided results
   with their provenance. End with a concrete handoff and the highest-value
   next experiment.
2. **Curate durable knowledge.** Promote supported facts to `FINDINGS.md` and
   failed, blocked, or inconclusive directions worth remembering to
   `DIDNT-WORK.md`, with links back to the session and explicit retry
   conditions. Update hypothesis statuses without treating absence of success
   as proof that every attempted hypothesis is false.
3. **Refresh the working model.** Update `REPRODUCTION.md`, `HYPOTHESES.md`, and
   `CODE-MAP.md` where this session changed them. If an artifact remains
   intentionally omitted, confirm that `README.md` still explains why and when
   it should be created.
4. **Replace `STATUS.md` with a handoff-ready resume point.** Name the session
   just finalized, latest verified baseline, current uncertainty, blockers,
   validation still needed, relevant temporary or uncommitted changes, and the
   next one to three executable experiments in priority order. The first step
   must be specific enough for a new agent to execute without reconstructing
   the investigation.
5. **Refresh `README.md`.** Keep the troubleshooting state `active` unless the
   user explicitly pauses it, an external dependency makes it `blocked`, or
   the success criteria make it `resolved`. Update the date, concise summary,
   workspace index, and session entry.
6. **Check the handoff.** Verify local links, ensure every created artifact is
   indexed, and ensure raw evidence is linked from the session that interprets
   it. Explicitly record temporary instrumentation, working-tree changes, and
   cleanup still required. Do not claim finalization if a required write or
   validation failed; identify what remains incomplete.

A later agent must be able to resume without reconstructing conclusions from
old session prose or the previous chat transcript.

### Final response and continuation prompt

After the artifacts are finalized, respond with a concise handoff summary and
a ready-to-copy prompt in a fenced text block. The prompt must use the actual
troubleshooting title, repository, and stable workspace path; it must not use
unresolved placeholders. Include the first recommended experiment from
`STATUS.md` so the new session has a concrete starting point, while making the
artifacts—not the copied prompt—the source of truth.

Use this shape:

```text
Continue “<Troubleshooting Title>” for repository <repo>.

Use the existing troubleshooting workspace at <absolute-workspace-path> and
follow the troubleshooting guide at
~/Artifacts/mycel/operations/troubleshooting.md. Read README.md and STATUS.md
first, then FINDINGS.md, DIDNT-WORK.md, REPRODUCTION.md, HYPOTHESES.md,
CODE-MAP.md, and the latest session file. Create the next incremented
SESSION-<NNN>-<slug>.md before running new experiments. Do not repeat a failed
direction unless its recorded retry condition is now true.

Resume with the current highest-priority next step: <first executable step from STATUS.md>.
```

The final response may also call out blockers, uncommitted changes, or
user-reported evidence that still needs verification. Do not paste the full
artifact contents or rely on chat-only context. If finalization was incomplete,
state that before the prompt and make the prompt identify the incomplete
handoff state rather than implying everything was persisted.

## Resolving, pausing, or abandoning

Mark the workspace `resolved` only when its success criteria are met and the
result has been validated at the appropriate level. Create `RESOLUTION.md` by
default and link every decisive finding, fix, test, MR/commit, and known
residual risk. Omit it only when the resolution is genuinely trivial and the
`README.md` records why a separate resolution artifact would add no value.

Use `paused` when work can continue but is intentionally deferred, and
`blocked` when a specific external condition prevents the next experiment.
Record the unblock condition in `STATUS.md`. If the direction is abandoned,
state why and what would justify reopening it; preserve the workspace because
its negative knowledge may prevent the same investigation from being repeated.

Do not move or delete a resolved workspace merely to clean up. Its stable path,
links, findings, and failed directions are the cross-session memory this
process is designed to preserve.
