# GPU-resident texture-match results (gpu-v2)

10 November 2026. Implementation contract; **native integration is not yet
verified**. The last installed/render-tested workflow remains
[hd-v1](HD_PACKS.md). This additive experiment is not a replacement by default,
a persistent match cache, general HD support or a demonstrated FPS improvement.

## Boundary

The [earlier measurement](HD_TIMING.md) distinguishes CPU result-readback waits
from GPU command intervals; subtracting them does not predict a speedup.
The new original [host methods](adapter/hd_runtime_gpu.inc) retain the same
full-source classifier, shader, resource reference, larger authored image and
barrier-before-raster consumption. Each batch resets its GPU flag storage and
eligible batches classify every submitted state. Nothing is cached across
batches or identified solely by an address, epoch or CLUT slot.

Only the continuation adapter's CPU match-result readback/counter loop is
removed. Other upstream readbacks, buffer uploads, driver waits and rendering
costs remain. Native logs say that dispatches were **submitted** and match counts
are **unread**, never zero or proven applied. Actual rendered controls remain
necessary. No timer/query wait is added to this path.

## Explicit selection and preservation

Requires the checked personal-disc setup and named-pack bridge in the selected
Windows/MSVC workspace; no game data or binary is downloaded here.

```powershell
python pc.py install-hd-textures --workspace-name retail-setup-v2 --version gpu-v2
python make_example_hd_pack.py --output .local/example-gpu-pack
python pc.py run --workspace-name retail-setup-v2 --iso "G:\path\God Hand (USA).iso" --profile enhanced --hd-textures --hd-textures-version gpu-v2 --hd-pack .local/example-gpu-pack/pack.json --strict-hd-pack
```

The recipe has a separate `hd-gpu-v2` layer/pointer, exact host preimages and a
14-file composite source identity. It preserves baseline source/executable/PDB
and reconfigures/forces affected host units before reusing private generated
inputs and objects. This is not a fresh ISO-generation recipe or resolution of
the retained generation error. Failures and interrupted-build locks are kept.

No-version installation/HD launch still means **v1**. No HD request still means
the old baseline/controls policy. Existing v1, controls-v1 and audio-v2 inputs,
fingerprints and pointers must not be silently upgraded or overwritten.
HD with controls-pause or same-size packs remains refused, not composable.
Original refuses HD requests; a version without its capability flag is refused
before workspace/disc/process access. Strict-HD remains a **preflight** refusal
policy, not proof that the GPU supported/matched/rendered a replacement.

The existing one-resource manifest, raw GS-alpha and private ISO-reference
contract is unchanged: only 512x512 on the documented 128x128 source has prior
native evidence. Source reference/envelopes, ISO, generated game code, assets,
dumps, saves, executable and PDB must remain private.

## Validation gates

- Compile the actual owned methods inside an original invented typed API model
  with **no CPU readback method**; verify reset/reused/changed/shrinking/empty
  batches, admission, barrier ordering and startup fallback. That model is not
  real GLSL, a driver, timing or game-fidelity evidence.
- Synthetic version coexistence, source/helper/binary drift, failed/live build
  preservation, invalid policy refusal and distinct launch receipts. Preserve
  the prior v1 fingerprint exactly.
- Build the exact committed public recipe locally, then observe actual valid,
  absent, invalid/fallback and Original controls. A separate direct-native
  interior-reference negative is not public pack-preflight validation.
- Check unchanged renderer originals at the same field/viewpoint; retain all
  failures. Do not invent a new visual pair for a nonvisual implementation or
  call a submitted dispatch an observed content match.

Native controls and any measured performance change are pending. Real game
SaveExitLoad, physical input/audible audio, later stages/campaign accuracy,
filter paths, other dimensions/resources, HD+controls composition, cache
invalidation, prototype kernel support, widescreen/FPS/lighting and multiplayer
remain separate gates. The full port/remaster goal is not complete.
