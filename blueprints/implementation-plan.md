---
role: blueprint
name: implementation-plan
summary: Ticket workspace → implementation plan artifact
inputs:
  - name: ticket
    type: string
    required: true
  - name: repo
    type: repo
    required: true
  - name: ticket_dir
    type: string
    required: true
    description: workspace folder from a chain; its docs ARE the brief. Missing
      or empty → stop with an error (the chain builds it before calling you)
outputs:
  - artifact: "{ticket_dir}/plan.md"
    must: [source-refs-resolve, every-change-names-files]
done_when: "{ticket_dir}/plan.md exists, every planned change names the files it
  touches, the toggle/test strategy is explicit, and open questions are listed
  rather than papered over"
restrictions: [no-repo-edit, no-git-mutations]
recipe: inherit          # hard pin; "inherit" = defer to caller/default
default-recipe: bro-opus-max
---
# Blueprint: Implementation Plan

## Goal

Everything needed to start coding a ticket with no surprises: what changes,
where, in what order, behind which toggle, tested how.

## Process

1. **Read the brief.** `{ticket_dir}` IS your brief — read `objectives.md`
   (they scope the plan), `ticket.md`, `jira-context.md` (constraints/
   decisions), `code-scout.md` (where to dig), and above all `research.md`.
   If `ticket_dir` is missing, empty, or lacks these docs, **stop with an
   error** — the chain builds the workspace before calling you; do not fetch
   or research from scratch to paper over a missing brief. Build ON the
   existing research; do NOT re-derive what the workspace already establishes.
2. **Prior-work gate.** A plan asserts "this work has not started" — verify
   it before planning a single change: the ticket mirror's `status` and
   `subtasks:` frontmatter (a subtask In Code / In Development / In Review
   means code likely exists); `mycel wt list` (local worktrees are the
   registry of in-flight work); remote refs matched against the ticket key
   AND every subtask key — `git -C ~/repo/<repo>/.bare for-each-ref
   refs/remotes/origin | grep -iE '<KEY>|<SUBTASK-KEYS>'` — branch names
   carry the *subtask* key, so a parent-key search proves nothing; open MRs
   for any hit. Prior work found → **stop and surface it**; the plan's job
   may shrink to "review/finish the existing branch", never to duplicate it.
3. **Research the gaps only.** Whatever the brief leaves unanswered for
   *coding* — current behavior, entry points, data flow, existing tests per
   affected domain — close with the level-3 loop
   ([code-research](../operations/code-research.md)): retrieval-first, prior
   research artifacts and glossary entries before exploring by hand. This is
   only what `research.md` did not already cover.
4. **Write the plan** to `{ticket_dir}/plan.md` per the
   [authoring guide](../operations/source-refs-authoring.md), every claim
   carrying a [Source Ref](../../arbol/GLOSSARY.md#source-ref):
   - scope & non-goals (from the objectives/ticket, stated back);
   - approach + ordered changes, each naming files/symbols;
   - **Feature-toggle strategy** (toggle key, what's gated, old path
     preserved unchanged) and branch naming per the git conventions — the
     toggle key comes **verbatim from the MAIN task's "Unleash Feature" Jira
     field** (`unleash_feature:` in the mirror frontmatter; on a subtask,
     fetch the parent — subtask prose never defines FT names and loses to
     the field on any discrepancy). Unleash creates the toggle under that
     exact string; a variant ships a permanently-disabled path. Field empty
     → derive `<main-ticket>-<slug>` and set the field before coding;
   - test plan (both toggle paths where applicable);
   - risks, migration/rollout notes, open questions.
5. **Update, don't duplicate.** Updating an existing `plan.md` beats writing a
   sibling — repair drift, keep the corpus curated. A companion
   `{ticket_dir}/plan-context.md` is welcome when gathered context outgrows the
   plan.

## Quality bar

- A teammate could execute the plan without re-deriving the research.
- Prior work was ruled out (or surfaced) — the plan never re-plans a branch
  that already exists.
- Every "change X" names concrete files; no hand-waved "update the service".
- Unknowns are explicit open questions with owners, never silent gaps.
- The plan built on the workspace's research rather than duplicating it.

## Output

Your final message must report the artifact you wrote — a clickable markdown
link to `{ticket_dir}/plan.md` (absolute path), plus the 2–3 decisions that
most shape how the work should proceed (approach, toggle, riskiest change). Do
not paste the file's contents back.
