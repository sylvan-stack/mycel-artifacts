---
role: authored
---
# tg-read CLI

`tg-read` is a local personal-account Telegram reader, with explicit chat grants,
ignored IDs and named streams. The [stream guide](../operations/tg-stream.md)
owns the agent workflow, activated only by `/tg-stream` (native Codex:
`$tg-stream`). This manual describes the existing tool, not a bot integration or
a Telegram-side stream subscription.

## Locate the tool

The installed commands are `tg-read` and `tg-read-owner`. Source and detailed
CLI documentation live at `~/repos/tg-read/`; see its
[README](../../../repos/tg-read/README.md) and
[project instructions](../../../repos/tg-read/AGENTS.md) for development work.
Use `tg-read --help` or the selected command's `--help` for current syntax.

## Resolve and manage streams

```sh
tg-read stream list
tg-read stream show work
tg-read stream create work 123456789 -1001234567890 --description "Work conversations"
tg-read stream add work 987654321
tg-read stream remove work 123456789
tg-read stream rename work operations
tg-read stream delete operations
```

Names are case-insensitive slugs starting with a letter, using a-z, 0-9, `_` or
`-`, with a maximum of 64 characters. Member arguments can be numeric IDs or
currently granted aliases. Listing/showing and membership changes are local;
they do not fetch messages or grant content access. `show` reports visible
members and their current grant status. Empty streams are supported.

These are fictional examples, not installed stream names or account data. Resolve
the owner's current names and membership through the CLI rather than this manual.

## Scope and output

```sh
tg-read messages stream:work --since today --limit 20
tg-read search stream:work "deployment" --since "2 days ago" --limit 10
tg-read list-granted --stream work --since yesterday --until today --limit 10
```

`messages` and `search` return JSONL messages merged newest first, with the source
chat ID/alias and a `stream` field. `list-granted --stream` returns a row per chat,
with its identity and a messages array, including an empty array when nothing
matches. `--limit` is per chat; a stream with several members may return that many
messages for each. Message command limits are 1–1000; defaults are 50 for messages
and search, 10 for list-granted.

`--since` is inclusive and `--until` exclusive. `today`, `yesterday` and `tomorrow`
mean local midnight for the relevant day. `now` is the invocation time.
`"2 days ago"` is exactly 48 elapsed hours before invocation; integer minutes,
hours and weeks are also supported. Quote phrases containing spaces. Explicit
date-only values retain midnight-UTC semantics; ISO timestamps need a timezone.
Output message times are UTC.

Every non-ignored member needs a current grant. A missing grant rejects the stream
read before connection, rather than silently returning a partial membership.
Empty/fully ignored streams produce no message output and do not connect.
Combined feeds are emitted only after all selected member reads succeed; grouped
list-granted output can have earlier rows before a later failure. Nonzero exits
must be reported as incomplete work.

Implementation locators: [CLI](../../../repos/tg-read/src/tg_read/cli.py),
[stream selection](../../../repos/tg-read/src/tg_read/streams.py), and
[history/search](../../../repos/tg-read/src/tg_read/client.py). This standalone
tool's source has ordinary file locators here; do not invent an unregistered
Mycel repository name for a Source Ref.

## Permission boundary

```sh
tg-read grant 123456789 -1001234567890
tg-read ignore 987654321
tg-read status
```

Use grant/ignore commands only for the owner's explicitly requested IDs.
Granting multiple IDs validates/resolves them before saving new grants together.
Ignored IDs override grants, are hidden in stream metadata and content reads, and
cannot be granted while ignored. Ignoring also removes existing grants; ignored
people are skipped as message authors in other approved chats. Natural-language
mentions inside another message are not scrubbed.

Metadata is stored privately under `~/.local/share/tg-read/`: account-bound
`streams.json`, grants in `policy.json`, and the one-ID-per-line `.ignored` file.
Use the filtered CLI rather than reading these files directly. Never print or
copy `credentials.json`, `account.session` or associated authentication keys.

Telegram does not provide a per-chat, read-only account session. The tool enforces
the restrictions locally: request guarding, selected peers, disabled account-wide
updates and no send/reply/edit/delete/reaction/join/read-receipt operations.
Possession of the raw session would bypass that tool boundary.

Account setup remains interactive through `tg-read-owner configure` and `login`;
the owner enters secrets locally. Never request those secrets in chat. This skill
does not authorize account setup, new grants or tests merely because the workflow
is invoked. Runtime implementation locators:
[guard](../../../repos/tg-read/src/tg_read/guard.py) and
[local permission changes](../../../repos/tg-read/src/tg_read/permissions.py).
