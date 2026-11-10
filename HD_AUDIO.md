# Explicit HD + audio-v2 composition

10 November 2026. **Build and native integration pending.** This document records
the checked experiment contract, not a validated combined release or a default
upgrade. Old HD/control combinations remain refused unless the new exact version
and both capabilities are explicitly selected. Original stays unchanged.

The additive `gpu-audio-v3` HD version composes existing GPU-v2 and audio-v2
recipes over the same pinned named-pack baseline. Six modified host files and
eight original helper copies have disjoint destinations; no fuzzy overlapping
edits, guest function changes or game regeneration. Component and joint
fingerprints are checked separately. The old component recipe bytes, source,
binaries, pointers and fingerprints retain their existing meanings.

```powershell
python pc.py install-hd-textures --workspace-name retail-setup-v2 --version gpu-audio-v3
python pc.py run --workspace-name retail-setup-v2 --iso "G:\path\God Hand (USA).iso" --profile enhanced --hd-textures --hd-textures-version gpu-audio-v3 --controls-pause --controls-pause-version audio-v2 --hd-pack .local/second-surface-example/pack.json --strict-hd-pack
```

The [original second-surface example](SECOND_RESOURCE.md) needs no game pixels
to author its external image. Its runtime envelope includes a private personal-
ISO source reference; never publish that envelope. Omit `--hd-pack` for the
same combined binary's original assets. Without all composite selection flags,
incomplete/old-version combinations refuse before filesystem/disc/process.
Same-size+HD composition remains unsupported. Normal launches disable mutating
controls self-tests and probes; no acknowledged hold or visible replacement is
inferred merely from requested flags or upload/submission logs.

Before runtime acceptance: preserve the baseline executable/PDB and all prior
variants; reconfigure and force affected host units in the existing private build
cache; actually link the exact public recipe and restore baseline ownership.
No new clone or generation is needed. Retain failed/interrupted outputs and
live-child locks; a polling timeout is not build completion or restart permission.

Then verify actual enabled/absent/invalid rendering on this exact binary,
separate guarded UI/hold/resume/stop controls, a pause-disabled control and old
version startup rollback/refusals. Inspect field/cycle/RAM and held original
images rather than trusting the generic coordination tests. Nonempty audio,
audible/device/focus/peripheral quality and physical controls are separate gates.
No game data belongs in synthetic tests or CI, no source preview/envelope/game
binary/save may be published, and selected native originals keep exact provenance.

The full PC/remaster goal, genuine SaveExitLoad and campaign/PS2 fidelity remain
open. No performance gain, cache, widescreen/FPS/lighting/multiplayer or hardware-
audio claim follows from composing two previously sampled host extensions.
