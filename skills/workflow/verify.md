# Verify the planned behavior

Use the [entry contract](SKILL.md), selected requirements and IMPLEMENTATION.
The coordinator owns local verification. When independent implementation review is
selected under [prepare.md](prepare.md#review-the-plan-before-approval), assign a
reviewer who did not author the implementation. Supply approved requirements and
decisions, base and candidate revisions, relevant code and verification evidence.
The reviewer applies the procedure below to the full change and returns findings
and evidence without implementing or publishing changes. Keep the reviewed revision
and findings in the existing batch evidence. Do not start model comparisons merely
to satisfy a fixed review count.

## Start with the required outcome

Derive observable obligations from requirements and approved decisions before reading
completion claims. Reconcile planned checks with them; an omitted requirement still
needs proof. Inspect known findings and failures, including those outside selected suites.

Review code against approved behavior and project rules. Trace changed state, data
meaning or timing through affected readers, writers and side effects. Follow the
real caller to the consumer's result and compare preserved behavior with the base.
Exercise materially different affected paths.

## Obtain evidence proportional to the claim

For each required scenario variant in IMPLEMENTATION, record demonstrated, missing
or contradicted alongside the expected and observed result, evidence location and
tested revision/environment. Inspect the executed trigger, selected tests and actual
assertions; a test name or green suite total does not establish scenario coverage.
Add focused checks for coverage gaps within approved scope.

Reconcile the before/after graphs and services/contracts table with the final diff.
Include consumers discovered during implementation and attach checks for their
changed or preserved behavior. Confirm primary and fallback/legacy paths separately,
including competing candidates and selection conditions where applicable.

For each planned check, record the planned command/procedure, the actual execution
and its result or missing evidence in IMPLEMENTATION. Expand project scripts when
comparing substitutions. A substitute needs evidence that it performs all required
steps, produces the required outputs and checks the same properties and scenarios.
Omitted steps remain unverified. Reused evidence retains its original command,
revision and environment.

For stateful behavior, continue through the planned recovery and next user action.
Confirm client permissions and persisted state/resources agree after each outcome;
a successful backend transition alone does not prove the consumer can continue.
Timing and concurrency evidence must cross the relevant execution boundary through
the actual timing or ordering mechanism and observe conditions at their point of use.
Constructed values or simpler paths that bypass this mechanism cannot establish
the behavior of the delayed or competing operation.

Before recommending a procedure, verify that the user can perform it from the
affected state with their permissions and trace its effect through the result they
need. Distinguish source-inspected procedures from executed ones; label unverified
steps. This applies to handoff advice as well as planned changes. A recommendation
does not authorize execution.

Isolated tests with constructed inputs do not prove the caller-to-consumer path.
Use the running interface for a claimed user interaction and focused checks for
isolated contracts. A plan, source inspection, test count or reviewer agreement
cannot replace execution when the claim requires it.

Select affected checks from the full base-to-candidate diff, including repairs.
Reuse evidence only when its inputs and scope remain valid. Investigate known failures
against the changed path; a filename or CI label does not prove they are unrelated.
Keep evidence supporting that disposition.

Return findings with requirement references, triggers, consequences and supporting
evidence. Distinguish confirmed defects, missing required proof, hypotheses and
optional improvements. The coordinator repairs defects within approved scope under
[deliver.md](deliver.md); changes to approved behavior return to preparation.
Optional improvements do not expand scope. Confirm repairs and affected consumers;
when independent review is required, the reviewer rechecks the affected behavior
and evidence. Retain valid findings and checks without repeating unaffected reviews
or suites.

## Result and publication boundary

Reconcile the scenario mapping with requirements and the final candidate before
marking a task done, a finding resolved or the batch verified. Every required variant
for that claim needs matching evidence. Missing or contradicted variants keep the
claim incomplete, even when all executed tests pass. A prerequisite check can still
unblock dependent work; shared integration scenarios keep the batch unverified,
not an otherwise completed prerequisite task. Explicitly authorized exceptions stay
labelled as exceptions, never demonstrated behavior. Confirm the separate explicit
exception decision under the entry contract; general plan approval is insufficient.

Findings remain open until repaired and confirmed,
rejected with evidence or explicitly waived by the authorized user. Pre-existing
failures of required local checks still need a visible disposition.

The local candidate is verified when required pre-publication behavior/checks have
adequate evidence and required independent review covers the final candidate.
Reconcile changes after review with its findings and recheck affected behavior.
Missing required proof, unavailable required review or confirmed unresolved local
failures prevent successful handoff unless an explicit applicable exception exists.
Unavailable required checks are not passed checks.

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
