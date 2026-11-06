"""Only the authored diagnostic asset is created, never a game fixture."""
from pathlib import Path
import json
import tempfile
import unittest

import make_example_pack as example


class ExampleTests(unittest.TestCase):
    def test_original_example_is_exact_reproducible_and_never_overwritten(self):
        with tempfile.TemporaryDirectory(prefix="godhand-example-original-") as name:
            root = Path(name).resolve()
            assert root.is_relative_to(Path(tempfile.gettempdir()).resolve())
            result = example.create(root / "pack")
            self.assertEqual(result["bytes"], 8256)
            self.assertEqual(result["sha256"], "fe467079e9695b5832af4b79a383db7ae76bc704ab439c2e481ceb65a543c357")
            manifest = Path(result["manifest"])
            original = manifest.read_bytes()
            self.assertEqual(json.loads(original)["replacements"][0]["payload"], "magenta.raw")
            with self.assertRaises(ValueError):
                example.create(manifest.parent)
            self.assertEqual(original, manifest.read_bytes())


if __name__ == "__main__":
    unittest.main()
