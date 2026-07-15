# Feature-contract prompt

Role: Act as the product and technical lead for one execution batch.

Goal: Produce an implementation-ready `FEATURE.md` contract for the selected
planned or spec batch.

Inputs: The selected `WORK_INDEX.md` row, its source backlog items, relevant
repository evidence, user material, canonical policies, and `templates/FEATURE.md`.

Success criteria:

1. Product behavior, roles, visibility, non-goals, data impact, failure modes,
   risks, assumptions, rollout, and verification are unambiguous enough to plan.
2. Requirements and acceptance criteria are objective, numbered, and traceable.
3. The scope decision uses coherence, independent deployment/rollback, validation,
   risk, and context criteria; counts are advisory only.
4. The contract stays inside the selected batch and proposes new NMI items for
   discovered work.
5. Lifecycle fields and history move the batch and source items to `spec` as one
   operation.

Output: Write the selected batch `FEATURE.md` from its template, update the two
ledgers, and report decisions, assumptions, and remaining open questions.

Stop rules: Ask the smallest useful question only when a product decision would
materially change behavior or safe implementation. Recommend a split when the
scope lacks one coherent completion bar; request approval only if continuing would
materially expand authorized scope.
