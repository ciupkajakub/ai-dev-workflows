---
name: workflow-deliver
description: Deliver an identified blueprint proposal through implementation, verification, repairs and PR handoff when the operator approves delivery.
---

# Deliver the approved proposal

Resolve this skill directory's symlinks before opening relative references.
Read the [shared entry rules](../entry-rules.md), then follow
[Approve and execute](../../feature_execution_blueprint.md#approve-and-execute).

Resolve the batch and the exact proposal and delivery scope presented to the
operator. Apply the shared approval rule before implementing. Record the approval
snapshot and retain any existing scoped authority. Do not interpret the command
as permission for an unspecified remote, merge, deployment, or scope change.

Coordinate the authorized run through PR handoff. Delegate bounded implementation
tasks to native workers by default under the configured execution profile. Follow
the blueprint's fallback, starting-revision, resource-isolation, and evidence rules.
Integrate worker results, run the required checks, assign repairs, and continue
without routine prompts at task boundaries.

Reuse the batch's open PR when one exists. Stop at `awaiting_review` only when the
authorized handoff and required proof exist, or report a genuine blocker with
recovery state. Human acceptance, merge, and deployment remain separate actions.
