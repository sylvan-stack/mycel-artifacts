---
role: authored
---
# Guide: Code Research (level 3)

In-session research for **question-shaped** requests — "how does X work",
"where is Y decided", "what happens when Z" — needing synthesis across files.
Deliverable: an **answer in chat with `file:line` citations**, minutes not
tens of minutes. (Exact-string lookups are level 1/2; producing a research
artifact as the goal is level 4 — see
[code-research-levels](code-research-levels.md).)

## The loop

1. **Mycel first — never start with grep or file reading.**
   ```bash
   mycel search --repo <repo> "<the question, as asked>"
   ```
   Run 2–3 phrasings if the first is thin. Note the annotations:
   - `via <doc>` — a glossary/research section pointed here; **read that doc
     section before the code** (it's a prior investigation of your question).
   - `documented_in` — same, reverse direction.
   - `⚠ stale` — the doc's claim may be outdated: trust the code, and treat the
     doc as a map of *where* to look, not *what is true*.
   - `heartwood` — describes a past state; useful for "how did this work
     before", misleading for "how does this work now".

2. **Read surfaced documents** (`~/Artifacts/<repo>/…`) before opening any
   code file. They carry the why and cite the exact symbols. For structural
   orientation ("what exists in this domain"), the auto-generated
   `generated/code-map.md` lists every directory's files and symbols — code
   hits also point back to their map section via `documented_in`.

3. **Targeted code reading** into the gaps only — follow the `path#symbol
   Lstart-end` spans from search results; `better-grep` for the enumeration
   questions that come up along the way (call sites, usages).

4. **Answer with citations**: every claim carries `path:line`. Distinguish
   *verified in code* from *taken from a doc* (and flag if that doc was stale).

5. **Persist if it earned it.** If the synthesis was expensive and reusable —
   you read 5+ files, reconciled a doc with reality, or answered something
   likely to recur — write/update the research doc: ticket-bound work goes to
   `~/Artifacts/<repo>/tickets/<KEY>/research.md`; repo-level reusable topics
   go to `~/Artifacts/<repo>/research/<topic>.md`. Never the corpus root.
   per the [Source Refs authoring guide](source-refs-authoring.md)
   (frontmatter governors, per-section `<!-- sources: -->`). Updating an
   existing stale research doc is worth more than writing a new one: it repairs
   a Drift and keeps the corpus curated. A quick one-file answer does NOT need
   persisting — don't litter the corpus.

## Rules of thumb

- A `via …/research/…` hit means someone already did (part of) this research —
  reading it is cheaper than redoing it. That's the point of the corpus.
- Mirrors (`~/.arbol/mirrors/<repo>`) hold what Mycel indexed: clean master.
  If your question is about a feature branch, say so in the answer — Mycel
  reflects master, your working copy may differ.
- If retrieval returns nothing sensible across 3 phrasings, fall back to
  level-1/2 exploration — and if the eventual answer was findable only by
  grep, consider a glossary entry for the missing vocabulary
  (`~/Artifacts/<repo>/GLOSSARY.md`): next time it's a bridge.
