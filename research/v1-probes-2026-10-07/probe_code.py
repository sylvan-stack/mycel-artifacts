import importlib.util, sys
sys.dont_write_bytecode = True
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
import os
from pathlib import Path
R = str(Path(os.environ.get("MYCEL_REPO", Path.home() / "repos/sylvan-stack/mycel_deprecated_v1")) / "mycel/knowledge") + "/"
cc = load("code_chunker_probe", R + "code_chunker.py")
def show(chunks):
    for c in chunks:
        print(f"  {c['symbol']!r:28} {c['kind']:9} {c['line_start']:>3}-{c['line_end']:<3} {c['text'][:50]!r}")

py = '''"""Doc."""
import os

@decorate
def alpha():
    def inner():
        pass
    return 1

X = 1

@dataclass
class Beta:
    """Doc."""
    y: int = 0

    @property
    def val(self):
        return 1

    @val.setter
    def val(self, v):
        pass

    Z = 2

    class Inner:
        def deep(self):
            pass

    async def run(self):
        pass

class Empty:
    pass

if True:
    def hidden():
        pass

async def gamma():
    pass
'''
print("== python"); show(cc.chunk_code("pkg/sample.py", py))
print("== python empty"); show(cc.chunk_code("a.py", ""))
print("== python blank"); show(cc.chunk_code("a.py", "\n\n"))
print("== python comment only"); show(cc.chunk_code("a.py", "# hi\n"))
print("== python syntax error"); show(cc.chunk_code("a.py", "def (:\n  pass\n"))
print("== python class starting with method")
show(cc.chunk_code("a.py", "class K:\n    def m(self):\n        pass\n"))
try:
    print("== python null byte"); show(cc.chunk_code("a.py", "x = 1\x00\n"))
except Exception as e:
    print("  raised", type(e).__name__, e)

sv = '''<script context="module">
  export const a = 1;
</script>
<script lang="ts">
  let b = 2;
</script>

<div>{b}</div>

<style>
  div { color: red; }
</style>
<p>tail</p>
'''
print("== svelte"); show(cc.chunk_code("ui/Thing.svelte", sv))
print("== svelte empty"); show(cc.chunk_code("ui/E.svelte", ""))
print("== svelte markup only"); show(cc.chunk_code("ui/M.svelte", "<div/>\n"))
print("== svelte same line"); show(cc.chunk_code("ui/S.svelte", "<p>x</p><script>let a</script><p>y</p>\n<i/>\n"))
print("== whole-file kinds")
for n in ["x.sh", "x.bash", "x.plist", "x.plist.in", "x.swift"]:
    show(cc.chunk_code(n, "line1\nline2\n"))
print("== unsupported"); print(" ", cc.chunk_code("x.go", "package main\n"), cc.chunk_code("x.md", "# t\n"), cc.chunk_code("x.json", "{}"))
print("== whole-file empty"); show(cc.chunk_code("x.sh", ""))
try:
    import tree_sitter, tree_sitter_typescript, tree_sitter_javascript
    print("tree-sitter available")
except Exception as e:
    print("tree-sitter NOT available:", type(e).__name__, e)
ts = "export function f() {}\nconst g = () => 1;\n"
print("== ts"); show(cc.chunk_code("x.ts", ts))
