# Progress log

Append only.
Use this file for detailed evidence. Do not include secrets, credentials, private customer data, proprietary logs, or production data.
Archive old evidence only with explicit user approval.

Example note: this file is fictional sanitized output for a sample task management app. Commands and validation evidence are illustrative.

## 2026-06-22

Initialized feature execution for B001.

## 2026-06-23

Task: T001

State path:
- T001 `planned -> in_progress` before editing.
- T001 `in_progress -> validated` after required validation passed.
- T001 `validated -> done` after evidence and lifecycle updates were recorded.

Changed:
- Added an overdue task query that selects incomplete tasks due before the user's local date.
- Excluded completed and undated tasks.

Validation:
- `npm test -- dashboard-task-query.test.ts` passed.

Evidence:
- Query test covers included overdue tasks.
- Query test excludes completed overdue tasks.
- Query test excludes tasks without due dates.

Review:
- Final diff was scoped to the task query layer and query tests.
- No generated files, debug code, focused tests, or sensitive data were added.

Risks or gaps:
- None.

Workflow updates:
- Marked T001 done in `IMPLEMENTATION.md`.
- Kept B001 active because T002 remained open.

## 2026-06-23

Task: T002

State path:
- T002 `planned -> in_progress` before editing.
- T002 `in_progress -> validated` after required validation passed.
- T002 `validated -> done` after evidence and lifecycle updates were recorded.
- B001 `active -> validated -> done` after all tasks and validation were complete.

Changed:
- Rendered the overdue section above today's tasks.
- Added a compact empty state for accounts with no overdue tasks.

Validation:
- `npm test -- dashboard-overdue-section.test.ts` passed.
- `npm test -- dashboard-today-section.test.ts` passed.
- Manual smoke check: dashboard showed overdue tasks above today's tasks for the sample account.

Evidence:
- UI test covers visible overdue section.
- UI test covers empty state.
- Existing today task rendering test still passes through `npm test -- dashboard-today-section.test.ts`.

Review:
- Final diff was scoped to dashboard UI and component tests.
- No generated files, debug code, focused tests, or sensitive data were added.

Risks or gaps:
- None.

Workflow updates:
- Marked T002 done in `IMPLEMENTATION.md`.
- Marked B001 done in `WORK_INDEX.md`.
- Marked NMI-001 done in `PRODUCT_BACKLOG.md`.

Commit:
- `feat: show overdue tasks on dashboard`
