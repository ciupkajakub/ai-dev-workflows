#!/usr/bin/env python3
"""Run a check command and report its real exit code, tested content and full log.

The result line identifies the content before the command started: `rev` is HEAD and
`tree` is the Git tree that committing every non-ignored file would produce. It equals
`git rev-parse <commit>^{tree}` for a commit of that same content.
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
UNKNOWN = ("unknown", "unknown", "unknown")


def git(*args, env=None):
    result = subprocess.run(["git", *args], capture_output=True, text=True,
                            timeout=GIT_TIMEOUT, env=env, check=True)
    return result.stdout.rstrip("\n")


def content_tree(top, log):
    """Hash the working content without touching the repository's index or objects."""
    with tempfile.TemporaryDirectory(prefix="workflow-tree-") as directory:
        index = Path(directory) / "index"
        objects = Path(directory) / "objects"
        objects.mkdir()
        # Copying the index keeps its cached file stats, so unchanged files are not rehashed.
        current = Path(git("-C", top, "rev-parse", "--path-format=absolute", "--git-path", "index"))
        if current.exists():
            shutil.copy2(current, index)
        alternates = git("-C", top, "rev-parse", "--path-format=absolute", "--git-path", "objects")
        env = {**os.environ, "GIT_INDEX_FILE": str(index), "GIT_OBJECT_DIRECTORY": str(objects),
               "GIT_ALTERNATE_OBJECT_DIRECTORIES": alternates}
        git("-C", top, "add", "-A", env=env)
        if log:
            git("-C", top, "rm", "-q", "-f", "--cached", "--ignore-unmatch", "--",
                f":(top,literal){log}", env=env)
        return git("-C", top, "write-tree", env=env)


def git_state(log):
    """Return (revision, dirty, tree). The check's own log is not part of the content."""
    try:
        top = git("rev-parse", "--show-toplevel")
        revision = git("rev-parse", "HEAD")
        resolved, root = log.resolve(), Path(top).resolve()
        own = resolved.relative_to(root).as_posix() if resolved.is_relative_to(root) else None
        paths = ["--", ".", f":(exclude,top,literal){own}"] if own else []
        dirty = bool(git("-C", top, "status", "--porcelain", *paths))
        return revision, str(dirty).lower(), content_tree(top, own)
    except (OSError, subprocess.SubprocessError):
        return UNKNOWN


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
    before = git_state(log)
    started = time.monotonic()
    code, timed_out = run(" ".join(args.command), args.timeout, log)
    seconds = round(time.monotonic() - started)
    after = git_state(log)
    if "unknown" in before + after:
        changed = "unknown"
    else:
        changed = str((before[0], before[2]) != (after[0], after[2])).lower()
    revision, dirty, tree = before
    lines = log.read_text(errors="replace").splitlines()
    print("\n".join(lines[-args.tail:]))
    print(f"CHECK exit={code} timed_out={str(timed_out).lower()} seconds={seconds} "
          f"rev={revision} dirty={dirty} tree={tree} changed_during_run={changed} "
          f"temporary_log={str(temporary).lower()} log={log}")
    return code if code >= 0 else 128 - code


if __name__ == "__main__":
    sys.exit(main())
