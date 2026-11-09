"""Original GPL-3.0-only launch policy, not a PS2 fidelity certificate."""
NAMES = ("original", "enhanced")


def resolve(name="original", pack=None, strict=False, controls_pause=False, controls_pause_version=None):
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
    return {"schema": 1, "name": name,
            "requested_extensions": (["same-size-named-texture"] if pack is not None else []) +
                                    (["experimental-controls-pause" +
                                      ("-audio-v2" if controls_pause_version == "audio-v2" else "")]
                                     if controls_pause else []),
            "baseline": "pinned native runtime; upstream settings/timing unchanged by this policy",
            "fidelity": "not certified; full-game, persistence, physical input and audio gates remain open"}
