# Testing policy

## Goal

Test observable behavior through the repository's public seams. Tests should
document business rules and survive internal refactors. Follow established local
test style before introducing a new convention.

For behavior-changing work, select the relevant cases rather than adding them
mechanically:

1. success behavior;
2. validation, failure, or authorization behavior;
3. rollback or no-partial-write behavior for write paths;
4. a nearby branch that must remain unchanged;
5. side effects the implementation could accidentally introduce.

## Tracer-bullet loop

When practical, add or update one behavior-level test, confirm it fails for the
expected reason, implement the smallest passing change, and repeat. Do not write
all tests before all implementation. If the repository lacks a useful test seam,
record why and use the strongest available validation.

## Test quality

- Prefer clear Arrange, Act, Assert structure and business-behavior names.
- Assert explicit expected outputs through public interfaces.
- Include relevant included, excluded, and unchanged records for filtering or
  scoping behavior.
- Keep tests deterministic; freeze time or use fixed timestamps when needed.
- Mock external boundaries where appropriate, not internal domain behavior.
- For writes, assert the public result, persisted state, and relevant rollback or
  no-partial-write behavior.
- Do not leave new tests skipped, pending, or focused.

For every changed test, record the business rule it proves and the exact command
and result in `PROGRESS.md`.
