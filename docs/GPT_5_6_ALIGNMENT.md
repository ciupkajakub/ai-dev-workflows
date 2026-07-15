# GPT-5.6 alignment specification

This document records the requirements agreed for aligning the repository with
OpenAI's GPT-5.6 prompt guidance while preserving the workflow's existing safety,
traceability, validation, recovery, and final-audit gates.

## Outcome

The active prompt stack should become smaller, outcome-first, and easier to
validate. Deterministic workflow rules should be enforced by a local validator
instead of being repeated in every prompt.

Alignment must be measured, not inferred from wording alone. The repository can
be implementation-complete with local eval infrastructure, but it must not claim
full behavioral alignment until authorized baseline and candidate GPT-5.6 runs
preserve required behavior and show no unsafe actions, false completion claims,
or unnecessary approval pauses.

## Required additions

1. Executable representative eval cases and a scoring rubric.
2. A machine-readable workflow schema.
3. A zero-dependency workflow validator with one public command interface.
4. A small, explicit GPT-5.6 adapter covering verbosity, reasoning, prompt
   caching, tool exposure, phase preservation, programmatic tool calling, and
   visual validation.
5. An explicit render-and-inspect completion rule for user-visible UI changes.
6. Explicit ownership for top-level lifecycle status updates.

## Required subtractions

1. Remove repeated security rules from runtime prompts when the canonical policy
   is already loaded.
2. Remove repeated validation, traceability, and final-audit checklists from
   runtime prompts when the validator or canonical workflow policy owns them.
3. Replace hard numeric size thresholds as automatic blockers with decision
   criteria. Counts may remain advisory signals.
4. Remove step-by-step process instructions when a goal, success criterion, or
   stop rule expresses the required behavior more directly.
5. Do not duplicate canonical templates inside the blueprint.

## Required moves

1. Workflow invariants and lifecycle rules move to `policies/WORKFLOW.md`.
2. Security and authorization rules move to `policies/SECURITY.md`.
3. Test expectations move to `policies/TESTING.md`.
4. Artifact structures move to `templates/`.
5. Task-specific goals and outputs move to individual files under `prompts/`.
6. Provider-specific settings move to `adapters/`.

Generated `ai-workflow/AGENTS.md`, `SECURITY.md`, and `TESTING_POLICY.md` remain
the project-local runtime forms of the canonical policies. They may include
project-specific additions but must not contradict the canonical source.

## Public validator interface

```text
node scripts/validate-workflow.mjs <ai-workflow-directory> [--json]
```

The command exits zero when the workflow is valid and non-zero when it finds an
error. Human output must identify the file and actionable finding. JSON output
must contain `valid`, `errors`, `warnings`, and `summary`.

The validator must check at least:

1. required base and batch artifacts exist;
2. statuses use the correct entity vocabulary;
3. required task fields exist;
4. traceability rows use allowed states;
5. a `done` batch has no planned or blocked traceability row;
6. a `done` batch has an empty open-validation list and a passed final audit;
7. top-level lifecycle state agrees across batch artifacts and ledgers;
8. required validation commands for done work have recorded passing evidence;
9. every accepted gap has recorded user approval;
10. lifecycle transitions recorded in progress evidence are allowed.

## Eval acceptance bar

The eval suite covers intake, planning, normal execution, ambiguity, safe
assumptions, repository conflicts, validation failures, unauthorized actions, and
final-audit gaps.

A prompt or harness change is acceptable only when:

1. all hard safety, scope, lifecycle, validation, and evidence expectations pass;
2. no case incorrectly reports `done`;
3. the normal successful case has no unnecessary approval pause;
4. quality and required evidence do not regress;
5. prompt tokens, tool loops, latency, or cost improve or remain justified by a
   documented quality gain.

Both baseline and candidate run sets must be structurally complete and pass all
hard behavioral gates before non-regression or efficiency comparisons count.

Live model runs require separately authorized credentials, repository
transmission, and spend. The local suite must still validate fixture structure,
derive gates from recorded observations, grade run results, validate workflow
artifacts, and measure the prompt stack without network access. Until live runs
are authorized, `evals/results/status.json` must record that behavioral acceptance
is pending.

## Completion criteria

1. Canonical policies, prompts, templates, schema, adapter, evals, and validator
   exist and are documented.
2. The example workflow passes the validator.
3. Tests cover both a valid completed workflow and representative invalid states.
4. Static prompt checks confirm runtime prompts reference canonical policies and
   do not reintroduce the removed duplicated rule groups.
5. Baseline and post-change prompt-stack measurements are recorded.
6. The README and blueprint direct users to the new sources of truth.
7. A standards review and a spec review report no unresolved blocking findings.
