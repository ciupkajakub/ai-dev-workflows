# 4.4 requirement coverage and failure disposition

Date: 2026-10-07. Baseline: `c9657dd`. The operator requested a workflow repair,
not completion of the application feature.

## Failure mechanism

The retained B119 report at `435aa843` passed V001 through V009 while admitting
that the closed-list timer clause of AC1 had no executed proof. It also put the
known G3 recovery failure outside the gate because its test was tagged release.
The instructions already prohibited both decisions. Receipt schema 1 nevertheless
allowed check IDs and an empty findings list to satisfy the record checker.

[The retained fixture](fixtures/b119-green-report-gaps.json) contains the green
check IDs/results, source head, review digest, AC1 source and exact review
excerpts. The focused obligation/finding labels are audit labels added here.
They are not a replacement for the complete application's requirement inventory.

## Changed decision mechanism

The verifier starts from approved requirement clauses before the author's verdict.
The coordinator independently supplies those obligation IDs and the run's known
finding IDs to the checker. Schema 2 accounts for obligations separately from
planned tests. Missing or undemonstrated obligations and omitted known findings
block publication even when every listed test passes. Rejected findings need a
scope-comparison artifact; a lane label by itself is insufficient. Existing
review notes hold the mapping and comparison, so no workflow state file is added.

Under authorized delivery, a rejected report enters repair and continues with
focused investigation, repair and verification. A diagnosis commit is not the
handoff. Audit-only requests still stop after the audit; unrelated repairs need
their own authority. This source task does not authorize application repairs.

## Executable regression and limits

`tests/test_delivery_gate.py` exercises the CLI in temporary Git repositories:

- Green checks plus an omitted or explicitly missing requirement return 1.
- A known failure omitted from the receipt returns 1.
- Rejecting a known failure with only a release-label reason and no scope
  comparison returns 1; an open finding also returns 1.
- Complete obligation records and evidenced dispositions can pass.
- A schema 1 receipt and a schema-only version bump both fail without coverage.

The retained-report test imports the actual green V001–V009 results into otherwise
valid synthetic records. It requires the missing AC1 clause and known G3 finding
independently, and asserts both blocking diagnostics. It tests a workflow decision,
not whether the application works. No application tests or repairs were performed.

These tests do not prove that an agent derives every obligation or every finding,
or that its observations are truthful. A fabricated demonstrated result with a
file digest is still beyond this checker's semantic ability. Native controls must
also enforce using the gate. This is a narrower, executable safeguard, not a claim
that instruction following is solved or a fresh blind agent trial succeeded.
The package remains uninstalled in the application until an authorized update.

Validation on 2026-10-07: all 18 delivery gate tests and 6 package checker tests
passed. Markdown validation passed for 21 documents and 66 local links. Whitespace
validation passed, including the staged new fixture and this report.
