# God Hand PC continuation tooling

Original GPL-3.0-only tooling for continuing the locally evaluated
[LasVola PC port](https://github.com/LasVola/godhand-recomp). This is a separate
project from the preserved MIT Rust/Bevy inspection lab. It is **not** a mirror
of upstream, a new engine, a downloadable game or a finished remaster.

Upstream source is fetched at an exact revision into ignored `.local/` storage.
No third-party source is vendored here. A personal **USA retail ISO** is required;
the prototype is a different research profile, never silently accepted as retail.
Generated game code, discs, ELFs, extracted assets, saves and executables remain
local. The project license covers its original tooling, not the game or its art.

## Current commands (Python 3.11+, Git)

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
[research journal](https://yyoudi.github.io/god-hand-rs/dashboard/), including an
original same-size external texture experiment. The corrected personal-disc
command now reproduces the full boot/81-overlay build on the evaluation machine;
generation still reports one unresolved error, not a clean translation.
The [named-resource planner](RESOURCE_PACK.md) and separate
[public runtime bridge/launcher](RUNTIME_PACKS.md) are locally tested: an original
magenta ground replacement renders, disabling it restores original assets, and an
invalid pack automatically falls back to the byte-identical sampled original PNG.
Use `python pc.py install-packs`, then create the game-free example with
`python make_example_pack.py --output .local/example-pack` and launch with
`python pc.py run --iso "G:\path\God Hand (USA).iso" --pack .local/example-pack/pack.json`.
See the contract for workspace selection, prerequisites and exact limits.
HD texture dimensions, full playthrough and genuine game-save round trip remain
open. The personal disc is verified before every launch.

Prototype generation/build/debug-menu research stays separate. Discovery output
is not a linked executable or a validated retail behavior. Do not attempt to beat
levels autonomously as a prerequisite for developing the port.

## Checks

```powershell
python -m unittest discover -s tests -p "test_*.py"
python scripts/check_public_tree.py
```

Only files in `PUBLIC_FILES.json` may be staged. CI uses no game input, custom
cache or retained build artifact. The journal remains on the existing free
GitHub Pages site; no second hosting service is introduced.
