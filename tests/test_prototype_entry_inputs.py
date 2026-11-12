"""Original invented dependency/source/ELF/disc fixtures, no game/vendor code."""
from contextlib import contextmanager,redirect_stdout,redirect_stderr
import hashlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

import prototype_entry_inputs as cli
from prototype_entries import Section
from test_prototype_entries import local_fixture,module_bytes
from test_prototype_sdk import invented_elf


def sha(blob):return hashlib.sha256(blob).hexdigest()


@contextmanager
def source_fixture():
    with tempfile.TemporaryDirectory(prefix='entry-dep-invented-') as tmp:
        root=Path(tmp);folder=root/'tools/snr2';folder.mkdir(parents=True)
        fmt=b'INVENTED_ONLY = True\n'
        link=b'''from snr2fmt import INVENTED_ONLY
class Registry:
 @staticmethod
 def from_boot_elf(elf, *, sndata_va):
  return (elf, sndata_va, INVENTED_ONLY)
'''
        (folder/'snr2fmt.py').write_bytes(fmt);(folder/'snr2link.py').write_bytes(link)
        def git(args,**kwargs):
            if args[1]=='rev-parse':return cli.REGISTRY_REVISION+'\n'
            return fmt if args[-1].endswith('snr2fmt.py') else link
        with mock.patch.object(cli.subprocess,'check_output',side_effect=git),mock.patch.dict(sys.modules):
            sys.modules.pop('snr2fmt',None)
            yield root,folder


def discovery_digest(folder):
    h=hashlib.sha256()
    for p in sorted(folder.glob('*.cpp'),key=lambda p:p.name):
        h.update((p.name+'\0'+sha(p.read_bytes())+'\n').encode('utf-8'))
    return h.hexdigest()


@contextmanager
def fixture():
    with tempfile.TemporaryDirectory(prefix='entry-inputs-invented-') as tmp:
        root=Path(tmp);subprocess.run(['git','init','--quiet',str(root)],check=True,capture_output=True)
        (root/'.gitignore').write_text('.local/\n',encoding='utf-8')
        elf=invented_elf();(root/'original.elf').write_bytes(elf)
        disc=b'original invented disc envelope'.ljust(2048,b'\0');(root/'original.disc').write_bytes(disc)
        folder=root/'discovery';folder.mkdir()
        (folder/'register_functions.cpp').write_text('struct GeneratedFunctionTableInitializer;\nint g_ps2RecompiledFunctionTableSlotCount;\n',encoding='utf-8')
        (folder/'invented.cpp').write_text('// Address: 0x100000 - 0x100010\n',encoding='utf-8')
        args=['--disc',str(root/'original.disc'),'--disc-sha256',sha(disc),'--elf',str(root/'original.elf'),
              '--elf-sha256',sha(elf),'--boot-name','INVENTED.ELF','--discovery',str(folder),
              '--discovery-sha256',discovery_digest(folder),'--registry-source',str(root/'invented-dependency'),
              '--module','invented.rel','--session','invented-new']
        # IO-only injection; actual scanners/resolver get separate invented unit
        # controls, plus the separately recorded real personal-disc CLI trials.
        response=({'modules':[], 'total_original_import_jal_uses':0,'unresolved_import_jal_uses':0,'candidates':[],'rejected':[]},
                  {'instructions':4,'qualified_local_uses':0,'candidate_tables':[]},
                  {'direct':[],'indirect':[]},'Name,Start,End,Size\n','Address,kind\n',{'revision':'invented-only'})
        with mock.patch.object(cli,'ROOT',root),mock.patch.object(cli,'produce',return_value=response):yield root,folder,args


def run(args):
    out=io.StringIO();err=io.StringIO()
    with redirect_stdout(out),redirect_stderr(err):code=cli.main(args)
    return code,out.getvalue(),err.getvalue()


class EntryDependencyTests(unittest.TestCase):
    def test_exact_and_explicit_crlf_postimages_only(self):
        raw=b'original invented source\nsecond\n'
        self.assertEqual(cli.dependency_checkout(raw,raw),'exact-git-blob')
        self.assertEqual(cli.dependency_checkout(raw.replace(b'\n',b'\r\n'),raw),'git-lf-to-checkout-crlf')
        for wrong in (b'changed source\n',raw.replace(b' ',b'\r'),raw.replace(b'\n',b'\r\r\n')):
            with self.subTest(wrong=wrong),self.assertRaises(ValueError):cli.dependency_checkout(wrong,raw)

    def test_pinned_dependency_executes_verified_source_and_explicit_own_va(self):
        with source_fixture() as (root,folder):
            import importlib.machinery
            with mock.patch.object(importlib.machinery.SourceFileLoader,'get_code',side_effect=AssertionError('Do not load unchecked bytecode')):
                registry,provenance=cli.pinned_registry(root,b'invented ELF bytes',0x420000)
            self.assertEqual(registry,(b'invented ELF bytes',0x420000,True))
            self.assertEqual(provenance['revision'],cli.REGISTRY_REVISION)
            self.assertFalse((folder/'__pycache__').exists())

    def test_changed_dependency_source_and_wrong_revision_refuse(self):
        with source_fixture() as (root,folder):
            (folder/'snr2fmt.py').write_bytes(b'changed invented source\n')
            with self.assertRaises(ValueError):cli.pinned_registry(root,b'invented',0x420000)
        with source_fixture() as (root,folder):
            with mock.patch.object(cli.subprocess,'check_output',return_value='0'*40):
                with self.assertRaises(ValueError):cli.pinned_registry(root,b'invented',0x420000)

    def test_preloaded_dependency_does_not_silently_replace_reviewed_source(self):
        with source_fixture() as (root,folder):
            sys.modules['snr2fmt']=SimpleNamespace(__file__='unrelated invented path')
            with self.assertRaises(ValueError):cli.pinned_registry(root,b'invented',0x420000)

    def test_produce_passes_original_section_address_not_retail_default(self):
        blob,sections,text,units=local_fixture();raw=module_bytes()
        registry=SimpleNamespace(lookup=lambda name,h:SimpleNamespace(name=name,addr=text.start+56,type=2),boot_relocs=[])
        original=SimpleNamespace(size=len(blob),read=lambda *_:blob)
        module=SimpleNamespace(size=len(raw),read=lambda *_:raw)
        descriptor=SimpleNamespace(path='folder/invented.rel',afs_ordinal=0,metadata=SimpleNamespace(sha256=sha(raw)))
        sndata=Section('.sndata',1,2,0x420000,sections[1].offset,4)
        with mock.patch.object(cli,'pinned_registry',return_value=(registry,{'invented':True})) as factory,\
             mock.patch.object(cli,'iso_root',return_value={'INVENTED.ELF':original,'_DATA.AFS':object()}),\
             mock.patch.object(cli,'afs_entries',return_value=[module]),\
             mock.patch.object(cli,'module_inputs',return_value=[descriptor]):
            result=cli.produce(blob,object(),'INVENTED.ELF',units,sections+(sndata,),text,'invented-source',['invented.rel'])
        self.assertEqual(factory.call_args.args,('invented-source',blob,0x420000))
        self.assertEqual(len(result[2]['direct']),1);self.assertEqual(len(result[2]['indirect']),3)


class EntryInputTests(unittest.TestCase):
    def test_io_only_invented_cli_writes_private_new_outputs(self):
        with fixture() as (root,folder,args):
            before={str(p):sha(p.read_bytes()) for p in root.rglob('*') if p.is_file() and '.git' not in p.parts}
            result=run(args);self.assertEqual(result[0],0,result)
            output=root/'.local/prototype-entries/sessions/invented-new'
            self.assertEqual({p.name for p in output.iterdir()},
                {'imports-private.json','indirect-private.json','entries-private.json','summary-private.json',
                 'functions-private.csv','runtime-relocations-private.csv'})
            self.assertTrue(all(sha(Path(p).read_bytes())==h for p,h in before.items()))
            self.assertEqual((output/'functions-private.csv').read_bytes(),b'Name,Start,End,Size\n')

    def test_check_only_does_not_create_output(self):
        with fixture() as (root,folder,args):
            self.assertEqual(run(args+['--check-only'])[0],0);self.assertFalse((root/'.local').exists())

    def test_each_input_identity_refuses_before_output(self):
        with fixture() as (root,folder,args):
            for flag in ('--disc-sha256','--elf-sha256','--discovery-sha256'):
                bad=args.copy();bad[bad.index(flag)+1]='0'*64
                with self.subTest(flag=flag):self.assertEqual(run(bad)[0],2)
            self.assertFalse((root/'.local').exists())

    def test_reused_session_never_overwrites(self):
        with fixture() as (root,folder,args):
            self.assertEqual(run(args)[0],0)
            expected={str(p):sha(p.read_bytes()) for p in (root/'.local').rglob('*') if p.is_file()}
            self.assertEqual(run(args)[0],2)
            self.assertTrue(all(sha(Path(p).read_bytes())==h for p,h in expected.items()))

    def test_unsafe_unignored_or_nondirectory_session_refuses(self):
        with fixture() as (root,folder,args):
            bad=args.copy();bad[bad.index('--session')+1]='../outside'
            self.assertEqual(run(bad)[0],2)
            (root/'.gitignore').write_text('# not ignored\n',encoding='utf-8')
            self.assertEqual(run(args)[0],2)
            (root/'.gitignore').write_text('.local/\n',encoding='utf-8')
            (root/'.local').write_bytes(b'invented existing file')
            self.assertEqual(run(args)[0],2)
            self.assertEqual((root/'.local').read_bytes(),b'invented existing file')

    def test_bad_registry_shape_and_duplicate_discovered_owner_refuse(self):
        with fixture() as (root,folder,args):
            for file,body in [('register_functions.cpp','// wrong registry\n'),
                              ('alias.cpp','// Address: 0x100000 - 0x100010\n')]:
                with self.subTest(file=file):
                    original=(folder/'register_functions.cpp').read_text(encoding='utf-8')
                    (folder/file).write_text(body,encoding='utf-8')
                    bad=args.copy();bad[bad.index('--discovery-sha256')+1]=discovery_digest(folder)
                    self.assertEqual(run(bad)[0],2)
                    (folder/'register_functions.cpp').write_text(original,encoding='utf-8')
            self.assertFalse((root/'.local').exists())


if __name__=='__main__':unittest.main()
