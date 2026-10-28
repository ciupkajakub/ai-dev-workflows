#!/usr/bin/env python3
"""Read-only comparison of an installed workflow package with a source Git commit."""

import argparse
from pathlib import Path
import subprocess
import sys


PACKAGE_PATHS = ("LICENSE", "skills")
RETIRED_PATHS = ("feature_execution_blueprint.md",)


def git(source, *args):
    result = subprocess.run(
        ["git", "-C", str(source), *args], capture_output=True, check=True
    )
    return result.stdout


def compare(source, commit, package):
    expected = set(
        git(source, "ls-tree", "-r", "--name-only", "-z", commit, "--", *PACKAGE_PATHS)
        .decode().rstrip("\0").split("\0")
    )
    expected.discard("")
    if not {"LICENSE", "skills/workflow/SKILL.md"}.issubset(expected):
        raise ValueError("Source commit does not contain the single-skill workflow package")
    actual = set()
    for name in (*PACKAGE_PATHS, *RETIRED_PATHS):
        path = package / name
        if path.is_symlink() or path.is_file():
            actual.add(name)
        elif path.is_dir():
            actual.update(
                item.relative_to(package).as_posix()
                for item in path.rglob("*") if item.is_file() or item.is_symlink()
            )
    problems = [f"missing: {name}" for name in sorted(expected - actual)]
    problems += [f"unexpected: {name}" for name in sorted(actual - expected)]
    for name in sorted(expected & actual):
        path = package / name
        canonical_parts = (
            part for part in (path, *path.parents)
            if part != package and part.is_relative_to(package)
        )
        if any(part.is_symlink() for part in canonical_parts):
            problems.append(f"symlink in canonical package: {name}")
        elif path.read_bytes() != git(source, "show", f"{commit}:{name}"):
            problems.append(f"changed: {name}")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Local source Git checkout")
    parser.add_argument("--package", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--commit", required=True, help="Source commit recorded by setup")
    args = parser.parse_args(argv)
    source, package = args.source.resolve(), args.package.resolve()
    try:
        pinned = git(
            source, "rev-parse", "--verify", "--end-of-options", f"{args.commit}^{{commit}}"
        ).decode().strip()
        head = git(source, "rev-parse", "HEAD").decode().strip()
        problems = compare(source, pinned, package)
        latest_problems = compare(source, head, package)
        dirty = bool(git(source, "diff", "--name-only", "HEAD", "--", *PACKAGE_PATHS))
        dirty |= bool(git(source, "ls-files", "--others", "--exclude-standard", "--", *PACKAGE_PATHS))
        print(f"Recorded source commit: {pinned}")
        print(f"Package integrity: {'mismatch' if problems else 'verified'}")
        print(f"Checked local source HEAD: {head}")
        if dirty:
            status = "unverified: source package has uncommitted changes"
        elif problems:
            status = "local package differs"
        else:
            status = "update available" if latest_problems else "matches local source HEAD"
        print(f"Currentness: {status}")
        for problem in problems:
            print(problem)
        return 1 if problems else 0
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Package verification unavailable: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
