"""Original invented code/comments and host paths only; never game fixtures."""
from contextlib import contextmanager,redirect_stdout,redirect_stderr
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import prototype_observer_inputs as cli
import prototype_native_project as project


def catalog_digest(root):
    h=hashlib.sha256()
    for p in sorted(root.glob('*.cpp'),key=lambda p:p.name):
        h.update((p.name+'\0'+cli.digest(p.read_bytes())+'\n').encode('utf-8'))
    return h.hexdigest()


@contextmanager
def fixture():
    with tempfile.TemporaryDirectory(prefix='source-assembly-invented-') as tmp:
        root=Path(tmp);subprocess.run(['git','init','--quiet',str(root)],check=True,capture_output=True)
        (root/'.gitignore').write_text('.local/\n',encoding='utf-8')
        generated=root/'invented-generated';generated.mkdir();rows=[]
        for n,name in enumerate(sorted(cli.IDS)):
            raw=('// invented fixture '+name+'\n// 0x1000: 0x00000000\nvoid invented_'+name+'() {}\n').encode()
            (generated/(name+'.cpp')).write_bytes(raw)
            text='void observe_invented_'+name+'();\n'
            output=(text.encode()+raw).replace(b'\n',b'\r\n')
            rows.append(dict(id=name,source_sha256=cli.digest(raw),output_sha256=cli.digest(output),
                output='prototype_observe_'+name+'.cpp',line_ending='crlf',insertions=[dict(before_line=0,text=text)]))
        policy=dict(schema=1,version='prototype-observer-inserts-v1',provenance='Invented only',profiles=rows)
        adapter=root/'adapter';adapter.mkdir();p=adapter/'prototype_observer_inserts.json'
        p.write_text(json.dumps(policy),encoding='utf-8')
        args=['--generated',str(generated),'--generated-sha256',catalog_digest(generated),'--session','invented-new']
        with mock.patch.object(cli,'ROOT',root):yield root,generated,policy,p,args


def call(args):
    out,err=io.StringIO(),io.StringIO()
    with redirect_stdout(out),redirect_stderr(err):code=cli.main(args)
    return code,out.getvalue(),err.getvalue()


class ObserverTests(unittest.TestCase):
    def test_exact_catalog_four_insertions_and_original_comment_sequence(self):
        with fixture() as (root,generated,policy,p,args):
            index,catalog=cli.source_catalog(generated,args[3])
            outputs,records=cli.produce_profiles(policy,index)
            self.assertEqual(len(outputs),4);self.assertEqual(catalog['cpp_files'],4)
            for row in records:
                self.assertEqual(row['original_pc_word_comments'],1)
                self.assertTrue(row['original_pc_word_sequence_unchanged'])
                self.assertEqual(cli.digest(outputs[row['output']]),row['output_sha256'])
                self.assertNotIn(b'\n',outputs[row['output']].replace(b'\r\n',b''))

    def test_source_byte_change_and_wrong_complete_catalog_digest_refuse(self):
        with fixture() as (root,generated,policy,p,args):
            with self.assertRaises(ValueError):cli.source_catalog(generated,'0'*64)
            index,_=cli.source_catalog(generated,args[3])
            target=generated/'damage.cpp';target.write_bytes(target.read_bytes()+b'changed\n')
            with self.assertRaises(ValueError):cli.produce_profiles(policy,index)

    def test_missing_or_ambiguous_selected_identity_refuses(self):
        with fixture() as (root,generated,policy,p,args):
            index,_=cli.source_catalog(generated,args[3]);h=policy['profiles'][0]['source_sha256']
            for paths in ([],index[h]*2):
                changed=dict(index);changed[h]=paths
                with self.assertRaises(ValueError):cli.produce_profiles(policy,changed)

    def test_wrong_postimage_or_invalid_insertion_refuses_before_output(self):
        with fixture() as (root,generated,policy,p,args):
            index,_=cli.source_catalog(generated,args[3])
            for patch in (dict(output_sha256='0'*64),dict(insertions=[dict(before_line=-1,text='observe();\n')])):
                bad=copy.deepcopy(policy);bad['profiles'][0].update(patch)
                with self.assertRaises(ValueError):cli.produce_profiles(bad,index)
            self.assertFalse((root/'.local').exists())

    def test_inserting_an_extra_pc_comment_is_not_false_preservation(self):
        with fixture() as (root,generated,policy,p,args):
            index,_=cli.source_catalog(generated,args[3]);row=policy['profiles'][0]
            row['insertions']=[dict(before_line=0,text='// 0x2000: 0x00000000\n')]
            raw=index[row['source_sha256']][0].read_bytes()
            row['output_sha256']=cli.digest((b'// 0x2000: 0x00000000\n'+raw).replace(b'\n',b'\r\n'))
            with self.assertRaises(ValueError):cli.produce_profiles(policy,index)

    def test_missing_pc_comments_are_not_a_recompiled_unit_certificate(self):
        with fixture() as (root,generated,policy,p,args):
            row=policy['profiles'][0];raw=b'void invented() {}\n';target=generated/'plain.cpp';target.write_bytes(raw)
            row['source_sha256']=cli.digest(raw);row['output_sha256']=cli.digest((row['insertions'][0]['text'].encode()+raw).replace(b'\n',b'\r\n'))
            index,_=cli.source_catalog(generated,catalog_digest(generated))
            with self.assertRaises(ValueError):cli.produce_profiles(policy,index)

    def test_policy_scope_output_names_and_duplicate_source_guards(self):
        with fixture() as (root,generated,policy,p,args):
            for change in (lambda x:x.update(schema=2),lambda x:x['profiles'][0].update(output='../outside.cpp'),
                           lambda x:x['profiles'][0].update(id='retail'),
                           lambda x:x['profiles'][0].update(source_sha256=x['profiles'][1]['source_sha256'])):
                altered=copy.deepcopy(policy);change(altered);p.write_text(json.dumps(altered),encoding='utf-8')
                with self.assertRaises(ValueError):cli.public_policy(root)

    def test_private_cli_production_check_only_and_stale_refusal(self):
        with fixture() as (root,generated,policy,p,args):
            self.assertEqual(call(args+['--check-only'])[0],0)
            self.assertFalse((root/'.local').exists())
            code,out,err=call(args);self.assertEqual(code,0,err);self.assertEqual(json.loads(out)['profiles'],4)
            dest=root/'.local/prototype-observers/sessions/invented-new'
            before={q:q.read_bytes() for q in dest.iterdir()};self.assertEqual(len(before),5)
            self.assertEqual(call(args)[0],2);self.assertEqual(before,{q:q.read_bytes() for q in before})

    def test_wrong_catalog_invalid_session_and_nonignored_output_are_read_only(self):
        with fixture() as (root,generated,policy,p,args):
            for flag,value in (('--generated-sha256','0'*64),('--session','../outside')):
                bad=args[:];bad[bad.index(flag)+1]=value;self.assertEqual(call(bad)[0],2)
            (root/'.gitignore').write_text('',encoding='utf-8');self.assertEqual(call(args)[0],2)
            self.assertFalse((root/'.local').exists())

    def test_public_policy_contains_only_original_added_statements_and_no_addresses(self):
        root=Path(__file__).resolve().parents[1];policy,_=cli.public_policy(root)
        blob=(root/'adapter/prototype_observer_inserts.json').read_text(encoding='utf-8')
        self.assertNotIn('0x',blob);self.assertNotIn('G:',blob)
        for row in policy['profiles']:
            for insertion in row['insertions']:
                for line in insertion['text'].splitlines():
                    self.assertTrue(not line or line.startswith('void prototypeObserve') or
                        line.startswith('    prototypeObserve'))


def graph_arguments(vu='G:/Invented/VU'):
    return dict(runtime_source='G:/Invented/Runtime',raylib_source='G:/Invented/Raylib',
        adapter_directory='G:/Invented/Adapter',boot_directory='G:/Invented/BOOT',
        host_directory='G:/Invented/Host',observer_directory='G:/Invented/Observers',
        observer_records=[dict(id=n,raw_basename='invented_'+n+'.cpp',output='prototype_observe_'+n+'.cpp')
                          for n in ('damage','refill','warp_create','warp_destroy')],
        module_directories={n:'G:/Invented/Modules/'+n for n in project.MODULES},
        generic_build='G:/Invented/Generic',bindings_file='G:/Invented/SDK/bindings.inc',vu_directory=vu)


class NativeProjectTests(unittest.TestCase):
    def test_default_flags_link_order_and_actual_source_replacements(self):
        text=project.cmake_project(**graph_arguments()).decode()
        self.assertIn('/O1 /Ob2 /DNDEBUG',text)
        self.assertIn('<ps2_runtime_macros.h>',text)
        self.assertIn('COPYONLY)',text)
        for n in project.OBSERVERS:
            self.assertIn('list(REMOVE_ITEM BOOT "G:/Invented/BOOT/invented_'+n+'.cpp")',text)
            self.assertIn('G:/Invented/Observers/prototype_observe_'+n+'.cpp',text)
        expected='prototype_mcport prototype_r020 prototype_r100 prototype_event prototype_r101'
        self.assertEqual(text.count(expected),2)
        self.assertLess(text.index('ps2_runtime.lib'),text.index('rlImGui.lib'))
        self.assertLess(text.index('rlImGui.lib'),text.index('imgui.lib'))

    def test_bootstrap_has_capability_macro_and_no_fake_vu_target_when_absent(self):
        text=project.cmake_project(**graph_arguments(None)).decode()
        self.assertIn('PROTOTYPE_INTERPRETER_BOOTSTRAP=1',text)
        self.assertNotIn('prototype-native',text);self.assertNotIn('prototype_vu1',text)

    def test_explicit_vu_target_has_o2_only_on_its_target(self):
        text=project.cmake_project(**graph_arguments()).decode()
        self.assertIn('target_compile_options(prototype_vu1 PRIVATE /O2)',text)
        self.assertIn('add_executable(prototype-native ',text)
        self.assertEqual(text.count('target_compile_options('),1)

    def test_game_observers_skip_pch_and_refill_retains_od(self):
        text=project.cmake_project(**graph_arguments()).decode()
        self.assertIn('SIZE GREATER 250000',text)
        self.assertIn('prototype_observe_refill.cpp" PROPERTIES COMPILE_OPTIONS /Od)',text)
        self.assertIn('PROPERTIES SKIP_PRECOMPILE_HEADERS ON)',text)

    def test_cmake_path_injection_relative_and_traversal_refuse(self):
        for value in ('G:/bad;injection','G:/bad${HOME}','relative','G:/a/../b','G:/bad"path'):
            args=graph_arguments();args['runtime_source']=value
            with self.assertRaises(ValueError):project.cmake_project(**args)

    def test_missing_modules_or_observers_and_unsafe_raw_filename_refuse(self):
        for change in (lambda a:a['module_directories'].pop('event'),
                       lambda a:a['observer_records'].pop(),
                       lambda a:a['observer_records'][0].update(raw_basename='../outside.cpp'),
                       lambda a:a['observer_records'][0].update(output='other.cpp')):
            args=graph_arguments();change(args)
            with self.assertRaises(ValueError):project.cmake_project(**args)


if __name__=='__main__':unittest.main()
