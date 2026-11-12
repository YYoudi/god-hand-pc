"""Invented instruction/data fields only; no game/vendor fixtures or execution."""
from contextlib import contextmanager, redirect_stdout, redirect_stderr
import copy
import io
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
from unittest import mock

import prototype_host_profile as model
import prototype_host_profile_inputs as cli
from test_prototype_host_sources import fixture as host_fixture


def word(op, rs=0, rt=0, imm=0):
    return (op << 26) | (rs << 21) | (rt << 16) | (imm & 65535)


def view_words(*words, base=0x2000):
    raw = struct.pack('<'+'I'*len(words), *words)
    return model.View(base, raw + bytes(range(1, 65)))


def anchor(view, offset=0, name='invented'):
    return dict(view=name, window_bytes=32, sha256=model.digest(view.blob[offset:offset+32]))


def style(width=0, suffix='u'):
    return dict(width=width, suffix=suffix)


def scalar_row(view, kind='simm16', negate=False, shift=0):
    w = struct.unpack_from('<I', view.blob)[0]
    return dict(kind=kind, anchor=anchor(view), opcode=w >> 26, rs=w >> 21 & 31,
                rt=w >> 16 & 31, shift=shift, negate=negate, format=style())


def derive(row, view):
    return model.derive_parameters({'VALUE':row}, {'invented':view}, {}, {})[0]['VALUE']


class FingerprintTests(unittest.TestCase):
    def test_aligned_unique_window_and_virtual_address(self):
        v = view_words(word(9, 4, 5, 17))
        a = anchor(v, 4)
        self.assertEqual(model.fingerprint_windows({'invented':v}, [a])[('invented',32,a['sha256'])],4)
        self.assertEqual(derive(dict(kind='vaddr',anchor=a,format=style(8)),v),'0x00002004u')

    def test_missing_ambiguous_and_unaligned_only_windows_refuse(self):
        v = view_words(word(9, 4, 5, 17))
        a = anchor(v); a['sha256'] = '0'*64
        with self.assertRaises(ValueError):model.fingerprint_windows({'invented':v},[a])
        repeated = model.View(0,b'abcd'*32)
        with self.assertRaises(ValueError):model.fingerprint_windows({'invented':repeated},[anchor(repeated)])
        with self.assertRaises(ValueError):model.fingerprint_windows({'invented':v},[anchor(v,1)])

    def test_invalid_window_shape_and_view_budgets_refuse(self):
        v = view_words(1)
        for bad in ({**anchor(v),'window_bytes':16},{**anchor(v),'view':'absent'},
                    {**anchor(v),'sha256':'not a digest'},{**anchor(v),'address':123}):
            with self.subTest(bad=bad),self.assertRaises(ValueError):model.fingerprint_windows({'invented':v},[bad])
        for base,blob in ((1,b'x'*32),(0,b'x'*31),(0,bytearray(b'x'*32)),(2**32-4,b'x'*32)):
            with self.assertRaises(ValueError):model.View(base,blob)


class OperandTests(unittest.TestCase):
    def test_signed_negative_stack_adjustment_becomes_guarded_positive_size(self):
        v = view_words(word(9,29,29,-48))
        self.assertEqual(derive(scalar_row(v,negate=True),v),'0x30u')

    def test_positive_memory_offset_and_unsigned_lui_mask(self):
        v = view_words(word(35,17,3,0x104))
        self.assertEqual(derive(scalar_row(v),v),'0x104u')
        hi = view_words(word(15,0,4,7))
        self.assertEqual(derive(scalar_row(hi,kind='uimm16',shift=16),hi),'0x70000u')

    def test_wrong_shape_wrong_shift_signedness_and_negative_result_refuse(self):
        v = view_words(word(35,17,3,-4));row=scalar_row(v)
        for mutator in (lambda r:r.update(rs=16),lambda r:r.update(opcode=9),lambda r:r.update(shift=16),
                        lambda r:r.update(kind='uimm16'),lambda r:r.update(negate=1)):
            bad=copy.deepcopy(row);mutator(bad)
            with self.assertRaises(ValueError):derive(bad,v)
        with self.assertRaises(ValueError):derive(row,v)

    def test_lui_address_signed_low_and_intervening_independent_write(self):
        v = view_words(word(15,0,2,0x23),word(9,29,29,-32),word(55,2,5,-16))
        row=dict(kind='lui-address',anchor=anchor(v),low_word=2,high_register=2,
                 low_opcode=55,low_target=5,format=style())
        self.assertEqual(derive(row,v),'0x22fff0u')

    def test_encoded_jr_delay_operand_allowed_without_execution_claim(self):
        jr=(31 << 21)|8
        v = view_words(word(15,0,3,0x24),jr,word(35,3,2,32))
        row=dict(kind='lui-address',anchor=anchor(v),low_word=2,high_register=3,
                 low_opcode=35,low_target=2,format=style())
        self.assertEqual(derive(row,v),'0x240020u')

    def test_lui_clobber_unknown_and_wrong_low_form_refuse(self):
        for middle in (word(15,0,2,1),word(18,0,2,1),word(4,0,0,0)):
            v=view_words(word(15,0,2,0x23),middle,word(35,2,3,16))
            row=dict(kind='lui-address',anchor=anchor(v),low_word=2,high_register=2,
                     low_opcode=35,low_target=3,format=style())
            with self.assertRaises(ValueError):derive(row,v)
        v=view_words(word(15,0,2,0x23),word(35,2,3,16))
        for patch in (dict(low_word=0),dict(low_word=4),dict(high_register=3),dict(low_opcode=43),dict(low_target=4)):
            row=dict(kind='lui-address',anchor=anchor(v),low_word=1,high_register=2,
                     low_opcode=35,low_target=3,format=style());row.update(patch)
            with self.assertRaises(ValueError):derive(row,v)

    def test_all_finite_selector_families_and_exact_numeric_spelling(self):
        v=view_words(word(9,4,5,8));sel={'A':dict(kind='vaddr',anchor=anchor(v),format=style()),
            'B':dict(kind='alias',parameter='A',add=4,format=style(8,'')),
            'C':dict(kind='host',name='ram_bytes',format=style()),
            'D':dict(kind='module-base',module='mod',format=style()),
            'E':dict(kind='module-end',module='mod',format=style()),
            'P':dict(kind='include',root='adapter',path='original.hpp')}
        values,_=model.derive_parameters(sel,{'invented':v},{'mod':(0x4000,96)},{'adapter':Path('invented')})
        self.assertEqual(values,dict(A='0x2000u',B='0x00002004',C='0x2000000u',D='0x4000u',E='0x4060u',P='invented/original.hpp'))

    def test_cycles_unknown_alias_kind_extra_fields_and_include_traversal_refuse(self):
        v=view_words(1);baseline={'A':dict(kind='vaddr',anchor=anchor(v),format=style())}
        for row in (dict(kind='alias',parameter='B',add=0,format=style()),
                    dict(kind='alias',parameter='B',add=12,format=style()),
                    dict(kind='host',name='unknown',format=style()),
                    dict(kind='include',root='adapter',path='../outside'),
                    dict(kind='cpp',text='arbitrary();')):
            with self.assertRaises(ValueError):model.derive_parameters({**baseline,'B':row},{'invented':v},{},{'adapter':'x'})
        with self.assertRaises(ValueError):derive({**baseline['A'],'guess':1},v)

    def test_module_overflow_and_literal_overflow_are_not_wrapped(self):
        v=view_words(1);a=dict(kind='vaddr',anchor=anchor(v),format=style())
        for module in ((32*1024*1024-4,96),(1,96),(0,59)):
            with self.assertRaises(ValueError):model.derive_parameters({'A':a,'B':dict(kind='module-end',module='m',format=style())}, {'invented':v},{'m':module},{})
        for value,fmt in ((2**32,style()),(-1,style()),(1,style(9)),(1,style(0,'cpp'))):
            with self.assertRaises(ValueError):model.literal(value,fmt)


@contextmanager
def observation_fixture():
    with tempfile.TemporaryDirectory(prefix='profile-capture-invented-') as tmp:
        root=Path(tmp);header=[0]*15;header[0]=int.from_bytes(b'SNR2','little');header[11]=96
        raw=struct.pack('<15I',*header)+b'original-invented'.ljust(36,b'.')
        captured=raw[:60]+b'captured-invented'.ljust(36,b'.')
        meta=dict(base=0x4000,size=96,ra=0x1234,name_pointer=0,header=header)
        a=root/'observation.json';b=root/'observation.bytes';a.write_text(json.dumps(meta),encoding='utf-8');b.write_bytes(captured)
        spec={'invented':dict(disc_source_sha256=model.digest(raw),metadata_sha256=model.digest(a.read_bytes()),capture_sha256=model.digest(captured))}
        paths={'invented':dict(metadata=str(a),capture=str(b))}
        yield spec,paths,{'invented':raw},meta,a,b


class ObservationTests(unittest.TestCase):
    def test_exact_historical_capture_and_complete_header_not_raw_selected_map(self):
        with observation_fixture() as (spec,paths,raw,meta,a,b):
            modules,provenance=cli.observed_modules(spec,paths,raw)
            self.assertEqual(modules,{'invented':(0x4000,96)})
            self.assertTrue(provenance['invented']['historical_observation'])

    def test_changed_capture_original_module_and_metadata_identity_refuse(self):
        for key in ('disc_source_sha256','metadata_sha256','capture_sha256'):
            with observation_fixture() as (spec,paths,raw,meta,a,b):
                spec['invented'][key]='0'*64
                with self.assertRaises(ValueError):cli.observed_modules(spec,paths,raw)

    def test_header_size_base_bounds_and_input_scope_refuse(self):
        for patch in (dict(base=True),dict(base=1),dict(base=32*1024*1024),dict(size=92),dict(header=[0]*15)):
            with observation_fixture() as (spec,paths,raw,meta,a,b):
                meta.update(patch);a.write_text(json.dumps(meta),encoding='utf-8');spec['invented']['metadata_sha256']=model.digest(a.read_bytes())
                with self.assertRaises(ValueError):cli.observed_modules(spec,paths,raw)
        with observation_fixture() as (spec,paths,raw,meta,a,b):
            with self.assertRaises(ValueError):cli.observed_modules(spec,{},raw)

    def test_source_postimages_are_computed_then_checked_not_an_independent_oracle(self):
        with host_fixture() as (root,dep,recipe,spec,profile,args):
            outputs,source=cli.describe_outputs(root,dep,profile['parameters'])
            self.assertEqual(outputs['window_shortcut_bridge.hpp']['line_ending'],'crlf')
            self.assertEqual(outputs['main.cpp'],profile['outputs']['main.cpp'])
            self.assertEqual(source['upstream_revision'],cli.recipe(root)['upstream_revision'])


@contextmanager
def cli_fixture():
    with tempfile.TemporaryDirectory(prefix='profile-inputs-invented-') as tmp:
        root=Path(tmp);subprocess.run(['git','init','--quiet',str(root)],check=True,capture_output=True)
        (root/'.gitignore').write_text('.local/\n',encoding='utf-8')
        elf=b'invented ELF input';disc=b'invented disc input'.ljust(2048,b'.')
        (root/'original.elf').write_bytes(elf);(root/'original.disc').write_bytes(disc)
        (root/'observations.json').write_text('{}',encoding='utf-8')
        args=[]
        for key,val in [('source',root/'dependency'),('elf',root/'original.elf'),('disc',root/'original.disc'),
                        ('observations',root/'observations.json'),('adapter-root',root/'adapter'),('module-root',root/'modules'),('session','invented-new')]:args+=['--'+key,str(val)]
        spec=dict(original_elf_sha256=model.digest(elf),original_disc_sha256=model.digest(disc))
        response=(dict(schema=1,qualification='Invented IO-only profile',parameters={'X':'0x1'},outputs={}),dict(observations={}))
        with mock.patch.object(cli,'ROOT',root),mock.patch.object(cli,'public_policy',return_value=(spec,'0'*64)),mock.patch.object(cli,'produce',return_value=response):
            yield root,args


def call(args):
    out,err=io.StringIO(),io.StringIO()
    with redirect_stdout(out),redirect_stderr(err):code=cli.main(args)
    return code,out.getvalue(),err.getvalue()


class InputTests(unittest.TestCase):
    def test_public_policy_covers_all_templates_without_populated_address_or_word_map(self):
        root=Path(__file__).resolve().parents[1]
        spec,_=cli.public_policy(root)
        self.assertEqual(set(spec['selectors']),set(cli.recipe(root)['parameters']))
        self.assertEqual(len(spec['selectors']),67)
        def bounded(value):
            if type(value) is int:self.assertLessEqual(value,128)
            elif isinstance(value,dict):
                for item in value.values():bounded(item)
            elif isinstance(value,list):
                for item in value:bounded(item)
        bounded(spec)
        self.assertNotIn('0x',(root/'adapter/prototype_host_profile.json').read_text(encoding='utf-8'))

    def test_fresh_private_profile_receipt_has_actual_complete_file_hash(self):
        with cli_fixture() as (root,args):
            code,_,err=call(args);self.assertEqual(code,0,err)
            out=root/'.local/prototype-host-profile/sessions/invented-new'
            receipt=json.loads((out/'derivation-private.json').read_text(encoding='utf-8'))
            self.assertEqual(receipt['profile_sha256'],model.digest((out/'host-profile-private.json').read_bytes()))
            self.assertEqual(set(p.name for p in out.iterdir()),{'derivation-private.json','host-profile-private.json'})

    def test_check_only_wrong_elf_wrong_disc_and_unsafe_name_leave_no_outputs(self):
        with cli_fixture() as (root,args):
            self.assertEqual(call(args+['--check-only'])[0],0)
            for flag,value in [('--elf',root/'original.disc'),('--disc',root/'original.elf'),('--session','../outside')]:
                bad=args[:];bad[bad.index(flag)+1]=str(value);self.assertEqual(call(bad)[0],2)
            self.assertFalse((root/'.local').exists())

    def test_stale_session_and_nonignored_output_refuse(self):
        with cli_fixture() as (root,args):
            (root/'.gitignore').write_text('',encoding='utf-8');self.assertEqual(call(args)[0],2)
            (root/'.gitignore').write_text('.local/\n',encoding='utf-8');self.assertEqual(call(args)[0],0)
            before={p:p.read_bytes() for p in (root/'.local').rglob('*') if p.is_file()}
            self.assertEqual(call(args)[0],2);self.assertEqual(before,{p:p.read_bytes() for p in before})


if __name__=='__main__':unittest.main()
