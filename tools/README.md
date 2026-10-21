---
role: authored
---
# Tool guides

These manuals describe the commands and library boundaries that exist today.
The Instructions Hub routes here; [the catalog](../INDEX.md) lists the guides.
Keep examples fictional and put no credentials, account data or run transcripts
in these files. Implementation claims must agree with the current program.

## Mycel 2 guide originals and copies

The repository files under `docs/` are the originals of these 19 guides:
`activity`, `capture`, `classification`, `drifts`, `embedding`, `evidence`,
`generated`, `identity`, `origins`, `overview`, `parsing`, `pin-observation`, `reading`,
`reconciliation`, `relations`, `retrieval`, `source-refs`, `store`, `summaries`.
Change the original with the code it describes, then remake its corpus copy.
The copy is `tools/mycel-2-<name>.md`; it adds authored frontmatter and rewrites
local guide links to this folder's `mycel-2-*.md` names. A link to
`command-line.md` becomes `mycel-2.md`. No body wording is changed.

From the repository checkout, use the explicit corpus destination:

```sh
python3 scripts/sync_guides.py check --corpus /path/to/mycel/tools
python3 scripts/sync_guides.py write --corpus /path/to/mycel/tools
python3 scripts/sync_guides.py write --corpus /path/to/mycel/tools --guide activity
```

`check` is read-only and exits 1 if any original or copy is absent or differs.
`write` replaces the selected copies; keep a backup before replacing existing
work. Repeated `--guide` options select a subset; without them all 19 are used.
The command never chooses the owner's corpus from their settings or home.
`tests/test_guide_copies.py` exercises rendering, every declared guide and drift
refusal in temporary directories, so `make check` also works in a standalone
clone and in the isolated installed Build checks. The explicit `check` above
verifies the actual external copies when publishing.

Read the originals before editing. A technical word such as `pending` can be a
real reply state; remove obsolete claims about missing implementation while
preserving the program's names. Any implementation still missing names the
open Beat responsible for it. Other guide families keep their existing Arc
owners and are outside this synchronization command.

<!-- sources:
mycel:@code/scripts/sync_guides.py
mycel:@code/tests/test_guide_copies.py
-->
