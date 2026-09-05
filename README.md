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

Use it when a change is too large or risky to keep only in chat memory: product feedback, multi-step features, cross-cutting backend/UI changes, migration work, or anything where acceptance criteria and verification evidence matter. For a small, local, reversible change, use the coding agent directly; this blueprint deliberately has no reduced fast lane.

Do not use it as a replacement for human review, security review, production change control, or project-specific engineering judgment.

## 5-minute quickstart

1. Copy `feature_execution_blueprint.md` into your project or keep it open next to your project.
2. Ask your coding agent to run sections 2-6 of the blueprint to create the base `ai-workflow/` files.
3. Paste raw feedback into the prompt from section 8 to create backlog and batch entries.
4. Run section 9 to turn one selected batch into `FEATURE.md`.
5. Run section 10 to create `IMPLEMENTATION.md`, `PROGRESS.md`, and `PROGRESS_STATE.md`.
6. Use section 11 to start from the next task and continue autonomously through
   dependency-ready tasks plus repair-mandatory finalization. Each task
   reconstructs its durable context; explicit continuation is available when
   useful. Use section 12 only when you intentionally want one named task.
7. Section 11 owns final verification and repair. Section 13 remains a compatible
   direct entry point for repairing an existing batch or running a read-only audit.
8. Use section 14 when measuring workflow changes. Local regression checks
   establish technical correctness; a comparable baseline/candidate experiment
   is needed to claim better agent behavior. Neither runs automatically.

For the executable reference checks, run:

```sh
bin/feature-execution doctor example/ai-workflow \
  --blueprint feature_execution_blueprint.md --batch B001
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

- `doctor` checks provenance, required files, and lifecycle owners. Use
  `--batch B001` to check one batch and its linked index entries; omit it for an
  explicit whole-workflow audit. Size targets are warnings, and the commit helper
  is optional. Unknown/ambiguous targets are errors. Schema 2 retains legacy
  status checks; schema 3 has one batch-status owner. The doctor does not verify
  semantic equivalence of generated prose or product correctness.
- `run` drives execution through internal continuation until a verified outcome,
  real blocker, authorization boundary, or the three-cycle no-progress watchdog.
  It preserves a provider session within a task, switches sessions at declared
  task boundaries, records safe continuation fallback, rejects terminal results
  with an executable next action, and enforces final-verification capability
  preflight requested after independent repairs are complete.
- `eval` runs a versioned case set and saves JSON plus Markdown evidence.
- `compare` compares a baseline with a candidate and is the only operation that
  can mark the candidate accepted. It rejects incomplete evidence and changes to
  more than one configuration group.

The canonical generic suite is
`eval/cases/v1/catalog.json`. It contains 32 sanitized cases covering every
section 14 behavior class, all ten measured dimensions, and all fifteen hard
gates. Run results belong in a separate report directory; never add private
transcripts or project identifiers to the canonical catalog.

The included Codex adapter uses structured output and provider-specific resume
tokens behind the generic session-routing contract. Pass its absolute path
because evaluation workspaces are temporary:

```sh
export FEATURE_EXECUTION_CODEX_MODEL='<model and version>'
export FEATURE_EXECUTION_CODEX_EFFORT='<effort setting>'
export FEATURE_EXECUTION_CODEX_TOOLS_LABEL='<tool set>'
export FEATURE_EXECUTION_CODEX_EXPECTED_SHA256='<sha256 of the resolved codex executable>'
export FEATURE_EXECUTION_CODEX_CAPABILITIES='["filesystem","database","browser"]'

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

The suite thresholds are acceptance policy for these cases, not universal
quality ratings. Dimension scores are ten times the pass fraction of tagged
cases. Section 14 also describes a smaller 24-run pilot; no behavioral comparison
was performed for revision 3.0.0, so technical checks do not establish a
productivity or reliability improvement.

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
adapter itself. The runner gives the judge a snapshot of the evaluated workspace
and a separate evidence-output directory, rejects any judge mutation of that
snapshot, and retains and hashes the calibration and visual evidence.

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
extra arguments, capability profile, and the included adapter's digest. The adapter ignores user
configuration and repository rules during controlled evaluation. Reserved extra
arguments cannot override the attested model, effort, sandbox, workspace, output
schema, extra writable directories, or hook trust.
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
`FEATURE_EXECUTION_CODEX_TOOLS_LABEL`, `FEATURE_EXECUTION_CODEX_SANDBOX`, and
`FEATURE_EXECUTION_CODEX_CAPABILITIES`. The capability list describes the local
resources available to the selected execution profile and is checked before the
agent continues into final validation. Only required local Batch validation
commands contribute to that check. Declarations do not prove that the database
or browser actually works; permitted diagnostics and validation provide proof.
`FEATURE_EXECUTION_CODEX_ARGS` must remain an empty JSON array during a controlled evaluation. For a behavioral report,
the first three values must match `--model`, `--effort`, and `--tools`; the runner
checks that match on every turn and never treats an unknown value as evidence.

Pasteable setup prompt:

```text
Use feature_execution_blueprint.md to create the base ai-workflow files for this repository.

Run only sections 2-6. Section 7 is an optional commit-message helper.
Create:
- ai-workflow/AGENTS.md
- ai-workflow/SECURITY.md
- ai-workflow/TESTING_POLICY.md
- ai-workflow/PRODUCT_BACKLOG.md
- ai-workflow/WORK_INDEX.md

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

The Coverage table maps contract ids and shared-contract consumers to task
owners, validation ids, and evidence links. Requirements stay in FEATURE.md,
commands in the plan, and results in PROGRESS.md. The table does not copy them.

Before accepting a completed batch, the blueprint's finalizer runs declared
broader local checks, exercises the observable result, evaluates UI against its
visual rubric when applicable, and repairs related in-scope findings while
evidence shows progress. Missing tests and workflow corrections are unfinished
repair, not blockers. After independent repairs, the adapter compares required
capabilities with its configured profile. The executor confirms actual access
through permitted diagnostics and validation. The finalizer checks lifecycle
owners, Coverage, security approvals, and final-report accuracy before closure.

## Outcome-driven task execution

Section 10 is the canonical source for the task execution policy copied into
generated `IMPLEMENTATION.md` files. Task boundaries follow coherent,
independently verifiable outcomes. Estimates are scheduling signals, not stop or
approval conditions. A ten-minute checkpoint produces a compact update and then
work continues. Hard bounds apply to individual commands, repeated no-progress
on the same root cause, and rerunning an unchanged check. Section 11 proceeds
across task boundaries and into finalization without requiring `Continue` or
`Fix` prompts.

Schema 3 tasks have six required fields: id, status, outcome, feature_refs,
dependencies, and validation_commands. Omitted session metadata means fresh
context reconstructed from durable state. An explicit `continue` names a prior
task and a concrete reason to reuse its implementation/debugging discoveries.
Dependencies alone do not imply continuation. A manual client can reconstruct
the selected context within its current session when provider-session control
is unavailable; creating another conversation is not a completion gate.

Provider adapters implement semantic continuity using their own mechanism. The
Codex adapter uses resume tokens, but those tokens never enter workflow
artifacts. If a requested source session is missing or the provider reports it
unavailable, the harness records the fallback and retries once as `fresh` from
durable state. Missing conversation history alone is not a blocker and never
relaxes lifecycle, validation, traceability, authorization, or security gates.
At the harness boundary, provider adapters use exit code `75` only to report
that a requested continuation handle is unavailable; other adapter failures
remain errors and are not retried as fresh sessions.

Full suites, repo-wide build/lint/typecheck, full-history or repository security
scans, dependency audits, and CI commands cannot be task-scoped. This avoids
scheduling the same broad proof for every task. Actual elapsed time or cost
improvements require a comparative measurement.

`IMPLEMENTATION.md` assigns every check to exactly one scope:

- `task`: focused checks run by section 11 or 12
- `batch`: broader local checks run once by section 11 final verification after all tasks
- `ci`: external checks that local execution records but never launches

Loading a security policy, testing policy, skill, or reference does not add a
validation command. A task executor can record and run a newly discovered safe,
focused check at the correct scope when evidence makes it necessary; broader or
external proof still requires the batch/CI declaration and applicable permission.
After the last task, section 11 enters its internal final verification phase. It
runs each declared batch command once initially, reruns only failed proof after a
relevant repair, and closes feature delivery separately from integration and
release evidence. Pending CI blocks `release_ready`, not a truthful
feature-delivery claim, unless the feature contract explicitly requires release
readiness. Section 13 enters the same repair loop for an existing batch,
including a partially implemented one. Unfinished work returns to its owning tasks before
final validation.

## Context strategy

The workflow keeps its single-file, numbered-section interface while loading
detail progressively:

- `ai-workflow/AGENTS.md` is a compact repo map, command reference, and router to
  the core workflow gates.
- A fresh runtime task starts from `PROGRESS_STATE.md`, one task, its completed
  dependency outcomes, relevant contract items, and `AGENTS.md`; conversation
  history is an optional optimization.
- `SECURITY.md`, `TESTING_POLICY.md`, detailed progress, references, and skills
  load only when the selected phase or task needs them.
- `FEATURE.md` records the smallest useful references and applicable skills.
  `IMPLEMENTATION.md` routes each reference or skill only to the tasks where it
  contributes a decision or required evidence.

For example, a UI batch can route `apple-design` to contract design, UI
implementation, and visual review without loading it for backend tasks. A
provider-specific skill is advisory unless the contract also defines a portable
fallback, so the workflow remains usable by another capable coding agent. A
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
- `ai-workflow/COMMIT_MESSAGE.md`, optional
- `ai-workflow/work/B###/FEATURE.md`
- `ai-workflow/work/B###/IMPLEMENTATION.md`
- `ai-workflow/work/B###/PROGRESS.md`
- `ai-workflow/work/B###/PROGRESS_STATE.md`

Schema 3 defines one owner for each changing fact:

| Information | Owner |
| --- | --- |
| Product requirements, AC, decisions, completion level | FEATURE.md |
| Task statuses, dependencies, commands, Coverage | IMPLEMENTATION.md |
| Batch status and integration/release state | WORK_INDEX.md |
| NMI status | PRODUCT_BACKLOG.md |
| Material decisions, command results, repairs, accepted gaps | PROGRESS.md |
| Next action, recovery facts, links to evidence and open checks | PROGRESS_STATE.md |

FEATURE.md has five required, populated sections: Outcome, Scope, Acceptance
criteria, Decisions and constraints, and Verification. Permissions, performance,
data, UI, and other relevant requirements belong inside these sections, without
nullable fields or empty optional headings. Stable AC/C references prevent the
shorter format from dropping a requirement during planning.

Generated current artifacts record the exact source, revision, schema, and digest.
Preflight checks operational instructions even when metadata already matches:
obsolete task/count limits, extra approval pauses, first-failure stops, provider
session requirements, and mirrored state must be reconciled against the canonical
contract. It preserves real project constraints and does not infer a semantic
migration from a changed hash.

The blueprint includes the known schema 2-to-3 migration. Apply it only to selected
work; preserve task ids, requirements, legacy references, and prior evidence.
PROGRESS.md keeps its earlier bytes and provenance and gains a migration entry.
Unrelated and archived batches are not rewritten. The doctor can still inspect
schema 2 artifacts and reports known migration drift as warnings; it remains a
structural check, not an agent-behavior verifier.

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

The workflow is designed around small verified task commits. Commit packaging is
separate from feature delivery: when a commit is not part of the feature contract,
staging or `.git/index.lock` failure does not block a verified batch. If your
agent or environment requires approval for git operations, approve the commit
step explicitly or ask the agent to draft the message first.

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
7. `example/session-routing/IMPLEMENTATION.md` is a sanitized generated-plan
   excerpt showing a justified `fresh -> continue` relationship without changing
   the indexed example batch's append-only history.

`WORK_INDEX.md` may list planned batches whose folders do not exist yet. A batch folder is created when that batch moves from intake into feature planning.
