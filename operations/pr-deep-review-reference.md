---
role: authored
---
# Deep Pull-Request Review — Reference

Lookup companion to the [deep review guide](pr-deep-review.md). Consult the
section you need; the guide holds the process.

## state.json

One file per pull request, at `<artifact_root>/reviews/pr-<number>/state.json`.

```json
{
  "schema": 1,
  "pr": {
    "url": "https://<host>/<owner>/<repo>/pull/<number>",
    "repo": "<owner>/<repo>",
    "number": 0,
    "title": "",
    "author": "",
    "head_ref": "",
    "base_ref": ""
  },
  "reviewer": "<login of the human reviewer>",
  "tracker": { "system": "", "issue": "", "url": "" },
  "default_stint": "<name of a stint, or null>",
  "stop_criteria": [
    {
      "measure": "findings | time | tokens | coverage | dry-spell",
      "kind": "hard-max | soft-max | soft-min | hard-min",
      "value": 0,
      "severity": "critical | major | minor  (findings only; omit for critical and major together)",
      "scope": "run | total"
    }
  ],
  "head": {
    "reviewed_sha": "<head the state describes>",
    "base_sha": "",
    "observed_at": "<UTC timestamp>",
    "mergeable": "",
    "previous": [{ "sha": "", "last_observed_at": "<UTC timestamp>" }]
  },
  "deltas": [
    {
      "from": "<older head>",
      "to": "<newer head>",
      "observed_at": "<UTC timestamp>",
      "commits": 0,
      "rewritten": false,
      "status": "unscreened | screened",
      "screened_in_run": "<run id, or null>",
      "notes": ""
    }
  ],
  "pending_replies": [
    { "url": "", "author": "", "at": "<UTC timestamp>", "finding": "<F id, or null for a general comment>" }
  ],
  "areas": [
    {
      "id": "<kebab-case>",
      "rank": 1,
      "class": "authored | vendored | generated | build | tests",
      "above_cut_line": true,
      "status": "not-started | in-progress | exited | reopened",
      "reason": "<one line: why this rank>",
      "paths": ["<path or path prefix>"],
      "files": 0,
      "knowledge": ["<corpus-relative path>"],
      "exited_at_sha": null,
      "notes": ""
    }
  ],
  "findings": [
    {
      "id": "F1",
      "title": "",
      "area": "<area id>",
      "severity": "critical | major | minor",
      "severity_reason": "",
      "status": "<see Finding statuses>",
      "evidence": "reproduced | proved-from-source | none",
      "claim": "<one or two sentences: what breaks and for whom>",
      "location": { "path": "", "line": 0, "sha": "" },
      "card": {
        "how_shown": "<one sentence>",
        "draft_comment": "<text for the reviewer to post, or null once posted>",
        "draft_reply": "<text for the reviewer to post on the thread, or null>"
      },
      "raised_by": "screening | commits | reply | fix | reviewer",
      "dossier": "<corpus-relative folder, or null>",
      "thread_url": "<comment on the pull request, or null>",
      "added_in_run": "<run id, or null when seeded from earlier work>",
      "reviewer_decision": "<what the reviewer wrote on the card, or null>",
      "history": [{ "at": "<UTC date>", "sha": "", "status": "", "note": "" }]
    }
  ],
  "runs": [
    {
      "id": "<date>-<nn>",
      "command": "next | commits | verify | replies | check | summary | seed",
      "report": "runs/<date>-<nn>.md",
      "started_at": "<UTC timestamp>",
      "ended_at": "<UTC timestamp>",
      "head": "",
      "stint": "<name of the stint the run used, or null>",
      "criteria": ["<the limits as resolved for this run, same shape as stop_criteria>"],
      "spent": { "minutes": 0, "tokens": 0, "token_counter": "<which counter>" },
      "queued": { "critical": 0, "major": 0, "minor": 0 },
      "areas_exited": 0,
      "ended_by": "<complete | the criterion that ended the run | user decision needed>",
      "summary": ""
    }
  ]
}
```

Rules:

- `findings` holds every lead ever raised, including rejected ones, so
  nothing is investigated twice. IDs are never reused.
- `location` is the place at `location.sha`. Refresh it during sync.
- `history` is append-only. The current status is the top-level `status`.
- `head.reviewed_sha` changes only at the end of a sync.
- `claim`, `severity_reason`, `location` and `card` together are the
  finding's card. The reviewer's page is rendered from them, so they must be
  complete before a finding is set `queued`.
- `deltas` records every move of the head. A range stays `unscreened` until
  the *New commits* stage has reviewed it, whichever command fetched it.
- `pending_replies` holds replies that were fetched but not yet processed by
  the *Replies* stage; processing a reply removes it and adds a `history`
  entry to the finding.
- `default_stint` names the [stint](stints.md) this review uses when a
  request names none. `stop_criteria` holds standing limits that apply on top
  of it and may be empty. Each
  run records the criteria it applied and what it spent, so later criteria
  can be set from what earlier runs cost.

## Area statuses

| Status | Meaning |
|---|---|
| `not-started` | Ranked, nothing read yet |
| `in-progress` | Being investigated or screened |
| `exited` | A full screening pass at `exited_at_sha` found no new critical or major candidate |
| `reopened` | Was exited; a later change to the pull request touched it |

## Finding statuses

| Status | Meaning | Open? |
|---|---|---|
| `candidate` | Lead from screening or sync; not yet verified | yes |
| `investigating` | In the finding loop | yes |
| `suspected` | Could not be verified to the evidence bar; not for posting | yes |
| `rejected` | Disproved, or a duplicate; `history` says why | closed |
| `minor-noted` | Minor; one line, no dossier | closed |
| `queued` | Verified and challenged; its card is under *Ready to post* on the reviewer's page | yes |
| `posted` | Its comment is on the pull request | yes |
| `fix-claimed` | The author changed the code under it; not yet re-verified | yes |
| `fixed-verified` | Reproduction re-run at a newer head; the defect is gone | closed |
| `still-present` | Reproduction re-run at a newer head; the defect remains | yes |
| `regressed` | Was fixed; a later change brought it back | yes |
| `disputed` | The author disagreed, the objection was tested and the finding stands; a reply is drafted | yes |
| `author-declined` | The author will not change it and does not contest the facts; the reviewer decides | yes |
| `retracted` | Posted, then shown by the author not to be a defect; a conceding reply is drafted | closed |
| `accepted-wontfix` | The reviewer accepted the author's reason | closed |
| `dropped` | The reviewer decided not to post it | closed |

The agent moves a finding as far as `queued` and applies the sync statuses.
Only the reviewer's decision produces `accepted-wontfix` or `dropped`.

## Reviewer page

`README.md` in the workspace is the one file the reviewer opens. It is
rewritten from `state.json` when a run closes. Sections appear in this order;
a section with nothing in it keeps its heading and says “None.”

```markdown
# PR #<number> review — <pull-request title>

**Pull request:** [<repo>#<number>](<pr.url from state.json>)

**Head** `<short-sha>` · **Last run** [<run id>](runs/<run id>.md), ended by
<what ended it> · **Updated** <date>

<Two or three sentences: where the review stands and what the reviewer should
do next. Name any minimum the last run did not reach.>

## Your actions

| Finding | Severity | Action | New |
|---|---|---|---|
| [F<id> <title>](#f<id>) | <severity> | <action> | <● if added or changed in the last run> |

## Ready to post
## Reply on a thread
## Resolve the thread
## Waiting
## Not ready — do not post
## Coverage
## Runs
## Closed
## More
```

- **The first four sections hold cards**, most severe first, grouped by what
  the reviewer has to do:
  - *Ready to post* — new comments (`queued`) and the overall review comment
    when `summary` has drafted one.
  - *Reply on a thread* — a reply is drafted: `still-present`, `regressed`,
    `disputed`, `retracted`, `author-declined`, and answers to the author's
    questions.
  - *Resolve the thread* — `fixed-verified` findings whose thread is still
    open.
  - *Waiting* — nothing to do yet: `posted` without an answer, and
    `fix-claimed` not yet re-verified. It starts with one line for each kind
    of pending sync work: replies not yet processed, commit ranges not yet
    screened.
- **Not ready** has one line per finding that is `investigating`, `suspected`
  or `candidate`: ID, status, provisional severity, claim, location. This is
  where candidates beyond a findings maximum stay visible.
- **Coverage** is a table of the areas in rank order: status, findings raised
  there, and a link to the area's knowledge artifact.
- **Runs** is a table, newest first: run report link, time and tokens spent,
  findings queued, what ended the run.
- **Closed** has one line per closed finding with its outcome and a link to
  the dossier: `fixed-verified` after its thread was resolved, `rejected`
  with the reason, `dropped`, `accepted-wontfix`, `minor-noted`.
- **More** links `BRIEF.md`, `state.json` and the repository's reviews
  contract. For Linear-backed reviews, also link the readable artifact index
  and readable evidence sections; retain document/section IDs and source
  hashes in `linear-mirror.json` for incremental sync.

### Finding card

````markdown
<a id="f<id>"></a>
### F<id> · <severity> · <title>

- **Action:** <Post this comment | Post this reply | Decide: accept or insist | Resolve the thread | Nothing yet>
- **Attach to:** `<path>`:<line> at `<short-sha>`
- **Code context:** [marked excerpt](../pr-<number>-f<id>-<slug>/README.md#comment-location)
- **What breaks:** <who is affected and what they get>
- **How it was shown:** <reproduced | proved-from-source> — <one sentence>
- **Why this severity:** <one sentence>
- **Details:** [dossier](../pr-<number>-f<id>-<slug>/README.md) · [thread](<url, once posted>)
- **Added:** run <run id>
- **Your decision:**

**Comment location** (`>` marks the target line):

```text
<numbered, marked source excerpt copied from the dossier>
```

> <neutral comment: triggering input, observed result, impact; optional question about the case or intended behavior>
````

Include the inline code excerpt for **Ready to post** cards. Cards that only
reply to or resolve an existing thread may omit it.

*Your decision* belongs to the reviewer. Empty means no decision yet. `drop`
closes the finding without posting; `revise:` followed by a note asks for a
new draft. The next run reads the line during sync and keeps its text when
the page is rewritten. A posted comment needs no entry: sync finds it on the
pull request.

Add these lines when they apply, after *Why this severity*:

- **After the author's change:** what the re-run or the source read showed,
  and at which head.
- **The author says:** the reply in one or two sentences, with its link.
- **Assessment:** what testing the author's objection showed, and what the
  independent judgement concluded.

When the action is a reply, the quoted block is the drafted reply.

## Run report

One file per run at `runs/<date>-<nn>.md`, written when the run closes and
not edited afterwards.

```markdown
# Run <run id> — PR #<number>

**Started** <UTC> · **Ended** <UTC> · **Head** `<short-sha>` · **Ended by**
<complete | the criterion | a decision the user must make>

## Limits and spend

Stint: <name, or none>. <Limits from the request that changed it, or none.>

| Measure | Kind | Limit | Reached | Result |
|---|---|---|---|---|
| <measure> | <kind> | <value> | <value> | <ended the run | within limit | met | not reached> |

Token counter: <which counter, and what the figure leaves out>.

## Fetch
## Replies
## Fix verification
## New commits
## Queued in this run
## Rejected in this run
## Left open
## Areas
## Deepening
## Next
```

- **Limits and spend** lists every criterion in effect, including those that
  did not end the run. With no criteria, say so and still record time and
  tokens when they can be read.
- **Fetch** says whether the head moved and what arrived. **Replies** gives
  each reply, how it was classified and the outcome. **Fix verification**
  gives each finding checked and its result. **New commits** has one row per
  commit: what it claims, what it is, and the candidates it raised. A stage
  the command did not run says “Not run.”
- **Queued** links each new card. **Rejected** gives each claim and why it
  failed. **Left open** lists what is `investigating`, `suspected` or still a
  `candidate`.
- **Areas** names each area entered or exited, what was read and what was not.
- **Deepening** appears only when a minimum kept the run going after the
  review looked complete; it lists the steps taken.

## Stop criteria

### Measures

| Measure | Unit | Counting rule |
|---|---|---|
| `findings` | findings | Findings whose status became `queued` during the run. `minor` counts `minor-noted`. Without a severity the limit counts critical and major together. Candidates, suspected and rejected findings never count. |
| `time` | minutes | Wall clock since the run's `started_at`. |
| `tokens` | tokens | New tokens since the run started: output plus input that was not read from cache. Cache reads are left out because they repeat the same context on every turn and dwarf everything else. |
| `coverage` | areas | Areas whose status became `exited` during the run. |
| `dry-spell` | areas | Areas exited one after another with no new critical or major finding queued. A queued finding resets it. |

With scope `total` a measure counts the whole review instead of the run:
findings ever queued, minutes and tokens summed over `runs`, areas exited.

One measured Claude Code session on 2026-10-05 used about 0.4 million new
tokens and 11.8 million cache-read tokens in 70 minutes, without subagents.
Use the `spent` figures in `runs` once there are some.

### From the user's words to a kind

| The user says | Kind |
|---|---|
| “at most”, “no more than”, “maximum”, “up to” | `soft-max` |
| “hard limit”, “never more than”, “hard maximum” | `hard-max` |
| “at least”, “minimum” | `soft-min` |
| “hard minimum”, “must reach” | `hard-min` |
| “recommended”, “target”, “about”, “aim for” | `soft-min` and `soft-max` at the same value |

An explicit “soft” or “hard” in the request always wins over this table.

### Worked example

The numbers are illustrative only; they show how kinds interact, not what a
run should be given. Limits used often are stored as a [stint](stints.md).

> Find maximum 10 critical issues, minimum of 3 major issues, work no more
> than 60 minutes (soft) with hard limit 80 minutes. Spend minimum (soft) of
> 500k tokens and soft maximum 2 million.

```json
[
  { "measure": "findings", "severity": "critical", "kind": "soft-max", "value": 10, "scope": "run" },
  { "measure": "findings", "severity": "major", "kind": "soft-min", "value": 3, "scope": "run" },
  { "measure": "time", "kind": "soft-max", "value": 60, "scope": "run" },
  { "measure": "time", "kind": "hard-max", "value": 80, "scope": "run" },
  { "measure": "tokens", "kind": "soft-min", "value": 500000, "scope": "run" },
  { "measure": "tokens", "kind": "soft-max", "value": 2000000, "scope": "run" }
]
```

How it plays out:

- At 60 minutes with one major finding queued and another being verified:
  the soft maximum outranks the soft minimums, so finish that finding, then
  close. If it is still unfinished at 80 minutes, save it as `investigating`
  and close. Report that the minimum of three major findings was not reached.
- The review becomes complete after 30 minutes and 200,000 tokens with two
  major findings: both minimums are unmet, so deepen the review until they
  are met, a maximum is reached, or nothing is left to examine.
- Ten critical findings are queued after 40 minutes: close after the tenth,
  and list any further critical candidates in the report.

### Reading token spend in Claude Code

Claude Code writes each session to
`~/.claude/projects/<project-dir>/<session-id>.jsonl`; the running session is
the newest `.jsonl` in its project directory. Each model response carries a
`usage` object. One response can span several records, so count each response
once:

```bash
python3 - "<transcript.jsonl>" "<run started_at, UTC ISO>" <<'EOF'
import json, sys
path, since = sys.argv[1], sys.argv[2]
seen = {}
for line in open(path):
    try:
        rec = json.loads(line)
    except ValueError:
        continue
    msg = rec.get("message")
    if not isinstance(msg, dict) or "usage" not in msg or rec.get("timestamp", "") < since:
        continue
    seen[msg.get("id") or rec.get("uuid")] = msg["usage"]
new = sum((u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)
          + (u.get("output_tokens") or 0) for u in seen.values())
print(f"responses={len(seen)} new_tokens={new}")
EOF
```

This counts the session itself. Agents it spawned keep their own transcripts;
add them if they can be found, and otherwise say the figure leaves them out.
Other harnesses need their own usage record. If none can be read, token
criteria are not applied and the run says so at the start.

## Reading a GitHub pull request

These read the pull request through the `gh` CLI without touching the source
checkout. Other hosts need their own equivalents.

Identity, state and discussion:

```bash
gh pr view <number> --repo <owner>/<repo> --json title,body,author,state,headRefOid,baseRefOid,headRefName,baseRefName,mergeable,mergeStateStatus,updatedAt,comments
```

Every changed file. `gh pr view --json files` stops at 100 files, so page the
REST list instead:

```bash
gh api --paginate "repos/<owner>/<repo>/pulls/<number>/files?per_page=100" --jq '.[] | [.status,.additions,.deletions,.filename] | @tsv'
```

Review threads with replies and resolved/outdated flags:

```bash
gh api graphql --paginate -f query='query($endCursor:String){repository(owner:"<owner>",name:"<repo>"){pullRequest(number:<number>){headRefOid reviewThreads(first:100,after:$endCursor){pageInfo{hasNextPage endCursor} nodes{isResolved isOutdated path line originalLine comments(first:50){nodes{author{login} url createdAt body}}}}}}}'
```

Commits and per-file patches between two heads:

```bash
gh api "repos/<owner>/<repo>/compare/<old-sha>...<new-sha>"
```

One file at a pinned commit:

```bash
gh api -H "Accept: application/vnd.github.raw" "repos/<owner>/<repo>/contents/<path>?ref=<sha>"
```
