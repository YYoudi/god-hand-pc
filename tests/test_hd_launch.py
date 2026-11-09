"""Original policy/process doubles; no native game, ISO or user input in CI."""
from pathlib import Path
from types import SimpleNamespace
import json
import os
import tempfile
import unittest
from unittest.mock import patch

import controls_pause
import launch_packs as launch
import profiles


class HDLaunchTests(unittest.TestCase):
    def test_original_unflagged_and_unsupported_combinations_refuse_before_runtime(self):
        cases = [dict(hd_textures=True), dict(profile="enhanced", hd_pack="pack"),
                 dict(profile="enhanced", hd_textures=True, strict_hd=True),
                 dict(profile="enhanced", hd_textures=True, controls_pause=True),
                 dict(profile="enhanced", hd_textures=True, controls_pause=True, controls_pause_version="audio-v2"),
                 dict(profile="enhanced", hd_textures=True, pack="old-pack"),
                 dict(profile="enhanced", hd_textures=1), dict(profile="enhanced", strict_hd=1)]
        with patch.object(launch.hd, "verified_install") as hd, patch.object(launch.pc, "verify_disc") as disc, \
             patch.object(launch.subprocess, "Popen") as child:
            for flags in cases:
                with self.subTest(flags=flags), self.assertRaises(ValueError):
                    launch.launch(Path("must-not-create"), "retail-test", "absent", **flags)
            hd.assert_not_called(); disc.assert_not_called(); child.assert_not_called()

    def test_existing_policies_and_native_fingerprints_are_not_silently_upgraded(self):
        self.assertEqual(profiles.resolve()["requested_extensions"], [])
        self.assertEqual(profiles.resolve("enhanced", controls_pause=True)["requested_extensions"], ["experimental-controls-pause"])
        self.assertEqual(profiles.resolve("enhanced", hd_textures=True)["requested_extensions"], ["experimental-hd-textures"])
        self.assertEqual(controls_pause.fingerprint(launch.pc.ROOT, controls_pause.integration(launch.pc.ROOT)),
                         "676d02219d7c29139c0c28b438245d685b9666cbbcf61400f89445d64e9d912a")

    def test_disc_or_variant_failure_never_enters_optional_hd_fallback(self):
        with tempfile.TemporaryDirectory(prefix="godhand-hd-policy-synthetic-") as name:
            with patch.object(launch, "os", SimpleNamespace(name="nt")), \
                 patch.object(launch.hd, "verified_install", return_value={}), \
                 patch.object(launch.pc, "load_pin", return_value={"retail_profile": {}}), \
                 patch.object(launch.pc, "verify_disc", side_effect=ValueError("invented wrong disc")), \
                 patch.object(launch.hd_packs, "protocol") as pack, patch.object(launch.subprocess, "Popen") as child:
                with self.assertRaisesRegex(ValueError, "wrong disc"):
                    launch.launch(name, "retail-test", "missing", profile="enhanced", hd_textures=True, hd_pack="bad")
                pack.assert_not_called(); child.assert_not_called()
            with patch.object(launch, "os", SimpleNamespace(name="nt")), \
                 patch.object(launch.hd, "verified_install", side_effect=ValueError("invented variant drift")), \
                 patch.object(launch.pc, "verify_disc") as disc, patch.object(launch.subprocess, "Popen") as child:
                with self.assertRaisesRegex(ValueError, "variant drift"):
                    launch.launch(name, "retail-test", "missing", profile="enhanced", hd_textures=True)
                disc.assert_not_called(); child.assert_not_called()

    def test_actual_launcher_selection_and_explicit_disabled_protocol_with_doubles(self):
        with tempfile.TemporaryDirectory(prefix="godhand-hd-launch-synthetic-") as name:
            root = Path(name).resolve(); workspace = root/".local/retail-test"; workspace.mkdir(parents=True)
            exe = root/"invented-not-executable.txt"; exe.write_bytes(b"Invented data, not a program")
            variant = {"executable": {"path": str(exe)}, "source_revision": "a"*40,
                       "adapter_fingerprint": "b"*64, "hd_fingerprint": "c"*64,
                       "controls_adoption_executable": str(exe)}
            platform = SimpleNamespace(name="nt", environ={"PATH": os.environ.get("PATH", ""),
                "GODHAND_PC_HD_FILE": "stale", "GODHAND_PC_HD_SHA256": "stale", "PS2X_STATE_LOAD_AT": "stale"})
            child = SimpleNamespace(pid=987654, wait=lambda **kwargs: 124)
            identity = {"path": str(root/"invented-disc.txt")}
            flags = dict(profile="enhanced", hd_textures=True, headless=True, seconds=10, fresh_user_data=True)
            with patch.object(launch, "os", platform), patch.object(launch.hd, "verified_install", return_value=variant) as hd, \
                 patch.object(launch.runtime_packs, "verified_install") as base, patch.object(launch.pause, "verified_install") as pause, \
                 patch.object(launch.pc, "verify_disc", return_value=identity), patch.object(launch.pc, "git", return_value="d"*40), \
                 patch.object(launch.build, "require_no_game"), patch.object(launch.pc, "load_pin", return_value={"retail_profile": {}}), \
                 patch.object(launch.subprocess, "CREATE_NO_WINDOW", 0, create=True), \
                 patch.object(launch.subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0, create=True), \
                 patch.object(launch.subprocess, "Popen", return_value=child) as spawn:
                r = launch.launch(root, "retail-test", identity["path"], **flags)
            hd.assert_called_once(); base.assert_not_called(); pause.assert_not_called()
            env = spawn.call_args.kwargs["env"]
            for key in ("GODHAND_PC_HD_FILE", "GODHAND_PC_HD_SHA256", "GODHAND_PC_HD_PROFILE"):
                self.assertEqual(env[key], "")
            self.assertNotIn("PS2X_STATE_LOAD_AT", env)
            self.assertEqual(r["hd_textures"]["mode"], "original"); self.assertTrue(r["hd_textures"]["requested"])
            self.assertIn("not inferred", r["hd_textures"]["runtime_application"])
            self.assertEqual(json.loads(Path(r["receipt"]).read_text())["hd_textures"]["version"], "hd-v1")

    def test_strict_hd_failure_records_error_without_any_native_spawn(self):
        with tempfile.TemporaryDirectory(prefix="godhand-hd-strict-synthetic-") as name:
            variant = {"executable": {"path": "not-run"}, "source_revision": "a"*40,
                       "adapter_fingerprint": "b"*64, "hd_fingerprint": "c"*64}
            with patch.object(launch, "os", SimpleNamespace(name="nt")), patch.object(launch.hd, "verified_install", return_value=variant), \
                 patch.object(launch.pc, "verify_disc", return_value={"path": "never-open"}), \
                 patch.object(launch.pc, "git", return_value="a"*40), patch.object(launch.pc, "load_pin", return_value={"retail_profile": {}}), \
                 patch.object(launch.build, "require_no_game"), patch.object(launch.hd_packs, "protocol", side_effect=ValueError("strict HD refused")), \
                 patch.object(launch.subprocess, "Popen") as child:
                with self.assertRaisesRegex(ValueError, "strict HD"):
                    launch.launch(name, "retail-test", "absent", profile="enhanced", hd_textures=True, hd_pack="bad", strict_hd=True)
                child.assert_not_called()
