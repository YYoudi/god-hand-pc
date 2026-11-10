"""Original GPL checked ordered video-menu layer over frozen GPU/audio-v3.

No game code, generation or automatic upstream vendoring. Old recipes are immutable.
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
import setup_pc as build
import runtime_packs as packs
import controls_pause as variants
import hd_textures as hd

VERSION = "native-menu-v1"
PARENT = "gpu-audio-v3"
RUNTIME = "runtime/ps2xRuntime/src/lib/ps2_runtime.cpp"
CMAKE = "runtime/ps2xRuntime/CMakeLists.txt"
OWN_MODIFIED = {RUNTIME, CMAKE}
COPIES = {"adapter/" + name: "runtime/ps2xRuntime/src/lib/godhand_pc_video/" + name for name in (
    "video_menu_model.hpp", "video_menu_protocol.hpp", "video_menu_io.hpp", "video_menu_io.cpp",
    "video_menu_client.hpp", "video_menu_view.hpp", "video_menu_host.hpp", "video_menu_probe.hpp",
    "video_menu_factory.hpp")}


def integration(root):
    recipe = json.loads((Path(root) / "adapter/native_menu_integration.json").read_text(encoding="utf-8"))
    parent = hd.integration(root, PARENT)
    build.require(recipe["schema"] == 1 and recipe["version"] == VERSION and
                  recipe["upstream_revision"] == pc.load_pin(root)["revision"] and
                  recipe["parent_fingerprint"] == hd.fingerprint(root, parent) and
                  recipe["copies"] == COPIES and len(recipe["files"]) == 2 and
                  {x["path"] for x in recipe["files"]} == OWN_MODIFIED,
                  "Unreviewed native-menu parent/paths")
    return recipe


def fingerprint(root, recipe):
    data = json.dumps(recipe, sort_keys=True, separators=(",", ":")).encode()
    for name in sorted(COPIES):
        data += name.encode() + b"\0" + packs.normalized((Path(root) / name).read_bytes())
    return packs.sha(data)


def plan_sources(source, root, recipe):
    source = Path(source)
    # Deliberate ORDERED composition. Runtime.cpp already has audio-v2 edits;
    # its next preimage is the exact parent postimage, not the operational base.
    planned = hd.plan_sources(source, root, hd.integration(root, PARENT))
    for item in recipe["files"]:
        path = build.contained(source, source / item["path"])
        planned[path] = packs.transform(planned[path] if path in planned else path.read_bytes(), item)
    for own, relative in COPIES.items():
        path = build.contained(source, source / relative)
        build.require(not path.exists() and path not in planned, "Menu helper destination exists; preserve/review")
        planned[path] = packs.normalized((Path(root) / own).read_bytes())
    return planned


def verified_install(root, name):
    base = packs.verified_install(root, name)
    workspace = packs.workspace_path(root, name)
    layer = build.contained(workspace, workspace / VERSION)
    pointer = json.loads((layer / "installed.json").read_text(encoding="utf-8"))
    run_id = pointer["run"]
    build.require(type(run_id) is str and re.fullmatch("[a-f0-9]{32}", run_id), "Invalid native-menu run")
    run = build.contained(layer, layer / "runs" / run_id)
    record = json.loads((run / "receipt.json").read_text(encoding="utf-8"))
    recipe = integration(root)
    build.require(record["status"] == "installed-not-runtime-validated" and record["baseline_restored"] and
                  record["menu_version"] == VERSION and record["menu_fingerprint"] == fingerprint(root, recipe) and
                  record["parent_fingerprint"] == recipe["parent_fingerprint"] and
                  record["base_identity"] == variants.baseline_identity(base), "Native-menu identity differs")
    source = build.contained(run, run / "source")
    pc.inspect_checkout(source, base["source_revision"], record["source_revision"])
    changed = set(pc.git("diff", "--name-only", base["source_revision"], record["source_revision"], cwd=source).splitlines())
    allowed = hd.modified(PARENT) | OWN_MODIFIED | set(hd.copies(PARENT).values()) | set(COPIES.values())
    build.require(changed == allowed, "Unreviewed native-menu source paths")
    planned = plan_sources(workspace / "upstream", root, recipe)
    expected = dict(base["source_files"], **{
        p.relative_to(workspace / "upstream").as_posix(): packs.sha(raw) for p, raw in planned.items()})
    build.require(record["source_files"] == expected, "Native-menu source manifest differs")
    for relative, digest in expected.items():
        path = build.contained(source, source / relative)
        build.require(packs.sha(packs.normalized(path.read_bytes())) == digest, "Native-menu source content differs")
    exe = build.contained(run, run / "native/godhand.exe")
    build.require(record["executable"]["path"] == str(exe) and
                  build.digest(exe) == record["executable"]["sha256"], "Native-menu executable differs")
    return dict(record, receipt=str(run / "receipt.json"), controls_adoption_executable=base["executable"]["path"])


def install(root, name):
    root = Path(root).resolve()
    build.require(os.name == "nt", "Native-menu variant currently requires Windows/MSVC")
    workspace = packs.workspace_path(root, name)
    layer = build.contained(workspace, workspace / VERSION)
    layer.mkdir(exist_ok=True)
    locks, run, mutated, terminal = [], None, False, True
    token = json.dumps({"pid": os.getpid(), "token": uuid.uuid4().hex, "at": build.now()})
    try:
        for path in (workspace / "setup.lock", layer / "install.lock"):
            with path.open("x", encoding="utf-8") as stream: stream.write(token)
            locks.append(path)
        build.require(not (workspace / "packs/install.lock").exists(), "Pack installer requires inspection")
        if (layer / "installed.json").exists(): return verified_install(root, name)
        build.require(not (layer / "attempt.json").exists(), "Previous menu attempt retained; inspect before retry")
        build.require(shutil.disk_usage(workspace).free >= 8 * 1024**3, "Native build requires at least8GiB free")
        build.require_no_game(subprocess.check_output)
        base = packs.verified_install(root, name)
        recipe = integration(root)
        source = build.contained(workspace, workspace / "upstream")
        planned = plan_sources(source, root, recipe)
        setup = json.loads(Path(base["setup_receipt"]).read_text(encoding="utf-8"))
        pc.verify_disc(setup["disc"]["path"], pc.load_pin(root)["retail_profile"])
        original_branch = pc.git("rev-parse", "--abbrev-ref", "HEAD", cwd=source)
        run = build.Run(layer)
        run.record.update(base_identity=variants.baseline_identity(base), baseline_restored=False,
                          menu_version=VERSION, menu_fingerprint=fingerprint(root, recipe),
                          parent_fingerprint=recipe["parent_fingerprint"],
                          adapter_fingerprint=base["adapter_fingerprint"],
                          tooling_revision=pc.git("rev-parse", "HEAD", cwd=root),
                          tooling_dirty=bool(pc.git("status", "--porcelain", cwd=root)),
                          setup_receipt=base["setup_receipt"], original_branch=original_branch,
                          scope="Experimental original native menu over ordered GPU/audio parent; reused private cache, not fresh generation or full fidelity",
                          baseline_backups={})
        for filename in ("godhand.exe", "godhand.pdb"):
            path = source / "build/port/bin" / filename
            if path.exists():
                run.record["baseline_backups"][filename] = variants.copy_exclusive(path, run.directory / "baseline" / filename)
        run.save()
        with (layer / "attempt.json").open("x", encoding="utf-8") as stream:
            json.dump({"receipt": str(run.directory / "receipt.json")}, stream)
        pc.git("checkout", "-b", "codex/" + VERSION + "-" + run.directory.name, cwd=source)
        mutated = True
        for path, data in planned.items():
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
        added = {p.relative_to(source).as_posix(): packs.sha(raw) for p, raw in planned.items()}
        run.record["source_files"] = dict(base["source_files"], **added)
        pc.git("add", "--", *added, cwd=source)
        pc.git("-c", "user.name=God Hand PC local tooling", "-c", "user.email=local@example.invalid",
               "commit", "-m", "Install original ordered native-video menu host layer", cwd=source)
        run.record["source_revision"] = pc.git("rev-parse", "HEAD", cwd=source); run.save()
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GODHAND_", "PS2X_"))}
        env.update(setup["environment"])
        try:
            run.step("menu-configure", [sys.executable, "-I", "build.py", "configure"], source, env)
            # The shared cache held a different variant even after source restore.
            for relative in variants.MODIFIED | {hd.GPU}: os.utime(source / relative, None)
            run.step("menu-build", [sys.executable, "-I", "build.py", "build"], source, env)
            run.record["executable"] = variants.copy_exclusive(source / "build/port/bin/godhand.exe", run.directory / "native/godhand.exe")
            for filename in ("godhand.pdb", "godhand.ini"):
                path = source / "build/port/bin" / filename
                if path.exists():
                    run.record.setdefault("variant_sidecars", {})[filename] = variants.copy_exclusive(path, run.directory / "native" / filename)
            pc.git("worktree", "add", "--detach", run.directory / "source", run.record["source_revision"], cwd=source)
        finally:
            terminal = run.child is None or run.child.poll() is not None
            if terminal:
                variants.restore_baseline(source, base, run, original_branch)
                packs.verified_install(root, name)
        pc.verify_disc(setup["disc"]["path"], pc.load_pin(root)["retail_profile"])
        run.record.update(status="installed-not-runtime-validated", ended_at=build.now()); run.save()
        with (layer / "installed.json").open("x", encoding="utf-8") as stream:
            json.dump({"run": run.directory.name}, stream, indent=2)
        return verified_install(root, name)
    except BaseException as error:
        if run:
            terminal = run.child is None or run.child.poll() is not None
            run.record.update(status="failed-or-interrupted", error=str(error), ended_at=build.now()); run.save()
        raise
    finally:
        if terminal and (not mutated or (run and run.record.get("baseline_restored"))):
            for path in reversed(locks):
                if path.exists() and path.read_text(encoding="utf-8") == token: path.unlink()
