"""Original GPL named external RGBA packs. Game-derived snapshots stay private."""
from pathlib import Path, PurePosixPath
from dataclasses import asdict
import hashlib
import json
import re

import resources
import hd_reference


def unique_object(items):
    result = {}
    for key, value in items:
        resources.require(key not in result, "Duplicate HD manifest field")
        result[key] = value
    return result


def compile_pack(disc, manifest):
    manifest = Path(manifest).resolve(strict=True)
    resources.require(manifest.is_file() and manifest.stat().st_size <= 65536, "HD manifest budget")
    with manifest.open("rb") as stream: raw = stream.read(65537)
    resources.require(len(raw) <= 65536, "HD manifest changed beyond budget")
    data = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    resources.require(type(data) is dict and set(data) == {"schema", "kind", "profile", "replacements"} and
                      type(data["schema"]) is int and data["schema"] == 1 and
                      data["kind"] == "decoded-rgba-replacement" and data["profile"] == resources.PROFILE,
                      "Unsupported HD manifest kind/profile/schema")
    items = data["replacements"]
    resources.require(type(items) is list and len(items) == 1, "HD v1 requires exactly one replacement")
    item = items[0]
    resources.require(type(item) is dict and set(item) == {"target", "image"}, "Invalid HD replacement keys")
    image = item["image"]
    resources.require(type(image) is dict and set(image) == {"path", "width", "height", "format", "sha256"} and
                      image["format"] == "rgba8-gs-alpha", "Unsupported HD image fields/format")
    w, h = image["width"], image["height"]
    resources.require(type(w) is int and type(h) is int and 128 < w <= 2048 and 128 < h <= 2048 and
                      w & (w-1) == 0 and h & (h-1) == 0, "Unsupported HD dimensions")
    name = image["path"]
    resources.require(type(name) is str and 0 < len(name) <= 1024 and "\\" not in name and ":" not in name,
                      "Unsafe HD image path")
    relative = PurePosixPath(name)
    resources.require(not relative.is_absolute() and ".." not in relative.parts, "Unsafe HD image path")
    payload = (manifest.parent/relative).resolve(strict=True)
    resources.require(payload.is_relative_to(manifest.parent) and payload.is_file(), "HD image escapes pack directory")
    resources.require(type(image["sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", image["sha256"]), "Invalid HD image hash")
    resources.require(payload.stat().st_size == w*h*4, "HD image length differs")
    with payload.open("rb") as stream: rgba = stream.read(w*h*4+1)
    resources.require(len(rgba) == w*h*4 and hashlib.sha256(rgba).hexdigest() == image["sha256"], "HD image changed/hash differs")
    selected, reference = hd_reference.read_reference(disc, item["target"])
    blob = hd_reference.envelope(reference, rgba, w, h)
    # No raw reference or game pixels belong in the public/printed plan.
    plan = {"schema": 1, "profile": resources.PROFILE, "target": item["target"],
            "source_metadata": asdict(selected), "image": {**image, "path": str(payload)},
            "manifest_sha256": hashlib.sha256(raw).hexdigest(),
            "identity": "full decoded content; identical aliases may also match",
            "scope": "experimental single-source raw RGBA, not general HD/full-game fidelity"}
    return plan, rgba, blob


def protocol(iso, manifest, directory, strict=False):
    resources.require(type(strict) is bool, "strict HD policy must be a boolean")
    empty = {"GODHAND_PC_HD_FILE": "", "GODHAND_PC_HD_SHA256": "", "GODHAND_PC_HD_PROFILE": ""}
    if manifest is None:
        resources.require(not strict, "strict HD mode requires a pack")
        return {"mode": "original"}, empty
    try:
        with Path(iso).open("rb") as stream:
            plan, rgba, blob = compile_pack(resources.Window(stream), manifest)
        frozen = Path(directory)/"hd-input.private-input"
        authored = Path(directory)/"hd-authored.rgba"
        # Snapshot only after full validation, never reread a user file to apply it.
        with authored.open("xb") as out: out.write(rgba)
        with frozen.open("xb") as out: out.write(blob)
        authored.chmod(0o444); frozen.chmod(0o444)
        return {"mode": "replacement-planned", "plan": plan, "frozen_image": str(authored),
                "private_input": str(frozen), "rendered_change": "not inferred from launch planning"}, {
                    "GODHAND_PC_HD_FILE": str(frozen), "GODHAND_PC_HD_PROFILE": resources.PROFILE,
                    "GODHAND_PC_HD_SHA256": hashlib.sha256(blob).hexdigest()}
    except (ValueError, OSError, RecursionError) as error:
        if strict: raise ValueError("HD pack refused in strict mode: " + str(error)) from error
        return {"mode": "original-fallback", "error": str(error)}, empty


def create_example(directory):
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    resources.require(not any(directory.iterdir()), "Example output must be new/empty; nothing overwritten")
    rgba = hd_reference.example_rgba()
    image = {"path": "authored.rgba", "width": 512, "height": 512, "format": "rgba8-gs-alpha",
             "sha256": hashlib.sha256(rgba).hexdigest()}
    manifest = {"schema": 1, "kind": "decoded-rgba-replacement", "profile": resources.PROFILE,
                "replacements": [{"target": {"path": "st1/r100.dat", "scp": 3, "bank": 0, "image": 0}, "image": image}]}
    with (directory/image["path"]).open("xb") as stream: stream.write(rgba)
    with (directory/"pack.json").open("x", encoding="utf-8") as stream:
        json.dump(manifest, stream, indent=2); stream.write("\n")
    return {"manifest": str(directory/"pack.json"), "bytes": len(rgba), "sha256": image["sha256"],
            "provenance": "Original authored512x512 diagnostic, no disc or game pixels read"}
