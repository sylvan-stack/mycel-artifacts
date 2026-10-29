---
role: authored
spec: MYC-15
status: implemented
---
# Mycel · 15 Distribution and replacement

Mycel is a Python command-line program that starts once for each operation. A caller must be able to choose a known Build and run it without installing dependencies, extracting a one-file bundle or needing another product. This specification fixes the installed files, release checks, numbered Builds and the one-time replacement of Mycel 1. It matters because version 1 replaced two large executables in place and shared its store and release arrangements with Arbol.

It follows the conventions of the [specifications chapter](README.md#conventions). The owner selected Python (MYC-D1), no carried-over version 1 state (MYC-D26), one `mycel` program (MYC-D33), and Apple Silicon only on 14 October 2026. The other packaging defaults below were selected for this implementation and accepted with the specification set; this is not a record of a release already built.

## Scope

Covered: Python packaging, supported release targets, immutable installed program files, build numbers and package versions, the Mycel-owned registry and launcher, release checks, withdrawing and pruning Builds, store-format compatibility, and the replacement sequence for version 1.

Not covered: the command behaviour ([MYC-0](00-overview-and-legacy-map.md) onwards), database schema and migrations ([MYC-6](06-index-store.md)), provider contracts ([MYC-3](03-embedding.md), [MYC-14](14-drift-detection.md)), and the check contents ([MYC-13](13-checks-and-evaluation.md)). No installation, removal or schema migration is performed by writing this specification.

## Behaviour

### The Python distribution

Owner-selected release target, decided 14 October 2026: macOS 14 or later on Apple Silicon, with native `arm64` Builds (`macos-arm64`) only. macOS is required by the current Keychain credential contract; other operating systems need a specified credential contract and passing release checks before being advertised. A Build carries a pinned, ordinary CPython 3.14 runtime, the installed Mycel wheel and every runtime dependency, including grammar and tokenizer files. It does not depend on a system Python, an editable checkout, a virtual environment at another path, Node.js or Arbol.

The initial runtime pin is the non-free-threaded `install_only_stripped` distribution from [python-build-standalone release 20260901](https://github.com/astral-sh/python-build-standalone/releases/tag/20260901), CPython 3.14.7. Public release metadata checked on 8 October 2026 gives this archive SHA-256 value:

| Target | Archive | SHA-256 |
|---|---|---|
| arm64 | `cpython-3.14.7+20260901-aarch64-apple-darwin-install_only_stripped.tar.gz` | `4632cb1a6edad9e73d3c81b6d2e69131637d995173e3e85005df14102b0592ba` |

Runtime updates are made in a new Build with its own recorded pin and successful checks. The repository's `pyproject.toml` holds the package version, initially `2.0.0`, and Python package metadata. A checked-in lock records exact runtime and release dependency versions and hashes. The build installs non-editable wheels into its own runtime and includes dependency licences, the lock digest, the Mycel source-input digest, and all bundled data-file digests in its manifest. Native modules must load on the recorded target without relying on an absolute path into the build machine. A cross-compiled package is not working until its installed checks pass on the target architecture.

Normal execution uses the bundled interpreter in [isolated mode](https://docs.python.org/3.14/using/cmdline.html#cmdoption-I), with bytecode writes disabled: `runtime/bin/python3 -I -B -m mycel.cli`. Internal modules do not create a library interface for callers. The current directory is preserved for repository selection, while Python ignores user site packages, the current directory as an import path and `PYTHON*` interpreter overrides. Mycel's documented variables, including `MYCEL_CONFIG`, keep their specified meanings. No invocation runs an installer, resolves dependencies, downloads assets or extracts its runtime.

### Build numbers and the registry

Mycel has its own registry at `~/.mycel/builds/`. No Arbol registry, launcher, build tool or instruction file is needed. Its records contain distribution metadata and check results, never repository settings, source-corpus caches, index state or credentials.

Build numbers count 1, 2, 3 and onwards, written in lowercase hexadecimal without a prefix or leading zero: `9`, `a`, `f`, `10`. Number allocation is serialized under a registry lock, recorded before building and never reused, including after failure or pruning. The package version is separate; several Builds can share it. Build `a3` is Mycel's 163rd Build, and the default is selected by numeric value, not lexical order or a timestamp.

Each number has a folder containing `build.json`, `checks.json` and a sanitized `build.log`. A successful Build also contains its runtime and installed program. Program files are immutable after publication; only status, withdrawal reason and pruning metadata in the record may change. Failed and pruned records remain so that numbers and results can be accounted for. A damaged or missing record makes its own Build unavailable without breaking other records.

| Status | Meaning | Selection |
|---|---|---|
| `building` | A number was allocated; packaging or checks have not finished | Never run |
| `failed` | Packaging or a required automatic check failed or could not run | Never run |
| `working` | The installed files and every required automatic check passed | Eligible for the default or explicit selection |
| `withdrawn` | A previously working Build has a recorded reason to avoid it | Run only when explicitly named, with the reason on standard error |

`prunedAt` makes any record unavailable regardless of status. A Build becomes working only when its staged runtime, dependencies and application have passed all checks and their final folder has been published. The working record is the last atomic replacement in publication, so an interrupted build leaves the previous default available. No partially populated folder can become the default. Listing and invoking Builds only read distribution files; they write no cache or access log.

### The launcher

The sole product name on the search path is `~/.local/bin/mycel`. Its small launcher has a separately installed, pinned bootstrap Python runtime under `~/.mycel/launcher/`, with the same isolation and no-download rules as a Build. This avoids depending on a system interpreter or on a Build that might later be withdrawn or pruned. The repository build produces and checks the launcher bundle together with its Build. Installing or updating the launcher stages that complete bundle before atomically changing its entry point. Older launcher bundles remain; the first implementation has no launcher-bundle cleanup operation. No invocation updates them.

The launcher reads records, selects the highest working number with intact files for the current target, and executes that Build. It does not read settings or open a database to choose a Build. It recognizes `-v <build>` only in the first argument position and removes those two arguments; every following argument is passed unchanged. It preserves the working directory, standard streams, process identity, signals and final exit status by replacing itself with the selected process. `mycel grep` therefore retains the stream and exit rules of MYC-10. It introduces no daemon, timer or watcher.

Selection takes the registry's shared read lock without waiting, returning `busy` if maintenance holds it, and keeps it until a shared operating-system lock on that Build's pre-created `run.lock` is acquired. The file descriptor is opened read-only and retained across execution for the invocation's lifetime; exit releases it without writing a file. Pruning takes the registry's exclusive maintenance lock, then a non-waiting exclusive lock on the same `run.lock`. Failure to acquire it means the Build is in use and pruning returns `busy`. Lock acquisition protects the interval between selection and execution as well as a running operation. Kernel locks are distribution-file coordination, not a persistent invocation log.

An unknown or malformed number yields `invalid_input`; a known but building, failed, pruned, damaged or incompatible Build yields `refused`. No available default also yields `refused`. Launcher failures follow MYC-0's JSON error and status 1 rules, listing the runnable numbers without exposing secrets. Selecting a withdrawn Build prints its reason on standard error and runs it; it is never chosen by default. Withdrawal of the current default makes the preceding available working Build the default at the next invocation. A running process keeps the Build it already started.

### Release checks and maintenance

The Mycel repository supplies a Python release tool under `python -m mycel_build`; this is development tooling, not another installed product command or a caller library. Its development interpreter and build dependencies are pinned in the repository. A build may download verified dependencies during preparation. Checks and normal installed invocations may not do so.

Every Build runs all `unit` and `store` checks of MYC-13. Store checks create and remove their own `mycel_check_` databases on the configured server; they never open the owner's actual database. If the disposable store or another required check cannot run, the Build is failed and the record names the missing check. Evaluation and live checks remain on demand; no real embedding, classifier or reviewer call is required to make a Build working.

Packaged checks additionally run the completed Build from two different installation paths, after removing access to its source checkout and developer environment. They prove that the selected target's interpreter, native modules, parsers and tokenizer load offline; help and `info` run with missing or invalid settings without downloading or writing files; repository selection uses the preserved current directory; `-v`, default and withdrawn selection work; JSON and grep streams remain correct; and cancellation/exit statuses propagate. Provider fixtures and disposable stores prove operation behaviour. A measured startup record names the machine, target and runtime; no unmeasured startup threshold is claimed. These records are kept with the Build.

Release-tool writes take a non-waiting registry maintenance lock for number allocation and each publication or status change, not during packaging and checks. A busy registry is reported with `busy`; readers see only complete atomically replaced records. `withdraw` changes a working record and requires a nonempty reason. `prune` deletes only program files for a specifically named failed or withdrawn Build and sets `prunedAt`; it keeps its record, check summary, log and lock file. There is no automatic age or space pruning. The exclusive run-lock rule proves that no supported invocation can still use the selected Build; inability to establish that condition refuses pruning. A working Build must be withdrawn before pruning. No maintenance command changes settings or index contents.

### Store format and rollback

Every manifest records its supported store format and search-reply version. Installing or selecting a Build does not initialize or migrate a store. Only explicit `mycel init` changes its structure under MYC-6. The format number belongs to Mycel and begins at 1; it has no dependency on another product's version scheme.

Several Builds can use one store only when each supports its format and configured dimensions. Switching the executable back does not downgrade the database. An older Build refuses an unsupported store format; `info` remains diagnostic and grep keeps its specified fallback. A rollback after migration uses an owner-restored compatible database or a newer compatible Build, never automatic reverse migrations or deletion of new state. Database backup remains the owner's use of PostgreSQL tools, outside Mycel's product interface.

### Replacing version 1

The owner decided that nothing from the old index is copied and everything of version 1 is removed (MYC-D26). Replacement is a one-time operator procedure recorded in Mycel's release instructions; it is not runtime behaviour, an automatic installer side effect or an Arbol procedure.

The concrete sequence is:

1. Inventory the actual version 1 programs, old launchers or aliases and ten `kn_` tables, recording exact paths or qualified table names and ownership evidence. The observations recorded `~/bin/mycel` and `~/bin/better-grep`; the current inventory must verify what exists before naming removal targets. Historical names alone authorize no wildcard deletion. Existing obsolete settings were removed on 8 October 2026; any remaining invalid keys are corrected by the owner or their editor under MYC-5.
2. Build and check Mycel 2, install its launcher, create a new private Mycel database with PostgreSQL tools, and run explicit `mycel init`. Run local ingest and the required nonpaid checks against this database. Run `mycel embed` and any live checks only as explicitly requested paid operations. No version 1 vectors, edges, summaries, confirmations, history or settings rows are imported.
3. Make the launcher the command selected on the owner's search path, verify `mycel info` identifies Mycel 2 and its new database, and update Mycel-owned guides and caller instructions together. Remove the verified old executables, the separate `better-grep` launcher and obsolete Mycel 1 hooks or aliases. A conflicting file with uncertain ownership is reported for resolution, never overwritten or deleted by guessing. The release tool does not rewrite shell startup files.
4. Remove only the inventoried Mycel 1 tables from the old shared database with an explicit one-time SQL operation using PostgreSQL tools. Refuse a plan that drops the database, uses a table-name wildcard or needs `CASCADE` into uninventoried objects. Verify that the old Mycel tables and programs are gone and that unrelated database objects remain. Mycel 2 itself never connects to the version 1 tables (MYC-6.17).

The release record lists each completed or blocked step and its verification; a partial replacement is reported as partial. A failure before command cutover leaves the old command available. A failure after cutover leaves Mycel 2 available and the remaining cleanup listed; it does not reconnect Mycel 2 to the old store. Source checkouts and the frozen historical evidence corpora are source material, not installed Mycel 1 state, and are not removal targets. No repository or document corpus is deleted. This specification defines the procedure without performing any of it.

## Requirements

| ID | Mycel must… | From v1 | Verified by |
|---|---|---|---|
| MYC-15.1 <!-- 62df578d-c123-4a15-a5a8-cc084a6b181e --> | ship an independent Apple Silicon macOS 14-or-later command-line distribution for macos-arm64 only, with its pinned Python runtime, locked non-editable dependencies and required data files, and no system-Python, Node, Arbol or source-checkout runtime dependency | Changed | unit |
| MYC-15.2 <!-- 8b386417-92c1-49c8-a063-a9d8905e4a13 --> | record target, runtime/archive and dependency pins, source and data-file digests, package version, store format, search-reply version and check results for each Build | New | unit |
| MYC-15.3 <!-- b5527328-3cba-4535-8e4c-110087cc3beb --> | run installed Builds in isolated Python mode without writing bytecode, resolving or installing packages, downloading assets, extracting a bundle or changing the caller's directory | Changed | unit |
| MYC-15.4 <!-- ee421dc0-a6d0-4968-a33d-66e1f1220745 --> | allocate unique monotonically increasing lowercase hexadecimal build numbers under a registry lock, preserve failed and pruned records, and keep installed program files immutable after publication | New | unit |
| MYC-15.5 <!-- 413afb5a-e3a4-4b89-a8de-ab4137e54ef7 --> | publish a working record only after staged installed files and every required automatic check pass, and leave the previous default available after failure or interruption | New | unit |
| MYC-15.6 <!-- ba4668c3-2ab3-46f0-bc5f-27b651670a4b --> | select the highest available working Build numerically, accept `-v` only first, permit a withdrawn Build only when explicitly named, and reject unavailable or incompatible selections with a structured error | New | unit |
| MYC-15.7 <!-- e9d40e5e-b305-46ea-b2a7-2dd16162b132 --> | preserve arguments, current directory, process identity, standard streams, signals and exit status through the independent launcher, including MYC-10 grep exceptions | New | unit |
| MYC-15.8 <!-- f13fd28e-d077-4d78-87b7-d475f4bdc452 --> | run every unit/store and packaged relocation/offline-launch check for each Build, record the results, and keep real account, evaluation and paid provider checks on demand | New | unit |
| MYC-15.9 <!-- d9948426-6d4d-431e-948e-6987ac6cc415 --> | serialize release mutations, perform no automatic pruning, and remove only an explicitly named nonworking Build whose running-process absence has been established, retaining its metadata | New | unit |
| MYC-15.10 <!-- fcb8f9b2-460c-4c04-97b5-7eb0cf3065bd --> | change no settings or store structure on build, installation, selection, withdrawal or pruning; support rollback only within the store compatibility rules of MYC-6 | New | store |
| MYC-15.11 <!-- 062348f5-3f2b-4d4b-9b48-7206ff850b76 --> | provide a verifiable one-time replacement plan that copies no version 1 index state, removes only inventoried version 1 runtime files and tables, preserves unrelated objects and source corpora, and reports partial completion accurately | Changed | unit |
| MYC-15.12 <!-- 2fefd25e-65e1-485b-a9b7-1b527a5a9cfd --> | keep release and replacement instructions in Mycel, with no required Arbol scripts, code, process or instruction files | Changed | unit |

## Interface

Runtime selection keeps the single interface of MYC-0:

```sh
mycel info
mycel -v a3 search --repo core "how a pass works"
mycel grep -rn "dependency" src
```

The repository's development release tool has these commands; it is not installed as a second product launcher:

```sh
python -m mycel_build create --target macos-arm64
python -m mycel_build list
python -m mycel_build install-launcher
python -m mycel_build withdraw a3 --reason "parser regression"
python -m mycel_build prune a3
```

`create` uses the current source inputs, allocates a number, stages and checks the Build, and reports that number and its final status. `install-launcher` accepts only a completed verified launcher bundle; an unrelated existing destination is refused. Development commands return one JSON result with failures and partial outcomes; their detailed internal flags may grow without changing the product command contract. The registry record has this minimum shape:

```ts
interface BuildRecord {
  build: string;
  version: string;
  target: "macos-arm64";
  status: "building" | "failed" | "working" | "withdrawn";
  startedAt: string;
  finishedAt?: string;
  source: { commit: string; dirty: boolean; inputsSha256: string };
  runtime: { python: string; distribution: string; archiveSha256: string };
  lockSha256: string;
  filesSha256: string;                 // manifest digest of the installed runtime/program/data files
  storeFormat: number;
  searchReply: number;
  checks: { required: number; passed: number; failed: number; report: "checks.json" };
  reason?: string;                      // sanitized failure or withdrawal reason
  prunedAt?: string;
}
```

The launcher validates recorded format, number and relative installed paths and never follows a program path outside that Build's verified folder. `filesSha256` is checked at publication and before explicit reuse of changed files; a Build whose integrity check fails is unavailable until rebuilt. Failed records can omit unfinished manifest fields and must still retain number, source inputs, target, status and failure evidence.

## Known problems in version 1

- **Startup involved a one-file bundle.** The observed installed program took seconds to show help; a packaging comparison found unbundled Python could start much sooner. This is evidence for installed runtime files, not a promise about Mycel 2 performance. See [the language and packaging research](../research/mycel-2-language-evaluation-2026-10.md#measured-command-startup).
- **Replacing a file lost the previous program.** Two executables were installed under `~/bin`; no named earlier Build could be selected.
- **Ownership was shared with another product.** The old tables lived in Arbol 1's database. Replacing Mycel must enumerate its own objects rather than remove that shared database.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel.spec`
- `mycel_deprecated_v1:Makefile`
- `mycel_deprecated_v1:mycel/knowledge/store.py#ensure_schema`
- [Version 1 observations](../research/v1-observations-2026-10.md)

## Decisions

The binding owner decisions are [MYC-D1](00-overview-and-legacy-map.md#decisions) (Python command line only), [MYC-D26](06-index-store.md#decisions) (remove version 1 and carry over nothing), and [MYC-D33](10-grep-replacement.md#decisions) (one program, `mycel grep`). The runtime pin, registry location, independent launcher and development-tool shape are defaults accepted with the specification set on 8 October 2026. On 14 October 2026 the owner decided: "we don't need Intel support. Remove this requirement and implementation if any". Apple Silicon (`macos-arm64`) is the sole supported target. This supersedes the former Intel target obligation; historical release and check receipts retain the scope under which they were produced. Building, qualifying and publishing an installed program remain separate work.

## Named checks

Written by `scripts/name_checks.py` from the `proven` and `stated` Origin Links of the tests and a complete check report in which they passed. Each requirement keeps its kind in its Verified by cell and names here up to three of its passing checks: those of its own kind first, then those that rest on the fewest requirements. `mycel origins --repo mycel --path tests` lists every link. Do not edit this section by hand: run the script again.

| Requirement | Kind | Checks |
|---|---|---|
| `MYC-15.1` | unit | `test_build.BuildInputsTests.test_creation_refuses_free_threaded_and_non_cpython_before_allocation`, `test_build.BuildWheelTests.test_product_only_noneditable_wheel_installs_exact_recorded_bytes`, `test_build.BuildWheelTests.test_runtime_directory_ancestors_refuse_case_and_unicode_file_collisions_before_writes` and 16 more |
| `MYC-15.2` | unit | `test_build.BuildInputsTests.test_source_identity_ignores_generated_egg_info_and_tool_caches`, `test_build.BuildInputsTests.test_source_inputs_include_dirty_untracked_and_gate_files`, `test_build.BuildSourceBindingTests.test_gate_input_identity_covers_runner_imports_scripts_metadata_and_entrypoint` and 21 more |
| `MYC-15.3` | unit | `test_build.BuildManifestTests.test_exec_uses_bundled_isolated_python_and_preserves_arguments_cwd`, `test_build.BuildManifestTests.test_cross_target_probe_is_an_explicit_failure`, `test_build.BuildWheelTests.test_runtime_relative_interpreter_link_remains_inside_relocated_folder` |
| `MYC-15.4` | unit | `test_build.BuildRegistryTests.test_busy_registry_refuses_without_waiting_or_writing`, `test_build.BuildRegistryTests.test_canonical_numeric_allocation_retains_failed_and_pruned_records`, `test_build.BuildRegistryTests.test_concurrent_process_allocations_are_unique_and_monotonic` and 16 more |
| `MYC-15.5` | unit | `test_working_publication.WorkingPublicationTests.test_each_precommit_failure_or_interrupt_preserves_old_default_and_exact_retry_is_controlled`, `test_working_publication.WorkingPublicationTests.test_peer_registry_lock_is_immediately_busy_with_no_write_or_default_change`, `test_working_publication.WorkingPublicationTests.test_postcommit_fsync_error_or_interrupt_reports_actual_working_state_without_downgrade` and 3 more |
| `MYC-15.6` | unit | `test_launcher_selection.LauncherSelectionTests.test_malformed_unknown_unavailable_and_empty_default_are_sanitized_structured_errors`, `test_launcher_selection.LauncherSelectionTests.test_numeric_default_skips_every_unavailable_status_target_and_damaged_build_without_writes`, `test_launcher_selection.LauncherSelectionTests.test_only_first_selector_is_consumed_and_withdrawn_requires_explicit_selection` and 4 more |
| `MYC-15.7` | unit | `test_launcher_selection.LauncherProcessTests.test_actual_binary_streams_stdin_and_arbitrary_exit_status_pass_without_json_wrapping`, `test_launcher_selection.LauncherProcessTests.test_actual_exec_preserves_pid_cwd_every_argument_and_environment_without_distribution_writes`, `test_launcher_selection.LauncherProcessTests.test_real_product_grep_keeps_raw_stdin_output_error_and_status_under_invalid_settings` and 4 more |
| `MYC-15.8` | unit | `test_offline_build.InstalledAutomaticTests.test_unknown_child_lifetime_retains_its_private_workspace_without_database_recovery`, `test_private_credential_contract.PrivateCredentialContractTests.test_both_publication_receivers_refuse_global_preference_claim_over_profile_view`, `test_private_credential_contract.PrivateCredentialContractTests.test_invalid_client_admission_never_loads_native_library_or_writes_foreign_root` and 20 more |
| `MYC-15.9` | unit | `test_launcher_installation.LauncherInstallationTests.test_busy_installer_and_failed_final_cutover_preserve_existing_runnable_launcher`, `test_launcher_installation.LauncherInstallationTests.test_unchecked_or_tampered_bundle_never_replaces_existing_command`, `test_launcher_installation.LauncherInstallationTests.test_unrelated_command_and_unsafe_parent_refuse_before_creating_or_replacing_owner_files` and 9 more |
| `MYC-15.10` | store | `test_launcher_store.LauncherRollbackStoreTests.test_build_install_select_withdraw_prune_and_version_rollback_preserve_settings_all_rows_schema_and_sequences` |
| `MYC-15.11` | unit | `test_replacement.ReplacementTests.test_absent_inventory_refuses_present_objects_ambiguous_claims_and_unobservable_paths`, `test_replacement.ReplacementTests.test_already_absent_old_runtime_is_observed_without_inventing_cleanup_or_availability`, `test_replacement.ReplacementTests.test_disposable_rehearsal_removes_only_approved_objects_and_preserves_sources_shell_tail_and_catalog` and 7 more |
| `MYC-15.12` | unit | `test_replacement.ReplacementTests.test_mycel_owned_help_and_replacement_guide_require_no_other_product_or_runtime_cleanup_command` |
