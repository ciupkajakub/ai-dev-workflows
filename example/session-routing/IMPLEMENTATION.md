# Implementation excerpt: intentional session continuation

This sanitized generated-plan excerpt demonstrates both task session modes. It
is not an indexed batch and is not executed by the example workflow.

Workflow schema: `3`

```yaml
- id: T001
  status: planned
  outcome: Identify and record the undocumented parser invariant.
  dependencies: []
  feature_refs:
    - AC1
  validation_commands:
    - command: python3 verify_reproduction.py
      id: V001
      purpose: proves the failure and records the invariant needed by the repair
      required: true
      scope: task
      timeout_seconds: 120
      required_capabilities: [filesystem]

- id: T002
  status: planned
  outcome: Apply the invariant discovered by T001 to the same local parser path.
  dependencies:
    - T001
  session:
    mode: continue
    from_task: T001
    reason: the immediate repair reuses T001's runtime-only parser investigation and local diagnostic state, which would be expensive to reconstruct
  feature_refs:
    - AC2
  validation_commands:
    - command: python3 verify_repair.py
      id: V002
      purpose: proves the repaired parser behavior
      required: true
      scope: task
      timeout_seconds: 120
      required_capabilities: [filesystem]
```
