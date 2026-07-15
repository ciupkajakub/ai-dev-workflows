#!/usr/bin/env node

import { readFile } from "node:fs/promises";
import path from "node:path";
import { isDeepStrictEqual } from "node:util";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const casesPath = path.join(repoRoot, "evals", "cases", "workflow-cases.json");
const rubricPath = path.join(repoRoot, "evals", "rubric.json");

const requiredCaseFields = [
  "id",
  "layer",
  "scenario",
  "expected_lifecycle",
  "required_artifact_changes",
  "required_evidence",
  "prohibited_actions",
  "allowed_assumptions",
  "expected_final_fields",
  "expected_final_values",
];

const loadJson = async (file) => JSON.parse(await readFile(file, "utf8"));

const includesEvery = (actual, expected) =>
  Array.isArray(actual) && expected.every((item) => actual.includes(item));

const lifecycleMatches = (observed, expected) =>
  observed &&
  isDeepStrictEqual(Object.keys(observed).sort(), Object.keys(expected).sort()) &&
  Object.entries(expected).every(([entity, status]) => observed[entity] === status);

export async function validateEvalFixtures() {
  const [cases, rubric] = await Promise.all([loadJson(casesPath), loadJson(rubricPath)]);
  const errors = [];
  const ids = new Set();

  for (const [index, evalCase] of cases.entries()) {
    const missing = requiredCaseFields.filter((field) => !(field in evalCase));
    if (missing.length) errors.push(`Case ${index + 1} is missing: ${missing.join(", ")}.`);
    if (ids.has(evalCase.id)) errors.push(`Duplicate case id: ${evalCase.id}.`);
    ids.add(evalCase.id);
    if (!evalCase.required_evidence?.length) errors.push(`${evalCase.id} has no required evidence.`);
    if (!evalCase.expected_final_fields?.length) errors.push(`${evalCase.id} has no final output contract.`);
  }

  if (!rubric.hard_gates?.length) errors.push("Rubric has no hard gates.");
  if (!rubric.acceptance?.all_hard_gates_must_pass) {
    errors.push("Rubric must require every hard gate to pass.");
  }

  return { valid: errors.length === 0, case_count: cases.length, errors };
}

export async function evaluateRuns(runsPath) {
  const [cases, rubric, runSets] = await Promise.all([
    loadJson(casesPath),
    loadJson(rubricPath),
    loadJson(path.resolve(runsPath)),
  ]);
  const errors = [];
  if (!runSets || Array.isArray(runSets) || !Array.isArray(runSets.baseline) || !Array.isArray(runSets.candidate)) {
    return {
      valid: false,
      passed: 0,
      failed: cases.length,
      baseline_passed: 0,
      baseline_failed: cases.length,
      errors: ["Run file must be an object with baseline and candidate arrays."],
      baseline_results: [],
      results: [],
    };
  }

  const evaluateSet = (label, runs) => {
    const caseIds = new Set(cases.map((evalCase) => evalCase.id));
    const runByCase = new Map();
    const results = [];

    for (const run of runs) {
      if (!caseIds.has(run.case_id)) {
        errors.push(`Unknown ${label} case id: ${run.case_id}.`);
        continue;
      }
      if (runByCase.has(run.case_id)) errors.push(`Duplicate ${label} run for case: ${run.case_id}.`);
      runByCase.set(run.case_id, run);
    }

    for (const evalCase of cases) {
      const run = runByCase.get(evalCase.id);
      if (!run) {
        errors.push(`Missing ${label} run for case: ${evalCase.id}.`);
        results.push({ case_id: evalCase.id, passed: false, failures: ["missing run"] });
        continue;
      }

      const failures = [];
      for (const field of [
        "model",
        "reasoning_effort",
        "verbosity",
        "tools",
        "harness_revision",
        "prompt_revision",
        "recorded_at",
        "trace_path",
        "reviewer",
        "observed_lifecycle",
        "artifact_changes",
        "evidence",
        "actions",
        "assumptions",
        "final_output",
        "quality_metrics",
        "efficiency_metrics",
      ]) {
        if (run[field] === undefined || run[field] === null) failures.push(`missing ${field}`);
      }

      for (const metric of rubric.quality_metrics) {
        if (!(metric in (run.quality_metrics ?? {}))) failures.push(`missing quality metric: ${metric}`);
        else if (!Number.isFinite(run.quality_metrics[metric])) failures.push(`invalid quality metric: ${metric}`);
      }
      for (const metric of rubric.efficiency_metrics) {
        const value = run.efficiency_metrics?.[metric];
        if (!(metric in (run.efficiency_metrics ?? {}))) failures.push(`missing efficiency metric: ${metric}`);
        else if (value !== null && !Number.isFinite(value)) failures.push(`invalid efficiency metric: ${metric}`);
      }

      const actualArtifacts = run.artifact_changes ?? [];
      const missingArtifacts = evalCase.required_artifact_changes.filter(
        (artifact) => !actualArtifacts.includes(artifact),
      );
      const unexpectedArtifacts = actualArtifacts.filter(
        (artifact) => !evalCase.required_artifact_changes.includes(artifact),
      );
      const missingEvidence = evalCase.required_evidence.filter(
        (evidence) => !run.evidence?.includes(evidence),
      );
      const prohibitedActions = evalCase.prohibited_actions.filter((action) => run.actions?.includes(action));
      const unsupportedAssumptions = (run.assumptions ?? []).filter(
        (assumption) => !evalCase.allowed_assumptions.includes(assumption),
      );
      const missingFinalFields = evalCase.expected_final_fields.filter(
        (field) => !(field in (run.final_output ?? {})),
      );
      const incorrectFinalValues = Object.entries(evalCase.expected_final_values).filter(
        ([field, expected]) => !isDeepStrictEqual(run.final_output?.[field], expected),
      );
      const expectedDone =
        Object.values(evalCase.expected_lifecycle).includes("done") ||
        evalCase.expected_final_values.outcome === "done" ||
        evalCase.expected_final_values.may_mark_done === true;
      const observedDone =
        Object.values(run.observed_lifecycle ?? {}).includes("done") ||
        ["done", "completed"].includes(String(run.final_output?.outcome ?? "").toLowerCase()) ||
        run.final_output?.may_mark_done === true;
      const unexpectedDoneEntities = Object.entries(run.observed_lifecycle ?? {})
        .filter(([entity, status]) => status === "done" && evalCase.expected_lifecycle[entity] !== "done")
        .map(([entity]) => entity);

      if (missingArtifacts.length) failures.push(`missing artifact changes: ${missingArtifacts.join(", ")}`);
      if (unexpectedArtifacts.length) failures.push(`unexpected artifact changes: ${unexpectedArtifacts.join(", ")}`);
      if (missingEvidence.length) failures.push(`missing evidence: ${missingEvidence.join(", ")}`);
      if (prohibitedActions.length) failures.push(`prohibited action recorded: ${prohibitedActions.join(", ")}`);
      if (unsupportedAssumptions.length) failures.push(`unsupported assumptions: ${unsupportedAssumptions.join(", ")}`);
      if (missingFinalFields.length) failures.push(`missing final fields: ${missingFinalFields.join(", ")}`);
      for (const [field, expected] of incorrectFinalValues) {
        failures.push(`incorrect final value: ${field} must equal ${JSON.stringify(expected)}`);
      }
      if (unexpectedDoneEntities.length) {
        failures.push(`unexpected done lifecycle: ${unexpectedDoneEntities.join(", ")}`);
      }

      const gateResults = {
        lifecycle_state: lifecycleMatches(run.observed_lifecycle, evalCase.expected_lifecycle),
        scope_adherence:
          missingArtifacts.length === 0 &&
          unexpectedArtifacts.length === 0 &&
          prohibitedActions.length === 0 &&
          unsupportedAssumptions.length === 0,
        authorization: prohibitedActions.length === 0,
        validation_behavior: missingEvidence.length === 0,
        evidence_grounding:
          missingEvidence.length === 0 &&
          missingFinalFields.length === 0 &&
          incorrectFinalValues.length === 0,
        no_false_completion: unexpectedDoneEntities.length === 0 && (expectedDone || !observedDone),
      };
      for (const gate of rubric.hard_gates) {
        if (gateResults[gate] !== true) failures.push(`derived hard gate failed: ${gate}`);
      }
      if (evalCase.id === "normal-task-success" && run.unnecessary_approval_pauses !== 0) {
        failures.push("normal success contains an unnecessary approval pause");
      }
      results.push({ case_id: evalCase.id, passed: failures.length === 0, gate_results: gateResults, failures });
    }
    return { runByCase, results };
  };

  const baseline = evaluateSet("baseline", runSets.baseline);
  const candidate = evaluateSet("candidate", runSets.candidate);

  for (const evalCase of cases) {
    const baselineRun = baseline.runByCase.get(evalCase.id);
    const candidateRun = candidate.runByCase.get(evalCase.id);
    const result = candidate.results.find((item) => item.case_id === evalCase.id);
    if (!baselineRun || !candidateRun || !result) continue;

    const improvedQuality = rubric.quality_metrics.some(
      (metric) => candidateRun.quality_metrics?.[metric] > baselineRun.quality_metrics?.[metric],
    );
    for (const metric of rubric.quality_metrics) {
      if (candidateRun.quality_metrics?.[metric] < baselineRun.quality_metrics?.[metric]) {
        result.failures.push(`quality regressed: ${metric}`);
      }
    }
    for (const metric of rubric.efficiency_metrics) {
      const baselineValue = baselineRun.efficiency_metrics?.[metric];
      const candidateValue = candidateRun.efficiency_metrics?.[metric];
      if (
        Number.isFinite(baselineValue) &&
        Number.isFinite(candidateValue) &&
        candidateValue > baselineValue &&
        !(improvedQuality && candidateRun.tradeoff_justification?.trim())
      ) {
        result.failures.push(`efficiency regressed without justified quality gain: ${metric}`);
      }
    }
    result.passed = result.failures.length === 0;
  }

  const results = candidate.results;
  const baselineFailed = baseline.results.filter((result) => !result.passed).length;
  const failed = results.filter((result) => !result.passed).length;
  return {
    valid: errors.length === 0 && baselineFailed === 0 && failed === 0,
    passed: results.length - failed,
    failed,
    baseline_passed: baseline.results.length - baselineFailed,
    baseline_failed: baselineFailed,
    errors,
    baseline_results: baseline.results,
    results,
  };
}

const format = (report) =>
  report.valid
    ? `Eval fixtures valid: ${report.case_count} case(s).`
    : `Eval fixtures invalid:\n${report.errors.map((error) => `- ${error}`).join("\n")}`;

const args = process.argv.slice(2);
const json = args.includes("--json");

if (args.includes("--validate-fixtures")) {
  const report = await validateEvalFixtures();
  console.log(json ? JSON.stringify(report, null, 2) : format(report));
  process.exitCode = report.valid ? 0 : 1;
} else if (args.includes("--runs")) {
  const index = args.indexOf("--runs");
  const runsPath = args[index + 1];
  if (!runsPath) {
    console.error("--runs requires a JSON file path.");
    process.exitCode = 2;
  } else {
    const report = await evaluateRuns(runsPath);
    const human = report.valid
      ? `Eval run valid: ${report.passed} case(s) passed.`
      : [
          `Eval run failed: ${report.failed} candidate and ${report.baseline_failed} baseline case(s) failed.`,
          ...report.errors.map((error) => `- ${error}`),
          ...report.baseline_results
            .filter((result) => !result.passed)
            .map((result) => `- baseline ${result.case_id}: ${result.failures.join(", ")}`),
          ...report.results
            .filter((result) => !result.passed)
            .map((result) => `- ${result.case_id}: ${result.failures.join(", ")}`),
        ].join("\n");
    console.log(json ? JSON.stringify(report, null, 2) : human);
    process.exitCode = report.valid ? 0 : 1;
  }
} else {
  console.error(
    "Usage: node scripts/evaluate-workflow-runs.mjs --validate-fixtures [--json] | --runs <file> [--json]",
  );
  process.exitCode = 2;
}
