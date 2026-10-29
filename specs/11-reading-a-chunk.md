---
role: authored
spec: MYC-11
status: implemented
---
# Mycel · 11 Reading a chunk

A search result shows the first 240 characters of a chunk and, when there is one, the file to open. `mycel read` returns the whole chunk: one function, one section, one summary. This specification fixes how a chunk is named for reading, what the reply holds, and what became of a second function of version 1 that described what the program offers. It matters because a summary and a section of the code overview have no file, so without this command their text could not be read at all.

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: naming the chunk to read, a name that fits several chunks, the reply, lines around a symbol, what the program says it offers.

Not covered: finding chunks ([MYC-4](04-retrieval.md)); how chunks are split and named ([MYC-1](01-corpora-and-ingest.md)); summaries and the code overview themselves ([MYC-8](08-summaries.md), [MYC-9](09-code-overview.md)).

## Behaviour

### Naming the chunk

Observed in version 1: a function took a file's path and the name of a symbol and returned that symbol's source. It looked among the code chunks of the file for one whose name was the symbol, or ended with it after a `#` or a `.`. Exactly one had to fit, an exact name winning. When several fitted it returned up to 20 of them as candidates. It read code only, and nothing called it: neither a command nor another part of the program.

Proposed: a command, `mycel read`, for any symbol or section that is on disk, and for any summary or section of the code overview, which have no file. The chunk is named in one of two ways:

| Named by | Example |
|---|---|
| Its place, in the form of a Source Ref (MYC-2, MYC-16) | `cellar:@code/src/net/retry.py#RetryPolicy.allow`, `cellar:@artifact/docs/net.md#Retry%20policy`, `handbook:@index/summaries#1%2F7`, `cellar:@index/overview#src%2Fnet` |
| Its identifier, as a search result gives it | `--id 01JB2M…` |

A place is parsed and resolved by [MYC-16](16-source-addresses-and-evidence.md#portable-addresses), including its root-qualified grammar, percent escaping and legacy literal aliases. Markdown under either configured root is read as a document. File-backed candidates and replies identify their actual root, relative path and canonical copyable address; a bare path fitting different physical files is refused as ambiguous, even if only one has the requested heading. The identifier from search selects the exact chunk without guessing a root. Index-only text uses `@index`; a colliding real file cannot be mistaken for a summary or overview. Two shorter forms are accepted, as in version 1 and in MYC-2.5: a method without its class (`retry.py#allow`), and a section by its unique bare title. A class's name gives the chunk of the class's header; each method is a chunk of its own.

Exactly one chunk must fit. When several fit, the command is refused with `invalid_input` and names up to 20 of them. When none fits, it is refused with `invalid_input` too. A repository that is switched off refuses it with `refused`, and one the settings do not name with `unknown_repository`.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/retrieval.py#symbol_read`

### The reply

Observed in version 1: the function read the file and returned the lines the index had stored for the chunk, with two more lines on each side, or up to 50 when asked. The reply said where the definition began and ended and whether the text had been cut at 5 MiB. Because it took the lines from the file by stored numbers, a file changed since the last pass gave the wrong lines (inferred from the source, not seen happening).

Proposed: the reply holds the chunk's whole text as the index has it for the version on disk. The index keeps the complete text of every version (MYC-3), so the same command reads a chunk that has no file. Before it reads, the command checks and ingests changes by MYC-4.18: its repository and the enabled repositories of its explicit upstream dependencies, recursively, under one existing time limit and with the same option to turn the entire check off. A source that is only needed for dependency checking does not become another returned chunk. When the check cannot finish, the command reads the index as it is and reports the pending work; it does not claim that unchecked text and sources match the disk.

The reply also says what a search result says about the chunk: its origin and kind, its lines, whether it is stale or Heartwood, every stale reason naming the original source and intermediate dependency path, whether its dependency check completed and any ref faults, and the file when there is one. It reports each required repository's completion or pending state using MYC-4's `RepositoryCheck`. An absent stale mark with an incomplete dependency check is not presented as verified current. This check does not rewrite the chunk, renew its pinned sources or verify its claims.

Since [MYC-D39](02-provenance-and-freshness.md#decisions), decided on 15 October 2026, the reply also lists every document section that describes the chunk, by a direct declared or asserted dependency in either direction, with the direction and the kind of edge ([MYC-2](02-provenance-and-freshness.md#which-documents-describe-a-chunk)). The list is complete, does not depend on embeddings, and is empty when no document describes the chunk.

Since 19 October 2026 a requirement or decision is a chunk of its own ([MYC-17](17-justification.md#requirements-and-decisions-are-entities)), named by its Entity URI, by its full address or by its human id within its file. The reply of such a chunk carries its `entity` fields: the kind, the UUID, the human id, the URI, the title, the status and the metadata of the row. For a decision it also carries the discussion: the content of each chat its Discussion cell names, read as data from the Arbol database that the `[discussions]` settings of [MYC-5](05-settings.md#the-keys) name, or `available: false` with the reason when the settings name none or it cannot be reached; the read succeeds either way and writes nothing there ([MYC-D48](17-justification.md#decisions)).

For a symbol of a code file that can be read, `--context` adds up to 50 lines before and after, taken from the file. Without the option there are none.

A text of more than 5 MiB is cut there, and the reply says so.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/retrieval.py#symbol_read`
- `mycel_deprecated_v1:mycel/retrieval.py#_read_location`

### What the program offers

Observed in version 1: a second function described the engine to a caller: the version of its protocol, the version of each reply, the names of its operations, and whether an index with vectors existed. Nothing called it.

Proposed: no command of its own. `mycel info` ([MYC-0](00-overview-and-legacy-map.md#the-command-line)) is that description. It already names the Build, the version of the search reply, the store and the embedding model. It gains the list of commands of the Build that runs and the version of the read reply. Whether a repository has chunks and vectors is said by `mycel status` (MYC-1.26).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/retrieval.py#capabilities`

## Requirements

| ID | Mycel must… | From v1 | Verified by |
|---|---|---|---|
| MYC-11.1 <!-- 453d6ce4-c11d-4c49-b630-c049c14b33f2 --> | return on request the whole text of one chunk: a symbol or a section that is on disk, a summary, or a section of the code overview | Changed | store |
| MYC-11.2 <!-- d71d1ff3-5017-44cd-88ef-8462151c8890 --> | accept the chunk by its place in the form of a Source Ref, or by the identifier a search result gave | Changed | unit |
| MYC-11.3 <!-- e84e262f-1b39-4fd6-9e7c-3cf1dff7f747 --> | match a place as written, and also accept a method without its class and a section by its bare title | Kept | store |
| MYC-11.4 <!-- ecf46433-def5-4353-aeee-5883ade80393 --> | refuse the command with `invalid_input` when no chunk fits or several do, naming up to 20 of those that fit; with `refused` for a repository that is switched off; and with `unknown_repository` for one the settings do not name | Kept | store |
| MYC-11.5 <!-- a1757601-5e4b-40b8-8bb4-9e950fd1e571 --> | take the text from the index, as stored for the version on disk, so that a chunk without a file can be read | Changed | store |
| MYC-11.6 <!-- fab708ca-a11d-4000-87c4-08aff2d04771 --> | before reading check and ingest changes in its repository and recursively in the enabled repositories of its explicit upstream sources under the one time limit of MYC-4.18 and MYC-4.19, unless the caller turns the entire check off; report what completed and every pending repository without returning dependency chunks | New | store |
| MYC-11.7 <!-- a3dc39bf-a7b5-411f-8fca-eb6e773caa84 --> | say in the reply the chunk's origin, actual root and relative path when file-backed, kind and lines, stale and Heartwood marks, source/path reasons, dependency-check completion and ref faults, and readable file; preserve document origin for checkout Markdown and never present an unchecked chunk as verified current | Changed | unit |
| MYC-11.8 <!-- a65e415e-dd4a-4ae8-bd6c-9c941777ffb0 --> | add, on request, up to 50 lines before and after a symbol from its file, and none without the request | Changed | unit |
| MYC-11.9 <!-- 90101f82-9341-43d2-846e-de1d6fe4d19a --> | cut a text of more than 5 MiB there and say so | Kept | unit |
| MYC-11.10 <!-- 831eb46e-4d4c-4137-a2b2-cea83b427f1b --> | name in `mycel info` the commands of the Build that runs and the version of the read reply, and have no other command that describes the program | Changed | unit |
| MYC-11.11 <!-- f0254d36-30c0-4e43-8f9b-e227ca30ae1e --> | accept MYC-16 qualified code/artifact/index addresses and legacy unambiguous aliases through the central resolver, return a canonical qualified address, and identify root-aware ambiguity candidates without silently choosing a file or index namespace | New | store |
| MYC-11.12 <!-- 11271647-a7a1-4931-8a06-937e3d2364e6 --> | list in the reply every document section that describes the chunk by a direct declared or asserted dependency in either direction, with its direction and kind, complete and independent of embeddings, and an empty list when there is none | New | store |
| MYC-11.13 <!-- 48054dd7-8c50-41c4-8719-afd270182640 --> | read a requirement or decision chunk by its Entity URI, its full address or its human id within its file, carry its entity fields in the reply, and for a decision show the chats of its Discussion cell from the configured Arbol database or `available: false` with the reason, succeeding either way and writing nothing there | New | store |

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

```sh
mycel read 'cellar:src/net/retry.py#RetryPolicy.allow'
mycel read 'cellar:src/net/retry.py#allow' --context 5   # a method without its class, with five lines around it
mycel read 'cellar:docs/net.md#Retry policy'
mycel read 'handbook:summaries#1/7'                      # a summary: it has no file
mycel read 'cellar:@code/README.md#Setup'               # explicit checkout document
mycel read 'cellar:@artifact/README.md#Setup'           # a distinct artifact document
mycel read 'handbook:@index/summaries#1%2F7'            # explicit index-only summary
mycel read --id 01JB2M0000000000000000000A --no-fresh    # by identifier, without the freshness check
mycel read '[dec:0f2c1b4e-8a9d-4c3e-9b7a-1d2e3f4a5b6c:V2hpY2ggbGFuZ3VhZ2U]'   # a decision by its Entity URI, with its discussion (MYC-17)
```

```ts
interface ReadReply {
  schema: number;                      // the version of this reply; the first one is 1
  id: string;
  repository: string;
  origin: "code" | "document" | "summary" | "overview";
  root: "code" | "artifact" | "index"; // actual binding or generated index-only namespace
  path: string;                        // relative to that root; synthetic for summary/overview
  address: string;                     // MYC-16 canonical qualified place
  name: string;
  kind?: string;
  lines?: { start: number; end: number };
  text: string;                        // the whole chunk, as stored for the version on disk
  cut: boolean;                        // true when the text was cut at 5 MiB
  context?: { before: string; after: string };     // only with --context
  stale: boolean;
  staleReasons: StaleReason[];          // MYC-2
  dependencyCheck: DependencyCheck;     // MYC-4
  heartwood: boolean;
  documents: DocumentLink[];            // MYC-D39 (MYC-2): every document section that describes this chunk; empty when none
  entity?: EntityFields;                // MYC-17: a chunk of kind req or dec, with its discussion for a decision
  file?: string;                       // absolute path, when the chunk has a file that can be read
  unreadable?: string;                 // the reason, when there is no file
  freshness: {
    checked: boolean;
    finished: boolean;
    ingested: number;
    repositories: RepositoryCheck[];   // MYC-4: completion or pending state for each required repository
  };
}

// A refusal because several chunks fit:
//   { error: { code: "invalid_input", message }, candidates: Place[] }
//
// MycelInfo of MYC-0 gains:
//   commands: string[];               // the commands of the Build that runs
//   readReply: number;                // the version of the read reply
```

## Known problems in version 1

- **Nothing could call it.** The function that reads a symbol had no command and no caller. The same holds for the function that describes the engine.
- **It read code only.** A section of a document had to be read from its file, and a summary could not be read at all: a search result for one named no file.
- **The lines could be the wrong ones.** They were taken from the file by the line numbers of the last pass (inferred from the source, not seen happening).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/retrieval.py#symbol_read`
- `mycel_deprecated_v1:mycel/retrieval.py#capabilities`
- `mycel_deprecated_v1:mycel/retrieval.py#_read_location`

## Decisions

No question of this specification's own is open. MYC-D39 of [MYC-2](02-provenance-and-freshness.md#decisions), decided on 15 October 2026, adds the documents that describe a chunk to the reply.

## Named checks

Written by `scripts/name_checks.py` from the `proven` and `stated` Origin Links of the tests and a complete check report in which they passed. Each requirement keeps its kind in its Verified by cell and names here up to three of its passing checks: those of its own kind first, then those that rest on the fewest requirements. `mycel origins --repo mycel --path tests` lists every link. Do not edit this section by hand: run the script again.

| Requirement | Kind | Checks |
|---|---|---|
| `MYC-11.1` | store | `test_read_store.ReadStoreTests.test_disk_selection_excludes_branch_and_stash_and_current_exact_bytes_override_text_projection`, `test_read_store.ReadStoreTests.test_whole_retained_code_document_summary_and_overview_text_need_no_vector_or_file`, `test_read_store.ReadFreshnessStoreTests.test_fresh_read_ingests_changed_exact_text_and_new_qualified_file_before_final_selection` and 2 more |
| `MYC-11.2` | unit | `test_read.ReadTests.test_identifier_and_qualified_alias_use_the_actual_primary_binding`, `test_read.ReadTests.test_qualified_and_legacy_places_and_result_identifier_select_one_exact_chunk`, `test_read_cli.ReadCliTests.test_cli_keeps_a_source_ref_or_identifier_context_and_skipped_check_explicit` |
| `MYC-11.3` | store | `test_read_store.ReadStoreTests.test_exact_name_wins_and_unique_bare_method_heading_and_class_header_match`, `test_read_store.ReadFreshnessStoreTests.test_fresh_discovery_refuses_a_new_duplicate_bare_heading_instead_of_the_old_unique_match` |
| `MYC-11.4` | store | `test_read_store.ReadStoreTests.test_missing_ambiguous_disabled_and_unknown_reads_use_the_closed_refusals`, `test_read_store.ReadFreshnessStoreTests.test_fresh_discovery_refuses_a_new_duplicate_bare_heading_instead_of_the_old_unique_match`, `test_read_store.ReadFreshnessStoreTests.test_fresh_discovery_refuses_a_new_physical_root_collision_before_an_old_heading_can_win` and 2 more |
| `MYC-11.5` | store | `test_read_store.ReadStoreTests.test_disk_selection_excludes_branch_and_stash_and_current_exact_bytes_override_text_projection`, `test_read_store.ReadStoreTests.test_shared_exact_chunk_version_reports_only_faults_owned_by_its_current_disk_location`, `test_read_store.ReadStoreTests.test_whole_retained_code_document_summary_and_overview_text_need_no_vector_or_file` and 3 more |
| `MYC-11.6` | store | `test_read_generated_store.GeneratedReadStoreTests.test_upper_summary_checks_generated_members_and_transitive_external_sources_without_regeneration`, `test_read_store.ReadFreshnessStoreTests.test_busy_upstream_keeps_committed_text_and_a_visible_incomplete_dependency_check`, `test_read_store.ReadFreshnessStoreTests.test_expired_one_deadline_reads_committed_index_and_lists_pending_work` and 5 more |
| `MYC-11.7` | unit | `test_read.ReadTests.test_original_source_and_intermediate_paths_faults_and_heartwood_survive_reply`, `test_read.ReadTests.test_pending_source_or_ref_fault_cannot_make_an_unmarked_chunk_verified_current`, `test_read.ReadTests.test_reply_keeps_checkout_markdown_document_origin_exact_lines_and_canonical_root` and 1 more |
| `MYC-11.8` | unit | `test_read.ReadTests.test_context_comes_from_the_file_while_the_chunk_text_stays_exactly_indexed`, `test_read.ReadTests.test_context_stops_at_file_boundaries`, `test_read.ReadTests.test_context_does_not_read_a_symlink_that_escapes_the_selected_configured_root` |
| `MYC-11.9` | unit | `test_read.ReadTests.test_five_mib_cut_is_measured_in_utf8_bytes_without_a_partial_character` |
| `MYC-11.10` | unit | `test_read_cli.ReadCliTests.test_info_names_the_running_build_commands_and_read_reply_without_a_capabilities_command` |
| `MYC-11.11` | store | `test_read_store.ReadStoreTests.test_qualified_roots_percent_names_index_collisions_and_aliases_never_guess_a_file`, `test_read_store.ReadFreshnessStoreTests.test_fresh_discovery_refuses_a_new_physical_root_collision_before_an_old_heading_can_win` |
| `MYC-11.12` | store | `test_document_links.DocumentLinksStoreTests.test_actual_declared_whole_file_and_class_family_describe_each_selected_code_chunk`, `test_document_links.DocumentLinksStoreTests.test_current_anchored_versions_replace_old_pins_and_stale_marks_do_not_hide_links`, `test_document_links.DocumentLinksStoreTests.test_read_lists_both_directions_and_edge_kinds_completely_without_vectors` and 1 more |
| `MYC-11.13` | store | `test_entities.EntityStoreTests.test_read_by_entity_uri_address_and_human_id_with_the_kind_tag_as_a_check` |
