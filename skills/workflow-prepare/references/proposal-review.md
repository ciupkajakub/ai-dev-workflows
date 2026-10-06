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

Return compact evidence and actionable findings with locations and consequences.
Use R1–R5 to identify gaps, not five mandatory reports. Separate confirmed defects
from product questions and hypotheses. Check that the operator can assess behavior,
technical changes, interfaces, relevant flow, decisions and proof under the
[approval presentation](../../../feature_execution_blueprint.md#approval-presentation).
Do not demand empty sections, a fixed layout or repeated descriptions of the design.
Check the approval message itself for named code interfaces and before/after
inputs, outputs and call conditions. A correct design hidden in implementation
notes does not satisfy R4 presentation. Check that the proposed delivery action
matches the inspected PR state and selected checkout; generic acceptance of an
update cannot authorize an undisclosed reopen or remote-branch restoration.
Do not redesign the feature, add unrelated improvements, edit application files
or supply the missing design on the author's behalf.

For the focused confirmation, inspect repaired paths and affected consumers and
carry forward unresolved findings. Do not limit review to textual agreement.
Reference unchanged evidence rather than duplicating it. If material gaps remain,
return the concrete missing fact or decision and a recommended investigation;
do not initiate another review round. The coordinator owns the review budget.
