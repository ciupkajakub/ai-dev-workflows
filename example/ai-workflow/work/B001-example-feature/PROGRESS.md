# Progress log

Append only.
Use this file for detailed evidence. Do not include secrets, credentials, private customer data, proprietary logs, or production data.
Archive old evidence only with explicit user approval.

Example note: this file is fictional sanitized output for a sample task management app. Commands and validation evidence are illustrative.

## 2026-06-22

Initialized feature execution for B001.

## 2026-06-23

Task: T001

Changed:
- Added an overdue task query that selects incomplete tasks due before the user's local date.
- Excluded completed and undated tasks.

Validation:
- `npm test -- dashboard-task-query.test.ts` passed.

Evidence:
- Query test covers included overdue tasks.
- Query test excludes completed overdue tasks.
- Query test excludes tasks without due dates.

Risks or gaps:
- None.

Workflow updates:
- Marked T001 done in `IMPLEMENTATION.md`.

## 2026-06-23

Task: T002

Changed:
- Rendered the overdue section above today's tasks.
- Added a compact empty state for accounts with no overdue tasks.

Validation:
- `npm test -- dashboard-overdue-section.test.ts` passed.
- Manual smoke check: dashboard showed overdue tasks above today's tasks for the sample account.

Evidence:
- UI test covers visible overdue section.
- UI test covers empty state.
- Existing today task rendering test still passes.

Risks or gaps:
- None.

Workflow updates:
- Marked T002 done in `IMPLEMENTATION.md`.
- Marked B001 done in `WORK_INDEX.md`.
- Marked NMI-001 done in `PRODUCT_BACKLOG.md`.

Commit:
- `feat: show overdue tasks on dashboard`
