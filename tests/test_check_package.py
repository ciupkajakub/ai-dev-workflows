"""Exercise package integrity and update detection without running agents."""

import contextlib
import importlib.util
import io
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_package", ROOT / "skills/check_package.py")
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class PackageCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="workflow-package-check-")
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name).resolve() / "source"
        self.package = Path(self.temp.name).resolve() / "installed"
        self.source.mkdir()
        for name in ("feature_execution_blueprint.md", "LICENSE"):
            shutil.copy2(ROOT / name, self.source / name)
        shutil.copytree(ROOT / "skills", self.source / "skills")
        self.git("init", "-q")
        self.git("add", ".")
        self.commit()
        self.pinned = self.git("rev-parse", "HEAD").strip()
        shutil.copytree(self.source, self.package, ignore=shutil.ignore_patterns(".git"))

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.source), *args], capture_output=True, text=True, check=True
        ).stdout

    def commit(self):
        self.git("-c", "user.name=Package test", "-c", "user.email=package-test@localhost",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "Package checkpoint")

    def run_check(self, commit=None):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = checker.main(["--source", str(self.source), "--package", str(self.package),
                                 "--commit", commit or self.pinned])
        return code, output.getvalue()

    def test_exact_copy_is_verified_without_mutation(self):
        before = {path.relative_to(self.package): path.read_bytes()
                  for path in self.package.rglob("*") if path.is_file()}
        code, output = self.run_check()
        self.assertEqual(code, 0)
        self.assertIn("Package integrity: verified", output)
        self.assertIn("Currentness: matches local source HEAD", output)
        self.assertEqual(before, {path.relative_to(self.package): path.read_bytes()
                                 for path in self.package.rglob("*") if path.is_file()})
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_changed_missing_and_extra_files_are_detected(self):
        (self.package / "skills/entry-rules.md").write_text("local edit\n")
        (self.package / "LICENSE").unlink()
        (self.package / "skills/local.txt").write_text("extra\n")
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("changed: skills/entry-rules.md", output)
        self.assertIn("missing: LICENSE", output)
        self.assertIn("unexpected: skills/local.txt", output)

    def test_intact_old_copy_reports_update(self):
        with (self.source / "skills/entry-rules.md").open("a") as document:
            document.write("\nAdditional instruction.\n")
        self.git("add", ".")
        self.commit()
        code, output = self.run_check()
        self.assertEqual(code, 0)
        self.assertIn("Package integrity: verified", output)
        self.assertIn("Currentness: update available", output)

    def test_uncommitted_source_does_not_claim_currentness(self):
        (self.source / "skills/local.txt").write_text("uncommitted\n")
        code, output = self.run_check()
        self.assertEqual(code, 0)
        self.assertIn("Package integrity: verified", output)
        self.assertIn("Currentness: unverified", output)

    def test_missing_commit_is_unavailable(self):
        code, output = self.run_check("nonexistent-package-revision")
        self.assertEqual(code, 2)
        self.assertIn("Package verification unavailable", output)

    def test_symlink_cannot_hide_content_substitution(self):
        path = self.package / "skills/entry-rules.md"
        path.unlink()
        path.symlink_to(self.source / "skills/entry-rules.md")
        code, output = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("symlink in canonical package: skills/entry-rules.md", output)


if __name__ == "__main__":
    unittest.main()
