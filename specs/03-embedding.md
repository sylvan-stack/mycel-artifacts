---
role: authored
spec: MYC-3
status: draft
---
# Mycel · 03 Embedding

Embedding turns every [Chunk](../../arbol/GLOSSARY.md#chunk) into a vector, so that a search can find it by meaning. This specification fixes what text is embedded, which chunks are embedded and when, how failures are handled, and what the counts in a status report mean. It matters because in version 1 one failed request ended a whole pass, the counts did not match what a pass would do, and the rule that kept some repositories off the external service had gaps.

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: the embedding model and its provider, the text sent for a chunk, the pending rule, the embed operation and its scope, failures and retries, the counts, the key.

Not covered: how chunks come to exist and when a vector is cleared ([MYC-1](01-corpora-and-ingest.md)); how vectors are searched ([MYC-4](04-retrieval.md)); summaries of chunk clusters, which are not part of the first version ([MYC-D4](00-overview-and-legacy-map.md#decisions)).

## Behaviour

### The model and the provider

Observed in version 1: chunks were embedded by the Voyage service with the model `voyage-code-3`, 1024 dimensions, 64 texts per request, 60 seconds per request, one attempt per batch. Chunks were sent with the input type `document`, queries with `query`. Nothing limited the length of a text; the request carried no truncation setting, so an over-long text was left to the service's default.

A second profile, `local`, sent texts to a separate program on the same machine that held an on-device model with the same number of dimensions. That program was a service of Arbol 1. Vectors of both models were stored in one column and one index; only the repository name kept them apart.

Proposed: one provider and one model in the first version ([MYC-D14](#decisions), [MYC-D16](#decisions)). Every vector is stored with the name of the model that produced it, and a search compares a query only with vectors of the model the query was embedded with. A change of model makes every chunk pending again; no command is needed to say so.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#embed
mycel_deprecated_v1:mycel/knowledge/embedder.py#_profile_for
mycel_deprecated_v1:mycel/knowledge/local_embedder.py#embed
mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema
-->

### The text that is embedded

Observed in version 1, and kept: the chunk's own text is never changed, but the text sent for embedding starts with one line that says where the chunk is.

| Chunk | Text sent |
|---|---|
| A symbol of a code file | `<path> — <symbol> (<kind>)`, a line break, the chunk's text |
| A section of a document | `<path> › <heading path>`, a line break, the chunk's text |

The path and the name often carry meaning the body lacks: a file called `invoice-export.service.ts` says "invoice export" even when its code never does. The line comes first, so if a text is cut for length the place is never what is lost. A query is embedded as it was typed, with nothing added.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#_embed_text
mycel_deprecated_v1:mycel/knowledge/embedder.py#_query_vec
-->

### Which chunks are pending

Observed in version 1: a chunk was pending when it was present and had no vector. Ingest cleared the vector of a chunk whose content changed and kept the vector of a chunk that was only renamed. A pass took every pending chunk of every repository in one list, ordered by identifier. A chunk of a disabled repository was skipped. A chunk of a repository that had no settings row was treated as enabled and sent to the external service.

Proposed: the same rule, with the model added. A chunk is pending when it is present and has no vector of the current model. A chunk whose repository is disabled, unknown or removed is never pending.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#embed_pending
mycel_deprecated_v1:mycel/knowledge/store.py#ingest
mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code
-->

### The embed operation

Observed in version 1: `mycel embed` took no arguments and processed every pending chunk of every enabled repository. `mycel sync` did the same after its pass unless told not to. Each chunk's vector was stored as soon as its batch came back, so an interrupted pass kept what it had done. An error from the service ended the pass. Because the list was in a fixed order, a batch the service rejected would be the first batch of every later pass (inferred from the source, not seen happening).

Proposed:

- **Scope.** An embed names what it covers: one repository, several, or all enabled ones. Nothing embeds across all repositories as a side effect of another command.
- **Progress survives.** Vectors are stored batch by batch. Stopping an embed, or losing the connection, loses at most the batch in flight.
- **One bad text does not block the rest.** A request that fails for a reason that can pass (no network, a time limit, a rate limit, a server error) is tried again with growing pauses. A request the service rejects for its content is split until the texts at fault are found; those chunks are marked as failed with the reason, and the pass goes on. A failed chunk is not tried again until its content changes or the owner asks.
- **Length.** A text longer than the model takes is cut at the end before it is sent, and the chunk records that it was cut ([MYC-D17](#decisions)).
- **Dry run.** An embed can report what it would send, in chunks and in an estimate of tokens, without sending anything.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#embed_pending
mycel_deprecated_v1:mycel/cli.py#_cmd_embed
mycel_deprecated_v1:mycel/cli.py#_cmd_sync
-->

### Counts

Observed in version 1: the status report gave two numbers, embedded and pending, for the whole index, whatever repository was asked about. Pending included chunks of disabled repositories, which no pass would ever embed. Observed on 7 October 2026: after the repository that held 11,973 of 13,707 pending chunks was disabled, the report still said 13,707.

Proposed: counts are per repository. For each one the report gives the chunks that are present, embedded, pending and failed, and pending means exactly what the next embed of that repository would send.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#pending_count
mycel_deprecated_v1:mycel/knowledge/embedder.py#embedded_count
mycel_deprecated_v1:mycel/cli.py#_cmd_status
-->

### The key

Observed in version 1: the key of the embedding service was read from the macOS Keychain, from an item named for Arbol's embedder, on every request. There was no other source.

Proposed: Mycel reads the key from the place its settings name, by default a Keychain item of its own, or else a command of the owner's that prints it ([MYC-D15](#decisions)). The key is never an argument, never in the settings file and never in output.

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#_api_key
mycel_deprecated_v1:mycel/macos_keychain.py#get_password
-->

## Requirements

| ID | Mycel must… | Origin | Verified by |
|---|---|---|---|
| MYC-3.1 | embed every present chunk of an enabled repository with one named model, and store the model's name with the vector | Changed | store |
| MYC-3.2 | start the text sent for a chunk with one line naming its place: path, symbol and kind for code; path and heading path for a document. The chunk's stored text stays as it is in the file | Kept | unit |
| MYC-3.3 | embed a query as typed, with the input type the model defines for queries | Kept | unit |
| MYC-3.4 | treat a chunk as pending exactly when it is present, its repository is enabled, and it has no vector of the current model and no recorded failure for its current content | Changed | store |
| MYC-3.5 | clear a chunk's vector when its content changes and keep it when only its name or place changes | Kept | store |
| MYC-3.6 | embed only the repositories an invocation names, or all enabled ones when it says so. No other command embeds chunks of a repository it was not asked about | Changed | store |
| MYC-3.7 | store vectors batch by batch, so that an interrupted embed keeps what it finished | Kept | store |
| MYC-3.8 | try a request again, with growing pauses, when it failed for a reason that can pass, and give up on the pass only after the attempts its settings allow | Changed | unit |
| MYC-3.9 | find the texts at fault when the service rejects a batch for its content, record the failure and its reason on those chunks, and embed the rest of the batch | New | unit |
| MYC-3.10 | cut a text that is longer than the model takes at its end, never at its first line, and record on the chunk that it was cut | New | unit |
| MYC-3.11 | report, without sending anything, how many chunks and roughly how many tokens an embed would send | New | store |
| MYC-3.12 | report per repository the chunks present, embedded, pending and failed, where pending is what the next embed of that repository would send | Changed | store |
| MYC-3.13 | never send text of a disabled, unknown or removed repository to the embedding service | Changed | store |
| MYC-3.14 | read the key from the place its settings name and nowhere else, and never print it, pass it as an argument or write it to a file | Changed | unit |
| MYC-3.15 | make every chunk pending again when the model named in the settings changes, and never search vectors of one model with a query embedded by another | New | store |

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

```sh
mycel embed --repo core                  # the pending chunks of one repository
mycel embed --repo core --repo mycel     # of several
mycel embed --all                        # of every enabled repository
mycel embed --repo core --dry-run        # what would be sent; nothing is sent
mycel embed --repo core --retry-failed   # also the chunks marked as failed
```

`mycel embed` without `--repo` or `--all` embeds the repository of the current directory, and is refused when the directory belongs to none.

```ts
interface EmbedResult {
  model: string;                       // the model that produced the vectors
  repositories: Record<string, {
    sent: number;                      // chunks embedded in this invocation
    failed: number;                    // chunks the service rejected, now marked as failed
    cut: number;                       // chunks whose text was cut for length
    pending: number;                   // what is still pending afterwards
  }>;
  stopped?: "interrupted" | "gave_up"; // absent when the embed finished
  estimate?: { chunks: number; tokens: number };   // only with --dry-run
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

<!-- sources:
mycel_deprecated_v1:mycel/knowledge/embedder.py#embed
mycel_deprecated_v1:mycel/knowledge/embedder.py#embed_pending
mycel_deprecated_v1:mycel/knowledge/embedder.py#pending_count
mycel_deprecated_v1:mycel/knowledge/embedder.py#_query_vec
mycel_deprecated_v1:mycel/knowledge/raptor.py#build_tree
mycel_deprecated_v1:mycel/knowledge/local_embedder.py#is_available
-->

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D14 | Which model and provider embed the chunks? | Voyage `voyage-code-3` with 1024 dimensions, as in version 1. The model is a setting, so another can be named later at the cost of embedding everything again | Open |
| MYC-D15 | Where does the key of the embedding service come from? | As the Drivers read theirs (DRV-D4): a Keychain item of Mycel's own, read with the system's `security` command, unless the settings name a command that prints the key | Open |
| MYC-D16 | Is there an on-device model for repositories whose text must not leave the machine? | Not in the first version. Version 1's needed a resident service of Arbol 1, and no repository uses it today. A repository that must stay on the machine is left disabled until a second provider is specified | Open |
| MYC-D17 | What happens to a text longer than the model takes? | Mycel cuts it at the end before sending and records that on the chunk. The other choice is to split such a chunk at ingest (MYC-1), which changes what a chunk is | Open |
