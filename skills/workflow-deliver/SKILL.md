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

Own the authorized run through verified PR handoff. Implement directly or delegate
where it has a concrete benefit, under the configured execution profile. Verify
combined behavior through the actual callers. Before closing a task, compare its
planned proof with the observed scenario; missing proof keeps it open. Apply the
blueprint's [implementation review](../../feature_execution_blueprint.md#implementation-review)
to the final code, independently of any earlier proposal review. Route failures
and PR findings through the feedback procedure to update repair tasks/checks before
editing code; continue without routine prompts.

Reuse the batch's open PR when one exists. Stop at `awaiting_review` only when the
authorized handoff, behavioral proof, required CI and configured code review are
complete. Pending checks remain `active`; preserve a resume point if the run must
end. Report genuine blockers with recovery state. Human acceptance, merge, and
deployment remain separate actions.

Present the result using the blueprint's
[Verification and handoff](../../feature_execution_blueprint.md#verification-and-handoff):
product overview, technical change summary based on the actual diff, and risks
with verification results and remaining gaps. Highlight material departures from
the approved proposal and link the PR or local diff and evidence.
