# Prepare a proposal

Use the entry contract and batch sections in [SKILL.md](SKILL.md). Preparation
owns the technical proposal and its presentation; it does not require a separate
plan reviewer or a readiness report.

## Discover and settle decisions

Read the original need, applicable project rules, relevant code and existing
checks. Trace the affected operation from its real caller through data,
validation and side effects to the consumer's resulting behavior. Inspect
materially different implementations when the change reaches them. Confirm that
the proposed inputs and results can actually travel along this path.

Present a preliminary solution before asking about unresolved expectations.
Separate requested behavior, necessary technical choices and proposed departures.
Every material change needs a requirement or an explanation of why the requested
result needs it; an adjacent defect is not sufficient justification. Resolve
technical facts through inspection or a permitted focused check. Ask the user
only about decisions that affect outcome or scope, with a recommendation and its
consequences. Reuse answers already given.

Keep the same batch while refining its proposal. A material unknown prevents an
execution-ready proposal. A technical uncertainty needs investigation, not an
invented product choice or another vote on unchanged prose.

## Make the proposal executable

Write observable requirements and a small sequence of verifiable changes in the
batch. Define shared contracts; leave private helper design to implementation.
For each required behavior choose a check with an actual trigger, expected
observation and project command or concrete procedure. Verify that commands
select the intended tests. Checks crossing a changed boundary must exercise that
boundary. Include relevant failure paths and affected existing behavior.

Identify the local checks, required CI and configured reviews needed for this
task, using project configuration rather than assumed job names. Planned checks
are not executed evidence. Use the entry contract to resolve the proposed GitHub
destination and operation before asking for approval.

## Present for one approval

Present the proposal in the user's language, from the same batch content the
implementer will use. Include the outcome and scope, material decisions and risks,
named interface changes, planned proof and the concrete delivery destination.
Show a compact before/after view of callers, inputs, outputs and side effects.
Changed call conditions or skipped calls belong in this view even when signatures
stay unchanged. Use a table, short code sketch or diagram only where it helps.

The approval message itself must expose these changes; linking a detailed plan
does not replace that explanation. Omit empty sections and repeated design prose.
If decisions remain, request those decisions rather than execution approval.
Otherwise identify the exact proposal and ask once for its presented delivery
scope. On approval, follow [deliver.md](deliver.md).
