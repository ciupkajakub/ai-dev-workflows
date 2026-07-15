#!/usr/bin/env node

import { readFile, readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const promptsRoot = path.join(repoRoot, "prompts");

const wordCount = (value) => value.trim().split(/\s+/).filter(Boolean).length;

const requiredPromptPatterns = [
  ["role", /^Role:/m],
  ["goal", /^Goal:/m],
  ["success criteria", /^Success criteria:/m],
  ["output", /^Output:/m],
  ["stop rules", /^Stop rules:/m],
];

const forbiddenDuplication = [
  /Final audit checklist/i,
  /Ask for explicit user approval before/i,
  /Use the strongest practical signal available/i,
  /more than (?:3|6|12) (?:source|implementation|acceptance)/i,
];

export async function checkPromptContracts() {
  const promptFiles = (await readdir(promptsRoot))
    .filter((file) => file.endsWith(".md"))
    .sort();
  const errors = [];

  for (const file of promptFiles) {
    const content = await readFile(path.join(promptsRoot, file), "utf8");
    for (const [label, pattern] of requiredPromptPatterns) {
      if (!pattern.test(content)) errors.push(`${file} is missing ${label}.`);
    }
    if (!/(?:canonical polic|AGENTS\.md)/i.test(content)) {
      errors.push(`${file} does not route to canonical policy.`);
    }
    for (const pattern of forbiddenDuplication) {
      if (pattern.test(content)) errors.push(`${file} repeats canonical rule: ${pattern}.`);
    }
    if (wordCount(content) > 350) errors.push(`${file} exceeds the 350-word prompt budget.`);
  }

  const [workflowPolicy, securityPolicy, adapter] = await Promise.all([
    readFile(path.join(repoRoot, "policies", "WORKFLOW.md"), "utf8"),
    readFile(path.join(repoRoot, "policies", "SECURITY.md"), "utf8"),
    readFile(path.join(repoRoot, "adapters", "openai-gpt-5.6.md"), "utf8"),
  ]);
  const policyStack = `${workflowPolicy}\n${securityPolicy}`;
  if (/more than (?:3|6|12) (?:source|implementation|acceptance)/i.test(policyStack)) {
    errors.push("Canonical policies contain hard numeric scope blockers.");
  }
  if (!/render every affected responsive state/i.test(workflowPolicy)) {
    errors.push("Workflow policy lacks the visual render-and-inspect gate.");
  }
  for (const requirement of [
    "gpt-5.6",
    "reasoning effort",
    "text.verbosity",
    "prompt caching",
    "task-relevant tools",
    "programmatic tool calling",
    "phase values",
    "render and inspect",
  ]) {
    if (!adapter.toLowerCase().includes(requirement.toLowerCase())) {
      errors.push(`GPT-5.6 adapter is missing ${requirement}.`);
    }
  }

  return { valid: errors.length === 0, checked_prompts: promptFiles.length, errors };
}

const report = await checkPromptContracts();
const json = process.argv.includes("--json");
console.log(
  json
    ? JSON.stringify(report, null, 2)
    : report.valid
      ? `Prompt contracts valid: ${report.checked_prompts} prompt(s).`
      : `Prompt contracts invalid:\n${report.errors.map((error) => `- ${error}`).join("\n")}`,
);
process.exitCode = report.valid ? 0 : 1;
