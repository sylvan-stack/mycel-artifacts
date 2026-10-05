---
role: authored
---
# Runbook: mycel

## Why it exists

The daemon-less knowledge tool: one process per job, direct to Postgres,
query embeddings via the configured embedding provider. It is how any agent
searches the corpus, keeps it fresh, manages worktree overlays, and mirrors
external surfaces. Settings live in **`~/.mycel/config.toml`** (repositories,
database, embedding, and mirror settings). Brain Recipes are owned separately
by Infer in **`~/.infer/config.toml`**. Mycel may read another product's
databases and logs as data, but it never depends on that product's code or
instructions.

## Use

```
mycel search "<query>" [--k N] [--repo R] [--overlay BRANCH] [--only code|docs] [--no-fresh]
mycel better-grep [grep flags] PATTERN [PATH...]   # also installed as `better-grep`
mycel sync [--no-embed]        # one mechanical Sync Pass, then exit
mycel embed [--overlay REPO@BRANCH]... [--include-overlays]
                               # embed pending base-repo chunks; overlays only
                               # via --overlay (scoped) or --include-overlays
mycel pull <repo> [--no-sync] [--no-embed]   # FF master for a container repo, then ingest
mycel status [--repo R]        # index freshness: pending embeds, last sync, stale counts
mycel activity [--k N] [--repo R] [--kind K]   # recent sync/embed/overlay/raptor/pull feed
mycel drifts [--repo R]        # Detection findings: docs whose cited code changed
mycel derive '<child-ref>' '<source-ref>'  # assert source governs derived code/doc/test chunk
mycel overlay add|list|refresh|drop [repo] [branch] [--worktree PATH] [--embed]
mycel wt add|list|refresh|drop|open [repo] [branch]   # worktree + overlay together
mycel wt add <repo> --mr <iid>       # fetch a GitLab MR head into a worktree (needs glab)
mycel wt drop <repo> <branch> --force # discard local changes in the worktree
mycel wt open [repo] <branch-fragment>  # fuzzy-open a worktree in VS Code
mycel repos [list] [--root PATH] [--organization NAME]     # repos under ~/repo + mycel-enabled/container/worktrees
mycel raptor status|plan|regen|build [--recipe NAME] [--repo R]   # default recipe: raptor-agent;
                               # recipe is resolved by the independent `infer` executable;
                               # no Arbol daemon or provider fallback is used
mycel secrets set|is-set|list|delete <name>          # write-only: no get, ever
mycel mirror fetch <jira|confluence|gitlab> <ref> [--closure] [--depth N] [--max-pages N]
mycel mirror tree confluence <space-key | page-id | url> [--max-pages N]
mycel mirror refresh [surface] [--older-than-min N]
mycel jira get <key> [--expand changelog] | search '<jql>' [--max N] | comments <key>
mycel jira create '<fields-json>' | update <key> '<body-json>' | comment <key> '<text>'
mycel jira transitions <key> [--expand transitions.fields] | transition <key> <id> ['<fields-json>']
mycel jira insight '<iql>' [--schema ID] [--max N]
mycel confluence create --space KEY --title T (--body MD | --body-file F) [--parent REF] [--format markdown|storage]
mycel confluence update <id-or-url> (--body MD | --body-file F) [--title T] [--format markdown|storage]
```

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
  `--no-fresh` skips.
- **wt** owns the full worktree + Branch Overlay lifecycle, daemon-less: `add`
  creates the git worktree (attaches a local ref; fetches from origin if the
  branch is remote-only), seeds the repo's Env Keepers, and ingests the
  overlay — **embedding is on-demand**: chunks stay pending until
  `mycel embed --overlay <repo>@<branch>` or the Elma status bar's
  "Embed N chunks"; `--mr <iid>` fetches a GitLab MR head into a worktree (via
  `glab`); `list` joins on-disk worktrees with overlay state
  (chunks/embedded/pending/merged, `droppable` when merged);
  `open <fragment>` fuzzy-opens a worktree in VS Code;
  `refresh` re-diffs; `drop` removes overlay + worktree together (dirty guard,
  `--force` to discard). This is the sole home for the worktree lifecycle — it
  is pure git/filesystem/overlay work with no Arbol daemon, so it lives in
  `mycel`; it has no daemon or host-application dependency.
- **repos** lists repos under `~/repo` (`--root` overrides) with each repo's
  mycel-enabled flag, embedder profile, whether it is a Worktree Container (and
  its worktrees), and whether it has an Artifact Corpus — the daemon-less twin
  of the mycel-client `repos.list` RPC (the Seqoya/Elma UIs still use the RPC).
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

- **secrets** are write-only (PATs for the mirrors); no read path ever exists.
- **mirror** fetches Jira tickets / Confluence pages / GitLab MRs into
  `~/Artifacts/mirrors/<surface>/` (local-profile corpus; company text never
  leaves the machine). `--closure` follows a ticket's linked pages/issues.
  Jira tickets also write the complete raw payload (`<KEY>.json`); both Jira
  and Confluence auto-download image attachments (`mirrors/<surface>/<ref>/`,
  ≤15 MB each, idempotent) — listed in the `.md`'s `## Attachments` for
  agents to READ. Confluence `--depth N` mirrors a page's descendants too
  (section fetch, capped by `--max-pages`, default 100).
- **mirror tree** writes a Confluence space's page tree — titles, links,
  hierarchy, NO content — to `mirrors/confluence/trees/<KEY>[-<root>].md`;
  metadata-only (~1 request per 100 pages), so it is cheap at any space size.
  A page ref instead of a space key renders just that subtree.
- **jira** is the full Jira Data Center surface: reads
  (get/search/comments/transitions/insight) and actions
  (create/update/comment/transition). PAT from the Keychain (`jira-pat`);
  a write on an already-mirrored ticket re-fetches its mirror.
- **confluence create/update** complete the write surface (the agreed
  exception to mirror one-way-ness — operations/external-mirrors.md):
  markdown converts to storage XHTML (`--format storage` passes through raw),
  and every write immediately re-fetches the page's mirror.
- **pull** advances the `master` branch of a [Worktree Container](../../arbol/GLOSSARY.md#worktree-containers)
  (pass the repo name): `git fetch origin` then a
  **fast-forward-only** merge in the `master/` worktree — never a force, so a
  diverged master is reported, not overwritten (master is clean corpus source).
  After a successful pull it runs one Sync Pass to ingest+embed the new code
  (`--no-sync` = git only, rely on fresh-on-read; `--no-embed` = chunk now, embed
  later). Skips the sync when no master advanced. Exit 1 only if every target
  failed to pull.
- **activity** reads the `kn_activity` feed — one row per completed
  sync/embed/overlay/raptor/pull, written by the shared library so daemon and
  CLI runs alike appear (actor column says which). No-op passes are never
  logged (fresh-on-read runs one on nearly every search). The same feed renders
  on Seqoya Lab's Dashboard as "Recent activity".
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
mycel:mycel/knowledge/embedder.py#code_search
mycel:mycel/mirror.py
mycel:mycel/jira_actions.py
mycel:mycel/confluence_write.py
-->
