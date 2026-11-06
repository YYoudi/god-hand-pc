"""Entirely invented ISO/container/texture bytes. No game input or game pixels."""
from pathlib import Path
import copy
import hashlib
import io
import json
import struct
import tempfile
import unittest

import resources as r


def put32(data, at, value):
    struct.pack_into("<I", data, at, value)


def tim3():
    h = bytearray(64)
    h[:8] = b"TIM3\x04\0\x01\0"
    struct.pack_into("<IIIHHBBBBHH", h, 16, 144, 64, 32, 48, 16, 0, 1, 3, 4, 8, 8)
    return h + bytes(range(32)) + bytes([7]) * 64


def bank(image):
    return b"TM3\0" + struct.pack("<I", 1) + bytes(8) + struct.pack("<I", 32) + bytes(4) + b"invented" + image


def tagged(tag, payload):
    return struct.pack("<II", 1, 16) + tag + bytes(4) + payload


def fst():
    pool = b"demo\0room.dat\0"
    rows = [(1, 0, 24), (3, 0, 0), (2, 5, 0), (3, 0, 0)]
    return b"FST\0\0\0\x80\x3f" + struct.pack("<II", 16, 16 + len(pool)) + pool + b"".join(struct.pack("<III", *row) for row in rows)


def record(name, lba, size, flags=0):
    h = bytearray(33 + len(name) + (0 if len(name) % 2 else 1))
    h[0] = len(h)
    struct.pack_into("<I", h, 2, lba)
    struct.pack_into(">I", h, 6, lba)
    struct.pack_into("<I", h, 10, size)
    struct.pack_into(">I", h, 14, size)
    h[25], h[32] = flags, len(name)
    h[33:33 + len(name)] = name
    return h


def invented_disc():
    room = tagged(b"SCP\0", tagged(b"TM3\0", bank(tim3())))
    archive = b"AFS\0" + struct.pack("<III", 1, 64, len(room)) + bytes(48) + room
    namespace = fst()
    d = bytearray(24 * 2048)
    pvd = bytearray(2048)
    pvd[:7] = b"\x01CD001\x01"
    struct.pack_into("<H", pvd, 128, 2048)
    struct.pack_into(">H", pvd, 130, 2048)
    root_record = record(b"\0", 20, 2048, 2)
    pvd[156:156 + len(root_record)] = root_record
    d[16 * 2048:17 * 2048] = pvd
    directory = record(b"\0", 20, 2048, 2) + record(b"\1", 20, 2048, 2)
    directory += record(b"GODHAND.FST;1", 21, len(namespace))
    directory += record(b"_DATA.AFS;1", 22, len(archive))
    d[20 * 2048:20 * 2048 + len(directory)] = directory
    d[21 * 2048:21 * 2048 + len(namespace)] = namespace
    d[22 * 2048:22 * 2048 + len(archive)] = archive
    return d


TARGET = {"path": "demo/room.dat", "scp": 0, "bank": 0, "image": 0}
PIXEL_AT = 22 * 2048 + 64 + 16 + 16 + 32 + 64


class CountingSource(io.BytesIO):
    def __init__(self, data):
        super().__init__(data)
        self.reads = []

    def read(self, size=-1):
        self.reads.append((self.tell(), size))
        return super().read(size)


class ResourceTests(unittest.TestCase):
    def test_full_invented_named_resolution(self):
        stream = CountingSource(invented_disc())
        found = r.resolve_texture(r.Window(stream), TARGET)
        self.assertEqual(found, r.TextureTarget(PIXEL_AT, 96, 8, 8, 4, 0, 0))
        self.assertTrue(all(at + n <= PIXEL_AT or at >= PIXEL_AT + 96 for at, n in stream.reads))
        self.assertLess(sum(n for _, n in stream.reads), 10000)

    def test_invalid_iso_descriptor(self):
        data = invented_disc()
        data[16 * 2048] = 2
        with self.assertRaises(ValueError):
            r.iso_root(r.Window(io.BytesIO(data)))

    def test_iso_endian_mismatch(self):
        data = invented_disc()
        data[16 * 2048 + 162] ^= 1
        with self.assertRaises(ValueError):
            r.iso_root(r.Window(io.BytesIO(data)))

    def test_iso_wrong_sector_size(self):
        data = invented_disc()
        struct.pack_into("<H", data, 16 * 2048 + 128, 512)
        with self.assertRaises(ValueError):
            r.iso_root(r.Window(io.BytesIO(data)))

    def test_multi_extent_is_refused(self):
        data = invented_disc()
        data[20 * 2048 + 2 * 34 + 25] |= 0x80
        with self.assertRaises(ValueError):
            r.iso_root(r.Window(io.BytesIO(data)))

    def test_window_rejects_outside_and_bool_reads(self):
        view = r.Window(io.BytesIO(bytes(32)))
        for at, size in [(-1, 1), (32, 1), (0, 33), (0, -1), (True, 1), (0, True)]:
            with self.subTest(at=at, size=size), self.assertRaises(ValueError):
                view.read(at, size)

    def test_window_detects_backing_length_change(self):
        stream = io.BytesIO(bytes(32))
        view = r.Window(stream)
        stream.seek(0, 2)
        stream.write(b"x")
        with self.assertRaises(ValueError):
            view.read(0, 1)

    def test_child_cannot_escape_parent(self):
        view = r.Window(io.BytesIO(bytes(128))).child(32, 16)
        with self.assertRaises(ValueError):
            view.child(16, 1)

    def test_fst_signature_and_version(self):
        for at in [0, 7]:
            data = bytearray(fst())
            data[at] ^= 1
            with self.subTest(at=at), self.assertRaises(ValueError):
                r.fst_files(r.Window(io.BytesIO(data)))

    def test_fst_shared_or_cyclic_listing(self):
        data = bytearray(fst())
        table = r.u32(data, 12)
        struct.pack_into("<III", data, table + 24, 1, 5, 24)
        with self.assertRaises(ValueError):
            r.fst_files(r.Window(io.BytesIO(data)))

    def test_fst_bad_pointer_alignment(self):
        data = bytearray(fst())
        put32(data, r.u32(data, 12) + 8, 25)
        with self.assertRaises(ValueError):
            r.fst_files(r.Window(io.BytesIO(data)))

    def test_fst_unsafe_name(self):
        data = bytearray(fst())
        data[16] = ord("/")
        with self.assertRaises(ValueError):
            r.fst_files(r.Window(io.BytesIO(data)))

    def test_fst_unreachable_records(self):
        data = fst() + struct.pack("<III", 2, 5, 0)
        with self.assertRaises(ValueError):
            r.fst_files(r.Window(io.BytesIO(data)))

    def test_fst_archive_binding_is_complete(self):
        data = invented_disc()
        table = r.u32(data, 21 * 2048 + 12)
        put32(data, 21 * 2048 + table + 24 + 8, 2)
        with self.assertRaises(ValueError):
            r.resolve_texture(r.Window(io.BytesIO(data)), TARGET)

    def test_afs_budget_rejected_before_big_read(self):
        stream = CountingSource(b"AFS\0" + struct.pack("<I", 65537))
        with self.assertRaises(ValueError):
            r.afs_entries(r.Window(stream))
        self.assertEqual(stream.reads, [(0, 8)])

    def test_afs_overlap_or_outside(self):
        for at, size in [(0, 1), (16, 100)]:
            data = b"AFS\0" + struct.pack("<III", 1, at, size)
            with self.subTest(at=at), self.assertRaises(ValueError):
                r.afs_entries(r.Window(io.BytesIO(data)))

    def test_dat_descending_offsets(self):
        data = bytearray(64)
        struct.pack_into("<III", data, 0, 2, 48, 32)
        data[12:20] = b"TM3\0TM3\0"
        with self.assertRaises(ValueError):
            r.tagged_section(r.Window(io.BytesIO(data)), 0, b"TM3\0")

    def test_wrong_dat_tag(self):
        with self.assertRaises(ValueError):
            r.tagged_section(r.Window(io.BytesIO(tagged(b"SCR\0", b"x"))), 0, b"TM3\0")

    def test_tm3_rejects_metadata_overlap(self):
        data = bytearray(bank(tim3()))
        put32(data, 16, 16)
        with self.assertRaises(ValueError):
            r.bank_image(r.Window(io.BytesIO(data)), 0)

    def test_tm3_rejects_excessive_count(self):
        data = bytearray(bank(tim3()))
        put32(data, 4, 4097)
        with self.assertRaises(ValueError):
            r.bank_image(r.Window(io.BytesIO(data)), 0)

    def test_tim3_format_dimensions_and_sizes(self):
        for at, value in [(0, 0), (4, 5), (5, 7), (6, 2), (28, 49), (30, 15),
                          (32, 1), (33, 2), (34, 4), (35, 6), (36, 0), (38, 0)]:
            data = tim3()
            data[at] = value
            with self.subTest(at=at), self.assertRaises(ValueError):
                r.tim3_payload(r.Window(io.BytesIO(data)), 0)
        data = tim3()
        put32(data, 24, 31)
        with self.assertRaises(ValueError):
            r.tim3_payload(r.Window(io.BytesIO(data)), 0)

    def test_stored_transfer_dimensions_are_not_guessed(self):
        data = tim3()
        data[5] = 6
        with self.assertRaises(ValueError):
            r.tim3_payload(r.Window(io.BytesIO(data)), 0)

    def test_selector_refuses_absolute_ranges_and_unsafe_paths(self):
        for target in [dict(TARGET, offset=0), dict(TARGET, path="../room.dat"),
                       dict(TARGET, path="/room.dat"), dict(TARGET, path="demo/a.elf"),
                       dict(TARGET, path="demo/no.dat"), dict(TARGET, scp=True),
                       dict(TARGET, bank=-1), dict(TARGET, image=1)]:
            with self.subTest(target=target), self.assertRaises(ValueError):
                r.resolve_texture(r.Window(io.BytesIO(invented_disc())), target)


class PackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="godhand-original-pack-test-")
        self.root = Path(self.temp.name).resolve()
        assert self.root.is_relative_to(Path(tempfile.gettempdir()).resolve())
        self.addCleanup(self.temp.cleanup)
        self.packdir = self.root / "pack"
        self.packdir.mkdir()
        self.payload = self.packdir / "invented.raw"
        self.payload.write_bytes(bytes([93]) * 96)
        self.manifest = self.packdir / "pack.json"
        self.data = {"schema": 1, "profile": r.PROFILE, "replacements": [
            {"target": copy.deepcopy(TARGET), "payload": "invented.raw",
             "sha256": hashlib.sha256(self.payload.read_bytes()).hexdigest()}]}

    def compile(self, data=None):
        self.manifest.write_text(json.dumps(self.data if data is None else data), encoding="utf-8")
        return r.compile_pack(r.Window(io.BytesIO(invented_disc())), self.manifest)

    def test_original_pack_plan(self):
        plan = self.compile()
        self.assertEqual(plan["resolved"]["offset"], PIXEL_AT)
        self.assertEqual(plan["resolved"]["size"], 96)
        self.assertEqual(self.payload.read_bytes(), bytes([93]) * 96)

    def test_cli_plan_verifies_disc_and_preserves_evidence(self):
        import pc
        self.compile()
        disc = self.root / "invented-disc.bin"
        content = invented_disc()
        disc.write_bytes(content)
        pin = pc.load_pin()
        pin["retail_profile"] = {"bytes": len(content),
                                 "sha256": hashlib.sha256(content).hexdigest()}
        (self.root / "upstream.json").write_text(json.dumps(pin), encoding="utf-8")
        first = pc.resource_plan(disc, self.manifest, self.root)
        original = Path(first["plan"]).read_bytes()
        second = pc.resource_plan(disc, self.manifest, self.root)
        self.assertNotEqual(first["plan"], second["plan"])
        self.assertEqual(original, Path(first["plan"]).read_bytes())
        self.assertEqual(content, disc.read_bytes())
        disc.write_bytes(bytes(len(content)))
        with self.assertRaises(ValueError):
            pc.resource_plan(disc, self.manifest, self.root)
        self.assertEqual(len(list((self.root / ".local/plans").glob("*.json"))), 2)

    def test_manifest_profile_schema_and_unknown_fields(self):
        for update in [{"schema": True}, {"schema": 2}, {"profile": "prototype"},
                       {"offset": 123}]:
            with self.subTest(update=update), self.assertRaises(ValueError):
                self.compile(dict(self.data, **update))

    def test_empty_and_multiple_packs_are_not_silently_accepted(self):
        for replacements in [[], self.data["replacements"] * 2]:
            with self.subTest(n=len(replacements)), self.assertRaises(ValueError):
                self.compile(dict(self.data, replacements=replacements))

    def test_payload_size_and_hash(self):
        self.payload.write_bytes(bytes(95))
        with self.assertRaises(ValueError):
            self.compile()
        self.payload.write_bytes(bytes(96))
        with self.assertRaises(ValueError):
            self.compile()

    def test_payload_path_escape(self):
        (self.root / "outside.raw").write_bytes(bytes(96))
        self.data["replacements"][0]["payload"] = "../outside.raw"
        with self.assertRaises(ValueError):
            self.compile()

    def test_absolute_payload_is_refused(self):
        self.data["replacements"][0]["payload"] = self.payload.as_posix()
        with self.assertRaises(ValueError):
            self.compile()

    def test_duplicate_json_fields_are_refused(self):
        self.manifest.write_text('{"schema":1,"schema":1}', encoding="utf-8")
        with self.assertRaises(ValueError):
            r.compile_pack(r.Window(io.BytesIO(invented_disc())), self.manifest)

    def test_oversized_manifest_is_refused(self):
        self.manifest.write_bytes(b" " * 65537)
        with self.assertRaises(ValueError):
            r.compile_pack(r.Window(io.BytesIO(invented_disc())), self.manifest)


if __name__ == "__main__":
    unittest.main()
