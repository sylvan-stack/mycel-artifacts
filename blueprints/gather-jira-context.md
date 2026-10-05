---
role: blueprint
name: gather-jira-context
summary: Traverse the ticket's Jira/Confluence edges; curate objective-relevant context
inputs:
  - name: ticket
    type: string
    required: true
  - name: ticket_dir
    type: string
    required: true
outputs:
  - artifact: "{ticket_dir}/jira-context.md"
    must: [objective-relevant-only, per-item-provenance]
done_when: jira-context.md exists; every included item names its source
  (ticket key / page id / comment author+date) with a mirror Source Ref;
  every EXCLUDED edge is listed one-line with the reason; nothing was
  included that does not serve the objectives
restrictions: [no-repo-edit, no-git-mutations]
recipe: inherit          # hard pin; "inherit" = defer to caller/default
default-recipe: bro-opus-medium
---
# Blueprint: Gather Jira Context

## Goal

Everything from the Jira/Confluence graph that MATTERS for this ticket's
objectives — and nothing else. There is no traversal algorithm: you judge
each linked item on relevance, one at a time.

## Process

1. **Read the objectives first** — `{ticket_dir}/objectives.md` is your relevance filter —
   then `{ticket_dir}/ticket.md` and the raw mirror
   (`~/Artifacts/mirrors/jira/{ticket}.md`, including its comments section
   and `linked_issues`/`confluence_links` frontmatter).
2. **Traverse edges with judgment**, fetching what you decide to inspect:
   `mycel mirror fetch jira <KEY>` for linked/parent/sub tickets,
   `mycel mirror fetch confluence <url>` for linked pages. Inspect the
   fetched mirror, then DECIDE: include (summarize the relevant part) or
   exclude (one line + reason). Follow further hops only when an inspected
   item points somewhere the objectives care about.
3. **Comments are context too:** extract decisions, constraints, and
   contradictions from the comment section — attribute each (author, date).
   Fetched Jira mirrors download image attachments automatically (their
   `## Attachments` section lists local paths) — VIEW the ones the
   objectives suggest matter; screenshots often decide include/exclude.
4. **Write `jira-context.md`** — to `{ticket_dir}/jira-context.md`:
   - **Included context**, grouped by source, each with a mirror Source Ref;
   - **Contradictions/updates** — where a comment or page supersedes the
     ticket body, say so explicitly;
   - **Excluded edges** — the one-line-with-reason list (this is the honest
     record that traversal happened).

Do NOT raise open questions or flag ambiguities here — that is the job of the
future **Refine Ticket** chain, a deliberate separate pass. This Blueprint
only gathers and curates what the graph *does* say; interrogating what it
leaves unanswered is not part of ticket preparation.

## Quality bar

- Relevance beats completeness: a lean, objective-driven document — not a
  dump of everything reachable.
- Every claim is traceable to a mirror file; excluded ≠ silently skipped.
- No open-questions / gaps section — that belongs to Refine Ticket.

## Output

Your final message must report the file you wrote — a clickable markdown link `[jira-context.md](<absolute path to {ticket_dir}/jira-context.md>)`, plus a one-line count of edges included vs excluded. Do not paste the file's contents back.
