# Implementation plan: Overdue dashboard section

Batch: `B001`
Source items: `NMI-001`
Status: `done`

## Size gate

- Source NMI count: 1
- Implementation task count: 2
- Acceptance criteria count: 4
- Risk areas: task query layer, dashboard UI
- Result: pass
- Reason: batch is below split thresholds and risk areas are adjacent.

## Tasks

```yaml
- id: T001
  status: done
  title: Add overdue task query
  goal: Return incomplete tasks due before the user's local date.
  done_when:
    - query excludes completed tasks
    - query excludes tasks without due dates
    - query uses the user's local date boundary
  acceptance_criteria:
    - FEATURE.md AC1
    - FEATURE.md AC2
  tests_required:
    - model or service test for included overdue tasks
    - test excluding completed overdue tasks
    - test excluding undated tasks
  areas:
    - task query layer
  risk: medium
  dependencies: []
  batch_group: query
  validation_level: targeted_tests
  likely_files:
    - app queries or services for dashboard tasks
    - dashboard task query tests
  context_budget: small
  stop_conditions:
    - user timezone source is unclear
  source_items:
    - NMI-001

- id: T002
  status: done
  title: Render overdue section on dashboard
  goal: Display overdue tasks above today's tasks with an empty state.
  done_when:
    - overdue section appears above today section
    - empty state appears when no overdue tasks exist
    - existing today task rendering is unchanged
  acceptance_criteria:
    - FEATURE.md AC3
    - FEATURE.md AC4
  tests_required:
    - view or component test for overdue section
    - view or component test for empty state
  areas:
    - dashboard UI
  risk: low
  dependencies:
    - T001
  batch_group: ui
  validation_level: targeted_tests
  likely_files:
    - dashboard view/component
    - dashboard view/component tests
  context_budget: small
  stop_conditions:
    - dashboard layout has competing pending changes
  source_items:
    - NMI-001
```

## Status update rules

Mark B001 done only when both tasks are verified and evidence is recorded in `PROGRESS.md`.

## Sequencing risks

Timezone behavior should be resolved in T001 before UI work starts.
