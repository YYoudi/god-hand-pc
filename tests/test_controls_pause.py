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

    def install(self, step=None, version="v1"):
        with patch.object(c, "os", self.platform), patch.object(c.subprocess, "check_output", side_effect=self.output), \
             patch.object(c.build.Run, "step", autospec=True, side_effect=step or self.fake_build):
            return c.install(self.root, "retail-fixture", version)

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

    def audio_recipe(self):
        module = SimpleNamespace(MODIFIED=c.MODIFIED, COPIES=c.AUDIO_COPIES)
        recipe = self.make_recipe(module, "adapter/audio_controls_integration.json",
                                  b"// Invented audio admission integration.\n")
        recipe["version"] = "audio-v2"
        (self.root / "adapter/audio_controls_integration.json").write_text(json.dumps(recipe))
        self.commit(self.root)

    def test_versioned_installs_coexist_and_never_overwrite_legacy_v1(self):
        v1 = self.install()
        legacy_receipt = Path(v1["receipt"])
        # The actual older v1 receipt predates the explicit version field.
        legacy = json.loads(legacy_receipt.read_text())
        del legacy["controls_version"]
        legacy_receipt.write_text(json.dumps(legacy))
        self.audio_recipe()
        v2 = self.install(version="audio-v2")
        self.assert_baseline()
        self.assertEqual(v2["controls_version"], "audio-v2")
        self.assertEqual(len(v2["source_files"]), 17)
        self.assertEqual(c.verified_install(self.root, "retail-fixture")["executable"], v1["executable"])
        self.assertNotEqual(v1["executable"]["path"], v2["executable"]["path"])
        self.assertEqual(json.loads(legacy_receipt.read_text()), legacy)
        self.assertTrue((self.workspace / "controls/installed.json").is_file())
        self.assertTrue((self.workspace / "controls-audio-v2/installed.json").is_file())
        again = self.install(step=lambda *args: self.fail("Must not rebuild"), version="audio-v2")
        self.assertEqual(again["source_revision"], v2["source_revision"])
        # Explicitly changed v2 metadata never qualifies as v1 or a silent upgrade.
        receipt = Path(v2["receipt"]); data = json.loads(receipt.read_text())
        data["controls_version"] = "v1"; receipt.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "install/base version"):
            c.verified_install(self.root, "retail-fixture", "audio-v2")
        c.verified_install(self.root, "retail-fixture")

    def test_unknown_version_refuses_before_creating_storage(self):
        for version in ("future", "../v1", "", None, 1):
            with self.subTest(version=version), self.assertRaisesRegex(ValueError, "Unknown controls version"):
                c.install(self.root / "not-created", "retail-fixture", version)
        self.assertFalse((self.root / "not-created").exists())

    def test_public_audio_recipe_has_extra_original_consumer_barrier_only(self):
        recipe = c.integration(pc.ROOT, "audio-v2")
        self.assertEqual(recipe["version"], "audio-v2")
        self.assertEqual(set(recipe["copies"]), set(c.AUDIO_COPIES))
        self.assertEqual(len(recipe["files"]), 4)

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

    def test_explicit_version_needs_pause_and_enhanced_before_runtime(self):
        for pause, profile in ((False, "enhanced"), (True, "original")):
            with patch.object(c, "verified_install") as check, self.assertRaises(ValueError):
                launch_packs.launch(self.root, "retail-fixture", "absent", profile=profile,
                                   controls_pause=pause, controls_pause_version="audio-v2")
            check.assert_not_called()
        self.assertEqual(profiles.resolve("enhanced", controls_pause=True,
                         controls_pause_version="audio-v2")["requested_extensions"],
                         ["experimental-controls-pause-audio-v2"])

    def test_full_launcher_selects_variant_only_on_request_and_never_leaks_probes(self):
        variant = self.install()
        audio = dict(variant, source_revision="2" * 40, controls_version="audio-v2",
                     executable=dict(variant["executable"], path=str(self.root / "invented-audio-v2.exe")))
        calls = []
        def popen(command, **kwargs):
            calls.append((command, kwargs))
            return SimpleNamespace(pid=123456, wait=lambda **ignored: 124)
        native = SimpleNamespace(check_output=lambda *args, **kwargs: "No invented game",
                                 Popen=popen, CREATE_NO_WINDOW=0, BELOW_NORMAL_PRIORITY_CLASS=0,
                                 TimeoutExpired=subprocess.TimeoutExpired, STDOUT=subprocess.STDOUT)
        dirty_env = dict(os.environ, GODHAND_PC_CONTROLS_PAUSE="1", GODHAND_PC_CONTROLS_PROBE="1",
                         GODHAND_CONTROLS_SELFTEST="f1,done", PS2X_STATE_LOAD_AT="invented-stale")
        platform = SimpleNamespace(name="nt", environ=dirty_env)
        with patch.object(launch_packs, "os", platform), patch.object(launch_packs, "subprocess", native), \
             patch.object(pc, "git", return_value="1" * 40), \
             patch.object(c.packs, "verified_install", return_value=self.base) as base_check, \
             patch.object(c, "verified_install", side_effect=lambda root, name, version:
                          audio if version == "audio-v2" else variant) as variant_check:
            for requested, version in ((False, None), (True, None), (True, "audio-v2")):
                receipt = launch_packs.launch(self.root, "retail-fixture",
                    self.workspace / "invented-disc.txt", headless=True, seconds=10,
                    fresh_user_data=True, profile="enhanced", controls_pause=requested,
                    controls_pause_version=version)
                command, kwargs = calls[-1]
                expected = (audio if version == "audio-v2" else variant) if requested else self.base
                self.assertEqual(command[0], expected["executable"]["path"])
                self.assertEqual(receipt["source_revision"], expected["source_revision"])
                env = kwargs["env"]
                self.assertEqual(env["GODHAND_PC_CONTROLS_PAUSE"], str(int(requested)))
                self.assertEqual(env["GODHAND_PC_CONTROLS_PROBE"], "0")
                self.assertEqual(env["GODHAND_CONTROLS_SELFTEST"], "0")
                self.assertNotIn("PS2X_STATE_LOAD_AT", env)
                self.assertEqual(receipt["controls_pause"]["requested"], requested)
                self.assertEqual(receipt["controls_pause"]["version"], (version or "v1") if requested else None)
                self.assertEqual(receipt["controls_pause"]["acknowledged_hold"], "not inferred from launch request")
            self.assertEqual(base_check.call_count, 1)
            self.assertEqual(variant_check.call_count, 2)
            self.assertEqual([call.args[2] for call in variant_check.call_args_list], ["v1", "audio-v2"])


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
