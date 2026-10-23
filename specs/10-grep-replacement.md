---
role: authored
spec: MYC-10
status: implemented
---
# Mycel · 10 The grep replacement

Agents and people reach for grep by habit. `mycel grep` is grep with one addition: it runs the system's grep exactly as it was asked, and then adds a few lines that name code and documents which are about the same words without containing them. This specification fixes how grep is run, when the added lines appear and what they hold, and where this command departs from the rules of every other Mycel command. It matters because version 1 guessed the search words from the arguments and guessed wrong for common forms, wrote its added lines into output that scripts were counting, and ran one fixed copy of grep.

The Glossary has it under [better-grep](../../arbol/GLOSSARY.md#better-grep).

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: running grep, finding the pattern among the arguments, the tail and when it is left out, the departures from the command-line rules, the name the command is started under.

Not covered: the search behind the tail ([MYC-4](04-retrieval.md)); which research tool fits which question, which the guides of this corpus say.

## Behaviour

### Running grep

Observed in version 1: the program started `/usr/bin/grep`, a fixed path, with the arguments it was given and with its own standard input, output and error. Its exit status was grep's. In one case it changed the arguments: with no path, a terminal on standard input and one of `-r`, `-R` or `--recursive` standing alone, it added `.`. Three inputs it answered itself: `--help` alone, `--version` alone, and no argument at all.

Proposed: `mycel grep` starts the first `grep` on the search path with exactly the arguments it was given. Standard input, output and error are grep's own, and the exit status is grep's. Nothing is added to the arguments and nothing is taken from them, so `mycel grep --help` shows grep's help. What grep prints is what grep alone would have printed, byte for byte.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/better_grep.py#run`

### Finding the pattern

Observed in version 1: to know what to search for, the program picked the pattern out of grep's arguments by a short rule: skip everything that starts with `-`, skip the argument after one of a list of options, take the first word left. Checked on fictional arguments, the rule misread common forms: `--regexp=needle src` gave the pattern `src`, and `-rA 3 needle src` gave `3`.

Proposed: Mycel reads the arguments the way grep does: it knows which options take a value, a value written onto its option (`-A3`, `--regexp=needle`), short options written together (`-rn`), and `--` as the end of the options. The pattern is the value of the first `-e` or `--regexp`, or else the first argument that is not an option. The arguments after it are the paths. When Mycel meets an option it does not know, it adds no tail. A missing tail does no harm; a tail for the wrong word misleads.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/better_grep.py#_parse`

### The tail

Observed in version 1: after grep ended, the program searched the index for the words of the pattern and printed up to five results on standard output, below grep's lines, in two blocks: results related by meaning, and the documents that cite them. It did so whatever grep had been asked to print, so a count, a list of file names or a quiet check got the tail as well. The environment variable `BETTER_GREP_PLAIN` switched it off. A pattern in the form of a regular expression lost its signs: `foo.bar` was searched as `foo bar`. When the paths lay in an organization and not in one repository, there was no tail and no word about it.

Proposed: the tail is kept, on standard output, after grep's own output. It is left out whenever it would not help or could not be told apart from what was asked for.

| Case | Tail |
|---|---|
| `MYCEL_GREP_PLAIN=1` is set | None |
| grep ended with a status above 1: grep itself failed | None |
| grep was asked for something other than matching lines: a count, file names only, or a quiet check (`-c`, `-l`, `-L`, `-q` and their long forms) | None |
| The patterns come from a file (`-f`) | None |
| Fewer than three characters are left of the pattern once its signs are taken out | None |
| The paths, or without paths the current directory, belong to no enabled repository, or to an organization | None |
| The search fails: the store cannot be reached, the settings cannot be read | None, and one line on standard error says why. grep's exit status stands |
| Otherwise | Printed |

The search is the one of [MYC-4](04-retrieval.md): documents and code, the shared documents included, five results, and no freshness check, so that grep is slowed by one search and never by a pass. The repository is the one the first path given to grep lies in, or else the one of the current directory (MYC-1.4). A pattern with no sign of a regular expression other than `.` is searched as it was written, so a name such as `session.renew` stays a name. In any other pattern the signs become spaces.

```text
── mycel: related by meaning (not literal matches) ──
  src/auth/session.py#renew  L40-72  ⇐ via docs/auth.md › Renewal
  src/auth/tokens.py#Token.expired  L12-30
── mycel: documented in ──
  docs/auth.md › Renewal  ⚠ stale
```

The first block has one line for each result: its place, its lines when it is code, and the document section that delivered it when there was one. The second block names once each document section that cites one of the results. A stale section and a Heartwood one are marked. Version 1 also printed a score on each line; it is left out, because scores of different kinds of search cannot be compared (MYC-4).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/better_grep.py#run`
- `mycel_deprecated_v1:mycel/better_grep.py#_semantic_query`
- `mycel_deprecated_v1:mycel/cli.py#search_payload`

### Where this command departs from the rules

Every other command follows the [rules of the command line](00-overview-and-legacy-map.md#the-command-line). `mycel grep` exists to behave like grep, so it departs from five of them.

| Rule of MYC-0 | `mycel grep` |
|---|---|
| One JSON document on standard output | grep's output unchanged, then the tail as text |
| A failure is an error object | grep's own messages. A tail that fails is one line on standard error |
| Exit status 0, 1 or 2 with Mycel's meanings | grep's status: 0 a line matched, 1 none did, above 1 grep failed |
| A command is refused when no repository is found | grep runs anywhere. Only the tail is left out |
| The settings and the store must be there | grep runs without them. Only the tail is left out |

One rule holds without exception: the command writes nothing into the store.

### The name

Observed in version 1: the grep replacement was a program of its own, `better-grep`, and also a command of `mycel`. There were four ways into it, and they did not behave alike: the separate program skipped the start-up steps of `mycel`, and one of the others handed its own name to grep as the pattern (inferred from the source, not seen happening).

Decided: one way, `mycel grep` ([MYC-D33](#decisions)). Mycel is one program (MYC-0.1) with one launcher ([MYC-15](15-distribution-and-replacement.md)).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/better_grep.py#main`
- `mycel_deprecated_v1:better_grep_entry.py`
- `mycel_deprecated_v1:mycel/cli.py#main`

## Requirements

| ID | Mycel must… | From v1 | Verified by |
|---|---|---|---|
| MYC-10.1 <!-- d7af356e-4643-48ef-9ca0-16fa5d861dfe --> | start, for `mycel grep`, the first `grep` on the search path with exactly the arguments given, on its own standard input, output and error | Changed | unit |
| MYC-10.2 <!-- a1c3765b-280f-4c34-9764-01930197a463 --> | end with grep's exit status, whatever happens to the tail | Kept | unit |
| MYC-10.3 <!-- 58b30731-a279-4aae-ad31-ef37b9462693 --> | add nothing to grep's arguments and take nothing from them | Changed | unit |
| MYC-10.4 <!-- 193c5f93-cdb7-4cbd-ba23-505825fd21d5 --> | find the pattern and the paths by grep's own rules for options: options with a value, a value written onto its option, short options written together, and `--` | Changed | unit |
| MYC-10.5 <!-- 6d08e90d-8654-4961-842c-15c0f83423f9 --> | print no tail when it meets an option it does not know | New | unit |
| MYC-10.6 <!-- 274a8884-eef2-4361-83c9-0baecc1f2fb2 --> | print the tail on standard output after grep's output, and leave it out in every case of the table above | Changed | unit |
| MYC-10.7 <!-- 36cfbcac-0901-4e4b-801c-dbfa7fc47db5 --> | search for the tail as MYC-4 says, with five results, documents and code, and without the freshness check | Kept | store |
| MYC-10.8 <!-- e4c20317-0794-4bdb-9d78-78247dd350f8 --> | take the repository of the tail from the first path given to grep, or else from the current directory | Kept | unit |
| MYC-10.9 <!-- ec7751c1-ea7c-40ea-8d55-0a87a50a329e --> | search a pattern that has no sign of a regular expression other than `.` as it was written, and turn the signs of any other pattern into spaces | Changed | unit |
| MYC-10.10 <!-- 53ee2659-2c80-4751-8956-64c0d7630749 --> | print in the tail each result's place, its lines when it is code and the section that delivered it, then once each document section that cites a result, marking stale and Heartwood sections, and print no score | Changed | unit |
| MYC-10.11 <!-- 98e4feb5-28c4-4d64-8d91-f50ea95eb979 --> | run grep when no repository is found, when the settings cannot be read and when the store cannot be reached | Kept | unit |
| MYC-10.12 <!-- f54e9cc0-b69f-4134-8ef0-38e5942bbea5 --> | write one line on standard error when the search for the tail fails | Kept | unit |
| MYC-10.13 <!-- 5515b86b-1f31-4d76-9db4-c5bbe7464f9e --> | write nothing into the store | Changed | store |
| MYC-10.14 <!-- d1c91b08-6d5a-461a-976d-006f0e23f6c0 --> | be reached as `mycel grep` and in no other way | Changed | unit |

## Interface

Proposed.

```sh
mycel grep -rn "session reminder" src            # grep's lines, then the tail
mycel grep -c "renew" src/auth/session.py        # a count: no tail
MYCEL_GREP_PLAIN=1 mycel grep -rn "renew" src    # grep alone
```

The lines of the tail are text for a reader. A program that needs the same results in a form it can rely on calls `mycel search`.

## Known problems in version 1

- **The tail went into output that was being counted.** It was printed below a count, a list of file names and a quiet check alike, unless a variable switched it off.
- **The pattern was guessed, and guessed wrong.** An option with its value attached, or short options written together before a value, made the program search for a path or a number.
- **One copy of grep was built in.** `/usr/bin/grep`, whatever the search path said.
- **A name with a dot in it was searched as two words.**
- **In the folder of an organization the tail was missing without a word.**
- **Four ways in, behaving differently.** The separate program skipped steps the others took, and one way searched for its own name.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/better_grep.py#run`
- `mycel_deprecated_v1:mycel/better_grep.py#_parse`
- `mycel_deprecated_v1:mycel/better_grep.py#_semantic_query`
- `mycel_deprecated_v1:mycel/better_grep.py#main`
- `mycel_deprecated_v1:better_grep_entry.py`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D33 <!-- 3673c632-1c80-4013-850e-421f9708f5dc --> | Under which name is the grep replacement started? | `mycel grep`, and no second program. Mycel is one program with one launcher. Version 1 also had `better-grep` as a program of its own, so that the habit of typing `grep` could be kept by changing one word; the guides and skills of this corpus still tell agents to call it. Keeping that name would need a second launcher, which the Builds specification does not provide, or a line in the owner's shell settings that maps the old name onto the new command | Decided 8 October 2026 by the owner: agreed. `mycel grep`, and no second program |

## Named checks

Written by `scripts/name_checks.py` from the `proven` Origin Links of the tests and a complete check report in which they passed. Each requirement keeps its kind in its Verified by cell and names here up to three of its passing checks: those of its own kind first, then those that rest on the fewest requirements. `mycel origins --repo mycel --path tests` lists every link. Do not edit this section by hand: run the script again.

| Requirement | Kind | Checks |
|---|---|---|
| `MYC-10.1` | unit | `test_grep_tail.GrepTailUnitTests.test_real_path_first_child_receives_literal_argv_binary_streams_and_unchanged_cwd_without_settings`, `test_grep_tail.GrepTailUnitTests.test_real_child_help_version_noargs_no_match_error_and_eligible_pipe_preserve_grep_prefix_and_status` |
| `MYC-10.2` | unit | `test_grep_tail.GrepTailUnitTests.test_primary_cancellation_keeps_signal_status_and_reaps_its_real_child_group`, `test_grep_tail.GrepTailUnitTests.test_real_child_status_survives_search_render_write_flush_and_tail_cancellation_faults`, `test_grep_tail.GrepTailUnitTests.test_real_child_help_version_noargs_no_match_error_and_eligible_pipe_preserve_grep_prefix_and_status` |
| `MYC-10.3` | unit | `test_grep_tail.GrepTailUnitTests.test_primary_cancellation_keeps_signal_status_and_reaps_its_real_child_group`, `test_grep_tail.GrepTailUnitTests.test_real_path_first_child_receives_literal_argv_binary_streams_and_unchanged_cwd_without_settings`, `test_grep_tail.GrepTailUnitTests.test_real_child_help_version_noargs_no_match_error_and_eligible_pipe_preserve_grep_prefix_and_status` |
| `MYC-10.4` | unit | `test_grep_tail.GrepTailUnitTests.test_explicit_attached_clustered_and_late_patterns_preserve_paths_conservatively` |
| `MYC-10.5` | unit | `test_grep_tail.GrepTailUnitTests.test_every_accepted_suppression_precedes_settings_and_optional_search`, `test_grep_tail.GrepTailUnitTests.test_explicit_attached_clustered_and_late_patterns_preserve_paths_conservatively` |
| `MYC-10.6` | unit | `test_grep_tail.GrepTailUnitTests.test_dotted_identifiers_survive_and_other_signs_become_spaces_before_literal_minimum`, `test_grep_tail.GrepTailUnitTests.test_every_accepted_suppression_precedes_settings_and_optional_search`, `test_grep_tail.GrepTailUnitTests.test_first_path_actual_folders_longest_root_and_single_member_organization_boundary` and 2 more |
| `MYC-10.7` | store | `test_grep_tail_store.GrepTailStoreTests.test_actual_append_uses_normal_wording_fallback_and_retains_every_row_xmin_sequence_and_cited_mark`, `test_grep_tail_store.GrepTailStoreTests.test_actual_default_tail_matches_normal_combined_top_five_with_shared_documents_and_no_freshness_or_writes` |
| `MYC-10.8` | unit | `test_grep_tail.GrepTailUnitTests.test_first_path_actual_folders_longest_root_and_single_member_organization_boundary` |
| `MYC-10.9` | unit | `test_grep_tail.GrepTailUnitTests.test_dotted_identifiers_survive_and_other_signs_become_spaces_before_literal_minimum` |
| `MYC-10.10` | unit | `test_grep_tail.GrepTailUnitTests.test_delimited_ordered_tail_has_exact_places_lines_delivery_and_unique_marked_sections_without_scores`, `test_grep_tail.GrepTailUnitTests.test_document_identity_dedup_and_control_characters_cannot_forge_tail_lines` |
| `MYC-10.11` | unit | `test_grep_tail.GrepTailUnitTests.test_explicit_plain_silences_invalid_settings_while_selected_failure_is_one_private_line`, `test_grep_tail.GrepTailUnitTests.test_real_path_first_child_receives_literal_argv_binary_streams_and_unchanged_cwd_without_settings` |
| `MYC-10.12` | unit | `test_grep_tail.GrepTailUnitTests.test_document_identity_dedup_and_control_characters_cannot_forge_tail_lines`, `test_grep_tail.GrepTailUnitTests.test_real_child_status_survives_search_render_write_flush_and_tail_cancellation_faults`, `test_grep_tail.GrepTailUnitTests.test_explicit_plain_silences_invalid_settings_while_selected_failure_is_one_private_line` |
| `MYC-10.13` | store | `test_grep_tail_store.GrepTailStoreTests.test_actual_append_uses_normal_wording_fallback_and_retains_every_row_xmin_sequence_and_cited_mark`, `test_grep_tail_store.GrepTailStoreTests.test_actual_default_tail_matches_normal_combined_top_five_with_shared_documents_and_no_freshness_or_writes` |
| `MYC-10.14` | unit | `test_grep_tail.GrepTailUnitTests.test_only_mycel_console_entry_and_raw_grep_command_are_exposed` |
