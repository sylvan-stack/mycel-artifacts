---
role: authored
---
# Runbook: arbol-agent

## Why it exists

`arbol-agent` is the standalone work-Mac encrypted-mailbox CLI. It can list,
inspect, explicitly read, compose, and reply without a running Arbol host or its
RPCs. A separate BLE Dashboard endpoint and trusted iPad relay are needed to
transmit queued records. No command launches an agent. Process and authorization
rules live in the [iPad Dashboard guide](../operations/ipad-dashboard.md).

## Locate and use

Verified local executable on this work Mac:

```sh
AGENT="$HOME/repo/arbol-dashboard/ArbolDashboardMac/build/arbol-agent"
"$AGENT" --help
"$AGENT" location
"$AGENT" list --unread
"$AGENT" status '<actual-incoming-UUID>'
"$AGENT" read '<actual-incoming-UUID>'
printf '%s' 'Authorized response body' | "$AGENT" reply '<actual-incoming-UUID>' 'Reply title'
"$AGENT" status '<returned-outgoing-UUID>'
```

The path above is a verified machine-local installation locator, not a portable
home-Mac path or a requirement to build/call repository scripts. Check the binary
exists and its help matches this interface. On another machine, obtain the
configured work-mailbox client location from the local user; never silently pick
a home-role CLI with the same name. If absent, report that setup is needed rather
than inventing a replacement. No Arbol host code or instructions are required.

Full public command surface:

| Command | Effect |
|---|---|
| no arguments, `help`, `--help` | Print usage, no mailbox access |
| `location` | Print shared encrypted-store path, no key access |
| `list` | Return all records including bodies; no read-stage change |
| `list --unread` | Return home -> work stage-2 records; no read-stage change |
| `status UUID` | Return one record including its body; no read-stage change |
| `read UUID` | Explicitly commit incoming record at stage 3; idempotent |
| `reply UUID TITLE` | Read UTF-8 body from stdin, commit new work -> home reply |
| `send TITLE` | Read UTF-8 body from stdin, commit new uncorrelated work -> home session |

Use `reply` for a response. `send` is for an explicitly requested new conversation,
not a fallback when the original ID is absent. `reply` copies the original session
ID and sets `replyTo` to the incoming ID; both compose commands return a fresh ID
at stage 0. No CLI option lets the agent override the sender/recipient or inject
receipts. Never change the encrypted files directly.

## Data and error contract

Record operations emit JSON to stdout; `list` returns an array. Record fields are
`message`, `stage`, `storedAt`, `updatedAt`, and optional `readAt`. The nested
message carries `id`, `sessionID`, `sender`, `recipient`, `createdAt`, `title`,
`body`, and optional `replyTo`. UUIDs are the correlation keys. CLI dates are ISO
8601; they are **not wire JSON** (wire dates use Swift's 2001 epoch).

Exit 0 means the requested local operation succeeded, not radio delivery.
Exit 1 emits sanitized `{"error":"<code>"}` JSON on stderr. Do not log bodies,
stdout records, keys, or packets as diagnostic evidence. Avoid putting sensitive
bodies in shell history or persistent plaintext files; use supported stdin input
without unintended logging. Body <=64 KiB UTF-8; title <=256 UTF-8 bytes, both
nonempty; escaped complete message <=90 KiB. A successful send/reply is durable
before it returns. If its output is lost, inspect `list` for the existing reply
before retrying compose: repeat compose creates another ID.

Stage meanings: 0 queued locally; 1 iPad custody; 2 destination stored but agent
unread; 3 explicitly read, not proof of task completion. The app observes explicit
reads and sends receipts when possible. Listing/UI viewing do not advance stage.
Do not run two agents against the same task assuming `read` claims it.

## State and boundaries

`location` resolves the same work-specific container Application Support path in
app and CLI contexts:

```text
~/Library/Containers/com.arbol.dashboard.mac/Data/Library/Application Support/ArbolWorkMac/AgentRelay/v1/
```

The authoritative store is `sessions.enc`, a ChaChaPoly-encrypted snapshot with a
separate work-mailbox Keychain key; `store.lock` serializes access. There is no
plaintext spool. Missing keys, corruption, permanent iPad-binding mismatch, or
capacity errors block access/acknowledgment. There is no reset, delete, export,
claim/lease, or agent-execution command. Production CLI accepts no root/key
namespace override; disposable test overrides are compile-time-test-only.

The local CLI is independently invocable. Radio transport remains authenticated
BLE between work and iPad; there is no HTTP, socket, cloud, or direct home-work
fallback. A queued outgoing response retains its ID while the endpoint retries
and reconciles through the relay. A stopped endpoint/offline relay leaves it
queued. Do not claim arrival at home until status supports it.

## Verification boundary

This command surface was checked against the local Swift CLI entry point and
`--help`. `location` is safe to validate without exposing chat or modifying read
state. Installed sandbox/Keychain access and physical relay delivery are separate
acceptance checks; documentation or Skill activation does not establish them.

Local implementation evidence (source paths, not procedures to execute):
`~/repo/arbol-dashboard/ArbolDashboardMac/AgentCLI.swift` and
`~/repo/arbol-dashboard/ArbolDashboardMac/ArbolDashboardMac/AgentStore.swift`.
These standalone source files are not currently confirmed as an enabled Mycel
code corpus; no fabricated resolved Source Ref is claimed for them.
