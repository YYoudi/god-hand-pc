"""Original GPL checked additive hd-v1 host variant; no game code generation."""
from pathlib import Path
import json
import os
import re
import subprocess
import sys
import uuid

import pc
import runtime_packs as packs
import controls_pause as variants
import setup_pc as build

VERSION = "hd-v1"
PREFIX = "runtime/ps2xRuntime/src/lib/"
GPU = PREFIX + "gs/gpu/gs_gpu_backend.cpp"
MODIFIED = {"src/CMakeLists.txt", GPU}
COPIES = {"adapter/hd_texture.hpp": PREFIX + "godhand_pc_hd/hd_texture.hpp",
          "adapter/hd_runtime.hpp": PREFIX + "godhand_pc_hd/runtime.hpp",
          "adapter/hd_runtime.inc": PREFIX + "godhand_pc_hd/runtime.inc",
          "adapter/hd_bridge.cpp": "src/godhand_pc_hd_bridge.cpp"}


def integration(root):
    recipe = json.loads((Path(root)/"adapter/hd_integration.json").read_text(encoding="utf-8"))
    build.require(recipe["schema"] == 1 and recipe["version"] == VERSION and
                  recipe["upstream_revision"] == pc.load_pin(root)["revision"] and
                  len(recipe["files"]) == len(MODIFIED) and
                  {x["path"] for x in recipe["files"]} == MODIFIED and recipe["copies"] == COPIES,
                  "Unreviewed HD integration profile/paths")
    return recipe


def fingerprint(root, recipe):
    data = json.dumps(recipe, sort_keys=True, separators=(",", ":")).encode()
    data += packs.fingerprint(root, packs.integration(root)).encode()
    for name in sorted(recipe["copies"]):
        data += name.encode() + b"\0" + packs.normalized((Path(root)/name).read_bytes())
    return packs.sha(data)


def plan_sources(source, root, recipe):
    # Same exact-preimage/contained-copy rule, without changing the old variants.
    return variants.plan_sources(source, root, recipe)


def verified_install(root, name):
    base = packs.verified_install(root, name)
    workspace = packs.workspace_path(root, name)
    layer = build.contained(workspace, workspace/VERSION)
    pointer = json.loads((layer/"installed.json").read_text(encoding="utf-8"))
    run_id = pointer["run"]
    build.require(type(run_id) is str and re.fullmatch(r"[a-f0-9]{32}", run_id), "Invalid HD run pointer")
    run = build.contained(layer, layer/"runs"/run_id)
    record = json.loads((run/"receipt.json").read_text(encoding="utf-8"))
    recipe = integration(root)
    build.require(record["status"] == "installed-not-runtime-validated" and record["baseline_restored"] and
                  record["hd_version"] == VERSION and record["hd_fingerprint"] == fingerprint(root, recipe) and
                  record["base_identity"] == variants.baseline_identity(base), "HD install/base identity differs")
    source = build.contained(run, run/"source")
    pc.inspect_checkout(source, base["source_revision"], record["source_revision"])
    changed = set(pc.git("diff", "--name-only", base["source_revision"], record["source_revision"], cwd=source).splitlines())
    build.require(changed == MODIFIED | set(recipe["copies"].values()), "Unreviewed HD derived paths")
    planned = plan_sources(workspace/"upstream", root, recipe)
    expected = dict(base["source_files"], **{
        p.relative_to(workspace/"upstream").as_posix(): packs.sha(raw) for p, raw in planned.items()})
    build.require(record["source_files"] == expected, "HD composite source manifest differs")
    for relative, digest in expected.items():
        path = build.contained(source, source/relative)
        build.require(packs.sha(packs.normalized(path.read_bytes())) == digest, "HD source content differs")
    exe = build.contained(run, run/"native/godhand.exe")
    build.require(record["executable"]["path"] == str(exe) and
                  build.digest(exe) == record["executable"]["sha256"], "HD executable identity differs")
    return dict(record, receipt=str(run/"receipt.json"), controls_adoption_executable=base["executable"]["path"])


def install(root, name):
    root = Path(root).resolve()
    build.require(os.name == "nt", "HD variant currently requires Windows/MSVC")
    workspace = packs.workspace_path(root, name)
    layer = build.contained(workspace, workspace/VERSION)
    layer.mkdir(exist_ok=True)
    locks, run, mutated, terminal = [], None, False, True
    token = json.dumps({"pid": os.getpid(), "token": uuid.uuid4().hex, "at": build.now()})
    try:
        for path in (workspace/"setup.lock", layer/"install.lock"):
            with path.open("x", encoding="utf-8") as stream: stream.write(token)
            locks.append(path)
        build.require(not (workspace/"packs/install.lock").exists(), "Pack installer requires inspection")
        if (layer/"installed.json").exists(): return verified_install(root, name)
        build.require(not (layer/"attempt.json").exists(), "Previous HD attempt retained; inspect before retry")
        build.require_no_game(subprocess.check_output)
        base = packs.verified_install(root, name)
        recipe = integration(root)
        source = build.contained(workspace, workspace/"upstream")
        planned = plan_sources(source, root, recipe)
        setup = json.loads(Path(base["setup_receipt"]).read_text(encoding="utf-8"))
        pc.verify_disc(setup["disc"]["path"], pc.load_pin(root)["retail_profile"])
        original_branch = pc.git("rev-parse", "--abbrev-ref", "HEAD", cwd=source)
        run = build.Run(layer)
        run.record.update(base_identity=variants.baseline_identity(base), baseline_restored=False,
                          hd_version=VERSION, adapter_fingerprint=base["adapter_fingerprint"],
                          hd_fingerprint=fingerprint(root, recipe), tooling_revision=pc.git("rev-parse", "HEAD", cwd=root),
                          tooling_dirty=bool(pc.git("status", "--porcelain", cwd=root)),
                          setup_receipt=base["setup_receipt"], original_branch=original_branch,
                          scope="Experimental checked HD host layer; reused private build cache, not fresh generation or full fidelity",
                          baseline_backups={})
        for filename in ("godhand.exe", "godhand.pdb"):
            path = source/"build/port/bin"/filename
            if path.exists():
                run.record["baseline_backups"][filename] = variants.copy_exclusive(path, run.directory/"baseline"/filename)
        run.save()
        with (layer/"attempt.json").open("x", encoding="utf-8") as stream:
            json.dump({"receipt": str(run.directory/"receipt.json")}, stream)
        pc.git("checkout", "-b", "codex/hd-v1-" + run.directory.name, cwd=source)
        mutated = True
        for path, data in planned.items():
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
        added = {p.relative_to(source).as_posix(): packs.sha(raw) for p, raw in planned.items()}
        run.record["source_files"] = dict(base["source_files"], **added)
        pc.git("add", "--", *added, cwd=source)
        pc.git("-c", "user.name=God Hand PC local tooling", "-c", "user.email=local@example.invalid",
               "commit", "-m", "Install original opt-in larger-texture host variant", cwd=source)
        run.record["source_revision"] = pc.git("rev-parse", "HEAD", cwd=source); run.save()
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GODHAND_", "PS2X_"))}
        env.update(setup["environment"])
        try:
            run.step("hd-configure", [sys.executable, "-I", "build.py", "configure"], source, env)
            # Flush other earlier private host variants from the shared object cache.
            for relative in variants.MODIFIED | {GPU}: os.utime(source/relative, None)
            run.step("hd-build", [sys.executable, "-I", "build.py", "build"], source, env)
            run.record["executable"] = variants.copy_exclusive(source/"build/port/bin/godhand.exe", run.directory/"native/godhand.exe")
            for filename in ("godhand.pdb", "godhand.ini"):
                path = source/"build/port/bin"/filename
                if path.exists():
                    run.record.setdefault("variant_sidecars", {})[filename] = variants.copy_exclusive(path, run.directory/"native"/filename)
            pc.git("worktree", "add", "--detach", run.directory/"source", run.record["source_revision"], cwd=source)
        finally:
            terminal = run.child is None or run.child.poll() is not None
            if terminal:
                variants.restore_baseline(source, base, run, original_branch)
                packs.verified_install(root, name)
        pc.verify_disc(setup["disc"]["path"], pc.load_pin(root)["retail_profile"])
        run.record.update(status="installed-not-runtime-validated", ended_at=build.now()); run.save()
        with (layer/"installed.json").open("x", encoding="utf-8") as stream:
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
