#!/usr/bin/env node

import { readFile, readdir, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const schemaPath = path.join(repoRoot, "schema", "workflow.schema.json");

const readText = (file) => readFile(file, "utf8");

const finding = (code, file, message) => ({ code, file, message });

const relativeTo = (root, file) => path.relative(root, file) || ".";

const parseMarkdownTable = (markdown, heading) => {
  const start = markdown.indexOf(heading);
  if (start === -1) return [];
  const afterHeading = markdown.slice(start + heading.length);
  const lines = afterHeading.split("\n");
  const rows = [];
  let tableStarted = false;

  for (const line of lines) {
    if (!line.trim().startsWith("|")) {
      if (tableStarted && line.trim()) break;
      continue;
    }
    tableStarted = true;
    const cells = line
      .split("|")
      .slice(1, -1)
      .map((cell) => cell.trim().replaceAll("`", ""));
    if (cells.every((cell) => /^-+$/.test(cell.replaceAll(" ", "")))) continue;
    rows.push(cells);
  }

  if (rows.length < 2) return [];
  const [headers, ...data] = rows;
  return data.map((cells) =>
    Object.fromEntries(headers.map((header, index) => [header, cells[index] ?? ""])),
  );
};

const parseTopLevelStatus = (markdown) =>
  markdown.match(/^Status:\s*`?([a-z_]+)`?\s*$/m)?.[1] ?? null;

const parseTasks = (markdown) => {
  const taskBlock = markdown.match(/```ya?ml\s*\n([\s\S]*?)```/i)?.[1] ?? "";
  const starts = [...taskBlock.matchAll(/^- id:\s*(T\d+)\s*$/gm)];

  return starts.map((match, index) => {
    const block = taskBlock.slice(match.index, starts[index + 1]?.index ?? taskBlock.length);
    const fields = new Set(
      [...block.matchAll(/^\s{2}([a-z_]+):(?:\s|$)/gm)].map((field) => field[1]),
    );
    fields.add("id");
    return {
      id: match[1],
      status: block.match(/^\s{2}status:\s*([a-z_]+)\s*$/m)?.[1] ?? null,
      fields,
      block,
      requiredValidationCommands: parseRequiredValidationCommands(block),
    };
  });
};

const parseRequiredValidationCommands = (taskBlock) => {
  const section = taskBlock.match(
    /^\s{2}validation_commands:\s*$([\s\S]*?)(?=^\s{2}existing_checks_to_rerun:|(?![\s\S]))/m,
  )?.[1];
  if (!section) return [];

  return [...section.matchAll(/^\s{4}- command:\s*["']?(.+?)["']?\s*$([\s\S]*?)(?=^\s{4}- command:|(?![\s\S]))/gm)]
    .filter((match) => /^\s{6}required:\s*true\s*$/m.test(match[2]))
    .map((match) => match[1].trim().replace(/["']$/, ""));
};

const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

const hasPositiveEvidenceLanguage = (line) =>
  /\b(?:passed|succeeded|confirmed|showed|approved|accepted)\b/i.test(line) &&
  !/\b(?:not|never|denied|declined|pending|stale|outdated|unverified|failed|failing|failure|cannot|can['’]?t|has(?:n['’]?t|nt)|was(?:n['’]?t|nt)|is(?:n['’]?t|nt)|did(?:n['’]?t|nt))\b/i.test(
    line,
  );

const hasPassingCommandEvidence = (progress, command) => {
  const commandPattern = new RegExp(`(?:\`${escapeRegExp(command)}\`|${escapeRegExp(command)})`, "i");
  const lines = progress.split("\n");
  if (lines.some((line) => commandPattern.test(line) && hasPositiveEvidenceLanguage(line))) return true;

  if (/^manual\s/i.test(command)) {
    const keywords = command
      .toLowerCase()
      .split(/[^a-z0-9]+/)
      .filter((word) => word.length > 3 && !["with", "manual", "check"].includes(word));
    return lines.some((line) => {
      const normalized = line.toLowerCase();
      const matched = keywords.filter((word) => normalized.includes(word));
      return matched.length >= Math.min(3, keywords.length) && hasPositiveEvidenceLanguage(line);
    });
  }

  return false;
};

const sectionHasNone = (markdown, heading) => {
  const start = markdown.indexOf(heading);
  if (start === -1) return false;
  const section = markdown.slice(start + heading.length).split(/^##\s/m)[0];
  const entries = section
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  return entries.length === 1 && /^-\s+None\.?$/i.test(entries[0]);
};

const finalAuditPassed = (markdown) => {
  const start = markdown.indexOf("## Final audit");
  if (start === -1) return false;
  const section = markdown.slice(start).split(/^##\s/m)[1] ?? markdown.slice(start);
  const entries = section
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  return (
    entries[0] === "Final audit" &&
    /^-\s+Passed\.?$/i.test(entries[1] ?? "") &&
    !entries.slice(2).some((line) => /\b(?:failed|not passed|pending)\b/i.test(line))
  );
};

const parseRecordedTransitions = (progress) => {
  const transitions = [];
  for (const match of progress.matchAll(/\b(NMI-\d+|B\d+|T\d+)\s+`([a-z_]+(?:\s*->\s*[a-z_]+)+)`/g)) {
    const entity = match[1];
    const states = match[2].split(/\s*->\s*/);
    const type = entity.startsWith("NMI-") ? "backlog" : entity.startsWith("B") ? "batch" : "task";
    for (let index = 0; index < states.length - 1; index += 1) {
      transitions.push({ entity, type, transition: `${states[index]}->${states[index + 1]}` });
    }
  }
  return transitions;
};

const existingBatchDirectories = async (workflowRoot) => {
  const workRoot = path.join(workflowRoot, "work");
  try {
    return (await readdir(workRoot, { withFileTypes: true }))
      .filter((entry) => entry.isDirectory())
      .map((entry) => path.join(workRoot, entry.name));
  } catch {
    return [];
  }
};

const resolveBatchFolder = (workflowRoot, row) => {
  const workRoot = path.resolve(workflowRoot, "work");
  const configuredFolder = row.Folder.replace(/^ai-workflow\//, "").replace(/\/$/, "");
  const target = path.resolve(workflowRoot, configuredFolder);
  const relative = path.relative(workRoot, target);
  if (
    !relative ||
    relative.startsWith("..") ||
    path.isAbsolute(relative) ||
    relative.includes(path.sep) ||
    !path.basename(target).startsWith(`${row.Batch}-`)
  ) {
    return null;
  }
  return target;
};

export async function validateWorkflow(workflowRootInput) {
  const workflowRoot = path.resolve(workflowRootInput);
  const schema = JSON.parse(await readText(schemaPath));
  const errors = [];
  const warnings = [];
  let taskCount = 0;

  for (const required of schema.required_base_files) {
    const target = path.join(workflowRoot, required);
    try {
      await readFile(target);
    } catch {
      errors.push(finding("missing-base-file", required, `Required file ${required} is missing.`));
    }
  }

  let workIndex = "";
  let backlog = "";
  try {
    [workIndex, backlog] = await Promise.all([
      readText(path.join(workflowRoot, "WORK_INDEX.md")),
      readText(path.join(workflowRoot, "PRODUCT_BACKLOG.md")),
    ]);
  } catch {
    return {
      valid: false,
      errors,
      warnings,
      summary: { batches: 0, tasks: 0 },
    };
  }

  const batchRows = parseMarkdownTable(workIndex, "## Batch queue");
  const backlogRows = parseMarkdownTable(backlog, "## Backlog index");

  for (const row of batchRows) {
    if (!schema.entity_statuses.batch.includes(row.Status)) {
      errors.push(
        finding("invalid-batch-status", "WORK_INDEX.md", `${row.Batch} uses invalid status ${row.Status}.`),
      );
    }
  }

  for (const row of batchRows.filter(
    (batch) => schema.lifecycle_expectations[batch.Status]?.directory_required,
  )) {
    const target = resolveBatchFolder(workflowRoot, row);
    if (!target) {
      errors.push(
        finding(
          "invalid-batch-folder",
          "WORK_INDEX.md",
          `${row.Batch} folder must be one direct child of work/ named for the batch: ${row.Folder}.`,
        ),
      );
      continue;
    }
    try {
      if (!(await stat(target)).isDirectory()) throw new Error("not a directory");
    } catch {
      errors.push(
        finding(
          "missing-batch-directory",
          "WORK_INDEX.md",
          `${row.Batch} status ${row.Status} requires artifact directory ${row.Folder}.`,
        ),
      );
    }
  }

  for (const row of backlogRows) {
    if (!schema.entity_statuses.backlog.includes(row.Status)) {
      errors.push(
        finding("invalid-backlog-status", "PRODUCT_BACKLOG.md", `${row.ID} uses invalid status ${row.Status}.`),
      );
    }
  }

  const batchDirectories = await existingBatchDirectories(workflowRoot);
  for (const batchDirectory of batchDirectories) {
    const batchName = path.basename(batchDirectory);
    const batchId = batchName.match(/^(B\d+)/)?.[1] ?? batchName;
    const indexRow = batchRows.find((row) => row.Batch === batchId);
    if (!indexRow) {
      errors.push(
        finding("missing-batch-row", "WORK_INDEX.md", `${batchId} has artifacts but no batch queue row.`),
      );
      continue;
    }
    if (resolveBatchFolder(workflowRoot, indexRow) !== path.resolve(batchDirectory)) {
      errors.push(
        finding(
          "batch-folder-mismatch",
          "WORK_INDEX.md",
          `${batchId} artifacts are in ${relativeTo(workflowRoot, batchDirectory)}, but its queue row points to ${indexRow.Folder}.`,
        ),
      );
      continue;
    }

    const files = Object.fromEntries(
      schema.required_batch_files.map((file) => [file, path.join(batchDirectory, file)]),
    );
    const contents = {};
    const lifecycleExpectation = schema.lifecycle_expectations[indexRow.Status];
    const requiredFiles = lifecycleExpectation?.required_files ?? [];

    for (const [name, file] of Object.entries(files)) {
      try {
        contents[name] = await readText(file);
      } catch {
        if (requiredFiles.includes(name)) {
          errors.push(
            finding(
              "missing-batch-file",
              relativeTo(workflowRoot, file),
              `${batchId} status ${indexRow.Status} requires file ${name}.`,
            ),
          );
        }
      }
    }
    if (requiredFiles.some((name) => !(name in contents))) continue;

    const sourceItems = indexRow["Source items"]
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
    for (const sourceItem of sourceItems) {
      const backlogRow = backlogRows.find((row) => row.ID === sourceItem);
      if (!backlogRow) {
        errors.push(
          finding(
            "missing-source-item",
            "PRODUCT_BACKLOG.md",
            `${batchId} references missing source item ${sourceItem}.`,
          ),
        );
        continue;
      }
      if (!lifecycleExpectation?.backlog_statuses.includes(backlogRow.Status)) {
        errors.push(
          finding(
            "inconsistent-backlog-status",
            "PRODUCT_BACKLOG.md",
            `${sourceItem} status ${backlogRow.Status} does not agree with ${batchId} status ${indexRow.Status}.`,
          ),
        );
      }
    }

    const artifactStatuses = {
      "FEATURE.md": contents["FEATURE.md"] ? parseTopLevelStatus(contents["FEATURE.md"]) : null,
      "IMPLEMENTATION.md": contents["IMPLEMENTATION.md"]
        ? parseTopLevelStatus(contents["IMPLEMENTATION.md"])
        : null,
      "PROGRESS_STATE.md": contents["PROGRESS_STATE.md"]
        ? contents["PROGRESS_STATE.md"].match(/^- Status:\s*`?([a-z_]+)`?\s*$/m)?.[1] ?? null
        : null,
    };
    const expectedArtifactStatuses = lifecycleExpectation?.artifact_statuses ?? {};

    for (const [name, expectedStatus] of Object.entries(expectedArtifactStatuses)) {
      if (indexRow.Status === "superseded" && !(name in contents)) continue;
      const status = artifactStatuses[name];
      if (!schema.entity_statuses.batch.includes(status)) {
        errors.push(
          finding(
            "invalid-artifact-status",
            relativeTo(workflowRoot, files[name]),
            `${batchId} ${name} status is missing or invalid: ${status ?? "missing"}.`,
          ),
        );
      } else if (status !== expectedStatus) {
        errors.push(
          finding(
            "inconsistent-artifact-status",
            relativeTo(workflowRoot, files[name]),
            `${batchId} status ${indexRow.Status} requires ${name} status ${expectedStatus}, found ${status}.`,
          ),
        );
      }
    }

    if (["planned", "spec", "superseded"].includes(indexRow.Status)) continue;

    const tasks = parseTasks(contents["IMPLEMENTATION.md"]);
    taskCount += tasks.length;
    if (tasks.length === 0) {
      errors.push(
        finding(
          "missing-tasks",
          relativeTo(workflowRoot, files["IMPLEMENTATION.md"]),
          `${batchId} status ${indexRow.Status} requires at least one task.`,
        ),
      );
    }
    for (const task of tasks) {
      if (!schema.entity_statuses.task.includes(task.status)) {
        errors.push(
          finding(
            "invalid-task-status",
            relativeTo(workflowRoot, files["IMPLEMENTATION.md"]),
            `${task.id} uses invalid or missing status ${task.status ?? "missing"}.`,
          ),
        );
      }
      const missingFields = schema.required_task_fields.filter((field) => !task.fields.has(field));
      if (missingFields.length) {
        errors.push(
          finding(
            "missing-task-fields",
            relativeTo(workflowRoot, files["IMPLEMENTATION.md"]),
            `${task.id} is missing required fields: ${missingFields.join(", ")}.`,
          ),
        );
      }
    }

    const traceabilityRows = parseMarkdownTable(
      contents["IMPLEMENTATION.md"],
      "## Traceability closure",
    );
    if (traceabilityRows.length === 0) {
      errors.push(
        finding(
          "missing-traceability",
          relativeTo(workflowRoot, files["IMPLEMENTATION.md"]),
          `${batchId} status ${indexRow.Status} requires at least one traceability row.`,
        ),
      );
    }
    const taskIds = new Set(tasks.map((task) => task.id));
    for (const row of traceabilityRows) {
      for (const referencedTask of row["Covered by"]?.match(/\bT\d+\b/g) ?? []) {
        if (!taskIds.has(referencedTask)) {
          errors.push(
            finding(
              "unknown-task-reference",
              relativeTo(workflowRoot, files["IMPLEMENTATION.md"]),
              `${row["Feature reference"] || "Traceability row"} references missing task ${referencedTask}.`,
            ),
          );
        }
      }
    }
    for (const recorded of parseRecordedTransitions(contents["PROGRESS.md"])) {
      if (!schema.transitions[recorded.type].includes(recorded.transition)) {
        errors.push(
          finding(
            "invalid-transition",
            relativeTo(workflowRoot, files["PROGRESS.md"]),
            `${recorded.entity} records disallowed ${recorded.type} transition ${recorded.transition}.`,
          ),
        );
      }
    }
    for (const row of traceabilityRows) {
      if (!schema.entity_statuses.traceability.includes(row.State)) {
        errors.push(
          finding(
            "invalid-traceability-state",
            relativeTo(workflowRoot, files["IMPLEMENTATION.md"]),
            `${row["Feature reference"] || "Traceability row"} uses invalid state ${row.State}.`,
          ),
        );
      }
      if (row.State === "accepted_gap") {
        const reference = row["Feature reference"] || "Traceability row";
        const approvalPattern = new RegExp(
          `${escapeRegExp(reference)}.*(?:user.*(?:approved|accepted)|(?:approved|accepted).*user)`,
          "i",
        );
        const approvalRecorded = contents["PROGRESS.md"]
          .split("\n")
          .some((line) => approvalPattern.test(line) && hasPositiveEvidenceLanguage(line));
        if (!approvalRecorded) {
          errors.push(
            finding(
              "accepted-gap-without-approval",
              relativeTo(workflowRoot, files["PROGRESS.md"]),
              `${reference} is accepted_gap without recorded user approval.`,
            ),
          );
        }
      }
    }

    if (indexRow.Status === "done") {
      const unfinishedTasks = tasks.filter((task) => task.status !== "done");
      if (unfinishedTasks.length) {
        errors.push(
          finding(
            "unfinished-task",
            relativeTo(workflowRoot, files["IMPLEMENTATION.md"]),
            `${batchId} is done while tasks remain unfinished: ${unfinishedTasks.map((task) => task.id).join(", ")}.`,
          ),
        );
      }
      for (const task of tasks) {
        for (const command of task.requiredValidationCommands) {
          if (!hasPassingCommandEvidence(contents["PROGRESS.md"], command)) {
            errors.push(
              finding(
                "validation-not-passed",
                relativeTo(workflowRoot, files["PROGRESS.md"]),
                `${task.id} is done but required validation lacks recorded passing evidence: ${command}.`,
              ),
            );
          }
        }
      }
      const openRows = traceabilityRows.filter((row) => ["planned", "blocked"].includes(row.State));
      if (openRows.length) {
        errors.push(
          finding(
            "open-traceability",
            relativeTo(workflowRoot, files["IMPLEMENTATION.md"]),
            `${batchId} is done with ${openRows.length} open traceability row(s).`,
          ),
        );
      }
      if (!sectionHasNone(contents["PROGRESS_STATE.md"], "## Open validation list")) {
        errors.push(
          finding(
            "open-validation",
            relativeTo(workflowRoot, files["PROGRESS_STATE.md"]),
            `${batchId} is done but its open-validation list is not empty.`,
          ),
        );
      }
      if (!finalAuditPassed(contents["PROGRESS_STATE.md"])) {
        errors.push(
          finding(
            "final-audit-not-passed",
            relativeTo(workflowRoot, files["PROGRESS_STATE.md"]),
            `${batchId} is done but the final audit is not recorded as passed.`,
          ),
        );
      }
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    summary: { batches: batchDirectories.length, tasks: taskCount },
  };
}

const formatReport = (report) => {
  if (report.valid) {
    return `Workflow valid: ${report.summary.batches} batch(es), ${report.summary.tasks} task(s).`;
  }
  return [
    `Workflow invalid: ${report.errors.length} error(s), ${report.warnings.length} warning(s).`,
    ...report.errors.map((error) => `- ${error.file}: ${error.message} [${error.code}]`),
    ...report.warnings.map((warning) => `- ${warning.file}: ${warning.message} [${warning.code}]`),
  ].join("\n");
};

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  const json = args.includes("--json");
  const workflowRoot = args.find((arg) => !arg.startsWith("-"));

  if (!workflowRoot) {
    console.error("Usage: node scripts/validate-workflow.mjs <ai-workflow-directory> [--json]");
    process.exitCode = 2;
  } else {
    try {
      const report = await validateWorkflow(workflowRoot);
      console.log(json ? JSON.stringify(report, null, 2) : formatReport(report));
      process.exitCode = report.valid ? 0 : 1;
    } catch (error) {
      const report = {
        valid: false,
        errors: [finding("validator-error", workflowRoot, error.message)],
        warnings: [],
        summary: { batches: 0, tasks: 0 },
      };
      console.log(json ? JSON.stringify(report, null, 2) : formatReport(report));
      process.exitCode = 1;
    }
  }
}
