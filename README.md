# God Hand PC continuation tooling

Latest [capture investigation](CAPTURE_READBACK.md): a same-frame native control
bounds a DPI readback bug, while a separate scene mismatch remains unresolved.
The new candidate is isolated on its research branch, not promoted on main.

Original GPL-3.0-only tooling for continuing the locally evaluated
[LasVola PC port](https://github.com/LasVola/godhand-recomp). This is a separate
project from the preserved MIT Rust/Bevy inspection lab. It is **not** a mirror
of upstream, a new engine, a downloadable game or a finished remaster.

Upstream source is fetched at an exact revision into ignored `.local/` storage.
No third-party source is vendored here. A personal **USA retail ISO** is required;
the prototype is a different research profile, never silently accepted as retail.
Generated game code, discs, ELFs, extracted assets, saves and executables remain
local. The project license covers its original tooling, not the game or its art.

**This is the sole active home for the PC port and its public communication.**
Read the [development journal](https://yyoudi.github.io/god-hand-pc/),
[roadmap](https://yyoudi.github.io/god-hand-pc/roadmap.html),
[dated reports](https://yyoudi.github.io/god-hand-pc/reports/index.html) and
[reviewed original comparisons](https://yyoudi.github.io/god-hand-pc/comparisons.html).
The independent MIT [Rust/Bevy lab](https://github.com/YYoudi/god-hand-rs) is
historical, paused and not achieved. Old results migrated here are labeled as
editorial migration, not new runtime validation. See [the workflow](PROGRESS.md).

The latest [fixed-field HD v1 / GPU v2 check](FRAME_SPANS.md) reproduces matching
sampled images, but does **not** establish a reliable speedup. Both the slower
repeat and the measurement limits are retained; defaults are unchanged.
The later [second named-resource control](SECOND_RESOURCE.md) modifies another
surface through the same retained binaries, with original-asset fallback.
It is still one room and one supported source format, not general HD support.
The explicit [HD + audio-v2 composition](HD_AUDIO.md) now has a checked additive
build and sampled native controls/render/resume/stop/rollback evidence. It is
opt-in, not a default upgrade, audible-audio or full-game validation.
The first [restart-required video preference](VIDEO_SETTINGS.md) now has actual
new-process2x persistence, default/reset3x and composite controls. It reuses a
native startup option without editing the INI. This is not an in-game graphics
menu, a quality/performance claim or eight verified scale modes.
The later explicit [native F2 extension](NATIVE_MENU_RESULTS.md) now renders one
restart-required scale preference in the actual game, with save-ACK/stale-reload/
resume controls. It is experimental; physical input and the retained capture-size
comparison failure still need work. Default Original remains unchanged.

## Active direction

Current research: [prototype debug tools for the PC build](PROTOTYPE_DEBUG.md).
The [input/menu follow-up](SIO2_PAD_STATUS.md) now opens, navigates and closes the
original prototype debug menu in the native build. One Room Jump executes the
original western-room introduction. It is not yet a public prototype installer,
a retail debug backend or verified warp/invincibility. The full developer-tools
goal remains active. Selected unchanged build originals and exact hashes are on
the journal; F1 key-event coexistence and in-scene actions still need testing.

Continue LasVola toward a faithful original PC baseline, then add reversible PC
features without rewriting the entire engine. Read [the medium-term gates](DIRECTION.md),
[extension architecture](ARCHITECTURE.md) and [Original/Enhanced policies](PROFILES.md).
The default launch refuses packs; use `--profile enhanced` to opt into one.
This is not yet an in-game settings menu or a complete accuracy claim.
See [user-data and launch-lifetime behavior](USER_DATA.md): normal launch without
`--seconds` explicitly requests no diagnostic timeout. The existing upstream F1
controls screen edits workspace-local preferences, not the executable's file.
Physical input, audible audio and actual game Save/Load remain separate gates.
The [experimental controls-pause boundary](CONTROLS_PAUSE.md) now has bounded
native hold/resume/UI/stop evidence; its generic original primitive is public,
and a [checked opt-in variant installer](CONTROLS_INSTALL.md) is now implemented.
Its exact public recipe has linked and passed bounded native hold/resume/stop,
public opt-in/pack and default-restoration controls locally. It is experimental;
default launch remains the unchanged evaluated executable, not an implicit relink.
The separately selected [audio-v2 boundary](AUDIO_HOLD.md) now excludes an
already-admitted callback at acknowledgement, with native interleaving controls
and preserved v1/Original rollback. A separate private diagnostic also holds one
ordinary nonempty queue at an earlier retail point. It is still experimental:
audible output, device transitions and broader scene coverage remain unverified.

## Bootstrap commands (Python 3.11+, Git)

The [game-free translation controls](TRANSLATION_DIAGNOSTICS.md) reproduce
return-tail versus reachable-failure behavior using original invented inputs.
They help investigate retained diagnostics, not certify a clean game translation
or silently replace unsupported instructions. Native integration uses an existing
private recompiler/MSVC toolchain; portable CI never uses game inputs.

```powershell
python pc.py fetch
python pc.py verify-disc --iso "G:\path\God Hand (USA).iso"
python pc.py status
```

`fetch` checks out the pinned source; it does not compile a game. For an existing
locally evaluated source tree, avoid another download:

```powershell
python pc.py adopt --checkout "G:\path\godhand-recomp" --revision FULL_COMMIT_SHA
```

Adoption requires clean non-ignored source and the pinned upstream commit as an
ancestor. It records the exact local revision without copying any game material.
`status` checks that the recorded revision/source are still unchanged. These
commands do not grant a modified checkout the same validation as the baseline.

## Build boundary and next work

An original [Windows personal-disc setup recipe](SETUP.md) now fetches pinned
dependencies and orchestrates the complete boot/81-overlay build in a separate
ignored workspace. Fresh source/dependency acquisition, all generation/build
steps and a bounded opening/first-fight scene are now locally verified. It does
not install the pack adapter implicitly or claim a tested game-save round trip.

The underlying retail executable has already been built and tested in the
[research journal](https://yyoudi.github.io/god-hand-pc/), including an
original same-size external texture experiment. The corrected personal-disc
command now reproduces the full boot/81-overlay build on the evaluation machine;
generation still reports one unresolved error, not a clean translation.
The [named-resource planner](RESOURCE_PACK.md) and separate
[public runtime bridge/launcher](RUNTIME_PACKS.md) are locally tested: an original
magenta ground replacement renders, disabling it restores original assets, and an
invalid pack automatically falls back to the byte-identical sampled original PNG.
Use `python pc.py install-packs`, then create the game-free example with
`python make_example_pack.py --output .local/example-pack` and launch with
`python pc.py run --iso "G:\path\God Hand (USA).iso" --profile enhanced --pack .local/example-pack/pack.json`.
See the contract for workspace selection, prerequisites and exact limits.
The [private larger-texture proof](HD_TEXTURES.md) now has a distinct
[checked experimental HD workflow](HD_PACKS.md): `install-hd-textures`,
`make_example_hd_pack.py`, then explicit Enhanced+HD launch. Its public recipe
builds locally and renders an original512x512 diagnostic in place of one128x128
texture. Absent/invalid/default controls reproduce the original PNG. This is
not general HD/remaster support: aliases, performance, other scenes and HD with
controls-pause/same-size packs remain open (those combinations are refused).
Full playthrough and genuine game-save round trip remain open. The personal disc
is verified before every launch; game-derived references remain private.
The [separate matcher timing trial](HD_TIMING.md) distinguishes CPU readback
waits from GPU command intervals. It does not change the installed HD binary
or claim an optimization/FPS gain; safe invalidation remains open.
Its later [explicit gpu-v2 follow-up](HD_GPU_RESULTS.md) now builds locally and
passes sampled native valid/absent/invalid/reference-negative controls without
CPU match-result readback. Older versions stay selectable and unchanged. This
is a functional integration result, not general HD, full fidelity or measured
FPS improvement.

Prototype generation/build/debug-menu research stays separate. Discovery output
is not a linked executable or a validated retail behavior. Do not attempt to beat
levels autonomously as a prerequisite for developing the port.

## Checks

```powershell
python -m unittest discover -s tests -p "test_*.py"
python scripts/check_public_tree.py
```

Only files in `PUBLIC_FILES.json` may be staged. CI uses no game input, custom
cache or custom retained build artifact. The canonical journal uses this
repository's free GitHub Pages at github.io, main:/docs. The old lab's Pages
remain historical; no paid or third-party hosting service is introduced.
