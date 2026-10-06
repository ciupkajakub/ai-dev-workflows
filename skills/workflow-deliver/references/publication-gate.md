# Publication receipt

The independent verifier writes `evidence/verification.json` in the batch folder.
Store its review note and focused check outputs beside it. These are evidence,
not a second workflow state store. Reuse the existing task/check IDs from the plan.
The coordinator derives the required ID list from the approved requirements and
current plan, not from the receipt's own claims. Include every required
pre-publication check. Checks explicitly assigned to post-publication `pr_checks`
run after the PR update and still block final handoff; they do not block creating
the PR they require. All required local behavioral scenarios remain in this gate.

Before accepting any check's `pass`, reconcile every promised behavior with the
verifier's trigger/assertion/evidence mapping in the existing review note. Its
`observed` summary must cover that whole check or report missing proof. For a
diff-scoped check, also reconcile the complete base-to-head file set with actual
command coverage or verified reusable results. The checker validates records,
not these semantic comparisons: exit 0 cannot override a missing behavior or file.

The receipt has this shape; replace all example values with actual observations:

```json
{
  "schema": 1,
  "batch": "B119",
  "head": "<full final application commit>",
  "feature_revision": 5,
  "plan_revision": 6,
  "implementer": "<native implementer/session identity>",
  "verifier": "<different native verifier/session identity>",
  "review": {
    "result": "pass",
    "evidence": { "path": "review.md", "sha256": "<file digest>" }
  },
  "checks": [
    {
      "id": "V001",
      "result": "pass",
      "observed": "<trigger, actual caller, observed result and invocation>",
      "evidence": { "path": "V001.log", "sha256": "<file digest>" }
    }
  ],
  "findings": []
}
```

Include every required scenario/check, not just passing examples. A non-passing
result or missing evidence blocks the gate. Findings use `id`, `status`, `reason`
and `evidence` with the same path/digest shape. Only `resolved` with repair proof
or `rejected` with supporting evidence clears a finding. Preserve earlier receipt
versions and failures as history. When reusing unaffected evidence, explain the
original tested revision and why the final diff leaves that proof applicable.

Run from the application before publication or a PR update:

```sh
python3 -B <package>/skills/workflow-deliver/scripts/check_delivery_gate.py \
  --repository . --receipt ai-workflow/work/<batch>/evidence/verification.json \
  --batch <batch> --feature-revision <revision> --plan-revision <revision> \
  --required V001 --required V002
```

Repeat `--required` for the complete required pre-publication check list. The checker compares the
receipt with actual HEAD and supplied batch/revisions, checks distinct identities,
passing observations, dispositions, evidence files/digests and a clean working
snapshot. Untracked receipt/evidence files are allowed in their separate directory. Keep the
current receipt untracked or in a separate durable artifact location; committing a
receipt changes HEAD and makes its recorded snapshot stale. If older evidence is
committed for history, write the final receipt to a new untracked file rather than
editing that tracked receipt. Retain its location in the handoff.
Commit other application/doc changes before the final verification snapshot.
After a metadata-only commit, the verifier may bind a new receipt by inspecting
that diff and reusing applicable results instead of rerunning the tests.

Exit 0 means the records pass these checks; 1 blocks publication; 2 means checking
was unavailable and also blocks publication. Keep the stage `verification` or
`repair` until resolved. Do not remove required IDs to obtain a pass.

The checker cannot authenticate who wrote a receipt or judge whether assertions
prove the stated behavior. It does not intercept Git/PR tools or start agents.
The coordinator must inspect the actual independent session and evidence; native
execution controls remain responsible for following the publication boundary.
