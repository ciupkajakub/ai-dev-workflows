import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { cp, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const runValidator = (...args) =>
  spawnSync(process.execPath, ["scripts/validate-workflow.mjs", ...args], {
    cwd: repoRoot,
    encoding: "utf8",
  });

const withWorkflowCopy = async (mutate, assertion) => {
  const root = await mkdtemp(path.join(tmpdir(), "ai-workflow-validator-"));
  const workflow = path.join(root, "ai-workflow");
  await cp(path.join(repoRoot, "example", "ai-workflow"), workflow, { recursive: true });
  try {
    await mutate(workflow);
    await assertion(workflow);
  } finally {
    await rm(root, { recursive: true, force: true });
  }
};

test("a completed example workflow passes through the public validator command", () => {
  const result = runValidator("example/ai-workflow", "--json");

  assert.equal(result.status, 0, result.stderr || result.stdout);
  const report = JSON.parse(result.stdout);
  assert.equal(report.valid, true);
  assert.deepEqual(report.errors, []);
  assert.equal(report.summary.batches, 1);
  assert.equal(report.summary.tasks, 2);
});

test("done work fails when a required command lacks recorded passing evidence", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const progress = path.join(workflow, "work", "B001-example-feature", "PROGRESS.md");
      const markdown = await readFile(progress, "utf8");
      await writeFile(
        progress,
        markdown.replaceAll("`npm test -- dashboard-query-plan.test.ts` passed.", "Query plan evidence omitted."),
      );
    },
    async (workflow) => {
      const result = runValidator(workflow, "--json");
      assert.equal(result.status, 1, result.stderr || result.stdout);
      const report = JSON.parse(result.stdout);
      assert.ok(report.errors.some((error) => error.code === "validation-not-passed"));
    },
  );
});

test("an accepted traceability gap fails without recorded user approval", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const implementation = path.join(
        workflow,
        "work",
        "B001-example-feature",
        "IMPLEMENTATION.md",
      );
      const markdown = await readFile(implementation, "utf8");
      await writeFile(
        implementation,
        markdown.replace(
          "| Functional requirement 1 | Overdue means incomplete task due before the user's current local date. | T001 | `npm test -- dashboard-task-query.test.ts` | verified |",
          "| Functional requirement 1 | Overdue means incomplete task due before the user's current local date. | T001 | User decision | accepted_gap |",
        ),
      );
    },
    async (workflow) => {
      const result = runValidator(workflow, "--json");
      assert.equal(result.status, 1, result.stderr || result.stdout);
      const report = JSON.parse(result.stdout);
      assert.ok(report.errors.some((error) => error.code === "accepted-gap-without-approval"));
    },
  );
});

test("a negated approval statement does not authorize an accepted gap", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const implementation = path.join(workflow, "work", "B001-example-feature", "IMPLEMENTATION.md");
      await writeFile(
        implementation,
        (await readFile(implementation, "utf8")).replace(
          "| Functional requirement 1 | Overdue means incomplete task due before the user's current local date. | T001 | `npm test -- dashboard-task-query.test.ts` | verified |",
          "| Functional requirement 1 | Overdue means incomplete task due before the user's current local date. | T001 | User decision | accepted_gap |",
        ),
      );
      const progress = path.join(workflow, "work", "B001-example-feature", "PROGRESS.md");
      await writeFile(
        progress,
        `${await readFile(progress, "utf8")}\n- Functional requirement 1: user has not approved this gap.\n`,
      );
    },
    async (workflow) => {
      const report = JSON.parse(runValidator(workflow, "--json").stdout);
      assert.ok(report.errors.some((error) => error.code === "accepted-gap-without-approval"));
    },
  );
});

test("negated validation language is not passing evidence", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const progress = path.join(workflow, "work", "B001-example-feature", "PROGRESS.md");
      await writeFile(
        progress,
        (await readFile(progress, "utf8")).replaceAll(
          "`npm test -- dashboard-query-plan.test.ts` passed.",
          "`npm test -- dashboard-query-plan.test.ts` has not passed.",
        ),
      );
    },
    async (workflow) => {
      const report = JSON.parse(runValidator(workflow, "--json").stdout);
      assert.ok(report.errors.some((error) => error.code === "validation-not-passed"));
    },
  );
});

test("negated contractions are not passing evidence", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const progress = path.join(workflow, "work", "B001-example-feature", "PROGRESS.md");
      await writeFile(
        progress,
        (await readFile(progress, "utf8")).replaceAll(
          "`npm test -- dashboard-query-plan.test.ts` passed.",
          "`npm test -- dashboard-query-plan.test.ts` wasn't passed.",
        ),
      );
    },
    async (workflow) => {
      const report = JSON.parse(runValidator(workflow, "--json").stdout);
      assert.ok(report.errors.some((error) => error.code === "validation-not-passed"));
    },
  );
});

test("recorded lifecycle paths reject transitions outside the schema", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const progress = path.join(workflow, "work", "B001-example-feature", "PROGRESS.md");
      const markdown = await readFile(progress, "utf8");
      await writeFile(progress, `${markdown}\n- T001 \`done -> planned\` after reopening completed work.\n`);
    },
    async (workflow) => {
      const result = runValidator(workflow, "--json");
      assert.equal(result.status, 1, result.stderr || result.stdout);
      const report = JSON.parse(result.stdout);
      assert.ok(report.errors.some((error) => error.code === "invalid-transition"));
    },
  );
});

test("a completed batch fails when its source backlog item is not done", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const backlog = path.join(workflow, "PRODUCT_BACKLOG.md");
      const markdown = await readFile(backlog, "utf8");
      await writeFile(
        backlog,
        markdown.replace(
          "| NMI-001 | done | high |",
          "| NMI-001 | active | high |",
        ),
      );
    },
    async (workflow) => {
      const result = runValidator(workflow, "--json");
      assert.equal(result.status, 1, result.stderr || result.stdout);
      const report = JSON.parse(result.stdout);
      assert.ok(report.errors.some((error) => error.code === "inconsistent-backlog-status"));
    },
  );
});

test("a batch at spec or later requires its artifact directory", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const index = path.join(workflow, "WORK_INDEX.md");
      const markdown = await readFile(index, "utf8");
      await writeFile(
        index,
        markdown.replace(
          "| B002 | planned | NMI-002 |",
          "| B002 | spec | NMI-002 |",
        ),
      );
      const backlog = path.join(workflow, "PRODUCT_BACKLOG.md");
      const backlogMarkdown = await readFile(backlog, "utf8");
      await writeFile(
        backlog,
        backlogMarkdown.replace("| NMI-002 | planned | medium |", "| NMI-002 | spec | medium |"),
      );
    },
    async (workflow) => {
      const result = runValidator(workflow, "--json");
      assert.equal(result.status, 1, result.stderr || result.stdout);
      const report = JSON.parse(result.stdout);
      assert.ok(report.errors.some((error) => error.code === "missing-batch-directory"));
    },
  );
});

test("a batch folder cannot escape or alias the work directory", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const index = path.join(workflow, "WORK_INDEX.md");
      await writeFile(
        index,
        (await readFile(index, "utf8")).replace(
          "work/B001-example-feature/",
          "../ai-workflow/",
        ),
      );
    },
    async (workflow) => {
      const result = runValidator(workflow, "--json");
      assert.equal(result.status, 1, result.stderr || result.stdout);
      assert.ok(
        JSON.parse(result.stdout).errors.some((error) => error.code === "invalid-batch-folder"),
      );
    },
  );
});

test("a spec batch is valid with only its feature contract", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const batch = path.join(workflow, "work", "B001-example-feature");
      await Promise.all([
        rm(path.join(batch, "IMPLEMENTATION.md")),
        rm(path.join(batch, "PROGRESS.md")),
        rm(path.join(batch, "PROGRESS_STATE.md")),
      ]);
      const feature = path.join(batch, "FEATURE.md");
      await writeFile(feature, (await readFile(feature, "utf8")).replace("Status: `done`", "Status: `spec`"));
      const index = path.join(workflow, "WORK_INDEX.md");
      await writeFile(index, (await readFile(index, "utf8")).replace("| B001 | done |", "| B001 | spec |"));
      const backlog = path.join(workflow, "PRODUCT_BACKLOG.md");
      await writeFile(backlog, (await readFile(backlog, "utf8")).replace("| NMI-001 | done |", "| NMI-001 | spec |"));
    },
    async (workflow) => {
      const result = runValidator(workflow, "--json");
      assert.equal(result.status, 0, result.stderr || result.stdout);
      assert.equal(JSON.parse(result.stdout).valid, true);
    },
  );
});

test("an empty planned batch folder does not crash validation", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const batch = path.join(workflow, "work", "B002-reminder-preferences");
      await cp(path.join(workflow, "work", "B001-example-feature"), batch, { recursive: true });
      await Promise.all([
        rm(path.join(batch, "FEATURE.md")),
        rm(path.join(batch, "IMPLEMENTATION.md")),
        rm(path.join(batch, "PROGRESS.md")),
        rm(path.join(batch, "PROGRESS_STATE.md")),
      ]);
    },
    async (workflow) => {
      const result = runValidator(workflow, "--json");
      assert.equal(result.status, 0, result.stderr || result.stdout);
      assert.equal(JSON.parse(result.stdout).valid, true);
    },
  );
});

test("non-done batch artifacts must agree with lifecycle ownership", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const index = path.join(workflow, "WORK_INDEX.md");
      await writeFile(index, (await readFile(index, "utf8")).replace("| B001 | done |", "| B001 | active |"));
      const backlog = path.join(workflow, "PRODUCT_BACKLOG.md");
      await writeFile(backlog, (await readFile(backlog, "utf8")).replace("| NMI-001 | done |", "| NMI-001 | active |"));
    },
    async (workflow) => {
      const result = runValidator(workflow, "--json");
      assert.equal(result.status, 1, result.stderr || result.stdout);
      const report = JSON.parse(result.stdout);
      assert.ok(report.errors.some((error) => error.code === "inconsistent-artifact-status"));
    },
  );
});

test("a ready or later batch requires at least one task", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const file = path.join(workflow, "work", "B001-example-feature", "IMPLEMENTATION.md");
      const markdown = await readFile(file, "utf8");
      await writeFile(file, markdown.replace(/## Tasks\n\n```yaml[\s\S]*?```/, "## Tasks\n\n```yaml\n```"));
    },
    async (workflow) => {
      const result = runValidator(workflow, "--json");
      assert.equal(result.status, 1, result.stderr || result.stdout);
      const report = JSON.parse(result.stdout);
      assert.ok(report.errors.some((error) => error.code === "missing-tasks"));
      assert.ok(report.errors.some((error) => error.code === "unknown-task-reference"));
    },
  );
});

test("a ready or later batch requires traceability rows", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const file = path.join(workflow, "work", "B001-example-feature", "IMPLEMENTATION.md");
      const markdown = await readFile(file, "utf8");
      await writeFile(
        file,
        markdown.replace(/(\| --- \| --- \| --- \| --- \| --- \|\n)(?:\|.*\n)+/, "$1"),
      );
    },
    async (workflow) => {
      const result = runValidator(workflow, "--json");
      assert.equal(result.status, 1, result.stderr || result.stdout);
      const report = JSON.parse(result.stdout);
      assert.ok(report.errors.some((error) => error.code === "missing-traceability"));
    },
  );
});

test("superseded artifacts must agree with the superseded ledger state", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const index = path.join(workflow, "WORK_INDEX.md");
      await writeFile(index, (await readFile(index, "utf8")).replace("| B001 | done |", "| B001 | superseded |"));
      const backlog = path.join(workflow, "PRODUCT_BACKLOG.md");
      await writeFile(backlog, (await readFile(backlog, "utf8")).replace("| NMI-001 | done |", "| NMI-001 | superseded |"));
    },
    async (workflow) => {
      const result = runValidator(workflow, "--json");
      assert.equal(result.status, 1, result.stderr || result.stdout);
      const report = JSON.parse(result.stdout);
      assert.ok(report.errors.some((error) => error.code === "inconsistent-artifact-status"));
    },
  );
});

test("a contract may be superseded before planning artifacts exist", async () => {
  await withWorkflowCopy(
    async (workflow) => {
      const batch = path.join(workflow, "work", "B001-example-feature");
      await Promise.all([
        rm(path.join(batch, "IMPLEMENTATION.md")),
        rm(path.join(batch, "PROGRESS.md")),
        rm(path.join(batch, "PROGRESS_STATE.md")),
      ]);
      const feature = path.join(batch, "FEATURE.md");
      await writeFile(
        feature,
        (await readFile(feature, "utf8")).replace("Status: `done`", "Status: `superseded`"),
      );
      const index = path.join(workflow, "WORK_INDEX.md");
      await writeFile(index, (await readFile(index, "utf8")).replace("| B001 | done |", "| B001 | superseded |"));
      const backlog = path.join(workflow, "PRODUCT_BACKLOG.md");
      await writeFile(backlog, (await readFile(backlog, "utf8")).replace("| NMI-001 | done |", "| NMI-001 | superseded |"));
    },
    async (workflow) => {
      const result = runValidator(workflow, "--json");
      assert.equal(result.status, 0, result.stderr || result.stdout);
      assert.equal(JSON.parse(result.stdout).valid, true);
    },
  );
});

const invalidWorkflowCases = [
  {
    name: "a missing required batch artifact",
    code: "missing-batch-file",
    mutate: async (workflow) =>
      rm(path.join(workflow, "work", "B001-example-feature", "FEATURE.md")),
  },
  {
    name: "an invalid task status",
    code: "invalid-task-status",
    mutate: async (workflow) => {
      const file = path.join(workflow, "work", "B001-example-feature", "IMPLEMENTATION.md");
      const markdown = await readFile(file, "utf8");
      await writeFile(file, markdown.replace("  status: done", "  status: complete"));
    },
  },
  {
    name: "a task missing a required field",
    code: "missing-task-fields",
    mutate: async (workflow) => {
      const file = path.join(workflow, "work", "B001-example-feature", "IMPLEMENTATION.md");
      const markdown = await readFile(file, "utf8");
      await writeFile(file, markdown.replace("  goal: Return incomplete tasks due before the user's local date.\n", ""));
    },
  },
  {
    name: "an unknown traceability state",
    code: "invalid-traceability-state",
    mutate: async (workflow) => {
      const file = path.join(workflow, "work", "B001-example-feature", "IMPLEMENTATION.md");
      const markdown = await readFile(file, "utf8");
      await writeFile(file, markdown.replace("| verified |", "| uncertain |"));
    },
  },
  {
    name: "an open traceability row on done work",
    code: "open-traceability",
    mutate: async (workflow) => {
      const file = path.join(workflow, "work", "B001-example-feature", "IMPLEMENTATION.md");
      const markdown = await readFile(file, "utf8");
      await writeFile(file, markdown.replace("| verified |", "| planned |"));
    },
  },
  {
    name: "an open validation item on a done batch",
    code: "open-validation",
    mutate: async (workflow) => {
      const file = path.join(workflow, "work", "B001-example-feature", "PROGRESS_STATE.md");
      const markdown = await readFile(file, "utf8");
      await writeFile(file, markdown.replace("## Open validation list\n\n- None.", "## Open validation list\n\n- Rerun dashboard suite."));
    },
  },
  {
    name: "an open validation item hidden below a None marker",
    code: "open-validation",
    mutate: async (workflow) => {
      const file = path.join(workflow, "work", "B001-example-feature", "PROGRESS_STATE.md");
      const markdown = await readFile(file, "utf8");
      await writeFile(
        file,
        markdown.replace(
          "## Open validation list\n\n- None.",
          "## Open validation list\n\n- None.\n- Rerun dashboard suite.",
        ),
      );
    },
  },
  {
    name: "a done batch without a passed final audit",
    code: "final-audit-not-passed",
    mutate: async (workflow) => {
      const file = path.join(workflow, "work", "B001-example-feature", "PROGRESS_STATE.md");
      const markdown = await readFile(file, "utf8");
      await writeFile(file, markdown.replace("- Passed.", "- Failed."));
    },
  },
  {
    name: "a contradictory failed final audit",
    code: "final-audit-not-passed",
    mutate: async (workflow) => {
      const file = path.join(workflow, "work", "B001-example-feature", "PROGRESS_STATE.md");
      const markdown = await readFile(file, "utf8");
      await writeFile(
        file,
        markdown.replace("- Passed.\n- Lifecycle statuses", "- Passed.\n- Validation pending.\n- Lifecycle statuses"),
      );
    },
  },
];

for (const invalidCase of invalidWorkflowCases) {
  test(`the validator rejects ${invalidCase.name}`, async () => {
    await withWorkflowCopy(invalidCase.mutate, async (workflow) => {
      const result = runValidator(workflow, "--json");
      assert.equal(result.status, 1, result.stderr || result.stdout);
      const report = JSON.parse(result.stdout);
      assert.ok(
        report.errors.some((error) => error.code === invalidCase.code),
        JSON.stringify(report, null, 2),
      );
    });
  });
}
