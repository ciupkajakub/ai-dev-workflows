import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

test("prompt measurement compares the candidate with the pinned baseline", () => {
  const result = spawnSync(process.execPath, ["scripts/measure-prompt-stack.mjs", "--json"], {
    cwd: repoRoot,
    encoding: "utf8",
  });

  assert.equal(result.status, 0, result.stderr || result.stdout);
  const report = JSON.parse(result.stdout);
  assert.equal(report.baseline.ref, "46786cf9b1bcc1add37fc68a14775dba539afb53");
  assert.ok(report.baseline.words > report.candidate.words);
  assert.ok(report.reduction.words_percent >= 40);
});
