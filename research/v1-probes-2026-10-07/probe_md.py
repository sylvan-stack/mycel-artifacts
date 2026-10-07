import importlib.util, sys, json
sys.dont_write_bytecode = True
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
import os
from pathlib import Path
R = str(Path(os.environ.get("MYCEL_REPO", Path.home() / "repos/sylvan-stack/mycel_deprecated_v1")) / "mycel/knowledge") + "/"
ch = load("chunker_probe", R + "chunker.py")

print("== heading regex")
for s in ["# C#", "#NoSpace", "####### seven", "  # indented", "# ", "## Title ##", "#\tTab", "#", "###### six", "# a # b #", "# Title \\#"]:
    m = ch.HEADING_RE.match(s)
    print(repr(s), "->", (len(m.group(1)), m.group(2)) if m else None)

print("== frontmatter")
cases = {
 "plain": "---\nstatus: heartwood\nimplemented: 2031-01-02\noutdated: 2032-03-04\nrole: Derived\ngenerated: Yes\nsources:\n  - zeta:lib/a.py#Foo\n  - zeta:docs/b.md#Some Heading\n---\n# T\n",
 "quoted": "---\nstatus: \"heartwood\"\nrole: 'authored'\n---\n# T\n",
 "flow": "---\nsources: [zeta:a.py, zeta:b.py]\n---\n",
 "scalar": "---\nsources: zeta:a.py, zeta:b.py#X\n---\n",
 "bom": "﻿---\nrole: authored\n---\n",
 "noclose": "---\nrole: authored\n# T\n",
 "dots": "---\nrole: authored\n...\n",
 "impl_without_hw": "---\nimplemented: 2031-01-02\n---\n",
 "blank_breaks_list": "---\nsources:\n  - zeta:a.py\n\n  - zeta:b.py\n---\n",
 "list_then_scalar_same_key": "---\nsources: zeta:x.py\nsources:\n - zeta:y.py\n---\n",
 "late_close": "---\n" + "\n".join(f"k{'a'*1}: v" for _ in range(90)) + "\nrole: authored\n---\n",
 "indented_key": "---\n  role: authored\n---\n",
 "key_digit": "---\nrole2: authored\nrole: authored\n---\n",
 "first_line_spaces": "  ---  \nrole: derived\n---\n",
 "crlf": "---\r\nrole: derived\r\n---\r\n",
 "upperkey": "---\nROLE: AUTHORED\nStatus: Heartwood\nGenerated: TRUE\n---\n",
 "gen_false": "---\ngenerated: false\n---\n",
}
for k, t in cases.items():
    print(k, "->", ch.parse_frontmatter(t))

print("== chunk_markdown with frontmatter")
doc = "---\nrole: authored\n# yaml comment\nsources:\n - zeta:a.py\n---\nIntro text.\n\n# Top\nbody a\n## Sub\nbody b\n```\n# not heading\n```\n### Deep\n# Second\n## Sub\nbody b\n#### Skip\n"
for c in ch.chunk_markdown(doc):
    print({k: c[k] for k in ("ordinal","level","natural_key","parent","title")}, repr(c["raw_text"][:40]), c["content_hash"][:8], c["title_hash"][:8])
print("frontmatter parsed:", ch.parse_frontmatter(doc))

print("== no heading / empty")
print(ch.chunk_markdown(""))
print(ch.chunk_markdown("\n\n  \n"))
print([(c["natural_key"], c["level"]) for c in ch.chunk_markdown("just text\nmore")])
print([(c["natural_key"], c["title"], c["title_hash"]) for c in ch.chunk_markdown("# \nbody")])

print("== hash normalisation")
a = ch.chunk_markdown("# T\nfoo  bar\n\nbaz\n")[0]; b = ch.chunk_markdown("# T\nfoo bar baz")[0]
print("body ws-insensitive:", a["content_hash"] == b["content_hash"], "raw equal:", a["raw_text"] == b["raw_text"])
c1 = ch.chunk_markdown("# T\nx")[0]; c2 = ch.chunk_markdown("# U\nx")[0]
print("title change keeps content_hash:", c1["content_hash"] == c2["content_hash"], "title_hash differs:", c1["title_hash"] != c2["title_hash"])
print("empty body hash:", ch.content_hash(""), "== sha(''):", ch.content_hash("") == ch.sha(""))
print("NFKC:", ch.content_hash("ﬁ") == ch.content_hash("fi"))

print("== fences")
t = "# A\n```md\n```python\n# H inside?\n```\n# B\n"
print([(c["natural_key"]) for c in ch.chunk_markdown(t)])
t = "# A\n~~~\n```\n# x\n~~~\n# B\n"
print([(c["natural_key"]) for c in ch.chunk_markdown(t)])
t = "# A\n    ```\n# x\n    ```\n# B\n"
print("indented fence:", [(c["natural_key"]) for c in ch.chunk_markdown(t)])
t = "# A\n```\n# never closed\n# B\n"
print("unclosed:", [(c["natural_key"]) for c in ch.chunk_markdown(t)])
t = "Title\n=====\ntext\nSub\n---\n"
print("setext:", [(c["natural_key"]) for c in ch.chunk_markdown(t)])

print("== source refs")
samples = {
 "basic": "# S\n<!-- sources:\nzeta:lib/a.py#Foo\nzeta:docs/b.md#Some Heading, zeta:c.py\n-->\n",
 "inline_one_line": "x <!-- sources: zeta:a.py#f --> y",
 "fenced": "```\n<!-- sources:\nzeta:a.py\n-->\n```\n",
 "inline_code": "`<!-- sources: zeta:a.py -->`",
 "upper": "<!-- SOURCES: zeta:a.py -->",
 "invalid": "<!-- sources:\nnot a ref\nzeta: spaced\nhttp://example.test/x\nzeta:ok.py\nrepo with space:x\nzeta@feat:lib/a.py\n-->",
 "two_blocks": "<!-- sources: zeta:a.py -->\ntext\n<!-- sources: zeta:b.py, zeta:a.py -->",
 "nospace": "<!--sources:zeta:a.py-->",
 "other_comment": "<!-- source: zeta:a.py -->",
 "trailing_text": "<!-- sources: zeta:a.py (the main file) -->",
 "bullets": "<!-- sources:\n- zeta:a.py\n* zeta:b.py\n-->",
}
for k, t in samples.items():
    print(k, "->", ch.parse_source_refs(t))
