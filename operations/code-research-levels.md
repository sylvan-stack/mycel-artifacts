---
role: authored
---
# Guide: Code Research Levels

Start with the least work that can answer the request. Exact lookup, a cited
explanation, and durable task context need different amounts of investigation.
Follow the [Hub's dated pre-ingest instruction](../README.md): until the owner
fills the index, use grep and file reads instead of Mycel retrieval.

| Level | Use when | Result |
| --- | --- | --- |
| 1 | an exact string or one location is needed | matching paths and lines |
| 2 | a question needs synthesis across files | a cited answer in the session |
| 3 | a task needs durable context across several angles | a research artifact |

## Level 1 — text and location lookup

Use `rg` or `grep` for complete enumeration and claims of absence. Mycel 2 can
add related recall through `mycel grep -rn "pattern" src`: it runs the first
`grep` on PATH with the literal arguments, preserves its output and status,
and may append a clearly marked, read-only search tail. The tail uses the
current index; it does not prove absence. Before the first ingest, or when a
script needs only grep bytes, use ordinary grep or
`MYCEL_GREP_PLAIN=1 mycel grep -rn "pattern" src`.

Every argument after `grep` belongs to system grep, including `--repo` and
`--help`. For explicit repository scope use structured retrieval instead:
`mycel search --repo <repo> "<query>"`. From a prepared folder always name the
repository; implicit scope can cover the organization. The
[grep manual](../tools/mycel-2.md#grep-and-its-related-search-tail) owns exact
eligibility, tail limits and failure behavior.

## Level 2 — code research

For “how does this work” or “why is this decided here”, follow
[code research](code-research.md): consume relevant indexed documents when
retrieval is available, fill the gaps with targeted reads, and answer with
file-and-line evidence. If vocabulary is uncertain, a few different search
phrasings may find prior research; an empty index is a reason to read files.

## Level 3 — deep research

For “build context for this task”, follow [deep research](deep-research.md).
Cover the planned angles and persist their evidence under the repository's
resolved artifact root. Update an existing useful document before adding one.

For example, “where is parseConfig used” is level 1; “how does token renewal
work” is level 2; “research everything the upload-limit change touches” is
level 3.

<!-- sources:
mycel:@code/src/mycel/_grep.py
mycel:@code/src/mycel/_search.py
-->
