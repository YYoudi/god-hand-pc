"""Original policy/process doubles; no game data, native executable or device."""
from pathlib import Path
from types import SimpleNamespace
import json,os,sys,tempfile,unittest
from unittest.mock import patch
import launch_packs as launch
import profiles
import pc

FLAGS=dict(profile='enhanced',hd_textures=True,hd_textures_version='gpu-audio-v3',
           controls_pause=True,controls_pause_version='audio-v2')


class HDAudioPolicyTests(unittest.TestCase):
    def test_incomplete_wrong_component_and_old_combinations_refuse_before_io(self):
        cases=[{**FLAGS,k:v} for k,v in [('profile','original'),('hd_textures',False),
               ('controls_pause',False),('controls_pause_version',None),('controls_pause_version','v1'),
               ('hd_textures_version','gpu-v2'),('hd_textures_version',None),('pack','old'),('strict',True)]]
        cases += [dict(profile='enhanced',hd_textures=True,hd_textures_version='gpu-audio-v3')]
        with patch.object(launch.runtime_packs,'workspace_path') as workspace,patch.object(launch.hd,'verified_install') as hd,\
             patch.object(launch.pc,'verify_disc') as disc,patch.object(launch.subprocess,'Popen') as child:
            for case in cases:
                with self.subTest(case=case),self.assertRaises(ValueError):launch.launch('no-create','retail-fixture','missing',**case)
            workspace.assert_not_called();hd.assert_not_called();disc.assert_not_called();child.assert_not_called()

    def test_exact_joint_selection_is_explicit_and_old_defaults_do_not_change(self):
        p=profiles.resolve('enhanced',hd_textures=True,hd_textures_version='gpu-audio-v3',
                           controls_pause=True,controls_pause_version='audio-v2')
        self.assertEqual(p['requested_extensions'],['experimental-controls-pause-audio-v2','experimental-hd-textures-gpu-audio-v3'])
        self.assertEqual(profiles.resolve()['requested_extensions'],[])
        self.assertEqual(profiles.resolve('enhanced',hd_textures=True)['requested_extensions'],['experimental-hd-textures'])

    def test_public_cli_routes_the_new_version_without_inventing_a_default_bundle(self):
        with patch.object(sys,'argv',['pc.py','install-hd-textures','--version','gpu-audio-v3']),\
             patch.object(launch.hd,'install',return_value={}) as install,patch('builtins.print'):
            pc.main()
        self.assertEqual(install.call_args.args[2],'gpu-audio-v3')
        with patch.object(sys,'argv',['pc.py','run','--iso','invented.iso','--profile','enhanced',
                '--hd-textures','--hd-textures-version','gpu-audio-v3','--controls-pause','--controls-pause-version','audio-v2']),\
             patch.object(launch,'launch',return_value={}) as run,patch('builtins.print'):
            pc.main()
        self.assertEqual(run.call_args.kwargs['hd_textures_version'],'gpu-audio-v3')
        self.assertEqual(run.call_args.kwargs['controls_pause_version'],'audio-v2')

    def test_launcher_uses_one_verified_composite_binary_and_records_both_identities(self):
        with tempfile.TemporaryDirectory(prefix='godhand-hd-audio-synthetic-') as name:
            root=Path(name).resolve();(root/'.local/retail-fixture').mkdir(parents=True)
            exe=root/'invented-not-executable.txt';exe.write_bytes(b'Original invented data')
            components={'audio-v2':'e'*64,'gpu-v2':'f'*64}
            variant={'executable':{'path':str(exe)},'source_revision':'a'*40,'adapter_fingerprint':'b'*64,
                     'hd_fingerprint':'c'*64,'controls_fingerprint':components['audio-v2'],
                     'component_fingerprints':components,'controls_adoption_executable':str(exe)}
            platform=SimpleNamespace(name='nt',environ={'PATH':os.environ.get('PATH',''),
                'GODHAND_CONTROLS_SELFTEST':'f1,done','GODHAND_PC_CONTROLS_PROBE':'1','PS2X_STATE_LOAD_AT':'stale'})
            child=SimpleNamespace(pid=987654,wait=lambda **kwargs:124)
            with patch.object(launch,'os',platform),patch.object(launch.hd,'verified_install',return_value=variant) as hd,\
                 patch.object(launch.pause,'verified_install') as pause,patch.object(launch.runtime_packs,'verified_install') as base,\
                 patch.object(launch.pc,'verify_disc',return_value={'path':'invented-disc-not-opened'}),\
                 patch.object(launch.pc,'load_pin',return_value={'retail_profile':{}}),\
                 patch.object(launch.pc,'git',return_value='d'*40),patch.object(launch.build,'require_no_game'),\
                 patch.object(launch.subprocess,'CREATE_NO_WINDOW',0,create=True),\
                 patch.object(launch.subprocess,'BELOW_NORMAL_PRIORITY_CLASS',0,create=True),\
                 patch.object(launch.subprocess,'Popen',return_value=child) as spawn:
                result=launch.launch(root,'retail-fixture','not-opened',headless=True,seconds=10,fresh_user_data=True,**FLAGS)
            hd.assert_called_once_with(root,'retail-fixture','gpu-audio-v3');pause.assert_not_called();base.assert_not_called()
            saved=json.loads(Path(result['receipt']).read_text())
            self.assertEqual(saved['component_fingerprints'],components)
            self.assertEqual(saved['controls_pause']['fingerprint'],components['audio-v2'])
            self.assertEqual(saved['hd_textures']['version'],'hd-gpu-audio-v3')
            self.assertIn('unread',saved['hd_textures']['runtime_application'])
            self.assertIn('not inferred',saved['controls_pause']['acknowledged_hold'])
            env=spawn.call_args.kwargs['env'];self.assertEqual(env['GODHAND_PC_CONTROLS_PAUSE'],'1')
            self.assertEqual(env['GODHAND_PC_CONTROLS_PROBE'],'0');self.assertEqual(env['GODHAND_CONTROLS_SELFTEST'],'0')
            self.assertNotIn('PS2X_STATE_LOAD_AT',env)
