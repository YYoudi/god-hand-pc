"""Invented typed host scheduling; real GLSL/driver behavior needs native controls."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import pc


class HDGPUHostTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('g++') or shutil.which('clang++'), 'C++20 needed')
    def test_actual_owned_methods_without_a_readback_api(self):
        with tempfile.TemporaryDirectory(prefix='godhand-hd-gpu-synthetic-') as name:
            exe = Path(name)/'invented.exe'
            subprocess.run([shutil.which('g++') or shutil.which('clang++'), '-std=c++20', '-O2',
                            '-Wall', '-Wextra', '-Werror', '-I', str(pc.ROOT/'adapter'),
                            str(pc.ROOT/'tests/hd_gpu_cases.cpp'), '-o', str(exe)],
                           check=True, capture_output=True, timeout=90)
            self.assertEqual(subprocess.check_output([str(exe)], text=True, stderr=subprocess.PIPE, timeout=15).strip(),
                             'invented GPU-result reset fresh batches barrier no CPU readback: PASS')
