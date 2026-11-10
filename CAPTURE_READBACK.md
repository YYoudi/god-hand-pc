# Framebuffer readback: additive follow-up, not improved game graphics

10 November 2026. Work on the separate readback branch. **The new version has
not yet been linked or observed in the game.** The old failed comparison remains
a failure; no existing image is cropped, resized or overwritten.

## Current evidence

The historical6November report already reproduced a screenshot-size bug in a
different private checkout. That is not new evidence for the current checked
menu binary. We now reran an original invented-color probe against the actual
Raylib static library in the retained menu build cache. Both hidden cases pass:

| Mode | Logical | Render | Queried GL viewport | Default screenshot | Direct render-size read |
| --- | --- | --- | --- | --- | --- |
| Normal | 640x480 | 640x480 | 0,0,640,480 | 800x600, padded | 640x480, all markers correct |
| HIGH_DPI | 640x480 | 800x600 | 0,0,800,600 | 800x600 | 800x600, byte-identical to default |

Both report desktop scale1.25 and GL read/draw framebuffer0. Unlike the old
probe, this new probe actually queries viewport/FBO; it does not fill a guessed
viewport value into evidence. No game data, shaders or code is involved.

The retained Raylib readback implementation multiplies logical dimensions by
desktop scale. That does not always describe the allocated framebuffer. The
new original helper reads the reported actual render extent directly, with
bounded dimensions/allocation arithmetic and the same library readback. It
does not set the viewport, window dimensions, DPI policy, renderer or game scale.
Caller owns/unloads the returned image. It is for the default-window capture
point, not arbitrary render textures, minimized windows or all backends.

## Proposed checked version

`readback-v2` is additive. No version still selects preserved native-menu-v1;
old helper bytes, fingerprints, pointers, executables, PDBs and defaults remain.
The exact v1 postimages at host field capture, F1 diagnostic capture and our F2
probe are patched to the same new capture helper. All other menu behavior is
unchanged. It has one extra checked file (33 total), not a new engine.

Experimental branch commands (native acceptance still pending):

```powershell
python pc.py install-native-menu --workspace-name retail-setup-v2 --version readback-v2
python pc.py run --workspace-name retail-setup-v2 --iso "G:\path\God Hand (USA).iso" --profile enhanced --video-settings --native-menu --native-menu-version readback-v2
```

Next: actually link the clean checked recipe, observe retail F2 save/hold/resume
and fresh2x/INI3x captures at field4741, then test default/oldv1 rollback. Passing
invented tests or synthetic GPU colors is not the native proof. Preserve the
failed800-vs640 comparison and old original timestamps/revisions. Only new
renderer originals may be published after review, with their own provenance.
Physical input/focus/audio, true game Save/exit/Load, broader scenes and full PC
accuracy remain open. There is no new FPS, widescreen or artwork improvement.
