"""Original synthetic policy checks; no disc, game strings or rendering fixtures."""
import subprocess
import sys
import unittest
from unittest.mock import patch
import launch_packs
import pc
import profiles


class ProfileTests(unittest.TestCase):
    def test_default_has_no_extensions(self):
        result = profiles.resolve()
        self.assertEqual(result['name'], 'original')
        self.assertEqual(result['requested_extensions'], [])
        self.assertIn('not certified', result['fidelity'])

    def test_original_refuses_pack_and_strict(self):
        for pack, strict in [('invented.json', False), (None, True), ('invented.json', True)]:
            with self.subTest(pack=pack, strict=strict), self.assertRaises(ValueError):
                profiles.resolve('original', pack, strict)

    def test_enhanced_records_only_requested_extension(self):
        self.assertEqual(profiles.resolve('enhanced')['requested_extensions'], [])
        self.assertEqual(profiles.resolve('enhanced', 'invented.json')['requested_extensions'],
                         ['same-size-named-texture'])

    def test_unknown_names_and_invalid_strict_refused(self):
        for name in ['Original', '', None, 'prototype', 'unlocked-fps']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                profiles.resolve(name)
        for strict in [0, 1, 'false', None]:
            with self.subTest(strict=strict), self.assertRaises(ValueError):
                profiles.resolve('enhanced', strict=strict)
        with self.assertRaises(ValueError):
            profiles.resolve('enhanced', strict=True)

    def test_policy_refusal_precedes_runtime_and_disc_checks(self):
        with patch.object(launch_packs.runtime_packs, 'verified_install') as runtime, \
             patch.object(launch_packs.pc, 'verify_disc') as disc, \
             patch.object(launch_packs.subprocess, 'Popen') as child:
            with self.assertRaisesRegex(ValueError, 'Original profile refuses'):
                launch_packs.launch('absent', 'retail-absent', 'absent', pack='invented.json')
            runtime.assert_not_called(); disc.assert_not_called(); child.assert_not_called()

    def test_cli_defaults_to_original(self):
        with patch.object(sys, 'argv', ['pc.py', 'run', '--iso', 'invented.iso']), \
             patch.object(launch_packs, 'launch', return_value={}) as launch, \
             patch('builtins.print'):
            pc.main()
        self.assertEqual(launch.call_args.kwargs['profile'], 'original')

    def test_cli_explicit_enhanced(self):
        with patch.object(sys, 'argv', ['pc.py', 'run', '--iso', 'invented.iso',
                                       '--profile', 'enhanced', '--pack', 'invented.json']), \
             patch.object(launch_packs, 'launch', return_value={}) as launch, \
             patch('builtins.print'):
            pc.main()
        self.assertEqual(launch.call_args.kwargs['profile'], 'enhanced')

    def test_cli_invalid_profile_refused(self):
        result = subprocess.run([sys.executable, str(pc.ROOT/'pc.py'), 'run',
                                 '--iso', 'invented.iso', '--profile', 'unknown'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('invalid choice', result.stderr)


if __name__ == '__main__': unittest.main()
