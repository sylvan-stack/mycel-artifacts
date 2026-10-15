---
role: authored
---
# Mycel specifications

What Mycel 2 does, written from what Mycel 1 did. [Mycel](../../arbol/GLOSSARY.md#mycel) is the knowledge engine of the Sylvan Stack: it turns the documents and the code of each repository into an index that is kept current, knows what each part rests on, and can be searched by meaning and by exact wording. Mycel 2 is implemented from scratch; these specifications say what is carried over from version 1, what changes and what is left behind.

## Specifications

| Spec | Title | Status |
|---|---|---|
| [MYC-0](00-overview-and-legacy-map.md) | Overview and legacy map | accepted |
| [MYC-1](01-corpora-and-ingest.md) | Corpora and ingest | accepted |
| [MYC-2](02-provenance-and-freshness.md) | Provenance and freshness | accepted |
| [MYC-3](03-embedding.md) | Embedding | accepted |
| [MYC-4](04-retrieval.md) | Retrieval | accepted |
| [MYC-5](05-settings.md) | Settings | accepted |
| [MYC-6](06-index-store.md) | The index store | accepted |
| [MYC-7](07-drifts-and-verification.md) | Drifts and verification | accepted |
| [MYC-8](08-summaries.md) | Summaries | accepted |
| [MYC-9](09-code-overview.md) | The code overview | accepted |
| [MYC-10](10-grep-replacement.md) | The grep replacement | accepted |
| [MYC-11](11-reading-a-chunk.md) | Reading a chunk | accepted |
| [MYC-12](12-record-of-work.md) | The record of work | accepted |
| [MYC-13](13-checks-and-evaluation.md) | Checks and the evaluation set | accepted |
| [MYC-14](14-drift-detection.md) | Drift detection | accepted |
| [MYC-15](15-distribution-and-replacement.md) | Distribution and replacement | accepted |
| [MYC-16](16-source-addresses-and-evidence.md) | Source addresses and evidence | accepted |

MYC-0 sets the boundary. MYC-1 to MYC-4 specify ingest, provenance, embedding and retrieval; MYC-5 and MYC-6 specify settings and storage; MYC-7 to MYC-12 specify relations, verification, summaries, overviews, grep, reads and activity; MYC-13 specifies checks and evaluation. MYC-14 completes Jev classification, five-minute debounce, smarter review and the Drift lifecycle. MYC-15 specifies independent Python distribution and version 1 removal. MYC-16 specifies portable source addresses, exact baseline evidence and retention. All 17 chapters are accepted for implementation on 8 October 2026, after the owner answered the final Drift decisions and agreed with the remaining proposals. Acceptance records the specification contract; runtime checks and provider qualification remain implementation/release work. Every chapter is required scope; task volume is not a reason to defer or drop a function (MYC-D4, MYC-D13).

Evidence the specifications rest on is in `research/`:

- the inventories of the version 1 source: [ingest and the knowledge graph](../research/v1-inventory-ingest-and-graph.md), [embedding and retrieval](../research/v1-inventory-embedding-and-retrieval.md), [the sync pass, settings, scope, commands and summaries](../research/v1-inventory-sync-settings-commands.md);
- [what the installed version 1 did](../research/v1-observations-2026-10.md) on 6 to 8 October 2026.

## Questions and decisions

Checked 9 October 2026 against the specification originals and their Linear copies. Each linked specification records the questions and proposed defaults in its Decisions section.

### Open questions and pending decisions

None remain among MYC-D1 through MYC-D38. The owner answered the final MYC-D28/MYC-D29 proposals on 8 October 2026; all 17 specifications are accepted for implementation.

Open since 14 October 2026: [MYC-D39](02-provenance-and-freshness.md#decisions), how Mycel answers "which document describes this chunk?" and shows code that no document describes. Proposed: `mycel read` lists the document sections joined to a chunk, a search marks code that has one, and `mycel undocumented` lists the code of a repository that has none. The proposed requirements MYC-2.27, MYC-4.29 and MYC-11.12 are not active before the owner decides.

MYC-D1 records the owner’s Python decision; MYC-15 makes its independent distribution concrete. MYC-D7 is now decided: Markdown in both the checkout and the artifact folder is searchable document content. MYC-D34 is decided by delegation: keep the newest 1,000 activity entries per repository, with running operations protected from pruning. The owner decided in [SYL-96](https://linear.app/sylvan-stack/issue/SYL-96/review-the-new-mycel-specifications-myc-5-to-myc-13-and-the-findings) that search must reflect changes to explicitly referenced upstream artifacts, including Glossary and Mycel dependencies of Driver chunks, and rejected the general term “refresh”. MYC-4 specifies checking and ingesting local changes before search, including contributing shared documents and recursive upstream dependencies.

### Accepted decisions

| Decision | Recorded outcome | Source |
|---|---|---|
| MYC-D1 · What language is Mycel 2 written in? | Decided 8 October 2026 by the owner: “It should be python.” Use Python; MYC-15 specifies the self-contained runtime and build contract | [MYC-D1](00-overview-and-legacy-map.md) |
| MYC-D2 · Where does the index live? | Decided 8 October 2026 by the owner: resolved; accept PostgreSQL with ParadeDB in a database of Mycel's own, at an address supplied by the settings | [MYC-D2](00-overview-and-legacy-map.md) |
| MYC-D3 · Where are the settings kept? | Decided 8 October 2026 by the owner: resolved; keep the settings in `~/.mycel/config.toml`. The owner or their editor writes the file; Mycel only reads it | [MYC-D3](00-overview-and-legacy-map.md) |
| MYC-D4 · Which further functions of version 1 follow the first version, and in what order? | Decided 8 October 2026 by the owner: implement all specifications regardless of how many tasks are involved. Every listed function remains required; task volume is not a reason to defer or drop it, and dependency order may guide the work | [MYC-D4](00-overview-and-legacy-map.md) |
| MYC-D5 · Does Mycel fetch content from outside? | Decided 8 October 2026 by the owner: resolved; Mycel has no integrations that fetch outside content. Another component saves that content as files, and Mycel indexes those files | [MYC-D5](00-overview-and-legacy-map.md) |
| MYC-D6 · Are work trees and a view of the index per branch carried over? | Decided 8 October 2026 by the owner: resolved; retire the work-tree commands and separate branch indexes. Read local branches and stashes from git and record where each chunk version is found, as decided in MYC-D8; search uses the versions on disk | [MYC-D6](00-overview-and-legacy-map.md) |
| MYC-D7 · Which file types and exclusions does the scan use, and does checkout Markdown belong to the document corpus? | Decided 8 October 2026 by the owner: resolved for the proposed default file types, the common skip list and `.gitignore`; include Markdown beside code, such as `README.md` and `docs/`, in the document corpus as well as Markdown under `artifact_root`. Keep each document's actual root/path and index overlapping-root files once; different files with colliding relative paths remain distinct | [MYC-D7](01-corpora-and-ingest.md) |
| MYC-D8 · How long do rows of what left the disk stay? | Decided 8 October 2026 by the owner: no time limit. Mycel reads the disk, every local branch and every stash, and no branch of a remote, and records for each version of a chunk the locations it is found in ([Branches and stashes](01-corpora-and-ingest.md#branches-and-stashes)). What is found in none is deleted by that pass. Search, edges and staleness look at the disk | [MYC-D8](01-corpora-and-ingest.md) |
| MYC-D9 · Does Mycel ever fetch from a remote or reset a checkout? | Decided 8 October 2026 by the owner: agreed. Mycel never fetches remote changes or resets a checkout; it reads disk, local branches and stashes without changing them | [MYC-D9](01-corpora-and-ingest.md) |
| MYC-D10 · How are the chunks between symbols named? | Decided 8 October 2026 by the owner: agreed. Name loose code after the following symbol as `<before name>`, and use `<end>` after the final symbol | [MYC-D10](01-corpora-and-ingest.md) |
| MYC-D11 · Which repositories may Source Refs target? | Decided 8 October 2026 by the owner: Source Refs may target only Mycel-enabled repositories. No outside-reference exemption; disabled or unregistered targets are invalid and visible, and valid unresolved refs are retained for retry | [MYC-D11](02-provenance-and-freshness.md) |
| MYC-D12 · What makes a stale chunk fresh again? | Decided 8 October 2026 by the owner: editing that section or explicitly confirming it clears the stale mark. A file scan or an edit to another section does not | [MYC-D12](02-provenance-and-freshness.md) |
| MYC-D13 · Which of the designs version 1 did not build are taken up? | Decided 8 October 2026 by the owner: implement all specifications regardless of the number of tasks, including all five previously deferred designs. Task volume is not a reason to defer them; their remaining detailed specifications and implementation are required follow-up work. The later MYC-D28 decision replaces the former numerical scoring design with Jev dependency classification without a change-size threshold, a five-minute quiet period and low-confidence review by a smarter model | [MYC-D13](02-provenance-and-freshness.md) |
| MYC-D14 · Which model and provider embed the chunks? | Decided 8 October 2026 by the owner: agreed, after checking for a newer Voyage code-family model. The check found `voyage-code-4`, released 13 August 2026, which replaces `voyage-code-3`; use it at 1024 dimensions | [MYC-D14](03-embedding.md) |
| MYC-D15 · Where does the key of the embedding service come from? | Decided 8 October 2026 by the owner: Mycel's own Keychain item is OK only if Arbol can also write it. Preserve Arbol configuring all secrets, including the Voyage API key; Mycel reads the same credential and remains independent of Arbol | [MYC-D15](03-embedding.md) |
| MYC-D16 · Is there an on-device model for repositories whose text must not leave the machine? | Decided 8 October 2026 by the owner: no, Voyage API only. No local model or second embedding provider is in scope | [MYC-D16](03-embedding.md) |
| MYC-D17 · What happens to a text longer than the model takes? | Decided 8 October 2026 by the owner: every bit of data must be embedded without loss. No truncation; complete coverage across all parts, with each input within the model's limit | [MYC-D17](03-embedding.md) |
| MYC-D18 · Do the documents of another repository take part in every search? | Decided 8 October 2026 by the owner: shared documents must be configurable by files or folders, not only by whole repository. `search.shared_documents` names `repo` and `paths` relative to its `artifact_root`; files select themselves and folders select document files recursively. Defaults: all Mycel artifact files (`mycel`, `.`), plus only Arbol's `GLOSSARY.md` (`arbol`, `GLOSSARY.md`). Only enabled repositories contribute, and code-only searches include no shared documents | [MYC-D18](04-retrieval.md) |
| MYC-D19 · Is one plain word an identifier? | Decided 8 October 2026 by the owner: yes, the proposed default. A plain word takes the identifier route in the first version; any later change requires the evaluation of MYC-4.25 | [MYC-D19](04-retrieval.md) |
| MYC-D20 · Where do the factors, margins and limits start? | Decided 8 October 2026 by the owner: use the previous values unless evaluation warrants a change. The owner delegates these values to the agent; adjustments require the before-and-after evaluation report of MYC-4.25 | [MYC-D20](04-retrieval.md) |
| MYC-D21 · Are the results of several repositories merged into one list? | Decided 8 October 2026 by the owner: separate replies, the proposed default. Return one reply per enabled repository, with the requested result limit per reply; do not merge the results or compare scores across repositories | [MYC-D21](04-retrieval.md) |
| MYC-D22 · Does switching a repository off also hide it from search? | Decided 8 October 2026 by the owner: yes, a disabled repository is hidden from every search, including direct searches, organization searches and shared documents | [MYC-D22](04-retrieval.md) |
| MYC-D23 · What does Mycel do with a key in the settings file that it does not know? | Decided 8 October 2026 by the owner: "Refuse unknown keys and show detailed error message." Unknown tables or keys stop commands that need valid settings with a detailed `settings` error. The earlier decision to remove deprecated keys remains recorded; that cleanup was completed the same day | [MYC-D23](05-settings.md) |
| MYC-D24 · Under what name is the key of the embedding service kept in the Keychain, and how is it written and read? | Decided 8 October 2026 by the owner: the agent chooses. Chosen: the proposed default, the service `mycel` and the account `voyage-api-key`, through the `security` program. The isolated dummy-item create/read/delete ACL trial passed on macOS 27.0.1 on 8 October 2026; packaged-runtime checks repeat the probe | [MYC-D24](05-settings.md) |
| MYC-D25 · How does the password of the store reach Mycel? | Decided 8 October 2026 by the owner: the Keychain. The password comes from Mycel's Keychain item; no setting names a command for it | [MYC-D25](06-index-store.md) |
| MYC-D26 · Is anything carried over from the index of version 1? | Decided 8 October 2026 by the owner: no, and everything of version 1 is removed. Nothing is copied across | [MYC-D26](06-index-store.md) |
| MYC-D27 · What does a command report when it covers several repositories and only some could be done? | Decided 8 October 2026 by the owner: agreed. One entry for each repository, the status 1 as soon as one was not done, and the full reply in that case too | [MYC-D27](06-index-store.md) |
| MYC-D28 · What contracts implement classification and smarter review? | Decided 8 October 2026: use the smarter-model command specified in settings (`drifts.review_command`), initial confidence floor 0.7, explicit bounded classification, five-minute quiet period and completed evidence/reviewer contracts; qualification remains a release check | [MYC-D28](14-drift-detection.md#decisions) |
| MYC-D29 · What does still_supported do? | Decided 8 October 2026: suppress/close only the exact pair's Drift work; stale marks and pins remain until an affected-section edit or explicit confirmation under MYC-D12 | [MYC-D29](14-drift-detection.md#decisions) |
| MYC-D30 · How is a relation between two chunks made, where neither governs the other? | Decided 8 October 2026 by the owner: agreed. A `related` comment in the section, and the command `mycel relate` | [MYC-D30](07-drifts-and-verification.md) |
| MYC-D31 · Who writes the text of a summary, now that `infer` is deprecated? | Decided 8 October 2026 by the owner: agreed. A command the owner names in the settings writes each summary | [MYC-D31](08-summaries.md) |
| MYC-D32 · Is the code overview a file in the repository's document folder, or is it kept in the index only? | Decided 8 October 2026 by the owner: resolved; keep the code overview in the index only, searchable and printable with `mycel overview`, without writing a file in a checkout | [MYC-D32](09-code-overview.md) |
| MYC-D33 · Under which name is the grep replacement started? | Decided 8 October 2026 by the owner: agreed. `mycel grep`, and no second program | [MYC-D33](10-grep-replacement.md) |
| MYC-D34 · How much activity history is kept? | Decided 8 October 2026 by the owner: delegate the size of the history to the agent. Chosen: newest 1,000 entries per repository, plus a separate newest 1,000 for entries belonging to no repository; delete all attached details with each pruned entry, and protect currently running entries until their invocations end. The chosen limit is not a measured one | [MYC-D34](12-record-of-work.md) |
| MYC-D35 · Where is the evaluation set kept, and who writes it? | Decided 8 October 2026 by the owner: resolved; one configured evaluation file per repository in its document folder, versioned with its documents. A person or an agent adds real questions and the chunks that should answer them | [MYC-D35](13-checks-and-evaluation.md) |
| MYC-D36 · Which store do the automatic checks work on? | Decided 8 October 2026 by the owner: resolved; automatic store checks create and remove their own `mycel_check_` databases on the configured server and never open the owner's actual database | [MYC-D36](13-checks-and-evaluation.md) |
| MYC-D37 · Keep prescribed named defaults/exclusions? | Decided 9 October 2026 by the owner: keep the prescribed names as explicit packaged-data exceptions, without implicit repository registration, aliasing, folder fallback or product dependency | [MYC-D37](00-overview-and-legacy-map.md) |
| MYC-D38 · Recognize a function rename separately from the complete-code hash? | Decided 9 October 2026 by the owner: preserve identity using a conservative parser-derived body/signature key; retain the complete-code hash for exact change tracking and evidence | [MYC-D38](01-corpora-and-ingest.md) |

## Conventions

These conventions belong to Mycel. Their shape is aligned with the historical [Driver Contract conventions](../../arbol/driver-contract/README.md#conventions); writing, building and running Mycel requires no Arbol procedure or implementation.

**Shape.** Purpose, Scope, Behaviour, Requirements, Interface, Known problems, Decisions. Historical statements keep ordinary evidence locators to the frozen version 1 source; those citations declare no index dependency.

**Identifiers.** Requirements are `MYC-1.4`: requirement 4 of specification 1. Decisions are numbered across the specifications, `MYC-D1` onwards. Never reuse a number. Append new requirements; withdrawing one leaves its identifier reserved and records its date and deciding outcome.

**Origin.** `Kept` carries over observed version 1 behavior; `Changed` alters it and explains why under Known problems; `New` has no version 1 counterpart; `Dropped` records behavior deliberately left behind.

**Status.** `draft` → `review` → `accepted` → `implemented`. Only the owner accepts a specification. Open implementation work after acceptance; mark it implemented only when every requirement names a passing check.

**Decisions.** Each unresolved choice has a proposed default and an Outcome row. Complete specification work may proceed with a plainly identified proposal; owner acceptance is never inferred from drafting it. Record an owner answer with its date and reconcile affected requirements in the same change.

**Wording.** Requirements are proposals until acceptance. Examples are fictional and contain no real credentials or conversation content.

**Source Refs.** Every tracked Source Ref must name a repository registered in Mycel and currently enabled (MYC-D11). The name `mycel:` means this corpus and, later, the new code. Deprecated repositories have no index entries. A section describing version 1 instead gives ordinary historical evidence locators, written `mycel_deprecated_v1:path#symbol` or `arbol_deprecated_v1:path#heading`, outside frontmatter `sources:` and `<!-- sources: -->` blocks. These preserve the evidence without declaring an index dependency.

**Verified by.** Mycel has no vendor tool behind it, so its kinds of check are its own:

| Check | Meaning |
|---|---|
| unit | Automated, with no index store and no network |
| store | Automated, against an index store made for the test and discarded after it. No network |
| eval | The evaluation set of MYC-4.25: queries with the chunks each should find. It needs vectors, so it is run on demand |
| live | A check that calls a model service and spends quota, including embedding, Jev or smarter-model review. Run on demand, never in the automatic suite |

**Observed.** *Observed in version 1* means read in the version 1 source; the inventories say for each statement whether it was also run. *Observed on* a date means seen on the installed program that day, and is recorded in the observations file.

The owner selected Apple Silicon (`macos-arm64`) only on 14 October 2026. The current target contract is [MYC-15](15-distribution-and-replacement.md#the-python-distribution); earlier target-scope receipts remain historical, and working publication still requires its own checks.
