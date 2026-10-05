> Deprecated (2026-09-16): use a standard Git checkout directly in the repository folder. Do not create nested worktree folders. The content below is historical, not current operating instructions.

---
role: authored
---
# Guide: Branch Context (worktrees + overlays)

This guide gives any branch —
a task in progress or an MR under review — a searchable context: **the repo as
that branch sees it**. Frontend-agnostic: the Arbol app drives it via RPCs,
CLI agents via the [Mycel runbook](../tools/mycel.md); the process below
is the invariant.

## The process

1. **A worktree exists** for the branch inside the repo's
   [Worktree Container](../../arbol_deprecated_v1/GLOSSARY.md#worktree-container)
   (`~/repo/<repo>/<branch>/`). However it was created — `mycel wt add`
   (daemon-less; owns git worktree + overlay + Env-Keeper seeding + `--mr`
   fetch + `open`), raw git, or the IDE — the system's invariant is:
   *worktree in a container ⇔ its
   [Branch Overlay](../../arbol_deprecated_v1/GLOSSARY.md#branch-overlay) exists*. The Sync Pass
   auto-registers discovered worktrees and auto-drops overlays whose worktree
   vanished.
2. **Overlay ingest**: the branch's delta vs the local `master` merge-base
   (uncommitted and untracked files included) chunks into the namespace
   `<repo>@<branch>`; deleted files become tombstones. Files reverted to
   master drop out automatically on the next re-diff.
3. **Embed — on demand only**: overlay chunks stay *pending* until explicitly
   embedded (`mycel embed --overlay <repo>@<branch>`, `mycel overlay
   add|refresh --embed`, or the Elma status bar's "Embed N chunks" button).
   Automatic passes never embed overlays — a pathological diff (dirty worktree,
   stale base) would otherwise silently burn hours of embedding compute. When
   embedded, overlay chunks use the **base repo's**
   [Embedder Profile](../../arbol_deprecated_v1/GLOSSARY.md#embedder-profile) — the
   base-repo interlock is inherited, never
   re-decided. Un-embedded overlay chunks still serve BM25/exact search; only
   dense (semantic) recall needs the embed.
4. **Scoped retrieval**: searches from inside the worktree see base-minus-
   shadowed-paths plus the overlay (shadowing by path); overlay hits are
   marked, and changed chunks surface their `documented_in` reverse edges —
   for an MR, that reads as "this MR drifts N research/glossary docs".

<!-- sources:
mycel:mycel/knowledge/store.py#ingest_overlay
mycel:mycel/knowledge/embedder.py#_overlay_scope
-->

## Before cutting a new branch

Creating a new-branch worktree asserts "no code exists for this ticket yet"
— verify that first: `mycel wt list` (local worktrees ARE the registry of
in-flight work), then remote refs matched against the ticket key **and every
subtask key** from the ticket mirror's `subtasks:` frontmatter — branches
are named by subtask key (`sub/DEMO-<SUBTASK>-…`), so a parent-key search
proves nothing. One `git -C <container>/.bare for-each-ref
refs/remotes/origin | grep -iE '<KEY>|<SUBTASK-KEYS>'` costs seconds;
duplicating a pushed implementation costs a day. A hit → attach to the
existing branch (`mycel wt add`) instead of cutting a new one.

## Dev-experience model

One VS Code window per worktree — matching Mycel's CWD scoping (`mycel wt
open <fragment>` fuzzy-opens; ⌘R recalls each worktree's window state). Avoid
multi-root workspaces mixing worktrees: search duplicates across copies.

`.bare` is the container's **single shared git object store** — a bare
repository holding all commits/branches/refs once. Each worktree's `.git` is a
small FILE pointing into `.bare/worktrees/<name>` (per-worktree HEAD + index);
one fetch updates every worktree, N worktrees cost ~one history. Plumbing —
never work inside it.

## The master worktree

The corpus worktree (`master/`, or `main/` for personal repos like Arbol) is permanent and is the repo's Code Corpus source: fetch + hard
reset each Sync Pass, **dirty guard** included — local edits there freeze
corpus refresh with a loud warning rather than being destroyed. Never work in
`master/`.

<!-- sources:
mycel:mycel/syncpass.py#refresh_mirror
-->

## Keeping a branch current (update with master)

From the branch's worktree: `git fetch origin master` then **merge**
(`git merge origin/master`) — the safe default for branches others may have
pulled; rebase (`git rebase origin/master` + force-push) only when the branch
is exclusively yours and team policy allows. *(Merge-first is an assumption —
correct it here if the team convention differs.)* Afterwards the overlay
re-diffs automatically on the next Sync Pass, or immediately via
`mycel wt refresh <repo> <branch>` — the merge-base moved, so the overlay
shrinks to the true remaining delta. Conflicts are yours to resolve; nothing
automated touches a conflicted tree.

## Lifecycle end

The Sync Pass marks overlays whose branch is merged into master; they show as
"merged — droppable" (Repos page, `wt list`). Dropping removes overlay rows
and the worktree together; overlays are ephemeral by design — recreatable in
minutes, never referenced by edges, exempt from
[Detection](../../arbol_deprecated_v1/GLOSSARY.md#detection)/[RAPTOR](../../arbol_deprecated_v1/GLOSSARY.md#raptor-tree)
(a *proposed future*, the mirror-image of
[Heartwood](../../arbol_deprecated_v1/GLOSSARY.md#heartwood)).
