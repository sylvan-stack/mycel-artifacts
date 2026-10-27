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
| Commits | the output of the agent's own commands, and the hold's branch | a line `[<branch> <commit>] <subject>` in a tool's output; for a hold with a work area, the commits of `beat/<Beat>` not yet on `main`, each once |
| Changed files | one scan of `~/repos/sylvan-stack/` and `~/Artifacts/` | files changed since the last run, leaving out `.git`, `.venv`, `venv`, `node_modules`, the caches and `*_deprecated_v1` |

**The last progress** of a held Beat's agent is the latest of the hold's
taking, the plan's first commit in this run, its last tick, and the owner's
last message. Of an agent outside any Saga, it is the latest of its first
entry, its last commit and the owner's last message. **Tokens since the last
progress** add up the agent's sessions and sub-agents since that moment.

**A changed file** is given to the hold whose work area holds it, else
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

## Steering and stopping

This is the SYL-221 implementation protocol, settled on 26 October 2026 before its code. Actions remain disabled until the qualified hook installation activates them; existing review history is not replayed.

### When an action is justified

A review only reports unless its verdict is off the plan, looping or stuck, its evidence is clear by the rules above, and no reason was given. Such a review steers once. For stuck, the message asks the agent to stop at a safe point and ask the owner. A stop is justified only by the held Beat's hard time limit being passed while the agent still spends tokens, a proven write inside another live held Beat's territory, or the first review after an actually delivered steer clearly finding the same verdict again with no reason. A proposed or queued steer is not a delivered steer. The first subsequent review consumes that escalation opportunity even when it finds progress, a reason, uncertainty or a different verdict.

The check never steers or stops during the 15 minutes after a real message from the owner. It never kills or interrupts a process. `ARBOL_ROOT` marks an Arbol chat, which this hook always lets through. Agent-record hooks remain watching hooks and are not changed.

<!-- sources:
sagas:@code/tools/agent-watch/agent_actions.py#observe
sagas:@code/tools/agent-watch/test_agent_actions.py#Actions
-->

### Action files and their lifetime

`control.json` under `~/.sagas/watch/` is the explicit activation switch and starting time. Installation enables only new observations and reviews begun after that time; past reviews and in-flight older packets stay historical. The normal check does not create an enabled switch by itself.

A private `steer/` directory holds one small JSON action per provider/session. Each action names its provider/session, steer or stop, issue time, reason/verdict, current hold's Beat and taking time when there is one, own Beat/Arc/hold paths, and root-transcript cursors. Atomic rename and one shared lock protect writers, one-use consumption and lifting. Only an actual blocked call consumes a steer and records delivery. A stop stays until its exact hold is released or replaced, or the owner lifts it. A file for an older run cannot act on a newly taken hold, even for the same Beat. An unheld session's stop lasts until lifted.

The control record keeps only action metadata, actual deliveries, first-follow-up review identity and lift watermarks; the action log contains these transitions, not prompts, tool payloads or transcript text. The hook uses no network and starts no lasting process. An unreadable, malformed, stale or unverifiable action, lock timeout, missing program or other fault of the hook lets the tool call through silently. The check can report the fault later; a broken hook must not block the session that could repair it.

Lifting removes the pending action and old escalation opportunity and records a watermark. An already running or older review cannot reinstate it. The same deterministic hard-stop/foreign-territory signal episode is not recreated after a lift; genuinely new observations/reviews can be considered again. Releasing a hold clears only actions for that exact run. Concurrent consumption or lifting cannot erase a newer replacement action.

<!-- sources:
sagas:@code/tools/agent-watch/agent_control.py#object_file
sagas:@code/tools/agent-watch/agent_control.py#atomic
sagas:@code/tools/agent-watch/agent_control.py#locked
sagas:@code/tools/agent-watch/agent_control.py#same_hold
sagas:@code/tools/agent-watch/agent_control.py#transition
sagas:@code/tools/agent-watch/agent_control.py#lift
sagas:@code/tools/agent-watch/test_agent_hook.py#Hook
sagas:@code/tools/agent-watch/agent_actions.py#action_state
sagas:@code/tools/agent-watch/agent_actions.py#queue
sagas:@code/tools/agent-watch/agent_actions.py#cursors
sagas:@code/tools/agent-watch/agent_review.py#after_run
sagas:@code/tools/agent-watch/agent_watch.py#run
-->

### Fresh messages from the owner

The writer captures the owner's latest message time and each root transcript's complete-line byte position and file identity from the current check. Before blocking, the hook reads only bytes appended since those cursors, in memory, using the same provider-specific human-message rules as the check. It persists only cursor metadata and the latest owner timestamp, never text. A new owner message suppresses the action until its 15 minutes end. Missing, rotated, truncated or excessively grown transcripts whose owner freshness cannot be established let the call through; they never count as evidence that the owner is absent. This also protects the gap between a five-minute check and the next tool call.

<!-- sources:
sagas:@code/tools/agent-watch/agent_control.py#fresh_owner
sagas:@code/tools/agent-watch/test_agent_hook.py#Hook.test_a_new_owner_message_after_the_check_suppresses_each_provider_without_consuming
-->

### What a stopped agent may do

The stop is a wrap-up policy for recognized tool calls, not an operating-system permission boundary. It permits file reads, git commands, editing its own Beat file, editing only its Arc's Progress section, deleting only its own matching hold, and Linear comments. Direct read tools and known filesystem-read MCP calls are allowed. Shell calls are parsed conservatively: simple read commands and git are allowed, as is a literal deletion of the one own hold; shell substitutions, arbitrary interpreters, background commands, redirects that write, unknown commands and mixed unrelated mutations are refused. An agent can split an ambiguous call into these small supported operations.

An apply_patch update of its own Beat file is permitted. An Arc update must be anchored wholly inside the unique current Progress section; creating/deleting that Arc or changing other sections is refused. Unknown edit shapes are refused. A Linear comment call is permitted; broader Linear issue/document mutations are not comments. The owner can run the lift command from a terminal; a stopped agent does not get permission to lift its own stop.

The block message names why the agent was stopped and how to commit/push what works, write the hand-over, return the work area, comment and release its hold. It includes the concrete own paths and the owner's lift command. Read-only transport/orchestration wrappers are allowed only where the provider invokes the hook again for their nested operations. Hosted tools and specialized paths which the provider does not hook are outside this policy's coverage; a write to an already open shell session is transport and is not intercepted again. No process is killed to close these gaps. Current Codex coverage and exit-status-2 behavior are documented in the [official hook reference](https://learn.chatgpt.com/docs/hooks); provider live checks record the actual tool names/events.

<!-- sources:
sagas:@code/tools/agent-watch/hook_policy.py#allowed
sagas:@code/tools/agent-watch/hook_policy.py#shell
sagas:@code/tools/agent-watch/hook_policy.py#patch
sagas:@code/tools/agent-watch/hook_policy.py#arc_edit
sagas:@code/tools/agent-watch/test_agent_hook.py#Policy
-->

### Installing, trust and speed

`agent-watch-hook claude-code` or `agent-watch-hook codex` is one fixed command under `~/.local/bin`. Its shell launcher exits before Python when there are no action JSON files or it is an Arbol chat. Otherwise it starts the fixed qualified Python implementation in the foreground; only an intended block prints its message and exits 2, every other outcome exits 0 silently. The no-action path is measured over 20 fresh processes against a 50 ms median.

The independent installer adds one foreground PreToolUse group for its exact command to each provider's own settings, with a five-second limit. It writes whole JSON files atomically, preserves every unrelated entry and order, refuses unreadable/malformed settings, and never adds a duplicate. Before its first change to a file or launcher it keeps a non-overwritten backup, or records that the path was absent. Codex trust is obtained from hooks/list and written through config/batchWrite, using only its own key/currentHash and preserving other trust/configuration entries; it never computes a provider hash or rewrites TOML by hand. Uninstall removes exactly its commands and trust entries and disables its action switch. Status reports installation, activation, trust and tool versions.

The launcher checks that its interpreter is executable and its Python script is a readable file before starting it; Python's own missing-script exit status 2 is not an intentional policy block. Uninstall preserves empty hook groups when removing a group would move another Codex hook's index-based trust key. It removes a launcher only while its bytes still match this installer's own file; owner changes and every first backup stay. An explicit provider setting that disables all hooks is preserved and installation refuses rather than enabling unrelated hooks.

Running Claude sessions retain their old hooks; Codex's desktop app must be reopened to load them. No restart or process kill is performed by the installer. Reviewers stay out of their own hook: Claude uses safe-mode and Codex explicitly disables hooks. The existing five-minute LaunchAgent and existing hooks are preserved.

<!-- sources:
sagas:@code/tools/agent-watch/agent_hook.py#launcher
sagas:@code/tools/agent-watch/agent_hook.py#run
sagas:@code/tools/agent-watch/agent_hook.py#main
sagas:@code/tools/agent-watch/test_agent_hook.py#Hook.test_wrapper_has_an_empty_fast_path_arbol_chat_bypass_and_silent_missing_runtime
sagas:@code/tools/agent-watch/hook_install.py#install
sagas:@code/tools/agent-watch/hook_install.py#uninstall
sagas:@code/tools/agent-watch/hook_install.py#status
sagas:@code/tools/agent-watch/hook_install.py#backup
sagas:@code/tools/agent-watch/hook_install.py#document
sagas:@code/tools/agent-watch/hook_codex.py#Codex
sagas:@code/tools/agent-watch/test_hook_install.py#Installation
sagas:@code/tools/agent-watch/test_hook_codex.py#Protocol
sagas:@code/tools/agent-watch/test_agent_hook.py#Hook.test_twenty_no_action_calls_stay_below_the_fifty_millisecond_median
sagas:@code/tools/agent-watch/hook_live.py#live
sagas:@code/tools/agent-watch/hook_live.py#claude_token
sagas:@code/tools/agent-watch/hook_live_controller.py#main
sagas:@code/tools/agent-watch/test_hook_live.py#LiveFixture
-->

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
- **Install steering hooks after qualification:** `python3 -I ~/Artifacts/sagas/tools/agent-watch/agent_watch.py --install-hooks` creates the fixed `agent-watch` and `agent-watch-hook` launchers, backs up settings, obtains and verifies Codex trust, and only then enables new actions. First backups and absent-path records are retained under `~/.sagas/watch/hook-backups/` and `hook-installation.json`; no old review is replayed.
- **Status:** `agent-watch --status-hooks` reports each provider’s entry, the Codex hook’s trust and enabled state, action activation and local tool versions. A trusted definition still needs to be enabled and loaded in the current session.
- **Lift:** the owner runs `agent-watch --lift codex:<session UUID>` or `agent-watch --lift claude:<session UUID>`. This removes that session’s pending action, clears its escalation opportunity and records the watermark. A stopped agent cannot lift its own stop through the permitted wrap-up calls.
- **Uninstall only steering:** `agent-watch --uninstall-hooks` disables actions and removes only the exact owned hook commands/trust and unchanged owned launchers. The independent five-minute LaunchAgent and other owners’ hooks are preserved. Hook controls can always be run through the Python source command above, including after uninstall removed the convenience launcher.
- **All private tests:** `python3 -I -B -m unittest discover -s ~/Artifacts/sagas/tools/agent-watch -p 'test_*.py'`. The explicit live fixture is `hook_live.py --provider codex|claude-code --evidence <new private folder>`; it is never run by discovery. It uses a test profile, synthetic actions around the real fixed hook and a throwaway home. The Claude test token is read from its existing profile’s Keychain entry into the child’s environment only, with no login or credential write. Do not run it while that account has a known rate limit. Results and traces stay outside Git.
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
  and `apply_patch` are, and the files in its hold's work area. They
  show as not attributed, with the Beat whose territory holds them.
- **Agents on other machines**, and in the cloud.
