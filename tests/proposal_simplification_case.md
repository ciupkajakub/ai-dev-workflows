# Prepare simplification: bounded behavioral comparison

## Question and change

Does a shorter preparation procedure preserve technical coverage while reducing
unsupported scope and producing a readable approval package on the retained B119
request? This compares complete instruction packages, not token count alone.

The pre-simplification baseline is the uncommitted candidate recorded in
[the previous trial](proposal_review_followup.md), based on source commit
`259cdc5d10de0e12067ff95ef9f3ef149e0a86e4`. Its exact instruction edits are retained in
[the baseline patch](fixtures/prepare-before-simplification.patch), which applies
to that source commit with `git apply --unidiff-zero` and was checked to
reconstruct both files byte for byte.
The lean candidate removes duplicated
procedure text from the skill, keeps R1–R5 in one place, gives the reviewer a
separate brief, and replaces repeated presentation rules with one neutral example.
The author starts from requested scenarios and justifies each material change.
No B119-specific service, parameter or expected answer is in the instructions.

Blueprint revision 4.1.0 and schema 4 remain unchanged. FEATURE, IMPLEMENTATION
and PROGRESS templates are byte-identical to baseline. Blueprint content outside
Prepare is unchanged, including approval, delegation, feedback and resume boundaries.

| Instruction measure | Baseline | Lean candidate |
| --- | --- | --- |
| Author's routed text: skill + entry rules + Boundaries/Pipeline + Prepare | 5061 words | 2685 words |
| Separate reviewer brief | Included in Prepare | 248 words |
| Whole blueprint | 7569 words | 5642 words |

Counts split on whitespace and omit boundary headings in section extraction.
They measure supplied instruction text, not the actual full model context, provider
tokens or monetary cost. Even counting the new brief, total selected procedure
text decreases. The author is not required to read the reviewer brief.

## Method fixed before runs

Application code is read-only at `10a5226206851e98a5360d68efba21188be1be7f`.
Both preparations get the identical [original request](fixtures/b119-request.txt)
and app checkout, a fresh
native agent context, inherited model settings without overrides, and their own
frozen instruction package. Existing app workflow instructions are overridden by
the selected package. Neither author gets earlier proposals, reviewer findings,
expected answers or sibling outputs. App policies still apply. Outputs use an
isolated directory and simulated batch identity B119-trial, never the real batch.

Each condition is limited to one preparation, one independent review, one author
repair and one focused rereview. Actual reviewer availability is reported. No app
implementation, tests, services, installs, commits, delivery or publication run.
The coordinator grades artifacts against code and the same R1–R5. It is not an
independent human evaluation. The original request contains genuine product
ambiguities; asking a grounded question is allowed and is not itself failure.

Before the runs, require: no confirmed material scope/technical defect; all material
interfaces visible in an approval/decision message targeting at most 600 words;
no false ready verdict; preserved request, decisions and revisions. Known risks
include both delivery validators, empty-cart guards, recovery through client state,
expiry/consent, existing hold boundaries, partial catalog responses and actual test
selection. A change to delivery SMS preflight needs a requested reachable scenario;
an adjacent unchecked entry point alone does not justify it. This reference is
withheld from authors and reviewers.

One additional fresh reviewer uses the lean brief on the retained old revision 3
proposal. The unchanged D1–D5 reference from the previous report grades whether
known defects remain detectable. This checks the reviewer, not full generation.
Only if both this review and the full lean preparation satisfy their gates can the
candidate be promoted to a local source commit. No instruction tuning after seeing
the lean result and no repeated preparation to obtain a favorable answer.

One run per condition cannot establish reliability, statistical superiority or a
causal effect of length alone. This is a bounded case comparison, not a Cursor or
cross-model benchmark. Wall time, if recorded, includes exploration/tool/scheduling
variation. No provider token/cost telemetry is available.

## Frozen instructions

Raw trial request SHA256: `094caa4c4152d2b94c7ab4d380349db2c1fbf18772ffdc86b59033a71529d1b7`.
Retained request SHA256 after trailing-whitespace normalization: `eb4c77bddc02bb6ca0a3383303de72859de64c9bf10e75900979d2431ca83273`.

### baseline

- `feature_execution_blueprint.md`: `146f067691c8e194d1a43c66c0d2156d70d71402d4cdd8ba0312a5791a517347`.
- `skills/workflow-prepare/SKILL.md`: `552d4721396976423ef28d3b491a70e001a837691dbee86973cca37bf3e9be0b`.
- `skills/entry-rules.md`: `9a814cb06f9284df18a577a28ecb83e3d0e3f956bf47c0e2251ba3470d9a0abb`.

### candidate

- `feature_execution_blueprint.md`: `1966bee9500e3a9d175b35b7de24c8b9fb16abd49e3e43cfce7b53f3a2fc5b32`.
- `skills/workflow-prepare/SKILL.md`: `98a85a736b874301607ac0177e5997281fed24124420f18d9c2d4041c8ffe39f`.
- `skills/entry-rules.md`: `9a814cb06f9284df18a577a28ecb83e3d0e3f956bf47c0e2251ba3470d9a0abb`.
- `skills/workflow-prepare/references/proposal-review.md`: `ca40aaa20f612f4fb38907749ba9a3e09094a2a1ed24f1b29cd7b9e2ddc4201b`.

## Results

### Retained-proposal review

Fresh reviewer `lean_known_proposal_review`, with no prior verdict or expected
findings, rejected the old revision 3 proposal. D1–D5 were all recognized with code:
missing selected-delivery validator/checkout recovery producer (F1), empty-delivery
guards (F2), pickup selection cleared by subsequent DOM/storage logic (F4), system
commands excluding their examples (F6), and omitted material approval interfaces
(F7). Its additional findings concern cart-aware successors, full delivery metadata
and timer/explicit-request dispatch. These do not replace the five reference cases.
R1–R5 were all fail for that historical proposal, not for the lean instructions.
No fresh diagram was present in this fixture; earlier graph evidence remains in
[the original case](proposal_readiness_case.md).

### Fresh preparations

The baseline run `prepare_baseline_trial` completed one initial review and one
focused rereview by `prepare_baseline_trial/independent_review`. The initial reviewer
used `fork_turns: none`; the focused rereview reused that context. Exact task messages
and provenance are in [the retained baseline output](fixtures/b119-prepare-baseline.txt).
Final FEATURE/IMPLEMENTATION are revision 2. The approval message is 415 words.
The author/reviewer report R1–R4 unknown for empty-cart delivery and no successor,
and R5 pass; neither claims execution readiness.

The coordinator separately confirms an R1 failure: final plan T4/P6 and the approval
still add delivery validation in `Orders::Checkout#read_only_call`. The public UI
only requests phone proof for guest pay-on-pickup, while delivery requires online
payment (`cart/checkout.js:55–61`, `cart/checkout_dom.js:145–153`,
`orders/checkout/delivery_selection.rb:30–31`, under `app/`). Click validation already
covers the requested before-phone behavior. The reviewer treats the extra preflight
validation as technically sound without establishing why the request needs it.
This repeats the previous full-run scope failure, despite a compact summary and
useful technical refinements. No finding was fed back to the author for another try.

The lean run `prepare_lean_trial` also completed one initial review, one repair and
one focused rereview, by `prepare_lean_trial/proposal_review`, initially
`fork_turns: none`, inherited model. [The complete retained lean output](fixtures/b119-prepare-lean.txt)
includes both proposal revisions, final progress/approval, both reviews, exact
reviewer prompts and provenance, plus the separate historical-proposal review.

The first review identified an overly broad OTP promise and inconsistent expiry
fetch rules. The author repaired the OTP scope by tracing the real pickup-only
journey, rather than adding delivery validation to the SMS preflight. Expiry became
local state requiring an explicit subsequent user action to recheck; no hidden
catalogue polling. The author also kept the shared-fleet race decision explicit.
No coordinator findings were supplied to either preparer or native reviewer.

The final reviewer reports R1/R2 unknown, R3 fail, R4/R5 pass. F3 is a concrete,
low-priority verification-assignment defect: V4 promises to observe the browser
never requesting delivery OTP but only runs request/service specs. The browser
observation belongs in the already planned V3/V6. This is technical repair, not
something the operator must design. The author agrees, records it and stops at the
predeclared one-repair limit. D1 (empty delivery cart), D2 (no available successor),
D3 (shared-fleet admission) and the proposed nearest-time rule remain visible product
choices. The final message adds an honest note about F3 after the reviewed draft;
it does not silently claim only product decisions remain.

The coordinator also records two limitations not closed by that review:

- The approval names existing component groups and describes the new intent/result
  conceptually, but omits the proposed shared `Public::SlotSelectionPreview` owner
  and the names `slot_intent` / `slot_selection`. Thus the native R5 pass is not proof
  that the requested named component/interface overview is fully satisfied. The
  plan is more explicit than the operator-facing text.
- T4's error classification lists pickup full/unavailable and delivery
  expired/window-unavailable, excludes other errors, yet broadly promises recovery
  after hold failures. `LockedDelivery#hold_delivery!` propagates the hold's code;
  `DeliveryCapacity.unavailable` uses `transport_unavailable`, and the existing
  concurrent own-driver test accepts that code (`checkout_spec.rb:2883–2886`). The
  proposal does not settle which such transport refusals represent loss of the
  selected window and need recovery. This is an unresolved producer/classification
  contract, not evidence that every transport error should be remapped. No runtime
  failure was reproduced; no application tests were authorized.

### Decision and limits

**The predeclared full-proposal promotion gate did not pass.** No extra repair,
new reviewer, new preparation or instruction tuning followed the result. The
experiment supports reduced instruction volume, detection of the five historical
gaps, and better scope reconciliation on this one case. It does not establish a
complete proposal, reliable preparation or superiority due to length alone.

The operator's current deliverable is an installable lean comparison variant.
Retaining that variant in a local experimental commit allows the documented
commit-pinned installer to copy it without falsely labelling dirty files as HEAD.
This is a deviation from the pre-run intention to commit only after the full gate
passed: the commit retains an experiment, not a validated replacement. The failed
gate and remaining gaps are not waived or relabelled as product questions. No
merge, push, PR or application installation is performed.

A new Cursor run can compare provider behavior, but is not necessary to rediscover
these known gaps and must not be advertised as a guaranteed successful proposal.
The original request is retained separately for an uncontaminated fresh input.


## Output size

| Artifact | Baseline | Lean |
| --- | --- | --- |
| FEATURE.md | 1295 words | 1058 words |
| IMPLEMENTATION.md | 2528 words | 2902 words |
| PROGRESS.md | 1419 words | 596 words |
| FINAL.md | 415 words | 557 words |

The output counts describe the whole retained files, including metadata/history.
They are not a score for quality. Both final messages are below the predeclared
600-word target; shorter instructions did not make every output shorter.

## Verification

`python3 -B tests/validate_blueprint.py` passed: 13 Markdown files, 49 local links.
`python3 -B tests/test_check_package.py` passed all six tests. `git diff --check`,
manual instruction diff review, and trailing-whitespace checks of all new fixtures
passed. The saved baseline patch reconstructs the exact pre-simplification bytes.
Source instruction hashes still match the candidate used in the trials. All three
batch templates and the blueprint outside Prepare match baseline byte for byte.

The auxiliary skill-creator validator could not start because PyYAML is unavailable;
no dependency was installed. The unchanged required skill frontmatter was compared
directly. This is not a claim that the auxiliary validator passed.

All 2374 tracked/nonignored application file hashes, Git status and HEAD match the
snapshot taken before this comparison. No real batch or installed package was
changed. No application tests, full delivery, CI, push, PR, merge or deployment ran.
Native discovery and a fresh prepare in Cursor remain untested for this candidate.
Structural/package checks do not change the failed behavioral gate above.
