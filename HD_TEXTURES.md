# Experimental size-aware texture boundary

**Later follow-up:** [HD_PACKS.md](HD_PACKS.md) records a distinct checked public
installer/pack build and actual launcher controls. The original private-trial
report below retains its own historical revisions, results and limitations;
statements about missing public integration describe that earlier milestone.

9 November 2026. **Private native trial; no public HD installer or launch flag.**
The ordinary installed baseline and both controls variants are unchanged. The
current public named-pack command still supports same-size stored bytes only.
An actual private native build has uploaded an original 512x512 image, matched
all 16,384 source texels and displayed the authored pattern on the early street.
Disabling it restores the sampled baseline PNG byte-for-byte. A second private
build using the exact original public helpers reproduces the same replacement
PNG. A single changed interior reference texel and an invalid input hash also
restore the sampled original. This is a private proof, not general HD resource
support or a finished remaster.

## The actual host boundary

The pinned LasVola GPU backend samples GS VRAM and CLUT shader-storage buffers
directly, through compute and specialized hardware raster shaders. Its OpenGL
texture upload is for the presented framebuffer, not a cache of decoded game
assets. Replacing that presentation texture would not be resource replacement.
Audited primary sources are the pinned
[GPU backend](https://github.com/LasVola/godhand-recomp/blob/14e956a1274332440273845fbab2c1f1e30c4a5a/runtime/ps2xRuntime/src/lib/gs/gpu/gs_gpu_backend.cpp),
[sampler](https://github.com/LasVola/godhand-recomp/blob/14e956a1274332440273845fbab2c1f1e30c4a5a/runtime/ps2xRuntime/src/lib/gs/gpu/gs_gpu_shaders.cpp)
and [presentation upload](https://github.com/LasVola/godhand-recomp/blob/14e956a1274332440273845fbab2c1f1e30c4a5a/runtime/ps2xRuntime/src/lib/gs/gpu/gs_gl.cpp).

This experiment leaves the original disc, guest bytes and VRAM untouched:

1. Verify the personal retail disc, then use the existing named selector
   `st1/r100.dat / SCP3 / bank0 / image0`. Read that bounded 128x128 4-bit selector6
   resource into a **private** raw-RGBA reference. The separate
   [reference expansion](hd_reference.py) follows the historical MIT lab's
   [documented transfer format](https://github.com/YYoudi/god-hand-rs/blob/de0091371f9d405abb02bb82ca57ac2f11ab245e/specs/tm3-tim3-v1.md),
   not a game function or imported engine implementation.
2. After transfers, epoch mapping and CLUT resolution, compare every decoded
   source texel on the GPU. Initially accept only 128x128 PSMT4/32-bit-CLUT states
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
  `example_rgba()` separately regenerates the original 512x512 test pattern
  without reading game data; that authored image is not remaster artwork.
- Original invented transfer, malformed-envelope, raw-alpha and source-preimage
  tests. No retail pixels, shader dumps or generated code are CI fixtures.

The provisional envelope is `GHHD001` plus a zero byte, six little-endian u32
fields (128,128,newWidth,newHeight,16384,newWidth*newHeight), reference RGBA and
replacement RGBA. Both new axes must be powers of two, larger than128 and at
most2048. Exact length and a 64MiB budget are checked before GPU allocation.
The native caller must verify the whole-file SHA-256 and retail profile first.
The envelope contains an original-game reference: **never distribute it**.
This is a private probe protocol, not a stable public resource-pack schema.

## Required controls and limits

Keep original 512x512 authorship, immutable input hash, exact source/executable,
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
remain distinct. No source-texture reference data, extracted asset or executable
is public; reviewed renderer screenshots are the separately authorized exception.

## Native provenance and observed controls

Pinned upstream: `14e956a1274332440273845fbab2c1f1e30c4a5a`. Operational source:
`193076584e277c95644dcbbb4a6922c3a59ca2b8`, executable SHA-256
`eaed174f4d0c1df5530e5a65b2d53611a14d3037c9e01a3e0aa02c8d6a0d4e53`.
Its source/executable and prior PDB bytes are restored after each terminal build;
the prior PDB is not asserted to match that original executable's symbols.
Both controls variants and the personal ISO are preserved separately.

The first private trial source is `9cdde7db753cb84c869dcbff61f9720cf21e11b2`,
executable SHA-256 `eb1b5bf7face1b16f9f0e69e58179ebd3fef788294aa8ebf816f49f88537aa1d`.
Its enabled300s and disabled220s starts finish at native deadline124 without
forced termination. Enabled uploads512x512/1048576 replacement bytes with
unchanged internal scale3 and reports exact source matches. Disabled uses no HD
input, reports no HD upload and reproduces baseline field4741 exactly.

Clean public helper tooling `0ce2bc347c05364b277c0bdef85023f762506053` is recorded by the later private build receipt.
The resulting private source is `9167a9c53f414dc07d107baa737d44549a2f6451`,
executable SHA-256 `cfc1c5a1b223f1ebfc66d7b69986e56577e7f89765d245d62a1b709d825f1899`.
This is a separate checked helper build, **not a public variant installer**.
Its enabled300s run also finishes at124 and produces the same field4741 PNG
byte-for-byte as the first trial. Its LF-normalized C++ helper source and the public Python
reference/envelope output match the actual compiled/used inputs exactly.

The same later executable also passes two separate controls:

| Control | Observed result |
| --- | --- |
| One changed interior reference pixel (73,101),300s | The valid input uploads512x512, but no exact source matches occur. Original field4741 PNG equals the baseline byte-for-byte. No game texture or VRAM bytes are modified. |
| Invalid whole-input SHA-256,220s | Native loader rejects the file before any HD GPU upload. Original field4741 PNG again equals the baseline byte-for-byte. |

All five native starts end at the intended deadline124, with no forced kill;
all validation drivers return0. Native shader failure lists are empty. These
are targeted title/start controls with isolated preferences/cards and muted
audio, not autonomous combat, a playthrough or a fresh-generation installer test.
The six new game-free tests bring the local suite to155:154pass, one Windows
symlink-privilege skip. No game input is supplied to CI.

The selected same-field original/replacement PNGs are unretouched 800x600 files.
All 74,290 changed pixels lie inside x0..639/y419..599; three named saloon, pharmacy
and sky rectangles are unchanged. Camera, actor/HUD image above that band and
known black capture padding are retained. This is a sampled native comparison,
not a PS2 hardware reference or full-game fidelity result.

The original 512x512 pattern is generated by `example_rgba()`; its SHA-256 is
`b3d871e3d5c6e76bf1c8343c099024033b38058de805c07f83ca6a33a6203b04`.
The private input envelope also contains game-derived reference pixels and is
not published. No original source texture, VRAM dump or game program is a
public synthetic test input.

Retained failures: the first handwritten address fixtures mixed up VRAM byte
addresses and stored raster bytes, and failed before any disc read. The first
actual C++ build used a GL wrapper function that does not exist; it fails2,
restores the baseline and is retained. The corrected build uses the wrapper's
actual 64-bit limit query. Neither failure is silently counted as a pass.

Only 512x512 is natively demonstrated here, not every parser-permitted dimension.
The default backend is observed; separate compute/hardware/filter/alpha sweeps
are not complete. The prototype/profile, later scenes, decoded-content aliases,
device buffering, real game saving and campaign coverage remain separate gates.
The per-candidate classification/readback is experimental and not performance
acceptance. A checked opt-in installer and stable external-image pack protocol
are future work, not features enabled by the current public run command.
