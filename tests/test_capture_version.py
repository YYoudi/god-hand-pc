"""Invented Git/build/CLI fixtures. No window, native runtime or game data."""
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import json,sys,unittest
import native_menu as menu
import pc,profiles,launch_packs
import test_native_menu_install as fixtures

class CaptureVersionTests(unittest.TestCase):
    def setUp(self):
        self.base=fixtures.NativeMenuInstallTests(methodName='runTest');self.base.setUp();self.addCleanup(self.base.doCleanups)
        f=self.base.f;parent=menu.plan_sources(f.source,f.root,menu.integration(f.root));files=[]
        for name in sorted(menu.CAPTURE_EDITED):
            before=parent[f.source/name];text='// Invented direct-readback addition\n';after=before+text.encode()
            files.append({'path':name,'before_sha256':menu.packs.sha(before),'after_sha256':menu.packs.sha(after),
                          'edits':[{'start':len(before),'end':len(before),'insert':text}]})
        for name in menu.CAPTURE_COPY:(f.root/name).write_bytes(b'// Original invented capture helper\n')
        recipe={'schema':1,'version':menu.layer_name('readback-v2'),'upstream_revision':f.pin['revision'],
                'parent_fingerprint':menu.fingerprint(f.root,menu.integration(f.root)),'files':files,'copies':menu.CAPTURE_COPY}
        (f.root/'adapter/capture_integration.json').write_text(json.dumps(recipe));f.commit(f.root)

    def install(self,step=None):
        f=self.base.f
        with patch.object(menu,'os',f.platform),patch.object(menu.subprocess,'check_output',side_effect=f.output),\
             patch.object(menu.shutil,'disk_usage',return_value=SimpleNamespace(free=16*1024**3)),\
             patch.object(menu.build.Run,'step',autospec=True,side_effect=step or f.fake_build):
            return menu.install(f.root,'retail-fixture','readback-v2')

    def test_additive_version_preserves_old_pointer_fingerprint_binary_and_default(self):
        f=self.base.f;old=self.base.install();pointer=f.workspace/'native-menu-v1/installed.json';raw=pointer.read_bytes()
        current=self.install();f.assert_base()
        self.assertEqual(pointer.read_bytes(),raw)
        self.assertEqual(menu.verified_install(f.root,'retail-fixture')['executable'],old['executable'])
        self.assertEqual(len(current['source_files']),33)
        self.assertEqual(current['parent_fingerprint'],old['menu_fingerprint'])
        self.assertNotEqual(current['menu_fingerprint'],old['menu_fingerprint'])
        self.assertEqual(self.install(lambda *a:self.fail('No relink'))['executable'],current['executable'])

    def test_ordered_preimage_or_parent_drift_refuses_before_build(self):
        f=self.base.f;r=menu.integration(f.root,'readback-v2');r['files'][0]['before_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'preimage'):menu.plan_sources(f.source,f.root,r)
        p=f.root/'adapter/capture_integration.json';r=json.loads(p.read_text());r['parent_fingerprint']='0'*64;p.write_text(json.dumps(r))
        with self.assertRaisesRegex(ValueError,'parent'):menu.integration(f.root,'readback-v2')
        f.assert_base()

    def test_terminal_failure_restores_base_and_retains_new_attempt(self):
        f=self.base.f
        def fail(run,name,*args):
            f.fake_build(run,name,*args)
            if name=='menu-build':raise ValueError('Invented readback link failure')
        with self.assertRaisesRegex(ValueError,'Invented readback'):self.install(fail)
        f.assert_base();self.assertFalse((f.workspace/'native-menu-readback-v2/installed.json').exists())
        with self.assertRaisesRegex(ValueError,'Previous menu attempt'):self.install()

    def test_helper_binary_source_and_receipt_drift_refuse(self):
        f=self.base.f;r=self.install();run=Path(r['receipt']).parent
        for path in [f.root/'adapter/framebuffer_capture.hpp',Path(r['executable']['path']),run/'source'/menu.RUNTIME]:
            raw=path.read_bytes()
            try:
                path.write_bytes(raw+b'Invented drift')
                with self.assertRaises(ValueError):menu.verified_install(f.root,'retail-fixture','readback-v2')
            finally:path.write_bytes(raw)

    def test_live_new_build_keeps_its_own_locks_and_source(self):
        def live(run,*args):run.child=SimpleNamespace(poll=lambda:None);raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):self.install(live)
        self.assertTrue((self.base.f.workspace/'setup.lock').exists())
        self.assertTrue((self.base.f.workspace/'native-menu-readback-v2/install.lock').exists())

class CapturePolicyTests(unittest.TestCase):
    def test_version_without_capability_and_unknown_refuse_before_io(self):
        with patch.object(launch_packs.runtime_packs,'workspace_path') as workspace:
            for opts in [dict(native_menu_version='readback-v2'),dict(native_menu=True,video_settings=True,native_menu_version='invented')]:
                with self.assertRaises(ValueError):launch_packs.launch('no-create','missing','missing',profile='enhanced',**opts)
        workspace.assert_not_called()

    def test_explicit_cli_version_and_default_old_policy(self):
        with patch.object(sys,'argv',['pc.py','install-native-menu','--version','readback-v2']),\
             patch.object(menu,'install',return_value={}) as install,patch('builtins.print'):
            pc.main()
        install.assert_called_once_with(pc.ROOT,'retail-setup','readback-v2')
        with patch.object(sys,'argv',['pc.py','run','--iso','invented','--profile','enhanced','--native-menu','--video-settings','--native-menu-version','readback-v2']),\
             patch.object(launch_packs,'launch',return_value={}) as run,patch('builtins.print'):
            pc.main()
        self.assertEqual(run.call_args.kwargs['native_menu_version'],'readback-v2')
        self.assertEqual(profiles.resolve('enhanced',native_menu=True,video_settings=True)['requested_extensions'][-1],
                         'experimental-native-video-menu-audio-v2')
        self.assertTrue(profiles.resolve('enhanced',native_menu=True,video_settings=True,native_menu_version='readback-v2')['requested_extensions'][-1].endswith('readback-v2'))
