# 4.3 delivery flow forward check

Candidate blueprint 4.3.0 was evaluated in one fresh independent agent session
against application HEAD `02bcbeb8c3a570c4962d9ed5a4bbd26f2fee3142` in the retained
B119 checkout. Input was the delivery skill, the request to finish approved B119
and hand off its PR, and the raw application/batch files. The evaluator was not
given expected defects, remote findings or a desired verdict.

The evaluation allowed application read-only inspection and small temporary
reproductions. It did not permit application repairs, publication, full services,
full suites or network inspection. Nine tool calls covered code, tests, approved
snapshots, recorded evidence and reproductions using the actual JavaScript modules.

## Observed decision

The evaluator selected `repair` with the batch remaining `active`, rather than
accepting recorded task completion. It found:

- Delivery's constructor accepts but does not store its supplied validation
  callbacks. A reproduction selected a dead window with zero validator calls.
- Overlapping catalog requests can apply the obsolete response after the current
  response. The existing guarded quote path does not protect the replacement.
- Applying a partial delivery refusal clears omitted fee/address fields. A
  reproduction changed fee 1200 to 0 and the retained address to an empty value.
  Recovery also leaves an old error when a subsequent message is absent.

It reconciled these findings with the approved batch checks, distinguished pickup
browser examples from missing delivery proof, and required repair tasks/regression
checks followed by independent verification. Running the publication checker with
V001–V005 and the absent receipt returned unavailable, which blocks publication.
It did not treat old passing summaries or unavailable current CI as a pass.

## What this proves and does not prove

This is one bounded forward check that the candidate can choose the repair stage
from real artifacts and refuse an unsupported handoff. It does not prove that
Cursor will always invoke an independent verifier or obey the checker. It did not
execute the complete implementation → repair → browser verification → PR cycle,
measure token savings or establish that future PR review will find no defects.
The application was not changed by this evaluation.

The separate `test_delivery_gate.py` suite tests the checker's actual publication
outcomes using temporary Git repositories, including missing scenarios, stale
snapshots, self-verification, incomplete findings and altered evidence. Those
checks validate record integrity, not whether the claimed scenarios are true.
