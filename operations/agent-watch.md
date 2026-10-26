---
role: authored
---
# Guide: The Check from Outside

Every 5 minutes, a program with no AI in it looks at every agent working on
this Mac and measures what it did since its last progress: its last ticked
step, its last commit, or the owner's last message to it. When the numbers
say that something may be wrong, it raises a *signal*, such as "no tick for
16 min, 4.1M tokens: review". A signal asks for a *review*: a fresh agent of
the other tool reads a packet about the agent and answers whether it is
progressing, off the plan, looping or stuck. The answers are recorded; nothing
is steered or stopped yet.

For example, on 15 October 2026 a Codex thread on Mycel 2 and its three
sub-agent threads worked for 31 hours without a commit. Replayed, the check
raises its signal at 12:15 UTC that day, 1 h 03 min and 128 million tokens
after the owner's last message, and keeps it open until the threads go quiet
the next morning, by then at 2.3 billion tokens.

This guide is authoritative for what the check counts, when it raises and
ends a signal, the numbers it uses, which the owner agreed on 17 October
2026, and what the reviewer reads and answers. The program is
`~/Artifacts/sagas/tools/agent-watch/agent_watch.py`, with the reviewer in
`agent_review.py`, its prompt `reviewer-prompt.md` and the schema of its
answer `reviewer-schema.json` beside it: standard-library Python run as
`python3 -I`, with their tests. It reads transcripts, holds, git histories
and changed files, runs `git`, `ps` and `lsof`, and starts `claude` and
`codex` for the reviews. It writes only in `~/.sagas/watch/`, never changes an
agent's files, and never runs an Arbol program. How Beats are held and
ticked is [Working in Sagas](sagas.md); the stint every Beat runs under is
`beat` in [Stints](stints.md).

**Contents:** when to use · what is counted · the signals and their numbers ·
raising and ending a signal · the review · a run · what a run leaves ·
commands · not built yet.

## When to use

- The owner asks what the agents are doing, whether one is stuck, or what
  the check from outside saw: read `~/.sagas/watch/report.txt`, or run the
  check by hand (see [Commands](#commands)).
- The owner asks what a reviewer said about an agent: read
  `~/.sagas/watch/reviews.jsonl`, and the packet it names.
- A later Beat builds on the signals and the reviews: steering and stopping
  through a hook of the check's own (SYL-221), reports on Telegram
  (SYL-222), and the agent records (SYL-223).

Not for how far each Saga is ([Radar Statistics](radar-stats.md)), nor for
taking or releasing a Beat ([Working in Sagas](sagas.md)).

## What is counted

**An agent** is one Claude Code session or Codex thread together with its
sub-agents, watched as one: the four Mycel 2 threads above are one agent.

| Measure | Where it is found | How it is counted |
|---|---|---|
| Claude Code sessions | `~/.claude/projects/<folder>/<session>.jsonl`, sub-agents in `<session>/subagents/agent-<id>.jsonl` | Each file is read from where the last run stopped; a line still being written waits for the next run |
| Codex threads | `~/.codex/sessions/YYYY/MM/DD/rollout-…-<thread>.jsonl` | A sub-agent thread names its root in its first `session_meta`, at `source.subagent.thread_spawn.parent_thread_id`. It copies its root's `session_meta` later on; that copy is ignored |
| Tokens, Claude Code | each API call's `usage` | `input_tokens + cache_creation_input_tokens + cache_read_input_tokens + output_tokens`, once per `message.id`: one call shows in several entries |
| Tokens, Codex | `event_msg` of type `token_count` | the growth of `info.total_token_usage.total_tokens` |
| The owner's messages, Claude Code | `user` entries that are not tool results | `turnOrigin` is `human`; not `isMeta` and not a compaction summary. The desktop app puts a `<system-reminder>` before the owner's words, so such a message may begin with `<`. Prompts with `turnOrigin` `sdk` (another session) or `task_notification` (the app) are not the owner's. A file without `turnOrigin`, from an older version, counts a prompt that does not begin with `<` |
| The owner's messages, Codex | `response_item` of type `message`, role `user`, in a root thread | text not beginning with `<` or `# AGENTS.md`, plus `<send_user_message_question_reply>`, the owner's answer to a question. A sub-agent's prompts are its parent's tasks, never the owner's |
| Holds | `~/.sagas/holds/<Beat>.json` | the owner of a Claude Code hold lives while its process does, a Codex hold while a Codex process has its thread file open, read with `radar_stats.py`'s readers |
| Ticks | the git history of the held Beat's file in `~/Artifacts/sagas/` | a commit that ticks one or more leaves of its `## Plan`, at the commit's author time; ticks before the hold's `takenAt` belong to an earlier run. The plan's first commit counts too |
| Commits | the output of the agent's own commands, and the hold's branch | a line `[<branch> <commit>] <subject>` in a tool's output; for a hold with an Environment, the commits of `beat/<Beat>` not yet on `main`, each once |
| Changed files | one scan of `~/repos/sylvan-stack/` and `~/Artifacts/` | files changed since the last run, leaving out `.git`, `.venv`, `venv`, `node_modules`, the caches and `*_deprecated_v1` |

**The last progress** of a held Beat's agent is the latest of the hold's
taking, the plan's first commit in this run, its last tick, and the owner's
last message. Of an agent outside any Saga, it is the latest of its first
entry, its last commit and the owner's last message. **Tokens since the last
progress** add up the agent's sessions and sub-agents since that moment.

**A changed file** is given to the hold whose Environment holds it, else
to the agent whose transcript wrote it (Claude Code's `Write` and `Edit`,
Codex's `apply_patch`), else it is shown as *not attributed*. A file that git
does not track, or that is in no repository, is *outside git*. A file inside
another live hold's territory is marked with that Beat: territories keep
their paths, so `~/repos/sylvan-stack/hare/arbol/…` and its physical path
`~/repos/sylvan-stack/red/arbol/…` are inside a territory that names
`~/repos/sylvan-stack/arbol/`. Animal, color and numbered paths are the same
areas; aliases do not cause files to be scanned twice.

**Repeated drafts** are 3 or more names in one folder that are the same once
their version marks are taken out, at least two of them with one: `v2`,
`v12`, a date with or without a time, `final`, `draft`, `copy`, ` (2)`, or
`-2` after a letter. `report.md`, `report-v2.md` and `report-v3.md` are
drafts; `SYL-219.md`, `SYL-220.md` and `SYL-221.md` are not, nor are
`iso8859-1.enc` to `iso8859-16.enc`. The check looks at each changed file's
folder and at the folder above it, so draft folders count too.

## The signals and their numbers

Each signal calls a review, as [The review](#the-review) says; none steers
anything by itself.
The numbers are the owner's, 17 October 2026.

| Signal | When it is raised | Basis |
|---|---|---|
| How often the check runs | Every 5 minutes | The owner's value. Its first ten runs from the LaunchAgent, at low priority, took 1.4 to 1.8 s, and the first, which read the transcripts of the last 6 hours, 2.5 s: the scan of about 69,000 files takes most of it, and each transcript is read only where it grew |
| A Beat without a tick | 15 minutes since the last progress while the agent spends tokens | On 16 October, the 54 tick commits of 6 Beats came a median of 1 minute apart; 95% came within 6 minutes, and the longest gap was 38 minutes (SYL-179, which ticked 5 steps at once). One day of data |
| New ticks | A review of the steps ticked since the last one, at most every 15 minutes per agent, the first no sooner than 15 minutes after the hold is taken | Three runs between two reviews, so that each judges a stretch of work. It catches a step ticked without being done |
| A write outside the territory | At the next run: a file the hold's agent changed outside its territory and outside the files every Beat may add to (Working in Sagas) | The guide forbids it. A file inside another held Beat's territory says which Beat |
| A change before the plan | At the next run: a file the hold's agent changed, other than its Beat's file, before its plan was committed | The guide asks for the plan before any other change |
| A third draft of one name | At the next run, for any agent | The Mycel 2 run left drafts up to `v12` |
| The hard stop | The hold's `time` hard maximum has passed and the agent still spends tokens | The `beat` stint: 240 minutes |
| An agent outside any Saga | 60 minutes and 50 million tokens since its last progress, while it spends tokens | Without a plan, a commit is its only sign of progress. Between two commits an agent spent a median of 42 minutes and 19 million tokens (Claude Code) or 102 minutes (Codex), from 12 to 16 October |
| A session the owner is talking to | Nothing is raised while the owner wrote to it in the last 15 minutes | The owner is there |

**Not signals:** the same tool call made 3 times in 10 minutes happens in 63
of 154 normal transcripts, from `git status` and re-running tests, so it will
go to the reviewer as evidence only. **Files written outside git** are
counted and shown, and raise no signal until a week of counts gives a number.

## Raising and ending a signal

- **Raised once.** A signal is raised when it first holds and stays open;
  while open, its text follows the latest run. New ticks are the exception:
  they ask for one review and are not kept open.
- **Ended at progress.** An open signal ends when the agent makes progress
  after it was raised: a tick, the owner's message, or, outside any Saga, a
  commit. The hard stop is not ended by progress.
- **Ended when the agent ends:** its hold's owner is gone, its transcripts
  are gone, or its transcripts did not grow for 60 minutes. Until the agent
  records exist (SYL-223), an agent waiting an hour for the owner's answer
  counts as ended; when it goes on, a new signal can be raised.
- **The owner's 15 minutes.** No signal is raised for an agent the owner
  wrote to in the last 15 minutes. Its open signals end, since the owner's
  message is progress.
- **The first run** of the check reads whole only the transcripts changed in
  the last 6 hours, and counts as working only the agents whose transcripts
  grew in the last 5 minutes. A transcript first seen after that is read from
  then on.

## The review

A *review* is a fresh agent of the other tool that reads a *packet* about an
agent and answers one question: is it progressing, off the plan, looping or
stuck? Codex reviews a Claude Code agent, and Claude Code reviews a Codex
agent. The answers are recorded; nothing acts on them yet (SYL-221).

For example, at 20:43 UTC on 18 October 2026, after SYL-231's agent ticked
steps 1 to 3, Codex answered *progressing*, clear, no reason needed, with two
commits and step 4 as evidence, in 13 seconds and 41,500 tokens.

### When a review runs

- **At each signal raised, and at each review of new ticks.** At most once
  every 15 minutes per agent: a signal raised in between waits for the first
  run after the 15 minutes, and is dropped when it ended meanwhile. A review
  of new ticks is never dropped.
- **Never for a session the owner wrote to in the last 15 minutes,** since no
  signal is raised for it.
- **One at a time per agent.** A review with no result after 11 minutes is
  given up, and the report says so.
- **In a process of its own.** The run writes only `order.json` in the
  packet's folder and starts `agent_review.py` on it, so that the run still
  takes seconds. That process writes the packet, asks the reviewer and records
  the answer; the next run reads the result and shows it in the report.

### What the reviewer reads: the packet

`~/.sagas/watch/reviews/<time>-<tool>-<id>/packet.md`, for example
`20261018T204311Z-claude-dad749fe/`. It covers a *stretch*: from the agent's
last review, else from the hold's taking, else from its last progress, to the
review. It has four parts, each cut at its size with the cut marked:

| Part | What it holds | Size in characters |
|---|---|---|
| 1. The task | the stretch, the last progress and the tokens since, and the signals. For a held Beat: its title, goal, "Done when" and plan as they stand, the steps ticked in the stretch, the changes of its plan in the stretch (a commit that only ticks is one line), and the hold's territory. For an agent outside any Beat: its first message and the owner's last message. The comments beginning with `**Agent:**` that its own calls posted | 20,000 |
| 2. What it changed | each commit of the stretch, from its own commands' output and the hold's branch, with its patch; the uncommitted changes of the files it wrote with its own tools; the files it wrote outside git, listed with their sizes | 40,000 |
| 3. Its last test, lint and type-check commands | the last six such commands in its transcript, such as `pytest`, `unittest`, a `test_*.py`, `ruff`, `mypy` or `make check`, but no `git` command, each with the end of its output | 12,000 |
| 4. A sample of its transcript | its first message, then its last calls, results and messages, its sub-agents' included, back to the size. A result keeps its start and its end; a repeated identical call is marked "the same call as at 12:47:40, 3rd time" | 40,000 |

The transcripts are read again from their last 4 MB. The packet is the whole
prompt: the reviewer gets `reviewer-prompt.md` followed by the packet on
standard input, and no tools, so it reads nothing else on this Mac.

### What the reviewer answers

An answer in the form of `reviewer-schema.json`, with:

- **a verdict.** *Progressing*: the stretch moves toward the "Done when"
  along the plan; a long step still on course, and a step ticked whose work
  the packet shows, are progressing. *Off the plan*: it works on something no
  step names, or without a plan its task does not, or it ticked a step whose
  work the packet does not show. *Looping*: it repeats the same actions
  without getting further, such as the same command and failure with no
  change between them, a file rewritten back and forth, or one more draft.
  *Stuck*: it cannot get further on its own.
- **clear**, true or false, as below.
- **the reason** the agent gave for leaving its plan, or none.
- **up to three points of evidence**, each a kind (`step`, `file`, `commit`,
  `command` or `other`), a name (`2.3`, a path, a hash, a command as the
  transcript shows it) and one sentence.

An answer is **clear**, as the owner agreed on 17 October 2026, when its
evidence names at least two things the check can verify. The check verifies
each point; a point it cannot verify does not count:

| Kind | Verified when |
|---|---|
| step | the Beat's plan has a step of that number |
| file | the packet names it, or it exists: as given, or in the agent's working folder or a repository the check looked in |
| commit | the packet's diff shows it, or a repository the check looked in has it |
| command | the transcript's sample or the test results show it, word for word |
| other | never |

So an answer counts as clear only when the reviewer says so and two of its
points are verified.

**A reason**, as the owner agreed on 17 October 2026, is any one of these: a
change of the plan with an `**Agent:**` comment, as Working in Sagas asks; a
territory grown as the guide says; or a message in the session that says why
the work left the plan, such as a check that fails and is being fixed first.
A stray with a reason is reported, never steered.

A verdict is one reviewer's judgment, not a measure. The same packet judged
twice can get another verdict: the Mycel 2 thread as it stood at 13:00 UTC on
15 October was judged *looping*, then *progressing*, both clear.

### What is recorded

One line per review in `~/.sagas/watch/reviews.jsonl`, and the same in the
packet's `result.json`: its time, the agent, its tool and its reviewer, the
Beat, the signals, the packet, whether it is live or past, the outcome
(`answered`, `failed`, `timeout` or `invalid`), the seconds, the tokens, the
model and the cost the tool gives, the verdict, `clearSaid` (the reviewer's
word), `clear` (after the check), the reason, each point of evidence with
whether it was verified, and `would` with `why`.

A reviewer that fails, has no answer within 5 minutes, or answers outside
the schema leaves no verdict: `verdict` is null and `clear` false.

`would` is what the check would do under the rules in SYL-221's file, which
nothing carries out yet: **stop** when the hold's hard stop has passed, when
the agent wrote inside another held Beat's territory, or when the first
review after a *steer* finds it straying again; **steer** when the verdict is
*off the plan*, *looping* or *stuck*, clear, and no reason was given; else
**report**.

### The two tools

Each is started from a clean login shell with the owner's terminal settings,
in the packet's folder, and uses the owner's default model:

| The agent | Its reviewer | Started as |
|---|---|---|
| Claude Code | Codex | `codex exec --ephemeral --sandbox read-only --skip-git-repo-check --ignore-rules -c model_reasoning_effort="medium" -c developer_instructions="" -c mcp_servers={} --disable apps --disable browser_use --disable computer_use --output-schema reviewer-schema.json -o answer.json --json -` |
| Codex | Claude Code | `claude -p --safe-mode --no-session-persistence --tools "" --output-format json --json-schema <the schema>` |

- `--ephemeral` and `--no-session-persistence` keep no session, so a
  reviewer never shows up among the agents the check watches.
- Codex's reasoning effort is lowered to `medium` for reviews, because the
  owner's default is `ultra`. Its MCP servers, apps and the copy of the Hub
  in its settings are left out, and so are Claude Code's CLAUDE.md, hooks and
  MCP servers (`--safe-mode`): a review needs none of them.
- Neither tool writes outside the packet's folder, except its own state:
  `~/.claude.json`, and Codex's logs and thread-history databases.

### What data goes to which vendor

As the owner agreed on 17 October 2026, samples of a Claude Code transcript
go to OpenAI, through Codex, and samples of a Codex transcript go to
Anthropic, through Claude Code. What is sent is exactly `reviewer-prompt.md`
followed by the packet, which stays in its folder for the owner to read.

Before the packet is written, secrets of known shapes are masked as
`[secret masked]`: private keys; Anthropic, OpenAI, GitHub, GitLab, Slack,
AWS, Google, Linear and Stripe keys; Telegram bots' tokens; JSON web tokens;
bearer tokens; the value after `password=`, `api_key=`, `token=`, `secret=`
and the like; and a password in an address such as `postgres://u:p@host`.
A secret of another shape is not masked.

### Cost and time

Estimated at 0.1 to 0.5 million tokens a review, measured on 17 and 18
October 2026 over 10 reviews: 35,000 to 52,000 tokens each. A review took 10
to 38 seconds by hand, and 67 to 95 seconds when the LaunchAgent started it:
the LaunchAgent runs at low priority, and so do the processes it starts. With at most 4 reviews an hour, a
busy agent costs at most about 0.2 million tokens an hour in reviews.

## A run

1. Take the lock `~/.sagas/watch/lock`; when another run holds it, end.
2. Read every transcript from where the last run stopped, and join each
   sub-agent to its session or thread.
3. Read the holds, and whether each owner lives.
4. Scan for files changed since the last run (the first run: the last 5
   minutes), and give each to a hold or an agent.
5. For every hold, every agent that spent tokens since the last run, and
   every agent with an open signal: its last progress, the tokens since, its
   files, its drafts and its signals. For a hold, the git history of its
   Beat's file and the commits of its branch.
6. Raise and end signals as above.
7. Read the results of the reviews that finished, and start the reviews
   that are due, as [The review](#the-review) says. Then write what the run
   leaves.

## What a run leaves

All in `~/.sagas/watch/`, on this Mac only:

| File | What it holds |
|---|---|
| `events.jsonl` | one line for each signal raised or ended and each review of new ticks: the time, the agent, its Beat, the signal, its text, the last progress and the tokens since, and why it ended |
| `report.txt`, `report.json` | the last run, as the table and as JSON |
| `runs.jsonl` | one line per run: its time, how long it took, how many agents, files and events |
| `state.json` | where each transcript was read to, a token count per minute for each, the open signals, the signals that wait for a review, each agent's running and last review and the time of its last, and the time of the last run. Delete it to start afresh; the next run is a first run |
| `reviews/<time>-<tool>-<id>/` | one folder per review: `order.json`, `packet.md`, `meta.json`, the reviewer's output, and `result.json`. A past review's folder has `past-` before the tool |
| `reviews.jsonl` | one line per review, as [What is recorded](#what-is-recorded) says |
| `launchd.log` | the LaunchAgent's output, empty unless a run fails |

## Commands

- **One run by hand:** `python3 -I ~/Artifacts/sagas/tools/agent-watch/agent_watch.py`
  prints the table; `--json` prints JSON. A run by hand is a run like the
  LaunchAgent's: it moves the last run's time.
- **The replay:** `python3 -I ~/Artifacts/sagas/tools/agent-watch/agent_watch.py --replay 2026-10-15T00:00 2026-10-16T23:59`
  runs the check every 5 minutes (`--step` changes it) over the transcripts
  as they stood at each time, both times in UTC, and prints the agents it
  flags with each thread's tokens. It reads no holds and no changed files,
  whose past is not kept, and writes nothing. Over 15 and 16 October it
  flags 6 agents, the Mycel 2 threads among them at 12:15 UTC on 15 October,
  in about 6 seconds.
- **Every 5 minutes:** `python3 -I ~/Artifacts/sagas/tools/agent-watch/agent_watch.py --install`
  writes `~/Library/LaunchAgents/com.sylvan-stack.agent-watch.plist` and
  loads it, keeping a copy of one it replaces in `~/.sagas/watch/`. It runs
  `/opt/homebrew/bin/python3 -I … --quiet` every 300 seconds with
  `PATH=/usr/bin:/bin:/usr/sbin:/sbin`. `--uninstall` unloads and removes it.
  `launchctl print gui/$(id -u)/com.sylvan-stack.agent-watch` shows its runs
  and last exit code.
- **A past review by hand:** `python3 -I ~/Artifacts/sagas/tools/agent-watch/agent_review.py --past codex:01a13f36-33f6-77e0-8ba9-12dfd885e5bc --at 2026-10-15T13:00`
  writes the packet of an agent as its transcripts stood at that UTC time,
  runs its review now and prints the record, which also goes into
  `reviews.jsonl` as a past one. `--since` starts the stretch (by default at
  the agent's last progress), `--beat SYL-219` gives the Beat it held, whose
  file is read as it stood then, and `--signal` the signal's text, which is
  otherwise worked out as a run would. Uncommitted changes of a past time are
  not known.
- **The tests:** `python3 -I ~/Artifacts/sagas/tools/agent-watch/test_agent_watch.py`
  and `python3 -I ~/Artifacts/sagas/tools/agent-watch/test_agent_review.py`,
  with transcripts, holds, Beat files and git histories made in a temporary
  home, and stand-in `claude` and `codex` programs started through a clean
  login shell as the real ones are.

## Not built yet

- **Steering and stopping** through a hook of the check's own, by the
  reviews' answers and the stint (SYL-221): until then a verdict and its
  `would` are only recorded. **Reports on Telegram** (SYL-222).
- **The agent records** (SYL-223): the check cannot yet tell an agent waiting
  for the owner or for a long command from one that is idle; neither spends
  tokens, so neither is flagged.
- **Files written by a program the agent runs**, such as a script or a
  `bash` redirect, are not given to the agent: only its own `Write`, `Edit`
  and `apply_patch` are, and the files in its hold's Environment. They
  show as not attributed, with the Beat whose territory holds them.
- **Agents on other machines**, and in the cloud.
