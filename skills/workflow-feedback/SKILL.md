---
name: workflow-feedback
description: Apply an operator's feedback to an existing blueprint batch, reconcile its contract and plan, and deliver another iteration of the same open PR.
---

# Apply feedback

Resolve this skill directory's symlinks before opening relative references.
Read the [shared entry rules](../entry-rules.md), then follow
[Feedback and operator edits](../../feature_execution_blueprint.md#feedback-and-operator-edits).

Resolve the batch and the supplied feedback or identified operator edits. Load
the current branch/PR, approved baseline, subsequent decisions, and affected
evidence. An arbitrary repository comment is not an authenticated approval.

Reconcile FEATURE and IMPLEMENTATION, record the specific authorized change, and
invalidate affected proof while preserving unrelated work. A clear operator
instruction can approve its exact change; ask only about unresolved conflicts or
new authority. Respect an explicitly planning-only request.

Under the authorized delivery scope, delegate implementation to native workers
by default, verify and repair, and update the same open PR. Follow the blueprint's
separate follow-up procedure if that PR is already closed or merged. Return the
revised result for human review; do not merge or mark it accepted on the user's behalf.
