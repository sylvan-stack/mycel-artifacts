---
role: authored
---
# Guide: Branch Context in a Standard Checkout

Use the selected repository folder directly for branch context and updates.
Worktree containers, nested checkouts, and their lifecycle commands are
deprecated. The historical [worktree guide](worktree-lifecycle.md) is not an
active operating procedure.

## Inspect branch context

Confirm the repository root, current branch, working tree status, and relevant
local or remote refs. For an MR, inspect its source and target refs and obtain
external context through [external mirrors](external-mirrors.md). Reading refs
and diffs does not require switching the checkout. Preserve existing changes.

Switch branches only with explicit user approval. A request to inspect an MR
is not approval to switch. Do not create, attach, refresh, drop, or archive
worktrees. If another repository is needed, use its standard folder; do not
silently substitute a different checkout of the selected repository.

## Update the current branch

Determine the intended base from the request, upstream configuration, or MR;
do not assume it is named master. Inspect local edits and ongoing Git
operations before fetching and integrating the base. Do not reset, discard,
or automatically stash existing changes. Proceed only when integration can
preserve them; explain any concrete blocking conflict.

Use the repository's merge/rebase policy. Prefer a merge for a shared branch;
rebase only with authorization and an appropriate repository policy. Resolve
conflicts where intent is clear, ask for missing intent when it is not, and
run checks appropriate to the affected code. Report the resulting branch and
validation outcome. Do not publish or force-push merely because a local update
was requested. Do not run the former overlay/worktree refresh commands.
