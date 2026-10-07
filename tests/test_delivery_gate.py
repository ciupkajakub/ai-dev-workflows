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
        self.receipt = dict(schema=2, batch='B119', head=self.git('rev-parse', 'HEAD'),
                            feature_revision=5, plan_revision=6, implementer='author', verifier='independent',
                            review={'result': 'pass', 'evidence': self.ref},
                            checks=[{'id': 'V001', 'result': 'pass', 'observed': 'caller -> result', 'evidence': self.ref}],
                            obligations=[{'id': 'AC1.open', 'result': 'demonstrated', 'checks': ['V001'],
                                          'observed': 'Actual UI trigger and assertion', 'evidence': self.ref}],
                            findings=[])

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], check=True, capture_output=True, text=True).stdout.strip()

    def errors(self, receipt=None, **changes):
        args = dict(head=self.git('rev-parse', 'HEAD'), batch='B119', feature_revision=5, plan_revision=6, required=['V001'])
        args.update(obligations=['AC1.open'], known_findings=[])
        args.update(changes)
        return gate.validate(self.receipt if receipt is None else receipt, self.directory, **args)

    def cli(self, raw=None, extra=()):
        receipt = self.directory / 'verification.json'
        receipt.write_text(json.dumps(self.receipt) if raw is None else raw)
        return subprocess.run(['python3', '-B', str(SCRIPT), '--repository', str(self.repo), '--receipt', str(receipt),
                               '--batch', 'B119', '--feature-revision', '5', '--plan-revision', '6', '--required', 'V001',
                               '--obligation', 'AC1.open', *extra],
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
        self.assertTrue(self.errors())
        finding['comparison'] = self.ref
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

    def test_green_checks_do_not_cover_an_omitted_requirement(self):
        result = self.cli(extra=['--obligation', 'AC1.closed'])
        self.assertEqual(result.returncode, 1)
        self.assertIn('AC1.closed: missing required behavior', result.stdout)
        self.receipt['obligations'].append(dict(id='AC1.closed', result='missing', checks=['V001'],
                                              observed='Timer was not exercised', evidence=self.ref))
        result = self.cli(extra=['--obligation', 'AC1.closed'])
        self.assertEqual(result.returncode, 1)
        self.assertIn('AC1.closed: required behavior is not demonstrated', result.stdout)

    def test_coverage_requires_unique_ids_existing_checks_and_evidence(self):
        original = copy.deepcopy(self.receipt)
        for field, value in [('checks', []), ('checks', ['V999']), ('observed', ''), ('evidence', None),
                             ('result', 'unknown'), ('result', 'contradicted')]:
            with self.subTest(field=field, value=value):
                self.receipt = copy.deepcopy(original)
                self.receipt['obligations'][0][field] = value
                self.assertTrue(self.errors())
        self.receipt = copy.deepcopy(original)
        self.receipt['obligations'].append(copy.deepcopy(self.receipt['obligations'][0]))
        self.assertTrue(self.errors())
        for ids in [[], ['AC1.open', 'AC1.open'], [''], [None]]:
            self.assertTrue(self.errors(obligations=ids))

    def test_known_failure_cannot_disappear_outside_the_selected_lane(self):
        result = self.cli(extra=['--finding', 'F-G3'])
        self.assertEqual(result.returncode, 1)
        self.assertIn('F-G3: known finding omitted', result.stdout)
        self.receipt['findings'] = [dict(id='F-G3', status='rejected', reason='Tagged release, not required',
                                         evidence=self.ref)]
        result = self.cli(extra=['--finding', 'F-G3'])
        self.assertEqual(result.returncode, 1)
        self.assertIn('scope comparison', result.stdout)
        self.receipt['findings'][0].update(status='open', reason='Base/head relation unresolved')
        self.assertEqual(self.cli(extra=['--finding', 'F-G3']).returncode, 1)
        self.receipt['findings'][0].update(status='resolved', reason='Repair verified at this head')
        self.assertEqual(self.cli(extra=['--finding', 'F-G3']).returncode, 0)

    def test_legacy_receipt_requires_reassessment_not_a_schema_only_bump(self):
        self.receipt['schema'] = 1
        del self.receipt['obligations']
        self.assertEqual(self.cli().returncode, 1)
        self.receipt['schema'] = 2
        self.assertEqual(self.cli().returncode, 1)

    def test_retained_b119_green_report_cannot_hide_missing_behavior_and_failure(self):
        fixture = Path(__file__).parent / 'fixtures/b119-green-report-gaps.json'
        case = json.loads(fixture.read_text())
        self.assertEqual(case['recorded_review_result'], 'pass')
        self.assertTrue(all(c['result'] == 'pass' for c in case['recorded_checks']))
        self.receipt['checks'] = [dict(c, observed='Retained green command', evidence=self.ref)
                                  for c in case['recorded_checks']]
        errors = self.errors(required=[c['id'] for c in case['recorded_checks']],
                             obligations=case['retained_obligations'], known_findings=case['known_findings'])
        self.assertIn('AC1.closed: missing required behavior', errors)
        self.assertIn('F-G3: known finding omitted', errors)

    def test_complete_multi_behavior_proof_and_compared_rejection_pass(self):
        self.receipt['obligations'].append(dict(id='AC1.closed', result='demonstrated', checks=['V001'],
                                              observed='Closed timer executed and state asserted', evidence=self.ref))
        self.receipt['findings'] = [dict(id='F-G3', status='rejected',
                                         reason='Scope investigation excludes this path', evidence=self.ref,
                                         comparison=self.ref)]
        self.assertEqual(self.cli(extra=['--obligation', 'AC1.closed', '--finding', 'F-G3']).returncode, 0)


if __name__ == '__main__':
    unittest.main()
