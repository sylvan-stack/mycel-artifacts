---
role: authored
---
# Blueprint Chain authoring rules

**Read this file before creating or changing any artifact in `chains/`.**
A Blueprint Chain is deterministic Python orchestration around Tools,
Blueprints, and inline agent lambdas. The script provides control flow,
logging, resume, and code-enforced gates; its sibling Markdown file is the
operator-facing runbook.

- **Dependency direction:** Mycel must not depend on Arbol code or instructions. Never import, invoke, or prescribe Arbol code, repository scripts, `arbol-cli`, or an Arbol artifact as a required procedure. Mycel may read Arbol-owned databases, logs, and other data as inputs; data access is not a code/instructions dependency. Keep Mycel code and required process truth in Mycel.

## Required artifact pair

Every chain named `<name>` normally consists of:

- `<name>.py` — executable implementation;
- `<name>.md` — same-name runbook beside it.

Use `kebab-case` for both. The same-folder/same-name proximity is the link
because scripts are not part of Mycel's Markdown corpus. `chainlib.py` is the
shared plumbing exception. Incident reports and design records may be
Markdown-only, but must say explicitly that they are not runnable chains.

Create a Chain only when the task needs multiple Cells, deterministic control
flow, resume, external Tool calls, parallelism, or a guarantee enforced in
code. A single reusable agent task belongs in `../blueprints/`.

## Script conventions

Start with a shebang and module docstring that state purpose, Cells, outputs,
workspace, usage, and sibling runbook. Then follow the established shape:

- import `Chain` and helpers from sibling `chainlib.py`;
- define a numbered `PLAN` of `(cell_number, kind, title)` entries;
- declare `PIN_RECIPE` and `DEFAULT_RECIPE` near `PLAN`;
- expose `main() -> int` with `argparse` and a `__main__` guard;
- instantiate `Chain(name, run_key, len(PLAN), resume=..., recipe=...,
  default_recipe=..., pin_recipe=...)`;
- execute Cells in PLAN order using `chain.tool`, `chain.blueprint`, or
  `chain.lam`; finish with `chain.finish(...)`.

Cell rules:

- Number Cells contiguously and keep code comments/runbook numbering aligned
  with `PLAN`. User-facing language says **Cell**, even though the process log
  schema uses `step`.
- Tools are deterministic work. Blueprints are named non-deterministic
  functions with `done_when`. Lambdas are small one-off agent transforms; if a
  lambda becomes reusable or complex, promote it to a Blueprint.
- Every important output gets a code-enforced gate: file existence, complete
  IDs, schema, coverage, non-empty diff, or another deterministic predicate.
  “The prompt asked for it” is not a gate.
- Abort loudly on Tool/session errors with actionable context. Never swallow a
  provider error, silently change recipes, or continue with missing inputs.
- Resume must be idempotent. Choose a stable `run_key`; completed agent Cells
  may skip, while cheap freshness Tools may deliberately rerun. `--fresh`
  starts a new run and `--until N` pauses a resumable run.
- Parallelize only independent Cells that do not write the same files. Let all
  parallel work settle and preserve partial results in logs.
- Use `os.path.expanduser`, absolute workspace paths, UTF-8, atomic writes for
  state where appropriate, and bounded subprocess/session timeouts.
- Keep business judgment in Blueprints/operations and orchestration/gates in
  Python. Do not duplicate `chainlib` facilities in each script.

## Recipe policy

`--recipe` is caller input only when the user named a recipe. A triggering
chat session's model is not inherited. Resolution is chain pin → caller
`--recipe` → chain default; a Blueprint's own hard pin may still win. Report
actual Cell recipes in the Chain output and never silently substitute on
failure.

## Runbook conventions

The sibling `<name>.md` starts with authored frontmatter (chain metadata is
recommended) and `# Runbook: <name> (Blueprint Chain)`. Include:

1. **Why it exists** and what guarantee the Chain adds;
2. **Use** with the exact command and every flag;
3. **Workspace / outputs** and the deliverable path;
4. **Cells**, numbered exactly like `PLAN`, each with kind, inputs, outputs,
   gate, skip/conditional behavior, and timeout where important;
5. **Operation** — resume, logs, aborts, prerequisites, idempotency;
6. **Recipes** and caller-only override behavior;
7. **Degraded/manual mode** when one exists.

Keep implementation detail in the script and operator truth in the runbook,
but do not let them disagree. Link the Blueprints and shared operations each
Cell relies on instead of restating their full instructions.

## Validation checklist

- [ ] Read this README, `chainlib.py`, and the nearest existing Chain pair.
- [ ] `<name>.py` and `<name>.md` exist and names/Cell counts match.
- [ ] `PLAN` is contiguous; `--dry-run` prints the intended path and conditions.
- [ ] Every output and cross-Cell assumption has a deterministic gate.
- [ ] Error, timeout, abort, resume, `--fresh`, and `--until` behavior is clear.
- [ ] Resume does not duplicate writes or lose the original deliverable path.
- [ ] Recipe handling follows the caller-only rule.
- [ ] Run the script's `--dry-run`; run syntax/tests for changed shared plumbing;
      exercise at least one safe/representative path when practical.
- [ ] Add the runbook to `../INDEX.md`, and route a new user-facing task shape
      from `../README.md` and an appropriate Skill.
