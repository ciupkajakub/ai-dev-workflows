"""Exercise evaluation graders and the trial pipeline without running an agent."""

import importlib.util
import io
import json
from pathlib import Path
import contextlib
import shlex
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("run_eval", ROOT / "tests/evals/run_eval.py")
harness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(harness)


def executor(source):
    """Return an executor command that runs Python source in the workspace."""
    return shlex.join([sys.executable, "-B", "-c", source])


REPORTING = ('import json; print(json.dumps({"type": "result", "result": "done", '
             '"total_cost_usd": 0.5, "num_turns": 1}))')


class GraderControls(unittest.TestCase):
    def test_controls_separate_good_from_bad(self):
        scenarios = harness.scenario_ids()
        self.assertEqual(len(scenarios), 6)
        for scenario in scenarios:
            for control, expected in (("good", "pass"), ("bad", "fail"), ("unchanged", "fail")):
                with self.subTest(scenario=scenario, control=control):
                    result = harness.check_control(scenario, control)
                    self.assertEqual(result["verdict"], expected, result["criteria"])


class Workspace(unittest.TestCase):
    def prepared(self, scenario, instructions):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        workspace = Path(temporary.name) / "workspace"
        harness.prepare_workspace(scenario, harness.resolve_instructions(instructions), workspace)
        return workspace

    def test_executor_cannot_see_rubric_or_answers(self):
        for scenario in harness.scenario_ids():
            workspace = self.prepared(scenario, "HEAD")
            names = {path.name for path in workspace.rglob("*") if ".git" not in path.parts}
            self.assertFalse({"grade.py", "controls", "evaluation.md", "prompt.md"} & names)

    def test_package_is_pinned_and_discoverable(self):
        workspace = self.prepared("plain_repair", "HEAD")
        for provider in (".claude", ".agents"):
            self.assertTrue((workspace / provider / "skills/workflow/SKILL.md").is_file())

    def test_no_instructions_variant_has_no_skill(self):
        workspace = self.prepared("plain_repair", "none")
        self.assertFalse((workspace / ".claude").exists())
        self.assertFalse((workspace / "ai-workflow/tooling").exists())
        self.assertFalse(harness.prompt_for("plain_repair", "none").startswith("/workflow"))


class Pipeline(unittest.TestCase):
    def run_trials(self, source, out):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = harness.main([
                "run", "--instructions", "HEAD", "--out", str(out), "--runs", "1",
                "--scenario", "plain_repair", "--executor-command", executor(source),
            ])
        self.assertEqual(code, 0)
        return output.getvalue()

    def results(self, out):
        return [json.loads(path.read_text()) for path in Path(out).rglob("result.json")]

    def test_agent_that_changes_nothing_fails_and_is_reported(self):
        with tempfile.TemporaryDirectory() as out:
            summary = self.run_trials(REPORTING, out)
            result = self.results(out)[0]
            self.assertEqual(result["verdict"], "fail")
            self.assertFalse(result["criteria"]["defect_fixed"])
            self.assertEqual(result["cost_usd"], 0.5)
            self.assertIn("defect_fixed x1", summary)
            self.assertTrue((Path(out) / "report.md").is_file())

    def test_broken_executor_is_invalid_not_failed(self):
        with tempfile.TemporaryDirectory() as out:
            self.run_trials("raise SystemExit(3)", out)
            self.assertEqual(self.results(out)[0]["verdict"], "invalid")

    def test_finished_trial_is_not_repeated(self):
        with tempfile.TemporaryDirectory() as out:
            self.run_trials(REPORTING, out)
            self.run_trials("raise SystemExit(3)", out)
            self.assertEqual(self.results(out)[0]["verdict"], "fail")

    def test_invalid_trial_runs_again(self):
        with tempfile.TemporaryDirectory() as out:
            self.run_trials("raise SystemExit(3)", out)
            self.run_trials(REPORTING, out)
            self.assertEqual(self.results(out)[0]["verdict"], "fail")

    def test_invalid_reason_includes_reported_error(self):
        source = ('import json; print(json.dumps({"type": "result", "is_error": True, '
                  '"result": "Failed to authenticate"})); raise SystemExit(1)')
        with tempfile.TemporaryDirectory() as out:
            self.run_trials(source, out)
            result = self.results(out)[0]
            self.assertEqual(result["verdict"], "invalid")
            self.assertIn("Failed to authenticate", result["reason"])


class Metrics(unittest.TestCase):
    def test_unsafe_command_shapes_are_counted(self):
        command = "./check.sh | tail -1; git commit -m x"
        events = [{"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": "1", "name": "Bash", "input": {"command": command}},
            {"type": "tool_use", "id": "1", "name": "Bash", "input": {"command": command}},
            {"type": "tool_use", "id": "2", "name": "Bash", "input": {"command": "./check.sh && git commit -m x"}},
            {"type": "tool_use", "id": "3", "name": "Bash", "input": {"command": "git log --oneline | head -3"}},
        ]}}]
        metrics = harness.behavior_metrics(events)
        self.assertEqual(metrics["bash_commands"], 3)
        self.assertEqual(metrics["commit_after_semicolon"], 1)
        self.assertEqual(metrics["checks_piped_without_pipefail"], 1)


if __name__ == "__main__":
    unittest.main()
