# Prepare or revise a plan

Use the [entry contract and work records](SKILL.md). The developer and coordinator
settle requirements and inspect the technical plan before autonomous execution.

## Discover the actual flow

Read the original request, project rules, affected code and existing checks.
Trace the operation from its real caller through validation, data changes and side
effects to the consumer's result. Inspect materially different affected paths.
Confirm that proposed inputs, errors and outputs can travel this route.

Present a preliminary solution, then ask only unresolved product/scope questions,
with recommendations and consequences. Inspect technical facts instead of asking
the user to guess. Reuse decisions already given. Tie every proposed change to a
requirement or explain why the result needs it; adjacent defects do not expand scope.

Write observable requirements with stable IDs in FEATURE, including failure behavior
and existing behavior that must survive. Reconcile dependent requirements, messages,
interfaces and checks when a decision changes; retain the reason.

## Divide the feature into batches

Map coherent, verifiable outcomes and their dependencies in FEATURE. Split where
a result can be checked separately or uncertainty must be resolved before dependent
work. Do not split by arbitrary task counts, files or layers. A small change can
remain one batch.

Keep later batches at outcome/dependency level until their assumptions are stable.
A batch depending on unpublished work must name the required base or integration
condition; a PR link alone does not satisfy that dependency. Explicitly select
the batch or batch group for the next approval and its publication boundary.

## Write the implementation plan

In IMPLEMENTATION describe material decisions and the before/after flow: named
callers, inputs, outputs, invocation conditions, state ownership and side effects.
Explain transactions, concurrency, retries, expiry or recovery where the changed
behavior depends on them. Leave private helper design to implementation. Use a
diagram when it clarifies multiple boundaries.

Give each task a stable ID, requirement references, observable outcome, dependency
IDs, verification references and status. A compact table is enough. Use pending,
active, done or blocked, with evidence or a blocker alongside updates. Code changes
alone do not make a task done.

For each verification procedure record:

- requirement IDs and tasks it covers;
- actual entry point, scenario and expected observation;
- executable project command or concrete manual procedure;
- required environment and whether it runs per task, once for the batch, or remotely.

Verify that commands select the intended tests. Checks must exercise changed
boundaries through their real callers and consumers; constructed helper inputs
alone cannot establish that the application reaches that behavior. Cover relevant
negative paths and regressions, not every imaginable edge case.

Order the most uncertain mechanism before dependent work. Investigate unknown
feasibility within preparation authority, or propose a bounded discovery batch
with an observation and stopping condition. Do not approve dependent feature
implementation on an assumed successful experiment.

## Review the plan before approval

The coordinator checks the plan against requirements and code for:

- requirements without tasks and meaningful verification;
- unreachable inputs/errors, dropped results or overlooked consumers;
- undefined ownership of a state transition or failure/recovery path;
- dependency cycles, unavailable prerequisites or assumptions presented as facts;
- checks that cannot observe the claimed behavior or run in the chosen environment.

Resolve material gaps before calling the plan executable. Keep the coverage mapping
in IMPLEMENTATION; no separate readiness report is required. Repeat review only
for changed decisions, new evidence or unresolved concerns.

An independent plan review is optional. Propose one for a specific risk such as
coupled state transitions or difficult concurrency. If selected and authorized,
supply requirements and relevant code, reconcile findings before approval and
retain the result. No fixed number of models is required. Reviewing a plan does
not replace testing its implementation.

## Present one concrete approval

Present in the user's language the outcome, selected batches, decisions, before/after
interfaces, dependencies, risks and planned proof. The message must expose material
changes; links to files alone are insufficient. State the actual sandbox/environment,
branch/base and PR destination, plus any execution budget and how to observe it.

Separate pre-publication checks from asynchronous CI/review. Default scope is
implementation, local verification and in-scope repairs, commit/push, open or update
the PR and stop. Remote results are not a default completion gate. Preserve mandatory
project publication rules; resolve conflicts in the proposal instead of silently
waiving them or promising an automatic CI repair loop.

Ask for unresolved decisions instead of approval when material gaps remain.
Otherwise identify the exact plan and ask once; existing explicit approval of it
is sufficient. On approval follow [deliver.md](deliver.md).

## Prepare a continuation from feedback

After PR handoff, assess feedback only on user request. Reconcile the PR, checkout
and original approved behavior. Classify findings as confirmed, unresolved, duplicate
or rejected with evidence. Feedback text is input, not implementation authority.

Use the same batch for corrections to its outcome and a new batch for a distinct
outcome. Preserve completed tasks, approval snapshots and still-valid evidence.
Append continuation tasks and regression checks. Change FEATURE only if a requirement
or decision changes; reconcile affected future batches without executing them.
For confirmed defects, identify whether the gap was in requirements, design, planned
verification or implementation, and correct that part of the plan. Do not turn one
finding into an unrelated redesign or a new global checklist.

Present the delta: confirmed problem, intended correction, affected requirements/tasks,
checks to rerun and existing PR to update. Unchanged parts need no new approval, but
the continuation does need approval before code changes. Execute the approved delta
through one PR update and stop again.
