---
role: authored
spec: MYC-4
status: accepted
---
# Mycel · 04 Retrieval

Retrieval is what Mycel is for: a caller asks a question or names a symbol, and Mycel returns the chunks of code and documents that answer it, ranked. This specification fixes how a search is scoped, how its two kinds of matching are combined, how documents and code compete, what a result says about itself, and when a search first brings the index up to date. It matters because version 1's ranking rules did not hold as its own comments stated them, a result did not say how far it could be trusted or compared, and one kind of search skipped the freshness check.

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: the scope of a search, the two arms (by meaning and by exact wording), the two ranking routes, the bridge from documents to code, the place of documents in the ranking, annotations, the result contract, freshness on read, searching several repositories.

Not covered: how chunks are made ([MYC-1](01-corpora-and-ingest.md)); edges between chunks, staleness and Heartwood ([MYC-2](02-provenance-and-freshness.md)); vectors ([MYC-3](03-embedding.md)); the grep replacement with a search tail ([MYC-10](10-grep-replacement.md)) and the reading of one chunk ([MYC-11](11-reading-a-chunk.md)); summaries and sections of the code overview among the results ([MYC-8](08-summaries.md#summaries-in-a-search), [MYC-9](09-code-overview.md#finding-and-reading-it)); the evaluation set and its report ([MYC-13](13-checks-and-evaluation.md)).

## Behaviour

### The scope of a search

Observed in version 1: a search covered one repository. Without a name it took the repository of the current directory, and when that belonged to none it searched a repository called `Arbol`. A search that included documents also searched the documents of the repository called `mycel`, whatever repository was asked for; that name was fixed in the code. A disabled repository was still searched: observed on 7 October 2026, a repository switched off in the settings kept answering from its stored chunks until its rows were deleted.

A search covers the repository it names, or the one the current directory belongs to. An organization's name, or its folder outside its members, means every enabled member of it ([Several repositories](#several-repositories)). When nothing gives a repository the search is refused. Shared documents are selected in the settings by repository and by files or folders, rather than by sharing a whole repository automatically ([MYC-D18](#decisions)). They take part in every search that includes documents, including a search for documents only; they take no part in a search for code only. A disabled repository is not searched, whether named directly, included through an organization or listed for shared documents ([MYC-D22](#decisions)). A search answers from what is on disk: a version of a chunk that is found only in a branch or a stash takes no part ([MYC-D8](01-corpora-and-ingest.md#decisions)).

`search.shared_documents` is a list of entries with `repo` and `paths`. Each path is relative to that repository's configured `artifact_root` and names a file or a folder; a folder selects the document files below it recursively. Only enabled repositories contribute shared documents. The default settings select all Mycel artifact files and only Arbol's `GLOSSARY.md`; the rest of the Arbol corpus is not shared by default. The owner can change these selections in the settings. Repository names are settings values, not special cases in the search code.

```toml
[search]
shared_documents = [
  { repo = "mycel", paths = ["."] },
  { repo = "arbol", paths = ["GLOSSARY.md"] },
]
```

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/cli.py#search_payload`
- `mycel_deprecated_v1:mycel/scope.py#resolve`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_doc_scope`

### Two arms

Observed in version 1, and kept: every search runs two kinds of matching over the same chunks.

| Arm | Finds | How |
|---|---|---|
| By meaning | Chunks that are about the query, whatever words they use | The query is embedded and compared with the chunks' vectors by cosine similarity |
| By exact wording | Chunks that contain the query's words | A BM25 index over the chunks' text |

Each arm returns its best candidates: the larger of the number of results asked for and 20. A chunk without a vector can be found by wording only. The index by wording covered the chunk's text; the chunk's name and path were indexed too but never searched, so a symbol's name matched only where it also appeared in the body.

Proposed: the name and the path of a chunk are searched by wording as well as its complete text. The meaning arm considers a chunk version only when every part of its current-model embedding plan has a vector ([MYC-3](03-embedding.md#embedding-parts)). Its similarity is the largest cosine similarity between the query and any of its parts. Part matches are collapsed to distinct logical chunks before candidate limits, ranks, rank fusion, bridge limits, score raises, document limits and final result limits. A long chunk takes one place in each list, and repeated part hits never multiply its score or its citations. Incomplete versions remain findable by wording.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#ensure_bm25_index`

### Two routes

Observed in version 1, and kept: the shape of the query decides how the arms are combined.

| Query | Route | Combination |
|---|---|---|
| Only letters, digits, `_`, `.`, `#`, `/` and `-`, with no space: `renewSession`, `auth/session.ts#renew` | Identifier | Reciprocal rank fusion: each arm adds 1/(60 + rank) to a chunk's score, both arms with the same weight |
| Anything else: `how does renewal decide` | Question | Cosine similarity is the score. Hits by wording that the meaning arm missed are appended below everything scored, in their own order |

One plain word, such as `payments`, counts as an identifier in the first version ([MYC-D19](#decisions)). A later change to that rule requires the before-and-after evaluation of MYC-4.25.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`

### The bridge from documents to code

Observed in version 1, on the question route: the eight document sections closest to the query were found by exact cosine. Each of them that belonged to the repository being searched was followed one step along its [Source Refs](../../arbol/GLOSSARY.md#source-ref) to the code it cites, and at most three code chunks per section, the three closest to the query, entered the ranking with the section's similarity times 0.92. A result that came this way named the section in a `via` field. When a chunk was found both directly and through a section, its score was raised by 0.05.

The raise was applied once for every section and every edge that reached the chunk, not once per chunk, so a chunk cited by eight sections could gain 0.40.

Proposed: the bridge is kept, with the raise given once per chunk. Its selection of document sections and cited code uses only fully embedded current-model versions, with each chunk's similarity taken from its best matching part before applying the section and code limits. It is why documents with Source Refs pay off: prose matches the question, and the edges deliver the code.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_bridge_expand`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`

### Down-weights

Observed in version 1: three families of chunks mirror the wording of features and would outrank the code they describe or accompany.

| Family | Recognised by | Question route | Identifier route | Lifted when the query says |
|---|---|---|---|---|
| Tests | `.spec.` and `.test.` files, `__tests__` folders, `test_*.py`, `conftest.py`, `_test.py`, `_test.go` | × 0.93 | × 0.85 | test, spec, e2e, mock, fixture |
| Generated code | `.generated.` files, `gql/types.ts` | × 0.93 | not applied | type, schema, graphql, gql, codegen, generated |
| Structural chunks | Whole-file, module, markup and style chunks | × 0.9 | × 0.75 | never |

The factors were applied only to chunks the meaning arm had found directly. A chunk that entered through the bridge or through the wording arm alone got none of them.

The same families and factors are the starting values ([MYC-D20](#decisions)), applied to a chunk however it entered the ranking. The owner delegates their later adjustment, together with the bridge factors, document margin and limits, rank-fusion constant and bridge limits, to the before-and-after evaluation of MYC-4.25. The version 1 values remain until that evaluation warrants a change. The patterns for tests and generated code are settings of a repository, with these as the defaults.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`

### Documents among the results

Observed in version 1, on the question route: a document section became a result of its own only when its similarity was at least 0.03 above the best code score, at most two such sections were returned, and the routing files `INDEX.md` and `README.md` were never returned this way. The comments in the source stated these as general rules.

They were not. A document found by the wording arm was appended with the other wording hits, where none of the three rules applied. On the identifier route a document could score through the wording arm only, so it could reach at most half the score of a code chunk found by both arms. The best code score that a document had to beat included the bridge scores and their repeated raises, so the bar could lie above any real similarity.

Proposed: the three rules hold for every way a document can enter a ranking that also holds code, and the bar is the best direct code similarity. A search for documents only has no such rules: every result is a document.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#doc_search`

### What a result says

Observed in version 1: a result of the usual search carried the chunk's place (path, name, kind, lines), a score, its rank in each arm, a preview of 240 characters, the file to read, and two annotations: `via`, the document section that delivered it, and `documented_in`, up to two document sections whose Source Refs cite it. Stale and Heartwood marks appeared only inside those annotations; a result that was itself a stale or Heartwood document did not say so. The score was on one of three scales, a cosine, a rank fusion value of at most about 0.033, or about 0.999 for wording hits when no vector could be made, and nothing said which. A search for documents only returned results of a different shape under the same version number.

Which two sections `documented_in` named was left to the database: the query had no order.

Proposed: one shape for every result. A file-backed result and its citations name their actual configured root (`code` or `artifact`) and relative path. Markdown under `code_root` has document origin; it is not treated as code or redirected to an artifact path. Index-only summaries and overviews have no file root. Each result says whether it is stale and whether it is Heartwood. It includes the stale reasons of MYC-2, naming the source by repository, path and heading or symbol, with the intermediate dependency path for an indirect reason. It also says whether its dependency check completed and reports faults in those refs. A `stale: false` result with an incomplete dependency check is not presented as verified current; completing the check says that changes were checked, not that the chunk's claims were semantically verified. The same dependency annotations accompany `via` and `documented_in` citations.

The reply names the route that was taken and says whether the meaning arm took part. `documented_in` is ordered by the similarity of the citing section to the query, then by path. That comparison uses the section's best matching part and requires complete current-model coverage; incomplete citing sections are left out of this annotation, while their Source Refs and edges are retained.

Since [MYC-D39](02-provenance-and-freshness.md#decisions), decided on 15 October 2026, each code result also says whether any document section describes it, by a direct declared or asserted dependency in either direction ([MYC-2](02-provenance-and-freshness.md#which-documents-describe-a-chunk)). Unlike `documentedIn`, this depends neither on embeddings nor on the query. `mycel read` lists the sections.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#doc_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_documented_in`
- `mycel_deprecated_v1:mycel/retrieval.py#_payload`
- `mycel_deprecated_v1:mycel/retrieval.py#_read_location`

### When the meaning arm cannot run

Observed in version 1: without a key, the search went on by wording alone and showed it only as a count of zero. With a key and an error from the embedding service, the whole search failed. Observed on 7 October 2026: that count is of code chunks only, so a corpus of documents always shows zero, which reads as a failure when it is not.

Proposed: a search never fails because the query could not be embedded. It answers by wording, and the reply says that the meaning arm did not take part and why.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_query_vec`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`

### Freshness on read

Observed in version 1: before searching, Mycel looked for any file in the repository changed since the last pass, and if it found one it ran a pass over that repository alone. That pass fetched nothing from a remote and embedded nothing, so chunks it added or changed could be found by wording only, and the reply did not say so. The check walked the whole tree with no time limit. A search for documents only skipped the check altogether: observed on 6 October 2026, such a search kept returning files that had been deleted from disk until a search of the usual kind was run.

Decided on 8 October 2026 by the owner: every kind of search checks and ingests changes in the enabled repositories that supply its result scope, then checks the repositories of their explicit upstream sources recursively. For a search that includes documents, this includes the repositories supplying the selected shared documents. Starting from the chunks in that scope, declared refs and asserted dependencies determine the upstream sources to check, including valid unresolved refs and retained missing-source records. Newly ingested refs extend the scope until every required enabled source has been checked or the check cannot finish. Dependencies are never inferred from mentions, names or semantic similarity.

Dependency checking is separate from selecting search results. A code-only search still checks an enabled repository whose documents govern the code it searches, while returning no shared documents (MYC-D18). A source may lie outside `search.shared_documents` and still require checking because a searched chunk explicitly depends on it. Checking a source repository does not add its other chunks to the results or change the ranking. If a Driver chunk depends on a contract that depends on a Glossary section, a change to that section must reach the Driver's stale mark and reasons even when the Driver's text did not change.

Each required repository is checked by the scan and ingest rules of MYC-1, then dependencies are resolved and stale state is propagated by MYC-2. This does not edit or regenerate dependant text, renew its pinned source hash, or embed pending chunks. Heartwood and generated chunks retain their existing rules. All required checks and propagation share the invocation's existing time limit; discovering another source repository does not start a new time allowance. When the limit ends, a repository is busy, or a check is refused or fails, the search uses the index as it is and reports what remains pending.

The caller can turn the entire check off with `--no-fresh`; the known required repositories are then reported as pending, and returned chunks and citations have incomplete dependency checks. Otherwise the reply reports each repository as `done`, `pending`, `busy`, `refused` or `failed`, with the reason when it was not done. `done` means its required file check, ingest and dependency-state updates completed; `pending` includes unstarted or partial work. A downstream repository whose dependency-state update could not be applied is also listed with that pending work, without adding its files to the scan scope. The overall `finished` is true only when the recursively required work and affected dependency-state updates finished. Invalid or unresolved refs remain visible as faults, and make the affected chunk's dependency check incomplete even when all eligible repository checks finished. The reply also states how many on-disk chunk versions in the result scope lack complete current-model embedding coverage, including versions with failed parts or failed plans.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/retrieval.py#search`
- `mycel_deprecated_v1:mycel/cli.py#search_payload`
- `mycel_deprecated_v1:mycel/syncpass.py#repo_stale`
- `mycel_deprecated_v1:mycel/syncpass.py#run_repo_pass`

### Side effects of a search

Observed in version 1: every search created the wording index if it was missing and copied the settings file into the index store. A read wrote.

Proposed: a search writes only what its check and ingest of changes requires: reconciled files in the checked repositories, resolved or retryable dependency records, affected stale marks and reasons in downstream dependants, and their activity entries (MYC-1.23, MYC-2.18, MYC-12). It changes no unrelated rows, generates no dependant text and embeds no pending chunks. The index's structure is made by the command that sets the index up, and settings are read from the settings file.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#ensure_bm25_index`
- `mycel_deprecated_v1:mycel/cli.py#search_payload`
- `mycel_deprecated_v1:mycel/config.py#load_apply`

### Several repositories

Observed in version 1: naming an organization searched each of its member repositories in turn and returned one full reply per member, not merged, with the number of results applying to each.

Kept by the owner's decision ([MYC-D21](#decisions)): one reply per enabled member, with the requested number of results applying to each. Scores of different repositories are not compared and their results are not merged into one list.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/cli.py#search_payload`
- `mycel_deprecated_v1:mycel/organizations.py#resolve`

## Requirements

| ID | Mycel must… | From v1 | Verified by |
|---|---|---|---|
| MYC-4.1 <!-- c7e23eb9-b727-4346-8872-97e0153c49ee --> | search the repository an invocation names, or the one the current directory belongs to, and refuse the search when neither gives one. An organization's name or folder gives its enabled members (MYC-1.4, MYC-4.24). No repository's name is built in | Changed | unit |
| MYC-4.2 <!-- 67523ca7-0285-4cd9-aae1-c1bbb9783053 --> | leave a disabled repository out of every search | Changed | store |
| MYC-4.3 <!-- 70d53b15-9cf2-4886-83cd-843cd228b2f1 --> | add to a search that includes documents only the document files selected by `search.shared_documents`, whose entries name an enabled repository and files or recursive folders relative to its `artifact_root`. Default to all Mycel artifact files and only Arbol's `GLOSSARY.md`; add none to a code-only search | Changed | store |
| MYC-4.4 <!-- b8a76713-3668-49bd-83c5-efe73da1e557 --> | match by meaning on fully embedded chunk versions and by exact wording on the complete text of every chunk, including versions with partial or failed embedding coverage | Changed | store |
| MYC-4.5 <!-- e8205dba-b208-46b2-98fd-95a702625737 --> | match by wording on a chunk's text, its name and its path | Changed | store |
| MYC-4.6 <!-- 45eaa185-6de7-43b7-bdad-7e63ce63eb6a --> | take the identifier route for a query made only of letters, digits, `_`, `.`, `#`, `/` and `-`, including one plain word, and the question route for any other | Kept | unit |
| MYC-4.7 <!-- 6d353769-4f2d-4c43-bfe2-feffb7c83abf --> | on the identifier route, score by reciprocal rank fusion of the two arms with equal weight | Kept | unit |
| MYC-4.8 <!-- 6fb4218a-9d36-447f-a662-d239e793a367 --> | on the question route, score by cosine similarity and place wording hits the meaning arm missed below every scored result | Kept | unit |
| MYC-4.9 <!-- c67dc7d9-33a5-4562-860d-fb8e964af81c --> | on the question route, follow the closest document sections of the searched repository one step along their Source Refs to the code they cite, and name the section on every result it delivered | Kept | store |
| MYC-4.10 <!-- 062bc706-ec0f-4769-b52a-eac634a19474 --> | raise the score of a chunk found both directly and through a section once, however many sections cite it | Changed | unit |
| MYC-4.11 <!-- 5290059f-7dbf-4a9b-a82d-dd735a0344ad --> | apply the down-weights for tests, generated code and structural chunks to a chunk however it entered the ranking, and lift the first two when the query asks for them | Changed | unit |
| MYC-4.12 <!-- 88d5a7c3-1ac8-4ffb-bd4f-22c6cdd676db --> | take the patterns that recognise tests and generated code from the repository's settings, with version 1's as defaults | Changed | unit |
| MYC-4.13 <!-- ff4a5350-ad80-4919-80a6-6df3cb8ddf9e --> | return a document among code results only when it clearly beats the best direct code match, at most twice per search, and never a routing file. The rule holds on both routes and for both arms | Changed | unit |
| MYC-4.14 <!-- ba02dcdc-21b8-446d-be78-ff139473ad77 --> | give every result and its citations the same dependency annotations: stale and Heartwood marks, every stale reason naming its original source and intermediate path, and whether checking the explicit dependencies completed, with ref faults; never present an unchecked chunk as verified current | Changed | unit |
| MYC-4.15 <!-- cc31396f-197a-4fde-8a5b-8d6914df989f --> | name in the reply the route taken and whether the meaning arm took part, with the reason when it did not | New | unit |
| MYC-4.16 <!-- 545e3cfd-deb3-43b5-bfa9-daa5e8e4393f --> | answer by wording alone, and say so, when the query cannot be embedded. A search does not fail for that reason | Changed | unit |
| MYC-4.17 <!-- ae3d495c-aa1a-422f-a288-0508ad472bfa --> | order equal scores and the entries of `documented_in` by a stated rule, so that the same index and query give the same reply | Changed | store |
| MYC-4.18 <!-- 9907936b-a941-4a2a-a02c-69a2398d09a5 --> | before every kind of search check and ingest changes in the enabled repositories supplying its results or selected shared documents and recursively in their explicit declared or asserted upstream sources, including valid unresolved refs; resolve dependencies and propagate affected stale marks without broadening result scope. The caller can turn the entire check off | Changed | store |
| MYC-4.19 <!-- ef8001ac-2840-42e0-88e2-fef7fc1c61af --> | share one existing time limit across the check, recursive source checks, ingest and propagation; search the index as it is when work cannot finish, report each required repository's completion or pending state and reason, and mark the affected result dependency checks incomplete | Changed | unit |
| MYC-4.20 <!-- 4744e114-00c2-4fc0-bd0e-f79ffce8ac0e --> | state in the reply how many on-disk chunk versions lack complete current-model embedding coverage, including partial coverage, failed parts and failed plans | New | store |
| MYC-4.21 <!-- 73cafcff-ff1f-4b42-b7bd-47803793340c --> | write during a search only the reconciled files, dependency records, affected stale marks and reasons, and activity entries required by its check and ingest of changes; change no unrelated rows and neither generate dependant text nor embed pending chunks | Changed | store |
| MYC-4.22 <!-- 784d7f0e-227d-4f0c-842e-47f7b2c35aad --> | refuse a number of results below 1 or above 100, and an empty query, in every kind of search | Changed | unit |
| MYC-4.23 <!-- 3848df83-d354-4a15-889e-f38258d6b5cb --> | identify each file-backed result by its actual configured root and relative path, giving a readable absolute file only when it exists within that root; keep checkout Markdown as document origin, distinguish colliding relative paths and otherwise explain why the file cannot be read | Changed | unit |
| MYC-4.24 <!-- 0d754795-6997-4a73-9e4c-6993e9d7b456 --> | search the enabled members of an organization one by one and return one reply per member, with the requested result limit per member, never one merged list | Kept | store |
| MYC-4.25 <!-- 01e77a11-e0e4-46b9-9deb-ee69aae9dda2 --> | keep an evaluation set of queries with the chunks each should find, report recall at 3 and at 10 for it, and change a ranking rule or a constant only with that report for before and after | New | eval |
| MYC-4.26 <!-- 4643a6e2-5eb4-4cfd-8f74-c7e7963a170b --> | answer from the versions of chunks that are on disk, and never return a version that is found only in a branch or a stash | New | store |
| MYC-4.27 <!-- 21b50a9c-14d9-4ad2-9592-193c1f579c48 --> | score a fully embedded chunk by its best matching part, collapse part matches before all candidate, bridge and result limits and ranks, and return each logical chunk once without accumulating score raises from its parts | New | store |
| MYC-4.28 <!-- 9d76b10a-4f5f-4b5e-859d-bba7723bd0fc --> | return MYC-16 canonical qualified addresses on results and citations, distinguishing actual root bindings from origin and index-only namespaces while preserving stable chunk identifiers | New | unit |
| MYC-4.29 <!-- 80fc82cf-e1a9-4677-9a84-19bc50831e4b --> | say in each code result whether any document section describes it by a direct declared or asserted dependency in either direction, independently of embeddings and of the query | New | store |

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

```sh
mycel search "how does renewal decide"            # the repository of the current directory
mycel search --repo core "convert a document"     # a named repository
mycel search --repo core --only code "DocBuilder" # code only; --only docs for documents only
mycel search --repo core --k 5 --no-fresh "…"     # five results, no freshness check
mycel search --repo "Euro Office" "…"             # every member of an organization
```

```ts
interface SearchReply {
  schema: number;                      // the version of this reply; the first one is 3
  repository: string;
  route: "identifier" | "question";
  meaning: { used: boolean; reason?: string };     // reason when the meaning arm did not take part
  candidates: { meaning: number; wording: number };
  freshness: {
    checked: boolean;                  // false with --no-fresh
    finished: boolean;                 // true only when all recursively required work finished
    ingested: number;                  // total chunks the check added or changed across checked repositories
    withoutVector: number;             // result-scope versions without complete current-model embedding coverage
    repositories: RepositoryCheck[];
  };
  results: SearchResult[];
}

interface SearchResult {
  id: string;
  repository: string;
  origin: "code" | "document";
  root: "code" | "artifact" | "index"; // actual binding, independently of origin; index for generated text
  path: string;                        // relative to that configured root; synthetic for index-only results
  address: string;                     // MYC-16 canonical qualified place, usable with mycel read
  name: string;                        // symbol for code, heading path for a document
  kind?: string;                       // function, method, class, section and so on
  lines?: { start: number; end: number };
  score: number;                       // comparable only within one reply
  ranks: { meaning?: number; wording?: number };
  stale: boolean;
  staleReasons: StaleReason[];          // MYC-2: original source and intermediate dependency path
  dependencyCheck: DependencyCheck;
  heartwood: boolean;
  via?: Citation;                      // the document section that delivered this result
  documentedIn: Citation[];            // at most two sections whose Source Refs cite it
  described?: boolean;                 // MYC-D39: code results only; whether any document section describes it
  preview: string;                     // the first 240 characters of the chunk
  file?: string;                       // absolute path to read, when readable
  unreadable?: string;                 // the reason, when there is no file
}

interface Citation {
  document: string;
  repository: string;
  root: "code" | "artifact" | "index"; // actual binding or index-only namespace
  path: string;                        // relative to its actual root
  address: string;                     // MYC-16 canonical qualified place
  stale: boolean;
  staleReasons: StaleReason[];
  dependencyCheck: DependencyCheck;
  heartwood: boolean;
}

interface RepositoryCheck {
  repository: string;
  state: "done" | "pending" | "busy" | "refused" | "failed";
  ingested: number;                    // chunks added or changed in this repository
  reason?: string;                     // required whenever state is not "done"
}

interface DependencyCheck {
  complete: boolean;                   // this chunk's repository and recursive explicit sources checked, no ref faults
  faults: RefFault[];                  // MYC-2: faults in this chunk's direct or upstream refs
}

// StaleReason and RefFault are defined in MYC-2.
```

The reply for an organization is `{ schema, organization, repositories: SearchReply[] }`.

Version 1's reply was version 2. The first reply of Mycel 2 is version 3, so that a caller written for version 1 can tell them apart.

## Known problems in version 1

- **The ranking rules were not the ones stated.** The raise for agreement accumulated per citing section. Documents entered through the wording arm past the margin, the limit of two and the routing-file rule. Down-weights were lost on chunks that entered through the bridge.
- **A result did not say how far to trust it.** Stale and Heartwood marks were missing on the results themselves. Nothing said which of three scales a score was on.
- **A degraded search looked like a healthy one.** Without a key the only sign was a count of zero, and that count is zero for every corpus of documents.
- **One kind of search skipped freshness.** A search for documents only never checked, and returned deleted files.
- **Fresh did not mean searchable by meaning.** The check ingested without embedding and did not say so.
- **A read wrote.** Every search ran statements that change the index's structure and copied the settings into the store.
- **Names were built in.** The fallback repository `Arbol`, the shared repository `mycel` and the two routing file names were constants in the code.
- **A disabled repository still answered.** Switching a repository off stopped ingest and embedding only.
- **The constants had no test.** The factors, margins and limits came from research that is not in the repository, and no test or evaluation set covered ranking.
- **The guides described other behaviour.** Observed on 6 October 2026: the runbook named a reply version and command options that neither the source nor the installed program had.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#doc_search`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_bridge_expand`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_query_vec`
- `mycel_deprecated_v1:mycel/retrieval.py#search`
- `mycel_deprecated_v1:mycel/cli.py#search_payload`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D18 <!-- b5c7733a-467a-4407-98c9-cd4d963b2b4d --> | Do the documents of another repository take part in every search? | Yes, for the repositories the settings list as shared, which replaces version 1's fixed name. The first list holds `mycel`, so the guides on how to work keep surfacing in every repository | Decided 8 October 2026 by the owner: shared documents must be configurable by files or folders, not only by whole repository. `search.shared_documents` names `repo` and `paths` relative to its `artifact_root`; files select themselves and folders select document files recursively. Defaults: all Mycel artifact files (`mycel`, `.`), plus only Arbol's `GLOSSARY.md` (`arbol`, `GLOSSARY.md`). Only enabled repositories contribute, and code-only searches include no shared documents |
| MYC-D19 <!-- 141ddff7-9b00-4dc9-ab85-e84a29d459bc --> | Is one plain word an identifier? | Yes in the first version, as in version 1. The evaluation set decides whether a word that matches no symbol should take the question route instead | Decided 8 October 2026 by the owner: yes, the proposed default. A plain word takes the identifier route in the first version; any later change requires the evaluation of MYC-4.25 |
| MYC-D20 <!-- e570583e-a881-4900-ab9e-a9e3b9ffe356 --> | Where do the factors, margins and limits start? | At version 1's values: 0.92 and 0.05 for the bridge, 0.03 and two for documents, the down-weights of the table above, 60 for rank fusion, eight sections and three chunks per section. They change only under MYC-4.25 | Decided 8 October 2026 by the owner: use the previous values unless evaluation warrants a change. The owner delegates these values to the agent; adjustments require the before-and-after evaluation report of MYC-4.25 |
| MYC-D21 <!-- 19f5adac-75f1-4d68-8b29-29a9242b9a44 --> | Are the results of several repositories merged into one list? | No. One reply per repository, as in version 1; scores of different repositories are not comparable | Decided 8 October 2026 by the owner: separate replies, the proposed default. Return one reply per enabled repository, with the requested result limit per reply; do not merge the results or compare scores across repositories |
| MYC-D22 <!-- 8e7bbc37-9f49-4353-98b3-8fa2f3f6861e --> | Does switching a repository off also hide it from search? | Yes. A repository that should stay searchable without being ingested is rare, and version 1's behaviour surprised its owner | Decided 8 October 2026 by the owner: yes, a disabled repository is hidden from every search, including direct searches, organization searches and shared documents |

## Named checks

Written by `scripts/name_checks.py` from the `proven` Origin Links of the tests and a complete check report in which they passed. Each requirement keeps its kind in its Verified by cell and names here up to three of its passing checks: those of its own kind first, then those that rest on the fewest requirements. `mycel origins --repo mycel --path tests` lists every link. Do not edit this section by hand: run the script again.

| Requirement | Kind | Checks |
|---|---|---|
| `MYC-4.1` | unit | `test_retrieval.RetrievalScopeTests.test_cwd_resolves_code_artifact_and_organization_folders`, `test_retrieval.RetrievalScopeTests.test_named_repository_overrides_cwd_and_unconfigured_names_refuse`, `test_retrieval.RetrievalScopeTests.test_no_containing_repository_has_no_fallback` |
| `MYC-4.2` | store | `test_retrieval_store.RetrievalStoreTests.test_disabled_and_selected_shared_documents_use_origin_and_artifact_aliases` |
| `MYC-4.3` | store | `test_retrieval_store.RetrievalStoreTests.test_disabled_and_selected_shared_documents_use_origin_and_artifact_aliases` |
| `MYC-4.4` | store | `test_retrieval_store.RetrievalStoreTests.test_complete_body_name_and_path_find_partial_failed_and_unembedded_versions`, `test_retrieval_store.RetrievalStoreTests.test_complete_current_model_parts_collapse_before_each_candidate_limit`, `test_retrieval_store.RetrievalStoreTests.test_deleted_planned_parts_and_failed_vectors_do_not_become_complete` and 1 more |
| `MYC-4.5` | store | `test_retrieval_store.RetrievalStoreTests.test_complete_body_name_and_path_find_partial_failed_and_unembedded_versions` |
| `MYC-4.6` | unit | `test_ranking.RankingTests.test_route_shapes_and_plain_word_are_fixed` |
| `MYC-4.7` | unit | `test_ranking.RankingTests.test_equal_weight_rrf_one_based_ranks_and_ties`, `test_ranking.RankingTests.test_input_validation_and_conflicting_snapshot_rows_refuse`, `test_ranking.RankingTests.test_score_ties_use_every_canonical_field_and_never_insertion_order` |
| `MYC-4.8` | unit | `test_ranking.RankingTests.test_question_signed_cosines_and_wording_tail_tier`, `test_ranking.RankingTests.test_input_validation_and_conflicting_snapshot_rows_refuse`, `test_ranking.RankingTests.test_score_ties_use_every_canonical_field_and_never_insertion_order` |
| `MYC-4.9` | store | `test_ranking_store.RankingStoreTests.test_bridge_uses_full_document_and_code_pools_before_eight_and_three_caps`, `test_ranking_store.RankingStoreTests.test_current_resolved_versions_replace_pins_and_retained_moves_keep_identity`, `test_ranking_store.RankingStoreTests.test_actual_ingest_file_and_class_family_refs_are_one_hop_current_disk_citations` and 5 more |
| `MYC-4.10` | unit | `test_ranking.RankingTests.test_bridge_full_pools_caps_and_citer_order_are_independent_of_arms`, `test_ranking.RankingTests.test_once_only_bridge_agreement_before_weights` |
| `MYC-4.11` | unit | `test_ranking.RankingTests.test_all_entry_families_and_trigger_lifts`, `test_ranking.RankingTests.test_weighting_applies_to_bridge_and_wording_only_sources` |
| `MYC-4.12` | unit | `test_ranking.RankingTests.test_repository_patterns_override_packaged_defaults` |
| `MYC-4.13` | unit | `test_ranking.RankingTests.test_mixed_document_margin_both_routes_arms_and_caps`, `test_ranking.RankingTests.test_mixed_document_negative_no_code_and_no_vector_policies` |
| `MYC-4.14` | unit | `test_search_reply.SearchReplyTests.test_no_check_or_missing_exact_version_requirement_never_certifies_an_unmarked_chunk`, `test_search_reply.SearchReplyTests.test_no_fresh_overrides_prior_done_statuses_for_results_and_citations`, `test_search_reply.SearchReplyTests.test_pending_upstream_or_reachable_fault_keeps_only_affected_exact_checks_incomplete` and 3 more |
| `MYC-4.15` | unit | `test_search_cli.SearchCliTests.test_syntax_keeps_literal_option_shaped_queries_and_advertises_schema3`, `test_search_reply.SearchReplyTests.test_incompatible_scope_and_invalid_options_are_refused`, `test_search_reply.SearchReplyTests.test_meaning_participation_and_distinct_candidate_counts_are_explicit` and 4 more |
| `MYC-4.16` | unit | `test_check_real.RealProviderIsolationTests.test_disposable_check_cannot_read_owner_provider_key_or_send_a_query`, `test_search_cli.SearchCliTests.test_dimension_mismatch_uses_wording_without_query_credential_or_provider_access`, `test_search_cli.SearchCliTests.test_every_provider_failure_and_invalid_response_has_safe_wording_fallback` and 7 more |
| `MYC-4.17` | store | `test_search_store.SearchStoreTests.test_same_version_has_identical_result_and_citation_marks_in_one_snapshot`, `test_ranking_store.RankingStoreTests.test_actual_ingest_file_and_class_family_refs_are_one_hop_current_disk_citations`, `test_ranking_store.RankingStoreTests.test_actual_ingest_shared_version_branch_ref_cannot_restore_deleted_disk_source` and 4 more |
| `MYC-4.18` | store | `test_search_store.SearchFreshnessStoreTests.test_new_unpublished_upstream_fault_names_captured_section_in_downstream_reply`, `test_search_store.SearchFreshnessStoreTests.test_ref_faults_keep_only_the_affected_result_incomplete_after_finished_checks`, `test_search_store.SearchFreshnessStoreTests.test_unpublished_renamed_heading_fault_uses_captured_place_with_retained_identity` and 16 more |
| `MYC-4.19` | unit | `test_deadline.DeadlineBoundaryTests.test_every_sql_read_uses_remaining_allowance_and_restores_autocommit_settings_on_failure`, `test_deadline.DeadlineBoundaryTests.test_nested_deadline_context_and_cleanup_restore_the_original_allowance`, `test_deadline.DeadlineBoundaryTests.test_one_active_budget_bounds_nested_git_and_child_work_then_restores_current_index_reads` and 15 more |
| `MYC-4.20` | store | `test_search_store.SearchStoreTests.test_reply_counts_current_disk_versions_with_partial_failed_and_wrong_model_coverage`, `test_search_store.SearchStoreTests.test_unavailable_pinned_tokenizer_keeps_wording_and_unverified_plan_coverage`, `test_search_store.SearchStoreTests.test_dimension_mismatch_discards_supplied_query_vector_and_answers_by_wording_without_writes` and 1 more |
| `MYC-4.21` | store | `test_search_store.SearchFreshnessStoreTests.test_busy_source_and_skipped_or_expired_checks_keep_index_reply_and_unchanged_pending_source`, `test_freshness_store.FreshnessStoreTests.test_activity_finalization_refusal_preserves_committed_prefix_and_reports_pending`, `test_freshness_store.FreshnessStoreTests.test_busy_downstream_update_is_pending_without_scanning_or_changing_its_files` and 14 more |
| `MYC-4.22` | unit | `test_retrieval.RetrievalCandidateTests.test_candidate_arms_validate_limits_and_produce_distinct_bounded_lists`, `test_retrieval.RetrievalCandidateTests.test_empty_query_and_limits_refuse_in_every_corpus` |
| `MYC-4.23` | unit | `test_search_reply.SearchReplyTests.test_unreadable_results_explain_missing_or_escaping_files_without_inventing_paths`, `test_search_reply.SearchReplyTests.test_checkout_and_artifact_markdown_keep_actual_roots_canonical_places_and_stable_ids`, `test_search_store.SearchFileTests.test_actual_root_distinguishes_collisions_and_rejects_missing_and_escaping_files` |
| `MYC-4.24` | store | `test_retrieval_store.RetrievalStoreTests.test_organization_members_keep_separate_candidate_lists_and_limits`, `test_search_store.SearchStoreTests.test_each_organization_member_has_its_own_reply_and_result_limit` |
| `MYC-4.25` | eval | no on-demand report yet |
| `MYC-4.26` | store | `test_retrieval_store.RetrievalStoreTests.test_branch_stash_and_replaced_disk_versions_never_enter_candidates`, `test_retrieval_store.RetrievalStoreTests.test_snapshot_keeps_text_places_vectors_together_and_changes_no_store_rows` |
| `MYC-4.27` | store | `test_retrieval_store.RetrievalStoreTests.test_complete_current_model_parts_collapse_before_each_candidate_limit`, `test_retrieval_store.RetrievalStoreTests.test_deleted_planned_parts_and_failed_vectors_do_not_become_complete` |
| `MYC-4.28` | unit | `test_search_reply.SearchReplyTests.test_index_only_namespace_is_canonical_and_never_gains_a_file_from_metadata`, `test_search_reply.SearchReplyTests.test_checkout_and_artifact_markdown_keep_actual_roots_canonical_places_and_stable_ids`, `test_search_store.SearchFileTests.test_actual_root_distinguishes_collisions_and_rejects_missing_and_escaping_files` |
| `MYC-4.29` | store | `test_document_links.DocumentLinksStoreTests.test_search_described_is_query_independent_and_uses_unembedded_unselected_documents`, `test_document_links.DocumentLinksStoreTests.test_relations_generated_edges_other_code_transitive_and_branch_only_sections_do_not_describe` |
