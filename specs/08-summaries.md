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

Covered: what is summarised, grouping and levels, the command that writes the text, the request it is given, how a summary is stored, building a set of summaries, writing stale ones again, status and removal, summaries in a search.

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

Decided: the settings name the command that writes a summary, `summaries.command` ([MYC-D31](#decisions)). Any program serves that reads a request on standard input and prints the answer, for example `["claude", "-p"]`.

- Mycel starts the command once for each summary, without a shell, in an empty folder of its own, so that the program finds no instructions of some project lying around.
- The whole request goes to its standard input. Nothing of it is in an argument.
- Its standard output is the summary, decoded as UTF-8. A status other than 0, invalid UTF-8, an empty/whitespace-only answer, or no answer within five minutes is a failure. Capture at most 1 MiB stdout and 64 KiB stderr; overflow terminates the process group and fails the request. A failed summary is tried once more and then recorded as failed with a redacted reason; raw stderr and credentials are not copied into replies or activity.
- At most `summaries.at_once` run at the same time.
- Mycel knows nothing of models, accounts or prices. They are the command's affair.

Without the setting, an actual `build` or `regenerate` is refused with `settings`. A dry-run, status, removal and search still work. The command array must contain a nonempty executable and string arguments. Instruction overrides must contain both UTF-8 files and exactly one `$sections` mark in the task; invalid overrides return `settings` before any request is sent.

This configured summary command is one external model boundary. MYC-14 separately defines the configured smarter-review command and direct Jev classification. Mycel directly calls the fixed embedding and Jev services; provider selection for summaries and review belongs to the configured commands (MYC-0.10). Only the explicit commands that request generation or classification spend those calls.

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
| MYC-8.5 <!-- 7de52396-3f80-4e7a-b79b-5a63a9c8aaab --> | write no summary text itself: start the command `summaries.command` once for each summary, without a shell, in an empty folder, with the whole request on standard input | Changed | unit |
| MYC-8.6 <!-- 56a7722d-3cb4-459f-972f-9da530a76af7 --> | take a status other than 0, an empty answer and no answer within five minutes as a failure, try a failed summary once more, and record the reason of one that failed again | Changed | unit |
| MYC-8.7 <!-- 28e6ea78-61a6-48fd-abb6-24e5f4d60686 --> | run at most `summaries.at_once` requests at the same time | Changed | unit |
| MYC-8.8 <!-- 5b835649-7c2c-4830-bae5-f1c8abe293b7 --> | refuse actual `build` and `regenerate` with `settings` when the settings name no command, and keep dry-runs, status, removal and search working | Changed | unit |
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
| MYC-8.20 <!-- f70708a3-880f-4fbd-b173-256e197dccad --> | report for a repository the summaries of each level, how many are stale, how many sections are in a summary, in none, and not embedded, and whether a command is set | Changed | store |
| MYC-8.21 <!-- 432e3a46-e88c-4ef5-b95e-5ba781a79d09 --> | remove every summary of a repository and its edges on request | New | store |
| MYC-8.22 <!-- 94867810-7e67-4ea9-95c8-2f2f72382fc1 --> | let summaries of the searched repository compete in a search as documents do, leave them out of a search for code only, never follow one to code, and return one with the origin `summary` and without a file | Kept | store |
| MYC-8.23 <!-- bc77a15e-279f-48e8-9225-01455063b5c9 --> | report a ref to a summary in a file as a fault, and refuse with `invalid_input` a `derive` or `relate` that names one | New | store |
| MYC-8.24 <!-- d0afd36d-1035-4428-b29d-a0154fcefe75 --> | use and record the deterministic `mycel-summary-v1` grouping profile and report invalid numerical inputs or failed fitting | New | unit |
| MYC-8.25 <!-- ecc1d34a-0f39-4315-b384-4dd7382ef3aa --> | validate configured command and prompt files before requests; retain the exact generation request, response and member evidence under MYC-16 | New | store |
| MYC-8.26 <!-- 9a99738e-2428-4361-96df-03d928d3a2b5 --> | keep staged summaries and vectors out of searches, recheck exact inputs before publication, discard changed-input builds, and replace an empty eligible set atomically | New | store |
| MYC-8.27 <!-- e554625a-8b7d-4924-90c4-b6d44936c71b --> | publish each regenerated summary with its vectors and pins atomically, keep independent successes, and block parents whose generated members remain stale | New | store |
| MYC-8.28 <!-- d1d8effd-f5d2-4273-bfa5-013e08954675 --> | make summary status and both dry-runs read-only with no service calls, distinguish estimated build plans, and return complete regeneration/removal replies | New | store |
| MYC-8.29 <!-- 4494a6cb-ca43-4831-a8c6-79b933f9d80b --> | serialize summary mutations with a nonblocking summary-operation lock, release pass locks during external calls, protect in-flight evidence by exact invocation liveness and clean up subprocesses/staging on interruption | New | store |

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
  commandSet: boolean;                 // whether the settings name a command
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
| MYC-D31 <!-- 4227641a-3f09-4e68-a076-1664dba1f8cf --> | Who writes the text of a summary, now that `infer` is deprecated? | A command the owner names in the settings, for example `claude -p`. Mycel starts it for each summary, gives it the sections and stores what it prints. This is what version 1 did with `infer`, with the program's name moved into the settings. Mycel then starts one program that is not its own, and summaries need that program to be installed and signed in. The other choice is that Mycel starts nothing: it hands the groups to whoever called it, an agent or Arbol writes the summaries and hands them back, and Mycel only stores them. Mycel would then stay free of any model, and a build would need a caller that does the writing | Decided 8 October 2026 by the owner: agreed. A command the owner names in the settings writes each summary |
