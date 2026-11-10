"""Portable original UI-model controls; not a drawn or integrated native menu."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import pc


class VideoMenuModelTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("g++") or shutil.which("clang++"), "C++20 needed")
    def test_request_hold_reply_and_restart_states(self):
        with tempfile.TemporaryDirectory(prefix="godhand-menu-model-synthetic-") as name:
            root = Path(name).resolve()
            assert root.is_relative_to(Path(tempfile.gettempdir()).resolve())
            executable = root / "invented-menu.exe"
            compiler = shutil.which("g++") or shutil.which("clang++")
            subprocess.run([compiler, "-std=c++20", "-O2", "-Wall", "-Wextra", "-Werror",
                            "-I", str(pc.ROOT / "adapter"), str(pc.ROOT / "tests/video_menu_model_cases.cpp"),
                            "-o", str(executable)], check=True, capture_output=True, timeout=90)
            result = subprocess.check_output([str(executable)], text=True, timeout=15)
            self.assertEqual(result.strip(), "ownership hold cancellation restart stale unknown bounded: PASS")
