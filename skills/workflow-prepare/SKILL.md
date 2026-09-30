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
the shared ledgers as the blueprint requires. Present one approval package with
the exact proposal baseline, verification plan, and intended delivery scope,
including the push destination and PR authority needed for delivery.

Present that package in the conversation using the blueprint's
[Approval presentation](../../feature_execution_blueprint.md#approval-presentation):
product overview, technical summary of proposed additions/changes/removals, and
material risks with observable verification scenarios. Distinguish code facts,
planned changes, and agent-added decisions or assumptions. Link the proposal
documents; use a readable flow diagram only when it helps explain the change.

Stop at `awaiting_approval`. This skill requests preparation, not implementation.
Do not start workers that implement the proposal or publish changes merely because
the plan is ready.
