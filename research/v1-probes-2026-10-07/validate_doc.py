import importlib.util, sys, ast, re, os
sys.dont_write_bytecode = True
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
import os
from pathlib import Path
ROOT = str(Path(os.environ.get("MYCEL_REPO", Path.home() / "repos/sylvan-stack/mycel_deprecated_v1"))) + "/"
ch = load("chunker_probe", ROOT + "mycel/knowledge/chunker.py")
doc = (Path(__file__).resolve().parents[1] / "v1-inventory-ingest-and-graph.md").read_text(encoding="utf-8")
defs = {}
def names(path):
    if path not in defs:
        tree = ast.parse(open(ROOT + path, encoding="utf-8").read())
        s = set()
        for n in tree.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)): s.add(n.name)
            elif isinstance(n, ast.ClassDef):
                s.add(n.name)
                for m in n.body:
                    if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)): s.add(f"{n.name}.{m.name}")
        defs[path] = s
    return defs[path]
bad = 0
for c in ch.chunk_markdown(doc):
    refs = ch.parse_source_refs(c["raw_text"])
    print(f"L{c['level']} {c['natural_key'][:70]!r:75} refs={len(refs)} chars={len(c['raw_text'])}")
    for r in refs:
        m = re.fullmatch(r"mycel_deprecated_v1:(mycel/[\w/]+\.py)#([\w.]+)", r)
        if not m:
            print("   NOT IN FORM:", r); bad += 1; continue
        if not os.path.exists(ROOT + m.group(1)) or m.group(2) not in names(m.group(1)):
            print("   MISSING SYMBOL:", r); bad += 1
print("bad:", bad)
print("frontmatter:", ch.parse_frontmatter(doc))
