---
role: authored
---
# Tool runbook authoring rules

**Read this file before creating or changing any artifact in `tools/`.**
This folder contains technical manuals for client-agnostic CLIs used by Mycel.
A runbook describes the real command surface and operating contract; it does
not own cross-tool workflow policy.

- **Dependency direction:** Mycel must not depend on Arbol code or instructions. Never import, invoke, or prescribe Arbol code, repository scripts, `arbol-cli`, or an Arbol artifact as a required procedure. Mycel may read Arbol-owned databases, logs, and other data as inputs; data access is not a code/instructions dependency. Keep Mycel code and required process truth in Mycel.

## Scope and naming

- One Tool per `kebab-case.md` file, normally matching its executable name
  (`mycel.md`, `infer.md`, `blueprint.md`, `better-grep.md`).
- Use `role: authored` frontmatter and `# Runbook: <tool>` as the title.
- Add a runbook only for an independently invocable Tool. Subcommands stay in
  their parent Tool's runbook unless they are effectively a separate product.
- Arbol-only Tool manuals belong in `~/Artifacts/arbol_deprecated_v1/tools/`. Cross-tool
  operating procedures belong in `../operations/`; executable agent tasks in
  `../blueprints/`; orchestration in `../chains/`.

## Required content

### Why it exists

State the Tool's responsibility, what abstraction it owns, what it deliberately
does not own, and whether it requires a daemon/network/provider. Link canonical
terms in the Arbol glossary instead of redefining them.

### Use

Provide a compact, copyable command synopsis in a fenced block. It must include
all public command families and important global options without turning into
a dump of `--help`. Use consistent placeholders and show repeatable flags.

### Behavioral contract

Document what operators and calling agents need to reason safely:

- input and output forms, stdout/stderr split, machine-readable schemas;
- path/CWD/repo/overlay inference and configuration/environment variables;
- defaults, precedence, idempotency, freshness, caching, and side effects;
- permission, secret, network, daemon, and provider boundaries;
- exit codes, timeouts, partial success, fallback, and failure behavior;
- where logs, session records, mirrors, generated files, or other state live;
- platform/profile limitations and explicitly unsupported paths.

Distinguish current behavior from intent. Do not document a command or option
until it exists. If a limitation is temporary, state it plainly rather than
implying enforcement that is only recorded or planned.

## Style and maintenance

- Keep examples safe and directly runnable after placeholder substitution.
  Mark destructive commands and their guards prominently.
- Use bullets for semantics and tables only when comparison improves lookup.
  Put the common path first; advanced and exceptional behavior follows.
- Keep one authoritative syntax/default/exit-code statement. Operations and
  Skills should link here rather than copying it.
- Link source implementation with resolving Source Refs in a trailing or
  section-local `<!-- sources: ... -->` block. Cite the CLI entry point and
  important shared service functions, not every implementation file.
- Update the runbook in the same change as the CLI. Removed behavior is deleted
  from the living runbook or preserved in an explicitly Heartwood historical
  artifact when its design remains useful.
- Ensure the documented path passes the VS Code Test when the Tool promises to
  be client-agnostic; call out any daemon-only feature honestly.

## Recommended skeleton

```markdown
---
role: authored
---
# Runbook: tool-name

## Why it exists

## Use

\`\`\`
tool-name command [options]
\`\`\`

- Behavioral details, boundaries, and state locations.
- Exit: `0` success · nonzero meanings.

<!-- sources:
Arbol:path/to/cli.py#entrypoint
-->
```

Add headings such as Configuration, Safety, Troubleshooting, or Examples only
when the Tool needs them; avoid boilerplate sections with no content.

## Validation checklist

- [ ] Read this README, the nearest Tool runbook, and the actual CLI help/entry point.
- [ ] Name/title/frontmatter identify exactly one Tool.
- [ ] Every documented command and option exists; important public commands are present.
- [ ] Defaults, state paths, side effects, restrictions, and exit behavior match code.
- [ ] Examples are copyable and destructive behavior has clear guards.
- [ ] Source Refs resolve to current implementation.
- [ ] Run representative `--help` and safe read-only commands; update relevant
      tests/docs when the CLI contract changed.
- [ ] Add the Tool to `../INDEX.md`; add a Hub route only when it serves a new
      user need rather than another syntax detail.
