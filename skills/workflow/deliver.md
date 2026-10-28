# Execute an approved plan

Use the [entry contract](SKILL.md), selected requirements, BATCH and IMPLEMENTATION.
Recover the exact approval and compare it with the checkout and actual PR state.
Continue only unfinished authorized work. An already published candidate with no
remaining approved work establishes handoff even if a local record is missing;
resolve uncertain publication state before retrying.

## Establish the environment

Preserve unrelated changes and inspect active workers. Use a suitable isolated
checkout and isolated mutable test resources; avoid concurrent writes or tests
against shared state. Confirm necessary tools, dependencies and checks work there.
This package does not provision the environment.

Retain the approved snapshot before changing records. Local commits may preserve
progress within authority; do not publish a planning checkpoint by default.

## Implement and verify

Start with the planned check of the most uncertain mechanism. Proceed to dependent
tasks only when their prerequisite conditions are demonstrated; do not wait for a
final integration check that requires those tasks. Record task results in IMPLEMENTATION
and the checkpoint/next action in BATCH.

Implement the selected scope and apply the [evidence standard](verify.md#evidence-standard).
Repair implementation defects within approved decisions without requesting approval
again. Update the flow/contracts and coverage when new affected consumers are found.
Run shared batch checks at integration points rather than repeating them per task.

If evidence disproves a design assumption or requires material scope/behavior changes,
preserve the observation and return to [preparation](prepare.md). Do not change
requirements to fit the code. Stop with attempts and a recoverable next action when
a resource/decision is missing, an agreed budget is reached, or attempts repeat
without new evidence.

Apply [findings and completion](verify.md#findings-and-completion) to the integrated
candidate, including required independent review. On resume, reuse valid results
and continue unfinished work without restarting discovery or reapproving unchanged scope.

## Publish once and stop

When the candidate meets the agreed publication conditions, reconcile the records
and report with the full final diff, actual results and exceptions. Follow the
project's PR template and publication rules; never invent missing metadata.

Recheck the destination under the entry contract, commit/push approved work and
open or update the PR. Use a draft when policy or disclosed outstanding evidence
requires it; draft status does not waive missing required checks. If publication
fails, save the actual checkpoint and reconcile remote state before retrying.

In the PR/handoff identify the approved snapshot or continuation, delivered behavior,
verification evidence and tested revision, limitations and unobserved remote checks.
Record the PR link and completed handoff in BATCH; identify local-only records.
Stop at the entry contract's boundary. Further requested feedback returns to preparation.
