---
role: authored
---
# Guide: Create a Mycel Skill

A Mycel Skill is one provider-independent activation contract backed by a
portable process and exposed to **native Codex CLI and Claude Code CLI**.
Universe is deprecated; do not create Universe adapters or use its runtime.

## Canonical source

Read [the authoring rules](../skills/README.md) and neighboring skill descriptions.
Choose a stable kebab-case name, a distinct task shape, scope, boundaries, and
at least two realistic activating prompts. Locate the owning process through
the [Instructions Hub](../README.md); create a process only when none owns it.

Keep the shared adapter at `skills/<name>/SKILL.md` with YAML `name` and
`description`. Keep its body a thin pointer to the Hub. Both CLIs use this same
file unless provider-specific frontmatter requires a separate adapter.
Commands, procedures, and policy belong in the routed document, never in a
provider copy.

```markdown
---
name: example-skill
description: >-
  Handle <task and outcome>. Examples: "<prompt one>" and "<prompt two>".
  Not for <neighboring task>.
---

Start at the Instructions Hub `~/Artifacts/mycel/README.md` and follow the route
for this task.
```

## Native Codex CLI

Link `~/.agents/skills/<name>` to the canonical skill directory. This is the
current user discovery location; do not install the same skill again under
`~/.codex/skills`. Existing legacy personal skills should be migrated without
losing their resources or leaving duplicate discovery entries.

Invoke with `$<name>` or select through `/skills`. Implicit discovery is enabled
by default. Preserve an existing explicit-only contract with
`agents/openai.yaml` containing `policy.allow_implicit_invocation: false`.
Claude's `disable-model-invocation` is not a substitute for that setting.

[Official Codex skill documentation](https://learn.chatgpt.com/docs/build-skills)
documents user discovery, symlink support, invocation, and policy metadata.

## Claude Code CLI

Link `~/.claude/skills/<name>` to the same canonical directory. Explicit invocation
uses `/<name>`. When Claude requires different frontmatter, keep only that thin
adapter at `skills/providers/claude/<name>/SKILL.md` and link Claude to it;
the shared activation intent and Hub route must match the main adapter.
An explicit-only skill, for example, carries `disable-model-invocation: true`
in its Claude adapter and the matching Codex policy in `agents/openai.yaml`.

## Install and validate

1. Inspect each destination before linking. Reuse correct symlinks. Preserve
   existing files and resources; never force-overwrite a conflicting installation.
2. Validate YAML, folder/name agreement, concise trigger descriptions, two
   positive examples, neighboring negative boundaries, and Hub-only bodies.
3. Verify every Hub route reaches an existing current process. Do not make
   deprecated runtime tools an active route.
4. Check both provider symlinks resolve to their canonical source. Check
   invocation policy parity when an adapter has provider-specific metadata.
5. Update [INDEX.md](../INDEX.md); add a Hub route only for a new task shape.
6. Check discovery in a fresh CLI session when available. Filesystem validation
   alone does not prove runtime activation; report that distinction. If Codex
   does not show an update automatically, start a new session.

Completion requires both providers, one maintained process, matching activation
intent, valid links, and a current catalog. Do not create a skill merely because
a document exists. Personal or third-party skills outside Mycel's catalog are
not copied or migrated as part of catalog maintenance.
