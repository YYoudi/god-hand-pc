"""Invented launch/policy inputs only, never game/native/hardware evidence."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json
import os
import sys
import tempfile
import unittest
import launch_packs as launch
import profiles
import pc
import video_settings as video


class NativeMenuPolicyTests(unittest.TestCase):
    def test_incomplete_or_wrong_compositions_refuse_before_io(self):
        flags = dict(profile="enhanced", native_menu=True, video_settings=True)
        cases = [{**flags, key: value} for key, value in [("profile", "original"), ("video_settings", False),
                 ("native_menu", 1)]]
        cases += [{**flags, "controls_pause": True}, {**flags, "controls_pause": True, "controls_pause_version": "v1"},
                  {**flags, "hd_textures": True}, {**flags, "hd_textures": True, "hd_textures_version": "gpu-audio-v3"},
                  {**flags, "hd_textures": True, "hd_textures_version": "gpu-v2", "pack": "no"}]
        with patch.object(launch.runtime_packs, "workspace_path") as workspace, patch.object(launch.subprocess, "Popen") as spawn:
            for case in cases:
                with self.subTest(case=case), self.assertRaises(ValueError): launch.launch("no-create", "fixture", "missing", **case)
        workspace.assert_not_called(); spawn.assert_not_called()
        self.assertEqual(profiles.resolve()["requested_extensions"], [])
        self.assertIn("experimental-native-video-menu-audio-v2", profiles.resolve(**{
            "name": "enhanced", "native_menu": True, "video_settings": True})["requested_extensions"])

    def test_cli_routes_explicit_capability_and_install(self):
        with patch.object(sys, "argv", ["pc.py", "install-native-menu"]), \
             patch.object(launch.menu, "install", return_value={}) as install, patch("builtins.print"):
            pc.main()
        install.assert_called_once_with(pc.ROOT, "retail-setup")
        with patch.object(sys, "argv", ["pc.py", "run", "--iso", "invented", "--profile", "enhanced", "--video-settings", "--native-menu"]), \
             patch.object(launch, "launch", return_value={}) as run, patch("builtins.print"):
            pc.main()
        self.assertTrue(run.call_args.kwargs["native_menu"])

    def test_real_broker_lifetime_scratch_seed_default_probe_off_and_exact_variant_selection(self):
        with tempfile.TemporaryDirectory(prefix="godhand-menu-launch-invented-") as name:
            root = Path(name).resolve(); (root / ".local/retail-fixture").mkdir(parents=True)
            initial = video.update(root, "retail-fixture", 3)
            exe = root / "invented-not-executable.txt"; exe.write_bytes(b"Invented original file")
            variant = {"executable": {"path": str(exe)}, "source_revision": "a" * 40, "adapter_fingerprint": "b" * 64,
                       "menu_fingerprint": "c" * 64, "controls_adoption_executable": str(exe)}
            platform = SimpleNamespace(name="nt", environ={"PATH": os.environ.get("PATH", ""),
                "GODHAND_PC_VIDEO_MENU_SELFTEST": "scale2", "GODHAND_PC_VIDEO_MENU_DIR": "inherited-wrong"})
            child = SimpleNamespace(pid=987654, wait=lambda **kw: 124, poll=lambda: 124)
            with patch.object(launch, "os", platform), patch.object(launch.menu, "verified_install", return_value=variant) as menu, \
                 patch.object(launch.hd, "verified_install") as hd, patch.object(launch.pause, "verified_install") as pause, \
                 patch.object(launch.runtime_packs, "verified_install") as base, \
                 patch.object(launch.pc, "verify_disc", return_value={"path": "invented-not-opened"}), \
                 patch.object(launch.pc, "load_pin", return_value={"retail_profile": {}}), \
                 patch.object(launch.pc, "git", return_value="d" * 40), patch.object(launch.build, "require_no_game"), \
                 patch.object(launch.subprocess, "CREATE_NO_WINDOW", 0, create=True), \
                 patch.object(launch.subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0, create=True), \
                 patch.object(launch.subprocess, "Popen", return_value=child) as spawn:
                result = launch.launch(root, "retail-fixture", "not-opened", headless=True, seconds=10,
                    fresh_user_data=True, profile="enhanced", native_menu=True, video_settings=True)
            menu.assert_called_once_with(root, "retail-fixture"); hd.assert_not_called(); pause.assert_not_called(); base.assert_not_called()
            env = spawn.call_args.kwargs["env"]
            self.assertEqual(env["GODHAND_PC_VIDEO_MENU_SELFTEST"], "0")
            self.assertEqual(env["GODHAND_PC_VIDEO_MENU_SELFTEST_FIELD"], "0")
            self.assertEqual(env["GODHAND_PC_CONTROLS_PAUSE"], "1")
            self.assertEqual(env["GODHAND_CONTROLS_SELFTEST"], "0")
            self.assertEqual(env["PS2X_GS_RENDERER"], "native")
            self.assertEqual(video.show(root, "retail-fixture"), initial)
            self.assertTrue(result["native_menu"]["broker"]["stopped"])
            self.assertIsNone(result["native_menu"]["broker"]["error"])
            config = (Path(result["native_menu"]["channel"]) / "config.txt").read_bytes()
            self.assertTrue(config.endswith(b"\tscratch\n"))
