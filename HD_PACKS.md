# Checked experimental larger-texture packs (hd-v1)

Implementation contract, 9 November 2026. **Not runtime-verified yet.** The
[earlier private proof](HD_TEXTURES.md) is retained, not relabeled as this public
recipe. No current installed executable or controls-version pointer is replaced.

## Proposed commands and isolation

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
refuses launch instead. The native loader independently checks profile, complete
input hash/length/shape before GPU upload. Requested/planned/uploaded/content-
matched/rendered are distinct evidence: a launcher receipt is not visual proof.
Explicit empty HD environment values must override stale native configuration
when the capability/pack is absent. Old Original/v1/audio-v2 meanings stay fixed.

## Acceptance gates

- Original invented fixtures for manifests, bounds, raw alpha, paths, immutable
  copies, duplicate fields, negative controls and no disc data in CI.
- Checked source/executable/PDB preservation, exact composite source manifest,
  no unrelated edits, retained failure/interruption and drift refusal.
- Actual clean committed public recipe build, enabled512x512 rendering, absent
  and invalid/fallback originals, strict refusal and old-binary restoration.
- Preserve all original screenshots and failed hypotheses; publish only reviewed
  same-view originals with hashes/provenance and factual English journal updates.

This does not complete accurate-PC, game Save/Load, hardware/audio, campaign,
performance, widescreen/FPS/lighting or multiplayer acceptance.
