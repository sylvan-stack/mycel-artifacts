---
role: authored
---
# Guide: Saga Planning

Use this guide to turn a feature's specification into Sagas, Arcs and Beats,
for implementation and Build delivery. Saga Planning is the fifth
stage of the [Feature Course](feature-course.md). The specification and the
feature's research document are its inputs. [Planning a Beat](implementation-planning.md)
covers the detailed steps that follow.

## Choose the Saga and Arcs

<!-- mycel:cues
type: literal
match: ["saga planning", "plan a saga"]
cue_target: none
instructions: >-
  For Saga Planning, the guide at
  ~/Artifacts/mycel/operations/saga-planning.md is required reading before
  dividing specified work into Sagas, Arcs and Beats.
-->

Read the requirements, decisions and research before dividing the work. Find
the existing Sagas in the [Forester Saga index](../../forester/sagas/INDEX.md).

1. Extend an unfinished Saga if its goal already covers the work. Otherwise
   draft a new Saga.
2. Extend an unfinished Arc if it owns the part of the system being changed.
   Otherwise draft new Arcs around parts of the system that can be worked on
   independently. Give each Arc a territory that mostly stays within that part.
3. Keep Done Sagas and Arcs closed. If related work remains, place it in a
   new unit and link the earlier result for context.

## Write the Approaches and Beats

Keep new Sagas and Arcs in Draft while writing their Approaches and Beats.
Follow [Working in Sagas](../../forester/operations/sagas.md) for the file
layout. In the Saga's Approach, explain how the feature is divided among
Arcs. In each Arc's Approach, explain how its Beats meet the Arc's goal.

Write a Beat only when the specification describes the behavior it would
implement. Note foreseen work in the Approach until the specification covers
it. If current work exposes a gap, return to
[Spec Writing](feature-course.md#return-to-spec-writing-when-behavior-is-missing) for the owner's decision.

Put a `### Order` list in each Arc's Approach, using the
[Forester data format](../../forester/specs/03-data-formats.md#the-order-of-an-arcs-beats).
Order the Beats that produce the implementation and resulting Build. Use
only dependencies that supply something required to build or deliver the
agreed result. For example, compilation can wait for the source changes it
packages. Follow [Working in Sagas](../../forester/operations/sagas.md#scope-and-completion)
for work outside the delivery scope.

## Check dependencies and record readiness

If one Arc needs a result from another, first try separating the prerequisite
from the remaining work so that more work can proceed independently. Record
any remaining dependency in the waiting unit's status line as Depends On,
linking the whole Saga or Arc whose completion it needs. A Beat can depend
only on Beats in its own Arc.

Before taking a unit out of Draft, check that its Approach and Beats are
written, no dependency forms a cycle, and every unit with a Ready status is
free of outstanding dependencies. The [status table in MYC-20](../specs/20-feature-course.md#statuses-of-sagas-and-arcs)
defines how a dependency lifts and how readiness reflects the available plans.
Ask the owner to confirm a new Saga and its priority in the index. Existing
Saga extensions, Arcs and Beats need no separate Saga Planning approval.

## Review the Arc

An Arc is Done when its implementation and Build Beats are finished. Keep
any owner-requested review outside its delivery order and dependency chain.
The owner decides whether to schedule it as separate work at the lowest
priority. See [Working in Sagas](../../forester/operations/sagas.md#finish-or-stop)
for the status refresh after delivery.

<!-- sources:
mycel:specs/20-feature-course.md#Saga Planning
mycel:specs/20-feature-course.md#The Arc Review
forester:specs/03-data-formats.md#The order of an Arc's Beats
-->
