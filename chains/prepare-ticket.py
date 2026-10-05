#!/usr/bin/env python3
"""Prepare Ticket — Blueprint Chain: the preparation slice, WITHOUT research.

Turns a Jira key into the light half of a ticket workspace: mirrored raw
ticket, formatted ticket.md, verifiable objectives.md, curated
jira-context.md — then stops. For the times you want the ticket understood
and its context curated but the codebase work (scout, deep research) deferred
or never wanted.

Deliberately DUPLICATES steps 1–4 of start-new-ticket.py rather than sharing
a sub-chain abstraction: the two chains evolve independently, and reading one
never requires the other (DRY explicitly rejected here; chainlib plumbing is
the only shared code). Needs no --repo — preparation never touches code.

Usage:  python3 ~/Artifacts/mycel/chains/prepare-ticket.py DEMO-10006
        [--until N]        stop after step N; the run stays resumable
        [--fresh]          ignore any unfinished run — start from step 1
        [--dry-run]        print the Cell plan and resume state, run nothing
Runbook: ./prepare-ticket.md (sibling). Full pipeline incl. code scout +
deep research: ./start-new-ticket.py.
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chainlib import Chain, frontmatter, slugify  # noqa: E402

HOME = os.path.expanduser("~")
MIRROR = os.path.join(HOME, "Artifacts/mirrors/jira")
WORKSPACES = os.path.join(HOME, "Artifacts/jira")

PLAN = [
    (1, "tool",      "fetch raw mirror + create workspace"),
    (2, "blueprint", "format-ticket → ticket.md"),
    (3, "lambda",    "objectives → objectives.md"),
    (4, "blueprint", "gather-jira-context → jira-context.md"),
]


# Recipe policy for this chain (the script's equivalent of a blueprint's
# frontmatter). PIN_RECIPE = a hard pin forcing every step ("inherit" = don't
# pin); DEFAULT_RECIPE = the fallback when not pinned and --recipe is absent.
PIN_RECIPE = "inherit"
DEFAULT_RECIPE = "jira-agent"


def _files(d: str) -> list:
    return [os.path.join(d, f) for f in sorted(os.listdir(d))] if os.path.isdir(d) else []


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepare Ticket — Blueprint Chain (no research)")
    ap.add_argument("ticket", help="Jira key, e.g. DEMO-10006")
    ap.add_argument("--until", type=int, default=len(PLAN),
                    help="stop after step N (run stays resumable)")
    ap.add_argument("--fresh", action="store_true",
                    help="ignore any unfinished run for this ticket; start over")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the Cell plan + resume state, run nothing")
    ap.add_argument("--recipe", default=None,
                    help="Brain Recipe for ALL steps (overrides blueprint frontmatter "
                         "+ lambda default). Caller-only: pass when the USER names a "
                         "recipe — a triggering session's model never inherits")
    args = ap.parse_args()
    key = args.ticket.strip().upper()

    if args.dry_run:
        resumable = Chain._find_unfinished("prepare-ticket", key)
        print(f"chain prepare-ticket · ticket={key} until={args.until}")
        done = set((resumable[2].get("completed_steps") or [])) if resumable else set()
        for n, kind, title in PLAN:
            mark = "SKIP (done, resume)" if n in done and kind != "tool" else \
                   ("re-run (tool, fresh-on-read)" if n in done else "run")
            mark = "not reached (--until)" if n > args.until else mark
            print(f"  Cell {n}/{len(PLAN)} [{kind:9}] {title}  →  {mark}")
        if resumable:
            print(f"resume target: {resumable[0]}")
        return 0

    chain = Chain("prepare-ticket", key, len(PLAN), resume=not args.fresh,
                  recipe=args.recipe, default_recipe=DEFAULT_RECIPE, pin_recipe=PIN_RECIPE)

    # -- 1. Tool: fetch the raw mirror; slug + workspace belong to the chain --
    chain.tool(1, PLAN[0][2], ["mycel", "mirror", "fetch", "jira", key])
    mirror_json = os.path.join(MIRROR, f"{key}.json")  # the complete raw payload
    fm = frontmatter(os.path.join(MIRROR, f"{key}.md"))  # readable view = slug source
    slug = slugify(fm.get("summary") or "ticket")
    ticket_dir = os.path.join(WORKSPACES, f"{key}-{slug}")
    os.makedirs(ticket_dir, exist_ok=True)
    print(f"   workspace: {ticket_dir}", file=sys.stderr)
    if args.until < 2:
        chain.pause(1, output_files=_files(ticket_dir), ticket_dir=ticket_dir)
        return 0

    # -- 2. Blueprint: format-ticket ------------------------------------------
    chain.blueprint(2, PLAN[1][2], "format-ticket", ticket=key, ticket_dir=ticket_dir)
    if args.until < 3:
        chain.pause(2, output_files=_files(ticket_dir), ticket_dir=ticket_dir)
        return 0

    # -- 3. Lambda: objectives -------------------------------------------------
    chain.lam(3, PLAN[2][2],
        f"Read {ticket_dir}/ticket.md and the complete raw payload {mirror_json} "
        "(the full Jira JSON — extract only what matters for objectives). "
        f"Write {ticket_dir}/objectives.md: the ticket's OBJECTIVES — verifiable "
        "completion conditions consulted when the work is done to decide met/unmet "
        "(NOT a restatement of requirements; each objective must be checkable, "
        "with what evidence would prove it). Frontmatter: a Source Refs comment "
        f"citing jira-mirror:{key}.md. Keep it lean: 3-8 objectives.",
        cwd=ticket_dir)
    if args.until < 4:
        chain.pause(3, output_files=_files(ticket_dir), ticket_dir=ticket_dir)
        return 0

    # -- 4. Blueprint: gather-jira-context --------------------------------------
    chain.blueprint(4, PLAN[3][2], "gather-jira-context", max_minutes=20,
                    ticket=key, ticket_dir=ticket_dir)

    chain.finish(output_files=_files(ticket_dir), ticket_dir=ticket_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
