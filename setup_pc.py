"""Original GPL-3.0-only retail build orchestration, not translated game code."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import uuid


def require(ok, message):
    if not ok:
        raise ValueError(message)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(path):
    with Path(path).open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def require_no_game(query=None):
    """Do not decode localized tasklist/OEM memory columns as Python UTF-8.

    The requested image name is ASCII; inspect the native byte result. Refuse
    unknown/NUL-containing output rather than interpreting it as an idle host.
    This is a preservation preflight, not a process-killing or recovery API.
    """
    raw = (query or subprocess.check_output)(
        ["tasklist", "/FI", "IMAGENAME eq godhand.exe", "/FO", "CSV", "/NH"])
    require(type(raw) is bytes and b"\0" not in raw, "Unrecognized native process-inventory encoding")
    require(b"godhand.exe" not in raw.lower(), "Close the running game before build or launch")


def contained(base, target):
    base, target = Path(base).resolve(), Path(target).resolve()
    require(target != base and target.is_relative_to(base), "Setup path escapes owned workspace")
    return target


def load_dependencies(root):
    data = json.loads((Path(root) / "dependencies.json").read_text(encoding="utf-8"))
    require(data["schema"] == 1, "Unsupported dependency lock")
    result, names = [], set()
    for item in data["dependencies"]:
        name = item["name"]
        require(re.fullmatch(r"[a-z][a-z0-9_]*", name) and name not in names,
                "Invalid/duplicate dependency name")
        require(re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+\.git", item["repository"]),
                "Dependency is not a reviewed GitHub source URL")
        require(re.fullmatch(r"[0-9a-f]{40}", item["revision"]), "Dependency needs an exact revision")
        license = item["license"]
        require(re.fullmatch(r"[A-Za-z0-9_.-]+", license["file"]) and
                license["file"] not in (".", "..") and
                re.fullmatch(r"[0-9a-f]{64}", license["sha256"]), "Invalid license receipt")
        names.add(name)
        result.append(item)
    require(names == {"elfio", "fmt", "imgui", "libdwarf", "rabbitizer", "raylib", "rlimgui", "toml11"},
            "Incomplete or unreviewed dependency set")
    return result


def cached_disc(source, destination, profile, verify):
    """Make an exclusive private copy for upstream's implicit sibling-disc path.

    No symlink or hardlink to the owner's original; a partial copy is retained and
    refused on retry, not overwritten. Hash verification precedes the read-only
    attribute on the copy. No original file attribute is changed.
    """
    source, destination = Path(source).resolve(strict=True), Path(destination).resolve()
    require(source != destination and not (destination.exists() and destination.samefile(source)),
            "Private disc must not alias the original")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        with source.open("rb") as src, destination.open("xb") as dst:
            shutil.copyfileobj(src, dst, 1024 * 1024)
    record = verify(destination, profile)
    destination.chmod(0o444)
    return record


def build_steps(checkout, iso):
    checkout = Path(checkout)
    python = sys.executable
    return [
        ("boot-generate", [python, "-I", "build.py", "generate", "--iso", str(iso)]),
        # snr2 has GLOBAL options before its subcommand; the README ordering does
        # not work at the pinned revision. gen_modules later needs the sibling ISO.
        ("overlay-extract", [python, "-I", "tools/snr2/snr2.py", "--iso", str(iso), "extract"]),
        ("overlay-link", [python, "-I", "tools/snr2/gen_modules.py"]),
        ("overlay-generate", [python, "-I", "build.py", "modules"]),
        # The first configure only exposed the recompiler (no boot code yet).
        # Merely having build.ninja is not proof that a game target now exists.
        ("game-configure", [python, "-I", "build.py", "configure"]),
        ("game-build", [python, "-I", "build.py", "build"]),
    ]


def generation_diagnostics(path, destination):
    """Retain the actual log: a successful process can report translation errors."""
    path, destination = Path(path), Path(destination)
    require(path.is_file() and path.stat().st_size <= 64 * 1024 * 1024,
            "Missing/oversized generation log")
    raw = path.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    counts = re.findall(r"(?im)^Warnings:\s*(\d+),\s*errors:\s*(\d+)\s*$", text)
    unhandled = re.findall(r"(?im)^Unhandled instructions:\s*(\d+)\s*$", text)
    require(len(counts) == 1 and len(unhandled) == 1, "Missing/ambiguous generation diagnostic summary")
    destination.parent.mkdir(exist_ok=True)
    with destination.open("xb") as output:
        output.write(raw)
    warnings, errors = map(int, counts[0])
    return {"warnings": warnings, "errors": errors, "unhandled": int(unhandled[0]),
            "log": str(destination), "sha256": hashlib.sha256(raw).hexdigest(),
            "error_lines": [line.strip() for line in text.splitlines() if "[error]" in line.lower()]}


def overlay_manifest(source):
    directory = Path(source) / "build/snr2/rel"
    manifest = directory / "manifest.json"
    require(manifest.is_file() and manifest.stat().st_size <= 1024 * 1024, "Missing/oversized overlay manifest")
    items = json.loads(manifest.read_text(encoding="utf-8"))
    require(type(items) is list and len(items) == 81, "Expected exactly 81 retail overlays")
    seen = set()
    for item in items:
        name = item["name"]
        require(re.fullmatch(r"[A-Za-z0-9_]+\.rel", name) and name not in seen,
                "Unsafe/duplicate overlay filename")
        seen.add(name)
        payload = contained(directory, directory / name)
        require(payload.is_file() and payload.stat().st_size == item["size"] and
                digest(payload) == item["sha256"], "Extracted overlay identity mismatch")
    return items


class Run:
    """Append-only per-invocation evidence, including live child identity."""
    def __init__(self, workspace):
        self.workspace = Path(workspace)
        self.directory = contained(workspace, self.workspace / "runs" / uuid.uuid4().hex)
        self.directory.mkdir(parents=True)
        self.record = {"started_at": now(), "status": "preparing", "steps": []}
        self.child = None
        self.save()

    def save(self):
        (self.directory / "receipt.json").write_text(json.dumps(self.record, indent=2) + "\n", encoding="utf-8")

    def step(self, name, command, checkout, env):
        path = self.directory / (name + ".log")
        step = {"name": name, "command": list(map(str, command)), "cwd": str(checkout),
                "started_at": now(), "status": "running", "log": str(path)}
        self.record["steps"].append(step)
        self.record["status"] = "running"
        print("Setup:", name, "log:", path, flush=True)
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
        with path.open("xb") as output:
            self.child = subprocess.Popen(command, cwd=checkout, env=env,
                                          stdout=output, stderr=subprocess.STDOUT, creationflags=flags)
            step["pid"] = self.child.pid
            self.save()
            code = self.child.wait()
        step.update(status="terminal", exit=code, ended_at=now())
        self.save()
        require(code == 0, f"{name} failed ({code}); retained evidence: {self.directory}")


def setup(iso, vsroot, jobs, root, prepare_only=False, workspace_name="retail-setup"):
    # Import here to avoid a module cycle with the CLI.
    import pc
    require(os.name == "nt", "This pinned native build recipe currently requires Windows/MSVC")
    require(type(jobs) is int and 1 <= jobs <= 16, "Jobs must be between 1 and 16")
    require(type(workspace_name) is str and re.fullmatch(r"retail-[a-z0-9][a-z0-9-]{0,40}", workspace_name),
            "Workspace name must be a single retail-* identifier")
    root = Path(root).resolve()
    # Upstream's nested cmd/batch invocations are not certified for shell
    # metacharacters or spaces in the checkout path. Refuse instead of guessing.
    require(not any(c.isspace() or c in '&|<>^%!"' for c in str(root)),
            "Use a checkout path without spaces or cmd metacharacters, e.g. G:/God-Hand-PC")
    vsroot = Path(vsroot).resolve(strict=True)
    require(not any(c in '&|<>^%!"\r\n' for c in str(vsroot)) and
            (vsroot / "VC/Auxiliary/Build/vcvars64.bat").is_file(), "Invalid MSVC/VSROOT environment")
    for name in ("git", "cmake", "ninja"):
        require(shutil.which(name) is not None, f"Missing prerequisite: {name}")
    pin = pc.load_pin(root)
    identity = pc.verify_disc(iso, pin["retail_profile"])
    dependencies = load_dependencies(root)
    workspace = contained(pc.private_dir(root), pc.private_dir(root) / workspace_name)
    workspace.mkdir(exist_ok=True)
    # Refuse a live OR unexplained stale lock. A client observation timeout never
    # authorizes another build. Inspect its PID/child receipt before manual recovery.
    lock = contained(workspace, workspace / "setup.lock")
    token = json.dumps({"pid": os.getpid(), "started_at": now(), "token": uuid.uuid4().hex})
    with lock.open("x", encoding="utf-8") as out:
        out.write(token)
    run, interrupted = None, False
    try:
        run = Run(workspace)
        run.record.update(disc=identity, upstream=pin, jobs=jobs, vsroot=str(vsroot),
                          dependency_lock_sha256=digest(root / "dependencies.json"),
                          tooling_sha256={name: digest(root / name) for name in ("pc.py", "setup_pc.py")},
                          continuation_revision=pc.git("rev-parse", "HEAD", cwd=root))
        run.save()
        source = contained(workspace, workspace / "upstream")
        pc.clone_pinned(pin["repository"], pin["revision"], source)
        deps = contained(workspace, workspace / "deps")
        deps.mkdir(exist_ok=True)
        for item in dependencies:
            destination = contained(deps, deps / (item["name"] + "-src"))
            pc.clone_pinned(item["repository"], item["revision"], destination)
            require(digest(destination / item["license"]["file"]) == item["license"]["sha256"],
                    "Dependency license receipt changed: " + item["name"])
        # Upstream removes its OWN staging trees. Refuse resolved path escapes
        # before invoking it; never pass original/evaluated workspaces as output.
        for relative in ("build", "build/generated_staging", "build/snr2/gen", "generated", "generated_modules", "out"):
            contained(source, source / relative)
        cache = contained(workspace, workspace / "disc/God Hand (USA).iso")
        cached = cached_disc(identity["path"], cache, pin["retail_profile"], pc.verify_disc)
        run.record.update(private_disc=cached, dependencies=dependencies)
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GODHAND_", "PS2X_"))}
        env.update(VSROOT=str(vsroot), GODHAND_JOBS=str(jobs), GODHAND_LOW_PRIORITY="1",
                   GODHAND_DEPS=str(deps), GODHAND_ALLOW_DOWNLOADS="0", GODHAND_ISO=str(cache))
        run.record["environment"] = {k: env[k] for k in ("VSROOT", "GODHAND_JOBS", "GODHAND_LOW_PRIORITY",
                                                       "GODHAND_DEPS", "GODHAND_ALLOW_DOWNLOADS", "GODHAND_ISO")}
        run.record["versions"] = {"python": sys.version, **{name: subprocess.check_output(
            [name, "--version"], text=True).splitlines()[0] for name in ("git", "cmake", "ninja")}}
        run.save()
        if not prepare_only:
            for name, command in build_steps(source, cache):
                run.step(name, command, source, env)
                if name == "boot-generate":
                    require(digest(source / "build/SLUS_215.03") == pin["retail_profile"]["boot_elf_sha256"],
                            "Extracted boot ELF identity mismatch")
                    require((source / "generated/register_functions.cpp").is_file(), "Missing generated boot registry")
                    run.record["generation_diagnostics"] = {"boot": generation_diagnostics(
                        source / "build/recomp.log", run.directory / "generation/boot.log")}
                if name == "overlay-extract":
                    run.record["overlays"] = overlay_manifest(source)
                if name == "overlay-generate":
                    for item in overlay_manifest(source):
                        module = item["name"][:-4]
                        require((source / f"generated_modules/{module}/{module}_pack.cpp").is_file(),
                                "Missing generated overlay pack")
                        run.record["generation_diagnostics"][module] = generation_diagnostics(
                            source / f"build/snr2/gen/{module}.recomp.log",
                            run.directory / f"generation/{module}.log")
                run.save()
                diagnostics = run.record.get("generation_diagnostics", {})
                if name in ("boot-generate", "overlay-generate") and any(
                        x["errors"] or x["unhandled"] for x in diagnostics.values()):
                    print("WARNING: generation reported translation diagnostics; logs retained, not a clean translation.",
                          flush=True)
            executable = source / "build/port/bin/godhand.exe"
            require(executable.is_file(), "Build returned without godhand.exe")
            run.record["executable"] = {"path": str(executable), "bytes": executable.stat().st_size,
                                        "sha256": digest(executable)}
            run.record["source_status_after"] = pc.git("status", "--porcelain", cwd=source)
            require(not run.record["source_status_after"], "Upstream source changed; review retained output")
        # Recheck the owner disc, not just the private copy, after all operations.
        pc.verify_disc(identity["path"], pin["retail_profile"])
        run.record.update(status="prepared" if prepare_only else "built-not-runtime-validated", ended_at=now())
        run.save()
        return {"receipt": str(run.directory / "receipt.json"), **run.record}
    except BaseException as error:
        interrupted = isinstance(error, (KeyboardInterrupt, SystemExit))
        if run:
            run.record.update(status="interrupted-or-failed", error=str(error), ended_at=now())
            run.save()
        raise
    finally:
        # Never unlock while our child may still be running after Ctrl+C.
        if not interrupted and (run is None or run.child is None or run.child.poll() is not None) and lock.exists() and lock.read_text(encoding="utf-8") == token:
            lock.unlink()
