---
role: authored
spec: MYC-21
status: accepted
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

The comment's body is YAML. A `cue_target` that names another target writes it
in the [Cue Target](../../arbol/GLOSSARY.md#cue-target) form: `<repo>:<path>`
for a whole file, or `<repo>:<path>#<heading path>` for a section, where
`<repo>` is the configured repository, `<path>` is relative to its artifact
root, and the heading path lists the headings that contain the section,
outermost first, ending with its own, joined by ` > `, such as
`arbol:GLOSSARY.md#Arbol Glossary > Arbol Trunk` (MYC-D89). The catalog still
names cards by the section's anchor (`id`, MYC-D88).

A declaration at the top of a file may derive one
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

### The catalog file

`~/.mycel/cues/catalog.json` is one JSON object in UTF-8, written whole by
`mycel cues compile` (MYC-21.6). Its reader, Forester, needs nothing else: no
Markdown, no matching rule (FOR-2, [Cue Cards](../../forester/specs/02-hooks.md#cue-cards)).
The form is MYC-D88.

| Key | Holds |
|---|---|
| `version` | the integer `1`; a reader that finds another value, or no file, treats it as no catalog |
| `compiled_at` | when the compile ran, UTC, ISO 8601 |
| `cards` | the cards, sorted by `id` in Unicode code point order |
| `sources` | one record per file a card's text comes from, sorted by `path` in code point order |
| `faults` | the declarations that did not compile (MYC-21.2), each `file`, `line` and `problem`, as `compile` replies, sorted by `file`, then `line` |

**A card** has these keys, all present, `null` where the table says so:

| Key | Holds |
|---|---|
| `id` | a name that stays the same from one compile to the next while the target keeps its heading: `<repo>:<path>#<anchor>` of the card's target section, with `<path>` relative to the repository's artifact root; `<repo>:<path>` for a whole file; for a card with instructions only, `<repo>:<path>#<anchor>` of the section that holds its declaration, or `<repo>:<path>` when the declaration stands before the first heading. Several cards that would get one `id` keep it for the first and get `~2`, `~3` for the others, in the order of their declaring file's path, then of `declared_at`'s `first_line` |
| `type` | `literal` |
| `group` | `glossary` for a card derived from a file-level `section_headings` declaration (MYC-21.4), `other` for every other card; FOR-2 delivers `other` first |
| `title` | the target's heading; for a whole file its first heading, or its file name if it has none; for a card with instructions only, its first term. The overflow statement lists cards by it |
| `match` | the terms that fire the card, as written, derived ones included: `Fold / Projection` gives `["Fold", "Projection"]` |
| `pattern` | one expression in the syntax of Python's `re` that applies MYC-D85 to all the terms (below) |
| `cue_target` | `path`, `heading`, `anchor`, `first_line` and `last_line` of the target; for a whole file `heading` and `anchor` are `null` and the lines run from the first line after its YAML front matter (1 if it has none) to its last line; the whole key is `null` for a card with instructions only |
| `instructions` | the card's instructions as written, or `null` |
| `text` | the exact text a delivery adds: the instructions without trailing line breaks, then `\n\n`, then the target's text; or only one of the two (MYC-21.3) |
| `sources` | the `path` of every file the text comes from: the declaration's file and the target's file, once each |
| `declared_at` | `path`, `first_line` and `last_line` of the whole `mycel:cues` comment that declares the card |

A target section runs from its heading line to the line before the next
heading with the same number of `#` or fewer, without trailing blank lines; a
heading inside a fenced code block is not a heading. Its anchor is the one
GitHub gives the heading. The target's text is those lines, or the whole
file's lines without its YAML front matter, with every `mycel:cues` comment
left out, each removed comment taking one blank line that follows it with it,
joined by `\n`, with no final line break. Paths are absolute; lines count
from 1.

**The pattern.** Each term is split at white space, each word escaped with
`re.escape`, and the words joined by `\s+`, so that a term broken over a line
still matches; the terms, longest first and terms of one length in the order written, are
joined into
`(?i)(?<!\w)(?:<term>|<term>…)(?:e?s)?(?!\w)`. The reader uses it as it
stands with `re.search` on the whole message, fenced code blocks included,
adding no flags. The start of the first match is where the card's terms first
appear; cards that first appear at the same place keep the order of `cards`.
`mycel cues match` uses the same expressions (MYC-21.8).

**A source** has `path` (absolute), `repo` (the configured repository whose
artifact root holds it), `size` in bytes, `mtime_ns`, the modification time in
integer nanoseconds, and `sha256`, of the file as the compile read it. A source
is stale when the file's size or `mtime_ns` on disk differs from the record,
and a card is stale when any of its `sources` is. FOR-2 says what Forester then
sends.

An example, with texts and digests shortened and line numbers, sizes and
times only illustrative:

```json
{
  "version": 1,
  "compiled_at": "2026-11-10T14:05:00Z",
  "cards": [
    {
      "id": "arbol:GLOSSARY.md#arc-review",
      "type": "literal",
      "group": "glossary",
      "title": "Arc Review",
      "match": [
        "Arc Review"
      ],
      "pattern": "(?i)(?<!\\w)(?:Arc\\s+Review)(?:e?s)?(?!\\w)",
      "cue_target": {
        "path": "/Users/msix/Artifacts/arbol/GLOSSARY.md",
        "heading": "Arc Review",
        "anchor": "arc-review",
        "first_line": 202,
        "last_line": 206
      },
      "instructions": null,
      "text": "## Arc Review\n\nThe last step of an [Arc](#arc): once all its [Beats](#beat) are finished, … \n\n**Example:** The three Beats of an Arc that adds a command are finished. …",
      "sources": [
        "/Users/msix/Artifacts/arbol/GLOSSARY.md"
      ],
      "declared_at": {
        "path": "/Users/msix/Artifacts/arbol/GLOSSARY.md",
        "first_line": 3,
        "last_line": 7
      }
    },
    {
      "id": "mycel:README.md#working-rules-for-every-task",
      "type": "literal",
      "group": "other",
      "title": "commit",
      "match": [
        "commit",
        "push"
      ],
      "pattern": "(?i)(?<!\\w)(?:commit|push)(?:e?s)?(?!\\w)",
      "cue_target": null,
      "instructions": "Commits use the identity Git already has; no agent is credited …",
      "text": "Commits use the identity Git already has; no agent is credited …",
      "sources": [
        "/Users/msix/Artifacts/mycel/README.md"
      ],
      "declared_at": {
        "path": "/Users/msix/Artifacts/mycel/README.md",
        "first_line": 118,
        "last_line": 122
      }
    },
    {
      "id": "mycel:operations/implementation-planning.md#the-procedure",
      "type": "literal",
      "group": "other",
      "title": "The procedure",
      "match": [
        "plan-beat",
        "implementation plan"
      ],
      "pattern": "(?i)(?<!\\w)(?:implementation\\s+plan|plan\\-beat)(?:e?s)?(?!\\w)",
      "cue_target": {
        "path": "/Users/msix/Artifacts/mycel/operations/implementation-planning.md",
        "heading": "The procedure",
        "anchor": "the-procedure",
        "first_line": 71,
        "last_line": 102
      },
      "instructions": "A Beat's plan is written by this procedure before its first step.",
      "text": "A Beat's plan is written by this procedure before its first step.\n\n## The procedure\n\n1. **Read the inputs.** …",
      "sources": [
        "/Users/msix/Artifacts/mycel/operations/implementation-planning.md"
      ],
      "declared_at": {
        "path": "/Users/msix/Artifacts/mycel/operations/implementation-planning.md",
        "first_line": 73,
        "last_line": 77
      }
    }
  ],
  "sources": [
    {
      "path": "/Users/msix/Artifacts/arbol/GLOSSARY.md",
      "repo": "arbol",
      "size": 187342,
      "mtime_ns": 1794268800000000000,
      "sha256": "3f1c…"
    },
    {
      "path": "/Users/msix/Artifacts/mycel/README.md",
      "repo": "mycel",
      "size": 14210,
      "mtime_ns": 1794265200000000000,
      "sha256": "9a07…"
    },
    {
      "path": "/Users/msix/Artifacts/mycel/operations/implementation-planning.md",
      "repo": "mycel",
      "size": 7633,
      "mtime_ns": 1794182400000000000,
      "sha256": "c45e…"
    }
  ],
  "faults": [
    {
      "file": "/Users/msix/Artifacts/mycel/operations/code-research.md",
      "line": 12,
      "problem": "unknown type: meaning"
    }
  ]
}
```

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
| MYC-D86 <!-- 2d402f73-7adb-493f-9aa6-0788991af584 --> | Where are cards declared, and what becomes of Cue Channel and Cue Command? | Decided by the owner on 9 November 2026, agreeing to the agent's proposal: beside their targets in `mycel:cues` comments, compiled into one catalog; Cue Channel is replaced by the card's `type` and Cue Command by the one effect a card has, adding its text. |
| MYC-D87 <!-- 88798b31-d4f2-461b-a4b7-5a52af847c7e --> | When is the catalog compiled, and who keeps the Hub copies? | Decided by the owner on 9 November 2026 ("Agreed on everything except shadow period"), accepting the agent's proposal: by one Mycel job, run every 15 minutes and when a file it watches changes, that both compiles the catalog and writes the three Hub copies, replacing `~/.config/agent-hub/sync-codex-hub.py` and its launchd job `local.agent-hub.codex-sync` (kept as a backup); `~/.claude/CLAUDE.md` imports `~/.mycel/hub/active.md` instead of the Hub. |
| MYC-D88 <!-- ccdbbef7-3275-4219-b961-877825ecc822 --> | What is the catalog's exact JSON form? | Chosen by the agent on 10 November 2026 in SYL-356, under MYC-21.1 and MYC-21.5, so that Mycel and Forester can be built at the same time: the keys of [The catalog file](#the-catalog-file); an `id` built from the target's anchor so that a recompile does not send a card again; `group` with `other` before `glossary`, the order the owner agreed for FOR-D129; one Python `re` expression per card; `text` composed by Mycel; and each card's `sources` and `declared_at`, so that a stale card names the lines to read (FOR-D131). |
| MYC-D89 <!-- b8162e02-0a03-4325-a876-79057dd0a43c --> | How does a declaration name another target? | Decided by the owner on 10 November 2026 ("Agreed with Heading path"), accepting the agent's recommendation over the GitHub anchor: the [Cue Target](../../arbol/GLOSSARY.md#cue-target) form, `<repo>:<path>` or `<repo>:<path>#<heading path>`, readable and unambiguous where two sections share a heading; the catalog's `id` and `cue_target.anchor` (MYC-D88) are unchanged. |
