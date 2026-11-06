"""Original GPL-3.0-only index allowlist; no game fixtures are needed."""
from pathlib import Path, PurePosixPath
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {".iso", ".bin", ".cue", ".elf", ".afs", ".rel", ".irx",
             ".exe", ".dll", ".ps2", ".p2s", ".state", ".zip", ".7z"}


def validate_paths(paths, allowed):
    for name in paths:
        p = PurePosixPath(name)
        if (p.is_absolute() or ".." in p.parts or "\\" in name or
                name not in allowed or p.suffix.lower() in FORBIDDEN):
            raise ValueError("Unapproved public path: " + name)


def main():
    allowed = set(json.loads((ROOT / "PUBLIC_FILES.json").read_text(encoding="utf-8")))
    validate_paths(allowed, allowed)
    raw = subprocess.check_output(["git", "ls-files", "--stage", "-z"], cwd=ROOT)
    names = []
    for entry in raw.decode("utf-8").split("\0"):
        if not entry:
            continue
        metadata, name = entry.split("\t", 1)
        if metadata.split()[0] != "100644":
            raise ValueError("Symlinks/executable blobs are not approved: " + name)
        names.append(name)
    if not names:
        raise ValueError("Empty index; nothing was reviewed")
    validate_paths(names, allowed)
    if set(names) != allowed:
        raise ValueError("Public allowlist and index differ; review missing files")
    for name in names:
        blob = subprocess.check_output(["git", "show", ":" + name], cwd=ROOT)
        blob.decode("utf-8")
        if len(blob) > 100_000 or b"\0" in blob:
            raise ValueError("Unexpected binary/large file: " + name)
    print(f"{len(names)} original-tooling paths approved; no game inputs required")


if __name__ == "__main__":
    main()
