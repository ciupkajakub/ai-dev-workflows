#!/usr/bin/env python3
"""Exercise publication decisions against real Git snapshots and evidence files."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/workflow-deliver/scripts/check_delivery_gate.py'
spec = importlib.util.spec_from_file_location('gate', SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class DeliveryGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Test')
        (self.repo / 'app.txt').write_text('implementation\n')
        self.git('add', 'app.txt')
        self.git('commit', '-qm', 'implementation')
        self.directory = self.repo / 'evidence files'
        self.directory.mkdir()
        self.proof = self.directory / 'proof.log'
        self.proof.write_text('Actual caller scenario and review observations\n')
        self.ref = {'path': 'proof.log', 'sha256': hashlib.sha256(self.proof.read_bytes()).hexdigest()}
        self.receipt = dict(schema=1, batch='B119', head=self.git('rev-parse', 'HEAD'),
                            feature_revision=5, plan_revision=6, implementer='author', verifier='independent',
                            review={'result': 'pass', 'evidence': self.ref},
                            checks=[{'id': 'V001', 'result': 'pass', 'observed': 'caller -> result', 'evidence': self.ref}],
                            findings=[])

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], check=True, capture_output=True, text=True).stdout.strip()

    def errors(self, receipt=None, **changes):
        args = dict(head=self.git('rev-parse', 'HEAD'), batch='B119', feature_revision=5, plan_revision=6, required=['V001'])
        args.update(changes)
        return gate.validate(self.receipt if receipt is None else receipt, self.directory, **args)

    def cli(self, raw=None):
        receipt = self.directory / 'verification.json'
        receipt.write_text(json.dumps(self.receipt) if raw is None else raw)
        return subprocess.run(['python3', '-B', str(SCRIPT), '--repository', str(self.repo), '--receipt', str(receipt),
                               '--batch', 'B119', '--feature-revision', '5', '--plan-revision', '6', '--required', 'V001'],
                              capture_output=True, text=True)

    def test_valid_snapshot_passes_without_mutation(self):
        before = self.git('status', '--porcelain')
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.receipt['head'])
        self.assertEqual(self.proof.read_text(), 'Actual caller scenario and review observations\n')
        self.assertEqual(self.git('status', '--porcelain'), before)

    def test_missing_scenario_blocks_even_with_passing_subset(self):
        self.assertIn('V002: missing required proof', self.errors(required=['V001', 'V002']))

    def test_self_verification_and_missing_review_block(self):
        self.receipt['verifier'] = ' author '
        self.receipt['review'] = None
        self.assertEqual(len(self.errors()), 2)
        self.assertEqual(self.cli().returncode, 1)

    def test_snapshot_metadata_mismatches_block(self):
        for key, value in [('head', '0' * 40), ('batch', 'B120'), ('feature_revision', 4), ('plan_revision', 5), ('schema', True)]:
            with self.subTest(key=key):
                receipt = copy.deepcopy(self.receipt)
                receipt[key] = value
                self.assertTrue(any(key in e for e in self.errors(receipt)))

    def test_nonpassing_or_unobserved_scenarios_block(self):
        for result, observed in [('fail', 'observed failure'), ('unknown', 'not run'), ('pass', '')]:
            with self.subTest(result=result, observed=observed):
                self.receipt['checks'][0].update(result=result, observed=observed)
                self.assertTrue(self.errors())

    def test_duplicate_or_empty_required_ids_block(self):
        self.receipt['checks'].append(copy.deepcopy(self.receipt['checks'][0]))
        self.assertTrue(self.errors())
        for required in [[], ['V001', 'V001'], ['']]:
            self.assertTrue(self.errors(required=required))

    def test_findings_need_disposition_and_evidence(self):
        finding = dict(id='F001', status='open', reason='Needs repair', evidence=self.ref)
        self.receipt['findings'] = [finding]
        self.assertTrue(self.errors())
        finding['status'] = 'resolved'
        self.assertEqual(self.errors(), [])
        finding['status'] = 'rejected'
        self.assertEqual(self.errors(), [])
        self.receipt['findings'].append(copy.deepcopy(finding))
        self.assertTrue(self.errors())

    def test_altered_missing_empty_and_escaped_evidence_block(self):
        self.proof.write_text('changed')
        self.assertTrue(self.errors())
        self.proof.unlink()
        self.assertTrue(self.errors())
        self.proof.touch()
        self.assertTrue(self.errors())
        for path in ['../app.txt', str(self.repo / 'app.txt')]:
            self.ref['path'] = path
            self.assertTrue(self.errors())

    def test_symlink_evidence_blocks(self):
        link = self.directory / 'linked.log'
        link.symlink_to(self.proof)
        self.ref['path'] = 'linked.log'
        self.assertTrue(self.errors())

    def test_dirty_tracked_or_untracked_application_blocks(self):
        (self.repo / 'app.txt').write_text('uncommitted behavior')
        self.assertEqual(self.cli().returncode, 1)
        self.git('restore', 'app.txt')
        (self.repo / 'new code.txt').write_text('untracked behavior')
        self.assertEqual(self.cli().returncode, 1)

    def test_metadata_commit_requires_rebinding_unaffected_proof(self):
        (self.repo / 'progress.md').write_text('verification stage')
        self.git('add', 'progress.md')
        self.git('commit', '-qm', 'record stage')
        self.assertEqual(self.cli().returncode, 1)
        self.receipt['head'] = self.git('rev-parse', 'HEAD')
        self.assertEqual(self.cli().returncode, 0)

    def test_malformed_or_nonobject_receipts_do_not_pass(self):
        self.assertEqual(self.cli(raw='{').returncode, 2)
        self.assertEqual(self.cli(raw='[]').returncode, 1)


if __name__ == '__main__':
    unittest.main()
