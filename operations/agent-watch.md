---
role: authored
---
# Guide: The Check from Outside

Every 5 minutes, a program with no AI in it looks at every agent working on
this Mac and measures what it did since its last progress: its last ticked
step, its last commit, or the owner's last message to it. When the numbers
say that something may be wrong, it raises a *signal*, such as "no tick for
16 min, 4.1M tokens: review". A signal only asks for a review; it steers and
stops nothing.

For example, on 15 October 2026 a Codex thread on Mycel 2 and its three
sub-agent threads worked for 31 hours without a commit. Replayed, the check
raises its signal at 12:15 UTC that day, 1 h 03 min and 128 million tokens
after the owner's last message, and keeps it open until the threads go quiet
the next morning, by then at 2.3 billion tokens.

This guide is authoritative for what the check counts, when it raises and
ends a signal, and the numbers it uses, which the owner agreed on 17 October
2026. The program is `~/Artifacts/sagas/tools/agent-watch/agent_watch.py`,
standard-library Python run as `python3 -I`, with its tests beside it. It
reads transcripts, holds, git histories and changed files, and runs `git`,
`ps` and `lsof`. It writes only in `~/.sagas/watch/`, never changes an
agent's files, and never runs an Arbol program. How Beats are held and
ticked is [Working in Sagas](sagas.md); the stint every Beat runs under is
`beat` in [Stints](stints.md).

**Contents:** when to use · what is counted · the signals and their numbers ·
raising and ending a signal · a run · what a run leaves · commands · not
built yet.

## When to use

- The owner asks what the agents are doing, whether one is stuck, or what
  the check from outside saw: read `~/.sagas/watch/report.txt`, or run the
  check by hand (see [Commands](#commands)).
- A later Beat builds on the signals: the reviewer of the other tool
  (SYL-220), steering and stopping through a hook of the check's own
  (SYL-221), reports on Telegram (SYL-222), and the agent records (SYL-223).

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
| Commits | the output of the agent's own commands, and the hold's branch | a line `[<branch> <commit>] <subject>` in a tool's output; for a hold with a prepared folder, the commits of `beat/<Beat>` not yet on `main`, each once |
| Changed files | one scan of `~/repos/sylvan-stack/` and `~/Artifacts/` | files changed since the last run, leaving out `.git`, `.venv`, `venv`, `node_modules`, the caches and `*_deprecated_v1` |

**The last progress** of a held Beat's agent is the latest of the hold's
taking, the plan's first commit in this run, its last tick, and the owner's
last message. Of an agent outside any Saga, it is the latest of its first
entry, its last commit and the owner's last message. **Tokens since the last
progress** add up the agent's sessions and sub-agents since that moment.

**A changed file** is given to the hold whose prepared folder holds it, else
to the agent whose transcript wrote it (Claude Code's `Write` and `Edit`,
Codex's `apply_patch`), else it is shown as *not attributed*. A file that git
does not track, or that is in no repository, is *outside git*. A file inside
another live hold's territory is marked with that Beat: territories keep
their paths, so `~/repos/sylvan-stack/4/arbol/…` is inside a territory that
names `~/repos/sylvan-stack/arbol/`.

**Repeated drafts** are 3 or more names in one folder that are the same once
their version marks are taken out, at least two of them with one: `v2`,
`v12`, a date with or without a time, `final`, `draft`, `copy`, ` (2)`, or
`-2` after a letter. `report.md`, `report-v2.md` and `report-v3.md` are
drafts; `SYL-219.md`, `SYL-220.md` and `SYL-221.md` are not, nor are
`iso8859-1.enc` to `iso8859-16.enc`. The check looks at each changed file's
folder and at the folder above it, so draft folders count too.

## The signals and their numbers

Each signal calls the reviewer of SYL-220; none steers anything by itself.
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
6. Raise and end signals as above, and write what the run leaves.

## What a run leaves

All in `~/.sagas/watch/`, on this Mac only:

| File | What it holds |
|---|---|
| `events.jsonl` | one line for each signal raised or ended and each review of new ticks: the time, the agent, its Beat, the signal, its text, the last progress and the tokens since, and why it ended |
| `report.txt`, `report.json` | the last run, as the table and as JSON |
| `runs.jsonl` | one line per run: its time, how long it took, how many agents, files and events |
| `state.json` | where each transcript was read to, a token count per minute for each, the open signals, and the time of the last run. Delete it to start afresh; the next run is a first run |
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
- **The tests:** `python3 -I ~/Artifacts/sagas/tools/agent-watch/test_agent_watch.py`,
  with transcripts, holds, Beat files and git histories made in a temporary
  home.

## Not built yet

- **The reviewer** (SYL-220): a fresh agent of the other tool that judges
  what a signal points at. Until then the signals are only recorded.
- **Steering and stopping** through a hook of the check's own (SYL-221), and
  **reports on Telegram** (SYL-222).
- **The agent records** (SYL-223): the check cannot yet tell an agent waiting
  for the owner or for a long command from one that is idle; neither spends
  tokens, so neither is flagged.
- **Files written by a program the agent runs**, such as a script or a
  `bash` redirect, are not given to the agent: only its own `Write`, `Edit`
  and `apply_patch` are, and the files in its hold's prepared folder. They
  show as not attributed, with the Beat whose territory holds them.
- **Agents on other machines**, and in the cloud.
