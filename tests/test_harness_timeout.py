import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

from feature_execution.harness import run_outcome_loop


@unittest.skipUnless(os.name == "posix", "requires POSIX process inspection")
class AdapterTimeoutTest(unittest.TestCase):
    def test_timeout_stops_adapter_children_and_grandchildren(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            worker = workspace / "worker.py"
            worker.write_text(
                "import os, pathlib, signal, subprocess, sys, time\n"
                "root = pathlib.Path(__file__).parent\n"
                "role = sys.argv[1]\n"
                "signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
                "(root / (role + '.pid')).write_text(str(os.getpid()))\n"
                "if role == 'child':\n"
                "    subprocess.Popen([sys.executable, __file__, 'grandchild'])\n"
                "deadline = time.monotonic() + 10\n"
                "while time.monotonic() < deadline:\n"
                "    if (root / 'released').exists():\n"
                "        (root / (role + '.escaped')).write_text('still running')\n"
                "        break\n"
                "    time.sleep(0.01)\n",
                encoding="utf-8",
            )
            adapter = workspace / "adapter.py"
            adapter.write_text(
                "import pathlib, subprocess, sys\n"
                "subprocess.run([sys.executable, "
                "str(pathlib.Path(__file__).with_name('worker.py')), 'child'])\n",
                encoding="utf-8",
            )

            try:
                started = time.monotonic()
                outcome, exit_code = run_outcome_loop(
                    workspace=workspace,
                    prompt="Exercise the local timeout fixture.",
                    adapter_command=[sys.executable, str(adapter)],
                    adapter_timeout_seconds=1,
                    max_turns=1,
                )
                self.assertEqual(outcome["terminal_state"], "adapter_error")
                self.assertEqual(exit_code, 5)
                self.assertIn("timed out", outcome["summary"])
                self.assertLess(time.monotonic() - started, 5)

                for role in ("child", "grandchild"):
                    self.assertTrue((workspace / f"{role}.pid").exists())
                (workspace / "released").touch()
                time.sleep(0.2)
                for role in ("child", "grandchild"):
                    self.assertFalse(
                        (workspace / f"{role}.escaped").exists(),
                        f"{role} continued writing after the timeout",
                    )
                    pid = (workspace / f"{role}.pid").read_text()
                    state = subprocess.run(
                        ["ps", "-p", pid, "-o", "stat="],
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=2,
                    ).stdout.strip()
                    self.assertTrue(not state or state.startswith("Z"), state)
            finally:
                for role in ("child", "grandchild"):
                    pid_file = workspace / f"{role}.pid"
                    if pid_file.exists():
                        try:
                            os.kill(int(pid_file.read_text()), signal.SIGKILL)
                        except ProcessLookupError:
                            pass
