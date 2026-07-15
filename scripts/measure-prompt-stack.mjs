#!/usr/bin/env node

import { execFileSync } from "node:child_process";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const configPath = path.join(repoRoot, "evals", "prompt-stacks.json");

const readSource = async (source, ref) => {
  const content = ref
    ? execFileSync("git", ["show", `${ref}:${source.file}`], {
        cwd: repoRoot,
        encoding: "utf8",
      })
    : await readFile(path.join(repoRoot, source.file), "utf8");

  const start = source.from_heading ? content.indexOf(source.from_heading) : 0;
  if (start === -1) throw new Error(`${source.file} is missing heading ${source.from_heading}.`);
  const end = source.to_heading ? content.indexOf(source.to_heading, start + 1) : content.length;
  if (end === -1) throw new Error(`${source.file} is missing heading ${source.to_heading}.`);
  return content.slice(start, end);
};

const count = (content) => ({
  words: content.trim().split(/\s+/).filter(Boolean).length,
  lines: content.split("\n").length,
  characters: content.length,
});

const duplicateLineCount = (contents) => {
  const frequencies = new Map();
  for (const content of contents) {
    for (const line of content.split("\n")) {
      const normalized = line.trim().toLowerCase().replace(/\s+/g, " ");
      if (normalized.length < 12 || /^[-#|`]+$/.test(normalized)) continue;
      frequencies.set(normalized, (frequencies.get(normalized) ?? 0) + 1);
    }
  }
  return [...frequencies.values()].reduce((total, frequency) => total + Math.max(0, frequency - 1), 0);
};

const measureStack = async (stack) => {
  const contents = await Promise.all(stack.sources.map((source) => readSource(source, stack.ref)));
  const sources = stack.sources.map((source, index) => ({ file: source.file, ...count(contents[index]) }));
  const totals = sources.reduce(
    (result, source) => ({
      words: result.words + source.words,
      lines: result.lines + source.lines,
      characters: result.characters + source.characters,
    }),
    { words: 0, lines: 0, characters: 0 },
  );
  return { ...(stack.ref ? { ref: stack.ref } : {}), ...totals, duplicate_lines: duplicateLineCount(contents), sources };
};

const percentReduction = (before, after) =>
  Math.round(((before - after) / before) * 1000) / 10;

export async function measurePromptStacks() {
  const config = JSON.parse(await readFile(configPath, "utf8"));
  const [baseline, candidate] = await Promise.all([
    measureStack(config.baseline),
    measureStack(config.candidate),
  ]);
  return {
    baseline,
    candidate,
    reduction: {
      words_percent: percentReduction(baseline.words, candidate.words),
      lines_percent: percentReduction(baseline.lines, candidate.lines),
      characters_percent: percentReduction(baseline.characters, candidate.characters),
      duplicate_lines_percent: percentReduction(baseline.duplicate_lines, candidate.duplicate_lines),
    },
  };
}

const report = await measurePromptStacks();
const json = process.argv.includes("--json");
console.log(
  json
    ? JSON.stringify(report, null, 2)
    : [
        `Prompt stack: ${report.baseline.words} -> ${report.candidate.words} words (${report.reduction.words_percent}% reduction).`,
        `Duplicate non-trivial lines: ${report.baseline.duplicate_lines} -> ${report.candidate.duplicate_lines}.`,
      ].join("\n"),
);
