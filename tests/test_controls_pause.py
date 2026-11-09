"""Invented host/Git/executable fixtures only; never generate or run a game."""
from pathlib import Path
import copy
import json
import os
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import controls_pause as c
import launch_packs
import pc
import profiles


class ControlsInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="godhand-controls-synthetic-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.workspace = self.root / ".local/retail-fixture"
        self.source = self.workspace / "upstream"
        self.source.mkdir(parents=True)
        self.raw = b"// Entirely invented source unit.\n"
        (self.source / ".gitignore").write_text("build/\n")
        for relative in c.MODIFIED | c.packs.MODIFIED:
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(self.raw)
        self.git_init(self.source)
        self.pin = c.pc.load_pin()
        self.pin["revision"] = pc.git("rev-parse", "HEAD", cwd=self.source)
        (self.root / "upstream.json").write_text(json.dumps(self.pin))
        self.make_recipe(c.packs, "adapter/integration.json", b"// Invented pack change.\n")
        pack_recipe = c.packs.integration(self.root)
        planned = c.packs.plan_sources(self.source, self.root, pack_recipe)
        for path, data in planned.items():
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
        self.commit(self.source)
        self.exe = self.source / "build/port/bin/godhand.exe"
        self.exe.parent.mkdir(parents=True)
        for filename in ("godhand.exe", "godhand.pdb", "godhand.ini"):
            (self.exe.parent / filename).write_bytes(("Invented baseline " + filename).encode())
        self.original = {p.name: p.read_bytes() for p in self.exe.parent.iterdir()}
        disc = self.workspace / "invented-disc.txt"
        disc.write_bytes(b"Original invented disc fixture; no game bytes.")
        self.pin["retail_profile"] = {"bytes": disc.stat().st_size, "sha256": c.build.digest(disc)}
        (self.root / "upstream.json").write_text(json.dumps(self.pin))
        setup = self.workspace / "invented-setup.json"
        setup.write_text(json.dumps({"environment": {}, "disc": {"path": str(disc)}}))
        self.base = {"source_revision": pc.git("rev-parse", "HEAD", cwd=self.source),
                     "adapter_fingerprint": c.packs.fingerprint(self.root, pack_recipe),
                     "source_files": {p.relative_to(self.source).as_posix(): c.packs.sha(raw)
                                      for p, raw in planned.items()},
                     "setup_receipt": str(setup), "executable": {
                         "path": str(self.exe), "bytes": self.exe.stat().st_size, "sha256": c.build.digest(self.exe)}}
        (self.workspace / "packs").mkdir()
        (self.workspace / "packs/installed.json").write_text(json.dumps(self.base))
        self.recipe = self.make_recipe(c, "adapter/controls_integration.json", b"// Invented controls change.\n")
        (self.root / ".gitignore").write_text(".local/\n")
        self.git_init(self.root)
        self.original_check_output = subprocess.check_output
        self.platform = SimpleNamespace(name="nt", getpid=os.getpid, environ=os.environ, utime=os.utime)

    def git_init(self, source):
        pc.git("init", cwd=source)
        pc.git("config", "user.name", "Original synthetic fixture", cwd=source)
        pc.git("config", "user.email", "fixture@example.invalid", cwd=source)
        pc.git("config", "core.autocrlf", "false", cwd=source)
        self.commit(source)

    def commit(self, source):
        pc.git("add", "--all", cwd=source)
        pc.git("commit", "-m", "Invented fixture only", cwd=source)

    def make_recipe(self, module, name, addition):
        result = self.raw + addition
        data = {"schema": 1, "upstream_revision": self.pin["revision"], "copies": module.COPIES,
                "files": [{"path": p, "before_sha256": c.packs.sha(self.raw),
                           "after_sha256": c.packs.sha(result), "edits": [
                               {"start": len(self.raw), "end": len(self.raw), "insert": addition.decode()}]}
                          for p in sorted(module.MODIFIED)]}
        for relative in module.COPIES:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"// Invented original header fixture.\n")
        (self.root / name).write_text(json.dumps(data))
        return data

    def output(self, command, **kwargs):
        if command[0] == "tasklist": return "No invented game process."
        return self.original_check_output(command, **kwargs)

    def fake_build(self, run, name, command, checkout, env):
        run.record["steps"].append({"name": name, "command": command, "exit": 0})
        if name == "controls-build":
            self.exe.write_bytes(b"Invented derived executable, not a runnable program.")
            self.exe.with_suffix(".pdb").write_bytes(b"Invented derived symbols.")
        run.save()

    def install(self, step=None):
        with patch.object(c, "os", self.platform), patch.object(c.subprocess, "check_output", side_effect=self.output), \
             patch.object(c.build.Run, "step", autospec=True, side_effect=step or self.fake_build):
            return c.install(self.root, "retail-fixture")

    def assert_baseline(self):
        self.assertEqual(c.packs.verified_install(self.root, "retail-fixture"), self.base)
        self.assertEqual({p.name: p.read_bytes() for p in self.exe.parent.iterdir()}, self.original)

    def test_public_recipe_only_touches_reviewed_host_files_and_original_copies(self):
        recipe = c.integration(pc.ROOT)
        self.assertEqual(len(recipe["files"]), 4)
        self.assertEqual(len(recipe["copies"]), 3)
        self.assertFalse(any("generated" in name for name in c.MODIFIED | set(c.COPIES.values())))

    def test_separate_worktree_executable_and_sidecars_baseline_byte_restoration(self):
        result = self.install()
        self.assertFalse(result["tooling_dirty"])
        self.assert_baseline()
        self.assertNotEqual(result["executable"]["path"], str(self.exe))
        self.assertTrue(result["baseline_restored"])
        self.assertEqual(len(result["source_files"]), 16)
        self.assertEqual(result["controls_adoption_executable"], str(self.exe))
        self.assertEqual(Path(result["variant_sidecars"]["godhand.ini"]["path"]).read_bytes(), self.original["godhand.ini"])
        self.assertNotEqual(result["variant_sidecars"]["godhand.pdb"]["sha256"], result["baseline_backups"]["godhand.pdb"]["sha256"])
        # Repeated install verifies, does not relink, recreate branches or overwrite.
        again = self.install(step=lambda *args: self.fail("Must not rebuild"))
        self.assertEqual(again["source_revision"], result["source_revision"])
        self.assertFalse((self.workspace / "setup.lock").exists())

    def test_terminal_build_failure_restores_baseline_but_refuses_blind_retry(self):
        def fail(run, name, command, checkout, env):
            self.fake_build(run, name, command, checkout, env)
            if name == "controls-build": raise ValueError("Invented terminal compile failure")
        with self.assertRaisesRegex(ValueError, "Invented terminal"):
            self.install(fail)
        self.assert_baseline()
        self.assertFalse((self.workspace / "setup.lock").exists())
        self.assertFalse((self.workspace / "controls/installed.json").exists())
        with self.assertRaisesRegex(ValueError, "Previous controls attempt"):
            self.install()

    def test_live_child_interruption_retains_lock_source_and_evidence(self):
        def interrupt(run, *args):
            run.child = SimpleNamespace(poll=lambda: None)
            raise KeyboardInterrupt("Invented live child")
        with self.assertRaises(KeyboardInterrupt): self.install(interrupt)
        self.assertTrue((self.workspace / "setup.lock").is_file())
        self.assertTrue((self.workspace / "controls/install.lock").is_file())
        self.assertNotEqual(pc.git("rev-parse", "HEAD", cwd=self.source), self.base["source_revision"])
        self.assertFalse((self.workspace / "controls/installed.json").exists())

    def test_concurrent_source_edit_is_preserved_not_reset(self):
        path = self.source / next(iter(c.MODIFIED))
        def changed(run, name, command, checkout, env):
            self.fake_build(run, name, command, checkout, env)
            if name == "controls-build": path.write_bytes(b"Preserve this invented unrelated edit.\n")
        with self.assertRaisesRegex(ValueError, "uncommitted"):
            self.install(changed)
        self.assertEqual(path.read_bytes(), b"Preserve this invented unrelated edit.\n")
        self.assertTrue((self.workspace / "setup.lock").exists())

    def test_variant_source_executable_or_base_drift_is_refused(self):
        result = self.install()
        worktree = Path(result["receipt"]).parent / "source"
        for path in (Path(result["executable"]["path"]), self.exe, worktree / next(iter(c.MODIFIED))):
            raw = path.read_bytes()
            try:
                path.write_bytes(raw + b"Invented drift.")
                with self.assertRaises(ValueError): c.verified_install(self.root, "retail-fixture")
            finally: path.write_bytes(raw)
        self.assert_baseline()

    def test_recipe_drift_wrong_paths_and_last_preimage_fail_without_writes(self):
        first = self.source / self.recipe["files"][0]["path"]
        last = self.source / self.recipe["files"][-1]["path"]
        last.write_bytes(b"Invented later change.")
        with self.assertRaisesRegex(ValueError, "preimage"):
            c.plan_sources(self.source, self.root, self.recipe)
        self.assertEqual(first.read_bytes(), self.raw)
        bad = copy.deepcopy(self.recipe)
        bad["files"][0]["path"] = "generated/forbidden.cpp"
        (self.root / "adapter/controls_integration.json").write_text(json.dumps(bad))
        with self.assertRaisesRegex(ValueError, "Unreviewed"): c.integration(self.root)

    def test_public_launcher_environment_overrides_ini_and_never_enables_probe(self):
        for on in (False, True):
            env = launch_packs.controls_pause_environment(on)
            self.assertEqual(env["GODHAND_PC_CONTROLS_PAUSE"], "1" if on else "0")
            self.assertEqual(env["GODHAND_PC_CONTROLS_PROBE"], "0")
            self.assertEqual(env["GODHAND_PC_CONTROLS_PROBE_FIELD"], "0")
        with self.assertRaises(ValueError): launch_packs.controls_pause_environment(1)

    def test_original_refusal_precedes_any_runtime_disc_or_native_access(self):
        with patch.object(c, "verified_install") as installed, patch.object(pc, "verify_disc") as disc:
            with self.assertRaisesRegex(ValueError, "Original profile refuses host-pause"):
                launch_packs.launch(self.root, "retail-fixture", "absent", controls_pause=True)
            installed.assert_not_called(); disc.assert_not_called()
        self.assertEqual(profiles.resolve("enhanced", controls_pause=True)["requested_extensions"],
                         ["experimental-controls-pause"])


class ProbeRoutingTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("g++") or shutil.which("clang++"), "C++20 needed")
    def test_actual_probe_guard_and_field_threshold_only_in_separate_processes(self):
        with tempfile.TemporaryDirectory(prefix="godhand-probe-synthetic-") as name:
            root = Path(name)
            source = root / "invented.cpp"
            source.write_text('#include "controls_probe.hpp"\n#include <cstdio>\nint main(){'
                              'std::printf("%d %d ",godhand_pc_probe::active(),godhand_pc_probe::ready());'
                              'godhand_pc_probe::observed_field.store(48);'
                              'std::printf("%d",godhand_pc_probe::ready());}\n')
            exe = root / "invented.exe"
            subprocess.run([shutil.which("g++") or shutil.which("clang++"), "-std=c++20", "-O2", "-Wall",
                            "-Wextra", "-Werror", "-I", str(pc.ROOT / "adapter"), str(source), "-o", str(exe)],
                           check=True, capture_output=True, timeout=90)
            env = launch_packs.clean_environment(os.environ)
            for flag, script, target, expected in [
                    ("0", "f1,done", "48", "0 1 1"), ("1", "0", "48", "0 1 1"),
                    ("1", "", "48", "0 1 1"), ("1", "f1,done", "48", "1 0 1"),
                    ("1", "f1,done", "49", "1 0 0"), ("1", "f1,done", "-1", "1 1 1"),
                    ("1", "f1,done", "18446744073709551616", "1 1 1"),
                    ("1", "f1,done", "48bad", "1 1 1")]:
                actual = subprocess.check_output([str(exe)], env=dict(env, GODHAND_PC_CONTROLS_PROBE=flag,
                    GODHAND_CONTROLS_SELFTEST=script, GODHAND_PC_CONTROLS_PROBE_FIELD=target), text=True, timeout=10)
                self.assertEqual(actual, expected, (flag, script, target))


if __name__ == "__main__": unittest.main()
