# Testing policy

## 1. Scope and intent

Test behavior, not implementation details.

Tests should document business rules.
Do not test private methods directly unless the repo already has a clear convention and there is no better public boundary.

## 2. Required coverage for behavior changes

For every behavior-changing task, include relevant coverage for:

1. success path
2. failure, validation, or authorization path
3. rollback or no-partial-write behavior for write paths
4. nearby branch that must remain unchanged
5. side effect risk introduced by the implementation

Do not add every category mechanically. Add the cases that match the touched behavior.

## 3. Test structure

Prefer self-contained tests with clear Arrange, Act, Assert structure.
Respect established local test style in the touched file or directory.
Do not rewrite existing test structure solely to satisfy this policy.
When deviating from this policy because of local conventions, record the reason in `PROGRESS.md`.

## 4. Tracer-bullet TDD loop

For behavior-changing tasks, prefer a tracer-bullet TDD loop:

1. add or update one behavior-level test through the public interface
2. run it and confirm it fails for the expected reason when practical
3. implement the smallest change that makes it pass
4. repeat for the next behavior

If test-first is impractical because the repo lacks a useful seam, record the reason in `PROGRESS.md` and use the strongest available validation signal.

Do not write all tests first and then all implementation. Keep tests and implementation moving one behavior at a time.

## 5. Naming

Test names should describe business behavior.
Avoid generic names unless the full name still explains the rule.

## 6. Assertions

Prefer explicit expected outputs. Keep assertions minimal and strong.
Keep assertion order stable.
If code filters, scopes, or selects records, tests should include included records, excluded records, and proof that excluded records remain unchanged when relevant.

## 7. Determinism

Tests must be deterministic.
Use fixed timestamps or time-freezing helpers when time matters.

## 8. External boundaries

Mock or stub external boundaries when appropriate:

1. HTTP
2. queues
3. external services
4. clock
5. file system boundaries
6. third-party APIs

Avoid stubbing internal domain logic under test.

## 9. Persistence and side effects

For write paths, assert public contract, persisted state, and rollback/no-partial-write behavior when relevant.
Before finishing a task, ask what the implementation could accidentally update, select, send, expose, enqueue, cache, or delete.

## 10. Reporting

For each task that changes tests, record tests added or changed, the business rule each test proves, and the validation command/result.

## 11. Forbidden final state

Do not leave new tests skipped, pending, or focused.
