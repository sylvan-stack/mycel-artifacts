"""Reproduce the semantic risk of translating legacy Python regexes to JS.

No Mycel imports, configuration, database, provider or repository writes.
Prints results as JSON; run with the desired Python and Node on PATH.
"""
from __future__ import annotations

import hashlib
import json
import platform
import re
import shutil
import subprocess
import unicodedata

SAMPLES = ["cafe", "café", "a\u0085b", "a\ufeffb", "a\u00a0b", "a\u3000b"]

def python_record(value: str) -> dict:
    normalized = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip()
    return {
        "input": value,
        "codepoints": [f"U+{ord(c):04X}" for c in value],
        "identifier_route": re.match(r"^[\w.#/-]+$", value) is not None,
        "normalized": normalized,
        "sha256": hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
    }

node = shutil.which("node")
if not node:
    raise SystemExit("node executable missing from PATH")

js = r"""
const fs = require('node:fs');
const crypto = require('node:crypto');
const samples = JSON.parse(fs.readFileSync(0, 'utf8'));
const records = samples.map(value => {
  const normalized = value.normalize('NFKC').replace(/\s+/g, ' ').trim();
  return {input:value, codepoints:Array.from(value, c => 'U+' + c.codePointAt(0).toString(16).toUpperCase().padStart(4,'0')),
    identifier_route:/^[\w.#/-]+$/.test(value), normalized,
    sha256:crypto.createHash('sha256').update(normalized,'utf8').digest('hex')};
});
process.stdout.write(JSON.stringify({version:process.version,records}));
"""
completed = subprocess.run(
    [node, "-e", js], input=json.dumps(SAMPLES), text=True,
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10, check=True,
)
javascript = json.loads(completed.stdout)
python = [python_record(v) for v in SAMPLES]
differences = [
    {"input":p["input"], "codepoints":p["codepoints"],
     "routing_differs":p["identifier_route"] != j["identifier_route"],
     "hash_differs":p["sha256"] != j["sha256"]}
    for p, j in zip(python, javascript["records"])
    if p["identifier_route"] != j["identifier_route"] or p["sha256"] != j["sha256"]
]
print(json.dumps({
    "date":"2026-10-07", "python_version":platform.python_version(),
    "node_version":javascript["version"], "node_path":node,
    "python":python, "javascript":javascript["records"], "differences":differences,
    "limits":["Tests default regex semantics of a straightforward translation, not a complete parser or engine",
              "No claim that intentional normalization policy changes are forbidden in the rewrite"],
}, indent=2, ensure_ascii=True))
