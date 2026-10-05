---
role: blueprint
name: code-review
summary: Review an MR (or branch) against its ticket with overlay-scoped retrieval
inputs:
  - name: mr
    type: string
    required: true
    description: MR URL, or repo+branch when reviewing before an MR exists
  - name: repo
    type: repo
    required: false
    description: inferred from the MR URL when omitted
outputs:
  - artifact: "findings presented in chat; persist to ~/Artifacts/{repo}/{ticket}-review.md only when asked"
    must: [every-finding-has-file-line, severity-ranked]
done_when: every changed file was examined or explicitly listed as skipped;
  each finding carries file:line, severity, and a concrete failure scenario;
  the MR was checked against its ticket's intent, not just against the diff
restrictions: [read-only]
recipe: inherit          # hard pin; "inherit" = defer to caller/default
default-recipe: bro-opus-max
---
# Blueprint: Code Review

The **interactive, one-session** path — review-with-dialogue where the user
can steer. The detached, rigorous path is the
[code-review Chain](../chains/code-review.md): same process split into Cells
with code-enforced coverage + fresh-context verification gates. Reach for the
chain when the user wants the review off this session or wants findings
independently verified; stay here for in-session review and for
branch-without-MR reviews.

## Goal

A review grounded in three contexts at once: the **diff**, the **ticket's
intent**, and the **repo as the branch sees it** — not a read-through of
changed lines in isolation.

## Process

1. **Context in** ([external-mirrors](../operations/external-mirrors.md)):
   `mycel mirror fetch gitlab <mr-url>`, then fetch its ticket with
   `--closure` (the MR description or source branch names it).
2. **Branch view** ([worktree-lifecycle](../operations/worktree-lifecycle.md)):
   `mycel wt add <repo> <branch>` — searches now see base-plus-changes; the
   overlay marks changed chunks and surfaces their `documented_in` reverse
   edges ("this MR drifts N research/glossary docs" — report those).
3. **Review from the worktree**, file by file: for each changed area, retrieve
   its neighbors and callers (`mycel search`, better-grep) before judging —
   correctness against the ticket, hidden blast radius, error paths, tests.
4. **Repo conventions are findings too**: feature-toggle rules
   (new behavior toggled, old path untouched), no `--no-verify`, naming/flow
   conventions per the user's standing rules and the repo GLOSSARY.
5. **Deliver findings** severity-first, each with `file:line`, what breaks,
   and a concrete scenario. Suggested MR comments on request — posting them
   is the user's action (Mycel mirrors the world; Arbol/user act on it).

## Quality bar

- No finding without a failure scenario; no "consider maybe" filler.
- Changed-file coverage is explicit: reviewed / skipped-because.
- The ticket's acceptance intent was compared against what the diff does.
