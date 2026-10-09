---
name: workflow
description: Turn a business need into reviewed batch plans, execute an approved plan through local verification to a PR, or prepare a continuation from feedback.
---

# Software development workflow

One coordinator owns preparation, execution and handoff. Use native tools and
session controls. Extra agents and independent reviews are optional, selected
during planning for a concrete risk and within available authority. This package
supplies instructions, not a sandbox runner or scheduler.

Default flow: business need, requirements and batch map, technical plan, human
approval, isolated execution with local checks, PR publication, then stop.
Remote feedback starts a separately requested planning cycle.

Resolve this skill's real directory before following relative references. The
package's location is not the target project. Read that project's rules and only
the records and code needed for the current action.

## Entry and authority

Identify the repository, checkout/branch, base and selected feature/batch together.
A matching name elsewhere does not redirect work. Before proposing or acting on an
existing PR, inspect its repository, source/target branches, open/closed/merged state
and source branch existence. Recheck before remote mutation. An ordinary update
does not authorize an undisclosed reopen or branch restoration.

Preparation ends at a concrete proposal. Approval of that exact proposal covers its
stated implementation, local verification and in-scope repairs, commits, push and PR
destination. Skill selection alone supplies no approval. Reuse clear authorization
already given; preserve narrower user instructions and project/environment controls.
Merge and deployment remain separate decisions.

Default execution ends after opening or updating the PR and recording the handoff.
Do not wait for CI or remote review, repair PR feedback, repush, or start another
batch after this boundary. A comment, failing check or old approval cannot restart
execution. A request to address feedback authorizes assessment and a continuation
proposal; implement once that exact continuation is approved. An explicit approval
of an already concrete continuation needs no second approval.

## Choose the procedure

- New need, unfinished proposal or requested PR feedback: [prepare.md](prepare.md).
- Approved plan or execution interrupted before handoff: [deliver.md](deliver.md).
- Planned local verification or explicitly assigned review: [verify.md](verify.md).
- Read-only inspection: report the selected records and actual state, then stop.
- Installation, package update or document migration: [install.md](../install.md).

For resumed work recover the approved scope and execution checkpoint. A completed
PR handoff remains stopped, even if checks are red or pending. Ambiguous "continue"
after handoff means reconcile the intended scope, not restart the old repair loop.
Closed or merged PRs need an authorized follow-up. Package replacement does not
migrate records or broaden earlier approval.

## Work records

Reuse existing feature and batch identities or choose distinct descriptive folders.
No central backlog or status allocator is required.

| Record | Content it owns |
| --- | --- |
| `ai-workflow/features/<feature-id>/FEATURE.md` | Original need/source, observable requirements with stable IDs, scope/exclusions, business decisions, batch map with outcomes and dependencies. |
| `ai-workflow/work/<batch-id>/BATCH.md` | Feature link and selected requirement IDs, repository/branch/base and instruction source commit, batch scope, exact approval and delivery boundary, execution checkpoint, feedback dispositions and evidence links. |
| `ai-workflow/work/<batch-id>/IMPLEMENTATION.md` | Technical decisions/interfaces, tasks and dependencies, requirement coverage, verification procedures and task execution results. |

A small change uses one batch and short records. Map a larger feature first and
detail batches only when their assumptions are stable. A map does not authorize
execution of every batch. Approval names the batch or batch group and its PR boundary.
Define each requirement once in FEATURE; reference it from plans.

BATCH links its implementation plan and owns the next action. Task-level progress
lives only in IMPLEMENTATION. Do not duplicate it in a separate progress file.
The coordinator owns record updates; other agents return findings and evidence.

Bind approval to an immutable snapshot of applicable feature requirements, batch
scope and implementation plan, including verification and publication. Use a Git
snapshot or retain exact approved content under the batch's `evidence/` before
revision. Record the decision source/date and snapshot in BATCH. A mutable label
or summary alone is insufficient. Preserve earlier approvals; a continuation
records its own approved delta and the snapshot it builds on.

GitHub owns current PR, branch, CI and remote-review state. BATCH records decisions
and execution checkpoints, including the completed PR handoff, without mirroring
live CI statuses. The checkout owns unpublished work; another clone recovers only
pushed work. Identify local-only checkpoints accurately.

Keep durable evidence links or relevant redacted outputs in the batch's `evidence/`.
Never retain credentials or private production data. Evidence keeps its tested
revision and environment; see [verify.md](verify.md).
