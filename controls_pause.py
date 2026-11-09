"""Original GPL-3.0-only, checked experimental host-pause build variant.

Reuse the private build cache, but retain the operational source/executable.
No game generation or durable edit to a generated guest function occurs here.
"""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import sys
import uuid

import pc
import runtime_packs as packs
import setup_pc as build

PREFIX = "runtime/ps2xRuntime/src/lib/"
MODIFIED = {PREFIX + name for name in (
    "Kernel/EeScheduler.cpp", "ps2_runtime.cpp", "ps2_controls_screen.cpp", "ps2_audio.cpp")}
COPIES = {"adapter/" + name: PREFIX + "godhand_pc_controls/" + name for name in (
    "host_pause.hpp", "controls_probe.hpp", "controls_pause.inc")}
VERSIONS = ("v1", "audio-v2")
AUDIO_COPIES = dict(COPIES)
del AUDIO_COPIES["adapter/controls_pause.inc"]
AUDIO_COPIES.update({"adapter/audio_controls_pause.inc": PREFIX + "godhand_pc_controls/controls_pause.inc",
                     "adapter/audio_activity.hpp": PREFIX + "godhand_pc_controls/audio_activity.hpp"})


def layer_name(version):
    build.require(version in VERSIONS, "Unknown controls version; choose v1 or audio-v2")
    return "controls" if version == "v1" else "controls-audio-v2"


def integration(root, version="v1"):
    layer_name(version)
    filename = "controls_integration.json" if version == "v1" else "audio_controls_integration.json"
    copies = COPIES if version == "v1" else AUDIO_COPIES
    recipe = json.loads((Path(root) / "adapter" / filename).read_text(encoding="utf-8"))
    build.require(recipe["schema"] == 1 and recipe["upstream_revision"] == pc.load_pin(root)["revision"] and
                  recipe.get("version", "v1") == version and
                  len(recipe["files"]) == len(MODIFIED) and
                  {item["path"] for item in recipe["files"]} == MODIFIED and recipe["copies"] == copies,
                  "Unreviewed controls integration profile/paths")
    return recipe


def fingerprint(root, recipe):
    data = json.dumps(recipe, sort_keys=True, separators=(",", ":")).encode()
    data += packs.fingerprint(root, packs.integration(root)).encode()
    for path in sorted(recipe["copies"]):
        data += path.encode() + b"\0" + packs.normalized((Path(root) / path).read_bytes())
    return packs.sha(data)


def plan_sources(source, root, recipe):
    planned = {}
    for item in recipe["files"]:
        path = build.contained(source, Path(source) / item["path"])
        planned[path] = packs.transform(path.read_bytes(), item)
    for own, relative in recipe["copies"].items():
        path = build.contained(source, Path(source) / relative)
        build.require(not path.exists(), "Controls destination already exists; preserve/review it")
        planned[path] = packs.normalized((Path(root) / own).read_bytes())
    return planned


def copy_exclusive(source, destination):
    source, destination = Path(source), Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as src, destination.open("xb") as dst:
        shutil.copyfileobj(src, dst, 1024 * 1024)
    build.require(build.digest(source) == build.digest(destination), "Private copy differs")
    return {"path": str(destination), "bytes": destination.stat().st_size, "sha256": build.digest(destination)}


def baseline_identity(record):
    return {key: record[key] for key in ("source_revision", "adapter_fingerprint", "executable")}


def verified_install(root, name, version="v1"):
    layer_id = layer_name(version)
    base = packs.verified_install(root, name)
    workspace = packs.workspace_path(root, name)
    layer = build.contained(workspace, workspace / layer_id)
    pointer = json.loads((layer / "installed.json").read_text(encoding="utf-8"))
    run_id = pointer["run"]
    build.require(type(run_id) is str and re.fullmatch(r"[a-f0-9]{32}", run_id), "Invalid controls run pointer")
    run = build.contained(layer, layer / "runs" / run_id)
    record = json.loads((run / "receipt.json").read_text(encoding="utf-8"))
    recipe = integration(root, version)
    build.require(record["status"] == "installed-not-runtime-validated" and record["baseline_restored"] and
                  record.get("controls_version", "v1") == version and
                  record["controls_fingerprint"] == fingerprint(root, recipe) and
                  record["base_identity"] == baseline_identity(base), "Controls install/base version differs")
    source = build.contained(run, run / "source")
    pc.inspect_checkout(source, base["source_revision"], record["source_revision"])
    changed = set(pc.git("diff", "--name-only", base["source_revision"], record["source_revision"], cwd=source).splitlines())
    build.require(changed == MODIFIED | set(recipe["copies"].values()), "Unreviewed controls derived source paths")
    # Recompute expected content from the *verified operational base*, not just
    # arbitrary hashes in the variant receipt. This also checks regeneration drift.
    planned = plan_sources(workspace / "upstream", root, recipe)
    expected = dict(base["source_files"], **{
        p.relative_to(workspace / "upstream").as_posix(): packs.sha(raw) for p, raw in planned.items()})
    build.require(record["source_files"] == expected, "Composite source manifest differs")
    for relative, digest in expected.items():
        path = build.contained(source, source / relative)
        build.require(packs.sha(packs.normalized(path.read_bytes())) == digest, "Controls source content differs")
    exe = build.contained(run, run / "native/godhand.exe")
    build.require(record["executable"]["path"] == str(exe) and
                  build.digest(exe) == record["executable"]["sha256"], "Controls executable identity differs")
    return dict(record, receipt=str(run / "receipt.json"),
                controls_adoption_executable=base["executable"]["path"])


def restore_baseline(source, base, run, original_branch):
    """Only restore a clean, exactly owned derived checkout after its child stops.

    Never reset dirty source. Preserve relinked/failed output before restoration;
    the saved PDB may predate this work and is NOT claimed to match the base exe.
    """
    build.require(run.child is None or run.child.poll() is not None, "Live build prevents restoration")
    pc.inspect_checkout(source, base["source_revision"], run.record["source_revision"])
    for name, backup in run.record["baseline_backups"].items():
        path = source / "build/port/bin" / name
        if path.exists():
            run.record.setdefault("relinked_outputs", {})[name] = copy_exclusive(path, run.directory / "relinked" / name)
            run.save()
        build.require(build.digest(backup["path"]) == backup["sha256"], "Baseline backup differs; restoration refused")
        with Path(backup["path"]).open("rb") as src, path.open("wb") as dst:
            shutil.copyfileobj(src, dst, 1024 * 1024)
        build.require(build.digest(path) == backup["sha256"], "Baseline restoration differs")
    if original_branch == "HEAD":
        pc.git("checkout", "--detach", base["source_revision"], cwd=source)
    else:
        build.require(pc.git("rev-parse", original_branch, cwd=source) == base["source_revision"],
                      "Original branch moved; preserve/review before restoration")
        pc.git("checkout", original_branch, cwd=source)
    # Caller additionally re-verifies the operational public installation.
    run.record["baseline_restored"] = True
    run.save()


def install(root, name, version="v1"):
    layer_id = layer_name(version)
    root = Path(root).resolve()
    build.require(os.name == "nt", "Controls variant currently requires Windows/MSVC")
    workspace = packs.workspace_path(root, name)
    layer = build.contained(workspace, workspace / layer_id)
    layer.mkdir(exist_ok=True)
    locks, run, mutated, terminal = [], None, False, True
    token = json.dumps({"pid": os.getpid(), "token": uuid.uuid4().hex, "at": build.now()})
    try:
        # Existing setup/pack installers and launchers honor this global lock.
        # A stale lock is evidence to inspect, never permission to restart.
        for path in (workspace / "setup.lock", layer / "install.lock"):
            with path.open("x", encoding="utf-8") as stream: stream.write(token)
            locks.append(path)
        build.require(not (workspace / "packs/install.lock").exists(), "Pack installer requires inspection")
        if (layer / "installed.json").exists():
            return verified_install(root, name, version)
        build.require(not (layer / "attempt.json").exists(), "Previous controls attempt requires review; retained evidence")
        tasks = subprocess.check_output(["tasklist", "/FI", "IMAGENAME eq godhand.exe", "/NH"], text=True)
        build.require("godhand.exe" not in tasks.lower(), "Close the game before building a variant")
        base = packs.verified_install(root, name)
        recipe = integration(root, version)
        source = build.contained(workspace, workspace / "upstream")
        planned = plan_sources(source, root, recipe)
        setup = json.loads(Path(base["setup_receipt"]).read_text(encoding="utf-8"))
        pc.verify_disc(setup["disc"]["path"], pc.load_pin(root)["retail_profile"])
        original_branch = pc.git("rev-parse", "--abbrev-ref", "HEAD", cwd=source)
        run = build.Run(layer)
        run.record.update(base_identity=baseline_identity(base), baseline_restored=False,
                          controls_version=version,
                          adapter_fingerprint=base["adapter_fingerprint"], controls_fingerprint=fingerprint(root, recipe),
                          tooling_revision=pc.git("rev-parse", "HEAD", cwd=root),
                          tooling_dirty=bool(pc.git("status", "--porcelain", cwd=root)),
                          setup_receipt=base["setup_receipt"], original_branch=original_branch,
                          scope="Experimental original host integration; reused private build cache, not a fresh installer/game-fidelity proof")
        run.record["baseline_backups"] = {}
        for filename in ("godhand.exe", "godhand.pdb"):
            path = source / "build/port/bin" / filename
            if path.exists():
                run.record["baseline_backups"][filename] = copy_exclusive(path, run.directory / "baseline" / filename)
        run.save()
        with (layer / "attempt.json").open("x", encoding="utf-8") as stream:
            json.dump({"receipt": str(run.directory / "receipt.json")}, stream)
        branch = "codex/controls-" + version + "-" + run.directory.name
        pc.git("checkout", "-b", branch, cwd=source)
        mutated = True
        for path, data in planned.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        added = {p.relative_to(source).as_posix(): packs.sha(raw) for p, raw in planned.items()}
        run.record["source_files"] = dict(base["source_files"], **added)
        pc.git("add", "--", *added, cwd=source)
        pc.git("-c", "user.name=God Hand PC local tooling", "-c", "user.email=local@example.invalid",
               "commit", "-m", "Install original opt-in host controls-pause variant", cwd=source)
        run.record["source_revision"] = pc.git("rev-parse", "HEAD", cwd=source)
        run.save()
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GODHAND_", "PS2X_"))}
        env.update(setup["environment"])
        try:
            run.step("controls-configure", [sys.executable, "-I", "build.py", "configure"], source, env)
            # Explicitly invalidate the four host units, including any private
            # trial objects in the reused build cache. Never touch guest sources.
            for relative in MODIFIED: os.utime(source / relative, None)
            run.step("controls-build", [sys.executable, "-I", "build.py", "build"], source, env)
            native = run.directory / "native"
            run.record["executable"] = copy_exclusive(source / "build/port/bin/godhand.exe", native / "godhand.exe")
            for filename in ("godhand.pdb", "godhand.ini"):
                path = source / "build/port/bin" / filename
                if path.exists():
                    run.record.setdefault("variant_sidecars", {})[filename] = copy_exclusive(path, native / filename)
            # Keep a separately clean source worktree for composite verification;
            # ignored generated game code/assets remain in the original workspace.
            pc.git("worktree", "add", "--detach", run.directory / "source", run.record["source_revision"], cwd=source)
        finally:
            terminal = run.child is None or run.child.poll() is not None
            if terminal:
                restore_baseline(source, base, run, original_branch)
                packs.verified_install(root, name)
        pc.verify_disc(setup["disc"]["path"], pc.load_pin(root)["retail_profile"])
        run.record.update(status="installed-not-runtime-validated", ended_at=build.now())
        run.save()
        with (layer / "installed.json").open("x", encoding="utf-8") as stream:
            json.dump({"run": run.directory.name}, stream, indent=2)
        return verified_install(root, name, version)
    except BaseException as error:
        if run:
            terminal = run.child is None or run.child.poll() is not None
            run.record.update(status="failed-or-interrupted", error=str(error), ended_at=build.now())
            run.save()
        raise
    finally:
        safe = terminal and (not mutated or (run and run.record.get("baseline_restored")))
        if safe:
            for lock in reversed(locks):
                if lock.exists() and lock.read_text(encoding="utf-8") == token: lock.unlink()
