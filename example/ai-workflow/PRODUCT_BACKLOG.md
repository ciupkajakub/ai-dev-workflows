# Product backlog

## Backlog index

| ID | Status | Priority | Title | Related | Batch | Updated |
| --- | --- | --- | --- | --- | --- | --- |
| NMI-001 | done | high | Show overdue tasks on the dashboard | - | B001 | 2026-06-23 |
| NMI-002 | planned | medium | Add due-date reminder preferences | - | B002 | 2026-06-23 |
| NMI-003 | superseded | medium | Add a single daily reminder toggle | Superseded by NMI-002 | - | 2026-06-23 |

## Item details

### NMI-001: Show overdue tasks on the dashboard

Status: done
Priority: high
Related: -
Batch: B001
Created: 2026-06-20
Updated: 2026-06-23

#### Feedback / source

Users miss overdue tasks because the dashboard only shows tasks due today.

#### Problem

The task list does not make overdue work visible enough during daily planning.

#### Requested outcome

Display overdue tasks in a dedicated dashboard section.

#### Notes / assumptions

Overdue means incomplete tasks with a due date before the user's current local date.

#### Acceptance hints

- Overdue tasks appear before today's tasks.
- Completed tasks do not appear in the overdue section.
- Empty state appears when no tasks are overdue.
- Multiple overdue tasks sort by due date ascending.
- Dashboard rendering should not introduce an N+1 query path.

### NMI-002: Add due-date reminder preferences

Status: planned
Priority: medium
Related: NMI-003
Batch: B002
Created: 2026-06-23
Updated: 2026-06-23

#### Feedback / source

Users want control over when reminders are sent for tasks with due dates.

#### Problem

A single reminder setting is too broad for users who plan at different times of day.

#### Requested outcome

Allow users to choose reminder timing for due-date notifications.

#### Notes / assumptions

The first version should support simple account-level preferences, not per-project rules.

#### Acceptance hints

- Users can choose a reminder timing preference.
- Existing users keep the default behavior.
- Disabled reminders do not schedule due-date notifications.

### NMI-003: Add a single daily reminder toggle

Status: superseded
Priority: medium
Related: Superseded by NMI-002
Batch: -
Created: 2026-06-21
Updated: 2026-06-23

#### Feedback / source

Original request asked for one daily reminder switch.

#### Problem

The request did not capture the need for reminder timing.

#### Requested outcome

Superseded by the broader reminder preference item.

#### Notes / assumptions

Keep this item for history.

#### Acceptance hints

- Do not implement this as a separate batch.

## Backlog history

| Date | Change |
| --- | --- |
| 2026-06-20 | Added NMI-001 for overdue dashboard visibility. |
| 2026-06-21 | Added NMI-003 for a simple reminder toggle. |
| 2026-06-23 | Added NMI-002 and marked NMI-003 superseded because reminder timing is required. |
| 2026-06-23 | Marked NMI-001 done after B001 verification. |
