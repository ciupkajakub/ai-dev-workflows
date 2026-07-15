# Agent workflow policy

## Goal and evidence

Complete the selected batch safely and end to end. The selected `FEATURE.md` is
the product contract; `IMPLEMENTATION.md` is the task and validation plan.

Do not invent requirements. Repository behavior, tests, schemas, migrations,
commands, and conventions are authoritative implementation evidence. If they
conflict with the contract, stop and report the conflict, impact, options, and
recommended next step.

## Lifecycle ownership

Use only the statuses defined for each entity in `schema/workflow.schema.json`.
That schema is the exhaustive transition source.

Lifecycle owners:

| Event | Required state updates |
| --- | --- |
| Intake grouped | backlog and batch become `planned` |
| Contract locked | `FEATURE.md`, `WORK_INDEX.md`, and source backlog items become `spec`; planning artifacts need not exist yet |
| Plan and progress artifacts valid | `FEATURE.md` stays `spec`; `IMPLEMENTATION.md`, `WORK_INDEX.md`, and `PROGRESS_STATE.md` become `ready`; source backlog stays `spec` |
| First task starts | task becomes `in_progress`; `FEATURE.md`, `IMPLEMENTATION.md`, `WORK_INDEX.md`, `PROGRESS_STATE.md`, and source backlog become `active` |
| Required validation fails | task and all batch artifacts become `failed_validation`; source backlog remains `active` or becomes `blocked` when progress cannot continue |
| Progress cannot continue safely | current task, all batch artifacts, and source backlog become `blocked` |
| All tasks and required validation pass | all batch artifacts become `validated`; source backlog remains `active` until final updates finish |
| Final audit and evidence finish | `FEATURE.md`, `IMPLEMENTATION.md`, `WORK_INDEX.md`, `PROGRESS_STATE.md`, and source backlog items become `done` |
| Scope becomes obsolete or is replaced | existing task and batch artifacts plus source backlog items become `superseded`; planning artifacts that were never created remain absent |
| Agent-created path is abandoned | task and batch become `rolled_back`; record recovery evidence and a safe backlog state |

Update top-level lifecycle fields as one operation. Never let the final response
claim a later state than the artifacts and evidence support.

## Traceability

Before a batch becomes `ready`, every functional requirement, non-functional
requirement, acceptance criterion, permission rule, assumption,
implementation-affecting risk, edge case, and failure mode must map to:

1. one or more tasks or an explicit non-code decision;
2. exact validation or evidence, or a reason validation is impossible;
3. `planned`, `verified`, `blocked`, or `accepted_gap`.

Only the user may authorize `accepted_gap`; record the approval against the
specific feature reference in `PROGRESS.md`. A batch cannot be `done` with a
`planned` or `blocked` traceability row.

## Autonomy and clarification

For review, explanation, diagnosis, planning, or audit requests, inspect and
report without implementing application changes. For change, build, or fix
requests, make safe in-scope local changes and run relevant non-destructive
validation without another confirmation.

Follow `SECURITY.md` for approval boundaries. Ask only for a missing decision that
blocks safe progress. Name the ambiguity, impact, options, recommendation, and
the default only when that default is safe. Otherwise proceed with the safest
reversible choice and record the assumption.

## Execution

Start from `PROGRESS_STATE.md`, the selected task, relevant feature criteria,
this policy, and `SECURITY.md`. Read other artifacts only when selection, scope,
history, testing, or lifecycle updates require them.

Before editing, record the branch, intended base when known, pre-existing modified
files, and selected task. Explore likely touchpoints, preserve unrelated user
changes, follow repository conventions, and make the smallest coherent change.
Do not add unrelated features, refactors, abstractions, compatibility layers, or
cleanup.

Complete one selected task at a time. Continue to another only after the current
task is verified and recorded, and only when the next task is tiny, adjacent,
low-risk, and the working context remains reliable.

## Validation and completion

Every task requires objective `done_when`, exact required validation commands,
nearby existing checks to rerun, and stop conditions. Prefer the smallest strong
signal first: targeted tests, type checks, lint, build or migration checks, smoke
tests, visual inspection, then exact manual evidence.

Related failures block completion until rerun successfully or proven unrelated
with repository-local evidence. Keep required or previously failing commands in
the open-validation list until closed. If validation cannot run, mark the task or
batch `blocked` unless the user explicitly accepts the named gap.

For user-visible UI changes, render every affected responsive state before
completion. Inspect layout, clipping, spacing, empty/loading/error states, and
consistency with existing design tokens and patterns. Record the inspected states
and findings.

Before reporting a task complete:

1. satisfy `done_when` and relevant acceptance criteria;
2. pass required validation and related existing checks;
3. inspect the final diff for scope, generated files, stale tests, debug residue,
   focused or skipped tests, and sensitive data;
4. update traceability and progress evidence;
5. run `node scripts/validate-workflow.mjs ai-workflow`.

Before marking a batch `done`, the validator must pass and the final audit must
confirm lifecycle agreement, traceability closure, empty open validation,
required passing evidence, approved gaps, safe tool use, mergeable workflow
ledgers when the base is locally available, and an accurate final report.

## Recovery

If the implementation path is wrong or repository state invalidates assumptions,
stop expanding the change. Identify agent-touched files, preserve unrelated work,
revert only agent-created changes when safe, record recovery actions, and set the
correct `rolled_back`, `blocked`, or `failed_validation` state. Do not claim
completion until a new path is verified.

## Scope decisions

Split work when parts can be deployed or rolled back independently, require
unrelated validation, cross unrelated risk areas, cannot share one coherent
completion bar, or cannot fit in reliable working context. Item, task, criterion,
and suite counts are advisory signals—not automatic blockers. Record the split
decision and rationale. Ask for approval only when continuing would materially
expand the user-authorized scope.

## State and communication

Use `PROGRESS.md` for append-only detailed evidence and `PROGRESS_STATE.md` for
compact restart state. Keep the latter under roughly 80 lines. Propose archival
when detailed ledgers become slow or unsafe to scan; never delete history without
an approved retention decision.

Before a multi-step tool task, give a one- or two-sentence update naming the first
action. Update again only at major phase changes or when a finding changes the
plan. Lead final responses with the outcome, then required evidence, material
caveats, and the next action. Preserve exact commands, paths, identifiers, and
errors; state explicitly what remains unverified.
