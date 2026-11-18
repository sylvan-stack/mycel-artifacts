---
role: authored
spec: MYC-8
status: accepted
---
# Mycel · 08 Summaries

A question such as "how does sign-in work here" is broader than any one section. Summaries answer it: Mycel groups the sections of a repository's documents that are about the same thing, has one short summary written for each group, and groups the summaries again. Each summary is a chunk of its own that a search can find. This specification fixes what is grouped and how, who writes the text, how a summary is stored and kept in step with its sections, and how summaries appear in a search. It matters because, as read from the source, version 1's command for this could not run, it deleted the old summaries before it could fail, and it depended on a program that is now deprecated.

Version 1 called this RAPTOR, after the method it follows, and the Glossary has it under [RAPTOR Tree](../../arbol/GLOSSARY.md#raptor-tree) and [Summary Node](../../arbol/GLOSSARY.md#summary-node).

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: what is summarised, grouping and levels, the command that writes the text, the request it is given, how a summary is stored, building a set of summaries, writing stale ones again, status and removal, quiet-period maintenance, and summaries in a search.

Not covered: generated edges as a kind of edge ([MYC-7](07-drifts-and-verification.md#generated-edges)); the classification and work lifecycle of [MYC-14](14-drift-detection.md); how a summary is embedded ([MYC-3](03-embedding.md)); the overview of a repository's code, which no model writes ([MYC-9](09-code-overview.md)).

## Behaviour

### What is summarised

Observed in version 1, and kept: the sections of one repository's documents that had a vector, except those of documents that are [Heartwood](../../arbol/GLOSSARY.md#heartwood) or declared `generated`. Code was not summarised, and neither were earlier summaries.

Proposed: the sections of the repository's documents that are on disk and fully embedded with the current model (MYC-3), from documents that are neither Heartwood nor declared `generated`. A section that is left out only because it is not embedded yet is counted in the reply, so that the owner can embed first.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/raptor.py#build_tree`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#plan_build`

### Grouping and levels

Observed in version 1: sections were grouped by their vectors with a standard statistical method.

| Step | What version 1 did |
|---|---|
| Simplify | Each vector was reduced to 10 numbers, by principal component analysis |
| Choose the number of groups | For every number of groups from 1 up to one for each 8 sections, and never more than 150, a mixture of Gaussian distributions was fitted, with one spread for each group. The number with the lowest Bayesian information criterion (BIC) was taken, the smaller number winning a tie |
| Assign | A section joined every group it fitted with a probability of 0.10 or more, so one section could sit in two groups. A section that reached 0.10 nowhere joined its likeliest group |
| Repeat | The random numbers started from a fixed value, so the same vectors always gave the same groups |

Groups were built in levels. Level 1 summarised sections. Level 2 summarised the summaries of level 1, and so on up to level 5. Building stopped when 10 or fewer nodes were left at the top, counting summaries and members that had moved up. A group of one was not summarised: its member moved up a level as it was. Nothing stopped the build early when a level produced no summary at all (inferred from the source, not seen happening).

Proposed: kept, with that stop added. A section whose text was embedded in several parts (MYC-3) is placed by the mean of its parts' vectors. The mean serves grouping only; a search still compares every part (MYC-4.27). The numbers above are starting values and change only with an evaluation report, by the rule of [MYC-D20](04-retrieval.md#decisions).

The exact initial grouping profile is `mycel-summary-v1`: canonical root/path/position order; random seed 0; spherical covariance with regularisation `1e-4`; PCA dimensions `min(10, vector dimensions, n - 1)` when reduction is needed; and candidate group counts `1..min(150, n - 1, ceil(n / 8))`. Zero members give no groups; one or two give one group. Empty groups are discarded. Equal BIC chooses the smaller count, and equal highest membership probability chooses the earlier component. The pinned numerical dependency versions of the Build (MYC-15) and this profile are recorded with the set. A non-finite vector or failed fit is a reported grouping failure, never silently a different algorithm.

A fictional repository with 400 sections gives about 31 summaries at level 1 and 4 at level 2. Four is fewer than ten, so the build ends there.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/clustering.py#cluster`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#build_tree`

### Who writes the text

Observed in version 1: Mycel wrote no summary itself. For each one it started a program called `infer`, which belonged to the stack and is now deprecated. It looked for that program in four places, gave it the name of a model and the instruction as arguments and the request on standard input, and took its standard output as the summary. A request had five minutes and one attempt. Up to 24 ran at the same time.

Decided in MYC-D102: Mycel ships [Narrator](22-narrator-summary-quality.md) and uses it as the sole RAPTOR writer for builds and regeneration. The operator configures the reasoning adapter it calls in `summaries.model_command`. Narrator runs in reasoned mode and verifies proposed claims before it assembles the prose. Mycel passes any configured prompt override to the same writer.

- Mycel starts the command once for each summary, without a shell, in an empty folder of its own, so that the program finds no instructions of some project lying around.
- The whole request goes to its standard input. Nothing of it is in an argument.
- Its standard output is the summary, decoded as UTF-8. A status other than 0, invalid UTF-8, an empty/whitespace-only answer, or no answer within five minutes is a failure. Capture at most 1 MiB stdout and 64 KiB stderr; overflow terminates the process group and fails the request. A failed summary is tried once more and then recorded as failed with a redacted reason; raw stderr and credentials are not copied into replies or activity.
- At most `summaries.at_once` run at the same time.
- The model adapter selects the provider, model and account and returns the structured responses Narrator requests.

Without an available model adapter, an actual `build` or `regenerate` is refused with `settings`. A dry-run, status, removal and search still work. The adapter uses literal argv with an absolute executable or a leading `~/`. The retired `summaries.command` setting is recognized so older configurations remain readable. It never selects or launches a writer. Instruction overrides must contain both UTF-8 files and exactly one `$sections` mark in the task; invalid overrides return `settings` before any request is sent.

Narrator’s configured adapter is the external model boundary for summaries. MYC-14 separately defines the configured smarter-review command and direct Jev classification. Mycel directly calls the fixed embedding and Jev services; provider selection for summaries and review belongs to the configured commands (MYC-0.10). Only the explicit commands that request generation or classification spend those calls.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/completion_client.py#_infer_bin`
- `mycel_deprecated_v1:mycel/completion_client.py#_run_infer`
- `mycel_deprecated_v1:mycel/completion_client.py#run`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_raptor`

### The request

Observed in version 1: the request was an instruction and a task, each read from a file in the document corpus of the repository called `mycel`, again for every summary. A missing file stopped the command. Observed on 6 October 2026: cleaning up that folder would have broken the command. Below the task came the group's sections. Each was cut to its first 1,200 characters, and sections were added until 48,000 characters were reached; the rest of the group was left out. Nothing fixed the order of the sections, so nothing fixed which were left out. Every section of the group was still joined to the summary by an edge, read or not.

Proposed:

- **Two texts, built in.** The instruction and the task are part of the program, with version 1's wording. The setting `summaries.instructions` names a folder whose two files replace them, under version 1's file names: `raptor-summary.md` and `raptor-request.md.tmpl`. The second holds the mark `$sections`, in whose place the sections are put, as in version 1.
- **Whole sections, in a fixed order.** Each section is given with its place line (MYC-3) and its complete text, in the order of path and position.
- **Nobody is left out.** Count the complete rendered request in Unicode code points, including instruction, task, place lines and separators. A group whose request would pass 48,000 characters is divided in two, in that order, until every part fits. Each part gets a summary of its own, so every edge joins a summary to sections it was written from.
- **One exception.** A single section longer than a whole request gets a request to itself, cut to the limit. Append `[Mycel: source text cut at request limit]` after the retained prefix and include that notice in the character budget. The reply names every section this happened to. If the fixed instruction/task framing alone reaches the limit, return `settings` before any call; never send a framing-only request or omit the cut notice.

```text
You summarise clusters of related project documentation so the summary can be retrieved on its own. Be faithful and self-contained.

Write a concise, self-contained summary of the following related documentation sections. Capture the key points and how they relate, with no preamble.

docs/net.md › Retry policy
Requests are retried three times, with a longer pause each time.

---

docs/limits.md › Limits > Backoff
The pause doubles after every failed attempt.
```

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/raptor.py#_instruction`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#_raptor_prompts`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#_prompt_sections`

### How a summary is stored

Observed in version 1: a summary was a chunk without a file, attached to one made-up document per repository, with its level, and joined to every member of its group by a generated edge that stored the member's hash. The summariser sent each summary to the external embedding service itself, whatever the repository's settings said about embedding.

Proposed: a summary is a chunk of its repository with the origin `summary`. It has no file. Its place is `summaries`, with the level and a number as its name: `cellar:summaries#1/7`. Its text is what the command printed, kept whole. Each member is joined to it by a generated edge ([MYC-7](07-drifts-and-verification.md#generated-edges)). The immutable MYC-16 manifest retains the exact member selections and snapshots, canonical request bytes/hash, prompt profile or override hashes, command argv and published response. A cut request records exactly the cut text sent as well as the full source snapshot; no edge claims that an omitted member was read.

A summary is embedded by the rules of MYC-3, like any chunk of an enabled repository. A build embeds the summaries of a level before it groups the next one, because the next level is grouped by their vectors.

A summary comes from no file and has no location. It stays until a build puts another set in its place, `regenerate` deletes it, `remove` is run or its repository is removed; the rule that deletes what is found in no location (MYC-1.21) is for chunks that come from files. For a search and for `mycel read` a summary counts as on disk.

The place of a summary can be read ([MYC-11](11-reading-a-chunk.md)). It is not accepted as a Source Ref or in a relation, because a claim does not rest on generated text. Such a ref in a file is reported as a fault (MYC-2.6), and `derive` or `relate` naming a summary is refused with `invalid_input`.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/raptor.py#_insert_summary`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#_summary_doc_id`
- `mycel_deprecated_v1:mycel/knowledge/store.py#derive`

### Building

Observed in version 1: a build first deleted every summary of the repository and its edges, and then wrote the new ones. A failure after that left the repository without summaries. A request that failed was reported as a build that had been cancelled, and the reason was not kept. A plan could be asked for first: it grouped level by level, using the mean vector of each group in place of the summary not yet written, and wrote nothing.

Proposed: `mycel summaries build` writes a complete new set beside the old one. Only when every level is done does the new set take the old one's place, in one transaction ([MYC-6](06-index-store.md#transactions)). A build that fails or is stopped leaves the old summaries as they were and discards what it had written; the reply names the summary that failed and the reason.

With `--dry-run` it reports the shape a build would have, the levels with their groups and the number of requests, as version 1's plan did. Higher levels use the mean member vectors as a stand-in for a summary vector, so the plan is explicitly an estimate. It starts no command, sends no embedding request, runs no freshness pass and writes nothing.

A real build snapshots its inputs and stages text, vectors and evidence apart from searchable rows. Before publication it rechecks required source inputs under the repository lock (MYC-16); changed or missing inputs discard the staged set and return `stopped: "inputs_changed"`. The old set remains untouched. An empty eligible input set successfully replaces the old set with an empty one. Summary numbering is assigned by canonical group-member order within each level; a replacement may reuse a readable place but receives a new chunk version and immutable evidence. Neither a request failure nor an embedding failure publishes an incomplete set.

An actual build/regeneration takes a nonblocking per-repository summary-operation lock until all subprocesses, staging and publication end; a second summary mutation or removal returns `busy`. Snapshot/staging and publication transactions also take the pass lock, which is released during model/embedding calls so ingest can proceed and obsolete the staged inputs. Repository removal must acquire the summary-operation lock before deleting its evidence (MYC-6). In-flight snapshots use the exact invocation liveness of MYC-12. On interruption, terminate subprocess groups and cancel embedding calls, discard an unpublished build, and preserve already published regeneration successes.

A build is the only way a section enters a summary. It is never started by a pass or by a search: writing summaries spends calls to a model and waits for a person.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/raptor.py#build_tree`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#_clear`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#plan_build`

### Writing stale summaries again

Observed in version 1: a summary was stale when a member's hash differed from the one its edge stored. One action wrote the stale summaries again, lowest level first, each in its place and with the members it had. A summary none of whose members were left was skipped and stayed stale for good. A removed section did not make its summary stale at all, because its row stayed (inferred).

Proposed: a summary is stale when a member changed or is gone ([MYC-2](02-provenance-and-freshness.md#detection), [MYC-7](07-drifts-and-verification.md#when-a-source-is-deleted)). `mycel summaries regenerate` writes only the stale ones again, lowest level first, so that a rewritten summary of level 1 feeds the one above it. A summary keeps its place and the members that still exist, and its edges are pinned to them. A summary with no member left is deleted. One whose request fails stays stale. With `--dry-run` the command says which summaries it would write or delete and which are blocked. It performs no freshness pass, writes nothing and sends no generation or embedding request.

Each successful regeneration publishes text, current-model vectors and new MYC-16 pins atomically after checking the exact inputs under lock; an input changed meanwhile leaves the old summary stale and records `inputs_changed`. Independent successes remain when a later summary fails. A higher summary with a failed or otherwise still-stale generated member is blocked and stays stale, rather than being regenerated from obsolete text. The reply distinguishes blocked work from requests that failed. Places and membership stay fixed except for missing members; regeneration does not regroup.

Which sections belong to which summary changes only in a build. Sections added since the last build are in no summary; the status counts them, which tells the owner when a build is due.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/raptor.py#regen_stale`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#_stale_members`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#plan_regen`

### Quiet-period maintenance

`mycel maintain --repo <name>` checks one explicitly selected enabled repository. It observes current on-disk document inputs in the repository’s code and Artifact roots using the normal scan rules. First observation, edits, additions, moves and deletions start a 15-minute quiet period for that repository. A different repository has its own timer. Code-only inputs do not reset the timer. A complete observation must be stable before work is admitted; an unreadable, interrupted or incomplete observation cannot authorize provider work.

Each invocation is finite. It persists the observation digest, due time and completion state outside the index, under a repository-specific lock. A completed unchanged observation returns without touching the store or calling providers. When due, ingest, embed pending on-disk document sections and regenerate existing stale summaries in that order. Recheck the observation between stages. A changed observation defers further work and starts a fresh quiet period. Regeneration uses the configured Narrator adapter and never broadens into a full tree build. New sections become directly searchable after ordinary indexing and embedding.

Keep unfinished work due for a later invocation with a 15-minute retry delay for the same inputs. Existing per-operation guards and atomic commits preserve completed work. When stale summaries need an adapter and none is configured, report that condition. A macOS LaunchAgent can invoke the command once a minute for each explicitly selected repository, and runs depend on that agent being installed by the operator. No scheduler is enabled by default.

### Tree browser and sentence labels

`mycel summaries browse --output <file>` exports a private, self-contained HTML page with all published, nonempty summary sets in the selected index store. It reads one repeatable snapshot. The export performs no generation, embedding or network requests beyond opening that store. It never replaces an existing output file. Each available repository starts as a collapsed branch. Cmd+Click on its name expands its top labels four spaces deeper. Each repository stays visible and can be expanded or collapsed independently. An ordinary click on a name leaves the tree unchanged.

The page displays repository names, node labels and selected text as plain text. Cmd+Click on a label opens that node’s full text in place. Cmd+Click on summary text shows its children below it, indented by four spaces at each level. Sibling branches stay visible and can be expanded independently. Use the source section name, or the file name when there is no section name, to label a document child. Opening it shows the exact retained chunk version pinned by its parent. Shift+Click on opened text hides its children first, then restores its label. Shift+Click on an expanded repository name or one of its collapsed top labels hides only that repository’s descendants. Shift+Click on any other collapsed child hides its parent’s child list. Opening a shared node under one parent does not open it under another. Show a boundary while Cmd or Shift is held over actionable text. Tab focuses text, Enter or Space opens it, and Escape goes back from the focused text. Current Summary Nodes link through their published logical member IDs, so stale parents can show a current child version. Show retained source text when a member lacks a current Summary Node.

Build and regeneration ask bundled Narrator for a sentence label from the generated summary text and store it with the exact published summary version. A label has one terminal sentence mark and at most 20 whitespace-separated words, including function words. Label failure follows ordinary summary publication failure. Existing unlabeled summaries remain browsable using their addresses as fallback labels. The explicit `mycel summaries labels --repo <name>` command backfills missing labels without generating new summary prose or embeddings. It keeps labels that are already stored and publishes a batch only if the captured versions are still current.

### Source-ordered Artifact reader

`mycel summaries ordered <artifact> [<artifact> ...] --output <file>` captures each explicitly selected UTF-8 text Artifact from disk and exports independent trees in argument order. Each tree uses one capture and divides it into contiguous child ranges in source order. A tree never interleaves two Artifacts. Include all content from the capture, including headings, preambles, whitespace and line endings. Use heading boundaries for Markdown and split long ranges as needed. Refuse files that cannot be read as UTF-8 text. Each private HTML export retains its source versions and never overwrites an existing path.

When a Narrator reasoning adapter is configured, generate an overview for each bounded group of ranges where possible using bundled Narrator and its sentence labels. A parent may summarize its ordered child summaries. Grouping and model work require no index or embeddings. A missing adapter, a range with no substantive body, or a failed generation leaves the same branch navigable through its source ranges. Reports count generated and unavailable summaries.

Cmd+Click opens a branch in place, from its label through any summary and down to the original text. Shift+Click reverses one step and sibling branches stay visible. Once a branch shows its children, its summary prose leaves the reading flow. When all text ranges for an Artifact are visible, their concatenation is the exact captured UTF-8 text from beginning to end. Modifier hover highlights the actionable text. Tab, Enter or Space, and Escape provide the corresponding keyboard access.

### Summaries in a search

Observed in version 1: a search that included documents took summaries among its document candidates. A summary could become a result where a document could. It was never followed to code, and a search for code only left it out. A summary result named no file to read.

Proposed: kept. This adds to [MYC-4](04-retrieval.md):

| Search | Summaries of the searched repository |
|---|---|
| Documents and code | Compete as documents do: the same margin over the best code match, and counted in the same limit of two (MYC-4.13) |
| Documents only | Ordinary results |
| Code only | Take no part |

A summary is never one of the sections from which the search follows Source Refs to code: it cites nothing. Summaries of another repository take no part, shared documents or not. A summary result has the origin `summary`, says whether it is stale, and names no file; it says that the text is kept in the index and is read with `mycel read`.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#doc_search`
- `mycel_deprecated_v1:mycel/retrieval.py#_read_location`

## Requirements

| ID | Mycel must… | From v1 | Verified by |
|---|---|---|---|
| MYC-8.1 <!-- 5f0b0cdc-41cb-4b7b-b5c8-7e2d8e336839 --> | summarise the sections of one repository's documents that are on disk and fully embedded, leaving out Heartwood documents, documents declared `generated`, code, sections of the code overview and summaries | Kept | store |
| MYC-8.2 <!-- 7fdbfe9c-fc8e-4e18-9ac0-5e99a16a6fb8 --> | count in its reply the sections left out because they are not embedded | New | store |
| MYC-8.3 <!-- 2dc8d10b-f545-415d-b6ef-0407f10b6239 --> | group by the vectors with version 1's method and starting values, give the same groups for the same vectors, and place a section embedded in several parts by the mean of its parts' vectors | Kept | unit |
| MYC-8.4 <!-- 31691e3c-205a-46b6-a574-388fad23e55d --> | build in levels up to five, stop when ten or fewer nodes are left at the top, summaries and members moved up counted together, or when a level produced no summary, and move a group of one up a level without a summary | Changed | unit |
| MYC-8.5 <!-- 7de52396-3f80-4e7a-b79b-5a63a9c8aaab --> | start bundled Narrator as the sole writer for each summary, without a shell, in an empty folder, with the whole request on standard input. Only its model adapter is configurable | Changed | unit |
| MYC-8.6 <!-- 56a7722d-3cb4-459f-972f-9da530a76af7 --> | take a status other than 0, an empty answer and no answer within five minutes as a failure, try a failed summary once more, and record the reason of one that failed again | Changed | unit |
| MYC-8.7 <!-- 28e6ea78-61a6-48fd-abb6-24e5f4d60686 --> | run at most `summaries.at_once` requests at the same time | Changed | unit |
| MYC-8.8 <!-- 5b835649-7c2c-4830-bae5-f1c8abe293b7 --> | refuse actual `build` and `regenerate` with `settings` when no available Narrator model adapter is configured. Keep dry-runs, status, removal and search working, including for older configurations | Changed | unit |
| MYC-8.9 <!-- e5f45a54-fbd6-4517-96f5-039e3a0c2ec1 --> | make each request of an instruction, a task and the group's sections, each section with its place line and its complete text, in the order of path and position | Changed | unit |
| MYC-8.10 <!-- dacc6330-8c09-4f3e-89ee-3dd60aea9b23 --> | divide a group whose request would pass 48,000 characters until every part fits, and write a summary for each part, so that no section of a group is left out | Changed | unit |
| MYC-8.11 <!-- dfa3c19c-52aa-4f57-95d3-5715f807e7ce --> | give a single section that is longer than a whole request a request to itself, cut to the limit, and name it in the reply | New | unit |
| MYC-8.12 <!-- bd80a339-0709-4c51-92fc-78f3289cb6ac --> | take the instruction and the task from the folder `summaries.instructions` when the settings name one, and otherwise from the texts built into the program, putting the sections in the place of the mark `$sections` in the task | Changed | unit |
| MYC-8.13 <!-- d1893d1e-48e9-41d1-8b9e-077d9fd1c3af --> | store a summary as a chunk with the origin `summary`, its level, the whole text the command printed, and a generated edge from every section it was written from | Kept | store |
| MYC-8.14 <!-- 2f4ddee5-1e7b-45a9-a11c-6a6f0c634a90 --> | embed summaries by the rules of MYC-3, and in a build embed each level before grouping the next | Changed | store |
| MYC-8.15 <!-- 77109e08-f642-4e16-b941-2f380412663d --> | put a new set of summaries in the old one's place in one transaction, only when every level is complete, and otherwise leave the old set untouched | Changed | store |
| MYC-8.16 <!-- c9f4dc35-051d-49a8-95f0-20fb53c123a7 --> | report with `--dry-run` the levels, groups and number of requests of a build, or the summaries a `regenerate` would write, starting no command and writing nothing | Kept | store |
| MYC-8.17 <!-- 75172d5c-2e65-4606-8b8d-9931c46bee42 --> | write again, on `regenerate`, only the stale summaries, lowest level first, each in its place with the members that still exist, and pin its edges | Kept | store |
| MYC-8.18 <!-- 2527c9ba-fd41-4fc2-ac06-4957fda33d8a --> | delete a summary that has no member left, and leave stale a summary whose request failed | Changed | store |
| MYC-8.19 <!-- 1304c052-b610-4a82-8404-7a19c0138951 --> | never write or rewrite a summary in a pass, a search or any command other than `summaries build` and `summaries regenerate` | Kept | store |
| MYC-8.20 <!-- f70708a3-880f-4fbd-b173-256e197dccad --> | report for a repository the summaries of each level, how many are stale, how many sections are in a summary, in none, and not embedded, and whether a Narrator model command is set | Changed | store |
| MYC-8.21 <!-- 432e3a46-e88c-4ef5-b95e-5ba781a79d09 --> | remove every summary of a repository and its edges on request | New | store |
| MYC-8.22 <!-- 94867810-7e67-4ea9-95c8-2f2f72382fc1 --> | let summaries of the searched repository compete in a search as documents do, leave them out of a search for code only, never follow one to code, and return one with the origin `summary` and without a file | Kept | store |
| MYC-8.23 <!-- bc77a15e-279f-48e8-9225-01455063b5c9 --> | report a ref to a summary in a file as a fault, and refuse with `invalid_input` a `derive` or `relate` that names one | New | store |
| MYC-8.24 <!-- d0afd36d-1035-4428-b29d-a0154fcefe75 --> | use and record the deterministic `mycel-summary-v1` grouping profile and report invalid numerical inputs or failed fitting | New | unit |
| MYC-8.25 <!-- ecc1d34a-0f39-4315-b384-4dd7382ef3aa --> | validate the Narrator entry point, model command and prompt files before requests. Guard their identities and retain the exact invocation, request, response and member evidence under MYC-16 | New | store |
| MYC-8.26 <!-- 9a99738e-2428-4361-96df-03d928d3a2b5 --> | keep staged summaries and vectors out of searches, recheck exact inputs before publication, discard changed-input builds, and replace an empty eligible set atomically | New | store |
| MYC-8.27 <!-- e554625a-8b7d-4924-90c4-b6d44936c71b --> | publish each regenerated summary with its vectors and pins atomically, keep independent successes, and block parents whose generated members remain stale | New | store |
| MYC-8.28 <!-- d1d8effd-f5d2-4273-bfa5-013e08954675 --> | make summary status and both dry-runs read-only with no service calls, distinguish estimated build plans, and return complete regeneration/removal replies | New | store |
| MYC-8.29 <!-- 4494a6cb-ca43-4831-a8c6-79b933f9d80b --> | serialize summary mutations with a nonblocking summary-operation lock, release pass locks during external calls, protect in-flight evidence by exact invocation liveness and clean up subprocesses/staging on interruption | New | store |
| MYC-8.30 <!-- 5bbd1345-5b8e-4f4a-85b5-7ae3683feebc --> | admit background maintenance for one enabled repository only after 15 minutes of unchanged complete on-disk document observations. Persist the state and suppress duplicate runs with an exclusive repository lock | New | unit |
| MYC-8.31 <!-- 755dd3c3-eab0-4775-b8a9-300a118726b2 --> | on a due observation ingest, embed pending on-disk document versions, and regenerate only stale summaries. Recheck inputs between stages and retain unfinished work for later without invoking a rebuild | New | store |
| MYC-8.32 <!-- 0b22c6c7-35c6-4abd-8430-2d6143e1883b --> | expose one finite `mycel maintain --repo <name>` check and an opt-in macOS LaunchAgent that invokes it once per minute | New | unit |
| MYC-8.33 <!-- 2b252459-3fbb-4746-b9d2-3d10ff16949c --> | generate and validate a one-sentence label of at most 20 words for each new published summary version, and store it atomically with the summary | New | store |
| MYC-8.34 <!-- 74434112-d208-43cd-9e12-3358fd20780c --> | backfill labels for existing summary versions on explicit request without rewriting prose or vectors, and keep already labeled versions | New | store |
| MYC-8.35 <!-- e442241e-d05c-40eb-9a13-a2e14dbcbbd9 --> | export all published nonempty summary sets to one private standalone HTML file using retained memberships and text from one checked read snapshot | New | store |
| MYC-8.36 <!-- 0f477049-adf5-4af2-a7e4-8b0f153649fa --> | show published summary sets as independent plain-text repository branches. Let Cmd and Shift clicks open and close every level in place, with children indented four spaces per level, siblings preserved on expansion, modifier hover boundaries and keyboard access through the text | New | unit |
| MYC-8.37 <!-- 2a59fd74-d478-4b76-a1f2-b11bbe26abc3 --> | export source-ordered trees for explicitly selected UTF-8 text Artifacts. Capture each file once, partition its exact text into ordered contiguous ranges, and use bounded Narrator summaries when available | New | unit |
| MYC-8.38 <!-- 05908cad-0545-4f55-a3f4-a0d4ac4b00ad --> | open and close Artifact branches in place with Cmd and Shift while preserving visible siblings. Show all original ranges in their exact order when fully expanded, including when a summary is unavailable | New | unit |

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

```sh
mycel summaries status --repo handbook
mycel summaries build --repo handbook --dry-run   # the shape a build would have; nothing is started
mycel summaries build --repo handbook
mycel summaries regenerate --repo handbook        # only the stale ones
mycel summaries remove --repo handbook
```

Each of them takes one repository: the one named, or the one of the current directory. The name or the folder of an organization is refused with `invalid_input`, because summaries are written for one repository at a time. In this the commands depart from the Repository rule of MYC-0.

```ts
interface SummariesStatus {
  repository: string;
  commandSet: boolean;                 // whether a Narrator model command is configured
  builtAt?: string;                    // when the present set took its place
  groupingProfile?: string;            // "mycel-summary-v1"
  build?: string;                      // MYC-15 Build that published the set
  levels: Array<{ level: number; summaries: number; stale: number }>;
  sections: { inSummary: number; inNone: number; notEmbedded: number };
                                       // disjoint counts of eligible current document sections
}

interface SummariesPlan {              // build --dry-run
  repository: string;
  sections: number;
  levels: Array<{ level: number; nodesIn: number; summaries: number; movedUp: number }>;
  requests: number;
  estimated: true;                     // later levels substitute mean member vectors
  notEmbedded: number;
}

interface SummariesResult {            // build and regenerate
  repository: string;
  written: number;
  deleted: number;                     // regenerate: summaries with no member left
  replaced: boolean;                   // build: whether the new set took the old one's place
  failed: Array<{ summary: string; reason: string }>;
  blocked: Array<{ summary: Place; reason: "stale_member" | "inputs_changed" }>;
  cut: Place[];                        // sections longer than a whole request
  stopped?: "interrupted" | "failed" | "inputs_changed";
}

interface SummariesRegenerationPlan {
  repository: string;
  write: Place[];
  remove: Place[];
  blocked: Array<{ summary: Place; reason: "stale_member" }>;
}

interface SummariesRemoval { repository: string; removed: number }

// SearchResult of MYC-4 gains:
//   origin: also "summary"
//
// RefFault of MYC-2 gains:
//   fault: also "generated_text"     // the ref names a summary or a section of the code overview
```

`status` returns `SummariesStatus`; `build --dry-run` returns `SummariesPlan`; `regenerate --dry-run` returns `SummariesRegenerationPlan`; real `build` and `regenerate` return `SummariesResult`; `remove` atomically removes the current set and returns `SummariesRemoval`. Empty status, plans and removal succeed. Status reports stored state only. `inSummary`/`inNone` partition fully embedded eligible current sections by membership in the present set; `notEmbedded` counts otherwise eligible sections lacking complete current-model vectors, with no double counting. Levels are ascending and places within a level are in canonical order.

## Known problems in version 1

- **The command could not run as written.** The two actions that write summaries used a part of the language's library that the file never loaded (read from the source, not tried).
- **A build deleted before it could fail.** The old summaries were gone before the first new one was written.
- **A failure looked like a cancellation.** The reason of a failed request was neither returned nor stored.
- **Sections were cut and left out.** Each section was cut to 1,200 characters and a group to 48,000, in an order nothing fixed, while every section was still recorded as a source of the summary.
- **A summary with no section left stayed stale for good.**
- **A removed section did not make its summary stale.**
- **Summaries left the machine whatever the settings said.** They were always embedded by the external service.
- **The instruction was visible to other programs.** It was passed as an argument.
- **The prompts lived in a document folder.** Tidying that folder would have stopped the command.
- **It needed `infer`.** That program is deprecated, and Mycel 2 has nothing in its place until this specification is accepted.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/cli.py#_cmd_raptor`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#build_tree`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#regen_stale`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#_prompt_sections`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#_instruction`
- `mycel_deprecated_v1:mycel/completion_client.py#_run_infer`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D31 <!-- 4227641a-3f09-4e68-a076-1664dba1f8cf --> | Who writes the text of a summary, now that `infer` is deprecated? | A command the owner names in the settings, for example `claude -p`. Mycel starts it for each summary, gives it the sections and stores what it prints. This is what version 1 did with `infer`, with the program's name moved into the settings. Mycel then starts one program that is not its own, and summaries need that program to be installed and signed in. The other choice is that Mycel starts nothing: it hands the groups to whoever called it, an agent or Arbol writes the summaries and hands them back, and Mycel only stores them. Mycel would then stay free of any model, and a build would need a caller that does the writing | Decided 8 October 2026 by the owner: agreed. Superseded by MYC-D102 |
| MYC-D102 <!-- 8ad187e5-b934-4a69-8ad5-53bccf7c5f55 --> | Which writer can RAPTOR use? | Ship and always use Narrator for RAPTOR builds and regeneration. Configure its reasoning adapter through `summaries.model_command`. Recognize the retired writer key for reading old settings | Decided by the owner on 18 November 2026: Narrator is the only available RAPTOR summarizer |
| MYC-D103 <!-- 51b86704-f11b-4d80-9b9d-10e0c4cf8cc4 --> | How should quiet-period maintenance run? | Use a 15-minute per-repository quiet period after on-disk document edits and batch incremental embedding and stale summary regeneration. | Decided 18 November 2026 by the owner: implement the proposed quiet-period workflow |
| MYC-D104 <!-- a8f53c75-485f-4230-bedd-60cc0d9be94f --> | How can a user inspect the repository summary sets? | Generate a local HTML browser, with a label and full text at each Summary Node and reversible Cmd and Shift expansion. | Decided 18 November 2026 by the owner. Each summary stores a single-sentence label of up to 20 words |

## Named checks

Written by `scripts/name_checks.py` from the `proven` and `stated` Origin Links of the tests and a complete check report in which they passed. Each requirement keeps its kind in its Verified by cell and names here up to three of its passing checks: those of its own kind first, then those that rest on the fewest requirements. `mycel origins --repo mycel --path tests` lists every link. Do not edit this section by hand: run the script again.

| Requirement | Kind | Checks |
|---|---|---|
| `MYC-8.1` | store | `test_summary_store.SummaryStoreTests.test_eligibility_uses_exact_current_disk_sections_and_complete_current_vectors` |
| `MYC-8.2` | store | `test_summary_store.SummaryStoreTests.test_eligibility_uses_exact_current_disk_sections_and_complete_current_vectors` |
| `MYC-8.3` | unit | `test_summary_grouping.SummaryGroupingTests.test_real_pca_mixture_is_repeatable_and_input_order_independent`, `test_summary_grouping.SummaryGroupingTests.test_zero_one_two_and_multipart_means_keep_canonical_members` |
| `MYC-8.4` | unit | `test_summary_grouping.SummaryGroupingTests.test_five_level_limit_and_estimated_mean_nodes`, `test_summary_grouping.SummaryGroupingTests.test_invalid_split_cannot_omit_duplicate_reorder_or_substitute_members`, `test_summary_grouping.SummaryGroupingTests.test_top_target_singleton_promotion_and_no_summary_stop` and 2 more |
| `MYC-8.5` | unit | `test_summary_writer.SummaryWriterTests.test_literal_arguments_complete_stdin_empty_cwd_and_exact_utf8_output`, `test_summary_writer.SummaryWriterTests.test_success_also_terminates_background_descendants`, `test_summary_writer.SummaryWriterTests.test_user_path_resolves_executable_without_forwarding_private_environment` and 2 more |
| `MYC-8.6` | unit | `test_summary_writer.SummaryWriterTests.test_deadline_and_overflow_kill_process_group_and_reap_each_attempt`, `test_summary_writer.SummaryWriterTests.test_direct_interruption_cleans_up_and_does_not_retry`, `test_summary_writer.SummaryWriterTests.test_exact_byte_limits_succeed_and_missing_executable_has_safe_reason` and 4 more |
| `MYC-8.7` | unit | `test_summary_writer.SummaryWriterTests.test_parallel_and_direct_calls_share_limit_and_preserve_request_order`, `test_summary_writer.SummaryWriterTests.test_batch_interruption_terminates_all_running_requests_and_cancels_pending`, `test_summary_writer.SummaryWriterTests.test_settings_and_request_validation_happen_before_any_process_starts` |
| `MYC-8.8` | unit | `test_summary_request.SummaryRequestTests.test_cli_missing_command_checks_generation_before_pending_handler`, `test_summary_request.SummaryRequestTests.test_invalid_argv_and_overrides_refuse_before_requests_with_redacted_settings`, `test_summary_request.SummaryRequestTests.test_missing_writer_refuses_generation_but_report_and_dry_run_plan_need_no_command` |
| `MYC-8.9` | unit | `test_summary_evidence.SummaryEvidenceTests.test_fileless_higher_level_summary_has_exact_member_identity_and_no_mutable_source_pointer`, `test_summary_evidence.SummaryEvidenceTests.test_capture_keeps_raw_prompts_literal_argv_full_sources_and_canonical_immutable_manifest`, `test_summary_evidence.SummaryEvidenceTests.test_changed_framing_corrupt_descriptors_order_and_unsupported_comparison_are_refused` and 3 more |
| `MYC-8.10` | unit | `test_summary_request.SummaryRequestTests.test_recursive_halves_cover_every_member_with_complete_unicode_budgets`, `test_summary_grouping.SummaryGroupingTests.test_real_request_splits_count_each_part_without_promoting_cut_parts`, `test_summary_request.SummaryRequestTests.test_duplicate_or_cross_repository_members_and_corrupt_source_are_refused` and 1 more |
| `MYC-8.11` | unit | `test_summary_evidence.SummaryEvidenceTests.test_cut_keeps_complete_unicode_source_and_exact_sent_prefix_notice_without_omitted_members`, `test_summary_request.SummaryRequestTests.test_single_oversized_section_retains_unicode_prefix_notice_and_disclosed_place`, `test_summary_request.SummaryRequestTests.test_exact_limit_is_not_cut_and_one_character_over_is_reported` and 1 more |
| `MYC-8.12` | unit | `test_summary_request.SummaryRequestTests.test_override_files_are_read_once_exactly_and_replace_single_marker`, `test_summary_evidence.SummaryEvidenceTests.test_capture_keeps_raw_prompts_literal_argv_full_sources_and_canonical_immutable_manifest`, `test_summary_evidence.SummaryEvidenceTests.test_changed_framing_corrupt_descriptors_order_and_unsupported_comparison_are_refused` and 3 more |
| `MYC-8.13` | store | `test_summary_build.SummaryBuildStoreTests.test_public_build_publishes_exact_text_complete_vectors_pins_and_new_versions_atomically`, `test_summary_build.SummaryBuildStoreTests.test_public_cli_uses_real_writer_and_validated_embedding_adapter_with_local_service`, `test_summary_publication.SummaryPublicationStoreTests.test_identical_requests_have_distinct_actual_command_leases_and_publish_distinct_response_evidence` and 2 more |
| `MYC-8.14` | store | `test_summary_build.SummaryBuildStoreTests.test_actual_multipart_summary_search_uses_best_part_and_excludes_other_shared_repository_trees`, `test_summary_build.SummaryBuildStoreTests.test_real_lower_response_vectors_feed_higher_groups_with_no_searchable_staging`, `test_summary_build.SummaryBuildStoreTests.test_public_build_publishes_exact_text_complete_vectors_pins_and_new_versions_atomically` and 3 more |
| `MYC-8.15` | store | `test_summary_build.SummaryBuildStoreTests.test_empty_eligible_replacement_keeps_complete_set_metadata_without_service_calls`, `test_summary_build.SummaryBuildStoreTests.test_exact_physical_source_settings_and_late_audit_changes_discard_whole_tree`, `test_summary_build.SummaryBuildStoreTests.test_interrupt_after_confirmed_commit_reports_the_actual_published_tree` and 11 more |
| `MYC-8.16` | store | `test_summary_store.SummaryStoreTests.test_build_dry_run_fits_exact_leaf_requests_and_keeps_current_store_unchanged`, `test_summary_store.SummaryStoreTests.test_regeneration_keeps_exact_logical_members_plans_lower_first_and_blocks_remaining_stale_generated_members` |
| `MYC-8.17` | store | `test_summary_regenerate.SummaryRegenerationStoreTests.test_fixed_membership_that_grew_past_request_budget_is_blocked_without_calls_or_new_places`, `test_summary_regenerate.SummaryRegenerationStoreTests.test_no_stale_work_makes_no_service_calls_and_mutation_lock_is_nonblocking`, `test_summary_regenerate.SummaryRegenerationStoreTests.test_only_stale_nodes_retain_places_and_exact_membership_with_lower_response_feeding_parent` and 4 more |
| `MYC-8.18` | store | `test_summary_lifecycle.SummaryLifecycleStoreTests.test_withdrawal_of_memberless_summary_preserves_parent_pins_and_recomposes_source_removed`, `test_summary_regenerate.SummaryRegenerationStoreTests.test_embedding_failure_and_exact_input_change_preserve_stale_original`, `test_summary_regenerate.SummaryRegenerationStoreTests.test_member_restored_during_memberless_deletion_preserves_stale_original` and 2 more |
| `MYC-8.19` | store | `test_summary_build.SummaryBuildStoreTests.test_complete_ingest_does_not_generate_rewrite_or_repin_existing_summaries`, `test_summary_build.SummaryBuildStoreTests.test_published_tree_competes_as_own_documents_has_no_file_code_bridge_or_search_mutations`, `test_summary_build.SummaryBuildStoreTests.test_real_tree_uses_shared_document_margin_limit_and_retains_stale_generated_annotations` |
| `MYC-8.20` | store | `test_summary_store.SummaryStoreTests.test_incompatible_published_state_fails_closed_without_writes`, `test_summary_store.SummaryStoreTests.test_public_cli_registration_returns_complete_status_and_dry_run_replies`, `test_summary_store.SummaryStoreTests.test_read_snapshot_survives_concurrent_changes_and_refuses_expired_use_and_writes` and 4 more |
| `MYC-8.21` | store | `test_summary_lifecycle.SummaryLifecycleStoreTests.test_settings_change_in_removal_audit_rolls_back_complete_set_and_audit`, `test_summary_lifecycle.SummaryLifecycleStoreTests.test_summary_and_pass_contention_and_interruption_refuse_without_partial_removal`, `test_summary_lifecycle.SummaryLifecycleStoreTests.test_complete_removal_atomically_drops_set_metadata_vectors_pins_and_only_unowned_evidence` and 3 more |
| `MYC-8.22` | store | `test_summary_build.SummaryBuildStoreTests.test_actual_multipart_summary_search_uses_best_part_and_excludes_other_shared_repository_trees`, `test_summary_build.SummaryBuildStoreTests.test_published_tree_competes_as_own_documents_has_no_file_code_bridge_or_search_mutations`, `test_summary_build.SummaryBuildStoreTests.test_real_tree_uses_shared_document_margin_limit_and_retains_stale_generated_annotations` |
| `MYC-8.23` | store | `test_summary_target_faults.SummaryTargetFaultStoreTests.test_first_overview_projection_repeat_missing_section_and_recreation_report_generated_text`, `test_summary_target_faults.SummaryTargetFaultStoreTests.test_real_built_summary_cannot_be_derive_or_relate_endpoint_or_source_including_legacy_alias`, `test_summary_target_faults.SummaryTargetFaultStoreTests.test_real_built_summary_source_and_related_faults_keep_occurrences_without_generated_edges` and 1 more |
| `MYC-8.24` | unit | `test_summary_grouping.SummaryGroupingTests.test_candidate_component_cap_is_150`, `test_summary_grouping.SummaryGroupingTests.test_duplicate_constant_vectors_use_valid_finite_fit_without_warning_output`, `test_summary_grouping.SummaryGroupingTests.test_exact_profile_pca_dimensions_candidate_range_and_smaller_bic_tie` and 6 more |
| `MYC-8.25` | store | `test_summary_evidence.SummaryEvidenceStoreTests.test_real_corrupt_snapshot_or_manifest_metadata_refuses_read_and_response_without_partial_writes`, `test_summary_evidence.SummaryEvidenceStoreTests.test_real_cut_evidence_retains_uncut_source_and_exact_sent_utf8_prefix_and_notice`, `test_summary_evidence.SummaryEvidenceStoreTests.test_real_foreign_nonactive_and_forged_invocations_or_changed_member_addresses_cannot_retain` and 3 more |
| `MYC-8.26` | store | `test_summary_build.SummaryBuildStoreTests.test_empty_eligible_replacement_keeps_complete_set_metadata_without_service_calls`, `test_summary_build.SummaryBuildStoreTests.test_exact_physical_source_settings_and_late_audit_changes_discard_whole_tree`, `test_summary_build.SummaryBuildStoreTests.test_ingest_pass_is_unlocked_during_calls_competing_mutations_and_removal_are_busy` and 12 more |
| `MYC-8.27` | store | `test_summary_lifecycle.SummaryLifecycleStoreTests.test_changed_exact_inputs_and_late_vector_tampering_roll_back_text_vectors_and_pins`, `test_summary_lifecycle.SummaryLifecycleStoreTests.test_withdrawal_of_memberless_summary_preserves_parent_pins_and_recomposes_source_removed`, `test_summary_regenerate.SummaryRegenerationStoreTests.test_embedding_failure_and_exact_input_change_preserve_stale_original` and 11 more |
| `MYC-8.28` | store | `test_summary_store.SummaryStoreTests.test_exact_repository_scope_rejects_organizations_even_one_member_and_empty_reports_succeed`, `test_summary_store.SummaryStoreTests.test_handler_reports_are_read_only_and_pending_actual_mutations_refuse_before_store_use`, `test_summary_store.SummaryStoreTests.test_build_dry_run_fits_exact_leaf_requests_and_keeps_current_store_unchanged` and 15 more |
| `MYC-8.29` | store | `test_summary_build.SummaryBuildStoreTests.test_ingest_pass_is_unlocked_during_calls_competing_mutations_and_removal_are_busy`, `test_summary_build.SummaryBuildStoreTests.test_interrupt_after_confirmed_commit_reports_the_actual_published_tree`, `test_summary_lifecycle.SummaryLifecycleStoreTests.test_changed_exact_inputs_and_late_vector_tampering_roll_back_text_vectors_and_pins` and 21 more |
