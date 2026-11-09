# Experimental size-aware texture boundary

9 November 2026. **Private native trial; no public HD installer or launch flag.**
The ordinary installed baseline and both controls variants are unchanged. The
current public named-pack command still supports same-size stored bytes only.
An actual private native build has uploaded an original512x512 image, matched
all16384 source texels and displayed the authored pattern on the early street.
Disabled/corrupt-reference controls and the checked public helper integration
are still being validated. Do not treat this provisional result as general HD
resource support or a finished remaster.

## The actual host boundary

The pinned LasVola GPU backend samples GS VRAM and CLUT shader-storage buffers
directly, through compute and specialized hardware raster shaders. Its OpenGL
texture upload is for the presented framebuffer, not a cache of decoded game
assets. Replacing that presentation texture would not be resource replacement.

This experiment leaves the original disc, guest bytes and VRAM untouched:

1. Verify the personal retail disc, then use the existing named selector
   `st1/r100.dat / SCP3 / bank0 / image0`. Read that bounded128x128 4-bit selector6
   resource into a **private** raw-RGBA reference. The separate
   [reference expansion](hd_reference.py) follows the historical MIT lab's
   [documented transfer format](https://github.com/YYoudi/god-hand-rs/blob/de0091371f9d405abb02bb82ca57ac2f11ab245e/specs/tm3-tim3-v1.md),
   not a game function or imported engine implementation.
2. After transfers, epoch mapping and CLUT resolution, compare every decoded
   source texel on the GPU. Initially accept only128x128 PSMT4/32-bit-CLUT states
   with repeat/repeat addressing. No guessed VRAM address or few-corner match.
3. Upload a separate original authored larger RGBA image in host storage. Only
   matched states sample it at scaled texture coordinates; keep STQ/fixed UV,
   raw alpha, original texture combination, draw order and framebuffer behavior.
   Unmatched/unsupported states keep the original sampler.

This identifies **decoded content**, not a unique original filename at GPU time.
Identical content aliases may match multiple named copies. Full file ownership,
animated/paletted variants, other resources/scenes and a production cache need
separate work. No camera, lighting, game logic, timing or generated function is
changed to make the pattern visible.

## Original public building blocks

- [C++ envelope and shader builders](adapter/hd_texture.hpp): bounded raw payload,
  full-source classifier, repeat addressing and point/linear external sampling.
  These need the reviewed private host integration; including this header alone
  does not install or enable anything.
- [Reference expansion](hd_reference.py): deliberately separate from the existing
  metadata-only planner. Original palette alpha is preserved, not reconstructed
  from normalized presentation alpha. Its game-derived output is private.
- Original invented transfer, malformed-envelope, raw-alpha and source-preimage
  tests. No retail pixels, shader dumps or generated code are CI fixtures.

The provisional envelope is `GHHD001` plus a zero byte, six little-endian u32
fields (128,128,newWidth,newHeight,16384,newWidth*newHeight), reference RGBA and
replacement RGBA. Both new axes must be powers of two, larger than128 and at
most2048. Exact length and a64MiB budget are checked before GPU allocation.
The native caller must verify the whole-file SHA-256 and retail profile first.
The envelope contains an original-game reference: **never distribute it**.
This is a private probe protocol, not a stable public resource-pack schema.

## Required controls and limits

Keep original512x512 authorship, immutable input hash, exact source/executable,
commands and shader/renderer outcomes. Build/link/upload are separate from an
actual rendered difference. Compare unchanged original PNGs from the same
viewpoint; retain capture padding and all failed attempts. Disabling the
extension, invalid input and a single changed reference texel must restore the
sampled original image, not a synthetic marker texture.

The original test image is diagnostic grid/checker artwork, not remaster art.
Same-size packs, a larger framebuffer or a larger allocated-but-unused image
are not HD acceptance. No performance, other-scene, hardware/audio, genuine
game-save, full-game accuracy, widescreen, FPS or multiplayer claim follows.
Original GPL tooling, historical MIT format documentation and game-image rights
remain distinct. No reference image, extracted asset or executable is public.
