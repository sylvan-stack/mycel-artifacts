---
role: authored
---
# Guide: Organize Linear Navigation

Use this guide to make what needs the owner's attention **now** easy to find
in Linear. Its primary result is a clearly named, prominent entry that opens
to individual questions, pending decisions, reviews, and other action items
with the next action and source links. Tidying project navigation supports
that result. The guide owns attention selection, relevance judgments, scope,
and verification. For current connector and UI mechanics, read the
[Linear navigation runbook](../tools/linear.md).

## Required outcome

A normal run creates or refreshes a **Needs your attention** document or an
equally clear existing view, and makes it visible near the top of the owner's
favorites. A project-scoped run uses `<project> · Needs your attention`.
Opening it must show what the owner needs to decide, answer, review, do, or
delegate without requiring them to browse specification chapters first.

A generic project index, a specification favorite, a hidden subsection, or a
table of decision-ID ranges does not satisfy this outcome. The entry itself
must communicate its attention purpose, and its content must name individual
items and their next actions. Reuse a suitable attention entry on later runs.
When no verified attention items remain, keep this useful entry with an
explicit checked-empty state, scope, and check date rather than deleting it.

## Scope and authority

The default workspace is [Sylvan Stack](https://linear.app/sylvan-stack), and
the default surface is the authenticated owner's personal left sidebar,
including favorites and their folders. Honor a named workspace, project,
folder, or different navigation surface. A project-scoped run changes that
project's entries; unrelated navigation retains its arrangement.

A request to organize authorizes reversible navigation changes and a sourced
attention document or view. Give a brief account
of the intended changes, then carry them out without an extra approval step.
A request to preview, list, or recommend performs the same inspection and
gives a concrete proposed layout without changing anything.

Removing an item means removing its shortcut or hiding its navigation entry.
It does not authorize deleting or archiving projects, issues, documents,
teams, or shared views; changing lifecycle states; editing project plans;
or changing membership, access, subscriptions, or notification settings.
Personal sidebar cleanup does not authorize rearranging shared project tabs
or resources. An attention index is the content exception described
below; changing shared view filters needs a request covering those changes.

Do not answer open questions, select a decision, or resolve discussion threads
as part of organizing. Requests to list the open questions in the session and
answer them there use
[Answer Open Questions from Linear](linear-open-questions.md). Requests to
work through comments use
[Resolve Linear Comments](linear-resolve.md). Keep that guide's response and
resolution workflow separate. Questions and requests recorded in unresolved
discussions are valid attention sources: index their subject, current state,
and needed action. Do not publish replies or reproduce a comment-resolution
report. Organizing surfaces the work; it does not perform the work it lists.

## Where state lives

| Fact | Source of truth |
|---|---|
| Current favorites, folders, order, and hidden entries | The owner's live Linear navigation |
| Project and issue lifecycle, relationships, and current discussions | Live Linear records, including archived records when checking existing shortcuts |
| Document text with a corpus original | The original file; the corpus's `.linear.json` maps it to its Linear copy |
| Documents without an original, saved views, and their filters | Live Linear |
| Whether a decision is accepted or a question remains open | An explicit record in the authoritative document or discussion, read with later amendments |
| Who needs to act next | Assignment, explicit requests, decision authority, and the latest relevant reply; do not infer it solely from who wrote a comment |

Use current source files to interpret mirrored specifications. Locate their
corpora through `~/.mycel/config.toml` and the relevant `.linear.json` mappings;
do not assume the session's working directory is the project's corpus. If a
copy and its original disagree, retain the existing entry and report the
conflict instead of silently rewriting the specification or treating an old
copy as current truth. Snapshot titles and dates help discovery but cannot
establish completion or acceptance by themselves.

## A run

### 1. Inspect navigation and project evidence

Confirm the workspace and account. Read the actual panel, including collapsed
favorite folders, and identify each in-scope entry's target, type, folder, and
position. Keep this before-state in the session so changes can be explained
and reversed. Do not infer the panel from a list of projects or documents.

Read all pages of the relevant project, document, and issue listings. Include the
underlying records of existing shortcuts even when completed, canceled, or
archived. For each candidate project, read its overview, resources, current
issues and outstanding requests in its documents and discussions. Read the
decision/question sections of every current specification in scope and the
complete open threads on current documents, project pages, and relevant
issues, following pagination. Read later replies before treating a request
as outstanding. Use status updates or milestones when they carry pending
input. Search for existing attention documents and views by content as well
as title. Inspect originals when mirrored content determines classification.

Do not restrict discovery to issues assigned to the owner or labeled Decision.
Questions may exist only in specification tables or comments; unassigned work
may still require the owner's choice or delegation. A workspace run collects
across its current projects, including Mycel and the Driver projects. Record
coverage and unread sources so an incomplete scan cannot appear empty.

An active project may still be in Backlog while its specifications or
implementation are being discussed. A recent date alone does not make an
item relevant; an old date alone does not make it obsolete. For a narrow run,
inspect only the named scope and the dependencies needed to judge it.

### 2. Identify attention items, then decide what belongs

Build the attention list before doing cosmetic cleanup. Include pending
choices and approvals, unanswered questions, requested reviews or responses,
blockers needing input, and unfinished actions the owner owns or must assign.
Distinguish **your next action**, **questions awaiting an answer**, and
**work to assign or delegate**. A question written by the owner may await
someone else's answer; say so rather than inventing an obligation to answer it.

A draft specification's explicitly open choice is a pending decision even
when no issue tracks it. Extract each question and its recorded proposed
default. Distinguish input needed before progress from optional design review
when the source explicitly permits work on defaults; do not invent blockers.
The owner can choose or confirm an option, but the run never accepts it for
them. Read later outcomes and discussions to exclude settled choices.
An accepted decision belongs in project reference material, not the attention
queue, unless a new request or concrete unfinished follow-up requires action.

Prioritize recorded urgent or overdue items, blockers, and decisions that
unlock work. Keep other pending choices accessible by project. Do not invent
due dates or call every backlog task urgent. If live implementation evidence
conflicts with an old open issue, mark the discrepancy and verification needed
instead of presenting its old premise as a fresh decision.

Assign each existing or proposed entry an action and a short reason grounded
in its current record. Use these criteria:

| Evidence | Navigation action |
|---|---|
| Active implementation, specification work, blockers, unanswered questions, or pending decisions | Keep or add a useful entry point |
| Accepted decision or reference that still governs active work | Keep accessible even if its tracking issue is completed |
| Completed or canceled work with no current dependency, follow-up, or requested reference role | Remove its everyday shortcut |
| Explicitly superseded or obsolete material with a verified current replacement | Add or confirm the replacement, then remove the old shortcut |
| Duplicate shortcut to the same target | Keep one useful placement within the run's scope |
| Unclear relevance, unreadable target, or conflicting evidence | Keep it and name the uncertainty |

Respect explicit requests to retain an item. Do not sweep away unexamined
personal favorites or hide ordinary workspace/team entry points merely
because they are not project records. When completed work still has active
follow-up, point to that follow-up and retain any reference it needs.

### 3. Publish the attention entry

Reuse an existing entry only if its name and visible content satisfy the
required outcome. A saved issue view works when all attention items are issues
with reliable filters. If any questions live in documents or discussions,
create or refresh a linked attention document covering them as well. Do not
create one issue per question, a new label taxonomy, or competing specifications
just to make a view possible. Do not change shared view filters outside scope.

For a workspace run, attach the document to the verified team; for a project
run, attach it to that project. Use a supported parent, not another document.
Search by parent and content before creating to avoid duplicates. A previous
empty or stale attention entry is a candidate to refresh, not evidence that
no current questions exist. Keep unrelated reference documents intact.

Use concise sections appropriate to the evidence: **Decisions and input
needed**, **Open questions awaiting answers**, **Follow-through owed to you**,
and **Actions and reviews**. Keep optional choices in **Decisions you can
review** when defaults permit work. A recorded owner instruction awaiting
implementation belongs in follow-through, not as a question to ask them again.
Each pending question or decision gets its own titled row or item. Include:

- the question or action in plain language, with its identifier when present;
- the recorded state and project;
- the concrete next action, and who is expected to take it when known;
- a short proposed option or relevant context when it helps the owner act;
- a verified link to the source, ideally to its section or thread when that
  link is available. Otherwise link the parent and identify the section/ID.

An ID range or a list of source chapters cannot replace these individual
entries. Deduplicate the same action represented in a table, issue, and
discussion, while keeping their useful links. Include owners and dates only
when recorded. Research recommendations remain proposals. Keep accepted
decisions outside pending sections, linking their project reference index
when useful. Refresh stale rows and remove settled items on each run.

Record the checked date and scope, counts by kind, and any unread sources.
Use the user's time context. A checked-empty state says no verified items
were found in the inspected scope and states any coverage limits. It is a
useful status, not a placeholder or a claim about unread records.

The attention document is a navigation summary of current state in Linear,
with links to authoritative sources; it can be Linear-native even when some
sources are mirrored specifications. Do not require a new corpus artifact or
rewrite a source specification just to create this navigation summary. If an
existing attention document already has a mapped local original, respect that
mapping: read its authoring rules, update the original first, then patch its
Linear copy and verify it before updating publication metadata.

### 4. Apply the layout

Place **Needs your attention** near the top of favorites, outside collapsed
project folders; for a project run, make its named attention entry prominent
within the requested scope. Keep useful existing folder conventions for
project references. Use project folders when they improve navigation;
avoid imposing the same folder structure or a fixed item count on every run.
Accepted decisions belong with the project they govern, while settled tasks
need not occupy the everyday panel.

Open the published attention target, add or confirm its favorite, and verify
its useful content before removing any older attention shortcut. Add useful
replacements before removing stale shortcuts. Move entries into the intended
folders and verify the order. Remove empty organization folders only after
their in-scope entries are accounted for and the observed control clearly
acts on the folder. Reuse existing favorites and indexes on repeated runs;
a second run on unchanged state should produce no new items or rearrangement.

Use supported connector capabilities when available; otherwise use observed
UI controls through computer use. Do not substitute undocumented API calls
or guessed app storage edits for unavailable navigation controls. Never
choose a control that deletes the underlying object to remove a shortcut.

### 5. Verify and report

Read the final panel again, expand changed folders, and reopen changed targets
to verify identity and content. Check new views against representative records,
and check new or updated indexes for source links and correct project parent.
Navigate away and return, or otherwise reread persisted state, to confirm
order, membership, additions, and removals survived the operation.

Check the primary outcome from the normal sidebar state: its attention entry
is visibly recognizable, opening it immediately shows individual pending
items and next actions, and it covers the sources inspected. A generic
specification favorite or hidden section is a failed attention outcome even
if its membership and ordering persisted. Do not report full completion
until the attention content and navigation access are both verified.

Give a concise report of what was added, removed, moved, or retained despite
completion, with reasons. Lead with the direct attention-document/view link,
the highest-priority items, and counts or coverage limits. Name
any documents or local files changed and any items left unresolved. Do not
claim the navigation was reorganized when only content or a proposal changed.
Commit local files only if requested. Do not schedule recurring upkeep unless
the user asks for it.

## Failure and resume

- If the account or workspace cannot be confirmed, do not change navigation.
  Explain the missing connection or access.
- If a target cannot be read, retain its shortcut and continue with verified
  items. Scope claims about missing questions or decisions to what was read.
- If navigation controls are unavailable but document writes work, publish
  or refresh the useful attention document in its team/project and return its
  direct link. Report sidebar placement as incomplete; do not claim full
  completion or withhold the useful content because favoriting is blocked.
- After a failed or ambiguous mutation, reread state before retrying. In
  particular, search for an index before repeating a create. Retry a clearly
  transient failure; stop that action when the same failure repeats.
- After interruption, inspect the live state again and apply only the remaining
  differences. Reuse successfully created targets. Report partial completion
  rather than repeating successful writes or undoing unrelated user changes.

<!-- sources:
mycel:tools/linear.md
mycel:operations/linear-resolve.md
-->
