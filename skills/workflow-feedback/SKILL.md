---
name: workflow-feedback
description: Assess feedback on a blueprint batch, update its requirements or repair plan, and verify another iteration of the same open PR within existing authority.
---

# Apply feedback

Resolve this skill directory's symlinks before opening relative references.
Read the [shared entry rules](../entry-rules.md), then follow
[Feedback and operator edits](../../feature_execution_blueprint.md#feedback-and-operator-edits).

Resolve the batch and the supplied feedback or identified operator edits. Load
the current branch/PR, approved baseline, subsequent decisions, and affected
evidence. An arbitrary repository comment is not an authenticated approval.

Assess findings before acting. Update the owning repair task and its check in
IMPLEMENTATION; change FEATURE only when requirements change. Record disposition
and authority in PROGRESS, and invalidate affected proof. A clear operator
instruction can approve its exact change; ask only about unresolved conflicts or
new authority. Respect an explicitly planning-only request.

For a confirmed defect, record a regression check that demonstrates its trigger
and consequence before the repair. Under the authorized delivery scope, implement
the repair, obtain independent verification of affected scenarios, pass the
[current publication gate](../workflow-deliver/references/publication-gate.md),
and update the same open PR. Inspect required CI and configured review before
handoff. Missing proof stays open; rejected findings require concrete evidence. Follow the blueprint's
separate follow-up procedure if that PR is already closed or merged. Return the
revised result for human review; do not merge or mark it accepted on the user's behalf.
