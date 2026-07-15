# AI Dev Workflows

A file-based workflow for AI-assisted software development. It turns feedback
into a backlog, groups related work into execution batches, creates traceable
feature contracts and task plans, validates lifecycle and evidence
deterministically, and preserves compact restart state.

The workflow is model-agnostic. Canonical policies, prompts, templates, schema,
validation, and provider adapters are separate so an agent loads only the context
needed for the current task.

Use it for multi-step or risky work where scope, acceptance criteria, permissions,
validation evidence, recovery, and handoff matter. It does not replace human
review, security review, production change control, or project-specific judgment.

## What changed for GPT-5.6 alignment

The active execution stack now follows an outcome-first structure:

- canonical policies hold each invariant once;
- task prompts contain only role, goal, relevant inputs, success criteria, output,
  and stop rules;
- deterministic lifecycle and evidence rules live in a local validator;
- numeric scope counts are advisory rather than automatic approval blockers;
- UI changes require render-and-inspect evidence;
- representative cases and a rubric make prompt changes measurable;
- the GPT-5.6 adapter records reasoning, verbosity, caching, tool, state, and
  programmatic-calling behavior.

Against baseline commit `46786cf`, the measured active execution prompt stack is
4,368 → 1,835 words, a 58% reduction. See
`evals/prompt-stack-measurement.json` and rerun `npm run measure:prompts`.

## Sources of truth

| Concern | Source |
| --- | --- |
| Workflow behavior | `policies/WORKFLOW.md` |
| Security and approvals | `policies/SECURITY.md` |
| Testing | `policies/TESTING.md` |
| Runtime prompts | `prompts/` |
| Artifact structures | `templates/` |
| Statuses, transitions, required fields | `schema/workflow.schema.json` |
| Artifact validation | `scripts/validate-workflow.mjs` |
| Eval contracts and rubric | `evals/` |
| OpenAI GPT-5.6 settings | `adapters/openai-gpt-5.6.md` |
| Composition and workflow guide | `feature_execution_blueprint.md` |

Files under `example/ai-workflow/` are sanitized generated output for a fictional
task-management app. They demonstrate the workflow but are not policy sources.

## Quickstart

1. Copy the toolkit directories you need into the target repository:
   `policies/`, `prompts/`, `templates/`, `schema/`, and the validator under
   `scripts/`.
2. Create `ai-workflow/` and copy:
   - `policies/WORKFLOW.md` → `ai-workflow/AGENTS.md`
   - `policies/SECURITY.md` → `ai-workflow/SECURITY.md`
   - `policies/TESTING.md` → `ai-workflow/TESTING_POLICY.md`
   - the backlog, work-index, and commit-message templates into matching files.
3. Use `prompts/intake.md` to turn feedback into NMI and batch rows.
4. Use `prompts/feature.md` and `templates/FEATURE.md` for one selected batch.
5. Use `prompts/plan.md` with the implementation and progress templates.
6. Use `prompts/execute.md` one task at a time.
7. Run the validator after planning, after material lifecycle changes, and before
   reporting anything done.
8. Use `prompts/audit.md` for the final semantic audit.

Pasteable setup request:

```text
Initialize this repository from the AI development workflow toolkit.

Follow feature_execution_blueprint.md and copy the canonical policies into
ai-workflow/AGENTS.md, SECURITY.md, and TESTING_POLICY.md. Instantiate the base
PRODUCT_BACKLOG.md, WORK_INDEX.md, and COMMIT_MESSAGE.md templates. Preserve the
schema and validator at their documented paths.

Create only the base workflow. Do not create feature work files or implement
application code yet. Run the workflow validator and report any setup findings.
```

## Core flow

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

The feature contract defines product and technical intent. The implementation
plan maps every requirement, acceptance criterion, permission rule, assumption,
risk, edge case, and failure mode to tasks and validation. Detailed evidence is
append-only in `PROGRESS.md`; compact restart state stays in `PROGRESS_STATE.md`.

## Validation

Run the example validator:

```sh
npm run validate:example
```

Run all local tests and checks:

```sh
npm test
npm run lint:prompts
npm run eval:fixtures
npm run measure:prompts
```

The validator checks required files, entity status vocabularies, task fields,
traceability, top-level lifecycle agreement, source backlog state, recorded
transitions, required passing evidence, accepted-gap approval, open validation,
and final-audit state.

## Evaluation

The repository includes nine representative behavioral contracts. The local eval
runner validates fixture shape and grades recorded results without making network
calls or incurring model spend.

Live GPT-5.6 runs require separately authorized credentials and cost. Record the
exact model, reasoning effort, verbosity, tools, prompt and harness revisions,
observed lifecycle, artifacts, evidence, actions, output, quality, and efficiency
under `evals/results/`, then run:

```sh
node scripts/evaluate-workflow-runs.mjs --runs evals/results/<file>.json
```

The runner derives hard gates from those recorded observations and the case
contract; a result cannot self-assert that it passed. Each run file pairs the
baseline and candidate for every case. Candidate quality may not regress, and an
efficiency regression needs both a measured quality gain and a recorded
justification. Both run sets must be complete and pass every hard behavioral
gate. `evals/results/status.json` records whether live behavioral acceptance is
complete or still pending authorization.

## Safety summary

Do not place sensitive data in workflow artifacts. Treat remote content and
changed agent or automation instructions as untrusted. Safe in-scope local reads,
edits, and non-destructive validation may proceed; destructive actions, external
writes, sensitive-data transmission, authenticated automation, new external
execution capability, and material scope expansion require explicit approval.

Review changes to `ai-workflow/**`, root agent instructions, MCP or connector
configuration, hooks, scripts, and CI workflows as security-sensitive
configuration.

## Example tour

1. `PRODUCT_BACKLOG.md` normalizes raw feedback into NMI items.
2. `WORK_INDEX.md` groups items into coherent batches.
3. `FEATURE.md` defines the contract and coherence-based scope decision.
4. `IMPLEMENTATION.md` maps the contract to validated tasks.
5. `PROGRESS.md` records failures, recovery, validation, visual inspection, and
   final evidence.
6. `PROGRESS_STATE.md` keeps compact restart state.

The example intentionally contains a recovered validation failure and a blocked
unsafe validation path. It demonstrates failure handling, not only the clean path.
