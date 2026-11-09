---
role: authored
spec: MYC-19
status: accepted
---
# Mycel · 19 File pieces

## Purpose

A caller comparing a working file with its last committed version needs the
same names and line ranges that Mycel gives its chunks. Mycel can list the
chunks of both versions directly from the checkout and Git.

## Scope

One file in a configured repository's code checkout. The command reports two
independent lists. The caller determines which pieces changed.

## Behaviour

`mycel pieces` takes a qualified `repo:@code/path` file address as specified in
[MYC-16](16-source-addresses-and-evidence.md#portable-addresses). It uses the
configured checkout of that repository that contains the working directory, or
the configured `code_root` when invoked elsewhere. It captures the working file
and pins the committed side to the `HEAD` commit resolved for the invocation.
The committed side reads the blob at that path and commit. Both sides use the
same corpus classification and chunk parsers as ingest. Each piece has its
parser name, one-based inclusive line range and SHA-256 of its exact chunk
bytes. The name is the code symbol or Markdown chunk name, with the file
address reported separately. Pieces appear in parser order.

An absent side reports `present: false` and an empty piece list. This lets the
caller distinguish a new file from a deleted one. An unborn checkout reports a
null `headCommit` and an absent committed side. A path absent on both sides,
an unsafe path, and a present file that cannot be read or parsed produce an
error. Source reads stay within the selected checkout and its Git objects.
The command uses no Index Store or provider.

## Requirements

| ID | Mycel shall | From v1 | Verified by |
|---|---|---|---|
| MYC-19.1 <!-- 24bf2b7d-d2c2-4f98-a9ce-a9e5f7d930e0 --> | report each present file version using the same chunk names and line ranges as ingest, with a digest of the exact bytes of each chunk | New | unit |
| MYC-19.2 <!-- f0a3b7c2-4fdf-4f5c-b9c7-d7a240e70e70 --> | report the working file and the blob at the resolved HEAD commit separately, distinguish absent versions, and reject a path absent on both sides or a version that cannot be read or parsed | New | unit |
| MYC-19.3 <!-- cd4e11b7-e7de-4e98-896d-15c191c0b88c --> | confine reads to the selected configured checkout and its Git history, and list pieces without changing Git, the files or the Index Store or calling a model | New | unit |
| MYC-19.4 <!-- 802e71c8-f7cf-4c4f-99bc-69e99b36b4fb --> | expose the ingest parser's conservative rename key for each piece when available, separately from its exact-byte digest | New | unit |

## Interface

```sh
mycel pieces cellar:@code/src/net/retry.py
```

The reply contains `path`, `headCommit`, `working` and `committed`. Each side
contains `present` and `pieces`. A piece contains `name`, `lineStart`, `lineEnd`,
`sha256` and `renameKey`. `renameKey` is the conservative identity key ingest
calculates for a parsed code declaration. It is null when no key exists. A
caller only matches a rename by key when the match is unique. If
`RetryPolicy.allow` moves from lines 12–18 to
14–20 with identical bytes, the two pieces share a name and digest and have
separate ranges.

## Known problems

A renamed file is reported at each requested path independently. The caller
can use Git's rename information when it wants to compare those paths.

## Decisions

| ID | Question | Outcome |
|---|---|---|
| MYC-D76 <!-- 0b02803d-1cbb-4cc4-9cc2-ef8c0a6f35cd --> | What should the file listing return? | Accepted by the owner with MYC-19 on 9 November 2026. Return both versions in one JSON response. Include a chunk digest so a caller can detect changed content at the same name and line range. |

## Named checks

MYC-19.1 through MYC-19.4 await named checks under the complete qualification
policy.
