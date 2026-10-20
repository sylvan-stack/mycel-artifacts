---
role: authored
---
# Runbook: Linear Navigation

This runbook covers the connector and UI mechanics used by
[Organize Linear Navigation](../operations/linear-organize.md). The guide owns
scope, relevance, and authorization. These capabilities were checked on
8 October 2026; discover the current tools and read their schemas before use.

## Connector capabilities

The connected Linear tools can inspect project evidence and maintain
documents. Their current surface has no tools for reading or changing
personal favorites, favorite folders, sidebar ordering or visibility, or
saved custom views. Read and mutate those through the observed Linear UI.
If a future connector provides these capabilities, prefer its supported tools.

| Need | Current tool family and useful fields |
|---|---|
| Confirm workspace and owner | `get_workspace`, `get_user` with `query: "me"` |
| Inventory projects | `list_projects`: status, description/summary, URL, labels, lead, teams; `includeArchived` when checking old entries |
| Read project details and resources | `get_project` with `includeResources: true` |
| Inventory documents | `list_documents`: content, URL, parent project/team/initiative, `archivedAt`; filter by scope where supported |
| Read a document | `get_document` |
| Read project work and owner actions | `list_issues`: status, project, labels, URL, description, assignee, priority, due date, completion/cancellation/archive fields; combine owner-assigned and project-scoped listings |
| Read current context | `get_status_updates`, `list_comments` on the relevant object |
| Locate existing question or decision records | `search` plus scoped listings and existing issue labels |
| Create or patch a navigation document | `save_document` |

What the connector cannot do, besides favorites, the sidebar and views
(seen 7 to 16 October 2026): delete a document or a project, edit team or
workspace settings, mark a comment thread resolved, list comments across the
workspace (comments are read per document, project or issue), and list or
create initiatives. Such a change needs the Linear desktop app through computer
use, and a deletion needs the owner's go-ahead each time. A thread is resolved
only when the owner asks for that thread, through the ⋯ menu of a reply,
"Resolve thread with comment". The desktop app may keep showing old text after
a connector save: verify content with `get_document`, not in the app.

One workspace is connected: **amorphius** (`https://linear.app/amorphius`),
through the claude.ai Linear connector, with the team **Sylvan Stack** (key
`SYL`) for all Sylvan Stack work. It was the Euro-Office workspace `eo-group`
until 20 October 2026, when the owner renamed it, the Sylvan Stack workspace
was imported into it with Linear's own "Linear to Linear import" (every SYL
identifier kept; documents and projects got new ids and slugs), and the
Euro-Office team, projects, documents and labels were removed at the owner's
request. The old workspace `linear.app/sylvan-stack` is left as it was and is
no longer written to. Both the MCP server `linear-sylvan` in `~/.claude.json`, re-authorized by
the owner for amorphius on 20 October 2026, and the claude.ai Linear connector
reach this workspace; either serves.

Follow each paginated list to completion for the selected scope. Current
`list_projects` has a maximum page size of 50; do not assume the larger limits
of other listings apply. A search's ranked top results are not a complete
inventory. Read tool errors as failures, even when transported in a successful
tool envelope.

`save_document` creation requires a title and exactly one parent: project,
issue, initiative, cycle, or team. Use the verified parent ID or unambiguous
identifier. Passing a parent during update moves the document; omit it when
preserving the parent. Prefer `patch` for focused updates. Derive anchors from
freshly read text and check that each is unique; do not replace an entire
mirrored document just to refresh an index section.

## Computer use

Use the host's supported computer-use interface and its returned
documentation. Find or open the relevant Linear app or browser, then inspect
the workspace, account, sidebar, and actual controls. In Codex the available
interface is `cua_repl`; another provider may expose a different interface.
Do not hardcode selectors, coordinates, hidden endpoints, or UI state from a
previous run.

### Favorites and folders

Favorites are personal shortcuts; documents, projects, issues, and saved views
are supported targets. Inspect the header star or command menu to add one.
The sidebar's hover removal control removes the shortcut. The Favorites
heading or star menu offers folder creation, and existing favorites can be
dragged into or out of a folder. Inspect folder rename/removal controls before
using them, and reread after a drag to verify its effect.
[Linear Favorites documentation](https://linear.app/docs/favorites).

### Other sidebar entries

Sidebar customization is available through an item's context menu or
**Customize sidebar**. Supported entries can be reordered and infrequently
used entries hidden under **More**. Apply this only to entries whose purpose
and requested scope are understood.
[Linear's sidebar customization announcement](https://linear.app/changelog/2024-12-18-personalized-sidebar).

### Custom views

Saved views collect issues, projects, or initiatives through filters. Create
one from **Views** after selecting the entity type, or save an already
filtered list/board. Inspect the view-name menu to edit it. Favorite a useful
view for sidebar access. Verify scope, filters, and visibility from the live
UI; initiative views depend on the workspace plan. A view cannot aggregate
arbitrary document sections, so use a linked navigation document for those.
[Linear Custom Views documentation](https://linear.app/docs/custom-views).

### Project resources and tabs

Project documents and links are resources on the overview, while attached
issue views appear as project tabs. Tabs can be repositioned and favorited.
These shared project surfaces differ from personal favorites; modifying them
must fit the requested scope. Creating a document does not itself place a
shortcut in the owner's sidebar: open the returned target and favorite it.
[Linear Projects documentation](https://linear.app/docs/projects).
