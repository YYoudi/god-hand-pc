"""Original invented files/env only. No real executable, disc, runtime or UI."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import prototype_workbench as w


class PrototypeWorkbenchTests(unittest.TestCase):
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
