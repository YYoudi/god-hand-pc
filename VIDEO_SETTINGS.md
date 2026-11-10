# Restart-required native video preferences

This is a small pre-launch preference boundary, **not an in-game graphics menu**.
RM03 remains in progress. It reuses the pinned runtime's internal-scale option;
there is no new renderer, FPS unlock, widescreen or resolution-independent HUD.

## Source audit

The evaluated host source193076584e277c95644dcbbb4a6922c3a59ca2b8 descends from
LasVola14e956a1274332440273845fbab2c1f1e30c4a5a. Its `src/main.cpp` reads only
the executable-directory `godhand.ini`; there is no alternative-config CLI.
Recognized CLI values precede existing environment values, which precede INI
defaults. We do not edit that INI or invent a config-path argument.

`ps2_game_menu.cpp` gates F2 on an active PCSX2 GS backend. That is **not a
working native-GS graphics menu**. F1 is the existing, separately tested controls
screen, not a full video settings screen.

`gs_gpu_backend.cpp` reads `PS2X_GS_SCALE` at startup and clamps it1..8. It then
reduces the scale if the sample-plane buffer would exceed the reported OpenGL
storage-block limit. A requested scale is **not necessarily the effective one**.
Internal sampling scale is not output framebuffer size, window resolution or an
accuracy certificate. Native initialization logs the effective value when >1;
absence of that line alone does not prove1x or successful initialization.

Vsync, simulation timing, alternate backends and fullscreen/window flags are not
exposed here. In particular, disabling vsync is not a safe FPS-unlock proof.

## Commands

After setting up an existing `retail-*` workspace:

```powershell
python pc.py video-settings --workspace-name retail-setup-v2 --internal-scale 2
python pc.py video-settings --workspace-name retail-setup-v2
python pc.py run --workspace-name retail-setup-v2 --iso "G:\path\God Hand (USA).iso" --profile enhanced --video-settings
python pc.py video-settings --workspace-name retail-setup-v2 --reset
```

`--internal-scale` accepts integer1..8, the source-audited range, **not eight
locally verified hardware modes**. Restart the process to apply a change.
`--reset` records a new immutable revision and supplies no video override on the
next explicitly selected run. It returns to upstream INI behavior, not a
hardcoded value or claimed original PS2 settings. No history is deleted.

Without `run --video-settings`, the launcher does not load this store at all.
Default Original and previous Enhanced commands retain their old meaning.
Original plus the flag refuses before filesystem/disc/process work; use Enhanced
explicitly. Selecting missing, corrupt or locked preferences refuses native
spawn rather than silently choosing a different configuration.

The flag is independent of the existing explicit pack/controls version flags;
it does not install, select or upgrade a native variant. It does not make old
unsupported HD/controls combinations valid. `--fresh-user-data` still isolates
input preferences/cards/states; when the video flag is supplied it deliberately
snapshots the selected workspace's video revision, rather than guessing a fresh
video default. It never edits native INIs or a player's controls.

## Storage and receipt contract

Ignored `userdata/video/` contains a small `current.json` pointer and immutable
SHA-256-named JSON revisions. Each revision has exactly `schema:1`,
`native_scale` (integer1..8 or null for reset), and `previous` (hash or null).
The previous hash retains the chain of settings/reset operations. An exclusive
writer lock prevents cooperative writers from overwriting each other; stale
locks require inspection, not automatic stealing. Pointer replacement is atomic.
Interrupted writes leave old/current or pending evidence for review. This is not
a guarantee against malicious concurrent filesystem mutation or power loss.

Reject duplicate/unknown keys, wrong types/bounds, nonfinite/malformed JSON,
tampered hashes, symlinks/reparse points, hardlinked files and metadata >4096
bytes. No arbitrary runtime environment key, native INI fragment, dump, self-test
or generated game code is accepted through this schema.

The launch freezes the selected original revision bytes into its private
directory, records their hash and requested value, and sets only native renderer
and scale for a non-reset selection. The receipt deliberately leaves effective
scale unproven: inspect actual native initialization/rendering separately.
Later preference changes cannot retroactively relabel the launch snapshot.

## Validation status

Original invented-data tests cover history/reset/reload, exact frozen bytes,
strict parsing, metadata/path limits, aliases, locks, atomic replacement failure,
CLI routing, policy refusal, safe environment and unselected defaults.
Native validation is pending for this new tooling revision. A source audit or
mock process is not runtime proof. The retained native binaries need no relink;
no game inputs belong in CI. Broader graphics UI/usability, other scales/GPUs,
physical input/audio, genuine Save/exit/Load and campaign fidelity remain open.
