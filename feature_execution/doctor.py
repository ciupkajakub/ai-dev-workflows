from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import re


PROVENANCE_FIELDS = (
    "Workflow schema",
    "Blueprint source",
    "Blueprint revision",
    "Blueprint digest",
)

BATCH_STATUSES = {
    "planned",
    "spec",
    "ready",
    "active",
    "failed_validation",
    "blocked",
    "validated",
    "done",
    "superseded",
    "rolled_back",
}

TASK_STATUSES = {
    "planned", "in_progress", "blocked", "failed_validation", "validated",
    "done", "superseded", "rolled_back",
}

ARTIFACT_LIMITS = {
    "FEATURE.md": 220,
    "IMPLEMENTATION.md": 360,
    "PROGRESS.md": 300,
    "PROGRESS_STATE.md": 70,
}

BASE_FILES = (
    "AGENTS.md",
    "SECURITY.md",
    "TESTING_POLICY.md",
    "PRODUCT_BACKLOG.md",
    "WORK_INDEX.md",
)


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str
    details: dict
    severity: str = "error"

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "path": self.path,
            "message": self.message,
            "details": self.details,
            "severity": self.severity,
        }


def _line_count(path: Path) -> int:
    with path.open(encoding="utf-8") as handle:
        return sum(1 for _ in handle)


def _extract_provenance(text: str) -> dict[str, str]:
    values = {}
    for field in PROVENANCE_FIELDS:
        match = re.search(
            rf"^[ \t]*(?:-[ \t]*)?{re.escape(field)}:\s*`?([^`\n]+)`?[ \t]*$",
            text,
            flags=re.MULTILINE,
        )
        if match:
            values[field] = match.group(1).strip()
    return values


def _extract_status(text: str) -> str | None:
    patterns = (
        r"^Status:\s*`?([^`\n]+)`?\s*$",
        r"^- Status:\s*`?([^`\n]+)`?\s*$",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.MULTILINE)
        if match:
            return match.group(1).strip()
    return None


def _work_index_rows(
    path: Path, *, batch: str | None = None
) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    rows = {}
    indexes = {"batch": 0, "status": 1, "folder": 2}
    for line in path.read_text(encoding="utf-8").splitlines():
        columns = [
            column.strip().strip("`")
            for column in line.strip().strip("|").split("|")
        ]
        normalized = [column.lower() for column in columns]
        if all(name in normalized for name in indexes):
            indexes = {name: normalized.index(name) for name in indexes}
            continue
        if len(columns) <= max(indexes.values()):
            continue
        batch_id = columns[indexes["batch"]]
        if not re.fullmatch(r"B\d{3}", batch_id):
            continue
        if batch is not None and batch_id != batch:
            continue
        if batch_id in rows:
            raise ValueError(f"ambiguous work index: multiple rows for {batch_id}")
        folder_parts = Path(columns[indexes["folder"]].rstrip("/")).parts
        if folder_parts[:2] == ("ai-workflow", "work"):
            folder_parts = folder_parts[1:]
        rows[batch_id] = {
            "status": columns[indexes["status"]],
            "folder": str(Path(*folder_parts)),
        }
    return rows


def _product_backlog_rows(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        columns = [
            column.strip().strip("`")
            for column in line.strip().strip("|").split("|")
        ]
        if len(columns) < 2 or not re.fullmatch(r"NMI-\d+", columns[0]):
            continue
        batch = next(
            (value for value in columns[2:] if re.fullmatch(r"B\d{3}", value)),
            "",
        )
        rows[columns[0]] = {"status": columns[1], "batch": batch}
    return rows


def _source_statuses_allowed(batch_status: str) -> set[str]:
    if batch_status in {"spec", "ready"}:
        return {"spec"}
    if batch_status in {"active", "failed_validation", "validated"}:
        return {"active", batch_status}
    return {batch_status}


def _expected_artifact_statuses(batch_status: str) -> dict[str, str]:
    if batch_status == "ready":
        return {
            "FEATURE.md": "spec",
            "IMPLEMENTATION.md": "ready",
            "PROGRESS_STATE.md": "ready",
            "WORK_INDEX.md": "ready",
        }
    return {
        "FEATURE.md": batch_status,
        "IMPLEMENTATION.md": batch_status,
        "PROGRESS_STATE.md": batch_status,
        "WORK_INDEX.md": batch_status,
    }


def _required_artifacts(batch_status: str | None) -> set[str]:
    if batch_status == "planned":
        return set()
    if batch_status == "spec":
        return {"FEATURE.md"}
    return set(ARTIFACT_LIMITS)


def _blueprint_identity(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    provenance = _extract_provenance(text)
    return {
        "path": str(path.resolve()),
        "Blueprint source": str(path.resolve()),
        "Workflow schema": provenance.get("Workflow schema", "unknown"),
        "Blueprint revision": provenance.get("Blueprint revision", "unknown"),
        "Blueprint digest": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _task_status_issues(
    text: str, relative: str, batch_id: str, index_status: str | None
) -> list[Issue]:
    issues = []
    task_blocks = re.split(r"(?m)^- id:[ \t]*(T\d{3})[ \t]*$", text)
    task_ids = task_blocks[1::2]
    if not task_ids:
        issues.append(Issue("missing_tasks", relative, "task plan has no T### tasks", {}))
    if len(task_ids) != len(set(task_ids)):
        issues.append(Issue("duplicate_task_id", relative, "task ids must be unique", {}))
    for task_id, block in zip(task_ids, task_blocks[2::2]):
        match = re.search(r"(?m)^  status:[ \t]*([a-z_]+)[ \t]*$", block)
        task_status = match.group(1) if match else None
        if task_status not in TASK_STATUSES:
            issues.append(Issue(
                "invalid_task_status", relative,
                f"{task_id} needs a supported task status",
                {"task": task_id, "actual": task_status},
            ))
        elif index_status in {"validated", "done"} and task_status not in {"done", "superseded"}:
            issues.append(Issue(
                "unfinished_task", relative,
                f"{batch_id} cannot be {index_status} while {task_id} is {task_status}",
                {"task": task_id, "status": task_status},
            ))
    return issues


def inspect_workflow(
    workflow_root: Path, blueprint: Path | None = None, *, batch: str | None = None
) -> dict:
    if batch is not None and not re.fullmatch(r"B\d{3}", batch):
        raise ValueError("--batch must be an exact B### identifier")
    workflow_root = workflow_root.resolve()
    issues: list[Issue] = []
    for filename in BASE_FILES:
        if not (workflow_root / filename).exists():
            issues.append(
                Issue(
                    "missing_file",
                    filename,
                    "required workflow file is missing",
                    {},
                )
            )
    agents_path = workflow_root / "AGENTS.md"
    if not agents_path.exists():
        canonical_provenance = {}
    else:
        canonical_provenance = _extract_provenance(
            agents_path.read_text(encoding="utf-8")
        )
        for field in PROVENANCE_FIELDS:
            if field not in canonical_provenance:
                issues.append(
                    Issue(
                        "missing_provenance",
                        "AGENTS.md",
                        f"{field} is missing",
                        {"field": field},
                    )
                )

    blueprint_identity = (
        _blueprint_identity(blueprint.resolve()) if blueprint else None
    )
    if canonical_provenance.get("Workflow schema") not in {None, "2", "3"}:
        issues.append(Issue(
            "unsupported_schema", "AGENTS.md", "unsupported workflow schema",
            {"actual": canonical_provenance["Workflow schema"], "supported": ["2", "3"]},
        ))
    if blueprint_identity:
        legacy_migration = (
            canonical_provenance.get("Workflow schema") == "2"
            and blueprint_identity["Workflow schema"] == "3"
        )
        for field, code in (
            ("Blueprint source", "blueprint_source_mismatch"),
            ("Workflow schema", "blueprint_schema_mismatch"),
            ("Blueprint revision", "blueprint_revision_mismatch"),
            ("Blueprint digest", "blueprint_digest_mismatch"),
        ):
            expected = blueprint_identity[field]
            actual = canonical_provenance.get(field)
            if field == "Blueprint source" and actual:
                source = Path(actual).expanduser()
                actual = str(
                    source.resolve()
                    if source.is_absolute()
                    else (Path.cwd() / source).resolve()
                )
            if actual != expected:
                issues.append(
                    Issue(
                        code,
                        "AGENTS.md",
                        f"{field} does not match the supplied blueprint",
                        {"expected": expected, "actual": actual},
                        severity=(
                            "warning" if legacy_migration and field != "Blueprint source"
                            else "error"
                        ),
                    )
                )

    index_rows = _work_index_rows(workflow_root / "WORK_INDEX.md", batch=batch)
    index_statuses = {
        batch_id: row["status"] for batch_id, row in index_rows.items()
    }
    backlog_rows = _product_backlog_rows(workflow_root / "PRODUCT_BACKLOG.md")
    batch_dirs = sorted(
        path for path in (workflow_root / "work").glob("B???-*") if path.is_dir()
    )
    if batch is not None:
        batch_dirs = [path for path in batch_dirs if path.name[:4] == batch]
        if batch not in index_rows and not batch_dirs:
            raise ValueError(f"unknown batch: {batch}")
        index_rows = {key: row for key, row in index_rows.items() if key == batch}
    for batch_id in sorted({path.name[:4] for path in batch_dirs}):
        matches = [path for path in batch_dirs if path.name[:4] == batch_id]
        if len(matches) > 1:
            issues.append(Issue(
                "ambiguous_batch_directory", "work",
                f"{batch_id} has multiple batch directories",
                {"batch": batch_id, "folders": [path.name for path in matches]},
            ))
    actual_batch_ids = {path.name[:4] for path in batch_dirs}
    required_index_ids = {
        batch_id
        for batch_id, row in index_rows.items()
        if row["status"] != "planned"
    }
    for batch_id, row in sorted(index_rows.items()):
        if batch_id not in required_index_ids:
            continue
        declared_folder = Path(row["folder"])
        valid_folder = (
            not declared_folder.is_absolute()
            and len(declared_folder.parts) == 2
            and declared_folder.parts[0] == "work"
            and declared_folder.parts[1].startswith(f"{batch_id}-")
        )
        if not valid_folder:
            issues.append(
                Issue(
                    "invalid_batch_directory",
                    row["folder"],
                    f"{batch_id} folder must match work/{batch_id}-* inside the workflow root",
                    {"batch": batch_id, "status": row["status"]},
                )
            )
            continue
        batch_path = workflow_root / declared_folder
        if not batch_path.is_dir():
            issues.append(
                Issue(
                    "missing_batch_directory",
                    row["folder"],
                    f"{batch_id} is indexed but its batch directory is missing",
                    {"batch": batch_id, "status": row["status"]},
                )
            )

    for batch_dir in batch_dirs:
        batch_id = batch_dir.name[:4]
        index_status = index_statuses.get(batch_id)
        required_artifacts = _required_artifacts(index_status)
        statuses: dict[str, str] = {}
        feature_source_items: set[str] = set()
        for filename in ARTIFACT_LIMITS:
            path = batch_dir / filename
            relative = str(path.relative_to(workflow_root))
            if not path.exists():
                if filename in required_artifacts:
                    issues.append(
                        Issue(
                            "missing_file",
                            relative,
                            "required batch artifact is missing",
                            {},
                        )
                    )
                continue
            line_count = _line_count(path)
            limit = ARTIFACT_LIMITS[filename]
            if line_count > limit:
                issues.append(
                    Issue(
                        "artifact_too_large",
                        relative,
                        f"artifact has {line_count} lines; target is {limit}",
                        {"actual_lines": line_count, "target_lines": limit},
                        severity="warning",
                    )
                )

            if filename not in {"FEATURE.md", "IMPLEMENTATION.md", "PROGRESS_STATE.md"}:
                continue
            text = path.read_text(encoding="utf-8")
            if filename == "FEATURE.md":
                feature_source_items.update(re.findall(r"NMI-\d+", text))
            provenance = _extract_provenance(text)
            schema = provenance.get("Workflow schema")
            if schema not in {"2", "3", None}:
                issues.append(Issue(
                    "unsupported_schema", relative, "unsupported workflow schema",
                    {"actual": schema, "supported": ["2", "3"]},
                ))
            status = _extract_status(text)
            if schema == "3":
                if status is not None:
                    issues.append(Issue(
                        "mirrored_batch_status", relative,
                        "schema 3 keeps batch status only in WORK_INDEX.md", {},
                    ))
                if filename == "IMPLEMENTATION.md":
                    issues.extend(_task_status_issues(text, relative, batch_id, index_status))
            elif status is None:
                issues.append(
                    Issue("missing_status", relative, "batch status is missing", {})
                )
            else:
                statuses[filename] = status
                if status not in BATCH_STATUSES:
                    issues.append(
                        Issue(
                            "invalid_status",
                            relative,
                            f"unsupported batch status: {status}",
                            {"status": status, "allowed": sorted(BATCH_STATUSES)},
                        )
                    )

            for field in PROVENANCE_FIELDS:
                if field not in provenance:
                    issues.append(
                        Issue(
                            "missing_provenance",
                            relative,
                            f"{field} is missing",
                            {"field": field},
                        )
                    )
                elif (
                    field in canonical_provenance
                    and provenance[field] != canonical_provenance[field]
                ):
                    issues.append(
                        Issue(
                            "provenance_mismatch",
                            relative,
                            f"{field} differs from AGENTS.md",
                            {
                                "field": field,
                                "expected": canonical_provenance[field],
                                "actual": provenance[field],
                            },
                            severity=(
                                "warning" if schema == "2"
                                and canonical_provenance.get("Workflow schema") == "3"
                                else "error"
                            ),
                        )
                    )

        if batch_id in index_statuses:
            statuses["WORK_INDEX.md"] = index_statuses[batch_id]
            if index_statuses[batch_id] not in BATCH_STATUSES:
                issues.append(
                    Issue(
                        "invalid_status",
                        "WORK_INDEX.md",
                        f"unsupported batch status: {index_statuses[batch_id]}",
                        {"batch": batch_id, "status": index_statuses[batch_id]},
                    )
                )
        else:
            issues.append(
                Issue(
                    "missing_index_row",
                    "WORK_INDEX.md",
                    f"{batch_id} is missing from the work index",
                    {"batch": batch_id},
                )
            )

        expected_statuses = (
            _expected_artifact_statuses(index_status) if index_status else {}
        )
        status_differences = {
            owner: {"expected": expected_statuses.get(owner), "actual": actual}
            for owner, actual in statuses.items()
            if expected_statuses.get(owner) != actual
        }
        if status_differences:
            issues.append(
                Issue(
                    "status_mismatch",
                    str(batch_dir.relative_to(workflow_root)),
                    f"{batch_id} has inconsistent lifecycle statuses",
                    {
                        "batch_status": index_status,
                        "statuses": statuses,
                        "differences": status_differences,
                    },
                )
            )

        if index_status:
            source_items = feature_source_items | {
                item_id
                for item_id, row in backlog_rows.items()
                if row["batch"] == batch_id
            }
            allowed_source_statuses = _source_statuses_allowed(index_status)
            for item_id in sorted(source_items):
                actual = backlog_rows.get(item_id, {}).get("status")
                if actual not in allowed_source_statuses:
                    issues.append(
                        Issue(
                            "source_status_mismatch",
                            "PRODUCT_BACKLOG.md",
                            f"{item_id} does not match {batch_id} lifecycle",
                            {
                                "batch": batch_id,
                                "batch_status": index_status,
                                "source_item": item_id,
                                "allowed": sorted(allowed_source_statuses),
                                "actual": actual,
                            },
                        )
                    )

    return {
        "schema_version": 1,
        "workflow_root": str(workflow_root),
        "valid": not any(issue.severity == "error" for issue in issues),
        "scope": {"batch": batch} if batch else {"all_batches": True},
        "batches_checked": len(actual_batch_ids | required_index_ids),
        "provenance": canonical_provenance,
        "blueprint": blueprint_identity,
        "artifact_targets": ARTIFACT_LIMITS,
        "semantic_rules_checked": False,
        "issues": [issue.as_dict() for issue in issues],
    }
