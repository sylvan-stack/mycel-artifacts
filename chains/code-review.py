#!/usr/bin/env python3
"""Code Review — a Blueprint Chain (a Tool).

The rigorous, detached review of an MR: deterministic Python composing seven
Cells with CODE-ENFORCED gates — the guarantee a chain adds over the manual
code-review Blueprint (which remains the interactive, in-session path):

  Tool Cells        (no agent):  mycel mirror fetch gitlab/jira; mycel wt add
  Blueprint Cells   (named fns): review-diff (executor), review-diff gap
                                 retry (conditional), verify-findings
                                 (adversarial verifier, FRESH context)
  lambda Cells      (inline):    brief.md — MR claim vs ticket intent;
                                 publish — the deliverable, written to the
                                 TICKET workspace as code-review-<datetime>.md
                                 (points most-important-first, [BLOCKING]
                                 markers, clickable file:line links, evidence)

Two gates no instruction can promise: the COVERAGE gate (every file in the
real merge-base diff is reviewed-or-skipped — one automatic scoped retry,
then abort) and the VERIFICATION gate (every finding gets a fresh-context
verdict with evidence). Pure code assembles review.md from confirmed +
adjusted findings; refuted ones appear under "dismissed by verification".

Workspace: ~/Artifacts/<repo>/tickets/<KEY>/review/mr-<iid>/ (reviews/mr<iid> when no ticket)
  brief.md            what the MR claims vs what the ticket demands
  changed-files.json  the coverage contract (authoritative git diff)
  findings.{json,md}  the executor's output
  verdicts.json       the verifier's output
  review.md           the code-assembled, machine-faithful record
Deliverable: {ticket_dir}/code-review-<datetime>.md — the ticket workspace
(~/Artifacts/jira/<KEY>-<slug>/); falls back to the review workspace when the
MR has no ticket.

Usage:  python3 ~/Artifacts/mycel/chains/code-review.py <MR-URL>
        [--until N]   [--fresh]   [--dry-run]   [--recipe NAME]
Branch-without-MR reviews stay on the manual Blueprint
(~/Artifacts/mycel/blueprints/code-review.md).
Runbook: ./code-review.md (sibling).
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chainlib import Chain, frontmatter, slugify  # noqa: E402

HOME = os.path.expanduser("~")
GITLAB_MIRROR = os.path.join(HOME, "Artifacts/mirrors/gitlab")
TICKET_RE = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")
MR_URL_RE = re.compile(r"https?://[^/]+/(.+?)/-/merge_requests/(\d+)")
SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2, "nit": 3}

PLAN = [
    (1, "tool",      "fetch MR mirror + create review workspace"),
    (2, "tool",      "fetch ticket closure (skipped when no ticket)"),
    (3, "tool",      "worktree + overlay; changed-files.json from merge-base diff"),
    (4, "lambda",    "brief: MR claim vs ticket intent → brief.md"),
    (5, "blueprint", "review-diff → findings.{json,md}  [coverage gate]"),
    (6, "blueprint", "review-diff gap retry (only when the gate found gaps)"),
    (7, "blueprint", "verify-findings (fresh context) → verdicts.json"),
    (8, "lambda",    "publish → {ticket_dir}/code-review-<datetime>.md  [file-exists gate]"),
]

# Recipe policy (the script's equivalent of a blueprint's frontmatter).
# Default bro-opus-max: EVERY Cell — reviewer, verifier, brief, publish —
# runs on the strong recipe unless the user names another via --recipe.
PIN_RECIPE = "inherit"
DEFAULT_RECIPE = "bro-opus-max"


def _git(cwd: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *argv], cwd=cwd, capture_output=True, text=True, timeout=120)


def _read_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _files(d: str) -> list:
    return [os.path.join(d, f) for f in sorted(os.listdir(d))] if os.path.isdir(d) else []


def changed_files(worktree: str, target_branch: str) -> list:
    """The coverage contract: name-status of the merge-base diff, authoritative
    from git (the mirror caps its diff list — never trust it for coverage)."""
    base = None
    for ref in (f"origin/{target_branch}", target_branch, "origin/master", "origin/main"):
        r = _git(worktree, "merge-base", ref, "HEAD")
        if r.returncode == 0:
            base = r.stdout.strip()
            break
    if not base:
        return []
    r = _git(worktree, "diff", "--name-status", f"{base}..HEAD")
    out = []
    for ln in r.stdout.splitlines():
        parts = ln.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0][0]  # M/A/D/R/C/T
        path = parts[-1]      # renames/copies: the NEW path
        out.append({"path": path, "status": status})
    return out


def ticket_workspace(ticket: str) -> str:
    """The ticket's workspace ~/Artifacts/jira/<KEY>-<slug>/ — reuse an existing
    one (whatever its slug) over deriving a fresh sibling; create when absent."""
    import glob
    hits = sorted(glob.glob(os.path.join(HOME, "Artifacts/jira", f"{ticket}-*")))
    if hits:
        return hits[0]
    fm = frontmatter(os.path.join(HOME, "Artifacts/mirrors/jira", f"{ticket}.md"))
    d = os.path.join(HOME, "Artifacts/jira",
                     f"{ticket}-{slugify(fm.get('summary') or 'ticket')}")
    os.makedirs(d, exist_ok=True)
    return d


def coverage_gaps(review_dir: str, changed: list) -> list:
    """Paths in the coverage contract with no reviewed/skipped entry."""
    try:
        cov = {c.get("path") for c in _read_json(
            os.path.join(review_dir, "findings.json")).get("coverage", [])}
    except (OSError, json.JSONDecodeError):
        return [c["path"] for c in changed]
    return [c["path"] for c in changed if c["path"] not in cov]


def assemble_review(review_dir: str, meta: dict) -> str:
    """Pure code: verdicts × findings → review.md, severity-ranked. Confirmed
    and adjusted findings are the review; refuted ones are shown dismissed
    (transparency beats silence); verifier-flagged criticals are appended."""
    findings = {f["id"]: f for f in _read_json(
        os.path.join(review_dir, "findings.json")).get("findings", [])}
    vdata = _read_json(os.path.join(review_dir, "verdicts.json"))
    verdicts = {v["id"]: v for v in vdata.get("verdicts", [])}
    kept, dismissed = [], []
    for fid, f in findings.items():
        v = verdicts.get(fid, {})
        if v.get("verdict") == "refuted":
            dismissed.append((f, v))
            continue
        sev = v.get("severity") or f.get("severity") or "minor"
        kept.append(({**f, "severity": sev}, v))
    for m in vdata.get("missed", []):
        kept.append(({**m, "id": m.get("id", "V?"), "evidence": "verifier-flagged"},
                     {"verdict": "confirmed", "evidence": m.get("scenario", "")}))
    kept.sort(key=lambda kv: SEVERITY_ORDER.get(kv[0].get("severity", "minor"), 9))

    changed = _read_json(os.path.join(review_dir, "changed-files.json"))
    cov = {c.get("path"): c for c in _read_json(
        os.path.join(review_dir, "findings.json")).get("coverage", [])}
    skipped = [c for c in cov.values() if c.get("status") == "skipped"]

    lines = ["---", "role: authored", f"sources: {meta['mirror_ref']}", "---",
             f"# Review: {meta['title']}", "",
             f"MR: {meta['url']}  ·  branch `{meta['branch']}` → `{meta['target']}`",
             f"Ticket: {meta['ticket'] or '(none found)'}  ·  reviewed {meta['date']}",
             f"Verdict counts: {len(kept)} stand ({sum(1 for k, v in kept if v.get('verdict') == 'adjusted')} adjusted) · {len(dismissed)} dismissed",
             ""]
    if kept:
        lines.append("## Findings (severity-ranked, independently verified)")
        for f, v in kept:
            lines += ["", f"### {f['severity'].upper()} · {f.get('title', f['id'])} — `{f.get('file')}:{f.get('line')}`",
                      f"{f.get('what_breaks', '')}", "",
                      f"**Scenario:** {f.get('scenario', '')}",
                      f"**Verification:** {v.get('verdict', 'unverified')} — {v.get('evidence', '')}"]
    else:
        lines.append("## No findings survived verification")
    lines += ["", "## Coverage",
              f"{sum(1 for c in cov.values() if c.get('status') == 'reviewed')} reviewed · "
              f"{len(skipped)} skipped · {len(changed)} changed files total"]
    for s in skipped:
        lines.append(f"- skipped `{s.get('path')}` — {s.get('why', '')}")
    if dismissed:
        lines += ["", "## Dismissed by verification"]
        for f, v in dismissed:
            lines.append(f"- ~~{f.get('severity')}~~ {f.get('title', f['id'])} "
                         f"(`{f.get('file')}:{f.get('line')}`) — {v.get('evidence', '')}")
    path = os.path.join(review_dir, "review.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description="Code Review — Blueprint Chain")
    ap.add_argument("mr", help="MR URL, e.g. https://gitlab…/group/project/-/merge_requests/123")
    ap.add_argument("--until", type=int, default=len(PLAN),
                    help="stop after Cell N (run stays resumable)")
    ap.add_argument("--fresh", action="store_true",
                    help="ignore any unfinished run for this MR; start over")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the Cell plan + resume state, run nothing")
    ap.add_argument("--recipe", default=None,
                    help="Brain Recipe for ALL Cells — a configured name or an ad-hoc "
                         "model:thinking descriptor (e.g. fable:xhigh). Caller-only: pass "
                         "when the USER names one — a session's model never inherits")
    args = ap.parse_args()

    m = MR_URL_RE.match(args.mr.strip())
    if not m:
        print("error: expected an MR URL (…/<project>/-/merge_requests/<iid>). "
              "Branch-without-MR reviews: use the manual code-review Blueprint.",
              file=sys.stderr)
        return 2
    project, iid = m.group(1), m.group(2)
    run_key = f"{project.rsplit('/', 1)[-1]}-mr{iid}"

    if args.dry_run:
        resumable = Chain._find_unfinished("code-review", run_key)
        print(f"chain code-review · {run_key} until={args.until}")
        done = set((resumable[2].get("completed_steps") or [])) if resumable else set()
        for n, kind, title in PLAN:
            mark = "SKIP (done, resume)" if n in done and kind != "tool" else \
                   ("re-run (tool, fresh-on-read)" if n in done else "run")
            mark = "not reached (--until)" if n > args.until else mark
            if n == 6:
                mark += "  [conditional: only on coverage gaps]"
            print(f"  Cell {n}/{len(PLAN)} [{kind:9}] {title}  →  {mark}")
        if resumable:
            print(f"resume target: {resumable[0]}")
        return 0

    chain = Chain("code-review", run_key, len(PLAN), resume=not args.fresh,
                  recipe=args.recipe, default_recipe=DEFAULT_RECIPE, pin_recipe=PIN_RECIPE)

    # -- 1. Tool: MR mirror; parse repo/branch/ticket; make the workspace --------
    chain.tool(1, PLAN[0][2], ["mycel", "mirror", "fetch", "gitlab", args.mr])
    mirror_md = os.path.join(GITLAB_MIRROR, f"{project.replace('/', '-')}-mr-{iid}.md")
    fm = frontmatter(mirror_md)
    repo = str(fm.get("project", project)).rsplit("/", 1)[-1]
    branch = str(fm.get("source_branch") or "")
    target = str(fm.get("target_branch") or "master")
    title = str(fm.get("title") or run_key)
    if not branch:
        chain.abort(1, f"mirror {mirror_md} has no source_branch")
    tk = TICKET_RE.search(branch) or TICKET_RE.search(title)
    ticket = tk.group(1) if tk else None
    if ticket:
        review_dir = os.path.join(HOME, "Artifacts", repo, "tickets", ticket,
                                  "review", f"mr-{iid}")
    else:
        review_dir = os.path.join(HOME, "Artifacts", repo, "reviews", f"mr{iid}")
    os.makedirs(review_dir, exist_ok=True)
    print(f"   review workspace: {review_dir}", file=sys.stderr)
    if args.until < 2:
        chain.pause(1, output_files=_files(review_dir), review_dir=review_dir)
        return 0

    # -- 2. Tool: ticket closure (the intent the diff answers to) ----------------
    if ticket:
        chain.tool(2, PLAN[1][2], ["mycel", "mirror", "fetch", "jira", ticket, "--closure"])
    else:
        print("   Cell 2 skipped: no ticket key in branch/title — reviewing "
              "against diff + conventions only", file=sys.stderr)
    if args.until < 3:
        chain.pause(2, output_files=_files(review_dir), review_dir=review_dir)
        return 0

    # -- 3. Tool: worktree + overlay; the coverage contract ----------------------
    container = os.path.join(HOME, "repo", repo)
    worktree = os.path.join(container, branch)
    # mycel wt add creates the worktree from a LOCAL ref only — ensure it first
    # (deterministic git; skipped when the local branch already exists).
    if _git(container, "--git-dir", os.path.join(container, ".bare"),
            "show-ref", "--verify", f"refs/heads/{branch}").returncode != 0:
        f = _git(container, "--git-dir", os.path.join(container, ".bare"),
                 "fetch", "origin", f"{branch}:refs/heads/{branch}")
        if f.returncode != 0:
            chain.abort(3, f"branch {branch} not found on origin: {f.stderr.strip()[-200:]}")
    chain.tool(3, PLAN[2][2], ["mycel", "wt", "add", repo, branch], timeout=1200)
    # The merge-base is only right if origin/<target> is FRESH — a stale ref
    # swept two weeks of master churn into the contract on the first live run
    # (4661 files for a 32-file MR). Fetch it; tolerate failure (local-only).
    f = _git(worktree, "fetch", "origin", target)
    if f.returncode != 0:
        print(f"   warning: could not fetch origin/{target} — merge-base may be stale",
              file=sys.stderr)
    changed = changed_files(worktree, target)
    if not changed:
        chain.abort(3, f"empty merge-base diff for {branch} vs {target} — nothing to review")
    # Sanity gate against the mirror's own count: a gross mismatch means a
    # stale/wrong base ref, and a bloated contract wastes a whole review run.
    mirror_count = str(fm.get("changes_count") or "").rstrip("+")
    if mirror_count.isdigit() and len(changed) > 3 * int(mirror_count) + 10:
        chain.abort(3, f"coverage contract of {len(changed)} files vs the MR's "
                       f"changes_count={fm.get('changes_count')} — merge-base is wrong "
                       f"(stale {target} ref?); refusing to review master churn")
    with open(os.path.join(review_dir, "changed-files.json"), "w", encoding="utf-8") as fh:
        json.dump(changed, fh, indent=1)
    print(f"   coverage contract: {len(changed)} changed files "
          f"(mirror says {fm.get('changes_count')})", file=sys.stderr)
    if args.until < 4:
        chain.pause(3, output_files=_files(review_dir), review_dir=review_dir)
        return 0

    # -- 4. Lambda: the brief -----------------------------------------------------
    ticket_line = (f"and the ticket mirror ~/Artifacts/mirrors/jira/{ticket}.md "
                   f"(follow its closure files for linked context) " if ticket else
                   "— no ticket was found; say so and derive intent from the MR alone ")
    chain.lam(4, PLAN[3][2],
        f"Read the MR mirror {mirror_md} {ticket_line}"
        f"and {review_dir}/changed-files.json. Write {review_dir}/brief.md — the "
        "review brief a fresh reviewer reads FIRST: (1) what the MR claims to do, "
        "(2) what the ticket demands (acceptance intent, constraints, anything the "
        "MR description is silent about), (3) risk areas to probe (auth, money, "
        "migrations, toggles, cross-service contracts — only those actually touched). "
        "Frontmatter: a Source Refs comment citing the mirrors. Keep it under a page.",
        cwd=review_dir)
    if not os.path.isfile(os.path.join(review_dir, "brief.md")):
        chain.abort(4, "brief gate failed — brief.md was not written")
    if args.until < 5:
        chain.pause(4, output_files=_files(review_dir), review_dir=review_dir)
        return 0

    # -- 5. Blueprint: review-diff (executor) + the coverage gate ----------------
    # tolerate_unmet covers a CLEAN-but-incomplete pass (done_when unmet because
    # a few files remain): those partial findings flow into the coverage gate +
    # the scoped gap retry below. A SESSION ERROR (refusal, rate limit, model
    # error) is NOT tolerated — chainlib aborts the chain immediately with the
    # provider's message. So Cell 6 recovers only honest incompleteness.
    chain.blueprint(5, PLAN[4][2], "review-diff", max_minutes=45, tolerate_unmet=True,
                    repo=repo, branch=branch, review_dir=review_dir)
    gaps = coverage_gaps(review_dir, changed)
    if args.until < 6:
        chain.pause(5, output_files=_files(review_dir), review_dir=review_dir,
                    coverage_gaps=gaps)
        return 0

    # -- 6. Blueprint (conditional): one scoped retry, then the gate is final ----
    if gaps:
        print(f"   coverage gate: {len(gaps)} uncovered file(s) — scoped retry",
              file=sys.stderr)
        chain.blueprint(6, PLAN[5][2], "review-diff", max_minutes=30,
                        repo=repo, branch=branch, review_dir=review_dir,
                        files=",".join(gaps))
        gaps = coverage_gaps(review_dir, changed)
        if gaps:
            chain.abort(6, f"coverage gate failed after retry — uncovered: {gaps[:10]}")
    else:
        print("   Cell 6 skipped: coverage complete on the first pass", file=sys.stderr)
    if args.until < 7:
        chain.pause(6, output_files=_files(review_dir), review_dir=review_dir)
        return 0

    # -- 7. Blueprint: verify-findings (fresh context) + the verification gate ---
    chain.blueprint(7, PLAN[6][2], "verify-findings", max_minutes=30,
                    repo=repo, branch=branch, review_dir=review_dir)
    finding_ids = {f["id"] for f in _read_json(
        os.path.join(review_dir, "findings.json")).get("findings", [])}
    verdict_ids = {v["id"] for v in _read_json(
        os.path.join(review_dir, "verdicts.json")).get("verdicts", [])}
    unverdicted = sorted(finding_ids - verdict_ids)
    if unverdicted:
        chain.abort(7, f"verification gate failed — findings without a verdict: {unverdicted}")

    # -- assemble (pure code) ------------------------------------------------------
    review_path = assemble_review(review_dir, {
        "url": str(fm.get("url") or args.mr), "title": title, "branch": branch,
        "target": target, "ticket": ticket,
        "mirror_ref": f"gitlab-mirror:{os.path.basename(mirror_md)}",
        "date": datetime.date.today().isoformat()})
    if args.until < 8:
        chain.pause(7, output_files=_files(review_dir), review_dir=review_dir)
        return 0

    # -- 8. Lambda: publish the deliverable into the ticket workspace -------------
    publish_dir = ticket_workspace(ticket) if ticket else review_dir
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    published = os.path.join(publish_dir, f"code-review-{stamp}.md")
    worktree_abs = os.path.join(HOME, "repo", repo, branch)
    # Relative path from the deliverable's own directory to the worktree — the
    # link form VS Code actually renders clickable. Absolute /paths render as a
    # site-root URL and file:// URIs get stripped to raw text by the previewer;
    # a scheme-less relative target linkifies everywhere.
    worktree_rel = os.path.relpath(worktree_abs, publish_dir)
    res = chain.lam(8, PLAN[7][2],
        f"Read {review_dir}/review.md (the verified, severity-ranked review), "
        f"{review_dir}/findings.json + {review_dir}/verdicts.json (the evidence), "
        f"and {review_dir}/brief.md. Write the review DELIVERABLE to {published} "
        "following these rules exactly:\n"
        "- Split into numbered points, ordered MOST IMPORTANT FIRST (only findings "
        "that survived verification — confirmed or adjusted).\n"
        "- Mark points that BLOCK the MR from being merged: start the point with "
        "**[BLOCKING]**. Blocking = merging without a fix breaks correctness, "
        "security, money, or compliance, or violates repo law (e.g. "
        "feature-toggle rules: new behavior toggled, old path untouched).\n"
        "- Every point gives the filepath AND line number in the MR as a CLICKABLE "
        f"markdown link. The link TARGET must be a RELATIVE path (from this "
        f"deliverable's directory) with the line anchored via #L — VS Code renders "
        f"a bare absolute /path as a URL and strips file:// URIs to raw text, but a "
        f"scheme-less relative target linkifies. Exactly: [<path>:<line>]"
        f"({worktree_rel}/<path>#L<line>) where <path> is the file's path inside "
        f"the repo. The link TEXT keeps the readable <path>:<line> form; only the "
        f"target uses the relative {worktree_rel}/ prefix + #L<line>.\n"
        "- Every point gives a short summary of the issue in plain words.\n"
        "- Every point is PROVEN with evidence from the code — quote or cite the "
        "exact code that shows the problem (the verifier's evidence is your "
        "starting material; re-check the worktree when unsure).\n"
        "- After the points, add anything else important to this review: test "
        "gaps, migration/rollout notes, risky-but-fine calls worth a comment, "
        "genuinely good changes worth keeping. Free form.\n"
        f"Header: MR {fm.get('url') or args.mr} · branch {branch} → {target} · "
        f"ticket {ticket or '(none)'} · one-line verdict (N blocking / M total). "
        f"Frontmatter: role: authored + a Source Refs comment citing "
        f"gitlab-mirror:{os.path.basename(mirror_md)}.",
        cwd=review_dir, max_minutes=15)
    # File-exists gate — only when the Cell actually ran (a resumed run keeps
    # its original stamp, so the freshly computed name must not be re-gated).
    if res is not None and not os.path.isfile(published):
        chain.abort(8, f"publish gate failed — {published} was not written")

    chain.finish(output_files=[*_files(review_dir),
                               *([published] if os.path.isfile(published) else [])],
                 review_dir=review_dir, review=review_path,
                 published=published if os.path.isfile(published) else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
