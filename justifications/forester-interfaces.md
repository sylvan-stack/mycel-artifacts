---
role: authored
---
# Rename keys and saved Justifications

The owner accepted FOR-D118 on 9 November 2026. Its Mycel contracts are
[MYC-19.4](../specs/19-file-pieces.md#requirements) and
[MYC-17.23](../specs/17-justification.md#requirements).

| Code | Reason |
|---|---|
| `mycel:@code/src/mycel/_pieces.py#_side` | Report the existing conservative parser key separately from the digest of the piece's exact bytes. |
| `mycel:@code/src/mycel/_justification_files.py#declarations_from_capture` | Read explicit terminal declarations from each captured per-source artifact, with its piece, Origins, Intention and date. |
| `mycel:@code/src/mycel/_justification_files.py#origin_repositories`, `mycel:@code/src/mycel/_ingest.py#_publication_guards` | Include referenced repositories in the publication guards before changing the Index Store. |
| `mycel:@code/src/mycel/_justification_files.py#reconcile_in_transaction`, `mycel:@code/src/mycel/_ingest.py#_CompleteProducer.__call__` | Reconcile file-owned stated links for the calling clone on the final step of explicit ingest. Report unresolved references and retain independently stated or proven links. |
