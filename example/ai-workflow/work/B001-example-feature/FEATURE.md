# Feature: Overdue dashboard section

Batch: `B001`
Source items: `NMI-001`
Completion level: `feature`
Workflow schema: `3`
Blueprint source: `feature_execution_blueprint.md`
Blueprint revision: `3.0.0`
Blueprint digest: `4ec4a15ff4b2718372b62fb42af6c10359f1c7028ea0c2e0820b9b2ae5eaaf4b`

## 1. Outcome

Authenticated users miss overdue tasks because the dashboard emphasizes tasks
due today. Show their incomplete overdue tasks above today's tasks so they can
find overdue work without changing the existing completion workflow.

## 2. Scope

Add overdue selection, ordering, display, and an empty state to the existing
dashboard. Query and presentation share one user-visible outcome and validation
story. Preserve today's section and existing selectors. Reminders, project-level
filtering, task completion changes, and schema migrations are outside this batch.

## 3. Acceptance criteria

AC1. Show only the current user's incomplete tasks whose due date precedes that
user's local date. Exclude undated tasks and apply the local-date boundary.
AC2. Exclude completed overdue tasks.
AC3. Show a compact overdue empty state when no overdue tasks exist.
AC4. Tasks due today remain in the existing today section with unchanged behavior.
AC5. Sort multiple overdue tasks by due date ascending.
AC6. Use the existing indexed user/due-date query path or equivalent query-plan
proof and introduce no N+1 query during overdue rendering.
AC7. Render overdue above today in populated/empty desktop and mobile states.
Preserve the dashboard's hierarchy, identity, density, spacing, and primary
commands; prevent clipping and maintain keyboard access, legibility, and reduced
motion. This is the visual rubric for the change.

## 4. Decisions and constraints

C1. Use the existing user-timezone setting and fixture as the local-date authority.
Timezone boundaries and query shape require focused regression proof.
C2. Preserve the dashboard task-query result and section-ordering contract for
existing today-section consumers. The illustrative repository search covered
the query entrypoint, section labels, stable selectors, task-query/today tests,
and synthetic dashboard fixture. Assign proof for these consumers in the plan.
C3. The existing today-section component defines the visual direction. Use a
synthetic interactive fixture for inspection; authenticated browser automation
requires the project's recorded approval. The apple-design skill is advisory
for UI implementation/review when available; AC7 is the portable visual contract.

Legacy reference mapping, retained for the unchanged historical evidence:
FR1/Edge3/Permission1 -> AC1; FR2/Edge2 -> AC2; FR3 -> AC5; FR4 -> AC4;
Edge1 -> AC1; NFR1 -> AC6; Assumption1/Risk1 -> C1; Risk2 -> AC6;
VIS1/VIS2/VIS3 -> AC7/C3. Existing AC1-AC6 identifiers retain their meaning.

## 5. Verification

Prove query inclusion/exclusion, local dates, user isolation, sorting, and query
shape with focused query tests. Prove overdue/empty and unchanged today behavior
with component tests. Inspect the synthetic populated/empty fixture at desktop
and mobile widths against AC7. Run the broader local suite once after task proof.
Local feature delivery needs this evidence and consumer compatibility; this
fictional batch requires no external CI or deployment proof.
