# Extension boundaries

This is an original GPL continuation layer around privately fetched LasVola,
not a vendored fork, a clean-room game engine or a published game-code tree.

```text
Personal retail ISO + pinned upstream/dependencies
  -> private generation and build -> original logic + compatibility runtime
Original public continuation code
  -> checked host integration + profile/pack policy
  -> local native executable and private validation receipts
```

## Ownership and lifecycle

| Layer | Current boundary | Modification rule |
| --- | --- | --- |
| Generated guest logic | Local only, regenerated from the owner's disc | No durable manual edits; future replacements need an explicit identity and tested registration point. |
| Compatibility runtime/rendering | Pinned upstream fetched into ignored storage | Reviewed host-source integration with exact preimage hashes; preserve upstream notices, baseline and private derived revision. |
| Our native adapter | Public original GPL files in adapter/ | Game-independent interfaces and synthetic tests; no embedded game instructions or assets. |
| PC policy | profiles.py, launch_packs.py, pc.py | Validate before launching; clean inherited GODHAND_/PS2X_ variables; record requested policy and actual pack outcome separately. |
| External original packs | Named resource schema | Exact disc/profile check, immutable per-run payload, original-asset fallback unless strict mode was requested. |

`Original` is the default launch policy: no continuation pack overrides.
`Enhanced` permits explicitly selected extensions, not an automatic bundle:
the same-size bridge, checked controls versions, or separate experimental
[hd-v1](HD_PACKS.md). HD+controls/same-size packs currently refuse combination;
they require a separately tested composite recipe. Only one512x512 authored
replacement on a128x128 source has HD runtime evidence. None enables widescreen,
frame-rate changes or a new renderer.
Upstream's own baseline may already differ from hardware in resolution/timing.
Neither profile claims full-game fidelity. Test input, headless audio muting and
capture options are diagnostic controls and must remain explicit in evidence.

The experimental controls-pause host layer is a separately built/verified variant
over that same base, never an implicit default relink. Enhanced plus an explicit
flag selects it; see [its checked installation contract](CONTROLS_INSTALL.md).
Its exact public integration now has a locally reproduced build, targeted native
hold/resume/stop, pack compatibility and default-baseline controls. This remains
experimental sampled evidence, not full-machine/campaign fidelity. Original
still rejects this host extension; future upstream changes need fresh preimage,
regeneration/build and behavior controls, not automatic replay.

Controls versions are additive private layers: legacy v1 retains its original
16-file identity, audio-v2 has17 files and an explicit separate installed pointer.
The existing no-version flag does not change meaning; audio-v2 requires explicit
installation/selection. Synthetic coexistence/drift and actual native startup
rollback controls cover that boundary. The activity barrier closes one reproduced
admitted-consumer race, not producer/device quiescence or audible quality; see
[the retained native controls](AUDIO_HOLD.md).

## HD match-result lifetime

Before caching native HD match results, read [the actual matcher measurement](HD_TIMING.md).
Epoch/state/CLUT slots are not persistent content identity. The current CPU
readback in preserved hd-v1 is diagnostic. Separate explicit
[gpu-v2](HD_GPU_RESULTS.md) now keeps match results on the GPU, resets/reclassifies
each batch and passes sampled native render/fallback controls. It is not a
persistent cache or a measured performance result. Indexed bindings stay fixed;
generic binding state is not asserted equal. Broader callers/drivers/scenes and
controlled performance measurements remain acceptance gates.

## Future readable function replacements

Before adding one: record the disc/revision, provenance, verified function or
subsystem identity, observable contract, original control and expected failure.
Store original replacement source separately from generated outputs, gate it by
explicit capability/profile, and test fallback and regeneration/update behavior.
The evaluated runtime exposes function-registration/replacement APIs; their
presence alone is not proof that a specific game override is correct. Overlay
lifetime, ABI, address identity and load order require their own experiments.

No game function replacement registry is implemented by the launch-policy change.
No decompiled code may be relabeled as independent MIT work. If source-derived
code is ever used, record that provenance and review licensing/distribution first.

## Update strategy

Pin for reproduction, not permanent isolation. Trial a new upstream commit in
a fresh ignored workspace, review license/dependency changes and integration
preimages, regenerate locally, then compare build/startup, actual saves and
representative behavior plus original/enhanced/fallback controls. Repin only
after the relevant gates; retain the earlier executable/evidence. An automatic
upstream merge or a successful compile is not a fidelity result.
