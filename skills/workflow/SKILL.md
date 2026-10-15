---
name: workflow
description: Prepare and independently review a plan, deliver approved work through local verification to a PR, or plan a requested continuation.
---

# Software development workflow

One coordinator owns preparation, execution and handoff. Use native tools and
session controls. This package supplies instructions, not a runner or scheduler.
Resolve this skill's real directory, then identify the target repository,
checkout/base and selected feature/batch. Read that project's rules and relevant
records; a similar name in another checkout does not redirect work.

## Entry and authority

Preparation ends at a concrete proposal. Approval of that exact proposal covers
its stated implementation, local verification and in-scope repairs, commits, push
and PR destination. Skill selection alone supplies no approval. Reuse existing
explicit approval; honor narrower user instructions and project/environment controls.
Merge and deployment require separate decisions.

A missing or failed required check, or unavailable required review, needs a
separate explicit exception naming the affected requirements, missing proof and
remaining uncertainty. General approval or silence does not waive it. Retain the
exception in BATCH with the approval snapshot. An exception to verification cannot
authorize a change to required behavior.

Default execution ends after opening or updating the PR and recording handoff.
Do not wait for CI/review, schedule monitoring, repair feedback, repush or start
another batch. A request to address feedback authorizes assessment and a continuation
proposal; its implementation needs approval. A pending check or old approval does
not restart completed delivery. Preserve stricter project publication requirements.

Before proposing work on an existing PR, inspect its repository, source/target,
state and source branch existence. Recheck before mutation; an ordinary update
does not authorize reopening a closed PR or restoring a branch.

## Choose the procedure

- New need, unfinished proposal or requested feedback: [prepare.md](prepare.md).
- Approved execution, including an interrupted run: [deliver.md](deliver.md).
- Evidence planning, local checks or assigned implementation review: [verify.md](verify.md).
- Read-only inspection: report actual state and stop.
- Installation, update or record migration: [install.md](../install.md).

## Work records

Reuse existing identities. For new work use these records, with detail proportional
to the decisions and risks. No additional backlog, progress or readiness document.

| Record | Content it owns |
| --- | --- |
| `ai-workflow/features/<feature-id>/FEATURE.md` | Original need/source, observable requirements with stable IDs, exclusions, business decisions and batch outcomes/dependencies. |
| `ai-workflow/work/<batch-id>/BATCH.md` | Feature/plan links, selected requirements, repository/branch/base, instruction commit, scope and PR boundary, approval, execution checkpoint and next action. |
| `ai-workflow/work/<batch-id>/IMPLEMENTATION.md` | Design and affected flow/contracts, tasks/dependencies, requirement-to-check mapping, procedures, results and review links. |

Define requirements once in FEATURE; keep task progress only in IMPLEMENTATION.
The coordinator updates records; reviewers return findings and evidence.

Bind approval to an immutable snapshot of the applicable requirements, batch scope
and plan, including verification and publication. Record decision source/date in
BATCH. Use Git or preserve exact content under `evidence/` before revising it.
Continuations retain earlier approvals and identify their approved delta and base.
Package updates do not migrate records or expand authority.

GitHub owns live PR/CI state; records retain decisions and execution checkpoints.
Another checkout recovers only pushed work. Mark local-only evidence accurately;
retain evidence links or redacted outputs under `evidence/`, never credentials or
private production data. Evidence identifies the actual tested revision/environment.
