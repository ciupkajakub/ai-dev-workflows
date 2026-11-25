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
from unittest.mock import patch


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
            controls = dict(harness.scenario_controls(scenario))
            self.assertTrue({"good", "bad", "unchanged"} <= controls.keys())
            for control, expected in controls.items():
                with self.subTest(scenario=scenario, control=control):
                    result = harness.check_control(scenario, control)
                    self.assertEqual(result["verdict"], expected, result["criteria"])

    def test_uncommitted_e2e_script_cannot_supply_evidence(self):
        with tempfile.TemporaryDirectory() as out:
            workspace = Path(out) / "workspace"
            base = harness.prepare_workspace("unhealthy_environment", "none", workspace)
            (workspace / "e2e/run.sh").write_text("exit 0\n")
            result = harness.grade("unhealthy_environment", workspace, base, "E2E: unverified",
                                   observations=["0 passed, 0 failed, 12 skipped"])
            self.assertFalse(result["criteria"]["harness_not_altered"])
            self.assertEqual(result["verdict"], "fail")


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
    def run_trials(self, source, out, *options, expected=0):
        with contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(output):
            code = harness.main([
                "run", "--instructions", "HEAD", "--out", str(out), "--runs", "1",
                "--scenario", "plain_repair", "--executor-command", executor(source), *options,
            ])
        self.assertEqual(code, expected, output.getvalue())
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
            self.assertNotIn("#1:", self.run_trials(REPORTING, out))
            self.assertEqual(self.results(out)[0]["verdict"], "fail")

    def test_invalid_trial_runs_again(self):
        with tempfile.TemporaryDirectory() as out:
            flag = Path(out) / "ready"
            source = f"from pathlib import Path\nif not Path({str(flag)!r}).exists(): raise SystemExit(3)\n{REPORTING}"
            self.run_trials(source, out)
            self.assertEqual(self.results(out)[0]["verdict"], "invalid")
            flag.touch()
            self.run_trials(source, out)
            self.assertEqual(self.results(out)[0]["verdict"], "fail")

    def test_changed_config_preserves_existing_trials(self):
        with tempfile.TemporaryDirectory() as out:
            self.run_trials(REPORTING, out)
            before = self.results(out)
            for options in (("--model", "different"), ("--effort", "low"),
                            ("--executor-command", executor("raise SystemExit(3)"))):
                with self.subTest(options=options):
                    self.assertIn("new --out", self.run_trials(REPORTING, out, *options, expected=2))
            with patch.object(harness, "evaluation_fingerprint", return_value="changed-fixture"):
                self.assertIn("evaluation_sha256", self.run_trials(REPORTING, out, expected=2))
            self.assertEqual(self.results(out), before)

    def test_prompt_edit_changes_the_evaluation_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scenarios = root / "scenarios"
            scenarios.mkdir()
            prompt = scenarios / "prompt.md"
            prompt.write_text("first")
            for name in ("run_eval.py", "grading.py"):
                (root / name).touch()
            with patch.multiple(harness, EVALS=root, SCENARIOS=scenarios, __file__=str(root / "run_eval.py")):
                before = harness.evaluation_fingerprint()
                prompt.write_text("second")
                self.assertNotEqual(harness.evaluation_fingerprint(), before)

    def test_legacy_results_need_a_fresh_directory(self):
        with tempfile.TemporaryDirectory() as out:
            old = Path(out) / "result.json"
            old.write_text('{"verdict":"pass"}')
            self.assertIn("no run-config.json", self.run_trials(REPORTING, out, expected=2))
            self.assertEqual(old.read_text(), '{"verdict":"pass"}')
            self.assertFalse((Path(out) / "run-config.json").exists())

    def test_report_includes_observed_runtime(self):
        init = {"type": "system", "subtype": "init", "model": "observed-model",
                "claude_code_version": "1.2.3", "tools": ["Read", "Bash"]}
        with tempfile.TemporaryDirectory() as out:
            summary = self.run_trials(f"print({json.dumps(init)!r}); {REPORTING}", out)
            self.assertIn("observed-model", summary)
            self.assertIn("1.2.3", summary)
            self.assertIn("Bash, Read", summary)
            self.assertEqual(self.results(out)[0]["runtime"]["tools"], ["Read", "Bash"])

    def test_report_keeps_different_observed_tools_in_separate_tables(self):
        with tempfile.TemporaryDirectory() as out:
            marker = Path(out) / "next-run"
            source = (f"from pathlib import Path\nimport json\np = Path({str(marker)!r})\n"
                      "tools = ['Read'] if p.exists() else ['Read', 'Edit']\np.touch()\n"
                      "print(json.dumps(dict(type='system', subtype='init', tools=tools)))\n" + REPORTING)
            summary = self.run_trials(source, out, "--runs", "2")
            self.assertEqual(summary.count("| plain_repair |"), 2)
            self.assertIn("tools: Edit, Read.", summary)
            self.assertIn("tools: Read.", summary)

    def test_native_command_restricts_the_tools_it_preapproves(self):
        with tempfile.TemporaryDirectory() as out, contextlib.redirect_stdout(io.StringIO()) as output:
            code = harness.main(["run", "--instructions", "none", "--out", out, "--dry-run"])
            self.assertEqual(code, 0)
            command = shlex.split(output.getvalue().splitlines()[-1])
            expected = {"Bash", "Read", "Edit", "Write", "Glob", "Grep", "Skill", "Agent"}
            for flag in ("--tools", "--allowedTools"):
                self.assertEqual(set(command[command.index(flag) + 1].split(",")), expected)

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

    def test_repair_procedure_and_check_wrapper_use_are_observed(self):
        def call(number, name, **arguments):
            return {"type": "tool_use", "id": number, "name": name, "input": arguments}
        events = [{"type": "assistant", "message": {"content": [
            call("1", "Read", file_path="/x/ai-workflow/tooling/skills/workflow/repair.md"),
            call("2", "Bash", command="python3 -B ai-workflow/tooling/skills/run_check.py -- ./check.sh"),
            call("3", "Bash", command="./check.sh"),
        ]}}]
        metrics = harness.behavior_metrics(events)
        self.assertEqual(metrics["instructions_read"], ["repair.md"])
        self.assertEqual(metrics["run_check_calls"], 1)


if __name__ == "__main__":
    unittest.main()
