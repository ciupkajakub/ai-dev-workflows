# Independently verify the implementation

Review the supplied fixed base/head or retained diff against the original request,
approved behavior, project rules and actual test evidence. This review inspects
implemented code and required behavioral scenarios. Derive scenarios from the
request and approved decisions, then reconcile them with the plan's check IDs.
Do this before reading the author's verdict. Give each independently observable
requirement clause a stable obligation reference in the review, even if the plan
omits it. The receipt must account for that list separately from executed checks.
Proposal readiness and recorded task completion are claims to
check, not evidence that the code works. Stay within the change's scope.

Trace affected actions through their real wiring, request construction, validator,
response and consumer state. Compare replaced paths with the base implementation
for safeguards that must survive. Inspect materially different implementations
separately rather than treating one example as proof of all of them.

For asynchronous state and partial recovery, inspect request/input identity,
omitted versus explicitly cleared fields, replacement data required by the next
action, and error-to-success transitions. Follow the replacement through rendering
and the next validation. Use the actual producer and consumer, not an invented
payload that assumes missing data or wiring exists.

Inspect what the tests execute and assert. Compare that with each task's promised
proof, including affected existing tests and known regressions when supplied.
A passing command does not close scenarios that its examples never exercise.
In this review note, list every behavior promised under each required check and
map it to the actual executed trigger, assertion/observation and retained evidence
at the tested revision. Mark each demonstrated, missing or contradicted. Include
requirements omitted from the planned checks as missing proof. Only a check with
all required behaviors demonstrated may pass. Do not substitute a helper call for
a required UI/timer trigger, or a replacement scenario for a no-replacement case.
Name missing proof without claiming an unrun test has passed or failed.
Missing proof makes the overall review non-passing, even if every planned check
passes. Never put an uncovered requirement in an "outside this gate" footnote.

Inventory known failures, including those in excluded test lanes, and retain them
as findings until resolved or rejected through a scope comparison. Trace the
changed path and use a focused base/head reproduction when needed. A release tag
or unchanged file does not prove a failure unrelated. Record comparison evidence
for rejection, or keep the finding open when the relation is unresolved.

For checks scoped to changed files, compare the approved base with the final head,
including all repairs. List applicable files and map each to actual command
coverage or confirmed reusable evidence. Record deletions, renames and configured
exclusions. A clean result on a repair subset does not cover the full change.

Return compact findings with locations, concrete triggers, consequences and the
check that would demonstrate each repair. Separate confirmed defects, missing
proof and hypotheses. Report the inspected snapshot and any access limits.
Do not supply an expected pass, unrelated redesign, or another full plan review.
Run focused tests or browser checks within the authorized delivery scope and
isolated resources. Inspect reused logs and actual assertions before accepting them.
Do not change application code; return defects and missing proof to the implementer.
Record the inspected commit, observations and dispositions in the
[verification receipt](publication-gate.md). Keep failures open and preserve their
repair checks. The coordinator owns repairs and publication. After a repair, verify
its regression check and affected consumers without repeating unchanged scenarios.
Do not claim a pass when required access or execution was unavailable.
