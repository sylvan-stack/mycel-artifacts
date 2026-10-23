---
role: authored
spec: MYC-17
status: draft
---
# Mycel · 17 Justification

Every chunk of code and every document chunk that is not itself authored should be traceable to what ordered it: a requirement, a decision, a document section or, when nothing better exists, a code chunk. This specification makes requirements and decisions entities of their own in the Index Store, addresses them by the glossary's Entity URI, keeps the discussion of a decision with it, and defines the Origin Link from a chunk to its Origin. It is the chapter the owner asked for on 19 October 2026 ([MYC-D63](#decisions)); the commands `mycel justify`, `mycel origins`, `mycel recovery` and `mycel audit` are specified here by the Beats that build them (SYL-260, SYL-262, SYL-263), and the agent procedure lives in a guide that this chapter points to, where running `origins` is useful, not required.

It follows the conventions of the [specifications chapter](README.md#conventions). It is written with the `From v1` column and with a UUID in every row, as [MYC-D49](#decisions) and [MYC-D45](#decisions) require; the seventeen earlier chapters are brought to the same form by the normalization run of SYL-261.

## Scope

Covered: the entity model of requirements and decisions, the UUID written in a table row, the Entity URI in Mycel, the Discussion column of a decision and how its chats are read, the Origin Link with its fields and bands. Also covered: stating an Origin Link (`justify`) and reporting Origin Coverage (`origins`). Recovery is covered here; audit remains the following Beat, SYL-263.

Specified elsewhere: how a document is split and how chunks keep their identity ([MYC-1](01-corpora-and-ingest.md)); Source Refs, edges and staleness ([MYC-2](02-provenance-and-freshness.md)); relations, confirmation and verification ([MYC-7](07-drifts-and-verification.md)); the reply of `mycel read` ([MYC-11](11-reading-a-chunk.md)); portable addresses and the one resolver ([MYC-16](16-source-addresses-and-evidence.md)); the settings file ([MYC-5](05-settings.md)); the store's format ([MYC-6](06-index-store.md)). Arbol's side of Entity URIs is Arbol's: Mycel reads and writes the string form the glossary gives and holds no Arbol entity table.

## Behaviour

### Requirements and decisions are entities

Before this chapter a requirement was one line of a table inside a section chunk. It had no identity of its own, so nothing could point at it, and an edit to a neighbouring row changed the hash of every requirement of the section. The owner decided on 19 October 2026 that requirements and decisions are entities, not locators ([MYC-D45](#decisions)).

A row of a Requirements or Decisions table is recognised when its first cell is exactly a human id, `<PREFIX>-<n>.<m>` for a requirement such as `MYC-2.13` or `<PREFIX>-D<n>` for a decision such as `MYC-D45`, followed by nothing but an HTML comment that holds the row's UUID:

```markdown
| MYC-2.13 <!-- 9b6984cc-db34-4a84-b948-0eaefbea916a --> | mark a chunk stale when a source of it has a content hash other than the one its edge stores … | Changed | store |
```

Readers and Linear copies do not see the comment; Mycel reads it. A first cell with more text than the id, such as `MYC-D1 · What language is Mycel 2 written in?`, is prose and not a row of an entity.

Such a row is a chunk of its own in the Index Store, beside the section chunk that holds it. Its identifier is the UUID of the comment, its kind is `req` or `dec`, its name is the human id, and its text is the exact row. Like any chunk it has versions, one for each text it has had, and locations, one per place its text is found ([MYC-1](01-corpora-and-ingest.md#branches-and-stashes)): a file, a row position, a branch, a clone. There may be several locations or none. The section keeps its own chunk with its complete text and hashes, so that the exact-byte coverage of [MYC-16](16-source-addresses-and-evidence.md#comparison-hashes-and-exact-versions) still holds; an edit to the row changes the section's hash as before, and in addition gives the entity a new version of its own.

The row holds what Mycel reads from its cells:

| Field | A requirement | A decision |
|---|---|---|
| `kind` | `req` | `dec` |
| `id`, the display name | the human id, never edited | the human id, never edited |
| `title` | the second cell, "Mycel must…" | the Question cell |
| `text`, and its hashes | the exact row | the exact row |
| `status` | the chapter's status from its frontmatter, or `withdrawn` when the row says so | `decided` when the Outcome begins with `Decided`, else `open` |
| `decidedBy`, `decidedAt` | — | from `Decided <date> by <who>` in the Outcome |
| `verifiedBy` | the Verified by cell: `unit`, `store`, `eval` or `live` | — |
| `fromV1` | the From v1 cell: `Kept`, `Changed`, `New` or `Dropped` | — |
| `discussion` | — | the chat Entity URIs of the Discussion cell |

Identity follows the UUID and nothing else. An edit to a neighbouring row leaves the entity, its version and its locations as they were. An edit to the row's own text makes a new version of the same entity. Moving the row to another section, another file or another chapter changes a location, not the entity. A row is never deleted: when its last version leaves every location the versions are collected like any chunk's, but the entity row stays, so a withdrawn id stays reserved and every edge that references the UUID keeps its end.

A recognised row without a UUID is a reported fault of its file, as a malformed Source Ref is ([MYC-2](02-provenance-and-freshness.md#source-refs)): the pass goes on, the section is split as before, and no entity is made of the row. Two rows with one UUID are a fault too, and neither becomes an entity, so that nothing silently wins. The normalization run of SYL-261 adds a UUID to every existing row once; a new row gets its UUID from its author.

### The Entity URI in Mycel

Mycel uses the glossary's [Entity URI](../../arbol/GLOSSARY.md#entity-uri) as it stands ([MYC-D46](#decisions)): `[req:<uuid>:<title>]`, `[dec:<uuid>:<title>]` and `[cht:<uuid>:<title>]`, with the title Base64-encoded as the glossary says, and the four-part form `[<repo>:req:<uuid>:<title>]` with the repository's code. The repo code is optional; when Mycel writes a URI it uses the repository's name, and no setting chooses it. Mycel resolves a URI by the UUID alone, because UUIDs are unique across kinds and repositories, and uses the kind tag only as a check: a URI whose tag does not match the entity's kind is refused as `invalid_input`. The title is a display snapshot; two URIs with different titles and one UUID name the same entity.

The one resolver of [MYC-16](16-source-addresses-and-evidence.md#root-aliases-and-one-resolver) accepts an Entity URI wherever it accepts an address, and its typed selection gains `req` and `dec`. An entity is also reached by its full address, `mycel:@artifact/specs/02-provenance-and-freshness.md#MYC-2.13`, and by its human id within its file, since the human id is the chunk's name. A reply writes an Origin as an Entity URI when it has a UUID and as a Mycel address otherwise.

### The discussion of a decision

A decision was taken in a discussion, and the discussion lives in an Arbol chat. The Discussion column of a Decisions table holds chat Entity URIs only ([MYC-D47](#decisions)). Mycel retains them with the decision and makes nothing else of them: a chat is not a source, derives no edge, and never makes the decision stale. A decision that rests on a research note cites it as an ordinary Source Ref and goes stale when the note changes. Editing a decision row makes everything that rests on it stale, as editing a requirement does.

`mycel read` of a decision shows the content of the chats its Discussion cell names ([MYC-D48](#decisions)): Mycel reads them from the Arbol database as data, through a settings table of its own, `[discussions]` in [MYC-5](05-settings.md#the-keys), with the database's address and the Keychain item for its password. MYC-D5 as amended on 19 October 2026 allows this read: it is no integration and no dependency on Arbol code, and Mycel writes nothing there. When the database cannot be reached, or the settings name none, the read still succeeds and the discussion says `available: false` with the reason.

### The Origin Link

An Origin is the chunk at the source end of an Origin Link: what ordered the chunk at the other end. It is of any kind: a requirement, a decision, a document section, or a code chunk when nothing better exists, as in an undocumented open-source repository. The word *origin* is used for nothing else in Mycel ([MYC-D49](#decisions)); the former `Origin` column of the requirement tables is named `From v1`.

An Origin Link is a directed link from a chunk to its Origin: a claim, never a proof. It lives in the Index Store, never in the code, and every link references the Origin's UUID when it has one. A chunk has a list of Origin Links, each with:

| Field | Values |
|---|---|
| `method` | `stated` by a person, `proven` by a check, `inferred` by a model, `recovered` from history |
| `confidence_score` | a number from 0 to 1 |
| `confidence` | the band the score falls in: `asserted` above 0.9, `proven` 0.8 to 0.9, `inferred` 0.5 to 0.8, `candidate` below 0.5. The thresholds are example values, set in one place |
| who and when | who made the link and when |
| `review` | the review of the link, when one was made |

The score rises by a review or a passing check and falls by a failed conformance check. Stating a link (`mycel justify`), listing Origin Coverage (`mycel origins`), inferring candidates for a chunk without Origin (`mycel recovery`) and disputing links (`mycel audit`) are specified in the sections the Beats SYL-260, SYL-262 and SYL-263 add here. Linear is never an Origin; a task, a Beat or a Linear issue never justifies code.

### Stating an Origin Link

`mycel justify <chunk> <origin>` resolves one current on-disk chunk and one Origin, by Entity URI or ordinary address, through the one resolver. The Origin must resolve; a missing, ambiguous, disabled or generated selection is refused. A requirement or decision is written as its Entity URI; another chunk is written as its canonical address. A file or class-family Origin is retained as its complete selection, as `derive` permits.

In one transaction the command asserts the dependency with exact pins, records the Origin Link and its author and time, and records a verification of the dependant's exact current version. The normal derive and confirm guards apply: changed-since-ingest dependant or source bytes, invalid selections and a final guard failure leave all feature writes rolled back. `refs`, `stale` and `verifications` read the ordinary dependency and verification result. An Origin Link is still a claim, not a conformance proof.

The single-pair command records `method: stated`, `confidenceScore: 1` and `confidence: asserted`, naming the identity from `--by` or the current operating-system user. These are implementation choices for a direct assertion, not adopted thresholds for inferred links. The example band boundaries above remain examples; recovery and audit own any configurable scoring policy. `review` is absent until a review exists. Repeated statements update the statement's metadata without inventing a review. The owner delegated MYC-D51 on 21 October 2026. Chosen: `mycel justify --file <pairs.jsonl>`, with one JSON object per nonempty line containing exactly `chunk` and `origin` text fields. All pairs are validated before writes, and the batch shares one transaction and final input guards: failure of any pair rolls back the whole batch. Duplicate exact pairs are refused. The reply is `{ justifications: JustifyReply[] }` in input order. Pairs naming one dependant share one final verification of its complete policy after all assertions have been stated. A class/file family remains an Origin selection; the dependant in each pair remains one chunk.

### Reporting Origin Coverage

`mycel origins [<chunk>]` lists current chunks and their Origin Links. `--missing` retains chunks with no links; repeated `--path` filters are component-bounded paths under the selected root. `--changes` compares only the calling clone's disk versions against the configured read-only clone's retained local `main`, using the Index Store query of MYC-1.39. `--unresting` additionally lists requirements and decisions with no dependant. Explicit repository scope and current-folder scope follow MYC-1.

The default performs one scoped ingest before reading the report, with no model call. `--no-fresh` reads only the stored snapshot. The report query itself changes no row. Listings, including nonempty missing-link lists and empty scopes, return status 0. Operational and input failures use the ordinary error statuses. This command is on demand; it installs no gate, hook or commit rule.

`mycel origins --needs-nothing <requirement> --reason <text>` records a nonempty explanation on one requirement. It suppresses that requirement from the unresting list; it invents no dependency, verification or proof. `--clear-needs-nothing <requirement>` withdraws the mark. A constraint such as a forbidden source language needs its conformance check, not a fictional Origin Link.

### Recovering Origin Links

`mycel recovery [<chunk>] [--repo <name>] [--path <path>] [--k <pairs>] [--dry-run]` selects current file-backed chunks without an Origin Link. A chunk reference chooses its repository; repository or component-bounded path scope uses the calling clone. It reads the indexed snapshot and checks complete current files; it never ingests, embeds, fetches, checks out or reads a remote. The caller ingests first when the snapshot is out of date.

Candidates are the document sections joined by direct Source Refs in either direction or naming the complete symbol in their text (MYC-D39), test chunks that call its symbol, the local introducing commit found by symbol pickaxe, the upstream issue/pull request named in that commit, and the nearest requirement/decision chunks by existing complete current-model vectors. Each candidate carries its canonical address or Entity URI and all its source categories. Duplicates are judged once. Missing chunk vectors disable only the embedding source, with an explicit reason; no query embedding is bought. The history arm uses only the selected clone's local Git. A raw commit is retained as exact judgement context. To be an Origin it needs a file-backed indexed snapshot naming its full hash; an upstream issue/PR needs an indexed time-pinned snapshot naming its exact URL (or a same-repository issue URL for a commit's bare #number). Missing snapshots are reported as unavailable; recovery does not invent an address or silently turn a commit into a code chunk. Source Refs rule 5 governs external snapshots before ingest. These matching rules identify proposals, not authority.

`--dry-run` lists every source and its unavailable reason, each candidate and its provenance, eligibility and exact byte counts, with no model credential, model call or state write. Non-dry execution uses the second pair question of MYC-14, `mycel-origin-v1`: does this candidate `governs`, `related` or `unrelated` the chunk? It retains complete exact chunk/candidate text, direct governor/ancestor context and local history in a distinct immutable payload and bounded evidence history. Every input and the configured model/reviewer identity is checked before each call and application. MYC-14's quiet period, confidence floor, byte/candidate/attempt/deadline limits and isolated reviewer apply. Recovery executes at most one pair at a time, within `at_once`. No missing or obsolete evidence authorizes an effect.

A complete `governs` or `related` result creates one Origin Link in a guarded Origin-claim transaction, with `inferred`, or `recovered` for commit/issue provenance, and the model's confidence score. An `unrelated` result creates none. The score is retained exactly as the validated result's numeric projection; initial inference and review never promote a link above `inferred`. The scoring policy is in one implementation place: scores at least 0.5 have band `inferred`, lower ones `candidate`. A model judgement never records a verification or clears a stale mark. Its dependency row has kind `origin`, outside the declared/asserted/generated source-policy graph; its exact candidate edge and retained request still support Origin Coverage and audit. This permits a describing section's reverse Source Ref without creating circular authority. A later explicit `justify` supersedes that proposal with the ordinary asserted policy and verification. Existing stated/proven links are never overwritten. Partial replies retain completed applications and pending or failed pairs.

`mycel recovery --review` selects existing inferred/recovered links in the same scopes and invokes the configured smarter reviewer on the same complete Origin question. Its strict reply adds `confidenceScore` in [0,1]. A `governs`/`related` review replaces the score, recomputes the capped band and records who, when and the outcome; an `unrelated` review withdraws only the model's proposal. Jev is not called in this mode. `mycel origins` shows the resulting score, band and review. Ordinary recovery still routes uncertain Jev results to this reviewer. Exact question/model/policy/command identities isolate these results from drift classification and from other inputs.

For a third-party repository, the owner's corpus may hold their own requirements and indexed snapshots of upstream documents, commits and issues. Recovery judges those exact snapshots against upstream code by the same rules. Linear text, tasks and Beats are never Origins; any snapshot containing a Linear URL or a Linear-task heading is excluded before judgement. An upstream issue may be an Origin. No owner corpus or upstream state is written by candidate gathering.

## Requirements

| ID | Mycel must… | From v1 | Verified by |
|---|---|---|---|
| MYC-17.1 <!-- 3b9f4d6a-7c2e-4f8b-9a1d-5e6f7a8b9c0d --> | keep every recognised requirement and decision row of a document as a chunk of its own in the Index Store, of kind `req` or `dec`, whose identifier is the UUID of the HTML comment in the row's first cell, beside the section chunk that holds the row, with versions and locations like any chunk | New | store |
| MYC-17.2 <!-- 8e1c2a3f-4b5d-4c6e-8f7a-9b0c1d2e3f4a --> | read from a recognised row its human id as its name and display name, its title, its exact text and hashes, its status, and its metadata: who decided and when, the discussion chats, the Verified by kind and the From v1 value | New | unit |
| MYC-17.3 <!-- 2f7a8b9c-0d1e-4f2a-b3c4-d5e6f7a8b9c0 --> | report a recognised row without a UUID, and two rows with one UUID, as faults of their file, make no entity of them, and split the section as before | New | unit |
| MYC-17.4 <!-- 6c5d4e3f-2a1b-4c0d-9e8f-7a6b5c4d3e2f --> | keep an entity's identity through an edit to a neighbouring row, through an edit to its own text and through a move of its row to another section, file or chapter; collect its versions like any chunk's but never delete the entity row, so a withdrawn id stays reserved | New | store |
| MYC-17.5 <!-- a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d --> | accept the glossary's Entity URI, with or without the repo code, wherever an address is accepted; resolve it by the UUID alone, refuse a kind tag that does not match the entity with `invalid_input`, and write an Origin as an Entity URI when it has a UUID and as a Mycel address otherwise | New | unit |
| MYC-17.6 <!-- d4c3b2a1-f6e5-4d7c-8b9a-0f1e2d3c4b5a --> | retain the chat Entity URIs of a decision's Discussion column with the decision, derive no edge and no stale mark from a chat, and mark what rests on a decision stale when its row is edited | New | store |
| MYC-17.7 <!-- 5e6f7a8b-9c0d-4e1f-a2b3-c4d5e6f7a8b9 --> | show with the read of a decision the content of the chats its Discussion column names, read as data from the Arbol database that the `[discussions]` settings name, writing nothing there; and succeed with `available: false` and the reason when the settings name none or it cannot be reached | New | store |
| MYC-17.8 <!-- 9c0d1e2f-3a4b-4c5d-8e6f-7a8b9c0d1e2f --> | keep Origin Links in the Index Store and never in a file, each with its method, its confidence score and band, who made it and when, and its review, referencing the Origin's UUID when it has one | New | store |
| MYC-17.9 <!-- 215362e4-200d-4d82-8652-f567363ef0cb --> | state an Origin Link and record a verification in one guarded transaction, resolving one current dependant and its complete Origin by URI or address, and return JustifyReply with the exact chunk version, canonical Origin, link and verification | New | store |
| MYC-17.10 <!-- d7da25ae-d86b-4723-bbef-d5f5d8510b80 --> | refuse an unresolved, invalid or changed-since-ingest justification without any partial link, pin, verification or feature-activity write, and expose successful results through refs, stale and verifications | New | store |
| MYC-17.11 <!-- 8e4caad4-8a09-4238-90d0-6c09620e2040 --> | report Origin Links and chunks without them by current repository, path or calling-clone changes, with one optional scoped ingest and no model call, a read-only report query and status zero regardless of what the list contains | New | store |
| MYC-17.12 <!-- 73929c40-7721-4723-a5d7-9c6189b42ecc --> | report requirements and decisions that have no dependant and let a requirement be marked needs nothing with a nonempty reason or have that mark withdrawn, without creating a link or a proof | New | store |
| MYC-17.13 <!-- 53d91ed8-2191-4ac2-9773-87b8d19dd695 --> | gather and name local document, test-call, introducing-commit/snapshotted-issue and existing-vector requirement/decision candidates for current unlinked chunks by chunk, path or repository; expose dry-run provenance, unavailable sources, exact byte counts and eligibility without writes or model calls | New | store |
| MYC-17.14 <!-- 6bdc7e7c-9f32-4311-911f-f953b4d31887 --> | write one inferred or recovered Origin Link per complete governs/related judgement with its score and a band capped at inferred, no verification, guarded exact inputs and retained evidence; allow isolated smarter review to raise/lower the score and band or withdraw an unrelated model proposal, exposing results through origins | New | store |
| MYC-17.15 <!-- 44400ae0-a0c9-4ff0-a501-85e3325f84db --> | recover third-party code against the owner requirements and indexed time-pinned upstream snapshots, exclude Linear/task text before judgement, and perform no remote read or source-file write | New | store |

Audit requirements are added by its owning Beat.

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

```sh
mycel read '[req:9b6984cc-db34-4a84-b948-0eaefbea916a:bWFyayBhIGNodW5rIHN0YWxl]'   # by Entity URI
mycel read '[mycel:dec:0f2c1b4e-8a9d-4c3e-9b7a-1d2e3f4a5b6c:V2hpY2ggbGFuZ3VhZ2U]' # with the repo code
mycel read 'mycel:@artifact/specs/02-provenance-and-freshness.md#MYC-2.13'          # by full address
mycel read 'mycel:specs/02-provenance-and-freshness.md#MYC-2.13'                    # by human id within the file
```

```ts
// A chunk of kind "req" or "dec" has, in a search result and in ReadReply of MYC-11:
interface EntityFields {
  entity: {
    kind: "req" | "dec";
    uuid: string;                        // the UUID of the row's comment, also the chunk's id
    id: string;                          // the human id, the display name: "MYC-2.13"
    uri: string;                         // the Entity URI with the repository's code
    title: string;
    status: string;                      // a requirement: its chapter's status or "withdrawn"; a decision: "decided" | "open"
    decidedBy?: string;
    decidedAt?: string;
    verifiedBy?: "unit" | "store" | "eval" | "live";
    fromV1?: "Kept" | "Changed" | "New" | "Dropped";
    discussion?: Discussion[];           // a decision: one entry per chat Entity URI of its Discussion cell
  };
}

interface Discussion {
  uri: string;                           // the chat Entity URI as written
  available: boolean;
  reason?: string;                       // when not available: no settings, unreachable, no such chat
  title?: string;
  messages?: Array<{ role: "user" | "assistant"; text: string }>;   // in the chat's order, replaced Exchanges left out
}

interface OriginLink {
  chunk: string;                         // the dependant: an Entity URI when it has a UUID, else a Mycel address
  origin: string;                        // the Origin: the same rule
  method: "stated" | "proven" | "inferred" | "recovered";
  confidenceScore: number;               // 0 to 1
  confidence: "asserted" | "proven" | "inferred" | "candidate";
  who: string;
  when: string;
  review?: { who: string; when: string; outcome: string };
}
```

```ts
interface JustifyReply {
  chunk: string;
  chunkVersion: number;
  origin: string;
  link: OriginLink;
  verification: object;                 // the ordinary recorded verification of MYC-7
}
interface OriginsReply {
  scope: { repository: string; location: string; paths: string[]; changes: boolean };
  chunks: Array<{ chunk: string; links: OriginLink[] }>;
  unresting?: Array<{ origin: string; reason?: string }>;
}
```

### RecoveryReply

`recovery` returns `{ repository, dryRun, review, selected, completed, jevCalls, reviewCalls, errors, incomplete, status, maxCalls, chunks, pairs }`. Each chunk lists its history, embedding availability and candidates. Each candidate names `chunk`, `origin`, `sources`, `status`, `eligibleAt`, `inputHash`, `questionVersion` and complete request byte counts, or its unresolved reason. Selected `pairs` additionally retain attempts, stage results, the final judgement/score and applied `link` (null for unrelated). `status` is 0 for a complete selection including ordinary pending debounce/reviewer configuration, 1 for an operational fault and 2 for an interrupted command. The reply always retains completed pairs.

## Known problems

This is a new contract. Version 1 had no entity of its own for a requirement or a decision; its `@proves` decorators and the registry `requirements.json` named requirements by human id alone, so a row could not be pointed at from the index and nothing noticed an edit to one row apart from its neighbours. The registry still gates `make check` until SYL-261 retires it after a one-time import.

A chunk of kind `req` or `dec` is embedded like any other chunk when the owner runs `mycel embed`; nothing in this chapter embeds it.

## Decisions

The owner answered the fifteen decisions of the Traceability Arc's first draft on 19 October 2026; this chapter records the six that concern the entities, the URIs, the discussion and the words. The others are recorded by the Beats that build their subject. Where this Beat needed a choice no decision covers, it chose a default and recorded it in its own file (`~/Artifacts/sagas/mycel-2-implementation/traceability/SYL-259.md`): entity rows are chunks whose identifier is the UUID, the section keeps its complete chunk, a row is recognised by its first cell alone, and the discussion database is read through `[discussions]`.

| ID | Question | Proposed default | Outcome | Discussion |
|---|---|---|---|---|
| MYC-D45 <!-- 0d9b7e4c-5a3f-4b2e-8c1d-6e7f8a9b0c1d --> | What is a requirement or decision in the Index Store, and how is it named? | A row of its own keyed by a UUID in an HTML comment after the human id; the alternative was a visible ID column | Decided 19 October 2026 by the owner: requirements and decisions are entities, not locators. A `req` or `dec` is a row of its own in the Index Store, keyed by a UUID that is written in the artifact in an HTML comment after the human id in the first cell of the table row, invisible to readers and Linear copies, read by Mycel. The human id such as `MYC-2.13` is the display name and is itself never edited. The row holds the kind, the human id, the title, the text and its hash, the status, and metadata: who decided and when, the discussion chats, the Verified-by kind, the From v1 value. Its locations are attributes of the row, one per place the text is found (file, row position, branch, clone); there may be several or none; a row is never deleted and a withdrawn id stays reserved. Every edge references the UUID, never a path. Moving a row between chapters changes a location, not the entity. A row without a UUID is a reported fault, and the normalization run adds UUIDs to every existing row once. The alternative of a visible ID column was rejected | |
| MYC-D46 <!-- 7a1e3c5b-9d2f-4e4a-b6c8-0d1e2f3a4b5c --> | How is a requirement, a decision or a chat addressed? | The glossary's Entity URI, resolved by UUID | Decided 19 October 2026 by the owner: Mycel uses the glossary's Entity URI as it stands: `[req:<uuid>:<title>]`, `[dec:<uuid>:<title>]`, `[cht:<uuid>:<title>]`, the title Base64-encoded as the glossary says. The repo code is optional and inferred from the repository name when a URI is written; no setting for it. Mycel resolves a URI by the UUID alone, since ids are unique across all kinds and repositories, and uses the kind tag only as a check. The resolver accepts an Entity URI wherever it accepts an address. `dec` is added as an entity kind in the glossary's table | |
| MYC-D47 <!-- c2d4e6f8-1a3b-4c5d-9e7f-8a9b0c1d2e3f --> | What is in the Discussion column of a decision, and what does Mycel make of it? | Chat Entity URIs only; a chat never makes the decision stale | Decided 19 October 2026 by the owner: the Discussion column holds chat Entity URIs only. A decision that rests on a research note cites it as an ordinary Source Ref and goes stale when the note changes. Editing a decision row makes everything based on it stale, as for a requirement. A discussion chat never makes the decision stale | |
| MYC-D48 <!-- e8f0a2b4-c6d8-4e0f-a1b3-c5d7e9f1a3b5 --> | How does Mycel read the content of a chat named in a Discussion cell? | By its Entity URI from the Arbol database, through a settings table of Mycel's own | Decided 19 October 2026 by the owner: by its Entity URI from the Arbol database, through a settings table of Mycel's own with the address and the Keychain item for the password. MYC-D5 was amended on 19 October 2026 (commit `2101eb5` in `~/Artifacts/mycel`): Mycel may read Arbol-owned databases as data. Unavailable with a reason when not reachable, the read still succeeds, Mycel writes nothing there. The form `chat:<root>/<chat>` of the first draft is dropped | |
| MYC-D49 <!-- 4b6d8f0a-2c4e-4a6b-8d0f-2e4a6c8e0a2c --> | Which words name the things of this Arc? | Requirement, Decision, Origin, Origin Link, Origin Coverage, Index Store; the column `Origin` renamed `From v1` | Decided 19 October 2026 by the owner. Terms, all added to `~/Artifacts/arbol/GLOSSARY.md`: **Requirement**; **Decision**; **Origin**, the one-word term for a chunk at the source end of an Origin Link, of any kind: a requirement, a decision, a document section, or a code chunk when nothing better exists, as in an undocumented open-source repository; **Origin Link**, the directed link from a chunk to its Origin, a claim and never a proof, with the fields `method` (`stated` by a person, `proven` by a check, `inferred` by a model, `recovered` from history), `confidence_score` from 0 to 1, `confidence` as the band the score falls in (`asserted` above 0.9, `proven` 0.8 to 0.9, `inferred` 0.5 to 0.8, `candidate` below 0.5; the thresholds are example values set in one place), who and when, and `review`; a chunk has a list of Origin Links; the score rises by a review or a passing check and falls by a failed conformance check; **Origin Coverage**, what the command `origins` reports; **Index Store**, Mycel's own PostgreSQL database with ParadeDB at the address in its settings, holding chunks, versions, vectors, edges, marks and the record of work, a different database from Arbol's. The word *origin* is used for nothing else: the requirement tables' column `Origin` with Kept, Changed, New, Dropped is renamed `From v1` (MYC-17 is written with `From v1`; the seventeen existing chapters are renamed by the normalization run of SYL-261). Rejected names: Entity Origin, Presumed Origin, Evidence (collides with MYC-16), Locator. Nodes of the graph are Chunks; no new entity type for code; a target is written as an Entity URI when it has a UUID and as a Mycel address otherwise | |
| MYC-D63 <!-- 1f3d5b7a-9c0e-4f2a-8b4c-6d8e0f2a4b6c --> | Where is justification specified? | A new chapter MYC-17, Justification, and a guide with the agent procedure | Decided 19 October 2026 by the owner: a new chapter MYC-17, Justification, specifies the entities, Origin Links, `justify`, `origins`, recovery and audit as Mycel behaviour, and points to a guide with the agent procedure for new and existing code, where running `origins` is useful, not required. Its requirements are `MYC-17.n`; the Status table lists it as `draft` until the owner accepts it | |
| MYC-D50 <!-- 29b9be1c-6564-4c11-9fa4-0eca516894d0 --> | What does justify compose? | One assertion and one verification | Decided 19 October 2026 by the owner: justify states the Origin Link and verification together under derive and confirm guards, records its method, score, band, who and when, writes an Origin as URI when it has a UUID and as an address otherwise, and refuses changed-since-ingest inputs without writing | |
| MYC-D51 <!-- 22700946-811b-4421-b514-e0392f55582b --> | What is the bulk form of justify? | JSON-lines file of explicit pairs | Decided 21 October 2026 by the owner: "you decide". Chosen: a JSON-lines file of explicit chunk and origin pairs, suitable for recovery output and the one-time decorator import; validate every pair before writing and commit the batch atomically. Selection expansion is not a second bulk syntax | |
| MYC-D52 <!-- ca869d23-64bc-4ad7-9df0-aa9b59395bd5 --> | What does origins report and enforce? | On-demand Origin Coverage | Decided 19 October 2026 by the owner: origins lists links and missing links by chunk, path, repository or branch changes, plus requirements and decisions nothing rests on, with reasoned needs-nothing marks. One scoped ingest and one query, never a model call. No release mode, gate, hook or commit rule; constraint rules need tests | |
| MYC-D53 <!-- 75bebcd2-fcfa-4fb6-b2f6-d389577b00e1 --> | What are changes on this branch? | A query of retained versions | Decided 19 October 2026 by the owner: versions on the calling clone disk absent from main in the read-only clone, found in the Index Store without Git. The former git-status proposal is dropped | |
| MYC-D57 <!-- 85cc8594-a137-4529-89b9-d95ae753cd60 --> | How does a chunk without Origin get one? | Recovery is a guarded Mycel command | Decided 19 October 2026 by the owner: recovery is Mycel's command. For a chunk without Origin, candidates come from the document sections whose Source Refs or text name the symbol (MYC-D39), the tests that call it, the commit that introduced it and the issue or pull request its message names, snapshotted into the corpus by Source Refs rule 5, and the requirement and decision chunks nearest by embedding; a model judges each candidate as `governs`, `related` or `unrelated` with a confidence, which is MYC-14's pair classification asked a different question; recovery writes Origin Links with `method: inferred` or `recovered` and the score. The smarter-model review raises or lowers scores. The agent-proposed origins of the first draft are replaced by this | |
| MYC-D61 <!-- 703f56f2-57f3-4a5c-8e3f-6a57e59510ff --> | What are the Origins of a third-party repository's code? | Owner requirements and upstream snapshots | Decided 19 October 2026 by the owner: for a third-party repository the owner's corpus holds their own requirements and snapshots of the upstream's documents and issues; upstream code is recovered against those; Linear is never an Origin; an upstream issue may be one | |
