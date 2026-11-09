# Checked experimental larger-texture packs (hd-v1)

**Later follow-up:** [gpu-v2](HD_GPU_RESULTS.md) keeps results on the GPU and has
separate native controls. No-version commands below still select this preserved
v1 workflow; there is no automatic upgrade or proven FPS gain.

9 November 2026. **Checked public recipe built and tested locally**, for the
single-resource scope below. The [earlier private proof](HD_TEXTURES.md) is
retained, not relabeled as this later build. No baseline executable or existing
controls-version pointer is replaced. This is not general HD support or a remaster.

## Commands and isolation

Requires the evaluated Windows/MSVC personal-disc setup and installed named-pack
bridge in the selected workspace; see [SETUP.md](SETUP.md) and
[RUNTIME_PACKS.md](RUNTIME_PACKS.md). This is an additive host build using its
existing private generated inputs/object cache, **not another fresh ISO setup**.

```powershell
python pc.py install-hd-textures --workspace-name retail-setup-v2
python make_example_hd_pack.py --output .local/example-hd-pack
python pc.py run --workspace-name retail-setup-v2 --iso "G:\path\God Hand (USA).iso" --profile enhanced --hd-textures --hd-pack .local/example-hd-pack/pack.json --strict-hd-pack
```

The example command creates original diagnostic artwork without reading a disc;
its output directory must be new/empty. Omit `--hd-pack` to run this same HD
binary with original assets. Omit **all** HD flags to select the old baseline.

`install-hd-textures` builds a separate `hd-v1` native layer over the checked
personal-disc/pack-bridge baseline. Preserve its source, executable and any PDB;
reconfigure, force affected host units, link and copy the new variant into its
own run directory, then restore the baseline before publishing its pointer.
Keep failures and locks if source ownership or a live child prevents recovery.
No game regeneration, guest instruction patch or imported game source.

`run --profile enhanced --hd-textures --hd-pack <manifest>` explicitly selects
it. Without a pack it uses original resources; without the HD flag it selects
the old baseline/controls policy. Original refuses all HD requests. A pack or
strict-HD request without its capability flag is refused, never ignored.
HD plus a same-size pack or controls-pause version is initially an unsupported
combination and must refuse before disc/source/process access. Composition needs
its own checked recipe/native tests; do not silently drop a requested feature.

## External manifest, schema 1

```json
{
  "schema": 1,
  "kind": "decoded-rgba-replacement",
  "profile": "retail-us-slus-21503",
  "replacements": [{
    "target": {"path": "st1/r100.dat", "scp": 3, "bank": 0, "image": 0},
    "image": {
      "path": "authored.rgba",
      "width": 512,
      "height": 512,
      "format": "rgba8-gs-alpha",
      "sha256": "THE_64_LOWERCASE_HEX_DIGEST_OF_THE_ORIGINAL_IMAGE"
    }
  }]
}
```

One replacement, original raw RGBA bytes only; opaque GS alpha is128, not
automatically normalized255. No PNG importer, mipmaps, hot reload or executable
pack content. Both dimensions must be powers of two, >128 and <=2048; only512x512
has native evidence so far. Source metadata must satisfy the tested128x128,
4-bit selector6/RGBA32-CLUT contract. Other compatible named sources are not
automatically validated scenes. Full decoded-content identity can also match
identical aliases; it is not unique GPU filename ownership.

Reject unknown/duplicate fields, wrong kind/profile, unsafe or escaping image
paths, bad dimensions/length/hash and unsupported source metadata. Verify disc,
source and executable **before** optional pack fallback. Freeze the original
image and its manifest identity per run; the native input additionally contains
a private raw source reference expanded read-only from the verified personal
disc. Never distribute that envelope/reference, game assets or binaries.

Invalid pack data warns and uses original assets by default. `--strict-hd-pack`
refuses launch on preflight pack validation failure instead. It does **not**
guarantee a GPU match or visible application: unsupported GPU states, no content
match or a later native input/capability failure can still use original assets.
The native loader independently checks profile, complete
input hash/length/shape before GPU upload. Requested/planned/uploaded/content-
matched/rendered are distinct evidence: a launcher receipt is not visual proof.
Explicit empty HD environment values must override stale native configuration
when the capability/pack is absent. Old Original/v1/audio-v2 meanings stay fixed.

## Reproduced build and controls

Clean public tooling: `8201ea1b3c0bbeabfe6cc15de617bd3051ba21e7`.
Pinned LasVola: `14e956a1274332440273845fbab2c1f1e30c4a5a`.
Derived local host source: `8dec4950b15f7fffe5e97b580dcc10fb758c8503`.
The 14-file composite source manifest and executable are checked on launch.

- HD fingerprint: `9477f5e5fdcd65cb16d928e6a22732438122acea456858823dde9cad6161ac70`.
- Executable SHA-256: `f17d67d6fc5efc1796176da3bb862dd7e3482f9361650d1f695005f6de3e809e`.
- Variant PDB SHA-256: `7cf1f35b14cfafd8a231880573fa744e49c8f0c80b27fe5123ad3d724dc3a04a`.

Configure and native build both return0 on the evaluation machine, using
MSVC14.44.35207, CMake/Ninja and Python3.11. The baseline source1930765,
executableeaed174 and prior PDB bytes are restored; that old PDB is not asserted
to match the baseline's symbols. Both prior controls variants remain verified.
No new game generation was attempted and the retained retail generation error
is not resolved by this host build.

All six public CLI runs use the same clean tooling revision, isolated fresh
preferences/cards, muted headless capture and bounded deadlines. Long controls
use only `1800v:start:20,2100v:cross:20,2400v:cross:20,4200v:start:20,4800v:start:20`:
title/start then pause, no attacks, save imports or autonomous level completion.

| Actual public control | Result |
| --- | --- |
| Enhanced + HD + valid original512x512 pack,400s | Native verifies the frozen input, uploads1048576 authored bytes, compares all16384 source texels and renders the larger diagnostic image. Field4741 PNG SHA-256 `c0720b6a89b05bed007fa76060029f8db542f69365df6270c4cedafff94428b2`. |
| Same HD binary, no pack,220s | Empty explicit HD protocol overrides inherited stale configuration. No HD upload; original field4741 PNG SHA-256 `fd53182e7a2982021e5c5008d2e5dbab4dbd907cf9dfe52edc520c9a5d02315e`, identical to the preserved baseline. |
| Invalid authored-image hash, fallback,220s | Public preflight warns, clears the native HD protocol and reproduces the same original PNG. This is not a native-loader checksum test. |
| Default Original,220s | Selects preserved baseline1930765/executableeaed174, not the HD binary; same original PNG. |
| Legacy controls v1,30s | Selects the preserved v1 source/executable and starts with no HD input. Startup rollback only. |
| Explicit audio-v2,30s | Selects the preserved audio-v2 source/executable and starts with no HD input. Startup rollback only. |

All six launchers return0 and natives reach deadline124; no forced termination.
Separate actual CLI strict-invalid and Original+HD controls return1 without a
native spawn. A separate **direct native**30s control on this exact HD executable
passes an unchanged valid private input with deliberately wrong expected hash:
it reports `disabled: input hash mismatch`, captures startup and exits124,
without HD upload. That test is not public CLI preflight or first-fight evidence.

The fresh enabled/disabled field4741 files equal the already published PNG bytes,
but have their own new timestamps/revision provenance in the
[checked-workflow comparison](https://yyoudi.github.io/god-hand-pc/comparisons.html#2026-11-09-checked-hd-workflow).
No old result is recounted as a new capture. All74290 changed pixels remain in
the ground band; three unmodified facade/sky regions remain exact. Both full
800x600 originals retain black readback padding; no camera/object/scale edits.

177 invented-data tests are collected locally and in an actual fresh public
checkout with autocrlf enabled:175pass, two Windows symlink-privilege skips.
The first GNU test compile rejected deprecated `u8path`; the C++20 path fix uses
no warning suppression. A missing synthetic fixture pin also initially failed;
both failed logs remain private. Neither was a game/native validation result.

Local receipts remain in ignored `checked-hd-native-2026-11-09` and the versioned
workspace runs: installer, six CLI cases, strict refusals and direct hash control.
Compiler logs are separately preserved; no game source, referenceRGBA, envelope,
authored raw payload, executable, PDB or save is published with this report.

## Remaining gates

- Original invented fixtures for manifests, bounds, raw alpha, paths, immutable
  copies, duplicate fields, negative controls and no disc data in CI.
- Checked source/executable/PDB preservation, exact composite source manifest,
  no unrelated edits, retained failure/interruption and drift refusal.
- The clean recipe build and one-source enabled/absent/invalid/default controls
  above pass locally; another machine, fresh-cache build and broader scenes are
  not implied. HD+controls/same-size-pack composition remains explicitly refused.
- Preserve all original screenshots and failed hypotheses; publish only reviewed
  same-view originals with hashes/provenance and factual English journal updates.

This does not complete accurate-PC, game Save/Load, hardware/audio, campaign,
performance, widescreen/FPS/lighting or multiplayer acceptance. Per-candidate
classification and GPU readback are expensive experimental operations; measure
them before designing a cache with correct VRAM/CLUT invalidation. No FPS claim.
