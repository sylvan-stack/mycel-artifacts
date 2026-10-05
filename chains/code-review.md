---
role: authored
---
# Runbook: code-review (Blueprint Chain)

## Why it exists

The **rigorous, detached** review of an MR — what the manual
[code-review Blueprint](../blueprints/code-review.md) instructs, this chain
**guarantees**: a coverage gate checked in code against the real merge-base
diff (not the reviewer's self-report), and an adversarial verification pass in
a **fresh [Chat Session](../../arbol_deprecated_v1/GLOSSARY.md#chat-session)** — the verifier
is never the context that produced the findings, so plausible-but-wrong
findings die before they reach a developer. The manual Blueprint stays the
interactive path (review-with-dialogue in the current session); this chain is
what "review MR X and tell me when it's done" runs.

**Errors are never hidden.** Any Cell whose agent session refuses, hits a rate
limit, or errors stops the chain at once and surfaces the provider's message —
no silent model-swap, no swallowed result. Re-run to resume from the failed
Cell once the cause is cleared (a different `--recipe`, a wait, an authorization
note).

## Use

```
python3 ~/Artifacts/mycel/chains/code-review.py <MR-URL>
        [--until N]     # stop after Cell N — the run stays RESUMABLE
        [--fresh]       # ignore any unfinished run for this MR; start over
        [--dry-run]     # print the Cell plan + resume state, run nothing
        [--recipe NAME|model:thinking]  # Brain Recipe for ALL Cells (caller-only:
                        # user-named; ad-hoc descriptor e.g. fable:xhigh)
```

Branch-without-MR reviews stay on the manual Blueprint (nothing to mirror or
diff against a target). Live view: `tail -f ~/.infer/chains/<run-id>/chain.jsonl`.
**Resume is automatic**: the run key is MR-derived, so re-running the same MR
after an abort resumes at the failed Cell (completed Cells keep their outputs);
`--fresh` starts over. Every agent Cell runs on `bro-opus-max` by default;
`--recipe fable:max` (or any `[ip:]model:thinking` descriptor) overrides.

## Workspace

`~/Artifacts/<repo>/tickets/<KEY>/review/mr-<iid>/`
(`~/Artifacts/<repo>/reviews/mr<iid>/` when no ticket key is found in the
branch/title):

```
brief.md            what the MR claims vs what the ticket demands; risk areas
changed-files.json  the COVERAGE CONTRACT — name-status of the merge-base diff
findings.json/.md   the executor's structured findings + per-file coverage
verdicts.json       the verifier's per-finding verdicts with evidence
review.md           the code-assembled, machine-faithful record
```

**The deliverable** lands in the **ticket workspace**:
`~/Artifacts/jira/<KEY>-<slug>/code-review-<datetime>.md` (an existing
workspace is reused whatever its slug; created when absent; falls back to the
review workspace when the MR has no ticket). Its rules: numbered points
most-important-first; **[BLOCKING]** markers on points that must be fixed
before merge; every point carries a clickable `file:line` link into the
branch worktree, a plain-words summary, and code evidence; free-form extras
(test gaps, rollout notes, good changes worth keeping) after the points.

## Cells

Eight [Cells](../../arbol_deprecated_v1/GLOSSARY.md#cell); `--until N` stops after Cell N.

1. **MR mirror** — *Tool* `mycel mirror fetch gitlab <url>`. The chain then
   parses repo / source & target branch / ticket key from the mirror
   frontmatter and makes the workspace. Gate: exit 0.
2. **Ticket closure** — *Tool* `mycel mirror fetch jira <KEY> --closure`
   (the intent the diff answers to). **Skipped** when no ticket key exists —
   the review proceeds against diff + conventions only, and says so.
3. **Worktree + coverage contract** — *Tool* `mycel wt add <repo> <branch>`
   (the chain first ensures the local branch ref — deterministic git fetch).
   The chain then **fetches `origin/<target>`** (a stale target ref would sweep
   weeks of master into the diff — it did on the first live run: 4661 files for
   a 32-file MR) and computes `changed-files.json` from the **merge-base diff in
   the worktree**. Gates: non-empty diff, and a **sanity gate** aborting when
   the contract grossly exceeds the mirror's `changes_count` (a wrong base).
4. **Brief** — *lambda*. MR mirror + ticket mirror → `brief.md`: claim vs
   intent vs risk areas, under a page. Runs on the cheap lambda recipe.
5. **review-diff** — *Blueprint* (executor). Reviews file-by-file from the
   worktree, checkpointing `findings.json` after each file. A **session error**
   (usage-policy refusal, rate limit, model error) **aborts the chain
   immediately** with the provider's own message — errors are never hidden or
   retried. A clean-but-incomplete pass (a few files still uncovered) is
   tolerated: its partial findings flow into the coverage gate and the scoped
   retry. Gate: the coverage gate in code — every changed file has an entry.
6. **review-diff gap retry** — *Blueprint, conditional*: runs when Cell 5 left
   HONEST coverage gaps (it completed cleanly but skipped some files), scoped to
   exactly those files (`files=` input, appends). A second gap **aborts** —
   coverage is a guarantee. (A refused/rate-limited Cell 5 never reaches here —
   it already aborted.)
7. **verify-findings** — *Blueprint* (adversarial verifier, fresh context).
   Tries to refute every finding from the code; verdicts with evidence →
   `verdicts.json`. Gate: `done_when` **plus the verification gate in code** —
   every finding id has a verdict. Pure code then assembles `review.md`:
   confirmed + adjusted findings severity-ranked (adjusted severities win),
   the coverage table, refuted findings under *dismissed by verification*.
8. **publish** — *lambda*. review.md + the finding/verdict evidence → the
   **deliverable** `{ticket_dir}/code-review-<datetime>.md` per the rules
   above (most-important-first, [BLOCKING] markers, clickable `file:line`
   links, evidence per point, free-form extras). Gate: **the file exists** —
   checked in code.

`finish()` renders the links + recipes.

## Recipes

`PIN_RECIPE = "inherit"`, `DEFAULT_RECIPE = "bro-opus-max"` — every Cell
(reviewer, verifier, brief, publish) runs on the strong recipe unless the user
names another via `--recipe` (caller-only — a triggering session's model never
inherits). `--recipe` also takes an ad-hoc `model:thinking` descriptor —
"with Fable xhigh" = `--recipe fable:xhigh` — with no config change
([infer runbook](../tools/infer.md)). A blueprint's OWN frontmatter pin would
still win over the chain, per the two-level recipe law.

## Degraded mode (the VS Code Test)

`--dry-run` prints exactly what by-hand means. Each Cell is independently
drivable: fetch the mirrors with `mycel mirror fetch`, `mycel wt add` the
branch, run `blueprint run review-diff --input …` / `verify-findings` yourself,
and check the two gates by eye (coverage vs `git diff --name-status`, verdict
ids vs finding ids). The manual code-review Blueprint remains the one-session
version of the same process.

<!-- sources:
mycel:mycel/cli.py
-->
