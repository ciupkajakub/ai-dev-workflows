# Verify the planned behavior

Use the [entry contract](SKILL.md), selected requirements and IMPLEMENTATION.
The coordinator verifies locally unless the approved plan or project requires an
independent reviewer. An assigned independent reviewer returns findings/evidence
without implementing or publishing changes. Do not start agents or model comparisons
merely to satisfy a fixed review count.

## Start with the required outcome

Derive observable obligations from requirements and approved decisions before reading
completion claims. Reconcile planned checks with them; an omitted requirement still
needs proof. Inspect known findings and failures, including those outside selected suites.

Review code against approved behavior and project rules. Trace changed state, data
meaning or timing through affected readers, writers and side effects. Follow the
real caller to the consumer's result and compare preserved behavior with the base.
Exercise materially different affected paths.

## Obtain evidence proportional to the claim

For each obligation identify the executed trigger, assertion or observation, evidence
location and tested revision/environment. Inspect what commands select and tests
assert. Add focused checks for coverage gaps within approved scope.

Isolated tests with constructed inputs do not prove the caller-to-consumer path.
Use the running interface for a claimed user interaction and focused checks for
isolated contracts. A plan, source inspection, test count or reviewer agreement
cannot replace execution when the claim requires it.

Select affected checks from the full base-to-candidate diff, including repairs.
Reuse evidence only when its inputs and scope remain valid. Investigate known failures
against the changed path; a filename or CI label does not prove they are unrelated.
Keep evidence supporting that disposition.

Return defects/missing proof with requirement references, triggers, consequences and
the check confirming a repair. Distinguish observed failures from hypotheses. Confirm
repaired paths and consumers without repeating unaffected reviews or suites unless
new evidence justifies it.

## Result and publication boundary

In IMPLEMENTATION mark required pre-publication behavior demonstrated, missing or
contradicted, with evidence links. Findings remain open until repaired and confirmed,
rejected with evidence or explicitly waived by the authorized user. Pre-existing
failures of required local checks still need a visible disposition.

The local candidate is verified when required pre-publication behavior/checks have
adequate evidence and any planned independent review is complete. Missing proof or
confirmed unresolved local failures prevent successful handoff unless an explicit
applicable exception exists. Unavailable required checks are not passed checks.

PR publication completes default execution. CI/remote review may be pending and must
not be described as passed or merge-ready. Later findings return to planning on user
request; they do not keep execution running. Honor stricter project publication
requirements settled in the approved plan.

Record commands/procedures, environment, observations and the code actually tested.
Inspect working changes rather than assuming HEAD identifies everything. After a
change explain which results still apply and rerun affected checks. Report-only
commits do not require rerunning unchanged application tests. Never relabel older
results as current-revision execution. Retain evidence under the entry contract;
no separate receipt or duplicate status file is needed.
