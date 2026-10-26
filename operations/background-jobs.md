---
role: authored
---
# Guide: Background Jobs

A chat whose agent waits for a long command looks idle in most coding apps,
so the owner cannot tell whether work is still running, finished or died.
This guide makes every such command visible outside the chat: in the macOS
menu bar, under the title of the chat that started it, with its elapsed time
and progress, and with a notification when it ends. It applies to every agent
on this Mac, Claude Code and Codex alike, and to the owner's own commands.

For example, a session titled "Radar stats" runs a Mycel ingest. The menu bar
shows `⏳ 1`; its menu reads:

```
Chat “Radar stats” in Claude Code (1d04a622)
⏳ Mycel: ingest of the mycel repository only — running 12m40s
```

When the ingest ends, macOS shows "Background job: Finished — Mycel: ingest
of the mycel repository only · 1h04m", or "Failed (exit 1)".

This guide is authoritative for when a command must be recorded, how to
record it and what the states mean. The recorder is
`~/Artifacts/sagas/tools/bgjobs/bgjob.py`, standard-library Python with its
tests beside it, installed as `~/.local/bin/bgjob`. The menu bar item is the
SwiftBar plugin `~/.sagas/swiftbar/bgjobs.10s.sh`, refreshed every 10 seconds.

## When to record a command

Record any command that may run more than **5 minutes**: complete check
suites, Build creation, ingest, embedding, imports, long downloads or
migrations. A command that will surely end within 5 minutes needs no record.
When a command already running turns out to be long, attach to it.

## Split long work into smaller steps

Whenever the tool allows it, run long work as a series of smaller steps
instead of one long command, and record each step as its own job, one after
another. Each step then shows its own progress and end, a failure loses only
that step, and the next step can be corrected before it starts.

| Work | Smallest step the tool allows |
|---|---|
| Mycel ingest or embedding of several repositories | one repository: `--repo <name>`, never `--all` |
| Mycel recovery or audit of a large repository | one path: `--path <folder or file>`, with `--k` to bound each command |
| A batch import of many items | one batch file per slice of the items |
| A complete check suite (`make check`) | none: its count is only valid for the complete run, so it stays one job |

Name each step so the series reads in order, for example "Mycel ingest 2 of
3: arbol". When a single step still runs long, as one repository's ingest can,
it cannot be split further: record it, give it a progress line if it has one,
and say in the chat that it is one indivisible step.

## Record a new command

```sh
bgjob run --name "Mycel: ingest of the mycel repository only" -- mycel ingest --repo mycel
bgjob run --name "Mycel: complete make check" --log /path/outside/repos/check.log -- make check
bgjob run --name "Mycel: first embedding" --progress-cmd '/path/to/progress.sh' -- mycel embed --repo mycel
```

- **The name** says in plain words what runs and on what, as the owner would
  say it, without IDs: "Mycel: complete make check", not "job 3".
- **Progress:** `--log <file>` shows the last line of a log the command
  writes, such as `Checks: 1300/1803 complete`; `--progress-cmd <command>`
  shows the last line a probe prints, for example a count from the program's
  own activity record. Give one when the command reports progress; without
  one the menu shows the elapsed time only.
- **Output and exit status** pass through unchanged, so `bgjob run` can stand
  in front of any command, including in a background shell of the agent.
- **The chat** is found from the environment: `CLAUDE_CODE_SESSION_ID` for
  Claude Code, `CODEX_THREAD_ID` for Codex. Its title is read from the chat's
  own record (the transcript's latest `custom-title`, or the Codex thread name
  in `~/.codex/session_index.jsonl`) and refreshed every 5 minutes, so a
  renamed chat shows its new title.

## Attach to a command already running

```sh
nohup bgjob watch --pid 61421 --name "Mycel: ingest of all repositories" \
  --exit-file /path/run.log --log /path/run.log > /dev/null 2>&1 &
```

The watcher takes the start time, folder and command line from the process
itself and follows it until it ends. It cannot see the exit status of a
process it did not start: give `--exit-file` a file to which the starting
shell appends `exit <status>`, as `cmd; echo "exit $?" >> run.log` does;
otherwise the job ends as `ended`, without a status.

## What the menu bar shows

| Title | Meaning |
|---|---|
| `⏳ N` | N jobs are running |
| `⚠️` | none runs, and a job failed or was lost in the last 24 hours |
| `✅` | every job of the last 24 hours finished |
| `·` | no job in the last 24 hours |

| State | Meaning |
|---|---|
| running | the command runs and its recorder is alive |
| unwatched | the command still runs but its recorder is gone: nothing will notify its end |
| lost | the recorder is gone and so is the command: how it ended is unknown |
| done | it ended with status 0 |
| failed | it ended with another status |
| ended | an attached process ended without a known status |

Jobs are grouped under their chat; jobs started outside any agent say so. The
menu keeps ended jobs for 24 hours. "Forget ended jobs" removes them at
once; `bgjob status` prints the same list in a terminal, and
`bgjob status --json` gives it to a program.

## When something looks wrong

- **Unwatched or lost:** the recorder died, for example because its shell was
  closed. An agent checks the process (`ps -p <pid>`) and its log, reports
  what it finds, and attaches a new watcher to a process still running.
- **A job runs much longer than its kind usually takes:** the agent says so
  in its chat with the measured time, and looks at why before starting it
  again.
- Records are JSON files in `~/.sagas/jobs/`; the recorder writes nothing
  else and changes no repository.

## Not built yet

- SwiftBar does not start at login unless the owner turns that on in its
  settings or in System Settings → General → Login Items.
- The menu cannot open the chat itself; it names it.
- The [check from outside](agent-watch.md) does not yet read these records,
  so an agent waiting for a recorded job can still look stale to it.
