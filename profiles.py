"""Original GPL-3.0-only launch policy, not a PS2 fidelity certificate."""
NAMES = ("original", "enhanced")


def resolve(name="original", pack=None, strict=False, controls_pause=False, controls_pause_version=None,
            hd_textures=False, hd_pack=None, strict_hd=False, hd_textures_version=None, video_settings=False,
            native_menu=False, native_menu_version=None):
    """Validate before any filesystem, disc, installer or subprocess operation."""
    if name not in NAMES:
        raise ValueError("Unknown launch profile; choose original or enhanced")
    if type(native_menu) is not bool:
        raise ValueError("native-menu must be a boolean")
    if native_menu_version not in (None, "v1", "readback-v2"):
        raise ValueError("Unknown native-menu version")
    if native_menu_version is not None and not native_menu:
        raise ValueError("native-menu-version requires --native-menu")
    if native_menu and (name != "enhanced" or not video_settings):
        raise ValueError("native-menu requires Enhanced and explicit --video-settings")
    if native_menu and controls_pause and controls_pause_version != "audio-v2":
        raise ValueError("native-menu requires audio-v2, not legacy controls pause")
    if native_menu and hd_textures and hd_textures_version != "gpu-v2":
        raise ValueError("native-menu HD requires explicit gpu-v2; other versions unchanged")
    if type(video_settings) is not bool:
        raise ValueError("video-settings must be a boolean")
    if name == "original" and video_settings:
        raise ValueError("Original profile refuses video overrides; use --profile enhanced explicitly")
    if type(strict) is not bool:
        raise ValueError("strict-pack must be a boolean")
    if type(controls_pause) is not bool:
        raise ValueError("controls-pause must be a boolean")
    if controls_pause_version not in (None, "v1", "audio-v2"):
        raise ValueError("Unknown controls pause version")
    if controls_pause_version is not None and not controls_pause:
        raise ValueError("controls-pause-version requires --controls-pause")
    if name == "original" and controls_pause:
        raise ValueError("Original profile refuses host-pause changes; use --profile enhanced explicitly")
    if name == "original" and (pack is not None or strict):
        raise ValueError("Original profile refuses packs; use --profile enhanced explicitly")
    if strict and pack is None:
        raise ValueError("strict-pack requires a pack")
    if type(hd_textures) is not bool or type(strict_hd) is not bool:
        raise ValueError("HD capability and strict mode must be booleans")
    if hd_textures_version not in (None, "v1", "gpu-v2", "gpu-audio-v3"):
        raise ValueError("Unknown HD version")
    if hd_textures_version is not None and not hd_textures:
        raise ValueError("hd-textures-version requires --hd-textures")
    if (hd_pack is not None or strict_hd) and not hd_textures:
        raise ValueError("HD pack options require --hd-textures")
    if name == "original" and hd_textures:
        raise ValueError("Original profile refuses HD changes; use --profile enhanced explicitly")
    if strict_hd and hd_pack is None:
        raise ValueError("strict-hd-pack requires an HD pack")
    composite = hd_textures_version == "gpu-audio-v3"
    if composite and (not controls_pause or controls_pause_version != "audio-v2"):
        raise ValueError("gpu-audio-v3 requires explicit --controls-pause --controls-pause-version audio-v2")
    if hd_textures and (pack is not None or strict or (controls_pause and not composite and not native_menu)):
        raise ValueError("HD with same-size packs or controls-pause needs a separately validated combined variant")
    return {"schema": 1, "name": name,
            "requested_extensions": (["same-size-named-texture"] if pack is not None else []) +
                                    (["experimental-controls-pause" +
                                      ("-audio-v2" if controls_pause_version == "audio-v2" else "")]
                                     if controls_pause else []) +
                                    (["experimental-hd-textures" +
                                      ("-" + hd_textures_version if hd_textures_version in ("gpu-v2", "gpu-audio-v3") else "")]
                                     if hd_textures else []) +
                                    (["restart-required-video-settings"] if video_settings else []) +
                                    (["experimental-native-video-menu-audio-v2" +
                                      ("-readback-v2" if native_menu_version == "readback-v2" else "")]
                                     if native_menu else []),
            "baseline": ("pinned native runtime; explicit video request recorded separately; timing unchanged"
                         if video_settings else
                         "pinned native runtime; upstream settings/timing unchanged by this policy"),
            "fidelity": "not certified; full-game, persistence, physical input and audio gates remain open"}
