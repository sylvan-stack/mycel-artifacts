---
role: authored
---
# Guide: Answer Open Questions from Linear

Use this guide to put every question that waits for the owner in front of
them in the session. Questions and pending decisions are recorded in the
Linear workspace Sylvan Stack (`https://linear.app/sylvan-stack`): as rows in
the Decisions table of a specification, as issues, and in comments. Answering
them there means opening each place and writing a comment. A run collects
them all and gives one numbered list in the session. The user answers there,
by number, and each answer is then written to the place the question is
recorded in.

This guide is authoritative for what counts as an open question, the list a
run gives, and what is written once the user has answered. How an artifact is
written is decided by the corpus the artifact lives in.

**Contents:** when to use · rules · where state lives · a run (collect → give
the list → take the answers → record them) · failure and resume.

## When to use

Start a run when the user asks which questions or decisions are waiting for
them in Linear, or asks to answer them in the session. The request is
complete as it stands: which questions are open comes from Linear. Do not ask
the user to name them. When the request names a project, a document or an
issue, the run reads only that place; otherwise it reads the whole workspace.

Not for:

- publishing or refreshing the **Needs your attention** entry in Linear, or
  tidying the sidebar — use [Organize Linear Navigation](linear-organize.md);
- the comments the owner left in Linear, which wait for an agent and not for
  the owner — use [Resolve Linear Comments](linear-resolve.md);
- creating, planning or closing issues.

## Rules

- **The owner answers.** A proposed answer stays a proposal until the user
  accepts it in the session. The agent never chooses for them, and an item
  the user does not mention stays open.
- **An item can be answered without opening Linear.** It says in plain words
  what is asked, what is proposed, what the other choices are, and what each
  would mean in practice. A name the owner may not know is explained before
  it is used.
- **Nothing is written before the user answers.** Collecting and listing
  change nothing, in Linear or in a file.
- **An answer is recorded as it was given:** in the owner's words, or in a
  short form that says the same. An answer that can be read in two ways is
  asked about in the session and not recorded.
- **Change the original first.** A Linear document is usually a copy of a
  file in a corpus. The file is changed, then the copy is brought in line.
  A copy is never changed alone.
- **Mark what the agent posts.** Every comment an agent posts in Linear
  begins with `**Agent:**`. Never mark a thread resolved, and never edit or
  delete a comment the owner wrote.
- **Keep no record.** The list is given in the session and nowhere else: no
  Linear document, no file.
- **Commit nothing** unless the request says so. Changed files stay in the
  working tree and are named in the report.

## Where state lives

| Fact | Source of truth |
|---|---|
| Whether a row of a Decisions table is open | The row's Outcome in the original file. `.linear.json` at the root of its corpus maps the file to the Linear copy |
| Whether an issue is open | Its state in Linear |
| Whether a question in a comment is answered | Its thread in Linear, read to the last comment |
| The user's answers | The session, until they are recorded |

Nothing is remembered between runs. A question that was listed and not
answered when its session ended is collected again by the next run.

## A run

### 1. Collect

Read every document, every project page, and every issue that is neither
done nor canceled, each with its comments. Follow each listing to its last
page. Count the places read: the list states them. The calls are in the
[Linear runbook](../tools/linear.md).

A question is open when it is one of these:

| Where it is recorded | It is open when |
|---|---|
| A row in the Decisions table of a specification | Its Outcome says `Open` |
| An issue that asks the owner to decide or to answer: it carries the label `Decision`, or its title or description puts a question to the owner | The issue is neither done nor canceled |
| A question an agent put to the owner in a comment on a document, an issue or a project page | The thread is not resolved in Linear |
| A question to the owner in the text of an issue or a project page | Nothing written later answers it |

Then read what was already said about each one, to the last comment:

- **The owner has answered it in Linear, or has asked something back.** It
  waits for an agent and not for the owner. It is not an item. Name it after
  the items; [Resolve Linear Comments](linear-resolve.md) works on it.
- **The same question is recorded in several places,** for example as a row
  and as an issue. It is one item with a link to each place.
- **The Linear copy and the original disagree** on whether a row is open.
  The original counts, and the item says that the copy is behind.

The document **Needs your attention**, which
[Organize Linear Navigation](linear-organize.md) publishes, is a list made on
an earlier day. It can show where to look. It is not a place a question is
recorded in: take no item from it.

### 2. Give the list

Give the user one list in the session. Put first the questions the source
says work is waiting for. Then the others, by project, in the order of the
place they are recorded in. Number them through. A number keeps its meaning
for the rest of the session, so the user can answer by number.

Each item has:

- the question in plain words, and its identifier as a link to the place it
  is recorded in;
- what is proposed, and what that means in practice. When no proposal is
  recorded, say so; a recommendation of the agent's own is marked as such;
- the other choices that are recorded, each with what it would change;
- when a thread on it already holds a conversation, its last message and one
  line on what came before.

```markdown
### 1. <the question in plain words> ([<identifier or title of the place>](<link>))
**Proposed:** <the proposed answer and what it means in practice>
**Otherwise:** <the other choices, each with what it would change>
```

A fictional example:

> ### 4. When a search finds nothing, does the command end with an error? ([QRY-D3](https://linear.app/sylvan-stack/document/example))
> **Proposed:** No. It prints an empty list and ends normally, so a script
> that calls it does not have to tell "nothing found" from "something broke".
> **Otherwise:** End with an error code. A script would notice an empty
> result without reading the output, and would need a second check to tell
> it from a failure.

A question in a comment is linked the way
[Resolve Linear Comments](linear-resolve.md#4-give-the-list) links a comment.
A row of a Decisions table is linked by its document; the identifier says
which row.

After the items, the list states:

- the questions the owner has already answered or asked back about in
  Linear, which wait for an agent;
- what was read: the number of documents, project pages and issues, and any
  place that could not be read;
- how to answer: by number. `ok` accepts what is proposed. Anything else is
  the owner's own answer, a choice among those listed, or a question back.
  One answer can cover several numbers, or all of them.

### 3. Take the answers

The user sends answers for some or all of the items. Read all of them before
changing anything: one answer can change more than its own item, and two
answers can touch the same passage.

| The answer to an item | What to do |
|---|---|
| accepts what is proposed, picks a choice, or gives the owner's own answer | Record it (step 4) |
| asks something back, or leaves the question undecided | Respond in the session. The item stays open |
| the item is not mentioned | It stays open. Nothing is written for it |

### 4. Record the answers

An answer is written to the place its question is recorded in:

| The question is | What is written |
|---|---|
| a row in a Decisions table | The row's Outcome: that the owner decided, the date, and what was decided. Text that rests on the earlier proposal is changed in the same change: requirements, other sections, other specifications, an index. Then the Linear copy is brought in line |
| an issue | One comment on the issue that gives the answer. When the issue names a row, the row is recorded as above. An issue that exists only to ask the question is then set to done; an issue that is a task keeps its state |
| a question in a comment | One reply in its thread that gives the answer. The owner closes the thread |

Changing a file and bringing its copy in line follow steps 5 and 6 of
[working a thread](linear-resolve.md#3-work-a-thread): read the README of the
file's folder first, change every place that says the same, and change the
copy with a partial edit.

A comment that gives an answer has this form:

```text
**Agent:** Answered in the session on <date>: <the owner's answer>
```

An answer can call for work the text cannot hold: new code, a new
specification, research. Record the decision, name the work in the report,
and do not start it.

Then report in the session:

- for each answered item, the words that were written and where;
- the files changed, and that they are not committed;
- the items still open, under their numbers, each with the response to what
  the user asked back.

Repeat steps 3 and 4 until no item is open or the user ends the run.

## Failure and resume

- **No connector, or not signed in.** Stop and say so. Do not work from a
  list of questions seen earlier.
- **A place cannot be read.** Go on with the others and name it in the list.
  A run that could not read every place never says that no questions are
  open.
- **The original is changed and the copy cannot be updated.** Say so in the
  report. An issue for that question is not set to done until the copy is in
  line.
- **A comment cannot be posted, or an issue cannot be changed.** Tell the
  user which one. The next run lists the question again.
- **The session ends before the user answers.** Nothing was written. The
  next run collects the same questions.
- **The session ends after an answer was given and before it was recorded.**
  The answer is not kept. The next run lists the question again.

<!-- sources:
mycel:operations/linear-resolve.md
mycel:operations/linear-organize.md
mycel:tools/linear.md
-->
