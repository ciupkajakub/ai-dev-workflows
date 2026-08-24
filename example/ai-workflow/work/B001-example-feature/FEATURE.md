# Feature: Overdue dashboard section

Batch: `B001`
Source items: `NMI-001`
Folder: `ai-workflow/work/B001-example-feature/`
Status: `done`
Completion level: `feature`
Workflow schema: `2`
Blueprint source: `feature_execution_blueprint.md`
Blueprint revision: `2.4.0`
Blueprint digest: `de5c2c52bb128c3337bc0c7c38c40833ac5badc84f13b8bbfa1d343b51ea7039`

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

FR1. A task is overdue when it is incomplete and its due date is before the user's current local date.
FR2. Completed tasks must not appear in the overdue section.
FR3. Overdue tasks must be sorted by due date ascending.
FR4. Tasks due today remain in the existing today section.

## 7. Non functional requirements

NFR1. The dashboard query must use the existing indexed task due-date/user filtering path or an equivalent query plan; it must not introduce an N+1 query for overdue task rendering.

## 8. Data and system impact

No schema changes are required.

### Changed contracts and consumer inventory

| Changed seam | Known consumers and search evidence | Compatibility decision | Regression proof |
| --- | --- | --- | --- |
| Dashboard task-query result and section ordering | Existing today-section component, dashboard task-query tests, today-section tests, and dashboard smoke fixture; repository searches covered the query entrypoint, section label, and existing selectors. | Preserve the today-section contract and add overdue results without renaming existing selectors. | T001 query/query-plan checks plus T002 today-section and rendered-state checks. |

## 9. Edge cases and failure modes

Edge1. Tasks with no due date are not overdue.
Edge2. Completed overdue tasks are excluded.
Edge3. Timezone handling must use the user's local date boundary.

## 10. Acceptance criteria

AC1. Given incomplete tasks due before today, they appear in the overdue section.
AC2. Given completed tasks due before today, they do not appear in the overdue section.
AC3. Given no overdue tasks, the dashboard shows an overdue empty state.
AC4. Given tasks due today, they remain in the today section.
AC5. Given multiple overdue tasks, they are sorted by due date ascending.
AC6. Given overdue tasks render on the dashboard, the implementation uses the existing indexed user/due-date query path or equivalent evidence shows no N+1 query was introduced.

## 11. Permissions and visibility rules

Permission1. Users can only see their own tasks.

## 12. Rollout and verification

Verify with targeted dashboard query tests, dashboard UI tests, a query-plan or
equivalent no-N+1 check, and a local smoke check of the affected responsive,
populated, and empty states. The UI review must also check keyboard access,
legibility, and reduced-motion behavior.

## 13. Risks and open questions

Risk1. Timezone boundaries are the main behavior risk.
Risk2. Query shape is the main performance risk.

## 14. Assumptions

Assumption1. The app already has a reliable user timezone setting.

## 15. References and applicable skills

References:

1. Existing today-section component and its dashboard tests define placement,
   typography, spacing, and unchanged behavior.
2. Existing user-timezone fixture defines the local-date boundary.
3. A small interactive dashboard fixture with populated and empty overdue states
   is the preferred visual reference; screenshots are supporting evidence only.

Applicable skills:

1. `apple-design`
   - Reason: the batch changes dashboard hierarchy, feedback, responsive states,
     and visual integration with an existing surface.
   - Required: no; advisory when available.
   - Phases: feature contract, T002 implementation, visual review.
   - Required evidence: affected desktop/mobile and populated/empty states,
     keyboard access, legibility, reduced motion, and consistency with existing
     dashboard patterns.
   - Portable fallback: apply the Visual contract below directly and record the
     same rendered-state, accessibility, and reduced-motion evidence.

Not applicable:

- `conversion-optimization`: this batch improves operational clarity and does not
  define a conversion funnel, conversion goal, experiment, or uplift claim.

### Visual contract

- VIS1 Direction status: `repo_reference`.
- VIS2 Rendered direction: preserve the existing dashboard identity and place the
  overdue section above today's tasks in the interactive populated/empty fixture.
- VIS3 Rubric: coherent hierarchy, existing-product identity, consistent density and
  spacing, obvious overdue/today distinction, unchanged primary actions,
  responsive populated/empty states, keyboard access, legibility, and reduced
  motion.

## 16. Backlog and batch updates

NMI-001 and B001 were marked done after verification.

Feature scope gate:
- Source NMI count: 1
- Estimated acceptance criteria count: 6
- Risk areas: task query layer, dashboard UI
- Result: coherent
- Reason: the query and dashboard presentation share one user-visible outcome, one permission model, related risks, and one integrated validation story.
