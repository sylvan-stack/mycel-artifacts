---
role: authored
---
# File pieces

The owner accepted [MYC-19](../specs/19-file-pieces.md) on 9 November 2026.

| Code | Reason |
|---|---|
| `mycel:@code/src/mycel/_capture.py#capture_file_versions` | Select the configured checkout, apply ingest's corpus classification and chunk parsers, and return the two versions independently (MYC-19.1 through MYC-19.3). |
| `mycel:@code/src/mycel/_capture.py#_Capture.working_file` | Walk exact names from the configured root using directory descriptors. Refuse unsafe entries and distinguish a missing file from a failed read (MYC-19.2 and MYC-19.3). |
| `mycel:@code/src/mycel/_capture.py#_Capture.head_commit`, `mycel:@code/src/mycel/_capture.py#_Capture.committed_file` | Resolve `HEAD` once and read the exact regular blob at the requested path. Distinguish an unborn branch from a Git error (MYC-19.2). |
| `mycel:@code/src/mycel/_safeguards.py#validate_read_only_git_args` | Permit exactly the read form of `symbolic-ref` needed to recognize an unborn branch (MYC-19.2 and MYC-19.3). |
| `mycel:@code/src/mycel/_pieces.py#handle_pieces`, `mycel:@code/src/mycel/_pieces.py#_side`, `mycel:@code/src/mycel/_cli.py`, `mycel:@code/src/mycel/_commands.py` | Expose the two version lists through the normal JSON command boundary, with parser names, ranges and exact-byte digests (MYC-19.1 and MYC-D76). |
