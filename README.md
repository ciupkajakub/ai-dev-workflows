# AI Dev Workflows

A portable workflow for turning a business need into an accepted code change.
The coordinator prepares a proposal and plan, a person approves the direction,
and the coordinator takes the work through implementation, verification, repairs,
and a PR. Native workers implement tasks by default when supported. Human feedback
starts another iteration of the same work when appropriate.

[The blueprint](feature_execution_blueprint.md) is the complete instruction.
Use it with your coding provider's native execution environment. This repository
does not run agents, provision sandboxes, listen to GitHub comments, or enforce
approval gates in software. It defines the stages and handoffs for manual starts
now and event-driven starts later. The operator and configured provider controls
must enforce the workflow; a written instruction alone is not a guarantee.

## The working flow

```text
Business need
  -> inspect the project and resolve missing decisions
  -> one proposal: behavior contract + implementation and verification plan
  -> HUMAN: approve the specific proposal and delivery scope
  -> coordinator delegates implementation to native workers by default
  -> verification -- failure --> repair -- back to verification
       | required checks pass on the combined result
       v
  -> PR with evidence
  -> HUMAN: review the delivered result
       -> accept the result
       -> actionable feedback: update contract/plan, implement, verify, update PR
       -> unclear change of direction: revised proposal for approval
       -> request unrelated work: add a backlog item
```

There are two planned human decisions: approving the solution and accepting the
result. The agent may also need an unresolved product decision or access it does
not have. A clear instruction to make a specific change can itself approve that
change. The verification/repair loop has no routine human gate. Finishing a task,
switching workers, or starting another check does not require a new prompt.

## What you ask the agent to do

Work in the application's repository with this blueprint available. These are
invocation templates; replace placeholders with the actual project and request.
The normal sequence is Prepare, approval through PR delivery, then human review.
Feedback starts another delivery round, not a series of manually launched tasks.

| Request | What happens |
| --- | --- |
| Use the blueprint to **set up** this project's workflow. | Inspect existing instructions and create only the missing base files. |
| **Prepare** this need: `<request>`. | Capture the need, inspect code, write the proposal and plan, and present them for approval. |
| I approve the presented proposal for `<batch>`. **Deliver it through a PR**, including implementation, verification, commits, and push to `<destination>`. Use native workers under the configured execution profile. | Record the exact approved content and scope. Coordinate implementation, checks, repairs, and PR publication without further routine prompts. |
| For `<batch>`, **apply this feedback and update the PR**: `<feedback>`. | Reconcile requirements, tasks, and affected evidence, implement, verify, and publish the next iteration under the authorized delivery scope. |
| I edited `<batch>`'s plan. **Reconcile my edits and execute** the changes. | Compare against the approved version, preserve the edits, resolve contradictions, and continue. |
| **Audit** `<batch>` without changes. | Read the proposal, plan, diff, and evidence; report gaps without edits or status changes. |
| **Integrate** `<batch>` against `<target>`. | Inspect the combined changes and verify affected behavior. Merge or publish only if separately authorized. |

The approval request includes any missing commit, push, and PR authority so that
approval can start the complete run. Existing scoped project authorization can
provide those permissions. Merge and deployment remain separate decisions.
For a plan-only review, explicitly ask to update the proposal without implementing.

Before approval, the agent presents a product overview, a technical summary of
what it plans to add/change/remove, and material risks with verification scenarios.
It separates inspected code facts from proposed changes and agent-added decisions,
and links the proposal documents. A flow diagram is optional. At PR handoff, the
same summary describes the actual diff, departures from the plan, and verification
results. See [Approval presentation](feature_execution_blueprint.md#approval-presentation).

The proposal combines the former sections 8, 9, and 10. Delivery replaces section
11 and includes verification and repairs. You can still limit a request to a
feature contract, plan, or named task; that scope is not a mandatory extra gate.

## Workflow commands

The repository includes five native skills that route to the blueprint. Their
canonical instructions live in `skills/`; `.agents/skills/` and `.claude/skills/`
contain relative links to those same directories. Codex and Cursor discover the
former; Claude Code discovers the latter. Cursor also supports the Claude path.
No separate Cursor copy is needed.

| Action | Codex invocation | Claude Code / Cursor invocation |
| --- | --- | --- |
| [Set up](skills/workflow-setup/SKILL.md) | `$workflow-setup` | `/workflow-setup` |
| [Prepare](skills/workflow-prepare/SKILL.md) | `$workflow-prepare <need>` | `/workflow-prepare <need>` |
| [Deliver](skills/workflow-deliver/SKILL.md) | `$workflow-deliver <batch>` | `/workflow-deliver <batch>` |
| [Apply feedback](skills/workflow-feedback/SKILL.md) | `$workflow-feedback <batch> <feedback>` | `/workflow-feedback <batch> <feedback>` |
| [Resume](skills/workflow-resume/SKILL.md) | `$workflow-resume <batch>` | `/workflow-resume <batch>` |

Select the skill through the client's skill picker if needed. Replace placeholders
with the actual request; they are chat inputs, not terminal commands. The skill
instructions are in English; requests and feedback can be in Polish or English.

A direct `workflow-deliver` invocation approves the exact proposal and delivery
scope already presented to the operator, including its publication destination.
If these are missing, ambiguous, or changed, the agent presents them for approval
before implementation. Merely discovering or automatically selecting the skill
does not approve delivery. `workflow-resume` reuses existing authority; it does not
approve a waiting proposal or accept a delivered result.

Run commands in the application repository after installation. For the one-time
bootstrap, give that repository's agent the absolute path to this package's
`skills/workflow-setup/SKILL.md` and request setup for Codex, Claude Code, Cursor,
or the providers your team uses. The [installation procedure](skills/install.md)
keeps a versioned copy of the blueprint and skills together in the application.
It preserves existing configuration and reports fresh-session discovery as pending
unless it has actually been checked. Installing in this repository alone does not
make the skills available in other application repositories.

Each workflow command identifies its blueprint revision and recorded source
package commit. The number alone is insufficient while source changes share a
blueprint revision. Setup and explicit updates compare the copied package with
that exact commit using the read-only [package checker](skills/check_package.py).
Matching the installed commit and matching a checked local source HEAD are
separate results. Without a comparison, integrity/currentness remain unverified.
Ask `workflow-setup` to check the installed version without changes, or explicitly
request an update from the source checkout. The source package is not fetched or
updated automatically, and the provider's skill picker is not a version checker.

These entry points standardize requests. Provider permissions, model configuration,
execution, and verification still apply. They do not enforce the workflow in software.
Provider documentation: [Codex skills](https://learn.chatgpt.com/docs/build-skills),
[Claude Code skills](https://code.claude.com/docs/en/skills), and
[Cursor skills](https://cursor.com/docs/skills).

## Models, sessions, and later automation

Configure a stronger planning/coordinator model and faster or cheaper implementation
workers in the provider's native execution settings where supported. Delegation
is the default, not a per-run preference of the coordinator. The coordinator
assigns bounded tasks, checks worker evidence, and verifies the combined result.
It remains responsible until PR handoff or a genuine blocker. An additional
reviewer may help; passing tests and observable behavior remain required proof.
If model selection is unavailable, report that limitation and use native workers
with the permitted model. If delegation itself is unavailable or prohibited by
project controls, report the reason and use the permitted executor directly.
An explicit operator instruction can also select direct execution. This repository
supplies no model-selection mechanism.

One chat is optional. Before switching sessions, save decisions, worker results,
and the next action in the batch documents. The next coordinator needs access to
the current files and branch; it must not race another coordinator on that batch.
The operator does not need to copy planning chat history into worker prompts.

Today, send the need, approval, or feedback to the agent tool to start or resume
the corresponding run. Later, a GitHub/Slack integration can deliver those same
events, bound to the authorized person, batch, and exact proposal/result revision.
It must reject stale approvals and prevent duplicate runs or PRs. The provider
handles agent execution and sessions. No listener or notification delivery is
implemented here. See [Pipeline and handoffs](feature_execution_blueprint.md#pipeline-and-handoffs)
for transition rules and the information each stage passes forward.

## Files in a project

```text
ai-workflow/
  AGENTS.md                 Project commands, constraints, and instruction links
  PRODUCT_BACKLOG.md        Business needs and their source
  WORK_INDEX.md             Batch identity, lifecycle, integration, and delivery
  work/B###-short-name/
    FEATURE.md              Expected behavior, decisions, and acceptance criteria
    IMPLEMENTATION.md       Tasks, dependencies, coverage, and verification
    PROGRESS.md             Current restart notes, approvals, and evidence history
```

Keep existing project security and testing policies. Link them from `AGENTS.md`;
create separate policy files only when there is a project-specific rule to record.
Store bulky evidence and approval snapshots outside the three working documents,
using stable links. Each changing fact has one owner, defined in the blueprint.

## Two issues running at the same time

Reserve distinct batch identities before starting independent branches. Each
issue runs in its own branch and checkout with its own application instance and
isolated mutable test resources. A worktree separates files; it does not separate
databases, queues, caches, ports, or external test accounts.

Each issue may modify the same application's schema, but it tests against its own
disposable database. Before integration, verify the combined migration chain and
affected application behavior against the current target branch. Isolation
prevents interference during execution; it cannot prevent semantic conflicts
between two changes. Dependent or incompatible changes need an explicit order.

Use the provider's native workspaces and agents where they satisfy these needs.
Default delegation does not require parallel execution: serialize workers when
isolation is unavailable. Required checks and evidence remain the same whichever
executor is used.

## What changed in version 4

- One prepare request covers intake, requirements, and task planning.
- Approval starts coordinated delivery through the authorized PR handoff, with
  native delegation and automatic verification/repair rounds.
- Pipeline handoffs support different sessions/models and future event triggers;
  manual starts do not require manually launching each internal stage.
- Approval identifies the actual feature and plan versions being accepted.
- Feedback and operator edits can revise the same batch without losing history.
- `PROGRESS.md` holds restart notes as well as append-only historical evidence.
- Completion includes human acceptance; integration and release remain separate.
- Concurrent work has explicit resource isolation and integration rules.
- The reference runner, provider adapter, JSON protocol, evaluation framework,
  and their tests have been removed. Prior implementations remain in Git history.
- The fictional generated examples have been removed with the old schema.
  Real implementation records can be added later; this revision adds none.

Existing project artifacts are not automatically rewritten. Follow
[Existing workflows and migration](feature_execution_blueprint.md#existing-workflows-and-migration)
for a selected batch. Old section numbers and CLI commands are retired; this is
an explicit version change, not a drop-in replacement for the former runner.

## Validation and limits

Run the lightweight documentation check:

```sh
python3 -B tests/validate_blueprint.py
python3 -B tests/test_check_package.py
git diff --check
```

The documentation check covers Markdown structure, local links, and skill discovery
links for Codex, Claude Code, and Cursor. Package tests exercise exact copies,
local changes, missing/extra files, source updates, and unavailable revisions.
Neither check runs an agent, validates a project's delivery, or proves productivity
gains. No new
behavioral experiment or quality-equivalence claim accompanies this revision.
Evaluate it on real work by recording human interventions, review rounds,
defects found after claimed completion, elapsed time, and available usage data.

The workflow is intended for changes that benefit from a durable plan and review.
Small, clear, reversible edits can use the coding agent directly. Keep the
blueprint independent of model versions, provider CLI flags, and fixed agent
counts; configure those in the selected execution environment.
