"""Original GPL-3.0-only checked native launcher and named-pack fallback."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import uuid

import pc
import resources
import profiles
import runtime_packs
import controls_pause as pause
import hd_textures as hd
import hd_packs
import setup_pc as build
import user_data
import video_settings as video
import native_menu as menu
import video_menu_channel as menu_channel


def clean_environment(environment):
    return {k: v for k, v in environment.items() if not k.startswith(("GODHAND_", "PS2X_"))}


def runtime_command(executable, iso, headless, seconds):
    # A missing CLI limit must not inherit a generated diagnostic INI timeout.
    return [str(executable), "--iso", str(iso), "--headless" if headless else "--window",
            "--time-limit", str(0 if seconds is None else seconds)]


def controls_pause_environment(enabled):
    build.require(type(enabled) is bool, "controls-pause must be a boolean")
    # Explicit zero overrides INI pass-through too, not just inherited variables.
    # Public launches never activate the mutating UI probe or its field delay.
    return {"GODHAND_PC_CONTROLS_PAUSE": "1" if enabled else "0",
            "GODHAND_PC_CONTROLS_PROBE": "0", "GODHAND_PC_CONTROLS_PROBE_FIELD": "0"}


def pack_protocol(iso, manifest, directory, strict=False):
    """Freeze only original pack bytes; never extract image pixels from the ISO."""
    if manifest is None:
        return {"mode": "original"}, {}
    try:
        with Path(iso).open("rb") as disc:
            plan = resources.compile_pack(resources.Window(disc), manifest)
        data = Path(plan["payload"]).read_bytes()
        build.require(len(data) == plan["resolved"]["size"] and len(data) <= resources.META_LIMIT and
                      hashlib.sha256(data).hexdigest() == plan["sha256"], "Pack changed after planning")
        frozen = Path(directory) / "texture.raw"
        with frozen.open("xb") as out:
            out.write(data)
        frozen.chmod(0o444)
        return {"mode": "replacement", "plan": plan, "frozen_payload": str(frozen)}, {
            "GODHAND_PC_TEXTURE_FILE": str(frozen),
            "GODHAND_PC_TEXTURE_OFFSET": str(plan["resolved"]["offset"]),
            "GODHAND_PC_TEXTURE_SIZE": str(len(data)),
            "GODHAND_PC_TEXTURE_SHA256": plan["sha256"],
            "GODHAND_PC_TEXTURE_PROFILE": resources.PROFILE,
        }
    except (ValueError, OSError) as error:
        if strict:
            raise ValueError("Pack refused in strict mode: " + str(error)) from error
        return {"mode": "original-fallback", "error": str(error)}, {}


def launch(root, name, iso, pack=None, strict=False, headless=False, seconds=None,
           capture=False, fresh_user_data=False, pad_script=None, profile="original", controls_pause=False,
           controls_pause_version=None, hd_textures=False, hd_pack=None, strict_hd=False,
           hd_textures_version=None, video_settings=False, native_menu=False, native_menu_version=None):
    policy = profiles.resolve(profile, pack, strict, controls_pause, controls_pause_version,
                              hd_textures, hd_pack, strict_hd, hd_textures_version, video_settings, native_menu, native_menu_version)
    build.require(os.name == "nt", "This native runtime currently requires Windows")
    build.require(seconds is None or (type(seconds) is int and 10 <= seconds <= 600),
                  "Runtime limit must be 10..600 seconds")
    build.require(not headless or seconds is not None, "Headless runs require an explicit deadline")
    build.require(pad_script is None or (type(pad_script) is str and 0 < len(pad_script) <= 4096),
                  "Invalid bounded input script")
    root = Path(root).resolve()
    workspace = runtime_packs.workspace_path(root, name)
    build.require(not (workspace / "setup.lock").exists() and not (workspace / "packs/install.lock").exists(),
                  "Build/installer lock requires inspection before launch")
    version = controls_pause_version or "v1"
    hd_version = hd_textures_version or "v1"
    menu_version = native_menu_version or "v1"
    installed = ((menu.verified_install(root, name) if menu_version == "v1" else
                  menu.verified_install(root, name, menu_version)) if native_menu else
                 hd.verified_install(root, name, hd_version) if hd_textures else
                 pause.verified_install(root, name, version) if controls_pause else runtime_packs.verified_install(root, name))
    identity = pc.verify_disc(iso, pc.load_pin(root)["retail_profile"])
    # Validate disc/source/binary BEFORE the optional pack fallback boundary.
    build.require_no_game(subprocess.check_output)
    if controls_pause and version == "v1":
        print("WARNING: legacy controls v1 does not drain an already admitted audio callback. "
              "audio-v2 requires its own install and explicit version selection; see AUDIO_HOLD.md.", flush=True)
    directory = build.contained(workspace, workspace / "packs/launches" / uuid.uuid4().hex)
    directory.mkdir(parents=True)
    record = {"started_at": build.now(), "status": "preparing", "disc": identity,
              "runtime": installed["executable"], "source_revision": installed["source_revision"],
              "adapter_fingerprint": installed["adapter_fingerprint"],
              "tooling_revision": pc.git("rev-parse", "HEAD", cwd=root),
              "tooling_dirty": bool(pc.git("status", "--porcelain", cwd=root))}
    record["profile"] = policy
    if hd_textures and hd_version == "gpu-audio-v3":
        record["component_fingerprints"] = installed["component_fingerprints"]
    record["controls_pause"] = {"requested": controls_pause,
                                "version": version if controls_pause else None,
                                "audio_scope": ("consumer admission; device buffering/audibility unverified"
                                                if controls_pause and version == "audio-v2" else
                                                "legacy/no consumer-admission guarantee"),
                                "acknowledged_hold": "not inferred from launch request",
                                "fingerprint": installed.get("controls_fingerprint")}
    record["native_menu"] = {"requested": native_menu, "version": menu.layer_name(menu_version) if native_menu else None,
                             "fingerprint": installed.get("menu_fingerprint"),
                             "requires_audio_v2_hold": native_menu, "observed": "not inferred from launch"}
    receipt = directory / "receipt.json"
    def save():
        receipt.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    save()
    service, child = None, None
    try:
        video_record, video_environment = (video.protocol(root, name, directory) if video_settings else
                                         ({"mode": "unselected", "requested": False}, {}))
        record["video_settings"] = video_record
        pack_record, pack_environment = pack_protocol(identity["path"], pack, directory, strict)
        record["pack"] = pack_record
        if pack_record["mode"] == "original-fallback":
            print("WARNING: invalid pack; using original assets:", pack_record["error"], flush=True)
        hd_record, hd_environment = hd_packs.protocol(identity["path"], hd_pack, directory, strict_hd)
        record["hd_textures"] = dict(hd_record, requested=hd_textures,
                                     version=hd.layer_name(hd_version) if hd_textures else None,
                                     fingerprint=installed.get("hd_fingerprint"),
                                     runtime_application="not inferred; GPU-only result counts are unread; inspect rendered controls"
                                                         if hd_textures and hd_version in ("gpu-v2", "gpu-audio-v3") else
                                                         "not inferred; inspect native exact-match logs and rendered controls")
        if hd_record["mode"] == "original-fallback":
            print("WARNING: invalid HD pack; using original assets:", hd_record["error"], flush=True)
        user = directory / "userdata" if fresh_user_data else build.contained(workspace, workspace / "userdata")
        cards = build.contained(user, user / "memcards")
        states = build.contained(user, user / "quickstates" / installed["source_revision"])
        cards.mkdir(parents=True, exist_ok=True)
        states.mkdir(parents=True, exist_ok=True)
        record["controls"] = user_data.prepare_controls(user, installed.get("controls_adoption_executable",
                                                        installed["executable"]["path"]), fresh_user_data)
        if native_menu:
            menu_store = user if fresh_user_data else None
            snapshot = video_record
            if fresh_user_data:
                snapshot = video.update(root, name, video_record["requested_native_scale"],
                                        expected_revision=None, user=user)
            broker = menu_channel.Broker(root, name, directory, snapshot["sha256"],
                                         video_record["requested_native_scale"], user=menu_store)
            record["native_menu"].update(channel=str(broker.directory),
                preference_scope="scratch-semantic-seed" if fresh_user_data else "persistent",
                source_revision=video_record["sha256"], menu_revision=snapshot["sha256"])
        env = clean_environment(os.environ)
        env.update({"GODHAND_ISO": identity["path"], "GODHAND_MC_DIR": str(cards),
                    "GODHAND_QUICK_STATE": str(states / "quick.state"),
                    "GODHAND_ISO_PREFETCH": "0", "GODHAND_DUMP_ON_TIME_LIMIT": "0",
                    "GODHAND_LOG_FILE": "", "GODHAND_DLL_LOG": str(directory / "dll-loads.csv"),
                    "PS2X_AUDIO_MUTE": "1" if headless else "0", "PS2X_SHOW_FPS": "0"})
        env.update(user_data.controls_environment(user))
        env.update(controls_pause_environment(controls_pause or native_menu))
        env.update(GODHAND_PC_VIDEO_MENU="1" if native_menu else "0",
                   GODHAND_PC_VIDEO_MENU_DIR=str(broker.directory) if native_menu else "",
                   GODHAND_PC_VIDEO_MENU_SELFTEST="0", GODHAND_PC_VIDEO_MENU_SELFTEST_FIELD="0")
        if pad_script:
            env.update(PS2X_PAD_SCRIPT=pad_script, PS2X_FAKE_PADS="1")
        if capture:
            (directory / "frames").mkdir()
            env.update(PS2X_SCREENSHOT_DIR=str(directory / "frames"),
                       PS2X_SCREENSHOT_FIELDS=",".join(map(str, range(180, 42001, 120))))
        env.update(pack_environment)
        # Empty values also disable native INI pass-through, not only inherited env.
        env.update(hd_environment)
        env.update(video_environment)
        if native_menu: env["PS2X_GS_RENDERER"] = "native" # menu capability requires this backend, even with INI scale
        command = runtime_command(installed["executable"]["path"], identity["path"], headless, seconds)
        record.update(command=command, environment={k: v for k, v in env.items()
                       if k.startswith(("GODHAND_", "PS2X_"))},
                      fresh_user_data=fresh_user_data,
                      time_limit_seconds=0 if seconds is None else seconds,
                      scope=("Experimental single-source size-aware host input, not general HD, hardware/audio, Save/Load or full fidelity"
                             if hd_textures else
                             "Named native payload MVP, not HD resizing, physical input, audio, Save/Load or full-game fidelity"))
        with (directory / "runtime.log").open("xb") as log:
            if native_menu: service = menu_channel.Service(broker).start()
            child = subprocess.Popen(command, cwd=Path(command[0]).parent, env=env, stdout=log,
                                     stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW |
                                     subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            record.update(status="running", pid=child.pid)
            save()
            print("Owned native runtime", child.pid, "receipt", receipt, flush=True)
            try:
                record["exit"] = child.wait(timeout=seconds + 45 if seconds is not None else None)
            except subprocess.TimeoutExpired:
                child.kill()
                record["exit"] = child.wait()
                record["forced_owned_pid_after_deadline"] = True
        if service:
            record["native_menu"]["broker"] = service.finish(); service = None
        # Runtime snapshots never substitute for game-card persistence tests.
        record.update(status="terminal", ended_at=build.now(), captures=[
            {"path": str(p), "sha256": build.digest(p)} for p in sorted((directory / "frames").glob("*.png"))])
        record["disc_after"] = pc.verify_disc(identity["path"], pc.load_pin(root)["retail_profile"])
        record["controls"]["after"] = user_data.snapshot(user / "controls.ini")
        save()
        return dict(record, receipt=str(receipt))
    except BaseException as error:
        if service and (child is None or child.poll() is not None):
            record["native_menu"]["broker"] = service.finish()
        elif service:
            record["native_menu"]["broker"] = {"stopped": False, "reason": "native child still alive; no restart"}
        record.update(status="observer-interrupted-or-failed", error=str(error), ended_at=build.now())
        save()
        raise
