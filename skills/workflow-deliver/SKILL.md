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

Own the authorized run through four recorded stages: implementation, verification,
repair when needed, and PR checks. The implementer leaves completion to a distinct
independent verifier. Follow the blueprint's
[independent verification and publication gate](../../feature_execution_blueprint.md#independent-verification-and-publication-gate).
Give that verifier the original request, approved decisions, fixed code snapshot,
project rules and application access. It checks the actual callers and each required
scenario, including preserved behavior. Author summaries are claims to examine.

Before closing tasks or publishing, inspect the verifier's evidence and run the
[publication checker](references/publication-gate.md) for the current commit and
complete pre-publication check list from the approved plan. Missing independent verification,
failed scenarios, stale evidence or unavailable checks keep the run active.
Do not replace that verifier with self-review. Route findings through the feedback
procedure to record a repair task and regression check before editing code.
Continue repairs and focused independent confirmation under existing authority.

Inspect the review's mapping for every behavior within each check, including
full base-to-head file coverage for diff-scoped checks. A checker exit 0 does not
resolve gaps in that mapping. Reconcile task statuses with the accepted evidence
before changing delivery stage; pending proof must remain active.

Reuse the batch's open PR when one exists. Stop at `awaiting_review` only when the
authorized handoff, behavioral proof, required CI and configured code review are
complete. Pending checks remain `active`; preserve a resume point if the run must
end. Claim continued monitoring only with a confirmed provider mechanism for the
PR/head, recording its reference and expiry when supplied. Otherwise report the
interruption with pending checks and an exact resume action in PROGRESS Current.
Report genuine blockers with recovery state. Human acceptance, merge, and
deployment remain separate actions.

Present the result using the blueprint's
[Verification and handoff](../../feature_execution_blueprint.md#verification-and-handoff):
product overview, technical change summary based on the actual diff, and risks
with verification results and remaining gaps. Highlight material departures from
the approved proposal and link the PR or local diff and evidence.
