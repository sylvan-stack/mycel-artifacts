---
role: authored
---
# Guide: Code Research (level 2)

Answer a question that needs evidence across files, in the session with
file-and-line citations. Exact lookups are [level 1](code-research-levels.md);
a durable task-context artifact is [level 3](deep-research.md).

## The loop

1. **Check whether retrieval is ready.** The [Hub's dated pre-ingest rule](../README.md)
   currently requires grep and file reads. After the owner fills the index,
   start with `mycel search --repo <repo> "<the question>"`; try a few phrasings
   when vocabulary is uncertain. From a prepared folder always pass the
   repository. Normal search can check local freshness and embed the query;
   it does not embed pending corpus text. `--no-fresh` suppresses freshness
   writes, not the query request.
2. **Read the documents the results cite.** `via` identifies a document bridge;
   `documentedIn` gives ranked document citations. Read those sections before
   using them to interpret code. `stale`, `staleReasons`, `heartwood` and
   `dependencyCheck` say what was checked; an incomplete check is not current
   verification. The [retrieval guide](retrieval.md) links the exact reply
   contract. For structural orientation use the stored overview through
   `mycel overview --repo <repo>` when it exists.
3. **Fill the gaps with targeted code reads.** Follow actual `file`, `lines`
   and qualified `address` fields. `mycel read '<qualified-address>'` returns
   full indexed text and all directly describing document sections; use file
   reads and grep to verify current working-tree behavior. A prepared folder
   may contain branch work that differs from the indexed readonly clone.
4. **Answer with citations.** Separate verified code behavior from document
   claims, and identify stale evidence or limits that affect the answer.
5. **Persist only useful synthesis.** When the investigation is expensive and
   reusable, update the existing research document or write one under the
   repository's resolved `research/` folder. Follow the
   [Source Refs authoring guide](source-refs-authoring.md). A quick one-file
   answer needs no new artifact.

If several honest searches find no useful result, use grep and direct reads.
A glossary entry with real file/symbol Source Refs can make missing vocabulary
retrievable later; an empty or stale index must never be reported as proof
that the implementation is absent.

<!-- sources:
mycel:@code/src/mycel/_search_reply.py
mycel:@code/src/mycel/_read_store.py
mycel:@code/src/mycel/_document_links.py
-->
