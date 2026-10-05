---
role: authored
---
# Blueprint authoring rules

**Read this file before creating or changing any artifact in `blueprints/`.**
A Blueprint is an executable, typed agent-work definition: frontmatter is its
machine contract; the Markdown body is the instruction set an agent executes.
It must work both through `blueprint run` and manually in an agent session.

- **Dependency direction:** Mycel must not depend on Arbol code or instructions. Never import, invoke, or prescribe Arbol code, repository scripts, `arbol-cli`, or an Arbol artifact as a required procedure. Mycel may read Arbol-owned databases, logs, and other data as inputs; data access is not a code/instructions dependency. Keep Mycel code and required process truth in Mycel.

## File and identity

- One Blueprint per `kebab-case.md` file. The filename and frontmatter `name`
  must match exactly; choose a stable, action-oriented name.
- Create a new Blueprint only for a reusable task with a distinct input/output
  contract. Extend an existing Blueprint when the goal and deliverable are the
  same. Do not use Blueprints for deterministic orchestration; that belongs in
  `../chains/`.
- Start from the nearest existing Blueprint, then remove assumptions that do
  not belong to the new task. Do not copy a contract blindly.

## Required frontmatter

Use YAML between `---` delimiters at the very top:

```yaml
---
role: blueprint
name: example-task
summary: One sentence describing input → outcome
inputs:
  - name: repo
    type: repo
    required: true
    description: Why the input is needed
outputs:
  - artifact: "~/Artifacts/{repo}/path/{name}.md"
    must: [specific-invariant, another-checkable-invariant]
done_when: the artifact exists and every declared invariant can be checked
restrictions: [no-repo-edit, no-git-mutations]
recipe: inherit
# default-recipe: configured-recipe-name  # add only when the task needs one
---
```

Contract rules:

- `summary` is concise and distinguishes this Blueprint in `blueprint list`.
- Every input has `name`, `type`, and `required`; add `description` whenever
  the meaning, accepted form, or binding is not obvious. Supported conventions
  include `string`, `repo`, `branch`, and `enum [a, b]`; optional inputs may
  declare `default`.
- Outputs name exact paths or path templates. Every `must` item is observable,
  not a vague quality adjective.
- `done_when` is a truthful completion gate over produced outputs. It must be
  possible for a runner to answer met/unmet from files or explicit evidence.
- Restrictions express the minimum permissions needed. Research and planning
  Blueprints normally use `no-repo-edit` and `no-git-mutations`; use
  `read-only` when no artifact is written.
- `recipe` is a hard pin. Prefer `inherit` unless the Blueprint truly must
  override every caller. `default-recipe` is a fallback, not a pin. Never copy
  the model/recipe of the chat session creating the file.

## Body structure

Use these sections unless the task has a strong reason not to:

1. `# Blueprint: <Human Name>`
2. a short positioning paragraph when there are neighboring/manual/chain paths;
3. `## Goal` — the outcome, not a repetition of the steps;
4. `## Process` — ordered, imperative steps with inputs and paths named;
5. `## Output contract` when the artifact shape needs more detail;
6. `## Quality bar` — checks that operationalize `done_when`;
7. `## Output` — what the final agent response reports, usually clickable
   artifact links and a compact result summary.

For a multi-message Blueprint, use exactly `## Steps` and sequential headings
`### Step 1. Name`, `### Step 2. Name`, and so on. Numbering is validated;
iteration happens inside a step, not by jumping back to an earlier one.

## Instruction rules

- Bind all behavior to declared inputs; use `{input_name}` consistently.
- State where the agent reads context, where it writes, and when it must stop
  rather than invent missing prerequisites.
- Separate signals from conclusions and deterministic gates from agent
  judgment. A chain should enforce guarantees that prose alone cannot.
- Make update-vs-create behavior explicit. For durable corpus artifacts,
  update an existing document instead of creating a competing sibling.
- Require evidence at the granularity appropriate to the task: Source Refs
  for durable research, `file:line` and scenarios for review findings, exact
  output fields for machine-readable JSON.
- Link shared operations/runbooks rather than copying their policy. Relative
  links from this folder normally begin `../operations/`, `../chains/`, or
  `../../arbol_deprecated_v1/`.
- Do not hide errors, silently weaken scope, or claim `done_when` when an output
  is absent. Define degraded/manual behavior only when it is genuinely usable.

## Validation checklist

Before considering a Blueprint ready:

- [ ] Read this README and the closest existing Blueprint.
- [ ] Filename equals `name`; YAML parses; `role: blueprint` is present.
- [ ] Required inputs are sufficient and no undeclared variable appears.
- [ ] Output paths, `must`, and `done_when` agree exactly.
- [ ] Restrictions and recipe policy are intentional and least-privilege.
- [ ] Process, quality bar, and final-response contract are unambiguous.
- [ ] Relative links resolve and cited operations remain the source of truth.
- [ ] `blueprint list` discovers it; perform a dry/manual contract review and,
      when practical, run it with representative inputs.
- [ ] Add the Blueprint to `../INDEX.md` and route it from `../README.md` only
      when it introduces a new user-facing task shape.
