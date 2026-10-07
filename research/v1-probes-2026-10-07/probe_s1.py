"""Stub-connection run of the real track_source + ingest_code control flow.
No database: FakeConn interprets only the statements these two functions issue."""
import sys, os, tempfile
sys.dont_write_bytecode = True
from pathlib import Path
sys.path.insert(0, str(Path(os.environ.get("MYCEL_REPO", Path.home() / "repos/sylvan-stack/mycel_deprecated_v1"))))
from mycel.knowledge import store
store._schema_ready = True   # skip DDL

class Cur:
    def __init__(self, rows=None): self.rows = rows or []; self.rowcount = len(self.rows)
    def fetchone(self): return self.rows[0] if self.rows else None
    def fetchall(self): return self.rows

class FakeConn:
    def __init__(self): self.docs = {}; self.chunks = {}; self.unhandled = []
    def execute(self, sql, p=()):
        s = " ".join(sql.split())
        D, C = self.docs, self.chunks
        if s.startswith("SELECT id FROM kn_documents WHERE path=%s AND source_type=%s ORDER BY"):
            rows = [d for d in D.values() if d["path"] == p[0] and d["source_type"] == p[1]]
            rows.sort(key=lambda d: (d["state"] == "present", d["last_seen"]), reverse=True)
            return Cur(rows)
        if s.startswith("INSERT INTO kn_documents (id,path,content_hash,source_type,state,first_seen,last_seen,last_run) "):
            did, path, h, st, fs, ls = p
            if did in D: D[did].update(content_hash=h, state="present", last_seen=ls)
            else: D[did] = dict(id=did, path=path, content_hash=h, source_type=st, state="present", first_seen=fs, last_seen=ls, repo="arbol")
            return Cur()
        if s.startswith("SELECT id, content_hash FROM kn_documents WHERE path=%s AND source_type='code' AND state='present' AND repo=%s"):
            return Cur([d for d in D.values() if d["path"] == p[0] and d["source_type"] == "code" and d["state"] == "present" and d["repo"] == p[1]])
        if s.startswith("UPDATE kn_documents SET content_hash=%s, last_seen=%s WHERE id=%s"):
            D[p[2]].update(content_hash=p[0], last_seen=p[1]); return Cur()
        if s.startswith("INSERT INTO kn_documents (id,path,content_hash,source_type,state,first_seen,last_seen,last_run,repo)"):
            did, path, h, fs, ls, repo = p
            D[did] = dict(id=did, path=path, content_hash=h, source_type="code", state="present", first_seen=fs, last_seen=ls, repo=repo); return Cur()
        if s.startswith("SELECT id,natural_key,content_hash FROM kn_chunks WHERE document_id=%s AND origin='code' AND state='present'"):
            return Cur([c for c in C.values() if c["document_id"] == p[0] and c["state"] == "present"])
        if s.startswith("INSERT INTO kn_chunks (id,document_id,natural_key,ordinal,level,raw_text,"):
            cid, did, nk, o, text, ch, lang, kind, a, b, fs, ls, repo = p
            C[cid] = dict(id=cid, document_id=did, natural_key=nk, raw_text=text, content_hash=ch, state="present", lang=lang, symbol_kind=kind, embedding="VEC"); return Cur()
        if s.startswith("UPDATE kn_chunks SET raw_text=%s,content_hash=%s,"):
            C[p[-1]].update(raw_text=p[0], content_hash=p[1], embedding=None); return Cur()
        if s.startswith("UPDATE kn_chunks SET ordinal=%s,line_start=%s"): return Cur()
        if s.startswith("UPDATE kn_chunks SET state='absent', last_seen=%s WHERE id=%s"):
            C[p[1]]["state"] = "absent"; return Cur()
        if s.startswith("SELECT id,path FROM kn_documents WHERE source_type='code' AND state='present' AND repo=%s"):
            return Cur([d for d in D.values() if d["source_type"] == "code" and d["state"] == "present" and d["repo"] == p[0]])
        if s.startswith("SELECT path FROM kn_documents WHERE source_type='code' AND state='present' AND repo=%s"):
            return Cur([d for d in D.values() if d["source_type"] == "code" and d["state"] == "present" and d["repo"] == p[0]])
        self.unhandled.append(s[:90]); return Cur()

def texts(conn): return sorted((c["natural_key"], c["state"], c["raw_text"].replace("\n", "\\n"), c["embedding"]) for c in conn.chunks.values())

def track_like_refresh(conn, base, repo):
    # verbatim shape of store.refresh lines 669-675
    from pathlib import Path
    b = Path(base).expanduser()
    for r in conn.execute("SELECT path FROM kn_documents WHERE source_type='code' AND state='present' "
                          "AND repo=%s", (repo,)).fetchall():
        q = b / r["path"]
        if q.exists():
            store.track_source(conn, r["path"], read_path=str(q))

for label, with_track in (("A: ingest_code only", False), ("B: track_source (as refresh does), then ingest_code", True)):
    with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(__file__))) as base:
        f = os.path.join(base, "app.py")
        open(f, "w").write("def tally():\n    return 1\n")
        conn = FakeConn()
        r1 = store.ingest_code(conn, base, None, repo="zeta")
        open(f, "w").write("def tally():\n    return 2\n")
        if with_track:
            track_like_refresh(conn, base, "zeta")
        r2 = store.ingest_code(conn, base, None, repo="zeta")
        print(label)
        print("  first :", {k: v for k, v in r1.items() if k != "items"})
        print("  second:", {k: v for k, v in r2.items() if k != "items"}, [i["action"] for i in r2["items"]])
        print("  chunks:", texts(conn))
        print("  unhandled:", conn.unhandled)
