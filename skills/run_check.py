#!/usr/bin/env python3
"""Run a check command and report its real exit code, revision and full log."""

import argparse
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time


def git_state():
    def git(*args):
        return subprocess.run(["git", *args], capture_output=True, text=True)

    head = git("rev-parse", "HEAD")
    if head.returncode != 0:
        return "unknown", "unknown"
    dirty = bool(git("status", "--porcelain").stdout.strip())
    return head.stdout.strip(), str(dirty).lower()


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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=600, help="Seconds before stopping the command")
    parser.add_argument("--log", type=Path, help="Full output file; defaults to a temporary file")
    parser.add_argument("--tail", type=int, default=40, help="Output lines to print")
    parser.add_argument("command", nargs="+", help="Shell command, after --")
    args = parser.parse_args(argv)
    log = args.log
    if log is None:
        handle, name = tempfile.mkstemp(prefix="workflow-check-", suffix=".log")
        os.close(handle)
        log = Path(name)
    log.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    code, timed_out = run(" ".join(args.command), args.timeout, log)
    seconds = round(time.monotonic() - started)
    revision, dirty = git_state()
    lines = log.read_text(errors="replace").splitlines()
    print("\n".join(lines[-args.tail:]))
    print(f"CHECK exit={code} timed_out={str(timed_out).lower()} seconds={seconds} "
          f"rev={revision} dirty={dirty} log={log}")
    return code if code >= 0 else 128 - code


if __name__ == "__main__":
    sys.exit(main())
