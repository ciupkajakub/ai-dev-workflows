---
name: workflow-prepare
description: Turn a business need into a blueprint feature contract and implementation plan for human approval when the user requests preparation.
---

# Prepare a proposal

Resolve this skill directory's symlinks before opening relative references.
Read the [shared entry rules](../entry-rules.md), then follow
[Prepare a proposal](../../feature_execution_blueprint.md#prepare-a-proposal).

Use the supplied business need or issue reference. If neither the request nor
existing context identifies the need, ask for it. Inspect the relevant project
code, tests, and decisions before asking product questions.

Prepare the batch's FEATURE, IMPLEMENTATION, and PROGRESS documents and update
the shared ledgers as the blueprint requires. In IMPLEMENTATION's existing Tasks
section, record the material component changes before/after, their responsibilities,
changed inputs/outputs, and affected callers. Follow the behavior through actual
validation, recovery, and alternate entry points. For changed validation/recovery,
name the inputs, validating component and chosen validation logic, response
fields, and consumer action. Settle relevant rule differences when reusing an
existing service. A file inventory or a promised response field is insufficient.

Complete the blueprint's
[Proposal readiness](../../feature_execution_blueprint.md#proposal-readiness)
review before requesting approval. Repair contradictions, missing shared contracts,
and path-specific verification gaps yourself. Resolve ordinary technical choices
from code evidence; ask only for unresolved product decisions or genuine blockers.
Keep the approach in the documents. Support readiness in PROGRESS with links to
the approach, inspected code, and planned checks. Do not label an incomplete
proposal ready and expect the operator to finish its technical design.

Present one approval package with
the exact proposal baseline, verification plan, and intended delivery scope,
including the push destination and PR authority needed for delivery.

Present that package in the conversation using the blueprint's
[Approval presentation](../../feature_execution_blueprint.md#approval-presentation):
product overview, concise component-level before/after summary of proposed
additions/changes/removals and interface changes, and
material risks with observable verification scenarios. Distinguish code facts,
planned changes, and agent-added decisions or assumptions. Link the proposal
documents; use a readable flow diagram only when it helps explain the change.
Write natural, precise prose in the operator's language. Name components, actions,
and consequences; shorten by selecting material information, not by using ambiguous
shorthand or fragmented sentences. Review the wording as part of preparation.

Stop at `awaiting_approval`. This skill requests preparation, not implementation.
Do not start workers that implement the proposal or publish changes merely because
the plan is ready.
