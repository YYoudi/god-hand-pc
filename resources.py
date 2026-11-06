"""Original GPL-3.0-only bounded texture-selector tooling; no game code.

Format provenance: the separately published FST/AFS/DAT/TM3/TIM3 contracts
in YYoudi/god-hand-rs/specs. No parser implementation is copied. This reader
resolves metadata only: it never extracts original texture pixels or palettes.
"""
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
import hashlib
import json
import struct

META_LIMIT = 16 * 1024 * 1024
PROFILE = "retail-us-slus-21503"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def ordinal(value, count):
    require(type(value) is int and 0 <= value < count, "Ordinal outside supported catalog")
    return value


class Window:
    """Bounded read-only window; validates unchanged backing length on every read."""
    def __init__(self, stream, offset=0, size=None):
        self.stream = stream
        stream.seek(0, 2)
        self.backing_size = stream.tell()
        self.offset = offset
        self.size = self.backing_size - offset if size is None else size
        require(type(offset) is int and type(self.size) is int and
                0 <= offset <= self.backing_size and
                0 <= self.size <= self.backing_size - offset, "Window outside backing")

    def read(self, at, size):
        require(type(at) is int and type(size) is int and 0 <= at <= self.size and
                0 <= size <= min(META_LIMIT, self.size - at), "Metadata read outside window/budget")
        self.stream.seek(0, 2)
        require(self.stream.tell() == self.backing_size, "Backing length changed")
        self.stream.seek(self.offset + at)
        data = self.stream.read(size)
        require(len(data) == size, "Truncated metadata read")
        return data

    def child(self, at, size):
        require(type(at) is int and type(size) is int and 0 <= at <= self.size and
                0 <= size <= self.size - at, "Child outside source window")
        result = Window(self.stream, self.offset + at, size)
        require(result.backing_size == self.backing_size, "Backing length changed")
        return result


def u32(data, at=0):
    require(0 <= at <= len(data) - 4, "Truncated u32")
    return struct.unpack_from("<I", data, at)[0]


def safe_component(name):
    require(1 <= len(name) <= 255 and name not in (".", "..") and
            all(32 <= ord(c) <= 126 and c not in "/\\:" for c in name), "Unsafe resource component")
    return name


def iso_root(disc):
    pvd = disc.read(16 * 2048, 2048)
    require(pvd[:7] == b"\x01CD001\x01", "Unsupported ISO9660 primary descriptor")
    require(struct.unpack_from("<H", pvd, 128)[0] == 2048 and
            struct.unpack_from(">H", pvd, 130)[0] == 2048, "Unsupported ISO block size")

    def extent(record):
        require(len(record) >= 34 and record[0] == len(record) and
                33 + record[32] <= len(record), "Invalid ISO directory record")
        lba, size = u32(record, 2), u32(record, 10)
        require(lba == struct.unpack_from(">I", record, 6)[0] and
                size == struct.unpack_from(">I", record, 14)[0], "ISO endian fields disagree")
        require(not record[25] & 0x80, "Multi-extent ISO file unsupported")
        return disc.child(lba * 2048, size)

    directory = extent(pvd[156:156 + pvd[156]])
    require(pvd[181] & 2, "ISO root is not a directory")
    data = directory.read(0, directory.size)
    result, at = {}, 0
    while at < len(data):
        n = data[at]
        if not n:
            at = (at // 2048 + 1) * 2048
            continue
        require(n <= len(data) - at and at // 2048 == (at + n - 1) // 2048,
                "ISO record crosses directory/sector boundary")
        record = data[at:at + n]
        view = extent(record)
        raw = record[33:33 + record[32]]
        if raw not in (b"\0", b"\1") and not record[25] & 2:
            name = safe_component(raw.decode("ascii").split(";", 1)[0]).upper()
            require(name not in result, "Duplicate ISO root filename")
            result[name] = view
        at += n
    return result


def fst_files(view):
    data = view.read(0, view.size)
    require(len(data) >= 16 and data[:8] == b"FST\0\0\0\x80\x3f", "Unsupported FST header")
    pool, table = u32(data, 8), u32(data, 12)
    require(pool == 16 and pool <= table <= len(data) and
            (len(data) - table) % 12 == 0, "Invalid FST metadata offsets")
    count = (len(data) - table) // 12
    require(0 < count <= 65536, "FST record budget exceeded")
    strings = data[pool:table]
    rows = list(struct.iter_unpack("<III", data[table:]))
    visited, paths, files = set(), set(), {}
    expanded = 0

    def listing(pointer, parent, depth):
        nonlocal expanded
        require(depth <= 64 and pointer % 12 == 0, "FST depth/pointer invalid")
        index = pointer // 12
        while True:
            ordinal(index, count)
            require(index not in visited, "FST cyclic/shared listing")
            visited.add(index)
            flags, name_at, value = rows[index]
            if (flags, name_at, value) == (3, 0, 0):
                return
            require(name_at < len(strings) and (name_at == 0 or strings[name_at - 1] == 0),
                    "FST name pointer is not a string boundary")
            end = strings.find(b"\0", name_at)
            require(end >= 0, "Unterminated FST name")
            name = safe_component(strings[name_at:end].decode("ascii"))
            path = parent + "/" + name if parent else name
            expanded += len(path)
            require(expanded <= META_LIMIT and path not in paths, "FST path budget/duplicate")
            paths.add(path)
            if flags == 1:
                if value:
                    listing(value, path, depth + 1)
            elif flags & 255 == 2:
                files[path] = value
            else:
                raise ValueError("Unsupported FST record flags")
            index += 1

    listing(0, "", 0)
    for i, row in enumerate(rows):
        require(i in visited or (i == count - 1 and row == (0, 0, 0)), "Unreachable FST records")
    return files


def afs_entries(view):
    header = view.read(0, 8)
    require(header[:4] == b"AFS\0", "Invalid AFS signature")
    count = u32(header, 4)
    require(count <= 65536 and 8 + count * 8 <= view.size, "AFS table outside budget/window")
    entries = []
    for at, size in struct.iter_unpack("<II", view.read(8, count * 8)):
        require(not size or at >= 8 + count * 8, "AFS payload overlaps catalog")
        entries.append(view.child(at, size))
    return entries


def tagged_section(view, index, expected):
    count = u32(view.read(0, 4))
    require(count <= 65536 and 4 + count * 8 <= view.size, "DAT catalog outside budget/window")
    ordinal(index, count)
    data = view.read(4, count * 8)
    offsets = list(struct.unpack_from("<" + "I" * count, data))
    for i, at in enumerate(offsets):
        require(4 + count * 8 <= at <= view.size and at % 16 == 0 and
                (i == 0 or at >= offsets[i - 1]), "Invalid DAT section offsets")
    require(data[count * 4 + index * 4:count * 4 + index * 4 + 4] == expected,
            "Selected DAT section has wrong tag")
    at = offsets[index]
    end = offsets[index + 1] if index + 1 < count else view.size
    return view.child(at, end - at)


def bank_image(view, index):
    head = view.read(0, 16)
    require(head[:4] == b"TM3\0", "Invalid TM3 bank signature")
    count = u32(head, 4)
    require(0 < count <= 4096, "TM3 image budget exceeded")
    ordinal(index, count)
    minimum = 16 + count * 12 + (4 if count % 2 else 0)
    require(minimum <= view.size, "TM3 metadata outside bank")
    offsets = struct.unpack("<" + "I" * count, view.read(16, count * 4))
    for i, at in enumerate(offsets):
        require(minimum <= at <= view.size and at % 16 == 0 and
                (i == 0 or at > offsets[i - 1]), "Invalid TM3 image offsets")
    at = offsets[index]
    end = offsets[index + 1] if index + 1 < count else view.size
    return view.child(at, end - at)


@dataclass(frozen=True)
class TextureTarget:
    offset: int
    size: int
    width: int
    height: int
    index_bits: int
    storage: int
    afs_ordinal: int


def tim3_payload(view, archive_ordinal):
    h = view.read(0, 64)
    require(h[:5] == b"TIM3\x04" and h[5] in (0, 6) and
            struct.unpack_from("<H", h, 6)[0] == 1, "Unsupported TIM3 picture/storage profile")
    total, palette, pixels = struct.unpack_from("<III", h, 16)
    header, colors = struct.unpack_from("<HH", h, 28)
    w, height = struct.unpack_from("<HH", h, 36)
    require(header == 48 and h[32:35] == b"\0\1\3" and h[35] in (4, 5),
            "Unsupported TIM3 header/palette/index format")
    require(0 < w <= 4096 and 0 < height <= 4096 and w * height <= 4194304,
            "TIM3 dimension budget exceeded")
    bits = 4 if h[35] == 4 else 8
    require(colors == (16 if bits == 4 else 256) and palette == colors * 4 and
            pixels == (w * height * bits + 7) // 8 and
            total == 48 + pixels + palette and 16 + total <= view.size,
            "TIM3 declared sizes disagree")
    if h[5] == 6:
        require(w >= 128 and height >= 128 and w & (w - 1) == 0 and
                height & (height - 1) == 0, "Unsupported TIM3 stored-transfer dimensions")
    return TextureTarget(view.offset + 64, pixels + palette, w, height, bits, h[5], archive_ordinal)


def resolve_texture(disc, target):
    require(type(target) is dict and set(target) == {"path", "scp", "bank", "image"},
            "Target requires exact path/scp/bank/image keys")
    path = target["path"]
    require(type(path) is str and path.lower().endswith(".dat"), "Only named DAT texture resources supported")
    for part in path.split("/"):
        safe_component(part)
    root = iso_root(disc)
    require("GODHAND.FST" in root and "_DATA.AFS" in root, "Missing named resource catalogs")
    files, archive = fst_files(root["GODHAND.FST"]), afs_entries(root["_DATA.AFS"])
    require(len(files) == len(archive) and sorted(files.values()) == list(range(len(archive))),
            "FST does not bind AFS exactly once")
    require(path in files, "Named FST resource not found")
    number = files[path]
    room = archive[number]
    scp = tagged_section(room, target["scp"], b"SCP\0")
    bank = tagged_section(scp, target["bank"], b"TM3\0")
    return tim3_payload(bank_image(bank, target["image"]), number)


def compile_pack(disc, manifest_path):
    """Strict single-replacement MVP, compatible with the evaluated read adapter.

    No absolute byte ranges are accepted from a pack. Malformed packs produce no
    plan/environment. The caller may explicitly continue without a pack, using
    original assets; this function never changes the ISO or extracts its pixels.
    """
    path = Path(manifest_path).resolve(strict=True)
    require(path.stat().st_size <= 65536, "Pack manifest exceeds budget")
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "Duplicate JSON field")
            result[key] = value
        return result

    pack = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    require(type(pack) is dict and set(pack) == {"schema", "profile", "replacements"} and
            type(pack["schema"]) is int and pack["schema"] == 1 and pack["profile"] == PROFILE,
            "Unsupported pack schema/profile")
    items = pack["replacements"]
    require(type(items) is list and len(items) == 1, "MVP requires exactly one replacement")
    item = items[0]
    require(type(item) is dict and set(item) == {"target", "payload", "sha256"}, "Invalid replacement keys")
    require(type(item["payload"]) is str, "Payload must be a relative filename")
    rel = PurePosixPath(item["payload"])
    require(not rel.is_absolute() and ".." not in rel.parts and "\\" not in item["payload"] and
            ":" not in item["payload"], "Unsafe payload path")
    payload = (path.parent / item["payload"]).resolve(strict=True)
    require(payload.is_relative_to(path.parent) and payload.is_file(), "Payload escapes pack directory")
    selected = resolve_texture(disc, item["target"])
    require(payload.stat().st_size == selected.size, "Payload must preserve native pixel/CLUT size")
    require(selected.size <= META_LIMIT, "Replacement exceeds payload budget")
    with payload.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    require(item["sha256"] == digest, "Replacement hash mismatch")
    return {"schema": 1, "profile": PROFILE, "target": item["target"],
            "resolved": asdict(selected), "payload": str(payload), "sha256": digest,
            "scope": "Same-size native stored pixel/CLUT replacement, not HD resizing or decoded RGBA"}
