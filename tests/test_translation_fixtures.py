"""Original ELF/control-flow fixtures, no game bytes or external tool required."""
from pathlib import Path
import hashlib
import json
import struct
import tempfile
import tomllib
import unittest
import translation_fixtures as f


class TranslationFixtureTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory(prefix='godhand-invented-translation-')
        self.root=Path(t.name).resolve()
        assert self.root.is_relative_to(Path(tempfile.gettempdir()).resolve())
        self.addCleanup(t.cleanup)

    def test_elf_headers_and_file_bounds(self):
        for name,(_,words,_,_) in f.CASES.items():
            with self.subTest(name=name):
                raw=f.minimal_elf(words)
                h=struct.unpack_from('<16sHHIIIIIHHHHHH',raw)
                self.assertEqual(h[0][:7],b'\x7fELF\x01\x01\x01')
                self.assertEqual(h[1:5],(2,8,1,f.BASE))
                self.assertEqual((h[9],h[10],h[11],h[12],h[13]),(32,1,40,3,2))
                p=struct.unpack_from('<8I',raw,h[5])
                self.assertEqual(p,(1,4096,f.BASE,f.BASE,4*len(words),4*len(words),5,4096))
                self.assertLessEqual(h[6]+3*40,len(raw))
                self.assertEqual(struct.unpack_from('<'+'I'*len(words),raw,p[1]),words)

    def test_branch_target_reaches_fault_beyond_other_return(self):
        _,words,offset,outcomes=f.CASES['branch-ingress']
        target=f.BASE+4+(words[0]&0xffff)*4
        self.assertEqual(target,f.BASE+offset)
        self.assertEqual(words[2],f.JR_RA)
        self.assertGreater(offset,2*4)
        self.assertEqual([r['outcome'] for r in outcomes],['returns','throws'])

    def test_return_and_reachable_fault_controls_are_distinct(self):
        dead=f.CASES['return-tail']; live=f.CASES['reachable-fault']
        self.assertGreater(dead[2],dead[1].index(f.JR_RA)*4+4)
        self.assertEqual(live[2],0)
        self.assertEqual(live[1][0],f.FAULT)

    def test_malformed_word_inputs_refused(self):
        for words in [[],[True],[-1],[0x100000000],[0]*1025]:
            with self.subTest(words=words[:2]),self.assertRaises(ValueError): f.minimal_elf(words)
        for base in [0,-16,f.BASE+4,True,0x02000000]:
            with self.subTest(base=base),self.assertRaises(ValueError): f.minimal_elf([0],base)

    def test_suite_configs_maps_and_hashes_are_self_consistent(self):
        result=f.write_suite(self.root/'suite')
        self.assertEqual(len(result['cases']),3)
        for c in result['cases']:
            raw=Path(c['input']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),c['sha256'])
            config=tomllib.loads(Path(c['config']).read_text())['general']
            self.assertEqual(Path(config['input']),Path(c['input']))
            self.assertEqual(config['output_worker_threads'],1)
            self.assertFalse(config['auto_stub_by_name'])
            self.assertTrue(Path(c['map']).read_text().startswith('Name,Start,End,Size\nInvented'))
            self.assertEqual(json.loads(Path(c['input']).with_name('expected.json').read_text())['expected'],c['expected'])

    def test_existing_destination_preserved(self):
        target=self.root/'suite';target.mkdir();sentinel=target/'keep.txt';sentinel.write_text('invented owner note')
        with self.assertRaises(FileExistsError): f.write_suite(target)
        self.assertEqual(sentinel.read_text(),'invented owner note')

    def test_cli_containment_refuses_public_root_or_escape(self):
        for target in [self.root,self.root/'.local',self.root/'outside']:
            with self.subTest(target=target),self.assertRaises(ValueError): f.private_output(target,self.root)
        self.assertEqual(f.private_output(self.root/'.local'/'suite',self.root),self.root/'.local'/'suite')


if __name__=='__main__': unittest.main()
