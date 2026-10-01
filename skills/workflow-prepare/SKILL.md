---
name: workflow-prepare
description: Turn a business need into a blueprint feature contract and implementation plan for human approval when the user requests preparation.
---

# Prepare a proposal

Resolve this skill directory's symlinks before opening relative references.
Read the [shared entry rules](../entry-rules.md), then follow the complete
[Prepare a proposal](../../feature_execution_blueprint.md#prepare-a-proposal)
procedure, including its templates, readiness criteria, and presentation rules.
The steps below route that procedure; they do not replace it.

Use the supplied business need or issue reference. If neither the request nor
existing records identify it, ask for it. Inspect relevant code, tests, and
recorded decisions before asking product questions. For an existing unapproved
proposal, recover its original request and latest revisions and repair the same
batch. Do not promote an earlier agent assumption into an operator requirement.

1. Separate requested behavior, necessary technical decisions, and proposed
   product assumptions in FEATURE's existing sections. Resolve unsupported scope
   or requirement exceptions before designing the dependent change.
2. In IMPLEMENTATION's Tasks, build one compact component change map from code:
   named owners, before/after responsibilities, added/changed/removed inputs and
   outputs, their sources, and consumers. Walk each materially distinct scenario
   from trigger through actual validation, result production, and consumer action.
   Identify side-effect boundaries. A recovery handler does not prove that the
   required error can be detected at that entry point.
3. Assign tasks and checks to those paths in the existing plan sections. A check
   must name the condition that exercises the actual validator and the observable
   result. Keep private implementation details with the worker.
4. Apply [R1–R5](../../feature_execution_blueprint.md#proposal-readiness). Build
   the approval draft from the component map, with no missing material interface
   change or extra promise. Check graph edges if a diagram adds useful information.
5. Follow [Independent proposal review](../../feature_execution_blueprint.md#independent-proposal-review)
   where warranted and native subagents are available. Supply the original request,
   fixed proposal snapshot, draft summary, code access, and R1–R5, without your
   verdict or expected findings. Repair confirmed gaps in their owning documents,
   re-walk affected paths and re-review material repairs. Reconcile all five
   criteria at the final revisions, not just the last reviewer comments.

Record concise criterion results and evidence links in PROGRESS History; keep
Current's next action accurate and update shared ledgers as required. Record a
concrete limitation if independent review cannot run. Do not claim independence
or require a new manual operator step as a substitute. A material `fail` or
`unknown` prevents a ready verdict. Resolve ordinary technical choices yourself;
ask only for unresolved product decisions or genuine blockers.

Present one short [approval package](../../feature_execution_blueprint.md#approval-presentation):
product behavior, component before/after and interface changes, material risks and
observable checks, exact proposal baseline, and intended delivery scope including
push destination and PR authority. Write clear prose in the operator's language.
Link the documents for detail; do not make the operator read every function to
understand the change. Keep durable design evidence in the batch's existing files.

Stop at `awaiting_approval`. An unresolved decision is a decision request, not a
ready proposal. Preparation does not authorize implementation or publication.
