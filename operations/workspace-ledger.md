---
role: authored
---
# Workspace Booking and Workspace Ledger

This document defines the proposed lifecycle and file format for the
Workspace Ledger for a named area such as **Beaver Workspace**. It extends
[Working in Sagas](sagas.md#named-work-areas).

**Status: design, not an activated runtime procedure.** The owner chose the
directory layout, a booking independent of a Chat Session, capture of every
tool call and file change, and Saga-linked bookings by default with named
ad-hoc work allowed on 26 October 2026. The schema, controller and capture
mechanisms below are proposed implementation choices. Existing live booking
and hold procedures remain in force until a tested migration activates this
design. No hook or recorder has been installed by writing this document.

## Workspace Booking

A **Workspace Booking** is the period from holding or booking a named area
until explicitly releasing it. Each booking has a permanent `booking_id`.
The reservation belongs to the work, normally a Saga, rather than to the
Chat Session that happened to start it.

- One named area has at most one open booking. A Saga can have several
  bookings in different named areas when their territories allow parallel work.
- A booking names one work scope: a stable Saga reference, or an explicit
  ad-hoc work reference and title. The latter preserves work outside Sagas.
- Arc and Beat references describe work within that scope. A booking can
  continue through successive Beats of the same Saga; completing a Beat
  alone does not end it. A different Saga requires release and a new booking.
- Several authorized Chat Sessions and their subagents can participate in
  the same booking. They share its `booking_id` and event stream. Joining,
  leaving, context compaction, interruption, retiring a Chat Session and
  transferring work to a replacement Chat Session do not rotate its files.
- One participant coordinates admission, work allocation and release. A
  handoff changes that participant while preserving the booking. A lost
  participant requires recovery or handoff; it does not free the area.
- Sharing a booking preserves territory rules. Participants coordinate
  edits, and serialize operations that affect the whole checkout, such as
  changing branches or modifying the Git index. A shared booking by itself
  does not prevent two participants editing the same file.

For example, a Chat Session books **Beaver Workspace** for a Saga, starts
two subagents, and hands coordination to a replacement Chat Session. All
four participate in one Workspace Booking. Its start time stays unchanged.

## Files on disk

```text
~/repos/sylvan-stack/beaver/
  .ledger/
    current.jsonl
    booking-2026-10-26-12-56-00Z-<booking_id>.jsonl
    history.jsonl
  mycel/
  arbol/
  ...
```

| File | Contents and lifetime |
|---|---|
| `.ledger/current.jsonl` | Only the open booking, starting with its opening record and containing its participants, tool calls, file changes and work notes. Absent when the area is free; never reused by truncating an old booking |
| `.ledger/booking-<start-time>-<booking_id>.jsonl` | A closed booking, produced by renaming `current.jsonl` on release. It retains the complete event stream and is immutable after closure |
| `.ledger/history.jsonl` | The area's append-only index: booking starts, releases, adoptions, coordination handoffs and capture/recovery incidents. Lifecycle entries identify the booking and its archive filename; detailed tool and file events stay in the booking file |

Resolve animal, color and numbered aliases to one physical area before
locking or writing. **Beaver Workspace** and its old color path therefore
share one `.ledger/` directory.

The archive basename is reserved when the booking opens. Proposed naming
uses the start time in UTC, with seconds, an explicit `Z` and the complete
booking ID, avoiding minute collisions and daylight-saving ambiguity. The
example above represents 13:56 in Europe/Madrid on 26 October 2026. Human
views can show local time without changing stored timestamps.

Every lifecycle entry carries the reserved `booking_file` path. While that
booking is open, a reader resolves its ID to `current.jsonl`; after release,
it resolves to the archive. A historical link must never open a later
booking merely because it is now in `current.jsonl`.

The whole `.ledger/` directory is local, Git-ignored operational data. Do not
commit it or place it inside one repository's checkout. The current named
areas sit outside their repositories' Git roots; a `.ledger/` entry in the
machine's Git ignore file also protects this name if the layout changes.
Git ignoring is separate from capture: ignored dependency files are still
in capture scope. Ignore rules do not supply a backup or retention policy.

## JSON Lines format

Every record is one complete UTF-8 JSON object followed by a newline. The
same envelope is used in all three file types:

```json
{
  "schema": 1,
  "event_id": "22222222-2222-4222-8222-222222222222",
  "sequence": 1,
  "recorded_at": "2026-10-26T12:56:00.000Z",
  "occurred_at": "2026-10-26T12:56:00.000Z",
  "workspace": "beaver",
  "booking_id": "11111111-1111-4111-8111-111111111111",
  "type": "booking.started",
  "actor": {"tool": "codex", "chat_session_id": "<chat-id>", "agent_id": "<agent-id>"},
  "source": {"kind": "controller", "id": "<producer-id>", "sequence": 1},
  "data": {
    "scope": {"kind": "saga", "ref": "<saga-reference>", "title": "<Saga name>"},
    "started_at": "2026-10-26T12:56:00.000Z",
    "coordinator": {"tool": "codex", "chat_session_id": "<chat-id>", "agent_id": "<agent-id>"},
    "participants": [{"tool": "codex", "chat_session_id": "<chat-id>", "agent_id": "<agent-id>"}],
    "capture": {"roots": ["."], "excluded_roots": [".ledger/"], "status": "not_qualified"},
    "booking_file": "booking-2026-10-26-12-56-00Z-11111111-1111-4111-8111-111111111111.jsonl"
  }
}
```

This example is expanded for reading; its on-disk form is one line. Capture
must be qualified before this illustrative booking can admit tool calls.

| Field | Rule |
|---|---|
| `schema` | Format version; proposed initial version is `1` |
| `event_id` | Stable unique identity supplied before recording. Retrying the same event does not append it again. Reusing the ID with conflicting content is an error |
| `sequence` | Controller-assigned increasing order across this named area's ledger. A lifecycle record copied to `history.jsonl` keeps its identity and sequence; that index therefore has gaps |
| `recorded_at`, `occurred_at` | UTC timestamps. The controller assigns recording time; source occurrence time is `null` if unknown. Recording order does not claim causal order between concurrent producers |
| `workspace` | Stable animal key, such as `beaver`; human views render **Beaver Workspace**. Aliases never create a second identity |
| `booking_id` | Stable identity of the booking; `null` is permitted only for an area-level incident outside any booking |
| `type` | Event kind from the table below |
| `actor` | Tool, Chat Session and distinct agent identities, or `null` when attribution is unknown. Subagents remain distinguishable even when a host reports their parent's Chat Session ID |
| `source` | Capture source kind, producer identity and source sequence/cursor, so duplicate or missing deliveries can be detected |
| `data` | Event-specific structured fields; human descriptions supplement these fields |

The opening record contains the work scope, coordinator, registered
participants and capture coverage. An ad-hoc scope uses `kind: "ad_hoc"`,
a stable work reference and a title. Later records reference the booking ID
and carry the current Arc/Beat references when applicable.

## Events and capture scope

| Kind | Required information |
|---|---|
| `booking.started` | Work scope, start time, coordinator, initial participants, reserved archive path and capture scope |
| `participant.joined`, `participant.left` | Chat Session/agent identity and relationship to its delegating participant |
| `booking.handoff` | Previous and new coordinator, reason and continuation references |
| `work.context` | Current Saga/Arc/Beat references within the booking's work scope |
| `tool.started` | Host invocation ID, tool name, arguments or an explicit payload reference, calling agent and working directory |
| `tool.finished` | Matching invocation ID, result/error status, result metadata or payload reference, and finish time. Cancellation and denial are explicit outcomes |
| `tool.transport` | Follow-up input/polling activity when a host represents it as transport for an already-running invocation |
| `process.started`, `process.finished` | Background process identity/incarnation, parent invocation and outcome, allowing release to wait for remaining writers |
| `file.changed` | Create, modify, delete, rename or metadata action; physical and displayed paths; previous path for a known rename; before/after identity or digest when available; source and attribution confidence |
| `work.note` | Optional progress, decision, check or handoff explanation. Notes never substitute for automatic tool/file capture |
| `booking.closing`, `booking.released` | Release request, final work references, closure checks, capture coverage and archive link |
| `capture.gap`, `capture.resumed`, `capture.late_event`, `booking.adopted` | Missing coverage, restart/reconciliation, delayed evidence or adoption of legacy work, with the interval and evidence limits explicitly stated |

Record every invocation by a registered participant, including reads,
failures, hosted tools, nested tool calls and subagents' calls. A model's
description of what it ran is not a capture source. Do not count repeated
polls as new executions of the original command. Record them separately
when needed to preserve the full host interaction history.

Record file creations, changes, deletions, renames and metadata changes
under the physical named area, including ignored files, generated files and
Git metadata. Register external work paths, such as the booking's shared
artifact territory, for capture too. Record that scope in the opening event;
an unrestricted process can write beyond it, so the recorder must not claim
machine-wide coverage. Do not follow a symlink outside scope implicitly.

The recorder's own `.ledger/` writes are the necessary exception: their
semantic events are already recorded. Feeding them back into file capture
would recurse indefinitely. This exception must be declared in coverage;
it is not a license to filter other ignored directories silently.

"Every file change" targets each file operation, including transient files
created and deleted within one tool call, rather than only the net Git diff
afterward. It does not mean each byte-sized kernel write is a separate work
item. A backend must state which operation boundaries and intermediate
versions it can observe; a final snapshot cannot prove complete coverage.

The event record is mandatory even when a payload is large, unavailable or
redacted. Payload references must state their storage location and digest,
and whether they survive transcript cleanup. An event's presence does not
claim that its complete tool output or every historical file body is stored.
File content retention and large-payload storage remain implementation
choices to settle before claiming replay or a self-contained content archive.

Concurrent tool calls can make attribution uncertain. Preserve an unknown
actor or an explicit set of candidates instead of assigning a filesystem
change to the nearest tool call by timestamp alone.

## Deterministic ownership and writing

One controller implementation owns booking transitions, participant
registration, event validation, ordering and file rotation. Agents and
hooks submit requests; they do not append JSONL or edit ownership files
themselves. A short-lived locked script can provide this writer; a daemon
is not required for the booking logic. Filesystem observation will require
a continuing capture process.

The controller uses a pool lock to prevent two bookings taking one physical
area, and serializes writes to each ledger. Where both locks are needed,
take the pool lock before the area's write lock. Hold neither while waiting
for a tool, a process, or a hook that needs to append its completion.

Opening a booking durably creates `current.jsonl` with the opening record,
then indexes that record in `history.jsonl` and updates any compatibility
ownership records. Return success only after the complete transition is
durable. A current file or a legacy hold always blocks a fresh allocation
until a mismatch has been reconciled.

Releasing first records a closing state that prevents new work from
starting. The controller then waits, without holding the pool lock, for
participants' outstanding calls/background writers and capture sources to
drain. It checks the existing repository-return conditions. Under the locks
it writes and syncs the terminal release record, renames `current.jsonl` to
its reserved archive path without overwriting another archive, syncs the
directory, appends the release index record and removes the derived
reservation. Only then is the area free. A failed check leaves it reserved.

JSONL appends and renames across multiple files are not one atomic
transaction. Persist event identities, sync writes and directory changes,
and recover unfinished transitions on controller startup before admitting
new work. Booking streams are the source for their contents; the history
index can be reconciled from them. Preserve independent area-level incident
records in that index.

After a crash, a durable release record can finish an interrupted rotation;
an opening record can finish a missing index update. Repeated requests
return the recorded result. A torn final line is preserved and reported for
repair; it is never silently discarded or treated as a successful action.
An uncertain reservation remains occupied.

Closed archives are immutable. A genuinely late event is preserved in a
`capture.late_event` history record with its booking ID, archive reference
and original evidence; it is never put into the next booking's current file.
That incident marks the affected capture interval incomplete.

## Hooks, capture and enforcement

Use three cooperating components:

1. **Booking controller:** enforces allocation, scope, participation,
   ordering, release and recovery deterministically.
2. **Host capture adapters:** record before dispatch and after completion,
   including failures, nested calls and subagents. They propagate explicit
   booking and distinct participant IDs instead of inferring them from CWD.
3. **File-operation capture:** records changes made by editors, commands and
   background processes, with watcher/snapshot reconciliation as a fallback.

A controlled dispatcher must durably record the start before running a
tool. If that write fails, do not dispatch. If completion recording fails,
the side effects have already happened: preserve the unfinished invocation,
report it, and stop admitting further work until recovery. Use synchronous
admission/recording, rather than a best-effort asynchronous hook.

Hooks are useful adapters, but do not establish full capture alone. Official
[Codex hook documentation](https://learn.chatgpt.com/docs/hooks#tool-coverage)
excludes hosted tools and some specialized paths. It also distinguishes
unified-exec polling from a new invocation and reports a parent Chat Session
ID for subagent hooks. These limitations require additional host/runtime
instrumentation and distinct subagent identities before the owner's full
capture requirement can be claimed. A transcript importer is useful evidence,
but retrospective import cannot prevent an unrecorded action.

Apple describes
[filesystem events](https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/FSEvents_ProgGuide/UsingtheFSEventsFramework/UsingtheFSEventsFramework.html)
as advisory, with coalescing/dropped-event cases requiring rescans. Such a
watcher can find changed paths but cannot prove every transient operation
or its author. Start observation before the baseline scan and keep gaps
visible. Strict capture needs a tested operation-level observer or mediated
filesystem execution; ordinary hooks plus a watcher remain incomplete.

At admission, declare each adapter's tool and file coverage. Missing events,
overflow, unavailable sources and intervals before capture started produce
explicit gap records. A new booking must not be presented as fully captured
unless every required source passes its qualification checks. Unrestricted
native clients or processes outside the controller's dispatch boundary
cannot be made compliant merely through an instruction file.

## Safe activation and migration

The existing [booking implementation](../../sagas/tools/environment.py)
reserves by one Arbol Chat Session, while Saga agents can write Beat holds
directly. The current [ownership procedure](sagas.md#what-happens-to-a-hold)
can release a gone agent's hold. These are implementation gaps against this
design; a ledger hook does not fix them by itself.

<!-- sources:
mycel:operations/sagas.md#A booked area for an Arbol chat
mycel:operations/sagas.md#What happens to a hold
-->

Implement and test the controller, ownership projection, all relevant
monitor/cleanup readers and capture adapters together. Existing hold files
can remain compatibility projections for readers, but must not become an
independent second authority for bookings. Participant death must no longer
trigger release of a booking that still belongs to continuing work.

Roll out first to a free named area, and activate capture for new bookings.
Keep running agents, paths, branches and legacy holds intact. Adopt an
existing booking only through an explicit, coordinated controller operation;
record its observed start, any independently known legacy start, and the
uncaptured interval. Never fabricate earlier tool/file events or pretend
that a Beat hold's timestamp proves when a longer booking first began.

Before activation, qualification must cover competing bookings, concurrent
participants, replacement Chat Sessions, retries, cancellation, background
writers, alias paths, two starts in the same minute, recorder outages,
partial lines, crashes at each rotation step and delayed events. Capture
tests must include hosted/nested calls and shell-created transient files,
not only ordinary edit-tool calls or final repository diffs.

Until those checks pass, this document is the design to implement, not a
claim that the machine already records every tool call and file change.
