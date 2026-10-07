#!/usr/bin/env python3
"""Check a verifier's receipt against the publication snapshot and required checks."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def evidence(record, directory, label, errors):
    if not isinstance(record, dict):
        errors.append(f"{label}: missing evidence record")
        return
    name = record.get("path")
    if not nonempty(name):
        errors.append(f"{label}: missing evidence path")
        return
    relative = Path(name)
    path = directory / relative
    if relative.is_absolute() or ".." in relative.parts:
        errors.append(f"{label}: evidence must stay within its directory")
        return
    if any(part.is_symlink() for part in (path, *path.parents) if part != directory
           and part.is_relative_to(directory)):
        errors.append(f"{label}: symlink evidence is not accepted")
        return
    if not path.is_file() or path.stat().st_size == 0:
        errors.append(f"{label}: evidence is missing or empty")
        return
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if record.get("sha256") != digest:
        errors.append(f"{label}: evidence digest differs")


def valid_ids(values, *, allow_empty=False):
    return (isinstance(values, list) and (allow_empty or bool(values))
            and all(nonempty(x) for x in values) and len(values) == len(set(values)))


def validate(receipt, directory, *, head, batch, feature_revision, plan_revision, required,
             obligations, known_findings):
    errors = []
    if not isinstance(receipt, dict):
        return ["receipt must be a JSON object"]
    expected = {"schema": 2, "batch": batch, "head": head,
                "feature_revision": feature_revision, "plan_revision": plan_revision}
    for key, value in expected.items():
        if type(receipt.get(key)) is not type(value) or receipt.get(key) != value:
            errors.append(f"{key}: does not match the requested snapshot")
    if not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", head):
        errors.append("head: expected a full commit id")
    if not valid_ids(required):
        errors.append("required checks: supply the complete, unique plan check IDs")
        required = []
    if not valid_ids(obligations):
        errors.append("obligations: supply the complete, unique approved behavior IDs")
        obligations = []
    if not valid_ids(known_findings, allow_empty=True):
        errors.append("known findings: supply unique finding IDs from the run history")
        known_findings = []
    if not nonempty(batch):
        errors.append("batch must be nonempty")
    if feature_revision < 1 or plan_revision < 1:
        errors.append("feature/plan revisions must be positive")
    implementer, verifier = receipt.get("implementer"), receipt.get("verifier")
    if not nonempty(implementer) or not nonempty(verifier) or implementer.strip() == verifier.strip():
        errors.append("verification requires distinct implementer and verifier identities")
    review = receipt.get("review")
    if not isinstance(review, dict) or review.get("result") != "pass":
        errors.append("independent code review is missing or not passed")
    else:
        evidence(review.get("evidence"), directory, "review", errors)
    checks = receipt.get("checks")
    seen = set()
    if not isinstance(checks, list):
        errors.append("checks: missing list")
        checks = []
    for check in checks:
        if not isinstance(check, dict) or not nonempty(check.get("id")):
            errors.append("check: missing ID")
            continue
        check_id = check["id"]
        if check_id in seen:
            errors.append(f"{check_id}: duplicate check")
        seen.add(check_id)
        if check.get("result") != "pass" or not nonempty(check.get("observed")):
            errors.append(f"{check_id}: passing observed scenario is required")
        evidence(check.get("evidence"), directory, check_id, errors)
    for check_id in sorted(set(required) - seen):
        errors.append(f"{check_id}: missing required proof")
    coverage = receipt.get("obligations")
    if not isinstance(coverage, list):
        errors.append("obligations: missing requirement coverage")
        coverage = []
    covered = set()
    for obligation in coverage:
        if not isinstance(obligation, dict) or not nonempty(obligation.get("id")):
            errors.append("obligation: missing ID")
            continue
        obligation_id = obligation["id"]
        if obligation_id in covered:
            errors.append(f"{obligation_id}: duplicate obligation")
        covered.add(obligation_id)
        if obligation.get("result") != "demonstrated" or not nonempty(obligation.get("observed")):
            errors.append(f"{obligation_id}: required behavior is not demonstrated")
        links = obligation.get("checks")
        if not valid_ids(links) or any(x not in seen for x in links):
            errors.append(f"{obligation_id}: reference existing executed check IDs")
        evidence(obligation.get("evidence"), directory, obligation_id, errors)
    for obligation_id in sorted(set(obligations) - covered):
        errors.append(f"{obligation_id}: missing required behavior")
    findings = receipt.get("findings")
    if not isinstance(findings, list):
        errors.append("findings: explicit dispositions are required")
        findings = []
    finding_ids = set()
    for finding in findings:
        if not isinstance(finding, dict) or not nonempty(finding.get("id")):
            errors.append("finding: missing ID")
            continue
        finding_id = finding["id"]
        if finding_id in finding_ids:
            errors.append(f"{finding_id}: duplicate finding")
        finding_ids.add(finding_id)
        if finding.get("status") not in ("resolved", "rejected") or not nonempty(finding.get("reason")):
            errors.append(f"{finding_id}: unresolved finding")
        evidence(finding.get("evidence"), directory, finding_id, errors)
        if finding.get("status") == "rejected":
            evidence(finding.get("comparison"), directory, f"{finding_id}: scope comparison", errors)
    for finding_id in sorted(set(known_findings) - finding_ids):
        errors.append(f"{finding_id}: known finding omitted")
    return errors


def git(repository, *args):
    return subprocess.run(["git", "-C", str(repository), *args],
                          check=True, capture_output=True, text=True).stdout.strip()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--batch", required=True)
    parser.add_argument("--feature-revision", type=int, required=True)
    parser.add_argument("--plan-revision", type=int, required=True)
    parser.add_argument("--required", action="append", required=True, help="Repeat for every required check ID")
    parser.add_argument("--obligation", action="append", required=True,
                        help="Repeat for every behavior derived from approved requirements, independently of checks")
    parser.add_argument("--finding", action="append", default=[],
                        help="Repeat for every known finding, including failures outside selected test lanes")
    args = parser.parse_args(argv)
    try:
        repository = Path(git(args.repository, "rev-parse", "--show-toplevel")).resolve()
        head = git(repository, "rev-parse", "HEAD")
        receipt_path = args.receipt.resolve()
        receipt = json.loads(receipt_path.read_text())
        errors = validate(receipt, receipt_path.parent, head=head, batch=args.batch,
                          feature_revision=args.feature_revision, plan_revision=args.plan_revision,
                          required=args.required, obligations=args.obligation, known_findings=args.finding)
        if git(repository, "diff", "HEAD", "--name-only"):
            errors.append("working tree differs from the verified commit")
        for name in filter(None, git(repository, "ls-files", "--others", "--exclude-standard", "-z").split("\0")):
            path = repository / name
            if receipt_path.parent == repository or not path.is_relative_to(receipt_path.parent):
                errors.append(f"uncommitted file outside evidence directory: {name}")
        if errors:
            print("Publication gate: blocked")
            print("\n".join(errors))
            return 1
        print(f"Publication gate: pass for {args.batch} at {head}")
        print("Record completeness and snapshot match only; behavioral truth and verifier identity are not authenticated.")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Publication gate unavailable: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
