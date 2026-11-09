"""Original invented Git fixtures for additive HD version identity/preservation."""
from pathlib import Path
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import hd_textures as hd
import pc
import test_hd_install as fixtures


class HDGPUInstallTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.HDInstallTests(methodName='runTest')
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.f.recipe(hd.MODIFIED, hd.copies('gpu-v2'), 'adapter/hd_gpu_integration.json',
                      version=hd.layer_name('gpu-v2'))
        (self.f.root/'adapter/hd_runtime_gpu.inc').write_bytes(b'// Original invented GPU-only helper.\n')
        self.f.commit(self.f.root)

    def install(self, version='gpu-v2', step=None):
        f = self.f
        with patch.object(hd, 'os', f.platform), \
             patch.object(hd.subprocess, 'check_output', side_effect=f.output), \
             patch.object(hd.build.Run, 'step', autospec=True, side_effect=step or f.fake_build):
            return hd.install(f.root, 'retail-fixture', version)

    def test_old_default_and_gpu_install_coexist_without_overwriting_pointers(self):
        old = self.install('v1'); pointer = self.f.workspace/'hd-v1/installed.json'
        original = pointer.read_bytes()
        new = self.install(); self.f.assert_base()
        self.assertEqual(pointer.read_bytes(), original)
        self.assertEqual(old['hd_version'], 'hd-v1'); self.assertEqual(new['hd_version'], 'hd-gpu-v2')
        self.assertNotEqual(old['hd_fingerprint'], new['hd_fingerprint'])
        self.assertNotEqual(old['source_revision'], new['source_revision'])
        self.assertEqual(len(new['source_files']), 14)
        self.assertEqual(hd.verified_install(self.f.root, 'retail-fixture')['executable'], old['executable'])
        self.assertEqual(self.install(step=lambda *a: self.fail('Must not rebuild'))['executable'], new['executable'])
        self.assertFalse((self.f.workspace/'setup.lock').exists())

    def test_terminal_failure_keeps_old_version_and_retained_gpu_attempt(self):
        old = self.install('v1')
        def fail(run, name, *args):
            self.f.fake_build(run, name, *args)
            if name == 'hd-build': raise ValueError('Invented GPU terminal build failure')
        with self.assertRaisesRegex(ValueError, 'Invented GPU terminal'): self.install(step=fail)
        self.f.assert_base()
        self.assertEqual(hd.verified_install(self.f.root, 'retail-fixture')['executable'], old['executable'])
        self.assertFalse((self.f.workspace/'hd-gpu-v2/installed.json').exists())
        self.assertTrue((self.f.workspace/'hd-gpu-v2/attempt.json').exists())
        with self.assertRaisesRegex(ValueError, 'Previous HD attempt'): self.install()

    def test_live_interruption_keeps_gpu_source_and_owned_locks(self):
        def live(run, *args):
            run.child = SimpleNamespace(poll=lambda: None)
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt): self.install(step=live)
        self.assertTrue((self.f.workspace/'setup.lock').exists())
        self.assertTrue((self.f.workspace/'hd-gpu-v2/install.lock').exists())
        self.assertFalse((self.f.workspace/'hd-v1/install.lock').exists())
        self.assertNotEqual(pc.git('rev-parse', 'HEAD', cwd=self.f.source), self.f.base['source_revision'])

    def test_gpu_source_helper_binary_and_cross_version_pointer_drift_refuse(self):
        self.install('v1'); new = self.install()
        for path in [Path(new['executable']['path']), Path(new['receipt']).parent/'source'/hd.GPU,
                     self.f.root/'adapter/hd_runtime_gpu.inc']:
            before = path.read_bytes()
            try:
                path.write_bytes(before+b'invented drift')
                with self.assertRaises(ValueError): hd.verified_install(self.f.root, 'retail-fixture', 'gpu-v2')
                hd.verified_install(self.f.root, 'retail-fixture')
            finally: path.write_bytes(before)
        pointer = self.f.workspace/'hd-gpu-v2/installed.json'; before = pointer.read_bytes()
        try:
            pointer.write_bytes((self.f.workspace/'hd-v1/installed.json').read_bytes())
            with self.assertRaises((ValueError, OSError)):
                hd.verified_install(self.f.root, 'retail-fixture', 'gpu-v2')
        finally: pointer.write_bytes(before)
        self.f.assert_base()

    def test_unknown_version_refuses_before_filesystem_or_runtime_access(self):
        with patch.object(hd.packs, 'verified_install') as base, \
             patch.object(hd.packs, 'workspace_path') as workspace:
            for bad in [None, True, 1, [], 'unknown', '../v1']:
                with self.subTest(version=bad), self.assertRaises(ValueError):
                    hd.verified_install('must-not-create', 'retail-fixture', bad)
                with self.subTest(install=bad), self.assertRaises(ValueError):
                    hd.install('must-not-create', 'retail-fixture', bad)
            base.assert_not_called(); workspace.assert_not_called()

    def test_public_recipe_scope_and_old_fingerprint_stay_fixed(self):
        old = hd.integration(pc.ROOT); new = hd.integration(pc.ROOT, 'gpu-v2')
        self.assertEqual(hd.fingerprint(pc.ROOT, old),
                         '9477f5e5fdcd65cb16d928e6a22732438122acea456858823dde9cad6161ac70')
        self.assertNotEqual(hd.fingerprint(pc.ROOT, old), hd.fingerprint(pc.ROOT, new))
        self.assertEqual(new['copies'], hd.copies('gpu-v2'))
        self.assertEqual({x['path'] for x in old['files']}, {x['path'] for x in new['files']})
        self.assertEqual([x['before_sha256'] for x in old['files']],
                         [x['before_sha256'] for x in new['files']])
        self.assertTrue(all('generated' not in p for p in new['copies'].values()))
