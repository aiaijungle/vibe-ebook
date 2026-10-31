import json
from pathlib import Path
import subprocess
import sys
import unittest
from reader_lab import CASES, RECORDS, select_context, simulate

FOLDER = Path(__file__).resolve().parent


class ReaderChecks(unittest.TestCase):
    def test_only_current_relevant_authoritative_context(self):
        self.assertEqual(select_context(RECORDS), ["R2", "R3", "R4"])

    def test_five_outcomes_twice_with_fresh_state(self):
        for case in CASES:
            for trial in (1, 2):
                with self.subTest(case=case["id"], trial=trial):
                    self.assertEqual(simulate(case), case["expected"])

    def guard(self, event):
        return subprocess.run([sys.executable, str(FOLDER / "hook_guard.py")],
                              input=event, text=True, capture_output=True, check=False)

    def test_read_event_allowed(self):
        self.assertEqual(self.guard(json.dumps({"tool_name": "Read", "tool_input": {"file_path": "sample.txt"}})).returncode, 0)

    def test_write_event_blocked_without_executing(self):
        result = self.guard(json.dumps({"tool_name": "Write", "tool_input": {"file_path": "sample.txt"}}))
        self.assertEqual(result.returncode, 2)
        self.assertIn("only Read", result.stderr)

    def test_malformed_event_blocks(self):
        for payload in ("{", "[]", "{}", '{"tool_name":"Read","tool_input":null}'):
            with self.subTest(payload=payload):
                self.assertEqual(self.guard(payload).returncode, 2)

    def test_runner_preserves_failure_status(self):
        result = subprocess.run([sys.executable, str(FOLDER / "run_checks.py"), "--demo-failure"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Intentional failure", result.stdout)


if __name__ == "__main__":
    unittest.main()
