---
role: authored
---
# Feature Course Guide

Use the Feature Course with the owner when a new feature comes up in a
Mycel-enabled repository. It takes the owner's idea through research and an
agreed specification to Beats an agent can implement. [MYC-20](../specs/20-feature-course.md)
defines the course.

## Follow the six stages

<!-- mycel:cues
type: literal
match: ["feature course guide", "start a feature course", "plan a new feature"]
cue_target: none
instructions: >-
  The Feature Course guide at ~/Artifacts/mycel/operations/feature-course.md
  is required reading when taking a new feature through research,
  specification and Beat planning.
-->

| Stage | Work with the owner | Result |
|---|---|---|
| 1. Idea Discussion | Listen to the feature in the owner's own words. Ask about what changes for the people who use it and restate the idea for the owner. | An idea clear enough to research. |
| 2. Initial Research | Study the current architecture and related code. Show where the behavior lives today with file and line evidence. | The feature's research document. |
| 3. Feature Triage | Gather the owner's requirements, limits and priorities. Work out what the feature reuses, changes or conflicts with. Return to the code when needed. | The same research document, extended. |
| 4. Spec Writing | Write or extend the specification. Bring open behavior choices to the owner and record their decisions in the specification. | Spec Requirements and Decisions that describe the feature. |
| 5. Saga Planning | Use the specification and the research document to plan the Sagas, Arcs and Beats. Follow the [Saga Planning guide](saga-planning.md). | Sagas and Arcs with Approaches, and Beats with defined goals. |
| 6. Implementation Planning | Turn each Beat's specified work into steps. Follow [Planning a Beat](implementation-planning.md). A plan can also be written when that Beat is taken for implementation. | Beats with plans. |

Repeat stages 1 to 3 in any order until the feature is understood. A finding
in the code can prompt another discussion, and an answer from the owner can
send the agent back to research before triage continues.

## Keep the research in one document

Resolve the repository's artifact root and keep one feature document in its
`research/` folder. Follow [Deep Research](deep-research.md#process) for
placement and evidence. During Initial Research, record the architecture
and behavior the feature touches, with paths and line numbers that show
each finding. During Feature Triage, extend the same document with evidence
about what can be reused, what needs to change and what conflicts with an
existing behavior. Record questions the evidence leaves open.

Pass that document forward to Spec Writing, Saga Planning, Implementation
Planning and the Beats. Update it when new evidence changes a finding. This
gives the next agent a place to verify the evidence behind the specification
and plans.

## Return to Spec Writing when behavior is missing

Every Saga, Arc, Beat and implementation plan needs specified behavior.
If planning reaches behavior the specification leaves open, pause planning
that behavior and return to Spec Writing. Name the missing behavior and
bring the choice to the owner. Record the owner's decision in the
specification before resuming the affected planning.

For example, if a specification says to retry a failed upload and leaves
the stopping condition open, take that choice to the owner before writing
a Beat or step that assumes a retry limit.

<!-- sources:
mycel:specs/20-feature-course.md#The six stages
mycel:specs/20-feature-course.md#Where the course lives
mycel:specs/20-feature-course.md#Requirements
mycel:operations/deep-research.md#Process
-->
