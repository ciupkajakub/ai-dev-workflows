# AI Dev Workflows

A file-based workflow for AI-assisted software development. It turns raw feedback into a backlog, groups work into execution batches, creates feature contracts and implementation plans, then records verified execution evidence.

Use it when a change is too large or risky to keep in chat memory: product feedback, multi-step features, cross-cutting backend/UI changes, migration work, or anything where acceptance criteria and verification evidence matter.

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

## How to use it

1. Copy `feature_execution_blueprint.md` into your project or open it next to your project.
2. Run the blueprint prompts in order.
3. Keep generated workflow files under `ai-workflow/` in your project.
4. Execute one batch task at a time and record evidence in `PROGRESS.md`.

## What the blueprint creates

The blueprint contains prompts and templates for:

- `ai-workflow/AGENTS.md`
- `ai-workflow/TESTING_POLICY.md`
- `ai-workflow/PRODUCT_BACKLOG.md`
- `ai-workflow/WORK_INDEX.md`
- `ai-workflow/COMMIT_MESSAGE.md`
- `ai-workflow/work/B###/FEATURE.md`
- `ai-workflow/work/B###/IMPLEMENTATION.md`
- `ai-workflow/work/B###/PROGRESS.md`
- `ai-workflow/work/B###/PROGRESS_STATE.md`

## Example

See `example/ai-workflow/` for sanitized generated output using a fictional task management app.
