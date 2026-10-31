# Prepare or revise a plan

Use the [entry contract and records](SKILL.md). Preparation must establish a
justified solution and a feasible way to check it before execution approval.

## Understand the outcome and choose the approach

Read the original request, project rules, affected code and existing checks.
Separate required outcomes from suggested implementation. Trace the actual caller
through validation, persisted state and side effects to the consumer's result,
including materially different affected paths. Support design-critical assumptions
with code/history inspection or tests; an unsuccessful inspection leaves them unknown.

Choose the simplest approach that satisfies the same requirements. Check existing
mechanisms before adding one, and explain material costs or risks of the choice.
For new or duplicated state, identify the authoritative representation, writers,
readers and rules that keep representations consistent throughout their lifecycle.
Multiple representations are acceptable when their roles and consistency are defined.

Limit changes to required outcomes and dependencies, including existing defects
that prevent success or whose consequences worsen. Resolve their treatment before
approval. When goals, acceptance criteria or the solution imply different behavior,
show a concrete example and obtain a decision before approving dependent scope.
Resolve missing behavior before adding heuristics;
weakening criteria requires a requirement change. Do not expand scope unilaterally.

Present a preliminary solution and ask only unresolved product/scope questions,
with recommendations and consequences. Investigate technical facts yourself and
reuse decisions already given. Record observable requirements with stable IDs in
FEATURE, including failures and behavior that must survive. Reconcile dependent
requirements and design when a decision changes.

## Plan the selected outcome

Map coherent, verifiable batches and their dependencies in FEATURE. Split where
an outcome can be checked separately or uncertainty must be resolved before more
work, not by file counts or layers. Keep later batches at outcome level until their
assumptions are stable. Name the base/integration condition for unpublished dependencies.

For the selected batch, keep the following in IMPLEMENTATION:

- The chosen approach and before/after flow, naming actual callers, contracts,
  readers, writers and side effects, including shared/generated contract consumers.
  Use prose, a diagram or a table according to what makes the change reviewable;
  do not repeat the same facts in all three formats.
- For changed stateful behavior, reachable outcomes and transitions: server/client
  state, resources, next permitted action, and recovery from interrupted or conflicting
  state. Explain transactions, concurrency and retries where correctness depends on
  them; distinguish an unresolved result from a confirmed one.
- Tasks with IDs, requirement references, outcomes, dependencies, checks and status
  (`pending`, `active`, `done`, `blocked`). A dependency names an observable prerequisite
  that can be checked before the dependent task starts. If none exists, group the
  coupled work. Final integration checks remain separate from prerequisite checks.
- One requirement-to-check mapping, using the [evidence standard](verify.md#evidence-standard).
  Each row names requirement/scenario, actual entry point, expected consumer result,
  procedure and any gap. Procedures include executable commands or manual steps,
  environment, expected observations and when they run. Reuse this mapping for results.

Investigate the most uncertain mechanism first within preparation authority, or
propose bounded discovery with an observation and stopping condition. Do not present
dependent implementation as executable while its feasibility is assumed.

## Review the plan before approval

Have an agent who did not author the plan independently assess the original request,
project rules, relevant code and the whole plan against this preparation procedure
and the evidence standard. The review must assess both whether the design is justified
and whether it can be implemented and verified. The author's concern list is context,
not a limit on review. No particular model or fixed number of rounds is required.

Keep the reviewed plan snapshot, code revision, checks, findings and supporting
sources in the batch's `evidence/`; link it from IMPLEMENTATION. The reviewer does
not edit files. No findings is valid; a review label alone establishes nothing.

Resolve findings by correcting the plan, rejecting them with evidence or asking for
a decision. Distinguish defects and missing proof from optional improvements.
After a material correction, reassess the affected design against the original
requirements, including whether retained mechanisms are still needed and consistent.
Have the reviewer recheck that change and its dependencies; reuse unchanged evidence.

Also decide whether independent implementation review is required before publication.
Require it when an incorrect result could cause material harm that is difficult to
detect or reverse, or when project rules or agreed scope require it. Record the risk,
review scope and in-scope repairs in IMPLEMENTATION; otherwise it is optional.
Plan review never establishes that the resulting implementation works.

## Present the proposal

After resolving material decisions and blocking findings, present the outcome,
batch, rationale, contract changes, dependencies, risks and planned proof in the
user's language. Show what limitations prevent users from doing or determining.
Include environment, branch/base, PR destination and agreed budget.
Show before/after behavior across the affected flow; links alone are insufficient.
Link details without duplication. Approval accepts presented behavior, not missing evidence.

If a material decision, feasibility assumption or gap in planned verification remains
unresolved, ask about it rather than calling the plan executable. Planned implementation
tests need not have run before approval. For an exception, explain the missing check,
affected requirements, setup considered and remaining uncertainty under the entry
contract. A deferred check also needs an owner, environment and required stage.
An unavailable independent reviewer is missing review, not satisfied by self-review.

Identify the exact plan for approval. Existing explicit approval is sufficient;
on approval follow [deliver.md](deliver.md).

## Requested feedback and continuations

Reconcile the actual PR/checkout and approved behavior. Classify feedback using the
[finding rules](verify.md#findings-and-completion). Correct the requirement, design,
verification plan or implementation task responsible for the confirmed problem.

Use the same batch for corrections to its outcome and a new batch for a distinct
outcome. Preserve approvals, completed work and valid evidence. Present only the
proposed delta, affected requirements/tasks, checks and publication destination;
review material changes under the procedure above. Approval covers the continuation,
not reapproval of unchanged work or execution of later batches.
