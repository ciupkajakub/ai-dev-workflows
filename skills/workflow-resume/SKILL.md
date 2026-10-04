---
name: workflow-resume
description: Resume an interrupted blueprint batch from its durable documents, repository state and existing authority without restarting planning.
---

# Resume a batch

Resolve this skill directory's symlinks before opening relative references.
Read the [shared entry rules](../entry-rules.md) and follow
[Pipeline and handoffs](../../feature_execution_blueprint.md#pipeline-and-handoffs).

Resolve the batch. Read its WORK_INDEX entry, FEATURE, IMPLEMENTATION, PROGRESS,
approval snapshots, and evidence. Inspect the actual checkout, changes, branch/PR,
and any recorded coordinator or worker sessions before choosing the next action.
Reconcile claimed task completion with its planned behavioral proof using the
[delivery verification procedure](../../feature_execution_blueprint.md#verification-and-handoff).
Missing or narrower proof returns the owning task to active verification.

Ensure no other coordinator owns the active run. Reconcile or stop previous
workers before reassigning interrupted work. Reuse a provider session when it is
available and appropriate; otherwise reconstruct context from the durable records.

Continue an already authorized `active` batch through the
[delivery procedure](../../feature_execution_blueprint.md#approve-and-execute).
Recover pending CI/review results and reconcile findings before assigning repairs.
For `planned`, continue discovery/interview from recorded answers. For `blocked`,
verify that the recorded blocker has cleared before dependent work. Do not repeat unchanged
passing checks or discard completed work merely because this is a new session.

Resume is not a new approval. At `awaiting_approval`, present the outstanding
decision unless the current request supplies it. At `awaiting_review`, check that
the recorded handoff still holds: new required failures return to authorized repair,
pending checks return to `active`, otherwise preserve the human review boundary.
Do not restart `done` or `superseded` work without a new authorized request.
Report and record the next boundary or remaining blocker.
