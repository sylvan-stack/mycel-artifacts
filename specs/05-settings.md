---
role: authored
spec: MYC-5
status: implemented
---
# Mycel · 05 Settings

Mycel is told everything it needs in one file that its owner writes: which repositories exist and where they are, where the index store is, which model embeds, and a handful of limits. This specification fixes where that file is, every key it may hold with its type and default, what happens to a key Mycel does not know, and the credential contracts for the store and embedding, and the additional model credentials the file must not hold. It matters because version 1 took its settings from a file, from sixteen environment variables and from a copy in its database, checked no value for its type, and wrote the file itself.

It follows the conventions of the [specifications chapter](README.md#conventions).

## Scope

Covered: the file and how it is found, its keys with types and defaults, keys Mycel does not know, faults, environment variables, model credentials, the store password and the Keychain items, what `mycel info` and `mycel repos` say about the settings.

Not covered: what each setting does, which is specified with its subject: repositories and the scan ([MYC-1](01-corpora-and-ingest.md)), embedding ([MYC-3](03-embedding.md)), search ([MYC-4](04-retrieval.md)), the store ([MYC-6](06-index-store.md)), Drift classification ([MYC-14](14-drift-detection.md)), summaries ([MYC-8](08-summaries.md)), the evaluation set ([MYC-13](13-checks-and-evaluation.md)).

## Behaviour

### The file

Observed in version 1: the settings were a TOML file, `~/.mycel/config.toml`, or the file named by the environment variable `MYCEL_CONFIG`. When the file was missing, the first command wrote one from the copy of the settings in the database. Every command then copied the repositories of the file into the database, and that copy took part in decisions ([MYC-1](01-corpora-and-ingest.md#repositories-and-corpora)). A file that could not be read gave a warning in some commands and stopped others. The part of the program that looked for the store treated an unreadable file as an empty one and went on to an address built into the code.

Decided: one file, `~/.mycel/config.toml` ([MYC-D3](00-overview-and-legacy-map.md#decisions)), in TOML. Mycel reads it once at the start of every invocation and never writes or creates it (MYC-0.4, MYC-0.5). `MYCEL_CONFIG` names another file; the automatic checks use it so that the program under check never works with the owner's settings ([MYC-13](13-checks-and-evaluation.md)).

A missing file is not a fault for `mycel info`, which says that there is none. Every other command is refused with `settings`, except `mycel grep`: it still runs grep and only leaves out its tail (MYC-10.11).

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/config.py#path`
- `mycel_deprecated_v1:mycel/config.py#load`
- `mycel_deprecated_v1:mycel/config.py#ensure_seeded`
- `mycel_deprecated_v1:mycel/config.py#load_apply`
- `mycel_deprecated_v1:mycel/database.py#dsn`

### The keys

Observed in version 1: the code read the tables `[database]`, `[providers]`, `[organizations.<name>]`, `[repos.<name>]` and `[mirrors]`. No key was checked for its type. Everything else that changed behaviour was a constant in the code or an environment variable.

Proposed: the keys below and no others. Each is named by the requirement that needs it. The names of version 1 are kept where the meaning is the same, so that the owner's file stays valid (MYC-D3).

| Table | Key | Type | Default | Needed by |
|---|---|---|---|---|
| `[store]` | `address` | text | none; required by every command except `info` and `grep` | [MYC-6](06-index-store.md) |
| `[embedding]` | `model` | text | `voyage-code-4` | MYC-D14 |
| `[embedding]` | `dimensions` | whole number | `1024` | MYC-D14, MYC-6 |
| `[embedding]` | `key_command` | list of texts | none: the Keychain item | MYC-3.14 |
| `[embedding]` | `attempts` | whole number, 1 or more | `5` | MYC-3.8 |
| `[scan]` | `document_endings` | list of texts | `[".md"]` | MYC-1.6, MYC-D7 |
| `[scan]` | `code_endings` | list of texts | version 1's fifteen endings | MYC-1.6, MYC-D7 |
| `[scan]` | `skip_folders` | list of texts | version 1's list for code | MYC-1.6, MYC-D7 |
| `[search]` | `shared_documents` | list of `{ repo, paths }` | the two entries of MYC-D18 | MYC-4.3 |
| `[search]` | `freshness_seconds` | number above 0 | `5` | MYC-4.19 |
| `[discussions]` | `address` | text: a password-free PostgreSQL address of the Arbol database | none: no discussion can be shown | [MYC-17](17-justification.md#the-discussion-of-a-decision), MYC-D48 |
| `[drifts]` | `debounce_seconds` | whole number, 0 or more | `300` | [MYC-14](14-drift-detection.md), MYC-D28 |
| `[drifts]` | `model` | text: exact versioned Jev ID | `jev-1.13.0` | [MYC-14](14-drift-detection.md) |
| `[drifts]` | `confidence_floor` | finite number from 0 to 1 inclusive | `0.7` | [MYC-14](14-drift-detection.md) |
| `[drifts]` | `candidates` | whole number, 1 or more | `100` | [MYC-14](14-drift-detection.md) |
| `[drifts]` | `at_once` | whole number, 1 or more | `2` | [MYC-14](14-drift-detection.md) |
| `[drifts]` | `seconds` | finite number above 0 | `300` | [MYC-14](14-drift-detection.md) |
| `[drifts]` | `jev_timeout_seconds` | finite number above 0 | `10` | [MYC-14](14-drift-detection.md) |
| `[drifts]` | `review_timeout_seconds` | finite number above 0 | `120` | [MYC-14](14-drift-detection.md) |
| `[drifts]` | `attempts` | whole number, 1 or more | `2` | [MYC-14](14-drift-detection.md) |
| `[drifts]` | `max_input_bytes` | whole number, 1 or more | `24000` | [MYC-14](14-drift-detection.md) |
| `[drifts]` | `review_max_input_bytes` | whole number, 1 or more | `1048576` | [MYC-14](14-drift-detection.md) |
| `[drifts]` | `origin_floor` | finite number from 0 to 1 inclusive | `0.7` | [MYC-17](17-justification.md#decisions) |
| `[drifts]` | `conformance_floor` | finite number from 0 to 1 inclusive | `0.7` | [MYC-17](17-justification.md#decisions) |
| `[drifts]` | `consistency_floor` | finite number from 0 to 1 inclusive | `0.7` | [MYC-17](17-justification.md#decisions) |
| `[drifts]` | `ambiguity_floor` | finite number from 0 to 1 inclusive | `0.8` | [MYC-17](17-justification.md#decisions) |
| `[drifts]` | `review_command` | nonempty NUL-free argv; absolute or ~/ executable | absent: uncertain work remains pending | [MYC-14](14-drift-detection.md) |
| `[drifts]` | `review_provider` | nonempty text | absent; required with review_command | [MYC-14](14-drift-detection.md) |
| `[drifts]` | `review_model` | nonempty exact model-version text | absent; required with review_command | [MYC-14](14-drift-detection.md) |
| `[drifts]` | `review_revision` | immutable adapter revision; 1–128 ASCII letters/digits or . _ : + -, starting alphanumeric | absent; required with review_command | [MYC-14](14-drift-detection.md#independent-smarter-reviewer) |
| `[summaries]` | `command` | list of texts | none: no summary can be written | [MYC-8](08-summaries.md) |
| `[summaries]` | `at_once` | whole number, 1 or more | `4` | MYC-8 |
| `[summaries]` | `instructions` | folder | none: the texts built into the program | MYC-8 |
| `[organizations."<name>"]` | `root` | folder | required | MYC-1.3 |
| `[organizations."<name>"]` | `artifact_root` | folder | `~/Artifacts/<last part of root>` | MYC-1.3 |
| `[repos.<name>]` | `enabled` | true or false | `false` | MYC-1.1 |
| `[repos.<name>]` | `code_root` | folder | from the organization; otherwise the repository has no code corpus | MYC-1.3 |
| `[repos.<name>]` | `code_clones` | list of absolute or ~/ checkout folders | empty: only the primary root | MYC-D60, MYC-1.38 |
| `[repos.<name>]` | `readonly_root` | an absolute or ~/ checkout folder already listed as primary or clone | absent: changes comparison requires configuration | MYC-D53, MYC-1.39 |
| `[repos.<name>]` | `artifact_root` | folder | from the organization; otherwise absent (checkout Markdown remains in the document corpus) | MYC-1.3 |
| `[repos.<name>]` | `code_subdirs` | list of paths inside `code_root` | the whole code folder; an empty list means the same | MYC-1 |
| `[repos.<name>]` | `test_patterns` | list of texts | version 1's patterns for tests | MYC-4.12 |
| `[repos.<name>]` | `generated_patterns` | list of texts | version 1's patterns for generated code | MYC-4.12 |
| `[repos.<name>]` | `evaluation` | path inside `artifact_root` | none: the repository has no evaluation set | [MYC-13](13-checks-and-evaluation.md) |

Three of the numbers remain first values and not measured ones: `attempts`, `freshness_seconds` and `at_once`. The owner selected Jev and a five-minute quiet period for Drift classification on 8 October 2026 (MYC-D28), represented by `drifts.debounce_seconds = 300`; it is distinct from the search time budget. There is no `drifts.threshold` key or change-size gate. Low-confidence Jev results require smarter-model review. MYC-14 specifies an initial confidence floor of 0.7, finite explicit classification and a configured independent protocol-1 reviewer. The owner accepted the agent-selected initial floor and classifier limits on 8 October 2026, and selected the smarter-model command named in settings (`drifts.review_command`); these values are not a measured correctness guarantee; MYC-13's provider qualification is an implementation/release check. The exact review provider/model is required deployment configuration rather than a hidden default.

The default of `shared_documents` is the one [MYC-D18](04-retrieval.md#decisions) decided: every document of `mycel`, and `GLOSSARY.md` of `arbol`.

`embedding.model` and `embedding.dimensions` must name a supported pair in the packaged MYC-3 model/tokenizer catalog; an unknown pair is a detailed `settings` fault before index or network access. Integers exclude TOML booleans, and numeric limits/floors must be finite. A Jev model must be a versioned `jev-<major>.<minor>.<patch>` ID, not a moving alias. Reviewer command/provider/model/revision must be supplied together or all absent; the command's first member is an absolute path or begins `~/`, every argv member is nonempty and NUL-free, and the revision matches `[A-Za-z0-9][A-Za-z0-9._:+-]{0,127}`. Incomplete combinations are detailed settings faults. Their absence is valid and leaves low-confidence work as `reviewer_unconfigured`. Changes to routing or reviewer identity change the MYC-14 policy fingerprint. MYC-14 defines exact argv, JSON/EOF, environment, authentication, success/failure, retry, termination and command-hash rules; an executable command alone is not a protocol adapter. No setting contains an API key or store password.

A folder may begin with `~`, which stands for the home folder. After that it must be an absolute path. A repository that is not a member of an organization and names neither folder is a fault of that repository.

The store's address has a table of its own, `[store]`, and not version 1's `[database]`. A file written for version 1 may still name Arbol 1's database there, and Mycel 2 must never take that for its own store.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/config.py#apply`
- `mycel_deprecated_v1:mycel/organizations.py#configured`
- `mycel_deprecated_v1:mycel/knowledge/store.py#set_repo_flags`
- `mycel_deprecated_v1:mycel/locations.py#RepositoryLocations`

### A key Mycel does not know

Observed in version 1: a table or a key the code did not read was ignored without a word. When the program wrote the file, it dropped them. Observed on 8 October 2026: the owner's file held `profile` in 11 repositories, a `[providers]` table and `url` in two organizations. None of them means anything to Mycel 2. The owner decided that what is left of version 1 is removed and not provided for, and these keys were taken out of the file the same day (MYC-D23).

Decided on 8 October 2026: refuse unknown keys and show a detailed error message ([MYC-D23](#decisions)). Validation covers unknown tables and keys at every level. A command that needs valid settings is refused with `settings` before it reads or changes the index or calls another service.

The error identifies the settings file, every unknown fully qualified key and its line when available, explains that the key is unsupported, and lists the accepted keys for that table or gives a correction when unambiguous. For example, an error for `repos.cellar.enabeld` says that this key is unknown and that the supported key is `enabled`; it never silently substitutes it. Diagnostics do not echo the supplied values, which could contain secrets. `mycel info` remains available to report the same faults; `mycel grep` still runs grep and omits its Mycel tail when settings are invalid.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/config.py#dumps`
- `mycel_deprecated_v1:tests/test_config_ownership.py#test_mycel_config_does_not_serialize_infer_recipes`

### Faults

Observed in version 1: `enabled = "false"`, a text and not a truth value, switched a repository on. A file that could not be read left some commands running against a built-in store.

Proposed:

| Fault | Effect |
|---|---|
| The file is not valid TOML | Every command except `info` is refused with `settings`. The message names the file and the line |
| A key of the table above has a value of the wrong type or outside its range | The same, naming the key (MYC-1.2) |
| A table or key is unknown | Refuse commands that need valid settings with `settings`; identify the file, fully qualified key and line when available, and explain how to correct it (MYC-D23) |
| A repository has no folder that can be found, or its name lies under several organizations | Only commands that need that repository are refused (MYC-1.29). Commands for other repositories go on |
| The store's address carries a password | Every command except `info` is refused with `settings`: a secret is not kept in the file |

`mycel info` is never refused for a fault in the settings. It is the command that shows the fault. `mycel grep` runs grep whatever the state of the settings, and only its tail is left out (MYC-10.11).

### Environment variables

Observed in version 1: sixteen environment variables changed what the program did. Seven of them were named for Arbol. They chose the settings file, the store and its schema, the repository and the branch view, two folders of one repository, the on-device model, the program that wrote summaries, the folder of its prompts and the tail of the grep replacement.

Proposed: Mycel reads two variables of its own.

| Variable | Effect |
|---|---|
| `MYCEL_CONFIG` | Names the settings file |
| `MYCEL_GREP_PLAIN` | `1` leaves out the tail of `mycel grep` ([MYC-10](10-grep-replacement.md)) |

Nothing else in the environment changes what Mycel does, apart from what every program takes from it: the home folder and the search path on which `git` and `grep` are found. Keychain access uses the fixed `/usr/bin/security` executable.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/scope.py#resolve`
- `mycel_deprecated_v1:mycel/database.py#connect`
- `mycel_deprecated_v1:mycel/knowledge/local_embedder.py#model_dir`
- `mycel_deprecated_v1:mycel/completion_client.py#_infer_bin`

### Credentials

Observed in version 1: the key of the embedding service was read from a Keychain item named for Arbol's embedder. The store's address, password included, could stand in the settings file, and the address built into the code carried a user name and a password. Before every command the address was placed into the environment, where each program Mycel started could read it.

The store, Voyage and Jev credentials use the contracts below. Mycel reads Jev's key from its generic-password Keychain item only when explicit classification or live drift qualification requires a Jev call; no environment fallback, plaintext settings key, or Jev or Voyage credential acquisition during dry-run; a dry-run reaches the store as every other command does ([MYC-D41](14-drift-detection.md#decisions)). The independent reviewer command owns its provider authentication; Mycel forwards none of its own credentials to it. No secret belongs in settings, a command argument or output (MYC-0, MYC-3.14). Missing Jev/reviewer credentials are visible `authentication` or reviewer faults in selected work; local ingest, stale reporting and ordinary search still work.

| Secret | Comes from |
|---|---|
| The key of the embedding service | The command `embedding.key_command` when the settings name one; otherwise the Keychain item below |
| The password of the store, when the store asks for one | The Keychain item below ([MYC-D25](06-index-store.md#decisions)); when there is none, no password is sent |
| The Jev API key | The `mycel` / `jev-api-key` Keychain item; no key means a classification authentication fault |
| The smarter reviewer's credential | The independently configured review command's own provider authentication; Mycel neither acquires nor forwards it |
| The password of the discussion database, when it asks for one | The Keychain item below; when there is none, no password is sent (MYC-D48) |

A command that gives a secret is a program of the owner's. Mycel starts it without a shell and takes what it prints, without the final line break, as the secret. A status other than 0 means there is none.

The Keychain items are generic passwords of the login Keychain ([MYC-D24](#decisions)):

| Secret | Service | Account |
|---|---|---|
| The key of the embedding service | `mycel` | `voyage-api-key` |
| The password of the store | `mycel` | `store-password` |
| The Jev API key | `mycel` | `jev-api-key` |
| The password of the discussion database | `mycel` | `discussions-password` |

Mycel reads an item with `/usr/bin/security`. Whoever sets one, the owner by hand, Arbol or another editor of settings, writes a generic password with the same program and explicitly trusts `/usr/bin/security` for reading (`-T /usr/bin/security`, without a blanket allow-all ACL). This is MYC-3.14's identity contract: one item, one secret, any number of independent writers. A missing Jev item, a locked Keychain or refused Jev access is an `authentication` fault within selected classification work. Voyage key failures stop embedding or refuse the query's provider operation with `refused`; they do not introduce a global error code. A missing store-password item sends no password; refusal or a rejected connection is `store_unavailable`. Credential readers do not rewrite an ACL or repeatedly prompt. The explicit `api-key` writer sets the trusted-reader rule when it writes an item.

`mycel api-key voyage` and `mycel api-key jev` read one nonempty printable-ASCII key from the controlling terminal with echo disabled and store it in the corresponding login-Keychain item above (MYC-D40). They do not accept a key in argv or standard input. Missing terminal access, empty or non-printable-ASCII input, or input that cannot safely fit in the native interpreter is `invalid_input`; a failed Keychain write is `refused`. Settings must be valid as for other commands. No store connection, provider call or old-secret read is needed.

The writer starts `/usr/bin/security -q -i` and sends exactly one `add-generic-password` command over a private pipe, with the printable-ASCII secret encoded as hexadecimal for `-X` and `/usr/bin/security` explicitly trusted with `-T`. Encoding does not make the secret public: neither that request nor native output is logged or written to a file. The explicit login-Keychain path is quoted for the native interpreter, which is not a shell. Requests that reach its 4096-byte input-line limit are refused before any write. The key is stored only in the intended encrypted Keychain item.

The writer first attempts creation. Duplicate-item status selects a single `-U` replacement attempt; other faults are not retried. The JSON reply names `stored`, the `item` service/account and `replaced`, without the key. `replaced` means an existing item was found by the creation attempt; concurrent independent writers can still change that item. macOS may request native permission to change an existing item's access rules. Refusal or a bounded timeout is a failed write, and the key may already have changed before an access-rule update fails; no rollback is claimed. Automated checks use stand-ins and isolated dummy items, never the owner's real API-key items.

Observed on 8 October 2026 on macOS 27.0.1: an isolated generic-password item with a generated probe service/account and a public dummy value was created with that trusted-program ACL, read by a separate `/usr/bin/security` invocation with an exact value match and no permission interaction, then deleted. Create/read/delete all returned 0. No real credentials were accessed or changed. This confirms the mechanism on this machine; packaged-runtime checks repeat it with a temporary item rather than assuming every existing item's ACL is suitable.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_api_key`
- `mycel_deprecated_v1:mycel/macos_keychain.py#get_password`
- `mycel_deprecated_v1:mycel/config.py#dumps`
- `mycel_deprecated_v1:mycel/cli.py#_export_dsn`

### What Mycel says about its settings

Observed in version 1: no command showed the settings as the program understood them. `mycel repos` listed the folders under one directory and looked each up in the database by its folder name.

Proposed: `mycel info` says which file was read, whether it exists and can be read, every key Mycel did not know, and every fault. `mycel repos` lists the repositories of the file with the folders Mycel worked out for each, and says for each folder whether it was given for the repository or follows from its organization.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/cli.py#_cmd_repos`
- `mycel_deprecated_v1:mycel/organizations.py#repo_dirs`

## Requirements

| ID | Mycel must… | From v1 | Verified by |
|---|---|---|---|
| MYC-5.1 <!-- e04d8254-6c82-4ea8-8052-83d0afe3f145 --> | read its settings from `~/.mycel/config.toml`, or from the file `MYCEL_CONFIG` names, and from nowhere else | Changed | unit |
| MYC-5.2 <!-- b6031cbc-4173-4431-8244-ee33782962d3 --> | know exactly the keys of the table above, use the default of a key that is absent, and check every value for its type and range | Changed | unit |
| MYC-5.3 <!-- c02887da-5225-490c-bdfa-cdce84d91b1d --> | refuse unknown tables and keys with `settings` before index access or service calls; identify the file, every unknown fully qualified key and its line when available, explain the fault and accepted keys or an unambiguous correction, and never echo supplied values; `info` reports these faults and `grep` only omits its Mycel tail | Changed | unit |
| MYC-5.4 <!-- d43deea7-3acc-4c4e-a03a-30fade7c7c92 --> | refuse every command except `info` and `mycel grep` with `settings` when the file is missing, is not valid TOML, holds an unknown table or key, or holds a known key with a wrong value, naming the file and the key or line | Changed | unit |
| MYC-5.5 <!-- f032c5c7-f1bb-40db-9937-306e51aa9876 --> | run `mycel info` whatever the state of the settings, and show every fault there | New | unit |
| MYC-5.6 <!-- f8d1bc70-68eb-41fe-90db-2c6e60db0a84 --> | take `~` at the start of a folder as the home folder, and refuse a folder that is not an absolute path after that | Changed | unit |
| MYC-5.7 <!-- 3561dd6a-ac5b-4985-b199-2922a4e1fe5b --> | read no environment variable of its own other than `MYCEL_CONFIG` and `MYCEL_GREP_PLAIN` | Changed | unit |
| MYC-5.8 <!-- 5b1f13ff-d9be-432e-9d27-1dd70da7d0cd --> | refuse with `settings` a store address that carries a password; take the key of the embedding service from the command the settings name or else from its Keychain item, and the password of the store from its Keychain item | Changed | unit |
| MYC-5.9 <!-- 71779747-705d-407e-98cc-4f930f3d758c --> | start a command that gives a secret without a shell, take its output without the final line break as the secret, and treat a status other than 0 as no secret | New | unit |
| MYC-5.10 <!-- 90d89f2e-49f5-4c27-a884-cdbd5ad956c1 --> | read a Keychain item with the system's `security` program, under the service and account named above | Changed | unit |
| MYC-5.11 <!-- e07a6517-00c6-4a85-bc1d-5735042c3e4c --> | never write a secret to standard output, standard error, the store, a file outside its named encrypted Keychain item, or the environment of a program it starts | Changed | unit |
| MYC-5.12 <!-- 69f13239-3ac8-473c-be12-1114a6a16c4f --> | list in `mycel repos` every repository of the file with the folders worked out for it, where each folder comes from, and its fault when it has one | Changed | unit |
| MYC-5.13 <!-- 1a4f6af3-534d-484b-9fa2-5cc02dbe046e --> | validate supported model/dimension pairs, finite classifier limits and complete reviewer command/provider/model/revision configuration before index or network access | New | unit |
| MYC-5.14 <!-- e72eb8a3-6171-4f74-8aa6-ee44a1390429 --> | read Jev's key only for explicit classification (including Origin recovery) or live drift qualification from the named Keychain item, forward none of Mycel's credentials to reviewer commands, and acquire no Jev or Voyage credential during dry-run | New | unit |
| MYC-5.15 <!-- d5aef9a1-82f7-42f8-8640-987b72ca7707 --> | validate the complete reviewer command/provider/model/revision configuration and exact argv/revision syntax, resolve only the first-member leading tilde, and document the protocol-1 setup without storing credentials or running a dry-run probe | New | unit |
| MYC-5.16 <!-- 5bde14f7-cbf0-4e4e-9e78-3c8a42157b62 --> | provide `mycel api-key voyage` and `mycel api-key jev` to read a nonempty printable-ASCII key from a terminal without echo, refuse absent or unsafe terminal input with `invalid_input`, create or replace its named login-Keychain item through `/usr/bin/security` with that program explicitly trusted for reading, keep the key out of argv, output, logs, plaintext files and child environments, and return only the provider, item identity and replacement flag | New | unit |
| MYC-5.17 <!-- ee66c862-41b4-4a16-b95a-35158bc9bbee --> | know the table `[discussions]` with its key `address`, a password-free PostgreSQL address of the Arbol database, refuse one that carries a password with `settings`, take its password from the Keychain item `mycel` / `discussions-password` when the database asks for one, and leave every command but the read of a decision's discussion untouched by its absence | New | unit |
| MYC-5.18 <!-- df29d081-b840-460c-92b3-6818d704ea97 --> | accept code_clones as additional absolute checkout folders and readonly_root as the listed main-comparison checkout, normalize home paths, reject invalid shapes and an unlisted readonly_root, and preserve existing single-root settings | New | unit |

## Interface

Proposed. The command line follows the rules of [MYC-0](00-overview-and-legacy-map.md#the-command-line).

A complete fictional file:

```toml
[store]
address = "postgresql://mycel@localhost:5432/mycel"   # no password in it

[embedding]
model = "voyage-code-4"
dimensions = 1024

[search]
shared_documents = [
  { repo = "handbook", paths = ["."] },
]

[summaries]
command = ["claude", "-p"]

[organizations."Orchard"]
root = "~/repos/orchard"

[repos.presses]                 # a member of Orchard: folders follow from it
enabled = true

[repos.cellar]                  # a repository of its own
enabled = true
code_root = "~/repos/cellar"
artifact_root = "~/Artifacts/cellar"
code_subdirs = ["src", "tests"]
evaluation = "evaluation/search.toml"

[repos.handbook]                # documents only
enabled = true
artifact_root = "~/Artifacts/handbook"
```

A smarter reviewer is a protocol adapter configured by the owner. These paths and identities are fictional; install and authenticate the adapter separately, then replace them with its actual pinned values. Mycel passes the argv literally and the JSON request on stdin, according to [MYC-14's command contract](14-drift-detection.md#independent-smarter-reviewer).

```toml
[drifts]
review_command = ["/Users/example/.local/bin/mycel-review-adapter",
                  "--config", "/Users/example/.config/reviewer/config.toml"]
review_provider = "example-provider"
review_model = "example-model-2026-10-01"
review_revision = "example-adapter-v1"
```

Setting either API key without placing it in an argument, and what Mycel runs to read the embedding key:

```sh
mycel api-key voyage
mycel api-key jev
# Each command asks for its key on the terminal without echo.
# Reply: {"stored":"voyage","item":{"service":"mycel","account":"voyage-api-key"},"replaced":false}
/usr/bin/security find-generic-password -s mycel -a voyage-api-key -w
```

```ts
// MycelInfo of MYC-0 gains `settings: SettingsReport`. Its `settingsFile` stays.
interface SettingsReport {
  file: string;
  exists: boolean;
  readable: boolean;                   // false when it is not valid TOML
  unknownKeys: string[];               // "repos.cellar.profile", "providers.embedder_url"
  faults: Array<{ key?: string; line?: number; message: string }>;
}

interface RepositoriesReply {
  organizations: Array<{ name: string; root: string; documents: string }>;
  repositories: Array<{
    name: string;
    enabled: boolean;
    organization?: string;
    code?: { folder: string; from: "repository" | "organization"; subfolders?: string[] };
    documents?: { folder: string; from: "repository" | "organization" };
    fault?: string;                    // why its folders cannot be worked out
  }>;
}
```

## Known problems in version 1

- **Settings came from three places.** The file, a copy of it in the database that outlived removed keys, and sixteen environment variables. Seven of the variables carried Arbol's name.
- **No value was checked.** A text where a truth value belonged switched a repository on.
- **The program wrote its own settings.** It created the file when it was missing, and its writer dropped every table it did not know.
- **A secret could stand in the file.** The store's address was written with its password, under a comment saying that secrets do not belong there. The address built into the code carried a password too.
- **The store's address was handed to every program Mycel started.** It was placed into the environment before each command.
- **A file that could not be read moved the program to another database.** The address fell back to the one built into the code, without a word.
- **The key belonged to another product.** Its Keychain item was named for Arbol's embedder.

**Historical evidence (unindexed):**

- `mycel_deprecated_v1:mycel/config.py#apply`
- `mycel_deprecated_v1:mycel/config.py#dumps`
- `mycel_deprecated_v1:mycel/config.py#ensure_seeded`
- `mycel_deprecated_v1:mycel/database.py#dsn`
- `mycel_deprecated_v1:mycel/cli.py#_export_dsn`
- `mycel_deprecated_v1:mycel/knowledge/embedder.py#_api_key`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| MYC-D23 <!-- e6108d18-0e76-4f81-ac5f-1806fce3569d --> | What does Mycel do with a key in the settings file that it does not know? | It runs, and `mycel info` lists the key. The owner's file was written for version 1 and holds such keys today: `profile`, `[providers]`, `url`. Refusing them would stop every command until the file is cleaned by hand. The other choice is to refuse: a misspelt key such as `enabeld` could then never go unnoticed, at the price of that clean-up first | Decided 8 October 2026 by the owner: "Refuse unknown keys and show detailed error message." Unknown tables or keys stop commands that need valid settings with a detailed `settings` error. The earlier decision to remove deprecated keys remains recorded; that cleanup was completed the same day |
| MYC-D24 <!-- 99178ad9-6bc3-4b7e-a3df-426fbd70ceba --> | Under what name is the key of the embedding service kept in the Keychain, and how is it written and read? | A generic password with the service `mycel` and the account `voyage-api-key`, written and read with the system's `security` program. Arbol sets the key by running the same program, so one item serves both and Mycel holds no code of Arbol (MYC-D15). The temporary-item ACL trial records the writer/reader mechanism and must be repeated by the packaged-runtime probe | Decided 8 October 2026 by the owner: the agent chooses. Chosen: the proposed default, the service `mycel` and the account `voyage-api-key`, through the `security` program. The isolated dummy-item create/read/delete trial passed on macOS 27.0.1 on 8 October 2026; real credentials were not touched |
| MYC-D40 <!-- f3b9e863-48b3-4d30-8874-05a0e2def26b --> | How does the owner set the Voyage and Jev API keys without running `security` by hand, and how does the key reach it safely? | One `mycel api-key voyage\|jev` command prompts without echo and writes the existing named Keychain item | Decided 17 October 2026 by the owner: "I don't know how to add this key in Keychain. Let's add command 'mycel api-key' that will prompt to enter API key and save it to Keychain"; the owner agreed that the command serves both Voyage and Jev. Implementation choice, 18 October 2026: a bounded private pipe to `/usr/bin/security -q -i`, exactly one command with hexadecimal `-X` data, an explicit login-Keychain path and `-T /usr/bin/security`; no shell, secret argv, plaintext file or old-secret read. Create first and retry only duplicate-item status with `-U`; native access-rule approval may be required on replacement |

## Named checks

Written by `scripts/name_checks.py` from the `proven` Origin Links of the tests and a complete check report in which they passed. Each requirement keeps its kind in its Verified by cell and names here up to three of its passing checks: those of its own kind first, then those that rest on the fewest requirements. `mycel origins --repo mycel --path tests` lists every link. Do not edit this section by hand: run the script again.

| Requirement | Kind | Checks |
|---|---|---|
| `MYC-5.1` | unit | `test_settings.SettingsTests.test_each_load_reads_the_file_once_and_holds_an_immutable_snapshot`, `test_settings.SettingsTests.test_home_default_and_config_override_are_the_only_file_sources`, `test_settings.SettingsTests.test_legacy_environment_overrides_cannot_change_the_snapshot` and 3 more |
| `MYC-5.2` | unit | `test_settings.SettingsTests.test_absent_keys_have_the_specified_defaults`, `test_settings.SettingsTests.test_complete_schema_accepts_custom_values_and_literal_repository_names`, `test_settings.SettingsTests.test_folder_tildes_use_the_invocation_home_and_other_folders_are_absolute` and 11 more |
| `MYC-5.3` | unit | `test_settings.SettingsTests.test_inline_and_dotted_unknown_keys_are_not_hidden_by_table_syntax`, `test_settings.SettingsTests.test_key_lines_ignore_comments_and_text_that_looks_like_toml`, `test_settings_cli.SettingsCliTests.test_settings_do_not_probe_reviewer_command_even_for_info` and 7 more |
| `MYC-5.4` | unit | `test_settings.SettingsTests.test_missing_unreadable_and_invalid_toml_have_safe_file_diagnostics`, `test_settings.SettingsTests.test_store_address_is_required_only_for_store_dependent_work`, `test_settings_cli.SettingsCliTests.test_settings_do_not_probe_reviewer_command_even_for_info` and 7 more |
| `MYC-5.5` | unit | `test_diagnostics_cli.DiagnosticsCliTests.test_info_includes_configured_models_when_store_is_unavailable_without_model_credentials`, `test_diagnostics_cli.DiagnosticsCliTests.test_info_reports_all_settings_faults_without_echoing_values_or_accessing_services` |
| `MYC-5.6` | unit | `test_settings.SettingsTests.test_folder_tildes_use_the_invocation_home_and_other_folders_are_absolute`, `test_settings.SettingsTests.test_repository_relative_paths_cannot_escape_their_roots` |
| `MYC-5.7` | unit | `test_settings.SettingsTests.test_home_default_and_config_override_are_the_only_file_sources`, `test_settings.SettingsTests.test_legacy_environment_overrides_cannot_change_the_snapshot`, `test_settings_cli.SettingsCliTests.test_grep_handler_receives_invalid_snapshot_and_plain_flag_without_refusal` and 3 more |
| `MYC-5.8` | unit | `test_credentials.CredentialsTests.test_reporting_ordinary_commands_and_all_dry_runs_acquire_no_model_credentials`, `test_credentials.CredentialsTests.test_store_address_is_only_the_password_free_setting_not_parent_environment`, `test_credentials.CredentialsTests.test_configured_credential_command_is_literal_argv_with_empty_stdin_and_no_shell` and 4 more |
| `MYC-5.9` | unit | `test_credentials.CredentialsTests.test_output_removes_one_final_line_break_without_trimming_any_other_text`, `test_credentials.CredentialsTests.test_credential_command_deadline_and_output_limits_are_private_failures`, `test_credentials.CredentialsTests.test_configured_credential_command_is_literal_argv_with_empty_stdin_and_no_shell` and 2 more |
| `MYC-5.10` | unit | `test_credentials.CredentialsTests.test_store_challenge_acquisition_interrupts_and_reaps_its_private_child`, `test_credentials.CredentialsTests.test_each_invocation_reads_each_needed_credential_only_once_even_when_access_fails`, `test_credentials.CredentialsTests.test_keychain_reads_use_fixed_program_service_accounts_and_login_keychain` and 3 more |
| `MYC-5.11` | unit | `test_database.DatabaseTests.test_cancellation_during_dns_returns_before_any_connection_or_password_acquisition`, `test_database.DatabaseTests.test_late_connector_success_is_closed_and_not_published_after_total_deadline`, `test_database.DatabaseTests.test_missing_password_sends_none_and_rejected_password_is_not_reacquired` and 27 more |
| `MYC-5.12` | unit | `test_scope.ScopeTests.test_listing_includes_disabled_and_folderless_repositories_and_fresh_json_copies`, `test_scope.ScopeTests.test_ambiguous_membership_is_local_lists_organizations_and_keeps_other_repos_usable`, `test_scope.ScopeTests.test_explicit_roots_are_configured_paths_and_do_not_need_existing_files` and 5 more |
| `MYC-5.13` | unit | `test_settings.SettingsTests.test_integer_limits_exclude_booleans_and_fractional_numbers`, `test_settings.SettingsTests.test_jev_model_must_be_an_exact_three_part_version`, `test_settings.SettingsTests.test_numeric_limits_and_confidence_are_finite_and_within_range` and 7 more |
| `MYC-5.14` | unit | `test_credentials.CredentialsTests.test_jev_key_requires_explicit_classification_or_live_drift_qualification`, `test_classification_local.ClassificationCliBoundaryTests.test_dry_run_reaches_the_store_as_every_command_and_takes_no_model_credential`, `test_credentials.CredentialsTests.test_cli_fault_conversion_does_not_disclose_credential_command_output` and 5 more |
| `MYC-5.15` | unit | `test_settings.SettingsTests.test_only_the_reviewer_executable_leading_tilde_is_expanded`, `test_guides.GuideTests.test_settings_guide_contract_and_fictional_examples_match_validation`, `test_settings.SettingsTests.test_reviewer_argv_is_nonempty_nul_free_and_has_an_absolute_executable` and 3 more |
| `MYC-5.16` | unit | `test_credentials.ApiKeyTests.test_help_and_info_name_api_key_and_invalid_settings_prevent_prompt`, `test_credentials.ApiKeyTests.test_hidden_input_in_real_pseudoterminal_and_echo_restoration`, `test_credentials.ApiKeyTests.test_invalid_or_overlong_keys_and_metadata_never_start_security` and 9 more |
| `MYC-5.17` | unit | `test_entities.DiscussionSettingsTests.test_discussions_table_knows_only_a_password_free_address_and_its_keychain_item` |
| `MYC-5.18` | unit | `test_clone_locations.CloneScopeTests.test_clone_paths_are_typed_and_home_expanded_and_baseline_must_be_listed`, `test_clone_locations.CloneScopeTests.test_listed_clone_wins_over_organization_and_selects_only_its_checkout`, `test_clone_locations.CloneScopeTests.test_symlink_alias_names_one_location_and_unknown_folders_register_nothing` and 1 more |
