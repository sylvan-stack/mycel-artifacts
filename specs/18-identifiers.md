---
role: authored
spec: MYC-18
status: review
---
# Mycel · 18 Issued identifiers

## Purpose

Mycel issues the numbers used for new work and keeps a record of what each
number was issued for. A series continues after the numbers already in use.

## Scope

Issuing and listing identifiers in the configured [Index Store](06-index-store.md).
The caller owns the documents it names with those identifiers.

## Behaviour

The first supported series is `SYL`. Numbers through 340 are reserved by prior
use, so the first issue is `SYL-341`. Series names are case-sensitive. Unknown
series and missing or blank purposes return `invalid_input` before any write.

`next` takes the allocation lock for the series without waiting. It finds the
next number and records it with the caller's purpose in one transaction. The
store enforces uniqueness on the series and number, and the reply identifies
the number only after commit. A concurrent allocation that cannot take the
lock returns `busy` and writes nothing. If the transaction rolls back, the
number is still available. A committed issue stays in the record even when the
caller loses the reply or abandons the work. Repeating a purpose requests a
fresh number. After a lost reply, the caller can inspect `list` before asking
for another.

`list` returns the committed issues for one series in ascending numerical
order. It returns an empty list before the first issue. It only reads the
store and can run during allocation.

The issues belong to the store and survive repository removal and index
collection. An issue is the durable record of the allocation. Format 6 adds
the empty issue table. `mycel init` creates it for new stores or adds it in
the format 5-to-6 migration, preserving existing data. A Build for format 5
refuses the migrated store under [MYC-6](06-index-store.md#making-and-changing-the-structure).

## Requirements

| ID | Mycel shall | From v1 | Verified by |
|---|---|---|---|
| MYC-18.1 <!-- ca944a06-654b-49c9-ac50-25e7d4a5489c --> | allocate a number in a recognized series from its first available number onward, with the supplied purpose, and refuse unknown series or blank purposes | New | store |
| MYC-18.2 <!-- 4af18f1f-44ee-4e9c-a4a2-df6ca8097ef9 --> | issue a series number at most once by committing the number and purpose together before replying, and return `busy` without writing if another allocation holds the series lock | New | store |
| MYC-18.3 <!-- c4b28df5-1103-4151-965b-f520e745afd5 --> | list a series's committed identifiers and purposes in ascending numeric order from one read-only snapshot | New | store |
| MYC-18.4 <!-- 68533d29-80ab-4739-bcfd-854d3feb0b74 --> | create the allocation record structure only through `mycel init`, preserve existing store data on migration, and keep issued identifiers independent of repository data and its collection | New | store |

## Interface

Both commands use the configured Index Store from any working directory and
follow [MYC-0's command-line contract](00-overview-and-legacy-map.md#the-command-line).
For example, the first invocation could be:

```sh
mycel ids next SYL --for "Document archive imports"
mycel ids list SYL
```

`next` returns `{"id":"SYL-341"}`. The subsequent `list` returns:

```json
{"series":"SYL","ids":[{"id":"SYL-341","for":"Document archive imports"}]}
```

## Known problems

Identifiers issued before the cutover remain in their original records. They
are outside the allocation list and remain reserved by the series floor.

## Decisions

| ID | Question | Outcome |
|---|---|---|
| MYC-D74 <!-- 072e5887-1991-454d-acb0-53352d95c20e --> | Who issues new numbers? | The owner directed on 9 November 2026 that Mycel issue new numbers. The initial `SYL` series continues at 341. |
| MYC-D75 <!-- eda4e219-3349-4b3d-891a-669f69e6d30d --> | What do the commands return? | Proposed for review. Use Mycel's single-JSON-document convention. `next` returns an `id`. `list` returns the series and the committed `id` and `for` pairs. |
