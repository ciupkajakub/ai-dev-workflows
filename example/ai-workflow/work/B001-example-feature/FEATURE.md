# Feature: Overdue dashboard section

Batch: `B001`
Source items: `NMI-001`
Folder: `ai-workflow/work/B001-example-feature/`
Status: `done`

## 1. Problem / Context

Users miss overdue tasks because the dashboard focuses on tasks due today.

## 2. Goals

1. Show incomplete overdue tasks in a dedicated dashboard section.
2. Keep overdue tasks visually distinct from today's tasks.
3. Provide an empty state when there are no overdue tasks.

## 3. Non goals

1. Do not add reminders.
2. Do not change project-level task filtering.
3. Do not change task completion behavior.

## 4. Users and roles

Authenticated users viewing their own dashboard.

## 5. UX and flows

When a user opens the dashboard, the overdue section appears above today's tasks if overdue tasks exist. If none exist, the section shows a compact empty state.

## 6. Functional requirements

1. A task is overdue when it is incomplete and its due date is before the user's current local date.
2. Completed tasks must not appear in the overdue section.
3. Overdue tasks must be sorted by due date ascending.
4. Tasks due today remain in the existing today section.

## 7. Non functional requirements

1. The dashboard query must use the existing indexed task due-date/user filtering path or an equivalent query plan; it must not introduce an N+1 query for overdue task rendering.

## 8. Data and system impact

No schema changes are required.

## 9. Edge cases and failure modes

1. Tasks with no due date are not overdue.
2. Completed overdue tasks are excluded.
3. Timezone handling must use the user's local date boundary.

## 10. Acceptance criteria

1. Given incomplete tasks due before today, they appear in the overdue section.
2. Given completed tasks due before today, they do not appear in the overdue section.
3. Given no overdue tasks, the dashboard shows an overdue empty state.
4. Given tasks due today, they remain in the today section.
5. Given multiple overdue tasks, they are sorted by due date ascending.
6. Given overdue tasks render on the dashboard, the implementation uses the existing indexed user/due-date query path or equivalent evidence shows no N+1 query was introduced.

## 11. Permissions and visibility rules

1. Users can only see their own tasks.

## 12. Rollout and verification

Verify with targeted dashboard query tests, dashboard UI tests, a query-plan or
equivalent no-N+1 check, and local rendering of overdue and empty states at desktop
and mobile widths. Inspect layout, clipping, spacing, and consistency with existing
dashboard patterns.

## 13. Risks and open questions

1. Timezone boundaries are the main behavior risk.
2. Query shape is the main performance risk.

## 14. Assumptions

1. The app already has a reliable user timezone setting.

## 15. Scope decision

- Coherent user-visible outcome: one overdue dashboard section backed by one query path.
- Independent deployment or rollback seams: query and UI tasks can be reverted separately but share one acceptance contract.
- Validation and risk areas: task query behavior, timezone boundary, query shape, dashboard layout.
- Context assessment: small; query and UI touchpoints are adjacent.
- Advisory counts: source items `1`; acceptance criteria `6`.
- Result: `coherent`.
- Rationale: the work shares one user-visible outcome and one integrated validation story.

## 16. Lifecycle updates

NMI-001 and B001 were marked done together after required validation, traceability
closure, evidence updates, and the final audit.
