"""Only invented ISO metadata/pixels and our authored diagnostic, no game data."""
from pathlib import Path
import copy
import hashlib
import io
import json
import os
import struct
import tempfile
import unittest
from unittest.mock import patch

import hd_packs
import hd_reference
import resources
from test_resources import bank, tagged, fst, record, TARGET


def invented_disc(second_payload=None):
    header = bytearray(64); header[:8] = b"TIM3\x04\x06\x01\0"
    struct.pack_into("<IIIHHBBBBHH", header, 16, 48+8256, 64, 8192, 48, 16, 0, 1, 3, 4, 128, 128)
    payload = bytes((n*17+3)&255 for n in range(8192)) + bytes(c for n in range(16) for c in (n*11, n*7, n*3, 128))
    if second_payload is None:
        textures = bank(header+payload)
    else:
        assert len(second_payload) == len(payload)
        first = 48
        second = first + len(header) + len(payload)
        prefix = (b"TM3\0" + struct.pack("<I", 2) + bytes(8) +
                  struct.pack("<II", first, second) + b"first___second__" + bytes(8))
        assert len(prefix) == first and second % 16 == 0
        textures = prefix + header + payload + header + second_payload
    room = tagged(b"SCP\0", tagged(b"TM3\0", textures))
    archive = b"AFS\0"+struct.pack("<III", 1, 64, len(room))+bytes(48)+room
    data = bytearray(32*2048); pvd = bytearray(2048); pvd[:7] = b"\x01CD001\x01"
    struct.pack_into("<H", pvd, 128, 2048); struct.pack_into(">H", pvd, 130, 2048)
    rr = record(b"\0", 20, 2048, 2); pvd[156:156+len(rr)] = rr; data[16*2048:17*2048] = pvd
    namespace = fst()
    entries = record(b"\0", 20, 2048, 2)+record(b"\1", 20, 2048, 2)
    entries += record(b"GODHAND.FST;1", 21, len(namespace))+record(b"_DATA.AFS;1", 22, len(archive))
    data[20*2048:20*2048+len(entries)] = entries; data[21*2048:21*2048+len(namespace)] = namespace
    data[22*2048:22*2048+len(archive)] = archive
    return bytes(data), payload


class HDPackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="godhand-hd-pack-synthetic-"); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve(); self.pack = self.root/"pack"
        self.result = hd_packs.create_example(self.pack)
        self.manifest = self.pack/"pack.json"; self.data = json.loads(self.manifest.read_text())
        self.data["replacements"][0]["target"] = copy.deepcopy(TARGET); self.write()
        self.disc = self.root/"invented-disc.txt"; self.disc_bytes, self.source_pixels = invented_disc(); self.disc.write_bytes(self.disc_bytes)
        self.run = self.root/"run"; self.run.mkdir()

    def write(self): self.manifest.write_text(json.dumps(self.data), encoding="utf-8")

    def compile(self): return hd_packs.compile_pack(resources.Window(io.BytesIO(self.disc_bytes)), self.manifest)

    def protocol(self, **kwargs):
        result = hd_packs.protocol(self.disc, self.manifest, self.run, **kwargs)
        for name in ("hd-input.private-input", "hd-authored.rgba"):
            path = self.run/name
            if path.exists(): self.addCleanup(lambda p=path: p.chmod(0o666))
        return result

    def test_original_generator_and_named_reference_read_only(self):
        plan, rgba, blob = self.compile()
        self.assertEqual(rgba, hd_reference.example_rgba())
        self.assertEqual(blob[32:32+65536], hd_reference.expand(self.source_pixels))
        self.assertEqual(blob[32+65536:], rgba); self.assertEqual(plan["target"], TARGET)
        self.assertNotIn("reference", plan); self.assertEqual(self.disc.read_bytes(), self.disc_bytes)
        self.assertEqual(hashlib.sha256(rgba).hexdigest(), self.result["sha256"])

    def test_nonzero_named_image_selects_its_own_reference_without_changing_authored_pixels(self):
        second = bytes([0x22])*8192 + bytes(c for n in range(16) for c in (n*3+17,n*5+19,n*7+23,128))
        disc, first = invented_disc(second)
        self.disc_bytes = disc
        self.disc.write_bytes(disc)
        plans, refs, authored = [], [], []
        for image, expected in [(0,first),(1,second)]:
            self.data['replacements'][0]['target'] = {**TARGET,'image':image}; self.write()
            plan, rgba, blob = self.compile()
            plans.append(plan); refs.append(blob[32:32+65536]); authored.append(rgba)
            self.assertEqual(refs[-1],hd_reference.expand(expected))
            self.assertEqual(plan['target']['image'],image)
            self.assertEqual(blob[32+65536:],rgba)
        self.assertNotEqual(refs[0],refs[1]); self.assertEqual(authored[0],authored[1])
        self.assertNotEqual(plans[0]['source_metadata']['offset'],plans[1]['source_metadata']['offset'])
        self.assertEqual(self.disc.read_bytes(),disc)

    def test_outside_named_image_never_silently_selects_first_reference(self):
        disc, _ = invented_disc(bytes([41])*8256)
        self.disc_bytes = disc
        self.disc.write_bytes(disc)
        self.data['replacements'][0]['target'] = {**TARGET,'image':2}; self.write()
        with self.assertRaisesRegex(ValueError,'Ordinal'):
            self.compile()
        result, env = self.protocol()
        self.assertEqual(result['mode'],'original-fallback');self.assertEqual(set(env.values()),{''})
        self.assertFalse((self.run/'hd-input.private-input').exists())
        self.assertEqual(self.disc.read_bytes(),disc)

    def test_snapshot_is_immutable_without_user_file_rereads_or_original_disc_writes(self):
        result, env = self.protocol(strict=True)
        self.assertEqual(result["mode"], "replacement-planned"); self.assertIn("not inferred", result["rendered_change"])
        frozen = Path(result["private_input"]); original = frozen.read_bytes()
        (self.pack/"authored.rgba").write_bytes(bytes([31])*(512*512*4))
        self.assertEqual(frozen.read_bytes(), original)
        self.assertEqual(env["GODHAND_PC_HD_SHA256"], hashlib.sha256(original).hexdigest())
        self.assertEqual(self.disc.read_bytes(), self.disc_bytes)

    def test_absent_pack_never_opens_disc_and_overrides_stale_native_configuration(self):
        with patch.object(Path, "open", side_effect=AssertionError("must not read")):
            result, env = hd_packs.protocol(self.root/"absent", None, self.run)
        self.assertEqual(result, {"mode": "original"}); self.assertEqual(set(env.values()), {""}); self.assertEqual(len(env), 3)
        with self.assertRaises(ValueError): hd_packs.protocol(self.disc, None, self.run, strict=True)

    def test_bad_image_hash_fallback_and_strict_refusal_never_create_native_input(self):
        self.data["replacements"][0]["image"]["sha256"] = "0"*64; self.write()
        result, env = self.protocol(); self.assertEqual(result["mode"], "original-fallback"); self.assertEqual(set(env.values()), {""})
        self.assertFalse((self.run/"hd-input.private-input").exists())
        with self.assertRaisesRegex(ValueError, "strict"): self.protocol(strict=True)

    def test_unknown_duplicate_and_wrong_kind_profile_fields_are_refused(self):
        original = copy.deepcopy(self.data)
        for key, value in [("schema", True), ("kind", "same-size"), ("profile", "prototype"), ("unknown", 1)]:
            self.data = copy.deepcopy(original); self.data[key] = value; self.write()
            with self.assertRaises(ValueError): self.compile()
        self.manifest.write_text('{"schema":1,"schema":1}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate"): self.compile()

    def test_unsafe_paths_and_unsupported_dimensions_formats_lengths_are_refused(self):
        original = copy.deepcopy(self.data)
        for key, values in {"path": ["../outside", "/absolute", "C:/outside", "a\\b", ""],
                            "width": [True, 128, 129, 4096], "height": [0, 2049], "format": ["png", "rgba8"],
                            "sha256": ["Z"*64, None]}.items():
            for value in values:
                self.data = copy.deepcopy(original); self.data["replacements"][0]["image"][key] = value; self.write()
                with self.subTest(key=key, value=value), self.assertRaises((ValueError, OSError)): self.compile()
        self.data = original; self.write(); (self.pack/"authored.rgba").write_bytes(b"short")
        with self.assertRaises(ValueError): self.compile()

    def test_symlink_escape_is_refused(self):
        outside = self.root/"outside.rgba"; outside.write_bytes(hd_reference.example_rgba())
        link = self.pack/"link.rgba"
        try: link.symlink_to(outside)
        except OSError: self.skipTest("Symlink privilege not available")
        self.data["replacements"][0]["image"]["path"] = link.name; self.write()
        with self.assertRaisesRegex(ValueError, "escapes"): self.compile()

    def test_payload_growth_is_bounded_and_not_silently_frozen(self):
        original_open = Path.open
        image = self.pack/"authored.rgba"
        class Growing(io.BytesIO):
            def read(self, size=-1):
                self_outer.assertEqual(size, 512*512*4+1)
                return super().read(size)
        self_outer = self
        def open_file(path, *args, **kwargs):
            if path == image: return Growing(hd_reference.example_rgba()+b"unexpected tail")
            return original_open(path, *args, **kwargs)
        with patch.object(Path, "open", open_file), self.assertRaisesRegex(ValueError, "changed"):
            self.compile()

    def test_existing_snapshots_and_example_outputs_are_never_overwritten(self):
        path = self.run/"hd-authored.rgba"; path.write_bytes(b"Preserve this existing file")
        result, env = self.protocol(); self.assertEqual(result["mode"], "original-fallback")
        self.assertEqual(path.read_bytes(), b"Preserve this existing file"); self.assertEqual(set(env.values()), {""})
        with self.assertRaises(ValueError): hd_packs.create_example(self.pack)


if __name__ == "__main__": unittest.main()
