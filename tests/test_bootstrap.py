"""Original synthetic tooling tests: temporary text files/Git, never a game disc."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest

import pc

spec = importlib.util.spec_from_file_location("guard", pc.ROOT / "scripts/check_public_tree.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="godhand-tooling-test-")
        self.root = Path(self.temporary.name).resolve()
        assert self.root.is_relative_to(Path(tempfile.gettempdir()).resolve())
        self.addCleanup(self.temporary.cleanup)

    def make_repo(self):
        repo = self.root / "source"
        repo.mkdir()
        subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
        (repo / "note.txt").write_text("Original synthetic fixture.\n", encoding="utf-8")
        pc.git("add", "note.txt", cwd=repo)
        pc.git("-c", "user.name=Synthetic Tooling Test", "-c",
               "user.email=test@example.invalid", "commit", "-m", "Synthetic fixture", cwd=repo)
        return repo, pc.git("rev-parse", "HEAD", cwd=repo)

    def test_real_manifest_is_pinned(self):
        self.assertEqual(len(pc.load_pin()["revision"]), 40)

    def test_manifest_rejects_unreviewed_repository(self):
        data = pc.load_pin()
        data["repository"] = "https://example.invalid/unreviewed.git"
        (self.root / "upstream.json").write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(ValueError):
            pc.load_pin(self.root)

    def test_manifest_rejects_moving_reference(self):
        data = pc.load_pin()
        data["revision"] = "main"
        (self.root / "upstream.json").write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaises(ValueError):
            pc.load_pin(self.root)

    def test_synthetic_disc_verification_does_not_change_file(self):
        p = self.root / "synthetic.txt"
        p.write_bytes(b"Original synthetic bytes, not game data.")
        before = p.read_bytes()
        profile = {"bytes": len(before), "sha256": hashlib.sha256(before).hexdigest()}
        self.assertEqual(pc.verify_disc(p, profile)["sha256"], profile["sha256"])
        self.assertEqual(p.read_bytes(), before)

    def test_wrong_disc_size_is_refused(self):
        p = self.root / "synthetic.txt"
        p.write_bytes(b"synthetic")
        with self.assertRaises(ValueError):
            pc.verify_disc(p, {"bytes": 1, "sha256": "0" * 64})

    def test_wrong_disc_hash_is_refused(self):
        p = self.root / "synthetic.txt"
        p.write_bytes(b"synthetic")
        with self.assertRaises(ValueError):
            pc.verify_disc(p, {"bytes": 9, "sha256": "0" * 64})

    def test_clean_checkout_is_recorded(self):
        repo, rev = self.make_repo()
        self.assertEqual(pc.inspect_checkout(repo, rev, rev)["revision"], rev)

    def test_dirty_tracked_source_is_refused(self):
        repo, rev = self.make_repo()
        (repo / "note.txt").write_text("changed", encoding="utf-8")
        with self.assertRaises(ValueError):
            pc.inspect_checkout(repo, rev, rev)

    def test_untracked_nonignored_source_is_refused(self):
        repo, rev = self.make_repo()
        (repo / "unreviewed.cpp").write_text("original but unreviewed", encoding="utf-8")
        with self.assertRaises(ValueError):
            pc.inspect_checkout(repo, rev, rev)

    def test_revision_mismatch_is_refused(self):
        repo, rev = self.make_repo()
        with self.assertRaises(ValueError):
            pc.inspect_checkout(repo, rev, "0" * 40)

    def test_original_synthetic_repository_fetch_and_reuse(self):
        repo, rev = self.make_repo()
        target = self.root / "clone"
        first = pc.clone_pinned(str(repo), rev, target)
        second = pc.clone_pinned(str(repo), rev, target)
        self.assertEqual(first, second)
        self.assertEqual((target / "note.txt").read_bytes(), (repo / "note.txt").read_bytes())

    def test_checkout_registration_cannot_replace_another(self):
        record = {"checkout": "original", "revision": "a" * 40}
        pc.store_checkout(record, self.root)
        p = self.root / ".local/checkout.json"
        original = p.read_bytes()
        pc.store_checkout(record, self.root)
        with self.assertRaises(ValueError):
            pc.store_checkout({"checkout": "different"}, self.root)
        self.assertEqual(p.read_bytes(), original)

    def test_public_paths_accept_original_tooling(self):
        guard.validate_paths(["pc.py"], {"pc.py"})

    def test_public_paths_refuse_unknown_and_traversal(self):
        for name in ["unknown.py", "../pc.py", "/pc.py", "folder\\pc.py"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                guard.validate_paths([name], {"pc.py"})

    def test_public_paths_refuse_game_files_even_if_allowlisted(self):
        for name in ["game.iso", "BOOT.ELF", "game.afs", "generated.bin", "card.ps2", "runtime.exe"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                guard.validate_paths([name], {name})


if __name__ == "__main__":
    unittest.main()
