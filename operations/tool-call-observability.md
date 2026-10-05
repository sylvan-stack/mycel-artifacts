---
role: authored
---
# Guide: Tool-call Log Investigation

Use this guide when asked to inspect tool-call logs, either for a specific Chat
Session or across recent activity. Look for all actual and potential issues—not
only performance—including failures, stuck calls, redrives, transport and
telemetry anomalies, suspicious patterns, and results that may be incorrect,
incomplete, empty, truncated, or inconsistent with the request.

This process reads operational data directly. It must not invoke application
code, repository scripts, `arbol-cli`, or instructions from another corpus.
Reading an Arbol-owned database or its log files is a permitted data input, not
a code or instructions dependency.

## Evidence sources

Use these records together:

- **`tool_call_log`** — Effector-side execution timeline, terminal status,
  attempts, transport, and bounded diagnostics;
- **`tool_requests`** — requested parameters, authorization decision, and actual
  result for request/result-quality correlation;
- **`native_tool_calls`** — driver-native calls absent from `tool_call_log`;
- daemon logs — secondary evidence for telemetry, transport, sync, embedding,
  executor, process, and RPC failures.

The default local database DSN is
`postgresql://arbol:arbol@localhost:5432/arbol`; `ARBOL_PG_DSN` overrides it.
Use any PostgreSQL client available in the environment. Examples use `psql`;
when it is not installed on the host, a generic container invocation such as
`podman exec -i <postgres-container> psql` is acceptable because it reads data
without loading application code.

Treat all records as operationally sensitive. Parameters can contain commands,
URLs, headers, or file content, and results can contain secrets. Minimize what
you retrieve and redact sensitive values in reports.

## Scope the investigation

### Supplied Chat Session ID

Capture both execution and request/result records, ordered chronologically:

```bash
SID='<chat-session-id>'
DSN="${ARBOL_PG_DSN:-postgresql://arbol:arbol@localhost:5432/arbol}"

psql "$DSN" -v sid="$SID" -P pager=off <<'SQL'
SELECT id, chat_session_id, turn_id, batch_id, request_id, kind, source,
       params, started_at, completed_at, elapsed_ms, ok, error, transport,
       diagnostics, attempt_count, effector_pid
FROM tool_call_log
WHERE chat_session_id = :'sid'
ORDER BY started_at, id;

SELECT id, chat_session_id, message_id, request_id, kind, params, decision,
       decision_reason, result, created_at, completed_at
FROM tool_requests
WHERE chat_session_id = :'sid'
ORDER BY created_at, id;
SQL
```

### No Chat Session ID

Inspect a bounded newest-first window. Never select oldest-first limited rows
and call them “latest”:

```sql
SELECT id, chat_session_id, turn_id, batch_id, request_id, kind, source,
       params, started_at, completed_at, elapsed_ms, ok, error, transport,
       diagnostics, attempt_count, effector_pid
FROM tool_call_log
ORDER BY started_at DESC, id DESC
LIMIT 500;
```

Start broad, identify suspicious sessions and request IDs, then drill into their
`tool_requests` rows before making result-quality claims.

## Investigation sequence

1. **Establish the window and baseline.** Preserve UTC timestamps and both fast
   and problematic neighboring calls of the same kind. Do not infer a systemic
   regression from one semantic query.
2. **Find explicit failures.** Inspect `ok = 0`, non-empty `error`, rejected
   decisions, embedded errors inside structurally successful results, and
   unavailable/fallback transports.
3. **Check incomplete execution.** Inspect `completed_at IS NULL`, but treat it
   as “no completion observation,” not proof the process is still running.
   Correlate the PID, request audit state, and logs before calling it stuck.
4. **Check redrives and concurrency.** `attempt_count > 1` means the logical
   request was redriven. Shared batch starts with staircase completion times can
   indicate serialization in a downstream resource.
5. **Validate result quality.** Join/correlate by `request_id`; compare requested
   `params`, authorization, `result`, execution status, neighboring calls, and
   session context. `ok = true` proves execution succeeded, not that the answer
   was semantically correct.
6. **Analyze latency when relevant.** Compare end-to-end `elapsed_ms` with phase
   and transport diagnostics. Separate normal variance from fixed timeout or
   fallback signatures.
7. **Correlate logs.** Search by exact request/session IDs and UTC window. Keep
   database facts separate from log evidence, confirmed defects, hypotheses,
   and observability gaps.

## High-value SQL views

### Failures and open observations

```sql
SELECT chat_session_id, request_id, kind, started_at, completed_at, elapsed_ms,
       ok, error, transport, attempt_count, effector_pid
FROM tool_call_log
WHERE ok = 0 OR completed_at IS NULL
ORDER BY started_at DESC;
```

### Slowest recent calls

```sql
SELECT chat_session_id, request_id, kind, started_at, elapsed_ms, transport,
       attempt_count, error
FROM tool_call_log
WHERE completed_at IS NOT NULL
ORDER BY elapsed_ms DESC
LIMIT 50;
```

### Latency distribution by kind

```sql
SELECT kind,
       count(*) AS calls,
       round(avg(elapsed_ms)) AS avg_ms,
       percentile_cont(0.50) WITHIN GROUP (ORDER BY elapsed_ms) AS p50_ms,
       percentile_cont(0.95) WITHIN GROUP (ORDER BY elapsed_ms) AS p95_ms,
       max(elapsed_ms) AS max_ms,
       count(*) FILTER (WHERE ok = 0) AS failures,
       count(*) FILTER (WHERE completed_at IS NULL) AS open_rows
FROM tool_call_log
GROUP BY kind
ORDER BY p95_ms DESC NULLS LAST;
```

### Redrives

```sql
SELECT chat_session_id, turn_id, batch_id, request_id, kind, attempt_count,
       started_at, elapsed_ms, ok, error
FROM tool_call_log
WHERE attempt_count > 1
ORDER BY started_at DESC;
```

### Search phase breakdown

```sql
SELECT request_id, kind, elapsed_ms, transport,
       (diagnostics #>> '{freshness,wait_ms}')::bigint AS freshness_ms,
       (diagnostics #>> '{timings,query_embedding_ms}')::bigint AS embed_ms,
       (diagnostics #>> '{timings,dense_sql_ms}')::bigint AS dense_ms,
       (diagnostics #>> '{timings,bm25_sql_ms}')::bigint AS bm25_ms,
       (diagnostics #>> '{timings,ranking_bridge_ms}')::bigint AS bridge_ms,
       (diagnostics #>> '{timings,hydrate_ms}')::bigint AS hydrate_ms,
       (diagnostics #>> '{timings,total_ms}')::bigint AS retrieval_ms,
       (diagnostics #>> '{transport_timings,rpc_ms}')::bigint AS rpc_ms,
       (diagnostics #>> '{transport_timings,cli_ms}')::bigint AS cli_ms
FROM tool_call_log
WHERE chat_session_id = :'sid'
  AND kind IN ('search', 'code_search')
ORDER BY started_at;
```

### Driver-native calls

```sql
SELECT tool_use_id, chat_session_id, turn_id, tool_name,
       settled_at - invoked_at AS observed_ms, ok, error, input, result
FROM native_tool_calls
WHERE chat_session_id = :'sid'
ORDER BY invoked_at;
```

## Interpretation

One `tool_call_log` row represents one logical Effector-executed request.
`elapsed_ms` begins immediately before instrumented execution and excludes
approval waiting and pre-execution batch queueing. Telemetry writes are best
effort, so rows can be missing or appear open after completed work. A redrive
reuses the logical row and preserves only the latest attempt timing while
incrementing `attempt_count`.

For Search/CodeSearch diagnostics:

| Signal | Interpretation |
|---|---|
| `freshness.wait_ms` dominates | repository freshness/sync barrier or lock contention |
| `query_embedding_ms` dominates | embedder queue/provider/health pressure |
| `dense_sql_ms` or `bm25_sql_ms` dominates | PostgreSQL retrieval/load/plan/lock issue |
| `ranking_bridge_ms` dominates | bridge expansion, candidate annotation, or DB contention |
| `hydrate_ms` dominates | final metadata/edge hydration fan-out |
| `rpc_ms` high while freshness and retrieval are low | queueing, connection, socket/event-loop, negotiation, or serialization gap |
| `transport=cli` after a fixed long `rpc_ms` | RPC timeout followed by fallback |
| `transport=unavailable` | no transport returned a usable result |
| `elapsed_ms` much greater than reported client latency | execution wrapper or telemetry/Core overhead |

Useful approximations, not accounting identities:

```text
client transport ≈ rpc_ms + cli_ms
RPC unexplained gap ≈ rpc_ms - freshness.wait_ms - timings.total_ms
execution-wrapper overhead ≈ elapsed_ms - latency_ms
```

Bimodal behavior—many healthy calls plus a small group near a fixed timeout—is
usually scheduling/timeout infrastructure rather than query complexity.

## Daemon-log correlation

Operational logs commonly live under:

```text
~/Library/Application Support/Arbol/logs/
```

Use exact correlation IDs and the database-derived time window. Relevant files
can include `core.log`, `effector.log`, and `mycel.log`, including rotated
backups. Not every internal call carries the original request ID, so combine
Chat Session ID, request ID, timestamp, kind, transport, and PID. Do not execute
application diagnostics code merely to obtain log data.

## Reporting contract

Report separately:

1. scope and evidence window;
2. confirmed failures or incorrect/incomplete results;
3. performance anomalies and baseline comparison;
4. redrives, stuck-looking calls, transport, and telemetry anomalies;
5. plausible risks/hypotheses, explicitly labeled;
6. observability gaps that prevent a firm conclusion;
7. recommended next actions, tied to evidence.

Preserve Chat Session, turn, batch, request, PID, UTC timestamps, elapsed time,
kind, transport, status/error, attempt count, diagnostic phase fields, relevant
request/result evidence, neighboring calls, and concise redacted log excerpts.

<!-- sources:
Arbol:daemons/core/arbol_core/db/tool_call_log.py
Arbol:daemons/core/arbol_core/db/tool_requests.py
Arbol:daemons/core/arbol_core/projections/native_tools.py
Arbol:daemons/effector/arbol_effector/mycel_client.py
-->
