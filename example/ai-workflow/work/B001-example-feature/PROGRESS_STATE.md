# Compact progress state

Updated: 2026-06-23

## Current batch

- Batch: B001
- Source items: NMI-001
- Status: done

## Completed

- T001: Added overdue task query.
- T002: Rendered overdue dashboard section and empty state.

## Next

- None for B001.
- Planned future work: B002 due-date reminder preferences.

## Validation evidence

- `npm test -- dashboard-task-query.test.ts` passed.
- `npm test -- dashboard-overdue-section.test.ts` passed.
- Manual smoke check confirmed overdue tasks appear above today's tasks.

## Open risks or blockers

- None.
