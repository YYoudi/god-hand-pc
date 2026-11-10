"""Original invented Git/source/build doubles, not native or game evidence."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json
import unittest

import native_menu as menu
import hd_textures as hd
import controls_pause as audio
import pc
import test_hd_install as fixtures


class NativeMenuInstallTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.HDInstallTests(methodName="runTest")
        # Include invented Runtime CMake in the initial source pin, NOT as an
        # unrelated edit to the already-verified pack baseline.
        with patch.object(hd, "MODIFIED", hd.MODIFIED | {menu.CMAKE}): self.f.setUp()
        self.addCleanup(self.f.doCleanups)
        self.f.recipe(hd.MODIFIED, hd.copies("gpu-v2"), "adapter/hd_gpu_integration.json", version="hd-gpu-v2")
        self.f.recipe(audio.MODIFIED, audio.AUDIO_COPIES, "adapter/audio_controls_integration.json", version="audio-v2")
        parent = hd.integration(self.f.root, menu.PARENT)
        planned = hd.plan_sources(self.f.source, self.f.root, parent)
        files = []
        for name in sorted(menu.OWN_MODIFIED):
            path = self.f.source / name
            before = planned[path] if path in planned else path.read_bytes()
            after = before + b"// Invented ordered addition.\n"
            files.append({"path": name, "before_sha256": hd.packs.sha(before), "after_sha256": hd.packs.sha(after),
                          "edits": [{"start": len(before), "end": len(before), "insert": "// Invented ordered addition.\n"}]})
        for name in menu.COPIES:
            path = self.f.root / name; path.parent.mkdir(exist_ok=True, parents=True)
            path.write_bytes(b"// Original invented menu helper\n")
        recipe = {"schema": 1, "version": menu.VERSION, "upstream_revision": self.f.pin["revision"],
                  "parent_fingerprint": hd.fingerprint(self.f.root, parent), "files": files, "copies": menu.COPIES}
        (self.f.root / "adapter/native_menu_integration.json").write_text(json.dumps(recipe))
        self.f.commit(self.f.root)

    def install(self, step=None):
        with patch.object(menu, "os", self.f.platform), patch.object(menu.subprocess, "check_output", side_effect=self.f.output), \
             patch.object(menu.shutil, "disk_usage", return_value=SimpleNamespace(free=16 * 1024**3)), \
             patch.object(menu.build.Run, "step", autospec=True, side_effect=step or self.f.fake_build):
            return menu.install(self.f.root, "retail-fixture")

    def test_ordered_install_preserves_baseline_and_repeated_install_does_not_relink(self):
        result = self.install(); self.f.assert_base()
        self.assertTrue(result["baseline_restored"])
        self.assertFalse(result["tooling_dirty"])
        self.assertEqual(len(result["source_files"]), 32)
        self.assertEqual(self.install(lambda *a: self.fail("No relink"))["executable"], result["executable"])
        self.assertFalse((self.f.workspace / "setup.lock").exists())

    def test_parent_then_menu_preimage_required_and_drift_never_fuzzed(self):
        recipe = menu.integration(self.f.root)
        entry = next(x for x in recipe["files"] if x["path"] == menu.RUNTIME)
        with self.assertRaisesRegex(ValueError, "preimage"):
            hd.packs.transform((self.f.source / menu.RUNTIME).read_bytes(), entry)
        entry["before_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "preimage"): menu.plan_sources(self.f.source, self.f.root, recipe)
        self.f.assert_base()

    def test_install_source_binary_and_helper_drift_refuse(self):
        result = self.install(); run = Path(result["receipt"]).parent
        for p in [run / "source" / menu.RUNTIME, Path(result["executable"]["path"]),
                  self.f.root / "adapter/video_menu_factory.hpp"]:
            before = p.read_bytes()
            try:
                p.write_bytes(before + b"invented drift")
                with self.assertRaises(ValueError): menu.verified_install(self.f.root, "retail-fixture")
            finally: p.write_bytes(before)

    def test_terminal_failure_restores_and_retains_attempt_no_retry(self):
        def fail(run, name, *args):
            self.f.fake_build(run, name, *args)
            if name == "menu-build": raise ValueError("Invented failed link")
        with self.assertRaisesRegex(ValueError, "Invented failed link"): self.install(fail)
        self.f.assert_base()
        layer = self.f.workspace / menu.VERSION
        self.assertTrue((layer / "attempt.json").exists()); self.assertFalse((layer / "installed.json").exists())
        with self.assertRaisesRegex(ValueError, "Previous menu attempt"): self.install()

    def test_live_build_interruption_keeps_source_and_locks(self):
        def live(run, *args): run.child = SimpleNamespace(poll=lambda: None); raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt): self.install(live)
        self.assertTrue((self.f.workspace / "setup.lock").exists())
        self.assertTrue((self.f.workspace / (menu.VERSION + "/install.lock")).exists())
        self.assertNotEqual(pc.git("rev-parse", "HEAD", cwd=self.f.source), self.f.base["source_revision"])

    def test_public_parent_fingerprint_frozen_and_only_ordered_host_paths(self):
        recipe = menu.integration(pc.ROOT)
        self.assertEqual(recipe["parent_fingerprint"], "72ceaf2309cd86aedbc1d9f122f36464bf3a65a82874a69594aad65f86ea8fa9")
        self.assertEqual(len(recipe["copies"]), 9)
        self.assertEqual({e["path"] for e in recipe["files"]}, menu.OWN_MODIFIED)
        self.assertNotIn("target_include_directories", recipe["files"][1]["edits"][0]["insert"])

    def test_low_capacity_refuses_without_creating_build_attempt(self):
        with patch.object(menu, "os", self.f.platform), \
             patch.object(menu.shutil, "disk_usage", return_value=SimpleNamespace(free=1024)):
            with self.assertRaisesRegex(ValueError, "8GiB"): menu.install(self.f.root, "retail-fixture")
        self.f.assert_base()
        self.assertFalse((self.f.workspace / (menu.VERSION + "/attempt.json")).exists())
        self.assertFalse((self.f.workspace / "setup.lock").exists())
