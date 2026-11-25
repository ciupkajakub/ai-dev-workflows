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


def git(*args, env=None):
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=True,
                            errors="surrogateescape", timeout=GIT_TIMEOUT, env=env)
    return result.stdout.rstrip("\n")


def environment():
    """Return the environment for identifying this checkout, or raise if it is ambiguous.

    Hooks can set GIT_DIR, which makes Git treat any subdirectory as the top of the
    checkout, and GIT_INDEX_FILE, which belongs to the hook's own repository.
    """
    env = dict(os.environ)
    if "GIT_WORK_TREE" in env:
        return env
    if "GIT_DIR" in env:
        without = {name: value for name, value in env.items() if name != "GIT_DIR"}
        given = git("rev-parse", "--absolute-git-dir", env=env)
        try:
            found = git("rev-parse", "--absolute-git-dir", env=without)
        except subprocess.CalledProcessError:
            return env
        if Path(found).resolve() != Path(given).resolve():
            raise ValueError("GIT_DIR names a different repository than this directory")
        env = without
    index = Path(env.get("GIT_INDEX_FILE", ""))
    if index.is_absolute():
        own = Path(git("rev-parse", "--absolute-git-dir", env=env))
        if not inside(index, own):
            raise ValueError("GIT_INDEX_FILE belongs to a different repository than this directory")
    return env


def describe(error):
    if isinstance(error, subprocess.CalledProcessError) and error.stderr:
        lines = error.stderr.strip().splitlines()
        return "; ".join(line for line in lines if line.startswith(("error:", "fatal:"))) or lines[0]
    return str(error) or repr(error)


def inside(path, top):
    path, top = path.resolve(), Path(top).resolve()
    return [path.relative_to(top).as_posix()] if path.is_relative_to(top) else []


def content_tree(top, log, base):
    """Hash the working content without writing to the repository's index or objects."""
    with tempfile.TemporaryDirectory(prefix="workflow-tree-") as directory:
        index = Path(directory) / "index"
        objects = Path(directory) / "objects"
        objects.mkdir()
        # Copying the index keeps its cached file stats, so unchanged files are not rehashed.
        current = Path(git("-C", top, "rev-parse", "--path-format=absolute", "--git-path", "index",
                           env=base))
        if current.exists():
            shutil.copy2(current, index)
        source = git("-C", top, "rev-parse", "--path-format=absolute", "--git-path", "objects",
                     env=base)
        # Quoted, because an unquoted entry ends at a path separator.
        quoted = '"' + source.replace("\\", "\\\\").replace('"', '\\"') + '"'
        inherited = base.get("GIT_ALTERNATE_OBJECT_DIRECTORIES")
        env = {**base, "GIT_INDEX_FILE": str(index), "GIT_OBJECT_DIRECTORY": str(objects),
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
            problems.append(describe(error))
            return "unknown"

    env = attempt(environment)
    top = env if env == "unknown" else attempt(lambda: git("rev-parse", "--show-toplevel", env=env))
    if top == "unknown":
        return top, top, top

    def is_dirty():
        own = [f":(exclude,top,literal){path}" for path in inside(log, top)]
        paths = ["--", ".", *own] if own else []
        status = git("--no-optional-locks", "-C", top, "status", "--porcelain", *paths, env=env)
        return str(bool(status)).lower()

    return (attempt(lambda: git("rev-parse", "--verify", "HEAD", env=env)), attempt(is_dirty),
            attempt(lambda: content_tree(top, log, env)))


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


def show(lines):
    """Print without letting an output problem replace the command's exit code."""
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(errors="backslashreplace")
        print("\n".join(lines), flush=True)
    except (OSError, ValueError):
        sys.stdout = None  # Nothing can be shown, and flushing again at exit would fail.


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
    try:
        lines = log.read_text(errors="replace").splitlines()[-args.tail:]
    except OSError as error:
        lines = [f"Log unavailable: {error}"]
    lines += [f"Content not fully identified: {problem}" for problem in dict.fromkeys(problems)]
    lines.append(
        f"CHECK exit={code} timed_out={str(timed_out).lower()} seconds={seconds} "
        f"rev={revision} dirty={dirty} tree={tree} changed_during_run={changed} "
        f"temporary_log={str(temporary).lower()} log={log}"
    )
    show(lines)
    return code if code >= 0 else 128 - code


if __name__ == "__main__":
    sys.exit(main())
