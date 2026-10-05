---
role: blueprint
name: spike-doc
summary: Spike ticket workspace → spike document (findings, options, open questions)
inputs:
  - name: ticket
    type: string
    required: true
    description: the spike/RND ticket
  - name: repo
    type: repo
    required: true
    description: primary repo; spikes often span several repos — say so
  - name: ticket_dir
    type: string
    required: true
    description: workspace folder from a chain; its docs ARE the brief. Missing
      or empty → stop with an error (the chain builds it before calling you)
outputs:
  - artifact: "{ticket_dir}/spike.md"
    must: [source-refs-resolve, behavior-vs-requirement-explicit, open-questions-listed]
done_when: "{ticket_dir}/spike.md exists, current behavior is verified against
  the BRD/requirement with code evidence, options carry trade-offs, and open
  questions are routed (who answers what)"
restrictions: [no-repo-edit, no-git-mutations]
recipe: inherit          # hard pin; "inherit" = defer to caller/default
default-recipe: bro-opus-max
---
# Blueprint: Spike Document

## Goal

Turn a spike ticket into a decision-ready document: what the system does
TODAY (verified, not assumed), what the requirement asks, the gap, the
options, and the questions only humans can answer.

## Process

1. **Read the brief.** `{ticket_dir}` IS your brief — read `objectives.md`,
   `ticket.md`, `jira-context.md` (the BRD/requirement constraints),
   `code-scout.md`, and `research.md`. If `ticket_dir` is missing, empty, or
   lacks these docs, **stop with an error** — the chain builds the workspace
   (BRD closure included) before calling you; do not fetch or research from
   scratch to paper over a missing brief. Build ON the existing research; do
   NOT re-derive what the workspace already establishes.
2. **Current-behavior research** per requirement area, cross-repo where the
   flow spans several repos, with the level-3 loop
   ([code-research](../operations/code-research.md)): every behavior claim
   backed by code evidence with path + lines. This is only what `research.md`
   did not already cover.
3. **Write the spike doc** to `{ticket_dir}/spike.md` (the proven DEMO-101
   shape) per the
   [authoring guide](../operations/source-refs-authoring.md), splitting
   into companions when large (`{ticket_dir}/spike-research-findings.md`,
   `spike-open-questions.md`, `spike-code-map.md`):
   - **current behavior vs requirement matrix** (the load-bearing section);
   - affected components across repos, each with a
     [Source Ref](../../arbol/GLOSSARY.md#source-ref);
   - options with trade-offs and rough effort;
   - open questions with proposed owners/routing.
4. **Update, don't duplicate.** Updating an existing `spike.md` beats writing a
   sibling — repair drift, keep the corpus curated. Glossary candidates
   surfaced by the spike (jargon the code never spells out) go to the repo
   GLOSSARY per the [embedding habits](../operations/embedding.md).

## Quality bar

- "The system currently does X" is never written without evidence.
- The requirement's ambiguities become routed questions, not assumptions.
- A stakeholder could pick an option from this doc alone.
- The spike built on the workspace's research rather than duplicating it.

## Output

Your final message must report the artifact you wrote — a clickable markdown
link to `{ticket_dir}/spike.md` (absolute path), plus the 2–3 findings that
most shape the decision (the biggest behavior-vs-requirement gap, the leading
option, the sharpest open question). Do not paste the file's contents back.
