---
role: authored
spec: MYC-12
status: implemented
---
# Mycel · 12 The record of work

Mycel runs for a moment and ends. What it did in that moment, which files a pass read, which chunks it took for renamed, how many parts an embed sent and how it ended, is gone unless it is written down. This specification fixes what Mycel records about its own work, when it records it, how long the record is kept and how it is read. It matters because version 1 kept three such records: a feed whose filter by repository hid every pass and every embed, and two logs that no code ever read.

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: which invocations leave an entry, what an entry holds, the identity decisions of a pass, an invocation that was cut short, how long entries are kept, reading the record.

Not covered: how a chunk is recognised again ([MYC-1](01-corpora-and-ingest.md#identity)); what the numbers of a command mean, which its own specification says; the locks that tell whether an invocation still runs ([MYC-6](06-index-store.md#two-invocations-at-once)).

## Behaviour

### Which invocations leave an entry

Observed in version 1: a feed held one row for a pass, an embed and a run of the summariser. A pass was meant to leave a row only when it had done something. The rule did not hold: a pass counted as having done something whenever any chunk in the index was stale, and each stale chunk of the repository was listed in the row again.

Proposed: an invocation that changes the store leaves one entry for each repository it worked on.

| Invocation | Kind of entry |
|---|---|
| `mycel ingest`; the check and ingest of changes before a search or read, when it changed files, dependency records or stale marks | `ingest` |
| `mycel embed` | `embed` |
| `mycel derive`, `mycel relate`, with or without `--remove` | `derive`, `relate` |
| `mycel confirm` | `confirm` |
| `mycel classify`, when it claims work, records a result or changes Drift work state | `classify` |
| `mycel summaries build`, `regenerate`, `remove` | `summaries_build`, `summaries_regenerate`, `summaries_remove` |
| `mycel repos remove` | `remove`, which belongs to no repository and names the removed one among its numbers |
| `mycel init`, when it changed the structure | `init`, which belongs to no repository |

Nothing else leaves one: not a command that only reports (MYC-1.28), not a dry-run, evaluation or `mycel grep`, and not a pass or a dependency check that found nothing to change. Mechanical eligibility/pending changes made during ingest/search/read belong to its `ingest` entry; only explicit `classify` records classification attempts and spends Jev/reviewer calls (MYC-14). An identical assertion, empty embed or removal, or classification with no eligible work leaves no entry. A search or read adds an entry for each repository whose files, dependency records or stale marks its check changed, including a dependant whose own text was unchanged. A check that only read files adds no entry. Each entry is part of the permitted writes of MYC-4.21 and obeys the repository locks of MYC-6.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#log_activity`
- `mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#embed_pending`

### What an entry holds

Observed in version 1: a row held a time, a kind, a repository, a summary of numbers, a duration and an error text. Rows of passes and embeds named no repository. Some numbers were not what their names said: the two that were named for documents counted chunks, and the number of stale chunks was that of the whole index, added once for each repository of the pass.

Proposed:

| An entry says | Detail |
|---|---|
| What ran, and for which repository | The kind, and always the repository, except for `init` and `remove` |
| What started it | A command, or the check and ingest of changes before a search or read |
| Which Build | Its Mycel build number ([MYC-15](15-distribution-and-replacement.md)) |
| When | The time it began and the time it ended |
| How it ended | `done`, `refused`, `failed` or `stopped`, with the error code and message when it was not `done` |
| What it did | The numbers of the command's own reply for that repository, under the same names and with the same meaning |
| For an `ingest`: the files | Each file that was added, changed or removed, with the location it was read in |

An entry caused only by dependency-state changes has no changed files or identity decisions. It still names the affected repository and the search, read or ingest that caused those changes. This is an audit of the changes; checking dependencies, matching chunks, scoring search results and deciding staleness use the current index state, not older activity entries. The existing use of an open entry to identify unfinished work remains as specified below.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#log_activity`
- `mycel_deprecated_v1:mycel/knowledge/store.py#refresh`

### Identity decisions

Observed in version 1: when a document was reconciled, each decision about one of its chunks was written to a log: unchanged, edited, renamed, new or gone, with the old and the new name. No decision about a code chunk was logged. Nothing read the log. A second log held one row for every ingest of documents, with its numbers; nothing read that either.

Proposed: a pass records every decision about identity for every chunk of every file it applies, documents and code alike (MYC-1.20). A decision belongs to the entry of its pass and is written in the same transaction as the file it is about (MYC-1.22), so the record and the chunks cannot disagree. Decisions are read with their entry.

In the fictional file of [MYC-1](01-corpora-and-ingest.md#splitting-code), a pass that finds the function `expire` renamed to `lapse` with the same body records one decision: `renamed`, from `expire` to `lapse`.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code`

### An invocation that was cut short

Observed in version 1: a row was written when the work was over. A process that was killed left none. An error while writing a row was swallowed, so a missing row could also mean that the feed itself had failed.

Proposed: an entry is opened with the first change an invocation makes and closed when it ends. Each entry records the identity of the exact invocation and its store connection. Running-entry protection and `unfinished` detection use that invocation's liveness, not whether some other invocation holds a repository lock. Before the first write, the invocation obtains a collision-free positive 64-bit liveness key from a store sequence in the dedicated invocation-lock namespace and holds a session-owned PostgreSQL advisory lock on that key until it ends. The entry retains the invocation UUID, that key and the exact server session identity (backend PID plus backend start time). A read checks that key is still owned by that exact session; a recycled PID, another invocation or an ordinary repository lock cannot supply liveness. Closing releases the liveness lock after the final entry transaction; loss of the owning session makes an open entry unfinished. These locks require no daemon, lease timer or background reaper. An entry left open after its own invocation ends is shown with the outcome `unfinished`. What that invocation had applied up to then stays applied, file by file (MYC-1.22), and its decisions are in the entry.

An entry that cannot be written is a failure of the command, with `internal`. It is not passed over.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#log_activity`

### How long entries are kept

Observed in version 1: nothing was ever removed from the feed or the logs.

Chosen under [MYC-D34](#decisions): the newest 1,000 entries of each repository are kept. Entries belonging to no repository form a separate group with its own limit of 1,000. The owner delegated the size to the agent, who chose the former proposed limit; it is a starting policy, not a measured capacity requirement.

Opening or closing an entry prunes entries beyond its group's limit, together with their attached file lists, identity decisions and other details. An entry belonging to an invocation that is still running is protected until that invocation ends; protected entries may temporarily take the group above 1,000. An unfinished entry whose invocation no longer runs is subject to normal retention. `mycel repos remove` deletes the entries of the repository with its other rows (MYC-1.27), under the existing repository locks. Its own entry, of the kind `remove`, belongs to no repository, and the name of the removed one is among its numbers.

### Reading the record

Observed in version 1: `mycel activity` printed the newest rows, 25 unless told otherwise and at most 500, and could filter by kind and by repository. The filter by repository compared with a column that the rows of passes and embeds left empty, so it hid them.

Proposed: the same command. It lists the entries of one repository, newest first by start time then ID, or all entries including global `init`/`remove` entries with `--all`. Given the identifier of an entry, it prints that entry with its files and decisions. `--entry` is exclusive with repository, kind and count filters. An unknown or pruned entry returns `refused`; an empty list succeeds. A nonpositive or malformed `--k`, or unknown kind, is `invalid_input`; values over 500 are capped. Listing is read-only: it computes `unfinished` without rewriting rows or pruning history. File and decision details sort by root, path, location, then chunk name; root distinguishes equal paths in different corpora.

A `classify` entry copies the repository portion of `ClassifyReply` (MYC-14), including selected/completed/needsReview/errors/obsolete and Jev/reviewer call counts, with exact model/question/routing identities and reported usage available through its classification bundle details. Its details point to retained classification bundle identifiers and judgement/failure summaries. It does not duplicate prompt text, secrets or full evidence in activity; evidence lifetime belongs to MYC-16 and is independent of activity pruning.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#list_activity`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_activity`

## Requirements

| ID | Mycel must… | From v1 | Verified by |
|---|---|---|---|
| MYC-12.1 <!-- 42eeaf60-c21e-49ef-9f8c-5162740f7528 --> | leave one entry of a kind in the table above for each repository whose store state an invocation changed, including downstream dependency records or stale marks changed by a search, read or ingest even when no file changed there | Changed | store |
| MYC-12.2 <!-- 85d3213e-16e6-42a8-b716-8a6618fe81e0 --> | leave no entry for a command that only reports, for `mycel grep`, or for a pass or dependency check that changed nothing | Changed | store |
| MYC-12.3 <!-- 01d85468-63d8-4ee6-8b94-dc836039ac78 --> | name in every entry its repository, except for `init` and `remove`, what started it, the Build, the times it began and ended, and how it ended, with the error when it did not end as `done` | Changed | store |
| MYC-12.4 <!-- 1f7db0c1-a4e6-457f-8cbf-9e2945c37aa1 --> | give in an entry the numbers of the command's own reply for that repository, under the same names and with the same meaning | Changed | store |
| MYC-12.5 <!-- dc79d1ce-acef-4c0a-ac06-9a464374f07c --> | record for an `ingest` each file that was added, changed or removed, with the location it was read in | Kept | store |
| MYC-12.6 <!-- 8f3db1b4-cfab-4eea-871b-4a1e6fcbbe1e --> | record every identity decision of a pass with its entry, for documents and code alike, in the same transaction as the file it is about | Changed | store |
| MYC-12.7 <!-- b784d8dd-5549-4e18-ad97-38be8dd62a7d --> | open an entry with the first change of an invocation and close it at the end; bind it to that exact invocation and store connection, and show it as `unfinished` when left open after its own invocation ends; another invocation's repository lock grants no running-entry protection | New | store |
| MYC-12.8 <!-- bcca48dc-74a9-4bcc-9bd1-5687d748940e --> | fail the command with `internal` when an entry cannot be written | Changed | store |
| MYC-12.9 <!-- ddc7f204-f668-4052-8452-604a321aac75 --> | keep the newest 1,000 entries of each repository and a separate newest 1,000 for entries belonging to no repository; prune older entries with all attached files, identity decisions and other details when an entry opens or closes, protecting currently running entries until their invocations end even if the limit is temporarily exceeded | New | store |
| MYC-12.10 <!-- d4224a89-0aeb-48d5-a1a4-d83d5ce49090 --> | delete the entries of a repository on `repos remove`, and record the removal in an entry that belongs to no repository | New | store |
| MYC-12.11 <!-- 085bc3e3-3bf0-4d3e-a873-209fddf5516a --> | list entries on request, newest first, for one repository or for all, optionally of one kind, 25 unless another number is asked for, a number above 500 being taken as 500 | Kept | store |
| MYC-12.12 <!-- 7fb261af-3e99-4844-ab0d-0251bb9d4eb3 --> | print on request one entry with its files and its identity decisions | New | store |
| MYC-12.13 <!-- 2c9ee640-44b6-44b5-a73f-ef517d5c8611 --> | record explicit classification as `classify`, audit mechanical eligibility changes under ingest, and leave no activity for read-only evaluation, dry-runs or no-op assertions | New | store |
| MYC-12.14 <!-- 087f7e41-fb14-479e-8f72-96e3b38f43b3 --> | identify exact invocation liveness with a collision-free session-owned advisory key plus session identity, and compute unfinished status read-only without using another invocation's lock | New | store |
| MYC-12.15 <!-- 1894f8e6-4642-419d-9b50-72137346dd2b --> | return root-qualified ordered file/decision details and classification bundle references, validate activity filters, and distinguish empty lists from missing/pruned entries | New | store |

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

```sh
mycel activity --repo cellar                 # the newest 25 entries of one repository
mycel activity --all --kind embed --k 100    # the newest 100 embeds of every repository
mycel activity --entry 01JB2M0000000000000000000B   # one entry with its files and decisions
```

```ts
interface ActivityReply { entries: ActivityEntry[] }

interface ActivityEntry {
  id: string;
  kind: "ingest" | "embed" | "derive" | "relate" | "confirm" | "remove" | "init"
      | "summaries_build" | "summaries_regenerate" | "summaries_remove" | "classify";
  repository?: string;                 // absent for "init" and "remove"
  invocation: string;                 // UUID shared by this invocation's repository entries
  startedBy: "command" | "freshness_check";
  build: string;                       // MYC-15 build number
  startedAt: string;
  endedAt?: string;                    // absent while it runs, and for an unfinished one
  outcome: "running" | "done" | "refused" | "failed" | "stopped" | "unfinished";
  error?: { code: string; message: string };
  counts: Record<string, unknown>;     // the entry of this repository in the command's own reply
}

interface ActivityDetail extends ActivityEntry {
  files: Array<{ root: "code" | "artifact"; path: string; change: "added" | "changed" | "removed"; location: string }>;
  decisions: Array<{
    root: "code" | "artifact";
    path: string;
    location: string;                  // "disk", a branch, or the commit of a stash
    decision: "unchanged" | "edited" | "renamed" | "new" | "removed";
    name: string;                      // the chunk's name after the pass
    previousName?: string;             // for "renamed"
  }>;
  classifications: Array<{
    bundle: string;
    dependant: Place;
    outcome: string;                   // MYC-14 judgement, failure or obsolete result
  }>;                                 // empty for other entry kinds
}
```

## Known problems in version 1

- **The filter by repository hid the main rows.** Passes and embeds were recorded without a repository.
- **Passes that did nothing were recorded as long as anything was stale.** Every stale chunk of the repository was written into the row of every such pass.
- **Numbers did not mean what their names said.** Two that were named for documents counted chunks. The number of stale chunks was that of the whole index, added up once per repository.
- **Two logs were written and never read:** the identity decisions for documents and a row for every ingest of documents.
- **Decisions about code were not recorded at all.**
- **A failing feed looked like a quiet one.** An error while writing a row was swallowed.
- **A pass that was killed left no trace** (inferred from the source, not seen happening).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/store.py#log_activity`
- `mycel_deprecated_v1:mycel/knowledge/store.py#list_activity`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ingest_code`
- `mycel_deprecated_v1:mycel/syncpass.py#_run_pass_locked`
- `mycel_deprecated_v1:mycel/cli.py#_cmd_activity`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D34 <!-- f2e43dd4-1fec-45c0-83c5-d82105a921b4 --> | How long is the record of work kept? | The newest 1,000 entries of each repository, with their files and decisions; older ones are deleted as new ones are written. Version 1 never removed a row. A pass after a large change records a decision for every chunk it touched, so a record without a limit would grow without end. The 1,000 are a first value and not a measured one | Decided 8 October 2026 by the owner: delegate the size of the history to the agent. Chosen: newest 1,000 entries per repository, plus a separate newest 1,000 for entries belonging to no repository; delete all attached details with each pruned entry, and protect currently running entries until their invocations end. The chosen limit is not a measured one |

Decided on 15 October 2026 by the owner: an unknown or pruned activity entry returns `refused`, using the existing error vocabulary of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

## Named checks

Written by `scripts/name_checks.py` from the `proven` and `stated` Origin Links of the tests and a complete check report in which they passed. Each requirement keeps its kind in its Verified by cell and names here up to three of its passing checks: those of its own kind first, then those that rest on the fewest requirements. `mycel origins --repo mycel --path tests` lists every link. Do not edit this section by hand: run the script again.

| Requirement | Kind | Checks |
|---|---|---|
| `MYC-12.1` | store | `test_activity_store.ActivityDeclaredRefStoreTests.test_settings_only_reference_fault_changes_audit_each_unchanged_owner`, `test_activity_store.ActivityStoreTests.test_global_init_remove_and_noop_reports_leave_only_applied_entries`, `test_check_real.RealActivityCheckStoreTests.test_profile_measures_the_real_numbered_subprocess_without_changing_its_reply` and 9 more |
| `MYC-12.2` | store | `test_activity_store.ActivityDeclaredRefStoreTests.test_repeated_reference_passes_use_producer_cumulative_and_final_noop_counts`, `test_init_activity.InitActivityStoreTests.test_actual_compatible_init_is_noop_and_dimensions_audit_uses_its_reply`, `test_activity_store.ActivityStoreTests.test_global_init_remove_and_noop_reports_leave_only_applied_entries` and 6 more |
| `MYC-12.3` | store | `test_recovery.RecoveryStoreTests.test_a_pair_in_error_keeps_the_step_reply_and_closes_its_activity_failed`, `test_activity_store.ActivityStoreTests.test_cancellation_closes_applied_work_before_releasing_liveness`, `test_activity_completion.ActivityCompletionStoreTests.test_refusal_closes_applied_prefix_with_command_error_and_exact_counts` and 5 more |
| `MYC-12.4` | store | `test_activity_store.ActivityDeclaredRefStoreTests.test_repeated_reference_passes_use_producer_cumulative_and_final_noop_counts`, `test_activity_store.ActivityDeclaredRefStoreTests.test_settings_only_reference_fault_changes_audit_each_unchanged_owner`, `test_activity_store.ActivityStoreTests.test_classify_bundle_references_counts_and_mechanical_ingest_are_separate` and 23 more |
| `MYC-12.5` | store | `test_activity_completion.ActivityCompletionStoreTests.test_added_changed_removed_files_and_all_identity_decisions_keep_exact_locations`, `test_activity_store.ActivityStoreTests.test_file_and_all_code_document_decisions_rollback_with_the_file_and_retry`, `test_ingest_activity.PublicIngestActivityStoreTests.test_public_ingest_history_and_detail_match_exact_reply_and_quiet_pass_is_silent` |
| `MYC-12.6` | store | `test_activity_completion.ActivityCompletionStoreTests.test_added_changed_removed_files_and_all_identity_decisions_keep_exact_locations`, `test_activity_store.ActivityStoreTests.test_file_and_all_code_document_decisions_rollback_with_the_file_and_retry`, `test_activity_store.ActivityStoreTests.test_later_file_failure_retains_only_applied_prefix_and_sanitized_failure` and 3 more |
| `MYC-12.7` | store | `test_activity_completion.ActivityCompletionStoreTests.test_running_and_unfinished_diagnostics_execute_read_only_without_changing_rows`, `test_activity_store.ActivityDeclaredRefStoreTests.test_real_reference_writes_rollback_on_native_audit_insert_failure`, `test_activity_store.ActivityStoreTests.test_caller_transaction_requires_own_guarded_live_connection` and 16 more |
| `MYC-12.8` | store | `test_activity_store.ActivityStoreTests.test_audit_insert_detail_and_close_failures_are_internal_and_atomic`, `test_init_activity.InitActivityStoreTests.test_bad_packaged_identity_refuses_before_schema_change_and_bootstrap_requires_guard`, `test_init_activity.InitActivityStoreTests.test_missing_installed_identity_cannot_silently_initialize_without_audit` and 20 more |
| `MYC-12.9` | store | `test_activity_retention.ActivityRetentionStoreTests.test_actual_numbered_initialization_prunes_global_history_atomically_with_dimension_change`, `test_activity_retention.ActivityRetentionStoreTests.test_concurrent_group_writers_refuse_without_partial_feature_or_prune_then_retry`, `test_activity_retention.ActivityRetentionStoreTests.test_group_guards_remain_compatible_with_peer_fk_key_share_and_other_groups` and 6 more |
| `MYC-12.10` | store | `test_activity_retention.ActivityRetentionStoreTests.test_numbered_repository_removal_deletes_its_history_and_retains_foreign_evidence_and_global_limit` |
| `MYC-12.11` | store | `test_activity_history.ActivityHistoryStoreTests.test_default_cap_all_kinds_and_repository_cwd_selection_use_exact_start_time_id_order`, `test_activity_history.ActivityHistoryStoreTests.test_public_cli_lists_all_or_named_and_returns_one_detail_without_mutation`, `test_activity_history.ActivityHistoryStoreTests.test_running_unfinished_and_over_limit_reads_never_prune_or_write_tables_or_sequences` and 1 more |
| `MYC-12.12` | store | `test_activity_history.ActivityHistoryStoreTests.test_complete_entry_details_keep_root_collisions_names_classification_references_and_build_identity`, `test_activity_history.ActivityHistoryStoreTests.test_public_cli_lists_all_or_named_and_returns_one_detail_without_mutation`, `test_activity_history.ActivityHistoryStoreTests.test_running_unfinished_and_over_limit_reads_never_prune_or_write_tables_or_sequences` and 2 more |
| `MYC-12.13` | store | `test_activity_store.ActivityStoreTests.test_classify_bundle_references_counts_and_mechanical_ingest_are_separate`, `test_activity_completion.ActivityCompletionStoreTests.test_classification_references_rollback_with_native_detail_fault_and_keep_only_summaries`, `test_activity_completion.ActivityCompletionStoreTests.test_every_kind_keeps_one_changed_scope_and_exact_complete_final_reply` |
| `MYC-12.14` | store | `test_activity_completion.ActivityCompletionStoreTests.test_running_and_unfinished_diagnostics_execute_read_only_without_changing_rows`, `test_activity_store.ActivityStoreTests.test_caller_transaction_requires_own_guarded_live_connection`, `test_activity_store.ActivityStoreTests.test_exact_session_loss_and_recycled_pid_or_other_lock_never_protect_open_work` and 2 more |
| `MYC-12.15` | store | `test_activity_history.ActivityHistoryStoreTests.test_empty_lists_succeed_unknown_or_pruned_entries_refuse_and_invalid_filters_leave_no_writes`, `test_activity_history.ActivityHistoryStoreTests.test_complete_entry_details_keep_root_collisions_names_classification_references_and_build_identity`, `test_activity_history.ActivityHistoryStoreTests.test_default_cap_all_kinds_and_repository_cwd_selection_use_exact_start_time_id_order` and 2 more |
