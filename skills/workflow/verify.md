# Evidence and implementation review

Use the [entry contract](SKILL.md), requirements and IMPLEMENTATION. During preparation,
use the evidence standard to plan checks. During execution, collect results against
it. The coordinator owns local verification.

## Evidence standard

Derive obligations from original requirements and approved decisions before relying
on the plan's coverage or completion claims. Reconcile them with the whole changed
flow and affected consumers. An omitted obligation still needs proof.

Select evidence that can observe each required result:

- Exercise the real caller through the changed boundary to the consumer. For visible
  UI or interaction, use the running interface. Isolated helper/API tests prove only
  their covered contracts; mocked boundaries leave integration unverified. Inspect
  available setup before proposing an exception for required application behavior.
- Cover materially different primary and fallback/legacy paths under the same required
  correctness, including relevant failures and preserved behavior. For candidate selection, include alternatives that must
  not be chosen. Derive variants from the actual change, not an exhaustive cross-product.
- For stateful behavior, follow recovery through the next user action and check
  server/client state and resources agree. For timing or concurrency, exercise the
  actual ordering mechanism and conditions at use; constructed values that bypass
  it cannot establish that behavior. A simpler ownership/resource model does not
  stand in for a materially different one.
- Inspect project scripts and CI configuration. Use applicable full commands and
  confirm they select the intended checks. A substitution must preserve required
  steps, outputs and observed properties. Remote checks cannot silently replace
  required pre-publication proof.

Keep the requirement-to-check mapping in IMPLEMENTATION. Record each required
scenario as planned, demonstrated, missing or contradicted, with procedure, expected
and observed result, evidence and actual tested revision/environment. Inspect test
assertions and executed triggers; passing counts and reviewer agreement are not proof
of uncovered behavior. Include dirty changes in the tested revision or exact diff.

Before recommending a user procedure, confirm it is reachable from the affected
state with the user's permissions and leads to the required result. Distinguish
source-inspected steps from executed ones; recommending a procedure does not authorize it.

## Independent implementation review

Apply the review decision from [preparation](prepare.md#review-the-plan-before-approval);
reassess it if the actual change reveals materially different risk. When required,
use an agent who did not author the implementation. Supply original requirements,
approved decisions, base/candidate revisions, relevant code and verification evidence.

The reviewer evaluates the full change against required behavior and this evidence
standard, including known failures outside selected suites. Trace changed data,
meaning and timing through readers, writers and side effects. Return findings and
evidence without implementing or publishing. Keep the reviewed revision and result
in the batch's `evidence/`.

## Findings and completion

Give findings a requirement reference, trigger, consequence and supporting evidence.
Distinguish confirmed defects, missing proof, unresolved hypotheses, duplicates and
optional improvements. Resolve each material finding by confirmed repair, rejection
with evidence or an explicit applicable user decision. Pre-existing failures of
required checks still need a disposition; optional improvements do not expand scope.

After any repair, select checks from the full change and recheck affected behavior
and consumers. Required independent review must cover the final candidate's affected
behavior. Reuse unaffected evidence with its original revision; repeat only when
changes, new evidence or unresolved concerns invalidate it. Updating a report alone
does not invalidate application checks.

A task is done when its own outcome and checks are demonstrated. A prerequisite
check may permit dependent work while shared integration checks remain pending.
The batch is locally verified only when required pre-publication scenarios/checks
have adequate evidence, material findings are resolved and required review covers
the final candidate. Missing or contradicted proof prevents that claim.

Apply explicit exceptions under the entry contract and label affected behavior
unverified, never passed. Honor mandatory project publication checks. Local success
does not establish remote CI success or merge readiness. Once the publication
conditions are met, proceed to the authorized handoff without extra review rounds
or unchanged test reruns.
