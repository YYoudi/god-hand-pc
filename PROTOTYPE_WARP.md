# Original Player Warp: actor movement and return to the game

12 November follow-up: [original no-death ON/OFF/death control](PROTOTYPE_NO_DEATH.md).
The dated results below are preserved; full menu/key/workflow acceptance stays open.

11 November 2026. Follow-up to [the original prototype menu](SIO2_PAD_STATUS.md).
The full developer-tools goal remains active. This is one scoped prototype
result, not a retail feature, checked prototype installer or complete port.

## Reproduced experiment

Two fresh, hidden/muted 240-second runs use the same native18 executable and
original prototype disc. All eight hardware-pad bindings are explicitly disabled;
only a virtual diagnostic controller is connected. Inherited diagnostics are
removed. No Windows keyboard/mouse input is sent after the owner stopped it.

Both runs use the original menu to select Stage 1 / Room 00 / Point 1, skip the
introduction with Start and enter **Player Warp**. The move run adds a bounded
left-stick-right request at fields 4100–4159. The control does not. Start at
4500 leaves Warp to its parent; Cross at 4800 closes that menu. No actor position,
debug flag, ready status or successful return value is written by the test.

Read-only guest-thread observations follow the original `Getplayer` object,
its actual position vector, cached vector and the Warp ground target. They are
not inferred from the camera work pointer:

- Both runs start with byte-identical actor coordinates.
- In each run, all twelve selected in-Warp samples have actor, cached and target
  vectors equal.
- The move run ends about **3.47 original world units** from the no-stick control.
  Units are not assumed to be metres. The difference persists after closing the
  menu and returning to the ordinary game.
- Actual lifecycle-tail observations show temporary-camera activation and
  restoration of the original camera manager. Original captures show the normal
  HUD again after closing the parent menu.

Both processes stop 0 after the watchdog requests shutdown. This is not campaign
completion. The [evidence receipt](docs/evidence/prototype-warp-2026-11-11.json)
and journal preserve unchanged before/during/after/control originals.

The control is **not a mathematical no-op**: entering Warp itself shifts placement
slightly toward its target. Exiting restores the camera/mode, not the previous
actor position. No cancel/undo feature is claimed. Earlier free-warp output also
contains a detached cloak-like artifact; it remains preserved, not declared fixed.

## Corrections retained during the investigation

A manual signed-immediate error initially selected the wrong fixed address.
Those read-only values are rejected, not used as player evidence. Original
instruction words establish the corrected address; no game memory was changed.

Stored original names then identify the active work as **camera** work. Camera
restoration alone cannot prove player teleportation or cancellation. The later
experiment therefore reads the actual player vector and compares a no-stick
control rather than inferring an action from a changed viewpoint.

A generated native function can yield before its logical guest return. An
immediate C++ wrapper return was consequently not constructor-completion proof.
Separate copied private units add read-only observations at the actual lifecycle
tails. Original instruction comments/order are unchanged; that identity check
does not certify translation, ABI or every guest-PC entry. The old 9,793 objects,
failed observers, executables, discs and unrelated work remain preserved.

## Build identity and limits

- Frozen LasVola runtime: `1646d8854e1c3e16e5ec9bb7aeddebe0fe0fa14a`.
- Pinned module tooling: `193076584e277c95644dcbbb4a6922c3a59ca2b8`.
- Native executable SHA-256:
  `947437e66ed077a6b4906e2a898dbc507f00eeba383f94e51de7010c702de1b2`.
- Linked source/input snapshot SHA-256:
  `2b8f1ff6017e63cdb2380b85205e59d08de7558b1b60d62bc1cf1d5b1779d077`.
- MSVC 14.44, actual host compile/link 0. Five actual prototype-captured VU1
  programs are explicitly selected. These Warp runs do not run a verifier.

The earlier strict VU1 comparison fails; its narrower observable counterpart is
not strict equivalence or a performance result. Original generation diagnostics
remain. No default retail executable, policy or launcher version is promoted.

This covers one room, one move and leaving the mode. Other destinations,
unavailable/invalid states and full fidelity need more evidence. Actual F1/F2
key acceptance after the [short-event candidate](WINDOW_SHORTCUTS.md) remains
open. A diagnostic handler invocation is not a Windows keypress.

`PL NO DEATH` has only an original option OFF/ON/OFF round trip so far. Lethal-hit
survival, no-death versus no-damage and restored death remain required. Static
inspection suggests another near-death safeguard in the damage path, so merely
surviving one hit will not be counted as proof. Runtime damage/health tracing is
the next experiment, not a completed cheat or an autonomous combat loop.

Private generated code was inspected for the GPL continuation, not an independent
clean-room engine. Public material contains only original continuation tooling
and reviewed evidence: no game code, disc, ELF, asset, dump, save, raw map or
binary. Game imagery is neither MIT nor GPL; the owner's publication request is
not rights-holder permission. The historical Rust lab remains paused, not achieved.

## Publication checks

The full invented-input suite passes: 262 tests, exit 0, three Windows symlink
skips (78.705 seconds). The explicit public-tree check reviews 244 allowed paths
and 55 retained screenshots, with no game inputs. Thirty-one retained file hashes
and four paused Rust WIP hashes match. These checks are not native key, campaign,
performance or general fidelity acceptance.
