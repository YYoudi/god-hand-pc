"""Invented native process doubles, explicit version selection and refusal gates."""
from pathlib import Path
from types import SimpleNamespace
import json
import os
import tempfile
import unittest
from unittest.mock import patch

import launch_packs as launch
import profiles


class HDGPUVersionPolicyTests(unittest.TestCase):
    def test_version_and_capability_errors_refuse_before_workspace_disc_or_process(self):
        cases = [dict(hd_textures=True, hd_textures_version='gpu-v2'),
                 dict(profile='enhanced', hd_textures_version='gpu-v2'),
                 dict(profile='enhanced', hd_textures=True, hd_textures_version='unknown'),
                 dict(profile='enhanced', hd_textures=True, hd_textures_version=True),
                 dict(profile='enhanced', hd_textures=True, hd_textures_version='gpu-v2', pack='old'),
                 dict(profile='enhanced', hd_textures=True, hd_textures_version='gpu-v2', controls_pause=True)]
        with patch.object(launch.runtime_packs, 'workspace_path') as workspace, \
             patch.object(launch.hd, 'verified_install') as hd, \
             patch.object(launch.pc, 'verify_disc') as disc, patch.object(launch.subprocess, 'Popen') as child:
            for flags in cases:
                with self.subTest(flags=flags), self.assertRaises(ValueError):
                    launch.launch('must-not-create', 'retail-fixture', 'missing', **flags)
            workspace.assert_not_called(); hd.assert_not_called(); disc.assert_not_called(); child.assert_not_called()

    def test_requested_extensions_keep_legacy_default_distinct(self):
        old = profiles.resolve('enhanced', hd_textures=True)
        self.assertEqual(old, profiles.resolve('enhanced', hd_textures=True, hd_textures_version='v1'))
        self.assertEqual(old['requested_extensions'], ['experimental-hd-textures'])
        self.assertEqual(profiles.resolve('enhanced', hd_textures=True, hd_textures_version='gpu-v2')['requested_extensions'],
                         ['experimental-hd-textures-gpu-v2'])

    def test_actual_launcher_selects_gpu_layer_but_never_infers_match_count(self):
        with tempfile.TemporaryDirectory(prefix='godhand-gpu-version-synthetic-') as name:
            root = Path(name).resolve(); (root/'.local/retail-fixture').mkdir(parents=True)
            exe = root/'invented-not-executable.txt'; exe.write_bytes(b'Original invented data, not a program')
            variant = {'executable': {'path': str(exe)}, 'source_revision': 'a'*40,
                       'adapter_fingerprint': 'b'*64, 'hd_fingerprint': 'c'*64,
                       'controls_adoption_executable': str(exe)}
            platform = SimpleNamespace(name='nt', environ={'PATH': os.environ.get('PATH', ''),
                'GODHAND_PC_HD_TIMING': '1', 'GODHAND_PC_HD_SHA256': 'stale', 'PS2X_STATE_LOAD_AT': 'stale'})
            child = SimpleNamespace(pid=987654, wait=lambda **kw: 124)
            with patch.object(launch, 'os', platform), \
                 patch.object(launch.hd, 'verified_install', return_value=variant) as hd, \
                 patch.object(launch.pause, 'verified_install') as pause, \
                 patch.object(launch.runtime_packs, 'verified_install') as base, \
                 patch.object(launch.pc, 'verify_disc', return_value={'path': 'invented-disc-not-opened'}), \
                 patch.object(launch.pc, 'load_pin', return_value={'retail_profile': {}}), \
                 patch.object(launch.pc, 'git', return_value='d'*40), patch.object(launch.build, 'require_no_game'), \
                 patch.object(launch.subprocess, 'CREATE_NO_WINDOW', 0, create=True), \
                 patch.object(launch.subprocess, 'BELOW_NORMAL_PRIORITY_CLASS', 0, create=True), \
                 patch.object(launch.subprocess, 'Popen', return_value=child) as spawn:
                result = launch.launch(root, 'retail-fixture', 'not-opened', profile='enhanced',
                                       hd_textures=True, hd_textures_version='gpu-v2', headless=True,
                                       seconds=10, fresh_user_data=True)
            hd.assert_called_once_with(root, 'retail-fixture', 'gpu-v2')
            pause.assert_not_called(); base.assert_not_called()
            saved = json.loads(Path(result['receipt']).read_text())
            self.assertEqual(saved['hd_textures']['version'], 'hd-gpu-v2')
            self.assertIn('unread', saved['hd_textures']['runtime_application'])
            self.assertNotIn('GODHAND_PC_HD_TIMING', spawn.call_args.kwargs['env'])
            self.assertEqual(spawn.call_args.kwargs['env']['GODHAND_PC_HD_FILE'], '')
