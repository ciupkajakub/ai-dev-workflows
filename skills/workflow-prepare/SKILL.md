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

Stop at `awaiting_approval`. This skill requests preparation, not implementation.
Do not start workers that implement the proposal or publish changes merely because
the plan is ready.
