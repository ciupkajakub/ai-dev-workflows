"""Check that run_check reports the real result of a command."""

import os
from pathlib import Path
import shutil
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

    def repository(self):
        subprocess.run([*self.git(), "init", "-q"], check=True)
        (self.directory / "app.txt").write_text("first\n")
        self.commit("start")

    def git(self):
        return ["git", "-C", str(self.directory), "-c", "user.name=t", "-c", "user.email=t@localhost",
                "-c", "commit.gpgsign=false"]

    def output(self, *args):
        return subprocess.run([*self.git(), *args], capture_output=True, text=True, check=True).stdout.strip()

    def commit(self, message):
        subprocess.run([*self.git(), "add", "-A"], check=True)
        subprocess.run([*self.git(), "commit", "-qm", message], check=True)

    def fields(self, result):
        return dict(part.split("=", 1) for part in self.summary(result).split()[1:])

    def run_default_log(self, command, cwd=None, env=None):
        return subprocess.run([sys.executable, "-B", str(TOOL), "--", command],
                              cwd=cwd or self.directory, capture_output=True, text=True, timeout=30,
                              env=env)

    def test_clean_revision_and_its_tree_are_reported(self):
        self.repository()
        for _ in range(2):  # the second run must not see the first run's log as a change
            fields = self.fields(self.run_tool("true"))
            self.assertEqual(fields["rev"], self.output("rev-parse", "HEAD"))
            self.assertEqual(fields["tree"], self.output("rev-parse", "HEAD^{tree}"))
            self.assertEqual((fields["dirty"], fields["changed_during_run"]), ("false", "false"))

    def test_different_uncommitted_content_is_distinguished(self):
        self.repository()
        trees = set()
        for text in ("second\n", "third\n"):
            (self.directory / "app.txt").write_text(text)
            fields = self.fields(self.run_default_log("true"))
            self.assertEqual(fields["dirty"], "true")
            trees.add(fields["tree"])
        (self.directory / "new.txt").write_text("untracked\n")
        trees.add(self.fields(self.run_default_log("true"))["tree"])
        self.assertEqual(len(trees), 3)

    def test_uncommitted_result_matches_the_later_commit_of_that_content(self):
        self.repository()
        (self.directory / "app.txt").write_text("second\n")
        (self.directory / "new.txt").write_text("untracked\n")
        tested = self.fields(self.run_default_log("true"))["tree"]
        self.commit("tested content")
        self.assertEqual(tested, self.output("rev-parse", "HEAD^{tree}"))

    def test_commit_made_by_the_command_is_not_reported_as_tested(self):
        self.repository()
        start = self.output("rev-parse", "HEAD")
        (self.directory / "app.txt").write_text("second\n")
        command = " ".join([*self.git(), "commit", "-qam", "during"])
        fields = self.fields(self.run_default_log(command))
        self.assertEqual(fields["exit"], "0")
        self.assertEqual(fields["rev"], start)
        self.assertEqual(fields["changed_during_run"], "true")

    def test_file_changed_by_the_command_is_reported(self):
        self.repository()
        fields = self.fields(self.run_default_log("echo rewritten > app.txt"))
        self.assertEqual((fields["dirty"], fields["changed_during_run"]), ("false", "true"))

    def test_staged_content_and_objects_are_not_changed(self):
        self.repository()
        (self.directory / "new.txt").write_text("untracked\n")
        before = self.output("status", "--porcelain"), self.output("count-objects")
        self.run_default_log("true")
        self.assertEqual((self.output("status", "--porcelain"), self.output("count-objects")), before)

    def test_default_log_is_kept_outside_the_working_content(self):
        self.repository()
        nested = self.directory / "nested"
        nested.mkdir()
        fields = self.fields(self.run_default_log("echo kept", nested))
        self.assertEqual(fields["temporary_log"], "false")
        self.assertEqual(Path(fields["log"]).parent.resolve(),
                         (self.directory / ".git/workflow-checks").resolve())
        self.assertEqual(Path(fields["log"]).read_text(), "kept\n")
        self.assertEqual(self.output("status", "--porcelain"), "")

    def test_default_log_survives_worktree_removal(self):
        self.repository()
        worktree = self.directory / "linked"
        self.output("worktree", "add", "-q", str(worktree))
        fields = self.fields(self.run_default_log("echo kept", worktree))
        self.output("worktree", "remove", str(worktree))
        self.assertEqual(Path(fields["log"]).read_text(), "kept\n")

    def test_tracked_log_does_not_change_the_reported_tree(self):
        self.repository()
        (self.directory / "check.log").write_text("committed\n")
        self.commit("track a log")
        fields = self.fields(self.run_tool("echo new output"))
        self.assertEqual(fields["tree"], self.output("rev-parse", "HEAD^{tree}"))
        self.assertEqual((fields["dirty"], fields["changed_during_run"]), ("false", "false"))

    def test_unhashable_content_keeps_the_known_revision_and_reports_why(self):
        self.repository()
        (self.directory / "embedded").mkdir()
        subprocess.run(["git", "init", "-q", str(self.directory / "embedded")], check=True)
        result = self.run_default_log("exit 3")
        self.assertEqual(result.returncode, 3)
        fields = self.fields(result)
        self.assertEqual(fields["rev"], self.output("rev-parse", "HEAD"))
        self.assertEqual((fields["dirty"], fields["tree"]), ("true", "unknown"))
        self.assertRegex(result.stdout, "Content not fully identified: .*embedded")

    def test_undecodable_names_and_output_do_not_replace_the_result(self):
        self.repository()
        (self.directory / "żó.txt").write_text("x\n")
        self.output("config", "core.quotepath", "false")
        result = subprocess.run(
            [sys.executable, "-B", "-X", "utf8=0", str(TOOL), "--", "printf 'żó\n'; exit 3"],
            cwd=self.directory, capture_output=True, timeout=30,
            env={**os.environ, "LC_ALL": "C", "PYTHONCOERCECLOCALE": "0"})
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn(b"CHECK exit=3", result.stdout)

    def test_temporary_directory_inside_the_checkout_is_not_content(self):
        self.repository()
        temporary = self.directory / "scratch"
        temporary.mkdir()
        result = subprocess.run([sys.executable, "-B", str(TOOL), "--", "true"], cwd=self.directory,
                                capture_output=True, text=True, timeout=30,
                                env={**os.environ, "TMPDIR": str(temporary)})
        fields = self.fields(result)
        self.assertEqual(fields["tree"], self.output("rev-parse", "HEAD^{tree}"))
        self.assertEqual(fields["changed_during_run"], "false")

    def test_git_dir_from_a_hook_does_not_move_the_top_of_the_checkout(self):
        self.repository()
        nested = self.directory / "nested"
        nested.mkdir()
        result = subprocess.run([sys.executable, "-B", str(TOOL), "--", "true"], cwd=nested,
                                capture_output=True, text=True, timeout=30,
                                env={**os.environ, "GIT_DIR": str(self.directory / ".git")})
        self.assertEqual(self.fields(result)["tree"], self.output("rev-parse", "HEAD^{tree}"))

    def test_path_separator_in_the_repository_path_is_supported(self):
        self.directory = self.directory / "a:b"
        self.directory.mkdir()
        subprocess.run([*self.git(), "init", "-q"], check=True)
        for name in ("app.txt", "unchanged.txt"):
            (self.directory / name).write_text("first\n")
            # Git rewrites recently modified files, which would hide missing objects.
            os.utime(self.directory / name, (1577836800, 1577836800))
        self.commit("start")
        time.sleep(1.2)
        (self.directory / "app.txt").write_text("second\n")
        tested = self.fields(self.run_default_log("true"))["tree"]
        self.commit("tested content")
        self.assertEqual(tested, self.output("rev-parse", "HEAD^{tree}"))

    def test_git_dir_of_another_repository_is_reported_not_guessed(self):
        self.repository()
        other = self.directory.parent / f"{self.directory.name}-other.git"
        self.addCleanup(shutil.rmtree, other)
        subprocess.run(["git", "init", "-q", "--bare", str(other)], check=True)
        for variable, value in (("GIT_DIR", other), ("GIT_INDEX_FILE", other / "index")):
            with self.subTest(variable):
                result = self.run_default_log("exit 3", env={**os.environ, variable: str(value)})
                self.assertEqual(result.returncode, 3)
                fields = self.fields(result)
                self.assertEqual((fields["rev"], fields["tree"]), ("unknown", "unknown"))
                self.assertIn(f"{variable} ", result.stdout)

    def test_closed_or_broken_output_does_not_replace_the_exit_code(self):
        tool = f"{sys.executable} -B {TOOL} --log {self.directory / 'x.log'} -- 'exit 3'"
        for command in (f"{tool} >&-", f"{tool} | true; exit ${{PIPESTATUS[0]}}"):
            with self.subTest(command):
                result = subprocess.run(["bash", "-c", command], capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 3, result.stderr)

    def test_log_removed_by_the_command_does_not_replace_the_exit_code(self):
        result = subprocess.run(
            [sys.executable, "-B", str(TOOL), "--log", "out/c.log", "--", "rm -rf out; exit 3"],
            cwd=self.directory, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn("Log unavailable", result.stdout)

    def test_unavailable_log_directory_falls_back_and_says_so(self):
        self.repository()
        (self.directory / ".git/workflow-checks").write_text("not a directory")
        result = self.run_default_log("exit 3")
        self.assertEqual(result.returncode, 3)
        fields = self.fields(result)
        self.assertEqual(fields["temporary_log"], "true")
        Path(fields["log"]).unlink()

    def test_ignored_log_inside_the_repository_is_accepted(self):
        self.repository()
        (self.directory / ".gitignore").write_text("*.log\n")
        self.commit("ignore logs")
        fields = self.fields(self.run_tool("true"))
        self.assertEqual(fields["tree"], self.output("rev-parse", "HEAD^{tree}"))
        self.assertEqual(fields["dirty"], "false")

    def test_outside_a_repository_revision_is_unknown(self):
        fields = self.fields(self.run_tool("true"))
        self.assertEqual({fields[name] for name in ("rev", "dirty", "tree", "changed_during_run")}, {"unknown"})


if __name__ == "__main__":
    unittest.main()
