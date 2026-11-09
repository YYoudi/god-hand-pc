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

This first increment is launch-policy isolation, **not an in-game PC settings
menu**, function replacement or full PS2 fidelity. The only current extension is
the previously tested same-size named texture bridge. Both profiles preserve the
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
