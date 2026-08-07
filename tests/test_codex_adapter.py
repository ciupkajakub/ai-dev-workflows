import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER = REPO_ROOT / "adapters" / "codex_exec.py"
SCHEMA = REPO_ROOT / "schemas" / "agent_turn.schema.json"


class CodexAdapterContractTests(unittest.TestCase):
    def test_initial_and_resumed_turns_use_schema_and_preserve_session(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            workspace.mkdir()
            prompt = root / "prompt.txt"
            prompt.write_text("Complete the batch.", encoding="utf-8")
            blueprint = root / "candidate.md"
            blueprint.write_text("# Candidate blueprint\n", encoding="utf-8")
            result = root / "result.json"
            invocation_log = root / "invocations.jsonl"
            fake_codex = root / "fake_codex.py"
            fake_codex.write_text(
                "#!/usr/bin/env python3\n"
                "import json, os, pathlib, sys\n"
                "args = sys.argv[1:]\n"
                "stdin = sys.stdin.read()\n"
                "with pathlib.Path(os.environ['FAKE_CODEX_LOG']).open('a', encoding='utf-8') as h:\n"
                "    h.write(json.dumps({'args': args, 'stdin': stdin}) + '\\n')\n"
                "output = pathlib.Path(args[args.index('-o') + 1])\n"
                "output.write_text(json.dumps({'terminal_state': 'verified_outcome', 'summary': 'verified', 'progress_made': True, 'progress_fingerprint': 'proof', 'root_cause': '', 'requested_user_instruction': False, 'evidence_refs': ['check:pass'], 'context_loaded': [], 'rubric_scores': [], 'commands_run': [], 'observations': [], 'modified_files': []}), encoding='utf-8')\n"
                "print(json.dumps({'type': 'thread.started', 'thread_id': 'session-123'}))\n"
                "print(json.dumps({'type': 'item.completed', 'item': {'type': 'command_execution', 'command': 'python3 verify.py', 'exit_code': 0, 'aggregated_output': 'pass'}}))\n",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)
            base_env = {
                **os.environ,
                "FEATURE_EXECUTION_WORKSPACE": str(workspace),
                "FEATURE_EXECUTION_PROMPT_FILE": str(prompt),
                "FEATURE_EXECUTION_RESULT_FILE": str(result),
                "FEATURE_EXECUTION_BLUEPRINT": str(blueprint),
                "FEATURE_EXECUTION_RESUME_TOKEN": "",
                "FEATURE_EXECUTION_CODEX_BIN": str(fake_codex),
                "FEATURE_EXECUTION_CODEX_MODEL": "test-model",
                "FEATURE_EXECUTION_CODEX_EFFORT": "high",
                "FEATURE_EXECUTION_CODEX_TOOLS_LABEL": "codex-shell",
                "FAKE_CODEX_LOG": str(invocation_log),
            }

            first = subprocess.run(
                ["python3", str(ADAPTER)],
                cwd=workspace,
                env=base_env,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(first.returncode, 0, first.stderr)
            first_result = json.loads(result.read_text(encoding="utf-8"))
            self.assertEqual(first_result["resume_token"], "session-123")
            self.assertEqual(
                first_result["commands_run"][0]["command"], "python3 verify.py"
            )
            self.assertTrue(first_result["adapter_metadata"]["behavioral_agent"])
            self.assertEqual(first_result["adapter_metadata"]["model"], "test-model")
            self.assertEqual(first_result["adapter_metadata"]["effort"], "high")
            first_call = json.loads(invocation_log.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(first_call["args"][0], "exec")
            self.assertIn("--output-schema", first_call["args"])
            self.assertIn(str(SCHEMA), first_call["args"])
            self.assertIn("--sandbox", first_call["args"])
            self.assertIn(str(workspace.resolve()), first_call["args"])
            self.assertIn(str(blueprint.resolve()), first_call["stdin"])
            self.assertNotIn("Do not request a user message", first_call["stdin"])
            self.assertNotIn("repair", first_call["stdin"].lower())

            resumed_env = {
                **base_env,
                "FEATURE_EXECUTION_RESUME_TOKEN": "session-123",
            }
            second = subprocess.run(
                ["python3", str(ADAPTER)],
                cwd=workspace,
                env=resumed_env,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(second.returncode, 0, second.stderr)
            calls = [
                json.loads(line)
                for line in invocation_log.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(calls[1]["args"][:2], ["exec", "resume"])
            self.assertIn("session-123", calls[1]["args"])
            self.assertIn("--output-schema", calls[1]["args"])

    def test_nonzero_codex_exit_surfaces_jsonl_error_message(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "workspace"
            workspace.mkdir()
            prompt = root / "prompt.txt"
            prompt.write_text("Run.", encoding="utf-8")
            fake_codex = root / "failing_codex.py"
            fake_codex.write_text(
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                "print(json.dumps({'type': 'error', 'message': 'invalid_json_schema'}))\n"
                "print('plugin warning', file=sys.stderr)\n"
                "raise SystemExit(1)\n",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)
            completed = subprocess.run(
                ["python3", str(ADAPTER)],
                cwd=workspace,
                env={
                    **os.environ,
                    "FEATURE_EXECUTION_WORKSPACE": str(workspace),
                    "FEATURE_EXECUTION_PROMPT_FILE": str(prompt),
                    "FEATURE_EXECUTION_RESULT_FILE": str(root / "result.json"),
                    "FEATURE_EXECUTION_CODEX_BIN": str(fake_codex),
                },
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 1)
            self.assertIn("invalid_json_schema", completed.stderr)


if __name__ == "__main__":
    unittest.main()
