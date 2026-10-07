---
role: authored
spec: MYC-4
status: draft
---
# Mycel · 04 Retrieval

Retrieval is what Mycel is for: a caller asks a question or names a symbol, and Mycel returns the chunks of code and documents that answer it, ranked. This specification fixes how a search is scoped, how its two kinds of matching are combined, how documents and code compete, what a result says about itself, and when a search first brings the index up to date. It matters because version 1's ranking rules did not hold as its own comments stated them, a result did not say how far it could be trusted or compared, and one kind of search skipped the freshness check.

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: the scope of a search, the two arms (by meaning and by exact wording), the two ranking routes, the bridge from documents to code, the place of documents in the ranking, annotations, the result contract, freshness on read, searching several repositories.

Not covered: how chunks are made ([MYC-1](01-corpora-and-ingest.md)); edges between chunks, staleness and Heartwood ([MYC-2](02-provenance-and-freshness.md)); vectors ([MYC-3](03-embedding.md)); the grep replacement with a search tail and the reading of one symbol's source, which are not part of the first version ([MYC-D4](00-overview-and-legacy-map.md#decisions)).

## Behaviour

### The scope of a search

Observed in version 1: a search covered one repository. Without a name it took the repository of the current directory, and when that belonged to none it searched a repository called `Arbol`. A search that included documents also searched the documents of the repository called `mycel`, whatever repository was asked for; that name was fixed in the code. A disabled repository was still searched: observed on 7 October 2026, a repository switched off in the settings kept answering from its stored chunks until its rows were deleted.

Proposed: a search covers the repository it names, or the one the current directory belongs to. When neither gives a repository the search is refused. Repositories whose documents take part in every search are listed in the settings ([MYC-D18](#decisions)). A disabled repository is not searched.

<!-- sources:
mycel_deprecated_v1:mycel/cli.py#search_payload
mycel_deprecated_v1:mycel/scope.py#resolve
mycel_deprecated_v1:mycel/knowledge/embedder.py#_doc_scope
-->

### Two arms

Observed in version 1, and kept: every search runs two kinds of matching over the same chunks.

| Arm | Finds | How |
|---|---|---|
| By meaning | Chunks that are about the query, whatever words they use | The query is embedded and compared with the chunks' vectors by cosine similarity |
| By exact wording | Chunks that contain the query's words | A BM25 index over the chunks' text |

Each arm returns its best candidates: the larger of the number of results asked for and 20. A chunk without a vector can be found by wording only. The index by wording covered the chunk's text; the chunk's name and path were indexed too but never searched, so a symbol's name matched only where it also appeared in the body.

Proposed: the name and the path of a chunk are searched by wording as well as its text.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search
mycel_deprecated_v1:mycel/knowledge/embedder.py#ensure_bm25_index
-->

### Two routes

Observed in version 1, and kept: the shape of the query decides how the arms are combined.

| Query | Route | Combination |
|---|---|---|
| Only letters, digits, `_`, `.`, `#`, `/` and `-`, with no space: `renewSession`, `auth/session.ts#renew` | Identifier | Reciprocal rank fusion: each arm adds 1/(60 + rank) to a chunk's score, both arms with the same weight |
| Anything else: `how does renewal decide` | Question | Cosine similarity is the score. Hits by wording that the meaning arm missed are appended below everything scored, in their own order |

One plain word, such as `payments`, counts as an identifier ([MYC-D19](#decisions)).

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search
-->

### The bridge from documents to code

Observed in version 1, on the question route: the eight document sections closest to the query were found by exact cosine. Each of them that belonged to the repository being searched was followed one step along its [Source Refs](../../arbol/GLOSSARY.md#source-ref) to the code it cites, and at most three code chunks per section, the three closest to the query, entered the ranking with the section's similarity times 0.92. A result that came this way named the section in a `via` field. When a chunk was found both directly and through a section, its score was raised by 0.05.

The raise was applied once for every section and every edge that reached the chunk, not once per chunk, so a chunk cited by eight sections could gain 0.40.

Proposed: the bridge is kept, with the raise given once per chunk. It is why documents with Source Refs pay off: prose matches the question, and the edges deliver the code.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#_bridge_expand
mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search
-->

### Down-weights

Observed in version 1: three families of chunks mirror the wording of features and would outrank the code they describe or accompany.

| Family | Recognised by | Question route | Identifier route | Lifted when the query says |
|---|---|---|---|---|
| Tests | `.spec.` and `.test.` files, `__tests__` folders, `test_*.py`, `conftest.py`, `_test.py`, `_test.go` | × 0.93 | × 0.85 | test, spec, e2e, mock, fixture |
| Generated code | `.generated.` files, `gql/types.ts` | × 0.93 | not applied | type, schema, graphql, gql, codegen, generated |
| Structural chunks | Whole-file, module, markup and style chunks | × 0.9 | × 0.75 | never |

The factors were applied only to chunks the meaning arm had found directly. A chunk that entered through the bridge or through the wording arm alone got none of them.

Proposed: the same families and factors as starting values ([MYC-D20](#decisions)), applied to a chunk however it entered the ranking. The patterns for tests and generated code are settings of a repository, with these as the defaults.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search
-->

### Documents among the results

Observed in version 1, on the question route: a document section became a result of its own only when its similarity was at least 0.03 above the best code score, at most two such sections were returned, and the routing files `INDEX.md` and `README.md` were never returned this way. The comments in the source stated these as general rules.

They were not. A document found by the wording arm was appended with the other wording hits, where none of the three rules applied. On the identifier route a document could score through the wording arm only, so it could reach at most half the score of a code chunk found by both arms. The best code score that a document had to beat included the bridge scores and their repeated raises, so the bar could lie above any real similarity.

Proposed: the three rules hold for every way a document can enter a ranking that also holds code, and the bar is the best direct code similarity. A search for documents only has no such rules: every result is a document.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search
mycel_deprecated_v1:mycel/knowledge/embedder.py#doc_search
-->

### What a result says

Observed in version 1: a result of the usual search carried the chunk's place (path, name, kind, lines), a score, its rank in each arm, a preview of 240 characters, the file to read, and two annotations: `via`, the document section that delivered it, and `documented_in`, up to two document sections whose Source Refs cite it. Stale and Heartwood marks appeared only inside those annotations; a result that was itself a stale or Heartwood document did not say so. The score was on one of three scales, a cosine, a rank fusion value of at most about 0.033, or about 0.999 for wording hits when no vector could be made, and nothing said which. A search for documents only returned results of a different shape under the same version number.

Which two sections `documented_in` named was left to the database: the query had no order.

Proposed: one shape for every result. Each result says whether it is stale and whether it is Heartwood. The reply names the route that was taken and says whether the meaning arm took part. `documented_in` is ordered by the similarity of the citing section to the query, then by path.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search
mycel_deprecated_v1:mycel/knowledge/embedder.py#doc_search
mycel_deprecated_v1:mycel/knowledge/embedder.py#_documented_in
mycel_deprecated_v1:mycel/retrieval.py#_payload
mycel_deprecated_v1:mycel/retrieval.py#_read_location
-->

### When the meaning arm cannot run

Observed in version 1: without a key, the search went on by wording alone and showed it only as a count of zero. With a key and an error from the embedding service, the whole search failed. Observed on 7 October 2026: that count is of code chunks only, so a corpus of documents always shows zero, which reads as a failure when it is not.

Proposed: a search never fails because the query could not be embedded. It answers by wording, and the reply says that the meaning arm did not take part and why.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#_query_vec
mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search
-->

### Freshness on read

Observed in version 1: before searching, Mycel looked for any file in the repository changed since the last pass, and if it found one it ran a pass over that repository alone. That pass fetched nothing from a remote and embedded nothing, so chunks it added or changed could be found by wording only, and the reply did not say so. The check walked the whole tree with no time limit. A search for documents only skipped the check altogether: observed on 6 October 2026, such a search kept returning files that had been deleted from disk until a search of the usual kind was run.

Proposed: every kind of search runs the check unless the caller turns it off. The check has a time limit, after which the search runs on the index as it is and says so. The reply states how many chunks of the repository are waiting for a vector.

<!-- sources:
mycel_deprecated_v1:mycel/retrieval.py#search
mycel_deprecated_v1:mycel/cli.py#search_payload
mycel_deprecated_v1:mycel/syncpass.py#repo_stale
mycel_deprecated_v1:mycel/syncpass.py#run_repo_pass
-->

### Side effects of a search

Observed in version 1: every search created the wording index if it was missing and copied the settings file into the index store. A read wrote.

Proposed: a search writes only what its freshness check ingests. The index's structure is made by the command that sets the index up, and settings are read from the settings file.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#ensure_bm25_index
mycel_deprecated_v1:mycel/cli.py#search_payload
mycel_deprecated_v1:mycel/config.py#load_apply
-->

### Several repositories

Observed in version 1: naming an organization searched each of its member repositories in turn and returned one full reply per member, not merged, with the number of results applying to each.

Proposed: kept. Scores of different repositories are not compared.

<!-- sources:
mycel_deprecated_v1:mycel/cli.py#search_payload
mycel_deprecated_v1:mycel/organizations.py#resolve
-->

## Requirements

| ID | Mycel must… | Origin | Verified by |
|---|---|---|---|
| MYC-4.1 | search the repository an invocation names, or the one the current directory belongs to, and refuse the search when neither gives one. No repository's name is built in | Changed | unit |
| MYC-4.2 | leave a disabled repository out of every search | Changed | store |
| MYC-4.3 | add the documents of the repositories the settings list as shared to a search that includes documents, and to no other | Changed | store |
| MYC-4.4 | match by meaning and by exact wording in every search, and find by wording a chunk that has no vector | Kept | store |
| MYC-4.5 | match by wording on a chunk's text, its name and its path | Changed | store |
| MYC-4.6 | take the identifier route for a query made only of letters, digits, `_`, `.`, `#`, `/` and `-`, and the question route for any other | Kept | unit |
| MYC-4.7 | on the identifier route, score by reciprocal rank fusion of the two arms with equal weight | Kept | unit |
| MYC-4.8 | on the question route, score by cosine similarity and place wording hits the meaning arm missed below every scored result | Kept | unit |
| MYC-4.9 | on the question route, follow the closest document sections of the searched repository one step along their Source Refs to the code they cite, and name the section on every result it delivered | Kept | store |
| MYC-4.10 | raise the score of a chunk found both directly and through a section once, however many sections cite it | Changed | unit |
| MYC-4.11 | apply the down-weights for tests, generated code and structural chunks to a chunk however it entered the ranking, and lift the first two when the query asks for them | Changed | unit |
| MYC-4.12 | take the patterns that recognise tests and generated code from the repository's settings, with version 1's as defaults | Changed | unit |
| MYC-4.13 | return a document among code results only when it clearly beats the best direct code match, at most twice per search, and never a routing file. The rule holds on both routes and for both arms | Changed | unit |
| MYC-4.14 | give every result the same fields in every kind of search, among them whether the chunk is stale and whether it is Heartwood | Changed | unit |
| MYC-4.15 | name in the reply the route taken and whether the meaning arm took part, with the reason when it did not | New | unit |
| MYC-4.16 | answer by wording alone, and say so, when the query cannot be embedded. A search does not fail for that reason | Changed | unit |
| MYC-4.17 | order equal scores and the entries of `documented_in` by a stated rule, so that the same index and query give the same reply | Changed | store |
| MYC-4.18 | check before every kind of search whether the repository's files changed since its last pass, ingest what changed, and say in the reply what it did. The caller can turn the check off | Changed | store |
| MYC-4.19 | end the freshness check at its time limit and search the index as it is, saying that the check was not finished | Changed | unit |
| MYC-4.20 | state in the reply how many present chunks of the searched repository have no vector | New | store |
| MYC-4.21 | write nothing during a search except what the freshness check ingests | Changed | store |
| MYC-4.22 | refuse a number of results below 1 or above 100, and an empty query, in every kind of search | Changed | unit |
| MYC-4.23 | give the file to read for a result only when it lies inside the repository's configured folder and exists, and otherwise say why it cannot be read | Kept | unit |
| MYC-4.24 | search the members of an organization one by one and return one reply per member, never one merged list | Kept | store |
| MYC-4.25 | keep an evaluation set of queries with the chunks each should find, report recall at 3 and at 10 for it, and change a ranking rule or a constant only with that report for before and after | New | eval |

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
    finished: boolean;                 // false when the time limit ended the check
    ingested: number;                  // chunks the check added or changed
    withoutVector: number;             // present chunks of the repository that have no vector
  };
  results: SearchResult[];
}

interface SearchResult {
  id: string;
  repository: string;
  origin: "code" | "document";
  path: string;                        // relative to the repository's code or document folder
  name: string;                        // symbol for code, heading path for a document
  kind?: string;                       // function, method, class, section and so on
  lines?: { start: number; end: number };
  score: number;                       // comparable only within one reply
  ranks: { meaning?: number; wording?: number };
  stale: boolean;
  heartwood: boolean;
  via?: Citation;                      // the document section that delivered this result
  documentedIn: Citation[];            // at most two sections whose Source Refs cite it
  preview: string;                     // the first 240 characters of the chunk
  file?: string;                       // absolute path to read, when readable
  unreadable?: string;                 // the reason, when there is no file
}

interface Citation { document: string; repository: string; stale: boolean; heartwood: boolean }
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

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#code_search
mycel_deprecated_v1:mycel/knowledge/embedder.py#doc_search
mycel_deprecated_v1:mycel/knowledge/embedder.py#_bridge_expand
mycel_deprecated_v1:mycel/knowledge/embedder.py#_query_vec
mycel_deprecated_v1:mycel/retrieval.py#search
mycel_deprecated_v1:mycel/cli.py#search_payload
-->

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D18 | Do the documents of another repository take part in every search? | Yes, for the repositories the settings list as shared, which replaces version 1's fixed name. The first list holds `mycel`, so the guides on how to work keep surfacing in every repository | Open |
| MYC-D19 | Is one plain word an identifier? | Yes in the first version, as in version 1. The evaluation set decides whether a word that matches no symbol should take the question route instead | Open |
| MYC-D20 | Where do the factors, margins and limits start? | At version 1's values: 0.92 and 0.05 for the bridge, 0.03 and two for documents, the down-weights of the table above, 60 for rank fusion, eight sections and three chunks per section. They change only under MYC-4.25 | Open |
| MYC-D21 | Are the results of several repositories merged into one list? | No. One reply per repository, as in version 1; scores of different repositories are not comparable | Open |
| MYC-D22 | Does switching a repository off also hide it from search? | Yes. A repository that should stay searchable without being ingested is rare, and version 1's behaviour surprised its owner | Open |
