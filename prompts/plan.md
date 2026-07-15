# Implementation-planning prompt

Role: Prepare one contracted batch for autonomous implementation.

Goal: Create an objective, traceable implementation plan and compact restart
state without changing application code.

Inputs: Selected batch and source rows, `FEATURE.md`, canonical policies,
repository structure, and the templates for implementation and progress files.

Success criteria:

1. Every implementation-affecting feature item has a traceability row.
2. Each small task has all fields required by `schema/workflow.schema.json`, exact
   validation commands, nearby existing checks, and stop conditions.
3. Task order reduces integration and rollback risk.
4. The scope decision is recorded using coherence criteria; counts remain advisory.
5. `IMPLEMENTATION.md`, `PROGRESS.md`, and `PROGRESS_STATE.md` exist and the batch
   becomes `ready` only after the validator passes.

Output: Create the three batch artifacts from their templates, update lifecycle
and history fields, run the validator, and report the next task or blockers.

Stop rules: Do not implement code. Stop for an unmapped contract item, missing
validation strategy, material repository conflict, or a scope that requires a
user-authorized expansion.
