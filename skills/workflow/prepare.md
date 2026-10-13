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
behavior depends on them. Leave private helper design to implementation.

Include compact before and after flow graphs, using Mermaid or an equivalent
diagram. Name real entry points, services/functions, persisted data and consumers
from the code; mark proposed additions. Show the changed path and affected readers,
writers and side effects, including dependencies through shared response schemas
or generated contracts. A small change needs only small graphs.

Include a services/contracts table with these columns:

| Service/function or contract | Caller and trigger | Inputs/outputs and behavior before → after | Affected consumers/state/side effects | Requirement and verification references |
| --- | --- | --- | --- | --- |

Use actual code names and describe each changed element or affected contract
consumer. Group identical impacts where useful; a file inventory is insufficient.
Every materially affected consumer needs a check of its changed or preserved
behavior. The graphs and table expose dependencies; they are not execution evidence.

For a changed stateful operation, map its applicable outcomes in IMPLEMENTATION
before approval: success, rejection, cancellation, expiry, compensation and unknown
result. For each, name persisted/server and client state, retained or released
resources, and the next action the user can or cannot perform. Follow the operation
through recovery and the next attempt, not just its first successful response.
Include reload, interrupted clients, conflicting old/new operation state and late
responses where those mechanisms exist. State what resolves an unknown result;
do not treat it as a completed failure or leave a certain outcome blocked forever.

Derive verification variants from these transitions and the affected code. Identify
all consumers of changed values, including later reads and notifications. Where
validity can change during a lock or external call, plan checks on both sides of
the validity boundary with the real wait in place, for each materially different path.
A simpler path cannot stand in for a different resource or ownership model. Keep
these scenarios in the existing verification mapping and select mechanisms used
by the changed flow; do not require an exhaustive cross-product of outcomes and paths.

Map primary and fallback/legacy paths separately. Apply related requirements
together: historical compatibility does not waive correctness of the selected data.
When behavior chooses a record, include a competing record that must not be chosen
and demonstrate why the intended one wins in each materially different path.

Give each task a stable ID, requirement references, observable outcome, dependency
IDs, verification references and status. A compact table is enough. Use pending,
active, done or blocked, with evidence or a blocker alongside updates. Code changes
alone do not make a task done.

For each dependency name the prerequisite result and the check that permits the
dependent task to start. That check must be executable before the dependent task;
it is distinct from final verification of the integrated batch. For example, an
API contract check can permit client integration, while the actual API-to-client
scenario remains a required batch check after integration. If no meaningful
prerequisite check is possible without the dependent work, group those tasks into
one integration task instead of creating a circular verification requirement.

Mark a task done when its own outcome and task checks are demonstrated. Keep
outstanding shared batch checks explicit; task completion or a satisfied dependency
does not establish that the batch is verified or ready for publication.

Maintain a requirement-to-check table in IMPLEMENTATION:

| Requirement | Scenario/path | Actual entry point | Expected consumer result | Command/manual procedure reference | Why this check proves the requirement; gaps/exceptions |
| --- | --- | --- | --- | --- | --- |

For each referenced verification procedure record:

- requirement IDs and tasks it covers;
- actual entry point, applicable scenario variants and expected observations,
  including the next user action and preserved state/resources where relevant;
- executable project command or concrete manual procedure;
- required environment and whether it runs per task, once for the batch, or remotely.

Inspect project scripts and CI configuration. Record full executable commands and
their relevant steps, including compilation, declaration generation, migrations
or setup when applicable. Use the project's applicable checks; explain any planned
substitution and which steps it preserves or omits. Classifying a check as remote
does not remove the need for adequate pre-publication proof of required behavior.

Verify that commands select the intended tests. Checks must exercise changed
boundaries through their real callers and consumers; constructed helper inputs
alone cannot establish that the application reaches that behavior. Cover relevant
negative paths and regressions, not every imaginable edge case.

For a requirement about visible UI or user interaction, plan execution through the
running interface, with concrete setup and observations. API tests do not establish
rendering, and typechecking does not establish interaction. Small diffs and difficult
test-data setup do not justify omitting required proof. Inspect available setup and
plan necessary prerequisites within scope before proposing an exception.

Order the most uncertain mechanism before dependent work. Investigate unknown
feasibility within preparation authority, or propose a bounded discovery batch
with an observation and stopping condition. Do not approve dependent feature
implementation on an assumed successful experiment.

## Review the plan before approval

The coordinator checks the plan against requirements and code for:

- requirements without tasks and meaningful verification;
- unreachable inputs/errors, dropped results or overlooked consumers;
- undefined ownership of a state transition or failure/recovery path;
- outcomes with no defined next action, stale client state with no reconciliation,
  or required variants represented only by a simpler scenario;
- dependency cycles, unavailable prerequisites or assumptions presented as facts;
- dependency checks that require the very task they are supposed to unblock;
- checks that cannot observe the claimed behavior or run in the chosen environment.

Reconcile every requirement with the check table, graphs and services/contracts
table. A missing check, weaker substitute or omitted affected path is a material
gap even when all rows have verification references. Do not present a plan with
such a gap as executable without a separately approved exception.

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
changes, both flow graphs, the services/contracts table and requirement-to-check
mapping; links to files alone are insufficient. State the actual sandbox/environment,
branch/base and PR destination, plus any execution budget and how to observe it.

Expose any requested verification exception as a distinct decision: affected
requirement/scenario, missing check, reason, attempted or considered setup, and the
remaining uncertainty. It may be decided alongside plan approval, but requires an
explicit answer of its own under the entry contract. General approval or silence
cannot waive it. Preserve mandatory project checks and label approved exceptions
as unverified behavior.

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
