"""Invented launch/process doubles, never a native executable or game file."""
from pathlib import Path
from types import SimpleNamespace
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

import launch_packs as launch
import pc
import profiles
import video_settings as video


class VideoLaunchTests(unittest.TestCase):
    def test_original_and_wrong_flag_types_refuse_before_io(self):
        with patch.object(launch.runtime_packs, "workspace_path") as workspace, \
             patch.object(launch.subprocess, "Popen") as child:
            for value in [True, 1, "true", None]:
                with self.subTest(value=value), self.assertRaises(ValueError):
                    launch.launch("no-create", "retail-invented", "no-disc", video_settings=value)
            workspace.assert_not_called(); child.assert_not_called()

    def test_policy_does_not_bundle_other_capabilities(self):
        self.assertEqual(profiles.resolve("enhanced", video_settings=True)["requested_extensions"],
                         ["restart-required-video-settings"])
        self.assertEqual(profiles.resolve()["requested_extensions"], [])
        self.assertEqual(profiles.resolve("enhanced")["requested_extensions"], [])

    def test_cli_routes_show_update_reset_and_explicit_run(self):
        for args, action, scale in [([], "show", None), (["--internal-scale", "2"], "update", 2),
                                    (["--reset"], "update", None)]:
            with patch.object(sys, "argv", ["pc.py", "video-settings", "--workspace-name", "retail-invented"] + args), \
                 patch.object(video, action, return_value={}) as operation, patch("builtins.print"):
                pc.main()
            self.assertEqual(operation.call_args.args[:2], (pc.ROOT, "retail-invented"))
            if action == "update": self.assertEqual(operation.call_args.args[2], scale)
        for flag in [[], ["--video-settings"]]:
            with patch.object(sys, "argv", ["pc.py", "run", "--iso", "invented.iso", "--profile", "enhanced"] + flag), \
                 patch.object(launch, "launch", return_value={}) as run, patch("builtins.print"):
                pc.main()
            self.assertEqual(run.call_args.kwargs["video_settings"], bool(flag))

    def test_launch_snapshots_requested_settings_and_default_never_loads_preferences(self):
        with tempfile.TemporaryDirectory(prefix="godhand-video-launch-synthetic-") as name:
            root = Path(name).resolve()
            (root / ".local/retail-invented").mkdir(parents=True)
            exe = root / "invented-not-executable.txt"; exe.write_bytes(b"Invented text")
            variant = {"executable": {"path": str(exe)}, "source_revision": "a"*40, "adapter_fingerprint": "b"*64}
            platform = SimpleNamespace(name="nt", environ={"PATH": os.environ.get("PATH", ""),
                                       "PS2X_GS_SCALE": "8", "PS2X_GS_RENDERER": "stale", "GODHAND_DUMP": "1"})
            child = SimpleNamespace(pid=987654, wait=lambda **kwargs: 124)
            with patch.object(launch, "os", platform), \
                 patch.object(launch.runtime_packs, "verified_install", return_value=variant), \
                 patch.object(launch.pc, "verify_disc", return_value={"path": "invented-not-opened"}), \
                 patch.object(launch.pc, "load_pin", return_value={"retail_profile": {}}), \
                 patch.object(launch.pc, "git", return_value="c"*40), patch.object(launch.build, "require_no_game"), \
                 patch.object(launch.subprocess, "CREATE_NO_WINDOW", 0, create=True), \
                 patch.object(launch.subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0, create=True), \
                 patch.object(launch.subprocess, "Popen", return_value=child) as spawn:
                selected = video.update(root, "retail-invented", 2)
                result = launch.launch(root, "retail-invented", "no-disc", profile="enhanced", headless=True,
                                       seconds=10, fresh_user_data=True, video_settings=True)
                env = spawn.call_args.kwargs["env"]
                self.assertEqual(env["PS2X_GS_SCALE"], "2"); self.assertEqual(env["PS2X_GS_RENDERER"], "native")
                self.assertEqual(env["GODHAND_CONTROLS_SELFTEST"], "0"); self.assertNotIn("GODHAND_DUMP", env)
                self.assertEqual(result["video_settings"]["sha256"], selected["sha256"])
                self.assertTrue(Path(result["video_settings"]["frozen_path"]).is_file())
                video.update(root, "retail-invented", None)
                launch.launch(root, "retail-invented", "no-disc", profile="enhanced", headless=True,
                              seconds=10, fresh_user_data=True, video_settings=True)
                self.assertNotIn("PS2X_GS_SCALE", spawn.call_args.kwargs["env"])
                with patch.object(video, "protocol", side_effect=AssertionError("Default must not read video prefs")):
                    baseline = launch.launch(root, "retail-invented", "no-disc", headless=True, seconds=10, fresh_user_data=True)
                self.assertEqual(baseline["video_settings"]["mode"], "unselected")
                self.assertNotIn("PS2X_GS_RENDERER", spawn.call_args.kwargs["env"])
                with patch.object(video, "protocol", side_effect=ValueError("Invented invalid explicit prefs")):
                    spawn.reset_mock()
                    with self.assertRaises(ValueError):
                        launch.launch(root, "retail-invented", "no-disc", profile="enhanced", headless=True,
                                      seconds=10, fresh_user_data=True, video_settings=True)
                    spawn.assert_not_called()
