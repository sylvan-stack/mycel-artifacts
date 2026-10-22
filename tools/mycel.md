---
role: authored
---
# Runbook: Mycel 2

The installed command is `~/.local/bin/mycel`, selected by Mycel's independent
launcher. Start with `mycel --help`; help is JSON and needs no settings.
`mycel info` reports the selected Build, package version and settings/store
diagnostics. The [command manual](mycel-2.md) owns command syntax and replies;
[settings](mycel-2-settings.md) owns configuration and credentials;
[Builds](mycel-2-builds.md) owns installation, selection and maintenance.

Follow the [Hub's dated pre-ingest instruction](../README.md) before running
search, ingest or embedding. Until the owner fills the index, research uses
`rg`, `grep` and file reads. Mycel 1 and its deprecated implementations are
never run.

## Repository corpus binding

`~/.mycel/config.toml`, or the file explicitly selected by `MYCEL_CONFIG`, is
the source of truth. `mycel repos` lists configured organizations and
repositories, resolved code/artifact roots, enabled state and local faults.
Use those resolved roots for authored artifacts; do not infer them from an
old flat-folder example. The [settings guide](mycel-2-settings.md#tables-and-defaults)
gives explicit `code_root`/`artifact_root` overrides, organization defaults,
`code_clones` and `readonly_root`. Creating a folder does not enable indexing.

From a prepared folder pass `--repo <name>` explicitly; without it scope can
cover the organization's enabled members. On this Mac the intended indexed
checkout is `~/repos/sylvan-stack/readonly/<repo>`, plus its configured corpus.
Settings preparation belongs to SYL-241; this guide changes no settings.

## Choose the current manual

- [Search and its schema-3 results](mycel-2-retrieval.md),
  [exact chunk reading](mycel-2-reading.md), and
  [grep with an optional related-search tail](mycel-2.md#grep-and-its-related-search-tail).
- [Complete scoped ingest](mycel-2-reconciliation.md#complete-public-ingest),
  [embedding and dry-run plans](mycel-2-embedding.md), and
  [summary status, build, regeneration and removal](mycel-2-summaries.md).
- [Dependencies, relations and verification](mycel-2-relations.md),
  [Origin Links and coverage](mycel-2-origins.md),
  [classification](mycel-2-classification.md), and
  [activity history](mycel-2-activity.md).

Normal search can perform a bounded local freshness pass and embed its query;
`--no-fresh` skips freshness writes, but does not disable query embedding.
Search never embeds pending corpus text. Ingest leaves Git checkouts as they
are and embeds only with explicit `--embed`; embedding itself uses retained
text and explicit/CWD scope. Use the manuals above for retries and partial
results rather than treating an empty result as proof that the index is ready.

<!-- sources:
mycel:@code/src/mycel/_cli.py
mycel:@code/src/mycel/_settings.py
mycel:@code/src/mycel/_scope.py
mycel:@code/src/mycel/_search.py
mycel:@code/src/mycel/_ingest.py
-->
