---
role: authored
---
# Guide: Code Map

A **mechanical, per-repo overview artifact** — `generated/code-map.md` in the
repo's [Artifact Corpus](../../arbol/GLOSSARY.md#artifact-corpus) — rebuilt from
[Chunks](../../arbol/GLOSSARY.md#chunk) alone (paths + symbols + kinds the corpus
already holds): no LLM, no interlock concerns, milliseconds to produce.

## The process

1. Any [Sync Pass](../../arbol/GLOSSARY.md#sync-pass) that changed a repo's code
   corpus regenerates its map — atomic write only when content actually
   changed; a failure warns and never blocks sync.
2. The map's directory sections list each file's classes and methods (capped
   at 8 names per file), and every section carries **file-level Source Refs**
   to the files it describes.
3. Normal ingestion then embeds it like any document — so overview-shaped
   queries ("what services exist in the limit domain") finally have a chunk
   to land on, and every code file gains a `documented_in` pointer back to
   its map section.

## Why `generated: true`

Regenerated-not-maintained: exempt from [Detection](../../arbol/GLOSSARY.md#detection)
(drift against a document that rewrites itself is noise) and from
[RAPTOR](../../arbol/GLOSSARY.md#raptor-tree) clustering — searchable, never stale.

<!-- sources:
mycel:mycel/knowledge/code_map.py#write_map
mycel:mycel/knowledge/code_map.py#build_markdown
-->
