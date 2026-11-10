# GPU-resident texture-match results (gpu-v2)

10 November 2026 (Europe/Paris). **Built and observed locally through the public
installer/launcher**, for the sampled scope below. [hd-v1](HD_PACKS.md) and every
older binary retain their identities. This additive version is not selected by
default, a persistent match cache, general HD support or a demonstrated FPS gain.

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

## Reproduced controls

Clean public tooling: `b3c57786b906f20f6a0e1eeb2b771ce81c112e2d`.
Pinned LasVola: `14e956a1274332440273845fbab2c1f1e30c4a5a`.
Derived native source: `953ea26336227e92455dbea1d4d791dd18b5159c`.

- Version fingerprint: `37018376887e83eac9f3356f528f062811ac152f6715131abae2a4875e1cbcb5`.
- Executable SHA-256: `5d27048f688e0264123d733826d8399a4e619af75852fe267100c92409001b02`.
- PDB SHA-256: `95c1f4833702f9e81b236eb5a3ccac517dd5ec887f667719eae235899c95ffb7`.

Actual configure/build both return0 on Windows/MSVC14.44.35207. Baseline source,
executable and prior PDB bytes are restored; that older PDB is not claimed to
match the original executable's symbols. The old controls versions and hd-v1
remain independently verified. Existing private generation/object/shader caches
are reused; this is not a clean-cache benchmark or fresh generation test.

| Actual public CLI control | Observed result |
| --- | --- |
| Enhanced + explicit gpu-v2 + valid512x512 pack,300s | Verified private input, larger-image upload and submitted classifier batches logged; match counts explicitly unread. Native field4741 PNG equals the prior authored-pattern PNG byte-for-byte. |
| Same GPU-v2 binary, no pack,220s | Empty HD protocol overrides stale inherited values; no HD upload/submission. Original field4741 equals the baseline PNG. |
| Same GPU-v2 binary, invalid image hash,220s | Preflight warns and falls back, then reproduces the same original PNG. This is not native checksum validation. |
| Default Original,30s | Selects preserved baseline1930765/executableeaed174; startup only, not another first-fight validation. |
| HD requested without a version,30s | Selects preserved hd-v1/source8dec495, not GPU-v2. Startup only. |
| Explicit legacy controls-v1 and audio-v2,30s each | Both select their preserved source/executable; no HD input. Startup rollback only, not input/audio/pause validation. |

All seven public launchers return0; every native process ends at deadline124,
without forced termination or shader errors. Clean tooling is recorded in each
receipt. Three separate actual CLI refusals return1 without native spawn:
strict invalid pack, Original+GPU-v2, and version without capability.

Two further **direct native** controls use this exact installed GPU-v2 binary:

- Valid input with one interior private reference byte changed,300s: upload and
  submitted classification still occur, but the sampled field4741 reproduces
  original assets. Counts remain unread: do not claim zero matches throughout
  the game. Disc, guest VRAM and authored image are not patched.
- Unchanged valid input with deliberately wrong expected whole-file hash,30s:
  native loader reports `disabled: input hash mismatch`, with no HD upload,
  startup captures and deadline124. Not public preflight or first-fight proof.

Both drivers return0, inputs remain unchanged and no shader errors are observed.
The first hash-control script failed its Python import before spawning anything;
it is retained, and a distinct corrected script uses the explicit repository
root. That scripting failure is not an additional native failure or pass.

Long runs use only the retained title/start/pause script with fresh scratch
preferences/cards and muted hidden capture. No attacks, imported saves,
autonomous level completion, camera/object or internal-scale edits. The sampled
800x600 originals retain known black readback padding:

- Valid: `c0720b6a89b05bed007fa76060029f8db542f69365df6270c4cedafff94428b2`.
- Absent, invalid/fallback and direct reference-negative:
  `fd53182e7a2982021e5c5008d2e5dbab4dbd907cf9dfe52edc520c9a5d02315e`.

These fresh captures equal existing reviewed image bytes. No new visual pair is
invented for this nonvisual implementation; the
[earlier checked-HD comparison](https://yyoudi.github.io/god-hand-pc/comparisons.html#2026-11-09-checked-hd-workflow)
keeps its own timestamps/revisions. New original files and native receipts remain
private in `hd-gpu-v2-2026-11-10`.

188 original synthetic tests pass locally and in a fresh public autocrlf
checkout:186pass/two Windows symlink-privilege skips. The typed model is later
strengthened for generic/indexed bindings and the real host's nonempty-draw
precondition; runtime helpers and the installed fingerprint are unchanged.

## Binding and test scope

The old readback-only generic rebind is also removed. Indexed13/14 bindings
remain the sampler/classifier interface, but **complete GL-state equality is
not claimed**: `BindBufferBase` also changes the generic binding according to
the primary [Khronos reference](https://raw.githubusercontent.com/KhronosGroup/OpenGL-Refpages/main/gl4/glBindBufferBase.xml).
Audited pinned upstream buffer manipulation sites select their own targets;
that source finding and the native image controls have limited scope, not a
promise about all future upstream callers. The invented API model now tracks
both binding types, rather than treating them as interchangeable.

Empty draw batches do not invoke preparation or raster in the host. The model
checks that caller precondition; a zero-sized toy buffer is not evidence of a
valid real GL operation. The typed model is not a shader/driver conformance test.

## Remaining gates

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

The sampled functional controls above pass. A later unchanged-binary pilot and
fixed-field v1/v2/v2/v1 block is documented in [FRAME_SPANS.md](FRAME_SPANS.md):
actual bounds and endpoint originals agree, but no reliable speedup is established.
It does not change defaults or complete broader performance acceptance.
Controlled repeated performance measurement,
other drivers/backend paths and wider scene/state coverage remain open. There
is **no FPS/speedup claim**, and the old timing scopes must not be subtracted as
time saved by this version. Real game
SaveExitLoad, physical input/audible audio, later stages/campaign accuracy,
filter paths, other dimensions/resources, HD+controls composition, cache
invalidation, prototype kernel support, widescreen/FPS/lighting and multiplayer
remain separate gates. The full port/remaster goal is not complete.
