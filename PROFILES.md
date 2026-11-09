# Original and Enhanced launch policies

```powershell
python pc.py run --workspace-name retail-setup-v2 --iso "G:\path\God Hand (USA).iso"
python pc.py run --workspace-name retail-setup-v2 --iso "G:\path\God Hand (USA).iso" --profile enhanced --pack .local/example-pack/pack.json
```

The default is `--profile original`. It refuses `--pack` and `--strict-pack`
before installer/disc access or process creation; it never silently ignores a
requested enhancement. Existing pack commands must now specify `--profile enhanced`.
`--strict-pack` requires a pack and refuses invalid pack data rather than falling
back. Enhanced without a pack currently uses original assets. With a pack, an
invalid pack still warns and falls back unless strict mode was selected.

Each private launch receipt records the policy schema/name and requested
extensions separately from the actual `pack.mode`. A requested extension is not
a successful application; check the runtime log and rendered result too.

This first increment was launch-policy isolation, **not an in-game PC settings
menu**, function replacement or full PS2 fidelity. The initial extension was
the tested same-size named texture bridge; later opt-ins are recorded below.
Both profiles preserve the
existing pinned runtime, its upstream settings/timing and private user data.
The policy does not reset general native configuration or turn a runtime snapshot
into a real game save. [Controls preferences](USER_DATA.md) now live in workspace
user data; an existing executable-local controls file is adopted byte-for-byte
only when the workspace file is absent. Fresh diagnostics use separate defaults,
not the owner's controls/cards. Never delete preferences or cards to clean a test.
Without `--seconds`, normal launch explicitly requests native limit zero, rather
than inheriting a diagnostic timeout from the runtime INI. Hidden public runs
still require a bounded deadline. These are host-usability changes in both profiles.

The launcher cleans inherited GODHAND_/PS2X_ environment settings in both modes.
Headless limits, scripted controls and captures remain explicitly recorded test
options, not claims about physical input, audible audio or simulation accuracy.
No runtime relink is required for this Python policy increment.

Follow-up: `--profile enhanced --controls-pause` explicitly requests a separate
experimental host-runtime variant. It requires `install-controls-pause`; Original
refuses the flag, Enhanced without it retains the baseline, and no host pause is
silently enabled through an inherited environment or INI. See
[the implementation/validation boundary](CONTROLS_INSTALL.md). The exact recipe
has now linked and passed bounded native UI hold/resume/stop and public pack/
default-restoration controls. It remains experimental, not a complete settings
menu, hardware/audio result or full-machine/campaign fidelity claim.

The new audio-v2 consumer-admission layer requires both explicit installation
`install-controls-pause --version audio-v2` and launch
`--profile enhanced --controls-pause --controls-pause-version audio-v2`.
Without the version, a pause request still selects preserved v1 and warns about
its admitted-callback boundary. Without a pause request, Original/Enhanced keep
the unchanged baseline. A version without its pause flag is refused, never
silently ignored. The actual selected version, fingerprint, executable and
tooling cleanliness are recorded separately from an acknowledged native hold.

The separate checked [hd-v1 workflow](HD_PACKS.md) requires
`install-hd-textures`, then `--profile enhanced --hd-textures --hd-pack <manifest>`.
Only a512x512 original image on the documented128x128 source is natively verified.
No pack means original assets on the HD binary; no HD flags means the old binary.
HD combined with controls-pause or same-size packs is refused before disc/process
access, not silently downgraded. Strict HD is a **preflight** refusal policy, not
proof that GPU matching/upload/rendering succeeded; inspect native evidence.
