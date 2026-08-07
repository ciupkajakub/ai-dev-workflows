# AI Dev Workflows

A small file-based workflow for AI-assisted software development. It turns raw feedback into a backlog, groups related work into execution batches, creates feature contracts and task plans, then records validation evidence and compact restart state.

The repository is a store for one self-contained reusable blueprint.
`feature_execution_blueprint.md` is the complete operational source; files under
`example/ai-workflow/` are generated sample output that demonstrates how the
blueprint should behave in practice. No separate toolkit files are required to
initialize or run the workflow.

Use it when a change is too large or risky to keep only in chat memory: product feedback, multi-step features, cross-cutting backend/UI changes, migration work, or anything where acceptance criteria and verification evidence matter.

Do not use it as a replacement for human review, security review, production change control, or project-specific engineering judgment.

## 5-minute quickstart

1. Copy `feature_execution_blueprint.md` into your project or keep it open next to your project.
2. Ask your coding agent to run sections 2-7 of the blueprint to create the base `ai-workflow/` files.
3. Paste raw feedback into the prompt from section 8 to create backlog and batch entries.
4. Run section 9 to turn one selected batch into `FEATURE.md`.
5. Run section 10 to create `IMPLEMENTATION.md`, `PROGRESS.md`, and `PROGRESS_STATE.md`.
6. Use section 11 to start from the next task and continue autonomously through
   dependency-ready tasks plus repair-capable finalization. Use section 12 only
   when you intentionally want one named task.
7. Section 11 invokes section 13 automatically. You can also invoke section 13
   directly for repair-and-close, or explicitly request its audit-only mode.
8. Deliberately run section 14 before accepting changes to prompts, models, tools,
   or harness behavior. It is an evaluation runbook, not an automatic part of
   feature execution.

The numbered sections are a stable interface designed for short remote or mobile
commands. For example: `Use section 11 of feature_execution_blueprint.md for
batch B001 and execute it to a verified outcome.` The agent reads that section and the
generated artifacts it names; it needs no other toolkit source. Execution phases
still inspect and modify the target repository's application code as needed.

Section 12 remains the named-task variant of section 11, but delegates to the
same canonical runtime procedure instead of maintaining a duplicated prompt.
Existing commands such as `Use section 12 ... task T002` remain valid.

Pasteable setup prompt:

```text
Use feature_execution_blueprint.md to create the base ai-workflow files for this repository.

Run only sections 2-7.
Create:
- ai-workflow/AGENTS.md
- ai-workflow/SECURITY.md
- ai-workflow/TESTING_POLICY.md
- ai-workflow/PRODUCT_BACKLOG.md
- ai-workflow/WORK_INDEX.md
- ai-workflow/COMMIT_MESSAGE.md

Do not create feature work files yet.
Do not implement code.
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
```

The execution artifacts define entity-specific lifecycle gates. Backlog items,
batches, and tasks each have their own allowed statuses, including `spec`,
`ready`, `in_progress`, `failed_validation`, `validated`, `done`, `superseded`,
and `rolled_back` where appropriate. Treat validation gaps, related failing
tests, and unsafe tool access truthfully. An ordinary related failing check stays
active while an evidence-backed repair path is progressing; real validation,
permission, scope, and safety blockers remain explicit.

The workflow combines a downstream-consumer impact map with grouped traceability
closure. Every implementation-affecting contract item and changed shared seam
maps to an owner plus proof, blocker, or explicitly accepted gap without
duplicating the same evidence across hundreds of rows.

Before accepting a completed batch, the blueprint's finalizer runs declared
broader local checks, exercises the observable result, evaluates UI against its
visual rubric when applicable, and repairs related in-scope findings while
evidence shows progress. It checks lifecycle consistency, impact and traceability
closure, security approvals, and final-report accuracy before closing delivery.

## Outcome-driven task execution

Section 10 is the canonical source for the task execution policy copied into
generated `IMPLEMENTATION.md` files. Task boundaries follow coherent,
independently verifiable outcomes. Estimates are scheduling signals, not stop or
approval conditions. A ten-minute checkpoint produces a compact update and then
work continues. Hard bounds apply to individual commands, repeated no-progress
on the same root cause, and rerunning an unchanged check. Section 11 proceeds
across task boundaries and into finalization without requiring `Continue` or
`Fix` prompts.

Full suites, repo-wide build/lint/typecheck, full-history or repository security
scans, dependency audits, and CI commands cannot be task-scoped. This reduces
total batch time by running broad proof once instead of repeating it for each
task.

`IMPLEMENTATION.md` assigns every check to exactly one scope:

- `task`: focused checks run by section 11 or 12
- `batch`: broader local checks run once by section 13 after all tasks
- `ci`: external checks that local execution records but never launches

Loading a security policy, testing policy, skill, or reference does not add a
validation command. A task executor may propose broader proof for replanning, but
cannot invent or run it. After the last task, section 11 invokes section 13.
Section 13 runs each declared batch command once initially, reruns only failed
proof after a relevant repair, and closes feature delivery separately from
integration and release evidence. Pending CI blocks `release_ready`, not a
truthful feature-delivery claim, unless the feature contract explicitly requires
release readiness.

## Context strategy

The workflow keeps its single-file, numbered-section interface while loading
detail progressively:

- `ai-workflow/AGENTS.md` is a compact repo map, command reference, and router to
  the core workflow gates.
- A runtime turn starts from `PROGRESS_STATE.md`, one task, relevant contract
  items, and `AGENTS.md`.
- `SECURITY.md`, `TESTING_POLICY.md`, detailed progress, references, and skills
  load only when the selected phase or task needs them.
- `FEATURE.md` records the smallest useful references and applicable skills.
  `IMPLEMENTATION.md` routes each reference or skill only to the tasks where it
  contributes a decision or required evidence.

For example, a UI batch can route `apple-design` to contract design, UI
implementation, and visual review without loading it for backend tasks. A
conversion skill applies only when the batch defines a funnel stage, conversion
goal, baseline or explicit unknown, hypothesis, primary metric, and guardrails.
Experiments additionally need a sample-size method and duration.
Installed skills are not global requirements.

## Generated files

The blueprint is the source of truth. It contains prompts and templates for generating:

- `ai-workflow/AGENTS.md`
- `ai-workflow/SECURITY.md`
- `ai-workflow/TESTING_POLICY.md`
- `ai-workflow/PRODUCT_BACKLOG.md`
- `ai-workflow/WORK_INDEX.md`
- `ai-workflow/COMMIT_MESSAGE.md`
- `ai-workflow/work/B###/FEATURE.md`
- `ai-workflow/work/B###/IMPLEMENTATION.md`
- `ai-workflow/work/B###/PROGRESS.md`
- `ai-workflow/work/B###/PROGRESS_STATE.md`

Generated runtime artifacts record the exact blueprint source, declared
revision, workflow schema, and SHA-256 digest. This lets a run detect a stale
project copy while continuing from the newer canonical source without rewriting
historical evidence.

`ai-workflow/AGENTS.md` is generated by the blueprint and is read by the workflow
prompts. It intentionally stays compact and repo-specific rather than repeating
the full lifecycle, security, testing, and phase procedures. Agent-level
auto-loading is optional and project-specific. If you prefer it, add whatever
instruction adapter your assistant supports, such as a root `AGENTS.md`,
`CLAUDE.md`, or `.github/copilot-instructions.md` that points to
`ai-workflow/AGENTS.md`.

## Safety note

The blueprint-generated workflow files include the detailed security and permissions rules. At a high level, do not paste secrets, credentials, customer data, private tickets, proprietary logs, or production data into workflow files unless your repository and agent environment are approved for that data. Treat browser content, web pages, issue comments, downloaded files, MCP/tool output, and files from untrusted branches as untrusted data rather than instructions.

Treat agent instruction and automation files as security-sensitive configuration. Review changes to `ai-workflow/**`, `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, MCP/tool configuration, hooks, scripts, and CI workflows before allowing an agent to load or execute them.

Follow the active environment's sandbox and confirmation controls. Obtain
explicit approval for sensitive or side-effecting actions that are not already
authorized by the request, project policy, or environment confirmation surface;
do not ask twice for the same scoped action. Destructive actions, production or
staging access, secrets, remote mutations, and external transmission remain
permission boundaries.

## Commit preference

The workflow is designed around small verified task commits. If your agent or environment requires approval for git operations, approve the commit step explicitly or ask the agent to draft the message first.

## Blueprint vs example

`feature_execution_blueprint.md` is the reusable source. `example/ai-workflow/` is sanitized generated output for a fictional task management app. Example commands and validation evidence are illustrative; replace them with real project commands in your own workflow.

The example intentionally includes a failed validation and a blocked unsafe
validation path. It is meant to show how the workflow behaves when something goes
wrong, not only the clean completion path.

To tour the example, read the files in workflow order:

1. `example/ai-workflow/PRODUCT_BACKLOG.md` shows raw feedback normalized into NMI backlog items.
2. `example/ai-workflow/WORK_INDEX.md` groups backlog items into executable batches.
3. `example/ai-workflow/work/B001-example-feature/FEATURE.md` defines the product and technical contract.
4. `example/ai-workflow/work/B001-example-feature/IMPLEMENTATION.md` breaks the contract into verified tasks.
5. `example/ai-workflow/work/B001-example-feature/PROGRESS.md` records detailed execution evidence.
6. `example/ai-workflow/work/B001-example-feature/PROGRESS_STATE.md` keeps compact restart state.

`WORK_INDEX.md` may list planned batches whose folders do not exist yet. A batch folder is created when that batch moves from intake into feature planning.
