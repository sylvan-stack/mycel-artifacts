---
role: authored
spec: MYC-16
status: accepted
---
# Mycel · 16 Source addresses and retained evidence

A Source Ref must select the same source on another machine, and a changed source must be compared with the text the dependant actually answered to. This specification completes the root-aware addresses introduced by MYC-D7 and the retained evidence needed by Drift detection. It keeps evidence owned by a surviving dependant without keeping a deleted source in the searchable index.

It follows the conventions of the [specifications chapter](README.md#conventions). The concrete grammar, evidence shape and retention below are agent-selected design defaults on 8 October 2026 under the owner's instruction to finish the specifications. They do not amend MYC-D8 or MYC-D12.

## Scope

Covered: portable natural addresses, legacy-address compatibility, root aliases and ambiguity, shared resolution for reads and mutations, comparison hashes and exact snapshot hashes, immutable baseline manifests, exact classifier-input evidence, deletion, rebuilds and evidence retention.

Specified elsewhere: scanning and stable chunk identities ([MYC-1](01-corpora-and-ingest.md)); provenance and freshness ([MYC-2](02-provenance-and-freshness.md)); relations, verification and generated edges ([MYC-7](07-drifts-and-verification.md)); Drift decisions and paid invocation ([MYC-14](14-drift-detection.md)); transactions and locks ([MYC-6](06-index-store.md)); activity retention ([MYC-12](12-record-of-work.md)). Evidence is data; it never directs Mycel to execute a cited repository's code or instructions.

## Behaviour

### Portable addresses

The qualified textual form is `repo:@root/path[#name]`. `root` is exactly `code`, `artifact` or `index`; it names a configured binding, never a machine's absolute folder. `code` and `artifact` are independent of content origin: Markdown under `code_root` is still a document. `index` selects generated text with no file and is valid for reading only, under the restrictions of MYC-8 and MYC-9.

| Address | Selects |
|---|---|
| `cellar:@code/src/net/retry.py#RetryPolicy.allow` | A method under `code_root` |
| `cellar:@code/README.md#Setup` | A checkout document section |
| `cellar:@artifact/README.md#Setup` | The distinct artifact-folder section |
| `cellar:@artifact/docs/limits.md` | The complete artifact file |
| `cellar:@index/summaries#1/7` | An index-only summary, for reading |
| `cellar:@index/overview#src/net` | An index-only overview section, for reading |

Qualified addresses use UTF-8 percent encoding. The repository and optional name leave only ASCII letters, digits, `-`, `.`, `_` and `~` unescaped; the path additionally leaves `/` as its separator. A canonical formatter uses uppercase hexadecimal escapes. Thus `Limits > Backoff` is formatted as `Limits%20%3E%20Backoff`. For author convenience, unescaped Unicode and spaces are accepted in qualified components and are canonicalized when returned. The first literal `:` separates the repository and the first literal `#` separates the optional name; these characters inside a component must be escaped. Literal `%` is `%25`. Decode once with strict UTF-8; malformed escapes, control characters and an empty repository, path or explicitly supplied name are `not_a_ref`.

A file path is relative to its selected root, uses `/`, and has no leading `/`, empty component, `.` or `..` component, trailing `/`, NUL or backslash. An encoded `/` in a path component is refused rather than decoded into traversal. Paths and names are case-sensitive strings and receive no Unicode normalization or case folding during parsing. Filesystem identity may establish aliases when the platform reaches the same file; textual spelling alone does not merge files. The `@index` path is exactly `summaries` or `overview` in this Build; other index-only namespaces are refused.

Legacy `repo:path[#name]` remains accepted without percent decoding and uses its existing literal path and symbol/heading matching. It checks both file roots and succeeds only when they identify one physical file. A heading or symbol cannot break a file-path tie. Different files yield `ambiguous_path` with up to 20 qualified candidate addresses, not a guessed edge. The qualified `@code/`, `@artifact/` and `@index/` prefixes are reserved by the new grammar; a real folder called `@code` is addressed as `repo:@code/@code/file.md`. Legacy summary and overview places remain read aliases when there is no colliding file; otherwise the caller must use `@index` or a chunk identifier. Existing stable identifiers are not changed by textual canonicalization.

### Root aliases and one resolver

Two configured roots reaching one physical file create aliases for one document and its chunks in that location. The document retains its existing primary binding while that binding still reaches it. On first discovery, the more specific containing root is primary, with `artifact` winning equal-root ties. The reply's canonical address uses that binding; either qualified alias resolves to the same identifiers. Reconfiguring a root or a genuine move updates addresses by MYC-1's identity rules and never merges two different files merely because their paths or contents coincide. A previously pinned resolved identifier follows a recognized move; its original declaration and original address remain in the audit evidence. A later legacy ref made ambiguous by a newly added file becomes a fault and is not silently kept valid by its former resolution.

One resolver serves sources comments, frontmatter, `derive`, `relate`, `confirm`, `read` and classifier evidence assembly. It returns a typed selection: `file`, `chunk`, `family` or `index`. A file selects all its bytes, including frontmatter. A document name selects one heading path or one unique bare title. A method may omit its class only when the match is unique. A class source selects its header and method family under MYC-2; its member list is part of the pinned selection. Its member places are sorted by canonical address, then full stable identifier. Adding or removing a method therefore changes the family selection even if every previously present method is unchanged. A class requested for `read` selects the header chunk as MYC-11 already specifies.

Mutation dependants and the endpoints of `relate` must each resolve to one chunk; they never expand a whole file or class into silent multiple mutations. A dependency source may be a file, chunk or class family. A sources/related comment can name such a selection; its expanded members and membership are tracked together. Index-only generated text remains ineligible as a declared/asserted source or relation target. Unknown, disabled, missing and ambiguous targets retain the visible faults of MYC-2. Declarations are preserved as written alongside their parsed and resolved forms.

A mutation that pins current sources must hold the required repository locks, compare the dependant's indexed exact version with current disk text, resolve sources again, and read the required current files again. If the files or resolution changed since ingest, it returns `invalid_input` with detail `changed_since_ingest` and the affected qualified addresses; the caller ingests and retries. It does not pin unchecked index text or silently rewrite a file. Previously resolved missing sources can be explicitly withdrawn when MYC-7 permits it; a new malformed, ambiguous, unresolved or ineligible ref cannot become a successful confirmation. Source byte changes immediately after the final check are found by the next ordinary detection pass, so a confirmation is bound to its recorded observation rather than a promise that disk cannot change.

### Comparison hashes and exact versions

These hashes have different jobs:

| Value | Bytes or text it covers | Purpose |
|---|---|---|
| File hash | SHA-256 of every original file byte | Scan changes, file-wide source comparison and full-file guards |
| Document content hash | SHA-256 of the UTF-8 body after NFKC, Unicode-whitespace runs collapsed to one ASCII space and outer whitespace stripped; excludes its heading line | Section matching and the existing body-comparison rule |
| Document title hash | The same normalization and hash of the parsed heading title | Recognizing a heading rename |
| Code content hash | SHA-256 of the chunk's exact UTF-8 text | Code comparison and matching |
| Snapshot hash | SHA-256 of exact retained bytes, with no normalization | Immutable evidence addressing and exact-input guards |
| Manifest/input hash | SHA-256 of the versioned canonical JSON bytes specified below | Reproducible selection and request identity |

Comparison records include the hash kind, algorithm revision and Unicode database version where relevant. A pinned normalized hash is compared using its recorded revision; a Build unable to reproduce that revision reports `unsupported_comparison` and cannot classify the pair or silently repin it. Code, file and exact snapshot hashes are unaffected by a Unicode normalization database change.

A chunk's stable identifier is independent of its text version. Every distinct complete stored text has a distinct version identified by its exact snapshot hash within that chunk. Name/path metadata changes with identical stored text keep that version and its vectors. A heading rename that changes stored text keeps the chunk identifier but creates a new exact text version. Normalized equality never authorizes sending yesterday's bytes as today's exact text or applying an old request to changed text. The identity pass still records a rename or whitespace-only body equivalence separately from a substantive content edit; inherited source pins survive the former, while an edit recognized under MYC-D12 may create new pins. Branch/stash restoration of a known version always restores its own existing pin rather than the disk version's later pin.

### A baseline owned by the dependant

At initial resolution, an accepted MYC-D12 repin, successful generated publication, or creation of a relation, the same transaction writes the link's immutable baseline manifest and the required snapshot blobs. The manifest records the dependant identifier, exact version and text, source declaration and resolved qualified place, kind, comparison revision/hash, exact before-text hash, member list for a file/family selection, and capture metadata. A branch/stash version may own its own baseline even while it is away from disk. Its source text is read from that location without checking anything out; an absent required source stays missing rather than being substituted from another branch.

Snapshots preserve complete exact source selections and the complete dependant text, including headings, code, comments and whitespace as supplied to the classifier. A file-wide selection preserves all original bytes; an extracted text snapshot records its encoding, original file hash and byte range or ordered member descriptors so the extraction can be checked. Line ranges help a reader but are not identity. Capture does not cut, summarize or normalize evidence. A non-UTF-8 selection may retain bytes, but a text-only classifier receives no lossy replacement and the case remains visibly `insufficient_evidence` until a supported exact textual representation exists.

Blobs are content-addressed by `(owner_repository, sha256)` in the Mycel store. A source in one repository may be copied into a dependant-owned evidence blob in another; identical blobs can be shared within their owner's repository, never through a source-row foreign key that source removal would cascade away. Each baseline, verification record, Drift bundle and in-flight operation holds explicit owning references to its blobs. A blob has no chunk identifier, locations, vector or searchable document row. It cannot be returned by ordinary search or `mycel read` as a current source.

Removing the source's last disk/branch/stash location deletes its source chunk/version rows and resolved edges as MYC-D8 requires. A surviving dependant's natural dependency record and pinned snapshot remain. Its current source state is `deleted` if no location holds it, or `away` if only a local branch or stash holds it. Neither condition replaces the baseline with empty text. A deletion observation includes the qualified place, prior observed file hash where known, and detection time; missing current text is represented as an explicit absence, never a fabricated empty file. A recreated source at the same natural place reconnects the retained dependency record without renewing its baseline; a resolved source recognized as a genuine move retains identity through the normal ingest rules.

### Exact request evidence and result guards

Before either paid stage, Mycel assembles an immutable request manifest from the retained baseline, current source selection or explicit absence, current dependant exact version/text, and all required context. It retains every required exact snapshot and the exact decision-payload bytes. The payload includes `mycel-dependency-v1`, the question/criteria revision, actual selected model, immutable adapter revision, command hash, instruction/environment identity and policy revision, source existence, current membership, before/current/dependant descriptors and text, and ordered context descriptors/text. The payload uses semantic manifest projections: omit baseline `id`, `capturedAt` and capture `location`, and omit full-file `fileHash`/byte `span` guards from every nested snapshot descriptor; retain kind, owner, declarations, exact snapshot/comparison hashes, places and membership. The full immutable manifest and its identity stay in the bundle and guard set. Its `inputHash` is SHA-256 of those canonical payload bytes excluding the `inputHash` field itself. MYC-14 defines the exact reviewer request/response schemas, semantic selection locators and derived allowed-citation list. A provider's transport wrapper, effective timeout/output/call budget, credentials and transient request identifier are not part of that decision payload and contain no evidence pointers the provider cannot read.

Canonical JSON is UTF-8, with object keys sorted by Unicode code point, ordered arrays, no insignificant whitespace and no Unicode normalization. Strings escape only quotation marks, backslashes and JSON control characters, using lowercase `\u00xx` for controls without a short JSON escape; other Unicode remains literal. Integers use their shortest base-10 form and no leading plus/zeros; booleans and null use JSON's literal forms. The semantic payload contains no floating-point numbers: confidence and probabilities are result fields, while byte counts, protocol revisions and offsets are integers. This makes the exact payload encoding deterministic without a language-specific float representation. The SHA-256 spelling is lowercase hexadecimal; JSON/schema/protocol revisions are recorded explicitly.

Full current-file hashes, observed modification/deletion/generated times, location identities and effective quiet-period eligibility are a separate guard set. Times and deadlines do not alter semantic cache identity, but every required full-file hash, current resolution/member list, dependant exact version, baseline identity, settings enablement, configured reviewer command identity and eligibility are rechecked before each call and before applying either result. A cached result must have the same decision payload, model, question and policy revisions; it still passes fresh guards. Required context changes invalidate reuse. A request holds an in-flight owning lease on its evidence until its operation has completed or its process is proven ended under MYC-12. A stale result may remain diagnostic history marked `obsolete`; it affects no current work, verification, stale mark or pin.

No call is made when required evidence is missing, corrupt or from an unsupported comparison revision. A paid stage receives no call when the complete input exceeds that stage's limit; MYC-14 may bypass oversized Jev input and route the same complete evidence to a reviewer with a sufficient input limit. If neither stage can fit it, work remains visibly unresolved. The visible status includes `baseline_missing`, `snapshot_corrupt`, `unsupported_comparison` or `input_too_large` as appropriate. Reconstructing missing evidence is allowed only from a retained exact version, local git blob or restored store copy whose bytes reproduce the recorded exact hash and extraction manifest. Re-reading a newer file, guessing from a diff or asking a model to invent the old text is not reconstruction. A snapshot read verifies its length and SHA-256 before use.

### Retention, removal and rebuilding

There is no time limit on snapshots referenced by a surviving dependency/version baseline, current verification record or open Drift bundle, including versions held only by local branches or stashes. In-flight leases protect their evidence until their invocation ends. A repin releases the old live baseline only after the new complete baseline commits; retained verification/Drift history may still own the old evidence. Disabling a repository hides its text and prevents paid calls without pruning its baselines.

Retain the newest 1,000 closed Drift bundles per owner repository, ordered by closure time and then full Drift identifier, with each bundle's classification stages, exact decision payloads, source/dependant/context evidence and closure provenance. A currently referenced bundle or active baseline cannot be pruned to meet that number and may temporarily exceed it. Repeated observations/cached uses of identical input are attached to one bundle; they do not create unlimited copies of text. When a newer request supersedes an older one in open work, the older bundle becomes closed diagnostic history with `obsolete` as its result disposition, then obeys this bound. Verification-owned evidence follows the lifetime of its MYC-7 verification record, independently of this bound. Activity pruning never deletes baselines, verification evidence, open work or classifier history.

Dropping a declared ref, removing an assertion/relation, deleting a dependant version or repository, or pruning its owning history record releases the applicable owner references in the same transaction. Delete a blob only when no surviving baseline, verification, retained bundle or live lease in that owner repository refers to it. A completed writing invocation collects such unreferenced blobs under its repository lock; a reporting command performs no collection. Removing a source repository deletes its own evidence but leaves other repositories' dependant-owned copies and visible now-ineligible source faults. Removing a dependant repository deletes all its evidence and leases once no mutation is running, without changing another repository's blobs.

A rebuild of a lost store can recreate current chunks and new dependency baselines from files, but cannot recover past pins, assertions, verifications or classifier history unless a store backup preserves their manifests and bytes. Report this as a new index generation in `info` and activity. No classifier claim is made about pre-rebuild source changes, and no old closed work or owner confirmation is invented. A missing baseline inside a surviving store stays visibly missing until exact reconstruction or an authorized MYC-D12 repin; a scan or provider call cannot repair it by silently choosing today's text.

### Checks

Unit fixtures cover qualified/legacy parsing, one-pass decoding, Unicode and escaped names, root/path traversal rejection, canonical JSON bytes and fixed SHA-256 vectors. Store fixtures cover overlapping roots and colliding names, source/family membership changes, exact versus normalized text changes, branch/stash pin restoration, removal and reconstruction, corrupt bytes, atomic capture/repin, obsolete results, guard changes and reference-counted collection. A history fixture closes 1,001 bundles while retaining an older live baseline, verification and in-flight lease; only eligible unreferenced history is collected. These checks use stand-in classifiers and spend no quota.

## Requirements

| ID | Mycel must… | Origin | Verified by |
|---|---|---|---|
| MYC-16.1 | parse, format and return portable qualified root addresses with the exact escaping/relative-path rules above; retain unqualified literal refs where unambiguous and refuse malformed or colliding selections visibly | New | unit |
| MYC-16.2 | retain one document/chunk identity for overlapping-root aliases, distinguish different files, return a stable primary qualified address and preserve source identities through recognized moves without guessed merging | New | store |
| MYC-16.3 | use one typed resolver for declarations, reads and mutations; pin file bytes and class membership as well as member hashes, and require one dependant or relate endpoint | New | store |
| MYC-16.4 | distinguish normalized comparison hashes from exact text/file/snapshot hashes, record comparison revisions, use exact text versions and refuse unsupported pinned comparisons without repinning | New | unit |
| MYC-16.5 | atomically capture each link baseline with complete source/dependant evidence, exact hashes, declarations, root-aware resolved selections and membership; retain separate pins for dependant versions in every location | New | store |
| MYC-16.6 | retain immutable content-addressed snapshots owned by the dependant repository, with no searchable chunk, vector or location row, and preserve them across source deletion only through surviving owner references | New | store |
| MYC-16.7 | distinguish explicit source absence from empty text, retain deleted/away baseline evidence, and reconnect a recreated source without renewing its pin | New | store |
| MYC-16.8 | retain exact canonical classifier decision payload bytes and all required evidence, bind reuse/results to their hash plus model/question/policy revisions, and recheck complete current-file/selection/version/eligibility guards at both calls and application | New | store |
| MYC-16.9 | verify retained bytes before use, reconstruct only hash-exact evidence, and make missing/corrupt/unsupported/over-limit inputs visible without a paid call or substituted baseline | New | store |
| MYC-16.10 | protect live baseline, verification, open work and in-flight evidence; bound closed Drift bundles to 1,000 per repository while protecting active references and keep activity pruning independent | New | store |
| MYC-16.11 | release owner references atomically and collect only wholly unreferenced evidence under the owner's repository lock; remove no other repository's dependant evidence when its source repository is removed | New | store |
| MYC-16.12 | report a fresh store rebuild as a new index generation and never claim reconstructed old pins, verifications or classifier history without exact backed-up evidence | New | store |
| MYC-16.13 | recheck indexed/current dependant and source versions before pinning mutations, reject changes since ingest with qualified addresses, and preserve MYC-D12's authorized edit/confirmation semantics | New | store |
| MYC-16.14 | bind immutable reviewer revision and exact command/instruction identities into canonical semantic evidence, keep transport budgets/file guards outside it, and invalidate reuse/application when the configured executable or revision changes | New | store |

## Interface

The address is returned alongside root/path metadata in search/read/citations, stale reasons and fault candidates. Callers can copy it into `mycel read`, a sources comment or a pinning command without knowing absolute folders. Snapshot access is an internal Mycel store operation, not a new search corpus or file-writing command.

```ts
type Root = "code" | "artifact" | "index";

interface SourceAddress {
  repository: string;
  root: Root;
  path: string;
  name?: string;
  address: string;                    // canonical qualified text
}

interface SnapshotEvidence {
  snapshot: string;                   // opaque owner-scoped locator: snapshot:<sha256>
  hash: string;                       // SHA-256 of exact bytes
  bytes: number;
  encoding: "utf-8" | "bytes";
  comparison?: {
    kind: "document_body" | "code_text" | "file_bytes" | "family";
    revision: string;
    unicodeVersion?: string;
    hash: string;
  };
  place?: SourceAddress;
  fileHash?: string;                  // full original file guard
  span?: { start: number; end: number }; // UTF-8 byte offsets, end exclusive
}

interface BaselineManifest {
  schema: 1;
  id: string;                        // SHA-256 of canonical manifest payload
  ownerRepository: string;
  dependantId: string;
  dependantVersion: string;
  dependant: SnapshotEvidence;
  kind: "declared" | "asserted" | "related" | "generated";
  ref?: string;                      // preserved declaration as written
  source: SourceAddress;
  selection: "file" | "chunk" | "family";
  members: Array<{ id?: string; place: SourceAddress; evidence: SnapshotEvidence }>;
  pinnedHash: string;                 // selected comparison/membership hash
  capturedAt: string;
  location: { kind: "disk" | "branch" | "stash" | "generated"; commit?: string };
}

interface EvidenceBundle {
  schema: 1;
  ownerRepository: string;
  baseline: string;                   // immutable BaselineManifest id
  inputHash: string;                  // exact canonical decision payload, excluding inputHash
  requestSnapshot: string;            // exact payload bytes, owner-scoped snapshot locator
  evidence: SnapshotEvidence[];       // complete required source/dependant/context bytes
  sourceState: "present" | "away" | "deleted";
  guards: Array<{
    place: SourceAddress;
    hash?: string;                   // complete current file/version, absent for deletion
    changedAt?: string;
    event: "file_changed" | "deleted" | "generated";
  }>;
  disposition: "active" | "complete" | "obsolete" | "error";
}
```

Within a manifest, its identifier is computed without its own `id` field. `snapshot:<sha256>` is resolved only with the owner repository of the baseline/bundle; it is not a path or URL and is never dereferenced by the provider. The actual request includes evidence text. The semantic source-family hash covers canonical ordered member places, comparison kinds/revisions/hashes and membership; changing a member changes it even when all other members are unchanged. Current resolved identifiers aid audits but are not portable Source Ref syntax. Reconnecting a recreated file uses the natural address and exact evidence rather than assuming its new internal identifier equals a deleted one.

## Known problems

This is a new Mycel 2 contract, not measured implementation behavior. Version 1 retained a normalized pinned hash without the required exact before-text evidence, and did not distinguish code-root documents with colliding artifact paths. Its source-removal behavior left indexed rows rather than dependant-owned immutable evidence. These defects prevent reliable semantic comparison after an edit or deletion. [MYC-1](01-corpora-and-ingest.md#known-problems-in-version-1) and [MYC-2](02-provenance-and-freshness.md#known-problems-in-version-1) retain their original historical evidence.

Live baselines may retain substantial text because semantic review needs the exact inputs, and normalized comparison versions require compatibility across Builds. The retention and explicit-fault rules make these costs and limitations visible without discarding evidence that active work still needs.

## Decisions

No owner question is introduced. On 8 October 2026 the agent selected the qualified grammar, exact-versus-comparison hash distinction, dependant-owned blobs, manifest/guard shapes and newest-1,000 closed-bundle bound under the request to finish the specifications; the owner accepted the completed specification set on 8 October 2026. MYC-D7's document scope, MYC-D8's deletion of unlocated source chunks and MYC-D12's edit/confirmation rule remain accepted as recorded. Provider selection, debounce, confidence routing and Drift-work consequences are recorded in MYC-14 rather than repeated here.
