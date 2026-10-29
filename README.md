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

## Details

- [Installation and updates](skills/install.md)
- [Workflow rules and work records](skills/workflow/SKILL.md)
- [Planning](skills/workflow/prepare.md), [delivery](skills/workflow/deliver.md)
  and [verification](skills/workflow/verify.md)
- [Evaluation criteria and evidence limits](tests/evaluation.md)
