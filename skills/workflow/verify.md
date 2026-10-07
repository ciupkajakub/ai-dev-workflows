# Independently verify the change

Use the shared [entry contract](SKILL.md). The verifier did not implement this
change and does not repair application code or publish the PR. It may run the
authorized checks using isolated resources and returns evidence to the coordinator.

## Start with the required outcome

Read the original need and approved decisions before assessing the author's
approach or results. Derive the observable obligations from those requirements,
using their batch references. Reconcile the plan's checks against that list;
a requirement missing from the plan still needs proof. Inspect known findings
and failed results from the run, including failures outside the selected suites.

Review actual code against the approved behavior and project standards. When a
state, data meaning or operation timing changes, trace its affected readers,
writers and side effects for assumptions that no longer hold. Follow the real
caller through subsequent consumer behavior, comparing with the base for behavior
that must survive. Exercise materially different affected implementations.

## Inspect and obtain evidence

For every obligation identify the executed trigger, actual assertion or observed
result, evidence location and tested revision/environment. Inspect what the tests
select, execute and assert, and independently choose checks for obligations they
leave uncovered. Passing isolated checks with constructed inputs do not prove
the actual caller-to-consumer path. Use the running interface for a
claimed user interaction; choose focused checks for isolated contracts. A plan,
test count, source inspection or reviewer agreement cannot stand in for execution
when the claim needs it.

For checks scoped to changed files, use the full base-to-head change, including
repairs, and compare applicable files with actual command coverage. Reuse prior
results only when their scope and inputs still apply. Investigate known failures
against the changed path; a file location or CI label does not establish that a
failure is unrelated. An out-of-scope rejection needs supporting comparison.
A pre-existing failure of a required check still needs resolution or an explicit
applicable user decision, not a silent waiver.

Return concrete defects and missing proof with requirement references, triggers,
consequences, locations and the check that can confirm a repair. Distinguish a
reproduced failure from an untested hypothesis. Focus confirmation after repairs
on affected behavior and consumers rather than repeating unchanged full reviews.

## Result and evidence

Keep one concise review with each required behavior marked demonstrated, missing
or contradicted and linked to its evidence. Findings stay open until repaired
with confirmation, rejected with evidence or explicitly waived by the authorized
user. Preserve those dispositions rather than dropping earlier failures. Report
which required CI/review results remain pending or inaccessible.

Delivery is complete only when required behavior has adequate proof, independent
verification is complete, known findings are resolved and required project checks
and configured reviews are complete for the applicable final revision. Missing
proof, unresolved findings and unavailable required checks prevent handoff.
An authorized exception must remain visible as an exception, never a passed test.
The coordinator applies these conditions to current GitHub state at handoff.

Record the code revision actually tested, commands/procedures, environment and
observations. Commit relevant code before final verification or retain an exact
diff for work that cannot yet be committed. Inspect working changes rather than
assuming HEAD identifies everything tested. Evidence keeps its original revision.
After another commit, inspect the difference and explain which results still
apply; rerun affected checks. A commit storing only the report does not require
rerunning unchanged application tests. Never relabel earlier CI as current-head
CI. Use durable links or retained outputs under the batch as defined by the entry
contract; there is no receipt JSON or publication checker.
