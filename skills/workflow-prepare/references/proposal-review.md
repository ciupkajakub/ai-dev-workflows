# Review a proposal

Review the supplied fixed FEATURE/IMPLEMENTATION snapshot and approval draft against
the original request and read-only code, using the blueprint's
[R1–R5](../../../feature_execution_blueprint.md#proposal-readiness).
This is design review, not implementation or a claim that planned tests passed.

Start with the request and code before reading the author's approach. Identify
required scenarios and their actual entry points. Then compare the proposal: which
requirement needs each material change, and what fails without it? An adjacent
code defect alone does not justify adding work to this proposal.

Trace each materially different path through input, validation, result production
and the consumer's resulting state, including subsequent rendering or storage.
Check that shared data is sufficient, error producers are reachable, and side
effects match this entry point. Check that planned commands select the intended
tests. Treat uninspected or unresolved material paths as unknown. Private helper
choices need not be settled; shared contracts do.

Return compact path evidence, actionable findings with proposal/code locations
and consequences, and R1–R5 results derived from that evidence. Separate confirmed
defects from genuine product questions and hypotheses. Check the draft against
the [approval presentation](../../../feature_execution_blueprint.md#approval-presentation),
requiring its filled sections, diagram, distinct open/proposed decisions and all
material interfaces. Correct prose alone cannot pass R5 when the template is incomplete.
Do not redesign the feature, add unrelated improvements, edit application files
or supply the missing design on the author's behalf.

For a focused rereview, inspect the changed paths and summary, carry forward
unresolved findings, and reconcile all criteria at the new baseline. Agreement with
the author is not evidence. Reference existing plan rows for unchanged evidence
rather than duplicating the design.
