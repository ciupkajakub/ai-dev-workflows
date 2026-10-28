# 4.3.2 approval and recovery clarification

Date: 2026-10-06. Baseline: `0c30da8`. Candidate: blueprint 4.3.2.
The operator requested conclusions and clarification after reviewing the next
B119 run. This correction changes workflow instructions only.

## Retained evidence and decisions

[The fixture](fixtures/b119-delivery-v7.json) preserves selected transcript
excerpts with original line numbers and a digest, plus the locally observed
PROGRESS Current. It is historical evidence, not a live GitHub inspection.

| Evidence from the run | Decision required by the clarified rule |
| --- | --- |
| The session selects `fix_delivery_hours_v7`, then asks whether to replace the other B119 on PR 147. | A same-topic batch is context, not a mandatory redirect. Keep the selected target unless the operator selects another. |
| The operator says `popraawiamy`; a later proposal explicitly names `b119-fresh-slot-check` and updating PR 147, and is accepted. | The short reply alone does not select a checkout. The later named approval does authorize that presented target; do not erase that authority or ask for it again. |
| Only after delivery does the agent disclose that the operator had closed PR 147 and deleted its remote branch. | Inspect and disclose state before proposing delivery. Acceptance of an ordinary update does not cover an undisclosed reopen or branch restoration. Propose a linked follow-up, or obtain explicit authority for those actions. Recheck before publication. |
| The approval message describes behavior. Three follow-up questions are needed to obtain `checkSlot`, `fetchPickupCatalog`, their parameters, return values and skipped `preview` calls. | R4 is incomplete at the first approval request. Include the code-interface view in that message; do not wait for the operator to request it. |
| The backend signatures remain unchanged, but two browser functions stop sending requests for an empty cart. | Show changed call conditions and early returns. Do not invent new backend parameters or equate unchanged signatures with an unchanged interface path. |
| A subscription delivers the final CI failure notification; the agent reports that `scan_ruby` blocks handoff. | Preserve this successful continuation and honest result boundary. A known failure is still a failure without an accepted exception. |
| Local Current still says `verification`, push is next and CI does not exist, despite the transcript reporting publication and final CI. | Update the durable checkpoint to the actual stage, observed head, failed check and next decision. A new session must not replay the obsolete next action. |

The correction places checks at three observable boundaries: the approval
message, publication, and the report after a CI/review event. It uses existing
documents and review roles, with no new workflow state file or review round.
Metadata commits still require evidence bound to their actual revision; keeping
an obsolete Current is not a workaround for receipt freshness.

## Verification and limits

This is an author comparison against retained evidence, not a fresh independent
agent run. The rules reject the undisclosed reopening, missing interface
presentation and stale checkpoint on this case, while preserving the later
explicit target approval and confirmed CI subscription. This does not establish
that future agents will obey the rules or that the application works.

Run the existing Markdown/link validator, package checker tests, delivery gate
tests and `git diff --check` for this source change. These validate structure and
checker behavior, not semantic compliance. No application edits, installation
update, PR action or remote CI inspection belongs to this correction.

Observed validation: 20 Markdown documents and 65 local links passed; all 6
package checker tests and all 12 delivery gate tests passed. `git diff --check`
passed, followed by a staged whitespace check including the new fixture/report.
