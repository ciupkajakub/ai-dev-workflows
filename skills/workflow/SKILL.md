---
name: workflow
description: Prepare a software change from a business need, or deliver and resume an approved batch through independent verification and a review-ready PR.
---

# Software development workflow

One coordinator owns the requested outcome. It may implement directly; an
independent agent/session that did not implement the change verifies it. Use the
environment's native agents, tools and session controls. Model selection belongs
to that environment. This package supplies no runner or scheduler.

Resolve this skill's real directory before following relative references. The
package's location is not the target project. Read the selected project's rules
and only the batch and code needed for the current action.

## Entry and authority

Identify the repository, checkout/branch, base and selected batch together. Use
the user's selected work; a matching name elsewhere does not redirect it. Before
proposing or acting on an existing PR, inspect its repository, source/target
branches and open/closed/merged state, including whether its source branch exists.
Recheck before a remote mutation. Approval of an ordinary update does not cover
an undisclosed reopen or branch restoration. Ask only about a genuinely ambiguous
target or a newly required operation.

Preparation ends at a proposal. A clear approval of that exact presented proposal
authorizes its stated implementation, verification, repairs, commits, push and PR
destination. Skill selection alone supplies no approval. Preserve narrower user
instructions and existing project/environment controls. Reuse approval for
in-scope work; ask for changed scope, missing decisions or an actual permission
limit. Review comments are evidence to assess, not authority to expand the task.
Merge and deployment require separate decisions. Stop at the requested boundary.

## Choose the procedure

- New need or unfinished proposal: read `prepare.md`.
- Approved work, execution feedback or interrupted delivery: read `deliver.md`.
- Assigned independent verification: read `verify.md`; return findings to the
  coordinator rather than implementing or publishing changes.
- Explicit read-only inspection: inspect the selected records and actual state,
  report findings, and stop without changing them or starting delivery.
- Installation, update or package comparison: read [install.md](../install.md).

For an existing batch recover its original need and decisions before selecting
the next action. Unapproved work returns to preparation. A ready PR with no new
feedback remains at human review. A closed or merged PR needs an authorized
follow-up rather than a restarted delivery. Legacy documents require the separate
migration described in the installation procedure; package replacement alone
does not migrate work or broaden earlier approval.

## One batch record

Use `ai-workflow/work/<id>/BATCH.md`. Reuse an existing issue or batch identity;
otherwise choose a distinct descriptive folder name. No central allocator,
backlog or status index is required. The coordinator owns this file. Other agents
return changes and evidence; coordinate shared writes through native controls.

The batch has four sections; omit empty tables and use short prose where enough:

| Section | Content it owns |
| --- | --- |
| Context | Original need or retained source text, repository, branch/base, PR link when known and instruction package source commit. |
| Proposal | Observable requirements with stable references, scope, decisions, technical/interface changes, small implementation steps and required verification commands or procedures. |
| Approval | The user's decision, its source/date, exact approved proposal and delivery scope; later material decisions with their reasons. |
| Continuation | Remaining work, next action, blockers, finding dispositions and links to verification evidence. |

Bind approval to immutable proposal content. Use a Git snapshot when it exists.
Otherwise retain the exact approved text with the decision in the first batch
commit before revising it; later entries can reference that commit. A mutable
revision label or a chat summary alone is insufficient. Keep history in Git,
and record reasons when changing the plan. Do not replace a requirement silently.

GitHub owns current PR, branch, CI and remote-review state. The batch records
decisions and continuation context, not another editable copy of those statuses.
The checkout owns unpublished changes. Another clone recovers the last pushed
checkpoint; local-only work remains in its existing checkout.

Keep retrievable evidence by link when durable, or in the batch's `evidence/`
directory when it must travel with the work. Retain only relevant, redacted
outputs and observations, never credentials or private production data. Evidence
describes an observation; it is not a second task-state file. Its interpretation
belongs to `verify.md`.
