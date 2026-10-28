# Workflow 4.2: bounded forward check

Date: 2026-10-04. Source baseline: `f2ea6ec57749300773fb687b43aa26eb3298619d`.
This records a process check, not an application implementation or a performance
comparison. The historical proposal trials remain unchanged.

## Candidate and method

The candidate uses discovery/interview before a settled plan, canonical document
ownership, optional delegation, a bounded design review and one feedback procedure
for implementation failures, CI, PR review and operator edits.

One fresh native agent received the candidate prepare skill and routed source
instructions, the original user request and read-only application access. It did
not receive historical proposals, known review findings or an expected answer for
the intake exercise. Application HEAD was
`10a5226206851e98a5360d68efba21188be1be7f`. Reads of application batch documents,
modifications, application tests and publication were excluded. The agent reported
six focused code reads/searches against a limit of ten. No second trial was run.

The intake is the [retained request](fixtures/b119-request.txt) up to, but excluding,
its `Testy` section, matching the second Cursor attempt. The actual pasted prompt
also has insignificant whitespace after the skill name.

Evaluated blueprint SHA256:
`ece7772dc03af2df368475c945bd9cfc6f973064d3f285289720ca5982f66ec0`.
The trial is retained in this Codex conversation under `workflow_forward_check`.

## Observed intake output

The agent produced a preliminary behavior proposal, a before/after component table
and a Mermaid diagram. It proposed questions about no available replacement,
the meaning of nearest time, empty-cart delivery and network failure. It explicitly
identified the empty-cart delivery recommendation as a departure requiring an
operator decision. It described clicks as non-reserving and planned verification
of the actual browser payload and both delivery implementations.

Its next state was `planned`, with unresolved decisions and no execution approval.
It did not invent a batch ID or claim tests passed. This supports the interview
transition on this input; it does not establish a complete implementation-ready plan.

## Feedback exercise

A separate simulated state supplied to the same agent had an approved requirement
to replace unavailable delivery times, unchanged capacity rules, completed task
T003 supported only by request/UI-selection tests, an open PR at H1, failed required
test-fast and completed code review. Comments reported a promised-time field
missing from the real checkout payload, proposed a new reservation table and
duplicated the payload finding. Existing authority covered implementation,
commit/push and updates to the same PR, excluding merge/deployment.

The observed response called for inspecting the finding and failed test, recording
dispositions, reopening T003 and defining a real browser-to-server recovery check
before changing code. It kept FEATURE unchanged, incremented the plan revision for
the changed check, invalidated affected evidence, retained the same PR and kept the
batch `active`. It rejected the new table against the approved scope and linked
the duplicate to the existing repair. H2 required fresh CI and applicable review
before `awaiting_review`, without another product approval for the repair.

This demonstrates routing of supplied feedback, not independent discovery of the
payload bug, successful code repair or actual CI waiting.

## Checks and limits

- Repository Markdown/link/discovery validation passed.
- All six package integrity/update tests passed.
- Ruby's YAML parser validated the five skill names and descriptions.
- The skill-creator Python validator could not start because PyYAML is absent in
  both available Python environments. No dependency was installed.
- Whitespace checks passed. No application package was installed or changed.

There was one intake and one simulated feedback exercise, with no operator answer,
delivery, recovery after interruption, real PR cycle or Cursor run. There is no
measured token/cost improvement or statistical reliability claim. Shorter text and
passing structural checks are not evidence that the five historical PR defects
will all be prevented. Further evaluation should measure the complete result and
operator interventions, not add review rounds to obtain a passing verdict.
