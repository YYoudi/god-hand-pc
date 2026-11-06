"""Original orchestration fixtures; no network, compiler or game input."""
from pathlib import Path
import copy
import hashlib
import json
import sys
import tempfile
import unittest

import pc
import setup_pc as s


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="godhand-setup-synthetic-")
        self.root = Path(self.temp.name).resolve()
        assert self.root.is_relative_to(Path(tempfile.gettempdir()).resolve())
        self.addCleanup(self.temp.cleanup)

    def lock_copy(self):
        data = json.loads((pc.ROOT / "dependencies.json").read_text(encoding="utf-8"))
        (self.root / "dependencies.json").write_text(json.dumps(data), encoding="utf-8")
        return data

    def save_lock(self, data):
        (self.root / "dependencies.json").write_text(json.dumps(data), encoding="utf-8")

    def test_actual_dependency_lock_is_exact_and_complete(self):
        dependencies = s.load_dependencies(pc.ROOT)
        self.assertEqual(len(dependencies), 8)
        self.assertTrue(all(len(x["revision"]) == 40 for x in dependencies))

    def test_dependency_duplicates_and_missing_sources_fail(self):
        data = self.lock_copy()
        data["dependencies"].append(copy.deepcopy(data["dependencies"][0]))
        self.save_lock(data)
        with self.assertRaises(ValueError):
            s.load_dependencies(self.root)
        data["dependencies"] = data["dependencies"][:1]
        self.save_lock(data)
        with self.assertRaises(ValueError):
            s.load_dependencies(self.root)

    def test_dependency_moving_references_and_foreign_hosts_fail(self):
        for change in ({"revision": "main"}, {"repository": "https://example.invalid/repo.git"},
                       {"name": "../escape"}):
            data = self.lock_copy()
            data["dependencies"][0].update(change)
            self.save_lock(data)
            with self.subTest(change=change), self.assertRaises(ValueError):
                s.load_dependencies(self.root)

    def test_license_path_and_digest_are_bounded(self):
        for change in ({"file": "../LICENSE"}, {"file": ".."}, {"sha256": "not-a-digest"}):
            data = self.lock_copy()
            data["dependencies"][0]["license"].update(change)
            self.save_lock(data)
            with self.subTest(change=change), self.assertRaises(ValueError):
                s.load_dependencies(self.root)

    def test_containment_never_accepts_root_or_parent(self):
        self.assertEqual(s.contained(self.root, self.root / "child"), self.root / "child")
        for target in [self.root, self.root.parent, self.root / "../outside"]:
            with self.assertRaises(ValueError):
                s.contained(self.root, target)

    def test_private_disc_copy_is_separate_verified_and_original_unchanged(self):
        original = self.root / "invented-disc.txt"
        original.write_bytes(b"Entirely invented read-only-copy fixture.")
        profile = {"bytes": original.stat().st_size, "sha256": s.digest(original)}
        destination = self.root / "private" / "copy.txt"
        result = s.cached_disc(original, destination, profile, pc.verify_disc)
        self.addCleanup(lambda: destination.chmod(0o666))
        self.assertEqual(result["sha256"], profile["sha256"])
        self.assertFalse(destination.samefile(original))
        self.assertEqual(s.digest(original), profile["sha256"])
        s.cached_disc(original, destination, profile, pc.verify_disc)

    def test_private_copy_never_aliases_original_or_overwrites_partial(self):
        original = self.root / "invented.txt"
        original.write_bytes(b"invented complete input")
        profile = {"bytes": original.stat().st_size, "sha256": s.digest(original)}
        with self.assertRaises(ValueError):
            s.cached_disc(original, original, profile, pc.verify_disc)
        partial = self.root / "partial.txt"
        partial.write_bytes(b"unfinished")
        with self.assertRaises(ValueError):
            s.cached_disc(original, partial, profile, pc.verify_disc)
        self.assertEqual(partial.read_bytes(), b"unfinished")

    def test_build_plan_orders_global_iso_option_correctly(self):
        steps = s.build_steps(self.root / "checkout", self.root / "a space.iso")
        self.assertEqual([x[0] for x in steps], ["boot-generate", "overlay-extract", "overlay-link",
                                               "overlay-generate", "game-build"])
        argv = steps[1][1]
        self.assertLess(argv.index("--iso"), argv.index("extract"))
        self.assertEqual(argv[argv.index("--iso") + 1], str(self.root / "a space.iso"))
        self.assertTrue(all(argv[:2] == [sys.executable, "-I"] for _, argv in steps))

    def test_run_logs_real_synthetic_child_exit(self):
        run = s.Run(self.root)
        run.step("invented", [sys.executable, "-c", "print('original synthetic child')"],
                 self.root, None)
        receipt = json.loads((run.directory / "receipt.json").read_text())
        self.assertEqual(receipt["steps"][0]["exit"], 0)
        self.assertEqual(receipt["steps"][0]["status"], "terminal")
        self.assertIn("original synthetic child", (run.directory / "invented.log").read_text())

    def test_run_retains_failure_and_creates_new_evidence_on_retry(self):
        first = s.Run(self.root)
        with self.assertRaises(ValueError):
            first.step("invented", [sys.executable, "-c", "raise SystemExit(7)"], self.root, None)
        original = (first.directory / "receipt.json").read_bytes()
        self.assertEqual(first.record["steps"][0]["exit"], 7)
        second = s.Run(self.root)
        self.assertNotEqual(first.directory, second.directory)
        self.assertEqual((first.directory / "receipt.json").read_bytes(), original)

    def test_zero_process_exit_is_not_zero_generation_errors(self):
        source = self.root / "invented.log"
        # Entirely invented output, not a pasted game-recompiler diagnostic.
        raw = b"Unhandled instructions: 2\nWarnings: 3, errors: 2\n[error] invented unsupported operation\nProcess finished\n"
        source.write_bytes(raw)
        destination = self.root / "evidence" / "generation.log"
        result = s.generation_diagnostics(source, destination)
        self.assertEqual((result["warnings"], result["errors"], result["unhandled"]), (3, 2, 2))
        self.assertEqual(destination.read_bytes(), raw)
        self.assertEqual(result["sha256"], hashlib.sha256(raw).hexdigest())
        with self.assertRaises(FileExistsError):
            s.generation_diagnostics(source, destination)

    def test_ambiguous_or_missing_generation_summaries_are_refused(self):
        source = self.root / "invented.log"
        for text in ["Process finished", "Warnings: 0, errors: 0\n",
                     "Unhandled instructions: 0\nWarnings: 0, errors: 0\nWarnings: 0, errors: 0\n"]:
            source.write_text(text, encoding="utf-8")
            with self.subTest(text=text), self.assertRaises(ValueError):
                s.generation_diagnostics(source, self.root / "not-written.log")
        self.assertFalse((self.root / "not-written.log").exists())

    def invented_overlays(self):
        folder = self.root / "build/snr2/rel"
        folder.mkdir(parents=True)
        items = []
        for index in range(81):
            name = f"fixture{index:03}.rel"
            content = f"Original invented overlay fixture {index}\n".encode()
            (folder / name).write_bytes(content)
            items.append({"name": name, "size": len(content),
                          "sha256": hashlib.sha256(content).hexdigest()})
        manifest = folder / "manifest.json"
        manifest.write_text(json.dumps(items), encoding="utf-8")
        return manifest, items

    def test_all_invented_overlay_files_are_verified_not_just_counted(self):
        _, items = self.invented_overlays()
        self.assertEqual(len(s.overlay_manifest(self.root)), 81)
        (self.root / "build/snr2/rel" / items[-1]["name"]).write_bytes(b"modified")
        with self.assertRaises(ValueError):
            s.overlay_manifest(self.root)

    def test_missing_duplicate_or_escaping_overlay_is_refused(self):
        manifest, items = self.invented_overlays()
        for wrong in [items[:80], [items[0]] * 81,
                      [dict(items[0], name="../outside.rel"), *items[1:]]]:
            manifest.write_text(json.dumps(wrong), encoding="utf-8")
            with self.subTest(first=wrong[0]["name"]), self.assertRaises(ValueError):
                s.overlay_manifest(self.root)


if __name__ == "__main__":
    unittest.main()
