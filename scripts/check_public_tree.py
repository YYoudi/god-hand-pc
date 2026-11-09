"""Original GPL-3.0-only index allowlist; no game fixtures are needed."""
from pathlib import Path, PurePosixPath
import json
import subprocess
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from journal import validate

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {".iso", ".bin", ".cue", ".elf", ".afs", ".rel", ".irx",
             ".exe", ".dll", ".ps2", ".p2s", ".state", ".zip", ".7z",
             ".dat", ".scp", ".mdb", ".tm2", ".tm3", ".wav", ".ogg", ".mp3"}


def validate_paths(paths, allowed):
    for name in paths:
        p = PurePosixPath(name)
        if (p.is_absolute() or ".." in p.parts or "\\" in name or
                name not in allowed or p.suffix.lower() in FORBIDDEN or
                set(p.parts) & {'.local', 'generated', 'generated_modules', 'research'}):
            raise ValueError("Unapproved public path: " + name)


def validate_blob(name, blob, media):
    if name in media:
        # Bytes/header/hash were validated through the staged comparison registry.
        return
    if Path(name).suffix.lower() in {'.png','.jpg','.jpeg','.ppm'}:
        raise ValueError('Unregistered screenshot: '+name)
    text = blob.decode('utf-8-sig')
    limit = 1024*1024 if name.startswith('docs/') else 100_000
    if len(blob) > limit or '\0' in text:
        raise ValueError('Unexpected binary/large file: '+name)
    if re.search(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)',text):
        raise ValueError('Credential-like content: '+name)


def main():
    read=lambda name:subprocess.check_output(['git','show',':'+name],cwd=ROOT)
    allowed = set(json.loads(read('PUBLIC_FILES.json')))
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
    media=validate(json.loads(read('docs/journal.json')),json.loads(read('docs/migration.json')),read)
    if not set(media).issubset(names):
        raise ValueError('Registered screenshot missing from index')
    for name in names: validate_blob(name,read(name),media)
    print(f"{len(names)} explicit public paths approved; {len(media)} reviewed screenshots, no game inputs")


if __name__ == "__main__":
    main()
