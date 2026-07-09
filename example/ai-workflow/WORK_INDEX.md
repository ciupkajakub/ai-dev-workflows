# Work index

## Batch queue

| Batch | Status | Source items | Folder | Purpose | Updated |
| --- | --- | --- | --- | --- | --- |
| B001 | done | NMI-001 | `ai-workflow/work/B001-example-feature/` | Show overdue tasks on the dashboard. | 2026-06-23 |
| B002 | planned | NMI-002 | `ai-workflow/work/B002-reminder-preferences/` | Add account-level due-date reminder preferences. | 2026-06-23 |

## Dependency and history notes

- B001 can ship independently because it only changes dashboard visibility.
- B002 follows the reminder preference decision captured in NMI-002.
- NMI-003 is historical and superseded by NMI-002.

## Batch history

| Date | Change |
| --- | --- |
| 2026-06-20 | Created B001 from NMI-001. |
| 2026-06-22 | Moved B001 from spec to ready after planning files were created. |
| 2026-06-23 | Moved B001 from active to failed_validation after T001 query validation exposed missing due-date sorting. |
| 2026-06-23 | Returned B001 to active after the T001 validation fix started. |
| 2026-06-23 | Moved B001 from active to blocked while authenticated browser smoke validation required explicit approval. |
| 2026-06-23 | Returned B001 to active after the user approved a synthetic local fixture smoke check. |
| 2026-06-23 | Moved B001 from active to validated after all task validation and traceability rows were closed. |
| 2026-06-23 | Marked B001 done after verification, traceability closure, and final audit. |
| 2026-06-23 | Created B002 from NMI-002. |
