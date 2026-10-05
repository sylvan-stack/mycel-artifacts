---
generated: true
---
# Code Map: mycel

Auto-generated structural overview — 57 files, 532 symbols. Do not edit; regenerated when the code corpus changes.

## .claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel

- **better_grep.py** — _parse, _semantic_query, run, main
- **cli.py** — search_payload, _cmd_search, _export_dsn, _connect_with_config, _cmd_sync, _cmd_embed, _cmd_raptor, _cmd_status, +20 more
- **completion_client.py** — CompletionError; _infer_bin, available, _run_infer, run
- **config.py** — path, load, _q, dumps, write, generate_from_db, apply, ensure_seeded, +3 more
- **confluence_write.py** — _md_to_storage, _send_json, _storage_body, create_page, update_page
- **database.py** — dsn, connect
- **jira_actions.py** — _url, _get, _send, _refetch_mirror, _parse_json_arg, get, search, comments, +6 more
- **macos_keychain.py** — KeychainWriteError; _Bindings (__init__, cfstr, cfdata, cfdict); _get_bindings, set_password, get_password, delete_password
- **mirror.py** — _mirrors_cfg, _base_url, _get_json, _download, _fetch_attachments, _now_iso, _fm, _write, +9 more
- **retrieval.py** — _repo_flags, _overlay_root, _code_root_for_view, _resolved_file, _read_location, _payload, search, capabilities, +1 more
- **scope.py** — _roots, resolve
- **secrets_store.py** — set_secret, delete, is_set, status, _read
- **syncpass.py** — artifact_root, is_container, list_worktrees, corpus_worktree, code_root, refresh_mirror, _ensure_last_sync_col, _repo_lock_key, +6 more

<!-- sources:
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/better_grep.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/cli.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/completion_client.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/config.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/confluence_write.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/database.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/jira_actions.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/macos_keychain.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/mirror.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/retrieval.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/scope.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/secrets_store.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/syncpass.py
-->

## .claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/knowledge

- **chunker.py** — parse_frontmatter, parse_source_refs, norm, sha, content_hash, chunk_markdown
- **clustering.py** — cluster
- **code_chunker.py** — chunk_code, _chunk, _whole_file, _uncovered_runs, chunk_python, chunk_svelte, _ts_parser, _ts_name, +1 more
- **code_map.py** — build_markdown, write_map
- **embedder.py** — set_api_key, has_api_key, _api_key, embed, _vec_literal, _base_repo, _profile_for, _query_vec, +13 more
- **fs.py** — corpus_root, _safe, _node, tree, read, write, _after_mutation, rename, +1 more
- **local_embedder.py** — provider_url, model_dir, is_available, provider_status, status, download, embed
- **raptor.py** — _Live (__init__, _emit, start, done); _instruction, _raptor_prompts, _parse_vec, _summary_doc_id, _clear, _prompt_sections, _insert_summary, _node_label, +5 more
- **store.py** — now_ms, ulid, ensure_schema, _scan_corpus, ingest, _parent_hash, _label, track_source, +26 more

<!-- sources:
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/knowledge/chunker.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/knowledge/clustering.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/knowledge/code_chunker.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/knowledge/code_map.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/knowledge/embedder.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/knowledge/fs.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/knowledge/local_embedder.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/knowledge/raptor.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/mycel/knowledge/store.py
-->

## .claude/worktrees/worktree-deps-frozen-spawn-47d2e0/tests

- **test_cli_metadata.py** — test_mycel_version, test_better_grep_help, test_better_grep_version
- **test_completion_routing.py** — test_missing_infer_is_honest, test_run_infer_contract
- **test_config_ownership.py** — test_mycel_config_does_not_serialize_infer_recipes, test_seeded_config_contains_only_mycel_owned_sections
- **test_repo_groups.py** — test_sylvan_stack_is_transparent_repo_group
- **test_worktree_cli.py** — Conn (commit, close); test_wt_list_honors_explicit_container, test_wt_add_new_creates_branch_from_requested_base, _porcelain, _wt_args, test_wt_list_excludes_archived_worktrees, test_wt_drop_resolves_directory_by_branch, test_wt_drop_errors_when_worktree_missing, test_wt_archive_moves_worktree_and_drops_overlay, +1 more

<!-- sources:
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/tests/test_cli_metadata.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/tests/test_completion_routing.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/tests/test_config_ownership.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/tests/test_repo_groups.py
mycel:.claude/worktrees/worktree-deps-frozen-spawn-47d2e0/tests/test_worktree_cli.py
-->

## mycel

- **better_grep.py** — _parse, _semantic_query, run, main
- **cli.py** — search_payload, _cmd_search, _export_dsn, _connect_with_config, _cmd_sync, _cmd_embed, _cmd_raptor, _cmd_status, +17 more
- **completion_client.py** — CompletionError; _infer_bin, available, _run_infer, run
- **config.py** — path, load, _q, dumps, write, generate_from_db, apply, ensure_seeded, +3 more
- **confluence_write.py** — _md_to_storage, _send_json, _storage_body, create_page, update_page
- **database.py** — dsn, connect
- **jira_actions.py** — _url, _get, _send, _refetch_mirror, _parse_json_arg, get, search, comments, +6 more
- **macos_keychain.py** — KeychainWriteError; _Bindings (__init__, cfstr, cfdata, cfdict); _get_bindings, set_password, get_password, delete_password
- **mirror.py** — _mirrors_cfg, _base_url, _get_json, _download, _fetch_attachments, _now_iso, _fm, _write, +9 more
- **retrieval.py** — _repo_flags, _overlay_root, _code_root_for_view, _resolved_file, _read_location, _payload, search, capabilities, +1 more
- **scope.py** — _roots, resolve
- **secrets_store.py** — set_secret, delete, is_set, status, _read
- **syncpass.py** — artifact_root, is_container, list_worktrees, corpus_worktree, code_root, refresh_mirror, _ensure_last_sync_col, _repo_lock_key, +6 more
- **worktree_deps.py** — _now, state_paths, _write_status, schedule, _dependency_snapshot, _root_package, _yarn_major, _node_marker, +10 more

<!-- sources:
mycel:mycel/better_grep.py
mycel:mycel/cli.py
mycel:mycel/completion_client.py
mycel:mycel/config.py
mycel:mycel/confluence_write.py
mycel:mycel/database.py
mycel:mycel/jira_actions.py
mycel:mycel/macos_keychain.py
mycel:mycel/mirror.py
mycel:mycel/retrieval.py
mycel:mycel/scope.py
mycel:mycel/secrets_store.py
mycel:mycel/syncpass.py
mycel:mycel/worktree_deps.py
-->

## mycel/knowledge

- **chunker.py** — parse_frontmatter, parse_source_refs, norm, sha, content_hash, chunk_markdown
- **clustering.py** — cluster
- **code_chunker.py** — chunk_code, _chunk, _whole_file, _uncovered_runs, chunk_python, chunk_svelte, _ts_parser, _ts_name, +1 more
- **code_map.py** — build_markdown, write_map
- **embedder.py** — set_api_key, has_api_key, _api_key, embed, _vec_literal, _base_repo, _profile_for, _query_vec, +13 more
- **fs.py** — corpus_root, _safe, _node, tree, read, write, _after_mutation, rename, +1 more
- **local_embedder.py** — provider_url, model_dir, is_available, provider_status, status, download, embed
- **raptor.py** — _Live (__init__, _emit, start, done); _parse_vec, _summary_doc_id, _clear, _prompt_sections, _insert_summary, _node_label, build_tree, _stale_members, +3 more
- **store.py** — now_ms, ulid, ensure_schema, _scan_corpus, ingest, _parent_hash, _label, track_source, +30 more

<!-- sources:
mycel:mycel/knowledge/chunker.py
mycel:mycel/knowledge/clustering.py
mycel:mycel/knowledge/code_chunker.py
mycel:mycel/knowledge/code_map.py
mycel:mycel/knowledge/embedder.py
mycel:mycel/knowledge/fs.py
mycel:mycel/knowledge/local_embedder.py
mycel:mycel/knowledge/raptor.py
mycel:mycel/knowledge/store.py
-->

## tests

- **test_cli_metadata.py** — test_mycel_version, test_better_grep_help, test_better_grep_version
- **test_completion_routing.py** — test_missing_infer_is_honest, test_run_infer_contract
- **test_config_ownership.py** — test_mycel_config_does_not_serialize_infer_recipes, test_seeded_config_contains_only_mycel_owned_sections
- **test_on_demand_overlay_embed.py** — Conn (commit, close); _capture_embed, test_cmd_embed_default_excludes_overlays, test_cmd_embed_overlay_flag_scopes_the_run, test_overlay_add_does_not_embed_by_default, test_overlay_add_embed_flag_scopes_to_that_overlay
- **test_repo_groups.py** — test_sylvan_stack_is_transparent_repo_group
- **test_worktree_cli.py** — Conn (commit, close); test_wt_list_honors_explicit_container, test_wt_add_new_creates_branch_from_requested_base
- **test_worktree_deps.py** — _project, test_select_source_prefers_exact_dependency_snapshot, test_worker_exact_clone_skips_yarn, test_worker_nearby_clone_runs_incremental_reconciliation, test_worker_falls_back_to_install_without_source, test_schedule_starts_detached_worker_without_waiting, test_schedule_skips_non_yarn_repo, test_clone_uses_apfs_copy_on_write_on_macos

<!-- sources:
mycel:tests/test_cli_metadata.py
mycel:tests/test_completion_routing.py
mycel:tests/test_config_ownership.py
mycel:tests/test_on_demand_overlay_embed.py
mycel:tests/test_repo_groups.py
mycel:tests/test_worktree_cli.py
mycel:tests/test_worktree_deps.py
-->
