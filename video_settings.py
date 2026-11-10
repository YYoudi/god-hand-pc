"""Original GPL-3.0-only restart-required preferences, not native menu code."""
from pathlib import Path
import hashlib
import json
import os
import re
import stat
import uuid

import runtime_packs

LIMIT = 4096
HASH = re.compile(r"[0-9a-f]{64}")
_ANY_REVISION = object()


class StaleRevision(ValueError):
    """Known no-commit conflict, distinct from an ambiguous I/O failure."""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _ordinary(path, directory=False):
    info = path.lstat()
    require(not stat.S_ISLNK(info.st_mode) and not (
        getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 1024)),
        "Video settings aliases/reparse points are not supported")
    require(stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode),
            "Video settings require ordinary directories/files")
    if not directory:
        require(info.st_nlink == 1 and info.st_size <= LIMIT,
                "Video settings hardlinks/oversize files are not supported")


def _storage(root, name, create=False, *, user=None):
    workspace = runtime_packs.workspace_path(root, name)
    # Check unresolved ancestors too; contained() alone would erase an alias.
    path = Path(root).resolve()
    relative = ("userdata",)
    if user is not None:
        user = Path(user)
        require(user.is_absolute() and user.parent.parent == workspace / "packs/launches" and
                user.name == "userdata" and re.fullmatch(r"[a-f0-9]{32}", user.parent.name),
                "Diagnostic video store requires an owned launch userdata directory")
        relative = ("packs", "launches", user.parent.name, "userdata")
    for part in (".local", name, *relative, "video"):
        path = path / part
        if not path.exists() and not path.is_symlink():
            if not create or part in (".local", name):
                raise FileNotFoundError("Video preferences require an existing workspace: " + str(path))
            path.mkdir()
        _ordinary(path, directory=True)
    expected = (workspace / "userdata" if user is None else user) / "video"
    require(path.resolve() == expected, "Video storage escapes workspace")
    return path


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate video settings key")
        result[key] = value
    return result


def _nonfinite(value):
    raise ValueError("Nonfinite video settings number: " + value)


def _read(path):
    _ordinary(path)
    with path.open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    require(len(raw) <= LIMIT, "Video settings grew beyond metadata limit")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    except (UnicodeError, RecursionError) as error:
        raise ValueError("Invalid video settings text") from error
    require(type(data) is dict, "Video settings must be a JSON object")
    return raw, data


def _revision(data):
    require(set(data) == {"schema", "native_scale", "previous"} and type(data["schema"]) is int
            and data["schema"] == 1, "Unknown video revision schema/fields")
    scale = data["native_scale"]
    require(scale is None or (type(scale) is int and 1 <= scale <= 8),
            "Native internal scale must be an integer1..8, or reset/null")
    require(data["previous"] is None or (type(data["previous"]) is str and HASH.fullmatch(data["previous"])),
            "Invalid previous video revision")
    return data


def _encode(data):
    return (json.dumps(data, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _current(storage):
    pointer = storage / "current.json"
    if not pointer.exists() and not pointer.is_symlink():
        return None
    _, active = _read(pointer)
    require(set(active) == {"schema", "sha256"} and type(active["schema"]) is int and active["schema"] == 1
            and type(active["sha256"]) is str and HASH.fullmatch(active["sha256"]),
            "Invalid current video revision pointer")
    path = storage / (active["sha256"] + ".json")
    raw, data = _read(path)
    require(hashlib.sha256(raw).hexdigest() == active["sha256"], "Video revision hash differs")
    _revision(data)
    return {"path": str(path), "sha256": active["sha256"], "settings": data}


def show(root, name, *, user=None):
    storage = _storage(root, name, user=user)
    require(not (storage / "write.lock").exists() and not (storage / "write.lock").is_symlink(),
            "Video write lock requires inspection")
    return _current(storage)


def update(root, name, native_scale, *, expected_revision=_ANY_REVISION, user=None):
    """Optionally compare a menu/editor snapshot under the writer lock.

    Omitted preserves the existing CLI's unconditional new revision. Explicit
    None means create only if absent; a hash means update only that revision.
    This prevents a future stale editor from silently replacing newer settings.
    """
    _revision({"schema": 1, "native_scale": native_scale, "previous": None})
    require(expected_revision is _ANY_REVISION or expected_revision is None or
            (type(expected_revision) is str and HASH.fullmatch(expected_revision)),
            "Expected video revision must be a SHA-256 or explicit None")
    storage = _storage(root, name, create=True, user=user)
    lock = storage / "write.lock"
    # Exclusive lock; never steal a stale/other writer's lock. Only remove our
    # own transient lock on normal unwinding. Revision/history files are retained.
    with lock.open("xb") as out:
        out.write((str(os.getpid()) + "\n").encode("ascii"))
    try:
        previous = _current(storage)
        if expected_revision is not _ANY_REVISION and expected_revision != (previous["sha256"] if previous else None):
            raise StaleRevision("Video preferences changed since selection; reload before saving")
        data = {"schema": 1, "native_scale": native_scale,
                "previous": previous["sha256"] if previous else None}
        raw = _encode(data)
        digest = hashlib.sha256(raw).hexdigest()
        with (storage / (digest + ".json")).open("xb") as out:
            out.write(raw)
        temporary = storage / ("pending-" + uuid.uuid4().hex + ".json")
        with temporary.open("xb") as out:
            out.write(_encode({"schema": 1, "sha256": digest}))
        # Existing pointer was checked above. Failed writes/replaces leave the
        # old pointer valid and the new immutable/pending evidence available.
        os.replace(temporary, storage / "current.json")
        return {"path": str(storage / (digest + ".json")), "sha256": digest, "settings": data}
    finally:
        lock.unlink()


def protocol(root, name, directory):
    selected = show(root, name)
    require(selected is not None, "No video preferences selected; use video-settings --internal-scale N first")
    frozen = Path(directory) / "video-settings.json"
    # Freeze the actual selected file bytes, not a silent JSON normalization.
    raw, _ = _read(Path(selected["path"]))
    require(hashlib.sha256(raw).hexdigest() == selected["sha256"], "Video revision changed before freeze")
    with frozen.open("xb") as out:
        out.write(raw)
    scale = selected["settings"]["native_scale"]
    return dict(selected, frozen_path=str(frozen), requested_native_scale=scale,
                mode="upstream-ini" if scale is None else "native-scale",
                effective_scale="not inferred; native may reduce to the GL storage-block limit",
                requires_restart=True), ({} if scale is None else {
                    "PS2X_GS_RENDERER": "native", "PS2X_GS_SCALE": str(scale)})
