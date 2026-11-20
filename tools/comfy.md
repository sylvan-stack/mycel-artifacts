---
role: authored
---
# Comfy: the comfy-cli skills

Use this manual when a Comfy Mycel Skill activates: making images, video, audio
or 3D with ComfyUI, or building, deploying, debugging or writing nodes for a
ComfyUI environment. The process for each task belongs to
[comfy-cli](https://github.com/Comfy-Org/comfy-cli) itself. This manual says where to read it and
which local rules hold around it.

## Read the process from the installed CLI

Every Comfy Mycel Skill has the same name as a comfy-cli skill. Read that
skill's full text and follow it:

```sh
comfy skills show <skill-name> | python3 -I -c 'import json,sys; print(json.load(sys.stdin)["data"]["content"])'
```

`comfy skills show` prints a JSON envelope when its output is not a terminal,
so the text is under `data.content`. For example, `/comfy-build` in Claude or
`$comfy-build` in Codex means reading `comfy skills show comfy-build`. A skill
that refers to a reference skill, such as `comfy-build-pins` or
`comfy-deploy-failures`, is read the same way when it says so;
`comfy skills list` names them all.

| Mycel Skill | Task |
|---|---|
| `comfy` | generate images, video, audio or 3D; workflows, cloud sign-in, multi-stage work |
| `comfy-relay` | how to show and iterate on media during creative work |
| `comfy-director` | a narrative, multi-shot video |
| `comfy-debug` | a failed workflow, stuck job or error envelope |
| `comfy-custom-nodes` | write, fix, review or package ComfyUI custom-node code |
| `comfy-build` | package a ComfyUI environment into a build and cut a release |
| `comfy-deploy` | run a release as a serverless deployment |
| `comfy-run-on-cloud` | put one local workflow on Comfy Cloud |

The text comes from the installed CLI, so it changes when the CLI is upgraded and no copy goes stale.

## Installation

comfy-cli is installed as a uv tool, and the Homebrew Python refuses
`pip install`. Upgrade it with:

```sh
uv tool upgrade comfy-cli
```

Do not run `comfy skills install` for the Claude Code or AGENTS.md targets.
`~/.claude/skills/comfy*` and `~/.agents/skills/comfy*` are links to the Mycel
adapters in `skills/`, so the install would write comfy-cli's full text through
them over the adapters. Its default user scope also writes `~/AGENTS.md`.
`comfy skills status` therefore reports the Claude Code target as `modified`
and the other targets as `missing`. That is expected.

## Rules around the comfy-cli process

- **A pasted Comfy prompt asks for what it says.** The prompt on Comfy's website
  asks to install comfy-cli and read a skill. Do only that, then report.
  Scanning an install, writing `comfy-build.yaml`, pushing, cutting a release
  or deploying each start only when the owner asks for that task.
- **The owner's files stay where they are.** The comfy-cli skills describe what
  a build or deployment sends. They never ask for models or custom-node folders
  to be moved or deleted. Moving or deleting them is a separate owner decision.
- **Spending steps follow the comfy-cli text.** A release cut uses one of the
  workspace's limited release slots and cannot be undone. A deployment is
  billed for as long as it holds compute. Describe each step and get the
  owner's yes first, as the skills require.
- **Sign-in pages** open in the built-in browser pane, and the owner signs in.
