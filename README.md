# AI Dev Workflows

A small file-based workflow for AI-assisted software development. It turns raw feedback into a backlog, groups related work into execution batches, creates feature contracts and task plans, then records validation evidence and compact restart state.

The repository is a store for one self-contained reusable blueprint.
`feature_execution_blueprint.md` is the complete operational source; files under
`example/ai-workflow/` are generated sample output that demonstrates how the
blueprint should behave in practice. No separate toolkit files are required to
initialize or run the workflow.

The repository also includes an optional reference harness. It automates the
workflow doctor, internal outcome continuation, and section 14 evaluation while
leaving the blueprint as the sole workflow contract.

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

For the executable reference checks, run:

```sh
bin/feature-execution doctor example/ai-workflow \
  --blueprint feature_execution_blueprint.md
python3 -m unittest discover -s tests
```

The numbered sections are a stable interface designed for short remote or mobile
commands. For example: `Use section 11 of feature_execution_blueprint.md for
batch B001 and execute it to a verified outcome.` The agent reads that section and the
generated artifacts it names; it needs no other toolkit source. Execution phases
still inspect and modify the target repository's application code as needed.

Section 12 remains the named-task variant of section 11, but delegates to the
same canonical runtime procedure instead of maintaining a duplicated prompt.
Existing commands such as `Use section 12 ... task T002` remain valid.

## Optional reference harness

`bin/feature-execution` is one public command with four operations:

- `doctor` checks generated provenance, lifecycle agreement, required files,
  allowed statuses, and artifact-size targets.
- `run` drives one agent session through internal continuation until a verified
  outcome, real blocker, authorization boundary, or the three-cycle no-progress
  watchdog.
- `eval` runs a versioned case set and saves JSON plus Markdown evidence.
- `compare` compares a baseline with a candidate and is the only operation that
  can mark the candidate accepted. It rejects incomplete evidence and changes to
  more than one configuration group.

The canonical generic suite is
`eval/cases/v1/catalog.json`. It contains 20 sanitized cases covering every
section 14 behavior class, all ten measured dimensions, and all fifteen hard
gates. Run results belong in a separate report directory; never add private
transcripts or project identifiers to the canonical catalog.

The included Codex adapter uses structured output and resumable sessions. Pass
its absolute path because evaluation workspaces are temporary:

```sh
export FEATURE_EXECUTION_CODEX_MODEL='<model and version>'
export FEATURE_EXECUTION_CODEX_EFFORT='<effort setting>'
export FEATURE_EXECUTION_CODEX_TOOLS_LABEL='<tool set>'
export FEATURE_EXECUTION_CODEX_EXPECTED_SHA256='<sha256 of the resolved codex executable>'

bin/feature-execution eval \
  --suite eval/cases/v1/catalog.json \
  --adapter-command '["python3","/absolute/path/to/ai-dev-workflows/adapters/codex_exec.py"]' \
  --blueprint /absolute/path/to/baseline-blueprint.md \
  --configuration-label baseline \
  --trials 3 \
  --report-dir eval/reports \
  --allow-verifier-commands \
  --behavioral-agent \
  --model '<model and version>' \
  --effort '<effort setting>' \
  --tools '<tool set>'
```

The canonical suite contains executable verifier commands. Review the suite
first: `--allow-verifier-commands` explicitly authorizes those commands to run
with the current user's permissions. The runner refuses them without that flag.

The material UI case also requires an independent calibrated judge. Supply it as
`--judge-command '["python3","/absolute/path/to/judge-adapter.py"]'`, together
with a non-`unknown` `--judge-label`, `--judge-model`, and
`--judge-calibration-file`. The calibration JSON records a revision, the exact
judge model, at least three human-rated examples with the judge's predictions,
and a maximum mean absolute error no greater than 1.0. The measured error must
satisfy that threshold. The judge runs after the evaluated agent while the
temporary workspace is still available. It returns rubric scores plus at least
one decodable PNG evidence reference
through `FEATURE_EXECUTION_JUDGE_RESULT_FILE`; it must not be the evaluated
adapter itself. The runner retains and hashes the calibration and visual evidence.

Repeat with the candidate blueprint and a different label, then compare the two
saved JSON reports:

```sh
bin/feature-execution compare \
  --baseline eval/reports/<baseline>.json \
  --candidate eval/reports/<candidate>.json \
  --output eval/reports/<comparison>.json
```

`--behavioral-agent` is an explicit evidence assertion: use it only for a real
agent run through the included Codex adapter. The runner additionally verifies
that every turn carries adapter-generated Codex JSONL provenance, so setting the
flag on the scripted adapter cannot make its report behavioral. Scripted adapters
are useful for testing the runner, but their reports remain unaccepted. A
standalone behavioral report can only say that it meets the absolute bar;
acceptance additionally requires the comparable baseline step.

`FEATURE_EXECUTION_CODEX_BIN` is a test hook. Runs that override the Codex binary
are marked non-behavioral. A behavioral run also requires
`FEATURE_EXECUTION_CODEX_EXPECTED_SHA256` to match the resolved executable.
Behavioral provenance records that executable, digest, version, sandbox, hashed
extra arguments, and the included adapter's digest. Reserved extra arguments
cannot override the attested model, effort, sandbox, workspace, or output schema.
Comparison treats a provider-runtime or adapter digest change as a separate
variable group.

Every trial retains a workspace hash manifest, Git patch/status, full structured
trajectory, independent verifier results, and safe explicitly referenced files
under the report directory before the temporary workspace is removed. Use only
sanitized fixtures; retained evidence must not contain secrets or production data.
Comparison reopens those files, verifies their hashes, and recomputes balanced
trial coverage, aggregate metrics, variance, tradeoffs, dimensions, gates, and the
absolute bar instead of trusting report claims.

Provider configuration stays outside the blueprint. The reference Codex adapter
reads `FEATURE_EXECUTION_CODEX_MODEL`, `FEATURE_EXECUTION_CODEX_EFFORT`,
`FEATURE_EXECUTION_CODEX_TOOLS_LABEL`, `FEATURE_EXECUTION_CODEX_SANDBOX`, and a
JSON string array in `FEATURE_EXECUTION_CODEX_ARGS`. For a behavioral report,
the first three values must match `--model`, `--effort`, and `--tools`; the runner
checks that match on every turn and never treats an unknown value as evidence.

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
