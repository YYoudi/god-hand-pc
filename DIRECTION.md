# Direction: faithful original first, reversible modernization second

Owner decision: 9 November 2026. This replaces evaluation-only planning; it does
not mark the paused independent Rust/Bevy rendering objective as achieved.

## Medium-term deliverable

A reproducible, personal-ISO-required native PC build with a documented original
behavior baseline, real persistence and usability checks, and separately enabled
PC extensions. Continue the evaluated LasVola base; do not rebuild combat and AI
in a different engine just to retain a language preference.

The canonical task/status registry and English journal remain in
[god-hand-rs](https://github.com/YYoudi/god-hand-rs/blob/main/docs/dashboard/data.json),
with its generated [roadmap](https://github.com/YYoudi/god-hand-rs/blob/main/ROADMAP.md).
This document defines acceptance, not a competing completion ledger or schedule.

## 1. Original baseline gate

- Reproduce ISO-required generation/build/startup while retaining all diagnostics.
  Exit zero does not establish clean translation. One retail generation error
  remains unresolved in the evaluated recipe.
- Save through the actual game, close the process, and load in a new process.
  Runtime snapshots, card-file existence and an HLE directory are not substitutes.
- Verify physical keyboard/controller round trips and audible output on hardware.
  Hidden scripted input and muted probes are different evidence.
- Compare representative rooms, combat, camera, transitions, cinematics, bosses
  and progression against a named reference. Organize human campaign testing and
  legitimate owner saves rather than autonomous level-completion loops.
- Preserve revisions, original screenshots and failures. A sampled opening scene
  is not a claim of accurate full-game coverage.

## 2. Maintainable modification gate

Keep upstream pinned privately and our original host extensions public under
GPL-3.0-only. Do not maintain edits by hand in regenerated game C++.
Establish a documented function/subsystem identity, an explicit replacement
boundary, and original-behavior controls before replacing that behavior.
Readable C/C++ can be introduced incrementally; generated C++ is not automatically
readable original source. LucasPicoli is a comprehension complement, not already
a PC port or a prerequisite to rebuilding every function.

Public `--profile original` refuses resource packs; `--profile enhanced` permits
an explicitly requested extension. Both still use the same pinned runtime.
Profile names express launch policy, not a PS2-accuracy certificate. Existing
upstream settings/timing are not frozen or validated by that policy.

## 3. First PC enhancements

| Work | Required proof |
| --- | --- |
| PC settings | Audit existing upstream options first; persist settings safely, validate them, and make enhancements reversible. |
| Widescreen | Camera/projection and FOV tests, HUD, cutscenes and visibility; no stretched-image shortcut. |
| HD resources | A distinct size-aware upload/import contract and an original external image of different dimensions actually rendered. Current same-size pack proof is not HD. |
| Variable/unlocked FPS | Separate presentation from simulation where possible; verify timers, animation, collision, hit windows and AI at different cadences. Removing a limiter is not acceptance. Fixed simulation/interpolation is a hypothesis until tested. |
| Graphics/lighting | Distinguish postprocessing from new material/light semantics. Replace the renderer incrementally if evidence requires it, preserving original gameplay; no promise that a GS stream directly provides modern materials. |
| Multiplayer | Separate feasibility milestone: second-player semantics, camera, targeting and progression as well as synchronization/networking. Snapshot support does not prove determinism or rollback. Not a promised feature. |

## Prototype research boundary

The prototype is a separately hashed private input for bounded discovery of
labels, resource organization and diagnostic leads. Static strings are not
executed functions, and matching names do not permit copying addresses between
builds. Debug-menu claims need actual runtime observation. The existing prototype
native build links but its startup blocks on unsupported kernel syscall 0x7a;
do not hold the retail baseline hostage to a prototype kernel port.

## Architecture decision

Use [the extension boundaries](ARCHITECTURE.md). Revisit a whole-engine migration
only after a reproduced blocker and a comparative experiment justify its cost.
Contribute generic fixes upstream when appropriate; evaluate new upstream pins
against retained baseline/profile/pack tests before adopting them.
