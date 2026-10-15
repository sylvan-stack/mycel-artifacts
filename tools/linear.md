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
