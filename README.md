# AI Dev Workflows

One `workflow` skill for Codex, Cursor and Claude Code that takes a development
request from planning to a pull request. You approve the plan before the agent
changes application code.

This repository supplies instructions for the agent. It does not run agents,
provision environments or enforce the process automatically.

## How it works

1. Describe what you need. The agent reads the project, clarifies requirements
   and prepares a technical plan.
2. Another agent reviews the plan against your request and the code. The author
   resolves blocking findings before asking for your approval.
3. Approve the scope. The agent implements it in an isolated checkout and test
   environment, runs the required checks and fixes defects within that scope.
   Independent code review is required when risk, project rules or the agreed
   scope call for it.
4. Once the required checks and reviews are satisfied, the agent opens or updates
   a PR and stops. Merge and deployment need separate decisions.

There is no automatic repair loop after the PR. To address feedback, ask the agent
to assess it and propose a continuation for approval.

You may instead start a PR maintenance tool such as Claude Code `/steward` yourself, for
any single PR. The workflow does not need one. See
[optional PR maintenance](skills/install.md#optional-pr-maintenance).

## Get started

Clone this repository:

```sh
git clone https://github.com/ciupkajakub/ai-dev-workflows.git
```

Open your application repository and ask its agent:

```text
Read <source-repo>/skills/install.md. Install this workflow from that checkout's
HEAD for the tools I use. Preserve project rules and local edits. Verify the
package. Do not implement application code.
```

Replace `<source-repo>` with the absolute path to your clone. Installation pins
the committed version; future updates are explicit.

Then describe a task in Codex:

```text
$workflow Let customers cancel an order before preparation starts.
```

Use `/workflow` in Cursor or Claude Code. Reply to the proposed plan in ordinary
language. To resume interrupted work, provide its `ai-workflow/work/<batch-id>/`
path.

## Update

Changes in this repository do not reach your applications automatically. First update
your clone:

```sh
git -C <source-repo> switch main && git -C <source-repo> pull --ff-only
```

Then ask the agent in each application repository:

```text
Read <source-repo>/skills/install.md. Update the installed workflow to that checkout's
HEAD for the tools I use. Compare the current copy with its recorded source commit
first. Preserve project rules, local edits and work records. Update the recorded source
commit and verify the package. Do not migrate batches or implement application code.
```

Start a new agent session afterwards so it reads the new version. To check for an update
without changing anything, ask instead:

```text
Read <source-repo>/skills/install.md. Check, read-only, whether the installed workflow
is intact and whether that checkout's HEAD has an update.
```

## Details

- [Installation and updates](skills/install.md)
- [Workflow rules and work records](skills/workflow/SKILL.md)
- [Planning](skills/workflow/prepare.md), [delivery](skills/workflow/deliver.md)
  and [verification](skills/workflow/verify.md)
- [Evaluation criteria and evidence limits](tests/evaluation.md)
