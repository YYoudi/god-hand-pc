"""Original invented plans/files only; no disc, executable, game data or pixels."""
import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

import prototype_scenarios as scenarios


def plan():
    return {'schema': 1, 'profile': 'prototype-june-2006',
        'name': scenarios.SCENARIOS[0], 'builds': list(scenarios.BUILDS),
        'seconds': 10, 'developer_probe_field': 1,
        'pad_script': '1v:start:2,3v:l2:3,4v:r3:1', 'fields': [2, 5],
        'expected_route': 'Invented original input test, not a game room',
        'limits': 'Invented bounded data, no target execution'}


class PrototypeScenarioTests(unittest.TestCase):
    def test_invented_plan_unchanged(self):
        data = plan()
        before = copy.deepcopy(data)
        self.assertEqual(scenarios.validate(data), before)
        self.assertEqual(data, before)

    def test_unknown_schema_and_profile_refused(self):
        for key, value in [('schema', True), ('schema', 2), ('profile', 'retail-usa'),
                           ('name', '../outside'), ('builds', ['auto'])]:
            data = plan(); data[key] = value
            with self.assertRaises(ValueError): scenarios.validate(data)
        data = plan(); data['extra'] = 'unqualified'
        with self.assertRaises(ValueError): scenarios.validate(data)

    def test_budget_cannot_disable_or_silently_extend(self):
        for value in [0, -1, 601, True, '480']:
            data = plan(); data['seconds'] = value
            with self.assertRaises(ValueError): scenarios.validate(data)

    def test_fields_order_identity_bounds(self):
        for fields in [[], [2, 2], [5, 2], [0], [42001], [True], ['2']]:
            data = plan(); data['fields'] = fields
            with self.assertRaises(ValueError): scenarios.validate(data)

    def test_script_refuses_loops_unknown_buttons_and_grammar(self):
        for script in ['', 'loop', '1v:square:2', '1v:start:0', '1v:start:121',
                       '2v:start:2,1v:r3:1', '1v:start:2,1v:r3:1',
                       '42001v:start:2', '1v:start:2\n', '1v:start:2;bad']:
            data = plan(); data['pad_script'] = script
            with self.assertRaises(ValueError): scenarios.validate(data)

    def test_environment_strips_inherited_state_exports_and_selftests(self):
        env = scenarios.environment({'PATH': 'invented', 'ps2x_GS_RECORD': 'unsafe',
            'GODHAND_CONTROLS_SELFTEST': 'unsafe', 'PROTOTYPE_USERDATA_ROOT': 'owner'},
            Path('invented-case'), plan())
        self.assertEqual(env['PATH'], 'invented')
        self.assertNotIn('ps2x_GS_RECORD', env)
        self.assertNotIn('GODHAND_CONTROLS_SELFTEST', env)
        self.assertNotIn('PROTOTYPE_USERDATA_ROOT', env)
        self.assertEqual(env['PROTOTYPE_EXECUTION_PROFILE'], 'diagnostic-v1')
        self.assertEqual(env['PROTOTYPE_PROBE_SECONDS'], '10')
        self.assertEqual(env['PS2X_FAKE_PADS'], '0')
        self.assertEqual(env['PS2X_PAD_SCRIPT'], plan()['pad_script'])
        self.assertEqual([env['PS2X_PAD' + str(i)] for i in range(2, 9)], ['0'] * 7)

    def check(self, root, *, seed=None, bad_identity=False, existing=False):
        directory = root / 'scenarios'; directory.mkdir(exist_ok=True)
        (directory / (scenarios.SCENARIOS[0] + '.json')).write_text(json.dumps(plan()))
        args = ['--scenario', scenarios.SCENARIOS[0], '--build', 'scheduler-candidate-v1',
                '--exe', 'invented-exe', '--elf', 'invented-elf', '--disc', 'invented-disc',
                '--session', 'invented-session', '--check-only']
        if seed is not None: args += ['--controls-seed', str(seed)]
        with mock.patch.object(scenarios, 'ROOT', root), \
             mock.patch.object(scenarios, 'os', SimpleNamespace(name='nt', environ={})), \
             mock.patch.object(scenarios.workbench, 'verify',
                 side_effect=ValueError('invented identity differs') if bad_identity
                 else lambda path, *a: root / path), \
             mock.patch.object(scenarios, 'require_idle') as inventory, \
             mock.patch.object(scenarios.subprocess, 'Popen') as spawn:
            result = scenarios.main(args)
            inventory.assert_not_called(); spawn.assert_not_called()
        if not existing:
            self.assertFalse((root / '.local').exists())
        return result

    def test_check_only_no_output_native_or_inventory(self):
        with tempfile.TemporaryDirectory() as name:
            self.assertEqual(self.check(Path(name)), 0)

    def test_identity_refusal_before_session_creation(self):
        with tempfile.TemporaryDirectory() as name:
            self.assertEqual(self.check(Path(name), bad_identity=True), 2)

    def test_binary_seed_refused_and_original_unchanged(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name); seed = root / 'invented-controls'
            seed.write_bytes(b'invented\0binary')
            self.assertEqual(self.check(root, seed=seed), 2)
            self.assertEqual(seed.read_bytes(), b'invented\0binary')

    def test_existing_session_never_reused(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            target = root / '.local/prototype-scenarios/invented-session'
            target.mkdir(parents=True); marker = target / 'original'; marker.write_text('keep')
            self.assertEqual(self.check(root, existing=True), 2)
            self.assertEqual(marker.read_text(), 'keep')
            self.assertEqual(list(target.iterdir()), [marker])
