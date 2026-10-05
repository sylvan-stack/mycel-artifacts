---
role: authored
---
# Guide: Living Topics — continuity across Chat Sessions

How to work a [Living Topic](../../arbol/GLOSSARY.md#living-topic): a durable,
evolving context hub for a subject that returns in different forms over months.
This guide is authoritative for the topic folder contract, how a new
[Chat Session](../../arbol/GLOSSARY.md#chat-session) picks an existing topic up,
what gets written back during the session, and the wrap-up. The definition and
boundaries of the term live in the glossary; this guide is only the process.

Contents: two layers · topic folder · session start · Chat Note template ·
write-back · wrap-up · new topic · Seqoya Chat action · anti-patterns.

## Two layers, one subject

A Living Topic exists on two surfaces with strictly separated jobs:

1. **The topic record** — the Entity itself (kind `living_topic`, id
   `liv-…`), managed on the `Seqoya[Living Topics]` page: title, description,
   and [Entity Edges](../../arbol/GLOSSARY.md#entity-edge) to Chat Sessions,
   Artifacts, tickets, Grafts, and messages. The **description is display
   text only** — one or two sentences so the UI card explains itself. It is
   never working context: agents must not read it for facts or write findings
   into it.
2. **The topic folder** — the working surface. Everything an agent needs to
   continue the subject, and everything it learns, lives in files here.

If the two disagree, the folder is the truth for content; the record is the
truth for identity (title, id) and links.

## The topic folder

Path: `~/Artifacts/living-topics/<slug>/` — deliberately at the top of the
Artifact Corpus, **outside every `~/Artifacts/<repo>/`**, because a Living
Topic is repo-agnostic: its linked Entities and manifestations may span any
number of repositories.

- `<slug>` is derived from the title once, at folder creation, and **frozen**:
  later title edits in Seqoya never rename the folder. The durable binding is
  the `living_topic_id` in INDEX.md frontmatter — to find a topic's folder by
  id, grep the frontmatter, not the slugs.
- The folder is created lazily, on the first session that actually works the
  topic — a topic record with no folder yet is fine.
- The topic may contain **any artifacts it needs** (investigations, data
  extracts, drafts, diagrams); every one of them must be registered in
  INDEX.md.

### Core file contract

| File | Contract |
|---|---|
| `INDEX.md` | Frontmatter: `living_topic_id`, canonical title. Body: one line per artifact in the folder — what it is and when to read it. Every new artifact is registered here in the same session that creates it. |
| `FINDINGS.md` | Confirmed insights worth carrying into every future session. Dated entries; update-don't-duplicate — supersede an entry rather than adding a contradicting sibling; a disproved finding moves to FALSE-POSITIVES.md. |
| `FALSE-POSITIVES.md` | Ruled-out hypotheses, dead ends, misleading signals. Entry = the claim, why it is wrong, the evidence. This is the highest-value file: it is what stops the next session from re-investigating. |
| `NEXT-STEPS.md` | How the next session should proceed. **Rewritten** at wrap-up, not appended — stale steps are deleted, not accumulated. |
| `SUMMARIES.md` | One dated entry per linked Entity examined in depth: entity chip/reference + 3–5 lines. If a summary needs more, it becomes its own artifact in the folder and SUMMARIES.md keeps only the pointer. |
| `TIMELINE.md` | Append-only, one line per manifestation or working session: date — what happened — link. Answers "when did this last flare up and what changed since". |

## Starting a session on an existing topic

1. **Recognize recurrence before starting fresh.** When an issue feels
   familiar, search Living Topics first (Entity Search, tag `liv`, or the
   Seqoya list). Continuing an existing topic beats re-deriving context.
2. **Hydrate via a Chat Note, not a bare entity chip.** A chip is only a
   pointer; a [Chat Note](../../arbol/GLOSSARY.md#chat-note) is durable and is
   included whenever a later Turn is composed, so the instructions survive the
   whole session. The note carries the topic chip *plus* the reading order and
   write-back rules — instantiate the template below (the Seqoya **Chat**
   button does all of this automatically; only a session started outside it
   needs the note added manually at session start).
3. **Read cheapest-first, never crawl.** `INDEX.md` → `NEXT-STEPS.md` (why
   you are probably here) → `FINDINGS.md` + `FALSE-POSITIVES.md` (mandatory,
   always) → `TIMELINE.md`, `SUMMARIES.md`, other folder artifacts, and linked
   Entities **only as the task needs them, most recently linked or updated
   first**. Reading every linked Entity up front is a failure mode, not
   thoroughness.

## Chat Note template

Single source of truth — manual use and the Seqoya Chat action must both
instantiate exactly this. Placeholders: `{TITLE}`, `{LIVING_TOPIC_ID}`,
`{FOLDER}`.

```
This Chat Session continues the Living Topic “{TITLE}” ({LIVING_TOPIC_ID}).
Topic folder: {FOLDER}

Before responding to the first request:
1. Read {FOLDER}/INDEX.md, then NEXT-STEPS.md, then FINDINGS.md and
   FALSE-POSITIVES.md — all four are mandatory.
2. Consult TIMELINE.md, SUMMARIES.md, other folder artifacts, and linked
   Entities only when the task needs them, most recent first.
3. Never re-investigate anything in FALSE-POSITIVES.md unless new evidence
   contradicts it — say so instead.

While working:
- Record durable conclusions in FINDINGS.md the moment they are reached;
  disproved directions go to FALSE-POSITIVES.md. Do not wait for the end of
  the session.
- Add a dated SUMMARIES.md entry for each Entity you examine in depth.
- Register every artifact you create in this folder in INDEX.md.

When asked to wrap up the topic (or the work clearly concludes): rewrite
NEXT-STEPS.md for the next session, append one TIMELINE.md line for this
session, reconcile INDEX.md, and list the Entities (including this Chat
Session) that should be linked to the topic in Seqoya.
```

## Write-back during the session

Write-back is **incremental, at conclusion time** — this is the contract that
keeps the topic living. An agent cannot detect that a session is about to end,
so end-of-session-only write-back silently rots the folder into a stale
bookmark. Whenever a durable conclusion is reached mid-session, it goes to
FINDINGS.md or FALSE-POSITIVES.md immediately; deep dives into an Entity earn
their SUMMARIES.md entry when the dive happens.

Entity linking (`living_topic.link_entity`) is performed by the user in Seqoya
via **Link Entity**; agents do not link directly. An agent that identifies an
Entity worth linking records it in the wrap-up list (and in NEXT-STEPS.md if
the session ends without a wrap-up).

## Wrap-up

Triggered by the user ("wrap up this topic") or when the work clearly
concludes:

1. Rewrite `NEXT-STEPS.md` from scratch for the next session.
2. Append one `TIMELINE.md` line for this session.
3. Reconcile `INDEX.md` against the folder's actual contents.
4. List the Entities to link — always including the current Chat Session —
   for the user to apply in Seqoya.

## Creating a new topic

1. **Search first** — Entity Search over existing Living Topics; a duplicate
   topic splits continuity, which is the one thing the mechanism exists to
   preserve.
2. Create the record in Seqoya: title + a one-to-two-sentence display
   description.
3. Create the folder skeleton (INDEX.md with frontmatter + the five core
   files), seed FINDINGS.md and NEXT-STEPS.md from the conversation that
   revealed the subject.
4. Link the current Chat Session and the Entities already on the table.

Boundary with [troubleshooting](troubleshooting.md): a difficult
implementation/bug-fix investigation inside one repository belongs to the
troubleshooting process and its per-repo records. A Living Topic is for a
*subject* whose continuity outlives any single investigation, ticket, or repo;
a troubleshooting record can itself be linked to a topic.

## Seqoya "Chat" action

The topic-card **Chat** button (RPC `living_topic.start_chat`): creates the
folder skeleton if missing, creates a new Chat Session titled after the topic,
adds a Chat Note instantiated from the template above (no Turn is opened),
links the new session to the topic, and opens it in Elma. The session's
workspace is **hardcoded to the Arbol repository** — the Worktree Container
`/Users/example/repo/sylvan-stack/Arbol`, executing on its default checkout
(`main`), with the IP resolved by the Arbol repo's routing rules — exactly the
session Elma would create for a new Arbol chat. Topics remain repo-agnostic
as a concept, but in practice they target long-lived Arbol issues, so the
button does not ask. Revisit if a topic for another repo ever appears. The
template in this guide is the source of truth the implementation mirrors
(`daemons/core/arbol_core/living_topic_folders.py`) — change them together.
A session started via the button is already linked; the wrap-up list then
covers only the other Entities.

## Anti-patterns

- **Topic as task tracker** — completable work is a
  [Graft](../../arbol/GLOSSARY.md#graft); a topic is never "done".
- **Topic as current focus** — that is a
  [Spotlight](../../arbol/GLOSSARY.md#spotlight).
- **Topic as per-ticket folder** — ticket deliverables stay in
  `~/Artifacts/<repo>/tickets/<KEY>/`; the topic links to them.
- **Description as summary** — description is UI display text; facts live in
  the folder.
- **Bare-chip hydration** — a chip without the Chat Note loses the reading
  order and write-back contract.
- **End-of-session write-back** — conclusions are recorded when reached.
- **SUMMARIES.md as a blob** — entries stay 3–5 lines; longer summaries become
  their own registered artifacts.
- **Crawling all linked Entities at session start** — read on demand, most
  recent first.

<!-- sources:
Arbol:daemons/core/arbol_core/rpc/living_topics.py
Arbol:renderer/apps/seqoya/src/pages/LivingTopics.svelte
-->
