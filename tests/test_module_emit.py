"""Original invented module/control fixtures only; no game or third-party data."""
import hashlib
import json
import struct
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock
from module_emit import backward_tail_end, emit_translation_inputs
from test_module_inputs import invented_module


def words(*values):
    return struct.pack('<'+'I'*len(values), *values)


class ModuleEmitTests(unittest.TestCase):
    def test_known_backward_tail_and_bounded_delay_slot(self):
        raw = words(0, 0, (2 << 26), 0)
        self.assertEqual(backward_tail_end(raw, 8, 16, {0}, lambda w, pc: None), 16)
        self.assertIsNone(backward_tail_end(raw, 8, 16, set(), lambda w, pc: None))
        self.assertIsNone(backward_tail_end(raw[:12], 8, 12, {0}, lambda w, pc: None))

    def test_forward_branch_prevents_premature_tail(self):
        raw = words(0, 0, 99, 2 << 26, 0, 0)
        branch = lambda w, pc: 20 if w == 99 else None
        self.assertIsNone(backward_tail_end(raw, 8, 24, {0}, branch))

    def test_successor_requires_zero_or_known_start(self):
        raw = words(0, 0, 2 << 26, 0, 91, 0)
        self.assertIsNone(backward_tail_end(raw, 8, 24, {0}, lambda w, pc: None))
        self.assertEqual(backward_tail_end(raw, 8, 24, {0, 16}, lambda w, pc: None), 16)

    def test_non_backward_or_indirect_transfer_is_not_qualified(self):
        for transfer in ((2 << 26) | 2, (2 << 26) | 3, 0x03e00008):
            self.assertIsNone(backward_tail_end(words(0, 0, transfer, 0), 8, 16,
                                               {0, 8, 12}, lambda w, pc: None))

    def test_bad_word_range_refuses(self):
        for start, bound in ((-4, 8), (0, 9), (4, 0), (0, 12), (True, 8)):
            with self.subTest(start=start, bound=bound), self.assertRaises(ValueError):
                backward_tail_end(words(0, 0), start, bound, set(), lambda w, pc: None)

    def backend(self):
        class Module:
            def __init__(self, raw, name):
                self.raw, self.name, self.h = raw, name, {'ctor_off': 64}
            def strings_start(self):return 160
            def _extent(self, start, bound, starts):return 73
        analysis = NS(checks={'ok': True}, L=NS(img=invented_module()), cs=64, ce=80,
                      functions=[dict(name='invented,quoted', start=0x1040, end=0x1050, size=16)],
                      sites=[dict(in_code=a, dynamic=b, kind=k, address=address)
                             for a,b,k,address in ((True,True,'j26',0x1044),
                             (True,False,'lo16',0x1048), (False,True,'hi16',0x1060),
                             (True,True,'w32',0x1064))])
        elf = NS(read_elf=Mock(return_value={'sections':[dict(name='.sndata',addr=4096)]}),
                 build_exec_elf=Mock(return_value=b'invented ELF output'),
                 self_check=Mock(return_value=True))
        return NS(snr2fmt=NS(Module=Module,branch_target=lambda w,pc:None),
                  snr2=NS(Analysis=Mock(return_value=analysis)),
                  snr2elf=elf,snr2link=NS(Registry=NS(from_boot_elf=Mock(return_value='registry'))))

    def emit(self, backend, **changes):
        args=dict(raw=invented_module(), boot=b'B'*64, base=4096, basename='invented',
                  expected_module_sha256=hashlib.sha256(invented_module()).hexdigest(),
                  expected_boot_sha256=hashlib.sha256(b'B'*64).hexdigest(),backend=backend)
        args.update(changes)
        return emit_translation_inputs(**args)

    def test_adapter_returns_private_files_and_keeps_backend_extent(self):
        backend=self.backend();result=self.emit(backend);files=dict(result.files)
        self.assertEqual((result.functions,result.runtime_relocations),(1,1))
        self.assertEqual(len(files),5)
        self.assertEqual(files['linked.bin'],invented_module())
        self.assertEqual(files['invented_functions.csv'],b'Name,Start,End,Size\r\n"invented,quoted",0x1040,0x1050,16\r\n')
        self.assertEqual(files['invented_runtime_relocations.csv'],b'Address,kind\r\n0x1044,j26\r\n')
        self.assertEqual(json.loads(files['link-private.json'])['runtime_relocation_sites'],[0x1044])
        module=backend.snr2.Analysis.call_args.args[0]
        self.assertEqual(module._extent(64,80,{64}),73)
        backend.snr2link.Registry.from_boot_elf.assert_called_once_with(b'B'*64,4096)

    def test_wrong_identity_base_and_output_identifier_refuse_before_backend(self):
        for args in (dict(expected_module_sha256='0'*64),dict(expected_boot_sha256='F'*64),
                     dict(raw=bytearray(invented_module())),dict(base=True),dict(base=4097),
                     dict(base=0xffffff80),dict(basename='../outside'),dict(basename='UPPER')):
            backend=self.backend()
            with self.subTest(args=args),self.assertRaises(ValueError):self.emit(backend,**args)
            backend.snr2elf.read_elf.assert_not_called()

    def test_boot_registry_and_backend_analysis_failure_are_not_overridden(self):
        for headers in ([],[dict(name='.sndata',addr=1),dict(name='.sndata',addr=2)]):
            backend=self.backend();backend.snr2elf.read_elf.return_value={'sections':headers}
            with self.assertRaises(ValueError):self.emit(backend)
            backend.snr2.Analysis.assert_not_called()
        backend=self.backend();backend.snr2.Analysis.return_value.checks={'ok':False}
        with self.assertRaises(ValueError):self.emit(backend)
        backend.snr2elf.build_exec_elf.assert_not_called()

    def test_invalid_linked_envelope_or_elf_refuses(self):
        for changes in (dict(ce=200),dict(cs=0),dict(L=NS(img=b'short'))):
            backend=self.backend();backend.snr2.Analysis.return_value.__dict__.update(changes)
            with self.subTest(changes=changes),self.assertRaises(ValueError):self.emit(backend)
            backend.snr2elf.build_exec_elf.assert_not_called()
        backend=self.backend();backend.snr2elf.self_check.return_value=False
        with self.assertRaises(ValueError):self.emit(backend)


if __name__ == '__main__':unittest.main()
