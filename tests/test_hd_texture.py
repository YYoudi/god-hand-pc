"""Original invented transfer/envelope controls, not native fidelity proof."""
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

import hd_reference
import pc


class ReferenceTests(unittest.TestCase):
    def test_all_slots_are_bijective_and_known_transfer_vectors(self):
        pairs = [hd_reference.transfer_address(x, y) for y in range(128) for x in range(128)]
        self.assertEqual(len(set(pairs)), 16384)
        self.assertEqual(set(pairs), {(byte, shift) for byte in range(8192) for shift in (0, 4)})
        for x, y, byte, shift in [(0, 0, 0, 0), (1, 0, 4, 0), (2, 0, 8, 0),
                                   (0, 1, 256, 0), (8, 0, 1, 0), (0, 2, 16, 4)]:
            self.assertEqual(hd_reference.transfer_address(x, y), (byte, shift))

    def test_raw_alpha_and_one_interior_stored_slot(self):
        palette = bytes(c for i in range(16) for c in (13*i, 255-7*i, 3*i, 128 if i % 2 else 255))
        stored = bytes([0x11])*8192 + palette
        before = hd_reference.expand(stored)
        self.assertEqual(before, palette[4:8]*16384)
        changed = bytearray(stored)
        at, shift = hd_reference.transfer_address(47, 59)
        changed[at] ^= 1 << shift
        after = hd_reference.expand(bytes(changed))
        self.assertEqual([p for p in range(16384) if before[p*4:p*4+4] != after[p*4:p*4+4]], [59*128+47])
        self.assertEqual(after[(59*128+47)*4+3], 255)

    def test_unsupported_coordinates_and_payload_are_refused(self):
        for x, y in [(128, 0), (-1, 0), (0, 128), (True, 0)]:
            with self.assertRaises(ValueError): hd_reference.transfer_address(x, y)
        for payload in [b'', bytes(8255), bytes(8257), bytearray(8256)]:
            with self.assertRaises(ValueError): hd_reference.expand(payload)

    def test_envelope_shape_and_exact_raw_bytes(self):
        ref = bytes([1, 2, 3, 128])*16384
        rgba = bytes([7, 8, 9, 255])*(512*512)
        blob = hd_reference.envelope(ref, rgba, 512, 512)
        self.assertEqual(blob[:8], b'GHHD001\0')
        self.assertEqual(struct.unpack_from('<6I', blob, 8), (128, 128, 512, 512, 16384, 512*512))
        self.assertEqual(blob[32:], ref+rgba)
        for w, h in [(128, 512), (129, 512), (4096, 512), (True, 512), (512, 0)]:
            with self.assertRaises(ValueError): hd_reference.envelope(ref, rgba, w, h)
        with self.assertRaises(ValueError): hd_reference.envelope(ref[:-1], rgba, 512, 512)
        with self.assertRaises(ValueError): hd_reference.envelope(ref, rgba[:-1], 512, 512)

    @unittest.skipUnless(shutil.which('g++') or shutil.which('clang++'), 'C++20 needed')
    def test_actual_cpp_envelope_and_shader_preimages(self):
        with tempfile.TemporaryDirectory(prefix='godhand-hd-synthetic-') as name:
            exe = Path(name)/'invented.exe'
            command = [shutil.which('g++') or shutil.which('clang++'), '-std=c++20', '-O2',
                       '-Wall', '-Wextra', '-Werror', '-I', str(pc.ROOT/'adapter'),
                       str(pc.ROOT/'tests/hd_texture_cases.cpp'), '-o', str(exe)]
            subprocess.run(command, check=True, capture_output=True, timeout=90)
            self.assertEqual(subprocess.check_output([str(exe)], text=True, timeout=10).strip(),
                             'invented envelope raw-alpha bounds preimages: PASS')


if __name__ == '__main__': unittest.main()
