"""Original invented C++ loader controls; actual native SHA/GPU need own tests."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import pc


class HDRuntimeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('g++') or shutil.which('clang++'), 'C++20 needed')
    def test_actual_loader_with_invented_file_and_digest_callback(self):
        with tempfile.TemporaryDirectory(prefix='godhand-hd-io-synthetic-') as name:
            exe = Path(name)/'invented.exe'
            command = [shutil.which('g++') or shutil.which('clang++'), '-std=c++20', '-O2', '-Wall', '-Wextra', '-Werror',
                       '-I', str(pc.ROOT/'adapter'), str(pc.ROOT/'tests/hd_runtime_cases.cpp'), '-o', str(exe)]
            subprocess.run(command, check=True, capture_output=True, timeout=90)
            self.assertEqual(subprocess.check_output([str(exe), str(Path(name)/'invented.private-input')], text=True, timeout=15).strip(),
                             'invented file identity digest shape refusal: PASS')
