---
role: authored
---
# Guide: Justify code and documents

Use this guide to bring an existing repository under Origin Coverage, or to
state what ordered new work. It owns the sequence: prepare identifiable
requirements and decisions, capture authorized inputs, preserve existing
claims, recover missing ones and inspect the audit. MYC-17 owns the product
contract; the [Origin manual](../tools/mycel-2-origins.md),
[recovery manual](../tools/mycel-2-recovery.md) and
[audit manual](../tools/mycel-2-audit.md) own command syntax and replies.

An Origin Link is a claim about why a chunk exists. For example, a retry test
can rest on the requirement that retries stop after the configured limit.
The link does not establish that the test or implementation conforms.
[Origin Coverage](../../arbol/GLOSSARY.md#origin-coverage) reports the claims
and gaps when requested; it creates no commit, release or qualification gate.

## Establish the scope and authority

Read the [Hub's current operator instructions](../README.md) before any store
operation. On 26 October 2026 the owner lifted the dated 22 October
direction that reserved the first ingest to the owner, and asked an agent to
run `mycel ingest --all` on the owner's store without embedding. Embedding,
recovery and the semantic audit still wait for the owner's cost approval and
model budget. A dry-run is still a store operation:
it needs an existing initialized index and does not authorize the first ingest.

Identify the repository, its configured code and artifact roots, the calling
clone and the read-only baseline. Read the settings before changing them;
use the [settings manual](../tools/mycel-2-settings.md) for clone registration.
The stored snapshot is the source for reports; the files are the source for
new content. Use a Build containing the commands being used. Installation
alone supplies no live qualification, and an earlier Build may omit recovery
or audit. Keep owner installation separate from private Build validation.

Before writing durable claims, establish the PostgreSQL backup arrangement
and keep the input files available. Statements live only in the Index Store;
Git does not back them up. The [store manual](../tools/mycel-2-store.md)
describes store ownership. Select explicit repository scope, especially from
a booked area such as Beaver Workspace, where implicit scope may include more
than one repository.

## Normalize existing requirements and decisions

Read the destination's authoring rules and preserve a backup. Give every
requirement and decision row one UUID comment after its human ID in the first
cell, following [MYC-17](../specs/17-justification.md#requirements-and-decisions-are-entities).
Preserve every existing UUID and human ID. Never allocate a second identity
because a row moved or its wording changed. Rename the version-comparison
column to `From v1`; reserve Origin for what ordered the chunk.

Validate all rows with the current parser before publishing. Missing UUIDs,
repeated UUIDs and ambiguous human IDs need explicit correction; a parser
fault does not become an entity. Keep a withdrawn ID reserved. A decision's
Discussion cell holds real chat Entity URIs when known; leave unavailable
discussion visible instead of inventing a chat or treating it as authority.
Publish the authoritative originals and their established copies.

Once the store operation is authorized, register the actual clone locations
and ingest the baseline and intended calling clone. Ingest captures code and
artifacts without buying vectors. Inspect the pass's reported faults and
partial outcomes, and compare the parsed UUID inventory with the stored rows.
A passing file validation alone does not prove the stored index is current.
Follow [authored-work integration](authored-work-integration.md) for corpus
coverage and real Source Refs; preserve editable document declarations in the
file instead of replacing them with database-only assertions.

<!-- sources:
mycel:@code/src/mycel/_markdown.py
mycel:@code/src/mycel/_entities.py
mycel:@code/src/mycel/_ingest.py
-->

## Preserve existing declarations before retiring them

Inventory any legacy requirement-to-check declarations against an exact
source snapshot. Keep the complete test symbol, each requirement's UUID and
the declaration's check kind. Import every declared pair, including multiple
requirements on one test, through the supported bulk form when available.
Validate the entire batch before writing and inspect the committed result.
An interrupted or uncertain response requires stored-state verification before
retry; do not infer rollback or success from the terminal alone.

For Mycel's one-time `@proves` transition, MYC-D56 requires method `proven`,
band `proven` and verification `how: check`. The ordinary statement command
writes method `stated` with `how: read`, so a generated pair file alone does
not complete that import. SYL-261 carried it out on 23 October 2026 and then
retired the registry, claims, decorators and their qualification checks
(MYC-D56). For another repository, preserve its legacy declarations the same
way until their import is verified in its authorized destination. Disposable
rehearsal is preparation, rather than acceptance of the owner run.

Read the Origin report with the unresting requirements included. Reconcile
the imported pairs with the frozen declarations, and retain exact source and
store receipts outside every corpus. Preserve the vocabulary `unit`, `store`,
`eval` and `live`; importing a declaration supplies no new live measurement or
Build qualification. After the verified import, retire the legacy mechanism
and update its check/build guides together, keeping the complete suite working.

## Recover and audit the remaining gaps

Read the current missing-Origin report without a freshness pass when the
snapshot must remain untouched. Before model execution, obtain the operator's
explicit model/reviewer selection and numeric candidate, attempt, byte and
deadline limits. Review a bounded recovery dry-run, source availability and
maximum calls before spending that allowance. Use existing vectors only when
they are available and authorized. For the first Mycel run no vectors exist,
so the embedding candidate source remains unavailable; do not buy embeddings.

Recovery proposes candidates from local documents, tests, history and any
existing vectors. A symbol mention or introducing commit is evidence to judge,
rather than a declaration of authority. It leaves missing or obsolete evidence
unresolved. Model claims stay inferred or candidate, never a check proof or a
freshness confirmation. Inspect the committed prefix, pending reasons and
remaining gaps after a partial or interrupted run; reuse only exact valid
inputs and respect the remaining operator allowance when resuming.

Run the audit within its separately accounted share of the agreed allowance.
Its deterministic rules need no model; semantic questions spend the chosen
model/reviewer budget. Audit can lower scores and open findings across every
link method. A person settles a finding with a reason. Never settle it just
to empty the list, or record a needs-nothing mark to hide a missing test.
Where nothing should rest on a constraint, a reasoned needs-nothing mark can
explain that fact without inventing a dependency or verification.

Report missing chunks before and after recovery, links written by band,
findings opened, unresolved work and actual model/reviewer calls. A capped
selection is incomplete coverage. Preserve open findings and exact request
history in the store; keep raw run transcripts outside repositories and
corpora. Remove disposable stores and copies only after their acknowledged
results are retained; preserve durable owner-store statements.

<!-- sources:
mycel:@code/src/mycel/_origins.py
mycel:@code/src/mycel/_recovery.py
mycel:@code/src/mycel/_audit.py
mycel:@code/src/mycel/_audit_semantic.py
-->

## Keep new work traceable

When adding or changing code, identify the requirement, decision or document
section that ordered it. State that link when the evidence is known. For an
editable document, keep its real Source Refs in the file. Give new requirement
and decision rows their UUID at authoring time, preserving it on later edits.

Checking Origin Coverage for the calling clone's changes before a commit is
useful and optional. Capture the authorized changed inputs first and ingest
the read-only baseline before relying on its stored comparison. A changed or
unresolved input is a reason to refresh or correct it, rather than guess an
Origin. Leave uncertain gaps visible for recovery or human review. A task,
Beat or Linear issue is never an Origin.

For third-party code, put the owner's actual requirements and time-pinned
upstream document, commit or issue snapshots in the owner's corpus before
an authorized ingest. An upstream issue can be an Origin; Linear snapshots
are excluded. Recovery uses local indexed snapshots and local Git, without
fetching or modifying upstream code. The owner decides when that repository
is normalized.

The final account separates file validation, store import, Origin Coverage,
audit, executable checks and live qualification. State indexing, embedding
and retrieval verification as deferred whenever they were not performed.
Running an Origin report never substitutes for those steps.

<!-- sources:
mycel:@code/src/mycel/_justify.py#JustifyStore.apply_pairs
mycel:@code/src/mycel/_origins.py
mycel:@code/src/mycel/_recovery.py
-->
