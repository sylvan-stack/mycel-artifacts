---
role: authored
---
# Issued identifiers

The owner accepted [MYC-18](../specs/18-identifiers.md) on 9 November 2026.

| Code | Reason |
|---|---|
| `mycel:@code/src/mycel/_cli.py#parse`, `mycel:@code/src/mycel/_cli.py#_handle_ids`, `mycel:@code/src/mycel/_commands.py` | Expose `ids next` and `ids list` through the usual CLI. Validate the series and purpose before opening the store and return the JSON replies in MYC-D75. |
| `mycel:@code/src/mycel/_ids.py#issue_identifier` | Continue `SYL` at 341 and commit each issue with its purpose before replying (MYC-18.1 and MYC-18.2). |
| `mycel:@code/src/mycel/_locks.py#identifier_allocation_guard` | Refuse a concurrent allocator without waiting or writing a lock row. Hold the lock until the allocation transaction ends (MYC-18.2). |
| `mycel:@code/src/mycel/_ids.py#list_identifiers` | Read the committed issues in numerical order from one read-only snapshot (MYC-18.3). |
| `mycel:@code/src/mycel/_store.py#_migrate_issued_identifiers`, `mycel:@code/src/mycel/_store.py#_validate_issued_identifiers` | Add and validate the empty issue table during `init`, with a unique series and number and no repository owner. The format 5 predecessor retains its own catalogue definition (MYC-18.4). |
