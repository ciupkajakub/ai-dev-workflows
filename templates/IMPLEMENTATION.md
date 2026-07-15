# Implementation plan: <batch title>

Batch: `B###`
Source items: `NMI-###`
Status: `ready`

## Scope decision

- Shared completion bar:
- Independent deployment or rollback seams:
- Validation and risk areas:
- Context assessment:
- Advisory counts: source items `<n>`; tasks `<n>`; acceptance criteria `<n>`; suites `<n>`
- Result: `coherent` | `split_recommended` | `scope_expansion_requires_approval`
- Rationale:

## Traceability closure

| Feature reference | Required item | Covered by | Validation or evidence | State |
| --- | --- | --- | --- | --- |
| Functional requirement 1 | <text> | T001 | `<exact command or evidence>` | planned |

## Tasks

```yaml
- id: T001
  status: planned
  title: <short title>
  goal: <task outcome>
  done_when:
    - <objective fact>
  acceptance_criteria:
    - FEATURE.md acceptance criterion 1
  tests_required:
    - <specific behavior>
  areas:
    - <code area>
  risk: low | medium | high
  dependencies: []
  batch_group: <group>
  validation_level: targeted_tests
  validation_commands:
    - command: <exact command>
      purpose: <what it proves>
      required: true
  existing_checks_to_rerun:
    - command: <exact command or none>
      reason: <why this check is relevant or why none exists>
  likely_files:
    - <path or area>
  context_budget: small | medium | large
  stop_conditions:
    - <specific blocker>
  source_items:
    - NMI-###
```

## Sequencing risks
