# Implementation plan: Overdue dashboard section

Batch: `B001`
Source items: `NMI-001`
Status: `done`
Completion level: `feature`
Delivery lane: `standard`
Workflow schema: `2`
Blueprint source: `feature_execution_blueprint.md`
Blueprint revision: `2.1.1`
Blueprint digest: `710e0fa0523beee315e3918496de503df648c79b11063a35aaf3e518ad5821ac`

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
  estimated total task minutes `20-35`.
- Result: `coherent`.
- Reason: both tasks share one contract and one integrated validation story.

## Execution policy

```yaml
task_execution_policy:
  continuation_mode: batch_to_verified_outcome
  progress_checkpoint_minutes: 10
  max_command_seconds: 120
  same_root_cause_no_progress_limit: 3
  max_same_check_retries_without_change: 0
  allow_repo_wide_commands: false
```

## Batch validation

```yaml
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

## Impact map

| Changed seam | Change | Known consumers and search evidence | Compatibility decision | Owner | Regression proof | State |
| --- | --- | --- | --- | --- | --- | --- |
| Dashboard task-query result and section ordering | Add overdue results and render them before today without renaming existing selectors. | Existing today-section component, task-query/today-section tests, and dashboard smoke fixture; searches covered the query entrypoint, labels, and selectors. | Preserve today's behavior and selector contract. | T001, T002 | Query/query-plan tests, today-section regression test, and live responsive fixture review. | verified |

## Traceability closure

| Feature reference | Required item | Covered by | Validation or evidence | State |
| --- | --- | --- | --- | --- |
| FR1-FR3, Edge1-Edge3, AC1, AC2, AC5, Permission1, Assumption1, Risk1 | Select the correct user's incomplete overdue tasks at the local-date boundary, excluding completed/undated tasks and sorting ascending. | T001 | `npm test -- dashboard-task-query.test.ts`; timezone fixture evidence in `PROGRESS.md`. | verified |
| NFR1, AC6, Risk2 | Preserve the indexed user/due-date path and avoid N+1 rendering. | T001 | `npm test -- dashboard-query-plan.test.ts`; query-plan evidence in `PROGRESS.md`. | verified |
| FR4, AC4 | Today's tasks and existing section behavior remain unchanged. | T002 | `npm test -- dashboard-today-section.test.ts`. | verified |
| AC1, AC3 | Render overdue tasks above today and show the empty state when needed. | T001, T002 | Query result plus `npm test -- dashboard-overdue-section.test.ts`. | verified |
| UX5, rollout verification, visual contract | Populated/empty desktop/mobile states satisfy hierarchy, identity, spacing, distinction, keyboard, legibility, and reduced-motion criteria. | T002 | Live synthetic fixture review and visual-rubric evidence in `PROGRESS.md`. | verified |

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
    estimated_minutes: 10-18
    confidence: medium
    rationale: one existing query seam, timezone fixture, and two focused checks; query-plan details may vary
    internal_milestones: none
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
    estimated_minutes: 10-17
    confidence: medium
    rationale: one existing dashboard component, two focused tests, and one live responsive visual review
    internal_milestones: none
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
