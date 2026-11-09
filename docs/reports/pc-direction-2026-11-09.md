# Faithful PC baseline, then reversible modernization

Owner decision: 9 November 2026. The medium-term target is a playable, verified
original PC version with a maintainable route to enhancements, not a wholesale
Rust/Bevy engine reconstruction. The earlier rendering objective is paused,
**not achieved**. Its source, pending changes, tests and screenshot originals
remain intact.

## Repository responsibilities

| Location | Role |
| --- | --- |
| [god-hand-pc](https://github.com/YYoudi/god-hand-pc) | Active original GPL continuation code: pinned private upstream acquisition, ISO-required build, host integration, launch policy and original named packs. |
| god-hand-rs | Preserved MIT independent lab, evidence contracts and the existing free Pages journal/task registry. No new Rust engine features. |
| Ignored local research | Third-party sources, generated game C++, original discs, native binaries, private prototype/retail evidence and candidate function maps. Never automatically published. |

The active architecture is defined in
[DIRECTION.md](https://github.com/YYoudi/god-hand-pc/blob/main/DIRECTION.md) and
[ARCHITECTURE.md](https://github.com/YYoudi/god-hand-pc/blob/main/ARCHITECTURE.md).
Continue LasVola rather than reimplement combat/AI in another engine. Upstream
remains pinned for reproducibility, not abandoned; trial updates separately and
repin only after relevant regression gates.

## Ordered acceptance gates

1. **Original baseline.** Retain a reproducible personal-disc build and unresolved
   translation diagnostics. Verify genuine game Save -> process exit -> Load,
   physical input and audible audio; compare representative rooms, combat, camera,
   cinematics, bosses and progression with a named reference. Human campaign
   testing and legitimate saves replace autonomous level-completion attempts.
2. **Readable modification boundary.** Identify one subsystem with explicit
   provenance, observable contract and an original control. Keep durable original
   replacements separate from regenerated game C++; validate registration, ABI
   and overlay lifetime before altering game functions. Matching names are leads,
   not automatically safe hooks. LucasPicoli remains an optional comprehension
   complement, not a proven full decompilation or PC port.
3. **First PC enhancements.** Audit existing options before building a settings
   menu. Validate widescreen projection/HUD/cinematics and a genuinely different-
   size original texture upload. Separate rendering cadence from simulation for
   FPS work; test combat timing instead of merely disabling a limiter. Lighting
   may require a targeted renderer replacement, not necessarily new gameplay.
4. **Multiplayer feasibility.** Separate later research: player/camera/targeting/
   progression semantics as well as state synchronization and networking.
   Snapshots are not proof of deterministic rollback. No guaranteed feature/date.

All task statuses live in docs/dashboard/data.json and the generated ROADMAP.md.
Unfinished historical independent-engine tasks are explicitly paused rather
than left as the active PC plan. No source/evidence directory was removed.

## First implementation slice

The separate GPL launcher now has explicit Original/Enhanced policies. Original
is the default and refuses pack arguments before runtime/disc checks. Enhanced
permits the existing named same-size texture bridge. Receipts record requested
policy separately from actual pack application/fallback. Inherited private
GODHAND_/PS2X_ settings are cleaned as before.

This is a real launch-policy change, not a PC settings screen, game-function
rewrite or PS2-accuracy certificate. Both modes retain the pinned runtime's
upstream timing/settings. HD dimensions, variable FPS and new lighting are not
implemented. See [the actual native controls](launch-profiles-2026-11-09.md); the
existing baseline and earlier failed experiments are retained.

## Prototype discovery

Read [the bounded metadata report](prototype-datamining-2026-11-09.md).
The saved HTML is a source of reported leads; original ELF metadata supplies
additional static observations. Neither proves the debug menu runs. The prior
native prototype syscall-0x7a startup blocker remains unresolved and is not a
dependency for retail work. Do not copy prototype addresses into retail hooks.

MIT applies to original independent-lab code only; the continuation is GPL and
not presented as clean room. Game imagery/content remains third-party property.
No original game program, generated function, asset or save accompanies this plan.
