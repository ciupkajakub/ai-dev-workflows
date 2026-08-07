import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from feature_execution.evals import (
    DIMENSIONS,
    HARD_GATES,
    _load_judge_calibration,
    _reference_adapter_verified,
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
        forbidden_prompt_hints = (
            "continue, fix",
            "three consecutive",
            "return verified_outcome",
            "stop safely",
            "record the baseline as unknown",
            "inventory every repository consumer",
            "declared task does not authorize",
            "move closed narrative to",
            "preserve every current decision",
        )
        for case in suite["cases"]:
            lowered = case["prompt"].lower()
            for hint in forbidden_prompt_hints:
                self.assertNotIn(hint, lowered, case["id"])

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
        evidence_directory = tempfile.TemporaryDirectory()
        self.addCleanup(evidence_directory.cleanup)
        evidence_root = Path(evidence_directory.name)
        manifest = evidence_root / "workspace-manifest.json"
        patch = evidence_root / "changes.patch"
        status = evidence_root / "git-status.txt"
        manifest.write_text("[]\n", encoding="utf-8")
        patch.write_text("", encoding="utf-8")
        status.write_text("", encoding="utf-8")

        def digest(path):
            return hashlib.sha256(path.read_bytes()).hexdigest()

        dimensions = {
            name: {"score": 10.0, "passed": 54, "total": 54}
            for name in DIMENSIONS
        }
        hard_gates = {
            name: {"passed": True, "passed_trials": 54, "total": 54}
            for name in HARD_GATES
        }
        trials = [
            {
                "case_id": f"complete-{case_number}",
                "trial": number,
                "dimensions": list(DIMENSIONS),
                "hard_gates": list(HARD_GATES),
                "passed": True,
                "failures": [],
                "outcome": {
                    "terminal_state": "verified_outcome",
                    "internal_turns": 1,
                    "visible_user_interventions": 0,
                    "trajectory": [
                        {
                            "adapter_metadata": {
                                "behavioral_agent": True,
                                "command_evidence_source": "codex_jsonl_events",
                                "model": "model-v1",
                                "effort": "high",
                                "tools": "shell",
                                "codex_binary_verified": True,
                                "codex_binary_override": False,
                                "codex_executable": "/trusted/codex",
                                "codex_executable_sha256": "c" * 64,
                                "codex_expected_sha256": "c" * 64,
                                "codex_version": "codex-cli 1.2.3",
                                "codex_args_sha256": "d" * 64,
                                "sandbox": "workspace-write",
                            }
                        }
                    ],
                },
                "retained_evidence": {
                    "manifest": str(manifest),
                    "manifest_sha256": digest(manifest),
                    "patch": str(patch),
                    "patch_sha256": digest(patch),
                    "git_status": str(status),
                    "git_status_sha256": digest(status),
                    "referenced_files": [],
                },
                "verifier_commands_declared": 0,
                "external_judgment_required": False,
                "verifier_results": [],
            }
            for case_number in range(1, 19)
            for number in (1, 2, 3)
        ]
        baseline = {
            "schema_version": 1,
            "case_set_revision": "same-v1",
            "case_set": {
                "sha256": "same-digest",
                "case_count": 18,
                "case_ids": [f"complete-{number}" for number in range(1, 19)],
            },
            "configuration": {
                "label": "baseline",
                "behavioral_agent": True,
                "trials_per_case": 3,
                "model": "model-v1",
                "effort": "high",
                "tools": "shell",
                "harness": "harness-v1",
                "verifier_commands_authorized": False,
                "external_judgment_required": False,
                "blueprint": {"revision": "1", "sha256": "baseline-blueprint"},
                "adapter": {
                    "command_sha256": "same-adapter",
                    "provenance": {
                        "reference_adapter_selected": True,
                        "all_turns_attested": True,
                        "reference_adapter_sha256": "a" * 64,
                        "provider_runtime_consistent": True,
                        "provider_runtime": {
                            "codex_executable": "/trusted/codex",
                            "codex_executable_sha256": "c" * 64,
                            "codex_version": "codex-cli 1.2.3",
                            "codex_args_sha256": "d" * 64,
                            "sandbox": "workspace-write",
                        },
                    },
                },
            },
            "aggregate": {
                "cases_passed": 18,
                "cases_total": 18,
                "trials_passed": 54,
                "trials_total": 54,
                "avoidable_user_interventions": 0,
                "trials_with_no_user_steering": 54,
                "trials_with_user_steering": 0,
                "trials_with_no_user_steering_rate": 1.0,
                "avoidable_user_intervention_rate": 0.0,
                "internal_turns_total": 54,
                "internal_turns_denominator": 54,
                "mean_internal_turns": 1.0,
            },
            "dimensions": dimensions,
            "hard_gates": hard_gates,
            "trials": trials,
            "variance": {
                f"complete-{case_number}": {
                    "passed": 3,
                    "total": 3,
                    "pass_rate": 1.0,
                    "internal_turns": {
                        "minimum": 1,
                        "maximum": 1,
                        "sum": 3,
                        "denominator": 3,
                        "mean": 1.0,
                    },
                    "visible_user_interventions": 0,
                }
                for case_number in range(1, 19)
            },
            "observed_tradeoffs": [],
            "accepted": False,
            "meets_absolute_bar": True,
            "absolute_bar_failures": [],
        }
        candidate = {
            **baseline,
            "configuration": {
                **baseline["configuration"],
                "label": "candidate",
                "blueprint": {"revision": "2", "sha256": "candidate-blueprint"},
            },
        }

        result = compare_reports(baseline, candidate)

        self.assertTrue(result["candidate_accepted"])
        self.assertEqual(result["regressions"], [])

        changed_suite = {
            **candidate,
            "case_set": {"sha256": "changed-without-revision", "case_count": 18},
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

        multiple_changes = {
            **candidate,
            "configuration": {**candidate["configuration"], "tools": "browser+shell"},
        }
        multiple_result = compare_reports(baseline, multiple_changes)
        self.assertFalse(multiple_result["candidate_accepted"])
        self.assertIn(
            "multiple_variable_groups_changed:blueprint,tools",
            multiple_result["regressions"],
        )

        forged = {
            **candidate,
            "hard_gates": {},
            "trials": [],
            "meets_absolute_bar": True,
        }
        forged_result = compare_reports(baseline, forged)
        self.assertFalse(forged_result["candidate_accepted"])
        self.assertIn("candidate_incomplete_hard_gates", forged_result["regressions"])

        duplicate_trial = copy.deepcopy(candidate)
        duplicate_trial["trials"][-1]["trial"] = 2
        duplicate_result = compare_reports(baseline, duplicate_trial)
        self.assertFalse(duplicate_result["candidate_accepted"])
        self.assertIn("candidate_unbalanced_trials", duplicate_result["regressions"])

        tampered_evidence = copy.deepcopy(candidate)
        tampered_evidence["trials"][0]["retained_evidence"][
            "manifest_sha256"
        ] = "0" * 64
        tampered_result = compare_reports(baseline, tampered_evidence)
        self.assertFalse(tampered_result["candidate_accepted"])
        self.assertIn(
            "candidate_trial_retained_evidence_invalid",
            tampered_result["regressions"],
        )

        missing_aggregate = copy.deepcopy(candidate)
        missing_aggregate.pop("aggregate")
        incomplete_result = compare_reports(baseline, missing_aggregate)
        self.assertFalse(incomplete_result["candidate_accepted"])
        self.assertIn(
            "candidate_aggregate_integrity_mismatch",
            incomplete_result["regressions"],
        )

        changed_adapter = copy.deepcopy(candidate)
        changed_adapter["configuration"]["adapter"]["provenance"][
            "reference_adapter_sha256"
        ] = "b" * 64
        changed_adapter_result = compare_reports(baseline, changed_adapter)
        self.assertFalse(changed_adapter_result["candidate_accepted"])
        self.assertIn(
            "multiple_variable_groups_changed:blueprint,harness_and_adapter",
            changed_adapter_result["regressions"],
        )

        changed_provider = copy.deepcopy(candidate)
        changed_provider["configuration"]["adapter"]["provenance"][
            "provider_runtime"
        ]["codex_version"] = "codex-cli 2.0.0"
        for trial in changed_provider["trials"]:
            trial["outcome"]["trajectory"][0]["adapter_metadata"][
                "codex_version"
            ] = "codex-cli 2.0.0"
        changed_provider_result = compare_reports(baseline, changed_provider)
        self.assertFalse(changed_provider_result["candidate_accepted"])
        self.assertIn(
            "multiple_variable_groups_changed:blueprint,provider_runtime",
            changed_provider_result["regressions"],
        )

    def test_reference_adapter_must_be_the_actual_command_entrypoint(self):
        reference = REPO_ROOT / "adapters" / "codex_exec.py"
        turns = [
            {
                "outcome": {
                    "trajectory": [
                        {
                            "adapter_metadata": {
                                "behavioral_agent": True,
                                "command_evidence_source": "codex_jsonl_events",
                                "model": "model-v1",
                                "effort": "high",
                                "tools": "shell",
                                "codex_binary_verified": True,
                                "codex_binary_override": False,
                                "codex_executable": "/trusted/codex",
                                "codex_executable_sha256": "c" * 64,
                                "codex_expected_sha256": "c" * 64,
                                "codex_version": "codex-cli 1.2.3",
                                "codex_args_sha256": "d" * 64,
                                "sandbox": "workspace-write",
                            }
                        }
                    ]
                }
            }
        ]

        malicious = ["python3", "malicious.py", str(reference)]
        verified, provenance = _reference_adapter_verified(
            malicious, turns, "model-v1", "high", "shell"
        )

        self.assertFalse(verified)
        self.assertFalse(provenance["reference_adapter_selected"])

    def test_judge_calibration_requires_measured_agreement(self):
        with tempfile.TemporaryDirectory() as directory:
            calibration = Path(directory) / "calibration.json"
            calibration.write_text(
                json.dumps(
                    {
                        "calibration_revision": "weak-v1",
                        "judge_model": "judge-v1",
                        "maximum_mean_absolute_error": 1.0,
                        "human_rated_examples": [
                            {"id": "one", "human_score": 8},
                            {"id": "two", "human_score": 9},
                            {"id": "three", "human_score": 10},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "judge predictions"):
                _load_judge_calibration(calibration, "judge-v1")


if __name__ == "__main__":
    unittest.main()
