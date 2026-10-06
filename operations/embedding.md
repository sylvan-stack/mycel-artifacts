---
role: authored
---
# Guide: Embedding

How [Mycel](../../arbol/GLOSSARY.md#mycel) turns chunks into vectors — the rules that
keep it correct, and the habits that keep retrieval getting smarter. This is
the write side; the read side is [Code Retrieval Guide](retrieval.md).

## The model

- **One profile per repo**, set in `~/.mycel/config.toml`. Every repository
  uses `voyage` today.
- **Chunks embed with an identity header** (`path — symbol (kind)` for code,
  `path › heading` for docs): the path and symbol carry meaning the body often
  lacks (`invoice-export.service.ts` says "invoice export" even when
  the code never does). Headers sit first, so token-window truncation drops
  the tail, never the identity.
- **Queries embed with the repo's profile model** — vectors from different
  models are different spaces; repo-scoped search guarantees query and corpus
  share one.

<!-- sources:
mycel:mycel/knowledge/embedder.py#_embed_text
-->

## The iron rules

1. **Clear vectors only after the new code is live.** A model swap or
   embed-input change re-embedded before the new executable is installed lets
   the old one overwrite new vectors with old semantics. Install first, clear
   second, backfill third.
2. **A backfill is interruptible.** Shutdown aborts the loop cooperatively
   within seconds; pending chunks resume on the next Sync Pass. Never fear
   restarting mid-embed.

## The compounding habits

- **Jargon the code never spells out** → an entry in
  `~/Artifacts/<repo>/GLOSSARY.md` with [Source
  Refs](../../arbol/GLOSSARY.md#source-ref) to the implementing code. One code
  glossary took jargon retrieval from 3/6 to 6/6; glossaries for the code repos
  took a 10-query jargon set from mostly-miss to 9/10 @3. Refs must point at
  **files** (optionally `#Symbol`) — directory refs resolve to no edges.
- **Expensive research synthesis** → persist per the
  [authoring guide](source-refs-authoring.md); **update existing
  docs rather than adding siblings** (repairs drift, keeps the corpus curated).
- **Superseded documents** → [Heartwood](../../arbol/GLOSSARY.md#heartwood)
  (`status: heartwood` + pins): searchable record, exempt from Detection,
  badged against masquerading as current truth.
