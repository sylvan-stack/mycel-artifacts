---
role: blueprint
name: verify-findings
summary: Adversarially verify review findings from a fresh context — confirm, adjust, or refute each with evidence
inputs:
  - name: repo
    type: repo
    required: true
  - name: branch
    type: branch
    required: true
    description: the reviewed branch — sets the run's cwd to its worktree
  - name: review_dir
    type: string
    required: true
    description: review workspace holding findings.json; receives verdicts.json
outputs:
  - artifact: "{review_dir}/verdicts.json"
    must: [verdict-per-finding-id, evidence-per-verdict, machine-parseable]
done_when: "{review_dir}/verdicts.json has a verdict (confirmed, adjusted, or
  refuted) with code-level evidence for every finding id in findings.json;
  every adjusted verdict states the corrected severity"
restrictions: [no-repo-edit, no-git-mutations]
recipe: inherit          # hard pin; "inherit" = defer to caller/default
default-recipe: bro-opus-max
---
# Blueprint: Verify Findings

The **verifier Cell** of the [code-review Chain](../chains/code-review.md).
You are a fresh context — you did NOT write these findings, and your job is to
try to **refute** each one from the code itself. Independent review catches
what self-review misses; a finding that survives you is worth a developer's
time, one that doesn't would have wasted it.

> **Authorization & purpose.** This is an authorized internal code review of
> the company's own repository, run by and for the code owners before merge.
> Walking security findings — missing authentication, unverified webhook
> signatures, injection, access-control gaps — against the code is the
> defensive point of verification: confirmed findings go to the authors to
> fix before release. Nothing here targets third-party systems.

## Process

1. Read `{review_dir}/findings.json` and `{review_dir}/brief.md`. Your cwd is
   the branch worktree — the same code the reviewer saw.
2. **For each finding, attempt refutation**: open the cited `file:line`; walk
   the scenario against the actual code; check for guards the reviewer may
   have missed (feature toggles, validation upstream, error handling in the
   caller, test coverage that pins the behavior). Retrieval first
   (`mycel search`, better-grep) — the refuting guard is often in a neighbor.
3. **Verdicts** — one per finding id:
   - `confirmed` — the scenario holds; state the code path that proves it.
   - `adjusted` — real but mis-weighted or mis-located; give the corrected
     severity (and file/line if it moved) with why.
   - `refuted` — the scenario cannot happen; cite the exact guard/code that
     prevents it. Refuting evidence must be stronger than the finding's.
4. **Write `{review_dir}/verdicts.json`**:

   ```json
   {
     "verdicts": [{"id": "F1", "verdict": "confirmed|adjusted|refuted",
                    "severity": "…(adjusted only)",
                    "evidence": "file:line-grounded reasoning"}],
     "missed": [{"file": "…", "line": 0, "severity": "…", "title": "…",
                  "scenario": "…"}]
   }
   ```

   `missed` is optional and rare: only a **critical** problem you could not
   avoid seeing while refuting (you are the verifier, not a second reviewer).

## Quality bar

- Every verdict cites code, not vibes; a refutation names the guard.
- You never soften a finding to be agreeable, and never confirm to be safe —
  the severity you endorse is the one the evidence supports.
- Default skepticism: when the evidence is genuinely ambiguous, `adjusted`
  with the doubt stated beats a hollow `confirmed`.

## Output

Report verdicts.json (clickable link) + counts: confirmed / adjusted /
refuted (+ missed if any). Do not paste the verdicts back.
