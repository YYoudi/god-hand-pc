"""Invented metadata/files only; no native, game pixels or game preferences."""
from pathlib import Path
import hashlib
import json
import os
import tempfile
import unittest
from unittest.mock import patch

import video_settings as video


class VideoSettingsTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="godhand-video-synthetic-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.name = "retail-invented"
        self.workspace = self.root / ".local" / self.name
        self.workspace.mkdir(parents=True)
        self.storage = self.workspace / "userdata/video"
        self.run = self.root / "invented-run"
        self.run.mkdir()

    def select(self, scale=2):
        return video.update(self.root, self.name, scale)

    def test_new_process_style_reload_reset_and_immutable_history(self):
        first = self.select()
        raw = Path(first["path"]).read_bytes()
        self.assertEqual(video.show(self.root, self.name), first)
        second = self.select(3)
        reset = self.select(None)
        self.assertEqual(second["settings"]["previous"], first["sha256"])
        self.assertEqual(reset["settings"]["previous"], second["sha256"])
        self.assertIsNone(video.show(self.root, self.name)["settings"]["native_scale"])
        self.assertEqual(Path(first["path"]).read_bytes(), raw)
        self.assertEqual(len(list(self.storage.glob("[0-9a-f]" * 64 + ".json"))), 3)

    def test_scale_bounds_types_and_unknown_capabilities_refuse_before_write(self):
        for scale in [True, False, 0, 9, -1, 1.0, "2", {}, [], float("nan")]:
            with self.subTest(scale=scale), self.assertRaises(ValueError):
                self.select(scale)
        self.assertFalse(self.storage.exists())
        for scale in [1, 8]:
            self.assertEqual(self.select(scale)["settings"]["native_scale"], scale)

    def test_explicit_protocol_freezes_exact_selected_revision_and_safe_env_only(self):
        first = self.select()
        record, env = video.protocol(self.root, self.name, self.run)
        self.assertEqual(env, {"PS2X_GS_RENDERER": "native", "PS2X_GS_SCALE": "2"})
        self.assertEqual(record["requested_native_scale"], 2)
        self.assertIn("not inferred", record["effective_scale"])
        frozen = Path(record["frozen_path"])
        self.assertEqual(frozen.read_bytes(), Path(first["path"]).read_bytes())
        self.select(3)
        self.assertEqual(hashlib.sha256(frozen.read_bytes()).hexdigest(), first["sha256"])

    def test_reset_does_not_force_renderer_scale_or_hardcoded_ini_baseline(self):
        self.select(None)
        record, env = video.protocol(self.root, self.name, self.run)
        self.assertEqual(env, {})
        self.assertEqual(record["mode"], "upstream-ini")
        self.assertTrue(record["requires_restart"])

    def test_missing_explicit_selection_refuses(self):
        with self.assertRaises(OSError): video.protocol(self.root, self.name, self.run)
        self.storage.mkdir(parents=True)
        self.assertIsNone(video.show(self.root, self.name))
        with self.assertRaises(ValueError): video.protocol(self.root, self.name, self.run)
        self.assertFalse((self.run / "video-settings.json").exists())

    def test_malformed_duplicate_unknown_nonfinite_pointer_and_revision_refuse(self):
        self.select()
        pointer = self.storage / "current.json"
        original = pointer.read_bytes()
        for raw in [b'{"schema":1,"schema":1,"sha256":"' + b"a"*64 + b'"}',
                    b'{"schema":1,"sha256":"../outside"}', b'{}', b'[]', b'{"schema":NaN}', b'\xff']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                pointer.write_bytes(raw)
                video.show(self.root, self.name)
        pointer.write_bytes(original)
        for raw in [b'{"schema":1,"native_scale":true,"previous":null}',
                    b'{"schema":1,"native_scale":2,"previous":null,"PS2X_DUMP":"1"}',
                    b'{"schema":1,"native_scale":2,"native_scale":3,"previous":null}',
                    b'{"schema":1,"native_scale":Infinity,"previous":null}',
                    b'{"schema":1,"native_scale":2,"previous":"../no"}']:
            digest = hashlib.sha256(raw).hexdigest()
            (self.storage / (digest + ".json")).write_bytes(raw)
            pointer.write_text(json.dumps({"schema": 1, "sha256": digest}))
            with self.subTest(raw=raw), self.assertRaises(ValueError): video.show(self.root, self.name)

    def test_tampered_oversized_and_directory_files_refuse_without_repair(self):
        first = self.select()
        path = Path(first["path"])
        original = path.read_bytes()
        for raw in [original + b" ", b"x" * (video.LIMIT + 1)]:
            path.write_bytes(raw)
            with self.assertRaises(ValueError): video.show(self.root, self.name)
            self.assertEqual(path.read_bytes(), raw)
        path.unlink(); path.mkdir()
        with self.assertRaises(ValueError): video.show(self.root, self.name)

    def test_stale_lock_refuses_show_and_write_without_stealing(self):
        first = self.select()
        lock = self.storage / "write.lock"
        lock.write_bytes(b"invented stale writer\n")
        with self.assertRaises(ValueError): video.show(self.root, self.name)
        with self.assertRaises(OSError): self.select(3)
        self.assertEqual(lock.read_bytes(), b"invented stale writer\n")
        self.assertTrue(Path(first["path"]).exists())

    def test_atomic_pointer_failure_preserves_old_settings_and_new_evidence(self):
        first = self.select()
        with patch.object(video.os, "replace", side_effect=OSError("invented replace failure")):
            with self.assertRaises(OSError): self.select(3)
        self.assertEqual(video.show(self.root, self.name), first)
        self.assertEqual(len(list(self.storage.glob("pending-*.json"))), 1)
        self.assertFalse((self.storage / "write.lock").exists())

    def test_hardlink_pointer_refuses_without_changing_source(self):
        self.select()
        pointer = self.storage / "current.json"
        owner = self.root / "invented-owner.txt"
        owner.write_bytes(pointer.read_bytes())
        pointer.unlink()
        try: os.link(owner, pointer)
        except OSError as error: self.skipTest(str(error))
        original = owner.read_bytes()
        with self.assertRaises(ValueError): self.select(3)
        self.assertEqual(owner.read_bytes(), original)

    def test_directory_alias_refuses_even_if_inside_workspace(self):
        target = self.workspace / "invented-real-user"
        (target / "video").mkdir(parents=True)
        try: (self.workspace / "userdata").symlink_to(target, target_is_directory=True)
        except OSError as error: self.skipTest(str(error))
        with self.assertRaises(ValueError): self.select()
        self.assertEqual(list((target / "video").iterdir()), [])

    def test_missing_workspace_and_path_traversal_never_create_user_data(self):
        for name in ["retail-missing", "../escape", "retail-../other", "retail-\\bad"]:
            with self.subTest(name=name), self.assertRaises((ValueError, OSError)):
                video.update(self.root, name, 2)
        self.assertFalse(self.storage.exists())
