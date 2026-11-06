"""Original GPL-3.0-only integration of the bounded native resource bridge."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import uuid

import pc
import setup_pc as build

MODIFIED = {
    "src/CMakeLists.txt", "runtime/ps2xRuntime/src/lib/ps2_cd_image.cpp",
    "runtime/ps2xRuntime/src/lib/ps2_iop_host.cpp", "runtime/ps2xRuntime/src/lib/ps2_iop_host.h",
    "runtime/ps2xRuntime/src/lib/Kernel/Stubs/Helpers/Support.h",
}
COPIES = {
    "adapter/overlay.hpp": "runtime/ps2xRuntime/src/lib/godhand_pc_packs/overlay.hpp",
    "adapter/settings.hpp": "runtime/ps2xRuntime/src/lib/godhand_pc_packs/settings.hpp",
    "adapter/bridge.hpp": "runtime/ps2xRuntime/src/lib/godhand_pc_packs/bridge.hpp",
    "adapter/bridge.cpp": "src/godhand_pc_pack_bridge.cpp",
}


def normalized(raw):
    raw.decode("utf-8")
    build.require(b"\0" not in raw and len(raw) <= 4 * 1024 * 1024, "Invalid host source text")
    return raw.replace(b"\r\n", b"\n")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def transform(raw, record):
    raw = normalized(raw)
    build.require(sha(raw) == record["before_sha256"], "Pinned host source preimage differs")
    previous, positions = 0, set()
    for edit in record["edits"]:
        start, end = edit["start"], edit["end"]
        build.require(type(start) is int and type(end) is int and
                      previous <= start <= end <= len(raw) and (start, end) not in positions,
                      "Invalid/overlapping integration edit")
        normalized(edit["insert"].encode("utf-8"))
        previous = end
        positions.add((start, end))
    result = raw
    for edit in reversed(record["edits"]):
        result = result[:edit["start"]] + edit["insert"].encode("utf-8") + result[edit["end"]:]
    normalized(result)
    build.require(sha(result) == record["after_sha256"], "Derived host source digest differs")
    return result


def integration(root):
    root = Path(root)
    recipe = json.loads((root / "adapter/integration.json").read_text(encoding="utf-8"))
    build.require(recipe["schema"] == 1 and recipe["upstream_revision"] == pc.load_pin(root)["revision"],
                  "Unreviewed integration profile")
    build.require(len(recipe["files"]) == len(MODIFIED) and
                  {x["path"] for x in recipe["files"]} == MODIFIED and recipe["copies"] == COPIES,
                  "Integration file allowlist differs")
    return recipe


def fingerprint(root, recipe):
    data = json.dumps(recipe, sort_keys=True, separators=(",", ":")).encode()
    for name in sorted(COPIES):
        data += name.encode() + b"\0" + normalized((Path(root) / name).read_bytes())
    return sha(data)


def plan_sources(source, root, recipe):
    """Validate every preimage before writing anything; never patch generated code."""
    planned = {}
    for record in recipe["files"]:
        path = build.contained(source, Path(source) / record["path"])
        planned[path] = transform(path.read_bytes(), record)
    for own, destination in COPIES.items():
        path = build.contained(source, Path(source) / destination)
        build.require(not path.exists(), "Original bridge destination already exists; preserve/review it")
        planned[path] = normalized((Path(root) / own).read_bytes())
    return planned


def workspace_path(root, name):
    build.require(type(name) is str and re.fullmatch(r"retail-[a-z0-9][a-z0-9-]{0,40}", name),
                  "Workspace name must be a single retail-* identifier")
    return build.contained(pc.private_dir(root), pc.private_dir(root) / name)


def verified_install(root, name):
    workspace = workspace_path(root, name)
    record = json.loads((workspace / "packs/installed.json").read_text(encoding="utf-8"))
    recipe = integration(root)
    build.require(record["adapter_fingerprint"] == fingerprint(root, recipe), "Installed adapter version differs")
    source = build.contained(workspace, workspace / "upstream")
    pc.inspect_checkout(source, pc.load_pin(root)["revision"], record["source_revision"])
    exe = build.contained(source, source / "build/port/bin/godhand.exe")
    build.require(str(exe) == record["executable"]["path"] and build.digest(exe) == record["executable"]["sha256"],
                  "Installed executable identity differs")
    for relative, expected in record["source_files"].items():
        build.require(relative in MODIFIED | set(COPIES.values()), "Unexpected installed source path")
        build.require(sha(normalized(build.contained(source, source / relative).read_bytes())) == expected,
                      "Installed source content differs")
    return record


def install(root, name):
    root = Path(root).resolve()
    build.require(os.name == "nt", "Native bridge build currently requires Windows/MSVC")
    workspace = workspace_path(root, name)
    build.require(not (workspace / "setup.lock").exists(), "Setup job/lock requires inspection first")
    packages = build.contained(workspace, workspace / "packs")
    packages.mkdir(exist_ok=True)
    lock = packages / "install.lock"
    token = json.dumps({"pid": os.getpid(), "token": uuid.uuid4().hex, "started_at": build.now()})
    with lock.open("x", encoding="utf-8") as out:
        out.write(token)
    run, interrupted = None, False
    try:
        if (packages / "installed.json").exists():
            return verified_install(root, name)
        # Do not silently rerun a failed or interrupted source mutation.
        build.require(not (packages / "attempt.json").exists(), "Previous installer attempt requires review; evidence retained")
        tasklist = subprocess.check_output(["tasklist", "/FI", "IMAGENAME eq godhand.exe", "/NH"], text=True)
        build.require("godhand.exe" not in tasklist.lower(), "Close the running game before relinking")
        records = []
        for path in (workspace / "runs").glob("*/receipt.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("status") == "built-not-runtime-validated":
                records.append((data["ended_at"], path, data))
        build.require(bool(records), "No successful personal-disc setup receipt")
        _, setup_path, setup = max(records, key=lambda x: x[0])
        pin = pc.load_pin(root)
        build.require(setup["upstream"]["revision"] == pin["revision"], "Setup upstream profile differs")
        pc.verify_disc(setup["disc"]["path"], pin["retail_profile"])
        source = build.contained(workspace, workspace / "upstream")
        pc.inspect_checkout(source, pin["revision"], pin["revision"])
        recipe = integration(root)
        planned = plan_sources(source, root, recipe)
        exe = build.contained(source, source / "build/port/bin/godhand.exe")
        build.require(build.digest(exe) == setup["executable"]["sha256"], "Baseline executable differs")
        backup = build.contained(workspace, workspace / "baseline-binary/godhand.exe")
        backup.parent.mkdir(exist_ok=True)
        if not backup.exists():
            with exe.open("rb") as src, backup.open("xb") as dst:
                shutil.copyfileobj(src, dst, 1024 * 1024)
        build.require(build.digest(backup) == setup["executable"]["sha256"], "Baseline backup differs")
        run = build.Run(packages)
        run.record.update(setup_receipt=str(setup_path), baseline=setup["executable"], backup=str(backup),
                          adapter_fingerprint=fingerprint(root, recipe),
                          tooling_revision=pc.git("rev-parse", "HEAD", cwd=root),
                          source_files={str(p.relative_to(source)).replace("\\", "/"): sha(raw) for p, raw in planned.items()})
        run.save()
        (packages / "attempt.json").write_text(json.dumps({"receipt": str(run.directory / "receipt.json")}), encoding="utf-8")
        pc.git("checkout", "-b", "codex/named-resource-packs", cwd=source)
        for path, raw in planned.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        pc.git("add", "--", *run.record["source_files"], cwd=source)
        pc.git("-c", "user.name=God Hand PC local tooling", "-c", "user.email=local@example.invalid",
               "commit", "-m", "Install original bounded named-resource host bridge", cwd=source)
        run.record["source_revision"] = pc.git("rev-parse", "HEAD", cwd=source)
        run.save()
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GODHAND_", "PS2X_"))}
        env.update(setup["environment"])
        run.step("pack-configure", [os.sys.executable, "-I", "build.py", "configure"], source, env)
        run.step("pack-build", [os.sys.executable, "-I", "build.py", "build"], source, env)
        pc.inspect_checkout(source, pin["revision"], run.record["source_revision"])
        run.record.update(status="installed-not-runtime-validated", ended_at=build.now(),
                          executable={"path": str(exe), "bytes": exe.stat().st_size, "sha256": build.digest(exe)})
        pc.verify_disc(setup["disc"]["path"], pin["retail_profile"])
        run.save()
        # Keep the complete per-run evidence; registry is a small verified pointer.
        installed = dict(run.record, receipt=str(run.directory / "receipt.json"))
        with (packages / "installed.json").open("x", encoding="utf-8") as out:
            json.dump(installed, out, indent=2)
        return installed
    except BaseException as error:
        interrupted = isinstance(error, (KeyboardInterrupt, SystemExit))
        if run:
            run.record.update(status="interrupted-or-failed", error=str(error), ended_at=build.now())
            run.save()
        raise
    finally:
        if not interrupted and (run is None or run.child is None or run.child.poll() is not None) and lock.exists() and lock.read_text() == token:
            lock.unlink()
