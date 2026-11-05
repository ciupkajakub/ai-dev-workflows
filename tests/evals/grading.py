"""Helpers shared by scenario graders. Graders never run inside the agent's workspace."""

from contextlib import contextmanager
from dataclasses import dataclass, field
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

TIMEOUT = 120


@dataclass
class Context:
    workspace: Path
    base: str
    final_message: str
    events: list = field(default_factory=list)

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.workspace), *args],
            capture_output=True, check=True,
        ).stdout

    def new_commits(self):
        output = self.git("rev-list", "--reverse", f"{self.base}..HEAD").decode()
        return output.split()

    def changed_files(self):
        output = self.git("diff", "--name-only", self.base, "HEAD").decode()
        return output.split()

    @contextmanager
    def snapshot(self, revision="HEAD"):
        """Yield a throwaway copy of committed content; uncommitted work does not count."""
        with tempfile.TemporaryDirectory(prefix="workflow-eval-grade-") as directory:
            archive = self.git("archive", "--format=tar", revision)
            with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
                tar.extractall(directory, filter="tar")
            yield Path(directory)


def run(path, *command):
    """Return (exit code, combined output); a hang counts as a failure."""
    try:
        result = subprocess.run(
            command, cwd=path, capture_output=True, text=True, timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return 124, "grader timeout"
    return result.returncode, result.stdout + result.stderr


def suite_passes(path):
    code, _ = run(path, sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests")
    return code == 0


def probe(path, source):
    """Run a snippet with the snapshot importable and return the JSON it prints."""
    code, output = run(path, sys.executable, "-B", "-c", source)
    if code != 0:
        return None
    try:
        return json.loads(output.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return None
