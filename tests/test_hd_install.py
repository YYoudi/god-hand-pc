"""Invented Git/source/executable fixtures; no game generation or execution."""
from pathlib import Path
import json
import os
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import controls_pause as controls
import hd_textures as hd
import pc


class HDInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="godhand-hd-variant-synthetic-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.workspace = self.root/".local/retail-fixture"
        self.source = self.workspace/"upstream"; self.source.mkdir(parents=True)
        (self.source/".gitignore").write_text("build/\n")
        for name in hd.MODIFIED | hd.packs.MODIFIED | controls.MODIFIED:
            p = self.source/name; p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"// Entirely invented original source.\n")
        self.init(self.source)
        self.pin = pc.load_pin(); self.pin["revision"] = pc.git("rev-parse", "HEAD", cwd=self.source)
        (self.root/"upstream.json").write_text(json.dumps(self.pin))
        pack = self.recipe(hd.packs.MODIFIED, hd.packs.COPIES, "adapter/integration.json")
        planned = hd.packs.plan_sources(self.source, self.root, pack)
        for p, raw in planned.items(): p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(raw)
        self.commit(self.source)
        self.exe = self.source/"build/port/bin/godhand.exe"; self.exe.parent.mkdir(parents=True)
        for name in ("godhand.exe", "godhand.pdb", "godhand.ini"):
            (self.exe.parent/name).write_bytes(("Invented original " + name).encode())
        self.original = {p.name: p.read_bytes() for p in self.exe.parent.iterdir()}
        disc = self.workspace/"invented-disc.txt"; disc.write_bytes(b"Original invented disc, not a game.")
        self.pin["retail_profile"] = {"bytes": disc.stat().st_size, "sha256": hd.build.digest(disc)}
        (self.root/"upstream.json").write_text(json.dumps(self.pin))
        setup = self.workspace/"invented-setup.json"; setup.write_text(json.dumps({"environment": {}, "disc": {"path": str(disc)}}))
        self.base = {"source_revision": pc.git("rev-parse", "HEAD", cwd=self.source),
                     "adapter_fingerprint": hd.packs.fingerprint(self.root, pack),
                     "source_files": {p.relative_to(self.source).as_posix(): hd.packs.sha(raw) for p, raw in planned.items()},
                     "setup_receipt": str(setup), "executable": {"path": str(self.exe),
                     "bytes": self.exe.stat().st_size, "sha256": hd.build.digest(self.exe)}}
        (self.workspace/"packs").mkdir(); (self.workspace/"packs/installed.json").write_text(json.dumps(self.base))
        self.recipe(hd.MODIFIED, hd.COPIES, "adapter/hd_integration.json", version=hd.VERSION)
        self.recipe(controls.MODIFIED, controls.COPIES, "adapter/controls_integration.json")
        (self.root/".gitignore").write_text(".local/\n"); self.init(self.root)
        self.platform = SimpleNamespace(name="nt", getpid=os.getpid, environ=os.environ, utime=os.utime)
        self.original_output = subprocess.check_output

    def commit(self, source):
        pc.git("add", "--all", cwd=source); pc.git("commit", "-m", "Invented fixture only", cwd=source)

    def init(self, source):
        pc.git("init", cwd=source); pc.git("config", "user.name", "Synthetic fixture", cwd=source)
        pc.git("config", "user.email", "fixture@example.invalid", cwd=source)
        pc.git("config", "core.autocrlf", "false", cwd=source); self.commit(source)

    def recipe(self, modified, copies, filename, **extra):
        items = []
        for name in sorted(modified):
            before = (self.source/name).read_bytes(); after = before+b"// Invented owned addition.\n"
            items.append({"path": name, "before_sha256": hd.packs.sha(before), "after_sha256": hd.packs.sha(after),
                          "edits": [{"start": len(before), "end": len(before), "insert": "// Invented owned addition.\n"}]})
        for name in copies:
            p = self.root/name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b"// Original invented helper.\n")
        result = {"schema": 1, "upstream_revision": self.pin["revision"], "files": items, "copies": copies, **extra}
        (self.root/filename).write_text(json.dumps(result)); return result

    def output(self, command, **kwargs):
        if command[0] == "tasklist": return b"No invented game process."
        return self.original_output(command, **kwargs)

    def fake_build(self, run, name, command, checkout, env):
        run.record["steps"].append({"name": name, "exit": 0})
        if name.endswith("-build"):
            self.exe.write_bytes(b"Invented derived file, not executable code.")
            self.exe.with_suffix(".pdb").write_bytes(b"Invented derived symbols.")
        run.save()

    def install(self, step=None):
        with patch.object(hd, "os", self.platform), patch.object(hd.subprocess, "check_output", side_effect=self.output), \
             patch.object(hd.build.Run, "step", autospec=True, side_effect=step or self.fake_build):
            return hd.install(self.root, "retail-fixture")

    def assert_base(self):
        self.assertEqual(hd.packs.verified_install(self.root, "retail-fixture"), self.base)
        self.assertEqual({p.name: p.read_bytes() for p in self.exe.parent.iterdir()}, self.original)

    def test_public_recipe_scope_and_private_pinned_preimages(self):
        recipe = hd.integration(pc.ROOT)
        self.assertEqual(len(recipe["files"]), 2); self.assertEqual(len(recipe["copies"]), 4)
        self.assertFalse(any("generated" in p for p in hd.MODIFIED | set(hd.COPIES.values())))

    def test_additive_install_and_repeated_verification_preserve_all_original_bytes(self):
        r = self.install(); self.assert_base()
        self.assertEqual(len(r["source_files"]), 14)
        self.assertFalse(r["tooling_dirty"]); self.assertTrue(r["baseline_restored"])
        self.assertEqual(r["controls_adoption_executable"], str(self.exe))
        self.assertEqual(Path(r["variant_sidecars"]["godhand.ini"]["path"]).read_bytes(), self.original["godhand.ini"])
        self.assertEqual(self.install(lambda *a: self.fail("Must not rebuild"))["source_revision"], r["source_revision"])
        self.assertFalse((self.workspace/"setup.lock").exists())

    def test_terminal_failure_restores_and_retains_attempt_without_automatic_retry(self):
        def fail(run, name, *a):
            self.fake_build(run, name, *a)
            if name == "hd-build": raise ValueError("Invented terminal failure")
        with self.assertRaisesRegex(ValueError, "Invented terminal"): self.install(fail)
        self.assert_base(); self.assertFalse((self.workspace/"hd-v1/installed.json").exists())
        with self.assertRaisesRegex(ValueError, "Previous HD attempt"): self.install()

    def test_live_interruption_keeps_exact_locks_and_source(self):
        def interrupt(run, *a): run.child = SimpleNamespace(poll=lambda: None); raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt): self.install(interrupt)
        self.assertTrue((self.workspace/"setup.lock").exists()); self.assertTrue((self.workspace/"hd-v1/install.lock").exists())
        self.assertNotEqual(pc.git("rev-parse", "HEAD", cwd=self.source), self.base["source_revision"])

    def test_unrelated_source_change_is_never_reset(self):
        target = self.source/hd.GPU
        def changed(run, name, *a):
            self.fake_build(run, name, *a)
            if name == "hd-build": target.write_bytes(b"Preserve unrelated invented source.\n")
        with self.assertRaisesRegex(ValueError, "uncommitted"): self.install(changed)
        self.assertEqual(target.read_bytes(), b"Preserve unrelated invented source.\n")
        self.assertTrue((self.workspace/"setup.lock").exists())

    def test_executable_base_source_and_recipe_drift_are_refused(self):
        r = self.install(); source = Path(r["receipt"]).parent/"source"
        for target in [Path(r["executable"]["path"]), self.exe, source/hd.GPU, self.root/"adapter/hd_runtime.hpp"]:
            before = target.read_bytes()
            try:
                target.write_bytes(before+b"invented drift")
                with self.assertRaises(ValueError): hd.verified_install(self.root, "retail-fixture")
            finally: target.write_bytes(before)
        self.assert_base()

    def test_existing_controls_install_remains_independent(self):
        with patch.object(controls, "os", self.platform), patch.object(controls.subprocess, "check_output", side_effect=self.output), \
             patch.object(controls.build.Run, "step", autospec=True, side_effect=self.fake_build):
            old = controls.install(self.root, "retail-fixture")
        self.assert_base(); self.install(); self.assert_base()
        self.assertEqual(controls.verified_install(self.root, "retail-fixture")["executable"], old["executable"])


if __name__ == "__main__": unittest.main()
