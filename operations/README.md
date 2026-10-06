---
role: authored
---
# Process guide authoring rules

**Read this file before creating or changing any artifact in `operations/` or
its subfolders.** These artifacts define tool-agnostic process truth: what must
happen regardless of whether the process is invoked through an agent Skill,
Blueprint, Chain, CLI, RPC, UI, or by a human.

- **Dependency direction:** Mycel must not depend on Arbol code or instructions. Never import, invoke, or prescribe Arbol code, repository scripts, `arbol-cli`, or an Arbol artifact as a required procedure. Mycel may read Arbol-owned databases, logs, and other data as inputs; data access is not a code/instructions dependency. Keep Mycel code and required process truth in Mycel.

## What “Mycel Operation” means

**Mycel Operation** is the architectural and catalog term for a reusable,
tool-agnostic process described in this folder. The category was created while
Arbol capabilities were being decoupled from the Arbol application: process
knowledge that had been embedded in Arbol was extracted into portable Mycel
instructions, so agents in other hosts—especially Claude Code—could follow the
same processes. A common integration is a thin Claude Code Skill that routes to
the corresponding process artifact here.

A Mycel Operation specifies **what should happen and why**, without depending on
a particular tool or invocation surface. A [Runbook](../../arbol/GLOSSARY.md#runbook)
is different: it is the technical manual for **how to use a particular tool**.
A tool may implement all or part of a process, so a process guide may link to
its runbook for commands and parameters, but must not absorb the runbook's
tool-specific reference material.

“Mycel Operation” is category vocabulary for architecture, catalogs, and this
authoring contract—not reader-facing vocabulary inside the process artifacts.
Do **not** call an artifact an “Operation,” title it `Operation: ...`, or make an
agent learn this taxonomy merely to perform the process. Use ordinary,
task-oriented language such as `# Guide: Code Retrieval`, `# Code Retrieval
Guide`, or a direct task name. In the body, say “guide,” “process,” or the
specific activity. This keeps instructions portable and avoids spending agent
context on internal Mycel terminology.

## Scope and placement

- One coherent process or invariant family per `kebab-case.md` file.
- Create a new process guide only when no existing guide owns the truth. Prefer
  updating the owning document over adding a sibling that competes with it.
- Separate process from lookup material when needed: `<topic>.md` contains the
  read-whole guide; `<topic>-reference.md` contains IDs, payloads, tables,
  syntax, and examples consulted on demand.
- Product specifications and glossary definitions belong in the Arbol corpus
  (`~/Artifacts/arbol/`), not here. Tool command manuals belong in `../tools/`;
  trigger-only dispatchers in `../skills/`.
- Superseded implementation truth moves to `archive/` with Heartwood metadata;
  it is never silently deleted or left looking current.

## Frontmatter and title

Living process guides start with:

```yaml
---
role: authored
---
# Guide: Human-readable Name
```

A natural task-oriented title such as `# Code Retrieval Guide` is equally
valid. Never use `# Operation: ...` or introduce the “Mycel Operation” term in
the artifact body.

Use in-band knowledge declarations when applicable (`sources`, `generated`,
status) according to `knowledge-model.md`. A Heartwood snapshot declares at
least `status: heartwood` and dates/notes sufficient to identify when and why
it became outdated. Generated artifacts must say `generated: true` and name
the generator; do not hand-edit generated output.

## Content conventions

- Open with purpose, scope, and who/what uses the guide. Define what it is
  authoritative for and point to any companion reference.
- Write for the agent or person performing the task, not for the Mycel catalog.
  Do not require readers to understand Mycel artifact taxonomy.
- State invariants and constraints in direct language. Use **must/never** only
  for real policy; distinguish defaults, recommendations, exceptions, and
  user-confirmation boundaries.
- Describe the process in execution order. Include triggers, prerequisites,
  inputs, state read first, side effects, outputs, gates, stop conditions,
  failure handling, retries/resume, and cleanup when relevant.
- Name the source of truth for each stateful fact. Say when cached/mirrored
  data is acceptable and when live state must be fetched.
- Separate deterministic actions from agent judgment. If a guarantee matters,
  identify the Tool/Chain code that enforces it rather than pretending prose
  enforces it.
- Keep the core process tool-agnostic. Put tool syntax, flags, payload formats,
  exit codes, and tool-specific troubleshooting in the relevant Runbook and
  link to it. Mention a tool in the guide only where it is a supported way to
  carry out a process step or where its behavior enforces an invariant.
- Commands must be copyable and use placeholders consistently (`<KEY>`,
  `<repo>`, `{workspace}`). Keep one authoritative copy of volatile IDs and
  payloads; link to it elsewhere.
- Explain where artifacts and code live. Use established vocabulary and link
  its canonical glossary definition instead of redefining terms locally.
- Record exceptions beside the rule they weaken, including authorization and
  confirmation requirements for writes or irreversible actions.
- Include degraded behavior only when it is safe and genuinely supported.
  Never invent fallback behavior that hides missing context or failed tools.

## Evidence and links

- Process claims about implementation carry Source Refs in `<!-- sources:
  ... -->` blocks, at the narrowest useful section or at file end when they
  govern the whole document. Prefer file or symbol refs that resolve; directory
  refs do not create useful edges.
- Link laterally rather than copy policy. Relative links inside this folder are
  preferred; use `../tools/` and `../skills/` for neighboring chapters and
  `../../arbol/` for the Arbol corpus.
- When code changes invalidate the process, update the guide in the same
  change. If the old behavior remains historically useful, freeze it as
  Heartwood and link to the living replacement prominently.

## Recommended shape

Not every guide needs every section, but a mature process normally covers:

1. purpose and authority;
2. quick start / routing;
3. concepts and where state lives;
4. core constraints;
5. ordered procedure by phase;
6. failure, resume, and cleanup behavior;
7. reference links and Source Refs.

Long documents should include a compact contents line. Human overview text
belongs in `OVERVIEW.md`; the root Instructions Hub routes agents by task.

## Validation checklist

- [ ] Read this README and the existing guide that most nearly owns the topic.
- [ ] Confirm this is a new authority domain, not a duplicate of living truth.
- [ ] Frontmatter/status accurately describes living, generated, or Heartwood state.
- [ ] Title and body use ordinary task language, not “Operation” or “Mycel Operation.”
- [ ] The core process is tool-agnostic; tool-specific reference material lives
      in and links to the appropriate Runbook.
- [ ] Process boundaries, state sources, writes, confirmation gates, and errors
      are explicit.
- [ ] Commands and links are valid; volatile lookup data has one owner.
- [ ] Implementation claims carry resolving Source Refs.
- [ ] Update `OVERVIEW.md` for a new process family, `../INDEX.md` for the
      catalog, and `../README.md` only for a new routing need.
- [ ] If agents invoke it, keep the corresponding Skill thin and pointing here.
