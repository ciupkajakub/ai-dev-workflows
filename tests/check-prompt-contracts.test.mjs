import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

test("canonical prompts satisfy the GPT-5.6 structural contract", () => {
  const result = spawnSync(process.execPath, ["scripts/check-prompt-contracts.mjs", "--json"], {
    cwd: repoRoot,
    encoding: "utf8",
  });

  assert.equal(result.status, 0, result.stderr || result.stdout);
  const report = JSON.parse(result.stdout);
  assert.equal(report.valid, true);
  assert.equal(report.checked_prompts, 5);
  assert.deepEqual(report.errors, []);
});
