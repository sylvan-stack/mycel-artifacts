---
role: authored
---
# Workspace Booking and Workspace Ledger

This document defines the proposed lifecycle and file format for the
Workspace Ledger for a named area such as **Beaver Workspace**. It extends
[Working in Sagas](sagas.md#named-work-areas). The independent `workspace-ledger`
component's draft runtime contract is in the
[Workspace Ledger specifications](../../sylvan-stack/repos/workspace-ledger/specs/README.md).
This guide owns the portable booking procedure; those chapters define the recorder.

**Status: design, not an activated runtime procedure.** The owner chose the
directory layout, a booking independent of a Chat Session, and Saga-linked
bookings by default with named ad-hoc work allowed on 26 October 2026. The
owner then chose passive tool history and file-change logging inside the
booked area, with unrestricted filesystem access and no command sandbox.
Logging must not control whether tools run. The owner subsequently accepted
missing intermediate edits between snapshots: the booking's resulting changes
are primary, while activity and attribution are supplementary. The schema,
booking controller and capture mechanisms below are proposed implementation
choices. Existing live booking and hold procedures remain in force until a
tested migration activates this design. No hook, recorder or snapshot store
has been installed by writing this document.

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

## Booking results and activity history

The primary record is the exact net file-content difference between saved
states at the beginning and end of a Workspace Booking. The owner accepted
that an edit undone between snapshots may leave no record. The purpose is
to preserve the work's result, with activity history helping explain it.

| Record | Authority and limits |
|---|---|
| Opening and closing snapshots | Authoritative net contents, additions and deletions within the declared scope, including staged, unstaged and untracked files. Existing dirty work belongs to the opening state, not automatically to the new booking |
| Retained Git commits | Precise saved project versions and commit history associated with the booking; independent of approximate Chat Session, Arc or Beat attribution |
| Watcher, tool and work-context events | Supplementary timeline and attribution to Chat Sessions, Arcs and Beats. Events may be missing or attribution unknown; these limits do not invalidate a complete result comparison |

Use Git snapshots and comparisons for repository contents. Record each
repository's identity, opening and closing commit IDs, index/working-tree
state and durable snapshot references. Merely saving `HEAD`, a branch name,
a status listing or the final commit range is insufficient: uncommitted and
untracked contents must also be preserved. Git can inspect these states;
ordinary commit history does not automatically retain them. See
[Git status](https://git-scm.com/docs/git-status) and
[Git diff](https://git-scm.com/docs/git-diff).

Capture covers the declared physical area, excluding `.ledger/`. Ignored
and generated files remain in scope unless an explicit coverage definition
changes that rule. Files outside repository trees also need saved contents;
Git status alone is not a snapshot of the whole area. Use a manifest and
content storage alongside Git where necessary. Preserve raw file bytes,
file types and symlink targets; do not silently lose content through Git
filters, nested-repository handling or unsupported file types. Report any
unreadable or omitted path as incomplete result coverage. The result
comparison concerns file contents and paths; watcher events may separately
report filesystem attributes and operational Git metadata.

The controller captures the opening state before participants begin changing
files, then captures the closing state after participants finish writing.
Participants coordinate those boundaries without a command sandbox. Verify
stable reads and retry a capture that overlaps ongoing writes; a live walk
of changing files must not be presented as an atomic snapshot. If a complete
boundary cannot be established, report the result as incomplete rather than
claiming exactness. A hash manifest detects differences but does not preserve
old contents by itself; the referenced snapshot data must remain available.

Record snapshot IDs, scope, coverage, content digests and comparison references
in the ledger. Retain snapshot objects and referenced commits for as long as
the booking archive depends on them. Storage may use a separate local Git
object store plus manifests; its exact layout remains an implementation
choice. It must not alter participants' staging, create commits on their
working branches, stash changes, reset files or rewrite their history.

For example, an agent edits and restores a file without committing. The net
booking comparison correctly shows no difference. A watcher event might
explain that activity, but its absence does not weaken the result record.

## Local configuration

The owner chose the repository name `workspace-ledger` and directed that working
area names belong in a Git-ignored configuration file on 26 October 2026. Stable
IDs, full display names, paths, aliases and booking order come from that local
inventory. They are not a compiled animal/color list or a fixed pool size.
The source repository contains a placeholder template and a Git-ignored
`workspace-ledger.local.toml`; [WL-0](../../sylvan-stack/repos/workspace-ledger/specs/00-scope-and-configuration.md)
defines its proposed versioned TOML contract and configuration-reload behavior.
A booking pins its configuration revision and identity so a name change does not
rename a physical folder or rewrite historical records. Existing legacy booking
scripts keep their live behavior until coordinated migration; creating the new
configuration does not switch them over.

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
| `.ledger/current.jsonl` | Only the open booking, starting with its opening record and containing snapshot/result references, participants, tool calls, observed file changes and work notes. Absent when the area is free; never reused by truncating an old booking |
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

The JSONL files reference retained snapshot data instead of embedding file
bodies in every event. An archive and its snapshot references must remain
resolvable together; the three JSONL names above do not prescribe the
snapshot store's internal layout.

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
  "workspace_name": "Beaver Workspace",
  "booking_id": "11111111-1111-4111-8111-111111111111",
  "type": "booking.started",
  "actor": {"tool": "codex", "chat_session_id": "<chat-id>", "agent_id": "<agent-id>"},
  "source": {"kind": "controller", "id": "<producer-id>", "sequence": 1},
  "data": {
    "scope": {"kind": "saga", "ref": "<saga-reference>", "title": "<Saga name>"},
    "started_at": "2026-10-26T12:56:00.000Z",
    "coordinator": {"tool": "codex", "chat_session_id": "<chat-id>", "agent_id": "<agent-id>"},
    "participants": [{"tool": "codex", "chat_session_id": "<chat-id>", "agent_id": "<agent-id>"}],
    "capture": {"roots": ["."], "excluded_roots": [".ledger/"], "activity_status": "starting", "result_status": "baseline_pending"},
    "booking_file": "booking-2026-10-26-12-56-00Z-11111111-1111-4111-8111-111111111111.jsonl"
  }
}
```

This example is expanded for reading; its on-disk form is one line. Capture
status describes recorder health; it does not grant or deny permission to
run tools. Activity coverage and result coverage are independent. A
`capture.resumed` event records when observation becomes active; a
`snapshot.captured` event identifies a successfully saved boundary state.

| Field | Rule |
|---|---|
| `schema` | Format version; proposed initial version is `1` |
| `event_id` | Stable unique identity supplied before recording. Retrying the same event does not append it again. Reusing the ID with conflicting content is an error |
| `sequence` | Controller-assigned increasing order across this named area's ledger. A lifecycle record copied to `history.jsonl` keeps its identity and sequence; that index therefore has gaps |
| `recorded_at`, `occurred_at` | UTC timestamps. The controller assigns recording time; source occurrence time is `null` if unknown. Recording order does not claim causal order between concurrent producers |
| `workspace` | Stable configured ID, such as `beaver`; independent of the display name. Aliases never create a second identity |
| `workspace_name` | Full configured name recorded with the event, such as **Beaver Workspace**; later renaming does not rewrite old records |
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
| `snapshot.captured` | Opening, closing or optional intermediate boundary; immutable snapshot ID, per-repository commit/state references, scope, manifest/content references, digests, capture interval and completeness |
| `booking.result` | Opening and closing snapshot IDs, exact net comparison references, retained commit references, result coverage and unresolved capture errors; no claim of exact Chat Session/Arc/Beat attribution |
| `tool.started` | Host invocation ID, tool name, arguments or an explicit payload reference, calling agent and working directory |
| `tool.finished` | Matching invocation ID, result/error status, result metadata or payload reference, and finish time. Cancellation and denial are explicit outcomes |
| `tool.transport` | Follow-up input/polling activity when a host represents it as transport for an already-running invocation |
| `process.started`, `process.finished` | Background process identity/incarnation, parent invocation and outcome when exposed by the runtime; evidence for coordinating release, not a complete process audit |
| `file.changed` | Observed create, modify, delete, rename, metadata or unknown change; physical and displayed paths; previous path for a known rename; before/after identity or digest when available; source, observation method and attribution confidence |
| `work.note` | Optional progress, decision, check or handoff explanation. Notes never substitute for automatic tool/file capture |
| `booking.closing`, `booking.released` | Release request, final work references, closure checks, separate result/activity coverage, booking result reference and archive link |
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
Intermediate scans reconcile the latest observable state, including untracked
and ignored paths. Opening and closing snapshots separately establish the
booking's result, even when intermediate events are missing. Neither kind
of snapshot reconstructs an unseen file created and deleted between captures;
that is an accepted limitation. Preserve uncertainty instead of inventing
an exact sequence of operations.

Capture an event's metadata even when its payload is large, unavailable or
redacted. Payload references must state their storage location and digest,
and whether they survive transcript cleanup. An event's presence does not
claim that its complete tool output or every historical file body is stored.
Boundary snapshot contents must be retained to support the result comparison.
Retention of every intermediate file body and full tool output is a separate
implementation choice; no complete replay of activity is promised.

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
ownership records. Capture and retain the verified opening snapshot and
append its `snapshot.captured` record before reporting a booking ready for
work. A failed baseline capture leaves the reservation visible for recovery;
it does not disable agents' tools. Return success only after the booking
transition and baseline are durable. A current file or a legacy hold always
blocks a fresh allocation until a mismatch has been reconciled.

Release is an explicit coordination operation. The coordinator first asks
participants to finish or hand off their work, then requests release. A
closing record expresses that intent; it does not disable tools or stop
processes. The controller checks participant acknowledgements, known
outstanding work and the existing repository-return conditions without
holding the pool lock while waiting. It also flushes pending observations
and records their last source cursors and any known gaps. Tool completion
alone does not prove that no background writer remains. Capture a verified
closing snapshot and persist `booking.result` before declaring release
complete. If that fails, keep the reservation for recovery and identify the
missing result data; do not stop or cancel tools.

When these checks permit release, the controller writes and syncs the
terminal release record under the locks, renames `current.jsonl` to its
reserved archive path without overwriting another archive, syncs the
directory, appends the release index record and removes the derived
reservation. Only then is the area free. A failed ownership or return check
leaves it reserved without interrupting tools. An activity-recorder outage
is reported as incomplete activity history; it does not by itself make the
result incomplete or prevent release when both boundary snapshots and the
result record are complete and durable.

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
That incident marks the affected activity interval incomplete. Result
coverage changes only if evidence invalidates a boundary snapshot or its
comparison, not merely because an activity event arrived late.

## Passive recording architecture

Use three cooperating components:

1. **Booking controller and ledger writer:** handles booking, participants,
   boundary snapshots, Git comparison, retained commit references, release,
   recovery, JSONL ordering and rotation. It controls reservations and saves
   results; it does not intercept tool execution.
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
execution permissions; an unavailable activity recorder means a partial
timeline. Boundary snapshot failures are reported separately as incomplete
result coverage.

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
deletes, watcher coalescing, overflow and restart reconciliation. Result
checks cover initial dirty work, staged and unstaged edits, untracked and
ignored files, binaries, symlinks, files outside repository roots, nested
repositories, incomplete reads, concurrent writes during capture and durable
snapshot retention. Verify that an edit restored between snapshots produces
no net difference, and that unavailable activity events do not weaken a
complete boundary comparison. Verify that logging failure leaves tool
execution unaffected, outside paths are not watched, and `.ledger/` writes
do not feed back into capture.

Until those checks pass, this document is the design to implement, not a
claim that passive recording is already active.
