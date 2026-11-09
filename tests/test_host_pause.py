"""Only original invented portable executor controls; not native runtime proof."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import pc


class HostPauseTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("g++") or shutil.which("clang++"), "C++20 needed")
    def test_actual_thread_and_continuous_clock(self):
        with tempfile.TemporaryDirectory(prefix="godhand-pause-synthetic-") as name:
            root = Path(name).resolve()
            compiler = shutil.which("g++") or shutil.which("clang++")
            exe = root / "invented-pause.exe"
            subprocess.run([compiler, "-std=c++20", "-O2", "-pthread", "-Wall", "-Wextra", "-Werror",
                            "-I", str(pc.ROOT / "adapter"), str(pc.ROOT / "tests/host_pause_cases.cpp"),
                            "-o", str(exe)], check=True, capture_output=True, timeout=90)
            result = subprocess.check_output([str(exe)], text=True, timeout=15)
            self.assertEqual(result.strip(),
                             "blocker cancellation frozen-clock frozen-executor reentry stop: PASS")


if __name__ == "__main__":
    unittest.main()
