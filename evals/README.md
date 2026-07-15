# Workflow evaluations

`cases/workflow-cases.json` contains the representative cases required by the
alignment specification. `rubric.json` separates hard behavioral gates from
quality and efficiency metrics.

Validate the fixture definitions locally:

```sh
npm run eval:fixtures
```

Live GPT-5.6 executions are intentionally not launched by the local runner. They
require separately authorized credentials and spend. Record paired baseline and
candidate results as JSON under `evals/results/`, then grade them with:

```sh
node scripts/evaluate-workflow-runs.mjs --runs evals/results/<file>.json
```

The run file has this top-level shape:

```json
{
  "baseline": [{ "case_id": "intake-clear" }],
  "candidate": [{ "case_id": "intake-clear" }]
}
```

Include one result per case in each array. Every result must identify the exact
model, reasoning effort, verbosity, tool set,
harness revision, prompt revision, case ID, timestamp, trace path, and reviewer.
It must record observed lifecycle, artifact changes, evidence, actions,
assumptions, final output fields, quality metrics, and efficiency metrics.

The runner derives every hard gate from those observations and the case contract;
results cannot supply their own gate values. It checks exact completion values,
rejects unexpected artifact changes, and compares candidate quality and
efficiency against the matching baseline case. Quality may not regress. An
efficiency regression is accepted only with a recorded justification and a
measured quality gain. Both baseline and candidate records must be structurally
complete and pass every behavioral hard gate; a failing baseline is not accepted
as a comparison reference. Observation labels must match the case contract so
the result remains traceable to the preserved run trace.
