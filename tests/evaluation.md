# Workflow evaluation

These criteria were fixed before implementing the single-skill workflow on
2026-10-07. Baseline: `9e723c0`, blueprint 4.4.0. Keep this material outside the
installed instructions. Historical reports retain their original verdicts.

## What counts as success

Evaluate observable work, not an agent's claim that it followed the instructions.
For each criterion record pass, fail or unverified, with the artifact or execution
that supports it. A material failure cannot be averaged away.

| Criterion | Required observation |
| --- | --- |
| Proposal | Preserves the original need, resolves material decisions and shows the actual interface changes in the approval message. |
| Authority | One approval starts the presented delivery scope; ordinary repairs continue without another approval, while new scope or unavailable authority is surfaced. |
| Verification | A separate non-implementing agent/session derives obligations from approved behavior and examines code and executed proof. |
| Coverage | Required behavior has evidence from the claimed trigger and execution boundary; missing proof and known failures remain visible. |
| Delivery | In-scope findings lead to repair and confirmation; the correct PR reaches readiness with required checks complete on the relevant revision. |
| Recovery | Another session can use the batch, checkout and GitHub to continue without importing unrelated approval or replaying finished work. |
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
| Review rejects completion but delivery stops at diagnosis. | The coordinator continues the repair and verification loop. | [4.2](workflow_42_case.md), [4.3](workflow_43_case.md), [4.4](workflow_44_case.md) |
| A helper invocation replaces the promised trigger, or checks cover only the last repair's files. | Executable checks cover the promised scenario and full applicable diff. | [4.3.1](workflow_431_case.md) |
| Green listed tests conceal an uncovered requirement or a known failure. | Verification starts with requirements and keeps missing proof and unresolved findings non-passing. | [4.4](workflow_44_case.md), [retained green report](fixtures/b119-green-report-gaps.json) |
| A similar batch redirects work or a closed PR is reopened without disclosed authority. | Entry resolves repository, branch, PR and actual authorized operation together. | [4.3.1](workflow_431_case.md), [4.3.2](workflow_432_case.md) |
| A stale checkpoint or unconfirmed watcher is treated as current remote state. | Delivery reconciles the batch with GitHub and confirms native continuation. | [4.3.1](workflow_431_case.md), [4.3.2](workflow_432_case.md) |
| Shorter instructions or a successful component trial are presented as full success. | Evaluation separates instruction size, proposal quality and completed delivery. | [Simplification](proposal_simplification_case.md), [4.2](workflow_42_case.md) |

Removing the receipt checker removes its automatic JSON completeness checks.
Evaluate omission, stale-evidence and unresolved-finding cases explicitly; do not
assume the new process preserves its effectiveness. Include a valid result so
that rejecting everything cannot satisfy the evaluation.

## New full deliveries

Use three new, separately authorized tasks: a local component change, a change
crossing component boundaries with a failure/recovery path, and an interrupted
delivery resumed through remaining checks or feedback. Together they must cover
Codex, Cursor and Claude Code, including one continuation in another tool. The
workflow and criteria are the same for all three. Do not create provider-specific
procedures or multiply every scenario by every tool.

Before each run retain its request, instruction commit, starting repository
revision, acceptance criteria and authorized operations. Give the executor only
the natural request and normal project context, not this rubric, earlier verdicts
or expected defects. Preserve outputs and available native execution references.
Inspect actual code, tool results and the PR independently of the final summary.

Record which checks were structural, which were bounded agent exercises and
which were real application executions. A simulated remote state cannot prove
GitHub publication, CI waiting or recovery in another tool. Missing access is
unverified, never a pass. Do not rerun the same trial until it produces a desired
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
