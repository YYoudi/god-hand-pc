"""Original invented ISO/pack fixtures; launcher tests never execute a game."""
from pathlib import Path
import copy
import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import launch_packs as l
from test_resources import invented_disc, TARGET


class LaunchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="godhand-launch-synthetic-")
        self.root = Path(self.temp.name).resolve()
        assert self.root.is_relative_to(Path(tempfile.gettempdir()).resolve())
        self.addCleanup(self.temp.cleanup)
        (self.root / "upstream.json").write_text(json.dumps(l.pc.load_pin()), encoding="utf-8")
        self.disc = self.root / "invented-disc.txt"
        self.disc.write_bytes(invented_disc())
        self.payload = self.root / "original.txt"
        self.payload.write_bytes(bytes([93]) * 96)
        self.manifest = self.root / "pack.json"
        self.data = {"schema": 1, "profile": "retail-us-slus-21503", "replacements": [
            {"target": copy.deepcopy(TARGET), "payload": self.payload.name,
             "sha256": hashlib.sha256(self.payload.read_bytes()).hexdigest()}]}
        self.run = self.root / "run"
        self.run.mkdir()

    def write(self):
        self.manifest.write_text(json.dumps(self.data), encoding="utf-8")

    def test_unrelated_and_legacy_runtime_environment_cannot_leak(self):
        environment = {"PATH": "original", "GODHAND_PC_TEXTURE_FILE": "stale",
                       "GODHAND_EVAL_TEXTURE_FILE": "stale", "PS2X_STATE_LOAD_AT": "stale"}
        self.assertEqual(l.clean_environment(environment), {"PATH": "original"})

    def test_no_pack_never_reads_a_disc_or_sets_native_override(self):
        record, env = l.pack_protocol(self.root / "absent", None, self.run)
        self.assertEqual(record["mode"], "original")
        self.assertEqual(env, {})

    def test_named_plan_is_frozen_without_extracting_original_pixels(self):
        self.write()
        original_disc = self.disc.read_bytes()
        record, env = l.pack_protocol(self.disc, self.manifest, self.run)
        self.assertEqual(record["mode"], "replacement")
        frozen = Path(record["frozen_payload"])
        self.addCleanup(lambda: frozen.chmod(0o666))
        self.assertEqual(frozen.read_bytes(), self.payload.read_bytes())
        self.payload.write_bytes(bytes([24]) * 96)
        self.assertNotEqual(frozen.read_bytes(), self.payload.read_bytes())
        self.assertEqual(env["GODHAND_PC_TEXTURE_SIZE"], "96")
        self.assertEqual(self.disc.read_bytes(), original_disc)
        self.assertEqual(len(env), 5)

    def test_invalid_digest_uses_original_assets_without_stale_environment(self):
        self.data["replacements"][0]["sha256"] = "0" * 64
        self.write()
        record, env = l.pack_protocol(self.disc, self.manifest, self.run)
        self.assertEqual(record["mode"], "original-fallback")
        self.assertIn("hash", record["error"].lower())
        self.assertEqual(env, {})
        self.assertFalse((self.run / "texture.raw").exists())

    def test_wrong_profile_and_missing_pack_fall_back_but_strict_refuses(self):
        self.data["profile"] = "prototype"
        self.write()
        for path in [self.manifest, self.root / "missing.json"]:
            record, env = l.pack_protocol(self.disc, path, self.run)
            self.assertEqual(record["mode"], "original-fallback")
            self.assertEqual(env, {})
            with self.assertRaises(ValueError):
                l.pack_protocol(self.disc, path, self.run, strict=True)

    def test_invalid_disc_never_enters_pack_fallback_or_spawns(self):
        with patch.object(l, "os", SimpleNamespace(name="nt")), \
             patch.object(l.runtime_packs, "verified_install", return_value={}), \
             patch.object(l.pc, "verify_disc", side_effect=ValueError("invented wrong disc")), \
             patch.object(l, "pack_protocol") as pack, patch.object(l.subprocess, "Popen") as child:
            with self.assertRaises(ValueError):
                l.launch(self.root, "retail-test", self.disc, self.manifest, headless=True, seconds=10)
            pack.assert_not_called()
            child.assert_not_called()

    def test_invalid_runtime_identity_never_enters_pack_fallback_or_spawns(self):
        with patch.object(l, "os", SimpleNamespace(name="nt")), \
             patch.object(l.runtime_packs, "verified_install", side_effect=ValueError("invented wrong runtime")), \
             patch.object(l, "pack_protocol") as pack, patch.object(l.subprocess, "Popen") as child:
            with self.assertRaises(ValueError):
                l.launch(self.root, "retail-test", self.disc, self.manifest, headless=True, seconds=10)
            pack.assert_not_called()
            child.assert_not_called()

    def test_headless_without_deadline_or_invalid_limits_never_spawn(self):
        with patch.object(l, "os", SimpleNamespace(name="nt")), patch.object(l.subprocess, "Popen") as child:
            for seconds in [None, 0, 601, True]:
                with self.subTest(seconds=seconds), self.assertRaises(ValueError):
                    l.launch(self.root, "retail-test", self.disc, headless=True, seconds=seconds)
            child.assert_not_called()


if __name__ == "__main__":
    unittest.main()
