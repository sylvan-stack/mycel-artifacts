---
role: authored
---
# Runbook: infer

## Why it exists

The one primitive that runs an agent **session** — a recipe-pinned,
permission-brokered claude conversation — and records its chat history. It is
role-blind: the same tool runs a [Lead](../../arbol_deprecated_v1/GLOSSARY.md#lead) or a
[Delegate](../../arbol_deprecated_v1/GLOSSARY.md#delegate). [Blueprints](../../arbol_deprecated_v1/GLOSSARY.md#blueprint)
run through it; Arbol runs Leads/Delegates through it; `mycel raptor` will use
it for completions. No daemon. It is installed as a standalone PyInstaller executable in `~/bin`.

## Use

```
infer run "<prompt>" --recipe NAME [--restrict R…] [--system TEXT] [--cwd DIR]
infer complete --recipe NAME [--prompt P] [--system S]   # one-shot tool-free completion; prompt from stdin; raw text out (claude OR codex)
                     [--add-dir DIR] [--label k=v…] [--max-minutes N]
                     [--image PATH|URL …]   # attach image(s) to the first turn (codex + claude; repeatable)
infer run --step "msg1" --step "msg2" --recipe NAME   # multi-step, ONE session
        [--context-budget TOKENS] [--max-turns N]
infer sessions [--limit N]                 # recent sessions (chat-history records)
infer show <session-id> [--transcript]     # metadata / full transcript
```

- **Recipe** = a [Brain Recipe](../../arbol_deprecated_v1/GLOSSARY.md#brain-recipe) from
  `~/.infer/config.toml` (model + provider) — **or an ad-hoc descriptor**
  `model:thinking` (e.g. `fable:xhigh`, `haiku:low`; full form
  `ip:model:thinking`) when no configured recipe fits: bare model words
  fable/opus/sonnet/haiku **expand to exact model IDs in the resolver** (the
  CLI's own alias support is inconsistent — `fable` is rejected raw; probed on
  a real run), other model strings pass verbatim;
  thinking ∈ none·minimum·low·medium·high·xhigh·max maps onto the CLI's
  `--effort` tiers (xhigh/max → max). Configured names always win over
  descriptors; a name without `:` never parses as one. **Fuzzy subscription
  words normalize in the engine**: bro/example-org/work → `bro-claude`,
  safe/personal → `safe-claude` (so `bro:fable:max` ≡ `bro-claude:fable:max`);
  a `gpt-*` model implies the codex family. Mapping phrases: drop filler words
  like "sub"/"subscription" — "bro sub fable max" → `bro:fable:max`; no effort
  named → use `high`. (cursor is still refused.)
- **Universe family (daemon-less).** A Universe/codex-family recipe (`ip =
  "universe"` or the legacy `"codex"`, or a `gpt-*` model) routes both
  completions and agent sessions through the independent `universe` executable
  (`infer:infer_engine/universe_agent.py`). Universe owns its login at
  `~/.universe/auth.json`, the Responses transport, and the model/tool loop;
  Infer owns permissions and session recording. Prerequisite: `universe login`
  and `universe` on PATH (or `UNIVERSE_BIN`). Cursor remains unsupported.
- **What a run reports**: `session.json` (and `blueprint run` output) carry
  `recipe`, `model`, `ip`, `effort`; a chain's Output lists each Cell's
  session + the distinct Brain Recipes used. Honesty note (v1): `ip` is
  RECORDED, not enforced — the claude binary's own login is the subscription
  that actually answers; per-subscription routing needs the Arbol driver.
- **Multi-step**: each `--step` is a message sent in ONE session, context
  accumulating; `--context-budget` stops at a step boundary once accumulated
  context exceeds N tokens.
- **Restrictions** (permission broker, auto-accept unless named): `read-only`,
  `no-repo-edit`, `write-to-files=p1,p2`, `write-to-branch`,
  `no-git-mutations`, `no-network`. **No defaults** — empty = permissive; the
  caller governs.
- **Session record**: `~/.infer/sessions/<id>/` = `session.json` + append-only
  `transcript.jsonl` (tail -f for live; read for history). Neutral event
  schema (meta/user/assistant/tool_result/permission/result) is what Arbol
  consumes to project a session as a chat session.
- Exit: `0` ok · `1` no result/provider error · `3` timed out. Use `--json-result` for the structured session result; `infer resolve --recipe NAME` validates a recipe as JSON.

<!-- sources:
infer:infer_engine/cli.py
infer:infer_engine/api.py
infer:infer_engine/broker.py
infer:infer_engine/wrapper.py
-->
