import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const recordedRunFor = (evalCase) => ({
  case_id: evalCase.id,
  model: "gpt-5.6",
  reasoning_effort: "medium",
  verbosity: "medium",
  tools: ["shell", "apply_patch"],
  harness_revision: "test-harness",
  prompt_revision: "candidate",
  recorded_at: "2026-07-15T12:00:00Z",
  trace_path: "evals/results/traces/test.json",
  reviewer: "test-reviewer",
  observed_lifecycle: evalCase.expected_lifecycle,
  artifact_changes: evalCase.required_artifact_changes,
  evidence: evalCase.required_evidence,
  actions: [],
  assumptions: [],
  final_output: {
    ...Object.fromEntries(evalCase.expected_final_fields.map((field) => [field, true])),
    ...evalCase.expected_final_values,
  },
  unnecessary_approval_pauses: 0,
  quality_metrics: {
    correctness: 1,
    artifact_completeness: 1,
    blocker_accuracy: 1,
    final_answer_completeness: 1,
  },
  efficiency_metrics: {
    input_tokens: 1000,
    output_tokens: 200,
    tool_calls: 2,
    turns: 1,
    retries: 0,
    latency_ms: 100,
    estimated_cost: null,
  },
});

const pairedRunsFor = (cases) => ({
  baseline: cases.map((evalCase) => {
    const run = recordedRunFor(evalCase);
    run.prompt_revision = "baseline";
    run.efficiency_metrics.input_tokens = 1200;
    run.efficiency_metrics.output_tokens = 250;
    return run;
  }),
  candidate: cases.map(recordedRunFor),
});

test("the eval runner accepts the complete representative fixture set", () => {
  const result = spawnSync(
    process.execPath,
    ["scripts/evaluate-workflow-runs.mjs", "--validate-fixtures", "--json"],
    { cwd: repoRoot, encoding: "utf8" },
  );

  assert.equal(result.status, 0, result.stderr || result.stdout);
  const report = JSON.parse(result.stdout);
  assert.equal(report.valid, true);
  assert.equal(report.case_count, 9);
});

test("the eval runner accepts a complete run only when every hard gate passes", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "ai-workflow-evals-"));
  try {
    const cases = JSON.parse(
      await readFile(path.join(repoRoot, "evals", "cases", "workflow-cases.json"), "utf8"),
    );
    const runs = pairedRunsFor(cases);
    const file = path.join(root, "runs.json");
    await writeFile(file, JSON.stringify(runs));

    const result = spawnSync(
      process.execPath,
      ["scripts/evaluate-workflow-runs.mjs", "--runs", file, "--json"],
      { cwd: repoRoot, encoding: "utf8" },
    );

    assert.equal(result.status, 0, result.stderr || result.stdout);
    const report = JSON.parse(result.stdout);
    assert.equal(report.valid, true);
    assert.equal(report.passed, 9);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("the eval runner rejects a recorded run with any failed hard gate", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "ai-workflow-evals-"));
  try {
    const cases = JSON.parse(
      await readFile(path.join(repoRoot, "evals", "cases", "workflow-cases.json"), "utf8"),
    );
    const runs = pairedRunsFor(cases);
    runs.candidate[0].actions = [cases[0].prohibited_actions[0]];
    const file = path.join(root, "runs.json");
    await writeFile(file, JSON.stringify(runs));

    const result = spawnSync(
      process.execPath,
      ["scripts/evaluate-workflow-runs.mjs", "--runs", file, "--json"],
      { cwd: repoRoot, encoding: "utf8" },
    );

    assert.equal(result.status, 1, result.stderr || result.stdout);
    const report = JSON.parse(result.stdout);
    assert.equal(report.valid, false);
    assert.equal(report.results[0].gate_results.scope_adherence, false);
    assert.ok(report.results[0].failures.some((failure) => failure.includes("prohibited action")));
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("the eval runner rejects an invalid baseline even when the candidate passes", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "ai-workflow-evals-"));
  try {
    const cases = JSON.parse(
      await readFile(path.join(repoRoot, "evals", "cases", "workflow-cases.json"), "utf8"),
    );
    const runs = pairedRunsFor(cases);
    delete runs.baseline[0].quality_metrics.correctness;
    const file = path.join(root, "runs.json");
    await writeFile(file, JSON.stringify(runs));

    const result = spawnSync(
      process.execPath,
      ["scripts/evaluate-workflow-runs.mjs", "--runs", file, "--json"],
      { cwd: repoRoot, encoding: "utf8" },
    );

    assert.equal(result.status, 1, result.stderr || result.stdout);
    const report = JSON.parse(result.stdout);
    assert.equal(report.valid, false);
    assert.equal(report.baseline_failed, 1);
    assert.ok(
      report.baseline_results[0].failures.includes("missing quality metric: correctness"),
    );
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("the eval runner rejects a false completion value even when all expected fields exist", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "ai-workflow-evals-"));
  try {
    const cases = JSON.parse(
      await readFile(path.join(repoRoot, "evals", "cases", "workflow-cases.json"), "utf8"),
    );
    const runs = pairedRunsFor(cases);
    const index = cases.findIndex((evalCase) => evalCase.id === "final-audit-gap");
    runs.candidate[index].final_output.may_mark_done = true;
    const file = path.join(root, "runs.json");
    await writeFile(file, JSON.stringify(runs));

    const result = spawnSync(
      process.execPath,
      ["scripts/evaluate-workflow-runs.mjs", "--runs", file, "--json"],
      { cwd: repoRoot, encoding: "utf8" },
    );

    assert.equal(result.status, 1, result.stderr || result.stdout);
    const report = JSON.parse(result.stdout);
    const audit = report.results.find((item) => item.case_id === "final-audit-gap");
    assert.equal(audit.gate_results.no_false_completion, false);
    assert.ok(audit.failures.some((failure) => failure.includes("incorrect final value")));
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("the eval runner rejects done state for an entity outside the case contract", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "ai-workflow-evals-"));
  try {
    const cases = JSON.parse(
      await readFile(path.join(repoRoot, "evals", "cases", "workflow-cases.json"), "utf8"),
    );
    const runs = pairedRunsFor(cases);
    const index = cases.findIndex((evalCase) => evalCase.id === "normal-task-success");
    runs.candidate[index].observed_lifecycle = { task: "done", batch: "done" };
    const file = path.join(root, "runs.json");
    await writeFile(file, JSON.stringify(runs));

    const result = spawnSync(
      process.execPath,
      ["scripts/evaluate-workflow-runs.mjs", "--runs", file, "--json"],
      { cwd: repoRoot, encoding: "utf8" },
    );

    assert.equal(result.status, 1, result.stderr || result.stdout);
    const report = JSON.parse(result.stdout);
    const normal = report.results.find((item) => item.case_id === "normal-task-success");
    assert.equal(normal.gate_results.lifecycle_state, false);
    assert.equal(normal.gate_results.no_false_completion, false);
    assert.ok(normal.failures.includes("unexpected done lifecycle: batch"));
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("the eval runner rejects candidate quality regression against baseline", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "ai-workflow-evals-"));
  try {
    const cases = JSON.parse(
      await readFile(path.join(repoRoot, "evals", "cases", "workflow-cases.json"), "utf8"),
    );
    const runs = pairedRunsFor(cases);
    runs.candidate[0].quality_metrics.correctness = 0.5;
    const file = path.join(root, "runs.json");
    await writeFile(file, JSON.stringify(runs));

    const result = spawnSync(
      process.execPath,
      ["scripts/evaluate-workflow-runs.mjs", "--runs", file, "--json"],
      { cwd: repoRoot, encoding: "utf8" },
    );

    assert.equal(result.status, 1, result.stderr || result.stdout);
    assert.ok(
      JSON.parse(result.stdout).results[0].failures.includes("quality regressed: correctness"),
    );
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});

test("the eval runner rejects an efficiency regression without a justified quality gain", async () => {
  const root = await mkdtemp(path.join(tmpdir(), "ai-workflow-evals-"));
  try {
    const cases = JSON.parse(
      await readFile(path.join(repoRoot, "evals", "cases", "workflow-cases.json"), "utf8"),
    );
    const runs = pairedRunsFor(cases);
    runs.candidate[0].efficiency_metrics.turns = 3;
    const file = path.join(root, "runs.json");
    await writeFile(file, JSON.stringify(runs));

    const result = spawnSync(
      process.execPath,
      ["scripts/evaluate-workflow-runs.mjs", "--runs", file, "--json"],
      { cwd: repoRoot, encoding: "utf8" },
    );

    assert.equal(result.status, 1, result.stderr || result.stdout);
    assert.ok(
      JSON.parse(result.stdout).results[0].failures.some((failure) =>
        failure.includes("efficiency regressed without justified quality gain: turns"),
      ),
    );
  } finally {
    await rm(root, { recursive: true, force: true });
  }
});
