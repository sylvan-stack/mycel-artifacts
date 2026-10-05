---
role: authored
---
# Places API Logs

Use these logs to diagnose Reservble's side of the Syrve integration at reservble.com: inbound plugin and Cloud API events, processing failures, and outbound requests. Plugin-side logs must be obtained separately when needed.

Based on the supplied `SYRVE_DEV_LOGS_ACCESS.md`. The connection values below are fictional placeholders. Configure the actual endpoint, account, log directory and verified host fingerprint locally before use; report actual access failures rather than assuming it remains available.

## Access

- Protocol: **SFTP only**, host `sftp.example.invalid`, port `22`, user `example-log-reader`.
- Remote directory: `/example-logs`.
- Expected ED25519 host fingerprint: `SHA256:uSxJK5U4/qI8zFCQmdObXfEuwqVrz07e3VLgGPBQ8wc`.
- Only listing, reading, and downloading are available. Shell commands, SSH tunnels, and writes are disabled. Do not use remote grep or rsync, which needs remote command execution.
- Verify the host fingerprint before authenticating. Stop on a mismatch and report it to the user; never disable host verification or automatically trust an unverified scanned key.
- Load `RESERVBLE_SFTP_PASSWORD` from the skill's local `credentials.env` file: `~/.agents/skills/places-api-logs/credentials.env` for Codex or `~/.claude/skills/places-api-logs/credentials.env` for Claude. Both resolve to `~/Artifacts/mycel/skills/places-api-logs/credentials.env`. Read the value directly inside the SFTP client process using a dotenv parser with interpolation disabled; do not display the file or source it as shell code. The repository application's `.env` is no longer the credential source for this skill.
- Keep `credentials.env` local, Git-ignored, and permission-restricted to `600`; exclude it from indexing, skill exports, prompts, and CI. Do not print the password, embed it in command text, or commit it. `RESERVBLE_SFTP_PASSWORD` may also be supplied explicitly as a runtime environment variable. If neither source is configured, ask the user to populate the skill's credential file securely rather than paste the password into chat.

Interactive SFTP can establish verified host trust and download a selected file:

```text
sftp -P 22 example-log-reader@sftp.example.invalid
# Check the displayed fingerprint against the value above before accepting.
sftp> ls /example-logs/syrve_plugin_rejected_*
sftp> get /example-logs/syrve_plugin_rejected_2026-09-28.log /absolute/scratch/path/rejected.log
sftp> bye
```

For unattended access, use an available SFTP-capable client with secure credential injection. Check `curl --version` for SFTP support before choosing curl. With curl, use the verified known-hosts entry or pin the host using `--hostpubsha256 'uSxJK5U4/qI8zFCQmdObXfEuwqVrz07e3VLgGPBQ8wc'`. Prefer a permission-restricted curl config or secret supplied through stdin over a password in process arguments. Do not enable verbose credential logging.

Curl URL patterns (supply authentication and host verification separately):

```text
# List filenames:
curl --show-error --fail --list-only sftp://sftp.example.invalid/example-logs/
# Selected daily file:
curl --show-error --fail sftp://sftp.example.invalid/example-logs/syrve_plugin_rejected_2026-09-28.log
# Last approximately 2 MB of the large Cloud API log:
curl --show-error --fail --range -2000000 sftp://sftp.example.invalid/example-logs/syrve_2026-09-28.log
```

These examples illustrate paths and operations, not an already configured connection. Replace dates for the incident. Check transfer success before interpreting an empty result; avoid pipelines that conceal download errors.

## Investigation workflow

1. Establish the incident time and timezone, place ID, and any request, order, or reservation IDs available. Convert the interval to UTC, respecting the incident date's timezone offset. Search adjacent UTC dates when the interval crosses midnight or the timing is uncertain.
2. List remote filenames and select the relevant types below. Files follow `<type>_<YYYY-MM-DD>.log`, with UTC dates and timestamps. Documented retention is 30 days. The current day's files are live and may grow during inspection.
3. Download only the types and dates needed. Use a unique OS temporary directory for disposable downloads, and remove them after diagnosis. Follow the user's Artifact Corpus conventions for any requested durable extracts; do not place logs in the code repository.
4. Search locally with `rg -F` for correlation IDs, then inspect matching JSON records with `jq`. Records are JSON Lines with `timestamp`, `type`, `data`, and sometimes `metadata`. `placeId` may be in `data.placeId`, `metadata.placeId`, or nested batch items; do not assume a single schema across types.
5. Correlate `requestId`, `orderId` / `syrveOrderId`, and `reservationId` across inbound, processing, outbound, and plugin-side logs. Use timestamps and place IDs to narrow ambiguous matches. Do not infer a causal connection from timestamp proximity alone.
6. Report the UTC timeline, relevant filenames and identifiers, error `code` / `stage`, and what the records establish. Separate observed facts from hypotheses and describe any coverage gaps.

The `syrve` log is roughly 60 MB/day. Prefer a bounded tail or streaming local filtering for the relevant interval, avoiding full-file storage unless needed. A byte-range tail may start inside a JSON record: discard only an incomplete leading fragment. A live file may also have an incomplete final line; do not classify that alone as a malformed event. A tail search covers only the downloaded suffix; expand the search when the incident may precede it.

If nothing matches, check that the file exists, the transfer succeeded, UTC conversion is correct, and the relevant batch fields were searched. Within retained dates, a missing type file normally indicates no events of that type were logged that day; an expired file, failed listing, or incomplete download is not evidence that the event never occurred.

## Choose log types

| Type or family | Use |
|---|---|
| `syrve_plugin_v2_webhook` | Inbound V2 batches: orders, reservations, payments, tables |
| `syrve_plugin_v2_event_failed` | V2 events that could not be applied, with `error` |
| `syrve_plugin_v2_dishes_warning`, `syrve_plugin_v2_order_*`, `syrve_plugin_v2_stoplist_*` | V2 dishes, orders, and stop-list processing |
| `syrve_plugin_request`, `syrve_plugin_response`, `syrve_plugin_error` | Outbound plugin requests, including reservation creation/update, and their outcomes |
| `syrve_plugin_rejected` | Rejection `code` and `stage`, e.g. `TABLE_NOT_MAPPED` / `table_resolution` |
| `syrve_plugin_place_loaded`, `syrve_plugin_place_not_found`, `syrve_plugin_placeid_missing`, `syrve_plugin_skipped_no_apikey` | Resolving the place for an inbound event |
| `syrve` | Cloud API webhooks, V1/direct mode; largest daily file |
| `syrve_reservation_create`, `syrve_reservation_response`, `syrve_reservation_cancel`, `syrve_reservation_error`, `syrve_reservation_failed` | Cloud API reservation operations |
| `syrve_orders_error`, `syrve_dishes_warning`, `syrve_spot_warning` | Order errors, unknown dishes, and unknown tables |
| `syrve_sync_tables_*` | Table synchronization outcomes |
| `syrve_webhook_ignored_wrong_mode`, `reserve_ignored_wrong_mode` | Events ignored because the place uses another integration mode |
| `reserve_no_spots`, `reserve_no_place` | Inbound reservations with unresolved tables or place |
| `order-archive` | Closed orders with their dishes |

Wildcards denote filename families; list actual files before downloading. Other integration logs (payments, SMS, email, Google) also exist in this directory and are outside this Syrve workflow.

## Guest data and credentials

Logs contain guest names, phone numbers, and sometimes email addresses and comments. Use them only for integration diagnosis. Minimize extracted records, redact guest details in reports, and do not publish or forward raw logs to third parties. Retain downloads only as long as the investigation requires. Access is logged server-side. If credentials leak or access is no longer needed, tell the user to contact the access provider for rotation or revocation.
