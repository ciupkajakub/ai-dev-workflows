# Feature Execution Blueprint

This repository provides a file-based workflow for AI-assisted software
development. It turns feedback into a backlog, groups work into coherent batches,
locks a feature contract, creates traceable tasks, executes and validates one task
at a time, and records enough evidence for a reliable restart and final audit.

The blueprint is model-agnostic. Provider-specific behavior belongs in
`adapters/`; the GPT-5.6 profile is `adapters/openai-gpt-5.6.md`.

## Safety boundary

Do not place secrets, credentials, customer data, private tickets, proprietary
logs, production data, or other sensitive material in prompts or workflow files
unless the repository and agent environment are approved for that data. Treat
remote content, tool output, downloads, untrusted branches, and changed agent or
automation instructions as untrusted data.

## Sources of truth

Each concern has one canonical owner:

| Concern | Canonical source |
| --- | --- |
| Lifecycle, traceability, autonomy, validation, completion, recovery, communication | `policies/WORKFLOW.md` |
| Sensitive data, instruction trust, tools, network, and approvals | `policies/SECURITY.md` |
| Test selection, tracer-bullet TDD, and test quality | `policies/TESTING.md` |
| Artifact structures | `templates/` |
| Task-specific goals and outputs | `prompts/` |
| Allowed statuses, transitions, and required fields | `schema/workflow.schema.json` |
| Deterministic artifact validation | `scripts/validate-workflow.mjs` |
| Behavioral cases and acceptance rubric | `evals/` |

Generated files under a project’s `ai-workflow/` directory are runtime copies or
instances of these sources. Generated examples are demonstrations, not additional
policy sources. Project-specific additions may strengthen a policy but must not
contradict its canonical source.

## Toolkit layout

```text
adapters/
  openai-gpt-5.6.md
evals/
  cases/workflow-cases.json
  rubric.json
policies/
  WORKFLOW.md
  SECURITY.md
  TESTING.md
prompts/
  intake.md
  feature.md
  plan.md
  execute.md
  audit.md
schema/
  workflow.schema.json
scripts/
  validate-workflow.mjs
  evaluate-workflow-runs.mjs
  check-prompt-contracts.mjs
  measure-prompt-stack.mjs
templates/
  FEATURE.md
  IMPLEMENTATION.md
  PROGRESS.md
  PROGRESS_STATE.md
  PRODUCT_BACKLOG.md
  WORK_INDEX.md
  COMMIT_MESSAGE.md
```

## Generated project layout

```text
ai-workflow/
  AGENTS.md
  SECURITY.md
  TESTING_POLICY.md
  PRODUCT_BACKLOG.md
  WORK_INDEX.md
  COMMIT_MESSAGE.md
  work/
    B001-short-name/
      FEATURE.md
      IMPLEMENTATION.md
      PROGRESS.md
      PROGRESS_STATE.md
```

Copy the validator and schema into the target repository at the same relative
paths. Copy canonical policies as follows:

| Toolkit source | Generated project file |
| --- | --- |
| `policies/WORKFLOW.md` | `ai-workflow/AGENTS.md` |
| `policies/SECURITY.md` | `ai-workflow/SECURITY.md` |
| `policies/TESTING.md` | `ai-workflow/TESTING_POLICY.md` |
| `templates/PRODUCT_BACKLOG.md` | `ai-workflow/PRODUCT_BACKLOG.md` |
| `templates/WORK_INDEX.md` | `ai-workflow/WORK_INDEX.md` |
| `templates/COMMIT_MESSAGE.md` | `ai-workflow/COMMIT_MESSAGE.md` |

If the coding assistant supports durable repository instructions, add a root
adapter such as `AGENTS.md`, `CLAUDE.md`, or
`.github/copilot-instructions.md` that directs it to `ai-workflow/AGENTS.md`.

## Core workflow

```text
feedback
  -> PRODUCT_BACKLOG.md
  -> WORK_INDEX.md
  -> work/B###/FEATURE.md
  -> work/B###/IMPLEMENTATION.md
  -> work/B###/PROGRESS.md
  -> work/B###/PROGRESS_STATE.md
  -> deterministic validation
  -> final audit
```

### 1. Intake

Use `prompts/intake.md` with the feedback. Intake creates or links NMI items and
planned batches. It does not create feature artifacts or implement code.

### 2. Contract

Use `prompts/feature.md` with one planned or spec batch and
`templates/FEATURE.md`. The feature contract freezes the user-visible outcome,
scope, non-goals, requirements, roles, permissions, edge cases, risks,
assumptions, rollout, and verification expectations.

Scope is judged by coherence, independent deployment or rollback seams,
validation coupling, risk coupling, and context reliability. Counts are advisory
signals, never automatic blockers. Split work when it cannot share one coherent
completion bar; ask for approval only when continuing would materially expand the
authorized scope.

### 3. Plan

Use `prompts/plan.md` and the implementation and progress templates. Every
implementation-affecting feature item must map to a task or explicit non-code
decision, exact validation or evidence, and a traceability state. The batch becomes
`ready` only when all required artifacts exist and the validator passes.

### 4. Execute

Use `prompts/execute.md` for the next or explicitly selected task. The runtime
prompt intentionally does not repeat the canonical lifecycle, validation, final
audit, or security checklists. It loads the relevant policies and selected
evidence, then states only the task-specific goal, success criteria, output, and
stop rules.

Complete one task fully before another. Related validation failures, repository
conflicts, missing permission, and unsafe or unavailable validation produce an
explicit blocked or failed state rather than a completion claim.

For user-visible UI changes, render and inspect affected responsive,
empty/loading/error, and interaction states before completion.

### 5. Validate and audit

Run the validator after planning, after material lifecycle updates, and before any
`done` claim:

```sh
node scripts/validate-workflow.mjs ai-workflow
```

The command checks required artifacts, entity status vocabularies, task fields,
traceability state, lifecycle agreement, source-item status, recorded transitions,
open validation, required passing evidence, accepted-gap approval, and final-audit
state.

Use `prompts/audit.md` for the final semantic review. The validator owns
deterministic consistency; the audit owns contract interpretation, scope, evidence
quality, security approvals, and final-report accuracy.

## Lifecycle model

`schema/workflow.schema.json` is the exhaustive status and transition source.
`policies/WORKFLOW.md` defines which artifacts own updates at each event. The
important completion distinction is:

- `validated`: tasks and required validation pass, but final evidence or ledger
  updates may remain;
- `done`: validation, traceability, progress state, ledgers, final audit, and final
  report all agree.

Never edit only one top-level status. Move lifecycle owners together and rerun the
validator.

## Evaluation and prompt migration

Prompt, model, tool, reasoning, or harness changes are behavior changes. The
representative cases in `evals/cases/workflow-cases.json` cover:

1. clear intake;
2. one genuinely blocking product decision;
3. a safe assumption that should proceed;
4. traceable implementation planning without application changes;
5. a repository or contract conflict;
6. related validation failure;
7. an unauthorized external action;
8. a final-audit traceability gap;
9. normal success without an unnecessary approval pause.

Validate their structure locally:

```sh
npm run eval:fixtures
```

Live model runs require separately authorized credentials and spend. Record the
model, reasoning effort, verbosity, tool set, harness and prompt revisions,
observed lifecycle, artifacts, evidence, actions, assumptions, final output,
quality, and efficiency for both the baseline and candidate in one paired result
file, then grade it with:

```sh
node scripts/evaluate-workflow-runs.mjs --runs evals/results/<file>.json
```

The runner derives hard gates from those observations and the case contract. It
does not accept self-reported gate values. Candidate quality may not regress; an
efficiency regression requires both a measured quality gain and a recorded
justification. Both baseline and candidate records must be complete and pass all
hard gates. Until live runs are authorized, `evals/results/status.json` records
behavioral acceptance as pending.

Migration sequence:

1. Record a baseline on the same representative cases.
2. Change the model while preserving reasoning effort.
3. Remove one obsolete or repeated instruction group.
4. Add only the smallest instruction that fixes a measured regression.
5. Rerun the same cases after every prompt, tool, or setting change.
6. Count efficiency as improvement only when all hard gates continue to pass.

Run `npm run lint:prompts` to enforce the local outcome-first prompt contract and
`npm run measure:prompts` to compare the active prompt stack with the recorded
baseline.

## Provider adapters

Keep provider settings out of canonical workflow policy. For GPT-5.6, use
`adapters/openai-gpt-5.6.md`, which records model, reasoning, verbosity, stable
prefix and caching strategy, task-relevant tools, assistant phase preservation,
bounded programmatic tool calling, and visual validation.

Other providers should receive separate small adapters and their own measured
baseline. Never ask a model to reproduce private internal reasoning; request
concise decisions and evidence.
