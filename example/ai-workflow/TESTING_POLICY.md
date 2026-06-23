# Testing policy

## 1. Scope and intent

Test behavior, not implementation details.

Tests should document business rules. Do not test private methods directly unless the repo already has that convention and there is no better public boundary.

## 2. Required coverage for behavior changes

For behavior-changing tasks, include relevant coverage for success paths, failure paths, rollback or no-partial-write behavior, nearby branches that must remain unchanged, and side effect risks.

## 3. Test structure

Prefer self-contained tests with clear Arrange, Act, Assert structure. Respect established local test style in the touched area.

## 4. Assertions

Prefer explicit expected outputs. Keep assertions minimal and strong.

## 5. Determinism

Use fixed timestamps or time-freezing helpers when time matters.

## 6. External boundaries

Mock or stub external boundaries when appropriate. Avoid stubbing internal domain logic under test.

## 7. Reporting

For each task that changes tests, record tests added or changed, the business rule each test proves, and the validation command/result.
