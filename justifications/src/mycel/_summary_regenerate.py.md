---
role: authored
---
# Justifications

## regenerate_summary_set

Reason: Generate labels from the exact text in regular build and regeneration. Publish labels atomically as version metadata with the summary, and retain an existing label on an identical reused version, filling it when absent. Keep older rows and existing private writer fixtures readable. Route label generation or validation failure through ordinary summary publication failure

Origins: MYC-8.33 · Intention i-df1359fc · 2026-11-18

## <before _snapshot>

Reason: Generate labels from the exact text in regular build and regeneration. Publish labels atomically as version metadata with the summary, and retain an existing label on an identical reused version, filling it when absent. Keep older rows and existing private writer fixtures readable. Route label generation or validation failure through ordinary summary publication failure

Origins: MYC-8.33 · Intention i-df1359fc · 2026-11-18

## _regenerate_summaries

Reason: Make RAPTOR use bundled Narrator for all writes while preserving the read paths and generation evidence.

Origins: MYC-8.5, MYC-8.8, MYC-8.20, MYC-8.25, MYC-22.7 · Intention i-e6b01359 · 2026-11-18

