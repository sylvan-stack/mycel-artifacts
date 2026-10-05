---
role: authored
---
# Runbook: better-grep

## Why it exists

**A strict superset of grep — the default text search, meant to replace grep
outright.** Everything grep does, better-grep does identically (its exact arm
literally runs `/usr/bin/grep`); then it *adds* the recall grep structurally
can't: semantic neighbours, corpus docs, and the runbook/glossary sections
that explain the hit. The win is **recall, not precision** — a literal match
is already maximally precise, so better-grep can't be "more exact"; what it
adds is the *places grep misses* (the code's word isn't your word) and the
*docs that describe them*. Prefer it over `grep`/`rg` for any code lookup.

## Use

```
better-grep [any grep flags] PATTERN [PATH...]
```

Byte-identical grep passthrough (the exact arm literally runs `/usr/bin/grep`,
with grep's exit codes: 0 match / 1 none / 2 error — so absence proofs and
scripts stay correct), then two labeled Mycel sections:
`── mycel: related by meaning ──` (dense + BM25 + doc-bridge over code **and**
corpus docs, plus RAPTOR summaries where generated) and
`── mycel: documented in ──` (runbook/research sections whose Source Refs cite
the matched code, with ⚠ stale flags). The tail is informational; parsers of
`path:line:` lines are unaffected.

Env: `BETTER_GREP_PLAIN=1` (pure grep, tail suppressed — the *only* reason to
fall back: an automated script that must not see the tail, or the `mycel` CLI
being unavailable), `ARBOL_REPO`/`ARBOL_OVERLAY` (scope override; else
inferred from CWD), `MYCEL_BIN` (explicit `mycel` executable; else PATH).

**Daemon-less and Mycel-owned**: `better-grep` is packaged from the same
standalone Mycel executable and invokes Mycel's search library directly with
freshness disabled. It has no Arbol module, daemon, socket, or CLI dependency.
The search includes docs by default, so the tail's recall spans
the whole knowledge graph (code + corpus docs + RAPTOR), gated so prose can't
drown implementation. `--no-fresh` keeps the tail inside its 20s budget — a
staleness-triggered sync pass can take minutes and the tail is informational.
RAPTOR summaries exist only where `mycel raptor` has run (today: the `Arbol`
repo); corpus-doc recall is everywhere. If the semantic search fails for any
reason, the tail degrades to a one-line stderr notice — better-grep is then
exactly grep.

<!-- sources:
mycel:mycel/better_grep.py
-->
