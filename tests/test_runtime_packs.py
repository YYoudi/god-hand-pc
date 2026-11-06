"""Original source-transform fixtures, not upstream/game source snapshots."""
from pathlib import Path
import copy
import json
import tempfile
import unittest

import pc
import runtime_packs as r


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="godhand-integration-synthetic-")
        self.root = Path(self.temp.name).resolve()
        assert self.root.is_relative_to(Path(tempfile.gettempdir()).resolve())
        self.addCleanup(self.temp.cleanup)
        self.source = self.root / "source"
        self.tooling = self.root / "tooling"
        self.tooling.mkdir()
        (self.tooling / "upstream.json").write_text(json.dumps(pc.load_pin()), encoding="utf-8")

    def fixture(self):
        raw = b"Entirely invented source fixture.\n"
        result = raw + b"Original test addition.\n"
        files = []
        for name in sorted(r.MODIFIED):
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            files.append({"path": name, "before_sha256": r.sha(raw), "after_sha256": r.sha(result),
                          "edits": [{"start": len(raw), "end": len(raw), "insert": "Original test addition.\n"}]})
        for name in r.COPIES:
            path = self.tooling / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Original invented bridge fixture.\n", encoding="utf-8")
        recipe = {"schema": 1, "upstream_revision": pc.load_pin()["revision"],
                  "files": files, "copies": r.COPIES}
        (self.tooling / "adapter/integration.json").write_text(json.dumps(recipe), encoding="utf-8")
        return recipe, raw, result

    def test_public_recipe_only_selects_reviewed_host_paths(self):
        recipe = r.integration(pc.ROOT)
        self.assertEqual({x["path"] for x in recipe["files"]}, r.MODIFIED)
        self.assertFalse(any("generated" in x["path"].split("/") for x in recipe["files"]))

    def test_planning_is_read_only_and_all_outputs_are_contained(self):
        recipe, raw, expected = self.fixture()
        planned = r.plan_sources(self.source, self.tooling, recipe)
        self.assertEqual(len(planned), 9)
        for item in recipe["files"]:
            path = self.source / item["path"]
            self.assertEqual(path.read_bytes(), raw)
            self.assertEqual(planned[path], expected)
        self.assertTrue(all(p.is_relative_to(self.source) for p in planned))

    def test_final_wrong_preimage_does_not_partially_patch_earlier_files(self):
        recipe, raw, _ = self.fixture()
        last = self.source / recipe["files"][-1]["path"]
        last.write_text("Changed synthetic input", encoding="utf-8")
        with self.assertRaises(ValueError):
            r.plan_sources(self.source, self.tooling, recipe)
        self.assertEqual((self.source / recipe["files"][0]["path"]).read_bytes(), raw)

    def test_derived_hash_and_edit_bounds_are_enforced(self):
        recipe, raw, _ = self.fixture()
        record = recipe["files"][0]
        for edit in [{"start": -1, "end": 0, "insert": "x"},
                     {"start": True, "end": 1, "insert": "x"},
                     {"start": len(raw), "end": len(raw) + 1, "insert": "x"}]:
            bad = dict(record, edits=[edit])
            with self.assertRaises(ValueError):
                r.transform(raw, bad)
        with self.assertRaises(ValueError):
            r.transform(raw, dict(record, after_sha256="0" * 64))

    def test_overlapping_or_duplicate_edits_and_nuls_are_refused(self):
        recipe, raw, _ = self.fixture()
        record = recipe["files"][0]
        for edits in [[{"start": 0, "end": 4, "insert": "a"}, {"start": 3, "end": 6, "insert": "b"}],
                      [record["edits"][0]] * 2,
                      [{"start": 0, "end": 0, "insert": "\0"}]]:
            with self.assertRaises(ValueError):
                r.transform(raw, dict(record, edits=edits))

    def test_unreviewed_paths_missing_files_or_wrong_base_are_refused(self):
        recipe, _, _ = self.fixture()
        for mutation in ["path", "copies", "base"]:
            data = copy.deepcopy(recipe)
            if mutation == "path": data["files"][0]["path"] = "generated/forbidden.cpp"
            if mutation == "copies": data["copies"]["adapter/extra.hpp"] = "../escape.hpp"
            if mutation == "base": data["upstream_revision"] = "0" * 40
            (self.tooling / "adapter/integration.json").write_text(json.dumps(data), encoding="utf-8")
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                r.integration(self.tooling)

    def test_fingerprint_normalizes_eol_but_detects_source_changes(self):
        recipe, _, _ = self.fixture()
        first = r.fingerprint(self.tooling, recipe)
        path = self.tooling / next(iter(r.COPIES))
        path.write_bytes(r.normalized(path.read_bytes()).replace(b"\n", b"\r\n"))
        self.assertEqual(first, r.fingerprint(self.tooling, recipe))
        path.write_text("A changed original fixture.\n", encoding="utf-8")
        self.assertNotEqual(first, r.fingerprint(self.tooling, recipe))

    def test_existing_bridge_content_is_never_overwritten(self):
        recipe, _, _ = self.fixture()
        path = self.source / next(iter(r.COPIES.values()))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Preserve this earlier fixture.\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            r.plan_sources(self.source, self.tooling, recipe)
        self.assertEqual(path.read_text(), "Preserve this earlier fixture.\n")

    def test_workspace_name_cannot_escape_local_storage(self):
        for name in ["../outside", "retail-a/../b", "C:/outside", "prototype", "retail-..", "retail-a\\b"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                r.workspace_path(self.tooling, name)


if __name__ == "__main__":
    unittest.main()
