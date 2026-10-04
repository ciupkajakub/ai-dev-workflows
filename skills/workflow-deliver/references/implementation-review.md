# Review the implementation

Review the supplied fixed base/head or retained diff against the original request,
approved behavior, project rules and actual test evidence. This review inspects
implemented code. Proposal readiness and recorded task completion are claims to
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
Name missing proof without claiming an unrun test has passed or failed.

Return compact findings with locations, concrete triggers, consequences and the
check that would demonstrate each repair. Separate confirmed defects, missing
proof and hypotheses. Report the inspected snapshot and any access limits.
Do not supply an expected pass, unrelated redesign, or another full plan review.
Keep the requested review read-only unless reproductions are explicitly authorized.
The coordinator owns task/evidence updates and repairs. A focused confirmation
checks material repairs and their affected consumers without restarting the review.
