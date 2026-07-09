# Agent rules

## Contract

Follow the selected batch `FEATURE.md` and `IMPLEMENTATION.md` as the feature contract.

Do not invent requirements.

Repo behavior, existing tests, schemas, migrations, commands, and conventions are authoritative implementation evidence.

If the feature contract conflicts with repo evidence, stop and report:

1. the conflict
2. why it matters
3. likely options
4. recommended next step

## Lifecycle state machine

Use these status meanings consistently across workflow files:

- `planned`: known work that is not ready for execution
- `spec`: `FEATURE.md` exists, but execution planning is not complete
- `ready`: `IMPLEMENTATION.md`, `PROGRESS.md`, and `PROGRESS_STATE.md` exist and tasks are objective
- `active`: implementation has started
- `in_progress`: selected T* task is currently being edited
- `blocked`: progress cannot continue safely without missing input, permission, environment, or a passing related validation signal
- `failed_validation`: implementation exists, but a required related validation command failed
- `validated`: selected T* task satisfies `done_when` and required validation passed, but ledger/final updates may still be pending
- `done`: validated work plus required evidence, progress state, and lifecycle updates are complete
- `superseded`: replaced by newer scope; do not implement unless user reactivates it
- `rolled_back`: agent-created implementation was reverted or abandoned and recovery evidence was recorded

Required transitions:

1. `planned -> spec`: `FEATURE.md` is written and contract lock checklist passes.
2. `spec -> ready`: `IMPLEMENTATION.md`, `PROGRESS.md`, and `PROGRESS_STATE.md` exist; every task has status, objective `done_when`, validation plan, and stop conditions.
3. `ready -> active`: first task starts; update `WORK_INDEX.md` and `PROGRESS_STATE.md` before editing.
4. `planned -> in_progress`: selected T* task starts.
5. `in_progress -> blocked`: missing requirement, repo conflict, permission limit, unsafe validation, or unresolved related validation failure blocks progress.
6. `in_progress -> failed_validation`: implementation was attempted but required related validation failed.
7. `failed_validation -> in_progress`: fix attempt starts.
8. `in_progress -> validated`: `done_when` is satisfied and required related validation passed.
9. `validated -> done`: `PROGRESS.md`, `PROGRESS_STATE.md`, `IMPLEMENTATION.md`, and lifecycle rows are updated.
10. `active -> done`: all T* tasks are done, open validation list is empty, and batch/backlog lifecycle rows are updated.
11. `active|blocked -> superseded`: user explicitly replaces the scope with newer backlog or batch work.
12. `active|blocked|failed_validation -> rolled_back`: agent-created code changes are reverted or abandoned; record exact files, commands, remaining risk, and next state.

## Clarification

Ask for clarification only when the missing decision blocks safe progress.

When asking, include:

1. what is ambiguous
2. why it matters
3. options
4. recommendation
5. default if no answer

If a reasonable default is safe and consistent with the contract, proceed and record the assumption in `PROGRESS.md`.

## Execution discipline

Explore before editing.
Identify likely files and touchpoints before implementation.
Prefer the smallest coherent change.
Avoid unrelated refactors.
Follow existing repo conventions first.
Use parallel reading/searching when independent touchpoints need investigation.
Do not use parallel write workflows unless file ownership boundaries are explicit and low overlap.

## Done discipline

Mark a task done only after:

1. `done_when` is satisfied
2. relevant acceptance criteria are checked
3. required related validation passed
4. evidence is appended to `PROGRESS.md`

If verification is partial, do not claim completion.

If required validation cannot be run, mark the task or batch `blocked` unless the user explicitly accepts an unvalidated state. Recording a validation gap is blocker evidence, not completion evidence.

Do not mark a task, batch, or backlog item done while any validation command in a touched or directly related area is failing unless the failure has been proven unrelated by reproducing it on the base branch or by another concrete repo-local explanation. Record that proof in `PROGRESS.md`.

Previously failed validation commands in the same batch are not optional. Final validation must rerun them after fixes, or the batch must remain blocked with a clear reason.

## Validation discipline

Every task needs a practical verification plan.
Prefer the strongest practical signal:

1. tests
2. typecheck
3. lint
4. build
5. migration check
6. smoke test
7. screenshot or visual comparison
8. exact command output

Run the smallest reliable check first.
Record validation evidence in `PROGRESS.md`.

When a validation failure appears in a touched or directly related area, treat it as blocking by default. Do not downgrade it to residual risk merely because a smaller focused subset passes.

If a broader suite is too slow or noisy, run a smaller reliable command first, but keep the failing broader command in the batch's open validation list until it passes or is proven unrelated.

Record the open validation list in `PROGRESS_STATE.md` whenever a required or previously failing command still needs rerun, proof, or user acceptance.

Final validation must include existing tests or checks that exercise the touched behavior, not only tests added by the current batch. When UI copy, labels, controls, selectors, routes, or interaction semantics change, rerun the nearest existing request/system/browser specs that operate through that UI. If those existing specs need expectation updates because the intended behavior changed, update them in the same task and rerun them before marking the task or batch done.

If workflow ledger files such as `PRODUCT_BACKLOG.md` or `WORK_INDEX.md` changed, check mergeability against the intended base branch before final completion when that base is discoverable locally. Record any ledger conflict as a blocker or resolve it before marking the batch done.

## Recovery and rollback

Before editing, record enough dirty-repo context to avoid overwriting unrelated user work:

1. current branch
2. intended base branch when known
3. pre-existing modified files, if any
4. selected task id

If implementation path is wrong, validation failure requires backing out, or the repo state differs from assumptions:

1. stop expanding the change
2. identify agent-touched files
3. preserve unrelated user changes
4. revert only agent-created changes when rollback is needed and safe
5. record rollback commands or manual actions in `PROGRESS.md`
6. update `PROGRESS_STATE.md` with current status, remaining risk, and next step
7. set task or batch status to `rolled_back`, `blocked`, or `failed_validation` as appropriate
8. do not claim completion until a new validated path is finished

## Batch size gate

Before implementation planning or execution, perform a short size review for the selected batch:

1. source NMI count
2. implementation task count
3. acceptance criteria count
4. risk areas touched
5. recommended split, if any

Record the result with these fields:
Size gate:
- Source NMI count:
- Implementation task count:
- Acceptance criteria count:
- Risk areas:
- Result: pass | split_recommended | user_approved_large_scope
- Reason:

Stop and recommend splitting before implementation when any of these are true:

1. more than 3 source NMI items
2. more than 6 implementation tasks
3. more than 12 acceptance criteria
4. unrelated risk areas are grouped together, such as auth plus reporting plus public routing plus localization
5. final validation would need many unrelated suites to prove the batch

Continue without asking only when the batch is below those limits or when the user explicitly approves the larger scope after the size review.

## Review gate

Before marking a task done, inspect the final diff for:

1. files outside selected task scope
2. generated files edited by hand
3. missing tests or stale expectations
4. leftover debug code, focused tests, skipped tests, or temporary logs
5. secrets or sensitive data in code, tests, screenshots, commits, or workflow files

Record the review result in `PROGRESS.md`. If review finds a blocking issue, fix it or mark the task `blocked`; do not mark it done.

## Security and permissions

Follow `ai-workflow/SECURITY.md` before using tools, handling sensitive data, calling external services, or recording workflow evidence.
If `SECURITY.md` and a task prompt conflict, follow the stricter rule and report the conflict.

## Context hygiene

Read only the files and artifact sections needed for the current task.
Default to one task per session.
Continue only when the next task is small, adjacent, and low risk.
If exploration becomes noisy, summarize findings in `PROGRESS.md` and restart from artifacts.

## Ledger hygiene

Keep `PROGRESS_STATE.md` compact enough to reload quickly.
Use `PROGRESS.md` for detailed evidence, not repeated summaries.
Default size targets:

1. keep `PROGRESS_STATE.md` under 80 lines
2. propose archiving `PROGRESS.md` after 300 lines
3. propose archiving done or superseded backlog/history entries when `PRODUCT_BACKLOG.md` or `WORK_INDEX.md` becomes slow to scan

When `PRODUCT_BACKLOG.md`, `WORK_INDEX.md`, or `PROGRESS.md` grows too large to scan safely, propose an archive file such as `ai-workflow/archive/YYYY-MM.md` or `ai-workflow/work/B###/PROGRESS_ARCHIVE.md` before continuing.
Do not delete historical evidence unless the user explicitly approves an archival or retention policy.

## Communication

Be concise and technical.
Keep commands, file paths, identifiers, and exact error messages unchanged.
