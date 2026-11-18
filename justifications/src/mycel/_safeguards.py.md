---
role: authored
---
# Justifications

## model_call_allowed

Reason: Expose `summaries labels --repo <name>` to backfill missing active labels under the summary-operation lock. Retain existing labels and publish the whole batch only if all captured versions are still current. Leave prose and vectors untouched. Allow this explicit model call through the normal provider boundary. Update command declarations and the checkout command contract

Origins: MYC-8.34 · Intention i-f7fab174 · 2026-11-18

