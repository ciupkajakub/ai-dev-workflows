# Agent rules

Example note: this file is fictional sanitized output for a sample task
management app. Paths and commands are illustrative.

## Repository map

- Purpose: task management app with dashboard, project, and reminder workflows.
- Primary application areas: `app/queries/` for task selection,
  `app/components/dashboard/` for dashboard UI, and `test/dashboard/` for related
  behavior coverage.
- Generated or vendored paths: dependency and build-output directories; do not
  hand-edit them.
- High-risk areas: user scoping, timezone boundaries, reminders, and database
  migrations.

## Commands

- Setup: `npm install`
- Targeted tests: `npm test -- <test-file>`
- Full tests: `npm test`
- Typecheck: `npm run typecheck`
- Lint/format: `npm run lint`
- Build: `npm run build`

## Working agreements

- Follow the selected batch `FEATURE.md` for outcomes and constraints and
  `IMPLEMENTATION.md` for task outcomes, dependencies, validation, and stop
  conditions.
- Treat likely files and techniques as hypotheses. Existing code, tests, schemas,
  migrations, commands, and local conventions are authoritative.
- If the contract conflicts with repo evidence, stop and report the conflict,
  impact, options, and recommended next step.
- Explore before editing, preserve unrelated user changes, make the smallest
  coherent change, and avoid unrelated refactors or speculative abstractions.
- Ask only when a missing decision blocks safe progress or materially expands the
  authorized outcome. Record safe assumptions in `PROGRESS.md`.

## Workflow routing

- Start execution from `PROGRESS_STATE.md`, the selected task, relevant
  `FEATURE.md` items, and this file.
- Read detailed progress, ledgers, policies, references, and skills only when the
  selected phase or task needs them.
- Lifecycle follows
  `planned -> spec -> ready -> active -> validated -> done`.
  A task follows `planned -> in_progress -> validated -> done`.
  Use `blocked`, `failed_validation`, `superseded`, or `rolled_back` only with
  evidence and a next state.
- Apply lifecycle ownership atomically:
  - contract lock updates `FEATURE.md`, `WORK_INDEX.md`, and source NMI rows
  - valid planning updates `IMPLEMENTATION.md`, `WORK_INDEX.md`, and
    `PROGRESS_STATE.md`
  - the first task start updates the task, batch artifacts, `WORK_INDEX.md`, and
    source NMI rows from `ready/spec` to `active`
  - later task starts and task completions update only the task, touched
    traceability rows, `PROGRESS.md`, and `PROGRESS_STATE.md` unless the batch
    itself changes state
  - final completion updates every owner only after validation, traceability
    closure, evidence, and final audit pass
- Source NMI rows never use task/batch-only `failed_validation`, `validated`, or
  `rolled_back`; keep them `active` or `blocked` until final `done`, unless scope
  is explicitly `superseded`.
- Never report a later lifecycle state than the artifacts support.

## Conditional guidance

- Read `SECURITY.md` before work involving sensitive data, untrusted content,
  permissions, dependency installation, external or production systems,
  browser/MCP/app actions, CI, destructive actions, or external transmission.
- Read `TESTING_POLICY.md` when behavior or tests change.
- Reading `SECURITY.md`, `TESTING_POLICY.md`, a skill, or a reference does not
  add validation commands. `IMPLEMENTATION.md` assigns each check to task,
  batch, or CI scope; run it only at that scope.
- Load only skills listed for the selected batch/task or whose description
  clearly matches the work; record material evidence in `PROGRESS.md`. If a
  required skill is unavailable, stop or use an explicitly approved fallback.
- Open only references that can change implementation or verification.
- For UI work, render the affected responsive, loading, empty, error, and
  interaction states. When a design skill applies, include accessibility and
  reduced-motion checks.
- For conversion work, require a funnel stage, conversion goal, baseline or
  explicit unknown, hypothesis, primary metric, and guardrails. Experiments also
  need a sample-size method and duration.

## Completion gates

A task is done only when:

1. `done_when` and relevant acceptance criteria are satisfied
2. required task-scoped validation and focused existing regression checks pass
   within the task execution budget
3. previously failed task-scoped checks pass after the fix or are proven unrelated
4. touched traceability rows contain evidence
5. final diff review finds no unrelated changes, temporary code, focused/skipped
   tests, generated-file mistakes, or sensitive data
6. detailed evidence, compact state, task status, and lifecycle owners agree

Batch- and CI-scoped validation does not run during task execution; it remains
open and blocks the batch, not a completed task. If task validation is missing,
times out, or fails, use `blocked` or `failed_validation`. `accepted_gap`
requires explicit user acceptance recorded in `PROGRESS.md`. Before a batch
becomes `done`, section 13 with `Mode: validate_and_audit` must pass, all scoped
open validation lists must be empty, and every required traceability row must be
`verified` or an approved `accepted_gap`.

## Context and communication

- Keep `PROGRESS_STATE.md` compact; put detailed evidence in append-only
  `PROGRESS.md`.
- One task per turn. Obey the selected `IMPLEMENTATION.md` Execution policy;
  section 10 must split work that cannot fit.
- Lead updates and final reports with outcome, evidence, caveats, and next action.
- Keep exact commands, paths, identifiers, and errors unchanged.
