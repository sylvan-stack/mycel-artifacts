---
role: authored
---
# Guide: External Mirrors

How knowledge from surfaces we do not control — **Jira tickets, Confluence
pages, GitLab merge requests** — becomes local, searchable corpus. Live since
2026-07-07 (design: [plans/external-mirrors](../../arbol_deprecated_v1/plans/external-mirrors.md)).

## The process

1. **Fetch on an event, never poll.** `mycel mirror fetch jira DEMO-10006
   [--closure]` / `fetch confluence <id-or-url>` / `fetch gitlab <mr-url>` —
   PATs read in-process from the Keychain (set via Seqoya → Secrets or
   `mycel secrets set`; write-only, no agent-readable surface). `--closure`
   follows a ticket's linked issues, **subtasks, parent**, and Confluence
   links one hop. Confluence
   `--depth N` mirrors a page's descendants too (bounded section fetch:
   depth AND `--max-pages`, default 100 — a section is fetched, never
   crawled). `mycel mirror tree confluence <space-key|page-ref>` writes the
   space's page tree (titles + links + hierarchy, NO content) to
   `mirrors/confluence/trees/` — metadata-only, so cheap at any space size;
   use it to *see* a space before deciding what deserves a real fetch.
2. **Write the mirror file**: `~/Artifacts/mirrors/<surface>/…md` —
   frontmatter carries remote metadata (`status`, `assignee`, `updated`,
   `fetched_at`, links, and for Jira `parent:` + `subtasks:`; the body's
   `## Subtasks` section adds each child's status and summary); body is
   description/comments/page-Markdown/diffs. **Read the frontmatter before
   acting on a ticket**: `status` In Development / In Code plus a non-empty
   `subtasks:` means implementation is already in flight — and branches are
   named by *subtask* key, so any prior-work search must use every key, not
   just the parent's (gates: [worktree-lifecycle](worktree-lifecycle.md#before-cutting-a-new-branch),
   the implementation-plan blueprint).
   Mirror class: fetched, never hand-edited, refresh = overwrite. For Jira the
   `.md` is only a **readable/indexed view**; the true raw is a companion
   `<KEY>.json` holding the **complete** API payload (`fields=*all` + expand:
   every field, changelog, rendered HTML) — the mirror loses nothing;
   extracting what matters is a downstream step's job. Its frontmatter points
   to the raw via `raw_json:`. **Image attachments download automatically**
   for Jira AND Confluence — to `mirrors/<surface>/<ref>/` (≤15 MB each;
   idempotent — an existing file with the expected size is not re-fetched;
   Jira attachments are immutable, Confluence ones re-download on size
   change) and are listed in the `.md`'s `## Attachments` section plus
   `images:` frontmatter — agents READ them (screenshots pinpoint what prose
   only hints at). Non-image attachments stay metadata-only.
3. **Ingest + embed** as the `<surface>-mirror` corpus namespaces —
   `profile = local` mandatory: company text never reaches an external
   embedder. When Arbol runs, its mycel client's watcher (`daemons/mycel_client/`
   — Arbol-owned; Mycel itself has no daemon) picks the new file up within
   seconds; otherwise the next `mycel search` folds it in (fresh-on-read).
4. **Retrieve**: `mycel search "…" --repo jira-mirror` (or
   `confluence-mirror` / `gitlab-mirror`). Curated derivatives belong in the
   processed layer (`~/Artifacts/jira/…`, authored class) and ref their
   mirror files — [Detection](../../arbol/GLOSSARY.md#detection) then flags the
   derived doc when a refresh changes the ticket underneath it.

`mycel mirror refresh [surface] [--older-than-min N]` re-fetches stale
mirrors by their `fetched_at` stamps.

## Boundaries that keep it sane

- **Mycel mirrors the world — and, for now, acts on it.** Surface writes
  live in Mycel until Arbol integrations own them: `mycel jira
  create|update|comment|transition` and `mycel confluence create|update`.
  GitLab writes remain out of scope. What keeps writes honest: every write
  re-fetches the target's mirror — Confluence always, Jira when the ticket
  is already mirrored — so the one-way mirror flow stays true.
- One bounded diffs page per MR (20 files; `changes_count` in frontmatter is
  the honest total) — the endpoint streams unbounded on big MRs.
- Scope discipline: fetch what an event names plus its closure — never crawl.

<!-- sources:
mycel:mycel/mirror.py
mycel:mycel/confluence_write.py
mycel:mycel/jira_actions.py
mycel:mycel/secrets_store.py
-->
