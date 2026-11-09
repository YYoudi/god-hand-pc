"""Original GPL-3.0-only launch policy, not a PS2 fidelity certificate."""
NAMES = ("original", "enhanced")


def resolve(name="original", pack=None, strict=False):
    """Validate before any filesystem, disc, installer or subprocess operation."""
    if name not in NAMES:
        raise ValueError("Unknown launch profile; choose original or enhanced")
    if type(strict) is not bool:
        raise ValueError("strict-pack must be a boolean")
    if name == "original" and (pack is not None or strict):
        raise ValueError("Original profile refuses packs; use --profile enhanced explicitly")
    if strict and pack is None:
        raise ValueError("strict-pack requires a pack")
    return {"schema": 1, "name": name,
            "requested_extensions": ["same-size-named-texture"] if pack is not None else [],
            "baseline": "pinned native runtime; upstream settings/timing unchanged by this policy",
            "fidelity": "not certified; full-game, persistence, physical input and audio gates remain open"}
