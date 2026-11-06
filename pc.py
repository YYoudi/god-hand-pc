"""Original GPL-3.0-only continuation bootstrap; no game code or data."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parent


def git(*args, cwd=None):
    return subprocess.check_output(["git", *map(str, args)], cwd=cwd, text=True).strip()


def load_pin(root=ROOT):
    pin = json.loads((root / "upstream.json").read_text(encoding="utf-8"))
    if pin["repository"] != "https://github.com/LasVola/godhand-recomp.git":
        raise ValueError("Unreviewed upstream repository")
    if not re.fullmatch(r"[0-9a-f]{40}", pin["revision"]):
        raise ValueError("An exact upstream commit is required")
    return pin


def inspect_checkout(path, base, expected):
    path = Path(path).resolve(strict=True)
    if git("rev-parse", "HEAD", cwd=path) != expected:
        raise ValueError("Checkout revision differs from the recorded revision")
    if git("status", "--porcelain", "--untracked-files=all", cwd=path):
        raise ValueError("Source has non-ignored uncommitted changes")
    if subprocess.run(["git", "merge-base", "--is-ancestor", base, expected],
                      cwd=path, capture_output=True).returncode:
        raise ValueError("Checkout does not descend from the pinned upstream")
    return {"checkout": str(path), "revision": expected, "upstream_base": base}


def verify_disc(path, profile):
    path = Path(path).resolve(strict=True)
    if not path.is_file() or path.stat().st_size != profile["bytes"]:
        raise ValueError("Disc size differs from the supported retail profile")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != profile["sha256"]:
        raise ValueError("Disc hash differs from the supported retail profile")
    return {"path": str(path), "sha256": digest, "bytes": path.stat().st_size,
            "operation": "read-only verification, not extraction or execution"}


def private_dir(root):
    root = Path(root).resolve()
    private = (root / ".local").resolve()
    if not private.is_relative_to(root) or private == root:
        raise ValueError("Private storage escapes the continuation directory")
    private.mkdir(exist_ok=True)
    return private


def clone_pinned(repository, revision, destination):
    destination = Path(destination)
    if destination.exists():
        return inspect_checkout(destination, revision, revision)
    # Argument vectors only; no shell or string-built commands. A failed partial
    # clone is retained for inspection, never recursively removed or overwritten.
    subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout",
                    repository, str(destination)], check=True)
    subprocess.run(["git", "checkout", "--detach", revision], cwd=destination, check=True)
    return inspect_checkout(destination, revision, revision)


def store_checkout(record, root=ROOT):
    private = private_dir(root)
    p = private / "checkout.json"
    if p.exists() and json.loads(p.read_text(encoding="utf-8")) != record:
        raise ValueError("A different checkout is already registered; preserve/review it first")
    p.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("fetch")
    adopt = sub.add_parser("adopt")
    adopt.add_argument("--checkout", required=True, type=Path)
    adopt.add_argument("--revision", required=True)
    disc = sub.add_parser("verify-disc")
    disc.add_argument("--iso", required=True, type=Path)
    sub.add_parser("status")
    args = parser.parse_args()
    pin = load_pin()
    if args.command == "fetch":
        result = clone_pinned(pin["repository"], pin["revision"], private_dir(ROOT) / "upstream")
        store_checkout(result)
    elif args.command == "adopt":
        if not re.fullmatch(r"[0-9a-f]{40}", args.revision):
            raise ValueError("Adoption requires an exact commit, not a branch or tag")
        result = inspect_checkout(args.checkout, pin["revision"], args.revision)
        store_checkout(result)
    elif args.command == "verify-disc":
        result = verify_disc(args.iso, pin["retail_profile"])
    else:
        p = ROOT / ".local" / "checkout.json"
        if not p.exists():
            raise ValueError("No checkout registered; fetch or adopt first")
        saved = json.loads(p.read_text(encoding="utf-8"))
        result = inspect_checkout(saved["checkout"], pin["revision"], saved["revision"])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
