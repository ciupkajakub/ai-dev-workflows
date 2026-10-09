# Execute an approved plan

Use the [entry contract](SKILL.md), selected requirements, BATCH and IMPLEMENTATION.
Recover exact approval and distinguish interrupted execution from completed PR
handoff. Remote feedback alone does not reopen execution.

## Establish the execution environment

Reconcile actual checkout, branch/base, local changes and any existing PR. Preserve
unrelated work and inspect active workers before taking ownership. Avoid concurrent
writes or tests against shared mutable resources. Use a suitable isolated checkout
and isolated mutable test resources
for the approved scope. Sandbox means the agreed execution environment; this package
does not provision Kubernetes, containers or remote workers. Confirm the necessary
tools, dependencies and checks work there.

Retain the approved snapshot before revising the plan. Local commits may preserve
progress within authority. Do not push a planning checkpoint or open a draft PR
before implementation by default. Publication happens at handoff.

## Implement and check the plan

Select a pending task whose dependencies have demonstrated results. Start with the
planned check of the most uncertain mechanism. Confirm it exercised that mechanism
before dependent work; success in a simpler scenario is insufficient. Record task
progress/evidence in IMPLEMENTATION and the next action in BATCH.

Implement the selected scope and run planned task checks. Repair implementation
errors within approved decisions and rerun affected checks. Ordinary local repairs
need no new approval; record the correction and regression check. Run shared batch
checks at integration points instead of repeating the full suite per task. Reuse
unaffected evidence with its original revision.

If execution disproves a design assumption or needs material behavior/scope changes,
save the observation and return to preparation. Do not rewrite approved requirements
to fit code. An adjacent defect remains outside this execution.

Apply [verify.md](verify.md) to the integrated candidate. The coordinator can verify
directly; use an independent reviewer only when the approved plan or project requires
one. Planning consultations are not evidence that the resulting code works.

Stop with a recoverable checkpoint for a missing resource/decision, an agreed budget
limit, or repeated attempts without new evidence. Record attempts and the next
investigation. Do not loop indefinitely or claim enforcement of unobservable usage.

## Publish once and stop

After required pre-publication behavior/checks are demonstrated, inspect the full
candidate diff and final working changes. Preserve the tested revision or exact diff
and explain reused evidence. Known local failures and missing required local proof
block successful handoff unless an explicit applicable exception exists. Never label
exceptions as passed tests.

Commit and push approved work. Open the PR to the approved target or update the
authorized existing PR. Recheck state before mutation; do not reopen a closed PR
or restore a deleted branch under ordinary update authority. If publication fails,
retain the unpublished checkpoint and report interruption. On resume inspect remote
state before retrying to avoid duplicate PRs or pushes.

In the PR and handoff identify the approved snapshot and continuation, delivered
behavior, scope, verification evidence and revision, limitations and external checks
not yet observed. Use a draft when project
policy or outstanding evidence requires it. Local success does not establish merge
readiness; required CI/review can run after publication.

Record the PR link and completed execution handoff in BATCH without mirroring live
CI status. Identify any final local-only record. The published diff and absence of
remaining approved execution tasks also establish the boundary if another clone
lacks that local record. Resolve uncertain publication outcomes through read-only
inspection before deciding whether execution remains.

End the run. Do not poll/wait for CI or remote review, schedule monitoring, repair
new PR findings, trigger another review round, or start the next mapped batch.
If remote results are already available, report their observed state without
starting repairs. Later requested feedback returns to [prepare.md](prepare.md).
A status-only request remains read-only.

## Resume interrupted execution

Compare the checkpoint with actual code, evidence and remote state. Continue only
unfinished work covered by approval. Preserve results whose inputs/scope still apply
and rerun affected checks. Do not restart discovery or reapprove unchanged work.

A pending remote check after successful PR publication is not interrupted execution.
A saved checkpoint does not schedule another run. Save the next action and missing
decision/resource so another session can resume without the original chat.
