#!/usr/bin/env python3
"""Run a check command and report its real exit code, tested content and full log.

The result line identifies the content before the command started: `rev` is HEAD and
`tree` is the Git tree that committing every non-ignored file would produce. It equals
`git rev-parse <commit>^{tree}` for a commit of that same content. It does not cover
ignored files, files marked assume-unchanged or skip-worktree, or changes inside submodules.
"""

import argparse
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

GIT_TIMEOUT = 120
ENVIRONMENT = dict(os.environ)
if "GIT_WORK_TREE" not in ENVIRONMENT:
    # Hooks set GIT_DIR, which makes Git treat any subdirectory as the top of the checkout.
    ENVIRONMENT.pop("GIT_DIR", None)


def git(*args, env=ENVIRONMENT):
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=True,
                            errors="surrogateescape", timeout=GIT_TIMEOUT, env=env)
    return result.stdout.rstrip("\n")


def inside(path, top):
    path, top = path.resolve(), Path(top).resolve()
    return [path.relative_to(top).as_posix()] if path.is_relative_to(top) else []


def content_tree(top, log):
    """Hash the working content without writing to the repository's index or objects."""
    with tempfile.TemporaryDirectory(prefix="workflow-tree-") as directory:
        index = Path(directory) / "index"
        objects = Path(directory) / "objects"
        objects.mkdir()
        # Copying the index keeps its cached file stats, so unchanged files are not rehashed.
        current = Path(git("-C", top, "rev-parse", "--path-format=absolute", "--git-path", "index"))
        if current.exists():
            shutil.copy2(current, index)
        source = git("-C", top, "rev-parse", "--path-format=absolute", "--git-path", "objects")
        # Quoted, because an unquoted entry ends at a path separator.
        quoted = '"' + source.replace("\\", "\\\\").replace('"', '\\"') + '"'
        inherited = ENVIRONMENT.get("GIT_ALTERNATE_OBJECT_DIRECTORIES")
        env = {**ENVIRONMENT, "GIT_INDEX_FILE": str(index), "GIT_OBJECT_DIRECTORY": str(objects),
               "GIT_ALTERNATE_OBJECT_DIRECTORIES": os.pathsep.join(filter(None, (quoted, inherited)))}
        git("-C", top, "add", "-A", env=env)
        own = inside(log, top) + inside(Path(directory), top)
        if own:
            git("-C", top, "reset", "-q", "HEAD", "--",
                *(f":(top,literal){path}" for path in own), env=env)
        return git("-C", top, "write-tree", env=env)


def git_state(log, problems):
    """Return (revision, dirty, tree). The check's own log is not part of the content."""
    def attempt(read):
        try:
            return read()
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            detail = getattr(error, "stderr", None) or str(error)
            problems.append(detail.strip().splitlines()[-1] if detail.strip() else repr(error))
            return "unknown"

    top = attempt(lambda: git("rev-parse", "--show-toplevel"))
    if top == "unknown":
        return top, top, top

    def is_dirty():
        own = [f":(exclude,top,literal){path}" for path in inside(log, top)]
        paths = ["--", ".", *own] if own else []
        status = git("--no-optional-locks", "-C", top, "status", "--porcelain", *paths)
        return str(bool(status)).lower()

    return (attempt(lambda: git("rev-parse", "--verify", "HEAD")), attempt(is_dirty),
            attempt(lambda: content_tree(top, log)))


def new_log():
    """Keep logs in the common Git directory, which worktree removal does not delete."""
    name = {"prefix": time.strftime("%Y%m%d-%H%M%S-"), "suffix": ".log"}
    try:
        directory = Path(git("rev-parse", "--path-format=absolute", "--git-common-dir"),
                         "workflow-checks")
        directory.mkdir(exist_ok=True)
        handle, path = tempfile.mkstemp(dir=directory, **name)
        temporary = False
    except (OSError, subprocess.SubprocessError):
        # Outside a repository, or in a sandbox that protects the Git directory.
        handle, path = tempfile.mkstemp(prefix="workflow-check-", suffix=".log")
        temporary = True
    os.close(handle)
    return Path(path), temporary


def run(command, timeout, log):
    with log.open("wb") as output:
        process = subprocess.Popen(
            ["bash", "-o", "pipefail", "-c", command],
            stdout=output, stderr=subprocess.STDOUT, start_new_session=True,
        )
        try:
            return process.wait(timeout=timeout), False
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            return 124, True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--timeout", type=float, default=600, help="Seconds before stopping the command")
    parser.add_argument("--log", type=Path, help="Full output file; defaults to the Git directory")
    parser.add_argument("--tail", type=int, default=40, help="Output lines to print")
    parser.add_argument("command", nargs="+", help="Shell command, after --")
    args = parser.parse_args(argv)
    log, temporary = (args.log, False) if args.log else new_log()
    log.parent.mkdir(parents=True, exist_ok=True)
    problems = []
    before = git_state(log, problems)
    started = time.monotonic()
    code, timed_out = run(" ".join(args.command), args.timeout, log)
    seconds = round(time.monotonic() - started)
    after = git_state(log, problems)
    if "unknown" in (before[0], before[2], after[0], after[2]):
        changed = "unknown"
    else:
        changed = str((before[0], before[2]) != (after[0], after[2])).lower()
    revision, dirty, tree = before
    lines = log.read_text(errors="replace").splitlines()
    sys.stdout.reconfigure(errors="backslashreplace")
    print("\n".join(lines[-args.tail:]))
    for problem in dict.fromkeys(problems):
        print(f"Content not fully identified: {problem}")
    print(f"CHECK exit={code} timed_out={str(timed_out).lower()} seconds={seconds} "
          f"rev={revision} dirty={dirty} tree={tree} changed_during_run={changed} "
          f"temporary_log={str(temporary).lower()} log={log}")
    return code if code >= 0 else 128 - code


if __name__ == "__main__":
    sys.exit(main())
