# Task-execution prompt

Role: Implement one selected workflow task.

Goal: Complete the next unfinished task—or the supplied task ID—with the smallest
coherent change.

Context: Start with `PROGRESS_STATE.md`, the selected task, relevant `FEATURE.md`
criteria, `AGENTS.md`, and `SECURITY.md`. Read testing policy, ledgers, or detailed
progress only when the task requires them.

Success criteria:

1. `done_when` and relevant acceptance criteria are satisfied.
2. Required validation and nearby existing checks pass.
3. The final diff is scoped and reviewed.
4. Traceability, progress evidence, compact state, and lifecycle owners are
   updated consistently.
5. `node scripts/validate-workflow.mjs ai-workflow` passes before any `done` claim.

Constraints: Follow canonical workflow, testing, and security policies. Preserve
unrelated user changes. Do not add unrequested behavior or cross an approval
boundary.

Output: Lead with `done`, `blocked`, `failed_validation`, or `rolled_back`, then
list changed files, validation and results, tests, traceability state, risks or
gaps, and the next task when obvious.

Stop rules: Stop and record the exact state when requirements conflict with
repository evidence, permission is missing, required validation fails or cannot
run, or progress would require material scope expansion. Continue to another task
only under the adjacent-task rule in `AGENTS.md`.
