# Implementation excerpt: intentional session continuation

This sanitized generated-plan excerpt demonstrates both task session modes. It
is not an indexed batch and is not executed by the example workflow.

```yaml
- id: T001
  status: planned
  title: Reproduce and instrument local parser failure
  goal: Identify and record the undocumented parser invariant.
  dependencies: []
  session:
    mode: fresh
    reason: the task can reconstruct its context from the failure fixture, repository code, and focused validation
  feature_refs:
    - FR1
  validation_commands:
    - command: python3 verify_reproduction.py
      purpose: proves the failure and records the invariant needed by the repair
      required: true
      scope: task
      timeout_seconds: 120

- id: T002
  status: planned
  title: Repair the investigated parser path
  goal: Apply the invariant discovered by T001 to the same local parser path.
  dependencies:
    - T001
  session:
    mode: continue
    from_task: T001
    reason: the immediate repair reuses T001's runtime-only parser investigation and local diagnostic state, which would be expensive to reconstruct
  feature_refs:
    - FR2
  validation_commands:
    - command: python3 verify_repair.py
      purpose: proves the repaired parser behavior
      required: true
      scope: task
      timeout_seconds: 120
```
