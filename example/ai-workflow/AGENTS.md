# Agent rules

## Contract

Follow `FEATURE.md` and `IMPLEMENTATION.md` as the feature contract.

Do not invent requirements.

Repo behavior, existing tests, schemas, migrations, command output, and conventions are authoritative implementation evidence.

If the feature contract conflicts with repo evidence, stop and report the conflict, why it matters, likely options, and the recommended next step.

## Clarification

Ask for clarification only when the missing decision blocks safe progress.

If a reasonable default is safe and consistent with the contract, proceed and record the assumption in `PROGRESS.md`.

## Execution discipline

Explore before editing. Prefer the smallest coherent change. Avoid unrelated refactors. Follow existing repo conventions first.

## Done discipline

Mark a task done only after `done_when` is satisfied, relevant acceptance criteria are checked, validation was run or the exact gap is recorded, and evidence is appended to `PROGRESS.md`.

## Validation discipline

Run the smallest reliable check first. Prefer tests, typecheck, lint, build, migration checks, smoke tests, visual checks, or exact command output depending on the task.

## Context hygiene

Default to one task per session. Continue only when the next task is small, adjacent, and low risk.
