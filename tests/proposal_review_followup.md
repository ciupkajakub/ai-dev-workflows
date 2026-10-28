# Follow-up: path evidence and the approval text

## Scope and fixed baseline

The next real Cursor proposal still received R1–R5 pass despite material gaps.
The [retained input](fixtures/b119-proposal-revision3.txt) includes the original
request, FEATURE revision 3, IMPLEMENTATION revision 3, and the final approval
text with the previous review verdict removed. It is historical data, not a skill.
Application code baseline: `10a5226206851e98a5360d68efba21188be1be7f`.
Workflow baseline: `259cdc5d10de0e12067ff95ef9f3ef149e0a86e4`, blueprint 4.1.0,
schema 4. Both versions remain unchanged in the candidate.

The initial diagnosis used three fresh native Codex subagents: a full review,
six pointed claim checks, and an isolated summary. No expected findings or prior
verdicts were given to agents. The application was read-only. These were actual
agent trials, not Markdown checks and not Cursor/model comparisons.

A code-backed reference was fixed before those trials and reused without changes:

| Case | Required recognition | Code anchor in application |
| --- | --- | --- |
| D1 | Quote generation does not specify validation of the supplied delivery token; the plan must choose the shared contract for both implementations. | `orders/checkout/delivery_selection.rb`, `own_fleet/delivery_offer.rb`, `delivery_promises.rb`, under `app/services/` |
| D2 | Removing the browser empty-cart shortcut does not bypass either delivery producer's nonempty-lines guard. A compatible approach or a genuine product decision remains unresolved. Do not invent a hypothetical load or waive minimum charges. | `DeliveryPromises#valid_request?`, `OwnFleet::DeliveryOffer#available?` |
| D3 | The pickup successor can disappear after receipt: `applySelectedFromPayload` calls `syncSelectedSlotButton`, which clears confirmed selection when no matching button exists. The plan promises preservation without specifying the integration. | `app/javascript/controllers/cart/pickup.js:86–91,201–208` |
| D4 | Default `bin/spec` excludes system examples even when given an explicit system spec path. | `bin/spec:11–12,25,171–179` |
| D5 | The approval text drops named component owners and material replacement payloads already present in the map. | Retained map versus retained approval draft |

The six pointed claims mixed three valid choices with three code contradictions:
omitting `day_groups` preserves the grid; explicit spec paths do not override the
fast filter; fleet verification reconstructs the signed generation time; an empty
delivery quote still cannot offer a window; rejection flags can exist without a
successor; applying a pickup payload alone does not preserve a missing-button
selection. The grader was this task's coordinator using code evidence, not an
independent human annotator.

## Candidate mechanism and predeclared gates

Keep R1–R5 and the three batch documents. Change the unit of review to material
paths: identify them from the request and code before reading the author's plan,
then record input/validator, producer/data, consumer/resulting state, and evidence.
Follow the consumer beyond receiving the payload. Carry unresolved paths into the
readiness result instead of silently omitting them.

Keep the exact approval text in PROGRESS History as part of the reviewed snapshot;
present that text without a new final rewrite. Group related owners, state each
fact once, and aim for roughly 300–500 words for a typical multi-component proposal
without hiding interfaces to meet a limit.

Before running the candidate, require concrete recognition of D1/D3/D4/D5, D2
resolved or explicitly unresolved, preservation of valid choices, and no material
unsupported finding. The summary must preserve nine material information groups
and stay within 600 whitespace-separated words for this case. This tolerance was
fixed before seeing the result, not used to redefine failure afterward. Only if
both gates pass run one fresh preparation in isolation, with at most one initial
native review and one focused rereview after repairs. No tuning loop or delivery.

## Component trial results

| Trial | Baseline instructions | Candidate instructions |
| --- | --- | --- |
| Full review | D1/D4/D5 detected; D2 code guard recognized but demoted to a hypothesis; D3 omitted. R1 pass, R2–R5 fail. | All five identified. D3 contains the concrete clearing path and remains `unknown`, correctly avoiding an assumption about which private helper the author must use. R1 pass, R2–R5 fail. |
| Pointed claims | 6/6 correct, including the missing-button claim omitted by full review. No false rejection of the three valid claims. | Not repeated; the changed mechanism concerns autonomous path coverage. |
| Isolated presentation | Nine information groups preserved, but 865 words. | Same groups preserved in 590 words. No invented test/review success; unresolved document inconsistency disclosed. |

The summary groups cover product/hold boundaries; pickup owners and nil; catalog
versus a single read; rejection/next pickup payload; delivery response and consumer;
expiry; distinct SMS/order paths; proposed ranking/network choices; and risks,
baseline and authority. This checks information retention from a map, not whether
the old map is a correct design. It does not establish exact-text handoff yet.

The candidate full reviewer also found missing successor offer metadata and cart
loads at checkout recovery. The coordinator checked these against actual consumers
and callers. They are additional findings, not replacements for missed cases in
the predeclared denominator. Valid choices, including nil normalization, separate
rejection flags, pickup preflight and the existing hold boundary, were preserved.

Candidate instruction identities:

- Blueprint SHA256: `146f067691c8e194d1a43c66c0d2156d70d71402d4cdd8ba0312a5791a517347`.
- Prepare skill SHA256: `552d4721396976423ef28d3b491a70e001a837691dbee86973cca37bf3e9be0b`.
- Shared entry rules unchanged: `9a814cb06f9284df18a577a28ecb83e3d0e3f956bf47c0e2251ba3470d9a0abb`.
- Reference SHA256 fixed before baseline trials: `b1b624998b5d135e414c283db0402e5e232a3533dbfb7075ced79c4dc7f03fdb`.
- Candidate gates SHA256: `04c38a32a25d9aba1b7f68502ccaf15fe1684bf3df1cc5cb5d356bf06bea934c`.

Native run names: `diagnostic_full_review`, `diagnostic_claims`,
`diagnostic_presentation`, `candidate_review`, `candidate_presentation`.
Each used a fresh context and inherited model configuration with no override.
The original Cursor transcript exposed `grok-4.7-high` for two reviewer calls;
this is not a controlled provider/model comparison. One run per condition cannot
establish reliability or attribute all variation to the instruction edit.

## Fresh preparation trial

The component gates passed. Native agent `candidate_full_prepare` then used the
original request, candidate instructions and read-only code in a fresh context.
It could not read earlier proposals, findings, reference answers or other results.
One initial review by `candidate_full_prepare/review_trial` and one focused
rereview followed one document repair; there was no second preparation attempt.
The [retained complete output](fixtures/b119-prepare-trial.txt) includes final
FEATURE/IMPLEMENTATION/PROGRESS, both review results and the exact final message.
It is explicitly not an approved feature or a reference solution.

The trial improved several specific outcomes: both delivery validators are named;
replacement data reaches consumers including timer/consent state; missing pickup
DOM state is addressed before selection; focused system commands use `browser`;
and empty-delivery/shared-concurrency questions remain visible rather than being
reported as completed design. The returned package is 382 words. Its text exactly
matches the last retained PROGRESS approval block and the reviewed APPROVAL file.
Final FEATURE and IMPLEMENTATION bytes also match the r2 reviewer snapshot:

- FEATURE r2: `466fd0f8c8368d8ea450fd34a1f461cbee8f59a23b3031869549516558abae17`.
- IMPLEMENTATION r2: `d7f651463b2e0af8bf91f66c4eac62ce43eddfbb9904662ff6f9f8533acec259`.
- Approval text: `9e0804eed2e1d0860ad2af45b962939f5e3fbe217ecbd7ba4fc89a3313315bb0`.

The preparer and reviewer report R1–R4 unknown, R5 pass. They explicitly request
product resolution rather than execution approval. That is an honest stop, not
proof of a complete executable plan. The empty-delivery load and shared stale-offer
questions were not answered on the real user's behalf.

**Full-trial gate: not passed. No source commit.** The coordinator's code-backed
assessment additionally rejects an unsupported scope extension still present in
final T3/S5 and the approval message: adding delivery validation to
`Orders::Checkout#read_only_call` for the SMS preflight. The requested UI invokes
phone proof only for guest `pay_on_pickup`
(`app/javascript/controllers/cart/checkout.js:55–61`,
`app/javascript/controllers/cart/checkout_dom.js:145–153`); delivery requires online
payment (`app/services/orders/checkout/delivery_selection.rb:30–31`). The planned
click validator already covers the required pre-phone delivery check. The proposal
does not demonstrate why changing the direct SMS preflight for delivery is needed
for this feature or identify it as a separate proposed scope addition. An observed
missing check on another entry point is not authority to expand that entry point.
Both reviews leave this extension unchallenged, treating the remaining problems
as only the two product questions. R1 therefore also has a confirmed scope gap,
not just those unknowns. This category was already distinguished in the original
regression case; the successful narrow review did not prevent it during generation.

No correction was fed to the preparer and no new trial was started to make the
result pass. The candidate remains uncommitted for inspection. The experiment
supports improved known-gap recognition and exact compact-text handoff on this
case, but not the claim that the revised prepare reliably produces a properly
scoped proposal. The next issue to address is separating reachable required
paths from adjacent opportunities during planning/review, not increasing the
reviewer count or silently repairing this application proposal.

## Repository checks and limits

Final checks: `python3 -B tests/validate_blueprint.py` passed for 11 Markdown
files and 40 local links; `python3 -B tests/test_check_package.py` passed all six
tests. `git diff --check`, direct whitespace checks for new fixtures/report, and
manual diff review passed. Candidate instruction hashes still match the tested
snapshot. Structural checks do not override the full behavioral trial's failure.
The skill creator's auxiliary
validator could not start because PyYAML is absent from both available Python
runtimes. No dependency was installed. The unchanged name/description frontmatter
was checked directly; this is not reported as a successful auxiliary validator run.

No changes were made to application code, installed workflow, or real batch.
No application tests, delivery, CI, push, or PR publication were run. Source
changes remain uncommitted because the full trial did not pass. All 2374 tracked
or nonignored application files, its Git HEAD and status match the pre-trial
baseline. There is no instruction to refresh the real installation from this
uncommitted candidate.

## Later simplification comparison

The [lean preparation comparison](proposal_simplification_case.md) records the
subsequent bounded experiment. Earlier outcomes and uncommitted-state statements
above describe their historical checkpoint, not a claim about the later source
commit. The lean variant also retains material limitations; see its actual results.
