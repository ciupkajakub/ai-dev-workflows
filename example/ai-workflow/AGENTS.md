# Agent rules

## Contract

Follow the selected batch `FEATURE.md` and `IMPLEMENTATION.md` as the feature contract.

Do not invent requirements.

Repo behavior, existing tests, schemas, migrations, command output, and conventions are authoritative implementation evidence.

If the feature contract conflicts with repo evidence, stop and report:

1. the conflict
2. why it matters
3. likely options
4. recommended next step

## Clarification

Ask for clarification only when the missing decision blocks safe progress.

When asking, include:

1. what is ambiguous
2. why it matters
3. options
4. recommendation
5. default if no answer

If a reasonable default is safe and consistent with the contract, proceed and record the assumption in `PROGRESS.md`.

## Execution discipline

Explore before editing.
Identify likely files and touchpoints before implementation.
Prefer the smallest coherent change.
Avoid unrelated refactors.
Follow existing repo conventions first.
Use parallel reading/searching when independent touchpoints need investigation.
Do not use parallel write workflows unless file ownership boundaries are explicit and low overlap.

## Done discipline

Mark a task done only after:

1. `done_when` is satisfied
2. relevant acceptance criteria are checked
3. validation was run or the exact gap is recorded
4. evidence is appended to `PROGRESS.md`

If verification is partial, do not claim completion.

## Validation discipline

Every task needs a practical verification plan.
Prefer the strongest practical signal:

1. tests
2. typecheck
3. lint
4. build
5. migration check
6. smoke test
7. screenshot or visual comparison
8. exact command output

Run the smallest reliable check first.
Record validation evidence in `PROGRESS.md`.

## Security and permissions

Follow `ai-workflow/SECURITY.md` before using tools, handling sensitive data, calling external services, or recording workflow evidence.
If `SECURITY.md` and a task prompt conflict, follow the stricter rule and report the conflict.

## Context hygiene

Read only the files and artifact sections needed for the current task.
Default to one task per session.
Continue only when the next task is small, adjacent, and low risk.
If exploration becomes noisy, summarize findings in `PROGRESS.md` and restart from artifacts.

## Ledger hygiene

Keep `PROGRESS_STATE.md` compact enough to reload quickly.
Use `PROGRESS.md` for detailed evidence, not repeated summaries.
Default size targets:

1. keep `PROGRESS_STATE.md` under 80 lines
2. propose archiving `PROGRESS.md` after 300 lines
3. propose archiving done or superseded backlog/history entries when `PRODUCT_BACKLOG.md` or `WORK_INDEX.md` becomes slow to scan

When `PRODUCT_BACKLOG.md`, `WORK_INDEX.md`, or `PROGRESS.md` grows too large to scan safely, propose an archive file such as `ai-workflow/archive/YYYY-MM.md` or `ai-workflow/work/B###/PROGRESS_ARCHIVE.md` before continuing.
Do not delete historical evidence unless the user explicitly approves an archival or retention policy.

## Communication

Be concise and technical.
Keep commands, file paths, identifiers, and exact error messages unchanged.
