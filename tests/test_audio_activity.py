"""Invented admission/freeze controls; not native callback/device proof."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import pc
import controls_pause


class ActivityTests(unittest.TestCase):
    def test_current_public_v1_native_recipe_is_preserved_not_silently_fixed(self):
        recipe = controls_pause.integration(pc.ROOT)
        self.assertNotIn("adapter/audio_activity.hpp", recipe["copies"])
        self.assertEqual(controls_pause.fingerprint(pc.ROOT, recipe),
                         "676d02219d7c29139c0c28b438245d685b9666cbbcf61400f89445d64e9d912a")

    @unittest.skipUnless(shutil.which("g++") or shutil.which("clang++"), "C++20 needed")
    def test_actual_threads_admission_and_negative_control(self):
        with tempfile.TemporaryDirectory(prefix="godhand-audio-activity-synthetic-") as name:
            exe = Path(name) / "invented.exe"
            command = [shutil.which("g++") or shutil.which("clang++"), "-std=c++20", "-O2", "-pthread",
                       "-Wall", "-Wextra", "-Werror", "-I", str(pc.ROOT / "adapter"),
                       str(pc.ROOT / "tests/audio_activity_cases.cpp"), "-o", str(exe)]
            subprocess.run(command, check=True, capture_output=True, timeout=90)
            for _ in range(3):
                result = subprocess.check_output([str(exe)], text=True, timeout=30)
                self.assertEqual(result.strip(),
                                 "legacy-race admission drain exclusion move resume concurrent: PASS")


if __name__ == "__main__": unittest.main()
