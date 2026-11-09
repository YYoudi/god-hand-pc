"""Original GPL-3.0-only launch policy, not a PS2 fidelity certificate."""
NAMES = ("original", "enhanced")


def resolve(name="original", pack=None, strict=False, controls_pause=False, controls_pause_version=None,
            hd_textures=False, hd_pack=None, strict_hd=False):
    """Validate before any filesystem, disc, installer or subprocess operation."""
    if name not in NAMES:
        raise ValueError("Unknown launch profile; choose original or enhanced")
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
    if (hd_pack is not None or strict_hd) and not hd_textures:
        raise ValueError("HD pack options require --hd-textures")
    if name == "original" and hd_textures:
        raise ValueError("Original profile refuses HD changes; use --profile enhanced explicitly")
    if strict_hd and hd_pack is None:
        raise ValueError("strict-hd-pack requires an HD pack")
    if hd_textures and (pack is not None or strict or controls_pause):
        raise ValueError("HD with same-size packs or controls-pause needs a separately validated combined variant")
    return {"schema": 1, "name": name,
            "requested_extensions": (["same-size-named-texture"] if pack is not None else []) +
                                    (["experimental-controls-pause" +
                                      ("-audio-v2" if controls_pause_version == "audio-v2" else "")]
                                     if controls_pause else []) +
                                    (["experimental-hd-textures"] if hd_textures else []),
            "baseline": "pinned native runtime; upstream settings/timing unchanged by this policy",
            "fidelity": "not certified; full-game, persistence, physical input and audio gates remain open"}
