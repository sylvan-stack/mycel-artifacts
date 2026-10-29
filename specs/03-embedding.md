---
role: authored
spec: MYC-3
status: implemented
---
# Mycel · 03 Embedding

Embedding turns the complete text of every [Chunk](../../arbol/GLOSSARY.md#chunk) into one or more vectors, so that a search can find it by meaning. This specification fixes what text is embedded, which chunks are embedded and when, how failures are handled, and what the counts in a status report mean. It matters because in version 1 one failed request ended a whole pass, the counts did not match what a pass would do, and the rule that kept some repositories off the external service had gaps.

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: the embedding model and its provider, the packaged tokenizer and model limits, the text sent for a chunk, deterministic part planning, the pending rule, the embed operation and its scope, failures and retries, the counts, the key.

Not covered: how chunks come to exist and get their identity ([MYC-1](01-corpora-and-ingest.md)); how vectors are searched ([MYC-4](04-retrieval.md)); summaries of chunk clusters ([MYC-8](08-summaries.md)); the settings that name the model, the attempts and the place of the key ([MYC-5](05-settings.md)).

## Behaviour

### The model and the provider

Observed in version 1: chunks were embedded by the Voyage service with the model `voyage-code-3`, 1024 dimensions, 64 texts per request, 60 seconds per request, one attempt per batch. Chunks were sent with the input type `document`, queries with `query`. Nothing limited the length of a text; the request carried no truncation setting, so an over-long text was left to the service's default.

A second profile, `local`, sent texts to a separate program on the same machine that held an on-device model with the same number of dimensions. That program was a service of Arbol 1. Vectors of both models were stored in one column and one index; only the repository name kept them apart.

Decided: Voyage API is the only embedding provider; no on-device provider is supported ([MYC-D16](#decisions)). The default model is `voyage-code-4` at 1024 dimensions ([MYC-D14](#decisions)). It is Voyage's current code-family successor to `voyage-code-3`, checked on 8 October 2026 against the [Voyage announcement](https://blog.voyageai.com/2026/08/13/voyage-code-4/) and [model documentation](https://www.mongodb.com/docs/voyageai/models/text-embeddings/). Every vector is stored with the name of the model that produced it, and a search compares a query only with vectors of the model the query was embedded with. A change of model makes every chunk pending again; no command is needed to say so.

### The tokenizer and limits

Agent-selected contract for the first implementation: a Build carries a model catalog and the corresponding tokenizer files. The initial catalog supports `voyage-code-4` with 256, 512, 1024 or 2048 dimensions; 1024 remains the owner-selected default. An unknown model or unsupported dimension is a detailed `settings` fault before any provider call. Adding a model requires a catalog entry, its official tokenizer, locally checked limits and fixtures in a new Build; a setting alone cannot select an unverified tokenizer. Changing dimensions still requires `mycel init` under MYC-6.

Voyage publishes model-specific tokenizers and its [Python client](https://github.com/voyage-ai/voyageai-python/blob/main/voyageai/_base.py) counts tokens with Hugging Face's `tokenizers` library, without truncation. Mycel uses that encoding contract with a packaged local file, never an unspecified model tokenizer, a character estimate or a runtime download. [Voyage's tokenization documentation](https://docs.voyageai.com/docs/tokenization) describes the model-specific counting contract.

The first catalog pins the official [`voyageai/voyage-code-4` repository](https://huggingface.co/voyageai/voyage-code-4/tree/ac780b405e54ff8b3aff681270e0e03840fed2f3) at revision `ac780b405e54ff8b3aff681270e0e03840fed2f3`, using `tokenizer.json` with SHA-256 `c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539`. These identifiers were checked against the public files on 8 October 2026, without an embedding call. The Build locks the exact `tokenizers` library version and records it with this revision, digest and planner version. Loading disables padding and truncation and retains the file's normalizer and post-processor; that affects counting, not the original text sent or stored. Missing or mismatched tokenizer files are a local planning failure; no approximate input is sent.

The provider documents a 32,000-token context and at most 1,000 inputs per request. Its current total-batch-token table omits `voyage-code-4`; Mycel does not borrow the larger limit of another model. Chosen first values are a 31,744-token cap for each input and the sum of inputs in a batch, at most 64 inputs per batch, and one in-flight request per repository embed. The 256-token margin and conservative batch cap are agent defaults, not measured throughput values or a claim about Voyage's exact batch allowance. Provider rejection remains visible and is handled without truncation. [Voyage embedding limits](https://docs.voyageai.com/docs/embeddings).

Keep two local counts using the same pinned tokenizer. The submitted-string count encodes exactly the complete place line, newline and part (or query string) and is compared with the provider's input-text usage in the live check. The conservative planning count additionally accounts for Voyage's documented document/query prompt and is used for input/batch caps and dry-run estimates. That prompt is not added to the submitted string: `input_type` asks the provider to add it. Provider-reported usage remains a separate measurement. Under [MYC-D42](13-checks-and-evaluation.md#decisions), the live report states whether usage matches the submitted count and retains their signed difference; disagreement does not fail compatibility or replace the pinned counts used for input/batch limits. Equality is never asserted against the larger planning count. Saved plans record all these limits and counting choices. The model catalog is immutable within a Build and changes only through a new Build, so an upstream tokenizer update cannot change plans during an invocation.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embed`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_profile_for`
- `mycel_deprecated_v1:mycel/knowledge/local_embedder.py#embed`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema`

### The text that is embedded

Observed in version 1, and kept: the chunk's own text is never changed, but the text sent for embedding starts with one line that says where the chunk is.

Proposed: retain that place line on every input, followed by one embedding part of the chunk's complete text:

| Chunk | Text sent |
|---|---|
| A symbol of a code file | `<path> — <symbol> (<kind>)`, a line break, the part's text |
| A section of a document | `<path> › <heading path>`, a line break, the part's text |

The path and the name often carry meaning the body lacks: a file called `invoice-export.service.ts` says "invoice export" even when its code never does. The place line is repeated on every part and counts toward the model's input limit. The complete body is sent across the parts; no part is trimmed or summarised. A query is embedded as it was typed, with nothing added. Its complete input is checked against the model's limit too; one that cannot fit is refused locally without truncation, and search uses the wording fallback of MYC-4.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_embed_text`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_query_vec`

### Embedding parts

A chunk remains one section or symbol with one identity ([MYC-1](01-corpora-and-ingest.md)). For the selected model, Mycel makes an ordered plan of embedding parts for each version of that chunk ([MYC-D17](#decisions)). A short chunk has one part. A longer one has consecutive, non-overlapping spans whose concatenation is exactly the stored text, including headings, comments, whitespace and the final characters. Splits are at Unicode character boundaries, preferring paragraph or code-line boundaries when they fit. Nothing is normalised, summarised or discarded to fit. An empty body still has one part carrying its place line.

The first embed saves the plan before sending any part. Status and dry-run reporting compute provisional plans locally without writing them: valid new work counts as pending and a plan that cannot be made is reported as a planning failure. The plan stores the exact-text chunk version, model and dimensions, tokenizer revision, file and library digests, planner version, limits, each part's order and byte offsets into the original UTF-8 text, token count, and the place line used for its inputs. The same exact text, place line and catalog give the same plan. Every complete input is measured with the pinned model tokenizer under the counting rule above and fits the chosen cap. Batches fit the catalog's token and input-count caps. Provider truncation is disabled. If a non-empty input cannot fit even its next Unicode character with the complete place line, or cannot be checked reliably, Mycel records a local planning failure instead of dropping text or sending an oversized input.

Planner version 1 proceeds from the next uncovered byte. If all remaining text fits, it takes all of it. Otherwise, an untruncated encoding under the counting rule above gives the last original-text character boundary covered by the first input-cap tokens as a tentative end. For documents, a paragraph boundary is after a blank line containing only spaces or tabs and its line ending; for code, a line boundary is after any line ending. The planner tries those boundaries no later than the tentative end, latest first, re-encoding the complete resulting input with the repeated context, and takes the first that fits and advances. If none advances and fits, it tries the tentative character boundary and moves backwards by Unicode characters until one fits. If it cannot advance, planning fails. Boundary lookup uses offsets into the original text, never decoded token text, so normalization and tokens spanning characters cannot lose or duplicate bytes. A conforming optimization must produce these same ranges. Inputs are batched greedily in repository, chunk identifier, exact-text version and part order, ending a batch before the next input would exceed either cap.

Each part receives a vector of its own; the vectors are not averaged into a single substitute. A version has complete coverage only after every part of its valid plan has a vector of the current model and dimensions. Saved parts retain their plan and place line through a metadata-only rename, move or branch switch when the exact stored text is unchanged, so a retry does not mix a newly generated prefix with earlier inputs. A heading or symbol edit that changes stored text creates a new version and plan even when normalized comparison says its body is equivalent; that comparison serves identity matching and freshness, not embedding-version identity. This does not renew dependency pins or confirm the section. A model change creates a new plan and makes its parts pending. A catalog change with the same model and dimensions may retain a saved plan only after validating its recorded tokenizer and inputs against the current caps; otherwise it creates a replacement plan with pending parts and retains no vector from differently planned inputs. Source Refs, edges, hashes and staleness continue to refer to the whole chunk or file, never to an embedding part. Search compares the parts and returns the original chunk ([MYC-4](04-retrieval.md)).

### Which chunks are pending

Observed in version 1: a chunk was pending when it was present and had no vector. Ingest cleared the vector of a chunk whose content changed and kept the vector of a chunk that was only renamed. A pass took every pending chunk of every repository in one list, ordered by identifier. A chunk of a disabled repository was skipped. A chunk of a repository that had no settings row was treated as enabled and sent to the external service.

Proposed: each vector belongs to one part of one exact-text chunk version, one model and one dimension. A part is pending when its repository is enabled, it lacks a vector of the current model and dimensions and it has no recorded failure. A failed part does not stop other pending parts of that version from being embedded. A version is fully embedded only when all of its parts have vectors. These rules hold wherever the version is found: on disk, in a local branch or in a stash. The same exact text of one chunk shared by several locations has one plan and is embedded once; a branch switch alone makes no retained exact-text version pending. A disabled, unknown or removed repository has no pending work.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embed_pending`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code`

### The embed operation

Observed in version 1: `mycel embed` took no arguments and processed every pending chunk of every enabled repository. `mycel sync` did the same after its pass unless told not to. Each chunk's vector was stored as soon as its batch came back, so an interrupted pass kept what it had done. An error from the service ended the pass. Because the list was in a fixed order, a batch the service rejected would be the first batch of every later pass (inferred from the source, not seen happening).

Proposed:

- **Scope.** An embed names what it covers: one repository, several, or all enabled ones. Nothing embeds across all repositories as a side effect of another command.
- **Progress survives.** Each returned part's vector is stored batch by batch. Stopping an embed or losing the connection keeps completed parts; a later pass sends only the missing parts. Partial coverage is never reported as fully embedded.
- **One bad text does not block the rest.** A request that fails for a reason that can pass (no network, a time limit, a rate limit, a server error) is tried again with growing pauses. A batch rejected for its content is divided into smaller batches until the parts at fault are found; their failures and reasons are recorded, and other pending parts are embedded. Failed parts or a failed plan are tried again only when the content or model changes, or the owner asks; successful parts are retained.
- **Length.** Split the complete chunk text into model-sized embedding parts before sending; never cut off a tail. Measure each complete input and each batch before sending, and disable provider truncation. If no valid plan fits, record a failure and preserve the complete text ([MYC-D17](#decisions)).
- **Dry run.** Report the chunk versions and input parts the pass would send, the estimated tokens including repeated place lines, and local planning failures, without sending anything.

Provider requests use `POST https://api.voyageai.com/v1/embeddings` with the selected model, explicit `output_dimension`, `output_dtype = "float"`, `input_type = "document"` for parts or `"query"` for a query, and `truncation = false`. A request has a 60-second total deadline. Transient failures are connection/deadline failures, HTTP 408, 429 and 5xx; the selected attempt count includes the first send. Before later attempts, waits are 1, 2, 4 and 8 seconds, capped at 30 seconds if more attempts are configured. A valid `Retry-After` increases that wait up to a 60-second cap. Every wait is interruptible. Authentication/authorization or missing-model failures stop sending for that repository and leave unsent work pending; they are not blamed on individual texts. Content or length rejection is isolated by splitting the batch, without changing its saved inputs or enabling truncation.

A response must have exactly one indexed vector per submitted input, without duplicate or missing indices, and each vector must contain exactly the configured number of finite values. Validate the entire provider response before any write. Under MYC-6's commit guards, atomically persist all vectors whose exact versions are still retained, discarding only vectors for versions deleted meanwhile. Counts exclude those discarded vectors. An invalid response is a provider failure, writes none of the batch, leaves its retained parts pending and never counts as coverage. Counts and a sanitized failure reason are returned if work stops after earlier batches succeeded. Raw provider bodies and authorization headers are not copied into output or activity. The key acquisition boundary is MYC-5.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embed_pending`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_embed`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_sync`

### Counts

Observed in version 1: the status report gave two numbers, embedded and pending, for the whole index, whatever repository was asked about. Pending included chunks of disabled repositories, which no pass would ever embed. Observed on 7 October 2026: after the repository that held 11,973 of 13,707 pending chunks was disabled, the report still said 13,707.

Proposed: counts are per repository and distinguish chunk versions from input parts. Counts and dry-run estimates include locally computed plans, so a new version with no saved plan is not omitted; a plan that cannot be made is reported as a failure. A version is embedded only with a valid plan and a vector for every part. It is pending while it has at least one sendable pending part, even if another part failed; it is failed when a planning failure is recorded, or a part failure is recorded and no pending part remains. Disabled, unknown and removed repositories have no pending work; incomplete coverage is never classified as a failure merely because the repository is ineligible. These three version counts are disjoint. Part counts are embedded, pending and failed separately, so a pending version's failed parts remain visible. Pending parts are exactly what an ordinary next pass would send; `--retry-failed` additionally selects the failed parts or remakes a failed plan. A version is never counted as embedded merely because one vector was saved.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#pending_count`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embedded_count`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_status`

### The key

Observed in version 1: the key of the embedding service was read from the macOS Keychain, from an item named for Arbol's embedder, on every request. There was no other source.

Decided: Mycel reads the key from the place its settings name, by default a Keychain item of its own, or else a command of the owner's that prints it ([MYC-D15](#decisions)). The item is one documented credential shared with compatible settings editors. Arbol can create and replace the same item so that it continues to configure the owner's secrets, including the Voyage API key. A key set through Arbol is the key Mycel subsequently reads; no duplicate secret is kept. Mycel also works when another editor sets the item and nothing of Arbol is installed. The Keychain identity and access rules must support both writers and readers. The key is never an argument, never in the settings file and never in output. This decision permits a compatible editor to write the credential; it does not add an Arbol code or process dependency to Mycel.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_api_key`
- `mycel_deprecated_v1:mycel/macos_keychain.py#get_password`

## Requirements

| ID | Mycel must… | From v1 | Verified by |
|---|---|---|---|
| MYC-3.1 <!-- aa1df4e1-99f1-4020-90d2-e9f5570f3dd3 --> | embed the complete text of every version of every chunk of an enabled repository, in whatever location it is found, with one named model, and store the model's name with every part's vector | Changed | store |
| MYC-3.2 <!-- 711eafa4-3c84-4416-aff8-a73bf95609e2 --> | start every part's input with the plan's place line: path, symbol and kind for code; path and heading path for a document. The chunk's stored text stays as it is in the file | Changed | unit |
| MYC-3.3 <!-- ab0ba214-7916-42c2-9b9c-d151229438ab --> | embed a query as typed, with the model's query input type; check its complete input locally and refuse it without truncation when it exceeds the model's limit | Changed | unit |
| MYC-3.4 <!-- 3af59333-5f5d-4fd7-bc32-e8b600850866 --> | treat a part as pending exactly when its repository is enabled and it has no vector of the current model and no recorded failure, and allow other pending parts of a version to proceed when one part fails | Changed | store |
| MYC-3.5 <!-- 78751471-a9c6-41b2-b0ca-d5327340b228 --> | keep a plan and one vector per part for each exact-text chunk version, model and dimensions: any change to stored text, including a heading or symbol rename, is a new version without vectors; keep the saved plan, place line and vectors through metadata-only name, place or location changes when exact stored text is unchanged | Changed | store |
| MYC-3.6 <!-- 4074eea6-9202-485f-ad0a-af673ba947cc --> | embed only the repositories an invocation names, or all enabled ones when it says so. No other command embeds chunks of a repository it was not asked about | Changed | store |
| MYC-3.7 <!-- 67684df4-f6b1-47cc-8da1-0b92abfcdbdc --> | store completed parts' vectors batch by batch, retain them after interruption or failure, and send only missing or explicitly retried failed parts on the next pass | Changed | store |
| MYC-3.8 <!-- 0309e151-44a8-45bb-9369-175472ae1fcd --> | try a request again, with growing pauses, when it failed for a reason that can pass, and give up on the pass only after the attempts its settings allow | Changed | unit |
| MYC-3.9 <!-- 5e9b0b2d-d5c0-4e63-b68d-28074542117e --> | find the parts at fault when the service rejects a batch for its content, record each failure and reason on its part, and embed the other pending parts | New | unit |
| MYC-3.11 <!-- 469214f2-e3d2-4bf9-9399-78802d81c40f --> | report without sending anything the chunk versions and input parts an embed would send, roughly how many tokens including repeated place lines, and any planning failures | New | store |
| MYC-3.12 <!-- 32d32a5c-b28c-45a0-82d3-fffb7b9352a1 --> | report per repository version counts for embedded, pending and failed under the coverage rules, and separate part counts; pending parts are exactly what an ordinary next embed would send | Changed | store |
| MYC-3.13 <!-- 5d8045a9-b477-480c-9c2c-21682161eb0a --> | never send text of a disabled, unknown or removed repository to the embedding service | Changed | store |
| MYC-3.14 <!-- 65762893-4165-464e-841d-a185cce252cf --> | read the key from the place its settings name and nowhere else; document one Keychain identity that Arbol or another compatible editor can create and replace and that Mycel can read, without duplicate secrets or an Arbol dependency; never print the key, pass it as an argument or write it to a file | Changed | unit |
| MYC-3.15 <!-- 519e80c9-87e4-434c-8f98-99475d198e71 --> | create a new plan with pending parts when the model changes, without carrying failures from the old model into it, and never search vectors with a query embedded by another model | New | store |
| MYC-3.16 <!-- a2182957-dbae-435f-a3df-5f919db1bad8 --> | split each chunk version's text into ordered parts whose concatenation is exactly the complete stored text, with offsets at Unicode character boundaries; embed every part independently without trimming, summarising or changing the logical chunk's identity | New | unit |
| MYC-3.17 <!-- e75d0da7-664e-4aaf-90b5-45ccc8d576f6 --> | retain each part's range, order, saved input context, vector and failure under its chunk version and model, and mark that version fully embedded only when every part of a valid plan has a vector | New | store |
| MYC-3.18 <!-- 82dda01c-602c-44ab-b122-da2bc821f721 --> | measure every complete input and batch against the selected model and provider limits before sending, disable provider truncation, and record a local failure without discarding text when a valid input plan cannot be made | New | unit |
| MYC-3.19 <!-- 2ea16608-437e-4936-9062-8c8f49d71960 --> | package and verify each supported model's official pinned tokenizer and catalog; count with that tokenizer locally without padding, truncation, approximate counts or runtime downloads, and retain tokenizer, planner and limit provenance in every saved plan | New | unit |
| MYC-3.20 <!-- cbe4d462-32d9-4e7e-acf4-f0c7cfbae4ac --> | produce deterministic version-1 part ranges and batches under the algorithm above, using original UTF-8 offsets and remeasuring each final complete input, with full coverage or an explicit planning failure | New | unit |
| MYC-3.21 <!-- e833592b-4fce-4444-be47-4627f4884433 --> | send explicit model, dimensions, float output, input type and disabled truncation; follow the request deadline, transient retry and authentication/model failure rules above without replacing saved inputs | New | unit |
| MYC-3.22 <!-- ca789879-12b7-454e-840c-2ce30119fefa --> | validate every returned vector's index, finite values and dimensions, atomically persist a wholly validated batch for still-retained versions, discard vectors only for versions deleted meanwhile, and report sanitized stopping reasons without exposing provider bodies or credentials | New | unit |

MYC-3.10, which allowed cutting off the body's end, was withdrawn on 8 October 2026 by MYC-D17. MYC-3.16 to MYC-3.18 replace it with complete coverage through bounded inputs.

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

```sh
mycel embed --repo core                  # the pending chunks of one repository
mycel embed --repo core --repo mycel     # of several
mycel embed --all                        # of every enabled repository
mycel embed --repo core --dry-run        # what would be sent; nothing is sent
mycel embed --repo core --retry-failed   # also the chunks marked as failed
```

`mycel embed` without `--repo` or `--all` embeds the repository of the current directory, or every enabled member of the organization whose folder it is (MYC-1.4), and is refused when the directory belongs to neither.

```ts
interface EmbedResult {
  model: string;                       // the model that produced the vectors
  dimensions: number;
  planner: { version: number; tokenizerRevision: string; tokenizerSha256: string };
  repositories: Record<string, {
    sent: number;                      // chunk versions made fully embedded in this invocation
    failed: number;                    // versions failed afterwards under the coverage rules
    pending: number;                   // versions with at least one pending part afterwards
    parts: {
      sent: number;                    // input parts successfully embedded in this invocation
      pending: number;                 // parts an ordinary next pass would send
      failed: number;                  // parts blocked by a recorded failure
    };
    error?: { code: "refused" | "internal"; message: string }; // sanitized provider stop after work started
  }>;
  stopped?: "interrupted" | "gave_up"; // absent when the embed finished
  estimate?: { versions: number; parts: number; tokens: number; planningFailed: number }; // only with --dry-run
}
```

## Known problems in version 1

- **One failure ended a pass.** A request was made once, with no retry. An error from the service ended the pass with everything after it still pending.
- **The counts did not describe a pass.** Pending was one number for the whole index and counted chunks that no pass would embed.
- **Embedding was all or nothing.** No command embedded one repository. Observed on 7 October 2026: bringing one small corpus up to date would have sent 13,707 chunks of every repository.
- **The rule that kept text off the external service had gaps.** A repository without a settings row was treated as enabled and external. Summaries were always embedded by the external service, whatever profile their repository had. A disabled repository's query text was still sent to be embedded.
- **Two models shared one index.** Nothing but the repository name told the vectors of the two models apart.
- **The on-device model belonged to another product.** The `local` profile needed a service of Arbol 1 to be running, and the model files under Arbol's application folder. Observed on 7 October 2026: that folder held no model, and every repository used the external service.
- **The key was Arbol's.** The Keychain item was named for Arbol's embedder, and the message for a missing key sent the reader to an Arbol window.
- **A changed text lost its vector for good.** The vector of the earlier text was cleared, so a switch to another branch and back embedded every chunk that differed twice (inferred from the rule, not seen happening).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embed`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embed_pending`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#pending_count`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_query_vec`
- `mycel_deprecated_v1:mycel/knowledge/raptor.py#build_tree`
- `mycel_deprecated_v1:mycel/knowledge/local_embedder.py#is_available`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D14 <!-- 12dd47db-51a5-409a-92ce-8abfd355b89d --> | Which model and provider embed the chunks? | Voyage's code-family model with 1024 dimensions. The model is a setting, so another can be named later at the cost of embedding everything again | Decided 8 October 2026 by the owner: agreed, after checking for a newer Voyage code-family model. The check found `voyage-code-4`, released 13 August 2026, which replaces `voyage-code-3`; use it at 1024 dimensions |
| MYC-D15 <!-- d4315335-7aec-4002-ba0f-764ffe798a20 --> | Where does the key of the embedding service come from? | A Keychain item of Mycel's own, read with the system's `security` command, unless the settings name a command that prints the key | Decided 8 October 2026 by the owner: Mycel's own Keychain item is OK only if Arbol can also write it. Preserve Arbol configuring all secrets, including the Voyage API key; Mycel reads the same credential and remains independent of Arbol |
| MYC-D16 <!-- bf3d4a96-490e-4df2-b865-897238620cd0 --> | Is there an on-device model for repositories whose text must not leave the machine? | No on-device embedding provider. A repository whose text must remain on the machine stays disabled | Decided 8 October 2026 by the owner: no, Voyage API only. No local model or second embedding provider is in scope |
| MYC-D17 <!-- b88e3680-660b-404a-a03d-b743679acf57 --> | What happens to a text longer than the model takes? | Split the complete text into bounded embedding parts while retaining the logical chunk. Every part gets a vector; none of its text is cut off | Decided 8 October 2026 by the owner: every bit of data must be embedded without loss. No truncation; complete coverage across all parts, with each input within the model's limit |

## Named checks

Written by `scripts/name_checks.py` from the `proven` and `stated` Origin Links of the tests and a complete check report in which they passed. Each requirement keeps its kind in its Verified by cell and names here up to three of its passing checks: those of its own kind first, then those that rest on the fewest requirements. `mycel origins --repo mycel --path tests` lists every link. Do not edit this section by hand: run the script again.

| Requirement | Kind | Checks |
|---|---|---|
| `MYC-3.1` | store | `test_embedding_store.EmbeddingStoreAcceptanceTests.test_actual_sql_transaction_rolls_back_mid_batch_fault_and_durable_receipt_can_resume`, `test_embedding_store.EmbeddingStoreAcceptanceTests.test_invalid_whole_batch_and_corrupt_receipt_write_no_vectors`, `test_embedding_store.EmbeddingStoreAcceptanceTests.test_row_lock_defers_whole_response_and_deleted_versions_alone_are_discarded` and 6 more |
| `MYC-3.2` | unit | `test_embedding_plan.EmbeddingPlanTests.test_code_and_document_place_lines_repeat_without_changing_body`, `test_embedding_plan.EmbeddingPlanTests.test_document_preamble_and_empty_heading_can_be_planned_without_invented_context`, `test_embedding_plan.EmbeddingPlanTests.test_empty_body_has_one_place_only_part_and_impossible_context_fails` and 1 more |
| `MYC-3.3` | unit | `test_embedding_plan.EmbeddingPlanTests.test_query_is_exact_complete_and_refused_without_splitting_or_truncation` |
| `MYC-3.4` | store | `test_embedding_store.EmbeddingStoreAcceptanceTests.test_isolated_failure_does_not_block_pending_parts_and_explicit_retry_retains_success`, `test_embedding_store.EmbeddingStoreAcceptanceTests.test_recorded_plan_provenance_is_validated_and_incompatible_replanning_removes_old_vectors`, `test_embedding_store.EmbeddingStoreAcceptanceTests.test_busy_pass_durable_batch_is_not_coverage_and_next_session_publishes_without_resend` and 6 more |
| `MYC-3.5` | store | `test_embedding_store.EmbeddingStoreAcceptanceTests.test_exact_version_all_locations_saved_spans_vectors_and_metadata_move_coverage` |
| `MYC-3.6` | store | `test_embed.EmbedStoreTests.test_busy_pass_keeps_receipt_and_embed_lock_refuses_duplicate_sends`, `test_embed.EmbedStoreTests.test_public_named_repeated_cwd_organization_and_all_scopes_exclude_other_repositories`, `test_embed.EmbedStoreTests.test_unavailable_final_recount_and_later_local_fault_preserve_committed_prefix_and_other_results` |
| `MYC-3.7` | store | `test_embed.EmbedStoreTests.test_interruption_during_later_repository_capture_keeps_first_reply_and_exact_stopped_activity`, `test_embed.EmbedStoreTests.test_lost_connection_after_first_batch_keeps_progress_reply_and_committed_vector`, `test_embed.EmbedStoreTests.test_publication_audit_failure_rolls_back_vectors_preserving_paid_receipt_and_safe_progress` and 7 more |
| `MYC-3.8` | unit | `test_voyage.VoyageTests.test_retry_after_only_increases_wait_with_sixty_second_cap`, `test_voyage.VoyageTests.test_transient_retries_grow_and_keep_identical_saved_inputs`, `test_voyage.VoyageTests.test_attempt_limit_leaves_parts_pending_and_stopping_output_is_sanitized` and 1 more |
| `MYC-3.9` | unit | `test_voyage.VoyageTests.test_content_isolation_keeps_exact_saved_strings_and_embeds_good_neighbors` |
| `MYC-3.11` | store | `test_embed.EmbedStoreTests.test_dry_run_has_provisional_exact_selection_tokens_and_local_faults_with_no_mutation`, `test_embed.EmbedStoreTests.test_changed_settings_stage_paid_response_block_publication_and_dry_run_never_drains`, `test_embed.EmbedStoreTests.test_retry_dry_run_reports_saved_planning_failure_as_failed_and_retry_selection_separately` |
| `MYC-3.12` | store | `test_embed.EmbedStoreTests.test_content_failures_keep_successful_parts_and_only_explicit_retry_selects_failures`, `test_embed.EmbedStoreTests.test_dry_run_has_provisional_exact_selection_tokens_and_local_faults_with_no_mutation`, `test_embed.EmbedStoreTests.test_interrupted_batches_retain_commits_and_resume_only_missing_parts_with_finite_inventory` and 5 more |
| `MYC-3.13` | store | `test_embed.EmbedStoreTests.test_disable_during_credential_acquisition_prevents_the_first_provider_send`, `test_embed.EmbedStoreTests.test_public_named_repeated_cwd_organization_and_all_scopes_exclude_other_repositories`, `test_embed.EmbedStoreTests.test_settings_change_after_audit_rolls_back_vectors_and_preserves_original_receipt` and 1 more |
| `MYC-3.14` | unit | `test_voyage.VoyageTests.test_query_exact_input_and_dry_run_or_missing_credentials_make_no_service_call`, `test_voyage.VoyageTests.test_exact_request_and_lazy_fixed_credential_boundary_with_no_ambient_fallback` |
| `MYC-3.15` | store | `test_embedding_store.EmbeddingStoreAcceptanceTests.test_disabled_unknown_and_old_model_state_never_supply_current_coverage` |
| `MYC-3.16` | unit | `test_embedding_plan.EmbeddingPlanTests.test_code_and_document_place_lines_repeat_without_changing_body`, `test_embedding_plan.EmbeddingPlanTests.test_document_preamble_and_empty_heading_can_be_planned_without_invented_context`, `test_embedding_plan.EmbeddingPlanTests.test_golden_document_ranges_use_original_text_after_normalization` and 6 more |
| `MYC-3.17` | store | `test_embedding_store.EmbeddingStoreAcceptanceTests.test_actual_sql_transaction_rolls_back_mid_batch_fault_and_durable_receipt_can_resume`, `test_embedding_store.EmbeddingStoreAcceptanceTests.test_invalid_whole_batch_and_corrupt_receipt_write_no_vectors`, `test_embedding_store.EmbeddingStoreAcceptanceTests.test_isolated_failure_does_not_block_pending_parts_and_explicit_retry_retains_success` and 9 more |
| `MYC-3.18` | unit | `test_embedding_plan.EmbeddingPlanTests.test_batch_counts_remeasure_exact_saved_inputs_and_empty_batch_is_empty`, `test_embedding_plan.EmbeddingPlanTests.test_batches_sort_identity_and_end_before_either_cap_or_repository_changes`, `test_embedding_plan.EmbeddingPlanTests.test_counts_never_pad_or_truncate_and_planning_adds_only_the_provider_prompt` and 9 more |
| `MYC-3.19` | unit | `test_embedding_plan.EmbeddingPlanTests.test_catalog_is_immutable_validated_and_requires_supported_dimensions`, `test_embedding_plan.EmbeddingPlanTests.test_packaged_asset_matches_official_revision_digest_and_known_counts`, `test_embedding_plan.EmbeddingPlanTests.test_counts_never_pad_or_truncate_and_planning_adds_only_the_provider_prompt` and 5 more |
| `MYC-3.20` | unit | `test_embedding_plan.EmbeddingPlanTests.test_batch_counts_remeasure_exact_saved_inputs_and_empty_batch_is_empty`, `test_embedding_plan.EmbeddingPlanTests.test_batches_sort_identity_and_end_before_either_cap_or_repository_changes`, `test_embedding_plan.EmbeddingPlanTests.test_golden_document_ranges_use_original_text_after_normalization` and 6 more |
| `MYC-3.21` | unit | `test_voyage.VoyageTests.test_cancellation_during_response_read_shuts_down_active_socket`, `test_voyage.VoyageTests.test_dns_deadline_and_cancellation_close_connections_and_prevent_late_post`, `test_voyage.VoyageTests.test_fixed_https_endpoint_and_headers_use_no_process_proxy_or_endpoint_environment` and 16 more |
| `MYC-3.22` | unit | `test_voyage.VoyageTests.test_entire_bad_response_writes_nothing_for_duplicate_missing_indices_and_vectors`, `test_voyage.VoyageTests.test_invalid_response_after_success_retains_only_previously_committed_progress`, `test_voyage.VoyageTests.test_out_of_order_valid_vectors_are_restored_and_race_deleted_vectors_excluded` and 13 more |
