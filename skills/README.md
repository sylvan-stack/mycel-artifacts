---
role: authored
---
# Skill authoring rules

**Read this file before creating or changing any artifact in `skills/`.**
This directory is the source of truth for the native Codex CLI and Claude Code CLI adapters of
[Mycel Skills](../../arbol/GLOSSARY.md#mycel-skill). Mycel Skills are
provider-agnostic; these files are provider-specific discovery and dispatch
surfaces, not the home of process truth. Follow the
[creation guide](../operations/create-skill.md) when adding one.

- **Dependency direction:** Mycel must not depend on Arbol code or instructions. Never import, invoke, or prescribe Arbol code, repository scripts, `arbol-cli`, or an Arbol artifact as a required procedure. Mycel may read Arbol-owned databases, logs, and other data as inputs; data access is not a code/instructions dependency. Keep Mycel code and required process truth in Mycel.

## Layout

- One directory per Skill: `skills/<kebab-case-name>/SKILL.md`.
- The directory name and frontmatter `name` must match exactly.
- Keep one `SKILL.md` unless the runtime genuinely requires supporting files.
  Do not place operation manuals or durable research here.
- A Skill that routes into this corpus lives here and is symlinked into
  `~/.agents/skills/` (Codex) and `~/.claude/skills/` (Claude). Genuinely
  personal Skills stay outside this corpus. Do not duplicate Codex discovery
  under `~/.codex/skills/`.

The shared `SKILL.md` uses portable frontmatter. Provider-specific differences
live only where needed: `agents/openai.yaml` for Codex metadata and
`skills/providers/claude/<name>/SKILL.md` for Claude-only frontmatter. Keep
those thin adapters aligned with the shared activation contract.

## Required format

```markdown
---
name: example-skill
description: Trigger-focused activation instructions with outcome/scope,
  explicit NOT-for boundaries, and at least two example activating prompts.
---

Read `~/Artifacts/mycel/operations/example.md` and follow it for this task.
```

Frontmatter rules:

- `name` is stable, lowercase kebab-case, and matches the folder.
- `description` is the primary discovery contract. Include natural phrases a
  user is likely to say, at least two quoted example prompts that should
  activate the Skill, supported repos/surfaces when relevant, the expected
  outcome, and `NOT` boundaries for easily confused Skills.
- Keep frontmatter valid YAML. Use a folded scalar only when a long description
  would otherwise become invalid or unreadable.

## Body rules

- Keep the adapter body to one sentence that names the Skill's owning
  document by its absolute path: an operation guide in `operations/` or a Tool
  manual in `tools/`. Do not point it at the Instructions Hub
  (`~/Artifacts/mycel/README.md`), which the owner deprecated on 9 November
  2026 (MYC-D82) and which is switched off.
- Do not put commands, copied policies, invocation details, or reporting rules
  in the adapter. The owning document holds those details.
- If the owning document is missing, stop and tell the user rather than
  improvising a replacement process.

## Choosing whether to add a Skill

Add a Skill only when users need a distinct natural-language trigger surface.
Do not add one merely because a new document exists. Before creating it:

1. compare neighboring Skill descriptions for overlap;
2. decide the positive trigger and the negative boundaries;
3. identify exactly one canonical process/runbook it dispatches to;
4. confirm the outcome is useful enough to be discoverable independently.

If two Skills would trigger for the same request and neither has a clear
boundary, improve or consolidate them instead of relying on agent guesswork.

## Validation checklist

- [ ] Read this README and all neighboring Skills with overlapping triggers.
- [ ] Folder, filename, and `name` match; frontmatter parses.
- [ ] Description includes realistic triggers, at least two activating example
      prompts, outcome, and NOT-for boundaries.
- [ ] Body only names the owning document, which exists; no process, commands
      or Instructions Hub pointer.
- [ ] Verify the source directory is symlinked/discoverable in
      both `~/.agents/skills/` and `~/.claude/skills/`, without copied forks.
- [ ] Update `../INDEX.md` when the Skill catalog changes; add no Instructions
      Hub row.
