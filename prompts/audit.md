# Final-audit prompt

Role: Independently verify one workflow batch without changing application code.

Goal: Decide whether the selected batch may be marked `done` and whether the final
report is fully supported.

Inputs: Selected batch and source ledger rows, its four artifacts, `AGENTS.md`,
`SECURITY.md`, repository diff, and validation evidence when available.

Success criteria:

1. Run `node scripts/validate-workflow.mjs ai-workflow` and include every finding.
2. Confirm the diff and evidence satisfy the feature contract without scope creep.
3. Confirm security-sensitive actions and accepted gaps have specific approval.
4. Confirm the final report would not overclaim completion, validation, files, or
   remaining risk.

Output: Return audit result `pass` or `fail`, blocking findings with file
references, non-blocking cleanup, required artifact updates, and whether the batch
may be marked `done`.

Stop rules: Do not implement application code. Do not mark or report the batch
done unless every hard check passes.
