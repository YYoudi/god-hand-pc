"""Original synthetic timing arithmetic, not a runtime performance acceptance."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import pc


class HDTimingTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('g++') or shutil.which('clang++'), 'C++20 needed')
    def test_totals_with_invented_times_only(self):
        with tempfile.TemporaryDirectory(prefix='godhand-hd-timing-synthetic-') as name:
            exe = Path(name)/'invented.exe'
            subprocess.run([shutil.which('g++') or shutil.which('clang++'), '-std=c++20', '-O2',
                            '-Wall', '-Wextra', '-Werror', '-I', str(pc.ROOT/'adapter'),
                            str(pc.ROOT/'tests/hd_timing_cases.cpp'), '-o', str(exe)],
                           check=True, capture_output=True, timeout=90)
            self.assertEqual(subprocess.check_output([str(exe)], text=True, timeout=15).strip(),
                             'invented timing totals invariants atomic overflow reset: PASS')
