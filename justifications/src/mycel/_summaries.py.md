---
role: authored
---
# Justifications

## <before handle_summaries>

Reason: Make RAPTOR use bundled Narrator for all writes while preserving the read paths and generation evidence.

Origins: MYC-8.5, MYC-8.8, MYC-8.20, MYC-8.25, MYC-22.7 · Intention i-e6b01359 · 2026-11-18

## generate_summary_requests

Reason: Make RAPTOR use bundled Narrator for all writes while preserving the read paths and generation evidence.

Origins: MYC-8.5, MYC-8.8, MYC-8.20, MYC-8.25, MYC-22.7 · Intention i-e6b01359 · 2026-11-18

## handle_summaries

Reason: Expose `summaries labels --repo <name>` to backfill missing active labels under the summary-operation lock. Retain existing labels and publish the whole batch only if all captured versions are still current. Leave prose and vectors untouched. Allow this explicit model call through the normal provider boundary. Update command declarations and the checkout command contract

Origins: MYC-8.34 · Intention i-f7fab174 · 2026-11-18

