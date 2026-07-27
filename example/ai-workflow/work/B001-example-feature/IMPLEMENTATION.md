# Implementation plan: Overdue dashboard section

Batch: `B001`
Source items: `NMI-001`
Status: `done`

## Implementation scope gate

- Shared completion bar: overdue behavior, user scoping, query performance, and final dashboard states are verified together.
- Independent deployment or rollback seams: T001 and T002 can be reverted independently, but T002 depends on T001.
- Validation and risk areas: task-scoped query/UI checks and rendered states;
  batch-scoped full suite; no CI-only check.
- Context assessment: small; both tasks use adjacent dashboard touchpoints.
- Throughput assessment: T001 has two unique task checks; T002 has three; broad
  validation runs once at batch scope and neither task boundary is time-driven.
- Advisory counts: source items `1`; tasks `2`; acceptance criteria `6`;
  task-scoped checks `5`; batch-scoped checks `1`; CI-scoped checks `0`;
  estimated total task minutes `16`.
- Result: `coherent`.
- Reason: both tasks share one contract and one integrated validation story.

## Execution policy

```yaml
task_execution_policy:
  target_elapsed_minutes: 10
  max_command_seconds: 120
  no_progress_cycle_limit: 2
  max_same_check_retries_without_change: 0
  allow_repo_wide_commands: false
```

## Batch validation

```yaml
execution_budget:
  max_elapsed_minutes: 15
  max_validation_commands: 6
  max_command_seconds: 300
  state_finalization_reserve_seconds: 60
validation_commands:
  - command: npm test
    purpose: proves the integrated dashboard change does not regress the wider application suite
    required: true
    scope: batch
    timeout_seconds: 300
```

## CI validation

```yaml
validation_commands:
  - command: none
    purpose: this fictional batch has no required external-only validation
    required: false
    scope: ci
```

## Traceability closure

| Feature reference | Required item | Covered by | Validation or evidence | State |
| --- | --- | --- | --- | --- |
| Functional requirement 1 | Overdue means incomplete task due before the user's current local date. | T001 | `npm test -- dashboard-task-query.test.ts` | verified |
| Functional requirement 2 | Completed tasks do not appear in overdue section. | T001 | `npm test -- dashboard-task-query.test.ts` | verified |
| Functional requirement 3 | Overdue tasks sort by due date ascending. | T001 | `npm test -- dashboard-task-query.test.ts` | verified |
| Functional requirement 4 | Tasks due today remain in the today section. | T002 | `npm test -- dashboard-today-section.test.ts` | verified |
| Non-functional requirement 1 | Use indexed user/due-date filtering or equivalent query plan; avoid N+1 rendering. | T001 | `npm test -- dashboard-task-query.test.ts`; query plan inspection recorded in `PROGRESS.md` | verified |
| Edge case 1 | Tasks with no due date are not overdue. | T001 | `npm test -- dashboard-task-query.test.ts` | verified |
| Edge case 2 | Completed overdue tasks are excluded. | T001 | `npm test -- dashboard-task-query.test.ts` | verified |
| Edge case 3 | Timezone handling uses user's local date boundary. | T001 | `npm test -- dashboard-task-query.test.ts` | verified |
| Acceptance criterion 1 | Incomplete tasks due before today appear. | T001, T002 | Query and UI tests recorded in `PROGRESS.md` | verified |
| Acceptance criterion 2 | Completed tasks due before today do not appear. | T001 | `npm test -- dashboard-task-query.test.ts` | verified |
| Acceptance criterion 3 | Empty state appears when no overdue tasks exist. | T002 | `npm test -- dashboard-overdue-section.test.ts` | verified |
| Acceptance criterion 4 | Tasks due today remain in today section. | T002 | `npm test -- dashboard-today-section.test.ts` | verified |
| Acceptance criterion 5 | Multiple overdue tasks sort by due date ascending. | T001 | `npm test -- dashboard-task-query.test.ts` | verified |
| Acceptance criterion 6 | No N+1 query introduced for overdue rendering. | T001 | Query plan inspection recorded in `PROGRESS.md` | verified |
| Permissions rule 1 | Users can only see their own tasks. | T001 | `npm test -- dashboard-task-query.test.ts` | verified |
| Assumption 1 | App has reliable user timezone setting. | T001 | Existing user timezone fixture confirmed in `PROGRESS.md` | verified |
| Risk 1 | Timezone boundaries. | T001 | User-local date boundary test recorded in `PROGRESS.md` | verified |
| Risk 2 | Query shape/performance. | T001 | Query plan inspection recorded in `PROGRESS.md` | verified |

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
    - query sorts overdue tasks by due date ascending
    - query preserves user scoping and indexed due-date filtering
  acceptance_criteria:
    - FEATURE.md AC1
    - FEATURE.md AC2
    - FEATURE.md AC5
    - FEATURE.md AC6
  tests_required:
    - model or service test for included overdue tasks
    - test excluding completed overdue tasks
    - test excluding undated tasks
    - test sorting multiple overdue tasks by due date
    - test proving another user's overdue tasks are excluded
    - query-plan or instrumentation check proving no N+1 path
  areas:
    - task query layer
  risk: medium
  dependencies: []
  batch_group: query
  validation_level: targeted_tests
  execution_guidance:
    estimated_minutes: 8
  validation_commands:
    - command: npm test -- dashboard-task-query.test.ts
      purpose: proves overdue query includes overdue tasks, excludes completed/undated/other-user tasks, applies user-local date boundary, and sorts by due date
      required: true
      scope: task
      timeout_seconds: 120
    - command: npm test -- dashboard-query-plan.test.ts
      purpose: proves overdue rendering uses the indexed user/due-date query path or equivalent no-N+1 guard
      required: true
      scope: task
      timeout_seconds: 120
  existing_checks_to_rerun:
    - command: npm test -- dashboard-task-query.test.ts
      reason: same command as required validation because the query test file is also the nearest existing behavior coverage for the touched query layer
      scope: task
      timeout_seconds: 120
  likely_files:
    - app queries or services for dashboard tasks
    - dashboard task query tests
  context_budget: small
  references:
    - item: existing user-timezone fixture
      reason: defines the authoritative local-date boundary
    - item: existing dashboard task query and query-plan tests
      reason: define user scoping, sorting, and performance regression behavior
  applicable_skills:
    - name: none
      reason: this backend query task does not need specialized UI or conversion guidance
      required: false
      load_when: none
      required_evidence: none
  stop_conditions:
    - user timezone source is unclear
    - no reliable query-plan or instrumentation check exists for the no-N+1 requirement
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
    - populated and empty overdue states are rendered and inspected at desktop and mobile widths
    - keyboard access, legibility, and reduced-motion behavior are inspected
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
  validation_level: targeted_tests, manual_check
  execution_guidance:
    estimated_minutes: 8
  validation_commands:
    - command: npm test -- dashboard-overdue-section.test.ts
      purpose: proves overdue section visibility and empty state behavior
      required: true
      scope: task
      timeout_seconds: 120
    - command: npm test -- dashboard-today-section.test.ts
      purpose: proves existing today task rendering remains unchanged
      required: true
      scope: task
      timeout_seconds: 120
    - command: manual smoke check with synthetic local account fixture
      purpose: renders populated and empty overdue states at desktop and mobile widths and proves layout, clipping, spacing, keyboard access, legibility, reduced-motion behavior, and existing-pattern consistency without authenticated browser automation or customer data
      required: true
      scope: task
      timeout_seconds: 120
  existing_checks_to_rerun:
    - command: npm test -- dashboard-today-section.test.ts
      reason: same command as required validation because it is the existing UI regression check for unchanged today task rendering
      scope: task
      timeout_seconds: 120
  likely_files:
    - dashboard view/component
    - dashboard view/component tests
  context_budget: small
  references:
    - item: existing today-section component and dashboard tests
      reason: define placement, typography, spacing, and behavior that must remain unchanged
    - item: interactive dashboard fixture with populated and empty overdue states
      reason: provides the inspectable visual and interaction reference
  applicable_skills:
    - name: apple-design
      reason: the task changes dashboard hierarchy, feedback, responsive states, and visual integration
      required: true
      load_when: implementation and visual review
      required_evidence: desktop/mobile populated/empty renders plus keyboard, legibility, reduced-motion, and existing-pattern findings in PROGRESS.md
  stop_conditions:
    - dashboard layout has competing pending changes
  source_items:
    - NMI-001
```

## Sequencing risks

Timezone behavior should be resolved in T001 before UI work starts.
