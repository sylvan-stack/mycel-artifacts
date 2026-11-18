---
role: authored
---
# Justifications

## <before _fail>

Reason: Store the canonical label before the mechanical dependency guard observes the published summary version

Origins: MYC-8.33 · Intention i-6d486f37 · 2026-11-18

## StagedSummary

Reason: Generate labels from the exact text in regular build and regeneration. Publish labels atomically as version metadata with the summary, and retain an existing label on an identical reused version, filling it when absent. Keep older rows and existing private writer fixtures readable. Route label generation or validation failure through ordinary summary publication failure

Origins: MYC-8.33 · Intention i-df1359fc · 2026-11-18

## SummaryPublicationStore.publish_in_transaction

Reason: Store the canonical label before the mechanical dependency guard observes the published summary version

Origins: MYC-8.33 · Intention i-6d486f37 · 2026-11-18

## SummaryPublicationStore.stage_response

Reason: Generate labels from the exact text in regular build and regeneration. Publish labels atomically as version metadata with the summary, and retain an existing label on an identical reused version, filling it when absent. Keep older rows and existing private writer fixtures readable. Route label generation or validation failure through ordinary summary publication failure

Origins: MYC-8.33 · Intention i-df1359fc · 2026-11-18

## SummaryPublicationStore.verify_in_transaction

Reason: Generate labels from the exact text in regular build and regeneration. Publish labels atomically as version metadata with the summary, and retain an existing label on an identical reused version, filling it when absent. Keep older rows and existing private writer fixtures readable. Route label generation or validation failure through ordinary summary publication failure

Origins: MYC-8.33 · Intention i-df1359fc · 2026-11-18

