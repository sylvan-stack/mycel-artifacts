---
role: authored
---
# Codex Guide: Search and Read Source

Use native Codex CLI shell and filesystem tools. Arbol hosts the CLI; it does
not imply Universe tools, a custom model loop, or disabled network access.
Follow the effective runtime permissions and the user's repository boundaries.

Read a known source location directly with a bounded shell read. For exact
text or filenames, prefer `rg` and `rg --files`. For semantic discovery across
indexed code or documentation, use `mycel search --repo <repo> --only code
"<question>"` or `--only docs` through the shell. See the
[Mycel runbook](../tools/mycel.md) for CLI details.

Inspect search hits in current files before making claims; snippets are leads.
Scope searches to the relevant repositories and inspect actual source for
unindexed repositories. Report missing commands or incomplete index coverage
without treating them as evidence that code does not exist.

Use the selected repository as a standard checkout. Preserve local changes;
do not create nested worktrees or switch branches without explicit approval.
Skills are discovered through the directories in the
[skill creation guide](create-skill.md); no Universe adapter is needed.
