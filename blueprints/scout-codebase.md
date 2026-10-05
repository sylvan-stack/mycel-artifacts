---
role: blueprint
name: scout-codebase
summary: Cheap, fast surface scan — files/modules worth investigating + first insights
inputs:
  - name: ticket_dir
    type: string
    required: true
  - name: repo
    type: repo
    required: true
outputs:
  - artifact: "{ticket_dir}/code-scout.md"
    must: [paths-with-one-line-why, signals-not-conclusions]
done_when: code-scout.md exists listing the files/modules worth investigating
  (each with a one-line why), plus first insights and hunches clearly marked
  as unverified — produced fast, wide, and shallow
restrictions: [no-repo-edit, no-git-mutations]
recipe: inherit          # hard pin; "inherit" = defer to caller/default
default-recipe: bro-opus-low
---
# Blueprint: Scout Codebase

## Goal

The reconnaissance pass — NOT deep research. Scan the surface with cheap,
fast signals (retrieval, better-grep, the corpus's mechanical
`~/Artifacts/{repo}/generated/code-map.md`) and hand later steps a map of
where to dig. Wide
and shallow beats narrow and deep here; do not verify, do not conclude.

## Process

1. **Read the brief** — `{ticket_dir}/objectives.md` and
   `{ticket_dir}/ticket.md`; scout FOR the objectives.
2. **Sweep, cheaply:** `mycel search` per objective vocabulary (the jargon
   glossaries bridge business words to code); `better-grep` for exact
   identifiers the ticket names; the repo's code map —
   `~/Artifacts/{repo}/generated/code-map.md` (in the Artifact Corpus, NOT
   inside the git repo) — for the module neighborhoods around every hit.
3. **Write `code-scout.md`** — to `{ticket_dir}/code-scout.md`:
   - **Where to dig** — files/modules, each with a one-line why (which
     objective it serves) and Source Refs;
   - **First insights & hunches** — clearly marked *unverified*;
   - **Surprises** — anything the ticket's framing did not predict (an
     unexpected extra implementation, an in-flight branch or MR for the
     ticket or its subtasks — check the mirror's `subtasks:` frontmatter and
     `mycel wt list`, it's the loudest surprise there is — a feature toggle,
     a test that contradicts the ask);
   - **Blind spots** — where the scan found nothing and deep research must
     look harder.

## Quality bar

- Fast and honest: signals, not conclusions; every hunch labeled as one.
- A deep-research run starting from this doc should waste zero time
  rediscovering where things live.

## Output

Your final message must report the file you wrote — a clickable markdown link `[code-scout.md](<absolute path to {ticket_dir}/code-scout.md>)`, plus the top 2–3 places to dig (each a clickable file link). Do not paste the file's contents back.
