---
role: authored
---
# Evidence for the Mycel 2 language evaluation

This folder supports [the evaluation](../mycel-2-language-evaluation-2026-10.md). It holds reproducible probes, raw results and dated primary-source notes. It is research evidence, not a replacement implementation or a production benchmark.

- `sources.md`: the external documentation claims used, paraphrased and dated 7 October 2026.
- `local-evidence.md`: short source/specification excerpts with paths, line ranges and file hashes.
- `startup-benchmark.py` and `startup-results.json`: randomized repeated command-readiness measurements, with environment isolation, version and revision caveats. No database, provider or ingest operation is dispatched by this probe.
- `archive-inspection.json`: inspection of the installed legacy executable, used to establish help-path behavior and differences from the current deprecated checkout.
- `unicode-probe.py` and `unicode-results.json`: reproduction of query-routing and normalization differences between Python and JavaScript defaults.

Run the Unicode probe with `python3 unicode-probe.py`; it invokes the `node` executable on PATH and prints JSON. The startup probe uses absolute paths captured for this machine; inspect and adapt those paths before reproducing it elsewhere, and create `/tmp/mycel-language-startup` before running it. Warmup and observed-cache results do not represent a deliberately cold filesystem.

The legacy executable and checked-out Python source have different revisions. Their timing difference must not be attributed entirely to extraction, and neither is a complete Python-versus-TypeScript Mycel benchmark.
