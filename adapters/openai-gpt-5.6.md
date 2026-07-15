# OpenAI GPT-5.6 adapter

This adapter applies the model-agnostic workflow to the GPT-5.6 family. Re-check
the current official model and prompting guides before changing it.

## Recorded profile

Every evaluated run must record:

- exact model ID, with `gpt-5.6` as the intended target for this adapter;
- reasoning effort;
- `text.verbosity`;
- available tools and tool versions;
- harness and prompt revisions;
- cache behavior and assistant-history strategy.

For an existing workload, switch the model while preserving the current reasoning
effort, run the baseline, then test the same setting and one level lower. For a new
workload, `medium` reasoning is the provisional baseline; use `low` for
latency-sensitive work only when evals preserve quality. Use `high` or above only
for measured gains, never as a global default.

Set `text.verbosity` to `medium` as the provisional default. Use prompt-specific
output requirements to preserve required evidence and omit secondary detail.
Evaluate `low` separately rather than combining a verbosity and prompt migration.

## Prompt composition and caching

Keep this stable reusable prefix order:

1. canonical workflow policy;
2. canonical security policy;
3. canonical testing policy only when relevant;
4. task prompt;
5. selected task and current evidence.

Do not inject the full blueprint, unrelated templates, full ledgers, or irrelevant
tools. Keep reusable prefixes byte-stable when prompt caching matters. Add cache
breakpoints only after measurement.

## Tool routing

Expose only task-relevant tools. Each tool description must say what it does, when
to use it, important result fields, and meaningful failure behavior. Resolve
required discovery and validation before acting. Parallelize independent reads;
keep dependent or approval-sensitive work sequential. Try one or two meaningful
fallbacks for empty or suspiciously narrow retrieval.

Use programmatic tool calling only for bounded deterministic reduction such as
filtering, joining, deduplication, aggregation, or repeated schema validation.
Define eligible read-only tools, compact output schema, retry limit, stop rule,
and handoff. Use direct calls for semantic judgment, citations, approvals,
side-effecting actions, native artifacts, and final validation.

## Conversation state

Send a short preamble before multi-step tool work and sparse outcome-based updates
at major phase changes. Preserve original assistant phase values when replaying
history; `previous_response_id` preserves them automatically. Compact after major
milestones, keep compacted state opaque, and discard stale reasoning when the
objective or assumptions change.

## Visual tasks

Choose image detail intentionally. For user-visible UI changes, render and inspect
all affected responsive and interaction states before finalizing. Do not add
decorative UI or new behavior outside the contract, and preserve the existing
design system.

## Migration loop

1. Record the current configuration and run every representative case.
2. Change only the model and preserve reasoning effort.
3. Remove one obsolete or duplicated instruction group.
4. Add only the smallest instruction that fixes a measured regression.
5. Rerun the same cases after each prompt, tool, or setting change.
6. Count efficiency as improvement only when every hard behavioral gate passes.
