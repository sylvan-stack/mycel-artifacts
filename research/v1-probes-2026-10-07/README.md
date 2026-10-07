---
role: authored
---
# Probes of the version 1 chunkers and store, 7 October 2026

The scripts behind the statements marked **(probe)** and **(stub run)** in the [inventory of ingest and the knowledge graph](../v1-inventory-ingest-and-graph.md). They are kept as records of what was run. They load code from the deprecated repository selected by `MYCEL_REPO` (default: `~/repos/sylvan-stack/mycel_deprecated_v1`), write nothing there, contact no database and use no network. Set `MYCEL_REPO` to another checkout when needed. The validation script reads the adjacent published inventory.

| Script | What it runs |
|---|---|
| `probe_md.py` | The Markdown chunker, the frontmatter reader and the Source Ref parser on fictional documents |
| `probe_code.py` | The Python and Svelte chunkers on fictional sources |
| `probe_ts.py` | The TypeScript, TSX and JavaScript chunker on fictional sources, with the grammar packages of the deprecated repository's own environment |
| `probe_s1.py` | The store's `track_source` and `ingest_code` against an in-memory stand-in for the connection, which shows a code edit being skipped. This checks the Python control flow, not PostgreSQL |
| `validate_doc.py` | That every Source Ref in the inventory names a function that exists in the deprecated source |
