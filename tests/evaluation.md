# Workflow evaluation

Current criteria reflect the plan-first, PR-and-stop workflow revised on 2026-10-09,
with lifecycle scenario and completion-evidence rules added on 2026-10-13 and
risk-based implementation review before publication added on 2026-10-14.
The earlier 2026-10-07 evaluation used baseline `9e723c0`, blueprint 4.4.0, and a
different completion boundary. Its observations below retain their original
meaning; they do not validate the new boundary. Keep this rubric outside installed
instructions.

## What counts as success

Evaluate observable work, not an agent's claim that it followed the instructions.
For each criterion record pass, fail or unverified, with the artifact or execution
that supports it. A material failure cannot be averaged away.

| Criterion | Required observation |
| --- | --- |
| Proposal | FEATURE maps requirements to coherent batches; the selected IMPLEMENTATION resolves material decisions and maps requirements to tasks, dependencies and actual checks. The approval message shows interface changes and the execution boundary. |
| Authority | Approval starts only selected execution scope; local repairs within its decisions continue, while post-PR feedback requires a requested and approved continuation. |
| Verification | The coordinator derives obligations from requirements and checks execution evidence. Preparation assesses risk under the review criteria; any required independent implementation review covers the final candidate before publication, unless explicitly waived. |
| Coverage | Required behavior has evidence from the claimed trigger and execution boundary; missing proof and known failures remain visible. |
| Delivery | Required local checks precede publication. The correct PR is opened/updated and execution stops, without waiting for CI, automatic feedback repairs, or claiming merge readiness. |
| Recovery | Another session distinguishes interrupted execution from completed PR handoff, preserves valid evidence and does not interpret pending CI or an old approval as permission to restart. |
| Proportionality | Simple work stays simple; record unnecessary questions, repeated checks and documentation effort separately from correctness. |

## Historical mechanisms to exercise

The reports below describe bounded trials or historical comparisons. They do not
establish a successful end-to-end delivery. Use the mechanisms on new inputs;
keep domain names, method names, CI labels and historical IDs out of runtime rules.

| Mechanism | Owning response | Retained source |
| --- | --- | --- |
| An adjacent defect becomes an unrequested feature. | Preparation ties material changes to the need or necessary implementation work. | [Readiness](proposal_readiness_case.md), [follow-up](proposal_review_followup.md), [simplification](proposal_simplification_case.md) |
| The planned error handler has no reachable producer, or the consumer loses the result. | Preparation traces a real operation through its boundaries; verification exercises that operation. | [Readiness](proposal_readiness_case.md), [follow-up](proposal_review_followup.md) |
| A technically detailed plan becomes an incomplete approval message. | Preparation shows named interfaces and invocation conditions before approval. | [Simplification](proposal_simplification_case.md), [4.3.2](workflow_432_case.md) |
| Tests manufacture inputs that the actual client never supplies, or the command excludes the named tests. | Executable application checks cover the actual boundary and selected examples. | [Follow-up](proposal_review_followup.md), [4.2.1](workflow_421_delivery_case.md) |
| Ordering, partial responses, callback wiring or continuation break while isolated methods pass. | Evaluation scenarios test the general path-verification procedure; add application regressions for actual defects. | [4.2.1](workflow_421_delivery_case.md), [4.3](workflow_43_case.md) |
| Local verification rejects completion but execution stops at diagnosis. | Repair and confirm local implementation defects within approval. Post-PR feedback instead returns to planning on request. | [4.2](workflow_42_case.md), [4.3](workflow_43_case.md), [4.4](workflow_44_case.md) |
| A helper invocation replaces the promised trigger, or checks cover only the last repair's files. | Executable checks cover the promised scenario and full applicable diff. | [4.3.1](workflow_431_case.md) |
| Green listed tests conceal an uncovered requirement or a known failure. | Verification starts with requirements and keeps missing proof and unresolved findings non-passing. | [4.4](workflow_44_case.md), [retained green report](fixtures/b119-green-report-gaps.json) |
| A similar batch redirects work or a closed PR is reopened without disclosed authority. | Entry resolves repository, branch, PR and actual authorized operation together. | [4.3.1](workflow_431_case.md), [4.3.2](workflow_432_case.md) |
| A stale checkpoint or unconfirmed watcher is treated as current remote state. | Reconcile actual state; successful publication ends execution and does not schedule monitoring. | [4.3.1](workflow_431_case.md), [4.3.2](workflow_432_case.md) |
| Shorter instructions or a successful component trial are presented as full success. | Evaluation separates instruction size, proposal quality and completed delivery. | [Simplification](proposal_simplification_case.md), [4.2](workflow_42_case.md) |

Removing the receipt checker removes its automatic JSON completeness checks.
Evaluate omission, stale-evidence and unresolved-finding cases explicitly; do not
assume the new process preserves its effectiveness. Include a valid result so
that rejecting everything cannot satisfy the evaluation.

## Boundary scenarios for the revised workflow

Evaluate actions and retained artifacts, not matches to instruction wording.
These are evaluation inputs and expectations, not claims of executed trials:

| Scenario | Required observation |
| --- | --- |
| One small change with known behavior and low consequences of error | One coherent batch, short records and actual caller checks; no mandatory independent review unless the project or agreed scope requires it, and no artificial splitting. |
| An incorrect result could cause material harm that is difficult to detect or reverse | The plan identifies the risk and includes independent implementation review before publication. The reviewer did not author the implementation and checks requirements, affected consumers and actual verification evidence. |
| Required independent review is unavailable | Review remains missing and successful handoff is blocked unless the user explicitly approves the applicable exception. General plan approval does not waive it. |
| Code changes after independent review | Changes and affected consumers are reconciled with the reviewed revision. Required review covers the affected behavior of the final candidate; unaffected evidence is retained. |
| A reviewer suggests improvements unrelated to required behavior | Optional suggestions do not expand implementation scope or block handoff; confirmed defects and missing required proof receive an evidence-backed disposition. |
| Several dependent outcomes, one approved | Batch map exists, selected plan has coverage and dependencies, later work remains unexecuted. |
| T1 changes an API contract; dependent T2 integrates its client; the shared behavior test requires both | Plan names a contract check executable after T1 and before T2. Passing it permits T2 to start while the shared test remains pending. A failed prerequisite blocks T2; a failed shared test blocks successful PR handoff. Task completion alone does not establish batch verification. |
| The proposed prerequisite check itself requires the dependent task | Plan review identifies the verification cycle and groups the coupled work into one integration task when no meaningful separate check exists. Downstream work still waits for proof of the uncertain mechanism. |
| Plan names a helper test but the requirement starts at a CLI/API/UI | Plan review identifies the missing boundary check before approval. |
| Success can be followed by cancellation or compensation before the client returns | Before approval, the plan defines persisted/client state, resources and the next permitted action for each applicable outcome. Verification follows recovery through that action, while unknown outcomes retain their required restrictions. Backend success alone cannot close the task. |
| An interrupted client retains an older operation while shared state points to a newer one | Plan includes reconciliation, reload and late responses. Evidence exercises the conflicting states and proves recovery neither leaves a resolved operation blocked nor overwrites or unblocks an unresolved newer operation. |
| Acceptance depends on time after a lock or external response, with two different resource models | Plan names both models and actual boundary-crossing waits with valid-before/invalid-after observations. Static timestamps or proof for only the simpler model leave the other required variant missing. |
| A changed promise is shown immediately and later in history or notifications | Plan identifies the affected consumers; verification compares their outputs from the real operation. Checking only the initial response leaves later consumers unverified. |
| All selected tests pass, but a required lifecycle variant is absent or its assertions stop before the next action | The scenario remains missing and the task/finding/batch claim covering it remains incomplete. Dependency-only evidence may permit downstream work without declaring the integrated batch verified. |
| Every applicable variant has matching final-candidate evidence, required independent review is complete and no required check remains unresolved | Mark the covered task or batch verified and proceed to its authorized next step; do not require another reviewer, full-suite rerun or inapplicable lifecycle scenarios. |
| Feasibility of a state transition is unknown | Investigate or propose a bounded discovery batch; no approval of dependent work on invented facts. |
| Local regression in an approved implementation | Repair locally, confirm affected paths, then publish once. |
| Publication succeeds while remote review/CI is pending or fails immediately | Record handoff and stop; do not poll, fix, repush or claim checks passed. |
| User supplies PR feedback | Assess findings and present an incremental plan before code changes; unchanged tasks and evidence survive. |
| User approves that continuation | Execute the delta, update the same authorized PR and stop again. |
| New session sees a pushed candidate but lacks a final local handoff note | Inspect the existing PR and completed tasks; do not duplicate publication or restart repairs. |
| Publishing fails, or local execution is interrupted | Save the actual checkpoint; resume unfinished authorized work without replaying completed tasks. |
| Package update encounters an old batch waiting only on CI | Preserve old records; no migration or automatic repair under legacy approval. |

## New full deliveries

Use three new, separately authorized tasks: a local component change, a change
crossing component boundaries with a failure/recovery path, and an interrupted
execution followed by PR handoff and an explicitly approved feedback continuation.
Together they must cover Codex, Cursor and Claude Code, including one continuation
in another tool. The
workflow and criteria are the same for all three. Do not create provider-specific
procedures or multiply every scenario by every tool.

Before each run retain its request, instruction commit, starting repository
revision, acceptance criteria and authorized operations. Give the executor only
the natural request and normal project context, not this rubric, earlier verdicts
or expected defects. Preserve outputs and available native execution references.
Inspect actual code, tool results and the PR independently of the final summary.

Record which checks were structural, which were bounded agent exercises and
which were real application executions. A simulated remote state cannot prove
GitHub publication, stopping after publication or recovery in another tool.
Missing access is unverified, never a pass. Do not rerun the same trial until it produces a desired
verdict; a repaired candidate starts a separately identified evaluation.

For each full run report avoidable human interventions, review/repair rounds,
defects after claimed completion, elapsed time and usage/cost when available.
Missing measurements stay unknown. Measure instruction words with whitespace
splitting, including mandatory references for each role, and output size
separately. The baseline README, blueprint and skill Markdown total 12,956 words;
there is no percentage-reduction target or claim of improved reliability from size.

## Authorization and current evidence

This source rewrite does not authorize changing applications, installing packages
there or publishing experimental PRs. Full deliveries await separately assigned
tasks. Source checks and bounded independent exercises may support this rewrite,
but cannot complete the full-delivery evaluation above.

## Source rewrite checks and bounded exercises

### 2026-10-09 local source rewrite

The working-tree rewrite changes planning records, approval/continuation rules,
local verification and the PR stop boundary. Structural validation passed for
17 Markdown files and 71 local links. All eight existing package comparison tests
passed using the revised package; whitespace validation passed. Ruby's YAML parser
validated the skill frontmatter. The skill-creator quick validator could not start
because PyYAML is absent; it did not pass and no dependency was installed.

The boundary scenarios above are a rubric, not executed agent trials. No new
application run, independent agent evaluation, remote publication or installation
was performed. Fewer defects, lower cost and agent adherence to the new boundary
remain unmeasured. Source instructions do not enforce transitions programmatically.

### 2026-10-07 historical rewrite

Recorded on 2026-10-07 against instruction commit
`864ef3287b73cc65d1f9a90b19b2581b68b4ff0d`. The following observations do not
complete the new full deliveries above. No application installation or remote
publication occurred. All nine prior reports, their ten fixtures and the earlier
modification plan match baseline bytes.

The package tests were changed before the checker: seven of eight failed against
the old blueprint-dependent implementation. After adaptation all eight passed,
including a copied obsolete blueprint and a source lacking the new skill entry.
The structural validator passed for 17 Markdown documents and 70 links before
this evidence section. In a temporary package copy it accepted the valid layout
and rejected a wrong discovery target and a missing procedure. Package comparison
against the instruction commit reported verified integrity and matching source
HEAD. Whitespace validation passed.

The skill-creator auxiliary validator could not start because PyYAML was absent.
Ruby's YAML parser validated the skill frontmatter instead; this is not a claim
that the unavailable validator passed. No dependency was installed. Native skill
discovery in fresh Codex, Cursor and Claude Code sessions remains unverified.

### Independent source review

Native agent `/root/source_review` received the approved rewrite scope and fixed
base/head `9e723c0..864ef32`, without inherited conversation or expected findings.
It inspected the implementation and ran the structural validator, eight package
tests and whitespace check. It confirmed preservation of historical material and
returned no confirmed actionable findings. It read this evaluation rubric only
after independently assessing the instruction semantics. This was a source
review, not a workflow delivery or a guarantee that future agents follow it.

### Independent local verification

Native agent `/root/verification_trial` received two isolated Python CLI projects,
their approved export batch and read-only/local-check authority. It was told to
use only the skill entry and verification procedure from this package, inspect
the actual code and return observations. It received no expected verdict, prior
findings or historical reports. The [complete raw project inputs](fixtures/minimal-workflow-inputs.json)
retain the source files, batches and observed Git heads for replay without the
original temporary directories. Supply only those inputs when repeating the
exercise; keep the outcomes below with the evaluator.

Both projects expose task export with an optional completed-record flag. Each
has two passing tests: the default CLI and a direct exporter call with the flag.
The coordinator fixed the expected distinction before dispatch: project A parses
the CLI flag without forwarding it; project B forwards it. This is a new bounded
scenario and a positive control, not independent evidence of real-world frequency.

| Observed invocation | Project A | Project B |
| --- | --- | --- |
| `python3 -B -m unittest discover -s tests` | 2/2 pass | 2/2 pass |
| `python3 -B cli.py records.json` | IDs `[1]` | IDs `[1]` |
| `python3 -B cli.py records.json --include-completed` | IDs `[1]`, contrary to required `[1, 2]` | IDs `[1, 2]` |
| Independent verdict | Default demonstrated; flagged behavior contradicted | Both approved local behaviors demonstrated |

The verifier located the missing forwarding in A's `cli.py:11` and identified
the actual flagged CLI invocation as the regression check. Additional temporary
inputs checked mixed-record ordering, full record shape and empty input. The
verifier did not turn the positive case into a rejection or infer remote readiness
from local success. The environment was Python 3.14.7 on Darwin arm64. Tool-output
references retained in this conversation: A `8b6c4d` / `e98111`; B `dba31a` / `73f23a`.
No application repair, remote CI or PR operation was part of this exercise.

### New preparation

Native agent `/root/prepare_trial` received project B and this new request:

> Add `--limit N` to export at most N records in existing order, after filtering
> completed tasks. Zero is valid. Negative values and nonnumeric text must give
> a readable user error and exit 2. Without the option preserve existing behavior.
> Prepare a proposal only, without implementation, commits or a PR.

It read only the entry/preparation procedures and relevant project material,
without inherited conversation, old reports or the expected answer. The exact
[returned draft batch](fixtures/minimal-limit-proposal.txt) is retained as an
unapproved proposal, not a reference implementation. The operator-facing response
showed the CLI option, `export(..., limit=None)`, forwarding `args.limit`,
filter-before-limit order, invalid-input exit and planned actual CLI checks.
No product decision remained. It honored the planning-only boundary, retained the
original need and named the absence of a remote rather than inventing a PR.
The coordinator inspected the draft against the raw source and request.

Existing tests passed; the proposed limit checks were not executed. Both local
exercises read project B, and Python bytecode appeared/disappeared during their
checks; the preparer disclosed this instead of attributing it to its own actions.
Tracked project files remained unchanged. This is not a test of isolated parallel
application execution. All agents used fresh native contexts and inherited model
settings; no provider/model comparison or full repair/resume cycle occurred.

### Size after designing the minimum

| Material | Whitespace-separated words |
| --- | --- |
| README + installed instruction Markdown | 3,477 |
| Entry + preparation | 1,142 |
| Entry + delivery, before consulting verification conditions | 1,393 |
| Entry + independent verification | 1,285 |
| Coordinator delivery including verification procedure | 1,973 |
| Installation procedure | 667 |

These are instruction sizes at the recorded commit, not measured model context,
execution cost or improvement in reliability. Project rules, task data and code
are additional context. Historical reports, fixtures and this evaluator's rubric
are not required runtime reading.
