---
role: authored
---
# Guide: Code Research Levels

Three levels for understanding code, ordered by cost. **Start at the lowest
level that can answer; a failed level is information for the next one.** This
guide exists so an agent picks the right tool on the first try.

| Level | Tool | Use when | Cost |
| --- | --- | --- | --- |
| 1 | `better-grep` | any text search — an **exact string OR uncertain words** | ~2s (ms with the tail off) |
| 2 | code-research | you have a **question** needing synthesis | minutes |
| 3 | deep-research | you need **task context / coverage / an artifact** | 10min+ |

## Level 1 — better-grep (the default text search — use it instead of grep)

**`better-grep` is a strict superset of grep, so it is the default reflex for
ALL text search — reach for it, not `grep`/`rg`, whenever you'd otherwise
grep.** Drop-in: swap the word, keep everything else
(`grep -rn "foo" src` → `better-grep -rn "foo" src`).

It is grep *plus* recall, in one call:

- **Head = byte-identical grep.** The exact arm literally runs `/usr/bin/grep`
  with your flags; same `path:line:` output, same exit code (0 match / 1 none
  / 2 error). Everything grep is good at, better-grep is exactly as good at —
  including grep's unique powers: **completeness within scope** (every
  occurrence, no ranking cutoff) and **proving absence** (exit code 1 is a real
  no-match; the informational tail never changes it). Scripts stay correct.
- **Tail = the recall grep can't give**, clearly delimited, informational only:
  `── mycel: related by meaning ──` — code and docs that are *about* the
  pattern's words without containing them (dense + **BM25** + doc-bridge over
  code *and* corpus documents, plus **RAPTOR** summaries where they exist,
  `⇐ via` attribution); `── mycel: documented in ──` — glossary/research
  sections citing those hits, with ⚠ stale / heartwood trust flags.
  *(RAPTOR summaries are generated per-repo on request — today only the `Arbol`
  repo has them; run `mycel raptor` on a repo to enable summary recall there.
  Corpus-doc recall — code-map, glossary, research — works everywhere now.)*

The win is **recall, not precision**: a literal match is already maximally
precise, so better-grep can't be "more exact" than grep — what it adds is the
*places grep would miss* (the code's word isn't your word) and the *docs that
explain the hit*. When grep returns 0 (vocabulary gap) or 500 (needle in a
haystack), the tail is what rescues you.

<!-- sources:
mycel:mycel/better_grep.py
-->

- Repo scope inferred from path operands / CWD (working copies and mirrors both
  recognized); `ARBOL_REPO` overrides.

**When to drop to plain `grep`:** only when you deliberately want *no* semantic
tail — an automated script parsing stdout, a tight enumeration loop, or when
the `mycel` CLI is unavailable. `BETTER_GREP_PLAIN=1 better-grep …` gives you
exactly that (pure grep, tail suppressed) without leaving the tool. In an
interactive or agent session there is essentially never a reason to prefer
bare grep.

(Reviewed 2026-07-08: better-grep promoted from "level 2, when vocabulary is
uncertain" to "level 1, the default" — it dominates grep for interactive use;
the old ladder mis-framed them as an exact-vs-fuzzy pair. Same day, the tail
went daemon-less: it shells out to `mycel search --no-fresh` per invocation —
no socket, no daemon; it works with Arbol fully stopped.)

## Level 2 — code-research

For **question-shaped** requests: "how does X work", "where is Y decided",
"what breaks if Z changes". In-session, minutes, answer in chat with
`file:line` citations. See [code-research](code-research.md) for the loop —
in one line: **Mycel first** (`mycel search`, read every surfaced
research/glossary doc before opening code), targeted reads into the gaps,
cited answer, and persist the synthesis if it was expensive and reusable.

## Level 3 — deep-research

Long-running research that **produces or updates a research artifact** in
`~/Artifacts/<repo>/research/` with Source Refs — task-context building,
multi-angle coverage of everything a task might touch. See
[deep-research](deep-research.md) for the inputs, the process and the quality
bar.

## Escalation examples

- "where is `parseConfig` used" → **better-grep** (its grep head
  enumerates every call site exactly; the tail flags any indirection).
- "where do we send the reminder email" → **better-grep** ("reminder" may not
  be the code's word — the tail finds the code's own term via the glossary).
- "how does token renewal decide?" → **code-research** (synthesis across
  service + events + config).
- "I'm picking up the work on upload limits, build me context" →
  **deep-research** (coverage + artifact).
