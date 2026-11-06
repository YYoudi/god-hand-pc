"""Original GPL diagnostic magenta pack. No ISO, game pixels or palette copied."""
from pathlib import Path
import argparse
import hashlib
import json

import resources


def create(directory):
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.iterdir()):
        raise ValueError("Example output must be a new or empty directory; nothing overwritten")
    # Uniform stored indices remain uniform under transfer addressing. Every
    # palette entry is authored here; this is diagnostic data, not remaster art.
    data = bytes([0x11]) * (128 * 128 // 2) + bytes([255, 0, 255, 128]) * 16
    digest = hashlib.sha256(data).hexdigest()
    with (directory / "magenta.raw").open("xb") as out:
        out.write(data)
    pack = {"schema": 1, "profile": resources.PROFILE, "replacements": [{
        "target": {"path": "st1/r100.dat", "scp": 3, "bank": 0, "image": 0},
        "payload": "magenta.raw", "sha256": digest}]}
    with (directory / "pack.json").open("x", encoding="utf-8") as out:
        json.dump(pack, out, indent=2)
        out.write("\n")
    return {"manifest": str(directory / "pack.json"), "bytes": len(data), "sha256": digest,
            "provenance": "Original uniform indexed pixels and original palette; no game data"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(create(args.output), indent=2))
