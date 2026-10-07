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
checkpoint. Keep unfinished work in draft; subsequent commits can trigger CI.
If publication is unavailable, record the limitation and continue independent
local work already authorized. Local progress is not a published checkpoint.

For resumed work, select the unfinished action from the batch and observed state.
Preserve existing approval, decisions and completed work. Reconcile a stale next
action instead of repeating a push or creating another PR. A ready result without
new work stays at human review; the entry contract governs closed or merged PRs.

## Implement and verify

Confirm the environment needed for the selected checks actually works. Implement
the smallest sufficient change in verifiable steps and run focused development
checks. Retain outputs needed by the verifier. Update the batch when a decision,
finding or next action changes, and commit/push useful checkpoints within scope.
Preserve unrelated changes; use a separate checkout when needed for a fixed,
reviewable snapshot. Avoid concurrent writes or tests on shared mutable resources.
Additional implementation delegation is optional.

Assign a separate non-implementing agent/session the [verification procedure](verify.md),
the original need, approved decisions, fixed code base/head, project rules, access
to the application and existing evidence. Supply known findings, but not an
expected verdict or the implementer's completion claim. Give the verifier only
the entry contract, its procedure and relevant task context. Confirm the actual
native assignment and retain its result; a name written in a report is not proof
that independent verification happened. If this capability is unavailable, keep
the limitation explicit rather than substituting self-review.

Required CI and configured remote review are part of delivery. Inspect results
on the PR's current head and use native bounded waits while work is pending.
They can run alongside independent verification when resources permit.

## Repair and handle feedback

Assess findings from verification, tests, CI and user feedback against the
approved outcome and actual code. Record each as confirmed, unresolved, duplicate
of a retained finding, or rejected with evidence. Before changing code, record
the intended correction and its regression check in the batch. Material behavior
or scope changes return to [preparation](prepare.md) under the entry contract;
ordinary technical repairs continue with existing authority.

Implement confirmed in-scope corrections, rerun affected checks and request
focused independent confirmation of the repaired paths and their consumers.
Retain unaffected proof according to the verification procedure. Continue until
the handoff conditions hold or a concrete decision/resource prevents progress.
A diagnostic report or commit is an intermediate result. If attempts stop making
progress, name the missing fact or resource and next investigation; do not repeat
the same review or command indefinitely. Unrelated fixes need their own scope.

## Hand off or leave a recoverable interruption

Before handoff apply the [readiness conditions](verify.md#result-and-evidence)
to the final change, inspect any changes since the verified snapshot and fetch
current required GitHub results. Resolve missing proof through the same repair
loop. Mark the PR ready only after those conditions hold. Present the delivered
behavior, material interface changes, PR, demonstration/evidence, tested revisions
and any departures from the proposal. Human review follows.

When interrupted, save the next action, outstanding findings and evidence links
in the batch and publish the checkpoint when permitted and possible. Another
session must be able to start from the batch and GitHub without the original chat.
Report pending work as pending. Claim continued monitoring only after a native
mechanism has confirmed it will continue after the turn; retain its reference and
expiry when provided. Otherwise state that execution is interrupted and how to
resume. A saved checkpoint does not itself restart an agent.
