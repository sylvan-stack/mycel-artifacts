---
role: authored
status: heartwood
superseded: 2026-09-29
---
# Universe Guide: Use Mycel for Code Search and Source Reading

Historical only: Universe is deprecated. Use the [native Codex CLI guide](codex-source-investigation.md). The tool names below are not current instructions.

Apply these rules whenever you locate, inspect, or reason about source code.
Arbol provides the native tools named below to Universe; call them directly.

## Route by intent

Use the first matching row.

| Need | Required action |
| --- | --- |
| A source symbol is already known | Use `ReadSymbol` with its source file and symbol name |
| A source file and relevant line range are already known | Use `Read` on that bounded range; do not search |
| Locate or understand an implementation, behavior, flow, ownership, or impact | Use `CodeSearch` with one natural-language question |
| Find rationale, architecture, policy, history, or a runbook | Use `Search` with one natural-language question |
| Enumerate an exact identifier, literal, regex, UUID, error, config key, caller, or registration | Use `Bash` to run `better-grep` with normal grep arguments |
| Inspect one known directory | Use `List` on that directory only |

For a task that requires both understanding and exhaustive coverage, use
`CodeSearch` first, inspect the relevant implementation, and then use
`better-grep` to enumerate exact occurrences in the discovered scope.

## Search and read correctly

- Ask `CodeSearch` one complete behavior-shaped question. Preserve the user's
  domain language and known identifiers. Prefer `"where is session renewal
  approved and persisted?"` over a keyword bag such as `"session renewal
  approve persist"`.
- Inspect ranked hits before making another search. Read the best relevant
  `path#symbol` with `ReadSymbol`, or its bounded line range with `Read`.
  Search results are leads; verify claims in current source.
- Use `Search` instead of `CodeSearch` when documents or summaries may contain
  the answer. Follow relevant `via` or `documented_in` entries when rationale
  matters.
- Use `better-grep` before claiming completeness or absence for exact text,
  callers, or registrations.

## Hard constraints

- Use native `CodeSearch`, `Search`, `ReadSymbol`, and `Read` directly. Do not
  bypass those native tools through `Bash`.
- Do not run bare `grep`, `rg`, or an ad-hoc grep-like shell pipeline for source
  investigation. `better-grep` is the required exact search command.
- Do not use `sed -n`, `cat`, `head`, `tail`, or a shell pipeline to read source.
  Use `ReadSymbol` or bounded `Read`. Use `sed` only when the task explicitly
  requires a text transformation.
- When a source location is unknown, do not start with `List`, directory
  walking, broad filename scans, guessed file reads, or speculative batches.
  Start with one `CodeSearch` question.
- There is no automatic fallback. If a required tool fails or semantic
  search returns no useful hit, stop and report the tool call and its result.
  Do not substitute primitive shell search/read commands, directory walking,
  or guessed reads unless the user explicitly authorizes that approach.

<!-- sources:
mycel:operations/code-research-levels.md
mycel:operations/code-research.md
mycel:tools/better-grep.md
Arbol:cli/arbol_cli/better_grep.py
Arbol:daemons/shared/arbol_shared/universe_wire.py
-->
