"""Invented editor revisions and real threads; no native UI, process or disc."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

import video_settings as video


class VideoRevisionGuardTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="godhand-video-editor-synthetic-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.name = "retail-invented"
        self.workspace = self.root / ".local" / self.name
        self.workspace.mkdir(parents=True)
        self.storage = self.workspace / "userdata/video"

    def snapshot(self):
        return {p.name: p.read_bytes() for p in self.storage.iterdir()}

    def test_missing_base_can_only_create_while_still_absent(self):
        first = video.update(self.root, self.name, 2, expected_revision=None)
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "changed since selection"):
            video.update(self.root, self.name, 3, expected_revision=None)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(video.show(self.root, self.name), first)

    def test_matching_snapshot_commits_then_requires_its_new_revision(self):
        first = video.update(self.root, self.name, 2)
        second = video.update(self.root, self.name, 3, expected_revision=first["sha256"])
        self.assertEqual(second["settings"]["previous"], first["sha256"])
        reset = video.update(self.root, self.name, None, expected_revision=second["sha256"])
        self.assertIsNone(reset["settings"]["native_scale"])
        self.assertEqual(reset["settings"]["previous"], second["sha256"])

    def test_external_cli_edit_is_not_overwritten_by_a_stale_menu_snapshot(self):
        selected = video.update(self.root, self.name, 2)
        external = video.update(self.root, self.name, 4)
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "reload before saving"):
            video.update(self.root, self.name, 3, expected_revision=selected["sha256"])
        self.assertEqual(video.show(self.root, self.name), external)
        self.assertEqual(self.snapshot(), before)

    def test_invalid_revision_types_and_paths_refuse_before_storage_work(self):
        for revision in [False, 1, b"a"*64, "../outside", "A"*64, "a"*63, {}, []]:
            with self.subTest(revision=revision), patch.object(video, "_storage") as storage:
                with self.assertRaises(ValueError):
                    video.update(self.root, self.name, 2, expected_revision=revision)
                storage.assert_not_called()

    def test_two_real_writers_from_one_revision_cannot_both_commit(self):
        selected = video.update(self.root, self.name, 2)
        barrier = threading.Barrier(2)

        def attempt(scale):
            barrier.wait(timeout=5)
            try:
                return video.update(self.root, self.name, scale, expected_revision=selected["sha256"])
            except (OSError, ValueError) as error:
                # Either the cooperative lock refuses first, or the hash compare
                # refuses after the winner released it; neither is a retry.
                return {"refused": str(error)}

        with ThreadPoolExecutor(max_workers=2) as workers:
            results = list(workers.map(attempt, [3, 4]))
        winners = [r for r in results if "sha256" in r]
        self.assertEqual(len(winners), 1)
        self.assertEqual(video.show(self.root, self.name), winners[0])
        self.assertEqual(winners[0]["settings"]["previous"], selected["sha256"])
        self.assertEqual(len(list(self.storage.glob("*.json"))), 3)  # two revisions + pointer
        self.assertFalse((self.storage / "write.lock").exists())

    def test_compare_happens_after_lock_and_before_any_revision_write(self):
        selected = video.update(self.root, self.name, 2)
        original = video._current
        observed = []

        def locked_current(storage):
            observed.append((storage / "write.lock").exists())
            return original(storage)

        before = self.snapshot()
        with patch.object(video, "_current", side_effect=locked_current):
            with self.assertRaises(ValueError):
                video.update(self.root, self.name, 3, expected_revision="0"*64)
        self.assertEqual(observed, [True])
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(video.show(self.root, self.name), selected)
