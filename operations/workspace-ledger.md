---
role: authored
---
# Workspace Booking and Workspace Ledger

This document defines the proposed lifecycle and file format for the
Workspace Ledger for a named area such as **Beaver Workspace**. It extends
[Working in Sagas](sagas.md#named-work-areas).

**Status: design, not an activated runtime procedure.** The owner chose the
directory layout, a booking independent of a Chat Session, and Saga-linked
bookings by default with named ad-hoc work allowed on 26 October 2026. The
owner then chose passive tool history and file-change logging inside the
booked area, with unrestricted filesystem access and no command sandbox.
Logging must not control whether tools run. The schema, booking controller
and capture mechanisms below are proposed implementation choices. Existing
live booking and hold procedures remain in force until a tested migration
activates this design. No hook or recorder has been installed by writing this document.

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
| `.ledger/booking-<start-time>-<booking_id>.jsonl` | A closed booking, produced by renaming `current.jsonl` on release. It retains the recorded event stream and is immutable after closure |
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
    "capture": {"roots": ["."], "excluded_roots": [".ledger/"], "status": "starting"},
    "booking_file": "booking-2026-10-26-12-56-00Z-11111111-1111-4111-8111-111111111111.jsonl"
  }
}
```

This example is expanded for reading; its on-disk form is one line. Capture
status describes recorder health; it does not grant or deny permission to
run tools. A `capture.resumed` event records when observation becomes active.

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
| `source` | Capture source kind, producer identity and source sequence/cursor, to help identify duplicate or missing deliveries where the source supports this |
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
| `process.started`, `process.finished` | Background process identity/incarnation, parent invocation and outcome when exposed by the runtime; evidence for coordinating release, not a complete process audit |
| `file.changed` | Observed create, modify, delete, rename, metadata or unknown change; physical and displayed paths; previous path for a known rename; before/after identity or digest when available; source, observation method and attribution confidence |
| `work.note` | Optional progress, decision, check or handoff explanation. Notes never substitute for automatic tool/file capture |
| `booking.closing`, `booking.released` | Release request, final work references, closure checks, capture coverage and archive link |
| `capture.gap`, `capture.resumed`, `capture.late_event`, `booking.adopted` | Missing coverage, restart/reconciliation, delayed evidence or adoption of legacy work, with the interval and evidence limits explicitly stated |

Aim to record every invocation by a registered participant, including
reads, failures, hosted tools, nested tool calls and subagents' calls. Capture
comes from runtime events, supported hooks or transcript import, rather than
an agent remembering to describe what it ran. Each adapter declares the
tool types and execution paths it can observe, with known omissions. Missing coverage is explicit;
unsupported calls still execute. Do not count repeated polls as new
executions of the original command. Record them separately when needed to
preserve the full host interaction history.

File capture covers changes observed under the physical named area,
including ignored files, generated files and Git metadata. An agent's tool
calls remain associated with its booking even when its working directory
is elsewhere, but file changes outside that area are outside this recorder's
scope. Agents retain unrestricted filesystem access. Record the watched
root in the opening event; do not follow a symlink outside scope implicitly.

The recorder's own `.ledger/` writes are the necessary exception: their
semantic events are already recorded. Feeding them back into file capture
would recurse indefinitely. This exception must be declared in coverage;
it is not a license to filter other ignored directories silently.

File history records observed changes throughout a booking, including
changes made by shell commands, editors and background processes. A watcher
can coalesce rapid writes or miss a transient file; it cannot promise one
record for every filesystem operation or every intermediate version.
Snapshots reconcile the latest observable state, including untracked and
ignored paths, rather than just the final Git diff. They cannot reconstruct
an unseen file that was created and deleted between observations. Preserve
uncertainty instead of inventing an exact sequence of operations.

Capture an event's metadata even when its payload is large, unavailable or
redacted. Payload references must state their storage location and digest,
and whether they survive transcript cleanup. An event's presence does not
claim that its complete tool output or every historical file body is stored.
File content retention and large-payload storage remain implementation
choices to settle before claiming replay or a self-contained content archive.

Concurrent tool calls can make attribution uncertain. Preserve an unknown
actor or an explicit set of candidates instead of assigning a filesystem
change to the nearest tool call by timestamp alone.

## Deterministic ownership and writing

One writer implementation owns booking transitions, participant
registration, event validation, ordering and file rotation. Agents, runtime
adapters and watchers submit events through it instead of independently
appending JSONL or editing ownership files. A locked script can provide the
booking commands; a background service is needed for continuing observation.
These can share one writer library and later run in one service. This is
coordination by convention and implementation, not an access-control boundary:
unrestricted agents can still edit or delete local ledger files.

The controller uses a pool lock to prevent two bookings taking one physical
area, and serializes writes to each ledger. Where both locks are needed,
take the pool lock before the area's write lock. Hold neither while waiting
for a tool, a process, or a hook that needs to append its completion.

Opening a booking durably creates `current.jsonl` with the opening record,
then indexes that record in `history.jsonl` and updates any compatibility
ownership records. Return success only after the complete transition is
durable. A current file or a legacy hold always blocks a fresh allocation
until a mismatch has been reconciled.

Release is an explicit coordination operation. The coordinator first asks
participants to finish or hand off their work, then requests release. A
closing record expresses that intent; it does not disable tools or stop
processes. The controller checks participant acknowledgements, known
outstanding work and the existing repository-return conditions without
holding the pool lock while waiting. It also flushes pending observations
and records their last source cursors and any known gaps. Tool completion
alone does not prove that no background writer remains.

When these checks permit release, the controller writes and syncs the
terminal release record under the locks, renames `current.jsonl` to its
reserved archive path without overwriting another archive, syncs the
directory, appends the release index record and removes the derived
reservation. Only then is the area free. A failed ownership or return check
leaves it reserved without interrupting tools. A capture outage is reported
as incomplete history rather than evidence that work must stop; durable
booking records are still required to complete release safely.

JSONL appends and renames across multiple files are not one atomic
transaction. Persist event identities, sync writes and directory changes,
and recover unfinished transitions on controller startup before allocating
a new booking. Booking streams are the source for their contents; the history
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

## Passive recording architecture

Use three cooperating components:

1. **Booking controller and ledger writer:** handles booking, participants,
   release, recovery, JSONL ordering and rotation. It controls reservations;
   it does not intercept tool execution.
2. **Runtime event adapters:** subscribe to each supported agent runtime's
   tool-start and tool-finish events and send them to the writer. Supported
   hooks can supply additional events; transcript import can backfill events
   after interruption. Preserve booking and distinct participant IDs instead
   of relying on the current working directory.
3. **Filesystem watcher with reconciliation:** watches the physical named
   area, starts before the baseline scan, and compares stored state with
   later scans after changes, restart or an overflow. It observes changes
   from any process, including tools that have no file-edit hook.

These are logical components, not three required daemons. A single local
background service can host the writer and watcher, with small adapters in
the agent drivers. Commands continue to run directly with the agent's normal
filesystem access; no command wrapper or sandbox is required by this design.
The watcher does not need to monitor the entire machine.

The adapters submit asynchronously. A recorder failure must not deny, delay
for recovery or cancel a tool call. Use a local queue and source cursors where
available, retry deliveries with stable event IDs, and backfill from retained
runtime history where possible. Bound the queue and report overflow rather
than exhausting resources. When capture resumes, record the affected interval
and what could or could not be recovered. Recorder health is separate from
execution permissions; an unavailable recorder means partial history.

Prefer native runtime events over relying on hooks alone. For example,
[Codex App Server](https://learn.chatgpt.com/docs/app-server) exposes item
lifecycle notifications, including command execution, file changes and web
search. The [hook coverage documentation](https://learn.chatgpt.com/docs/hooks#tool-coverage)
excludes hosted tools and some specialized paths. An adapter must be attached
to the runtime actually executing a participant's calls; instrumenting one
driver does not cover unrelated native chats. A transcript importer records
source occurrence time when known and actual import time separately. It
must deduplicate events already received live.

On this Mac, use an FSEvents-backed watcher with a stored file inventory for
reconciliation. Apple documents
[coalescing and dropped-event cases](https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/FSEvents_ProgGuide/UsingtheFSEventsFramework/UsingtheFSEventsFramework.html)
that require rescans. Record the source cursor, detected gaps and whether
an event came from live observation or a later scan. Leave a change's actor
unknown when the observer cannot identify it. Do not claim that a watcher
provides every intermediate write, exact authorship or complete history.

At booking boundaries, retain source cursors and the mapping from participants
to booking IDs. A delayed event belongs to its original booking, not whichever
booking is open when it arrives. If that identity cannot be established,
record an area-level incident with the ambiguity rather than guessing.

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

Before activation, tests must cover competing bookings, concurrent
participants, replacement Chat Sessions, retries, cancellation, background
writers, alias paths, two starts in the same minute, recorder outages,
partial lines, crashes at each rotation step and delayed events. Capture
checks include hosted/nested calls, ignored files, shell changes, renames,
deletes, watcher coalescing, overflow and restart reconciliation. Verify that
logging failure leaves tool execution unaffected, that scans recover lasting
changes, and that transient changes and missing sources are described within
the observer's limits. Verify that outside paths are not watched and that
`.ledger/` writes do not feed back into capture.

Until those checks pass, this document is the design to implement, not a
claim that passive recording is already active.
