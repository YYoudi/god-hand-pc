"""Original invented source/Git/data doubles; never retail or native programs."""
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import controls_pause as audio
import hd_textures as hd
import pc
import test_hd_install as fixtures


class HDAudioInstallTests(unittest.TestCase):
    def setUp(self):
        self.f=fixtures.HDInstallTests(methodName='runTest');self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.f.recipe(hd.MODIFIED,hd.copies('gpu-v2'),'adapter/hd_gpu_integration.json',version=hd.layer_name('gpu-v2'))
        self.f.recipe(audio.MODIFIED,audio.AUDIO_COPIES,'adapter/audio_controls_integration.json',version='audio-v2')
        self.f.commit(self.f.root)

    def install(self,version='gpu-audio-v3',step=None):
        with patch.object(hd,'os',self.f.platform),patch.object(hd.subprocess,'check_output',side_effect=self.f.output),\
             patch.object(hd.build.Run,'step',autospec=True,side_effect=step or self.f.fake_build):
            return hd.install(self.f.root,'retail-fixture',version)

    def test_disjoint_recipe_union_and_immutable_public_component_fingerprints(self):
        recipe=hd.integration(pc.ROOT,'gpu-audio-v3')
        self.assertEqual(len(recipe['files']),6);self.assertEqual(len(recipe['copies']),8)
        self.assertEqual(len(set(recipe['copies'].values())),8)
        self.assertEqual({x['path'] for x in recipe['files']},hd.MODIFIED|audio.MODIFIED)
        self.assertEqual(recipe['component_fingerprints'],{
            'gpu-v2':'37018376887e83eac9f3356f528f062811ac152f6715131abae2a4875e1cbcb5',
            'audio-v2':'1b1202fc25b238017c9c6b02b1e297855b8f18c928bfaf173e994e3e8a5b5624'})
        self.assertEqual(hd.fingerprint(pc.ROOT,hd.integration(pc.ROOT)),
                         '9477f5e5fdcd65cb16d928e6a22732438122acea456858823dde9cad6161ac70')
        self.assertEqual(hd.fingerprint(pc.ROOT,recipe),
                         '72ceaf2309cd86aedbc1d9f122f36464bf3a65a82874a69594aad65f86ea8fa9')
        for component in [hd.integration(pc.ROOT,'gpu-v2'),audio.integration(pc.ROOT,'audio-v2')]:
            for item in component['files']:self.assertIn(item,recipe['files'])

    def test_additive_install_preserves_old_hd_and_audio_pointers_and_complete_source_union(self):
        old={v:self.install(v) for v in ['v1','gpu-v2']}
        with patch.object(audio,'os',self.f.platform),patch.object(audio.subprocess,'check_output',side_effect=self.f.output),\
             patch.object(audio.build.Run,'step',autospec=True,side_effect=self.f.fake_build):
            a=audio.install(self.f.root,'retail-fixture','audio-v2')
        pointers={p:p.read_bytes() for p in self.f.workspace.glob('*/installed.json')}
        result=self.install();self.f.assert_base()
        for path,blob in pointers.items():self.assertEqual(path.read_bytes(),blob)
        self.assertEqual(result['controls_fingerprint'],result['component_fingerprints']['audio-v2'])
        expected=set(self.f.base['source_files'])|hd.modified('gpu-audio-v3')|set(hd.copies('gpu-audio-v3').values())
        self.assertEqual(set(result['source_files']),expected)
        for v,r in old.items():self.assertEqual(hd.verified_install(self.f.root,'retail-fixture',v)['executable'],r['executable'])
        self.assertEqual(audio.verified_install(self.f.root,'retail-fixture','audio-v2')['executable'],a['executable'])
        self.assertEqual(self.install(step=lambda *args:self.fail('Must not relink'))['source_revision'],result['source_revision'])

    def test_component_helper_receipt_source_binary_and_pointer_drift_refuse(self):
        old=self.install('gpu-v2');new=self.install();run=Path(new['receipt']).parent
        for p in [Path(new['executable']['path']),run/'source'/hd.GPU,
                  run/'source'/next(iter(audio.MODIFIED)),self.f.root/'adapter/audio_activity.hpp']:
            before=p.read_bytes()
            try:
                p.write_bytes(before+b'Original invented drift')
                with self.assertRaises(ValueError):hd.verified_install(self.f.root,'retail-fixture','gpu-audio-v3')
            finally:p.write_bytes(before)
        receipt=Path(new['receipt']);before=receipt.read_bytes();data=json.loads(before)
        try:
            data['component_fingerprints']['audio-v2']='0'*64;receipt.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'component'):hd.verified_install(self.f.root,'retail-fixture','gpu-audio-v3')
        finally:receipt.write_bytes(before)
        pointer=self.f.workspace/'hd-gpu-audio-v3/installed.json';before=pointer.read_bytes()
        try:
            pointer.write_bytes((self.f.workspace/'hd-gpu-v2/installed.json').read_bytes())
            with self.assertRaises((ValueError,OSError)):hd.verified_install(self.f.root,'retail-fixture','gpu-audio-v3')
        finally:pointer.write_bytes(before)
        self.assertEqual(hd.verified_install(self.f.root,'retail-fixture','gpu-v2')['executable'],old['executable'])

    def test_overlapping_owned_copy_destinations_refuse(self):
        bad=dict(audio.AUDIO_COPIES);bad['adapter/audio_activity.hpp']=next(iter(hd.copies('gpu-v2').values()))
        with patch.object(audio,'AUDIO_COPIES',bad),self.assertRaisesRegex(ValueError,'overlap'):
            hd.copies('gpu-audio-v3')

    def test_terminal_failure_retains_attempt_without_publishing_or_overwriting_old_pointer(self):
        old=self.install('gpu-v2')
        def fail(run,name,*args):
            self.f.fake_build(run,name,*args)
            if name=='hd-build':raise ValueError('Invented composite terminal failure')
        with self.assertRaisesRegex(ValueError,'Invented composite'):self.install(step=fail)
        self.f.assert_base();layer=self.f.workspace/'hd-gpu-audio-v3'
        self.assertFalse((layer/'installed.json').exists());self.assertTrue((layer/'attempt.json').exists())
        self.assertEqual(hd.verified_install(self.f.root,'retail-fixture','gpu-v2')['executable'],old['executable'])
        with self.assertRaisesRegex(ValueError,'Previous HD attempt'):self.install()

    def test_live_interruption_preserves_owned_source_and_locks(self):
        def live(run,*args):run.child=SimpleNamespace(poll=lambda:None);raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):self.install(step=live)
        self.assertTrue((self.f.workspace/'setup.lock').exists())
        self.assertTrue((self.f.workspace/'hd-gpu-audio-v3/install.lock').exists())
        self.assertNotEqual(pc.git('rev-parse','HEAD',cwd=self.f.source),self.f.base['source_revision'])
