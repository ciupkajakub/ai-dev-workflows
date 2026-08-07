import json
from pathlib import Path
import tempfile
import unittest

from feature_execution.evals import (
    DIMENSIONS,
    HARD_GATES,
    compare_reports,
    load_eval_suite,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CATALOG = REPO_ROOT / "eval" / "cases" / "v1" / "catalog.json"


class EvalCatalogContractTests(unittest.TestCase):
    def test_canonical_catalog_is_generic_complete_and_versioned(self):
        suite = load_eval_suite(CATALOG)

        self.assertGreaterEqual(len(suite["cases"]), 18)
        self.assertEqual(
            set(DIMENSIONS),
            {dimension for case in suite["cases"] for dimension in case["dimensions"]},
        )
        self.assertEqual(
            set(HARD_GATES),
            {gate for case in suite["cases"] for gate in case["hard_gates"]},
        )
        raw = CATALOG.read_text(encoding="utf-8")
        self.assertNotRegex(raw, r"B\d{3}|NMI-\d{3}|Smacznego|Smashnego")

    def test_suite_rejects_unknown_dimensions_and_unsafe_paths(self):
        invalid = {
            "case_set_revision": "bad-v1",
            "cases": [
                {
                    "id": "unsafe",
                    "prompt": "Do the work.",
                    "starting_files": {"../outside.txt": "bad"},
                    "expected": {"terminal_state": "verified_outcome"},
                    "dimensions": ["invented_dimension"],
                    "hard_gates": ["lifecycle_traceability"],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "suite.json"
            path.write_text(json.dumps(invalid), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsafe fixture path"):
                load_eval_suite(path, minimum_cases=1, require_full_coverage=False)

    def test_only_comparison_can_accept_a_candidate_that_meets_the_bar(self):
        dimensions = {
            name: {"score": 10.0, "passed": 3, "total": 3}
            for name in DIMENSIONS
        }
        baseline = {
            "case_set_revision": "same-v1",
            "case_set": {"sha256": "same-digest", "case_count": 20},
            "configuration": {
                "label": "baseline",
                "behavioral_agent": True,
                "trials_per_case": 3,
                "model": "model-v1",
                "effort": "high",
                "tools": "shell",
                "harness": "harness-v1",
            },
            "dimensions": dimensions,
            "accepted": False,
            "meets_absolute_bar": True,
        }
        candidate = {
            **baseline,
            "configuration": {
                **baseline["configuration"],
                "label": "candidate",
            },
        }

        result = compare_reports(baseline, candidate)

        self.assertTrue(result["candidate_accepted"])
        self.assertEqual(result["regressions"], [])

        changed_suite = {
            **candidate,
            "case_set": {"sha256": "changed-without-revision", "case_count": 20},
        }
        changed_result = compare_reports(baseline, changed_suite)
        self.assertFalse(changed_result["candidate_accepted"])
        self.assertIn("case_set_digest_mismatch", changed_result["regressions"])

        unknown_baseline = {
            **baseline,
            "configuration": {**baseline["configuration"], "model": "unknown"},
        }
        unknown_result = compare_reports(unknown_baseline, candidate)
        self.assertFalse(unknown_result["candidate_accepted"])
        self.assertIn(
            "baseline_configuration_unknown:model", unknown_result["regressions"]
        )


if __name__ == "__main__":
    unittest.main()
