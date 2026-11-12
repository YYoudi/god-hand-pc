"""Original invented source metadata/ELFs only; no personal/game inputs."""
from contextlib import contextmanager,redirect_stderr,redirect_stdout
import hashlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import prototype_sdk_inputs as cli
from test_prototype_sdk import invented_elf,pipeline_fixture


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(folder):
    h=hashlib.sha256()
    for p in sorted(folder.glob('*.cpp'),key=lambda p:p.name):
        h.update((p.name+'\0'+sha(p)+'\n').encode('utf-8'))
    return h.hexdigest()


@contextmanager
def fixture():
    with tempfile.TemporaryDirectory(prefix='sdk-inputs-invented-') as tmp:
        root=Path(tmp);subprocess.run(['git','init','--quiet',str(root)],check=True,capture_output=True)
        (root/'.gitignore').write_text('.local/\n',encoding='utf-8')
        p,r,_,_=pipeline_fixture(False)
        (root/'prototype.elf').write_bytes(invented_elf(p.text,p.start))
        (root/'retail.elf').write_bytes(invented_elf(r.text,r.start))
        (root/'functions.csv').write_text('Name,Start,End\nInventedCaller,0x100000,0x100010\nInventedLeaf,0x100020,0x100030\n',encoding='utf-8')
        (root/'symbols.inc').write_text('X(0x00100000u, InventedCaller, "invented-only", 0.8f)\nX(0x00100020u, InventedLeaf, "invented-only", 0.8f)\n',encoding='utf-8')
        discovery=root/'discovery';discovery.mkdir()
        (discovery/'register_functions.cpp').write_text('// 0x200000\n',encoding='utf-8')
        for n,start in enumerate((p.start,p.start+32,p.start+64)):
            (discovery/('invented'+str(n)+'.cpp')).write_text('// Address: 0x%x - 0x%x\n'%(start,start+16),encoding='utf-8')
        args=[]
        for option,name in [('prototype-elf','prototype.elf'),('retail-elf','retail.elf'),
                            ('functions','functions.csv'),('sdk-metadata','symbols.inc')]:
            args+=['--'+option,str(root/name),'--'+option+'-sha256',sha(root/name)]
        args+=['--discovery',str(discovery),'--discovery-sha256',manifest(discovery),'--session','invented-new']
        with mock.patch.object(cli,'ROOT',root):yield root,discovery,args


def run(args):
    out=io.StringIO();err=io.StringIO()
    with redirect_stdout(out),redirect_stderr(err):code=cli.main(args)
    return code,out.getvalue(),err.getvalue()


class SdkInputTests(unittest.TestCase):
    def test_ordinary_read_uses_validated_size_plus_sentinel_and_refuses_changes(self):
        with tempfile.TemporaryDirectory(prefix='sdk-read-invented-') as tmp:
            path=Path(tmp)/'invented';path.write_bytes(b'five!')
            for actual,valid in [(b'five!',True),(b'longer',False),(b'tiny',False)]:
                stream=io.BytesIO(actual);stream.read=mock.Mock(wraps=stream.read)
                with mock.patch.object(Path,'open',return_value=stream):
                    if valid:self.assertEqual(cli.ordinary_bytes(path),b'five!')
                    else:
                        with self.assertRaises(ValueError):cli.ordinary_bytes(path)
                stream.read.assert_called_once_with(6)

    def test_invented_cli_produces_only_ignored_private_outputs(self):
        with fixture() as (root,discovery,args):
            before={str(p):sha(p) for p in root.rglob('*') if p.is_file() and '.git' not in p.parts}
            result=run(args);self.assertEqual(result[0],0,result)
            output=root/'.local/prototype-sdk/sessions/invented-new'
            self.assertEqual({p.name for p in output.iterdir()},
                             {'initial-private.json','cfg-private.json','qualified-private.json',
                              'summary-private.json','bindings-private.inc'})
            self.assertEqual((output/'bindings-private.inc').read_bytes(),
                             b'{0x00200000u,"InventedCaller"},\n{0x00200040u,"InventedLeaf"},\n')
            self.assertTrue(all(sha(Path(p))==h for p,h in before.items()))
            self.assertEqual(subprocess.run(['git','check-ignore','--quiet','--',str(output)],cwd=root).returncode,0)

    def test_check_only_has_no_output_side_effect(self):
        with fixture() as (root,discovery,args):
            self.assertEqual(run(args+['--check-only'])[0],0)
            self.assertFalse((root/'.local').exists())

    def test_each_wrong_qualified_input_refused_before_output(self):
        with fixture() as (root,discovery,args):
            for option in ('prototype-elf','retail-elf','functions','sdk-metadata'):
                bad=args.copy();bad[bad.index('--'+option+'-sha256')+1]='0'*64
                with self.subTest(option=option):self.assertEqual(run(bad)[0],2)
            self.assertFalse((root/'.local').exists())

    def test_wrong_discovery_identity_refused_before_output(self):
        with fixture() as (root,discovery,args):
            bad=args.copy();bad[bad.index('--discovery-sha256')+1]='0'*64
            self.assertEqual(run(bad)[0],2);self.assertFalse((root/'.local').exists())

    def test_existing_session_refused_without_overwriting(self):
        with fixture() as (root,discovery,args):
            self.assertEqual(run(args)[0],0)
            before={str(p):sha(p) for p in (root/'.local').rglob('*') if p.is_file()}
            self.assertEqual(run(args)[0],2)
            self.assertTrue(all(sha(Path(p))==h for p,h in before.items()))

    def test_unignored_or_nondirectory_private_root_refused(self):
        with fixture() as (root,discovery,args):
            (root/'.gitignore').write_text('# intentionally not ignored\n',encoding='utf-8')
            self.assertEqual(run(args)[0],2);self.assertFalse((root/'.local').exists())
            (root/'.gitignore').write_text('.local/\n',encoding='utf-8')
            (root/'.local').write_text('invented ordinary file, not directory',encoding='utf-8')
            self.assertEqual(run(args)[0],2)
            self.assertEqual((root/'.local').read_text(encoding='utf-8'),'invented ordinary file, not directory')

    def test_malformed_or_duplicate_discovered_header_refused(self):
        with fixture() as (root,discovery,args):
            for content in ('// no address header\n','// Address: 0x200020 - 0x200030\n'):
                (discovery/'invented0.cpp').write_text(content,encoding='utf-8')
                bad=args.copy();bad[bad.index('--discovery-sha256')+1]=manifest(discovery)
                with self.subTest(content=content):self.assertEqual(run(bad)[0],2)
            self.assertFalse((root/'.local').exists())

    def test_metadata_unsupported_row_is_not_silently_dropped(self):
        with fixture() as (root,discovery,args):
            path=root/'symbols.inc';path.write_text(path.read_text(encoding='utf-8')+'X(unsupported-row)\n',encoding='utf-8')
            bad=args.copy();bad[bad.index('--sdk-metadata-sha256')+1]=sha(path)
            self.assertEqual(run(bad)[0],2);self.assertFalse((root/'.local').exists())

    def test_unsafe_session_is_refused_before_any_private_write(self):
        with fixture() as (root,discovery,args):
            for name in ('../outside','Upper','', 'a'*65):
                bad=args.copy();bad[-1]=name
                with self.subTest(name=name):self.assertEqual(run(bad)[0],2)
            self.assertFalse((root/'.local').exists())

    def test_explicit_crlf_is_not_platform_default_newline(self):
        with fixture() as (root,discovery,args):
            self.assertEqual(run(args+['--binding-line-ending','crlf'])[0],0)
            blob=(root/'.local/prototype-sdk/sessions/invented-new/bindings-private.inc').read_bytes()
            self.assertEqual(blob.count(b'\n'),2);self.assertEqual(blob.count(b'\r\n'),2)


if __name__=='__main__':unittest.main()
