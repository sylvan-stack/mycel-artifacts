---
role: authored
---
# Guide: Saga Planning and Arc Review

Use this guide to turn a feature's specification into Sagas, Arcs and Beats,
and to review an Arc after its Beats finish. Saga Planning is the fifth
stage of the [Feature Course](feature-course.md). The specification and the
feature's research document are its inputs. [Planning a Beat](implementation-planning.md)
covers the detailed steps that follow.

## Choose the Saga and Arcs

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
Put the testing Beat last and have it wait for the work it covers. Testing
starts when the owner requests it under the [Test Strategy](test-strategy.md).
For example, two independent Beats might build a command and write a guide.
Both can start immediately. The final Beat checks their combined result.

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

When the final testing Beat is complete, the Arc enters In Review. The
Forester action item that dispatches the review is specified in
[FOR-1](../../forester/specs/01-forester.md#2--planning) and is still planned.
The reviewer must be a session that took none of the Arc's Beats.

Read the Arc's Approach and Spec Requirements, the changes from its Beats,
and the testing Beat's evidence. Check whether the combined result fulfills
the Approach and each requirement. A finished Beat records what it did.
The review checks whether the pieces work together as specified.

- If the result meets the Approach and requirements, record the review and
  mark the Arc Done.
- If the review finds gaps, record them as new fix Beats in the Arc's
  `### Order` and add a final testing Beat for the revised result. Return
  the Arc to the applicable Ready status. A fresh reviewer checks the Arc
  again after the new testing Beat finishes.

The owner closes the Saga.

<!-- sources:
mycel:specs/20-feature-course.md#Saga Planning
mycel:specs/20-feature-course.md#The Arc Review
forester:specs/03-data-formats.md#The order of an Arc's Beats
-->
