---
role: authored
---
# Guide: Author Source Refs

Use Source Refs when a durable document makes claims derived from code,
artifacts, or mirrored external state and Mycel should track when those claims
need re-verification.

## Document shape

```markdown
---
role: derived
sources:
  - mycel:tickets/DEMO-XXXXX-context.md
---
# Limit cooldown research — DEMO-XXXXX

## How cooldown works today

The cooldown is enforced in the limit resolver…

<!-- sources:
arbol:daemons/core/arbol_core/db/entity_catalog.py#EntityCatalog.repos
arbol:daemons/core/arbol_core/artifact_reconciler.py
-->
```

- Frontmatter `sources:` names document-wide governors such as a ticket mirror.
  Use 1–3 refs and `role: derived` when the whole document answers to them.
- A section-level `<!-- sources: -->` block carries one
  `repo:path[#symbol-or-heading]` per line. Ingest attaches those edges to that
  section's chunk.

## Rules

1. **Cite claims, not attention.** Reference what the section says something
   about, not everything read. A consequential dismissal must be stated as a
   claim before it earns a ref.
2. **Match granularity to the claim.** Use `path#Class.method` for one symbol,
   `path#ClassName` for a class family, `path` for a genuinely file-wide claim,
   and `file.md#Heading` for an artifact section.
3. **Use natural keys, never chunk IDs.** Ingest resolves stable external
   identities to database records.
4. **The file is truth.** Removing a ref removes its edge on the next ingest.
   Unresolved refs remain visible and are retried; fix the ref rather than
   deleting a valid claim to silence the warning.
5. **Snapshot external truth first.** Mirror remote Jira, Confluence, or GitLab
   state into the artifact corpus and derive from that time-pinned snapshot.

## Resolution examples

| Ref | Resolves to |
|---|---|
| `arbol:daemons/core/arbol_core/x.service.ts#Service.logout` | one method chunk |
| `arbol:daemons/core/arbol_core/x.service.ts#Service` | class header and method family |
| `arbol:daemons/core/arbol_core/x.service.ts` | code document/file |
| `mycel:operations/knowledge-model.md#Derivation edges` | artifact section |

Cross-repository refs are valid when the target repository is enabled. A Source
Ref is provenance, not an instruction to execute target-repository code.

See [knowledge-model.md](knowledge-model.md) for edge direction, role/state
semantics, Detection, and Drift behavior.

<!-- sources:
mycel:mycel/knowledge/store.py
-->
