# Original prototype no-death: damage, refill, OFF and death

12 November 2026 (Europe/Paris). Original capture timestamps are retained in UTC
on 11 November. Follow-up to [the original menu](SIO2_PAD_STATUS.md) and
[Player Warp](PROTOTYPE_WARP.md). The full developer-tools goal remains active.

## What now works in the local build

One fresh native22 process uses the original prototype menu to turn **PL NO DEATH**
ON, return to combat, receive real enemy attacks, reopen the menu, turn the option
OFF and return to combat again. After OFF, health falls to zero, Gene collapses
and the original **Continue? Yes / No** prompt appears. This is not just an ON
label or an inference from a zero health value.

Read-only observations qualify the actual player, original damage stack frame
and the original positive-health refill site:

- 14 selected damage calls while ON apply 125 HP in total, exceeding
  the original maximum of 100. The player remains alive.
- 16 actual events at the original same-flag refill site restore positive
  health to maximum. Damage really happens: this is **not a no-damage mode**.
- After the original menu clears the option and both menu levels close,
  12 selected damage calls are observed. Health reaches zero, and the
  unchanged native captures show the collapse and Continue transition.

The hook covers one selected damage function, **not every health writer or every
enemy attack**. Extra refill events and gaps between consecutive observed health
values are retained rather than invented as complete coverage. The separate
nonpositive-health clamp in the damage path was not exercised while ON; its
static presence is not runtime acceptance of that branch. A separate original
near-death safeguard also means surviving a single hit would be insufficient.

## Experiment and limits

The original Room Jump selects **Stage 1 / Room 00 / Point 0**, with nearby enemies.
This differs from the earlier Point 1 Warp experiment. Start skips the introduction.
Original menu inputs enable no-death, then one bounded backwards-stick request
moves Gene before idle observation. The test sends no player attacks, automated
level-completion loop, imported save, health write or debug-flag write.

At fields 7600/7610 the original chord reopens the menu. Down 7800, Circle 8000
and Left 8200 clear the option. Cross 8400 and 8700 leave both menu levels. These
widely separated guest-field requests are observed, not merely assumed delivered.
The exact full script is in the [aggregate evidence receipt](docs/evidence/prototype-no-death-2026-11-12.json).

All eight hardware-controller bindings are disabled; one diagnostic virtual pad
uses the repaired original IOP/EE path. Inherited diagnostic variables are stripped.
The process is hidden/muted, with a prospective 900-second watchdog and fresh scratch
preferences. It exits 0 when the watchdog requests shutdown; no Continue selection
or campaign completion is attempted. No owned compiler or synthetic suite overlaps
this native GPU run. This is not whole-machine performance isolation.

The reviewed comparison originals are unchanged PNGs: menu ON/OFF, live ON,
reduced-health OFF, empty-health collapse and Continue. Combat poses and the death
view differ; these are **unmatched action/restore evidence**, not PS2 image parity.
No crop, resize, normalization, generated illustration or journal screenshot is used.

## Corrections and failures retained

The first read-only damage observer incorrectly passed a ternary expression into
a retained macro with an unparenthesized index. Its entry reads were rejected;
those rejected observations are not gameplay proof. Precomputing the diagnostic
register index corrects the call site. An invented-register probe using the actual
retained header reproduces the mistake and the correction; no original macro,
runtime library, game instruction, register, health or debug flag is patched.

The first probe driver also removed the shell's `/c` instead of the compiler's
`/c`, and failed. Its owned idle shell and failed receipt are retained. A separate
corrected V2 compiles/runs 0. Neither probe executes the game or sends OS input.

Native21 already showed real ON damage and later an OFF option, but its closely
spaced back requests left the parent menu open. A final input was appended **after
that process exited** and was not delivered. That 600-second run is incomplete,
not restored-death acceptance. Native22 is a new prospective 900-second experiment,
not an extension or passing relabel of it. Future manual diagnostic requests must
check a live process handle/identity; old log growth or a stale PID is insufficient.

The earlier floor-only interpretation was incomplete. The original same-flag
positive-health refill branch is now observed directly; the harness does not
implement a replacement heal or artificially lower health to force a test.

## Exact build and remaining work

- Frozen LasVola runtime: `1646d8854e1c3e16e5ec9bb7aeddebe0fe0fa14a`.
- Module tooling: `193076584e277c95644dcbbb4a6922c3a59ca2b8`.
- Native executable SHA-256: `7b5d91cb475b98ea44e6e3919dd8f62497f2a0f44c958b16d5f1645b693478ac`.
- Linked source/input snapshot SHA-256: `a9a13cd2a3bea9e740a47c80f367f0ba8a69b8e456b148fc6a6449919738500d`.
- MSVC 14.44.35207; host compiles/link 0; all 9,793 old objects, original discs,
  previous executables and unrelated work preserved. No old object is overwritten.

The private generated-source observations retain original instruction comments
and order, checked against the exact prototype ELF. That check is not proof of
translation, ABI or every guest-PC entry. Experimental prototype VU1 AOT remains
explicit; the previous strict verifier failure is not fixed or hidden. No measured
speedup, hardware input/audio, real Save/Load or campaign/fidelity claim follows.

This establishes one no-death ON/OFF/death cycle in one prototype room, alongside
the earlier Warp and Room Jump proofs. It is **not a complete debug menu release**:

1. Actual Windows short F1/F2 events and focus/owner coexistence still need native
   acceptance. Owner Escape stopped desktop control; it has not been resumed.
   A separate in-scene shared-handler request works, but is not a physical keypress.
2. A source-complete, profile-gated prototype generation/build workflow remains to
   be packaged and tested. The public retail setup does not install this candidate.
3. Other original options, destinations, module lifetimes and unavailable states
   need separate bounded tests. Only four prototype modules are currently compiled;
   the menu's list is not a claim that every room/action is supported.
4. Retail debug equivalents require their own identity/ABI/lifetime evidence.
   Prototype addresses and flags must not be transplanted into retail.

Public source remains original GPL continuation tooling. Private generated game
code was inspected: this is not presented as an independent clean-room component.
No disc, ELF, extracted asset, raw map/log, dump, save, binary or generated game
source is published. Selected game imagery is neither MIT nor GPL; the owner's
publication request is not rights-holder permission. The Rust lab stays paused.

## Publication checks

The full invented-input suite passes: 262 tests, exit 0, three Windows symlink
skips (85.069 seconds), using a short command-local temporary directory on G:.
All 31 retained file hashes and four paused Rust WIP hashes match the previous
publication receipt. These synthetic/hash checks are not additional native key,
performance, campaign or general fidelity acceptance.
