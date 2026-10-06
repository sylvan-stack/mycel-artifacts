---
role: authored
---
# Runbook: mycel

## Why it exists

The daemon-less knowledge tool: one process per job, direct to Postgres,
query embeddings via the configured embedding provider. It is how any agent
searches the corpus and keeps it fresh. Settings live in
**`~/.mycel/config.toml`** (repositories, organizations, database and
embedding settings). Brain Recipes are owned separately by Infer in
**`~/.infer/config.toml`**. Mycel may read another product's databases and
logs as data, but it never depends on that product's code or instructions.

This runbook describes the Mycel 1 executable installed as `mycel`. Its
`--help` also lists `wt`, `pull`, `mirror`, `jira`, `confluence` and
`secrets`: they belong to retired worktree and external-mirror workflows, are
not part of any current procedure and are not documented here.

## Use

```
mycel search "<query>" [--k N] [--repo R] [--path P] [--overlay BRANCH] [--only code|docs] [--no-fresh]
mycel better-grep [grep flags] PATTERN [PATH...]   # also installed as `better-grep`
mycel sync [--no-embed]        # one Sync Pass over every enabled repository, then exit
mycel embed                    # embed every pending chunk, then exit
mycel status [--repo R]        # index freshness: documents, chunks, stale counts, embed counters
mycel activity [--k N] [--repo R] [--kind K]   # recent sync/embed/overlay/raptor feed
mycel drifts [--repo R]        # Detection findings: docs whose cited code changed
mycel derive '<child-ref>' '<source-ref>'  # assert source governs derived code/doc/test chunk
mycel overlay add|list|refresh|drop [repo] [branch] [--worktree PATH] [--no-embed]
mycel repos [list] [--root PATH] [--organization NAME]     # repos under ~/repo + mycel-enabled flag
mycel raptor status|plan|regen|build [--recipe NAME] [--repo R] [--regen]   # default recipe: raptor-agent;
                               # recipe is resolved by the independent `infer` executable;
                               # no Arbol daemon or provider fallback is used
```

- **Name the repository.** `search` defaults to the repository containing the
  CWD and falls back to `Arbol`; `status`, `drifts` and `raptor` default to
  `Arbol` outright. Pass `--repo` whenever another repository is meant.
- **Search contract.** CLI and Arbol's resident RPC call the same shared
  retrieval service and return schema version 1: `{schema_version, transport,
  repo, overlay, results, dense, bm25, freshness}`. Arbol prefers RPC and falls
  back to this independently usable CLI; Mycel itself never depends on Arbol.
- **derive** records an asserted Derivation using stable Source Refs rather
  than database chunk IDs. The first argument is the derived child
  (`repo:path#symbol` or `#Heading`); the second is its governor. It runs
  Detection after the edge is committed.
- **search** is unified — code + docs + summaries in one ranking; docs appear
  only when they clearly beat the best code hit (≤2, never INDEX/README).
  `--only` narrows. **Fresh-on-read**: `search` mtime-scans the repo
  (milliseconds, early-exit) and auto-syncs the delta when the source changed;
  `--no-fresh` skips, and so does `--only docs`. That pass is local and
  scoped to the searched repository: it refreshes no remotes and embeds
  nothing, so new or edited chunks stay pending until an embed runs.
- **sync** is the all-repository pass. It refreshes the remotes of code
  corpora, ingests every enabled repository, rewrites their code maps and,
  unless `--no-embed` is given, embeds every pending chunk of every enabled
  repository. Check `mycel status` for the pending count before running it
  without `--no-embed`. To bring one repository up to date, search in it.
- **overlay** is the Branch Overlay registry for a worktree that already
  exists. It runs no git: `add` and `refresh` ingest the worktree's
  difference from its base repository as `repo@branch`, `list` shows the
  registrations and `drop` removes one.
- **repos** lists repos under `~/repo` (`--root` overrides) with each repo's
  mycel-enabled flag, embedder profile, and whether it has an Artifact Corpus.
- **Organizations** are configured in `~/.mycel/config.toml`. Compatible
  settings editors use the same file. For example:

  ```toml
  [organizations."Euro Office"]
  root = "~/repos/euro-office"
  url = "https://github.com/Euro-Office"
  ```

  Direct Git repository children of that folder are members (including
  `.github`; ordinary folders and symlinks are excluded). `repos` flattens
  organization folders and adds `organization` to each member.
  `mycel repos list --organization "Euro Office"` resolves the name
  case-insensitively; an unknown organization fails with nonzero exit.
  Configured checkout and artifact roots infer the individual repo from CWD;
  the organization checkout/corpus root infers its name. This includes roots
  under `~/repos` and relocated paths. `mycel search --repo "Euro Office" "<query>"` searches each member
  corpus and returns `{schema_version: 2, organization, transport,
  repositories}` with a complete search payload per member. `--k` applies per
  member; an organization-wide overlay is rejected because overlays belong to
  individual repos. Membership alone does not enable indexing: configure each
  member's `[repos."<name>"]` entry and opt in separately; paths are inferred.
  Other commands retain their individual-repository scope.

- **raptor** `regen` and `build` read their two prompt files from
  `system-instructions/` in this corpus (`raptor-summary.md` and
  `raptor-request.md.tmpl`); the `MYCEL_SYSTEM_INSTRUCTIONS` environment
  variable names another folder. A missing or empty file stops the run with
  an error.
- **activity** reads the `kn_activity` feed — one row per completed
  sync/embed/overlay/raptor run, written by the shared library so daemon and
  CLI runs alike appear (actor column says which). No-op passes are never
  logged (fresh-on-read runs one on nearly every search).
- A disabled repo (config `enabled = false`) ingests AND embeds nothing — the
  pause switch.

## Repository corpus binding

`~/.mycel/config.toml` is the authoritative repository-to-corpus mapping.
`[repos."<repo>"]` may independently specify `code_root` and `artifact_root`:

```toml
[repos.core]
enabled = true
profile = "voyage"
code_root = "/Users/example/repos/euro-office/core"
artifact_root = "/Users/example/Artifacts/euro-office/repos/core"
```

The example's indexing flag/profile are independent settings, not requirements
for the folder layout. Preserve existing flags when changing paths. Creating
a folder or joining an organization does not itself opt a repository into
indexing; adding a new mapping may use `enabled = false`.

For organization members, place repository-specific artifacts under
`~/Artifacts/<org-directory>/repos/<repo>/`. Keep organization-wide research
under `~/Artifacts/<org-directory>/researches/`. Standalone corpora keep their
flat layout. Existing `~/Artifacts/<repo>/…` examples should be expanded using
the configured root. Source Ref identities remain `repo:relative/path`, with
the path relative to that repository's configured corpus, rather than the
organization's container directory.

The shared `mycel.locations.RepositoryLocations` resolver reads current file
settings and discovers direct Git checkouts / worktree containers through the
existing Organizations catalog. Its location precedence is:

1. The historical Arbol environment override (`ARBOL_KN_CORPUS` or
   `ARBOL_KN_CODE_ROOT`), when set.
2. Explicit repository `artifact_root` / `code_root` from the settings file;
   supplied database flags act as a compatibility cache.
3. Organization membership: code stays in the discovered checkout;
   artifacts use `~/Artifacts/<checkout-org-directory>/repos/<repo>/`.
   Optional `[organizations."<name>"].artifact_root` replaces the organization
   corpus root while retaining the `repos/<repo>` suffix.
4. Existing standalone defaults (including Arbol's historical folder spelling).

Sync, generated code maps, search-result files, browser/editor operations and
repository listings share this resolver. CWD scope uses the longest matching
configured code/artifact root and preserves worktree overlays. New organization
checkouts acquire a corpus location without a per-repository path entry;
membership does not enable indexing. Existing flat corpora can be retained
through explicit repository overrides without moving their contents.

Repository keys remain globally bare names. If multiple organizations contain
the same repository key, inference fails and requests an explicit `code_root`
rather than choosing an organization arbitrarily. This selects one corpus for
that key; fully independent namespaced identities need a separate migration.
An organization-name search still fans out to member corpora; it does not index
organization-wide research into a separate Mycel corpus.

These statements describe the checked-out source implementation. Installed
executables must be rebuilt to acquire the new resolver.

<!-- sources:
mycel:mycel/config.py#dumps
mycel:mycel/config.py#apply
mycel:mycel/locations.py#RepositoryLocations
mycel:mycel/syncpass.py#artifact_root
mycel:mycel/syncpass.py#code_root
mycel:mycel/retrieval.py#_read_location
mycel:mycel/knowledge/fs.py#corpus_root
mycel:mycel/scope.py#resolve
mycel:mycel/organizations.py#members
mycel:mycel/repo_identity.py#canonical_repo
-->

**Keeping the index warm without a daemon** (optional — fresh-on-read already
guarantees correctness): per-worktree git hooks and/or a Claude Code hook that
run `mycel sync --no-embed >/dev/null 2>&1 &` on commit/checkout/session-start.

<!-- sources:
mycel:mycel/cli.py
mycel:mycel/retrieval.py
mycel:mycel/syncpass.py#run_pass
mycel:mycel/syncpass.py#run_repo_pass
mycel:mycel/knowledge/embedder.py#code_search
mycel:mycel/knowledge/raptor.py
-->
