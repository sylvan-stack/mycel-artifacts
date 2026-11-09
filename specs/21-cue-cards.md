---
role: authored
spec: MYC-21
status: draft
---
# Mycel · 21 Cue Cards

## Purpose

Every agent session on this Mac loads the whole Instructions Hub, about 4,000
tokens, and is trusted to find in it what applies. A Cue Card replaces that
with a precise rule: when a message contains a cue, such as the glossary term
"Arc Review", the instructions that cue calls for are added to the agent's
context, and the agent must read them. Mycel holds the cards and compiles
them into a catalog; [Forester](../../arbol/GLOSSARY.md#forester) delivers
what fires through the hooks of Claude Code, Codex and Kimi Code
([FOR-2](../../forester/specs/02-hooks.md#cue-cards)). The research and the
owner's triage are in
`~/Artifacts/sylvan-stack/research/instruction-injection-2026-11-09.md`.

## Scope

The Cue Card, how cards are declared, the compiled catalog, and the switch
that turns the Instructions Hub on and off. The first version has one type of
card, `literal`: an exact term in the owner's message. Out of scope: matching
the message, delivering the text and checking it was read, which are
Forester's (FOR-2); cards that fire on a session start or before an action,
and matching by meaning, which come later.

## Behaviour

### The Cue Card

A [Cue Card](../../arbol/GLOSSARY.md#cue-card) is a rule record with these
fields:

| Field | Meaning | Required |
|---|---|---|
| `type` | the kind of cue; the first version knows `literal` only | yes |
| `match` | for a literal card, the terms that fire it, one or more | yes, for `literal` |
| `cue_target` | the [Cue Target](../../arbol/GLOSSARY.md#cue-target) whose exact text is added: a whole file or one Markdown section | `cue_target`, `instructions`, or both |
| `instructions` | text added verbatim, written by the card's author | |

A card with both adds its `instructions` and then its target's text. Fields
for other types are decided when those types are introduced. Text that a
card adds is written as plain statements, not as commands addressed to a
system: Claude Code's documentation warns that imperative "system" wording
can make the model treat injected text as an attack.

Example: the card that fires on "commit" and "push" adds the commit rules,
`instructions: "Commits use the identity Git already has; no agent is credited
…"`; the card for "Arc Review" adds that glossary section.

### Declaring a card

A card is declared beside its target, in a `mycel:cues` HTML comment in a
Markdown file of a configured repository's artifact root. A declaration
inside a section targets that section unless it names another `cue_target`:

```markdown
## Planning a Beat

<!-- mycel:cues
type: literal
match: ["plan-beat", "implementation plan"]
-->
```

The comment's body is YAML. A declaration at the top of a file may derive one
card per selected heading, as the glossary does today
([Cue Detection Catalog](../../arbol/GLOSSARY.md#cue-detection-catalog)):
`literal: section_headings` with `heading-levels`, where a heading such as
`Fold / Projection` gives two terms for one target, `literal: exclude` in a
section suppresses its card, and a local `match` list adds terms.

### The catalog

`mycel cues compile` reads every declaration and writes one catalog,
`~/.mycel/cues/catalog.json`, outside every corpus's Git. For each card it
holds the fields, the target's exact text, and a regular expression ready to
apply, so that the reader needs no knowledge of Markdown or of matching rules.
For each source file it holds the path, size, modification time and SHA-256.
The catalog is written to a temporary file and moved into place; a compile
that fails leaves the previous catalog. A declaration with an unknown type or
field, no target and no instructions, or a target that does not resolve is a
fault reported with its file and line, and the other cards compile.

The catalog is compiled on demand, and by one Mycel job every 15 minutes and
whenever a file it watches changes (MYC-D87). A reader that finds a source's size or
time changed since the compile knows that source's cards are stale without
parsing anything (FOR-2 says what Forester then does).

Whatever a card targets is read in full every time it fires, so a targeted
section is kept short; a long section is split into smaller targets rather
than cut when it is added.

`mycel cues match "<text>"` reports which cards the text fires, with the same
expressions, for the owner's and an agent's checks.

### The Hub switch

`mycel hub on | off | status` turns the Instructions Hub on or off for new
sessions and reports which it is. Mycel keeps the state and takes over the
sync that `~/.config/agent-hub/sync-codex-hub.py` does today, writing three
copies:

| Copy | Read by | When on | When off |
|---|---|---|---|
| `~/.mycel/hub/active.md`, imported by `~/.claude/CLAUDE.md` | Claude Code | the Hub | empty |
| `developer_instructions` in `~/.codex/config.toml` | Codex | the Hub with its header | removed |
| `~/.agents/AGENTS.md` | Kimi Code and other tools | the Hub with its header | empty |

Each copy is written atomically; the file it replaces is backed up once.
Switching Claude Code this way needs a one-time change of the owner's
`~/.claude/CLAUDE.md`: its import `@~/Artifacts/mycel/README.md` becomes
`@~/.mycel/hub/active.md`. Taking over the sync, the three copies and this
change were decided with MYC-D87.
Running sessions keep what they loaded. The two switches, this one and
Forester's injection switch (FOR-2), give the four combinations the owner
wants for testing.

## Requirements

| ID | Mycel shall | From v1 | Verified by |
|---|---|---|---|
| MYC-21.1 <!-- 1f8ae79f-b63e-4f6f-8504-8b5d1ba534eb --> | compile every `mycel:cues` declaration in the Markdown files of the configured repositories' artifact roots into one catalog of Cue Cards with `type`, `match`, `cue_target` and `instructions` | New | unit |
| MYC-21.2 <!-- 29db0032-ad3e-489b-b867-f48c208f5bf9 --> | accept the type `literal` only, and report a declaration with an unknown type or field, with neither target nor instructions, or with an unresolved target as a fault with its file and line, compiling the other cards | New | unit |
| MYC-21.3 <!-- ff93ca15-95c3-4798-b6c3-102e897b0316 --> | take a card's target from the section that holds its declaration unless it names a `cue_target`, and record a card that has both `instructions` and a target as adding the instructions first | New | unit |
| MYC-21.4 <!-- a4c158fc-a1bb-4069-af23-32e77be54727 --> | derive one literal card per selected heading from a file-level `section_headings` declaration, splitting `A / B` headings into terms of one target and honouring `literal: exclude` and local `match` lists | New | unit |
| MYC-21.5 <!-- 23a0e5b4-2571-453f-8c3d-93b2caa0b97a --> | store with each card its target's exact text and a regular expression that applies the matching rule of MYC-D85, and with each source its path, size, modification time and SHA-256 | New | unit |
| MYC-21.6 <!-- a246adc4-e8cc-4a43-b633-d07e4d82442e --> | write the catalog atomically and keep the previous catalog when a compile fails | New | unit |
| MYC-21.7 <!-- deb8083d-28a6-42e1-9369-878edea91c96 --> | compile the catalog on demand | New | unit |
| MYC-21.8 <!-- 905279c1-5db5-44bc-a543-6770b9b0ba96 --> | report for a text, with the catalog's expressions, which cards it fires, under the rule of MYC-D85 | New | unit |
| MYC-21.9 <!-- 5dd66fb7-2367-4751-88d2-5fb6dd86cb15 --> | switch the Instructions Hub on or off for new sessions and report its state, writing the three copies atomically from the Hub or empty, with one backup of each file replaced | New | unit |
| MYC-21.10 <!-- 89b150ae-6625-4865-a2c8-20482f405c7b --> | take over the existing Hub sync job, so that one Mycel job keeps the copies current when the Hub is on | New | review |
| MYC-21.11 <!-- 68a66d4b-60f8-4860-aa03-e7e737efc0e8 --> | compile the catalog by one scheduled job every 15 minutes and whenever a file it watches changes | New | review |

## Interface

```sh
mycel cues compile
mycel cues match "Is the Arc Review done before the Saga closes?"
mycel hub off
mycel hub status
```

`compile` replies with the number of cards and sources and the faults, each
with `file`, `line` and `problem`. `match` replies with the cards it fires,
in order of first appearance in the text, each with its terms and target.
`hub status` replies `on` or `off` and the time of the last sync.

## Known problems

- The owner set the first version to literal cards only, so the cards that
  fire once per session for rules every reply needs (agreed in triage) wait
  for a later type. Rules every reply needs, such as plain words, and rules tied to an action,
  such as commit identity before `git commit`, need cards that fire on a
  session start or a tool call. The first version has literal cards only, so
  the Hub stays switchable until those types exist; the commit card fires
  only from the message's words.
- Kimi Code adds hook text only on a submitted prompt (FOR-2), so its later
  card types will also have to ride on prompts.
- Subagents receive no cards in the first version.
- Matching by meaning comes later, probably with Jev rather than Voyage.

## Decisions

| ID | Question | Outcome |
|---|---|---|
| MYC-D82 <!-- 19e2cf83-6ce3-4025-aeb0-f6f3c91a2da9 --> | Does precise injection replace the Instructions Hub? | Decided by the owner on 9 November 2026: "I would like to start deprecating Instruction Hub in favor of more precise instruction injection. I don't like the approach of providing too many instruction and rely on agent reading them carefully." Mycel holds the cards and the catalog; Forester delivers. Claude Code, Codex and Kimi Code are all required ("Kimi Code is required as much as Claude Code and Codex"). |
| MYC-D83 <!-- e9cd23ea-86c5-45e7-b2d0-19c9563ee7bc --> | What is a Cue Card? | Decided by the owner on 9 November 2026: "Let's call them Cue Cards and it will have fields `type`, `activation_rule` and `cue_target`", with no separate term "Cue Type"; `match` replaces `activation_rule` for literal cards; an optional `instructions` field is added verbatim, and a card may have both a target and instructions. Fields of later types are decided with those types; the first version has `literal` only. |
| MYC-D84 <!-- 6a234ad1-3ee6-4efd-99ac-94720b3fb3e8 --> | What stays loaded in every session? | Decided by the owner on 9 November 2026: "as little … as possible. If possible to use none it would be ideal", and "for testing purposes I would like to be able turn on and off Instructions Hub when needed": nothing static once later card types exist, and `mycel hub on | off` meanwhile. |
| MYC-D85 <!-- 401f2c02-3d6b-4c9e-a77a-8f8de7569519 --> | How does a literal term match? | Decided by the owner on 9 November 2026 ("Agreed on everything except shadow period"), accepting the agent's proposal: case-insensitive, as whole words, also with a trailing `s` or `es`, so that "sagas" fires "Saga"; matches inside a fenced code block of the message count too. |
| MYC-D87 <!-- 88798b31-d4f2-461b-a4b7-5a52af847c7e --> | When is the catalog compiled, and who keeps the Hub copies? | Decided by the owner on 9 November 2026 ("Agreed on everything except shadow period"), accepting the agent's proposal: by one Mycel job, run every 15 minutes and when a file it watches changes, that both compiles the catalog and writes the three Hub copies, replacing `~/.config/agent-hub/sync-codex-hub.py` and its launchd job `local.agent-hub.codex-sync` (kept as a backup); `~/.claude/CLAUDE.md` imports `~/.mycel/hub/active.md` instead of the Hub. |
| MYC-D86 <!-- 2d402f73-7adb-493f-9aa6-0788991af584 --> | Where are cards declared, and what becomes of Cue Channel and Cue Command? | Decided by the owner on 9 November 2026, agreeing to the agent's proposal: beside their targets in `mycel:cues` comments, compiled into one catalog; Cue Channel is replaced by the card's `type` and Cue Command by the one effect a card has, adding its text. |
