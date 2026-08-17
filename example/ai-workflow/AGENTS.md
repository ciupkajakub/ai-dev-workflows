# Agent rules

Workflow schema: `2`
Blueprint source: `feature_execution_blueprint.md`
Blueprint revision: `2.2.0`
Blueprint digest: `270e71dfc2af0bbadf458e08694fbf7321575d5af6e8929b730a4ffe721b3425`

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

- Follow the selected blueprint section as the source of procedure, `FEATURE.md`
  for the locked outcome, and `IMPLEMENTATION.md` for task scope and validation.
- Start runtime work from `PROGRESS_STATE.md`, the selected task, its exact
  `feature_refs`, and this repo map. Load detailed progress, ledgers, policies,
  references, and skills only when the selected phase or task needs them.
- Treat likely files and techniques as hypotheses. Explore before editing,
  preserve unrelated work, and make the smallest coherent change.
- Read `TESTING_POLICY.md` when behavior or tests change. Read `SECURITY.md`
  before sensitive-data, permission, dependency, browser/app, CI, production,
  destructive, untrusted-content, or external-transmission work.
- A listed skill is advisory unless its task marks it required and provides a
  portable fallback. Use the fallback when a provider-specific skill is absent.
- Keep `PROGRESS_STATE.md` compact and `PROGRESS.md` append-only. Record evidence
  before advancing a task, batch, or backlog item; never report a later state
  than all lifecycle owners support.
- Section 11 continues across dependency-ready tasks and owns final verification
  and repair. Section 13 is only its repair/audit compatibility entry point.
- Ask only for a genuinely blocking product decision or a new permission,
  side-effect, data, or scope boundary.
- Preserve exact commands, paths, identifiers, and errors except required
  sensitive-data redaction; mark every redaction explicitly.
