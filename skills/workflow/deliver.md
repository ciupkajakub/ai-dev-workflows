# Deliver or resume a batch

The coordinator owns continuation, implementation, repair and PR handoff. Read
the [entry contract](SKILL.md) and selected batch, then reconcile the checkout
with the actual branch, PR, checks and review on GitHub. Inspect unpublished
changes and any native workers before taking over; one coordinator owns the work.
Use existing results where valid instead of restarting preparation.

## Establish the shared checkpoint

For newly approved work, record its exact approval and commit the batch before
changing the proposal. Push the checkpoint to the authorized branch and open a
draft PR, or reuse the authorized open PR. Link it from the batch at the next
checkpoint. Keep unfinished work in draft except when readiness is the configured
review trigger described below; subsequent commits can trigger CI.
If publication is unavailable, record the limitation and continue independent
local work already authorized. Local progress is not a published checkpoint.

For resumed work, select the unfinished action from the batch and observed state.
Preserve existing approval, decisions and completed work. Reconcile a stale next
action instead of repeating a push or creating another PR. A ready result with
completed required checks and configured reviews and no new work stays at human
review; the entry contract governs closed or merged PRs.

## Implement and verify

Confirm the environment needed for the selected checks actually works. Implement
the smallest sufficient change in verifiable steps and run focused development
checks. Retain outputs needed by the verifier. Update the batch when a decision,
finding or next action changes, and commit/push useful checkpoints within scope.
Preserve unrelated changes; use a separate checkout when needed for a fixed,
reviewable snapshot. Avoid concurrent writes or tests on shared mutable resources.
Additional implementation delegation is optional.

Assign final verification of a stable candidate to a separate non-implementing
agent/session using [verify.md](verify.md). Supply the original need, approved
decisions, fixed base/head or exact diff, project rules, application access and
existing evidence. Include known findings, not an expected verdict or completion
claim. Earlier consultations during implementation do not replace this assessment.
Give the verifier only the entry contract, its procedure and relevant task context.
Retain the native assignment and result. If independent verification is unavailable,
report the limitation rather than substituting self-review.

Required CI and configured remote review are part of delivery. Determine the
review trigger and completion signal; an empty review list is not proof of a
completed review. If marking ready starts the review, first confirm required
behavior, independent verification and checks available in draft, then mark ready
to trigger it. This state is provisional: wait for the result and handle findings
through the repair loop before handoff. After repairs, apply the scoped confirmation
below, respecting configured review requirements. Use native bounded waits; if
continuation is unavailable, leave an interrupted checkpoint. Checks and review
may run alongside independent verification when their triggers and resources permit.

## Repair and handle feedback

Assess findings from verification, tests, CI and user feedback against the
approved outcome and actual code. Record each as confirmed, unresolved, duplicate
of a retained finding, or rejected with evidence. Before changing code, record
the intended correction and its regression check in the batch. Material behavior
or scope changes return to [preparation](prepare.md) under the entry contract;
ordinary technical repairs continue with existing authority.

Implement confirmed in-scope corrections, rerun affected checks and request
focused independent confirmation of repaired paths and their consumers. Retain
unaffected proof. A new commit alone does not justify another full review; record
the reason for one, such as a redesign invalidating prior coverage or a project
requirement. When later reviews uncover independent defects already present in the
reviewed candidate, diagnose the coverage gap and choose checks for the missed
dependencies before requesting another full review. Unrelated fixes need their
own scope.

Continue until handoff conditions hold, an agreed execution budget is reached or
a concrete decision/resource blocks progress. If budget usage cannot be observed,
disclose that limitation; do not claim to enforce it. On exhaustion or stalled
attempts, leave an interrupted checkpoint with unresolved work and the next
investigation, not a completed delivery or another automatic review round.

## Hand off or leave a recoverable interruption

Before handoff apply the [readiness conditions](verify.md#result-and-evidence)
to the final change, inspect any changes since the verified snapshot and fetch
current required GitHub results. Resolve missing proof through the same repair
loop. Mark the PR ready if it was not already needed to trigger review; ready
state alone does not establish completion. Present the delivered behavior,
material interface changes, PR, demonstration/evidence, tested revisions and any
departures from the proposal. Human review follows.

When interrupted, save the next action, outstanding findings and evidence links
in the batch and publish the checkpoint when permitted and possible. Another
session must be able to start from the batch and GitHub without the original chat.
Report pending work as pending. Claim continued monitoring only after a native
mechanism has confirmed it will continue after the turn; retain its reference and
expiry when provided. Otherwise state that execution is interrupted and how to
resume. A saved checkpoint does not itself restart an agent.
