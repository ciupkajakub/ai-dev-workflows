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
    "COMMIT_MESSAGE.md",
)


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str
    details: dict

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "path": self.path,
            "message": self.message,
            "details": self.details,
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


def _work_index_statuses(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    statuses = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        columns = [
            column.strip().strip("`")
            for column in line.strip().strip("|").split("|")
        ]
        if len(columns) < 2 or not re.fullmatch(r"B\d{3}", columns[0]):
            continue
        statuses[columns[0]] = columns[1]
    return statuses


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
        "Workflow schema": provenance.get("Workflow schema", "unknown"),
        "Blueprint revision": provenance.get("Blueprint revision", "unknown"),
        "Blueprint digest": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def inspect_workflow(workflow_root: Path, blueprint: Path | None = None) -> dict:
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
    if blueprint_identity:
        for field, code in (
            ("Workflow schema", "blueprint_schema_mismatch"),
            ("Blueprint revision", "blueprint_revision_mismatch"),
            ("Blueprint digest", "blueprint_digest_mismatch"),
        ):
            expected = blueprint_identity[field]
            actual = canonical_provenance.get(field)
            if actual != expected:
                issues.append(
                    Issue(
                        code,
                        "AGENTS.md",
                        f"{field} does not match the supplied blueprint",
                        {"expected": expected, "actual": actual},
                    )
                )

    index_statuses = _work_index_statuses(workflow_root / "WORK_INDEX.md")
    backlog_rows = _product_backlog_rows(workflow_root / "PRODUCT_BACKLOG.md")
    batch_dirs = sorted(
        path for path in (workflow_root / "work").glob("B???-*") if path.is_dir()
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
                    )
                )

            if filename not in {"FEATURE.md", "IMPLEMENTATION.md", "PROGRESS_STATE.md"}:
                continue
            text = path.read_text(encoding="utf-8")
            if filename == "FEATURE.md":
                feature_source_items.update(re.findall(r"NMI-\d+", text))
            status = _extract_status(text)
            if status is None:
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

            provenance = _extract_provenance(text)
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
        "valid": not issues,
        "batches_checked": len(batch_dirs),
        "provenance": canonical_provenance,
        "blueprint": blueprint_identity,
        "artifact_targets": ARTIFACT_LIMITS,
        "issues": [issue.as_dict() for issue in issues],
    }
