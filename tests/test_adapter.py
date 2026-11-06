"""Compile only original portable C++ tests with invented inputs, never a game."""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

import pc


class AdapterTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("g++") or shutil.which("clang++"), "Portable synthetic adapter tests need C++20")
    def test_actual_cpp_overlap_and_loader_fallback(self):
        with tempfile.TemporaryDirectory(prefix="godhand-adapter-synthetic-") as name:
            root = Path(name).resolve()
            assert root.is_relative_to(Path(tempfile.gettempdir()).resolve())
            compiler = shutil.which("g++") or shutil.which("clang++")
            exe = root / "invented-check.exe"
            subprocess.run([compiler, "-std=c++20", "-O2", "-Wall", "-Wextra", "-Werror",
                            "-I", str(pc.ROOT / "adapter"), str(pc.ROOT / "tests/adapter_cases.cpp"),
                            "-o", str(exe)], check=True, capture_output=True)
            result = subprocess.check_output([str(exe), str(root / "invented-payload.txt")], text=True)
            counts = re.fullmatch(r"overlap_cases=(\d+) invalid_settings=(\d+)\s*", result)
            self.assertIsNotNone(counts)
            self.assertEqual(int(counts[1]), 608256)
            self.assertEqual(int(counts[2]), 15)


if __name__ == "__main__":
    unittest.main()
