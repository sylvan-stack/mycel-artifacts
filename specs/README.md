---
role: authored
---
# Mycel specifications

What Mycel 2 does, written from what Mycel 1 did. [Mycel](../../arbol/GLOSSARY.md#mycel) is the knowledge engine of the Sylvan Stack: it turns the documents and the code of each repository into an index that is kept current, knows what each part rests on, and can be searched by meaning and by exact wording. Mycel 2 is implemented from scratch; these specifications say what is carried over from version 1, what changes and what is left behind.

## Specifications

| Spec | Title | Status |
|---|---|---|
| [MYC-0](00-overview-and-legacy-map.md) | Overview and legacy map | draft |
| [MYC-1](01-corpora-and-ingest.md) | Corpora and ingest | draft |
| [MYC-2](02-provenance-and-freshness.md) | Provenance and freshness | draft |
| [MYC-3](03-embedding.md) | Embedding | draft |
| [MYC-4](04-retrieval.md) | Retrieval | draft |

MYC-0 says what Mycel is for, and MYC-1 to MYC-4 are the four parts of that function in the order a file passes through them. Functions of version 1 beyond these four are listed in MYC-0 with their fate; those that follow later get a specification of their own.

Evidence the specifications rest on is in `research/`:

- the inventories of the version 1 source: [ingest and the knowledge graph](../research/v1-inventory-ingest-and-graph.md), [embedding and retrieval](../research/v1-inventory-embedding-and-retrieval.md), [the sync pass, settings, scope, commands and summaries](../research/v1-inventory-sync-settings-commands.md);
- [what the installed version 1 did](../research/v1-observations-2026-10.md) on 6 and 7 October 2026.

## Conventions

The shape of a specification, requirement identifiers, origin, status, decisions and wording are defined once, in the [Driver Contract's README](../../arbol/driver-contract/README.md#conventions) of the Arbol corpus. What differs here:

**Identifiers.** Requirements are `MYC-1.4`: requirement 4 of specification 1. Decisions are numbered across the specifications, `MYC-D1` onwards.

**Source Refs.** A section that describes version 1 ends with Source Refs into the deprecated repository, written `mycel_deprecated_v1:`. The name `mycel:` means this corpus and, later, the new code. The deprecated repository is not indexed, so these refs are locators for a reader: they say where a disputed claim can be checked, and they do not become edges. Refs into the deprecated Arbol corpus are written `arbol_deprecated_v1:` for the same reason.

**Verified by.** Mycel has no vendor tool behind it, so its kinds of check are its own:

| Check | Meaning |
|---|---|
| unit | Automated, with no index store and no network |
| store | Automated, against an index store made for the test and discarded after it. No network |
| eval | The evaluation set of MYC-4.25: queries with the chunks each should find. It needs vectors, so it is run on demand |
| live | A check that calls the embedding service and spends quota. Run on demand, never in the automatic suite |

**Observed.** *Observed in version 1* means read in the version 1 source; the inventories say for each statement whether it was also run. *Observed on* a date means seen on the installed program that day, and is recorded in the observations file.
