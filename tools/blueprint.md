---
role: authored
---
# Runbook: blueprint

## Why it exists

Runs a [Blueprint](../../arbol_deprecated_v1/GLOSSARY.md#blueprint) — instructions + typed
input/output parameters — as a non-deterministic **function**: it binds
inputs, composes the agent prompt, runs a [Delegate](../../arbol_deprecated_v1/GLOSSARY.md#delegate)
via [`infer`](infer.md), and extracts the declared outputs + `done_when`. It
owns the *function abstraction* only; session mechanics (recipe pinning,
permission broker, chat history) belong to `infer`. Standalone PyInstaller CLI, no daemon; it invokes `infer` through the executable/JSON contract rather than importing Infer internals.

## Use

```
blueprint list
blueprint run <name|path> --input k=v [--input k=v…] [--recipe NAME|model:thinking] [--max-minutes N]
```

- Blueprints live in `~/Artifacts/mycel/blueprints/`; `--input` binds the
  declared inputs (required ones are validated). `repo`/`branch` inputs set
  the run's working dir (the corpus worktree, or the branch worktree).
- **Restrictions** come from the blueprint's `restrictions:` frontmatter (the
  blueprint governs; the engine imposes nothing).
- **`--recipe`** takes a configured name or an ad-hoc `model:thinking`
  descriptor (e.g. `fable:xhigh`) — see the [infer runbook](infer.md) for the
  syntax; pass it only when the USER named a brain (caller rule unchanged).
- **Multi-step** bodies: a `## Steps` section with `### Step N. <optional
  name>` — numbering obligatory (validated), names referenceable. Each step
  is one sequential message in ONE session; the roster is injected into the
  system prompt; a step whose condition fails answers `SKIPPED — <why>`;
  iteration happens *within* a step (you can't return to an earlier one).
  `execution.context_budget` caps the accumulating window.
- **Chat history** is the underlying `infer` session (labeled
  `role=delegate, blueprint=…`): read it with `infer show <session-id>` — the
  run JSON prints the `session_id`.
- Exit: `0` done_when met · `4` unmet · `3` timed out.

<!-- sources:
blueprint:blueprint_engine/cli.py
-->
