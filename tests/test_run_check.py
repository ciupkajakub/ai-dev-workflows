"""Check that run_check reports the real result of a command."""

from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "skills" / "run_check.py"


class RunCheck(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    def run_tool(self, command, *options):
        log = self.directory / "check.log"
        return subprocess.run(
            [sys.executable, "-B", str(TOOL), "--log", str(log), *options, "--", command],
            cwd=self.directory, capture_output=True, text=True, timeout=30,
        )

    def summary(self, result):
        return result.stdout.strip().splitlines()[-1]

    def test_success_is_reported(self):
        result = self.run_tool("echo fine")
        self.assertEqual(result.returncode, 0)
        self.assertIn("fine", result.stdout)
        self.assertTrue(self.summary(result).startswith("CHECK exit=0 "))

    def test_failure_exit_code_passes_through(self):
        result = self.run_tool("echo looks-good; exit 3")
        self.assertEqual(result.returncode, 3)
        self.assertIn("exit=3", self.summary(result))

    def test_pipeline_cannot_hide_failure(self):
        result = self.run_tool("false | grep -c nothing; false | cat")
        self.assertEqual(result.returncode, 1)
        self.assertIn("exit=1", self.summary(result))

    def test_missing_program_is_a_failure(self):
        result = self.run_tool("definitely-not-a-program-here 2>&1 | grep nothing-matches")
        self.assertNotEqual(result.returncode, 0)

    def test_dependent_operation_does_not_run_after_failure(self):
        marker = self.directory / "committed"
        command = (
            f"{sys.executable} -B {TOOL} --log {self.directory / 'x.log'} -- 'exit 1' "
            f"&& touch {marker}"
        )
        subprocess.run(["bash", "-c", command], capture_output=True)
        self.assertFalse(marker.exists())

    def test_timeout_stops_the_whole_process_group(self):
        marker = self.directory / "survived"
        started = time.monotonic()
        result = self.run_tool(f"(sleep 3; touch {marker}) & sleep 30", "--timeout", "1")
        self.assertEqual(result.returncode, 124)
        self.assertIn("timed_out=true", self.summary(result))
        self.assertLess(time.monotonic() - started, 10)
        time.sleep(3.5)
        self.assertFalse(marker.exists())

    def test_full_output_is_logged_and_only_the_end_is_printed(self):
        result = self.run_tool("seq 1 500", "--tail", "5")
        log = self.directory / "check.log"
        self.assertEqual(len(log.read_text().splitlines()), 500)
        self.assertIn("500", result.stdout)
        self.assertNotIn("\n400\n", result.stdout)
        self.assertIn(f"log={log}", self.summary(result))

    def test_revision_is_reported_in_a_repository(self):
        git = ["git", "-C", str(self.directory), "-c", "user.name=t", "-c", "user.email=t@localhost",
               "-c", "commit.gpgsign=false"]
        subprocess.run([*git, "init", "-q"], check=True)
        subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "start"], check=True)
        clean = self.summary(self.run_tool("true"))
        self.assertRegex(clean, r"rev=[0-9a-f]{40} ")
        self.assertIn("dirty=true", clean)  # the check log itself is untracked here

    def test_outside_a_repository_revision_is_unknown(self):
        self.assertTrue(re.search(r"rev=unknown ", self.summary(self.run_tool("true"))))


if __name__ == "__main__":
    unittest.main()
