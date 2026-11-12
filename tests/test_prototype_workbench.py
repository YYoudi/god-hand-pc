"""Original invented files/env only. No real executable, disc, runtime or UI."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from types import SimpleNamespace
import prototype_workbench as w


class PrototypeWorkbenchTests(unittest.TestCase):
    def test_default_build_identity_and_userdata_remain_native07(self):
        self.assertEqual(w.build_profile('native07'), {
            'sha256': w.BUILD_SHA256, 'default_user_data': 'prototype-default'})
        self.assertEqual(w.BUILD_SHA256,
            '0afc8392bcab3db0aeb2ef3c9d57d9530598a408c68fa707091db56ac195c2e6')

    def test_explicit_combined_profile_has_separate_identity_and_userdata(self):
        profile=w.build_profile('room01-v1')
        self.assertEqual(profile['sha256'],
            '4acf41e7d0495dbb883629dc9a12b15dc7e0b33b6bee10ea6a97bbeef8f047f7')
        self.assertNotEqual(profile['default_user_data'],
                            w.build_profile('native07')['default_user_data'])
        profile['sha256']='invented mutation'
        self.assertNotEqual(w.build_profile('room01-v1')['sha256'],profile['sha256'])

    def test_unknown_build_profiles_never_fall_back_or_auto_detect(self):
        for name in ['', 'latest', '../outside', None, []]:
            with self.assertRaises(ValueError): w.build_profile(name)

    def test_source_profile_is_explicit_and_keeps_both_old_profiles_unchanged(self):
        profile=w.build_profile('source-v1')
        self.assertEqual(profile['sha256'],
            'e677f789c9f51400ba054b5a72ab7807f363a5bd4c099ba10f5c2c07edcc8e34')
        self.assertEqual(profile['default_user_data'],'prototype-source')
        self.assertEqual(w.build_profile('room01-v1'),{
            'sha256':'4acf41e7d0495dbb883629dc9a12b15dc7e0b33b6bee10ea6a97bbeef8f047f7',
            'default_user_data':'prototype-room01'})
        self.assertEqual(len({w.build_profile(n)['default_user_data'] for n in w.BUILD_PROFILES}),3)
        profile['sha256']='invented mutation'
        self.assertNotEqual(w.build_profile('source-v1')['sha256'],profile['sha256'])

    def check_only_profile(self, profile=None, user=None):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            args=['--exe','invented-exe','--elf','invented-elf','--disc','invented-disc',
                  '--session','invented-session','--check-only']
            if profile is not None: args+=['--build',profile]
            if user is not None: args+=['--user-data',user]
            with mock.patch.object(w,'ROOT',root), \
                 mock.patch.object(w,'os',SimpleNamespace(name='nt',environ={})), \
                 mock.patch.object(w,'verify',side_effect=lambda path,*a:root/path) as verify, \
                 mock.patch.object(w,'launch_environment',wraps=w.launch_environment) as environment, \
                 mock.patch.object(w.subprocess,'Popen') as spawn:
                self.assertEqual(w.main(args),0)
                selected=w.build_profile(profile or 'native07')
                self.assertEqual(verify.call_args_list[0].args,
                                 ('invented-exe',selected['sha256']))
                self.assertEqual(environment.call_args.args[1],root/'.local'/
                    'prototype-workbench'/'userdata'/
                    (user if user is not None else selected['default_user_data']))
                spawn.assert_not_called()
            self.assertFalse((root/'.local').exists())

    def test_default_check_only_uses_old_build_without_output_or_process(self):
        self.check_only_profile()

    def test_combined_check_only_uses_explicit_build_without_output_or_process(self):
        self.check_only_profile('room01-v1')

    def test_source_check_only_uses_explicit_build_without_output_or_process(self):
        self.check_only_profile('source-v1')

    def test_source_profile_explicit_userdata_stays_owner_choice(self):
        self.check_only_profile('source-v1','invented-explicit-source-user')

    def test_unsupported_executable_never_creates_a_source_session(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            args=['--build','source-v1','--exe','invented-wrong','--elf','invented',
                  '--disc','invented','--session','invented-session']
            with mock.patch.object(w,'ROOT',root),mock.patch.object(w,'os',SimpleNamespace(name='nt',environ={})),\
                 mock.patch.object(w,'verify',side_effect=ValueError('Invented identity differs')),\
                 mock.patch.object(w.subprocess,'Popen') as spawn:
                self.assertEqual(w.main(args),2);spawn.assert_not_called()
            self.assertFalse((root/'.local').exists())

    def test_explicit_user_data_name_is_not_silently_replaced(self):
        self.check_only_profile('room01-v1','invented-explicit-user')

    def test_environment_strips_case_insensitive_automatic_and_future_flags(self):
        parent={'PATH':'invented', 'Ps2x_PAD_SCRIPT':'unsafe', 'PROTOTYPE_FUTURE':'unsafe',
                'godhand_state_load':'unsafe', 'PS2X_AUDIO_MUTE':'0', 'PROTOTYPE_PROBE_SECONDS':'90'}
        env=w.launch_environment(parent, Path('invented-data'))
        self.assertEqual(env['PATH'], 'invented')
        self.assertNotIn('Ps2x_PAD_SCRIPT', env)
        self.assertNotIn('PROTOTYPE_FUTURE', env)
        self.assertNotIn('godhand_state_load', env)
        self.assertEqual(env['PROTOTYPE_PROBE_SECONDS'], '0')
        self.assertEqual(env['PS2X_AUDIO_MUTE'], '1')
        self.assertEqual(env['PROTOTYPE_PROBE_VISIBLE'], '1')
        self.assertEqual([env['PS2X_PAD'+str(i)] for i in range(2,9)], ['0']*7)

    def test_invented_identity_guard_and_readonly_preparation(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); f=root/'invented'; f.write_bytes(b'original test only')
            h=hashlib.sha256(f.read_bytes()).hexdigest()
            self.assertEqual(w.verify(f,h,f.stat().st_size), f.absolute())
            for digest,size in [('0'*64,f.stat().st_size),(h,1)]:
                with self.assertRaises(ValueError):w.verify(f,digest,size)
            self.assertEqual(f.read_bytes(),b'original test only')
            if os.name == 'nt':
                missing=root/'missing-\u00e9.exe'
                r=subprocess.run([sys.executable,w.__file__,'--exe',str(missing),
                    '--elf','invented','--disc','invented','--session','one'],
                    env=dict(os.environ,PYTHONIOENCODING='ascii'),capture_output=True,timeout=20)
                self.assertEqual(r.returncode,2)
                self.assertIn('missing-\u00e9.exe',r.stderr.decode('utf8'))
            p=w.private_path(root,'prototype-workbench','sessions','one-2')
            self.assertFalse(p.exists())
            for name in ['../outside','UPPER','', 'a/b','a'*65]:
                with self.assertRaises(ValueError):w.private_path(root,name)

    def test_original_defaults_are_keyboard_only(self):
        import configparser
        c=configparser.ConfigParser(); c.read_string(w.CONTROLS)
        keys=['Cross','Circle','Square','Triangle','L1','R1','L2','R2','L3','R3','Start','Select',
              'Up','Down','Left','Right','LUp','LDown','LLeft','LRight','RUp','RDown','RLeft','RRight']
        for key in keys:
            value=c['Pad1'][key]
            self.assertTrue(not value or value.startswith('Keyboard/'))
        self.assertNotIn('SDL',w.CONTROLS)


if __name__=='__main__':unittest.main()
