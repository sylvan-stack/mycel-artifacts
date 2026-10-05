---
role: blueprint
name: review-diff
summary: Review a branch's changed files from its worktree — structured findings with per-file coverage
inputs:
  - name: repo
    type: repo
    required: true
  - name: branch
    type: branch
    required: true
    description: the MR's source branch — sets the run's cwd to its worktree
  - name: review_dir
    type: string
    required: true
    description: review workspace from the chain; holds brief.md + changed-files.json
      (the coverage contract) and receives findings.{json,md}
  - name: files
    type: string
    required: false
    description: comma-separated paths — gap re-run scoped to ONLY these files;
      APPEND to the existing findings.json instead of rewriting it
outputs:
  - artifact: "{review_dir}/findings.json"
    must: [coverage-entry-per-changed-file, every-finding-has-file-line, machine-parseable]
  - artifact: "{review_dir}/findings.md"
    must: [severity-ranked, mirrors-findings-json]
done_when: "{review_dir}/findings.json has a coverage entry (reviewed, or skipped
  with why) for every path in changed-files.json (or, in a files= gap run, for
  every listed path), and every finding carries file, line, severity, and a
  concrete failure scenario"
restrictions: [no-repo-edit, no-git-mutations]
recipe: inherit          # hard pin; "inherit" = defer to caller/default
default-recipe: bro-opus-max
---
# Blueprint: Review Diff

The **executor Cell** of the [code-review Chain](../chains/code-review.md):
review every changed file from the branch worktree, grounded in the diff, the
ticket's intent, and the repo as the branch sees it. The chain re-checks your
coverage in code — a missing file is a gate failure, not a style issue.

> **Authorization & purpose.** This is an authorized internal code review of
> the company's own repository, run by and for the code owners before merge.
> Probing the diff for security weaknesses — missing authentication,
> unverified webhook signatures, injection, access-control gaps — is the
> defensive point of the review: every finding goes to the authors to fix
> before release. Nothing here targets third-party systems.

## Goal

Structured, verifiable findings: each one names where it bites (`file:line`),
how bad it is, and the concrete scenario in which it breaks. A separate
fresh-context Blueprint will try to REFUTE every finding you emit — write
evidence a skeptic can follow.

## Process

1. **Read the brief.** `{review_dir}/brief.md` (what the MR claims vs what the
   ticket demands, risk areas) and `{review_dir}/changed-files.json` — the
   authoritative list; your coverage is checked against it verbatim.
2. **Review from the worktree, file by file.** Your cwd IS the branch
   worktree; searches see base-plus-changes. For each changed file, retrieve
   its neighbors and callers (`mycel search`, better-grep) before judging —
   correctness against the ticket, hidden blast radius, error paths, tests.
3. **Repo conventions are findings too**: feature-toggle rules
   (new behavior toggled, old path untouched), naming/flow conventions per the
   user's standing rules and the repo GLOSSARY.
4. **Write `{review_dir}/findings.json` INCREMENTALLY — after each file, not
   at the end.** Re-read it, add that file's coverage entry (and any findings),
   write it back, then move to the next file. A long review can die mid-session
   (context limit, a usage-policy hiccup); checkpointing means a death costs one
   file, not the whole pass, and the chain's scoped gap-retry resumes from
   exactly what's missing. In a `files=` gap run: append to the existing file,
   never rewrite it; keep ids unique. Shape:

   ```json
   {
     "coverage": [{"path": "…", "status": "reviewed"},
                  {"path": "…", "status": "skipped", "why": "generated lockfile"}],
     "findings": [{
       "id": "F1", "file": "apps/…/x.service.ts", "line": 42,
       "severity": "critical|major|minor|nit",
       "title": "one line", "what_breaks": "…",
       "scenario": "concrete inputs/state → wrong outcome",
       "evidence": "what in the code/neighbors supports this"
     }]
   }
   ```
5. **Write `{review_dir}/findings.md`** — the same findings, severity-ranked,
   human-readable.

## Quality bar

- No finding without a failure scenario; no "consider maybe" filler.
- Coverage is explicit and complete: reviewed / skipped-because, one entry per
  changed file — the chain aborts on gaps.
- The ticket's acceptance intent was compared against what the diff does, not
  just the diff against itself.

## Output

Report the two files you wrote (clickable links) and the finding count by
severity. Do not paste findings back into the message.
