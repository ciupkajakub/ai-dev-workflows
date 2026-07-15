# Intake prompt

Role: Maintain the product backlog and execution queue.

Goal: Convert the supplied feedback into coherent NMI backlog items and planned
batches without beginning feature design or implementation.

Inputs:

- supplied feedback;
- `ai-workflow/PRODUCT_BACKLOG.md`;
- `ai-workflow/WORK_INDEX.md`;
- `ai-workflow/AGENTS.md` and `SECURITY.md`.

Success criteria:

1. New feedback is represented by new NMI items with source, problem, requested
   outcome, assumptions, and acceptance hints.
2. Related items are grouped into coherent planned batches.
3. Existing descriptions remain historical; refinements or replacements use new
   linked items and explicit supersession.
4. Backlog and batch history record material changes.
5. No feature, plan, progress, or application-code file is created.

Constraints: Do not expand active or completed batches. Make conservative grouping
assumptions when safe and record them. Follow the canonical policies.

Output: Report created or updated IDs, grouping decisions, assumptions, and any
blocking ambiguity.

Stop rules: Ask only when missing information prevents safe grouping. If no
eligible or coherent grouping exists, report the smallest missing decision.

Feedback:

`<PASTE FEEDBACK>`
