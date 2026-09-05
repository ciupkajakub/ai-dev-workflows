# Implementation plan: Overdue dashboard section

Batch: `B001`
Workflow schema: `3`
Blueprint source: `feature_execution_blueprint.md`
Blueprint revision: `3.0.0`
Blueprint digest: `4ec4a15ff4b2718372b62fb42af6c10359f1c7028ea0c2e0820b9b2ae5eaaf4b`

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
    id: V001
    purpose: proves the integrated change against the wider application suite
    required: true
    scope: batch
    timeout_seconds: 300
    required_capabilities: [filesystem]
```

## CI validation

This fictional feature has no required external-only checks or deployment proof.

## Coverage

| Feature refs | Consumers and compatibility | Owner / validation ids | Evidence |
| --- | --- | --- | --- |
| AC1, AC2, AC5, C1 | Query consumers preserve user scoping, local dates, exclusions, and order; search evidence in C2. | T001 / V002 | [Query recovery](PROGRESS.md#2026-06-23-1) |
| AC6 | Indexed query/rendering path remains free of N+1 fetches. | T001 / V003 | [Query-plan proof](PROGRESS.md#2026-06-23-1) |
| AC3, AC4, C2 | Existing today component, stable selectors, and overdue empty state remain compatible. | T002 / V004, V005 | [Component proof](PROGRESS.md#2026-06-23-2) |
| AC7, C3 | Synthetic populated/empty responsive fixture preserves the visual contract. | T002 / V006 | [Final visual proof](PROGRESS.md#2026-07-27--context-routing-clarification) |
| AC1-AC7 | Combined dashboard behavior. | T001, T002 / V001 | [Final batch proof](PROGRESS.md#2026-07-27--context-routing-clarification) |

## Tasks

```yaml
- id: T001
  status: done
  outcome: Return the current user's incomplete overdue tasks in local-date order through the existing dashboard query seam; use the timezone fixture and retain indexed filtering.
  feature_refs: [AC1, AC2, AC5, AC6, C1, C2]
  dependencies: []
  validation_commands:
    - command: npm test -- dashboard-task-query.test.ts
      id: V002
      purpose: proves overdue inclusion, completed/undated/other-user exclusion, local dates, and ascending order
      required: true
      scope: task
      timeout_seconds: 120
      required_capabilities: [filesystem]
    - command: npm test -- dashboard-query-plan.test.ts
      id: V003
      purpose: proves indexed user/due-date filtering and no N+1 rendering
      required: true
      scope: task
      timeout_seconds: 120
      required_capabilities: [filesystem]

- id: T002
  status: done
  outcome: Render the overdue and empty states above today's unchanged section using the existing component and synthetic fixture as the visual references.
  feature_refs: [AC3, AC4, AC7, C2, C3]
  dependencies:
    - T001
  validation_commands:
    - command: npm test -- dashboard-overdue-section.test.ts
      id: V004
      purpose: proves overdue visibility and empty state
      required: true
      scope: task
      timeout_seconds: 120
      required_capabilities: [filesystem]
    - command: npm test -- dashboard-today-section.test.ts
      id: V005
      purpose: proves existing today-section behavior remains unchanged
      required: true
      scope: task
      timeout_seconds: 120
      required_capabilities: [filesystem]
    - command: manual smoke check with synthetic local account fixture
      id: V006
      purpose: proves AC7 in populated/empty desktop/mobile states, including keyboard, legibility, reduced motion, and existing visual patterns
      required: true
      scope: task
      timeout_seconds: 120
      required_capabilities: [filesystem, browser]
```

Both tasks use schema 3's fresh-context default. T002 depends on durable query
output; it does not need T001's conversation. If a required assertion or query-plan
check is missing, repair it in the owning task instead of declaring a blocker.
