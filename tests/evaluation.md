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

## Source rewrite checks and bounded exercises

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
