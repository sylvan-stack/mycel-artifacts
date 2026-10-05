"""Shared plumbing for Blueprint Chains.

Provides append-only process logs, resume, abort semantics, parallel independent
Cells, nested-chain labels, deterministic Tool calls, Blueprint subprocesses,
and inline agent lambdas through the standalone infer CLI.
"""
from __future__ import annotations

import concurrent.futures
import datetime
import json
import os
import re
import shutil
import subprocess
import sys

CHAINS_ROOT = os.path.expanduser(os.environ.get("INFER_CHAINS", "~/.infer/chains"))
MYCEL_BIN_DIR = os.path.expanduser(os.environ.get("MYCEL_BIN_DIR", ""))
DEFAULT_LAMBDA_RECIPE = "sonnet-summariser"


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _executable(name: str) -> str:
    candidate = os.path.join(MYCEL_BIN_DIR, name) if MYCEL_BIN_DIR else ""
    return candidate if candidate and os.path.exists(candidate) else (shutil.which(name) or name)


class Chain:
    def __init__(self, name: str, run_key: str, total_steps: int, *,
                 resume: bool = True, recipe: "str | None" = None,
                 default_recipe: "str | None" = None, pin_recipe: str = "inherit"):
        self.name = name
        self.total = total_steps
        self.recipe = pin_recipe if pin_recipe and pin_recipe != "inherit" else recipe or default_recipe
        self.parent = os.environ.get("INFER_CHAIN_RUN") or ""
        self.completed: set = set()
        existing = self._find_unfinished(name, run_key) if resume else None
        if existing:
            self.run_id, self.dir, meta = existing
            self.completed = set(meta.get("completed_steps") or [])
            self._log("resumed", run_id=self.run_id, log_dir=self.dir,
                      completed_steps=sorted(self.completed), prior_status=meta.get("status"))
            if meta.get("status") == "aborted":
                self._meta(None, status="running", ended_at=None)
        else:
            stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
            base = f"{name}-{run_key}-{stamp}"
            for i in range(100):
                self.run_id = base if i == 0 else f"{base}-{i + 1}"
                self.dir = os.path.join(CHAINS_ROOT, self.run_id)
                try:
                    os.makedirs(self.dir)
                    break
                except FileExistsError:
                    continue
            self._meta({"chain": name, "run_key": run_key, "run_id": self.run_id,
                        "parent": self.parent, "total_steps": total_steps,
                        "started_at": _now(), "status": "running", "completed_steps": []})
            self._log("started", run_id=self.run_id, log_dir=self.dir,
                      total_steps=total_steps, parent=self.parent)
        self.summary: list = []

    def _meta(self, obj: "dict | None" = None, **updates) -> dict:
        path = os.path.join(self.dir, "chain.json")
        if obj is None:
            with open(path, encoding="utf-8") as handle:
                obj = json.load(handle)
            obj.update(updates)
        temp = path + ".tmp"
        with open(temp, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(obj, indent=2))
        os.replace(temp, path)
        return obj

    def _log(self, event: str, **fields) -> None:
        record = {"ts": _now(), "event": event, **fields}
        with open(os.path.join(self.dir, "chain.jsonl"), "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")
            handle.flush()
        print(self._human_line(event, fields), file=sys.stderr)

    def _human_line(self, event: str, fields: dict) -> str:
        if event.startswith("step_") and "step" in fields:
            verb = event.replace("step_", "")
            desc = " ".join(x for x in (fields.get("kind"), fields.get("blueprint") or fields.get("title")) if x)
            tail = fields.get("reason") or (f"session {fields['session_id']}" if fields.get("session_id") else "")
            return " · ".join(x for x in (f"[chain {self.name}] Cell {fields['step']}/{self.total} {verb}", desc, tail) if x)
        shown = {k: v for k, v in fields.items() if k in
                 ("run_id", "log_dir", "reason", "session_id", "after_step",
                  "total_steps", "completed_steps")}
        return f"[chain {self.name}] {event} " + " ".join(f"{k}={v}" for k, v in shown.items())

    @staticmethod
    def _find_unfinished(name: str, run_key: str):
        if not os.path.isdir(CHAINS_ROOT):
            return None
        for run_id in sorted(os.listdir(CHAINS_ROOT), reverse=True):
            if not run_id.startswith(f"{name}-{run_key}-"):
                continue
            path = os.path.join(CHAINS_ROOT, run_id, "chain.json")
            try:
                with open(path, encoding="utf-8") as handle:
                    meta = json.load(handle)
            except OSError:
                continue
            if meta.get("status") in ("running", "aborted"):
                return run_id, os.path.join(CHAINS_ROOT, run_id), meta
        return None

    def _done_step(self, n: int, **fields) -> None:
        self.completed.add(n)
        self._meta(None, completed_steps=sorted(self.completed))
        self._log("step_finished", step=n, **fields)

    def labels(self, n: int) -> dict:
        labels = {"chain": self.name, "chain_run": self.run_id, "chain_step": n}
        if self.parent:
            labels["chain_parent"] = self.parent
        return labels

    def _env(self) -> dict:
        return {**os.environ, "INFER_CHAIN_RUN": self.run_id}

    def skip_if_done(self, n: int, title: str) -> bool:
        if n in self.completed:
            self._log("step_skipped", step=n, title=title, reason="already completed (resume)")
            return True
        self._log("step_started", step=n, title=title)
        return False

    def tool(self, n: int, title: str, argv: list, timeout: int = 600,
             resumable: bool = False) -> "str | None":
        if resumable and n in self.completed:
            self._log("step_skipped", step=n, title=title, reason="resume")
            return None
        self._log("step_started", step=n, title=title, kind="tool", argv=argv[:4])
        command = [_executable(argv[0]), *argv[1:]]
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, env=self._env())
        if result.returncode != 0:
            self.abort(n, f"tool failed: {result.stderr.strip()[-300:]}")
        self.summary.append({"step": n, "kind": "tool", "title": title})
        self._done_step(n, kind="tool")
        return result.stdout

    def blueprint(self, n: int, title: str, name: str, max_minutes: float = 30,
                  recipe: "str | None" = None, tolerate_unmet: bool = False,
                  **inputs) -> "dict | None":
        if n in self.completed:
            self._log("step_skipped", step=n, title=title, reason="resume")
            return None
        self._log("step_started", step=n, title=title, kind="blueprint", blueprint=name)
        argv = [_executable("blueprint"), "run", name, "--max-minutes", str(max_minutes)]
        effective_recipe = recipe or self.recipe
        if effective_recipe:
            argv += ["--recipe", effective_recipe]
        for key, value in self.labels(n).items():
            argv += ["--label", f"{key}={value}"]
        for key, value in inputs.items():
            argv += ["--input", f"{key}={value}"]
        result = subprocess.run(argv, capture_output=True, text=True,
                                timeout=int(max_minutes * 60) + 120, env=self._env())
        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.abort(n, f"blueprint {name}: unparseable output — {result.stdout[-200:]} / {result.stderr[-200:]}")
        output["exit_code"] = result.returncode
        self.summary.append({"step": n, "kind": "blueprint", "name": name,
                             "recipe": output.get("recipe"), "session_id": output.get("session_id"),
                             "done_when_met": output.get("done_when_met")})
        if output.get("is_error") or output.get("exit_code") == 5:
            self.abort(n, f"blueprint {name} SESSION ERROR: {output.get('result_tail') or '(no message)'} (session {output.get('session_id')})")
        if result.returncode != 0 or not output.get("done_when_met"):
            tail = output.get("result_tail") or ""
            detail = f"blueprint {name} done_when: {output.get('done_when')}" + (f" — last result: {tail}" if tail else "") + f" (session {output.get('session_id')})"
            if tolerate_unmet:
                self._log("step_unmet_tolerated", step=n, reason=detail)
            else:
                self.abort(n, detail)
        self._done_step(n, kind="blueprint", session_id=output.get("session_id"), recipe=output.get("recipe"))
        return output

    def lam(self, n: int, title: str, prompt: str, *, cwd: str,
            recipe: "str | None" = None, max_minutes: float = 10,
            restrictions: "list | None" = None, images: "list | None" = None) -> "dict | None":
        if n in self.completed:
            self._log("step_skipped", step=n, title=title, reason="resume")
            return None
        recipe = recipe or self.recipe or DEFAULT_LAMBDA_RECIPE
        self._log("step_started", step=n, title=title, kind="lambda")
        argv = [_executable("infer"), "run", prompt, "--recipe", recipe,
                "--cwd", cwd, "--add-dir", os.path.expanduser("~/Artifacts"),
                "--max-minutes", str(max_minutes)]
        for restriction in restrictions or ["no-repo-edit", "no-git-mutations"]:
            if isinstance(restriction, dict) and "write-to-files" in restriction:
                restriction = "write-to-files=" + ",".join(restriction["write-to-files"])
            argv += ["--restrict", str(restriction)]
        for image in images or []:
            argv += ["--image", image]
        for key, value in {"role": "delegate", **self.labels(n)}.items():
            argv += ["--label", f"{key}={value}"]
        try:
            result = subprocess.run(argv, capture_output=True, text=True,
                                    timeout=int(max_minutes * 60) + 120, env=self._env())
        except subprocess.TimeoutExpired:
            self.abort(n, "lambda timed out")
        if result.returncode != 0:
            self.abort(n, f"lambda SESSION ERROR: {result.stderr.strip()[-300:]}")
        output = {"result": result.stdout, "session_id": None, "recipe": recipe,
                  "timed_out": False, "is_error": False, "num_turns": 1}
        self.summary.append({"step": n, "kind": "lambda", "title": title,
                             "recipe": recipe, "session_id": None})
        self._done_step(n, kind="lambda", session_id=None, recipe=recipe)
        return output

    @staticmethod
    def parallel(thunks: list) -> list:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, len(thunks))) as executor:
            futures = [executor.submit(thunk) for thunk in thunks]
            results, first_error = [], None
            for future in futures:
                try:
                    results.append(future.result())
                except BaseException as error:  # noqa: BLE001
                    results.append(None)
                    first_error = first_error or error
            if first_error:
                raise first_error
        return results

    def _recipes(self) -> list:
        seen = []
        for step in self.summary:
            recipe = step.get("recipe")
            if recipe and recipe not in seen:
                seen.append(recipe)
        return seen

    def _render_output(self, output_files: "list | None", note: str) -> str:
        lines = [f"## {self.name} — {note}"]
        if self.summary:
            lines += ["", "Cells:"]
            for step in self.summary:
                label = step.get("name") or step.get("title") or ""
                bit = f"- Cell {step.get('step')}/{self.total} · {step.get('kind')}"
                if label:
                    bit += f" {label}"
                if step.get("session_id"):
                    bit += f" · session {step['session_id']}"
                lines.append(bit)
        if output_files:
            lines += ["", "Files:"]
            for path in output_files:
                absolute = os.path.abspath(os.path.expanduser(path))
                lines.append(f"- [{os.path.basename(absolute)}]({absolute})")
        if self._recipes():
            lines += ["", f"Brain Recipe(s): {', '.join(self._recipes())}"]
        return "\n".join(lines)

    def _emit(self, output: dict, output_files: "list | None", note: str) -> dict:
        output["recipes"] = self._recipes()
        output["output"] = self._render_output(output_files, note)
        print(json.dumps(output, indent=2))
        print("\n" + output["output"], file=sys.stderr)
        return output

    def abort(self, n: int, message: str) -> None:
        self._log("aborted", step=n, reason=message)
        self._meta(None, status="aborted", ended_at=_now(), aborted_at_step=n, abort_reason=message)
        print(json.dumps({"chain": self.name, "chain_run": self.run_id,
                          "status": "aborted", "aborted_at_step": n, "error": message,
                          "log_dir": self.dir, "resume": "re-run the same command to resume from this Cell"}, indent=2))
        print(f"\nCHAIN ABORTED at Cell {n} — {message}\n  log: {self.dir}/chain.jsonl", file=sys.stderr)
        raise SystemExit(6)

    def pause(self, after_step: int, *, output_files: "list | None" = None, **extra) -> dict:
        self._log("paused", after_step=after_step)
        output = {"chain": self.name, "chain_run": self.run_id, "log_dir": self.dir,
                  "status": "paused (resumable)", "completed_steps": sorted(self.completed),
                  "steps": self.summary, **extra}
        return self._emit(output, output_files, f"paused after step {after_step} (resumable)")

    def finish(self, *, output_files: "list | None" = None, **extra) -> dict:
        self._meta(None, status="done", ended_at=_now())
        self._log("finished")
        return self._emit({"chain": self.name, "chain_run": self.run_id,
                           "log_dir": self.dir, "steps": self.summary, **extra},
                          output_files, "done")


def slugify(text: str, limit: "int | None" = None) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return value[:limit] if limit else value


def frontmatter(path: str) -> dict:
    output = {}
    with open(path, encoding="utf-8") as handle:
        lines = handle.read().split("\n")
    if not lines or lines[0].strip() != "---":
        return output
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^(\w[\w_-]*):\s*(.+)$", line)
        if match:
            try:
                output[match.group(1)] = json.loads(match.group(2))
            except json.JSONDecodeError:
                output[match.group(1)] = match.group(2)
    return output
