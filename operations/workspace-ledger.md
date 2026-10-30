---
role: authored
---
# Workspace Booking and Workspace Ledger

This guide defines how a territory in a Workspace such as **Beaver Workspace**
is booked, recorded and released, and the files of the Workspace Ledger. It
extends [Working in Sagas](sagas.md#workspaces). The independent
`workspace-ledger` component's runtime contract is in the
[Workspace Ledger specifications](../../sylvan-stack/repos/workspace-ledger/specs/README.md).
This guide owns the portable booking procedure; those chapters define the recorder.

**Status: decided design, not yet implemented. No Workspace uses the Ledger now;
the live booking record is still the hold files described in
[Working in Sagas](sagas.md#holds).** The owner chose the `.ledger/` directory,
a booking independent of a Chat Session, and Saga-linked bookings with named
ad-hoc work allowed on 26 October 2026, then passive tool history and file-change
logging with unrestricted filesystem access and no command sandbox. Logging must
not control whether tools run. The owner accepted missing intermediate edits
between snapshots: the booking's resulting changes are primary, activity and
attribution supplementary. On 30 October 2026 the owner decided that a booking
reserves a territory, that several bookings can share a Workspace, that every
Workspace keeps `.ledger/bookings.json`, and that hold files are replaced in one
switch-over (WL-D16 to WL-D21). Hare Workspace used the Ledger for new bookings
from 28 October 2026 until its folder, with its `.ledger/`, was deleted on
29 October 2026.

## Workspace Booking

A **Workspace Booking** reserves a territory in one Workspace, from booking it
until explicitly releasing it. Each booking has a permanent `booking_id`. The
reservation belongs to the work, normally a Saga, rather than to the Chat Session
that happened to start it.

- A territory is a list of folders and files relative to the Workspace root,
  such as `arbol-trunk/trunks/trivial/` or `mycel/specs/README.md`. A folder ends
  in `/` and covers everything inside it. Two territories overlap when they share
  a path or one contains the other.
- Several bookings can be open in one Workspace at once, for the same or
  different Sagas, while their territories do not overlap. A booking whose
  territory overlaps an open one is refused.
- A booking names one work scope: a stable Saga reference, or an explicit
  ad-hoc work reference and title. The latter preserves work outside Sagas.
- Arc and Beat references describe work within that scope. A booking can
  continue through successive Beats of the same Saga; completing a Beat alone
  does not end it.
- Several authorized Chat Sessions and their subagents can participate in the
  same booking. They share its `booking_id` and event file. Joining, leaving,
  context compaction, interruption, retiring a Chat Session and transferring
  work to a replacement Chat Session do not end it. A Chat Session takes part
  in at most one open booking per Workspace.
- One participant coordinates admission, work allocation and release. A handoff
  changes that participant while preserving the booking. A lost participant
  requires recovery or handoff; it does not free the territory.
- Participants coordinate edits, and serialize operations that affect a whole
  checkout, such as changing branches or modifying the Git index, also with
  participants of other bookings in the same repository.

For example, **Fox Workspace** holds two open bookings: the Arbol 2 Specs
Implementation Saga with the territory `arbol-trunk/trunks/trivial/`, and named
ad-hoc work with the territory `mycel/operations/`. A Chat Session of the Saga
starts two subagents and hands coordination to a replacement Chat Session; all
four take part in the first booking, whose start time stays unchanged. A third
booking asking for `arbol-trunk/` is refused, because that folder contains the
first territory.

## Booking results and activity history

The primary record is the exact net file-content difference inside the booking's
territory between saved states at its beginning and end. The owner accepted that
an edit undone between snapshots may leave no record. The purpose is to preserve
the work's result, with activity history helping explain it.

| Record | Authority and limits |
|---|---|
| Opening and closing snapshots | Authoritative net contents, additions and deletions within the territory, including staged, unstaged and untracked files. Existing dirty work belongs to the opening state, not automatically to the new booking |
| Retained Git commits | Precise saved project versions and commit history associated with the booking; independent of approximate Chat Session, Arc or Beat attribution |
| Watcher, tool and work-context events | Supplementary timeline and attribution to Chat Sessions, Arcs and Beats. Events may be missing or attribution unknown; these limits do not invalidate a complete result comparison |

Use Git snapshots and comparisons for repository contents. Record the identity,
opening and closing commit IDs, index/working-tree state and durable snapshot
references of each repository the territory touches. Merely saving `HEAD`, a
branch name, a status listing or the final commit range is insufficient:
uncommitted and untracked contents must also be preserved. Git can inspect these
states; ordinary commit history does not automatically retain them. See
[Git status](https://git-scm.com/docs/git-status) and
[Git diff](https://git-scm.com/docs/git-diff).

Capture covers the territory, never the Workspace's `.ledger/`. Ignored and
generated files inside it remain in scope unless an explicit coverage definition
changes that rule. Files outside repository trees also need saved contents; Git
status alone is not a snapshot. Use a manifest and content storage alongside Git
where necessary. Preserve raw file bytes, file types and symlink targets; do not
silently lose content through Git filters, nested-repository handling or
unsupported file types. Report any unreadable or omitted path as incomplete
result coverage. Changes another booking makes in its own territory never enter
this booking's result. The result comparison concerns file contents and paths;
watcher events may separately report filesystem attributes and operational Git
metadata.

The Ledger captures the opening state before participants begin changing files,
then captures the closing state after participants finish writing. Participants
coordinate those boundaries without a command sandbox. Verify stable reads and
retry a capture that overlaps ongoing writes; a live walk of changing files must
not be presented as an atomic snapshot. If a complete boundary cannot be
established, report the result as incomplete rather than claiming exactness. A
hash manifest detects differences but does not preserve old contents by itself;
the referenced snapshot data must remain available.

Record snapshot IDs, scope, coverage, content digests and comparison references
in the ledger. Retain snapshot objects and referenced commits for as long as the
booking's event file depends on them. Storage may use a separate local Git object
store plus manifests; its exact layout remains an implementation choice. It must
not alter participants' staging, create commits on their working branches, stash
changes, reset files or rewrite their history.

For example, an agent edits and restores a file without committing. The net
booking comparison correctly shows no difference. A watcher event might explain
that activity, but its absence does not weaken the result record.

## Local configuration

The owner chose the repository name `workspace-ledger` and directed that Workspace
names belong in a Git-ignored configuration file on 26 October 2026. Stable IDs,
full display names, paths, aliases and booking order come from that local
inventory. They are not a compiled animal list or a fixed pool size.
[WL-0](../../sylvan-stack/repos/workspace-ledger/specs/00-scope-and-configuration.md)
defines its versioned TOML contract and configuration-reload behavior. A booking
pins its configuration revision and identity so a name change does not rename a
folder or rewrite historical records. The installed service's settings file was
lost on 29 October 2026 with the checkout that held it; it needs a location
outside every checkout and Workspace.

## Files on disk

```text
~/repos/sylvan-stack/fox/
  .ledger/
    bookings.json
    history.jsonl
    booking-2026-10-30-15-00-00Z-<booking_id>.jsonl
    booking-2026-10-30-16-20-00Z-<booking_id>.jsonl
  arbol-trunk/
  mycel/
  ...
```

| File | Contents and lifetime |
|---|---|
| `.ledger/bookings.json` | Every open booking in the Workspace: its ID, phase, Saga or ad-hoc scope, current Beat, territory, coordinator, participating Chat Sessions, start time and event file. An empty list means nothing is booked. It is the Workspace's only booking authority |
| `.ledger/booking-<start-time>-<booking_id>.jsonl` | One booking's event stream, written from its first event: opening record, snapshot/result references, participants, tool calls, observed file changes and work notes. It keeps its name when the booking closes and is immutable from then on |
| `.ledger/history.jsonl` | The Workspace's append-only index: `ledger.created`, booking starts and releases, coordination handoffs, changes outside every territory and capture/recovery incidents. Lifecycle entries identify the booking and its event file; detailed tool and file events stay in the event file |

One entry of `bookings.json`, expanded for reading:

```json
{
  "booking_id": "11111111-1111-4111-8111-111111111111",
  "phase": "active",
  "scope": {"kind": "saga", "ref": "arbol-2-specs-implementation", "title": "Arbol 2 Specs Implementation Saga"},
  "beat": "SYL-255",
  "territory": ["arbol-trunk/trunks/trivial/"],
  "coordinator": {"tool": "claude-code", "chat_session_id": "<chat-id>", "agent_id": null},
  "participants": [{"tool": "claude-code", "chat_session_id": "<chat-id>", "agent_id": null, "active": true}],
  "started_at": "2026-10-30T15:00:00.000Z",
  "booking_file": "booking-2026-10-30-15-00-00Z-11111111-1111-4111-8111-111111111111.jsonl"
}
```

The whole file and its remaining fields are defined in
[WL-1](../../sylvan-stack/repos/workspace-ledger/specs/01-bookings-and-ledger.md#interface).

**Every Workspace has a `.ledger/` folder, booked or not.** When the Ledger finds
no `.ledger/` in a configured Workspace, nothing is booked there: it creates the
folder with an empty `bookings.json` and `history.jsonl` and records
`ledger.created`. The owner accepted that deleting `.ledger/` during work frees the
Workspace's territories and loses its history; the return checks for clean
repositories still stop a new booking over unfinished work. A `.ledger/` folder
whose `bookings.json` is missing, malformed or unreadable is a fault, never a free
Workspace.

No other file records who holds a territory: no hold file, guard file, routing
file or lock in `~/.sagas/` or elsewhere, and no `.saga` or `.sagas` folder in a
Workspace or repository. Sagas themselves live only in `~/Artifacts/sagas/`.

Resolve aliases to one physical Workspace folder before locking or writing. An
event file is named when its booking opens, using the start time in UTC with
seconds, an explicit `Z` and the complete booking ID, which avoids minute
collisions and daylight-saving ambiguity. The first example above represents
16:00 in Europe/Madrid on 30 October 2026. Human views can show local time
without changing stored timestamps. A historical link resolves a booking ID to its
own event file and never to a later booking's file.

The JSONL files reference retained snapshot data instead of embedding file bodies
in every event. An event file and its snapshot references must remain resolvable
together; the names above do not prescribe the snapshot store's internal layout.

The whole `.ledger/` directory is local, Git-ignored operational data. Do not
commit it or place it inside one repository's checkout. The Workspace folders sit
outside their repositories' Git roots; a `.ledger/` entry in the machine's Git
ignore file also protects this name if the layout changes. Git ignoring is
separate from capture: ignored dependency files are still in capture scope.
Ignore rules do not supply a backup or retention policy.

## JSON Lines format

Every record in `history.jsonl` and the event files is one complete UTF-8 JSON
object followed by a newline, with the same envelope:

```json
{
  "schema": 1,
  "event_id": "22222222-2222-4222-8222-222222222222",
  "sequence": 1,
  "recorded_at": "2026-10-30T15:00:00.000Z",
  "occurred_at": "2026-10-30T15:00:00.000Z",
  "workspace": "fox",
  "workspace_name": "Fox Workspace",
  "booking_id": "11111111-1111-4111-8111-111111111111",
  "type": "booking.started",
  "actor": {"tool": "codex", "chat_session_id": "<chat-id>", "agent_id": "<agent-id>"},
  "source": {"kind": "controller", "id": "<producer-id>", "sequence": 1},
  "data": {
    "scope": {"kind": "saga", "ref": "<saga-reference>", "title": "<Saga name>"},
    "territory": ["arbol-trunk/trunks/trivial/"],
    "started_at": "2026-10-30T15:00:00.000Z",
    "coordinator": {"tool": "codex", "chat_session_id": "<chat-id>", "agent_id": "<agent-id>"},
    "participants": [{"tool": "codex", "chat_session_id": "<chat-id>", "agent_id": "<agent-id>"}],
    "capture": {"activity_status": "starting", "result_status": "baseline_pending"},
    "booking_file": "booking-2026-10-30-15-00-00Z-11111111-1111-4111-8111-111111111111.jsonl"
  }
}
```

This example is expanded for reading; its on-disk form is one line. Capture status
describes recorder health; it does not grant or deny permission to run tools.
Activity coverage and result coverage are independent. A `capture.resumed` event
records when observation becomes active; a `snapshot.captured` event identifies a
successfully saved boundary state.

| Field | Rule |
|---|---|
| `schema` | Format version; initial version is `1` |
| `event_id` | Stable unique identity supplied before recording. Retrying the same event does not append it again. Reusing the ID with conflicting content is an error |
| `sequence` | Writer-assigned increasing order across all of this Workspace's ledger files. A lifecycle record copied to `history.jsonl` keeps its identity and sequence; each file therefore has gaps |
| `recorded_at`, `occurred_at` | UTC timestamps. The writer assigns recording time; source occurrence time is `null` if unknown. Recording order does not claim causal order between concurrent producers |
| `workspace` | Stable configured ID, such as `fox`; independent of the display name. Aliases never create a second identity |
| `workspace_name` | Full configured name recorded with the event, such as **Fox Workspace**; later renaming does not rewrite old records |
| `booking_id` | Stable identity of the booking; `null` only for a Workspace-level incident outside any booking, such as `ledger.created` or a change outside every territory |
| `type` | Event kind from the table below |
| `actor` | Tool, Chat Session and distinct agent identities, or `null` when attribution is unknown. Subagents remain distinguishable even when a host reports their parent's Chat Session ID |
| `source` | Capture source kind, producer identity and source sequence/cursor, to help identify duplicate or missing deliveries where the source supports this |
| `data` | Event-specific structured fields; human descriptions supplement these fields |

The opening record contains the work scope, territory, coordinator, registered
participants and capture coverage. An ad-hoc scope uses `kind: "ad_hoc"`, a stable
work reference and a title. Later records reference the booking ID and carry the
current Arc/Beat references when applicable.

## Events and capture scope

| Kind | Required information |
|---|---|
| `booking.started` | Work scope, territory, start time, coordinator, initial participants, event file and capture scope |
| `participant.joined`, `participant.left` | Chat Session/agent identity and relationship to its delegating participant |
| `booking.handoff` | Previous and new coordinator, reason and continuation references |
| `work.context` | Current Saga/Arc/Beat references within the booking's work scope |
| `snapshot.captured` | Opening, closing or optional intermediate boundary; immutable snapshot ID, per-repository commit/state references, territory, manifest/content references, digests, capture interval and completeness |
| `booking.result` | Opening and closing snapshot IDs, exact net comparison references, retained commit references, result coverage and unresolved capture errors; no claim of exact Chat Session/Arc/Beat attribution |
| `tool.started` | Host invocation ID, tool name, arguments or an explicit payload reference, calling agent and working directory |
| `tool.finished` | Matching invocation ID, result/error status, result metadata or payload reference, and finish time. Cancellation and denial are explicit outcomes |
| `tool.transport` | Follow-up input/polling activity when a host represents it as transport for an already-running invocation |
| `process.started`, `process.finished` | Background process identity/incarnation, parent invocation and outcome when exposed by the runtime; evidence for coordinating release, not a complete process audit |
| `file.changed` | Observed create, modify, delete, rename, metadata or unknown change inside the booking's territory; physical and displayed paths; previous path for a known rename; before/after identity or digest when available; source, observation method and attribution confidence |
| `work.note` | Optional progress, decision, check or handoff explanation. Notes never substitute for automatic tool/file capture |
| `booking.closing`, `booking.released` | Release request, final work references, closure checks, separate result/activity coverage, booking result reference and event file |
| `ledger.created` | The Ledger created a missing `.ledger/`; recorded in history with `booking_id: null` |
| `file.outside_territory` | A change observed inside the Workspace but inside no open territory; recorded in history with `booking_id: null` and the same details as `file.changed` |
| `capture.gap`, `capture.resumed`, `capture.late_event` | Missing coverage, restart/reconciliation or delayed evidence, with the interval and evidence limits explicitly stated. `booking.adopted` was withdrawn with adoption of hold-file work |

Aim to record every invocation by a registered participant, including reads,
failures, hosted tools, nested tool calls and subagents' calls. Capture comes from
runtime events, supported hooks or transcript import, rather than an agent
remembering to describe what it ran. Each adapter declares the tool types and
execution paths it can observe, with known omissions. Missing coverage is
explicit; unsupported calls still execute. Do not count repeated polls as new
executions of the original command. Record them separately when needed to
preserve the full host interaction history.

The watcher observes the whole Workspace folder, including ignored files,
generated files and Git metadata. A file change belongs to the open booking whose
territory contains its path; that says in which booking's reservation it fell,
not who made it. A change inside no open territory is a Workspace-level
`file.outside_territory` incident in history, never guessed into a booking. An
agent's tool calls remain associated with its booking even when its working
directory is elsewhere, but file changes outside the Workspace are outside this
recorder's scope. Agents retain unrestricted filesystem access. Record the
watched root in the opening event; do not follow a symlink outside scope
implicitly.

The recorder's own `.ledger/` writes are the necessary exception: their semantic
events are already recorded. Feeding them back into file capture would recurse
indefinitely. This exception must be declared in coverage; it is not a license
to filter other ignored directories silently.

File history records observed changes throughout a booking, including changes
made by shell commands, editors and background processes. A watcher can coalesce
rapid writes or miss a transient file; it cannot promise one record for every
filesystem operation or every intermediate version. Intermediate scans reconcile
the latest observable state, including untracked and ignored paths. Opening and
closing snapshots separately establish the booking's result, even when
intermediate events are missing. Neither kind of snapshot reconstructs an unseen
file created and deleted between captures; that is an accepted limitation.
Preserve uncertainty instead of inventing an exact sequence of operations.

Capture an event's metadata even when its payload is large, unavailable or
redacted. Payload references must state their storage location and digest, and
whether they survive transcript cleanup. An event's presence does not claim that
its complete tool output or every historical file body is stored. Boundary
snapshot contents must be retained to support the result comparison. Retention of
every intermediate file body and full tool output is a separate implementation
choice; no complete replay of activity is promised.

Concurrent tool calls can make attribution uncertain. Preserve an unknown actor
or an explicit set of candidates instead of assigning a filesystem change to the
nearest tool call by timestamp alone.

## Deterministic ownership and writing

One writer implementation per Workspace owns booking transitions, participant
registration, event validation and ordering. Agents, runtime adapters and
watchers submit events through it instead of independently appending JSONL or
editing `bookings.json`. A locked command can provide the booking verbs; a
background service is needed for continuing observation. These share one writer
library. This is coordination by convention and implementation, not an
access-control boundary: unrestricted agents can still edit or delete local
ledger files.

The Workspace's writer lock serializes changes to `bookings.json` and appends to
its files. Take it before checking a requested territory for overlap and keep it
until the new booking is listed. Booking in the first available Workspace takes
one Workspace's lock at a time; no lock spans the pool. Hold it neither while
waiting for a tool, a process, a participant acknowledgement or a source read,
nor while a long snapshot scan runs.

Opening a booking durably creates its event file with the opening record, indexes
that record in `history.jsonl` and lists the booking in `bookings.json`. Capture
and retain the verified opening snapshot of its territory and append its
`snapshot.captured` record before reporting the booking ready for work. A failed
baseline capture leaves the booking listed for recovery; it does not disable
agents' tools. Return success only after the booking transition and baseline are
durable.

Release is an explicit coordination operation on one booking. The coordinator
first asks participants to finish or hand off their work, then requests release.
A closing record expresses that intent; it does not disable tools or stop
processes. The Ledger checks participant acknowledgements, known outstanding work
and the existing return conditions for the repositories the territory touches,
without holding the lock while waiting. It also flushes pending observations and
records their last source cursors and any known gaps. Tool completion alone does
not prove that no background writer remains. Capture a verified closing snapshot
and persist `booking.result` before declaring release complete. If that fails,
keep the booking listed for recovery and identify the missing result data; do not
stop or cancel tools.

When these checks permit release, the Ledger writes and syncs the terminal release
record, appends the release index record and then removes the booking from
`bookings.json`. Only then is the territory free. Other bookings in the Workspace
are untouched. A failed ownership or return check leaves the booking listed without
interrupting tools. An activity-recorder outage is reported as incomplete activity
history; it does not by itself make the result incomplete or prevent release when
both boundary snapshots and the result record are complete and durable.

JSONL appends across multiple files and the rewrite of `bookings.json` are not one
atomic transaction. Persist event identities, sync writes and directory changes,
rewrite `bookings.json` whole and atomically after the event it reflects is
durable, and recover unfinished transitions before allocating a new booking. Event
files are the source for their contents; `bookings.json` and the history index can
be reconciled from them. Preserve independent Workspace-level incident records in
that index.

After a crash, a durable release record can finish an interrupted release; an
opening record can finish a missing index or listing update. Repeated requests
return the recorded result. A torn final line is preserved and reported for
repair; it is never silently discarded or treated as a successful action. An
uncertain booking remains listed.

Closed event files are immutable. A genuinely late event is preserved in a
`capture.late_event` history record with its booking ID, event file and original
evidence; it is never put into another booking's file. That incident marks the
affected activity interval incomplete. Result coverage changes only if evidence
invalidates a boundary snapshot or its comparison, not merely because an activity
event arrived late.

## Passive recording architecture

Use three cooperating components:

1. **Booking writer:** handles booking, participants, boundary snapshots, Git
   comparison, retained commit references, release, recovery and JSONL ordering.
   It controls reservations and saves results; it does not intercept tool
   execution.
2. **Runtime event adapters:** subscribe to each supported agent runtime's
   tool-start and tool-finish events and send them to the writer. Supported hooks
   can supply additional events; transcript import can backfill events after
   interruption. Preserve booking and distinct participant IDs instead of relying
   on the current working directory.
3. **Filesystem watcher with reconciliation:** watches the Workspace folder,
   starts before the baseline scan, and compares stored state with later scans
   after changes, restart or an overflow. It observes changes from any process,
   including tools that have no file-edit hook.

These are logical components, not three required daemons. A single local
background service can host the writer and watcher, with small adapters in the
agent drivers. Commands continue to run directly with the agent's normal
filesystem access; no command wrapper or sandbox is required by this design. The
watcher does not need to monitor the entire machine.

The adapters submit asynchronously. A recorder failure must not deny, delay for
recovery or cancel a tool call. Use a local queue and source cursors where
available, retry deliveries with stable event IDs, and backfill from retained
runtime history where possible. Bound the queue and report overflow rather than
exhausting resources. When capture resumes, record the affected interval and what
could or could not be recovered. Recorder health is separate from execution
permissions; an unavailable activity recorder means a partial timeline. Boundary
snapshot failures are reported separately as incomplete result coverage.

Prefer native runtime events over relying on hooks alone. For example,
[Codex App Server](https://learn.chatgpt.com/docs/app-server) exposes item
lifecycle notifications, including command execution, file changes and web
search. The [hook coverage documentation](https://learn.chatgpt.com/docs/hooks#tool-coverage)
excludes hosted tools and some specialized paths. An adapter must be attached to
the runtime actually executing a participant's calls; instrumenting one driver
does not cover unrelated native chats. A transcript importer records source
occurrence time when known and actual import time separately. It must deduplicate
events already received live.

On this Mac, use an FSEvents-backed watcher with a stored file inventory for
reconciliation. Apple documents
[coalescing and dropped-event cases](https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/FSEvents_ProgGuide/UsingtheFSEventsFramework/UsingtheFSEventsFramework.html)
that require rescans. Record the source cursor, detected gaps and whether an
event came from live observation or a later scan. Leave a change's actor unknown
when the observer cannot identify it. Do not claim that a watcher provides every
intermediate write, exact authorship or complete history.

At booking boundaries, retain source cursors and the mapping from participants to
booking IDs. A delayed event belongs to its original booking, not whichever
booking is open when it arrives. If that identity cannot be established, record a
Workspace-level incident with the ambiguity rather than guessing.

## Switch-over from hold files

Until the switch-over, the [booking tool](../../sagas/tools/environment.py) and its
entry points, direct Beat claims and gone-owner cleanup in `beat_claim.py`, the
progress report and the check from outside all read and write hold files in
`~/.sagas/holds/` under `~/.sagas/booking.lock`. The routing file
`~/.sagas/workspace-ledger-authority.json` marks every Workspace `legacy`, so none
of them uses the Ledger.

<!-- sources:
mycel:operations/sagas.md#A booked Workspace for an Arbol chat
mycel:operations/sagas.md#What happens to a hold
sagas:@code/tools/environment.py#route
sagas:@code/tools/environment.py#controller
sagas:@code/tools/beat_claim.py#clean
sagas:@code/tools/agent-watch/agent_watch.py#read_bookings
-->

The switch-over moves every Workspace at once:

1. Wait until no hold file exists and every repository in every Workspace is
   clean on `main`. An open hold postpones the switch-over; it never takes over
   or frees running work.
2. Create each Workspace's `.ledger/` with an empty `bookings.json` and
   `history.jsonl`.
3. In the same change, switch the booking, Beat-claim, cleanup, progress and
   agent-check tools, and the instructions that describe them, to book and read
   only through the Ledger.
4. Back up, then remove, `~/.sagas/holds/`, `~/.sagas/booking.lock` and the
   routing file.

There is no per-Workspace staging, adoption of running work, compatibility hold
file or rollback to hold files. Undoing the switch-over means restoring the
backed-up tools and instructions while no booking is open. Participant death must
never release a booking that still belongs to continuing work, before or after
the switch-over.

Before the switch-over, the acceptance cases in
[WL-4](../../sylvan-stack/repos/workspace-ledger/specs/04-interface-recovery-and-rollout.md#named-contract-cases)
must pass on disposable Workspaces, among them overlapping and separate
territories across Sagas, a missing `.ledger/`, a malformed `bookings.json`,
two bookings changing one repository, changes outside every territory and a crash
at each step of opening and closing. The earlier cases still cover competing
bookings, concurrent participants, replacement Chat Sessions, retries, background
writers, alias paths, recorder outages, partial lines, delayed events, capture of
hosted/nested calls and ignored files, and complete results for dirty, staged,
untracked, ignored, binary and symlinked files. Verify that logging failure
leaves tool execution unaffected, outside paths are not watched, and `.ledger/`
writes do not feed back into capture.
