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
`Enhanced` currently permits only the existing same-size named texture extension;
it does not turn on widescreen, HD dimensions, frame-rate changes or a new renderer.
Upstream's own baseline may already differ from hardware in resolution/timing.
Neither profile claims full-game fidelity. Test input, headless audio muting and
capture options are diagnostic controls and must remain explicit in evidence.

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
