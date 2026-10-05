---
role: blueprint
name: format-ticket
summary: Raw Jira mirror → clean processed ticket.md in the ticket workspace
inputs:
  - name: ticket
    type: string
    required: true
  - name: ticket_dir
    type: string
    required: true
    description: the workspace folder (created by the calling chain)
outputs:
  - artifact: "{ticket_dir}/ticket.md"
    must: [mirror-source-ref, clean-statement]
done_when: ticket.md exists in the workspace with frontmatter (key, url,
  status, updated) + a Source Ref to the mirror, a clean problem statement,
  and explicit scope/out-of-scope — no raw Jira noise carried over
restrictions: [no-repo-edit, no-git-mutations]
recipe: inherit          # hard pin; "inherit" = defer to caller/default
default-recipe: bro-haiku-medium
---
# Blueprint: Format Ticket

## Goal

Turn the raw mirror (`~/Artifacts/mirrors/jira/{ticket}.md` — Jira markup,
image tags, boilerplate) into a clean, readable ticket document a human or
agent can absorb in one pass.

## Process

1. **Read the mirror.** If it is missing, state so and stop (the chain
   fetches before calling you).
2. **READ every image in the mirror's `## Attachments` section** (local
   paths under `~/Artifacts/mirrors/jira/{ticket}/` — the Read tool renders
   them). Screenshots often pinpoint what prose only hints at: the exact
   file/line, an error message, a design. Fold what each image SHOWS into
   the Statement, attributed ("screenshot-1.png shows …"). Attachments the
   mirror did not download (non-images) stay described as "[attachment: …]".
3. **Write the ticket doc** — `{ticket_dir}/ticket.md`:
   - frontmatter: `key`, `url`, `status`, `assignee`, `updated` (from the
     mirror), and a Source Refs comment citing `jira-mirror:{ticket}.md`;
   - **Statement** — what is asked and why, in clean prose (translate Jira
     markup; image insights folded in per step 2);
   - **Attachments** — carry the mirror's list over with local paths, so
     later steps (objectives, scout, research) can view the images too;
   - **Scope / Out of scope** — explicit, inferred conservatively from the
     ticket text; mark inferences as such.
4. **Stay in scope.** Do not editorialize beyond the ticket's content —
   objectives and context are later steps' jobs.

## Quality bar

- Someone who never opened Jira understands the ask.
- Nothing from the raw description is silently lost; unclear fragments are
  quoted and marked unclear rather than paraphrased into false confidence.
- Every downloaded image was actually viewed — an Attachments list without
  folded-in insights means the step was skipped, not done.

## Output

Your final message must report the ticket workspace file you wrote — a clickable markdown link `[ticket.md](<absolute path to {ticket_dir}/ticket.md>)` and one line on what it captures. Do not paste the file's contents back.
